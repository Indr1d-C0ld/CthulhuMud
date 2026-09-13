"""
CHAT (Fase K, nona tornata): confermato dalla fonte (helps/ooc.txt,
elencato assieme agli altri canali OOC) come canale "used for answering
questions of curious people who are checking out the game" - quindi
raggiungibile PRIMA del login, un concetto distinto dai canali Evennia
nativi (Channel/Account, entrambi richiedono un account gia' autenticato
- vedi world/canali.py). Dichiarato esplicitamente fuori scope in quella
tornata proprio per questo motivo; risolto qui con un broadcast diretto
a livello di Session invece che di Canale Evennia.

Raggiunge letteralmente OGNI sessione connessa (incluse quelle ancora
alla schermata di connessione, tramite
evennia.SESSION_HANDLER.get_sessions(include_unloggedin=True)) - non
richiede alcuna iscrizione ne' un account per essere letto o scritto.
"""

import evennia


def _nome_mittente(session):
    puppet = session.get_puppet() if hasattr(session, "get_puppet") else None
    if puppet:
        return puppet.key
    account = session.get_account() if hasattr(session, "get_account") else None
    if account:
        return account.key
    return f"un ospite (sessione #{session.sessid})"


def invia_chat(session_mittente, testo):
    """Manda <testo> a TUTTE le sessioni connesse, loggate o meno."""
    mittente = _nome_mittente(session_mittente)
    messaggio = f"|y[CHAT] {mittente}:|n {testo}"
    for sessione in evennia.SESSION_HANDLER.get_sessions(include_unloggedin=True):
        sessione.msg(messaggio)
