"""
LivingMixin: campi e comportamenti condivisi tra Character e NPC per il
combattimento (M3) e per l'equipaggiamento (Fase F, decima tornata).
Vedi Architettura Balthasar §02.

Le formule di colpire/danno qui sotto NON sono documentate dal sito
originale (nessuna pagina di help recuperata specifica percentuali o dadi
esatti): sono scelte di design esplicite, pensate per essere facili da
ritarare in seguito senza toccare il resto del codice. E' invece confermato
dal sito originale (vedi world/equipment.py) che l'arma impugnata usa la
skill del suo tipo (non 'hand_to_hand') e che l'armatura indossata conta
davvero in combattimento.
"""

import random


class LivingMixin:
    """Mixin per qualunque entita' che puo' combattere: Character e NPC."""

    def at_living_creation(self):
        """Da chiamare da at_object_creation() delle classi che usano il mixin."""
        self.db.hp = self.db.hp if self.db.hp is not None else 20
        self.db.hp_max = self.db.hp_max if self.db.hp_max is not None else 20
        if self.db.skills is None:
            self.db.skills = {}
        self.db.combat_target = None
        self.db.wimpy_soglia = 0       # 0 = disabilitato
        self.db.wimpy_direzione = None
        self.db.bonus_colpire = 0      # bonus temporanei (es. Benedizione)
        self.db.bonus_danno_temp = 0   # bonus danno temporanei (Fase K, sesta tornata: incantesimi)
        self.db.bonus_ca_temp = 0      # bonus classe armatura temporanei (scudi magici, ecc.)
        self.db.riduzione_danno_temp = 0  # frazione di danno FISICO ridotto (Fase K, ottava tornata: Armatura di Ygolonac); negativa = piu' vulnerabile
        self.db.riduzione_danno_magico_temp = 0  # come sopra ma per il danno NON fisico (Fase K, nona tornata: Santuario/Vendetta di Cthugha-Ithaqua-Yog)
        self.db.riflesso_danno_temp = 0  # Fase K, decima tornata: Scudo di Fuoco/Gelo/Fulmine - danno restituito a chi colpisce in mischia
        self.db.riduzione_danno_temp2 = 0  # Fase K, decima tornata: "livello Parola" delle Benedizioni elementali - campo separato da riduzione_danno_temp perche' la fonte permette di avere UNA Parola e UNA Benedizione attive insieme
        self.db.riduzione_danno_magico_temp2 = 0  # come sopra ma per il danno non fisico
        if self.db.equip is None:
            self.db.equip = {}         # slot -> oggetto indossato/impugnato
        if self.db.stati is None:
            self.db.stati = {}         # stati temporanei (cieco/muto/addormentato/... - world/effetti.py)
        if self.db.invisibile is None:
            self.db.invisibile = False
        if self.db.posizione is None:
            self.db.posizione = "in_piedi"   # Fase K, quattordicesima tornata: REST/SLEEP/STAND/WAKE (world/posizione.py)
        # Fase K, sesta tornata: lock dinamici per l'invisibilita' magica
        # (invis/mass_invis) - impostati una volta sola, mai piu' toccati:
        # leggono db.invisibile ad ogni valutazione (vedi server/conf/lockfuncs.py).
        self.locks.add("view:invisibilita_permessa();search:invisibilita_permessa()")

    @property
    def vivo(self):
        return (self.db.hp or 0) > 0

    @property
    def in_combattimento(self):
        return self.db.combat_target is not None

    def skill_rating(self, skill_id):
        return (self.db.skills or {}).get(skill_id, 0)

    def livello_per_equip(self):
        """Livello usato per i controlli WEAR/WIELD: il 'livello personaggio'
        per i giocatori, il campo db.livello per gli NPC."""
        if hasattr(self, "livello_personaggio"):
            return self.livello_personaggio()
        return self.db.livello or 1

    def avvia_combattimento(self, bersaglio):
        """Ingaggia bersaglio; crea lo script di round o lo riavvia se era
        rimasto agganciato (ma fermo) da un combattimento precedente.
        Affrontare qualcosa di orrorifico (db.orrore sul bersaglio) costa
        sanity (vedi world/sanita.py) - confermato meccanica reale dalla
        fonte, non solo uno stat cosmetico."""
        if getattr(bersaglio, "db", None) and (bersaglio.db.stati or {}).get("astrale"):
            # Fase K, ottava tornata: Cammino Astrale - un corpo astrale non
            # puo' essere ingaggiato in combattimento normale (confermato
            # dalla fonte: "most mobs cannot attack astral bodies"),
            # solo Esplosione Astrale lo colpisce (chiama subisci_danno()
            # direttamente, senza passare da qui).
            if hasattr(self, "msg"):
                self.msg(f"{bersaglio.key} e' distaccato/a nel suo corpo astrale: non puoi ingaggiarlo/a cosi'.")
            return
        if getattr(bersaglio, "db", None) and bersaglio.db.orrore and hasattr(self, "db") and self.db.sanity is not None:
            from world.sanita import perdi_sanita
            perdi_sanita(self, bersaglio.db.orrore, fonte=bersaglio.key, tipo=bersaglio.db.tipo_orrore)
        if self.db.invisibile and not (self.db.stati or {}).get("vera_invisibilita"):
            # Fase K, sesta tornata: Invisibilita'/Invisibilita' di Massa
            # svaniscono entrando in combattimento (confermato dalla fonte).
            # Fase K, decima tornata: Vera Invisibilita' fa eccezione -
            # confermato dalla fonte ("does not immediately wear off when
            # a character engages in combat").
            self.db.invisibile = False
            self.msg("L'incantesimo di invisibilita' svanisce mentre entri in combattimento.")
        if (self.db.posizione or "in_piedi") != "in_piedi":
            # Fase K, quattordicesima tornata: chi attacca si rialza per
            # farlo (la vulnerabilita' di REST/SLEEP resta invece a chi
            # SUBISCE l'attacco, finche' non decide di STAND da solo/a -
            # vedi world/posizione.py).
            self.db.posizione = "in_piedi"
            self.msg("Ti alzi di scatto per combattere.")
        self.db.combat_target = bersaglio
        esistenti = self.scripts.get("combat_round")
        if esistenti:
            if not esistenti[0].is_active:
                esistenti[0].start()
        else:
            self.scripts.add("typeclasses.scripts.CombatRoundScript")

        # Fase K, tredicesima tornata: AUTOASSIST - "If one member of the
        # group is attacked, all the members of the group will
        # automatically join the fight" (helps/follow.txt).
        from world.gruppo import assist_automatico
        assist_automatico(bersaglio, self)

        # Fase K, pre-release: ASSIST-ALL tra mob (immhelp_flags.txt) -
        # vedi world/mostri.py:tenta_assist per la scelta di scope.
        from world.mostri import tenta_assist
        tenta_assist(bersaglio, self)

    def ferma_combattimento(self):
        self.db.combat_target = None
        script = self.scripts.get("combat_round")
        if script:
            script[0].stop()

    def calcola_hit_chance(self, difensore, forza_disarmato=False):
        """Percentuale (5-95) di andare a segno. Se si impugna un'arma non
        rotta, conta la skill del SUO tipo (es. 'sword'), non 'hand_to_hand'
        - confermato dal sito originale: l'arma in se' non aiuta a colpire,
        solo la competenza in quel tipo d'arma. L'armatura del difensore
        offre una piccola difesa aggiuntiva oltre alla schivata. Fame/sete
        gravi indeboliscono chi attacca (confermato dalla fonte: "seriously
        weaken your character" - vedi world/sopravvivenza.py)."""
        from world.equipment import skill_arma, classe_armatura_totale
        from world.sopravvivenza import penalita_fame_sete

        from world.gruppo import bonus_gruppo_colpire
        from world.posizione import bonus_vulnerabilita_posizione

        if forza_disarmato or self.db.lich_empower_no_armi:
            # world/sottorazze.py: LICH EMPOWER - "you will not be
            # allowed to use weapons of any kind" mentre e' attivo.
            # forza_disarmato=True e' usato anche da BITE (helps/bite.txt:
            # "effectiveness is based off... HAND TO HAND skill").
            skill_id = "hand_to_hand"
        else:
            skill_id = skill_arma(self) or "hand_to_hand"
        attacco = self.skill_rating(skill_id)
        ca_difensore = classe_armatura_totale(difensore) + (difensore.db.bonus_ca_temp or 0)
        difesa = difensore.skill_rating("dodge") + ca_difensore / 2
        base = 50 + (attacco - difesa) / 2 + (self.db.bonus_colpire or 0) + bonus_gruppo_colpire(self)
        base -= penalita_fame_sete(self)
        if (self.db.stati or {}).get("cieco"):
            base -= 25  # Fase K, sesta tornata: Accecamento/Cura Cecita'
        if (self.db.stati or {}).get("sbilanciato"):
            base -= 10  # Fase K, ventiduesima tornata: KICK fallito (helps/kick.txt)
        if (self.db.stati or {}).get("affaticato"):
            base -= 8  # Fase K, ventitreesima tornata: affaticamento da lancio interrotto
        if self.db.forma_nebbia:
            # helps/vampires.txt: VAMPIRE MISTFORM - "cannot perform any
            # actions that require physical interaction" (attaccare incluso).
            base -= 60
        if difensore.db.forma_nebbia:
            # helps/vampires.txt: "cannot easily be hurt" mentre in forma di nebbia.
            base -= 40
        # Fase K, quattordicesima tornata: REST/SLEEP rendono piu'
        # vulnerabili agli attacchi (helps/rest.txt).
        base += bonus_vulnerabilita_posizione(difensore)
        if (difensore.db.stati or {}).get("a_terra"):
            # Fase K, ventiduesima tornata: BASH/TRIP - "increasing
            # their vulnerability to attack" (helps/trip.txt).
            base += 20
        return max(5, min(95, base))

    def calcola_danno(self):
        """Danno di un colpo: dado dell'arma impugnata (o 1-4 a mani nude) +
        bonus fisso dell'arma + bonus Forza/Danno Potenziato."""
        from world.equipment import arma_equipaggiata, bonus_arma_attivo

        arma = arma_equipaggiata(self)
        if arma and bonus_arma_attivo(arma):
            dado_min = arma.db.dado_min or 1
            dado_max = arma.db.dado_max or dado_min
            base = random.randint(dado_min, dado_max)
            bonus_arma = arma.db.bonus_danno or 0
        else:
            base = random.randint(1, 4)
            bonus_arma = 0

        forza = 0
        if hasattr(self, "valore_attributo"):
            forza = self.valore_attributo("str")
        else:
            forza = self.db.forza or 10
        bonus_forza = forza // 5
        bonus_danno = self.skill_rating("enhanced_damage") // 25
        return base + bonus_arma + bonus_forza + bonus_danno + (self.db.bonus_danno_temp or 0)

    def subisci_danno(self, quantita, fisico=True):
        """Applica danno; ritorna True se l'entita' muore per questo colpo.
        fisico=True per i colpi da combattimento normale (arma/mani nude):
        solo questi vengono ridotti/amplificati da db.riduzione_danno_temp
        (Fase K, ottava tornata: Armatura di Ygolonac limita "slash/pierce/
        bash" - dato che qui non esiste una distinzione per tipo di danno,
        la semplificazione dichiarata e' che la riduzione vale per TUTTO il
        danno fisico da combattimento). fisico=False usa invece
        db.riduzione_danno_magico_temp (Fase K, nona tornata: Santuario la
        riduce, le Vendette elementali la rendono negativa per aumentare il
        danno invece di ridurlo - stesso meccanismo, segno opposto). I campi
        "...2" (Fase K, decima tornata: le Parole elementali) si sommano ai
        primi invece di sostituirli, perche' la fonte permette di avere una
        Parola e una Benedizione elementale attive insieme."""
        if fisico:
            riduzione = (self.db.riduzione_danno_temp or 0) + (self.db.riduzione_danno_temp2 or 0)
        else:
            riduzione = (self.db.riduzione_danno_magico_temp or 0) + (self.db.riduzione_danno_magico_temp2 or 0)
        if riduzione:
            quantita = max(0, round(quantita * (1 - riduzione)))
        self.db.hp = max(0, (self.db.hp or 0) - quantita)
        if quantita > 0 and self.db.incantesimo_in_corso:
            # Fase K, ventitreesima tornata: helps/spell_casting.txt, "a
            # foe's attack can disrupt your spell casting before you
            # finish" - probabilita' dichiarata, nessuna formula nella fonte.
            from world.magic import PROBABILITA_INTERRUZIONE_COMBATTIMENTO, interrompi_lancio
            if random.uniform(0, 100) <= PROBABILITA_INTERRUZIONE_COMBATTIMENTO:
                interrompi_lancio(self, "Il colpo subito interrompe il tuo incantesimo!")
        return self.db.hp <= 0
