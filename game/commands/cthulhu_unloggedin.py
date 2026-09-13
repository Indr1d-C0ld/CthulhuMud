"""
Localizzazione dei comandi della schermata di pre-login (Fase C, terza
tornata): sono le primissime cose che un nuovo giocatore vede prima
ancora di autenticarsi.

Le CHIAVI dei comandi (connect, create, quit, look, help, encoding,
screenreader, info) restano in inglese, seguendo la stessa convenzione
gia' adottata per i comandi da builder: sono parole-comando universali
nella tradizione MUD/telnet, note anche a chi non conosce l'italiano e
riportate cosi' in ogni guida esterna. Cio' che traduciamo sono i
messaggi e i testi di aiuto mostrati al nuovo utente.
"""

import datetime
import re
from codecs import lookup as codecs_lookup

from django.conf import settings

import evennia
from evennia.commands.cmdhandler import CMD_LOGINSTART
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils import class_from_module, gametime, utils

CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE


class CmdUnconnectedConnect(MuxCommand):
    """
    connettiti al gioco

    Uso (alla schermata di login):
      connect nomeaccount password
      connect "nome account" "pass word"

    Usa il comando create per creare prima un account, se non ne hai
    ancora uno.

    Se il tuo nome contiene spazi, racchiudilo tra virgolette doppie.
    """

    key = "connect"
    aliases = ["conn", "con", "co"]
    locks = "cmd:all()"
    arg_regex = r"\s.*?|$"

    def func(self):
        """
        Usa l'API admin di Django. Nota che i comandi non ancora
        autenticati hanno una posizione particolare: il loro func()
        riceve un oggetto Session invece di un source_object come tutti
        gli altri comandi (perche' non esiste ancora nessun oggetto
        prima che l'account abbia effettuato il login).
        """
        session = self.caller
        address = session.address

        args = self.args
        parts = [part.strip() for part in re.split(r"\"", args) if part.strip()]
        if len(parts) == 1:
            parts = parts[0].split(None, 1)

            if len(parts) == 1 and parts[0].lower() == "guest":
                Guest = class_from_module(settings.BASE_GUEST_TYPECLASS)

                account, errors = Guest.authenticate(ip=address)
                if account:
                    session.sessionhandler.login(session, account)
                    return
                else:
                    session.msg("|R%s|n" % "\n".join(errors))
                    return

        if len(parts) != 2:
            session.msg("\n\r Uso (senza <>): connect <nome> <password>")
            return

        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

        name, password = parts
        account, errors = Account.authenticate(
            username=name, password=password, ip=address, session=session
        )
        if account:
            # Fase K, ventesima tornata: WIZLOCK (helps/wizlock.txt) -
            # "prevents all non-Immortals from connecting to the game".
            from evennia.server.models import ServerConfig
            if ServerConfig.objects.conf("wizlock", default=False) and not account.check_permstring("Builder"):
                session.msg(
                    "|RIl gioco e' temporaneamente chiuso a chiunque non sia dello staff (WIZLOCK).|n"
                )
                return
            session.sessionhandler.login(session, account)
        else:
            session.msg("|R%s|n" % "\n".join(errors))


class CmdUnconnectedCreate(MuxCommand):
    """
    crea un nuovo account

    Uso (alla schermata di login):
      create <nomeaccount> <password>
      create "nome account" "pass word"

    Crea un nuovo account.

    Se il tuo nome contiene spazi, racchiudilo tra virgolette doppie.
    """

    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"
    arg_regex = r"\s.*?|$"

    def at_pre_cmd(self):
        """Verifica che la creazione di account sia abilitata."""
        if not settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
            self.msg("La registrazione e' al momento disabilitata.")
            return True

        return super().at_pre_cmd()

    def func(self):
        """Esegue i controlli e crea l'account."""

        session = self.caller
        args = self.args.strip()

        address = session.address

        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

        parts = [part.strip() for part in re.split(r"\"", args) if part.strip()]
        if len(parts) == 1:
            parts = parts[0].split(None, 1)
        if len(parts) != 2:
            string = (
                "\n Uso (senza <>): create <nome> <password>"
                "\nSe <nome> o <password> contengono spazi, racchiudili tra virgolette doppie."
            )
            session.msg(string)
            return

        username, password = parts

        non_normalized_username = username
        username = Account.normalize_username(username)
        if non_normalized_username != username:
            session.msg(
                "Nota: il tuo nome utente e' stato normalizzato per togliere gli spazi e "
                "rimuovere caratteri che potrebbero risultare visivamente ambigui."
            )

        answer = yield (
            f"Vuoi creare un account '{username}' con password '{password}'."
            "\nE' quello che intendevi? [S]/N?"
        )
        if answer.lower() in ("n", "no"):
            session.msg(
                "Annullato. Se il tuo nome utente contiene spazi, racchiudilo tra virgolette."
            )
            return

        account, errors = Account.create(
            username=username, password=password, ip=address, session=session
        )
        if account:
            from world.notifiche import notifica_nuovo_account
            notifica_nuovo_account(username, address)
            string = "E' stato creato un nuovo account '%s'. Benvenuto!"
            if " " in username:
                string += (
                    "\n\nOra puoi accedere con il comando 'connect \"%s\" <la tua password>'."
                )
            else:
                string += "\n\nOra puoi accedere con il comando 'connect %s <la tua password>'."
            session.msg(string % (username, username))
        else:
            session.msg("|R%s|n" % "\n".join(errors))


