"""
Popolamento NPC ostili (Fase H, prima tornata): vedi world/mostri.py
per il bestiario e la nota sul perche' e' un'invenzione dichiarata
(nessun bestiario esiste nella fonte originale).

Zone popolate: Arkham (vie), Cairo, il sommergibile. DELIBERATAMENTE
LASCIATE PULITE: l'interno di Ulthar (tempio) e Zoog Village, e i
tre hub RECALL/RESPAWN/MORGUE di ogni professione newbie - confermato
dalla fonte (guides_heroes.txt): "Newbies are sacred... every God in
existence protects them... don't call lightning in MU, Temple of
Ulthar, Zoogville or any other heavy newbie area." I mostri nella
regione Dreamlands (fuori da Ulthar/Zoog) e nel sommergibile sono
invece pienamente legittimi: zone di esplorazione, non hub di partenza.

Fase H, terza tornata (saturazione): popolate la quasi totalita' delle
vie di Arkham, delle stanze di Cairo e del sommergibile, con criteri di
esclusione dichiarati voce per voce qui sotto - in sintesi: le vie/
piazze descritte esplicitamente come arterie di traffico centrali
(non semplici vie di quartiere), gli edifici/stanze con un negoziante
o un luogo di culto attivo (coerenza con il "mondo vivo" di Fase G/
D-E: un mostro non convive con un venditore che serve i clienti), e i
punti di arrivo/respawn (equivalenti agli hub newbie). Gli edifici
civici/commerciali di Arkham (72 su 72, tranne il cimitero) restano
fuori scope per lo stesso motivo.

Non idempotente per design (vedi world/mostri.py, crea_mostro): pensata
per un singolo popolamento iniziale. TABELLA_RESET (sotto) e' la stessa
identica lista di voci, con l'aggiunta della zona: e' la fonte unica di
verita' usata anche dal sistema di repop (world/repop.py, Fase H,
seconda tornata) cosi' che popolamento iniziale e reset periodico non
possano mai divergere.
"""

from evennia.utils import search

from world.mostri import crea_mostro

# (chiave_bestiario, tag_stanza, categoria_tag, zona)
ARKHAM = [
    ("ghoul", "street_lich_est", "arkham_street", "arkham"),
    ("cultista", "street_church_ovest", "arkham_street", "arkham"),
    ("sciacallo_mutato", "street_west_sud", "arkham_street", "arkham"),
    ("sciacallo_mutato", "street_river_ovest", "arkham_street", "arkham"),
    ("ibrido_profondo", "street_water_nord", "arkham_street", "arkham"),
    # Seconda tornata (Fase H, terza tornata - estensione zone):
    ("ghoul", "street_pickman_est", "arkham_street", "arkham"),
    ("ghoul", "building_olde_towne_cemetery", "arkham_building", "arkham"),
    ("cultista", "street_bad_water_sud", "arkham_street", "arkham"),
    ("sciacallo_mutato", "street_boundary_sud", "arkham_street", "arkham"),
    ("ibrido_profondo", "street_powder_mill_sud", "arkham_street", "arkham"),
    # Terza tornata (saturazione delle vie rimanenti): DELIBERATAMENTE
    # ESCLUSE le 4 vie-ponte (garrison_nord/sud, peabody_nord/sud,
    # "spina dorsale" della citta' secondo lo stesso file
    # rooms_arkham.py) e Via Main Ovest ("l'arteria commerciale
    # PRINCIPALE della citta' vecchia") - le uniche vie descritte
    # esplicitamente come arterie di traffico centrali, non semplici
    # vie di quartiere.
    ("cultista", "street_west_nord", "arkham_street", "arkham"),
    ("sciacallo_mutato", "street_derby_ovest", "arkham_street", "arkham"),
    ("cultista", "street_derby_est", "arkham_street", "arkham"),
    ("ghoul", "street_curwen_ovest", "arkham_street", "arkham"),
    ("sciacallo_mutato", "street_hyde_ovest", "arkham_street", "arkham"),
    ("cultista", "street_armitage_ovest", "arkham_street", "arkham"),
    ("ibrido_profondo", "street_federal_nord", "arkham_street", "arkham"),
    ("marinaio_annegato", "street_fishe_nord", "arkham_street", "arkham"),
    ("cultista", "street_jenkin_nord", "arkham_street", "arkham"),
    ("sciacallo_mutato", "street_whatley_nord", "arkham_street", "arkham"),
    ("ibrido_profondo", "street_goode_nord", "arkham_street", "arkham"),
    ("cultista", "street_apple_nord", "arkham_street", "arkham"),
    ("cultista", "street_church_est", "arkham_street", "arkham"),
    ("ghoul", "street_college_ovest", "arkham_street", "arkham"),
    ("cultista", "street_college_est", "arkham_street", "arkham"),
    ("ghoul", "street_pickman_ovest", "arkham_street", "arkham"),
    ("cane_di_tindalos", "street_miskatonic_ovest", "arkham_street", "arkham"),
    ("cultista", "street_washington_ovest", "arkham_street", "arkham"),
    ("ghoul", "street_washington_est", "arkham_street", "arkham"),
    ("sciacallo_mutato", "street_crane_ovest", "arkham_street", "arkham"),
    ("cultista", "street_parsonage_sud", "arkham_street", "arkham"),
    ("marinaio_annegato", "street_french_hill_sud", "arkham_street", "arkham"),
]

