"""
Nomi italiani dei comandi (fase 1 della traduzione dell'interfaccia).

PERCHE' QUESTO MODULO ESISTE
----------------------------
Il gioco e' interamente in italiano - stanze, oggetti, messaggi, aiuti -
tranne i nomi dei comandi, ereditati dalla fonte inglese. Per chi arriva
da zero e' proprio quello lo scoglio: non le regole, ma dover sapere che
per guardarsi intorno si scrive LOOK e non GUARDA.

Qui si aggiunge un nome italiano a ogni comando di gioco. I nomi inglesi
NON vengono toccati: restano chiavi valide, cosi' nulla di cio' che
funziona oggi smette di funzionare, e chi ha gia' la memoria delle dita
non deve reimpararla. Un alias non sostituisce, si affianca.

QUELLO CHE C'ERA GIA'
---------------------
Lo strato italiano non parte da zero: 58 dei 163 comandi di gioco avevano
gia' un alias, e molti erano gia' italiani (saldo, compra, deposita,
mangia, bevi, forgia, ripara, orari, cambia, sogna, canali, genere) - uno
(alloggia) ha perfino il nome principale in italiano. Questo modulo
completa uno schema gia' avviato e collaudato, non ne inventa uno nuovo.

IL RISCHIO DA TENERE A BADA
---------------------------
In Evennia il cmdset di un'uscita ha priorita' 101, quello del
personaggio 0: **un'uscita vince sempre su un comando che si chiama allo
stesso modo**. Se un alias qui sotto si chiamasse come un'uscita del
mondo (per esempio "fuori" o "infermeria"), quel comando smetterebbe di
funzionare in ogni stanza che ha quell'uscita - e smetterebbe in
silenzio, senza alcun messaggio d'errore.

Per questo esiste verifica_collisioni(), che confronta gli alias con i
nomi delle uscite realmente presenti nel mondo e con i nomi gia'
occupati nei cmdset. L'audit la esegue: se un domani qualcuno aggiunge
un'uscita chiamata "guarda", il controllo lo segnala prima che diventi
un difetto silenzioso.

La corrispondenza in Evennia e' ESATTA su chiave e alias (nessuna
abbreviazione automatica), quindi aggiungere nomi non introduce
ambiguita': puo' solo creare collisioni esatte, che sono appunto cio'
che il controllo cerca.

DESCRIZIONI E CATEGORIE
-----------------------
Qui NON si duplicano le descrizioni: sono gia' in italiano nelle
docstring dei comandi, e il prontuario (commands/cthulhu_prontuario.py)
le legge da li'. Una sola fonte di verita', che non puo' divergere.
"""

