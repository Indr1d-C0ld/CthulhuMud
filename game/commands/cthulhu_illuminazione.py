"""
LIGHT/EXTINGUISH (Fase K, sedicesima tornata): vedi world/illuminazione.py
per le note sulla fonte e sulle scelte di design. Il comportamento di
default (accensione/spegnimento automatico tenendo/lasciando l'oggetto)
e' su typeclasses/objects.py:OggettoLuce - questi due comandi servono
solo a scavalcarlo manualmente (helps/light.txt: "particularly useful
if a character plans to ignite a light and leave it on the ground as a
stationary light source").
"""

from evennia.commands.default.muxcommand import MuxCommand


def _cerca_oggetto_luce(caller, testo):
    """Cerca sia nell'inventario che a terra nella stanza (LIGHT/EXTINGUISH
    devono poter agire anche su un oggetto lasciato a terra come fonte
    fissa, non solo su quello che si tiene in mano). Con quiet=True
    .search() ritorna sempre una lista (vuota se nulla trovato) invece
    di messaggiare da solo gli errori - va spacchettata a mano, stesso
    schema gia' usato in commands/cthulhu_shop.py:CmdSell."""
    candidati = list(caller.contents)
    if caller.location:
        candidati += list(caller.location.contents)
    trovati = caller.search(testo, candidates=candidati, quiet=True)
    return trovati[0] if trovati else None


class CmdLight(MuxCommand):
    """
    accendi un oggetto-luce

    Uso:
      light <oggetto>
      accendi <oggetto>

    Funziona su un oggetto-luce (torcia/lanterna/candela) che tieni con
    te o che si trova a terra nella stanza - utile per lasciarne uno
    acceso a terra come fonte di luce fissa.
    """

    key = "light"
    aliases = ["accendi"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Accendere cosa?")
            return
        oggetto = _cerca_oggetto_luce(caller, self.args.strip())
        if not oggetto:
            caller.msg(f"Non trovi '{self.args.strip()}'.")
            return
        if not oggetto.db.luce:
            caller.msg(f"{oggetto.key} non e' un oggetto che si puo' accendere.")
            return
        if oggetto.db.luce_accesa:
            caller.msg(f"{oggetto.key} e' gia' accesa/o.")
            return
        oggetto.db.luce_accesa = True
        caller.msg(f"Accendi {oggetto.key}.")
        if caller.location:
            caller.location.msg_contents(f"{caller.key} accende {oggetto.key}.", exclude=caller)


class CmdExtinguish(MuxCommand):
    """
    spegni un oggetto-luce

    Uso:
      extinguish <oggetto>
      spegni <oggetto>
    """

    key = "extinguish"
    aliases = ["spegni"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Spegnere cosa?")
            return
        oggetto = _cerca_oggetto_luce(caller, self.args.strip())
        if not oggetto:
            caller.msg(f"Non trovi '{self.args.strip()}'.")
            return
        if not oggetto.db.luce:
            caller.msg(f"{oggetto.key} non e' un oggetto che si puo' spegnere.")
            return
        if not oggetto.db.luce_accesa:
            caller.msg(f"{oggetto.key} e' gia' spenta/o.")
            return
        oggetto.db.luce_accesa = False
        caller.msg(f"Spegni {oggetto.key}.")
        if caller.location:
            caller.location.msg_contents(f"{caller.key} spegne {oggetto.key}.", exclude=caller)
