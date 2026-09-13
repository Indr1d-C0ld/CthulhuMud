"""
La griglia stradale di Arkham (Fase D, prima tornata: le vie, non ancora
i 73 edifici che vi si affacciano - quelli arrivano nella tornata
successiva, categoria per categoria).

Schema deciso col committente: "una stanza per via" - ogni via nominata
diventa un'unica stanza percorribile; dove il catalogo mostra edifici
su entrambi i lati di un riferimento (Garrison Street per Est/Ovest, il
fiume Miskatonic per Nord/Sud), la via viene sdoppiata in due stanze
(es. "Via Derby Est" e "Via Derby Ovest").

Analisi del catalogo (world/arkham_catalog.py) per decidere quali vie
sdoppiare:
    Vie a un solo lato (16, una stanza ciascuna):
        Armitage(O), Bad Water Road(S), Boundary(S), Crane(O), Curwen(O),
        Federal(N), Fishe(N), French Hill(S), Hyde(O), Jenkin(N), Lich(E),
        Main(O), Miskatonic Avenue(O), Parsonage(S), Powder Mill(S), River(O)
    Vie su due lati (8, due stanze ciascuna):
        Church(E/O), College(E/O), Derby(E/O), Garrison(N/S - e' lei
        stessa il riferimento Est/Ovest, quindi si sdoppia per Nord/Sud
        rispetto al fiume), Peabody Avenue(N/S - fusa con "Peabody
        Street" del catalogo, quasi certamente la stessa via chiamata
        in due modi sul sito originale), Pickman(E/O), Washington(E/O),
        West Street(N/S - come Garrison, corre nord-sud e attraversa
        il fiume)
    Totale dal catalogo: 16 + 8*2 = 32 stanze. A queste si aggiungono 4
    vie di puro collegamento visibili sulle mappe ma senza esercizi
    catalogati (Whatley, Goode Lane, Apple Lane, Water Street) -
    necessarie per tenere la griglia percorribile. Totale reale: 36.

Le tre vie che attraversano il fiume con un ponte (Garrison, Peabody
Avenue, West Street - le uniche cui il catalogo assegna indirizzi sia a
Nord che a Sud) fanno da "spina dorsale" verticale che tiene insieme
Arkham Nord e Arkham Sud, esattamente come si vede nelle mappe (tre
ponti sul Miskatonic).

NOTA DI METODO (come per il sottomarino): il catalogo ci da' via per
via QUALI edifici vi si affacciano, ma non la topologia esatta
isolato-per-isolato del sito originale. La disposizione qui sotto e'
una nostra ricostruzione ragionevole e internamente coerente, basata
sia sul catalogo sia sull'ispezione visiva delle mappe cittadine
(arkham.gif / arkham-new.jpg): le vie di Arkham Nord (Derby, Curwen,
Hyde, Armitage in sequenza da nord a sud, piu' Federal/Fishe/Jenkin
nel quadrante dell'universita'/parco) e quelle di Arkham Sud (River,
Main, Church, College, Pickman, Miskatonic Avenue, Washington in
sequenza), unite dalle tre vie-ponte.
"""

from evennia.utils import create, search

TAG_CATEGORY = "arkham_street"