# chiave inglese del comando -> nomi italiani da aggiungere.
# Piu' di un nome quando esiste sia una forma naturale sia
# un'abbreviazione comoda.
ALIAS_ITALIANI = {
    # ---------------------------------------------------------- generale
    "access": ("accesso",),
    "autogold": ("autooro",),
    "autokill": ("autouccidi",),
    "autolist": ("autoelenco",),
    "autoloot": ("autobottino",),
    "autosac": ("autosacrificio",),
    "backstab": ("pugnala",),
    "bash": ("travolgi",),
    "bite": ("mordi",),
    # "taglie" e' un'uscita del Riformatorio di Dylath-Leen verso
    # l'Ufficio Taglie: l'avrebbe oscurato. Trovato da verifica_collisioni().
    "bounty": ("cacciataglie",),
    "clan": ("societa",),
    "deed": ("imprese",),
    "deliver": ("consegna",),
    "dirt": ("polvere",),
    "disarm": ("disarma",),
    "drop": ("lascia",),
    "ed": ("scenografia",),
    "equipment": ("equipaggiamento",),
    "get": ("prendi",),
    "give": ("dai",),
    "gunsmith": ("armaiolo",),
    "help": ("aiuto",),
    "home": ("casa",),
    "inventory": ("inventario",),
    "kick": ("calcia",),
    "lineage": ("lignaggio",),
    "list": ("listino",),
    "look": ("guarda",),
    "mindtransfer": ("trasferiscimente",),
    # "missione" e' un'uscita di Via Federal Nord. Stesso motivo.
    "mission": ("missioni",),
    "money": ("denaro",),
    "murder": ("assassina",),
    "nick": ("soprannome",),
    "noloot": ("nonsaccheggiabile",),
    "pose": ("posa",),
    "privacy": ("riservatezza",),
    "quest": ("incarichi",),
    "remort": ("rinascita",),
    "remove": ("togli",),
    "return": ("ritorna",),
    "say": ("dici",),
    "setdesc": ("descriviti",),
    "subrace": ("sottorazza",),
    "trip": ("sgambetto",),
    "vampire": ("vampiro",),
    "were": ("licantropo",),
    "whisper": ("sussurra",),
    "worship": ("venera",),
    "yith": ("yithadatta",),
    "yithabduct": ("yithrapisci",),

    # -------------------------------------------------------- cthulhumud
    "affects": ("effetti",),
    "autoassist": ("autoassistenza",),
    "autosplit": ("autodividi",),
    "cast": ("lancia",),
    "close": ("chiudi",),
    "consider": ("valuta",),
    "cut": ("taglia",),
    "debate": ("dibatti",),
    "duel": ("duello",),
    "experience": ("esperienza",),
    "flee": ("fuggi",),
    "follow": ("segui",),
    "group": ("gruppo",),
    "gtell": ("gdici",),
    "kill": ("attacca",),
    "learn": ("impara",),
    "lock": ("serra",),
    "lore": ("conoscenza",),
    "nofollow": ("nonseguirmi",),
    "open": ("apri",),
    "order": ("ordina",),
    "pick": ("scassina",),
    "practice": ("esercitati",),
    "prof": ("professione",),
    "raffects": ("effettistanza",),
    "research": ("ricerca",),
    "righteouskill": ("colpogiusto",),
    "ritual": ("rituale",),
    "score": ("scheda",),
    # "abilita" e' invariabile in italiano: il plurale va alla forma piu'
    # usata (l'elenco), il singolare prende un nome esplicito.
    "skills": ("abilita",),
    "skill": ("infoabilita",),
    "spell": ("incantesimo",),
    "spells": ("incantesimi",),
    "split": ("dividi",),
    "tame": ("addomestica",),
    "time": ("ora",),
    "train": ("allena",),
    "unlock": ("apriserratura",),
    "use": ("usa",),
    "voodoo": ("bambola",),
    "wimpy": ("codardia",),

    # ------------------------------------------------------ comunicazioni
    "chat": ("chiacchiera",),
    "gossip": ("pettegolezzo",),
    "hero": ("eroe",),
    "ignore": ("ignora",),
    "immtalk": ("immparla",),
    "investigatortalk": ("investigatori",),
    "music": ("musica",),
    "question": ("domanda",),
    "quiet": ("silenzio",),
    "remtalk": ("remparla",),
    "reply": ("rispondi",),

    # --------------------------------------------------------------- staff
    "advance": ("avanza",),
    "bamfin": ("messaggioarrivo",),
    "bamfout": ("messaggiopartenza",),
    "cloak": ("mantello",),
    "freeze": ("congela",),
    "goto": ("vaia",),
    "holylight": ("lucesacra",),
    "incarnate": ("incarna",),
    "newlock": ("bloccanuovi",),
    "peace": ("pace",),
    "restore": ("ripristina",),
    "slay": ("annienta",),
    "switch": ("impersona",),
    "wizinvis": ("invisibilemago",),
    "wizlock": ("bloccaaccessi",),

    # ----------------------------------------------------- amministrazione
    "ban": ("bandisci",),
    "boot": ("espelli",),
    "emit": ("emetti",),
    "perm": ("permessi",),
    "unban": ("riammetti",),
    "userpassword": ("passwordutente",),
    "wall": ("annuncio",),

    # --------------------------------------------------------- costruzione
    "force": ("costringi",),
    "sethelp": ("modificaaiuto",),
    "unlink": ("scollega",),
}


def applica_alias_italiani(cmdset):
    """Aggiunge a ogni comando del cmdset i suoi alias italiani.

    Va chiamata in at_cmdset_creation(), DOPO aver aggiunto i comandi.

    Non basta appendere a `cmd.aliases`: Evennia costruisce da chiave e
    alias due strutture di ricerca (`_matchset` e `_keyaliases`) al
    momento della definizione della classe, ed e' su quelle che avviene
    la corrispondenza. Senza ricostruirle, gli alias nuovi resterebbero
    nell'elenco ma non verrebbero mai riconosciuti - il tipo di difetto
    che sembra funzionare finche' non lo si prova davvero.

    Idempotente: _init_command deduplica, quindi rilanciarla non fa
    danni. Ritorna il numero di comandi a cui e' stato aggiunto qualcosa.
    """
    from evennia.commands.command import _init_command

    toccati = 0
    for cmd in cmdset.commands:
        nuovi = ALIAS_ITALIANI.get(cmd.key)
        if not nuovi:
            continue
        cls = type(cmd)
        esistenti = list(cls.aliases or [])
        da_aggiungere = [a for a in nuovi if a not in esistenti]
        if not da_aggiungere:
            continue
        cls.aliases = esistenti + da_aggiungere
        _init_command(cls)          # ricostruisce _matchset e _keyaliases
        cmd.aliases = list(cls.aliases)
        cmd._matchset = cls._matchset
        cmd._keyaliases = cls._keyaliases
        toccati += 1
    return toccati


