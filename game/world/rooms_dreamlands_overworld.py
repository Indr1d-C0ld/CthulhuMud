"""
Il connettivo regionale delle Dreamlands (Fase E, terza tornata): i
sentieri che uniscono Ulthar, Zoog Village/il Bosco Incantato e
Dylath-Leen, ricostruiti dalla mappa regionale del sito ufficiale
(dlands1.jpg, attribuita a "Ithaqua" nel Dossier Miskatonic).

NOTA DI METODO piu' forte del solito: questa mappa usa un font runico
stilizzato, molto piu' difficile da leggere con certezza rispetto alle
mappe di Arkham/Ulthar/Zoog Village. Manteniamo solo i nomi letti con
ragionevole sicurezza (The Enchanted Wood, Oukranos River, e la
posizione relativa di Ulthar/Nir/Hatheg/Dylath-Leen, tutti confermati
anche dal canone di Lovecraft e dalla tabella delle professioni del
Dossier Miskatonic) e NON costruiamo citta' vere e proprie per Nir e
Hatheg - restano nominate come punti di passaggio sulla strada, non
ancora luoghi esplorabili. Dylath-Leen ha gia' un hub newbie
(world/rooms_newbie.py, "dylath_reformatory") che qui colleghiamo alla
rete stradale senza costruire il resto della citta' - stesso approccio
di rimando esplicito usato altrove per le lacune non ancora colmate.
"""

from evennia.utils import create, search

TAG_CATEGORY = "dreamlands_overworld"

ROOMS = {
    "crocevia": (
        "Il Crocevia delle Dreamlands",
        "Un incrocio di sentieri sterrati nel cuore della regione "
        "onirica. Segnavia consumati indicano direzioni che sembrano "
        "cambiare leggermente ogni volta che non li si guarda "
        "direttamente.",
    ),
    "verso_ulthar": (
        "Il Sentiero di Ulthar",
        "Il sentiero sale dolcemente verso le mura di Ulthar, "
        "visibili in lontananza. Gatti selvatici osservano i "
        "viandanti dai cespugli ai lati della strada.",
    ),
    "presso_nir": (
        "Nei Pressi di Nir",
        "Il sentiero costeggia i campi che circondano la piccola "
        "città di Nir, appena visibile oltre un dolce declivio. Non "
        "e' ancora possibile entrarvi - i suoi vicoli restano, per "
        "ora, non mappati.",
    ),
    "verso_bosco": (
        "Il Margine del Bosco Incantato",
        "Gli alberi si infittiscono qui, e la luce del sole (per "
        "quanto le Dreamlands ne abbiano uno) si fa più tenue e "
        "verdastra. Da qualche parte tra i tronchi si sente il "
        "chiacchiericcio distante degli Zoog.",
    ),
    "presso_hatheg": (
        "Nei Pressi di Hatheg",
        "In lontananza, oltre un ponte di pietra, si scorgono i tetti "
        "di Hatheg, la citta' gemella di Ulthar ai piedi del Monte "
        "Hatheg-Kla. Anche questa citta' resta, per ora, non "
        "esplorabile oltre questo punto.",
    ),
    "lungofiume_skai": (
        "Lungo il Fiume Skai",
        "Il sentiero segue l'argine del fiume Skai verso sud, le sue "
        "acque scure dirette verso il mare e, oltre esso, verso "
        "Dylath-Leen dalle torri di basalto nero.",
    ),
}

CONNECTIONS = [
    ("crocevia", "ovest", "verso_ulthar"),
    ("crocevia", "est", "verso_bosco"),
    ("crocevia", "nord", "presso_nir"),
    ("presso_nir", "nord", "presso_hatheg"),
    ("crocevia", "sud", "lungofiume_skai"),
]

OPPOSTA = {"nord": "sud", "sud": "nord", "est": "ovest", "ovest": "est"}

DYLATH_RECALL_TAG = "dylath_reformatory_recall"


def _get_or_create_room(chiave):
    tag_key = f"dlo_{chiave}"
    existing = search.search_tag(tag_key, category=TAG_CATEGORY)
    if existing:
        return existing[0]
    nome, descrizione = ROOMS[chiave]
    room = create.create_object("typeclasses.rooms.Room", key=nome)
    room.db.desc = descrizione
    room.tags.add(tag_key, category=TAG_CATEGORY)
    return room


def _get_or_create_exit(origine, destinazione, chiave, alias):
    for obj in origine.exits:
        if obj.destination and obj.destination.id == destinazione.id:
            return obj
    return create.create_object(
        "typeclasses.exits.Exit",
        key=chiave,
        aliases=[alias] if alias else [],
        location=origine,
        destination=destinazione,
    )


def crea_dreamlands_overworld():
    """
    Crea (se non esistono gia') i sentieri regionali delle Dreamlands e
    li collega a Ulthar (Hatheg Way), Zoog Village (Cancello
    Settentrionale) e Dylath-Leen (hub newbie gia' esistente).
    Idempotente. Se una delle tre zone non e' ancora stata costruita, il
    collegamento a quella zona viene rimandato alla prossima chiamata.
    """
    stanze = {chiave: _get_or_create_room(chiave) for chiave in ROOMS}

    for chiave_a, direzione, chiave_b in CONNECTIONS:
        room_a = stanze[chiave_a]
        room_b = stanze[chiave_b]
        direzione_opposta = OPPOSTA[direzione]
        _get_or_create_exit(room_a, room_b, direzione, direzione[0])
        _get_or_create_exit(room_b, room_a, direzione_opposta, direzione_opposta[0])

    # Ulthar: Hatheg Way ha gia' solo l'uscita "sud" verso la piazza
    hatheg_way = search.search_tag("street_hatheg_way", category="ulthar_room")
    if hatheg_way:
        hatheg_way = hatheg_way[0]
        _get_or_create_exit(hatheg_way, stanze["verso_ulthar"], "nord", "n")
        _get_or_create_exit(stanze["verso_ulthar"], hatheg_way, "sud", "s")

    # Zoog Village: il Cancello Settentrionale ha gia' solo l'uscita
    # "sud" verso la Radura Aperta
    north_gate = search.search_tag("zv_north_gate", category="zoogvillage_room")
    if north_gate:
        north_gate = north_gate[0]
        _get_or_create_exit(north_gate, stanze["verso_bosco"], "nord", "n")
        _get_or_create_exit(stanze["verso_bosco"], north_gate, "sud", "s")

    # Dylath-Leen: colleghiamo il sentiero fluviale al recall dell'hub
    # newbie gia' esistente, senza costruire il resto della citta'
    dylath_recall = search.search_tag(DYLATH_RECALL_TAG, category="start_room")
    if dylath_recall:
        dylath_recall = dylath_recall[0]
        _get_or_create_exit(stanze["lungofiume_skai"], dylath_recall, "sud", "s")
        _get_or_create_exit(dylath_recall, stanze["lungofiume_skai"], "nord", "n")

    problemi = []
    tutte = list(stanze.values())
    for extra_tag, extra_cat in (
        ("street_hatheg_way", "ulthar_room"),
        ("zv_north_gate", "zoogvillage_room"),
        (DYLATH_RECALL_TAG, "start_room"),
    ):
        found = search.search_tag(extra_tag, category=extra_cat)
        if found:
            tutte.append(found[0])
    for room in tutte:
        chiavi = [e.key for e in room.exits]
        if len(set(chiavi)) != len(chiavi):
            problemi.append((room.key, chiavi))
    if problemi:
        raise RuntimeError(f"Conflitti di direzione nel connettivo Dreamlands: {problemi}")

    return stanze
