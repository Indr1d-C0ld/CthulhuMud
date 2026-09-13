"""
Localizzazione dei comandi da admin/moderazione (Fase C, quarta tornata):
boot, ban/unban, emit/pemit/remit, userpassword, perm, wall, force.

Usati solo da chi modera il gioco (te), ma tradotti per coerenza e
completezza con tutto il resto gia' fatto.
"""

import re
import time

from django.conf import settings

import evennia
from evennia.commands.default.muxcommand import MuxCommand
from evennia.server.models import ServerConfig
from evennia.utils import logger, search

PERMISSION_HIERARCHY = [p.lower() for p in settings.PERMISSION_HIERARCHY]

IPREGEX = re.compile(r"[0-9*]{1,3}\.[0-9*]{1,3}\.[0-9*]{1,3}\.[0-9*]{1,3}")


def list_bans(cmd, banlist):
    """Funzione di supporto per mostrare l'elenco dei ban attivi."""
    if not banlist:
        return "Non e' stato trovato nessun ban attivo."

    table = cmd.styled_table("|wid", "|wnome/ip", "|wdata", "|wmotivo")
    for inum, ban in enumerate(banlist):
        table.add_row(str(inum + 1), ban[0] and ban[0] or ban[1], ban[3], ban[4])
    return f"|wBan attivi:|n\n{table}"


class CmdBoot(MuxCommand):
    """
    espelli un account dal server

    Uso
      boot[/switch] <account> [: motivo]

    Switch:
      quiet - espelle senza avvisare l'account
      sid - espelle per id di sessione invece che per nome o dbref

    Espelle un account dal server. Se viene fornito un motivo, verra'
    mostrato all'utente a meno che non sia impostato /quiet.
    """

    key = "boot"
    switch_options = ("quiet", "sid")
    locks = "cmd:perm(boot) or perm(Admin)"
    help_category = "Amministrazione"

    def func(self):
        """Implementa la funzione."""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("Uso: boot[/switch] <account> [:motivo]")
            return

        if ":" in args:
            args, reason = [a.strip() for a in args.split(":", 1)]
        else:
            args, reason = args, ""

        boot_list = []

        if "sid" in self.switches:
            sessions = evennia.SESSION_HANDLER.get_sessions(True)
            for sess in sessions:
                if sess.sessid == int(args):
                    boot_list.append(sess)
                    break
        else:
            pobj = search.account_search(args)
            if not pobj:
                caller.msg(f"L'account {args} non e' stato trovato.")
                return
            pobj = pobj[0]
            if not pobj.access(caller, "boot"):
                caller.msg(f"Non hai il permesso di espellere {pobj.key}.")
                return
            matches = evennia.SESSION_HANDLER.sessions_from_account(pobj)
            for match in matches:
                boot_list.append(match)

        if not boot_list:
            caller.msg("Nessuna sessione corrispondente trovata. L'account non sembra essere online.")
            return

        feedback = None
        if "quiet" not in self.switches:
            feedback = f"Sei stato disconnesso da {caller.name}.\n"
            if reason:
                feedback += f"\nMotivo indicato: {reason}"

        for session in boot_list:
            session.msg(feedback)
            session.account.disconnect_session_from_account(session)

        if pobj and boot_list:
            logger.log_sec(
                f"Booted: {pobj} (Reason: {reason}, Caller: {caller}, IP: {self.session.address})."
            )


