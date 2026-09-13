"""
Ulthar, la citta' dei gatti nelle Dreamlands (Fase E, prima tornata),
ricostruita dalla mappa del sito ufficiale (ulthar.jpg). Citta' murata
con pianta stradale ben leggibile: Hatheg Way, Barzai Street, Xarnes
Street, Atal Way, Calico Cross, attorno a una piazza centrale con
fontana e un grande tempio dal tetto rosso.

Barzai e Atal sono personaggi citati esplicitamente da Lovecraft in
"The Other Gods", entrambi legati al culto dei gatti e agli Dei della
Terra proprio a Ulthar - la scelta dei nomi delle vie non e' casuale.

Integrazione con l'hub newbie gia' esistente (world/rooms_newbie.py,
hub "ulthar_temple"): la piazza con la fontana e' la stessa stanza di
RECALL/RESPAWN gia' creata li' ("Tempio di Ulthar - La Fontana"), e la
cripta sotto il tempio e' la stessa stanza di MORGUE ("Tempio di Ulthar
- Obitorio") - non vengono duplicate, solo collegate alla nuova pianta
stradale.

NOTA DI METODO (come per Arkham e il sottomarino): la mappa ci mostra i
nomi delle vie e la loro disposizione attorno alla piazza, ma non ogni
singolo dettaglio di quali edifici si affaccino dove - quelli, quando
serviranno, andranno popolati con lo stesso approccio usato per Arkham.
"""

from evennia.utils import create, search

TAG_CATEGORY = "ulthar_room"

STREETS = {
    "hatheg_way": (
        "Hatheg Way",
        "La via settentrionale di Ulthar, che prende il nome dalla "
        "città gemella al di la' delle colline. Gatti di ogni colore "
        "sonnecchiano sui davanzali delle case di pietra.",
    ),
    "barzai_street": (
        "Barzai Street",
        "Una via acciottolata che porta il nome del saggio Barzai, "
        "che tanto amava studiare gli dei da salire un giorno troppo "
        "in alto per fare ritorno.",
    ),
    "xarnes_street": (
        "Xarnes Street",
        "Una stretta via commerciale nella parte orientale della "
        "città, dove i mercanti onirici espongono le loro merci più "
        "strane.",
    ),
    "atal_way": (
        "Atal Way",
        "Una via ampia che porta il nome del compagno di Barzai, "
        "l'unico tornato a raccontare cosa si trova oltre le vette "
        "proibite.",
    ),
    "calico_cross": (
        "Calico Cross",
        "La via meridionale di Ulthar, cosi' chiamata per il "
        "viavai instancabile di gatti maculati che vi si radunano "
        "ogni crepuscolo. Il grande tempio domina la vista verso "
        "nord.",
    ),
}

CONNECTIONS = [
    # la piazza (vedi crea_ulthar) fa da mozzo centrale con le quattro
    # vie principali come raggi; Calico Cross e Barzai Street hanno
    # anche un collegamento diretto tra loro, e Xarnes Street e' una
    # traversa secondaria che si stacca da Atal Way.
    ("calico_cross", "est", "barzai_street"),
    ("atal_way", "est", "xarnes_street"),
]

# La Fucina di Maro (Fase G, terza tornata): confermata dalla fonte
# (guides_forging.txt/guides_better.txt) come blacksmith con incudine a
# Ulthar, dove forgiare senza sapere l'incantesimo Greater Creation.
# Non e' tra le vie della mappa originale: aggiunta come bottega fuori
# da Xarnes Street (coerente con la descrizione di quella via come zona
# commerciale), stessa logica gia' usata per gli edifici di Arkham.
FUCINA_MARO_TAG = "ulthar_fucina_maro"

OPPOSTA = {"nord": "sud", "sud": "nord", "est": "ovest", "ovest": "est"}

PLAZA_TAG = "ulthar_temple_recall"
CRYPT_TAG = "ulthar_temple_morgue"
TEMPLE_KEY = "ulthar_temple_interior"


def _get_or_create_street(chiave):
    tag_key = f"street_{chiave}"
    existing = search.search_tag(tag_key, category=TAG_CATEGORY)
    if existing:
        return existing[0]
    nome, descrizione = STREETS[chiave]
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


def _get_plaza():
    """La piazza con la fontana: stessa stanza di RECALL/RESPAWN dell'hub newbie."""
    rooms = search.search_tag(PLAZA_TAG, category="start_room")
    if not rooms:
        return None
    return rooms[0]


def _get_crypt():
    """La cripta sotto il tempio: stessa stanza di MORGUE dell'hub newbie."""
    rooms = search.search_tag(CRYPT_TAG, category="start_room")
    if not rooms:
        return None
    return rooms[0]