CAIRO = [
    ("mummia_custode", "cairo_pyramids", "cairo_room", "cairo"),
    ("cultista", "cairo_sphinx", "cairo_room", "cairo"),
    ("sciacallo_mutato", "cairo_city_gates", "cairo_room", "cairo"),
    ("sciacallo_mutato", "cairo_causeway", "cairo_room", "cairo"),
    # Seconda tornata:
    ("ibrido_profondo", "cairo_docks", "cairo_room", "cairo"),
    ("cultista", "cairo_slums", "cairo_room", "cairo"),
    # Terza tornata (saturazione delle stanze rimanenti): DELIBERATAMENTE
    # ESCLUSI il grande mosque (luogo di culto attivo, come le chiese di
    # Arkham) e le stanze chiaramente commerciali gia' o non ancora
    # popolate con un negoziante (abduls_armoury, falcon_armory,
    # farmers_stall, winemakers_shop gia' negozi; anubis_hotel,
    # cloth_merchant, bakery hanno nomi da negozio anche se non ancora
    # implementati - riservate a un eventuale futuro popolamento
    # commerciale invece che a un mostro).
    ("sciacallo_mutato", "cairo_bazaar", "cairo_room", "cairo"),
    ("cultista", "cairo_administrative_area", "cairo_room", "cairo"),
    ("mummia_custode", "cairo_british_citadel", "cairo_room", "cairo"),
    ("cultista", "cairo_residential_ne", "cairo_room", "cairo"),
    ("ibrido_profondo", "cairo_residential_se", "cairo_room", "cairo"),
]

