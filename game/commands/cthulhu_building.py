"""
Localizzazione del nucleo essenziale dei comandi da builder (Fase C).

evennia/commands/default/building.py e' enorme (4600+ righe, 25 comandi):
tradurlo tutto in blocco non e' realistico ne' utile adesso. Qui copriamo
il nucleo che serve davvero per costruire stanze/uscite/oggetti a mano:
create, desc, destroy, dig, tunnel, link/unlink, sethome, name, open.

CmdSetAttribute (@set), CmdExamine (@examine), CmdTypeclass, CmdLock,
CmdFind, CmdTeleport, CmdTag, CmdSpawn, CmdCopy, CmdCpAttr, CmdMvAttr,
CmdSetObjAlias, CmdWipe, CmdScripts, CmdObjects sono stati tradotti a
parte in commands/cthulhu_building_advanced.py (Fase C, seconda
tornata) - qui restava solo il nucleo essenziale. L'unico comando
davvero mai tradotto e' CmdListCmdSets, ma non ha comunque testo da
tradurre.

Riusiamo `ObjManipCommand` di Evennia cosi' com'e' per il parsing
(nome;alias;alias:typeclass) - non contiene stringhe rivolte al
giocatore, solo logica.
"""

from django.conf import settings

from evennia import InterruptCommand
from evennia.commands.default.building import ObjManipCommand
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils import utils as evennia_utils
from evennia.utils.eveditor import EvEditor
from evennia.utils.utils import variable_from_module


class CmdCreate(ObjManipCommand):
    """
    crea nuovi oggetti

    Uso:
      create[/drop] <nomeoggetto>[;alias;alias...][:typeclass], <nomeoggetto>...

    switch:
       drop - deposita automaticamente il nuovo oggetto nella tua
              posizione attuale (senza messaggio). Imposta anche la
              home del nuovo oggetto sulla posizione attuale invece
              che su di te.

    Crea uno o piu' nuovi oggetti. Se viene indicata una typeclass,
    l'oggetto viene creato come figlio di quella classe.
    """

    key = "@create"
    switch_options = ("drop",)
    locks = "cmd:perm(create) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        caller = self.caller

        if not self.args:
            self.msg("Uso: create[/drop] <nuovonome>[;alias;alias...] [:percorso.typeclass]")
            return

        for objdef in self.lhs_objs:
            string = ""
            name = objdef["name"]
            aliases = objdef["aliases"]

            obj_typeclass, errors = self.get_object_typeclass(
                obj_type="object", typeclass=objdef["option"]
            )
            if errors:
                self.msg(errors)
            if not obj_typeclass:
                continue

            obj, errors = obj_typeclass.create(
                name,
                account=caller.account,
                location=caller,
                home=caller,
                aliases=aliases,
                report_to=caller,
                caller=caller,
            )
            if errors:
                self.msg(errors)
            if not obj:
                continue

            if aliases:
                string = f"Crei un nuovo {obj.typename}: {obj.name} (alias: {', '.join(aliases)})."
            else:
                string = f"Crei un nuovo {obj.typename}: {obj.name}."

            if "drop" in self.switches:
                if caller.location:
                    obj.home = caller.location
                    obj.move_to(caller.location, quiet=True, move_type="drop")
        if string:
            caller.msg(string)


def _desc_load(caller):
    return caller.db.evmenu_target.db.desc or ""


def _desc_save(caller, buf):
    caller.db.evmenu_target.db.desc = buf
    caller.msg("Salvato.")
    return True


def _desc_quit(caller):
    caller.attributes.remove("evmenu_target")
    caller.msg("Editor chiuso.")


