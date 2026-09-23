"""
Voodoo: CUT + VOODOO STAB/TWIST/TEAR (Fase K, decima tornata). Confermati
verbatim dalla fonte (helps/consecrate_doll.txt, che descrive per intero
la skill Vudu'): per creare una bambola personalizzata serve tagliare i
capelli del bersaglio (CUT), poi lanciare CAST 'CONSECRATE DOLL' tenendo
in mano sia una bambola vuota sia i capelli. Una volta pronta, la bambola
agisce a distanza sulla vittima ovunque si trovi: STAB e' solo un
avvertimento doloroso, TWIST danneggia sia la bambola sia la vittima,
TEAR distrugge la bambola infliggendo danno grave, potenzialmente letale.
"""

import random

from world.colori import magia

from evennia import Command
from evennia.utils import create


class CmdCut(Command):
    """
    taglia una ciocca di capelli a qualcuno

    Uso:
      cut <bersaglio>

    Serve per l'incantesimo Consacra Bambola (skill Vudu').
    """

    key = "cut"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: cut <bersaglio>")
            return
        bersaglio = caller.search(self.args.strip())
        if not bersaglio:
            return
        if bersaglio is caller:
            caller.msg("Non serve tagliare i tuoi stessi capelli.")
            return
        # NPC di servizio (NPC.intoccabile): la bambola che se ne ricaverebbe servirebbe
        # solo a far loro del male a distanza
        from world.pk import e_intoccabile, messaggio_intoccabile
        if e_intoccabile(bersaglio):
            caller.msg(messaggio_intoccabile(bersaglio))
            return
        capelli = create.create_object(
            "typeclasses.objects.Object", key=f"una ciocca di capelli di {bersaglio.key}", location=caller,
        )
        capelli.db.capelli_di = bersaglio
        caller.location.msg_contents(f"{caller.key} taglia una ciocca di capelli a {bersaglio.key}.")


class CmdVoodoo(Command):
    """
    manipola una bambola voodoo personalizzata

    Uso:
      voodoo stab <bambola>
      voodoo twist <bambola>
      voodoo tear <bambola>

    STAB e' solo un avvertimento doloroso. TWIST infligge danno sia alla
    bambola sia alla vittima. TEAR distrugge la bambola infliggendo dolore
    e danno gravissimi, potenzialmente letali, ovunque si trovi la vittima.
    """

    key = "voodoo"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        parti = self.args.split(None, 1)
        if len(parti) != 2:
            self.msg("Uso: voodoo stab/twist/tear <bambola>")
            return
        azione, resto = parti[0].lower(), parti[1]
        if azione not in ("stab", "twist", "tear"):
            self.msg("Uso: voodoo stab/twist/tear <bambola>")
            return
        caller = self.caller
        bambola = caller.search(resto)
        if not bambola:
            return
        vittima = bambola.db.bambola_di
        if not vittima or not vittima.pk:
            caller.msg(f"{bambola.key} non e' una bambola voodoo personalizzata.")
            return

        if azione == "stab":
            vittima.msg(magia("Senti improvvisamente una fitta di dolore, come se qualcuno ti stesse pensando male."))
            caller.msg(f"Pungi {bambola.key}: solo un avvertimento, per ora.")
        elif azione == "twist":
            danno_bambola = random.randint(5, 10)
            bambola.db.integrita = max(0, (bambola.db.integrita if bambola.db.integrita is not None else 100) - danno_bambola)
            danno = random.randint(8, 16)
            vittima.msg(magia(f"Un dolore lancinante ti attraversa il corpo, infliggendoti {danno} danni!"))
            morto = vittima.subisci_danno(danno, fisico=False)
            caller.msg(f"Torci {bambola.key}: {vittima.key} soffre a distanza.")
            if morto:
                from world.combat import gestisci_morte
                gestisci_morte(vittima, caller)
            if bambola.db.integrita <= 0:
                bambola.delete()
                caller.msg(f"{bambola.key} si sgretola, consumata.")
        elif azione == "tear":
            danno = random.randint(30, 55)
            vittima.msg(magia("Un dolore devastante ti squarcia il corpo intero!"))
            morto = vittima.subisci_danno(danno, fisico=False)
            caller.location.msg_contents(f"{caller.key} strappa {bambola.key} in due!")
            bambola.delete()
            if morto:
                from world.combat import gestisci_morte
                gestisci_morte(vittima, caller)
