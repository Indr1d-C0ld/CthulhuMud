"""
NPC (versione minima per M2/M3).

Non e' ancora il sistema completo di building/mobprogs descritto in
Architettura Balthasar (§02, §06) - qui serve solo un NPC abbastanza
funzionale da poter insegnare/far praticare skill ai giocatori (M2) e
da poter combattere in modo elementare (M3). Verra' esteso quando
affronteremo il motore reattivo NPC.
"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent
from .living import LivingMixin
from world.colori import orrore


class NPC(LivingMixin, ObjectParent, DefaultCharacter):
    """NPC di base: puo' insegnare skill, far praticare e/o combattere."""

    def at_object_creation(self):
        super().at_object_creation()
        self.at_living_creation()
        self.db.skills_insegnabili = []   # lista di skill_id che questo NPC puo' insegnare
        self.db.is_practice_trainer = False
        self.db.livello = 1
        self.db.alignment = 0    # -1000..1000, come Character.db.alignment (vedi world/esperienza.py)
        self.db.non_morto = False   # world/sottorazze.py: LICH DOMINATE richiede un NPC non-morto
        self.db.ostile = False   # se True, contrattacca automaticamente se attaccato
        self.db.yithian_originale = None   # world/yithian.py: chi possiede questo corpo via MINDTRANSFER
        self.db.protetto = False   # world/pk.py: KILL rifiutato, serve MURDER (rende criminale chi lo usa)
        self.locks.add("puppet:false()")  # mai puppettabile da un account (salvo MINDTRANSFER attivo)

    # Gli stessi valori di at_object_creation qui sopra, per completare gli
    # NPC creati prima che esistessero (vedi LivingMixin.completa_default_mancanti).
    DEFAULT_VIVENTI = {
        **LivingMixin.DEFAULT_VIVENTI,
        "skills_insegnabili": list, "is_practice_trainer": False, "livello": 1,
        "alignment": 0, "non_morto": False, "ostile": False,
        "yithian_originale": None, "protetto": False,
    }

    def get_display_name(self, looker, **kwargs):
        """helps/bounty.txt: "the subject of your search will have the
        [TARGET] flag next to its name" - mostrato solo a chi ha
        ricevuto la missione di caccia su questo NPC, non a chiunque
        (per non rivelare a estranei i dettagli della missione altrui)."""
        nome = super().get_display_name(looker, **kwargs)
        if self.db.bersaglio_missione_di and getattr(looker, "key", None) == self.db.bersaglio_missione_di:
            return f"{nome} |r[TARGET]|n"
        return nome

    def at_death(self, uccisore):
        """Comportamento minimo alla morte: assegna XP a chi ha ucciso
        (se e' un personaggio giocante, vedi world/esperienza.py -
        divisa a meta' se chi uccide sta possedendo questo corpo via
        MINDTRANSFER, vedi world/yithian.py), lascia un cadavere e
        sparisce. Il ripopolamento non e' gestito qui: e' un sistema
        periodico a parte, per zona (vedi world/repop.py, Fase H, seconda
        tornata). Se QUESTO corpo era posseduto da uno Yithiano,
        la mente torna automaticamente al corpo originale, con una
        perdita di XP dimezzata rispetto al normale. Se questo NPC era
        il bersaglio di una missione di caccia (world/pk.py), segnala
        il completamento a chi l'ha ricevuta."""
        if self.db.bersaglio_missione_di:
            from evennia.utils import search
            richiedenti = search.search_object(self.db.bersaglio_missione_di, exact=True)
            for richiedente in richiedenti:
                missione = richiedente.db.missione
                if missione and missione.get("tipo") == "caccia" and missione.get("bersaglio_dbref") == self.dbref:
                    missione["bersaglio_ucciso"] = True
                    richiedente.db.missione = missione
                    richiedente.msg(
                        "|gIl fuggitivo ricercato e' morto: torna all'Ufficio Taglie e usa "
                        "MISSION COMPLETE.|n"
                    )

        if uccisore is not None and hasattr(uccisore, "db") and uccisore.db.active_profession:
            from world.esperienza import xp_da_uccisione, guadagna_xp, sposta_allineamento

            if self.db.bestiario_chiave:
                # world/quest.py: contatore per l'impresa deed_9061
                # ("Si e' dimostrato/a valoroso/a in combattimento") -
                # solo i mostri veri del bestiario contano, non gli NPC
                # di ambientazione/negozianti.
                uccisore.db.mostri_uccisi = (uccisore.db.mostri_uccisi or 0) + 1

            xp = xp_da_uccisione(uccisore, self)
            sposta_allineamento(uccisore, self)
            yithiano_uccisore = uccisore.db.yithian_originale
            if yithiano_uccisore:
                xp = xp // 2
                uccisore.msg(
                    f"Guadagni {xp} punti esperienza (l'altra meta' va al tuo corpo Yithiano)."
                )
                for messaggio in guadagna_xp(uccisore, xp):
                    uccisore.msg(messaggio)
                yithiano_uccisore.msg(f"Il tuo corpo Yithiano guadagna {xp} punti esperienza.")
                for messaggio in guadagna_xp(yithiano_uccisore, xp):
                    yithiano_uccisore.msg(messaggio)
            else:
                # Fase K, tredicesima tornata: "share the experience from
                # killing" (helps/follow.txt) - se uccisore e' in un
                # gruppo, l'XP si divide tra i membri presenti invece di
                # andare tutta a lui solo.
                from world.gruppo import condividi_xp_gruppo
                for membro, quota in condividi_xp_gruppo(uccisore, xp).items():
                    if not membro.db.active_profession:
                        continue
                    if membro is uccisore:
                        membro.msg(f"Guadagni {quota} punti esperienza.")
                    else:
                        membro.msg(f"Guadagni {quota} punti esperienza dal gruppo.")
                    for messaggio in guadagna_xp(membro, quota):
                        membro.msg(messaggio)

        # il corpo va catturato PRIMA di un eventuale swap di puppet:
        # DefaultCharacter.at_post_unpuppet() azzera self.location non
        # appena la sessione smette di controllare questo NPC (lo tratta
        # come un personaggio che va OOC), quindi dopo il RETURN
        # automatico self.location sarebbe None.
        luogo_morte = self.location

        if self.db.yithian_originale:
            from world.esperienza import perdi_xp_morte
            from world.yithian import PENALITA_XP_MORTE_YITHIAN

            yithiano = self.db.yithian_originale
            sessioni = self.sessions.get()
            if sessioni and self.account:
                self.account.puppet_object(sessioni[0], yithiano)
            self.locks.add("puppet:false()")
            self.db.yithian_originale = None
            messaggio_xp = perdi_xp_morte(yithiano, moltiplicatore=PENALITA_XP_MORTE_YITHIAN)
            yithiano.msg(orrore("Il corpo che possedevi muore! La tua mente torna di scatto al tuo corpo Yithiano."))
            if messaggio_xp:
                yithiano.msg(messaggio_xp)

        from world.combat import crea_cadavere
        cadavere = crea_cadavere(self, location=luogo_morte)
        if luogo_morte:
            luogo_morte.msg_contents(f"{self.key} si accascia senza vita.", exclude=[])
        # Fase K, ventisettesima tornata: AUTOSAC (helps/autokill.txt,
        # gia' tracciato come toggle in world/pk.py ma dichiarato inerte
        # finche' non esisteva un vero sistema WORSHIP a cui agganciarlo).
        if uccisore is not None and getattr(uccisore, "db", None) and uccisore.db.autosac:
            from world.worship import sacrifica_automatico_cadavere
            sacrifica_automatico_cadavere(uccisore, cadavere)
        self.delete()
