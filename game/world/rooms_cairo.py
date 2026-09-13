"""
Il Cairo del gioco (Fase E, quarta tornata), ricostruito dalla guida
testuale ufficiale (cthulhumud.com/guides_cairo) - non da una mappa
visiva: quella (cairo.gif, citata nel Dossier Miskatonic) non ci e'
mai stata fornita in questa sessione. La guida testuale e' pero'
piuttosto ricca: cinque macro-aree e sette negozi nominati nel Bazaar,
piu' quattro siti esterni alla citta'.

A differenza di Arkham (indirizzi puntuali per 73 edifici), qui la
fonte parla di AREE, non di singoli edifici con indirizzo: la fedelta'
possibile e' quindi a livello di quartiere, non di singola bottega -
un edificio per area invece di uno per via, con l'eccezione del
Bazaar che elenca esplicitamente 7 esercizi.

NOTA: Cairo e' ora collegata ad Arkham via nave (Moli sul Nilo <->
"In Mare Aperto" <-> Moli Passeggeri di Arkham), coerentemente con la
guida ufficiale ("vessels traveling to America and England"). I Moli
Passeggeri di Arkham ospitano quindi due collegamenti indipendenti
(chiavi diverse, nessun conflitto): "largo" verso il relitto del
sommergibile, "nave" verso l'Egitto.
"""

from evennia.utils import create, search

TAG_CATEGORY = "cairo_room"

ROOMS = {
    "bazaar": (
        "Il Bazaar del Cairo",
        "Il centro pulsante della citta', gremito di venditori "
        "ambulanti, portatori d'acqua e cittadini che contrattano ad "
        "alta voce. L'aria e' densa di spezie, fumo di narghile' e "
        "polvere dorata sollevata da mille sandali.",
    ),
    "docks": (
        "I Moli sul Nilo",
        "Battelli da pesca e piroscafi diretti verso l'America e "
        "l'Inghilterra sono ormeggiati lungo la riva fangosa del "
        "Nilo. Facchini scalzi caricano casse sotto il sole "
        "implacabile.",
    ),
    "city_gates": (
        "Le Porte della Città",
        "Un massiccio arco di pietra segna il confine settentrionale "
        "del Cairo. Oltre le porte, la città lascia il posto alla "
        "sabbia e alla foschia dell'altopiano.",
    ),
    "pyramids": (
        "Le Piramidi di Giza",
        "Le grandi piramidi si ergono sull'altopiano di Giza, "
        "immense e silenziose. Il vento del deserto porta con se' un "
        "silenzio che nessuna guida turistica riesce mai a "
        "descrivere davvero.",
    ),
    "sphinx": (
        "La Sfinge",
        "Il volto consumato dalla Sfinge osserva l'orizzonte da "
        "millenni, a sud-est delle piramidi. Alcuni studiosi "
        "dell'università Miskatonic sosterrebbero che osservi "
        "qualcosa di ben più specifico dell'orizzonte.",
    ),
    "administrative_area": (
        "L'Area Amministrativa",
        "Uffici coloniali dalle facciate imbiancate ospitano "
        "l'amministrazione del Khedivè. Soldati in uniforme "
        "sorvegliano gli ingressi con aria annoiata.",
    ),
    "british_citadel": (
        "La Cittadella Britannica",
        "Il quartier generale delle forze del Khedivè, una fortezza "
        "di pietra chiara che domina la parte orientale della città. "
        "Le sentinelle non lasciano passare nessuno senza un buon "
        "motivo.",
    ),
    "residential_ne": (
        "Quartiere Residenziale di Nord-Est",
        "Case dai balconi intagliati in legno ospitano mercanti e "
        "commercianti benestanti. Il profumo di gelsomino aleggia "
        "nei cortili interni.",
    ),
    "residential_se": (
        "Quartiere Residenziale di Sud-Est",
        "Un quartiere simile a quello di nord-est ma piu' tranquillo, "
        "dove vivono soprattutto famiglie di funzionari e piccoli "
        "proprietari terrieri.",
    ),
    "slums": (
        "Gli Slums",
        "Vicoli stretti e case fatiscenti ospitano i cittadini piu' "
        "poveri del Cairo. Qui la legge del Khedivè conta molto meno "
        "di quella della strada.",
    ),
    "causeway": (
        "La Strada Rialzata",
        "Un'antica strada rialzata sul livello delle inondazioni "
        "annuali del Nilo, che conduce verso sud, fuori dai confini "
        "della città.",
    ),
    "great_mosque": (
        "La Grande Moschea",
        "In fondo alla strada rialzata, i minareti della Grande "
        "Moschea si stagliano contro il cielo. Il richiamo alla "
        "preghiera risuona cinque volte al giorno su tutta la città.",
    ),
}