def _get_or_create_temple_interior():
    """L'interno del grande tempio dal tetto rosso, tra la piazza e la cripta."""
    existing = search.search_tag(TEMPLE_KEY, category=TAG_CATEGORY)
    if existing:
        return existing[0]
    room = create.create_object("typeclasses.rooms.Room", key="Il Grande Tempio di Ulthar")
    room.db.desc = (
        "Colonne di pietra bianca sorreggono un tetto di tegole rosse, "
        "visibile da ogni angolo della città. Statue di gatti "
        "accovacciati vegliano lungo le pareti, e l'aria odora di "
        "incenso e di qualcosa di piu' antico dell'incenso stesso."
    )
    room.tags.add(TEMPLE_KEY, category=TAG_CATEGORY)
    return room


def _get_or_create_fucina_maro():
    """La bottega del fabbro Maro, con la sua incudine (vedi
    world/forgiatura.py)."""
    existing = search.search_tag(FUCINA_MARO_TAG, category=TAG_CATEGORY)
    if existing:
        return existing[0]
    room = create.create_object("typeclasses.rooms.Room", key="La Fucina di Maro")
    room.db.desc = (
        "Il calore di una forgia sempre accesa riempie questa piccola "
        "bottega, ricavata a ridosso di Xarnes Street. Un'incudine "
        "annerita dagli anni occupa il centro della stanza, circondata "
        "da attrezzi appesi con cura maniacale."
    )
    room.tags.add(FUCINA_MARO_TAG, category=TAG_CATEGORY)
    return room


def crea_ulthar():
    """
    Crea (se non esistono gia') le 5 vie di Ulthar, il tempio, e i
    collegamenti con la piazza/fontana e la cripta gia' create come
    hub newbie. Idempotente. Se l'hub newbie non e' ancora stato
    creato, i collegamenti alla piazza vengono rimandati alla
    prossima chiamata.

    Ritorna il dizionario {chiave_via: Room} (senza piazza/tempio/cripta,
    reperibili con le funzioni _get_plaza/_get_or_create_temple_interior/
    _get_crypt).
    """
    vie = {chiave: _get_or_create_street(chiave) for chiave in STREETS}

    for chiave_a, direzione, chiave_b in CONNECTIONS:
        room_a = vie[chiave_a]
        room_b = vie[chiave_b]
        direzione_opposta = OPPOSTA[direzione]
        _get_or_create_exit(room_a, room_b, direzione, direzione[0])
        _get_or_create_exit(room_b, room_a, direzione_opposta, direzione_opposta[0])

    plaza = _get_plaza()
    if plaza:
        # la piazza e' il mozzo centrale, con le quattro vie come raggi
        _get_or_create_exit(plaza, vie["hatheg_way"], "nord", "n")
        _get_or_create_exit(vie["hatheg_way"], plaza, "sud", "s")
        _get_or_create_exit(plaza, vie["calico_cross"], "sud", "s")
        _get_or_create_exit(vie["calico_cross"], plaza, "nord", "n")
        _get_or_create_exit(plaza, vie["atal_way"], "est", "e")
        _get_or_create_exit(vie["atal_way"], plaza, "ovest", "o")
        _get_or_create_exit(plaza, vie["barzai_street"], "ovest", "o")
        _get_or_create_exit(vie["barzai_street"], plaza, "est", "e")

        tempio = _get_or_create_temple_interior()
        _get_or_create_exit(plaza, tempio, "tempio", "tempio")
        _get_or_create_exit(tempio, plaza, "fuori", "fu")

        cripta = _get_crypt()
        if cripta:
            _get_or_create_exit(tempio, cripta, "giu", "g")
            _get_or_create_exit(cripta, tempio, "su", "s")

    fucina = _get_or_create_fucina_maro()
    _get_or_create_exit(vie["xarnes_street"], fucina, "est", "e")
    _get_or_create_exit(fucina, vie["xarnes_street"], "ovest", "o")

    # verifica di sicurezza sugli stessi conflitti gia' visti altrove
    problemi = []
    tutte = list(vie.values())
    tutte.append(fucina)
    if plaza:
        tutte.append(plaza)
        tutte.append(_get_or_create_temple_interior())
        if _get_crypt():
            tutte.append(_get_crypt())
    for room in tutte:
        chiavi = [e.key for e in room.exits]
        if len(set(chiavi)) != len(chiavi):
            problemi.append((room.key, chiavi))
    if problemi:
        raise RuntimeError(f"Conflitti di direzione a Ulthar: {problemi}")

    return vie
