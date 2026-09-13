"""
Comandi di Forgiatura (Fase G, terza tornata): forge/forgia,
fix/ripara, refit/adatta. Vedi world/forgiatura.py per la logica e le
citazioni della fonte originale.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.forgiatura import forgia, ripara, refit, TIPI_FORGIABILI
from world.munizioni import gunsmith_arma, gunsmith_munizioni, ricarica, TIPI_ARMI_DA_FUOCO, CALIBRI_VALIDI


class CmdForge(MuxCommand):
    """
    forgia un'arma o un pezzo d'armatura da un materiale grezzo

    Uso:
      forge <tipo> [livello]
      forgia <tipo> [livello]

    Devi tenere in mano il materiale, e trovarti in una stanza con
    un'incudine o una forgia (es. la bottega di un fabbro). Costa 200
    punti movimento. Se non specifichi il livello, viene usato il tuo.
    Tipi disponibili: dagger, sword, mace, spear, whip, flail, axe,
    polearm, bow, armor, shield, helmet.
    """

    key = "forge"
    aliases = ["forgia"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            tipi = ", ".join(TIPI_FORGIABILI)
            caller.msg(f"Uso: forge <tipo> [livello]. Tipi: {tipi}")
            return

        parti = self.args.split()
        tipo = parti[0]
        livello = None
        if len(parti) > 1:
            if not parti[1].isdigit():
                caller.msg("Il livello deve essere un numero.")
                return
            livello = int(parti[1])

        materiale = next(
            (o for o in caller.contents if o.db.materiale_forgiatura), None
        )
        ok, messaggio, oggetto = forgia(caller, tipo, materiale, livello)
        caller.msg(messaggio)


class CmdFix(MuxCommand):
    """
    ripara un pezzo di equipaggiamento danneggiato (skill Forgiatura)

    Uso:
      fix <oggetto>
      ripara <oggetto>

    Serve un'incudine o una forgia nella stanza. Costa 80 punti
    movimento, e c'e' un rischio (che scende salendo di rating in
    Forgiatura) di romperlo invece di ripararlo.
    """

    key = "fix"
    aliases = ["ripara"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Riparare cosa?")
            return
        oggetto = caller.search(self.args, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{self.args}'.")
            return
        ok, messaggio = ripara(caller, oggetto)
        caller.msg(messaggio)


class CmdRefit(MuxCommand):
    """
    adatta il livello minimo di un pezzo di equipaggiamento

    Uso:
      refit <oggetto> <livello>
      adatta <oggetto> <livello>

    Serve un'incudine o una forgia nella stanza. Costa 100 punti
    movimento, con un rischio di rompere l'oggetto.
    """

    key = "refit"
    aliases = ["adatta"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        parti = self.args.split(None, 1) if self.args else []
        if len(parti) != 2 or not parti[1].strip().isdigit():
            caller.msg("Uso: refit <oggetto> <livello>")
            return
        oggetto = caller.search(parti[0], location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{parti[0]}'.")
            return
        ok, messaggio = refit(caller, oggetto, int(parti[1]))
        caller.msg(messaggio)


class CmdGunsmith(MuxCommand):
    """
    costruisce armi da fuoco o munizioni (skill Forgiatura + Esplosivi/Chimica)

    Uso:
      gunsmith <tipo> <calibro> [livello]
      gunsmith ammo <calibro>

    Devi tenere in mano un materiale grezzo (polvere da sparo per le
    munizioni) e trovarti presso un'incudine o una forgia. Costa 200
    punti movimento per un'arma, 120 per un caricatore. Le munizioni
    richiedono anche le skill Esplosivi e Chimica.
    Tipi d'arma: handgun, gun, machinegun, submachinegun.
    Calibri: .22, .38, .45, 9mm, 12 gauge.
    """

    key = "gunsmith"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        parti = self.args.split() if self.args else []
        if not parti:
            caller.msg(f"Uso: gunsmith <tipo> <calibro> [livello] | gunsmith ammo <calibro>. "
                       f"Tipi: {', '.join(TIPI_ARMI_DA_FUOCO)}. Calibri: {', '.join(CALIBRI_VALIDI)}")
            return

        materiale = next((o for o in caller.contents if o.db.materiale_forgiatura), None)

        if parti[0].lower() == "ammo":
            if len(parti) < 2:
                caller.msg("Uso: gunsmith ammo <calibro>")
                return
            ok, messaggio, oggetto = gunsmith_munizioni(caller, parti[1], materiale)
            caller.msg(messaggio)
            return

        if len(parti) < 2:
            caller.msg("Uso: gunsmith <tipo> <calibro> [livello]")
            return
        tipo, calibro = parti[0], parti[1]
        livello = None
        if len(parti) > 2:
            if not parti[2].isdigit():
                caller.msg("Il livello deve essere un numero.")
                return
            livello = int(parti[2])
        ok, messaggio, oggetto = gunsmith_arma(caller, tipo, calibro, materiale, livello)
        caller.msg(messaggio)


class CmdReload(MuxCommand):
    """
    ricarica l'arma da fuoco impugnata con un caricatore compatibile

    Uso:
      reload
      ricarica

    Cerca automaticamente nel tuo inventario un caricatore dello stesso
    calibro dell'arma che impugni.
    """

    key = "reload"
    aliases = ["ricarica"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        ok, messaggio = ricarica(self.caller)
        self.caller.msg(messaggio)
