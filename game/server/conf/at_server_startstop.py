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

    Fase K, nona tornata: corregge un bug di piattaforma scoperto per caso
    costruendo AFFECTS - su randolph si erano accumulati 56 Script di
    scadenza a colpo singolo (StatoScadenzaScript, SottorazzaBuffExpireScript,
    EffettoPeriodicoScript - vedi world/effetti.py) con is_active=False e
    time_until_next_repeat()=None: mai piu' schedulati per scattare, quindi
    destinati a restare per sempre ne' a ripristinare il valore precedente
    ne' a rimuovere lo stato/buff che rappresentano. Non e' chiaro se la
    causa esatta sia legata ai numerosi `evennia reload` di questa sessione
    di sviluppo o a un comportamento piu' generale - qui ci si limita a
    riattivare quelli trovati inattivi a ogni avvio, invece di indagare a
    fondo l'origine (fuori dallo scope di questa tornata)."""
    from evennia.scripts.models import ScriptDB

    tipi_da_riattivare = (
        "typeclasses.scripts.StatoScadenzaScript",
        "typeclasses.scripts.SottorazzaBuffExpireScript",
        "typeclasses.scripts.EffettoPeriodicoScript",
    )
    riattivati = 0
    for script in ScriptDB.objects.filter(db_typeclass_path__in=tipi_da_riattivare):
        if not script.is_active:
            script.start()
            riattivati += 1
    if riattivati:
        from evennia.utils import logger
        logger.log_info(f"at_server_start: riattivati {riattivati} script di scadenza rimasti inattivi dopo il riavvio.")


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