class CmdDesc(MuxCommand):
    """
    descrivi un oggetto o la stanza attuale

    Uso:
      desc [<obj> =] <descrizione>

    Switch:
      edit - apre un editor di riga per modifiche piu' avanzate

    Imposta l'attributo "desc" su un oggetto. Se non viene indicato un
    oggetto, descrive la stanza attuale.
    """

    key = "@desc"
    switch_options = ("edit",)
    locks = "cmd:perm(desc) or perm(Builder)"
    help_category = "Costruzione"

    def edit_handler(self):
        if self.rhs:
            self.msg("|rPuoi specificare un valore, oppure usare lo switch edit, ma non entrambi.|n")
            return
        if self.args:
            obj = self.caller.search(self.args)
        else:
            obj = self.caller.location or self.msg("|rNon puoi descrivere il nulla.|n")
        if not obj:
            return

        if not (obj.access(self.caller, "control") or obj.access(self.caller, "edit")):
            self.msg(f"Non hai il permesso di modificare la descrizione di {obj.key}.")
            return

        self.caller.db.evmenu_target = obj
        EvEditor(
            self.caller,
            loadfunc=_desc_load,
            savefunc=_desc_save,
            quitfunc=_desc_quit,
            key="desc",
            persistent=True,
        )
        return

    def func(self):
        caller = self.caller
        if not self.args and "edit" not in self.switches:
            caller.msg("Uso: desc [<obj> =] <descrizione>")
            return

        if "edit" in self.switches:
            self.edit_handler()
            return

        if "=" in self.args:
            obj = caller.search(self.lhs)
            if not obj:
                return
            desc = self.rhs or ""
        else:
            obj = caller.location or self.msg("|rNon hai una posizione da descrivere.|n")
            if not obj:
                return
            desc = self.args
        if obj.access(self.caller, "control") or obj.access(self.caller, "edit"):
            obj.db.desc = desc
            caller.msg(f"La descrizione e' stata impostata su {obj.get_display_name(caller)}.")
        else:
            caller.msg(f"Non hai il permesso di modificare la descrizione di {obj.key}.")


class CmdDestroy(MuxCommand):
    """
    elimina definitivamente degli oggetti

    Uso:
       destroy[/switch] [obj, obj2, obj3, [dbref-dbref], ...]

    Switch:
       override - di norma destroy evita di eliminare per errore gli
                  oggetti degli account; questo switch forza comunque
                  l'eliminazione.
       force - elimina senza chiedere conferma.

    Esempi:
       destroy casa, tetto, porta, 44-78
       destroy 5-10, fiore, 45
       destroy/force nord
    """

    key = "@destroy"
    aliases = ["@delete", "@del"]
    switch_options = ("override", "force")
    locks = "cmd:perm(destroy) or perm(Builder)"
    help_category = "Costruzione"

    confirm = True
    default_confirm = "si"

    def func(self):
        caller = self.caller
        delete = True

        if not self.args or not self.lhslist:
            caller.msg("Uso: destroy[/switch] [obj, obj2, obj3, [dbref-dbref], ...]")
            delete = False

        def delobj(obj):
            string = ""
            if not obj.pk:
                string = f"\nL'oggetto {obj.db_key} era gia' stato eliminato."
            else:
                objname = obj.name
                if not (obj.access(caller, "control") or obj.access(caller, "delete")):
                    return f"\nNon hai il permesso di eliminare {objname}."
                if obj.account and "override" not in self.switches:
                    return (
                        f"\nL'oggetto {objname} e' controllato da un account attivo. Usa "
                        "/override per eliminarlo comunque."
                    )
                if obj.dbid == int(settings.DEFAULT_HOME.lstrip("#")):
                    return (
                        f"\nStai cercando di eliminare |c{objname}|n, impostato come "
                        "DEFAULT_HOME. Reindirizza settings.DEFAULT_HOME a un altro oggetto "
                        "prima di continuare."
                    )

                obj_exits = obj.exits if hasattr(obj, "exits") else ()
                obj_contents = obj.contents if hasattr(obj, "contents") else ()
                had_exits = bool(obj_exits)
                had_objs = any(entity for entity in obj_contents if entity not in obj_exits)

                okay = obj.delete()
                if not okay:
                    string += (
                        f"\nERRORE: {objname} non eliminato, probabilmente perche' delete() "
                        "ha restituito False."
                    )
                else:
                    string += f"\n{objname} e' stato distrutto."
                    if had_exits:
                        string += f" Anche le uscite da e verso {objname} sono state distrutte."
                    if had_objs:
                        string += f" Gli oggetti dentro {objname} sono stati spostati alle loro home."
            return string

        objs = []
        for objname in self.lhslist:
            if not delete:
                continue

            if "-" in objname:
                dmin, dmax = [
                    evennia_utils.dbref(part, reqhash=False) for part in objname.split("-", 1)
                ]
                if dmin and dmax:
                    for dbref in range(int(dmin), int(dmax + 1)):
                        obj = caller.search("#" + str(dbref))
                        if obj:
                            objs.append(obj)
                    continue
                else:
                    obj = caller.search(objname)
            else:
                obj = caller.search(objname)

            if obj is None:
                self.msg(
                    " (Gli oggetti da distruggere devono essere locali o specificati con un "
                    "#dbref univoco.)"
                )
            elif obj not in objs:
                objs.append(obj)

        if objs and ("force" not in self.switches and type(self).confirm):
            confirm = "Sei sicuro di voler distruggere "
            if len(objs) == 1:
                confirm += objs[0].get_display_name(caller)
            elif len(objs) < 5:
                confirm += ", ".join([obj.get_display_name(caller) for obj in objs])
            else:
                confirm += ", ".join(["#{}".format(obj.id) for obj in objs])
            confirm += " [si]/no?" if self.default_confirm == "si" else " si/[no]"
            answer = yield (confirm)
            answer = self.default_confirm if answer == "" else answer

            if answer and answer.strip().lower() not in ("si", "s", "yes", "y", "no", "n"):
                caller.msg(
                    "Annullato: premi invio per accettare il valore predefinito, oppure "
                    "specifica si/no."
                )
                delete = False
            elif answer.strip().lower() in ("n", "no"):
                caller.msg("Annullato: nessun oggetto e' stato distrutto.")
                delete = False

        if delete:
            results = []
            for obj in objs:
                results.append(delobj(obj))
            if results:
                caller.msg("".join(results).strip())