class CmdUnconnectedQuit(MuxCommand):
    """
    esci quando sei nello stato non autenticato

    Uso:
      quit

    Manteniamo qui una versione diversa del comando quit per gli
    account non ancora connessi, per semplicita'. La versione per chi
    ha gia' effettuato il login e' un po' piu' complessa.
    """

    key = "quit"
    aliases = ["q", "qu"]
    locks = "cmd:all()"

    def func(self):
        """Chiude semplicemente la connessione."""
        session = self.caller
        session.sessionhandler.disconnect(session, "Arrivederci! Disconnessione in corso.")


class CmdUnconnectedLook(MuxCommand):
    """
    guarda quando sei nello stato non autenticato

    Uso:
      look

    Questa e' una versione non autenticata del comando look, per
    semplicita'.

    Viene chiamata dal server e mette in moto tutto quanto. Il suo unico
    compito e' mostrare la schermata di connessione.
    """

    key = CMD_LOGINSTART
    aliases = ["look", "l"]
    locks = "cmd:all()"

    def func(self):
        """Mostra la schermata di connessione."""

        callables = utils.callables_from_module(CONNECTION_SCREEN_MODULE)
        if "connection_screen" in callables:
            connection_screen = callables["connection_screen"]()
        else:
            connection_screen = utils.random_string_from_module(CONNECTION_SCREEN_MODULE)
            if not connection_screen:
                connection_screen = "Nessuna schermata di connessione trovata. Contatta un admin."
        self.msg(connection_screen)


class CmdUnconnectedHelp(MuxCommand):
    """
    ottieni aiuto quando sei nello stato non connesso

    Uso:
      help

    Questa e' una versione non autenticata del comando help, per
    semplicita'. Mostra un riquadro informativo.
    """

    key = "help"
    aliases = ["h", "?"]
    locks = "cmd:all()"

    def func(self):
        """Mostra l'aiuto."""

        string = """
Non hai ancora effettuato il login al gioco. Comandi disponibili a questo punto:

  |wcreate|n - crea un nuovo account
  |wconnect|n - connettiti con un account esistente
  |wlook|n - mostra di nuovo la schermata di connessione
  |whelp|n - mostra questo aiuto
  |wencoding|n - cambia la codifica del testo per farla corrispondere al tuo client
  |wscreenreader|n - rendi il server piu' adatto all'uso con screen reader
  |wquit|n - interrompi la connessione

Prima crea un account, es. con |wcreate Anna c67jHL8p|n
(Se il tuo nome contiene spazi, usa le virgolette doppie: |wcreate "Anna la Barbara" c67jHL8p|n)
Poi puoi connetterti al gioco: |wconnect Anna c67jHL8p|n

Puoi usare il comando |wlook|n se vuoi rivedere la schermata di connessione.

"""

        if settings.STAFF_CONTACT_EMAIL:
            string += "Per assistenza, contatta: %s" % settings.STAFF_CONTACT_EMAIL
        self.msg(string)


