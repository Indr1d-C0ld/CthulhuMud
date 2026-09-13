"""
Zoog Village, il villaggio degli Zoog nel Bosco Incantato delle
Dreamlands (Fase E, seconda tornata), ricostruito dalla mappa del sito
ufficiale (new_zoogville.gif, attribuita a "Aemilia" nel Dossier
Miskatonic). Punto di partenza delle professioni newbie Mageling e
Zephyr (razza Zoog).

La mappa originale e' una fitta griglia con moltissime celle generiche
"ZV" (radure senza nome) e una ventina di location nominate. Qui
manteniamo fedelmente tutte le location nominate leggibili sulla mappa,
collegate in una struttura piu' snella (non l'intera griglia cella per
cella) - lo stesso approccio di semplificazione ragionata gia' usato
per il sommergibile e per le vie di Arkham.

Integrazione con l'hub newbie gia' esistente (world/rooms_newbie.py,
hub "zoog_village"): "Open Glade" e "Tree Stump" sulla mappa
corrispondono esattamente ai nomi gia' coniati per RESPAWN ("La Radura
Aperta") e MORGUE ("Sulla Cima del Ceppo") - non vengono duplicate,
solo agganciate alla nuova struttura. "Sotto le Radici" (RECALL) non
corrisponde a una cella specifica della mappa, ed e' stata inserita
nel punto piu' sensato: accanto alle altre tane private (Slorril Home,
Jhilorin's Burrow).
"""

from evennia.utils import create, search

TAG_CATEGORY = "zoogvillage_room"

# chiave -> (nome, descrizione)
ROOMS = {
    "north_gate": (
        "Il Cancello Settentrionale",
        "Due tronchi ricurvi, intrecciati fino a formare un arco "
        "naturale, segnano il confine del villaggio degli Zoog. Radici "
        "sottili pendono dall'arco come tende vive.",
    ),
    "in_the_pond": (
        "Nello Stagno",
        "L'acqua scura di uno stagno del bosco arriva fin quasi alle "
        "ginocchia. Piccole bolle salgono di continuo dal fondo "
        "melmoso, per ragioni che nessuno Zoog si e' mai preso la "
        "briga di indagare.",
    ),
    "cozy_pond": (
        "Lo Stagno Accogliente",
        "Uno stagno più piccolo e tranquillo, circondato da felci "
        "morbide. Gli Zoog vi si radunano nelle sere calde per "
        "raccontarsi storie sempre più incredibili.",
    ),
    "tree_of_souls": (
        "L'Albero delle Anime",
        "Un albero immenso, dal tronco contorto in forme che ricordano "
        "vagamente volti. Gli Zoog vi lasciano piccole offerte, "
        "sussurrando nomi di parenti scomparsi nel sogno.",
    ),
    "high_temple": (
        "L'Alto Tempio",
        "Un tempio costruito interamente con rami intrecciati e "
        "muschio, che si innalza più in alto di qualunque altra "
        "struttura del villaggio. Il suo interno è perennemente in "
        "penombra.",
    ),
    "chamber_elders": (
        "La Camera degli Anziani",
        "Una cavità naturale nel terreno, foderata di radici, dove i "
        "pochi Zoog davvero anziani si riuniscono per discutere - a "
        "modo loro, tra risatine e battibecchi - le questioni piu' "
        "importanti del villaggio.",
    ),
    "slorril_home": (
        "La Casa di Slorril",
        "Una tana ben tenuta, con pareti di terra battuta decorate da "
        "sassolini colorati. Slorril e' fiero della sua collezione, "
        "anche se nessun altro ne capisce il criterio.",
    ),
    "jhilorin_burrow": (
        "La Tana di Jhilorin",
        "Una tana più modesta delle altre, con un ingresso cosi' "
        "basso da costringere chiunque non sia uno Zoog a entrare "
        "carponi.",
    ),
    "thussis_shop": (
        "La Bottega di Thussis",
        "Un piccolo emporio ricavato dentro un tronco cavo, dove "
        "Thussis vende di tutto un po' - soprattutto cose che nessuno "
        "sapeva di aver bisogno finche' non le ha viste.",
    ),
    "klorl_shop": (
        "La Bottega di Klorl",
        "Klorl commercia funghi rari e radici luminescenti, disposti "
        "in ceste intrecciate. Alcuni funghi, se fissati troppo a "
        "lungo, sembrano fissare a loro volta.",
    ),
    "flaerr_shop": (
        "La Bottega di Flaerr",
        "Un piccolo chiosco all'estremità del villaggio, dove Flaerr "
        "ripara utensili e vende cianfrusaglie recuperate da sogni "
        "altrui naufragati nel bosco.",
    ),
    "bakery_silaer": (
        "Il Forno di Silaer",
        "L'odore di pane caldo e miele di fiori onirici riempie "
        "l'aria. Silaer sforna dolci che, dicono gli Zoog piu' "
        "anziani, sanno sempre un po' del sogno di chi li mangia.",
    ),
    "blacksmith_chorl": (
        "La Fucina di Chorl",
        "Il calore di una piccola forgia scalda questa tana. Chorl "
        "batte il metallo con una forza sorprendente per la sua "
        "piccola statura, forgiando lame sottili come aghi.",
    ),
    "gem_cavern": (
        "La Caverna delle Gemme",
        "Una piccola grotta le cui pareti scintillano di cristalli "
        "onirici. Gli Zoog li raccolgono per gioco più che per "
        "valore, anche se qualche mercante di passaggio direbbe il "
        "contrario.",
    ),
    "in_the_fungus": (
        "Nel Fungheto",
        "Funghi giganteschi, alcuni piu' alti di uno Zoog adulto, "
        "formano un bosco nel bosco. Hok, uno Zoog dall'aria "
        "distratta, vive qui da solo, e pare parlare ai funghi come "
        "se rispondessero.",
    ),
    "deposito": (
        "Il Deposito degli Zoog",
        "Una cavità sotterranea dove il villaggio custodisce provviste "
        "e oggetti di valore comune. Merith ne tiene le chiavi, e il "
        "conto di ogni singolo chicco messo da parte.",
    ),
    "durnith_log": (
        "Il Tronco di Durnith",
        "Un enorme tronco caduto, cavo all'interno, che Durnith ha "
        "trasformato nella propria abitazione. Muschio e funghi "
        "luminosi ne decorano l'ingresso.",
    ),
    "goryth": (
        "Presso Goryth",
        "Una piccola radura dove vive Goryth, uno Zoog piu' silenzioso "
        "della media, che passa le giornate a osservare il bosco senza "
        "mai spiegare cosa stia cercando.",
    ),
    "empty_house": (
        "La Casa Vuota",
        "Una tana abbandonata da tempo, il cui ingresso si restringe "
        "in un cunicolo - uno zoogtunnel - che si perde nel buio "
        "sottoterra. Nessuno Zoog ammette volentieri di sapere dove "
        "porti.",
    ),
}

