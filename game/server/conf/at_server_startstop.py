"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_init()
at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""


def at_server_init():
    """
    This is called first as the server is starting up, regardless of how.
    """
    pass


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.

    Storia di questa funzione (importante per non reintrodurre il bug).

    In Fase K, nona tornata, costruendo AFFECTS si era notato per caso che
    si accumulavano decine di Script di scadenza a colpo singolo
    (StatoScadenzaScript, SottorazzaBuffExpireScript, EffettoPeriodicoScript)
    con is_active=False e time_until_next_repeat()=None: mai piu' schedulati,
    quindi incapaci sia di ripristinare il valore precedente sia di rimuovere
    lo stato che rappresentavano. All'epoca la causa non fu indagata
    (dichiarata fuori scope) e si ripiego' su un workaround: RIATTIVARLI
    tutti a ogni avvio.

    L'audit globale pre-beta ha trovato la causa vera, che era in
    world/effetti.py: assegnare `script.interval` come semplice attributo
    non arma il timer del reattore, quindi quegli script nascevano gia'
    morti (la stessa classe di bug gia' corretta per RigenerazioneScript e
    per i buff delle sottorazze). Corretta la causa, il workaround non solo
    e' diventato inutile: era diventato DANNOSO, perche' riattivava
    indiscriminatamente anche gli script fermati di proposito - una cecita'
    gia' curata, i buff azzerati alla morte del personaggio - facendoli
    scattare di nuovo su uno stato ormai superato. E' all'origine degli
    errori sporadici "FOREIGN KEY constraint failed" visti nei log.

    Al suo posto qui si fa ora l'opposto: una PULIZIA, ma deliberatamente
    CONSERVATIVA. Vengono eliminati solo gli script effimeri rimasti
    ORFANI, cioe' agganciati a un oggetto nel frattempo cancellato: una
    condizione non ambigua, perche' un tale script non potra' mai piu'
    fare nulla di utile e, se scatta, produce gli errori
    "FOREIGN KEY constraint failed" gia' visti nei log.

    NON si filtra invece su `is_active`, benche' sarebbe stato comodo per
    ripulire anche le righe lasciate indietro da `.stop()`: l'audit ha
    verificato dal vivo che `is_active` e' un flag inaffidabile, che puo'
    restare False su uno script il cui timer e' in realta' regolarmente
    armato e funzionante (succede dopo un ri-armo con force_restart).
    Cancellare in base a quel flag rischierebbe di distruggere script
    perfettamente sani - una cura peggiore del male. L'accumulo di righe
    e' quindi affrontato alla fonte, usando `.delete()` invece di
    `.stop()` nei punti in cui siamo noi a scartare uno script (vedi
    world/effetti.py, world/sottorazze.py, typeclasses/living.py)."""
    from evennia.scripts.models import ScriptDB
    from evennia.utils import logger
    from evennia.utils import delay

    tipi_effimeri = (
        "typeclasses.scripts.StatoScadenzaScript",
        "typeclasses.scripts.SottorazzaBuffExpireScript",
        "typeclasses.scripts.EffettoPeriodicoScript",
        "typeclasses.scripts.CombatRoundScript",
        "typeclasses.scripts.BlessExpireScript",
    )
    rimossi = 0
    for script in ScriptDB.objects.filter(db_typeclass_path__in=tipi_effimeri):
        obj = script.obj
        if obj is None or not obj.pk:
            script.delete()
            rimossi += 1
    if rimossi:
        logger.log_info(
            f"at_server_start: rimossi {rimossi} script effimeri rimasti "
            "orfani del proprio oggetto."
        )

    # Controllo del "battito cardiaco" (audit globale pre-beta).
    # Motivo: l'audit ha trovato RigenerazioneScript fermo in produzione
    # con is_active=True ma nessun timer armato - la rigenerazione di
    # HP/mana/movimento era del tutto assente, e un semplice reload non
    # bastava a farlo ripartire (Evennia non riavvia uno script che il
    # database dichiara gia' attivo). Un difetto del genere e' silenzioso
    # e pericoloso su un server destinato a restare acceso per mesi:
    # qui si verifica esplicitamente che ogni script globale abbia un
    # timer davvero armato e, se non ce l'ha, lo si fa ripartire.
    # Il controllo e' rinviato di qualche secondo perche' al momento di
    # at_server_start Evennia non ha ancora finito di riavviare gli
    # script persistenti, e li vedremmo tutti (falsamente) fermi.
    delay(10, _verifica_battito_script_globali)


def _verifica_battito_script_globali():
    """Riavvia gli script globali il cui timer non risulta armato.

    Volutamente NON usa `is_active` come criterio (flag inaffidabile, vedi
    la nota in at_server_start): l'unica prova attendibile che uno script
    stia davvero girando e' che `time_until_next_repeat()` non sia None."""
    from evennia.scripts.models import ScriptDB
    from evennia.utils import logger

    globali = (
        "typeclasses.scripts.RigenerazioneScript",
        "typeclasses.scripts.SopravvivenzaScript",
        "typeclasses.scripts.RepopScript",
        "typeclasses.scripts.MostriMovimentoScript",
        "typeclasses.scripts.CristalliFocusScript",
        "typeclasses.scripts.InteresseBancarioScript",
    )
    for script in ScriptDB.objects.filter(db_typeclass_path__in=globali):
        if script.time_until_next_repeat() is None:
            nome = script.db_typeclass_path.split(".")[-1]
            # interval=None conserva quello gia' impostato sullo script,
            # cosi' non si azzera per errore il conto alla rovescia lungo
            # di InteresseBancarioScript a ogni riavvio.
            script.start(force_restart=True)
            logger.log_warn(
                f"battito: {nome} era fermo (nessun timer armato) ed e' stato riavviato."
            )

    # Script di combattimento "zombie": timer non armato E nessun bersaglio.
    # Sono inservibili per definizione (non scatteranno mai, e non hanno
    # nulla da fare nemmeno se scattassero) e, non potendo scattare, non
    # riescono nemmeno ad auto-ripulirsi passando da ferma_combattimento().
    # La doppia condizione rende il criterio non ambiguo, al contrario del
    # solo `is_active` che l'audit ha dimostrato inaffidabile.
    zombie = 0
    for script in ScriptDB.objects.filter(
        db_typeclass_path="typeclasses.scripts.CombatRoundScript"
    ):
        obj = script.obj
        senza_timer = script.time_until_next_repeat() is None
        senza_bersaglio = obj is None or not obj.pk or not obj.db.combat_target
        if senza_timer and senza_bersaglio:
            script.delete()
            zombie += 1
    if zombie:
        logger.log_info(
            f"battito: rimossi {zombie} script di combattimento inservibili "
            "(nessun timer armato e nessun bersaglio)."
        )


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass
