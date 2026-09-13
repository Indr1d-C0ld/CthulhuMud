"""
Logica delle Dreamlands (Fase E, quinta tornata; estratta e completata
nella ventiseiesima tornata durante l'audit del sistema).

Confermato dalla scansione esaustiva: i file helps/dream.txt, dreams.txt,
dream_walk.txt, dream_awaken.txt sono tutti alias della stessa pagina
canonica DREAMING (skill); trance.txt, true_dreaming.txt,
rude_awakening.txt, recurring_dream.txt, enchanted_sleep.txt,
accursed_sleep.txt sono tutti alias della pagina canonica DREAM MAGIC
(vedi world/magic.py per i 6 incantesimi). Nessun file documenta
esplicitamente flag di stanza tipo DREAM_SAFE/NO_DREAM/MARE.

Gap chiusi in questa tornata (helps/dreaming.txt):
- "attempts to make this journey become easier as a character's rating
  in this skill increases... modified by the WISDOM attribute" - prima
  la probabilita' dipendeva SOLO dalla Sanity, la skill "dreaming" non
  veniva mai letta.
- "characters who attempt to travel in their dreams without developing
  this skill will often find themselves trapped in terrible nightmares
  that can be both dangerous and deadly" - prima un fallimento era
  sempre innocuo.
- "Dream walking from different locations will often result in
  traveling to different destinations" - prima si andava sempre e solo
  al crocevia, ora la zona di partenza sceglie l'ingresso piu' vicino
  tra quelli gia' costruiti (world/rooms_dreamlands_overworld.py).
- "a character's rating in various skills may fluctuate up or down
  while traveling between worlds" - nessuna formula/lista dalla fonte:
  qui una piccola fluttuazione dichiarata su un paio di skill a caso
  tra quelle gia' possedute.
- WAKE su un ALTRO personaggio non lo riportava mai dalle Dreamlands
  (bug reale, non solo gap): la logica di risveglio viveva solo dentro
  CmdWake (self-risveglio) - estratta qui in sveglia_da_sogno() cosi'
  world/posizione.py:tenta_wake() puo' usarla anche per un bersaglio
  altrui.
"""

import random

DREAMLANDS_HUB_PREFIXES = ("ulthar_temple", "dylath_reformatory", "zoog_village")
DREAMLANDS_TAG_CATEGORIES = ("ulthar_room", "zoogvillage_room", "dreamlands_overworld")

CROCEVIA_TAG = "dlo_crocevia"
CROCEVIA_CATEGORY = "dreamlands_overworld"

# helps/dreaming.txt: "traveling from different locations often results
# in traveling to different destinations" - mappa la CATEGORIA di tag
# della stanza di partenza (mondo reale) all'ingresso piu' vicino tra
# quelli gia' costruiti in world/rooms_dreamlands_overworld.py. Nessuna
# mappa esatta dalla fonte: scelta di design dichiarata, per ora limitata
# alle zone che hanno davvero un sentiero dedicato verso le Dreamlands.
DESTINAZIONE_PER_CATEGORIA = {
    "ulthar_room": "dlo_verso_ulthar",
    "zoogvillage_room": "dlo_verso_bosco",
}
DESTINAZIONE_PER_PREFISSO_START_ROOM = {
    "dylath_reformatory": "dlo_lungofiume_skai",
}

PROBABILITA_INCUBO_SENZA_SKILL = 25  # non specificato dalla fonte
BONUS_TRANCE = 20  # incantesimo Trance: "improves a character's dreaming ability"
NUMERO_SKILL_FLUTTUANTI = 2
FLUTTUAZIONE_SKILL_MIN, FLUTTUAZIONE_SKILL_MAX = -2, 3


def in_dreamlands(stanza):
    """Ritorna True se <stanza> fa parte delle Dreamlands (sogno)."""
    if not stanza:
        return False
    for categoria in DREAMLANDS_TAG_CATEGORIES:
        if stanza.tags.get(category=categoria):
            return True
    for tag in stanza.tags.get(category="start_room", return_list=True) or []:
        if isinstance(tag, str) and tag.startswith(DREAMLANDS_HUB_PREFIXES):
            return True
    return False


def get_crocevia():
    from evennia.utils import search
    rooms = search.search_tag(CROCEVIA_TAG, category=CROCEVIA_CATEGORY)
    return rooms[0] if rooms else None


def get_destinazione_ingresso(stanza_partenza):
    """Sceglie dove far atterrare chi si addormenta, in base a dove si
    trovava (helps/dreaming.txt, vedi nota di modulo). Ripiega sul
    crocevia se la zona di partenza non ha un ingresso dedicato, o se
    quell'ingresso non e' stato ancora costruito."""
    from evennia.utils import search

    if stanza_partenza:
        for categoria, tag in DESTINAZIONE_PER_CATEGORIA.items():
            if stanza_partenza.tags.get(category=categoria):
                trovate = search.search_tag(tag, category=CROCEVIA_CATEGORY)
                if trovate:
                    return trovate[0]
        for tag_partenza in stanza_partenza.tags.get(category="start_room", return_list=True) or []:
            for prefisso, tag_arrivo in DESTINAZIONE_PER_PREFISSO_START_ROOM.items():
                if isinstance(tag_partenza, str) and tag_partenza.startswith(prefisso):
                    trovate = search.search_tag(tag_arrivo, category=CROCEVIA_CATEGORY)
                    if trovate:
                        return trovate[0]
    return get_crocevia()


def sveglia_da_sogno(personaggio, messaggio=None):
    """Riporta personaggio dal sogno al mondo reale, se davvero ci si
    trova dentro. Ritorna True se lo ha svegliato per davvero (usato sia
    da CmdWake su se stessi, sia - correggendo un bug reale - da
    world/posizione.py:tenta_wake() su un bersaglio altrui)."""
    if not in_dreamlands(personaggio.location):
        return False
    destinazione = personaggio.db.recall_room or personaggio.db.respawn_room
    if not destinazione:
        return False
    if messaggio:
        personaggio.msg(messaggio)
    personaggio.move_to(destinazione, quiet=True, move_type="teleport")
    return True


def fluttua_skill_casuali(personaggio):
    """helps/dreaming.txt: "a character's rating in various skills may
    fluctuate up or down while traveling between worlds." Nessuna
    formula dalla fonte: qui NUMERO_SKILL_FLUTTUANTI skill a caso tra
    quelle gia' possedute (rating > 0) cambiano di un piccolo importo
    casuale, mai sotto 0."""
    skills = personaggio.db.skills or {}
    conosciute = [sid for sid, rating in skills.items() if rating > 0]
    if not conosciute:
        return
    for sid in random.sample(conosciute, min(NUMERO_SKILL_FLUTTUANTI, len(conosciute))):
        delta = random.randint(FLUTTUAZIONE_SKILL_MIN, FLUTTUAZIONE_SKILL_MAX)
        skills[sid] = max(0, skills[sid] + delta)
    personaggio.db.skills = skills