class CmdDig(ObjManipCommand):
    """
    costruisci nuove stanze e collegale alla posizione attuale

    Uso:
      dig[/switch] <nomestanza>[;alias;alias...][:typeclass]
            [= <uscita_verso_la>[;alias][:typeclass]]
               [, <uscita_verso_qui>[;alias][:typeclass]]

    Switch:
       tel o teleport - spostati nella nuova stanza

    Esempi:
       dig cucina = nord;n, sud;s
       dig casa:miestanze.MiaCasaTypeclass
       dig scogliera scoscesa;scogliera = sali su, scendi giu'
    """

    key = "@dig"
    switch_options = ("teleport",)
    locks = "cmd:perm(dig) or perm(Builder)"
    help_category = "Costruzione"

    method_type = "cmd_dig"

    new_room_lockstring = (
        "control:id({id}) or perm(Admin); "
        "delete:id({id}) or perm(Admin); "
        "edit:id({id}) or perm(Admin)"
    )

    def func(self):
        caller = self.caller

        if not self.lhs:
            string = "Uso: dig[/teleport] <nomestanza>[;alias;alias...][:parent] [= <uscita_verso>"
            string += "[;alias;alias..][:parent]] "
            string += "[, <uscita_di_ritorno>[;alias;alias..][:parent]]"
            caller.msg(string)
            return

        room = self.lhs_objs[0]

        if not room["name"]:
            caller.msg("Devi fornire un nome per la nuova stanza.")
            return
        location = caller.location

        room_typeclass, errors = self.get_object_typeclass(
            obj_type="room", typeclass=room["option"], method=self.method_type
        )
        if errors:
            self.msg("|rErrore nella creazione della stanza:|n %s" % errors)
        if not room_typeclass:
            return

        new_room, errors = room_typeclass.create(
            room["name"],
            aliases=room["aliases"],
            report_to=caller,
            caller=caller,
            method=self.method_type,
        )
        if errors:
            self.msg("|rErrore nella creazione della stanza:|n %s" % errors)
        if not new_room:
            return

        alias_string = ""
        if new_room.aliases.all():
            alias_string = " (%s)" % ", ".join(new_room.aliases.all())

        room_string = (
            f"Creata la stanza {new_room}({new_room.dbref}){alias_string} di tipo "
            f"{new_room.typeclass_path}."
        )

        exit_to_string = ""
        exit_back_string = ""

        if self.rhs_objs:
            to_exit = self.rhs_objs[0]
            if not to_exit["name"]:
                exit_to_string = "\nNessuna uscita creata verso la nuova stanza."
            elif not location:
                exit_to_string = "\nNon puoi creare un'uscita da una posizione inesistente."
            else:
                exit_typeclass, errors = self.get_object_typeclass(
                    obj_type="exit", typeclass=to_exit["option"], method=self.method_type
                )
                if errors:
                    self.msg("|rErrore nella creazione dell'uscita:|n %s" % errors)
                if not exit_typeclass:
                    return

                new_to_exit, errors = exit_typeclass.create(
                    to_exit["name"],
                    location=location,
                    destination=new_room,
                    aliases=to_exit["aliases"],
                    report_to=caller,
                    caller=caller,
                    method=self.method_type,
                )
                if errors:
                    self.msg("|rErrore nella creazione dell'uscita:|n %s" % errors)
                if not new_to_exit:
                    return

                alias_string = ""
                if new_to_exit.aliases.all():
                    alias_string = " (%s)" % ", ".join(new_to_exit.aliases.all())
                exit_to_string = (
                    f"\nCreata l'uscita da {location.name} a {new_room.name}:"
                    f" {new_to_exit}({new_to_exit.dbref}){alias_string}."
                )

        if len(self.rhs_objs) > 1:
            back_exit = self.rhs_objs[1]
            if not back_exit["name"]:
                exit_back_string = "\nNessuna uscita di ritorno creata."
            elif not location:
                exit_back_string = "\nNon puoi creare un'uscita di ritorno verso una posizione inesistente."
            else:
                exit_typeclass, errors = self.get_object_typeclass(
                    obj_type="exit", typeclass=back_exit["option"], method=self.method_type
                )
                if errors:
                    self.msg("|rErrore nella creazione dell'uscita:|n %s" % errors)
                if not exit_typeclass:
                    return
                new_back_exit, errors = exit_typeclass.create(
                    back_exit["name"],
                    location=new_room,
                    destination=location,
                    aliases=back_exit["aliases"],
                    report_to=caller,
                    caller=caller,
                    method=self.method_type,
                )
                if errors:
                    self.msg("|rErrore nella creazione dell'uscita:|n %s" % errors)
                if not new_back_exit:
                    return
                alias_string = ""
                if new_back_exit.aliases.all():
                    alias_string = " (%s)" % ", ".join(new_back_exit.aliases.all())
                exit_back_string = (
                    f"\nCreata l'uscita di ritorno da {new_room.name} a {location.name}:"
                    f" {new_back_exit}({new_back_exit.dbref}){alias_string}."
                )
        caller.msg(f"{room_string}{exit_to_string}{exit_back_string}")
        if new_room and "teleport" in self.switches:
            caller.move_to(new_room, move_type="teleport")