BAZAAR_SHOPS = {
    "anubis_hotel": (
        "Anubis Hotel",
        "hotel anubis",
        "anubis",
        "Un albergo modesto ma pulito, con una grande statua di Anubi "
        "all'ingresso che alcuni ospiti giurano muova la testa quando "
        "nessuno guarda direttamente.",
    ),
    "cloth_merchant": (
        "Mercante di Stoffe",
        "mercante di stoffe",
        "stoffe",
        "Rotoli di lino egiziano di ogni colore riempiono la bottega, "
        "impilati fino al soffitto basso.",
    ),
    "farmers_stall": (
        "Bancarella dei Contadini",
        "bancarella dei contadini",
        "bancarella",
        "Frutta e verdura fresca, appena portata dai campi lungo il "
        "Nilo, sono esposte su teli colorati stesi a terra.",
    ),
    "abduls_armoury": (
        "Armeria di Abdul",
        "armeria di abdul",
        "abdul",
        "Sciabole curve e fucili d'ordinanza sono appesi alle pareti. "
        "Abdul rifornisce soprattutto i soldati del Khedivè, ma non "
        "fa troppe domande ad altri clienti paganti.",
    ),
    "winemakers_shop": (
        "Bottega del Vinaio",
        "bottega del vinaio",
        "vinaio",
        "Anfore di vino egiziano riempiono gli scaffali di questa "
        "piccola bottega, il cui proprietario ne decanta le virtu' "
        "con entusiasmo forse eccessivo.",
    ),
    "falcon_armory": (
        "Falcon Armory",
        "falcon armory",
        "falcon",
        "Un'armeria piu' moderna delle altre, che vende anche armi da "
        "fuoco importate dall'Europa a chi puo' permettersele.",
    ),
    "bakery": (
        "Panetteria del Bazaar",
        "panetteria",
        "pane",
        "L'odore di pane appena sfornato e dolci al miele si diffonde "
        "per tutto il Bazaar, richiamando una fila costante di "
        "clienti.",
    ),
}

CONNECTIONS = [
    ("bazaar", "nord", "docks"),
    ("docks", "nord", "city_gates"),
    ("city_gates", "nord", "pyramids"),
    ("pyramids", "est", "sphinx"),
    ("bazaar", "est", "administrative_area"),
    ("administrative_area", "est", "british_citadel"),
    ("administrative_area", "sud", "residential_se"),
    ("docks", "est", "residential_ne"),
    ("bazaar", "ovest", "slums"),
    ("bazaar", "sud", "causeway"),
    ("causeway", "sud", "great_mosque"),
]

OPPOSTA = {"nord": "sud", "sud": "nord", "est": "ovest", "ovest": "est"}


def _get_or_create_room(chiave):
    tag_key = f"cairo_{chiave}"
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


def _get_or_create_shop(chiave, bazaar_room):
    tag_key = f"cairo_shop_{chiave}"
    existing = search.search_tag(tag_key, category=TAG_CATEGORY)
    if existing:
        return existing[0]
    nome, uscita, alias, descrizione = BAZAAR_SHOPS[chiave]
    room = create.create_object("typeclasses.rooms.Room", key=nome)
    room.db.desc = descrizione
    room.tags.add(tag_key, category=TAG_CATEGORY)
    _get_or_create_exit(bazaar_room, room, uscita, alias)
    _get_or_create_exit(room, bazaar_room, "fuori", "fu")
    return room


def _collega_arkham():
    """
    Collega i Moli sul Nilo ai Moli Passeggeri di Arkham, coerentemente
    con la guida ufficiale ("vessels traveling to America and
    England"): un lungo viaggio per nave, con una stanza intermedia
    che rappresenta la traversata. Idempotente; se Arkham non e'
    ancora stata costruita, non fa nulla e viene ritentato alla
    prossima chiamata di crea_cairo().
    """
    arkham_docks = search.search_tag("building_passenger_docks", category="arkham_building")
    if not arkham_docks:
        return None
    arkham_docks = arkham_docks[0]

    cairo_docks = _get_or_create_room("docks")

    existing = search.search_tag("cairo_high_seas", category=TAG_CATEGORY)
    if existing:
        mare_aperto = existing[0]
    else:
        mare_aperto = create.create_object(
            "typeclasses.rooms.Room", key="In Mare Aperto"
        )
        mare_aperto.db.desc = (
            "Settimane di navigazione attraverso il Mediterraneo e "
            "l'Atlantico separano l'Egitto dalle coste del "
            "Massachusetts. L'equipaggio conosce la rotta a memoria; "
            "i passeggeri, molto meno."
        )
        mare_aperto.tags.add("cairo_high_seas", category=TAG_CATEGORY)

    _get_or_create_exit(cairo_docks, mare_aperto, "nave", "imbarco")
    _get_or_create_exit(mare_aperto, cairo_docks, "cairo", None)
    _get_or_create_exit(mare_aperto, arkham_docks, "arkham", None)
    _get_or_create_exit(arkham_docks, mare_aperto, "nave", "imbarco")

    return mare_aperto


def crea_cairo():
    """
    Crea (se non esistono gia') tutte le aree del Cairo e i 7 negozi
    del Bazaar. Idempotente. Ritorna {chiave: Room} con tutte le aree
    e i negozi (chiavi separate, nessuna sovrapposizione di nomi).
    """
    aree = {chiave: _get_or_create_room(chiave) for chiave in ROOMS}

    for chiave_a, direzione, chiave_b in CONNECTIONS:
        room_a = aree[chiave_a]
        room_b = aree[chiave_b]
        direzione_opposta = OPPOSTA[direzione]
        _get_or_create_exit(room_a, room_b, direzione, direzione[0])
        _get_or_create_exit(room_b, room_a, direzione_opposta, direzione_opposta[0])

    negozi = {chiave: _get_or_create_shop(chiave, aree["bazaar"]) for chiave in BAZAAR_SHOPS}

    _collega_arkham()

    problemi = []
    for room in list(aree.values()) + list(negozi.values()):
        chiavi = [e.key for e in room.exits]
        if len(set(chiavi)) != len(chiavi):
            problemi.append((room.key, chiavi))
    if problemi:
        raise RuntimeError(f"Conflitti di direzione al Cairo: {problemi}")

    risultato = dict(aree)
    risultato.update(negozi)
    return risultato
