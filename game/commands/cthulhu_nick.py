"""
Localizzazione del comando `nick` (alias personali) - Fase C, terza tornata.

E' un comando che i giocatori normali usano abbastanza spesso (per
abbreviare comandi ripetitivi, dare soprannomi ad altri personaggi, ecc.),
quindi lo trattiamo alla pari dei comandi generali gia' tradotti in Fase B.
"""

import re

from evennia.commands.default.muxcommand import MuxCommand
from evennia.typeclasses.attributes import NickTemplateInvalid
from evennia.utils import utils


class CmdNick(MuxCommand):
    """
    definisci un alias/soprannome personale, indicando una stringa da
    cercare e una da sostituire al volo

    Uso:
      nick[/switch] <stringa> [= [stringa_sostitutiva]]
      nick[/switch] <modello> = <modello_sostitutivo>
      nick/delete <stringa> o numero
      nicks

    Switch:
      inputline - sostituisce sulla riga di comando digitata (default)
      object    - sostituisce nella ricerca di oggetti
      account   - sostituisce nella ricerca di account
      list      - mostra tutti gli alias definiti (funziona anche "nicks")
      delete    - rimuove un nick per indice in /list
      clearall  - cancella tutti i nick

    Esempi:
      nick ciao = say Ciao, sono Sara!
      nick/object tom = l'uomo alto
      nick build $1 $2 = create/drop $1;$2
      nick tell $1 $2=page $1=$2
      nick tm?$1=page tallman=$1
      nick tm\\\\=$1=page tallman=$1

    Un 'nick' e' una sostituzione di stringa personale. Usa $1, $2, ... per
    catturare argomenti. Metti l'ultimo marcatore $ senza uno spazio finale
    per catturare tutto il testo rimanente. Puoi anche usare il pattern
    matching in stile unix-glob per la <stringa> a sinistra:

        * - corrisponde a tutto
        ? - corrisponde a 0 o 1 caratteri singoli
        [abcd] - corrisponde a questi caratteri in qualsiasi ordine
        [!abcd] - corrisponde a tutto cio' che non e' tra questi caratteri
        \\\\= - per usare un '=' letterale dentro la tua <stringa>

    Nota che nessun oggetto viene realmente rinominato o modificato da
    questo comando - i tuoi nick sono disponibili solo per te. Se vuoi
    aggiungere permanentemente delle parole chiave a un oggetto perche'
    tutti possano usarle, ti servono i permessi da builder e il comando
    alias.
    """

    key = "nick"
    switch_options = ("inputline", "object", "account", "list", "delete", "clearall")
    aliases = ["nickname", "nicks"]
    locks = "cmd:all()"

    def parse(self):
        """Supporta l'escape del segno = con \\="""
        super().parse()
        args = (self.lhs or "") + (" = %s" % self.rhs if self.rhs else "")
        parts = re.split(r"(?<!\\)=", args, 1)
        self.rhs = None
        if len(parts) < 2:
            self.lhs = parts[0].strip()
        else:
            self.lhs, self.rhs = [part.strip() for part in parts]
        self.lhs = self.lhs.replace("\\=", "=")

    def func(self):
        """Crea il nickname."""

        def _cy(string):
            "aggiunge colore ai marcatori speciali"
            return re.sub(r"(\$[0-9]+|\*|\?|\[.+?\])", r"|Y\1|n", string)

        caller = self.caller
        switches = self.switches
        nicktypes = [switch for switch in switches if switch in ("object", "account", "inputline")]
        specified_nicktype = bool(nicktypes)
        nicktypes = nicktypes if specified_nicktype else ["inputline"]

        nicklist = (
            utils.make_iter(caller.nicks.get(category="inputline", return_obj=True) or [])
            + utils.make_iter(caller.nicks.get(category="object", return_obj=True) or [])
            + utils.make_iter(caller.nicks.get(category="account", return_obj=True) or [])
        )

        if "list" in switches or self.cmdstring in ("nicks",):
            if not nicklist:
                string = "|wNessun nick definito.|n"
            else:
                table = self.styled_table("#", "Tipo", "Nick da cercare", "Sostituzione")
                for inum, nickobj in enumerate(nicklist):
                    _, _, nickvalue, replacement = nickobj.value
                    table.add_row(
                        str(inum + 1), nickobj.db_category, _cy(nickvalue), _cy(replacement)
                    )
                string = "|wNick definiti:|n\n%s" % table
            caller.msg(string)
            return

        if "clearall" in switches:
            caller.nicks.clear()
            if caller.account:
                caller.account.nicks.clear()
            caller.msg("Tutti i nick sono stati cancellati.")
            return

        if "delete" in switches or "del" in switches:
            if not self.args or not self.lhs:
                caller.msg("uso: nick/delete <nick> o <#numero> (usa 'nicks' per l'elenco)")
                return
            arg = self.args.lstrip("#")
            oldnicks = []
            if arg.isdigit():
                delindex = int(arg)
                if 0 < delindex <= len(nicklist):
                    oldnicks.append(nicklist[delindex - 1])
                else:
                    caller.msg("Non e' un indice di nick valido. Vedi 'nicks' per l'elenco.")
                    return
            else:
                if not specified_nicktype:
                    nicktypes = ("object", "account", "inputline")
                for nicktype in nicktypes:
                    oldnicks.append(caller.nicks.get(arg, category=nicktype, return_obj=True))

            oldnicks = [oldnick for oldnick in oldnicks if oldnick]
            if oldnicks:
                for oldnick in oldnicks:
                    nicktype = oldnick.category
                    nicktypestr = "Nick-%s" % nicktype.capitalize()
                    _, _, old_nickstring, old_replstring = oldnick.value
                    caller.nicks.remove(old_nickstring, category=nicktype)
                    caller.msg(
                        f"{nicktypestr} rimosso: '|w{old_nickstring}|n' -> |w{old_replstring}|n."
                    )
            else:
                caller.msg("Nessun nick corrispondente da rimuovere.")
            return

        if not self.rhs and self.lhs:
            # controlla a cosa e' impostato un nick
            strings = []
            if not specified_nicktype:
                nicktypes = ("object", "account", "inputline")
            for nicktype in nicktypes:
                nicks = [
                    nick
                    for nick in utils.make_iter(
                        caller.nicks.get(category=nicktype, return_obj=True)
                    )
                    if nick
                ]
                for nick in nicks:
                    _, _, nick, repl = nick.value
                    if nick.startswith(self.lhs):
                        strings.append(f"Nick-{nicktype.capitalize()}: '{nick}' -> '{repl}'")
            if strings:
                caller.msg("\n".join(strings))
            else:
                caller.msg(f"Nessun nick trovato che corrisponda a '{self.lhs}'")
            return

        if not self.args or not self.lhs:
            caller.msg("Uso: nick[/switch] nickname = [nome_vero]")
            return

        # impostazione di nuovi nick

        nickstring = self.lhs
        replstring = self.rhs

        if replstring == nickstring:
            caller.msg("Non ha senso impostare un nick uguale alla stringa da sostituire...")
            return

        errstring = ""
        string = ""
        for nicktype in nicktypes:
            nicktypestr = f"Nick-{nicktype.capitalize()}"
            old_nickstring = None
            old_replstring = None

            oldnick = caller.nicks.get(key=nickstring, category=nicktype, return_obj=True)
            if oldnick:
                _, _, old_nickstring, old_replstring = oldnick.value
            if replstring:
                errstring = ""
                if oldnick:
                    if replstring == old_replstring:
                        string += f"\n{nicktypestr} identico gia' impostato."
                    else:
                        string += (
                            f"\n{nicktypestr} '|w{old_nickstring}|n' aggiornato per puntare a"
                            f" '|w{replstring}|n'."
                        )
                else:
                    string += f"\n{nicktypestr} '|w{nickstring}|n' associato a '|w{replstring}|n'."
                try:
                    caller.nicks.add(nickstring, replstring, category=nicktype)
                except NickTemplateInvalid:
                    caller.msg(
                        "Devi usare gli stessi marcatori $ sia nel nick che nella sostituzione."
                    )
                    return
            elif old_nickstring and old_replstring:
                string += f"\n{nicktypestr} '|w{old_nickstring}|n' punta a '|w{old_replstring}|n'."
                errstring = ""
        string = errstring if errstring else string
        caller.msg(_cy(string))