class CmdTunnel(MuxCommand):
    """
    crea nuove stanze solo nelle direzioni cardinali

    Uso:
      tunnel[/switch] <direzione>[:typeclass] [= <nomestanza>[;alias;...][:typeclass]]

    Switch:
      oneway - non creare un'uscita di ritorno verso la posizione attuale
      tel - teletrasportati nella nuova stanza

    Esempio:
      tunnel n
      tunnel n = casa di mike;casotto verde

    Direzioni comprese: n,ne,e,se,s,sw,w,nw (punti cardinali), u,d (su/giu'), i,o (dentro/fuori).
    """

    key = "@tunnel"
    aliases = ["@tun"]
    switch_options = ("oneway", "tel")
    locks = "cmd: perm(tunnel) or perm(Builder)"
    help_category = "Costruzione"

    method_type = "cmd_tunnel"

    # nomi delle uscite in italiano (non solo i messaggi): sono quello che i
    # giocatori digiteranno davvero per muoversi, quindi vanno tradotti al
    # pari di qualunque altro comando - non solo i testi di errore attorno.
    directions = {
        "n": ("nord", "s"),
        "ne": ("nordest", "so"),
        "e": ("est", "o"),
        "se": ("sudest", "no"),
        "s": ("sud", "n"),
        "so": ("sudovest", "ne"),
        "o": ("ovest", "e"),
        "no": ("nordovest", "se"),
        "su": ("su", "giu"),
        "giu": ("giu", "su"),
        "de": ("dentro", "fu"),
        "fu": ("fuori", "de"),
    }

    def func(self):
        if not self.args or not self.lhs:
            string = (
                "Uso: tunnel[/switch] <direzione>[:typeclass] [= <nomestanza>"
                "[;alias;alias;...][:typeclass]]"
            )
            self.msg(string)
            return

        exitshort = self.lhs.split(":")[0]

        if exitshort not in self.directions:
            string = "tunnel comprende solo le seguenti direzioni: %s." % ",".join(
                sorted(self.directions.keys())
            )
            string += "\n(usa dig per maggiore liberta')"
            self.msg(string)
            return

        exitname, backshort = self.directions[exitshort]
        backname = self.directions[backshort][0]

        if ":" in self.lhs:
            exit_typeclass = ":" + self.lhs.split(":", 1)[-1]
            exitshort += exit_typeclass
            backshort += exit_typeclass

        roomname = "Un luogo qualsiasi"
        if self.rhs:
            roomname = self.rhs

        telswitch = ""
        if "tel" in self.switches:
            telswitch = "/teleport"
        backstring = ""
        if "oneway" not in self.switches:
            backstring = f", {backname};{backshort}"

        digstring = f"@dig{telswitch} {roomname} = {exitname};{exitshort}{backstring}"
        self.execute_cmd(digstring)


