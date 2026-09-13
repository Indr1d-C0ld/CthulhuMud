"""
KICK/BASH/TRIP/DISARM/DIRT/BACKSTAB (Fase K, ventiduesima tornata):
vedi world/mosse_speciali.py per le note sulla fonte e le scelte di
design. Ognuna richiede una skill gia' presente nel registro
(world/skills.py) e gia' assegnata a molte professioni, ma priva di
comando/effetto fino a questa tornata.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.mosse_speciali import (
    tenta_kick, tenta_bash, tenta_trip, tenta_disarm,
    tenta_dirt_kicking, tenta_backstab,
)


def _trova_bersaglio(caller, testo):
    if not testo:
        caller.msg("Contro chi?")
        return None
    bersaglio = caller.search(testo.strip())
    if not bersaglio:
        return None
    if bersaglio is caller:
        caller.msg("Non puoi farlo a te stesso/a.")
        return None
    if not hasattr(bersaglio, "avvia_combattimento"):
        caller.msg("Non puoi farlo a questo.")
        return None
    return bersaglio


class CmdKick(MuxCommand):
    """
    sferra un calcio extra al tuo avversario

    Uso:
      kick <bersaglio>

    Un tentativo fallito ti sbilancia, penalizzando i tuoi prossimi
    colpi (helps/kick.txt).
    """
    key = "kick"
    locks = "cmd:all()"

    def func(self):
        bersaglio = _trova_bersaglio(self.caller, self.args)
        if bersaglio:
            tenta_kick(self.caller, bersaglio)


class CmdBash(MuxCommand):
    """
    tenta di mandare in ginocchio il tuo avversario

    Uso:
      bash <bersaglio>

    Se riesce, il bersaglio finisce a terra: piu' vulnerabile e
    incapace di fuggire finche' non si rialza (helps/bash.txt).
    """
    key = "bash"
    locks = "cmd:all()"

    def func(self):
        bersaglio = _trova_bersaglio(self.caller, self.args)
        if bersaglio:
            tenta_bash(self.caller, bersaglio)


class CmdTrip(MuxCommand):
    """
    fai cadere a terra il tuo avversario

    Uso:
      trip <bersaglio>

    Se riesce, il bersaglio finisce a terra: piu' vulnerabile e
    incapace di fuggire finche' non si rialza (helps/trip.txt).
    """
    key = "trip"
    locks = "cmd:all()"

    def func(self):
        bersaglio = _trova_bersaglio(self.caller, self.args)
        if bersaglio:
            tenta_trip(self.caller, bersaglio)


class CmdDisarm(MuxCommand):
    """
    fai cadere l'arma di mano al tuo avversario

    Uso:
      disarm <bersaglio>
    """
    key = "disarm"
    locks = "cmd:all()"

    def func(self):
        bersaglio = _trova_bersaglio(self.caller, self.args)
        if bersaglio:
            tenta_disarm(self.caller, bersaglio)


class CmdDirtKicking(MuxCommand):
    """
    tira della terra negli occhi del tuo avversario

    Uso:
      dirt <bersaglio>

    Lo acceca temporaneamente, un piccolo vantaggio finche' non si
    ripulisce gli occhi (helps/dirt_kicking.txt).
    """
    key = "dirt"
    aliases = ["dirtkick"]
    locks = "cmd:all()"

    def func(self):
        bersaglio = _trova_bersaglio(self.caller, self.args)
        if bersaglio:
            tenta_dirt_kicking(self.caller, bersaglio)


class CmdBackstab(MuxCommand):
    """
    pugnala alle spalle il tuo avversario

    Uso:
      backstab <bersaglio>

    Un danno molto piu' alto del normale, che scala con il tuo
    livello e le tue skill (helps/backstab.txt).
    """
    key = "backstab"
    locks = "cmd:all()"

    def func(self):
        bersaglio = _trova_bersaglio(self.caller, self.args)
        if bersaglio:
            tenta_backstab(self.caller, bersaglio)
