"""
Localizzazione dei 15 comandi da builder/sviluppatore piu' avanzati (Fase C,
seconda tornata), rimasti volutamente fuori da cthulhu_building.py:

@alias, @copy, @cpattr, @mvattr, @set, @typeclass, @wipe, @lock, @examine,
@find, @scripts, @objects, @teleport, @tag, @spawn.

Come per cthulhu_building.py: i NOMI dei comandi (le chiavi digitate dal
builder, es. "set", "examine", "spawn") restano quelli originali di Evennia
- sono strumenti da sviluppatore, non contenuto rivolto al giocatore comune,
e mantenerli identici all'inglese standard di Evennia evita ambiguita' nella
documentazione ufficiale. Cio' che viene tradotto sono i docstring (mostrati
da `help <comando>`) e tutti i messaggi che il comando stampa al chiamante.

Riusiamo `ObjManipCommand` di Evennia cosi' com'e' (parsing puro, nessuna
stringa rivolta al giocatore).

NOTA - LACUNA VOLUTAMENTE NON RISOLTA QUI: @spawn con gli switch
/olc, /edit, /menu delega all'intero sistema di menu OLC
(evennia.prototypes.menus.start_olc) e /search, /list, /show delegano a
funzioni di formattazione in evennia.prototypes.prototypes
(list_prototypes, prototype_to_str) e evennia.prototypes.spawner
(format_diff). Sono sottosistemi enormi e a se stanti, con la propria
interfaccia EvMenu multi-schermata: tradurli esula dallo scopo di questo
file (localizzare i comandi in building.py) e viene rimandato a un
intervento dedicato futuro, se il crafting via prototype verra' davvero
usato nel gioco.
"""

import re
import typing

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Max, Min, Q

import evennia
from evennia import InterruptCommand
from evennia.commands.cmdhandler import generate_cmdset_providers, get_and_merge_cmdsets
from evennia.commands.default.building import ObjManipCommand
from evennia.locks.lockhandler import LockException
from evennia.objects.models import ObjectDB
from evennia.prototypes import menus as olc_menus
from evennia.prototypes import prototypes as protlib
from evennia.prototypes import spawner
from evennia.scripts.models import ScriptDB
from evennia.utils import create, funcparser, logger, search, utils
from evennia.utils.ansi import raw as ansi_raw
from evennia.utils.dbserialize import deserialize
from evennia.utils.eveditor import EvEditor
from evennia.utils.evmore import EvMore
from evennia.utils.evtable import EvTable
from evennia.utils.utils import (
    class_from_module,
    crop,
    dbref,
    display_len,
    format_grid,
    get_all_typeclasses,
    inherits_from,
    interactive,
    list_to_string,
    variable_from_module,
)

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)

_FUNCPARSER = None
_ATTRFUNCPARSER = None

from ast import literal_eval as _LITERAL_EVAL  # noqa

LIST_APPEND_CHAR = "+"

CHAR_TYPECLASS = settings.BASE_CHARACTER_TYPECLASS
ROOM_TYPECLASS = settings.BASE_ROOM_TYPECLASS
EXIT_TYPECLASS = settings.BASE_EXIT_TYPECLASS
_DEFAULT_WIDTH = settings.CLIENT_DEFAULT_WIDTH


def _convert_from_string(cmd, strobj):
    """Converte una stringa nel suo equivalente tipo Python (int, list, dict...)."""
    try:
        return _LITERAL_EVAL(strobj)
    except (SyntaxError, ValueError):
        strobj = utils.to_str(strobj)
        string = (
            f'|RNota: il valore "|r{strobj}|R" e\' stato convertito in stringa. '
            "Assicurati che sia accettabile."
        )
        cmd.caller.msg(string)
        return strobj
    except Exception as err:
        string = f"|RErrore sconosciuto nella valutazione dell'attributo: {err}"
        return string


class CmdSetObjAlias(COMMAND_DEFAULT_CLASS):
    """
    imposta alias permanenti per un oggetto

    Uso:
      alias <obj> [= [alias[,alias,alias,...]]]
      alias <obj> =
      alias/category <obj> = [alias[,alias,...]:<categoria>
      alias/delete <obj> = <alias>

    Switch:
      category - richiede di terminare l'input con :categoria, per
        salvare gli alias indicati con quella categoria.
      delete - elimina tutte le occorrenze dell'alias indicato,
        a prescindere dalla categoria

    Assegna alias a un oggetto in modo che possa essere indicato con piu'
    di un nome. Assegna vuoto per rimuovere tutti gli alias dall'oggetto.
    Se si assegna una categoria, tutti gli alias forniti useranno quella
    categoria.

    Nota bene: questo non e' la stessa cosa degli alias personali creati
    con il comando 'nick'! Gli alias impostati con alias modificano
    l'oggetto stesso, rendendoli utilizzabili da chiunque.
    """

    key = "@alias"
    aliases = "setobjalias"
    switch_options = ("category", "delete")
    locks = "cmd:perm(setobjalias) or perm(Builder)"
    help_category = "Costruzione"

    method_type = "cmd_create"

    def func(self):
        """Imposta gli alias."""

        caller = self.caller

        if not self.lhs:
            string = "Uso: alias <obj> [= [alias[,alias ...]]]"
            self.msg(string)
            return
        objname = self.lhs

        obj = caller.search(objname)
        if not obj:
            return
        if self.rhs is None and "delete" not in self.switches:
            aliases = obj.aliases.all(return_key_and_category=True)
            if aliases:
                caller.msg(
                    "Alias per %s: %s"
                    % (
                        obj.get_display_name(caller),
                        ", ".join(
                            "'%s'%s"
                            % (alias, "" if category is None else "[categoria:'%s']" % category)
                            for (alias, category) in aliases
                        ),
                    )
                )
            else:
                caller.msg(f"Non esistono alias per '{obj.get_display_name(caller)}'.")
            return

        if not (obj.access(caller, "control") or obj.access(caller, "edit")):
            caller.msg("Non hai il permesso di farlo.")
            return

        if not self.rhs:
            old_aliases = obj.aliases.all()
            if old_aliases:
                caller.msg(
                    "Alias rimossi da %s: %s"
                    % (obj.get_display_name(caller), ", ".join(old_aliases))
                )
                obj.aliases.clear()
            else:
                caller.msg("Nessun alias da rimuovere.")
            return

        if "delete" in self.switches:
            existed = False
            for key, category in obj.aliases.all(return_key_and_category=True):
                if key == self.rhs:
                    obj.aliases.remove(key=self.rhs, category=category)
                    existed = True
            if existed:
                caller.msg("Alias '%s' eliminato da %s." % (self.rhs, obj.get_display_name(caller)))
            else:
                caller.msg("%s non ha l'alias '%s'." % (obj.get_display_name(caller), self.rhs))
            return

        category = None
        if "category" in self.switches:
            if ":" in self.rhs:
                rhs, category = self.rhs.rsplit(":", 1)
                category = category.strip()
            else:
                caller.msg(
                    "Se usi lo switch /category, la categoria va indicata "
                    "come :categoria alla fine."
                )
        else:
            rhs = self.rhs

        old_aliases = obj.aliases.get(category=category, return_list=True)
        new_aliases = [alias.strip().lower() for alias in rhs.split(",") if alias.strip()]

        old_aliases.extend(new_aliases)
        aliases = list(set(old_aliases))

        obj.aliases.add(aliases, category=category)

        obj.at_cmdset_get(force_init=True)

        caller.msg(
            "Alias di '%s' impostati su '%s'%s."
            % (
                obj.get_display_name(caller),
                str(obj.aliases),
                " (categoria: '%s')" % category if category else "",
            )
        )


class CmdCopy(ObjManipCommand):
    """
    copia un oggetto e le sue proprieta'

    Uso:
      copy <oggetto originale> [= <nuovo_nome>][;alias;alias..]
      [:<nuova_posizione>] [,<nuovo_nome2> ...]

    Crea una o piu' copie di un oggetto. Se non specifichi bersagli,
    verra' creata una copia esatta dell'originale chiamata *_copy.
    """

    key = "@copy"
    locks = "cmd:perm(copy) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        """Usa ObjManipCommand.parse()"""

        caller = self.caller
        args = self.args
        if not args:
            caller.msg(
                "Uso: copy <obj> [=<nuovo_nome>[;alias;alias..]]"
                "[:<nuova_posizione>] [, <nuovo_nome2>...]"
            )
            return

        if not self.rhs:
            from_obj_name = self.args
            from_obj = caller.search(from_obj_name)
            if not from_obj:
                return
            to_obj_name = "%s_copy" % from_obj_name
            to_obj_aliases = [
                (f"{alias}_copy", category)
                for alias, category in from_obj.aliases.all(return_key_and_category=True)
            ]
            copiedobj = ObjectDB.objects.copy_object(
                from_obj, new_key=to_obj_name, new_aliases=to_obj_aliases
            )
            if copiedobj:
                string = "Creata una copia identica di %s, chiamata '%s'." % (
                    from_obj_name,
                    to_obj_name,
                )
            else:
                string = "C'e' stato un errore copiando %s."
        else:
            from_obj_name = self.lhs_objs[0]["name"]
            from_obj = caller.search(from_obj_name)
            if not from_obj:
                return
            for objdef in self.rhs_objs:
                to_obj_name = objdef["name"]
                to_obj_aliases = objdef["aliases"]
                to_obj_location = objdef["option"]
                if to_obj_location:
                    to_obj_location = caller.search(to_obj_location, global_search=True)
                    if not to_obj_location:
                        return

                copiedobj = ObjectDB.objects.copy_object(
                    from_obj,
                    new_key=to_obj_name,
                    new_location=to_obj_location,
                    new_aliases=to_obj_aliases,
                )
                if copiedobj:
                    string = (
                        f"Copiato {from_obj_name} su '{to_obj_name}' (alias: {to_obj_aliases})."
                    )
                else:
                    string = f"C'e' stato un errore copiando {from_obj_name} su '{to_obj_name}'."
        caller.msg(string)


class CmdCpAttr(ObjManipCommand):
    """
    copia attributi tra oggetti

    Uso:
      cpattr[/switch] <obj>/<attr> = <obj1>/<attr1> [,<obj2>/<attr2>,<obj3>/<attr3>,...]
      cpattr[/switch] <obj>/<attr> = <obj1> [,<obj2>,<obj3>,...]
      cpattr[/switch] <attr>[:categoria] = <obj1>/<attr1>[:categoria] [,<obj2>/<attr2>,<obj3>/<attr3>,...]
      cpattr[/switch] <attr> = <obj1>[,<obj2>,<obj3>,...]

    Switch:
      move - elimina l'attributo dall'oggetto sorgente dopo la copia.

    Esempio:
      cpattr coolness = Anna/chillout, Anna/nicety, Tom/nicety
      ->
      copia l'attributo coolness (definito su di te) in attributi su
      Anna e Tom.

      cpattr box/width:dimension = tube/width:dimension
      ->
      copia l'attributo width di box nella categoria dimension, come
      attributo width di tube nella stessa categoria.

    Copia l'attributo di un oggetto in uno o piu' attributi su un altro
    oggetto. Se non fornisci un oggetto sorgente, viene usato te stesso.
    """

    key = "@cpattr"
    switch_options = ("move",)
    locks = "cmd:perm(cpattr) or perm(Builder)"
    help_category = "Costruzione"

    def check_from_attr(self, obj, attr, category=None, clear=False):
        """Punto di estensione per sottoclassi: verifica il permesso di copiare l'attributo."""
        return True

    def check_to_attr(self, obj, attr, category=None):
        """Punto di estensione per sottoclassi: verifica il permesso di scrivere l'attributo."""
        return True

    def check_has_attr(self, obj, attr, category=None):
        """Verifica che l'oggetto abbia l'attributo richiesto."""
        if not obj.attributes.has(attr, category=category):
            self.msg(
                f"{obj.name} non ha un attributo {attr}{f'[{category}]' if category else ''}."
            )
            return False
        return True

    def get_attr(self, obj, attr, category=None):
        """Recupera l'attributo dall'oggetto."""
        return obj.attributes.get(attr, category=category)

    def func(self):
        """Esegue la copia."""
        caller = self.caller

        if not self.rhs:
            string = """Uso:
            cpattr[/switch] <obj>/<attr>[:categoria] = <obj1>/<attr1> [,<obj2>/<attr2>,<obj3>/<attr3>,...]
            cpattr[/switch] <obj>/<attr> = <obj1> [,<obj2>,<obj3>,...]
            cpattr[/switch] <attr> = <obj1>/<attr1> [,<obj2>/<attr2>,<obj3>/<attr3>,...]
            cpattr[/switch] <attr> = <obj1>[,<obj2>,<obj3>,...]"""
            caller.msg(string)
            return

        lhs_objattr = self.lhs_objattr
        to_objs = self.rhs_objattr
        from_obj_name = lhs_objattr[0]["name"]
        from_obj_attrs = lhs_objattr[0]["attrs"]
        from_obj_category = lhs_objattr[0]["category"]
        from_obj_category_str = f"[{from_obj_category}]" if from_obj_category else ""

        if not from_obj_attrs:
            from_obj_attrs = [from_obj_name]
            from_obj = self.caller
        else:
            from_obj = caller.search(from_obj_name)
        if not from_obj or not to_objs:
            caller.msg("Devi fornire sia l'oggetto sorgente che i bersagli.")
            return
        if "move" in self.switches:
            clear = True
        else:
            clear = False
        if not self.check_from_attr(
            from_obj, from_obj_attrs[0], clear=clear, category=from_obj_category
        ):
            return

        for attr in from_obj_attrs:
            if not self.check_has_attr(from_obj, attr, category=from_obj_category):
                return

        if (len(from_obj_attrs) != len(set(from_obj_attrs))) and clear:
            self.msg("|RNon puoi avere nomi sorgente duplicati durante uno spostamento!")
            return

        result = []
        for to_obj in to_objs:
            to_obj_name = to_obj["name"]
            to_obj_attrs = to_obj["attrs"]
            to_obj_category = to_obj.get("category")
            to_obj_category_str = f"[{to_obj_category}]" if to_obj_category else ""
            to_obj = caller.search(to_obj_name)
            if not to_obj:
                result.append(f"\nImpossibile trovare l'oggetto '{to_obj_name}'")
                continue
            for inum, from_attr in enumerate(from_obj_attrs):
                try:
                    to_attr = to_obj_attrs[inum]
                except IndexError:
                    to_attr = from_attr
                if not self.check_to_attr(to_obj, to_attr, to_obj_category):
                    continue
                value = self.get_attr(from_obj, from_attr, from_obj_category)
                to_obj.attributes.add(to_attr, value, category=to_obj_category)
                if clear and not (from_obj == to_obj and from_attr == to_attr):
                    from_obj.attributes.remove(from_attr, category=from_obj_category)
                    result.append(
                        f"\nSpostato {from_obj.name}.{from_attr}{from_obj_category_str} -> {to_obj_name}.{to_attr}{to_obj_category_str}. (valore:"
                        f" {repr(value)})"
                    )
                else:
                    result.append(
                        f"\nCopiato {from_obj.name}.{from_attr}{from_obj_category_str} -> {to_obj.name}.{to_attr}{to_obj_category_str}. (valore:"
                        f" {repr(value)})"
                    )
        caller.msg("".join(result))