class CmdBan(MuxCommand):
    """
    banna un account dal server

    Uso:
      ban [<nome o ip> [: motivo]]

    Senza argomenti, mostra l'elenco numerato dei ban attivi.

    Questo comando impedisce a un utente di accedere al gioco. Fornisci
    opzionalmente un motivo per poterti ricordare in seguito perche' e'
    stato messo in atto il ban.

    Spesso e' preferibile bannare un account dal server piuttosto che
    eliminarlo con accounts/delete. Se bannato per nome, quell'account
    non potra' piu' effettuare il login.

    Il ban per indirizzo IP permette di bloccare tutti gli accessi da un
    indirizzo o una sottorete specifica. Usa un asterisco (*) come
    carattere jolly.

    Esempi:
      ban thomas             - banna l'account 'thomas'
      ban/ip 134.233.2.111   - banna un indirizzo ip specifico
      ban/ip 134.233.2.*     - banna un'intera sottorete
      ban/ip 134.233.*.*     - un ban ancora piu' ampio

    Un singolo filtro IP puo' essere facilmente aggirato cambiando
    computer o richiedendo un nuovo indirizzo IP. Impostare un filtro IP
    ampio con caratteri jolly puo' essere allettante, ma ricorda che
    potrebbe bloccare per errore anche utenti innocenti che si
    connettono dallo stesso paese o regione.
    """

    key = "ban"
    aliases = ["bans"]
    locks = "cmd:perm(ban) or perm(Developer)"
    help_category = "Amministrazione"

    def func(self):
        """
        I ban sono salvati in un oggetto serverconf come lista di
        tuple: [ (nome, ip, ipregex, data, motivo), ...  ] dove nome e
        ip sono impostati dall'utente e mostrati negli elenchi. ipregex
        e' una forma convertita dell'ip dove * e' sostituito da un
        pattern regex appropriato per un confronto rapido. data e' il
        timestamp di quando il ban e' stato attivato e 'motivo' e'
        qualsiasi informazione opzionale fornita al comando. I valori
        non impostati in ogni tupla sono impostati come stringa vuota.
        """
        banlist = ServerConfig.objects.conf("server_bans")
        if not banlist:
            banlist = []

        if not self.args or (
            self.switches and not any(switch in ("ip", "name") for switch in self.switches)
        ):
            self.msg(list_bans(self, banlist))
            return

        now = time.ctime()
        reason = ""
        if ":" in self.args:
            ban, reason = self.args.rsplit(":", 1)
        else:
            ban = self.args
        ban = ban.lower()
        ipban = IPREGEX.findall(ban)
        if not ipban:
            typ = "Nome"
            bantup = (ban, "", "", now, reason)
        else:
            typ = "IP"
            ban = ipban[0]
            ipregex = ban.replace(".", r"\.")
            ipregex = ipregex.replace("*", "[0-9]{1,3}")
            ipregex = re.compile(r"%s" % ipregex)
            bantup = ("", ban, ipregex, now, reason)

        ret = yield (f"Sei sicuro di voler bannare per {typ} '|w{ban}|n' [S]/N?")
        if str(ret).lower() in ("no", "n"):
            self.msg("Annullato.")
            return

        banlist.append(bantup)
        ServerConfig.objects.conf("server_bans", banlist)
        self.msg(f"Il ban per {typ} '|w{ban}|n' e' stato aggiunto. Usa |wunban|n per rimuoverlo.")
        logger.log_sec(
            f"Banned {typ}: {ban.strip()} (Caller: {self.caller}, IP: {self.session.address})."
        )


class CmdUnban(MuxCommand):
    """
    rimuove un ban da un account

    Uso:
      unban <idban>

    Rimuove un ban su nome/ip account precedentemente impostato con il
    comando ban. Usa questo comando senza argomenti per vedere l'elenco
    numerato dei ban. Usa i numeri di questo elenco per scegliere quale
    rimuovere.
    """

    key = "unban"
    locks = "cmd:perm(unban) or perm(Developer)"
    help_category = "Amministrazione"

    def func(self):
        """Implementa la rimozione del ban."""

        banlist = ServerConfig.objects.conf("server_bans")

        if not self.args:
            self.msg(list_bans(self, banlist))
            return

        try:
            num = int(self.args)
        except Exception:
            self.msg("Devi fornire un id di ban valido da rimuovere.")
            return

        if not banlist:
            self.msg("Non ci sono ban da rimuovere.")
        elif not (0 < num < len(banlist) + 1):
            self.msg(f"Il ban con id |w{self.args}|n non e' stato trovato.")
        else:
            ban = banlist[num - 1]
            value = (" ".join([s for s in ban[:2]])).strip()

            ret = yield (f"Sei sicuro di voler rimuovere il ban {num}: '|w{value}|n' [S]/N?")
            if str(ret).lower() in ("n", "no"):
                self.msg("Annullato.")
                return

            del banlist[num - 1]
            ServerConfig.objects.conf("server_bans", banlist)
            self.msg(f"Rimosso il ban {num}: '{value}'")
            logger.log_sec(
                f"Unbanned: {value.strip()} (Caller: {self.caller}, IP: {self.session.address})."
            )