# (chiave_a, direzione_da_a_a_b, chiave_b) - collega solo le nuove
# stanze tra loro; l'aggancio agli hub esistenti avviene in crea_zoogvillage()
CONNECTIONS = [
    ("in_the_pond", "est", "cozy_pond"),
    ("cozy_pond", "sud", "tree_of_souls"),
    ("tree_of_souls", "sud", "high_temple"),
    ("high_temple", "sud", "chamber_elders"),
    ("chamber_elders", "sud", "slorril_home"),
    ("slorril_home", "sud", "jhilorin_burrow"),
    ("chamber_elders", "est", "thussis_shop"),
    ("thussis_shop", "est", "klorl_shop"),
    ("klorl_shop", "nord", "flaerr_shop"),
    ("klorl_shop", "sud", "bakery_silaer"),
    ("bakery_silaer", "sud", "blacksmith_chorl"),
    ("blacksmith_chorl", "est", "gem_cavern"),
    ("in_the_fungus", "sud", "deposito"),
    ("deposito", "sud", "durnith_log"),
    ("durnith_log", "ovest", "goryth"),
    ("goryth", "sud", "empty_house"),
]

OPPOSTA = {"nord": "sud", "sud": "nord", "est": "ovest", "ovest": "est"}

RECALL_TAG = "zoog_village_recall"
RESPAWN_TAG = "zoog_village_respawn"
MORGUE_TAG = "zoog_village_morgue"


def _get_or_create_room(chiave):
    tag_key = f"zv_{chiave}"
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


def _get_hub_room(tag_key):
    rooms = search.search_tag(tag_key, category="start_room")
    return rooms[0] if rooms else None


def crea_zoogvillage():
    """
    Crea (se non esistono gia') tutte le location nominate di Zoog
    Village e le aggancia agli hub newbie gia' esistenti (Open Glade =
    respawn, Tree Stump = morgue, e "Sotto le Radici" = recall, messo
    accanto alle altre tane). Idempotente.

    Ritorna il dizionario {chiave: Room} delle nuove stanze (non
    include gli hub esistenti, reperibili con _get_hub_room).
    """
    stanze = {chiave: _get_or_create_room(chiave) for chiave in ROOMS}

    for chiave_a, direzione, chiave_b in CONNECTIONS:
        room_a = stanze[chiave_a]
        room_b = stanze[chiave_b]
        direzione_opposta = OPPOSTA[direzione]
        _get_or_create_exit(room_a, room_b, direzione, direzione[0])
        _get_or_create_exit(room_b, room_a, direzione_opposta, direzione_opposta[0])

    open_glade = _get_hub_room(RESPAWN_TAG)
    tree_stump = _get_hub_room(MORGUE_TAG)
    sotto_radici = _get_hub_room(RECALL_TAG)

    if open_glade:
        if tree_stump:
            _get_or_create_exit(open_glade, tree_stump, "sud", "s")
            _get_or_create_exit(tree_stump, open_glade, "nord", "n")
        _get_or_create_exit(open_glade, stanze["in_the_pond"], "est", "e")
        _get_or_create_exit(stanze["in_the_pond"], open_glade, "ovest", "o")
        _get_or_create_exit(open_glade, stanze["north_gate"], "nord", "n")
        _get_or_create_exit(stanze["north_gate"], open_glade, "sud", "s")

    if tree_stump:
        _get_or_create_exit(tree_stump, stanze["in_the_fungus"], "ovest", "o")
        _get_or_create_exit(stanze["in_the_fungus"], tree_stump, "est", "e")

    if sotto_radici:
        _get_or_create_exit(stanze["chamber_elders"], sotto_radici, "ovest", "o")
        _get_or_create_exit(sotto_radici, stanze["chamber_elders"], "est", "e")

    problemi = []
    tutte = list(stanze.values())
    for extra in (open_glade, tree_stump, sotto_radici):
        if extra:
            tutte.append(extra)
    for room in tutte:
        chiavi = [e.key for e in room.exits]
        if len(set(chiavi)) != len(chiavi):
            problemi.append((room.key, chiavi))
    if problemi:
        raise RuntimeError(f"Conflitti di direzione a Zoog Village: {problemi}")

    return stanze