class CmdLink(MuxCommand):
    """
    collega stanze esistenti tra loro con delle uscite

    Uso:
      link[/switch] <oggetto> = <bersaglio>
      link[/switch] <oggetto> =
      link[/switch] <oggetto>

    Switch:
      twoway - collega due uscite. Perche' funzioni, sia <oggetto> che
               <bersaglio> devono essere uscite.

    Se <oggetto> e' un'uscita, ne imposta la destinazione su <bersaglio>.
    La seconda forma (solo =) azzera la destinazione (come unlink), la
    terza (senza =) mostra solo la destinazione attuale.
    """

    key = "@link"
    locks = "cmd:perm(link) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Uso: link[/twoway] <oggetto> = <bersaglio>")
            return

        object_name = self.lhs

        results = caller.search(object_name, quiet=True)
        if len(results) > 1:
            _AT_SEARCH_RESULT = variable_from_module(*settings.SEARCH_AT_RESULT.rsplit(".", 1))
            return _AT_SEARCH_RESULT(results, caller, query=object_name)
        elif len(results) == 1:
            obj = results[0]
        else:
            obj = caller.search(object_name, global_search=True)
            if not obj:
                return

        if self.rhs:
            target = caller.search(self.rhs, global_search=True)
            if not target:
                return

            if target == obj:
                self.msg("Non puoi collegare un oggetto a se stesso.")
                return

            string = ""
            note = (
                "Nota: %s(%s) non aveva una destinazione impostata in precedenza. Assicurati "
                "di aver collegato la cosa giusta."
            )
            if not obj.destination:
                string = note % (obj.name, obj.dbref)
            if "twoway" in self.switches:
                if not (target.location and obj.location):
                    string = (
                        f"Per creare un collegamento a due vie, {obj} e {target} devono "
                        "entrambi avere una posizione"
                    )
                    string += " (cioe' non possono essere stanze, ma devono essere uscite)."
                    self.msg(string)
                    return
                if not target.destination:
                    string += note % (target.name, target.dbref)
                obj.destination = target.location
                target.destination = obj.location
                string += (
                    f"\nCollegamento creato {obj.name} (in {obj.location}) <-> {target.name} (in"
                    f" {target.location}) (a due vie)."
                )
            else:
                obj.destination = target
                string += f"\nCollegamento creato {obj.name} -> {target} (a senso unico)."

        elif self.rhs is None:
            dest = obj.destination
            if dest:
                string = f"{obj.name} e' un'uscita verso {dest.name}."
            else:
                string = f"{obj.name} non e' un'uscita. La sua home e' {obj.home}."

        else:
            if obj.destination:
                obj.destination = None
                string = f"L'ex uscita {obj.name} non porta piu' da nessuna parte."
            else:
                string = f"{obj.name} non aveva nessuna destinazione da scollegare."
        caller.msg(string.strip())