class CmdEmit(MuxCommand):
    """
    comando da admin per emettere un messaggio verso piu' oggetti

    Uso:
      emit[/switch] [<obj>, <obj>, ... =] <messaggio>
      remit           [<obj>, <obj>, ... =] <messaggio>
      pemit           [<obj>, <obj>, ... =] <messaggio>

    Switch:
      room     -  limita l'emissione alle sole stanze (default)
      accounts -  limita l'emissione ai soli account
      contents -  invia anche al contenuto degli oggetti trovati

    Emette un messaggio verso gli oggetti selezionati o verso i tuoi
    immediati dintorni. Se l'oggetto e' una stanza, lo invia al suo
    contenuto. remit e pemit sono solo forme limitate di emit, per
    inviare rispettivamente a stanze e ad account.
    """

    key = "emit"
    aliases = ["pemit", "remit"]
    switch_options = ("room", "accounts", "contents")
    locks = "cmd:perm(emit) or perm(Builder)"
    help_category = "Amministrazione"

    def func(self):
        """Implementa il comando."""

        caller = self.caller
        args = self.args

        if not args:
            string = "Uso: "
            string += "\nemit[/switch] [<obj>, <obj>, ... =] <messaggio>"
            string += "\nremit           [<obj>, <obj>, ... =] <messaggio>"
            string += "\npemit           [<obj>, <obj>, ... =] <messaggio>"
            caller.msg(string)
            return

        rooms_only = "rooms" in self.switches
        accounts_only = "accounts" in self.switches
        send_to_contents = "contents" in self.switches

        if self.cmdstring == "remit":
            rooms_only = True
            send_to_contents = True
        elif self.cmdstring == "pemit":
            accounts_only = True

        if not self.rhs:
            message = self.args
            objnames = [caller.location.key]
        else:
            message = self.rhs
            objnames = self.lhslist

        for objname in objnames:
            obj = caller.search(objname, global_search=True)
            if not obj:
                return
            if rooms_only and obj.location is not None:
                caller.msg(f"{objname} non e' una stanza. Ignorato.")
                continue
            if accounts_only and not obj.has_account:
                caller.msg(f"{objname} non ha un account attivo. Ignorato.")
                continue
            if obj.access(caller, "tell"):
                obj.msg(message)
                if send_to_contents and hasattr(obj, "msg_contents"):
                    obj.msg_contents(message)
                    caller.msg(f"Emesso verso {objname} e il suo contenuto:\n{message}")
                else:
                    caller.msg(f"Emesso verso {objname}:\n{message}")
            else:
                caller.msg(f"Non hai il permesso di emettere verso {objname}.")


class CmdNewPassword(MuxCommand):
    """
    cambia la password di un account

    Uso:
      userpassword <oggetto utente> = <nuova password>

    Imposta la password di un account.
    """

    key = "userpassword"
    locks = "cmd:perm(newpassword) or perm(Admin)"
    help_category = "Amministrazione"

    def func(self):
        """Implementa la funzione."""

        caller = self.caller

        if not self.rhs:
            self.msg("Uso: userpassword <oggetto utente> = <nuova password>")
            return

        account = caller.search_account(self.lhs)
        if not account:
            return

        newpass = self.rhs

        validated, error = account.validate_password(newpass)
        if not validated:
            errors = [e for suberror in error.messages for e in error.messages]
            string = "\n".join(errors)
            caller.msg(string)
            return

        account.set_password(newpass)
        account.save()
        self.msg(f"{account.name} - nuova password impostata a '{newpass}'.")
        if account.character != caller:
            account.msg(f"{caller.name} ha cambiato la tua password in '{newpass}'.")
        logger.log_sec(
            f"Password Changed: {account} (Caller: {caller}, IP: {self.session.address})."
        )


