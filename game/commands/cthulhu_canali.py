"""
Comandi dei canali OOC e della messaggistica privata (Fase K, settima
tornata): confermati verbatim dalla fonte (helps/ooc.txt) - vedi
world/canali.py per la creazione dei canali e le note sulle soglie.

Ogni canale ha un comando dedicato invece di affidarsi al sistema di
alias personali di Evennia (channel/alias): garantisce che la sintassi
esatta della fonte (es. "GOSSIP <messaggio>", "- <messaggio>") funzioni
subito per chiunque, senza bisogno di configurazione manuale.

TELL: la fonte lo descrive come comando a se' per la messaggistica
privata, ma il nostro porting ha GIA' un PAGE/TELL completo (con
cronologia, invio multiplo, notifica di destinatario offline -
commands/cthulhu_comms.py, Fase C) con "tell" gia' registrato come suo
alias - costruirne uno nuovo qui avrebbe creato un comando duplicato in
conflitto (scoperto testando: Evennia segnalava un'ambiguita' "tell-1/
tell-2" all'invocazione). Qui si aggiungono solo REPLY (mancante) e
IGNORE (mancante), entrambi pensati per lavorare CON il PAGE esistente.
"""

from evennia import Command
from evennia.commands.default.muxcommand import MuxCommand

from world.canali import trova_canale


class _CmdCanale(MuxCommand):
    """Base per i comandi-scorciatoia dei singoli canali OOC.

    I canali di Evennia funzionano a livello di ACCOUNT (solo Account
    implementa l'hook at_pre_channel_msg richiesto da Channel.msg() -
    un Character no): iscrizione e controllo d'accesso usano quindi
    caller.account, mentre "senders" resta il Character per mostrare il
    nome del personaggio invece del nome dell'account nel messaggio."""

    nome_canale = None
    locks = "cmd:all()"
    help_category = "Comunicazioni"

    def func(self):
        caller = self.caller
        account = caller.account
        testo = self.args.strip()
        if not testo:
            self.msg(f"Uso: {self.key} <messaggio>")
            return
        canale = trova_canale(self.nome_canale)
        if not canale:
            self.msg(f"Il canale {self.nome_canale.upper()} non esiste.")
            return
        if not canale.access(account, "send"):
            self.msg("Non hai accesso a questo canale (livello insufficiente o non ancora disponibile).")
            return
        if not canale.has_connection(account):
            canale.connect(account)
        canale.msg(testo, senders=caller)


class CmdGossip(_CmdCanale):
    """
    parla sul canale GOSSIP, il canale OOC principale del gioco

    Uso:
      gossip <messaggio>
      . <messaggio>

    La fonte usa anche "OOC <messaggio>" come alias, ma nel nostro
    porting "ooc" e' gia' il comando per uscire dal personaggio
    (commands/cthulhu_account.py) - alias deliberatamente NON
    replicato per non spezzare quel comando, gia' piu' fondamentale.
    """

    key = "gossip"
    aliases = ["."]
    nome_canale = "gossip"


class CmdInvestigatorTalk(_CmdCanale):
    """
    parla sul canale INVESTIGATORTALK (riservato al 51o livello+)

    Uso:
      investigatortalk <messaggio>
      - <messaggio>
    """

    key = "investigatortalk"
    aliases = ["-"]
    nome_canale = "investigatortalk"


class CmdHero(_CmdCanale):
    """
    parla sul canale HERO (riservato al 101o livello+)

    Uso:
      hero <messaggio>
      + <messaggio>
    """

    key = "hero"
    aliases = ["+"]
    nome_canale = "hero"


class CmdRemTalk(_CmdCanale):
    """
    parla sul canale REMTALK (riservato a chi ha completato un remort)

    Uso:
      remtalk <messaggio>
      & <messaggio>
    """

    key = "remtalk"
    aliases = ["&"]
    nome_canale = "remtalk"


class CmdImmTalk(_CmdCanale):
    """
    parla sul canale IMMTALK (riservato allo staff)

    Uso:
      immtalk <messaggio>
    """

    key = "immtalk"
    nome_canale = "immtalk"


class CmdQuestion(_CmdCanale):
    """
    fai una domanda sul gioco (canale condiviso con ANSWER)

    Uso:
      question <messaggio>
      answer <messaggio>
    """

    key = "question"
    aliases = ["answer"]
    nome_canale = "question"


