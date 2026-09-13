"""
Comandi di equipaggiamento (Fase F, decima tornata): wear/indossa,
wield/impugna, remove/rimuovi, equipment/eq.

Vedi world/equipment.py per la logica e le scelte di design (slot
disponibili, formule di livello/condizione) e la nota sulla fonte
originale che ha ispirato questa milestone. FORGE/FIX/REFIT vivono in
commands/cthulhu_forgiatura.py (Fase G, terza tornata).
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.equipment import (
    SLOT_ARMA, SLOTS, e_arma, e_equipaggiabile, nome_slot,
    puo_equipaggiare, puo_usare_oggetto, descrizione_condizione,
)


class CmdWear(MuxCommand):
    """
    indossa un'armatura

    Uso:
      wear <oggetto>
      indossa <oggetto>

    Funziona solo con oggetti pensati per essere indossati (armature,
    scudi, amuleti...). Per le armi vedi WIELD.
    """

    key = "wear"
    aliases = ["indossa"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Indossare cosa?")
            return
        if not puo_equipaggiare(caller):
            caller.msg("Il tuo corpo non ha slot per l'equipaggiamento.")
            return

        oggetto = caller.search(self.args, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{self.args}'.")
            return
        if not e_equipaggiabile(oggetto) or e_arma(oggetto):
            caller.msg(f"{oggetto.key} non e' qualcosa che puoi indossare.")
            return
        if not puo_usare_oggetto(caller, oggetto):
            caller.msg(
                f"{oggetto.key} e' di livello troppo alto per te (richiede "
                f"livello {oggetto.db.livello})."
            )
            return

        slot = oggetto.db.slot
        equip = caller.db.equip or {}
        attuale = equip.get(slot)
        if attuale:
            caller.msg(f"Devi prima togliere {attuale.key} ({nome_slot(slot)}).")
            return

        equip[slot] = oggetto
        caller.db.equip = equip
        oggetto.db.indossato = True
        caller.msg(f"Indossi {oggetto.key}.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} indossa {oggetto.key}.", exclude=caller
            )


class CmdWield(MuxCommand):
    """
    impugna un'arma

    Uso:
      wield <oggetto>
      impugna <oggetto>
    """

    key = "wield"
    aliases = ["impugna"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Impugnare cosa?")
            return
        if not puo_equipaggiare(caller):
            caller.msg("Il tuo corpo non ha slot per l'equipaggiamento.")
            return

        oggetto = caller.search(self.args, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{self.args}'.")
            return
        if not e_arma(oggetto):
            caller.msg(f"{oggetto.key} non e' un'arma impugnabile.")
            return
        if not puo_usare_oggetto(caller, oggetto):
            caller.msg(
                f"{oggetto.key} e' di livello troppo alto per te (richiede "
                f"livello {oggetto.db.livello})."
            )
            return

        equip = caller.db.equip or {}
        attuale = equip.get(SLOT_ARMA)
        if attuale:
            caller.msg(f"Devi prima riporre {attuale.key}.")
            return

        equip[SLOT_ARMA] = oggetto
        caller.db.equip = equip
        oggetto.db.indossato = True
        caller.msg(f"Impugni {oggetto.key}.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} impugna {oggetto.key}.", exclude=caller
            )


class CmdRemove(MuxCommand):
    """
    togli qualcosa che indossi o impugni

    Uso:
      remove <oggetto>
      rimuovi <oggetto>
    """

    key = "remove"
    aliases = ["rimuovi"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Togliere cosa?")
            return

        equip = caller.db.equip or {}
        oggetto = caller.search(
            self.args, location=caller, quiet=True,
            candidates=[o for o in equip.values() if o],
        )
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non stai indossando/impugnando nulla chiamato '{self.args}'.")
            return

        slot = next((s for s, o in equip.items() if o == oggetto), None)
        if slot:
            equip[slot] = None
            caller.db.equip = equip
        oggetto.db.indossato = False
        caller.msg(f"Ti togli {oggetto.key}.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} si toglie {oggetto.key}.", exclude=caller
            )


class CmdEquipment(MuxCommand):
    """
    mostra cosa indossi e impugni

    Uso:
      equipment
      eq
    """

    key = "equipment"
    aliases = ["eq"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        equip = caller.db.equip or {}
        righe = ["|wIndossi/impugni:|n"]
        for slot, etichetta in SLOTS.items():
            oggetto = equip.get(slot)
            if oggetto:
                righe.append(
                    f"  <{etichetta}> {oggetto.key}{descrizione_condizione(oggetto)}"
                )
            else:
                righe.append(f"  <{etichetta}> niente")
        caller.msg("\n".join(righe))


## CmdRepair (a pagamento in Oro, self-service ovunque) e' stato RIMOSSO
## (Fase G, terza tornata): non era fedele alla fonte, che descrive FIX
## come parte della skill Forgiatura, con incudine e costo in movimento,
## non oro. Vedi commands/cthulhu_forgiatura.py (CmdFix) per la versione
## allineata alla fonte.
