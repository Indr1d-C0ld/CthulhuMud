"""
Liste di nomi per la generazione casuale del personaggio (Fase K,
diciottesima tornata): aggiunta dichiaratamente NUOVA rispetto alla
fonte - CthulhuMUD originale non ha mai avuto un generatore di nomi o
un elenco preimpostato (verificato: nessuna pagina del sito ne parla).
Qui i pool sono differenziati per origine/razza, coerentemente con
l'ambientazione anni '20 e il Mythos di Lovecraft, non per fedelta' a
un requisito della fonte.

Ogni professione newbie (world/professions_newbie.py) e' associata a
un pool tramite POOL_PER_PROFESSIONE. I pool "umani" (Arkham/Ulthar/
Dylath-Leen) condividono la stessa razza ma hanno un sapore diverso:
Arkham e' la Nuova Inghilterra reale degli anni '20 (nomi anglosassoni
puritani/coloniali, coerenti con i cataloghi di negozi/edifici di
Arkham gia' usati altrove - world/arkham_catalog.py), Ulthar e
Dylath-Leen sono citta' delle Dreamlands di Lovecraft (piu' arcaiche/
senza tempo, la seconda con un tocco da porto esotico - "citta' dei
galeoni neri").

Vincolo tecnico da rispettare: il nome del personaggio deve passare
world/chargen_menu.py:_check_nome (solo lettere, min. 3 caratteri,
NIENTE spazi/apostrofi/trattini/cifre - un personaggio ha sempre un
solo "nome di scena" giocabile in questo porting, coerente con tutte
le ricerche a singola parola gia' usate nel motore). Per questo ogni
pool di GENERA_NOME e' gia' pulito e alfabetico puro; i "cognomi"/
designazioni piu' elaborate (con trattini, apostrofi, numeri) esistono
SOLO come testo descrittivo (background/desc), mai come proposta di
nome giocabile - vedi genera_nome() vs genera_descrizione_estesa().
"""

import random

# --- Umani di Arkham (professioni: apprendista, cadetto,
# studentessa_conventuale, teppista, universitario) - Nuova Inghilterra
# anni '20, nomi anglosassoni/puritani coloniali. ---
ARKHAM_NOMI_M = [
    "Ezekiel", "Obadiah", "Silas", "Ambrose", "Increase", "Jedediah",
    "Nathaniel", "Ephraim", "Josiah", "Zebulon", "Cotton", "Enoch",
    "Barnabas", "Elihu", "Thaddeus", "Amos", "Jeremiah", "Asaph",
    "Wilbur", "Herbert", "Walter", "Arthur", "Henry", "Edwin",
    "Francis", "George", "Albert", "Frederick", "Theodore", "Simeon",
]
ARKHAM_NOMI_F = [
    "Abigail", "Prudence", "Mehitable", "Charity", "Patience", "Temperance",
    "Keziah", "Submit", "Thankful", "Content", "Faith", "Hope",
    "Lavinia", "Cordelia", "Sophronia", "Almira", "Rhoda", "Sylvia",
    "Edith", "Mabel", "Agatha", "Clarissa", "Beatrice", "Winifred",
    "Eleanor", "Margaret", "Constance", "Harriet", "Louisa", "Miriam",
]
ARKHAM_COGNOMI = [
    "Whateley", "Pickman", "Curwen", "Armitage", "Peabody", "Derby",
    "Waite", "Gilman", "Eliot", "Ward", "Corey", "Bishop",
    "Hutchins", "Danforth", "Akeley", "Wilmarth", "Sawyer", "Crane",
    "Fenner", "Goodenough", "Hardwick", "Osborne", "Talbot", "Winthrop",
    "Griswold", "Chandler", "Marsh", "Carter", "Blackwood", "Holt",
    "Prescott", "Stanhope", "Kingsley", "Vane", "Rutherford", "Cabot",
]

# --- Umani di Ulthar (professioni: iniziato, scudiero) - Dreamlands,
# tono piu' arcaico/senza tempo, echi da fiaba/leggenda. ---
ULTHAR_NOMI_M = [
    "Atal", "Barzai", "Kranon", "Thul", "Nasht", "Kaman",
    "Sansu", "Yath", "Pnom", "Ulthos", "Zenig", "Athok",
    "Orabon", "Selim", "Karkoth", "Vendis", "Halkor", "Imnar",
]
ULTHAR_NOMI_F = [
    "Yala", "Nithra", "Selanna", "Ombrys", "Vashti", "Ilaria",
    "Menet", "Suvara", "Thessaly", "Orlith", "Zanet", "Ysolde",
]
ULTHAR_EPITETI = [
    "delle Cento Torri", "del Vecchio Tempio", "il Sognatore", "la Sognatrice",
    "delle Terre Basse", "del Fiume Skai", "dei Sette Gatti", "il Silenzioso",
    "la Silenziosa", "delle Nebbie", "il Viandante", "la Viandante",
    "delle Colline Grige", "del Bosco Incantato", "il Custode", "la Custode",
]