# chiave_via -> (nome_stanza, descrizione)
STREETS = {
    # --- Le tre vie-ponte (spina dorsale Nord/Sud) ---
    "garrison_nord": (
        "Via Garrison Nord",
        "Il grande viale che taglia in due Arkham Nord, separando "
        "convenzionalmente l'Est dall'Ovest cittadino. Verso sud, oltre "
        "il ponte, si intravede la sponda opposta del Miskatonic.",
    ),
    "garrison_sud": (
        "Via Garrison Sud",
        "La prosecuzione meridionale di Garrison Street, dall'altra "
        "parte del fiume. Il traffico di carrozze e automobili è più "
        "fitto qui, vicino al cuore commerciale della città.",
    ),
    "peabody_nord": (
        "Viale Peabody Nord",
        "Un viale alberato che corre verso il fiume, con la sagoma "
        "squadrata dell'osservatorio visibile in lontananza verso "
        "ovest.",
    ),
    "peabody_sud": (
        "Viale Peabody Sud",
        "La sponda meridionale del viale Peabody, animata dal viavai "
        "verso il commissariato di polizia.",
    ),
    "west_nord": (
        "Via West Nord",
        "Una via residenziale nella parte occidentale di Arkham Nord, "
        "che scende dolcemente verso il fiume.",
    ),
    "west_sud": (
        "Via West Sud",
        "La prosecuzione meridionale di West Street, fiancheggiata da "
        "edifici pubblici e case signorili.",
    ),

    # --- Arkham Nord: vie orizzontali ad ovest di Garrison ---
    "derby_ovest": (
        "Via Derby Ovest",
        "Una via commerciale vivace, la più a nord di Arkham, "
        "fiancheggiata da negozi di ogni genere.",
    ),
    "derby_est": (
        "Via Derby Est",
        "Il tratto orientale di Derby Street, oltre Garrison, con un "
        "carattere più tranquillo e residenziale.",
    ),
    "curwen_ovest": (
        "Via Curwen Ovest",
        "Una via stretta che porta il nome di un'antica e controversa "
        "famiglia di Arkham. Le case qui sembrano più vecchie che "
        "altrove.",
    ),
    "hyde_ovest": (
        "Via Hyde Ovest",
        "Una via tranquilla, con negozi di mobili e forniture per la "
        "casa.",
    ),
    "armitage_ovest": (
        "Via Armitage Ovest",
        "Corre verso la stazione ferroviaria, il cui fischio dei treni "
        "si sente distintamente da qui.",
    ),

    # --- Arkham Nord: quadrante universitario/parco (est) ---
    "federal_nord": (
        "Via Federal Nord",
        "Una piccola via nel quadrante nord-orientale della città, "
        "vicino al porto sul fiume.",
    ),
    "fishe_nord": (
        "Via Fishe Nord",
        "Una via di artigiani e piccoli negozi, non lontana dal molo.",
    ),
    "jenkin_nord": (
        "Via Jenkin Nord",
        "Una via elegante, con il Grand Hotel di Arkham che domina "
        "l'incrocio.",
    ),
    "whatley_nord": (
        "Via Whatley",
        "Una via secondaria che prende il nome da un'altra famiglia "
        "nota da queste parti, per ragioni non sempre lusinghiere.",
    ),
    "goode_nord": (
        "Vicolo Goode",
        "Uno stretto vicolo vicino alla riva del fiume, all'estremità "
        "orientale della città.",
    ),
    "apple_nord": (
        "Vicolo Apple",
        "Un vicoletto ombreggiato da meli, all'estremità occidentale "
        "di Arkham Nord.",
    ),
    "water_nord": (
        "Via Water",
        "Corre lungo l'argine settentrionale del Miskatonic, "
        "affacciata sui tre ponti che portano alla città vecchia.",
    ),

    # --- Arkham Sud: vie orizzontali, dalla più vicina al fiume ---
    "river_ovest": (
        "Via River Ovest",
        "La prima via a sud del fiume, appena oltre i ponti.",
    ),
    "main_ovest": (
        "Via Main Ovest",
        "L'arteria commerciale principale della città vecchia.",
    ),
    "church_ovest": (
        "Via Church Ovest",
        "Il cuore della città vecchia: qui sorge l'ingresso della "
        "Miskatonic University, tra negozi e case di culto.",
    ),
    "church_est": (
        "Via Church Est",
        "Il tratto orientale di Church Street, più residenziale, "
        "verso il quartiere di French Hill.",
    ),
    "college_ovest": (
        "Via College Ovest",
        "Fiancheggiata da edifici pubblici e istituzioni cittadine, "
        "vicino al campus universitario.",
    ),
    "college_est": (
        "Via College Est",
        "Il tratto orientale di College Street, verso la prima banca "
        "di Arkham.",
    ),
    "pickman_ovest": (
        "Via Pickman Ovest",
        "Una via dal nome inquietante per chi conosce certe voci sulla "
        "città, fiancheggiata da alberghi modesti.",
    ),
    "pickman_est": (
        "Via Pickman Est",
        "Il tratto orientale di Pickman Street, verso il porto "
        "passeggeri.",
    ),
    "miskatonic_ovest": (
        "Viale Miskatonic Ovest",
        "Un ampio viale che porta il nome del fiume e dell'università, "
        "con l'osservatorio cittadino in fondo alla vista.",
    ),
    "washington_ovest": (
        "Via Washington Ovest",
        "La via più meridionale della città vecchia, tranquilla e "
        "residenziale.",
    ),
    "washington_est": (
        "Via Washington Est",
        "Il tratto orientale di Washington Street, con l'Istituto "
        "d'Arte di Arkham in vista.",
    ),

    # --- Arkham Sud: vie minori a un solo lato ---
    "bad_water_sud": (
        "Strada Bad Water",
        "Una strada periferica dal nome poco invitante, all'estremità "
        "occidentale della città vecchia.",
    ),
    "boundary_sud": (
        "Via Boundary",
        "Come dice il nome, segna uno dei confini della città vecchia.",
    ),
    "crane_ovest": (
        "Via Crane Ovest",
        "Una via tranquilla nella parte occidentale della città "
        "vecchia.",
    ),
    "lich_est": (
        "Via Lich",
        "Una via dal nome sinistro, non a caso adiacente al vecchio "
        "cimitero cittadino.",
    ),
    "powder_mill_sud": (
        "Via Powder Mill",
        "Prende il nome da un vecchio mulino da polvere da sparo, "
        "ormai scomparso.",
    ),
    "parsonage_sud": (
        "Via Parsonage",
        "Una via tranquilla nei pressi della basilica di San Genesio.",
    ),
    "french_hill_sud": (
        "Via French Hill",
        "Sale dolcemente verso la collina che le da' il nome, "
        "affacciata sui moli passeggeri.",
    ),
}