class CmdUnLink(CmdLink):
    """
    rimuove il collegamento tra due stanze

    Uso:
      unlink <oggetto>

    Scollega un oggetto (tipicamente un'uscita) da qualsiasi cosa fosse
    collegato.
    """

    key = "unlink"
    locks = "cmd:perm(unlink) or perm(Builder)"
    help_key = "Building"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: unlink <oggetto>")
            return
        self.rhs = ""
        super().func()


class CmdSetHome(CmdLink):
    """
    imposta la home di un oggetto

    Uso:
      sethome <obj> [= <posizione_home>]
      sethome <obj>

    La "home" e' una posizione di sicurezza per un oggetto: ci verra'
    spostato se la sua posizione attuale smette di esistere. Senza
    argomenti, mostra solo la home attuale.
    """

    key = "@sethome"
    locks = "cmd:perm(sethome) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        if not self.args:
            self.msg("Uso: sethome <obj> [= <posizione_home>]")
            return

        obj = self.caller.search(self.lhs, global_search=True)
        if not obj:
            return
        if not self.rhs:
            home = obj.home
            if not home:
                string = "Questo oggetto non ha una home impostata!"
            else:
                string = f"La home attuale di {obj} e' {home}({home.dbref})."
        else:
            new_home = self.caller.search(self.rhs, global_search=True)
            if not new_home:
                return
            old_home = obj.home
            obj.home = new_home
            if old_home:
                string = (
                    f"La home di {obj} e' cambiata da {old_home}({old_home.dbref}) a"
                    f" {new_home}({new_home.dbref})."
                )
            else:
                string = f"La home di {obj} e' stata impostata su {new_home}({new_home.dbref})."
        self.msg(string)


class CmdName(ObjManipCommand):
    """
    cambia il nome e/o gli alias di un oggetto

    Uso:
      name <obj> = <nuovonome>;alias1;alias2

    Rinomina un oggetto. Usa *obj per rinominare un account.
    """

    key = "@name"
    aliases = ["@rename"]
    locks = "cmd:perm(rename) or perm(Builder)"
    help_category = "Costruzione"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: name <obj> = <nuovonome>[;alias;alias;...]")
            return

        obj = None
        if self.lhs_objs:
            objname = self.lhs_objs[0]["name"]
            if objname.startswith("*") and caller.account:
                obj = caller.account.search(objname.lstrip("*"))
                if obj:
                    if self.rhs_objs[0]["aliases"]:
                        caller.msg("Gli account non possono avere alias.")
                        return
                    newname = self.rhs
                    if not newname:
                        caller.msg("Nessun nome definito!")
                        return
                    if not (obj.access(caller, "control") or obj.access(caller, "edit")):
                        caller.msg(f"Non hai il diritto di modificare questo account {obj}.")
                        return
                    obj.username = newname
                    obj.save()
                    caller.msg(f"Nome dell'account cambiato in '{newname}'.")
                    return
            obj = caller.search(objname)
            if not obj:
                return
        if self.rhs_objs:
            newname = self.rhs_objs[0]["name"]
            aliases = self.rhs_objs[0]["aliases"]
        else:
            newname = self.rhs
            aliases = None
        if not newname and not aliases:
            caller.msg("Nessun nome o alias definito!")
            return
        if not (obj.access(caller, "control") or obj.access(caller, "edit")):
            caller.msg(f"Non hai il diritto di modificare {obj}.")
            return
        if newname:
            obj.key = newname
        astring = ""
        if aliases:
            [obj.aliases.add(alias) for alias in aliases]
            astring = " (%s)" % ", ".join(aliases)
        if obj.destination:
            obj.flush_from_cache(force=True)
        caller.msg(f"Nome dell'oggetto cambiato in '{newname}'{astring}.")