class CmdPerm(MuxCommand):
    """
    imposta i permessi di un account/oggetto

    Uso:
      perm[/switch] <oggetto> [= <permesso>[,<permesso>,...]]
      perm[/switch] *<account> [= <permesso>[,<permesso>,...]]

    Switch:
      del     -  elimina il permesso indicato da <oggetto> o <account>.
      account -  imposta il permesso su un account (equivale ad
                 aggiungere * al nome)

    Questo comando imposta/rimuove singole stringhe di permesso su un
    oggetto o account. Se non viene indicato nessun permesso, elenca
    tutti i permessi su <oggetto>.
    """

    key = "perm"
    aliases = "setperm"
    switch_options = ("del", "account")
    locks = "cmd:perm(perm) or perm(Developer)"
    help_category = "Amministrazione"

    def func(self):
        """Implementa la funzione."""

        caller = self.caller
        switches = self.switches
        lhs, rhs = self.lhs, self.rhs

        if not self.args:
            string = "Uso: perm[/switch] oggetto [ = permesso, permesso, ...]"
            caller.msg(string)
            return

        accountmode = "account" in self.switches or lhs.startswith("*")
        lhs = lhs.lstrip("*")

        if accountmode:
            obj = caller.search_account(lhs)
        else:
            obj = caller.search(lhs, global_search=True)
        if not obj:
            return

        if not rhs:
            if not obj.access(caller, "examine"):
                caller.msg("Non hai il permesso di esaminare questo oggetto.")
                return

            string = f"Permessi su |w{obj.key}|n: "
            if not obj.permissions.all():
                string += "<Nessuno>"
            else:
                string += ", ".join(obj.permissions.all())
                if (
                    hasattr(obj, "account")
                    and hasattr(obj.account, "is_superuser")
                    and obj.account.is_superuser
                ):
                    string += "\n(... ma questo oggetto e' attualmente controllato da un SUPERUSER! "
                    string += "Tutti i controlli di accesso vengono superati automaticamente.)"
            caller.msg(string)
            return

        locktype = "edit" if accountmode else "control"
        if not obj.access(caller, locktype):
            accountstr = "account" if accountmode else "oggetto"
            caller.msg(f"Non hai il permesso di modificare i permessi di questo {accountstr}.")
            return

        caller_result = []
        target_result = []
        if "del" in switches:
            for perm in self.rhslist:
                obj.permissions.remove(perm)
                if obj.permissions.get(perm):
                    caller_result.append(
                        f"\nNon e' stato possibile rimuovere il permesso {perm} da {obj.name}."
                    )
                else:
                    caller_result.append(
                        f"\nPermesso {perm} rimosso da {obj.name} (se esisteva)."
                    )
                    target_result.append(
                        f"\n{caller.name} ti revoca il/i permesso/i {perm}."
                    )
                    logger.log_sec(
                        f"Permissions Deleted: {perm}, {obj} (Caller: {caller}, IP: {self.session.address})."
                    )
        else:
            permissions = obj.permissions.all()

            for perm in self.rhslist:
                if perm.lower() in PERMISSION_HIERARCHY and not obj.locks.check_lockstring(
                    caller, f"dummy:perm({perm})"
                ):
                    caller.msg(
                        "Non puoi assegnare un permesso superiore a quello che hai tu stesso."
                    )
                    return

                if perm in permissions:
                    caller_result.append(f"\nIl permesso '{perm}' e' gia' definito su {obj.name}.")
                else:
                    obj.permissions.add(perm)
                    plystring = "l'Account" if accountmode else "l'Oggetto/Personaggio"
                    caller_result.append(
                        f"\nPermesso '{perm}' assegnato a {obj.name} ({plystring})."
                    )
                    target_result.append(
                        f"\n{caller.name} ti da' ({obj.name}, {plystring}) il permesso '{perm}'."
                    )
                    logger.log_sec(
                        f"Permissions Added: {perm}, {obj} (Caller: {caller}, IP: {self.session.address})."
                    )

        caller.msg("".join(caller_result).strip())
        if target_result:
            obj.msg("".join(target_result).strip())


class CmdWall(MuxCommand):
    """
    fai un annuncio a tutti

    Uso:
      wall <messaggio>

    Annuncia un messaggio a tutte le sessioni connesse, incluse quelle
    non ancora autenticate.
    """

    key = "wall"
    locks = "cmd:perm(wall) or perm(Admin)"
    help_category = "Amministrazione"

    def func(self):
        """Implementa il comando."""
        if not self.args:
            self.msg("Uso: wall <messaggio>")
            return
        message = f'{self.caller.name} urla "{self.args}"'
        self.msg("Annuncio a tutte le sessioni connesse...")
        evennia.SESSION_HANDLER.announce_all(message)


class CmdForce(MuxCommand):
    """
    costringe un oggetto a eseguire un comando

    Uso:
        force <oggetto>=<stringa di comando>

    Esempio:
        force bob=get bastone
    """

    key = "force"
    locks = "cmd:perm(spawn) or perm(Builder)"
    help_category = "Costruzione"
    perm_used = "edit"

    def func(self):
        """Implementa il comando force."""
        if not self.lhs or not self.rhs:
            self.msg("Devi fornire un bersaglio e una stringa di comando da eseguire.")
            return
        targ = self.caller.search(self.lhs)
        if not targ:
            return
        if not targ.access(self.caller, self.perm_used):
            self.msg(f"Non hai il permesso di costringere {targ} a eseguire comandi.")
            return
        targ.execute_cmd(self.rhs)
        self.msg(f"Hai costretto {targ} a: {self.rhs}")
