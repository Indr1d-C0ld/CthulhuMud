"""
LORE e USE (Fase K, settima tornata): confermati dalla fonte
(world/skills.py, skill "lore" - "Ogni tentativo di LORE un oggetto
costa 100 movimento"; guides_yithianfaq.txt per USE sui Cristalli Focus
Yithiani - vedi world/focus_crystal.py). LORE funziona su qualunque
oggetto (non solo cristalli): mostra le stesse informazioni
dell'incantesimo Identificare, ma dipende solo dal rating nella skill
Lore, non anche da Lancio degli Incantesimi (confermato dalla fonte).

USE resta per ora specifico dei Cristalli Focus (l'unico oggetto della
fonte con un verbo USE dedicato, come RECITE per le pergamene o
BRANDISH per i bastoni) - su qualunque altro oggetto risponde con un
messaggio onesto invece di far finta di funzionare.
"""

from evennia import Command

from world.focus_crystal import e_cristallo, descrivi_cristallo, usa_cristallo


class CmdLore(Command):
    """
    Scopre informazioni dettagliate su un oggetto.

    Uso:
      lore <oggetto>

    Richiede la skill Lore; ogni tentativo costa 100 movimento,
    indipendentemente dal successo.
    """

    key = "lore"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    COSTO_MOVIMENTO = 100

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: lore <oggetto>")
            return
        if caller.skill_rating("lore") <= 0:
            caller.msg("Non conosci la skill Sapienza Arcana (Lore).")
            return
        if (caller.db.move or 0) < self.COSTO_MOVIMENTO:
            caller.msg(f"Ti servono almeno {self.COSTO_MOVIMENTO} movimento per usare LORE.")
            return
        bersaglio = caller.search(self.args)
        if not bersaglio:
            return
        caller.db.move -= self.COSTO_MOVIMENTO

        if e_cristallo(bersaglio):
            caller.msg(f"|w{bersaglio.key}|n\n{descrivi_cristallo(bersaglio)}")
            return

        righe = [f"|w{bersaglio.key}|n"]
        if bersaglio.db.tipo_arma:
            righe.append(f"Arma ({bersaglio.db.tipo_arma}): {bersaglio.db.dado_min}-{bersaglio.db.dado_max} danni, "
                          f"bonus {bersaglio.db.bonus_danno or 0}")
        if bersaglio.db.classe_armatura:
            righe.append(f"Armatura: classe {bersaglio.db.classe_armatura}")
        if bersaglio.db.livello:
            righe.append(f"Livello oggetto: {bersaglio.db.livello}")
        if bersaglio.db.condizione is not None:
            righe.append(f"Condizione: {bersaglio.db.condizione}/100")
        if bersaglio.db.marchio:
            righe.append(f"Marchio: {bersaglio.db.marchio}")
        if len(righe) == 1:
            righe.append("Nessuna proprieta' magica o di combattimento rilevabile.")
        caller.msg("\n".join(righe))


class CmdUse(Command):
    """
    Usa un oggetto che richiede un'attivazione dedicata.

    Uso:
      use <oggetto>

    Funziona sui Cristalli Focus Yithiani e sulle statuette create con
    l'incantesimo Crea Statuetta (world/seguaci.py, Fase K decima tornata).
    """

    key = "use"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: use <oggetto>")
            return
        bersaglio = caller.search(self.args)
        if not bersaglio:
            return
        if bersaglio.db.seguace_racchiuso is not None:
            seguace = bersaglio.db.seguace_racchiuso
            if not seguace or not seguace.pk:
                caller.msg("La statuetta si sgretola: non conteneva piu' nulla.")
                bersaglio.delete()
                return
            seguace.move_to(caller.location, quiet=True)
            seguaci = caller.db.seguaci or []
            if seguace not in seguaci:
                seguaci.append(seguace)
            caller.db.seguaci = seguaci
            caller.location.msg_contents(f"{bersaglio.key} si anima e si trasforma di nuovo in {seguace.key}!")
            bersaglio.delete()
            return
        if not e_cristallo(bersaglio):
            caller.msg("Non sai come usare questo oggetto.")
            return
        ok, messaggio = usa_cristallo(caller, bersaglio)
        caller.msg(messaggio)