# --- Umani di Dylath-Leen (professione: monello) - citta' portuale
# delle Dreamlands, tono da orfano di strada/porto esotico. ---
DYLATH_LEEN_NOMI_M = [
    "Sabbat", "Marek", "Corin", "Yusef", "Tobar", "Rashid",
    "Fennic", "Damaskus", "Orlan", "Petrik", "Alcott", "Bram",
]
DYLATH_LEEN_NOMI_F = [
    "Sable", "Marisol", "Yasmin", "Corvina", "Talia", "Esmet",
    "Ondine", "Kestrel", "Marika", "Farrah", "Lior", "Zohra",
]
DYLATH_LEEN_EPITETI = [
    "il Randagio", "la Randagia", "delle Banchine", "il Contrabbandiere",
    "la Contrabbandiera", "dai Piedi Leggeri", "delle Vele Nere", "lo Scugnizzo",
    "la Scugnizza", "del Molo Vecchio", "il Nottambulo", "la Nottambula",
]

# --- Profondi (Deep Ones, professioni: cacciatore_di_molluschi,
# tentacolo_di_dagon) - Y'ha-nthlei: un "nome di superficie" (usabile
# come nome giocabile, pensato per chi si e' mostrato/e' passato tra
# gli umani) piu' un nome piu' antico/sibilante usato solo come
# epiteto descrittivo tra i Profondi stessi. ---
PROFONDI_NOMI = [
    "Obed", "Zadok", "Barnabas", "Enoch", "Jonas", "Ahab",
    "Nereus", "Triton", "Marlin", "Coral", "Pearl", "Nerine",
    "Thalassa", "Undine", "Naida", "Marina", "Delphine", "Lorelei",
]
PROFONDI_EPITETI = [
    "dal sangue antico", "delle acque profonde", "di Yhanthlei", "del profondo",
    "che serve Dagon", "che serve Hydra", "dalle branchie nascoste", "del coro sommerso",
]

# --- Mi-Go (professioni: cacciatore_di_cervelli, scienziato_migo) -
# specie aliena/fungoide: nessun nome umano. Qui una designazione
# breve alfabetica (usabile come nome giocabile) piu' un codice
# esteso con numeri/trattini per la sola descrizione - scelta di
# design esplicita (la fonte non descrive convenzioni di
# denominazione Mi-Go). ---
MIGO_NOMI = [
    "Fthaggua", "Nyarlek", "Vhoorlan", "Kyarnak", "Zinshass", "Ghortull",
    "Nkaian", "Ossadag", "Yaddith", "Tondbaas", "Shugonar", "Ixanoth",
]
MIGO_CODICI = [
    "Unita' di Raccolta 7-Yuggoth", "Emissario del Corpo di Spedizione 3",
    "Osservatore Designato 12", "Agente Micologico 9", "Esploratore-Chirurgo 4",
    "Unita' di Trasporto Cerebrale 2",
]

# --- Shoggoth (professione: melma) - privi di un vero nome proprio:
# qui un nome-di-comodo pronunciabile (usabile come nome giocabile,
# spesso un frammento riconoscibile di un nome umano assorbito) piu'
# una descrizione della forma/imitazione attuale - scelta di design
# esplicita coerente con la loro natura mutaforma (info_races.txt:
# "they also imitate other beings that they absorb"). ---
SHOGGOTH_NOMI = [
    "Marsh", "Waite", "Gilman", "Eliot", "Orne", "Corey",
    "Akeley", "Sawyer", "Danforth", "Jenkins", "Prescott", "Holt",
]
SHOGGOTH_DESCRIZIONI = [
    "una forma instabile che ricorda vagamente un pescatore",
    "l'eco di qualcuno che una volta si chiamava cosi'",
    "una forma assunta di recente, non ancora perfezionata",
    "cio' che resta di una vittima, indossato come un vestito",
    "una delle tante forme che porta a turno",
    "un'imitazione approssimativa, con troppi occhi",
]

