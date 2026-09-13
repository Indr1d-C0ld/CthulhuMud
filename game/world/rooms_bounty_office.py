"""
Ufficio della Gilda dei Cacciatori di Taglie a Dylath-Leen (Fase G,
decima tornata): confermato dalla fonte (helps/bounty.txt) come sede
delle missioni ("players can go on missions for the Dylath-Leen Bounty
Hunters Guild") - collegata all'hub newbie "dylath_reformatory" gia'
costruito (world/rooms_newbie.py), con lo stesso pattern gia' usato per
la Fucina di Maro a Ulthar.
"""

from evennia.utils import create, search

from world.rooms_newbie import stanza_per_ruolo

TAG_UFFICIO = "dylath_bounty_office"
TAG_CATEGORY = "start_room"


def _get_or_create_ufficio():
    esistente = search.search_tag(TAG_UFFICIO, category=TAG_CATEGORY)
    if esistente:
        return esistente[0]
    stanza = create.create_object(
        "typeclasses.rooms.Room",
        key="Ufficio della Gilda dei Cacciatori di Taglie",
    )
    stanza.db.desc = (
        "Bacheche coperte di volantini con volti sospetti riempiono le pareti "
        "di questo ufficio spartano. Un bancone consumato separa i visitatori "
        "da un archivio di taglie, missioni e conti in sospeso."
    )
    stanza.tags.add(TAG_UFFICIO, category=TAG_CATEGORY)
    return stanza


def _get_or_create_impiegato(stanza):
    esistente = [o for o in stanza.contents if o.db.impiegato_taglie]
    if esistente:
        return esistente[0]
    npc = create.create_object(
        "typeclasses.npcs.NPC",
        key="l'impiegato della gilda",
        location=stanza,
    )
    npc.db.desc = (
        "Un uomo magro con le maniche rimboccate, che sfoglia un registro di "
        "nomi e taglie senza mai alzare completamente lo sguardo."
    )
    npc.db.impiegato_taglie = True
    npc.db.ostile = False
    return npc


def crea_ufficio_taglie():
    """Crea (se non esiste gia') l'ufficio e il suo impiegato, collegati
    alla stanza di RECALL di Dylath-Leen. Idempotente."""
    hub = stanza_per_ruolo("dylath_reformatory", "recall")
    ufficio = _get_or_create_ufficio()
    _get_or_create_impiegato(ufficio)

    if hub:
        esiste_uscita = any(
            e.destination and e.destination.id == ufficio.id for e in hub.exits
        )
        if not esiste_uscita:
            create.create_object(
                "typeclasses.exits.Exit", key="taglie", aliases=["ufficio"],
                location=hub, destination=ufficio,
            )
        esiste_ritorno = any(
            e.destination and e.destination.id == hub.id for e in ufficio.exits
        )
        if not esiste_ritorno:
            create.create_object(
                "typeclasses.exits.Exit", key="fuori", aliases=["f"],
                location=ufficio, destination=hub,
            )
    return ufficio
