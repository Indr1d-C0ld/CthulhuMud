"""
NPC di esempio per testare LEARN/PRACTICE (M2).

Non e' ancora il sistema di building NPC completo (vedi Architettura
Balthasar §02, §06): un solo insegnante di prova nella sala comune di
Arkham, sufficiente a rendere provabili i comandi learn/practice/debate.
"""

from evennia.utils import create, search

TAG_CATEGORY = "start_npc"


def crea_npc_newbie():
    """Crea (se non esiste gia') Dr. Henry Armitage nella sala comune di
    Arkham: insegna le skill di base dell'hub e funge anche da bersaglio
    per PRACTICE/DEBATE. Idempotente."""
    from world.rooms_newbie import stanza_per_ruolo

    tag = "armitage"
    esistente = search.search_tag(tag, category=TAG_CATEGORY)
    if esistente:
        return esistente[0]

    stanza = stanza_per_ruolo("arkham_miskatonic", "recall")
    npc = create.create_object(
        "typeclasses.npcs.NPC",
        key="Dr. Henry Armitage",
        location=stanza,
    )
    npc.db.desc = (
        "Il bibliotecario capo della Miskatonic University, con un aspetto "
        "curato ma lo sguardo di chi ha letto troppi libri proibiti."
    )
    npc.db.skills_insegnabili = [
        "arkham", "education", "streetwise", "world_affairs", "occult", "debating",
        "spell_casting", "cure_light", "shocking_grasp", "bless",
        "detect_magic", "mask_self", "clairvoyance",
    ]
    npc.db.is_practice_trainer = True
    npc.db.triggers = [
        {
            "fase": "reaction",
            "tipo": "icc",
            "sottotipo": "say",
            "template": "occult|cthulhu|necronomicon",
            "dice": "Attento a pronunciare certi nomi ad alta voce, {attore}... "
                    "i muri di questa universita' hanno orecchie, e alcuni libri hanno occhi.",
        },
        {
            "fase": "challenge",
            "tipo": "attack",
            "sottotipo": "kill",
            "solo_se_vittima": True,
            "blocca": True,
            "dice": "Niente violenza nella sala di lettura, {attore}! Ne va della mia incolumita' "
                    "e della vostra reputazione accademica.",
        },
    ]
    npc.tags.add(tag, category=TAG_CATEGORY)
    return npc


def crea_mob_test():
    """Crea (se non esiste gia') un piccolo NPC ostile nella sala comune di
    Arkham, solo per provare il combattimento (M3). Placeholder: il
    sistema di building/mobprogs vero arrivera' con Architettura
    Balthasar §06."""
    from world.rooms_newbie import stanza_per_ruolo

    tag = "topo_test"
    esistente = search.search_tag(tag, category=TAG_CATEGORY)
    if esistente:
        return esistente[0]

    stanza = stanza_per_ruolo("arkham_miskatonic", "recall")
    mob = create.create_object(
        "typeclasses.npcs.NPC",
        key="un topo enorme",
        location=stanza,
    )
    mob.db.desc = (
        "Un topo dalle dimensioni innaturali, intrufolatosi tra le pile di "
        "libri della sala comune. I suoi occhietti rossi non promettono nulla di buono."
    )
    mob.db.hp = 8
    mob.db.hp_max = 8
    mob.db.livello = 1
    mob.db.skills = {"hand_to_hand": 20, "dodge": 10}
    mob.db.ostile = False  # per ora si difende solo se attaccato, non aggredisce
    mob.tags.add(tag, category=TAG_CATEGORY)
    return mob