class CmdMusic(_CmdCanale):
    """
    parla/canta sul canale MUSIC

    Uso:
      music <messaggio>
    """

    key = "music"
    nome_canale = "music"


class CmdChat(MuxCommand):
    """
    parla con chiunque sia connesso, anche chi non si e' ancora autenticato

    Uso:
      chat <messaggio>

    Fase K, nona tornata: a differenza degli altri canali OOC di questo
    file, CHAT non e' un vero Canale Evennia (che richiederebbe un
    account autenticato) - raggiunge invece OGNI sessione connessa,
    incluse quelle ancora alla schermata di login (vedi
    world/chat_pre_login.py, commands/cthulhu_unloggedin.py per la
    controparte pre-login). Confermato dalla fonte come lo scopo esatto
    di questo canale: rispondere a chi sta ancora decidendo se giocare.
    """

    key = "chat"
    locks = "cmd:all()"
    help_category = "Comunicazioni"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: chat <messaggio>")
            return
        sessioni = caller.sessions.get()
        if not sessioni:
            return
        from world.chat_pre_login import invia_chat
        invia_chat(sessioni[0], self.args.strip())


class CmdChannels(Command):
    """
    mostra lo stato dei canali di comunicazione

    Uso:
      channels
    """

    key = "channels"
    aliases = ["canali"]
    locks = "cmd:all()"
    help_category = "Comunicazioni"

    def func(self):
        self.caller.execute_cmd("channel/all")


class CmdQuiet(Command):
    """
    silenzia tutti i tuoi canali OOC in un colpo solo

    Uso:
      quiet
    """

    key = "quiet"
    locks = "cmd:all()"
    help_category = "Comunicazioni"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        account = caller.account
        from evennia.comms.models import ChannelDB
        canali = [c for c in ChannelDB.objects.get_all_channels() if c.has_connection(account)]
        if not canali:
            caller.msg("Non sei iscritto a nessun canale.")
            return
        for canale in canali:
            canale.mute(account)
        caller.msg("Hai silenziato tutti i tuoi canali OOC.")


class CmdReply(MuxCommand):
    """
    risponde all'ultima persona che ti ha scritto (PAGE/TELL)

    Uso:
      reply <messaggio>

    Scorciatoia confermata dalla fonte (helps/ooc.txt): risponde
    all'ultima persona che ti ha inviato un TELL. Riusa il comando
    PAGE/TELL gia' esistente (commands/cthulhu_comms.py, Fase C)
    invece di duplicarne la logica.
    """

    key = "reply"
    locks = "cmd:all()"
    help_category = "Comunicazioni"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: reply <messaggio>")
            return
        from evennia.comms.models import Msg
        account = caller.account
        ricevuti = Msg.objects.get_messages_by_receiver(account).order_by("-db_date_created")
        ultimo = next((m for m in ricevuti if m.senders), None)
        if not ultimo:
            caller.msg("Non hai ancora ricevuto nessun messaggio a cui rispondere.")
            return
        mittente = ultimo.senders[0]
        caller.execute_cmd(f"page {mittente.key} = {self.args.strip()}")


class CmdIgnore(MuxCommand):
    """
    blocca (o sblocca) i PAGE/TELL di un altro account

    Uso:
      ignore <nome>
      ignore <nome> clear
      ignore

    Confermato dalla fonte (helps/ooc.txt): blocca i messaggi di un
    account, con possibilita' di rimuovere il blocco in seguito se lo
    desideri. Il PAGE/TELL esistente (commands/cthulhu_comms.py) e' comunicazione
    tra ACCOUNT, non tra personaggi: la lista IGNORE vive quindi
    sull'account, non sul personaggio, per essere davvero rispettata li'.
    """

    key = "ignore"
    locks = "cmd:all()"
    help_category = "Comunicazioni"
    account_caller = True

    def func(self):
        caller = self.caller
        ignorati = caller.db.ignora or set()
        if not self.args:
            if not ignorati:
                caller.msg("Non stai ignorando nessuno.")
            else:
                caller.msg("Stai ignorando: " + ", ".join(sorted(ignorati)))
            return
        parti = self.args.split()
        nome = parti[0]
        if len(parti) > 1 and parti[1].lower() == "clear":
            ignorati.discard(nome)
            caller.db.ignora = ignorati
            caller.msg(f"Non ignori piu' '{nome}'.")
            return
        ignorati.add(nome)
        caller.db.ignora = ignorati
        caller.msg(f"Ora ignori '{nome}'.")
