"""
TAME/ORDER (Fase K, nona tornata): vedi world/seguaci.py per le note
sulla fonte. RECRUIT non ha un comando dedicato (funziona da solo,
agganciato a typeclasses/rooms.py).
"""

from evennia import Command

from world.seguaci import tenta_tame, ordina


class CmdTame(Command):
    """
    prova ad addomesticare una creatura

    Uso:
      tame <bersaglio>

    Funziona solo su creature non senzienti, non-morte o prive di una
    seppur minima intelligenza naturale - nessun mostro del bestiario
    lo e'. Costa 200 movimento.
    """

    key = "tame"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: tame <bersaglio>")
            return
        bersaglio = caller.search(self.args.strip())
        if not bersaglio:
            return
        ok, messaggio = tenta_tame(caller, bersaglio)
        caller.msg(messaggio)
        if ok:
            caller.location.msg_contents(f"{bersaglio.key} si acquieta e inizia a seguire {caller.key}.", exclude=[caller])


class CmdOrder(Command):
    """
    comanda i tuoi seguaci

    Uso:
      order <seguace> <comando>
      order all <comando>

    Sei responsabile delle azioni dei tuoi seguaci.
    """

    key = "order"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: order <seguace>/all <comando>")
            return
        ok, messaggio = ordina(caller, self.args.strip())
        caller.msg(messaggio)