def verifica_collisioni():
    """Controlla che nessun alias italiano possa essere oscurato o
    oscurare qualcos'altro. Ritorna un elenco di problemi (vuoto = tutto
    a posto); pensata per essere chiamata dall'audit.

    Tre controlli:
      1. un alias che coincide con il nome di un'uscita del mondo
         sarebbe oscurato in ogni stanza che ha quell'uscita, perche' il
         cmdset di un'uscita ha priorita' 101 contro 0;
      2. un alias che coincide con una chiave o un alias gia' esistente
         creerebbe un doppione irrisolvibile;
      3. due comandi che chiedono lo stesso alias italiano.
    """
    import collections
    from world.socials_italiano import ALIAS_SOCIAL

    problemi = []

    # 3. doppioni interni alle tabelle (comandi + social insieme: sono
    #    tutti nomi che convivono nello stesso spazio del cmdset)
    tutti = [a for alias in ALIAS_ITALIANI.values() for a in alias]
    tutti += list(ALIAS_SOCIAL.values())
    usati = collections.Counter(tutti)
    for nome, n in usati.items():
        if n > 1:
            chi = [k for k, v in ALIAS_ITALIANI.items() if nome in v]
            chi += [k for k, v in ALIAS_SOCIAL.items() if v == nome]
            problemi.append(f"l'alias '{nome}' e' chiesto da piu' comandi: {sorted(chi)}")

    from commands import default_cmdsets
    cs = default_cmdsets.CharacterCmdSet()
    cs.at_cmdset_creation()

    # 2. collisioni con nomi gia' occupati (esclusi quelli che siamo noi
    #    ad aver aggiunto al comando giusto)
    proprietario = {}
    for cmd in cs.commands:
        for nome in [cmd.key] + list(cmd.aliases or []):
            proprietario.setdefault(nome.lower(), []).append(cmd.key)
    coppie = [(k, a) for k, alias in ALIAS_ITALIANI.items() for a in alias]
    coppie += list(ALIAS_SOCIAL.items())
    for chiave, nome in coppie:
        padroni = set(proprietario.get(nome, []))
        if padroni - {chiave}:
            problemi.append(
                f"l'alias '{nome}' di {chiave} e' gia' usato da: {sorted(padroni - {chiave})}")

    # 1. collisioni con le uscite del mondo
    from evennia.objects.models import ObjectDB
    uscite = collections.defaultdict(set)
    for e in ObjectDB.objects.filter(db_typeclass_path__endswith="exits.Exit"):
        uscite[e.db_key.lower()].add(e.db_location.key if e.db_location else "?")
        for a in (e.aliases.all() or []):
            uscite[a.lower()].add(e.db_location.key if e.db_location else "?")
    for chiave, nome in coppie:
        if nome in uscite:
            dove = sorted(uscite[nome])[:3]
            problemi.append(
                f"l'alias '{nome}' di {chiave} coincide con un'uscita "
                f"(sarebbe oscurato in: {dove}...)")
    return problemi


def copertura():
    """Quanti comandi di gioco hanno un nome italiano e quanti no.
    Ritorna (con_italiano, senza_italiano, elenco_senza)."""
    from commands import default_cmdsets
    from world.socials import SOCIALS

    cs = default_cmdsets.CharacterCmdSet()
    cs.at_cmdset_creation()
    soc = set(SOCIALS)
    gioco = [c for c in cs.commands if c.key not in soc and not c.key.startswith("@")]

    senza = []
    for c in gioco:
        nomi = set(ALIAS_ITALIANI.get(c.key, ())) | {c.key}
        # un comando "coperto" ha almeno un nome che non sia la sola
        # chiave inglese; i comandi gia' italiani di loro contano.
        if not ALIAS_ITALIANI.get(c.key) and not _sembra_italiano(c):
            senza.append(c.key)
    return len(gioco) - len(senza), len(senza), sorted(senza)


# Elenco dei comandi che erano gia' italiani prima di questa tabella
# (nome principale o alias). Tenuto esplicito invece che dedotto con
# un'euristica sulle lettere: dedurre la lingua da una stringa corta
# sbaglia troppo spesso, e qui serve un conteggio onesto.
GIA_ITALIANI = {
    "alloggia", "balance", "buy", "channels", "deposit", "dream", "drink",
    "eat", "exchange", "extinguish", "feed", "feedme", "fix", "forge",
    "gender", "hours", "light", "locker", "psychology", "refit", "reload",
    "rest", "sacrifice", "sell", "sleep", "stand", "therapy", "wake",
    "wear", "wield", "withdraw", "costruiscimondo", "comandi",
}


def _sembra_italiano(cmd):
    return cmd.key in GIA_ITALIANI
