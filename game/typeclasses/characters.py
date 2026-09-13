"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

Estesa con i dati di CthulhuMUD ITA Redux: attributi, skill, razza,
professione, sanity. Vedi world/races.py, world/professions_newbie.py,
world/skills.py per i registri dati.
"""

import random

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent
from .living import LivingMixin

ATTRIBUTI_BASE = ("str", "int", "wis", "dex", "con", "luck", "cha")
# Fase K, diciottesima tornata: TRAIN su Fortuna e' l'unico attributo
# escluso - confermato dalla fonte (helps/attributes.txt: "Luck cannot
# even be trained").
ATTRIBUTI_ALLENABILI = tuple(a for a in ATTRIBUTI_BASE if a != "luck")

# Valori di partenza e limiti non documentati dal sito originale (che non
# specifica formule di guadagno skill per pratica/insegnamento/dibattito,
# ne' la dotazione iniziale di "trains"/"practices"): scelte di design
# esplicite, facili da ritarare in seguito.
PRACTICES_INIZIALI = 5
TRAINS_INIZIALI = 5
CAP_PRACTICE = 75     # oltre questo valore, PRACTICE da solo non basta piu'
CAP_LEARN = 90        # LEARN da un insegnante arriva un po' piu' in alto
CAP_DEBATE = 50       # DEBATE (gratuito) e' il metodo meno efficace
COSTO_CAMBIO_PROFESSIONE = 3   # in practices, come da sito originale
# Fase K, diciottesima tornata: confermato dalla fonte che PROF CHANGE
# richiede anche "a minimum number of levels in your current
# profession" (helps/prof.txt), oltre alle 3 practice - il numero
# esatto non e' specificato, scelta di design esplicita, facile da
# ritarare (1 = non puoi cambiare professione a livello 0 appena creato).
LIVELLO_MINIMO_CAMBIO_PROFESSIONE = 1
# Fase K, diciottesima tornata: anti-minmax - confermato dalla fonte
# (guides_newbieschool.txt: "The MUD is coded to prevent any new
# character from having high scores in all attributes"). Nessuna
# soglia esatta e' data: 85 e' una scelta di design esplicita (la
# somma attesa di 7 tiri 3d6 e' 73.5 - 85 lascia margine a un tiro
# buono senza permettere che tutti e 7 gli attributi siano alti
# insieme), facile da ritarare.
SOMMA_MASSIMA_ATTRIBUTI = 85

# TRAIN su HP/mana/movimento/practice/sanity: confermato dalla fonte che
# queste opzioni esistono (helps/train.txt), ma non la quantita' esatta
# per train speso - scelta di design esplicita, facile da ritarare.
TRAIN_EXTRA = {
    "hp": ("HP massimi", "hp_max", 5),
    "mana": ("Mana massimo", "mana_max", 5),
    "move": ("Movimento massimo", "move_max", 5),
    "practice": ("Practice", "practices", 1),
    "sanity": ("Sanity massima", "sanity_max", 5),
}


def tira_3d6():
    """Tiro di base per un attributo: 3d6 (media 10.5). Scelta di design non
    documentata dal sito originale - punto aperto, facile da tarare in seguito."""
    return sum(random.randint(1, 6) for _ in range(3))


class Character(LivingMixin, ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Character child classes like this.

    """

    def at_object_creation(self):
        super().at_object_creation()
        self.at_living_creation()
        # attributi grezzi (prima dei modificatori di professione), 0 se non ancora tirati
        for attr in ATTRIBUTI_BASE:
            self.attributes.add(f"stat_{attr}", 0, category="cthulhu")
        self.db.race = None
        self.db.professions = {}       # {prof_id: livelli_accumulati}
        self.db.active_profession = None
        self.db.mana = 10
        self.db.mana_max = 10
        self.db.move = 100
        self.db.move_max = 100
        self.db.sanity = 100
        self.db.sanity_max = 100
        self.db.fame = 0
        self.db.appetito = 0
        self.db.sete = 0
        self.db.gold = 0
        self.db.dollari = 0            # world/valute.py: le altre 4 valute regionali (Oro = db.gold)
        self.db.corone = 0
        self.db.rame = 0
        self.db.yuggos = 0
        self.db.divinita = None       # world/worship.py: id della divinita' adorata, o None
        self.db.pieta = 0             # world/worship.py: fedelta'/generosita' verso la divinita' attuale
        self.db.alignment = 0
        # Fase K, diciannovesima tornata: RIGHTEOUSKILL (helps/righteouskill.txt)
        # - default disattivo, come le altre opzioni AUTO* di questo porting.
        self.db.righteouskill = False
        # Fase K, ventesima tornata: vantaggi/comandi staff (world/staff.py,
        # commands/cthulhu_staff.py) - irrilevanti per un personaggio
        # mortale, ma inizializzati qui per coerenza con il resto.
        self.db.holylight = False
        self.db.frozen = False
        self.db.wizinvis = False
        self.db.cloak = False
        self.db.incarnato = False
        self.db.bamfin = None
        self.db.bamfout = None
        self.db.cult = None            # world/professions_avanzate.py: condizione CULT per alcune professioni
        self.db.imprese = set()        # world/imprese.py: id di "deed" completate (es. "deed_59")
        self.db.deed_dettagli = {}     # world/imprese.py: {deed_id: {"quando":..., "resa_pubblica": bool}}
        self.db.quest_progress = {}    # world/quest.py: {quest_id: numero_tappa} per le quest in corso
        self.db.societa_ranghi = {}    # world/societies.py: {societa_id: rango} - appartenenza multipla
        self.db.sottorazza = None      # world/sottorazze.py: None/"lich"/"vampire"/"were" (permanente)
        self.db.generazione = None
        self.db.pool_sottorazza = 0
        self.db.casa_sottorazza = None
        self.db.genitore_sottorazza = None
        self.db.in_forma_animale = False
        self.db.criminale = False      # world/pk.py: status da MURDER su un NPC protetto
        self.db.taglia_oro = 0         # oro promesso a chi ti uccide
        self.db.missione = None        # world/pk.py: missione attiva della Gilda Taglie
        self.db.missione_prossima_disponibile = 0
        self.db.genere = "m"           # world/socials.py: "m"/"f", per i pronomi nei messaggi in terza persona
        self.db.recall_room = None
        self.db.respawn_room = None
        self.db.morgue_room = None
        self.db.practices = PRACTICES_INIZIALI
        self.db.trains = TRAINS_INIZIALI
        self.db.train_spesi = {}   # {attr: volte gia' allenato} - vedi train_attributo
        self.db.xp = 0             # esperienza verso il prossimo livello (world/esperienza.py)

        # Fase K, tredicesima tornata: FOLLOW/GROUP (world/gruppo.py)
        self.db.seguendo = None            # il personaggio che sto seguendo (FOLLOW), None se nessuno
        self.db.seguaci_giocatori = []      # i personaggi che mi seguono
        self.db.leader_gruppo = None        # il leader del mio gruppo, None se non sono in un gruppo o se lo guido io
        self.db.membri_gruppo = []          # (solo se sono leader) gli altri membri del mio gruppo
        self.db.non_accetta_seguaci = False  # NOFOLLOW (senza argomento): rifiuta ogni nuovo FOLLOW su di me
        self.db.autoassist = False
        self.db.autosplit = False

    def tira_attributi_base(self):
        """Tira 3d6 per ognuno dei 7 attributi grezzi (prima dei modificatori
        di professione). Da chiamare una sola volta, in creazione personaggio.
        Ritira l'intero set se la somma supera SOMMA_MASSIMA_ATTRIBUTI (anti-
        minmax, confermato dalla fonte - vedi la costante)."""
        while True:
            valori = {attr: tira_3d6() for attr in ATTRIBUTI_BASE}
            if sum(valori.values()) <= SOMMA_MASSIMA_ATTRIBUTI:
                break
        for attr, valore in valori.items():
            self.attributes.add(f"stat_{attr}", valore, category="cthulhu")

    def valore_attributo(self, attr):
        """Valore finale di un attributo: base tirato + somma dei modificatori
        di tutte le professioni mai giocate (non solo quella attiva) + eventuali
        modificatori temporanei da incantesimi (Forza/Indebolisci/Invecchiamento/
        Giovinezza/Fretta - Fase K, sesta tornata, vedi world/magic.py).

        Bug corretto (Fase K, nona tornata): fino a questa tornata venivano
        sommati solo i modificatori delle professioni NEWBIE - le 39
        professioni avanzate hanno il proprio campo "modificatori_attributi"
        (nome diverso da "attributi" delle newbie) mai controllato qui, quindi
        restava dato morto anche per chi aveva gia' cambiato professione."""
        base = self.attributes.get(f"stat_{attr}", default=0, category="cthulhu")
        mod = 0
        from world.professions_newbie import NEWBIE_PROFESSIONS
        from world.professions_avanzate import PROFESSIONI_AVANZATE
        for prof_id in (self.db.professions or {}):
            prof = NEWBIE_PROFESSIONS.get(prof_id)
            if prof:
                mod += prof["attributi"].get(attr, 0)
                continue
            prof_avanzata = PROFESSIONI_AVANZATE.get(prof_id)
            if prof_avanzata:
                mod += prof_avanzata["modificatori_attributi"].get(attr, 0)
        mod += getattr(self.db, f"mod_temp_{attr}", 0) or 0
        return base + mod

    def imposta_razza(self, race_id):
        self.db.race = race_id

    def applica_professione_newbie(self, prof_id):
        """
        Assegna la professione newbie scelta in creazione personaggio:
        - registra 0 livelli accumulati in quella professione (ledger)
        - la imposta come professione attiva
        - assegna a rating 0 tutte le skill previste al livello 0
        - imposta recall/respawn/morgue in base all'hub della professione

        Usata SOLO in creazione personaggio (non fa pulizia delle skill
        della professione precedente). Per cambiare professione a
        personaggio gia' creato vedi `cambia_professione_newbie`.
        """
        from world.professions_newbie import NEWBIE_PROFESSIONS
        from world.rooms_newbie import stanza_per_ruolo

        prof = NEWBIE_PROFESSIONS.get(prof_id)
        if not prof:
            return False

        professions = self.db.professions or {}
        professions.setdefault(prof_id, 0)
        self.db.professions = professions
        self.db.active_profession = prof_id

        skills = self.db.skills or {}
        for skill_id in prof["skill_per_livello"].get(0, []):
            skills.setdefault(skill_id, 0)
        self.db.skills = skills

        hub = prof["start_tag"]
        self.db.recall_room = stanza_per_ruolo(hub, "recall")
        self.db.respawn_room = stanza_per_ruolo(hub, "respawn")
        self.db.morgue_room = stanza_per_ruolo(hub, "morgue")
        return True

    def cambia_professione_newbie(self, prof_id):
        """
        PROF CHANGE: cambia la professione attiva a personaggio gia' creato.

        Regole (dal sito originale, sezione 5 del Dossier):
        - costa COSTO_CAMBIO_PROFESSIONE practices
        - richiede almeno LIVELLO_MINIMO_CAMBIO_PROFESSIONE livelli nella
          professione attuale (helps/prof.txt: "provided that you have 3
          practice sessions... AND you have already acquired a minimum
          number of levels in your current profession" - il numero esatto
          non e' specificato dalla fonte)
        - le skill gia' portate sopra 0 restano per sempre
        - le skill ancora a rating 0, concesse SOLO dalla professione che si
          lascia, spariscono dalla lista "practice"
        - i livelli di professione sono cumulativi: tornare a una professione
          gia' giocata in passato ne riprende il livello da dove era rimasto

        Ritorna (ok: bool, messaggio: str).
        """
        from world.professions_newbie import NEWBIE_PROFESSIONS, skill_fino_al_livello

        nuova = NEWBIE_PROFESSIONS.get(prof_id)
        if not nuova:
            return False, "Professione sconosciuta."
        if (self.db.practices or 0) < COSTO_CAMBIO_PROFESSIONE:
            return False, f"Ti servono almeno {COSTO_CAMBIO_PROFESSIONE} practice."

        vecchia_id = self.db.active_profession
        if vecchia_id == prof_id:
            return False, "Sei gia' in quella professione."
        if vecchia_id and self.livello_professione(vecchia_id) < LIVELLO_MINIMO_CAMBIO_PROFESSIONE:
            return False, (
                f"Devi raggiungere almeno il livello {LIVELLO_MINIMO_CAMBIO_PROFESSIONE} "
                f"nella tua professione attuale prima di poterla cambiare."
            )

        skills = self.db.skills or {}

        if vecchia_id:
            vecchia_livello = self.livello_professione(vecchia_id)
            skill_vecchia = skill_fino_al_livello(vecchia_id, vecchia_livello)
            nuovo_livello = self.livello_professione(prof_id)
            skill_nuova = skill_fino_al_livello(prof_id, nuovo_livello)
            for skill_id in skill_vecchia - skill_nuova:
                if skills.get(skill_id, 0) == 0:
                    skills.pop(skill_id, None)

        nuovo_livello = self.livello_professione(prof_id)
        for skill_id in nuova["skill_per_livello"].get(0, []):
            skills.setdefault(skill_id, 0)
        # se si rientra in una professione gia' giocata, ri-assegna anche le
        # skill dei livelli gia' raggiunti in passato
        for skill_id in skill_fino_al_livello(prof_id, nuovo_livello):
            skills.setdefault(skill_id, 0)
        self.db.skills = skills

        professions = self.db.professions or {}
        professions.setdefault(prof_id, 0)
        self.db.professions = professions
        self.db.active_profession = prof_id
        self.db.practices -= COSTO_CAMBIO_PROFESSIONE

        from world.professions_newbie import nome_professione
        return True, f"Ora sei {nome_professione(prof_id)}."

    def cambia_professione_avanzata(self, prof_id):
        """Come cambia_professione_newbie, ma per le 40 professioni
        avanzate (world/professions_avanzate.py): richiede di soddisfare
        le condizioni d'accesso (livello/razza/cult/allineamento/skill/
        imprese) prima di poter cambiare. Costa comunque
        COSTO_CAMBIO_PROFESSIONE practice come le newbie."""
        from world.professions_avanzate import PROFESSIONI_AVANZATE, valuta_condizioni, nome_professione_avanzata

        if prof_id not in PROFESSIONI_AVANZATE:
            return False, "Professione avanzata sconosciuta."
        ok, mancanti = valuta_condizioni(self, prof_id)
        if not ok:
            return False, "Non soddisfi le condizioni:\n  " + "\n  ".join(mancanti)
        if (self.db.practices or 0) < COSTO_CAMBIO_PROFESSIONE:
            return False, f"Ti servono almeno {COSTO_CAMBIO_PROFESSIONE} practice."

        vecchia_id = self.db.active_profession
        if vecchia_id and self.livello_professione(vecchia_id) < LIVELLO_MINIMO_CAMBIO_PROFESSIONE:
            return False, (
                f"Devi raggiungere almeno il livello {LIVELLO_MINIMO_CAMBIO_PROFESSIONE} "
                f"nella tua professione attuale prima di poterla cambiare."
            )
        skills = self.db.skills or {}
        entry = PROFESSIONI_AVANZATE[prof_id]
        for skill_id in entry.get("skill_per_livello", {}).get(0, []):
            skills.setdefault(skill_id, 0)
        self.db.skills = skills

        professions = self.db.professions or {}
        professions.setdefault(prof_id, professions.get(vecchia_id, 0) if vecchia_id else 0)
        self.db.professions = professions
        self.db.active_profession = prof_id
        self.db.practices -= COSTO_CAMBIO_PROFESSIONE

        return True, f"Ora sei {nome_professione_avanzata(prof_id)}."

    def livello_professione(self, prof_id):
        return (self.db.professions or {}).get(prof_id, 0)

    def livello_personaggio(self):
        """Il 'livello' complessivo e' la somma dei livelli accumulati in
        tutte le professioni mai giocate (multi-classing cumulativo)."""
        return sum((self.db.professions or {}).values())

    def execute_cmd(self, raw_string, session=None, **kwargs):
        """FREEZE (Fase K, ventesima tornata, commands/cthulhu_staff.py):
        confermato dalla fonte (helps/freeze.txt) - "The game will not
        accept or process any commands issued from a frozen character,
        but the character will still be able to see things that happen
        around him/her" - qui bloccato prima ancora di interpretare il
        comando, cosi' la seconda meta' (continuare a ricevere messaggi)
        resta intatta di suo (msg() non e' toccato)."""
        if self.db.frozen:
            self.msg("|rSei congelato/a: non puoi inserire comandi.|n")
            return
        return super().execute_cmd(raw_string, session=session, **kwargs)

    def get_display_name(self, looker=None, **kwargs):
        if self.db.maschera and looker is not self:
            # Fase K, decima tornata: Vera Vista permette di vedere
            # attraverso Maschera di Se'/Incognito/Metamorfosi.
            stati_looker = getattr(looker, "db", None) and looker.db.stati
            if stati_looker and stati_looker.get("vede_attraverso_maschere"):
                return super().get_display_name(looker, **kwargs)
            return self.db.maschera
        return super().get_display_name(looker, **kwargs)

    def at_post_move(self, source_location, move_type="move", **kwargs):
        """Fase K, nona tornata: i seguaci (TAME/RECRUIT - world/seguaci.py)
        ti seguono automaticamente da stanza a stanza. Fase K, tredicesima
        tornata: lo stesso vale per FOLLOW tra personaggi giocanti
        (world/gruppo.py) - confermato dalla fonte: "The FOLLOW command
        will force your character to tag along... following them from
        room to room"."""
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        if self.db.seguaci:
            from world.seguaci import sposta_seguaci
            sposta_seguaci(self)
        if self.db.seguaci_giocatori:
            from world.gruppo import sposta_seguaci_giocatori
            sposta_seguaci_giocatori(self)
        if self.db.incantesimo_in_corso:
            # Fase K, ventitreesima tornata: helps/spell_casting.txt,
            # "you can stop casting a spell... by leaving the room."
            from world.magic import interrompi_lancio
            interrompi_lancio(self, "Ti allontani, interrompendo il tuo incantesimo.")
        from world.dreamlands import in_dreamlands
        if in_dreamlands(self.location):
            # Fase K, ventiseiesima tornata: helps/dreaming.txt (via
            # recurring_dream.txt) - RECURRING DREAM riporta "all'ultimo
            # punto in cui si sognava": aggiornato ad ogni spostamento
            # dentro le Dreamlands, non solo al primo ingresso.
            self.db.ultimo_sogno = self.location

    def costo_train_attributo(self, attr):
        """Il costo sale di 1 train ogni volta che alleni lo STESSO
        attributo (1a volta 1 train, 2a volta 2, 3a volta 3, ecc.) -
        confermato dalla fonte (helps/train.txt)."""
        spesi = self.db.train_spesi or {}
        return spesi.get(attr, 0) + 1

    def train_attributo(self, attr):
        """TRAIN <attributo>: aumenta di 1 punto un attributo grezzo. Il
        costo in train sale ogni volta (vedi costo_train_attributo). La
        Fortuna e' esclusa (vedi ATTRIBUTI_ALLENABILI)."""
        if attr not in ATTRIBUTI_BASE:
            return False, "Attributo sconosciuto."
        if attr == "luck":
            return False, "La Fortuna non puo' essere allenata."
        costo = self.costo_train_attributo(attr)
        if (self.db.trains or 0) < costo:
            return False, f"Ti servono {costo} train per allenare di nuovo questo attributo."
        self.attributes.add(
            f"stat_{attr}",
            self.attributes.get(f"stat_{attr}", default=0, category="cthulhu") + 1,
            category="cthulhu",
        )
        self.db.trains -= costo
        spesi = self.db.train_spesi or {}
        spesi[attr] = spesi.get(attr, 0) + 1
        self.db.train_spesi = spesi
        if attr in ("int", "wis"):
            # helps/sanity.txt: "Training your Intelligence decreases
            # your sanity, while training your Wisdom increases it."
            from world.sanita import sanita_da_train_attributo
            sanita_da_train_attributo(self, attr)
        return True, (
            f"Il tuo {attr.upper()} e' aumentato di 1 (costo: {costo} train). "
            f"La prossima volta costera' {costo + 1} train."
        )

    def train_extra(self, tipo):
        """TRAIN HP/MANA/MOVE/PRACTICE/SANITY: opzioni confermate dalla
        fonte oltre agli attributi grezzi (helps/train.txt); qui a costo
        fisso di 1 train ciascuna (la fonte non specifica il costo esatto
        di queste, solo che esistono)."""
        info = TRAIN_EXTRA.get(tipo)
        if not info:
            return False, "Opzione di train sconosciuta."
        etichetta, campo, quantita = info
        if (self.db.trains or 0) < 1:
            return False, "Non hai trains a sufficienza."
        self.db.trains -= 1
        setattr(self.db, campo, (getattr(self.db, campo) or 0) + quantita)
        return True, f"{etichetta} aumentato di {quantita} (ora {getattr(self.db, campo)})."

    def pratica_skill(self, skill_id):
        """PRACTICE: da solo, senza insegnante. Richiede di conoscere gia'
        la skill (rating presente, anche a 0) e costa 1 practice."""
        skills = self.db.skills or {}
        if skill_id not in skills:
            return False, "Non conosci questa skill: non puoi praticarla."
        if (self.db.practices or 0) < 1:
            return False, "Non hai practice a sufficienza."
        if skills[skill_id] >= CAP_PRACTICE:
            return False, f"Non puoi migliorare oltre {CAP_PRACTICE}% senza un insegnante."
        self.db.practices -= 1
        guadagno = random.randint(1, 5)
        skills[skill_id] = min(CAP_PRACTICE, skills[skill_id] + guadagno)
        self.db.skills = skills
        from world.skills import nome_skill
        return True, f"Hai praticato {nome_skill(skill_id)}: ora al {skills[skill_id]}%."

    def impara_da_insegnante(self, insegnante, skill_id):
        """LEARN: da un NPC insegnante che conosca quella skill. Puo'
        introdurre skill non ancora possedute. Costa 1 practice."""
        insegnabili = insegnante.db.skills_insegnabili or []
        if skill_id not in insegnabili:
            return False, f"{insegnante.key} non conosce questa materia."
        if (self.db.practices or 0) < 1:
            return False, "Non hai practice a sufficienza."
        skills = self.db.skills or {}
        attuale = skills.get(skill_id, 0)
        if attuale >= CAP_LEARN:
            return False, f"{insegnante.key} non ha piu' nulla da insegnarti su questo."
        self.db.practices -= 1
        guadagno = random.randint(3, 10) if attuale == 0 else random.randint(1, 5)
        skills[skill_id] = min(CAP_LEARN, attuale + guadagno)
        self.db.skills = skills
        from world.skills import nome_skill
        return True, f"{insegnante.key} ti insegna {nome_skill(skill_id)}: ora al {skills[skill_id]}%."

    COSTO_MOVIMENTO_DEBATE = 15  # drena movimento a ogni tentativo (fonte: "drain the movement
                                  # points of the participants" - quantita' non specificata)

    def dibatti_skill(self, avversario, skill_id):
        """DEBATE <avversario> <skill>: gratuito in Practice, ma drena
        movimento e richiede un minimo di rating in Dibattito (skill
        'debating'). Confermato dalla fonte (helps/debate.txt): vince chi
        ha il rating di Dibattito piu' alto; il vincitore guadagna XP e
        pratica la skill, il perdente perde un po' di XP."""
        from world.esperienza import guadagna_xp

        skills = self.db.skills or {}
        if skill_id not in skills:
            return False, "Non puoi dibattere di qualcosa che non conosci gia'."
        if skills.get("debating", 0) <= 0:
            return False, "Non conosci ancora l'arte del Dibattito."
        if skills[skill_id] >= CAP_DEBATE:
            return False, f"Il dibattito non ti porta oltre il {CAP_DEBATE}%."
        if (self.db.move or 0) < self.COSTO_MOVIMENTO_DEBATE:
            return False, "Sei troppo stanco per dibattere: ti manca il movimento."

        self.db.move -= self.COSTO_MOVIMENTO_DEBATE

        rating_mio = skills.get("debating", 0)
        rating_avversario = (avversario.db.skills or {}).get("debating", 0) if hasattr(avversario, "db") else 0
        vinco = random.randint(0, 100) + rating_mio > random.randint(0, 100) + rating_avversario

        from world.skills import nome_skill
        if not vinco:
            if (self.db.xp or 0) > 0:
                self.db.xp = max(0, self.db.xp - 5)
            return False, (
                f"{avversario.key} controbatte le tue argomentazioni su "
                f"{nome_skill(skill_id)}: perdi il dibattito (e un po' di esperienza)."
            )

        guadagno = 1 if random.randint(1, 100) > rating_mio else random.randint(1, 3)
        skills[skill_id] = min(CAP_DEBATE, skills[skill_id] + guadagno)
        self.db.skills = skills
        for messaggio in guadagna_xp(self, 10):
            self.msg(messaggio)
        return True, f"Convinci {avversario.key} su {nome_skill(skill_id)}: ora al {skills[skill_id]}%."

    def scheda(self):
        """Rappresentazione testuale minimale della scheda personaggio (SCORE)."""
        from world.races import nome_razza
        from world.professions_newbie import nome_professione, NEWBIE_PROFESSIONS
        from world.professions_avanzate import nome_professione_avanzata, PROFESSIONI_AVANZATE

        righe = [f"|w{self.key}|n"]
        if self.db.race:
            righe.append(f"Razza: {nome_razza(self.db.race)}")
        if self.db.active_profession:
            if self.db.active_profession in PROFESSIONI_AVANZATE:
                nome_prof = nome_professione_avanzata(self.db.active_profession)
            else:
                nome_prof = nome_professione(self.db.active_profession)
            righe.append(
                f"Professione: {nome_prof} "
                f"(livello {self.livello_professione(self.db.active_profession)})"
            )
        righe.append(f"Livello personaggio: {self.livello_personaggio()}")
        righe.append(
            "STR {str} INT {int} WIS {wis} DEX {dex} CON {con} FOR.{luck} CAR.{cha}".format(
                **{a: self.valore_attributo(a) for a in ATTRIBUTI_BASE}
            )
        )
        righe.append(f"HP {self.db.hp}/{self.db.hp_max}  Mana {self.db.mana}/{self.db.mana_max}  "
                      f"Movimento {self.db.move}/{self.db.move_max}")
        # Fase K, ventiduesima tornata: HITR/DAMR (helps/hitroll.txt) -
        # i bonus temporanei esistevano gia' (usati davvero dalle formule
        # in typeclasses/living.py) ma non comparivano mai su SCORE.
        righe.append(f"HITR {self.db.bonus_colpire or 0:+d}  DAMR {self.db.bonus_danno_temp or 0:+d}")
        # Fase K, ventisettesima tornata: helps/money.txt - la scheda
        # mostra solo la valuta di DEFAULT della zona attuale, non
        # sempre l'Oro (MONEY/WORTH mostra il totale di tutte e 5).
        from world.valute import valuta_locale, saldo, NOMI_VALUTE
        valuta_qui = valuta_locale(self.location)
        righe.append(f"Sanity {self.db.sanity}/{self.db.sanity_max}  Fama {self.db.fame}  "
                      f"{NOMI_VALUTE[valuta_qui]} {saldo(self, valuta_qui)}")
        # Fase K, ventiseiesima tornata: campi COUNT/MSTATUS confermati
        # dalla fonte (helps/bounty.txt) - mancavano del tutto dalla
        # scheda, nonostante mission_prossima_disponibile/db.missione
        # esistessero gia'.
        from world.pk import tempo_missione, stato_missione
        righe.append(f"COUNT {tempo_missione(self)}  MSTATUS {stato_missione(self)}")
        # Fase K, ventisettesima tornata: helps/sacrifice.txt - "The deity
        # you are currently worshiping is displayed on your Score Sheet,
        # along with your current piety."
        if self.db.divinita:
            from world.worship import nome_divinita
            righe.append(f"Divinita': {nome_divinita(self.db.divinita)}  Pieta': {self.db.pieta or 0}")
        from world.sopravvivenza import stato_bisogno
        appetito = stato_bisogno(self.db.appetito or 0)
        sete = stato_bisogno(self.db.sete or 0)
        if appetito != "nessuno" or sete != "nessuno":
            righe.append(f"Fame: {appetito}  Sete: {sete}")
        righe.append(f"Practices {self.db.practices}  Trains {self.db.trains}")
        return "\n".join(righe)
