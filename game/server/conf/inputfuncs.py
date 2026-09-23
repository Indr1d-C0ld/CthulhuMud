"""
Input functions

Input functions are always called from the client (they handle server
input, hence the name).

This module is loaded by being included in the
`settings.INPUT_FUNC_MODULES` tuple.

All *global functions* included in this module are considered
input-handler functions and can be called by the client to handle
input.

An input function must have the following call signature:

    cmdname(session, *args, **kwargs)

Where session will be the active session and *args, **kwargs are extra
incoming arguments and keyword properties.

A special command is the "default" command, which is will be called
when no other cmdname matches. It also receives the non-found cmdname
as argument.

    default(session, cmdname, *args, **kwargs)

"""

# def oob_echo(session, *args, **kwargs):
#     """
#     Example echo function. Echoes args, kwargs sent to it.
#
#     Args:
#         session (Session): The Session to receive the echo.
#         args (list of str): Echo text.
#         kwargs (dict of str, optional): Keyed echo text
#
#     """
#     session.msg(oob=("echo", args, kwargs))
#
#
# def default(session, cmdname, *args, **kwargs):
#     """
#     Handles commands without a matching inputhandler func.
#
#     Args:
#         session (Session): The active Session.
#         cmdname (str): The (unmatched) command name
#         args, kwargs (any): Arguments to function.
#
#     """
#     pass


# ---------------------------------------------------------------------
# Correzioni per i client MUD (audit totale)
# ---------------------------------------------------------------------
#
# Questo modulo viene caricato DOPO evennia.server.inputfuncs
# (settings.INPUT_FUNC_MODULES) e le funzioni con lo stesso nome
# sostituiscono quelle di Evennia: e' il posto previsto per correggerle
# senza toccare la libreria, dove una modifica sparirebbe al primo
# aggiornamento.


def msdp_report(session, *args, **kwargs):
    """MSDP REPORT, corretto.

    In Evennia 6.1 (evennia/server/inputfuncs.py) la funzione originale
    contiene un refuso - kwargs["outputfunc_name":"report"], con i due
    punti al posto di "] =" - che solleva KeyError a ogni chiamata. Mudlet
    la invoca a ogni connessione: il log del server ne conteneva 14 in una
    settimana, tutte cadute durante le sessioni di gioco."""
    from evennia.server.inputfuncs import monitor
    kwargs["outputfunc_name"] = "report"
    monitor(session, *args, **kwargs)


def client_name(session, *args, **kwargs):
    """Core.Hello di Mudlet (nome del client). Lo si registra nei flag del
    protocollo, dove Evennia tiene gia' il nome ricavato dal TTYPE, invece
    di lasciare a ogni connessione un "Input command not recognized"."""
    if args:
        session.update_flags(CLIENTNAME=str(args[0]))


def client_version(session, *args, **kwargs):
    """Core.Hello di Mudlet (versione del client). Vedi client_name."""
    if args:
        session.update_flags(CLIENTVERSION=str(args[0]))


def supports_add(session, *args, **kwargs):
    """Core.Supports.Add: il client annuncia i moduli GMCP che gestisce.
    Il server manda comunque Room.Info e Char.Vitals a chi ha negoziato
    il GMCP, quindi non c'e' nulla da fare: si accetta in silenzio."""
    return


def external_discord_get(session, *args, **kwargs):
    """Richiesta dell'integrazione Discord di Mudlet: il gioco non ha una
    presenza Discord da comunicare. Accettata in silenzio."""
    return