SOMMERGIBILE = [
    ("marinaio_annegato", "sub_12", "submarine_room", "sommergibile"),
    ("marinaio_annegato", "sub_16", "submarine_room", "sommergibile"),
    ("cane_di_tindalos", "sub_21", "submarine_room", "sommergibile"),
    ("cane_di_tindalos", "sub_22", "submarine_room", "sommergibile"),
    ("shoggoth_minore", "sub_9", "submarine_room", "sommergibile"),
    # Seconda tornata:
    ("cultista", "sub_3", "submarine_room", "sommergibile"),
    ("ibrido_profondo", "sub_19", "submarine_room", "sommergibile"),
    ("sciacallo_mutato", "sub_14", "submarine_room", "sommergibile"),
    ("marinaio_annegato", "sub_13", "submarine_room", "sommergibile"),
    ("marinaio_annegato", "sub_17", "submarine_room", "sommergibile"),
    # Terza tornata (saturazione delle stanze rimanenti): DELIBERATAMENTE
    # ESCLUSE la stanza 1 (punto d'arrivo di chiunque si avventuri nel
    # relitto: "e' da qui che chiunque... finisce per ritrovarsi") e la
    # 23/Infermeria (esplicitamente un punto di respawn: "chi muore nel
    # relitto si risveglia sempre qui") - equivalenti a hub di
    # arrivo/respawn, da tenere sicuri come gli hub newbie.
    ("cultista", "sub_2", "submarine_room", "sommergibile"),
    ("cane_di_tindalos", "sub_4", "submarine_room", "sommergibile"),
    ("marinaio_annegato", "sub_5", "submarine_room", "sommergibile"),
    ("ibrido_profondo", "sub_6", "submarine_room", "sommergibile"),
    ("marinaio_annegato", "sub_7", "submarine_room", "sommergibile"),
    ("cane_di_tindalos", "sub_8", "submarine_room", "sommergibile"),
    ("sciacallo_mutato", "sub_10", "submarine_room", "sommergibile"),
    ("ibrido_profondo", "sub_11", "submarine_room", "sommergibile"),
    ("ibrido_profondo", "sub_15", "submarine_room", "sommergibile"),
    ("marinaio_annegato", "sub_18", "submarine_room", "sommergibile"),
    ("cane_di_tindalos", "sub_20", "submarine_room", "sommergibile"),
]

DREAMLANDS = [
    ("byakhee", "dlo_crocevia", "dreamlands_overworld", "dreamlands"),
    ("cacciatore_notturno", "dlo_verso_ulthar", "dreamlands_overworld", "dreamlands"),
    ("bestia_lunare", "dlo_presso_nir", "dreamlands_overworld", "dreamlands"),
    ("gug", "dlo_verso_bosco", "dreamlands_overworld", "dreamlands"),
    ("cultista", "dlo_presso_hatheg", "dreamlands_overworld", "dreamlands"),
    ("sciacallo_mutato", "dlo_lungofiume_skai", "dreamlands_overworld", "dreamlands"),
]

TABELLA_RESET = ARKHAM + CAIRO + SOMMERGIBILE + DREAMLANDS

# Categorie di tag valide per zona (usata da world/mostri_movimento.py
# per vincolare il vagabondare dei mostri alla propria area, equivalente
# al flag STAY-AREA della fonte - immhelp_flags.txt).
ZONA_CATEGORIE = {
    "arkham": ("arkham_street", "arkham_building"),
    "cairo": ("cairo_room",),
    "sommergibile": ("submarine_room",),
    "dreamlands": ("dreamlands_overworld",),
}


def _popola_lista(lista):
    creati = []
    non_trovati = []
    for chiave_bestiario, tag_stanza, categoria, zona in lista:
        stanze = search.search_tag(tag_stanza, category=categoria)
        if not stanze:
            non_trovati.append(tag_stanza)
            continue
        creati.append(crea_mostro(chiave_bestiario, stanze[0], zona=zona))
    return creati, non_trovati


def popola_arkham():
    return _popola_lista(ARKHAM)


def popola_cairo():
    return _popola_lista(CAIRO)


def popola_sommergibile():
    return _popola_lista(SOMMERGIBILE)


def popola_dreamlands():
    return _popola_lista(DREAMLANDS)


def popola_tutto():
    """Popola tutte e 4 le zone in un colpo solo.

    ATTENZIONE - NON E' IDEMPOTENTE. Genera l'intera TABELLA_RESET a
    ogni chiamata senza controllare cosa c'e' gia': rilanciarla su un
    mondo popolato aggiunge altri ~70 mostri, e cosi' a ogni giro.
    E' il primitivo di popolamento "da zero", non un reset.

    Per ripopolare un mondo gia' esistente usa invece
    world/repop.py:popola_tutte_le_zone_mancanti(), che crea solo le
    voci effettivamente mancanti."""
    risultati = {}
    for nome, funzione in (
        ("arkham", popola_arkham),
        ("cairo", popola_cairo),
        ("sommergibile", popola_sommergibile),
        ("dreamlands", popola_dreamlands),
    ):
        creati, non_trovati = funzione()
        risultati[nome] = (creati, non_trovati)
    return risultati
