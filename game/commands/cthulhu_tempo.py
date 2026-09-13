"""
TIME/HOURS (Fase K, quindicesima tornata): vedi world/tempo.py per le
note sulla fonte e sulle scelte di design (orologio di gioco nativo
di Evennia, orari dei negozi dal catalogo Arkham).
"""

import datetime

from evennia import Command
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils import gametime

from world.economia import trova_mercante
from world.tempo import ora_di_gioco, descrivi_orari


class CmdTime(Command):
    """
    mostra l'ora di gioco

    Uso:
      time

    Mostra l'ora corrente di gioco, il momento dell'ultimo avvio del
    MUD e l'ora reale locale del server.
    """

    key = "time"
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        ora = ora_di_gioco()
        avvio = datetime.datetime.fromtimestamp(gametime.server_epoch())
        adesso_reale = datetime.datetime.now()
        self.caller.msg(
            f"L'ora di gioco e' le {ora:02d}:00.\n"
            f"Il MUD e' in esecuzione dal {avvio:%d/%m/%Y %H:%M}.\n"
            f"L'ora locale del server e' le {adesso_reale:%H:%M} del {adesso_reale:%d/%m/%Y}."
        )


class CmdHours(MuxCommand):
    """
    mostra gli orari di apertura di un negozio

    Uso:
      hours
      orari

    Se nella stanza e' presente un mercante, mostra a che ora apre e
    chiude il negozio (e se e' aperto in questo momento).
    """

    key = "hours"
    aliases = ["orari"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        mercante = trova_mercante(caller.location) if caller.location else None
        if not mercante:
            caller.msg("Non c'e' nessun mercante qui.")
            return
        caller.msg(descrivi_orari(caller.location))