class CmdOpen(ObjManipCommand):
    """
    apri una nuova uscita dalla stanza attuale

    Uso:
      open <nuova_uscita>[;alias;alias..][:typeclass] [,<uscita_di_ritorno>[;alias..][:typeclass]]] = <destinazione>

    Crea un'uscita verso la destinazione indicata. L'argomento opzionale
    <uscita_di_ritorno> crea anche un'uscita nella destinazione che
    riporta qui.
    """

    key = "@open"
    locks = "cmd:perm(open) or perm(Builder)"
    help_category = "Costruzione"

    method_type = "cmd_open"

    new_obj_lockstring = "control:id({id}) or perm(Admin);delete:id({id}) or perm(Admin)"

    def create_exit(self, exit_name, location, destination, exit_aliases=None, typeclass=None):
        caller = self.caller
        string = ""
        exit_obj = caller.search(exit_name, location=location, quiet=True, exact=True)
        if len(exit_obj) > 1:
            caller.search(exit_name, location=location, exact=True)
            return None
        if exit_obj:
            exit_obj = exit_obj[0]
            if not exit_obj.destination:
                caller.msg(
                    f"'{exit_name}' esiste gia' e non e' un'uscita!\nSe vuoi convertirlo in "
                    "un'uscita, devi prima assegnargli una 'destination'."
                )
                return None
            old_destination = exit_obj.destination
            if old_destination:
                string = f"L'uscita {exit_name} esiste gia'."
                if old_destination.id != destination.id:
                    exit_obj.destination = destination
                    if exit_aliases:
                        [exit_obj.aliases.add(alias) for alias in exit_aliases]
                    string += (
                        f" Reindirizzata dalla vecchia destinazione '{old_destination.name}' a"
                        f" '{destination.name}' e alias aggiornati."
                    )
                else:
                    string += " Punta gia' al posto giusto."

        else:
            exit_typeclass, errors = self.get_object_typeclass(
                obj_type="exit", typeclass=typeclass, method=self.method_type
            )
            if errors:
                self.msg("|rErrore nella creazione dell'uscita:|n %s" % errors)
            if not exit_typeclass:
                return
            exit_obj, errors = exit_typeclass.create(
                exit_name,
                location=location,
                aliases=exit_aliases,
                report_to=caller,
                caller=caller,
                method=self.method_type,
            )
            if errors:
                self.msg("|rErrore nella creazione dell'uscita:|n %s" % errors)
            if not exit_obj:
                return
            if exit_obj:
                exit_obj.destination = destination
                string = (
                    ""
                    if not exit_aliases
                    else " (alias: %s)" % ", ".join([str(e) for e in exit_aliases])
                )
                string = (
                    f"Creata la nuova uscita '{exit_name}' da {location.name} a"
                    f" {destination.name}{string}."
                )
            else:
                string = f"Errore: uscita non creata."
        caller.msg(string)
        return exit_obj

    def parse(self):
        super().parse()
        self.location = self.caller.location
        if not self.args or not self.rhs:
            self.msg(
                "Uso: open <nuova_uscita>[;alias...][:typeclass]"
                "[,<uscita_di_ritorno>[;alias..][:typeclass]]] "
                "= <destinazione>"
            )
            raise InterruptCommand
        if not self.location:
            self.msg("Non puoi creare un'uscita da una posizione inesistente.")
            raise InterruptCommand
        self.destination = self.caller.search(self.rhs, global_search=True)
        if not self.destination:
            raise InterruptCommand
        self.exit_name = self.lhs_objs[0]["name"]
        self.exit_aliases = self.lhs_objs[0]["aliases"]
        self.exit_typeclass = self.lhs_objs[0]["option"]

    def func(self):
        ok = self.create_exit(
            self.exit_name, self.location, self.destination, self.exit_aliases, self.exit_typeclass
        )
        if not ok:
            return
        if len(self.lhs_objs) > 1:
            back_exit_name = self.lhs_objs[1]["name"]
            back_exit_aliases = self.lhs_objs[1]["aliases"]
            back_exit_typeclass = self.lhs_objs[1]["option"]
            self.create_exit(
                back_exit_name,
                self.destination,
                self.location,
                back_exit_aliases,
                back_exit_typeclass,
            )