# (chiave_a, direzione_da_a_a_b, chiave_b)
CONNECTIONS = [
    # spina dorsale: i tre ponti sul Miskatonic
    ("garrison_nord", "sud", "garrison_sud"),
    ("peabody_nord", "sud", "peabody_sud"),
    ("west_nord", "sud", "west_sud"),

    # Arkham Nord, fascia ovest (Derby/Curwen/Hyde/Armitage), in sequenza
    # nord->sud, con West Street a ovest e Garrison a est
    ("derby_ovest", "sud", "curwen_ovest"),
    ("curwen_ovest", "sud", "hyde_ovest"),
    ("hyde_ovest", "sud", "armitage_ovest"),
    ("derby_ovest", "ovest", "west_nord"),
    ("curwen_ovest", "ovest", "apple_nord"),
    ("derby_ovest", "est", "garrison_nord"),
    ("armitage_ovest", "sud", "water_nord"),

    # Derby Est, oltre Garrison
    ("garrison_nord", "est", "derby_est"),

    # Arkham Nord, quadrante universitario/parco (est di Garrison,
    # verso Peabody/Whatley/Fishe/Federal)
    ("garrison_nord", "nord", "jenkin_nord"),
    ("jenkin_nord", "est", "peabody_nord"),
    ("peabody_nord", "nord", "whatley_nord"),
    ("whatley_nord", "est", "fishe_nord"),
    ("fishe_nord", "nord", "federal_nord"),
    ("federal_nord", "est", "goode_nord"),
    ("peabody_nord", "est", "water_nord"),

    # Arkham Sud, in sequenza nord->sud (dal fiume verso Washington),
    # lato ovest
    ("river_ovest", "nord", "west_sud"),
    ("river_ovest", "sud", "main_ovest"),
    ("main_ovest", "sud", "church_ovest"),
    ("church_ovest", "sud", "college_ovest"),
    ("college_ovest", "sud", "pickman_ovest"),
    ("pickman_ovest", "sud", "miskatonic_ovest"),
    ("miskatonic_ovest", "sud", "washington_ovest"),

    # lato est di Arkham Sud, oltre Garrison
    ("church_ovest", "est", "church_est"),
    ("college_ovest", "est", "college_est"),
    ("pickman_ovest", "est", "pickman_est"),
    ("washington_ovest", "est", "washington_est"),
    ("church_est", "sud", "college_est"),
    ("college_est", "sud", "pickman_est"),
    ("pickman_est", "sud", "washington_est"),
    ("college_est", "est", "garrison_sud"),
    ("river_ovest", "est", "peabody_sud"),

    # vie minori a un solo lato, agganciate al punto piu' sensato
    ("river_ovest", "ovest", "bad_water_sud"),
    ("main_ovest", "ovest", "boundary_sud"),
    ("church_ovest", "ovest", "crane_ovest"),
    ("church_est", "est", "lich_est"),
    ("garrison_sud", "sud", "powder_mill_sud"),
    ("pickman_est", "est", "parsonage_sud"),
    ("washington_est", "est", "french_hill_sud"),
]

OPPOSTA = {
    "nord": "sud", "sud": "nord",
    "est": "ovest", "ovest": "est",
}


def _get_or_create_street(chiave):
    """Trova la stanza-via <chiave>, o la crea."""
    tag_key = f"street_{chiave}"
    existing = search.search_tag(tag_key, category=TAG_CATEGORY)
    if existing:
        return existing[0]
    nome, descrizione = STREETS[chiave]
    room = create.create_object("typeclasses.rooms.Room", key=nome)
    room.db.desc = descrizione
    room.tags.add(tag_key, category=TAG_CATEGORY)
    room.tags.add(f"arkham_via_{chiave}", category="arkham_location")
    return room


def _get_or_create_exit(origine, destinazione, chiave, alias):
    """Crea un'uscita da origine a destinazione se non esiste gia'."""
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


def crea_vie_arkham():
    """
    Crea (se non esistono gia') tutte le 32 stanze-via di Arkham e i
    loro collegamenti. Idempotente. Non crea ancora gli edifici: quelli
    sono affrontati in world/rooms_arkham_edifici.py.

    Ritorna il dizionario {chiave_via: Room}.
    """
    vie = {chiave: _get_or_create_street(chiave) for chiave in STREETS}

    problemi = []
    for chiave_a, direzione, chiave_b in CONNECTIONS:
        room_a = vie[chiave_a]
        room_b = vie[chiave_b]
        direzione_opposta = OPPOSTA[direzione]
        _get_or_create_exit(room_a, room_b, direzione, direzione[0])
        _get_or_create_exit(room_b, room_a, direzione_opposta, direzione_opposta[0])

    for chiave, room in vie.items():
        direzioni = [e.key for e in room.exits]
        if len(set(direzioni)) != len(direzioni):
            problemi.append((chiave, direzioni))

    if problemi:
        raise RuntimeError(f"Conflitti di direzione rilevati: {problemi}")

    return vie