# --- Yithiani (professione: esploratore_yithiano) - la Grande Razza,
# viaggiatori del tempo/mente: qui un nome breve alfabetico (usabile
# come nome giocabile) piu' un titolo cosmico/archivistico per la
# descrizione - scelta di design esplicita (la fonte non descrive nomi
# Yithiani specifici). ---
YITHIAN_NOMI = [
    "Nlarro", "Ossvaar", "Klyneth", "Ssaroth", "Quorvain", "Menthar",
    "Ilyaros", "Corvath", "Theodrin", "Vareth", "Zyanor", "Ulmenoth",
]
YITHIAN_TITOLI = [
    "Primo Osservatore della Grande Razza", "Cronista del Ciclo Undicesimo",
    "Custode degli Archivi Conici", "Trasmigrato tra un'era e l'altra",
    "Studioso delle menti altrui", "Guardiano della memoria collettiva",
]

# --- Zoog (professioni: maghetto, zefiro) - piccoli e chiassosi
# abitanti delle Dreamlands: nomi brevi, giocosi, senza cognome. ---
ZOOG_NOMI = [
    "Ziq", "Fitti", "Brol", "Nix", "Tazzo", "Wibb",
    "Ruffo", "Snip", "Miko", "Vellu", "Prik", "Ozzu",
    "Baffo", "Tinni", "Sgrol", "Puffi", "Krik", "Lellu",
]

# profession_id -> pool key
POOL_PER_PROFESSIONE = {
    "apprendista": "arkham", "cadetto": "arkham",
    "studentessa_conventuale": "arkham", "teppista": "arkham",
    "universitario": "arkham",
    "iniziato": "ulthar", "scudiero": "ulthar",
    "monello": "dylath_leen",
    "cacciatore_di_molluschi": "profondi", "tentacolo_di_dagon": "profondi",
    "cacciatore_di_cervelli": "migo", "scienziato_migo": "migo",
    "melma": "shoggoth",
    "esploratore_yithiano": "yithian",
    "maghetto": "zoog", "zefiro": "zoog",
}

_NOMI_PER_POOL = {
    "arkham": (ARKHAM_NOMI_M, ARKHAM_NOMI_F),
    "ulthar": (ULTHAR_NOMI_M, ULTHAR_NOMI_F),
    "dylath_leen": (DYLATH_LEEN_NOMI_M, DYLATH_LEEN_NOMI_F),
    "profondi": (PROFONDI_NOMI, PROFONDI_NOMI),
    "migo": (MIGO_NOMI, MIGO_NOMI),
    "shoggoth": (SHOGGOTH_NOMI, SHOGGOTH_NOMI),
    "yithian": (YITHIAN_NOMI, YITHIAN_NOMI),
    "zoog": (ZOOG_NOMI, ZOOG_NOMI),
}

_ESTESO_PER_POOL = {
    "arkham": ARKHAM_COGNOMI,
    "ulthar": ULTHAR_EPITETI,
    "dylath_leen": DYLATH_LEEN_EPITETI,
    "profondi": PROFONDI_EPITETI,
    "migo": MIGO_CODICI,
    "shoggoth": SHOGGOTH_DESCRIZIONI,
    "yithian": YITHIAN_TITOLI,
}


def genera_nome(prof_id, genere="m"):
    """Genera un nome giocabile (solo lettere) coerente con l'origine
    della professione data - passa sempre world/chargen_menu.py:
    _check_nome."""
    pool = POOL_PER_PROFESSIONE.get(prof_id, "arkham")
    maschili, femminili = _NOMI_PER_POOL.get(pool, (ARKHAM_NOMI_M, ARKHAM_NOMI_F))
    return random.choice(femminili if genere == "f" else maschili)


def genera_descrizione_estesa(prof_id, nome):
    """Ritorna una riga descrittiva che combina il nome giocabile con
    un cognome/epiteto/titolo piu' elaborato (puo' contenere spazi,
    apostrofi, trattini, numeri) - SOLO per testo di sfondo/background,
    mai come proposta di nome giocabile. Ritorna None per i pool senza
    un simile elemento descrittivo."""
    pool = POOL_PER_PROFESSIONE.get(prof_id, "arkham")
    if pool in ("arkham",):
        return f"{nome} {random.choice(_ESTESO_PER_POOL[pool])}"
    if pool in ("ulthar", "dylath_leen", "profondi"):
        return f"{nome}, {random.choice(_ESTESO_PER_POOL[pool])}"
    if pool in ("migo", "yithian"):
        return f"{nome} ({random.choice(_ESTESO_PER_POOL[pool])})"
    if pool == "shoggoth":
        return f"{nome} - {random.choice(_ESTESO_PER_POOL[pool])}"
    return None