class CmdUnconnectedEncoding(MuxCommand):
    """
    imposta quale codifica del testo usare nello stato non connesso

    Uso:
      encoding/switch [<codifica>]

    Switch:
      clear - cancella la tua codifica personalizzata

    Imposta la codifica del testo per comunicare con Evennia. E' un
    problema soprattutto se vuoi usare caratteri non-ASCII (cioe'
    lettere/simboli non presenti nell'inglese). Se vedi che i tuoi
    caratteri sembrano strani (o ricevi errori di codifica), dovresti
    usare questo comando per impostare la codifica del server sulla
    stessa usata dal tuo programma client.

    Codifiche comuni sono utf-8 (default), latin-1, ISO-8859-1 ecc.

    Se non indichi una codifica, verra' mostrata quella attuale.
    """

    key = "encoding"
    aliases = "encode"
    locks = "cmd:all()"

    def func(self):
        """Imposta la codifica."""

        if self.session is None:
            return

        sync = False
        if "clear" in self.switches:
            old_encoding = self.session.protocol_flags.get("ENCODING", None)
            if old_encoding:
                string = "La tua codifica del testo personalizzata ('%s') e' stata cancellata." % (
                    old_encoding
                )
            else:
                string = "Non era impostata nessuna codifica personalizzata."
            self.session.protocol_flags["ENCODING"] = "utf-8"
            sync = True
        elif not self.args:
            pencoding = self.session.protocol_flags.get("ENCODING", None)
            string = ""
            if pencoding:
                string += (
                    "Codifica predefinita: |g%s|n (cambiala con |wencoding <codifica>|n)"
                    % pencoding
                )
            encodings = settings.ENCODINGS
            if encodings:
                string += (
                    "\nCodifiche alternative del server (provate in quest'ordine):\n   |g%s|n"
                    % ", ".join(encodings)
                )
            if not string:
                string = "Nessuna codifica trovata."
        else:
            old_encoding = self.session.protocol_flags.get("ENCODING", None)
            encoding = self.args
            try:
                codecs_lookup(encoding)
            except LookupError:
                string = (
                    "|rLa codifica '|w%s|r' non e' valida. Mantengo la codifica precedente"
                    " '|w%s|r'.|n" % (encoding, old_encoding)
                )
            else:
                self.session.protocol_flags["ENCODING"] = encoding
                string = "La tua codifica del testo personalizzata e' cambiata da '|w%s|n' a '|w%s|n'." % (
                    old_encoding,
                    encoding,
                )
                sync = True
        if sync:
            self.session.sessionhandler.session_portal_sync(self.session)
        self.msg(string.strip())


class CmdUnconnectedScreenreader(MuxCommand):
    """
    attiva la modalita' screenreader

    Uso:
        screenreader

    Usato per attivare/disattivare la modalita' screenreader prima del
    login (una volta autenticato, usa option screenreader on).
    """

    key = "screenreader"

    def func(self):
        """Inverte l'impostazione screenreader."""
        new_setting = not self.session.protocol_flags.get("SCREENREADER", False)
        self.session.protocol_flags["SCREENREADER"] = new_setting
        string = "Modalita' screenreader %s." % ("attivata" if new_setting else "disattivata")
        self.msg(string)
        self.session.sessionhandler.session_portal_sync(self.session)


class CmdUnconnectedChat(MuxCommand):
    """
    parla con chiunque sia connesso, anche prima di autenticarti

    Uso:
      chat <messaggio>

    Confermato dalla fonte (helps/ooc.txt): il canale CHAT serve a
    rispondere alle domande di chi sta ancora decidendo se giocare, prima
    ancora di aver creato un account. Raggiunge chiunque sia connesso in
    quel momento, autenticato o no.
    """

    key = "chat"
    locks = "cmd:all()"

    def func(self):
        if not self.args.strip():
            self.msg("Uso: chat <messaggio>")
            return
        from world.chat_pre_login import invia_chat
        invia_chat(self.session, self.args.strip())


class CmdUnconnectedInfo(MuxCommand):
    """
    Fornisce l'output MUDINFO, cosi' i giochi Evennia possono essere
    aggiunti a Mudconnector e Mudstats. Purtroppo la specifica MUDINFO
    sembra essere sparita dalla rete, ma e' ancora usata da alcuni
    crawler. Questa implementazione e' stata creata guardando quella di
    MUX2, TinyMUSH, Rhost e PennMUSH.
    """

    key = "info"
    locks = "cmd:all()"

    def func(self):
        self.msg(
            "## BEGIN INFO 1.1\nName: %s\nUptime: %s\nConnected: %d\nVersion: Evennia %s\n## END"
            " INFO"
            % (
                settings.SERVERNAME,
                datetime.datetime.fromtimestamp(gametime.SERVER_START_TIME).ctime(),
                evennia.SESSION_HANDLER.account_count(),
                utils.get_evennia_version(),
            )
        )