class CmdMvAttr(ObjManipCommand):
    """
    sposta attributi tra oggetti

    Uso:
      mvattr[/switch] <obj>/<attr> = <obj1>/<attr1> [,<obj2>/<attr2>,<obj3>/<attr3>,...]
      mvattr[/switch] <obj>/<attr> = <obj1> [,<obj2>,<obj3>,...]
      mvattr[/switch] <attr> = <obj1>/<attr1> [,<obj2>/<attr2>,<obj3>/<attr3>,...]
      mvattr[/switch] <attr> = <obj1>[,<obj2>,<obj3>,...]

    Switch:
      copy - non elimina l'originale dopo lo spostamento.

    Sposta un attributo da un oggetto a uno o piu' attributi su un altro
    oggetto. Se non fornisci un oggetto sorgente, viene usato te stesso.
    """

    key = "@mvattr"
    switch_options = ("copy",)
    locks = "cmd:perm(mvattr) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        """Esegue lo spostamento."""
        if not self.rhs:
            string = """Uso:
      mvattr[/switch] <obj>/<attr> = <obj1>/<attr1> [,<obj2>/<attr2>,<obj3>/<attr3>,...]
      mvattr[/switch] <obj>/<attr> = <obj1> [,<obj2>,<obj3>,...]
      mvattr[/switch] <attr> = <obj1>/<attr1> [,<obj2>/<attr2>,<obj3>/<attr3>,...]
      mvattr[/switch] <attr> = <obj1>[,<obj2>,<obj3>,...]"""
            self.msg(string)
            return

        if "copy" in self.switches:
            self.execute_cmd("cpattr %s" % self.args)
        else:
            self.execute_cmd("cpattr/move %s" % self.args)


class CmdSetAttribute(ObjManipCommand):
    """
    imposta un attributo su un oggetto o un account

    Uso:
      set[/switch] <obj>/<attr>[:categoria] = <valore>
      set[/switch] <obj>/<attr>[:categoria] =                  # elimina l'attributo
      set[/switch] <obj>/<attr>[:categoria]                    # mostra l'attributo
      set[/switch] *<account>/<attr>[:categoria] = <valore>

    Switch:
        edit: apre l'editor di riga (solo valori stringa)
        script: se stai impostando un attributo su uno script
        channel: se stai impostando un attributo su un canale
        account: se stai impostando un attributo su un account
        room: imposta un attributo su una stanza (ricerca globale)
        exit: imposta un attributo su un'uscita (ricerca globale)
        char: imposta un attributo su un personaggio (ricerca globale)
        character: alias di char, come sopra.

    Esempio:
        set self/foo = "bar"
        set/delete self/foo
        set self/foo = $dbref(#53)

    Imposta attributi sugli oggetti. Il secondo esempio sopra elimina un
    attributo precedentemente impostato, mentre il terzo mostra il
    valore attuale dell'attributo (se esiste). L'ultimo (con l'asterisco)
    e' una scorciatoia per operare su un Account invece che su un Object.

    Se vuoi che <valore> sia un oggetto, usa $dbref(#dbref) o
    $search(chiave) per assegnarlo. Devi avere accesso control o edit
    sull'oggetto a cui lo stai aggiungendo.

    I dati piu' comuni da salvare con questo comando sono stringhe e
    numeri. Puoi pero' anche impostare strutture Python primitive come
    liste, dizionari e tuple sugli oggetti (puo' essere importante per il
    funzionamento di certi oggetti personalizzati). Questo viene
    indicato facendo iniziare il valore con uno tra |c'|n, |c"|n, |c(|n,
    |c[|n o |c{ |n.

    Una volta salvata una struttura Python primitiva come sopra, puoi
    includere |c[<chiave>]|n in <attr> per riferirti a valori annidati
    in una lista o dizionario.

    Ricorda che se usi strutture Python in questo modo devi scrivere una
    sintassi Python corretta - in particolare devi mettere le virgolette
    attorno alle stringhe dentro liste e dizionari.
    """

    key = "@set"
    locks = "cmd:perm(set) or perm(Builder)"
    help_category = "Costruzione"
    nested_re = re.compile(r"\[.*?\]")
    not_found = object()

    def check_obj(self, obj):
        """Punto di estensione per sottoclassi: restrizioni su quali oggetti sono modificabili."""
        return True

    def check_attr(self, obj, attr_name, category):
        """Punto di estensione per sottoclassi: restrizioni su quali attributi sono modificabili."""
        return attr_name

    def split_nested_attr(self, attr):
        """
        Genera tuple (possibile nome attributo, chiavi annidate su quell'attributo).
        """
        quotes = "\"'"

        def clean_key(val):
            val = val.strip("[]")
            if val[0] in quotes:
                return val.strip(quotes)
            if val[0] == LIST_APPEND_CHAR:
                return val
            try:
                return int(val)
            except ValueError:
                return val

        parts = self.nested_re.findall(attr)

        base_attr = ""
        if parts:
            base_attr = attr[: attr.find(parts[0])]
        for index, part in enumerate(parts):
            yield (base_attr, [clean_key(p) for p in parts[index:]])
            base_attr += part
        yield (attr, [])

    def do_nested_lookup(self, value, *keys):
        result = value
        for key in keys:
            try:
                result = result.__getitem__(key)
            except (IndexError, KeyError, TypeError):
                return self.not_found
        return result

    def view_attr(self, obj, attr, category):
        """Cerca il valore di un attributo e restituisce una stringa che lo mostra."""
        nested = False
        for key, nested_keys in self.split_nested_attr(attr):
            nested = True
            if obj.attributes.has(key, category):
                if nested_keys:
                    val = obj.attributes.get(key, category=category)
                    deep = self.do_nested_lookup(val, *nested_keys[:-1])
                    if deep is not self.not_found:
                        try:
                            val = deep[nested_keys[-1]]
                        except (IndexError, KeyError, TypeError):
                            continue
                        return f"\nAttributo {obj.name}/|w{attr}|n [categoria:{category}] = {val}"
                else:
                    val = obj.attributes.get(key, category=category)
                    if val:
                        return f"\nAttributo {obj.name}/|w{attr}|n [categoria:{category}] = {val}"
        error = f"\nL'attributo {obj.name}/|w{attr}|n [categoria:{category}] non esiste."
        if nested:
            error += " (tentata ricerca annidata)"
        return error

    def rm_attr(self, obj, attr, category):
        """Rimuove un attributo dall'oggetto, o una struttura annidata, e riporta l'esito."""
        nested = False
        for key, nested_keys in self.split_nested_attr(attr):
            nested = True
            if obj.attributes.has(key, category):
                if nested_keys:
                    del_key = nested_keys[-1]
                    val = obj.attributes.get(key, category=category)
                    deep = self.do_nested_lookup(val, *nested_keys[:-1])
                    if deep is not self.not_found:
                        try:
                            del deep[del_key]
                        except (IndexError, KeyError, TypeError):
                            continue
                    return f"\nEliminato l'attributo {obj.name}/|w{attr}|n [categoria:{category}]."
                else:
                    exists = obj.attributes.has(key, category)
                    if exists:
                        obj.attributes.remove(attr, category=category)
                        return f"\nEliminato l'attributo {obj.name}/|w{attr}|n [categoria:{category}]."
                    else:
                        return (
                            f"\nNessun attributo {obj.name}/|w{attr}|n [categoria: {category}] "
                            "trovato da eliminare."
                        )
        error = f"\nNessun attributo {obj.name}/|w{attr}|n [categoria: {category}] trovato da eliminare."
        if nested:
            error += " (tentata ricerca annidata)"
        return error

    def set_attr(self, obj, attr, value, category):
        done = False
        for key, nested_keys in self.split_nested_attr(attr):
            if obj.attributes.has(key, category) and nested_keys:
                acc_key = nested_keys[-1]
                lookup_value = obj.attributes.get(key, category)
                deep = self.do_nested_lookup(lookup_value, *nested_keys[:-1])
                if deep is not self.not_found:
                    if isinstance(acc_key, str) and acc_key[0] == LIST_APPEND_CHAR:
                        try:
                            if len(acc_key) > 1:
                                where = int(acc_key[1:])
                                deep.insert(where, value)
                            else:
                                deep.append(value)
                        except (ValueError, AttributeError):
                            pass
                        else:
                            value = lookup_value
                            attr = key
                            done = True
                            break

                    try:
                        deep[acc_key] = value
                    except TypeError as err:
                        return f"\n{err} - {deep}"

                    value = lookup_value
                    attr = key
                    done = True
                    break

        verb = "Modificato" if obj.attributes.has(attr) else "Creato"
        try:
            if not done:
                obj.attributes.add(attr, value, category)
            return f"\n{verb} l'attributo {obj.name}/|w{attr}|n [categoria:{category}] = {value}"
        except SyntaxError:
            return (
                "\n|RErrore critico di sintassi Python nel tuo valore. Sono "
                "ammesse solo strutture Python primitive.\nDevi anche "
                "usare una sintassi Python corretta. Ricorda in "
                "particolare di mettere le virgolette attorno a tutte le "
                "stringhe dentro liste e dizionari.|n"
            )

    @interactive
    def edit_handler(self, obj, attr, caller):
        """Attiva l'editor di riga."""

        def load(caller):
            try:
                old_value = obj.attributes.get(attr, raise_exception=True)
            except AttributeError:
                old_value = ""
            return str(old_value)

        def save(caller, buf):
            obj.attributes.add(attr, buf)
            caller.msg(f"Attributo {attr} salvato.")

        try:
            old_value = obj.attributes.get(attr, raise_exception=True)
            if not isinstance(old_value, str):
                answer = yield (
                    f"|rAttenzione: l'attributo |w{attr}|r e' di tipo |w{type(old_value).__name__}|r. "
                    "\nPer continuare a modificarlo, deve essere convertito (e salvato) come "
                    "stringa. Continuare? [S]/N?"
                )
                if answer.lower() in ("n", "no"):
                    self.msg("Modifica annullata.")
                    return
        except AttributeError:
            pass

        EvEditor(self.caller, load, save, key=f"{obj}/{attr}")

    def search_for_obj(self, objname):
        """Cerca un oggetto (o account/script/canale a seconda degli switch) che corrisponda a objname."""
        from evennia.utils.utils import variable_from_module

        _AT_SEARCH_RESULT = variable_from_module(*settings.SEARCH_AT_RESULT.rsplit(".", 1))
        caller = self.caller
        if objname.startswith("*") or "account" in self.switches:
            found_obj = caller.search_account(objname.lstrip("*"))
        elif "script" in self.switches:
            found_obj = _AT_SEARCH_RESULT(search.search_script(objname), caller)
        elif "channel" in self.switches:
            found_obj = _AT_SEARCH_RESULT(search.search_channel(objname), caller)
        else:
            global_search = True
            if "char" in self.switches or "character" in self.switches:
                typeclass = settings.BASE_CHARACTER_TYPECLASS
            elif "room" in self.switches:
                typeclass = settings.BASE_ROOM_TYPECLASS
            elif "exit" in self.switches:
                typeclass = settings.BASE_EXIT_TYPECLASS
            else:
                global_search = False
                typeclass = None
            found_obj = caller.search(objname, global_search=global_search, typeclass=typeclass)
        return found_obj

    def func(self):
        """Implementa l'impostazione dell'attributo - una forma limitata di py."""

        caller = self.caller
        if not self.args:
            caller.msg("Uso: set obj/attr[:categoria] = valore. Usa un valore vuoto per eliminare.")
            return

        value = self.rhs
        objname = self.lhs_objattr[0]["name"]
        attrs = self.lhs_objattr[0]["attrs"]
        category = self.lhs_objs[0].get("option")

        obj = self.search_for_obj(objname)
        if not obj:
            return

        if not self.check_obj(obj):
            return

        result = []
        if "edit" in self.switches:
            if not (obj.access(self.caller, "control") or obj.access(self.caller, "edit")):
                caller.msg(f"Non hai il permesso di modificare {obj.key}.")
                return

            if len(attrs) > 1:
                caller.msg("L'editor di riga puo' essere usato su un solo attributo alla volta.")
                return
            if not attrs:
                caller.msg(
                    "Usa `set/edit <nomeoggetto>/<attr>` per definire l'attributo da modificare.\n"
                    "Per modificare la descrizione della stanza attuale, usa `set/edit "
                    "here/desc` (oppure usa il comando `desc`)."
                )
                return
            self.edit_handler(obj, attrs[0], caller)
            return
        if not value:
            if self.rhs is None:
                if not attrs:
                    attrs = [
                        attr.key
                        for attr in obj.attributes.get(
                            category=None, return_obj=True, return_list=True
                        )
                    ]
                for attr in attrs:
                    if not self.check_attr(obj, attr, category):
                        continue
                    result.append(self.view_attr(obj, attr, category))
            else:
                if not (obj.access(self.caller, "control") or obj.access(self.caller, "edit")):
                    caller.msg(f"Non hai il permesso di modificare {obj.key}.")
                    return
                for attr in attrs:
                    if not self.check_attr(obj, attr, category):
                        continue
                    result.append(self.rm_attr(obj, attr, category))
        else:
            global _ATTRFUNCPARSER
            if not _ATTRFUNCPARSER:
                _ATTRFUNCPARSER = funcparser.FuncParser(
                    {
                        "dbref": funcparser.funcparser_callable_search,
                        "search": funcparser.funcparser_callable_search,
                    }
                )

            if not (obj.access(self.caller, "control") or obj.access(self.caller, "edit")):
                caller.msg(f"Non hai il permesso di modificare {obj.key}.")
                return
            for attr in attrs:
                if not self.check_attr(obj, attr, category):
                    continue
                parsed_value = _ATTRFUNCPARSER.parse(value, return_str=False, caller=caller)
                if hasattr(parsed_value, "access"):
                    if not (
                        parsed_value.access(caller, "control")
                        or parsed_value.access(self.caller, "edit")
                    ):
                        caller.msg(
                            f"Non hai il permesso di impostare l'oggetto con identificatore '{value}'."
                        )
                        continue
                    value = parsed_value
                else:
                    value = _convert_from_string(self, value)
                result.append(self.set_attr(obj, attr, value, category))
        if not result:
            caller.msg(
                "Nessun attributo valido trovato. Uso: set obj/attr[:categoria] = valore. Usa un "
                "valore vuoto per eliminare."
            )
        else:
            caller.msg("".join(result).strip("\n"))


class CmdTypeclass(COMMAND_DEFAULT_CLASS):
    """
    imposta o cambia la typeclass di un oggetto

    Uso:
      typeclass[/switch] <oggetto> [= percorso.typeclass]
      typeclass/prototype <oggetto> = chiave_prototipo

      typeclasses o typeclass/list/show [percorso.typeclass]
      swap - scorciatoia per usare gli switch /force/reset.
      update - scorciatoia per usare lo switch /force/reload.

    Switch:
      show, examine - mostra la typeclass attuale dell'oggetto (default)
            oppure, se dato un percorso di typeclass, mostra il
            docstring di quella typeclass.
      update - esegue di nuovo *solo* at_object_creation su questo
              oggetto: lock o altre proprieta' impostate in seguito
              potrebbero rimanere.
      reset - ripulisce *tutti* gli attributi e le proprieta'
              dell'oggetto - rendendolo di fatto un oggetto nuovo di
              zecca. Questo azzera anche i cmdset!
      force - cambia la typeclass anche se l'oggetto ha gia' una
              typeclass con lo stesso nome.
      list - mostra le typeclass disponibili. Compaiono solo le
             typeclass effettivamente importate o usate da qualche
             parte nel codice (sono comunque disponibili se ne conosci
             il percorso)
      prototype - ripulisce e sovrascrive l'oggetto con il prototipo
               indicato - rendendolo di fatto un oggetto interamente
               nuovo.

    Esempio:
      type button = examples.red_button.RedButton
      type/prototype button=a red button

    Se il percorso della typeclass non e' indicato, si assume la
    typeclass attuale dell'oggetto.

    Mostra o imposta la typeclass di un oggetto. Se la imposti, gli hook
    di creazione della nuova typeclass verranno eseguiti sull'oggetto.
    Se hai proprieta' in conflitto con la vecchia classe, usa /reset. Per
    default sei protetto dal cambiare a una typeclass con lo stesso nome
    di quella che gia' hai - usa /force per aggirare questa protezione.

    La typeclass indicata deve essere identificata con la notazione a
    punti Python che punta al modulo e alla classe corretti. Se non
    viene fornita una typeclass (o ne viene fornita una sbagliata), o
    ci sono errori nel percorso o nella nuova typeclass, la vecchia
    typeclass viene mantenuta. Il modulo della typeclass viene cercato
    a partire dalla cartella predefinita delle typeclass, definita nelle
    impostazioni del server.
    """

    key = "@typeclass"
    aliases = ["@type", "@parent", "@swap", "@update", "@typeclasses"]
    switch_options = ("show", "examine", "update", "reset", "force", "list", "prototype")
    locks = "cmd:perm(typeclass) or perm(Builder)"
    help_category = "Costruzione"

    def _generic_search(self, query, typeclass_path):
        caller = self.caller
        if typeclass_path:
            try:
                new_typeclass = class_from_module(typeclass_path)
            except ImportError:
                return caller.search(query)

            dbclass = new_typeclass.__dbclass__

            if caller.__dbclass__ == dbclass:
                obj = caller.search(query)
                if not obj:
                    return
            elif self.account and self.account.__dbclass__ == dbclass:
                caller.msg(f"Provo a cercare {new_typeclass} con la query '{self.lhs}'.")
                obj = self.account.search(query)
                if not obj:
                    return
            elif hasattr(caller, "puppet") and caller.puppet.__dbclass__ == dbclass:
                caller.msg(f"Provo a cercare {new_typeclass} con la query '{self.lhs}'.")
                obj = caller.puppet.search(query)
                if not obj:
                    return
            else:
                caller.msg(f"Provo a cercare {new_typeclass} con la query '{self.lhs}'.")
                obj = new_typeclass.search(query)
                if not obj:
                    if isinstance(obj, list):
                        caller.msg(f"Impossibile trovare {new_typeclass} con la query '{self.lhs}'.")
                    return
        else:
            obj = caller.search(query)
            if not obj:
                return

        return obj

    def func(self):
        """Implementa il comando."""

        caller = self.caller

        if "list" in self.switches or self.cmdname in ("typeclasses", "@typeclasses"):
            tclasses = get_all_typeclasses()
            contribs = [key for key in sorted(tclasses) if key.startswith("evennia.contrib")] or [
                "<Nessuna caricata>"
            ]
            core = [
                key for key in sorted(tclasses) if key.startswith("evennia") and key not in contribs
            ] or ["<Nessuna caricata>"]
            game = [key for key in sorted(tclasses) if not key.startswith("evennia")] or [
                "<Nessuna caricata>"
            ]
            string = (
                "|wTypeclass principali|n\n"
                "    {core}\n"
                "|wTypeclass contrib caricate|n\n"
                "    {contrib}\n"
                "|wTypeclass della cartella di gioco|n\n"
                "    {game}"
            ).format(
                core="\n    ".join(core), contrib="\n    ".join(contribs), game="\n    ".join(game)
            )
            EvMore(caller, string, exit_on_lastpage=True)
            return

        if not self.args:
            caller.msg("Uso: %s <oggetto> [= typeclass]" % self.cmdstring)
            return

        if "show" in self.switches or "examine" in self.switches:
            oquery = self.lhs
            obj = caller.search(oquery, quiet=True)
            if not obj:
                tclasses = get_all_typeclasses()
                matches = [
                    (key, tclass) for key, tclass in tclasses.items() if key.endswith(oquery)
                ]
                nmatches = len(matches)
                if nmatches > 1:
                    caller.msg(
                        "Trovate piu' typeclass corrispondenti a {}:\n  {}".format(
                            oquery, "\n  ".join(tup[0] for tup in matches)
                        )
                    )
                elif not matches:
                    caller.msg(f"Nessun oggetto o percorso di typeclass trovato per '{oquery}'")
                else:
                    caller.msg(f"Docstring per la typeclass '{oquery}': \n{matches[0][1].__doc__}")
            else:
                obj = caller.search(oquery)
                if not obj:
                    return
                caller.msg(
                    f"La typeclass attuale di {obj.name} e'"
                    f" '{obj.__class__.__module__}.{obj.__class__.__name__}'"
                )
            return

        obj = self._generic_search(self.lhs, self.rhs)
        if not obj:
            return

        if not hasattr(obj, "__dbclass__"):
            string = "%s non e' un oggetto tipizzato." % obj.name
            caller.msg(string)
            return

        new_typeclass = self.rhs or obj.path

        prototype = None
        if "prototype" in self.switches:
            key = self.rhs
            prototype = protlib.search_prototype(key=key)
            if len(prototype) > 1:
                caller.msg(
                    "Piu' di una corrispondenza per {}:\n{}".format(
                        key, "\n".join(proto.get("prototype_key", "") for proto in prototype)
                    )
                )
                return
            elif prototype:
                prototype = prototype[0]
            else:
                caller.msg(f"Non e' stato trovato nessun prototipo '{key}'.")
                return
            new_typeclass = prototype["typeclass"]
            self.switches.append("force")

        if "show" in self.switches or "examine" in self.switches:
            caller.msg(f"La typeclass attuale di {obj.name} e' '{obj.__class__}'")
            return

        if self.cmdstring in ("swap", "@swap"):
            self.switches.append("force")
            self.switches.append("reset")
        elif self.cmdstring in ("update", "@update"):
            self.switches.append("force")
            self.switches.append("update")

        if not (obj.access(caller, "control") or obj.access(caller, "edit")):
            caller.msg("Non hai il permesso di farlo.")
            return

        if not hasattr(obj, "swap_typeclass"):
            caller.msg("Questo oggetto non puo' avere una typeclass!")
            return

        is_same = obj.is_typeclass(new_typeclass, exact=True)
        if is_same and "force" not in self.switches:
            string = (
                f"{obj.name} ha gia' la typeclass '{new_typeclass}'. Usa /force per forzare."
            )
        else:
            reset = "reset" in self.switches
            update = "update" in self.switches or not reset

            hooks = "at_object_creation" if update and not reset else "all"
            old_typeclass_path = obj.typeclass_path

            if reset:
                answer = yield (
                    "|yNota che questo riportera' l'oggetto allo stato predefinito della sua "
                    "typeclass, rimuovendo eventuali lock/permessi/attributi personalizzati "
                    "aggiunti da una chiamata esplicita a create_object. Usa `update` oppure "
                    "type/force per mantenere questi dati. Continuare [S]/N?|n"
                )
                if answer.upper() in ("N", "NO"):
                    caller.msg("Annullato.")
                    return

            if "prototype" in self.switches:
                diff, _ = spawner.prototype_diff_from_object(prototype, obj)
                txt = spawner.format_diff(diff)
                prompt = (
                    f"Applicare il prototipo '{prototype['key']}' su '{obj.name}' causera' le"
                    f" seguenti modifiche:\n{txt}\n"
                )
                if not reset:
                    prompt += (
                        "\n|yATTENZIONE:|n usa lo switch /reset per applicare il prototipo su "
                        "uno stato vuoto."
                    )
                prompt += "\nSei sicuro di voler applicare queste modifiche [si]/no?"
                answer = yield (prompt)
                if answer and answer.strip().lower() in ("no", "n"):
                    caller.msg("Annullato: nessuna modifica e' stata applicata.")
                    return

            obj.swap_typeclass(
                new_typeclass, clean_attributes=reset, clean_cmdsets=reset, run_start_hooks=hooks
            )

            if "prototype" in self.switches:
                modified = spawner.batch_update_objects_with_prototype(
                    prototype, objects=[obj], caller=self.caller
                )
                prototype_success = modified > 0
                if not prototype_success:
                    caller.msg(f"Impossibile applicare il prototipo {prototype['key']}.")

            if is_same:
                string = f"{obj.name} ha aggiornato la sua typeclass esistente ({obj.path}).\n"
            else:
                string = (
                    f"{obj.name} ha cambiato typeclass da {old_typeclass_path} a"
                    f" {obj.typeclass_path}.\n"
                )
            if update:
                string += "E' stato eseguito solo l'hook at_object_creation (modalita' update)."
            else:
                string += "Sono stati eseguiti tutti gli hook di creazione dell'oggetto."
            if reset:
                string += " Tutti i vecchi attributi sono stati eliminati prima dello scambio."
            else:
                string += (
                    " Gli attributi impostati prima dello scambio non sono stati rimossi\n(usa "
                    "`swap` o `type/reset` per ripulirli)."
                )
            if "prototype" in self.switches and prototype_success:
                string += (
                    f" Il prototipo '{prototype['key']}' e' stato applicato con successo "
                    "sull'oggetto."
                )

        caller.msg(string)


class CmdWipe(ObjManipCommand):
    """
    elimina tutti gli attributi di un oggetto

    Uso:
      wipe <oggetto>[/<attr>[/<attr>...]]

    Esempio:
      wipe box
      wipe box/colore

    Elimina tutti gli attributi di un oggetto, oppure solo quelli che
    corrispondono alla stringa di ricerca indicata.
    """

    key = "@wipe"
    locks = "cmd:perm(wipe) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        """inp e' il dizionario prodotto da ObjManipCommand.parse()"""

        caller = self.caller

        if not self.args:
            caller.msg("Uso: wipe <oggetto>[/<attr>/<attr>...]")
            return

        objname = self.lhs_objattr[0]["name"]
        attrs = self.lhs_objattr[0]["attrs"]

        obj = caller.search(objname)
        if not obj:
            return
        if not (obj.access(caller, "control") or obj.access(caller, "edit")):
            caller.msg("Non hai il permesso di farlo.")
            return
        if not attrs:
            obj.attributes.clear()
            string = f"Ripuliti tutti gli attributi di {obj.name}."
        else:
            for attrname in attrs:
                obj.attributes.remove(attrname)
            string = f"Ripuliti gli attributi {','.join(attrs)} di {obj.name}."
        caller.msg(string)


class CmdLock(ObjManipCommand):
    """
    assegna una definizione di lock a un oggetto

    Uso:
      lock <oggetto o *account>[ = <stringa_di_lock>]
      oppure
      lock[/switch] <oggetto o *account>/<tipo_accesso>

    Switch:
      del - elimina il tipo di accesso indicato
      view - mostra il lock associato al tipo di accesso indicato (default)

    Se non viene data nessuna stringa di lock, mostra tutti i lock
    sull'oggetto.

    La stringa di lock e' nella forma
       tipo_accesso:[NOT] func1(argomenti)[ AND|OR][ NOT] func2(argomenti) ...]
    dove func1, func2 ... sono funzioni di lock valide con o senza
    argomenti. I separatori non devono per forza essere maiuscoli.

    Per esempio:
       'get: id(25) or perm(Admin)'
    Il tipo di accesso 'get' viene controllato ad es. dal comando
    'get'. Un oggetto bloccato con questo esempio potra' essere
    raccolto solo da Admin o da un oggetto con id=25.

    Puoi aggiungere piu' tipi di accesso uno dopo l'altro separandoli
    con ';', cioe':
       'get:id(25); delete:perm(Builder)'
    """

    key = "@lock"
    aliases = ["@locks"]
    locks = "cmd: perm(locks) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        """Imposta il comando."""

        caller = self.caller
        if not self.args:
            string = "Uso: lock <oggetto>[ = <stringa_di_lock>] oppure lock[/switch] <oggetto>/<tipo_accesso>"
            caller.msg(string)
            return

        if "/" in self.lhs:
            objname, access_type = [p.strip() for p in self.lhs.split("/", 1)]
            obj = None
            if objname.startswith("*"):
                obj = caller.search_account(objname.lstrip("*"))
            if not obj:
                obj = caller.search(objname)
                if not obj:
                    return
            has_control_access = obj.access(caller, "control")
            if access_type == "control" and not has_control_access:
                caller.msg("Ti serve l'accesso 'control' per cambiare questo tipo di lock.")
                return

            if not (has_control_access or obj.access(caller, "edit")):
                caller.msg("Non hai il permesso di farlo.")
                return

            lockdef = obj.locks.get(access_type)

            if lockdef:
                if "del" in self.switches:
                    obj.locks.delete(access_type)
                    string = "lock %s eliminato" % lockdef
                else:
                    string = lockdef
            else:
                string = f"{obj} non ha nessun lock del tipo di accesso '{access_type}'."
            caller.msg(string)
            return

        if self.rhs:
            if self.switches:
                swi = ", ".join(self.switches)
                caller.msg(
                    f"Lo/gli switch |w{swi}|n non puo'/possono essere usati con "
                    "un'assegnazione di lock. Usa ad es. "
                    "|wlock/del nomeoggetto/tipolock|n."
                )
                return

            objname, lockdef = self.lhs, self.rhs
            obj = None
            if objname.startswith("*"):
                obj = caller.search_account(objname.lstrip("*"))
            if not obj:
                obj = caller.search(objname)
                if not obj:
                    return
            if not (obj.access(caller, "control") or obj.access(caller, "edit")):
                caller.msg("Non hai il permesso di farlo.")
                return
            ok = False
            lockdef = re.sub(r"\'|\"", "", lockdef)
            try:
                ok = obj.locks.add(lockdef)
            except LockException as e:
                caller.msg(str(e))
            if "cmd" in lockdef.lower() and inherits_from(
                obj, "evennia.objects.objects.DefaultExit"
            ):
                obj.at_init()
            if ok:
                caller.msg(f"Aggiunto il lock '{lockdef}' a {obj}.")
            return

        obj = None
        if self.lhs.startswith("*"):
            obj = caller.search_account(self.lhs.lstrip("*"))
        if not obj:
            obj = caller.search(self.lhs)
        if not obj:
            return
        if not (obj.access(caller, "control") or obj.access(caller, "edit")):
            caller.msg("Non hai il permesso di farlo.")
            return
        caller.msg("\n".join(obj.locks.all()))


class CmdExamine(ObjManipCommand):
    """
    ottieni informazioni dettagliate su un oggetto

    Uso:
      examine [<oggetto>[/nomeattributo]]
      examine [*<account>[/nomeattributo]]

    Switch:
      account - esamina un Account (equivale ad aggiungere *)
      object - esamina un Object (utile da fuori gioco/OOC)
      script - esamina uno Script
      channel - esamina un Canale

    Il comando examine mostra informazioni dettagliate su un oggetto e,
    opzionalmente, su un suo attributo specifico. Se l'oggetto non e'
    indicato, viene esaminata la posizione attuale.

    Anteponi un * alla stringa di ricerca per esaminare un account.
    """

    key = "@examine"
    aliases = ["@ex", "@exam"]
    locks = "cmd:perm(examine) or perm(Builder)"
    help_category = "Costruzione"
    arg_regex = r"(/\w+?(\s|$))|\s|$"
    switch_options = ["account", "object", "script", "channel"]

    object_type = "object"

    detail_color = "|c"
    header_color = "|w"
    quell_color = "|r"
    separator = "-"

    def msg(self, text):
        """Punto centrale per inviare messaggi al chiamante, taggati come 'examine'."""
        super().msg(text=(text, {"type": "examine"}))

    def format_key(self, obj):
        return f"{obj.name} ({obj.dbref})"

    def format_aliases(self, obj):
        if hasattr(obj, "aliases") and obj.aliases.all():
            return ", ".join(utils.make_iter(str(obj.aliases)))

    def format_typeclass(self, obj):
        if hasattr(obj, "typeclass_path"):
            return f"{obj.typename} ({obj.typeclass_path})"

    def format_sessions(self, obj):
        if hasattr(obj, "sessions"):
            sessions = obj.sessions.all()
            if sessions:
                return ", ".join(f"#{sess.sessid}" for sess in obj.sessions.all())

    def format_email(self, obj):
        if hasattr(obj, "email") and obj.email:
            return f"{self.detail_color}{obj.email}|n"

    def format_last_login(self, obj):
        if hasattr(obj, "last_login") and obj.last_login:
            return f"{self.detail_color}{obj.last_login}|n"

    def format_account_key(self, account):
        return f"{self.detail_color}{account.name}|n ({account.dbref})"

    def format_account_typeclass(self, account):
        return f"{account.typename} ({account.typeclass_path})"

    def format_account_permissions(self, account):
        perms = account.permissions.all()
        if account.is_superuser:
            perms = ["<Superuser>"]
        elif not perms:
            perms = ["<Nessuno>"]
        perms = ", ".join(perms)
        if account.attributes.has("_quell"):
            perms += f" {self.quell_color}(quelled)|n"
        return perms

    def format_location(self, obj):
        if hasattr(obj, "location") and obj.location:
            return f"{obj.location.key} (#{obj.location.id})"

    def format_home(self, obj):
        if hasattr(obj, "home") and obj.home:
            return f"{obj.home.key} (#{obj.home.id})"

    def format_destination(self, obj):
        if hasattr(obj, "destination") and obj.destination:
            return f"{obj.destination.key} (#{obj.destination.id})"

    def format_permissions(self, obj):
        perms = obj.permissions.all()
        if perms:
            perms_string = ", ".join(perms)
            if obj.is_superuser:
                perms_string += " <Superuser>"
            return perms_string

    def format_locks(self, obj):
        locks = str(obj.locks)
        if locks:
            return utils.fill("; ".join([lock for lock in locks.split(";")]), indent=2)
        return "Predefinito"

    def format_scripts(self, obj):
        if hasattr(obj, "scripts") and hasattr(obj.scripts, "all") and obj.scripts.all():
            return f"{obj.scripts}"

    def format_single_tag(self, tag):
        if tag.db_category:
            return f"{tag.db_key}[{tag.db_category}]"
        else:
            return f"{tag.db_key}"

    def format_tags(self, obj):
        if hasattr(obj, "tags"):
            tags = sorted(obj.tags.all(return_objs=True))
            if tags:
                formatted_tags = [self.format_single_tag(tag) for tag in tags]
                return utils.fill(", ".join(formatted_tags), indent=2)

    def format_single_cmdset_options(self, cmdset):
        def _truefalse(string, value):
            if value is None:
                return ""
            if value:
                return f"{string}: V"
            return f"{string}: F"

        txt = ", ".join(
            _truefalse(opt, getattr(cmdset, opt))
            for opt in ("no_exits", "no_objs", "no_channels", "duplicates")
            if getattr(cmdset, opt) is not None
        )
        return ", " + txt if txt else ""

    def format_single_cmdset(self, cmdset):
        options = self.format_single_cmdset_options(cmdset)
        return f"{cmdset.path} [{cmdset.key}] ({cmdset.mergetype}, priorita' {cmdset.priority}{options})"

    def format_stored_cmdsets(self, obj):
        if hasattr(obj, "cmdset"):
            stored_cmdset_strings = []
            stored_cmdsets = sorted(obj.cmdset.all(), key=lambda x: x.priority, reverse=True)
            for cmdset in stored_cmdsets:
                if cmdset.key != "_EMPTY_CMDSET":
                    stored_cmdset_strings.append(self.format_single_cmdset(cmdset))
            return "\n  " + "\n  ".join(stored_cmdset_strings)

    def format_merged_cmdsets(self, obj, current_cmdset):
        if not hasattr(obj, "cmdset"):
            return None

        all_cmdsets = [(cmdset.key, cmdset) for cmdset in current_cmdset.merged_from]
        if inherits_from(obj, evennia.DefaultObject) and obj.account:
            all_cmdsets.extend([(cmdset.key, cmdset) for cmdset in obj.account.cmdset.all()])
            if obj.sessions.count():
                all_cmdsets.extend(
                    [(cmdset.key, cmdset) for cmdset in obj.account.sessions.all()[0].cmdset.all()]
                )
        else:
            try:
                all_cmdsets.extend(
                    [
                        (cmdset.key, cmdset)
                        for cmdset in obj.get_session(obj.sessions.get()).cmdset.all()
                    ]
                )
            except (TypeError, AttributeError):
                pass
        all_cmdsets = [cmdset for cmdset in dict(all_cmdsets).values()]
        all_cmdsets.sort(key=lambda x: x.priority, reverse=True)

        merged_cmdset_strings = []
        for cmdset in all_cmdsets:
            if cmdset.key != "_EMPTY_CMDSET":
                merged_cmdset_strings.append(self.format_single_cmdset(cmdset))
        return "\n  " + "\n  ".join(merged_cmdset_strings)

    def format_current_cmds(self, obj, current_cmdset):
        current_commands = sorted([cmd.key for cmd in current_cmdset if cmd.access(obj, "cmd")])
        return "\n" + utils.fill(", ".join(current_commands), indent=2)

    def _get_attribute_value_type(self, attrvalue):
        typ = ""
        if not isinstance(attrvalue, str):
            try:
                name = attrvalue.__class__.__name__
            except AttributeError:
                try:
                    name = attrvalue.__name__
                except AttributeError:
                    name = attrvalue
            if str(name).startswith("_Saver"):
                try:
                    typ = str(type(deserialize(attrvalue)))
                except Exception:
                    typ = str(type(deserialize(attrvalue)))
            else:
                typ = str(type(attrvalue))
        return typ

    def format_single_attribute_detail(self, obj, attr):
        global _FUNCPARSER
        if not _FUNCPARSER:
            _FUNCPARSER = funcparser.FuncParser(settings.FUNCPARSER_OUTGOING_MESSAGES_MODULES)

        key, category, value = attr.db_key, attr.db_category, attr.value
        valuetype = ""
        if value is None and attr.strvalue is not None:
            value = attr.strvalue
            valuetype = " |B[strvalue]|n"
        typ = self._get_attribute_value_type(value)
        typ = f" |B[tipo:{typ}]|n{valuetype}" if typ else f"{valuetype}"
        value = utils.to_str(value)
        value = _FUNCPARSER.parse(ansi_raw(value), escape=True)
        return (
            f"Attributo {obj.name}/{self.header_color}{key}|n "
            f"[categoria={category}]{typ}:\n\n{value}"
        )

    def format_single_attribute(self, attr):
        global _FUNCPARSER
        if not _FUNCPARSER:
            _FUNCPARSER = funcparser.FuncParser(settings.FUNCPARSER_OUTGOING_MESSAGES_MODULES)

        key, category, value = attr.db_key, attr.db_category, attr.value
        valuetype = ""
        if value is None and attr.strvalue is not None:
            value = attr.strvalue
            valuetype = " |B[strvalue]|n"
        typ = self._get_attribute_value_type(value)
        typ = f" |B[tipo: {typ}]|n{valuetype}" if typ else f"{valuetype}"
        value = utils.to_str(value)
        value = _FUNCPARSER.parse(ansi_raw(value), escape=True)
        value = utils.crop(value)
        if category:
            return f"{self.header_color}{key}|n[{category}]={value}{typ}"
        else:
            return f"{self.header_color}{key}|n={value}{typ}"

    def format_attributes(self, obj):
        output = "\n  " + "\n  ".join(
            sorted(self.format_single_attribute(attr) for attr in obj.db_attributes.all())
        )
        if output.strip():
            return output

    def format_nattributes(self, obj):
        try:
            ndb_attr = obj.nattributes.all()
        except Exception:
            return

        if ndb_attr and ndb_attr[0]:
            return "\n  " + "\n  ".join(
                sorted(self.format_single_attribute(attr) for attr in ndb_attr)
            )

    def format_exits(self, obj):
        if hasattr(obj, "exits"):
            exits = ", ".join(f"{exit.name}({exit.dbref})" for exit in obj.exits)
            return exits if exits else None

    def format_chars(self, obj):
        if hasattr(obj, "contents"):
            chars = ", ".join(f"{obj.name}({obj.dbref})" for obj in obj.contents if obj.account)
            return chars if chars else None

    def format_things(self, obj):
        if hasattr(obj, "contents"):
            things = ", ".join(
                f"{obj.name}({obj.dbref})"
                for obj in obj.contents
                if not obj.account and not obj.destination
            )
            return things if things else None

    def format_script_desc(self, obj):
        if hasattr(obj, "db_desc") and obj.db_desc:
            return crop(obj.db_desc, 20)

    def format_script_is_persistent(self, obj):
        if hasattr(obj, "db_persistent"):
            return "V" if obj.db_persistent else "F"

    def format_script_timer_data(self, obj):
        if hasattr(obj, "db_interval") and obj.db_interval > 0:
            start_delay = "V" if obj.db_start_delay else "F"
            next_repeat = obj.time_until_next_repeat()
            active = "|gattivo|n" if obj.db_is_active and next_repeat else "|rinattivo|n"
            interval = obj.db_interval
            next_repeat = "N/D" if next_repeat is None else f"{next_repeat}s"
            repeats = ""
            if obj.db_repeats:
                remaining_repeats = obj.remaining_repeats()
                remaining_repeats = 0 if remaining_repeats is None else remaining_repeats
                repeats = f" - {remaining_repeats}/{obj.db_repeats} rimasti"
            return (
                f"{active} - intervallo: {interval}s "
                f"(prossimo: {next_repeat}{repeats}, ritardo iniziale: {start_delay})"
            )

    def format_channel_sub_totals(self, obj):
        if hasattr(obj, "db_account_subscriptions"):
            account_subs = obj.db_account_subscriptions.all()
            object_subs = obj.db_object_subscriptions.all()
            online = len(obj.subscriptions.online())
            ntotal = account_subs.count() + object_subs.count()
            return f"{ntotal} ({online} online)"

    def format_channel_account_subs(self, obj):
        if hasattr(obj, "db_account_subscriptions"):
            account_subs = obj.db_account_subscriptions.all()
            if account_subs:
                return "\n  " + "\n  ".join(
                    format_grid([sub.key for sub in account_subs], sep=" ", width=_DEFAULT_WIDTH)
                )

    def format_channel_object_subs(self, obj):
        if hasattr(obj, "db_object_subscriptions"):
            object_subs = obj.db_object_subscriptions.all()
            if object_subs:
                return "\n  " + "\n  ".join(
                    format_grid([sub.key for sub in object_subs], sep=" ", width=_DEFAULT_WIDTH)
                )

    def get_formatted_obj_data(self, obj, current_cmdset):
        """Chiama tutti gli altri metodi `format_*`."""
        objdata = {}
        objdata["Nome/chiave"] = self.format_key(obj)
        objdata["Alias"] = self.format_aliases(obj)
        objdata["Typeclass"] = self.format_typeclass(obj)
        objdata["Sessioni"] = self.format_sessions(obj)
        objdata["Email"] = self.format_email(obj)
        objdata["Ultimo accesso"] = self.format_last_login(obj)
        if inherits_from(obj, evennia.DefaultObject) and obj.has_account:
            objdata["Account"] = self.format_account_key(obj.account)
            objdata["  Typeclass account"] = self.format_account_typeclass(obj.account)
            objdata["  Permessi account"] = self.format_account_permissions(obj.account)
        objdata["Posizione"] = self.format_location(obj)
        objdata["Home"] = self.format_home(obj)
        objdata["Destinazione"] = self.format_destination(obj)
        objdata["Permessi"] = self.format_permissions(obj)
        objdata["Lock"] = self.format_locks(obj)
        if current_cmdset and not (
            len(obj.cmdset.all()) == 1 and obj.cmdset.current.key == "_EMPTY_CMDSET"
        ):
            objdata["Cmdset memorizzati"] = self.format_stored_cmdsets(obj)
            objdata["Cmdset uniti"] = self.format_merged_cmdsets(obj, current_cmdset)
            objdata[f"Comandi disponibili per {obj.key} (risultato dei Cmdset uniti)"] = (
                self.format_current_cmds(obj, current_cmdset)
            )
        if self.object_type == "script":
            objdata["Descrizione"] = self.format_script_desc(obj)
            objdata["Persistente"] = self.format_script_is_persistent(obj)
            objdata["Ripetizione script"] = self.format_script_timer_data(obj)
        objdata["Script"] = self.format_scripts(obj)
        objdata["Tag"] = self.format_tags(obj)
        objdata["Attributi persistenti"] = self.format_attributes(obj)
        objdata["Attributi non persistenti"] = self.format_nattributes(obj)
        objdata["Uscite"] = self.format_exits(obj)
        objdata["Personaggi"] = self.format_chars(obj)
        objdata["Contenuto"] = self.format_things(obj)
        if self.object_type == "channel":
            objdata["Totale iscrizioni"] = self.format_channel_sub_totals(obj)
            objdata["Iscrizioni account"] = self.format_channel_account_subs(obj)
            objdata["Iscrizioni oggetti"] = self.format_channel_object_subs(obj)

        return objdata

    def format_output(self, obj, current_cmdset):
        """Formatta la pagina completa restituita da examine."""
        objdata = self.get_formatted_obj_data(obj, current_cmdset)

        main_str = []
        max_width = -1
        for header, block in objdata.items():
            if block is not None:
                blockstr = f"{self.header_color}{header}|n: {block}"
                max_width = max(max_width, max(display_len(line) for line in blockstr.split("\n")))
                main_str.append(blockstr)
        main_str = "\n".join(main_str)

        max_width = max(0, min(self.client_width(), max_width))
        sep = self.separator * max_width

        return f"{sep}\n{main_str}\n{sep}"

    def _search_by_object_type(self, obj_name, objtype):
        """Instrada verso funzioni di ricerca diverse a seconda del tipo di oggetto esaminato."""
        obj = None

        if objtype == "object":
            obj = self.caller.search(obj_name)
        elif objtype == "account":
            try:
                obj = self.caller.search_account(obj_name.lstrip("*"))
            except AttributeError:
                obj = self.caller.search(
                    obj_name.lstrip("*"), search_object="object" in self.switches
                )
        else:
            obj = getattr(search, f"search_{objtype}")(obj_name)
            if not obj:
                self.msg(f"Nessun {objtype} trovato con chiave {obj_name}.")
                obj = None
            elif len(obj) > 1:
                err = "Trovati piu' {objtype} con chiave {obj_name}:\n{matches}"
                self.msg(
                    err.format(
                        obj_name=obj_name, matches=", ".join(f"{ob.key}(#{ob.id})" for ob in obj)
                    )
                )
                obj = None
            else:
                obj = obj[0]
        return obj

    def parse(self):
        super().parse()

        self.examine_objs = []

        if not self.args:
            if hasattr(self.caller, "location"):
                self.examine_objs.append((self.caller.location, None))
            else:
                self.msg("Devi fornire un bersaglio da esaminare.")
                raise InterruptCommand
        else:
            for objdef in self.lhs_objattr:
                obj = None
                obj_name = objdef["name"]
                obj_attrs = objdef["attrs"]

                object_type = "object"
                if (
                    utils.inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount")
                    or "account" in self.switches
                    or obj_name.startswith("*")
                ):
                    object_type = "account"
                elif "script" in self.switches:
                    object_type = "script"
                elif "channel" in self.switches:
                    object_type = "channel"

                self.object_type = object_type
                obj = self._search_by_object_type(obj_name, object_type)

                if obj:
                    self.examine_objs.append((obj, obj_attrs))

    def func(self):
        """Elabora il comando."""
        for obj, obj_attrs in self.examine_objs:

            if not obj.access(self.caller, "examine"):
                self.msg(self.caller.at_look(obj))
                continue

            if obj_attrs:
                attrs = [attr for attr in obj.db_attributes.all() if attr.db_key in obj_attrs]
                if not attrs:
                    self.msg(f"Nessun attributo trovato su {obj.name}.")
                else:
                    out_strings = []
                    for attr in attrs:
                        out_strings.append(self.format_single_attribute_detail(obj, attr))
                    out_str = "\n".join(out_strings)
                    max_width = max(display_len(line) for line in out_strings)
                    max_width = max(0, min(max_width, self.client_width()))
                    sep = self.separator * max_width
                    self.msg(f"{sep}\n{out_str}")
                return

            if self.object_type in ("object", "account"):
                session = None
                if obj.sessions.count():
                    mergemode = "session"
                    session = obj.sessions.get()[0]
                elif self.object_type == "account":
                    mergemode = "account"
                else:
                    mergemode = "object"

                account = None
                objct = None
                if self.object_type == "account":
                    account = obj
                else:
                    account = obj.account
                    objct = obj

                obj.cmdset.update()

                def _get_cmdset_callback(current_cmdset):
                    self.msg(self.format_output(obj, current_cmdset).strip())

                (
                    command_objects,
                    command_objects_list,
                    command_objects_list_error,
                    caller,
                    error_to,
                ) = generate_cmdset_providers(obj, session=session)

                get_and_merge_cmdsets(
                    obj, command_objects_list, mergemode, self.raw_string, error_to
                ).addCallback(_get_cmdset_callback)

            else:
                self.msg(self.format_output(obj, None).strip())


class CmdFind(COMMAND_DEFAULT_CLASS):
    """
    cerca oggetti nel database

    Uso:
      find[/switches] <nome o dbref o *account> [= dbrefmin[-dbrefmax]]
      locate - scorciatoia per usare lo switch /loc.

    Switch:
      room       - cerca solo stanze (location=None)
      exit       - cerca solo uscite (destination!=None)
      char       - cerca solo personaggi (BASE_CHARACTER_TYPECLASS)
      exact      - restituisce solo corrispondenze esatte.
      loc        - mostra la posizione dell'oggetto se esiste ed e' un
                   risultato unico
      startswith - cerca nomi che iniziano con la stringa, invece che
                   la contengono

    Cerca nel database un oggetto con un certo nome o #dbref esatto. Usa
    *nomeaccount per cercare un account. Gli switch permettono di
    limitare i risultati a certe entita' di gioco. Dbrefmin e dbrefmax
    limitano i risultati all'intervallo di dbref indicato, oppure sopra
    o sotto se ne viene dato solo uno.
    """

    key = "@find"
    aliases = ["@search", "@locate"]
    switch_options = ("room", "exit", "char", "exact", "loc", "startswith")
    locks = "cmd:perm(find) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        """Funzionalita' di ricerca."""
        caller = self.caller
        switches = self.switches

        if not self.args or (not self.lhs and not self.rhs):
            caller.msg("Uso: find <stringa> [= min [-max]]")
            return

        if "locate" in self.cmdstring:
            switches.append("loc")

        searchstring = self.lhs

        try:
            qs = ObjectDB.objects.values("id").aggregate(low=Min("id"), high=Max("id"))
            low, high = sorted(qs.values())
            if not (low and high):
                raise ValueError(
                    f"{self.__class__.__name__}: aggregazione min/max ID non riuscita;"
                    " ripiego su slicing del queryset."
                )
        except Exception as e:
            logger.log_trace(e)
            low, high = 1, ObjectDB.objects.all().order_by("-id").first().id

        if self.rhs:
            try:
                bounds = tuple(
                    sorted(dbref(x, False) for x in re.split(r"[-\s]+", self.rhs.strip()))
                )

                assert bounds
                assert None not in bounds

                low = bounds[0]
                if len(bounds) > 1:
                    high = bounds[-1]

            except AssertionError:
                caller.msg("Intervallo di dbref non valido (non e' un numero).")
                return
            except IndexError as e:
                logger.log_err(
                    f"{self.__class__.__name__}: errore analizzando i limiti superiore e "
                    "inferiore della query."
                )
                logger.log_trace(e)

        low = min(low, high)
        high = max(low, high)

        is_dbref = utils.dbref(searchstring)
        is_account = searchstring.startswith("*")

        restrictions = ""
        if self.switches:
            restrictions = ", %s" % ", ".join(self.switches)

        if is_dbref or is_account:
            if is_dbref:
                result = caller.search(searchstring, global_search=True, quiet=True)
                string = "|wCorrispondenza esatta di dbref|n(#%i-#%i%s):" % (low, high, restrictions)
            else:
                searchstring = searchstring.lstrip("*")
                result = caller.search_account(searchstring, quiet=True)
                string = "|wCorrispondenza|n(#%i-#%i%s):" % (low, high, restrictions)

            if "room" in switches:
                result = result if inherits_from(result, ROOM_TYPECLASS) else None
            if "exit" in switches:
                result = result if inherits_from(result, EXIT_TYPECLASS) else None
            if "char" in switches:
                result = result if inherits_from(result, CHAR_TYPECLASS) else None

            if not result:
                string += "\n   |RNessuna corrispondenza trovata.|n"
            elif not low <= int(result[0].id) <= high:
                string += f"\n   |RNessuna corrispondenza trovata per '{searchstring}' nell'intervallo di #dbref.|n"
            else:
                result = result[0]
                string += (
                    f"\n|g   {result.get_display_name(caller)}"
                    f"{result.get_extra_display_name_info(caller)} - {result.path}|n"
                )
                if "loc" in self.switches and not is_account and result.location:
                    string += (
                        f" (|wposizione|n: |g{result.location.get_display_name(caller)}"
                        f"{result.location.get_extra_display_name_info(caller)}|n)"
                    )
        else:
            if "exact" in switches:
                keyquery = Q(db_key__iexact=searchstring, id__gte=low, id__lte=high)
                aliasquery = Q(
                    db_tags__db_key__iexact=searchstring,
                    db_tags__db_tagtype__iexact="alias",
                    id__gte=low,
                    id__lte=high,
                )
            elif "startswith" in switches:
                keyquery = Q(db_key__istartswith=searchstring, id__gte=low, id__lte=high)
                aliasquery = Q(
                    db_tags__db_key__istartswith=searchstring,
                    db_tags__db_tagtype__iexact="alias",
                    id__gte=low,
                    id__lte=high,
                )
            else:
                keyquery = Q(db_key__icontains=searchstring, id__gte=low, id__lte=high)
                aliasquery = Q(
                    db_tags__db_key__icontains=searchstring,
                    db_tags__db_tagtype__iexact="alias",
                    id__gte=low,
                    id__lte=high,
                )

            result_qs = ObjectDB.objects.filter(keyquery | aliasquery).distinct()
            nresults = result_qs.count()

            results = result_qs.iterator()

            if any(x in switches for x in ("room", "exit", "char")):
                obj_ids = set()
                for obj in results:
                    if (
                        ("room" in switches and inherits_from(obj, ROOM_TYPECLASS))
                        or ("exit" in switches and inherits_from(obj, EXIT_TYPECLASS))
                        or ("char" in switches and inherits_from(obj, CHAR_TYPECLASS))
                    ):
                        obj_ids.add(obj.id)

                filtered_qs = result_qs.filter(id__in=obj_ids).distinct()
                nresults = filtered_qs.count()

                results = filtered_qs.iterator()

            if nresults:
                if nresults > 1:
                    header = f"{nresults} corrispondenze"
                else:
                    header = "Una corrispondenza"

                string = f"|w{header}|n(#{low}-#{high}{restrictions}):"
                res = None
                for res in results:
                    string += (
                        "\n  "
                        f" |g{res.get_display_name(caller)}"
                        f"{res.get_extra_display_name_info(caller)} -"
                        f" {res.path}|n"
                    )
                if (
                    "loc" in self.switches
                    and nresults == 1
                    and res
                    and getattr(res, "location", None)
                ):
                    string += (
                        " (|wposizione|n:"
                        f" |g{res.location.get_display_name(caller)}"
                        f"{res.get_extra_display_name_info(caller)}|n)"
                    )
            else:
                string = f"|wNessuna corrispondenza|n(#{low}-#{high}{restrictions}):"
                string += f"\n   |RNessuna corrispondenza trovata per '{searchstring}'|n"

        caller.msg(string.strip())


class ScriptEvMore(EvMore):
    """
    Elencare 1000+ Script puo' essere molto lento e dispendioso in
    memoria. Usiamo quindi questo figlio di EvMore che costruisce una
    EvTable solo per ogni pagina della lista.
    """

    def init_pages(self, scripts):
        """Prepara la paginazione della lista script."""
        script_pages = Paginator(scripts, max(1, int(self.height / 2)))
        super().init_pages(script_pages)

    def page_formatter(self, scripts):
        """Prende una pagina di script e ne formatta l'output in una EvTable."""

        if not scripts:
            return "<Nessuno script>"

        table = EvTable(
            "|wdbref|n",
            "|wobj|n",
            "|wchiave|n",
            "|wintervallo|n",
            "|wprossimo|n",
            "|wripet.|n",
            "|wtypeclass|n",
            "|wdesc|n",
            align="r",
            border="tablecols",
            width=self.width,
        )

        for script in scripts:
            nextrep = script.time_until_next_repeat()
            if nextrep is None:
                nextrep = script.db._paused_time
                nextrep = f"IN PAUSA {int(nextrep)}s" if nextrep else "--"
            else:
                nextrep = f"{nextrep}s"

            maxrepeat = script.repeats
            remaining = script.remaining_repeats() or 0
            if maxrepeat:
                rept = "%i/%i" % (maxrepeat - remaining, maxrepeat)
            else:
                rept = "-/-"

            table.add_row(
                f"#{script.id}",
                (
                    f"{script.obj.key}({script.obj.dbref})"
                    if (hasattr(script, "obj") and script.obj)
                    else "<Globale>"
                ),
                script.db_key,
                script.interval if script.interval > 0 else "--",
                nextrep,
                rept,
                script.typeclass_path.rsplit(".", 1)[-1],
                crop(script.desc, width=20),
            )

        return str(table)


class CmdScripts(COMMAND_DEFAULT_CLASS):
    """
    elenca e gestisce tutti gli script attivi. Permette anche di creare
    nuovi script globali.

    Uso:
      script[/switches] [script-#dbref, chiave, percorso.script]
      script[/start||stop] <obj> = [<percorso.script o chiave-script>]

    Switch:
      start  - avvia/riprende il timer di uno script esistente.
      stop   - ferma il timer di uno script esistente
      pause  - mette in pausa il timer di uno script
      delete - elimina lo script. Ferma anche il timer se necessario

    Esempi:
        script                             - elenca tutti gli script
        script chiave:foo.bar.Script       - crea un nuovo Script globale
                                             con typeclass e chiave 'chiave'
        script foo.bar.Script              - crea un nuovo Script globale
                                             con typeclass (chiave presa
                                             dalla typeclass o autogenerata)
        script/pause foo.bar.Script        - mette in pausa uno script globale
        script typeclass|nome|#dbref       - esamina uno script globale esistente
        script/delete #dbref[-#dbref]      - elimina script o intervallo per #dbref

        script mioobj =                    - elenca tutti gli script sull'oggetto
        script mioobj = foo.bar.Script     - crea e assegna uno script all'oggetto
        script/stop mioobj = nome|#dbref   - ferma lo script indicato sull'oggetto
        script/delete mioobj = nome|#dbref - elimina lo script indicato sull'oggetto
        script/delete mioobj =             - elimina TUTTI gli script sull'oggetto

    Se viene dato un `<obj>` come lato sinistro, questo crea e assegna
    un nuovo script a quell'oggetto. Senza `<obj>`, gestisce e ispeziona
    gli script globali.

    Se non vengono dati switch, il comando mostra solo tutti gli script
    attivi. L'argomento puo' essere un oggetto, nel qual caso verranno
    cercati tutti gli script definiti su di esso, oppure un nome di
    script o un #dbref. Per usare lo switch /stop serve un #dbref
    univoco dello script, poiche' intere classi di script spesso
    condividono lo stesso nome.
    """

    key = "@scripts"
    aliases = ["@script"]
    switch_options = ("start", "stop", "pause", "delete")
    locks = "cmd:perm(scripts) or perm(Builder)"
    help_category = "Sistema"

    excluded_typeclass_paths = ["evennia.prototypes.prototypes.DbPrototype"]

    switch_mapping = {
        "start": "|gAvviato|n",
        "stop": "|RFermato|n",
        "pause": "|yMesso in pausa|n",
        "delete": "|rEliminato|n",
    }
    hide_script_paths = ("evennia.prototypes.prototypes.DbPrototype",)

    def _search_script(self):

        if dbref(self.typeclass_query):
            scripts = ScriptDB.objects.get_all_scripts(self.typeclass_query)
            if scripts:
                return scripts
            self.caller.msg(f"Nessuno script trovato con dbref {self.typeclass_query}")
            raise InterruptCommand

        if self.key_query:
            return ScriptDB.objects.filter(
                db_key__iexact=self.key_query, db_typeclass_path__iendswith=self.typeclass_query
            ).exclude(db_typeclass_path__in=self.hide_script_paths)

        scripts = (
            ScriptDB.objects.filter(db_typeclass_path__iendswith=self.typeclass_query)
            .exclude(db_typeclass_path__in=self.hide_script_paths)
            .order_by("id")
        )
        if scripts:
            return scripts

        args = self.typeclass_query
        if "-" in args:
            val1, val2 = (dbref(part.strip()) for part in args.split("-", 1))
            if val1 and val2:
                scripts = (
                    ScriptDB.objects.filter(id__in=(range(val1, val2 + 1)))
                    .exclude(db_typeclass_path__in=self.hide_script_paths)
                    .order_by("id")
                )
                if scripts:
                    return scripts

    def parse(self):
        super().parse()

        if not self.args:
            return

        def _separate_key_typeclass(part):
            part1, *part2 = part.split(":", 1)
            return (part1, part2[0]) if part2 else (None, part1)

        if self.rhs:
            self.obj_query = self.lhs
            self.key_query, self.typeclass_query = _separate_key_typeclass(self.rhs)
        elif self.rhs is not None:
            self.obj_query = self.lhs
            self.key_query, self.typeclass_query = None, None
        else:
            self.obj_query = None
            self.key_query, self.typeclass_query = _separate_key_typeclass(self.args)

    def func(self):
        """Implementa il metodo."""

        caller = self.caller

        if not self.args:
            scripts = ScriptDB.objects.all().exclude(db_typeclass_path__in=self.hide_script_paths)
            if not scripts:
                caller.msg("Nessuno script trovato.")
                return
            ScriptEvMore(caller, scripts.order_by("id"), session=self.session)
            return

        scripts = self._search_script() if self.typeclass_query else None
        objects = caller.search(self.obj_query, quiet=True) if self.obj_query else None
        obj = objects[0] if objects else None

        if not self.switches:
            if obj:
                if self.rhs:
                    if obj.scripts.add(self.typeclass_query, key=self.key_query, autostart=True):
                        caller.msg(
                            f"Script |w{self.rhs}|n aggiunto e avviato con successo su"
                            f" {obj.get_display_name(caller)}."
                        )
                    else:
                        caller.msg(
                            f"Non e' stato possibile aggiungere e/o avviare lo script {self.rhs} "
                            f"su {obj.get_display_name(caller)} (oppure si e' avviato e "
                            "spento subito dopo)."
                        )
                else:
                    scripts = ScriptDB.objects.filter(db_obj=obj).exclude(
                        db_typeclass_path__in=self.hide_script_paths
                    )
                    if scripts:
                        ScriptEvMore(caller, scripts.order_by("id"), session=self.session)
                    else:
                        caller.msg(f"Nessuno script definito su {obj}")

            elif scripts:
                ScriptEvMore(caller, scripts.order_by("id"), session=self.session)

            else:
                try:
                    new_script = create.create_script(
                        typeclass=self.typeclass_query, key=self.key_query
                    )
                except ImportError:
                    logger.log_trace()
                    new_script = None

                if new_script:
                    caller.msg(
                        f"Script globale creato - {new_script.key} ({new_script.typeclass_path})"
                    )
                    ScriptEvMore(caller, [new_script], session=self.session)
                else:
                    caller.msg(
                        f"Script globale |rNON|n creato |r(vedi il log)|n - argomenti: {self.args}"
                    )

        elif scripts or obj:

            if not scripts:
                scripts = ScriptDB.objects.filter(db_obj=obj).exclude(
                    db_typeclass_path__in=self.hide_script_paths
                )

            if scripts.count() > 1:
                ret = yield (
                    f"Trovati piu' script: {scripts}. Sei sicuro di voler operare su "
                    "tutti? [S]/N? "
                )
                if ret.lower() in ("n", "no"):
                    caller.msg("Annullato.")
                    return

            for script in scripts:
                script_key = script.key
                script_typeclass_path = script.typeclass_path
                scripttype = f"Script su {obj}" if obj else "Script globale"

                for switch in self.switches:
                    verb = self.switch_mapping[switch]
                    msgs = []
                    try:
                        getattr(script, switch)()
                    except Exception:
                        logger.log_trace()
                        msgs.append(
                            f"{scripttype} |rNON|n {verb} |r(vedi il log)|n - "
                            f"{script_key} ({script_typeclass_path})|n"
                        )
                    else:
                        msgs.append(f"{scripttype} {verb} - {script_key} ({script_typeclass_path})")
                caller.msg("\n".join(msgs))
                if "delete" not in self.switches:
                    if script and script.pk:
                        ScriptEvMore(caller, [script], session=self.session)
                    else:
                        caller.msg("Lo script e' stato eliminato automaticamente.")
        else:
            caller.msg("Nessuno script trovato.")


class CmdObjects(COMMAND_DEFAULT_CLASS):
    """
    statistiche sugli oggetti nel database

    Uso:
      objects [<nr>]

    Fornisce statistiche sugli oggetti nel database e un elenco degli
    ultimi <nr> oggetti creati. Se non specificato, <nr> vale 10.
    """

    key = "@objects"
    locks = "cmd:perm(listobjects) or perm(Builder)"
    help_category = "Sistema"

    def func(self):
        """Implementa il comando."""

        caller = self.caller
        nlim = int(self.args) if self.args and self.args.isdigit() else 10
        nobjs = ObjectDB.objects.count()
        Character = class_from_module(settings.BASE_CHARACTER_TYPECLASS)
        nchars = Character.objects.all_family().count()
        Room = class_from_module(settings.BASE_ROOM_TYPECLASS)
        nrooms = Room.objects.all_family().count()
        Exit = class_from_module(settings.BASE_EXIT_TYPECLASS)
        nexits = Exit.objects.all_family().count()
        nother = nobjs - nchars - nrooms - nexits
        nobjs = nobjs or 1

        totaltable = self.styled_table(
            "|wtipo|n", "|wcommento|n", "|wconteggio|n", "|w%|n", border="table", align="l"
        )
        totaltable.align = "l"
        totaltable.add_row(
            "Personaggi",
            "(BASE_CHARACTER_TYPECLASS + figli)",
            nchars,
            "%.2f" % ((float(nchars) / nobjs) * 100),
        )
        totaltable.add_row(
            "Stanze",
            "(BASE_ROOM_TYPECLASS + figli)",
            nrooms,
            "%.2f" % ((float(nrooms) / nobjs) * 100),
        )
        totaltable.add_row(
            "Uscite",
            "(BASE_EXIT_TYPECLASS + figli)",
            nexits,
            "%.2f" % ((float(nexits) / nobjs) * 100),
        )
        totaltable.add_row("Altro", "", nother, "%.2f" % ((float(nother) / nobjs) * 100))

        typetable = self.styled_table(
            "|wtypeclass|n", "|wconteggio|n", "|w%|n", border="table", align="l"
        )
        typetable.align = "l"
        dbtotals = ObjectDB.objects.get_typeclass_totals()
        for stat in dbtotals:
            typetable.add_row(
                stat.get("typeclass", "<errore>"),
                stat.get("count", -1),
                "%.2f" % stat.get("percent", -1),
            )

        objs = ObjectDB.objects.all().order_by("db_date_created")[max(0, nobjs - nlim) :]
        latesttable = self.styled_table(
            "|wcreato|n", "|wdbref|n", "|wnome|n", "|wtypeclass|n", align="l", border="table"
        )
        latesttable.align = "l"
        for obj in objs:
            latesttable.add_row(
                utils.datetime_format(obj.date_created), obj.dbref, obj.key, obj.path
            )

        string = "\n|wTotali per sottotipo di oggetto (su %i oggetti):|n\n%s" % (nobjs, totaltable)
        string += "\n|wDistribuzione typeclass degli oggetti:|n\n%s" % typetable
        string += "\n|wUltimi %s oggetti creati:|n\n%s" % (min(nobjs, nlim), latesttable)
        caller.msg(string)


class CmdTeleport(COMMAND_DEFAULT_CLASS):
    """
    teletrasporta un oggetto in un'altra posizione

    Uso:
      tel/switch [<oggetto> to||=] <posizione bersaglio>

    Esempi:
      tel Limbo
      tel/quiet scatola = Limbo
      tel/tonone scatola

    Switch:
      quiet  - non manda i messaggi di partenza/arrivo alle posizioni
               sorgente/bersaglio dello spostamento.
      intoexit - se il bersaglio e' un'uscita, teletrasporta DENTRO
                 l'oggetto uscita invece che alla sua destinazione
      tonone - se impostato, teletrasporta l'oggetto in una posizione
               None (nessuna posizione). Se questo switch e' impostato,
               <posizione bersaglio> viene ignorato.
               Nota che l'unico modo di recuperare un oggetto da una
               posizione None e' tramite riferimento diretto al #dbref.
               Un oggetto posseduto (puppettato) non puo' essere
               spostato in None.
      loc - teletrasporta l'oggetto nella posizione del bersaglio
            invece che nel suo contenuto

    Teletrasporta un oggetto da qualche parte. Se non viene indicato
    nessun oggetto, sei tu stesso a essere teletrasportato nella
    posizione bersaglio.

    Per impedire che un oggetto venga teletrasportato, imposta il suo
    lock `teleport`, che verra' controllato contro il chiamante. Per
    bloccare una destinazione dall'essere raggiunta via teletrasporto,
    imposta il lock `teleport_here` della destinazione, che verra'
    controllato contro l'oggetto da spostare. Admin e permessi
    superiori possono sempre teletrasportare.
    """

    key = "@teleport"
    aliases = "@tel"
    switch_options = ("quiet", "intoexit", "tonone", "loc")
    rhs_split = ("=", " to ")
    locks = "cmd:perm(teleport) or perm(Builder)"
    help_category = "Costruzione"

    def parse(self):
        """Ricerca separata in un metodo a parte per facilitarne l'override."""
        super().parse()
        self.obj_to_teleport = self.caller
        self.destination = None
        if self.rhs:
            self.obj_to_teleport = self.caller.search(self.lhs, global_search=True)
            if not self.obj_to_teleport:
                self.msg("Non e' stato trovato l'oggetto da teletrasportare.")
                raise InterruptCommand
            self.destination = self.caller.search(self.rhs, global_search=True)
        elif self.lhs:
            self.destination = self.caller.search(self.lhs, global_search=True)

    def func(self):
        """Esegue il teletrasporto."""

        caller = self.caller
        obj_to_teleport = self.obj_to_teleport
        destination = self.destination

        if "tonone" in self.switches:

            if destination:
                obj_to_teleport = destination

            if obj_to_teleport.has_account:
                caller.msg(
                    f"Non puoi teletrasportare un oggetto posseduto ({obj_to_teleport.key}, "
                    f"posseduto da {obj_to_teleport.account}) in una posizione None."
                )
                return
            caller.msg(f"Teletrasportato {obj_to_teleport} -> posizione None.")
            if obj_to_teleport.location and "quiet" not in self.switches:
                obj_to_teleport.location.msg_contents(
                    f"{caller} ha teletrasportato {obj_to_teleport} nel nulla.", exclude=caller
                )
            obj_to_teleport.location = None
            return

        if not self.args:
            caller.msg("Uso: teleport[/switch] [<obj> =] <bersaglio o (X,Y,Z)>||home")
            return

        if not destination:
            return

        if "loc" in self.switches:
            destination = destination.location
            if not destination:
                caller.msg("La destinazione non ha una posizione.")
                return

        if obj_to_teleport == destination:
            caller.msg("Non puoi teletrasportare un oggetto dentro se stesso!")
            return

        if obj_to_teleport == destination.location:
            caller.msg("Non puoi teletrasportare un oggetto dentro qualcosa che lo contiene!")
            return

        if obj_to_teleport.location and obj_to_teleport.location == destination:
            caller.msg(f"{obj_to_teleport} e' gia' a {destination}.")
            return

        if not (caller.permissions.check("Admin") or obj_to_teleport.access(caller, "teleport")):
            caller.msg(
                f"Il lock 'teleport' di {obj_to_teleport} ti impedisce di teletrasportarlo."
            )
            return

        if not (
            caller.permissions.check("Admin")
            or destination.access(obj_to_teleport, "teleport_here")
        ):
            caller.msg(
                f"Il lock 'teleport_here' di {destination} impedisce a {obj_to_teleport} di "
                "spostarsi li'."
            )
            return

        if not obj_to_teleport.location:
            obj_to_teleport.location = destination
            caller.msg(f"Teletrasportato {obj_to_teleport} None -> {destination}")
        elif obj_to_teleport.move_to(
            destination,
            quiet="quiet" in self.switches,
            emit_to_obj=caller,
            use_destination="intoexit" not in self.switches,
            move_type="teleport",
        ):
            if obj_to_teleport == caller:
                caller.msg(f"Teletrasportato a {destination}.")
            else:
                caller.msg(f"Teletrasportato {obj_to_teleport} -> {destination}.")
        else:
            caller.msg("Teletrasporto fallito.")


class CmdTag(COMMAND_DEFAULT_CLASS):
    """
    gestisce i tag di un oggetto

    Uso:
      tag[/del] <obj> [= <tag>[:<categoria>]]
      tag/search <tag>[:<categoria>]

    Switch:
      search - restituisce tutti gli oggetti con un dato tag
      del - rimuove il tag indicato. Se non viene indicato nessun tag,
            elimina tutti i tag sull'oggetto.

    Manipola ed elenca i tag sugli oggetti. I tag permettono di
    raggruppare e cercare rapidamente gli oggetti. Se viene dato solo
    <obj>, elenca tutti i tag sull'oggetto. Se viene usato /search,
    elenca gli oggetti con il tag dato.
    La categoria puo' essere usata per raggruppare i tag stessi, ma
    andrebbe usata con moderazione - i tag da soli di solito bastano
    per la maggior parte degli schemi di raggruppamento.
    """

    key = "@tag"
    aliases = ["@tags"]
    switch_options = ("search", "del")
    locks = "cmd:perm(tag) or perm(Builder)"
    help_category = "Costruzione"
    arg_regex = r"(/\w+?(\s|$))|\s|$"

    def func(self):
        """Implementa la funzionalita' dei tag."""

        if not self.args:
            self.msg("Uso: tag[/switch] <obj> [= <tag>[:<categoria>]]")
            return
        if "search" in self.switches:
            tag = self.args.strip()
            category = None
            if ":" in tag:
                tag, category = [part.strip() for part in tag.split(":", 1)]
            tag = tag or None
            objs = search.search_tag(tag, category=category)
            nobjs = len(objs)
            if nobjs > 0:
                catstr = (
                    " (categoria: '|w%s|n')" % category
                    if category
                    else ("" if nobjs == 1 else " (potrebbero avere categorie di tag diverse)")
                )
                matchstr = ", ".join(o.get_display_name(self.caller) for o in objs)

                string = "Trovat%s |w%i|n oggett%s con il tag '|w%s|n'%s:\n %s" % (
                    "o" if nobjs == 1 else "i",
                    nobjs,
                    "o" if nobjs == 1 else "i",
                    tag,
                    catstr,
                    matchstr,
                )
            else:
                string = "Nessun oggetto trovato con il tag '%s%s'." % (
                    tag,
                    " (categoria: %s)" % category if category else "",
                )
            self.msg(string)
            return
        if "del" in self.switches:
            obj = self.caller.search(self.lhs, global_search=True)
            if not obj:
                return
            if self.rhs:
                tag = self.rhs
                category = None
                if ":" in tag:
                    tag, category = [part.strip() for part in tag.split(":", 1)]
                if obj.tags.get(tag, category=category):
                    obj.tags.remove(tag, category=category)
                    string = "Rimosso il tag '%s'%s da %s." % (
                        tag,
                        " (categoria: %s)" % category if category else "",
                        obj,
                    )
                else:
                    string = "Nessun tag '%s'%s da eliminare su %s." % (
                        tag,
                        " (categoria: %s)" % category if category else "",
                        obj,
                    )
            else:
                old_tags = [
                    "%s%s" % (tag, " (categoria: %s)" % category if category else "")
                    for tag, category in obj.tags.all(return_key_and_category=True)
                ]
                if old_tags:
                    obj.tags.clear()
                    string = "Rimossi tutti i tag da %s: %s" % (obj, ", ".join(sorted(old_tags)))
                else:
                    string = "Nessun tag da rimuovere su %s." % obj
            self.msg(string)
            return
        if self.rhs:
            obj = self.caller.search(self.lhs, quiet=True)
            if not obj:
                obj = self.caller.search(self.lhs, global_search=True)
            else:
                obj = obj[0]
            if not obj:
                return
            tag = self.rhs
            category = None
            if ":" in tag:
                tag, category = [part.strip() for part in tag.split(":", 1)]
            obj.tags.add(tag, category=category)
            string = "Aggiunto il tag '%s'%s a %s." % (
                tag,
                " (categoria: %s)" % category if category else "",
                obj,
            )
            self.msg(string)
        else:
            obj = self.caller.search(self.args, quiet=True)
            if not obj:
                obj = self.caller.search(self.args, global_search=True)
            else:
                obj = obj[0]
            if not obj:
                return
            tagtuples = obj.tags.all(return_key_and_category=True)
            ntags = len(tagtuples)
            tags = [tup[0] for tup in tagtuples]
            categories = [" (categoria: %s)" % tup[1] if tup[1] else "" for tup in tagtuples]
            if ntags:
                string = "Tag%s su %s: %s" % (
                    "" if ntags == 1 else "s",
                    obj,
                    ", ".join(sorted("'%s'%s" % (tags[i], categories[i]) for i in range(ntags))),
                )
            else:
                string = f"Nessun tag associato a {obj}."
            self.msg(string)


class CmdSpawn(COMMAND_DEFAULT_CLASS):
    """
    genera oggetti da un prototipo

    Uso:
      spawn[/noloc] <chiave_prototipo>
      spawn[/noloc] <dizionario_prototipo>

      spawn/search [chiave_prototipo][;tag[,tag]]
      spawn/list [tag, tag, ...]
      spawn/list modules    - elenca solo i prototipi definiti da moduli
      spawn/show [<chiave_prototipo>]
      spawn/update <chiave_prototipo>

      spawn/save <dizionario_prototipo>
      spawn/edit [<chiave_prototipo>]
      olc     - equivalente a spawn/edit

    Switch:
      noloc - permette alla posizione di essere None se non indicata
              esplicitamente. Altrimenti, la posizione sara' quella
              attuale del chiamante.
      search - cerca un prototipo per nome o tag.
      list - elenca i prototipi disponibili, opzionalmente filtrati per tag.
      show, examine - ispeziona un prototipo per chiave. Se non indicato,
              si comporta come list.
      raw - mostra il dizionario grezzo del prototipo come stringa su
            una riga, per modifiche manuali.
      save - salva un prototipo nel database. Sara' elencabile con /list.
      delete - rimuove un prototipo dal database, se consentito.
      update - trova oggetti esistenti con la stessa chiave_prototipo e
               li aggiorna con l'ultima versione del prototipo dato. Se
               usato insieme a /save, aggiorna automaticamente tutti gli
               oggetti con la vecchia versione senza chiedere conferma.
      edit, menu, olc - crea/modifica un prototipo in un'interfaccia a menu.

    Esempio:
      spawn GOBLIN
      spawn {"key":"goblin", "typeclass":"monster.Monster", "location":"#2"}
      spawn/save {"key": "grunt", prototype: "goblin"};;mobs;edit:all()
    \f
    Chiavi del dizionario:
      |wprototype_parent  |n - nome del prototipo genitore da usare.
                        Richiesto se typeclass non e' impostato. Puo'
                        essere un percorso o una lista per ereditarieta'
                        multipla (eredita da sinistra a destra). Se
                        impostato, uno dei genitori deve avere una
                        typeclass.
      |wtypeclass  |n - stringa. Richiesto se prototype_parent non e' impostato.
      |wkey        |n - stringa, l'identificatore principale dell'oggetto
      |wlocation   |n - deve essere un oggetto valido o un #dbref
      |whome       |n - oggetto valido o #dbref
      |wdestination|n - valido solo per le uscite (oggetto o dbref)
      |wpermissions|n - stringa o lista di stringhe di permesso
      |wlocks      |n - una stringa di lock
      |waliases    |n - stringa o lista di stringhe.
      |wndb_|n<nome>  - valore di un nattribute (ndb_ viene tolto)

      |wprototype_key|n   - nome di questo prototipo. Univoco. Usato per
                            salvare/recuperare dal db e aggiornare gli
                            oggetti gia' generati, se richiesto
      |wprototype_desc|n  - descrizione di questo prototipo. Usata negli elenchi
      |wprototype_locks|n - lock di questo prototipo. Limita chi puo' usarlo
      |wprototype_tags|n  - tag di questo prototipo. Usati per trovarlo

      qualsiasi altra chiave viene interpretata come un attributo e il
      suo valore.

    I prototipi disponibili sono definiti globalmente nei moduli
    impostati in settings.PROTOTYPE_MODULES. Se spawn viene usato senza
    argomenti, mostra un elenco dei prototipi disponibili.
    """

    key = "@spawn"
    aliases = ["@olc"]
    switch_options = (
        "noloc",
        "search",
        "list",
        "show",
        "raw",
        "examine",
        "save",
        "delete",
        "menu",
        "olc",
        "update",
        "edit",
    )
    locks = "cmd:perm(spawn) or perm(Builder)"
    help_category = "Costruzione"

    def _search_prototype(self, prototype_key, quiet=False):
        """Cerca il prototipo e gestisce nessuna corrispondenza/corrispondenze multiple e accesso."""
        prototypes = protlib.search_prototype(prototype_key)
        nprots = len(prototypes)

        err = None
        if not prototypes:
            err = f"Non e' stato trovato nessun prototipo chiamato '{prototype_key}'."
        elif nprots > 1:
            err = "Trovati {} prototipi corrispondenti a '{}':\n  {}".format(
                nprots,
                prototype_key,
                ", ".join(proto.get("prototype_key", "") for proto in prototypes),
            )
        else:
            prototype = prototypes[0]
            if not self.caller.locks.check_lockstring(
                self.caller, prototype.get("prototype_locks", ""), access_type="spawn", default=True
            ):
                err = "Non hai accesso a questo prototipo."

        if err:
            if not quiet:
                self.msg(err)
            return
        return prototype

    def _parse_prototype(self, inp, expect=dict):
        """Analizza un dizionario o una chiave di prototipo dall'input e lo converte in dict se opportuno."""
        eval_err = None
        try:
            prototype = _LITERAL_EVAL(inp)
        except (SyntaxError, ValueError) as err:
            eval_err = err
            prototype = utils.to_str(inp)

        if not isinstance(prototype, expect):
            if eval_err:
                string = (
                    f"{inp}\n{eval_err}\n|RErrore critico di sintassi Python nell'argomento. Sono"
                    " ammesse solo strutture Python primitive. \nAssicurati di usare una sintassi"
                    " Python corretta. Ricorda in particolare di mettere le virgolette attorno a"
                    " tutte le stringhe dentro liste e dizionari.|n Per usi piu' avanzati, incorpora"
                    " funzioni funcparser ($funcs) nelle stringhe."
                )
            else:
                string = f"Atteso {expect}, ricevuto {type(prototype)}."
            self.msg(string)
            return

        if expect == dict:
            if "exec" in prototype and not self.caller.check_permstring("Developer"):
                self.msg("Spawn annullato: non puoi usare la chiave prototipo 'exec'.")
                return
            try:
                protlib.validate_prototype(protlib.homogenize_prototype(prototype))
            except RuntimeError as err:
                self.msg(str(err))
                return
        return prototype

    def _get_prototype_detail(self, query=None, prototypes=None):
        """Mostra le specifiche dettagliate di uno o piu' prototipi."""
        if not prototypes:
            prototypes = protlib.search_prototype(key=query)
        if prototypes:
            return "\n".join(protlib.prototype_to_str(prot) for prot in prototypes)
        elif query:
            self.msg(f"Non e' stato trovato nessun prototipo chiamato '{query}'.")
        else:
            self.msg("Nessun prototipo trovato.")

    def _list_prototypes(self, key=None, tags=None):
        """Mostra i prototipi come elenco, opzionalmente limitato per chiave/tag."""
        protlib.list_prototypes(self.caller, key=key, tags=tags, session=self.session)

    @interactive
    def _update_existing_objects(self, caller, prototype_key, quiet=False):
        """Aggiorna gli oggetti esistenti (se presenti) con questa chiave_prototipo all'ultima versione."""
        prototype = self._search_prototype(prototype_key)
        if not prototype:
            return

        existing_objects = protlib.search_objects_with_prototype(prototype_key)
        if not existing_objects:
            if not quiet:
                caller.msg("Nessun oggetto esistente trovato con una versione precedente di questo prototipo.")
            return

        if existing_objects:
            n_existing = len(existing_objects)
            slow = " (nota che potrebbe essere lento)" if n_existing > 10 else ""
            string = (
                f"Ci sono {n_existing} oggetti esistenti con una versione precedente "
                f"del prototipo '{prototype_key}'. Vuoi riapplicarlo{slow}? [S]/N"
            )
            answer = yield (string)
            if answer.lower() in ["n", "no"]:
                caller.msg(
                    "|rNon e' stato eseguito nessun aggiornamento degli oggetti esistenti. "
                    "Usa spawn/update <chiave> per applicarlo in seguito.|n"
                )
                return
            try:
                n_updated = spawner.batch_update_objects_with_prototype(
                    prototype,
                    objects=existing_objects,
                    caller=caller,
                )
            except Exception:
                logger.log_trace()
            caller.msg(f"{n_updated} oggetti sono stati aggiornati.")
        return

    def _parse_key_desc_tags(self, argstring, desc=True):
        """Analizza un elenco separato da ';'."""
        key, desc, tags = "", "", []
        if ";" in argstring:
            parts = [part.strip().lower() for part in argstring.split(";")]
            if len(parts) > 1 and desc:
                key = parts[0]
                desc = parts[1]
                tags = parts[2:]
            else:
                key = parts[0]
                tags = parts[1:]
        else:
            key = argstring.strip().lower()
        return key, desc, tags

    def func(self):
        """Implementa lo spawner."""

        caller = self.caller
        noloc = "noloc" in self.switches

        if (
            self.cmdstring == "olc"
            or "menu" in self.switches
            or "olc" in self.switches
            or "edit" in self.switches
        ):
            prototype = None
            if self.lhs:
                prototype_key = self.lhs
                prototype = self._search_prototype(prototype_key)
                if not prototype:
                    return
            olc_menus.start_olc(caller, session=self.session, prototype=prototype)
            return

        if "search" in self.switches:

            if not self.args:
                self._list_prototypes()
                return

            key, _, tags = self._parse_key_desc_tags(self.args, desc=False)
            self._list_prototypes(key, tags)
            return

        if "raw" in self.switches:
            if not self.args:
                caller.msg("Devi specificare una chiave di prototipo di cui ottenere i dati grezzi.")
            prototype = self._search_prototype(self.args)
            if not prototype:
                return
            caller.msg(str(prototype))
            return

        if "show" in self.switches or "examine" in self.switches:
            if not self.args:
                caller.msg("Devi specificare una chiave di prototipo da mostrare.")
                return

            detail_string = self._get_prototype_detail(self.args)
            if not detail_string:
                return
            caller.msg(detail_string)
            return

        if "list" in self.switches:
            tags = self.lhslist
            err = self._list_prototypes(tags=tags)
            if err:
                caller.msg(
                    "Nessun prototipo trovato con il/i tag: {}".format(
                        list_to_string(tags, "or")
                    )
                )
            return

        if "save" in self.switches:
            if not self.args:
                caller.msg(
                    "Uso: spawn/save [<chiave>[;desc[;tag,tag[,...][;stringa_di_lock]]]] ="
                    " <dizionario_prototipo>"
                )
                return
            if self.rhs:
                prototype_key, prototype_desc, prototype_tags = self._parse_key_desc_tags(self.lhs)
                prototype_key = None if not prototype_key else prototype_key
                prototype_desc = None if not prototype_desc else prototype_desc
                prototype_tags = None if not prototype_tags else prototype_tags
                prototype_input = self.rhs.strip()
            else:
                prototype_key = prototype_desc = None
                prototype_tags = None
                prototype_input = self.lhs.strip()

            prototype = self._parse_prototype(prototype_input)
            if not prototype:
                return

            prot_prototype_key = prototype.get("prototype_key")

            if not (prototype_key or prot_prototype_key):
                caller.msg(
                    "Deve essere fornita una prototype_key, come `prototype_key = <prototipo>` "
                    "oppure come chiave 'prototype_key' dentro la struttura del prototipo."
                )
                return

            if prototype_key is None:
                prototype_key = prot_prototype_key

            if prot_prototype_key != prototype_key:
                caller.msg("(Sostituisco `prototype_key` nel prototipo con la chiave data.)")
                prototype["prototype_key"] = prototype_key

            if prototype_desc is not None and prot_prototype_key != prototype_desc:
                caller.msg("(Sostituisco `prototype_desc` nel prototipo con la descrizione data.)")
                prototype["prototype_desc"] = prototype_desc
            if prototype_tags is not None and prototype.get("prototype_tags") != prototype_tags:
                caller.msg("(Sostituisco `prototype_tags` nel prototipo con il/i tag dato/i)")
                prototype["prototype_tags"] = prototype_tags

            string = ""
            old_prototype = self._search_prototype(prototype_key, quiet=True)

            diff = spawner.prototype_diff(old_prototype, prototype, homogenize=True)
            diffstr = spawner.format_diff(diff)
            new_prototype_detail = self._get_prototype_detail(prototypes=[prototype])

            if old_prototype:
                if not diffstr:
                    string = f"|yPrototipo gia' esistente:|n\n{new_prototype_detail}\n"
                    question = (
                        "\nNon sembrano esserci cambiamenti. Vuoi comunque (ri)salvare? [S]/N"
                    )
                else:
                    string = (
                        f'|yTrovato il prototipo esistente "{prototype_key}". Modifica:|n\n{diffstr}\n'
                        f"|yNuovo prototipo modificato:|n\n{new_prototype_detail}"
                    )
                    question = (
                        "\n|yVuoi applicare la modifica al prototipo esistente?|n [S]/N"
                    )
            else:
                string = f"|yCreazione nuovo prototipo:|n\n{new_prototype_detail}"
                question = "\nVuoi continuare a salvare? [S]/N"

            answer = yield (string + question)
            if answer.lower() in ["n", "no"]:
                caller.msg("|rSalvataggio annullato.|n")
                return

            try:
                prot = protlib.save_prototype(prototype)
                if not prot:
                    caller.msg("|rErrore nel salvataggio:|R {}.|n".format(prototype_key))
                    return
            except protlib.PermissionError as err:
                caller.msg("|rErrore nel salvataggio:|R {}|n".format(err))
                return
            caller.msg("|gPrototipo salvato:|n {}".format(prototype_key))

            self._update_existing_objects(self.caller, prototype_key, quiet=True)
            return

        if not self.args:
            ncount = len(protlib.search_prototype())
            caller.msg(
                "Uso: spawn <chiave-prototipo> oppure {{key: value, ...}}"
                f"\n ({ncount} prototipi esistenti. Usa /list per ispezionarli)"
            )
            return

        if "delete" in self.switches:
            prototype_detail = self._get_prototype_detail(self.args)
            if not prototype_detail:
                return

            string = f"|rEliminazione prototipo:|n\n{prototype_detail}"
            question = "\nVuoi continuare a eliminarlo? [S]/N"
            answer = yield (string + question)
            if answer.lower() in ["n", "no"]:
                caller.msg("|rEliminazione annullata.|n")
                return

            try:
                success = protlib.delete_prototype(self.args)
            except protlib.PermissionError as err:
                retmsg = f"|rErrore nell'eliminazione:|R {err}|n"
            else:
                retmsg = (
                    "Eliminazione riuscita"
                    if success
                    else "Eliminazione fallita (il prototipo esiste davvero?)"
                )
            caller.msg(retmsg)
            return

        if "update" in self.switches:
            prototype_key = self.args.strip().lower()
            self._update_existing_objects(self.caller, prototype_key)
            return

        prototype = self._parse_prototype(
            self.args, expect=dict if self.args.strip().startswith("{") else str
        )
        if not prototype:
            return

        key = "<senza nome>"
        if isinstance(prototype, str):
            prototype_key = prototype
            prototype = self._search_prototype(prototype_key)

            if not prototype:
                return

        try:
            for obj in spawner.spawn(prototype, caller=self.caller):
                self.msg("Generato %s." % obj.get_display_name(self.caller))
                if not prototype.get("location") and not noloc:
                    obj.location = caller.location
        except RuntimeError as err:
            caller.msg(err)
