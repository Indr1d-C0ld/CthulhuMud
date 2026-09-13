"""
REST/SLEEP/STAND (Fase K, quattordicesima tornata): vedi
world/posizione.py per le note sulla fonte e sulle scelte di design.
WAKE non e' qui: e' stato unito al gia' esistente CmdWake (vedi
commands/cthulhu_dream.py), che significava gia' "svegliati dalle
Dreamlands" - stesso trattamento gia' dato alla collisione TELL/PAGE.
"""

from evennia import Command

from world.posizione import tenta_rest, tenta_sleep, tenta_stand


class CmdRest(Command):
    """
    siediti a riposare

    Uso:
      rest
      riposa

    Recuperi HP, Mana e Movimento piu' in fretta, ma sei piu'
    vulnerabile agli attacchi finche' non ti rialzi (STAND).
    """

    key = "rest"
    aliases = ["riposa"]
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        ok, messaggio = tenta_rest(self.caller)
        self.caller.msg(messaggio)


class CmdSleep(Command):
    """
    addormentati

    Uso:
      sleep
      dormi

    Recuperi HP, Mana e Movimento molto piu' in fretta, ma non ti
    accorgerai di quasi nulla intorno a te e sei piu' vulnerabile
    agli attacchi finche' qualcuno non ti sveglia (WAKE) o non ti
    alzi da solo/a (STAND).
    """

    key = "sleep"
    aliases = ["dormi"]
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        ok, messaggio = tenta_sleep(self.caller)
        self.caller.msg(messaggio)


class CmdStand(Command):
    """
    alzati in piedi

    Uso:
      stand
      alzati

    Torni in posizione eretta, di default, interrompendo anche REST o
    SLEEP.
    """

    key = "stand"
    aliases = ["alzati"]
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        ok, messaggio = tenta_stand(self.caller)
        self.caller.msg(messaggio)
