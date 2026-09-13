"""
Popolamento Forgiatura (Fase G, terza tornata): l'incudine di Maro a
Ulthar (gia' costruita in world/rooms_ulthar.py) e la sua bottega di
materiali, piu' un'incudine nella Fucina di Chorl a Zoog Village (gia'
descritta come una forgia - vedi world/rooms_zoogvillage.py - ma finora
priva di un'incudine vera e propria).
"""

from evennia.utils import search

from world.economia import crea_mercante
from world.rooms_ulthar import crea_ulthar, FUCINA_MARO_TAG, TAG_CATEGORY as ULTHAR_TAG_CATEGORY

MATERIALI_MARO = [
    {"chiave": "cristallo", "nome": "un cristallo grezzo", "prezzo": 25,
     "descrizione": "Un cristallo dalle sfaccettature irregolari, buono per forgiare.",
     "materiale_forgiatura": 10},
    {"chiave": "oro", "nome": "una pepita d'oro", "prezzo": 45,
     "descrizione": "Una pepita d'oro grezzo, pesante in mano.",
     "materiale_forgiatura": 20},
    {"chiave": "diamante", "nome": "un diamante grezzo", "prezzo": 80,
     "descrizione": "Un diamante non tagliato, che cattura la luce della forgia.",
     "materiale_forgiatura": 35},
    {"chiave": "mithril", "nome": "una scheggia di mithril", "prezzo": 150,
     "descrizione": "Un frammento di un metallo leggerissimo e freddo al tatto, "
                    "raro anche nelle Dreamlands.",
     "materiale_forgiatura": 50},
]


def _crea_incudine(stanza):
    from evennia.utils import create

    esistente = [o for o in stanza.contents if o.db.incudine]
    if esistente:
        return esistente[0]
    incudine = create.create_object(
        "typeclasses.objects.Object",
        key="un'incudine",
        location=stanza,
    )
    incudine.db.desc = "Una pesante incudine di ferro, annerita da anni di lavoro."
    incudine.db.incudine = True
    incudine.locks.add("get:false()")
    return incudine


def popola_forgiatura():
    """Crea (se non gia' presenti) l'incudine + il mercante di materiali
    a Ulthar, e l'incudine nella Fucina di Chorl a Zoog Village.
    Idempotente."""
    crea_ulthar()  # assicura che la Fucina di Maro esista

    fucina_maro = search.search_tag(FUCINA_MARO_TAG, category=ULTHAR_TAG_CATEGORY)[0]
    _crea_incudine(fucina_maro)

    maro_esistente = [
        obj for obj in fucina_maro.contents
        if obj.attributes.has("negozio") and obj.db.negozio
    ]
    if maro_esistente:
        maro = maro_esistente[0]
    else:
        maro = crea_mercante(
            fucina_maro,
            "Maro, il fabbro",
            "Un uomo dalle spalle larghe e le braccia coperte di cicatrici da "
            "ustione, che valuta ogni cliente dalla presa della stretta di mano.",
            MATERIALI_MARO,
        )
        maro.db.skills_insegnabili = ["forging", "lore"]
        maro.db.is_practice_trainer = True

    fucina_chorl = search.search_tag("zv_blacksmith_chorl", category="zoogvillage_room")
    incudine_chorl = None
    if fucina_chorl:
        incudine_chorl = _crea_incudine(fucina_chorl[0])

    return maro, incudine_chorl
