"""
Canali OOC (Fase K, settima tornata): confermati dalla fonte
(helps/ooc.txt) - "l'ultima grande lacuna esplicitamente rimandata"
(vedi commands/cthulhu_channels.py, Fase C, quarta tornata: la
localizzazione del comando @channel di Evennia era gia' pronta, ma
nessun canale reale esisteva).

Canali confermati verbatim dalla fonte, con soglie/permessi:
- GOSSIP: il canale primario, aperto a tutti (alias anche OOC o ".").
- INVESTIGATORTALK: solo dal 51o livello (alias "-").
- HERO: solo dal 101o livello (alias "+").
- REMTALK: riservato a chi ha completato un remort (alias "&") - il
  sistema di remort e' stato costruito in Fase K, nona tornata (comando
  staff REMORT, vedi world/remort.py): il canale e' ora davvero
  raggiungibile da chi ha remortato almeno una volta.
- IMMTALK: riservato agli Immortali (qui: permesso Builder+).
- QUESTION/ANSWER: stesso canale, due nomi diversi per lo stesso scopo.
- MUSIC: canale per chi vuole cantare (si lega bene alla skill Musica
  gia' esistente).
- CHAT (pre-login, "used for answering questions of curious people who
  are checking out the game"): risolto in Fase K, nona tornata - non e'
  un vero Canale Evennia (impossibile prima del login) ma un broadcast
  diretto a livello di Session (vedi world/chat_pre_login.py,
  commands/cthulhu_unloggedin.py:CmdUnconnectedChat per la schermata di
  login, commands/cthulhu_canali.py:CmdChat per chi e' gia' in gioco).

TELL/REPLY/IGNORE non sono canali Evennia ma messaggistica diretta
(vedi commands/cthulhu_channels_extra.py).
"""

CANALI = [
    ("gossip", ["ooc", "."], "Il canale primario per chiacchierare con tutti i giocatori.",
     "send:all();listen:all()"),
    ("investigatortalk", ["-"], "Canale riservato ai personaggi di almeno 51o livello.",
     "send:livello_minimo(51);listen:livello_minimo(51)"),
    ("hero", ["+"], "Canale riservato ai personaggi di almeno 101o livello.",
     "send:livello_minimo(101);listen:livello_minimo(101)"),
    ("remtalk", ["&"], "Canale riservato a chi ha completato un remort.",
     "send:e_remortato();listen:e_remortato()"),
    ("immtalk", [], "Canale riservato agli Immortali.",
     "send:perm(Builder);listen:perm(Builder)"),
    ("question", ["answer"], "Canale per fare domande sul gioco (e rispondere).",
     "send:all();listen:all()"),
    ("music", [], "Canale per chi non resiste all'impulso di cantare.",
     "send:all();listen:all()"),
]


def crea_canali():
    """Idempotente: crea tutti i canali se non esistono gia'."""
    from evennia.comms.models import ChannelDB
    from evennia.utils import create

    creati = []
    for nome, alias, descrizione, lock in CANALI:
        if ChannelDB.objects.filter(db_key__iexact=nome):
            continue
        canale = create.create_channel(nome, aliases=alias, desc=descrizione, locks=lock)
        creati.append(canale)
    return creati


def trova_canale(nome):
    from evennia.comms.models import ChannelDB
    return ChannelDB.objects.filter(db_key__iexact=nome).first()


def iscrivi_a_gossip(account):
    """Iscrive automaticamente un account al canale GOSSIP, il canale
    'primario' secondo la fonte - da chiamare dalla chargen. Crea i
    canali al volo se non esistono ancora (idempotente): evita di dover
    ricordare un passaggio di bootstrap manuale separato, a differenza
    di altri sistemi globali di questo progetto.

    NOTA IMPORTANTE: i canali di Evennia si basano sull'ACCOUNT, non sul
    Character (solo Account implementa l'hook at_pre_channel_msg
    richiesto da Channel.msg()) - per questo la funzione vuole
    direttamente un Account, non un personaggio.

    Bug reale scoperto testando dal vivo via telnet (Fase K,
    ventunesima tornata): in precedenza si passava il personaggio
    appena creato e si leggeva il suo .account - ma durante il chargen
    (world/chargen_menu.py:menunode_fine) il personaggio non e' ancora
    "puppettato" da nessuno (lo diventa solo DOPO che il menu si
    chiude, vedi ContribCmdCharCreate.finish_char_callback), quindi
    personaggio.account era sempre None e l'iscrizione non avveniva
    mai - ne' con questa implementazione ne' con quella precedente
    (commands/cthulhu_account.py, rimossa nella ventesima tornata) che
    soffriva dello stesso problema. Il chiamante nel chargen ora passa
    l'account della SESSIONE (sempre valido, dato che si e' gia'
    autenticati) invece del personaggio."""
    crea_canali()
    canale = trova_canale("gossip")
    if canale and account and not canale.has_connection(account):
        canale.connect(account)
