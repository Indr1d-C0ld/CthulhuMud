"""
Gli edifici di Arkham (Fase D, seconda tornata), agganciati alle vie
costruite in world/rooms_arkham.py. Si procede per categorie, seguendo
il catalogo di world/arkham_catalog.py (73 edifici totali).

Tutte le 9 categorie sono coperte: municipale(7), abbigliamento(6),
cibo(6), negozio(23), culto(7), banca(2), albergo(3), aperto(3),
altro(16) = 73/73.

Schema di collegamento: dalla stanza-via, un'uscita con il nome
(abbreviato) dell'edificio porta dentro; dall'edificio, un'uscita
"fuori" riporta sulla via. Ogni edificio e' una singola stanza (non
un interno multi-stanza) - coerente con l'idea di "una stanza per via
piu' una stanza per edificio", lo stesso principio di semplificazione
concordato per le vie.

Le chiavi delle uscite dalla via verso ciascun edificio sono scelte
apposta brevi e distinte per evitare conflitti quando piu' edifici si
affacciano sulla stessa via (es. Via Derby Ovest ne ospita 4).
"""

from evennia.utils import create, search

from world.rooms_arkham import _get_or_create_street
from world.arkham_catalog import ARKHAM_BUILDINGS

TAG_CATEGORY = "arkham_building"

# nome_italiano (world/arkham_catalog.py) -> orari originali (Fase K,
# quindicesima tornata - vedi world/tempo.py). Le chiavi di BUILDINGS
# qui sotto usano quasi sempre lo stesso nome_italiano del catalogo,
# quindi il collegamento e' perlopiu' un semplice lookup per nome.
# 4 edifici furono pero' rinominati quando le stanze sono state
# davvero costruite (Fase D, seconda tornata), senza piu' badare al
# nome esatto del catalogo (es. "Bottega di Hans Yodin..." invece di
# "Hans Yodin, Mastro Calzolaio") - verificato confrontando le due
# liste: qui sotto la corrispondenza esplicita, altrimenti questi 4
# negozi risulterebbero sempre aperti per un semplice mancato match.
# Gli altri 3 nomi non allineati (Mortis & Carver, L'Osservatore,
# Universita' Miskatonic) non necessitano override: nella fonte non
# hanno comunque un orario (None), quindi il mancato match produce
# lo stesso risultato corretto per puro caso.
_ORARI_PER_NOME = {nome_it: orari for (_, nome_it, _, _, _, orari) in ARKHAM_BUILDINGS}
_ORARI_PER_NOME.update({
    "Bottega di Hans Yodin, Mastro Calzolaio": _ORARI_PER_NOME["Hans Yodin, Mastro Calzolaio"],
    "Cappelleria di V. Carrington": _ORARI_PER_NOME["V. Carrington, Cappellaia Esperta"],
    "Bottega di Charles Browning, Mastro Armaiolo": _ORARI_PER_NOME["Charles Browning - Mastro Armaiolo"],
    "Bottega di Harold Wingham, Mastro Carpentiere Navale": _ORARI_PER_NOME["Harold Wingham - Mastro Carpentiere Navale"],
})

# chiave_edificio -> (nome, via_di_riferimento, chiave_uscita_dalla_via,
#                      alias_uscita, descrizione)
BUILDINGS = {
    "city_courthouse": (
        "Tribunale Municipale",
        "college_ovest",
        "tribunale",
        "tribunale",
        "Colonne di granito grigio incorniciano l'ingresso. All'interno, "
        "corridoi di marmo freddo conducono alle aule dove si "
        "decidono i destini di Arkham - e talvolta, si dice, qualcosa "
        "di piu' oscuro delle solite dispute civili.",
    ),
    "city_hall": (
        "Municipio",
        "west_sud",
        "municipio",
        "municipio",
        "L'edificio piu' imponente della città vecchia, con una cupola "
        "di rame ormai verdastra. Impiegati indaffarati vanno e "
        "vengono tra sportelli di legno scuro.",
    ),
    "fire_department": (
        "Caserma dei Vigili del Fuoco",
        "garrison_sud",
        "caserma",
        "caserma",
        "Le autopompe rosse luccicano, perfettamente lucidate, in "
        "attesa del prossimo allarme. Un palo di ottone scende dal "
        "piano superiore dei dormitori.",
    ),
    "medical_center": (
        "Centro Medico Regionale Miskatonic",
        "west_sud",
        "centro medico",
        "ospedale",
        "L'odore di disinfettante permea ogni corridoio. Infermiere in "
        "uniforme bianca si muovono rapide tra le corsie, mentre "
        "qualche paziente lancia sguardi vitrei al soffitto.",
    ),
    "miskatonic_university": (
        "Ingresso della Miskatonic University",
        "church_ovest",
        "universita",
        "universita",
        "Un imponente cancello in ferro battuto segna l'ingresso "
        "principale del campus. Oltre le sue sbarre si intravedono "
        "edifici in stile georgiano e studenti che si affrettano tra "
        "una lezione e l'altra, ignari - per ora - di certi scaffali "
        "della biblioteca universitaria.",
    ),
    "police_station": (
        "Commissariato di Polizia",
        "peabody_sud",
        "commissariato",
        "commissariato",
        "Un edificio severo in mattoni rossi. Il tenente di turno alza "
        "appena lo sguardo dalla scrivania quando qualcuno entra, "
        "come se avesse gia' visto tutto cio' che Arkham puo' offrire "
        "- e sapesse di sbagliarsi.",
    ),
    "post_office": (
        "Ufficio Postale",
        "church_ovest",
        "ufficio postale",
        "posta",
        "File ordinate di caselle postali di ottone rivestono una "
        "parete intera. Il ticchettio dei timbri scandisce il tempo "
        "quasi quanto l'orologio a pendolo appeso sopra gli sportelli.",
    ),

    # --- Abbigliamento (6/6) ---
    "bridal_boutique": (
        "Boutique da Sposa di Arkham",
        "river_ovest",
        "boutique",
        "boutique",
        "Abiti color avorio pendono da manichini senza volto, disposti "
        "in vetrina come in una processione silenziosa. La sarta "
        "sorride sempre un po' troppo a lungo alle spose.",
    ),
    "giovanni_clothing": (
        "Abbigliamento da Uomo di Giovanni",
        "west_nord",
        "sartoria giovanni",
        "giovanni",
        "Completi di lana pettinata e cappelli a bombetta riempiono gli "
        "scaffali. Giovanni stesso misura ogni cliente con un metro da "
        "sarto e un'attenzione quasi eccessiva.",
    ),
    "hans_yodin": (
        "Bottega di Hans Yodin, Mastro Calzolaio",
        "fishe_nord",
        "calzoleria",
        "calzoleria",
        "L'odore di cuoio e cera impregna ogni angolo. Hans lavora "
        "curvo sul suo banco, e giura di riconoscere il carattere di "
        "un uomo dalla suola consumata delle sue scarpe.",
    ),
    "miss_ann": (
        "Moda da Donna di Miss Ann",
        "church_ovest",
        "sartoria",
        "sartoria",
        "Rotoli di seta e merletto sono impilati fino al soffitto. Le "
        "commesse sussurrano tra loro ogni volta che una cliente "
        "distoglie lo sguardo.",
    ),
    "carrington_milliner": (
        "Cappelleria di V. Carrington",
        "main_ovest",
        "cappelleria",
        "cappelleria",
        "Cappelli di ogni foggia occupano teste di legno allineate su "
        "mensole polverose, come un pubblico silenzioso e un po' "
        "inquietante.",
    ),
    "watkins_formal": (
        "Abiti Eleganti Watkins",
        "river_ovest",
        "abiti eleganti",
        "watkins",
        "Smoking neri e papillon bianchi sono esposti con cura "
        "maniacale. Qui si vestono gli invitati ai ricevimenti piu' "
        "in vista di Arkham - e talvolta ai loro funerali.",
    ),

    # --- Cibo e locali (6/6) ---
    "fish_market": (
        "Mercato del Pesce di Arkham",
        "derby_ovest",
        "mercato del pesce",
        "mercato",
        "Banchi di ghiaccio esibiscono il pescato del giorno. Alcuni "
        "esemplari, pescati piu' a largo del solito, hanno squame di "
        "una lucentezza che i pescivendoli preferiscono non commentare.",
    ),
    "barlows_butcher": (
        "Macelleria Barlow",
        "church_ovest",
        "macelleria",
        "macelleria",
        "Carcasse appese ad ganci di ferro ondeggiano appena a ogni "
        "apertura di porta. Il macellaio affila i coltelli con un "
        "ritmo che mette involontariamente a disagio.",
    ),
    "black_dahlia": (
        "Jazz Club Black Dahlia",
        "jenkin_nord",
        "jazz club",
        "dalia",
        "Fumo di sigaretta e note di tromba riempiono la sala a "
        "qualunque ora. Si dice che qui si possa comprare molto piu' "
        "del solo contrabbando, per chi sa chi chiedere.",
    ),
    "blue_ballroom": (
        "La Sala da Ballo Blu",
        "washington_ovest",
        "sala da ballo",
        "ballroom",
        "Un lampadario di cristallo proietta riflessi azzurrastri "
        "sulla pista da ballo lucidata. L'orchestra suona fino "
        "all'alba per chi ha di che pagare l'ingresso.",
    ),
    "cat_and_fiddle": (
        "Il Pub Il Gatto e il Violino",
        "derby_est",
        "pub",
        "pub",
        "Birra scura e chiacchiere sommesse riempiono questo locale dal "
        "soffitto basso. I marinai di passaggio raccontano storie che "
        "gli avventori abituali fingono di non credere.",
    ),
    "dovers_groceries": (
        "Drogheria Dover",
        "church_ovest",
        "drogheria",
        "drogheria",
        "Barattoli di conserve e sacchi di farina sono impilati con "
        "ordine quasi militare. Il proprietario conosce per nome ogni "
        "famiglia della via, e i loro segreti insieme ai loro debiti.",
    ),

    # --- Altri negozi (23/23) ---
    "leatherworks": (
        "Lavorazione del Cuoio di Arkham",
        "college_ovest",
        "pelletteria",
        "pelletteria",
        "Valigie, cinture e finimenti da cavallo pendono da ogni "
        "parete. L'odore di cuoio conciato e' cosi' intenso da far "
        "lacrimare gli occhi ai clienti meno abituati.",
    ),
    "medical_supplies": (
        "Forniture Mediche di Arkham",
        "derby_est",
        "forniture mediche",
        "forniture",
        "Scaffali di vetro espongono strumenti chirurgici lucidati e "
        "boccette etichettate a mano. Alcuni strumenti in fondo alla "
        "vetrina non sembrano avere un uso medico convenzionale.",
    ),
    "burns_agricultural": (
        "Prodotti Agricoli Burns",
        "main_ovest",
        "prodotti agricoli",
        "burns",
        "Sacchi di sementi e attrezzi agricoli riempiono il negozio "
        "fino al soffitto. Il proprietario parla volentieri del "
        "raccolto, meno volentieri di certi campi ai margini della "
        "città che nessuno vuole più coltivare.",
    ),
    "carlas_collectibles": (
        "Da Collezione di Carla",
        "west_sud",
        "collezionismo",
        "carla",
        "Francobolli, monete e cartoline d'epoca riempiono vetrinette "
        "polverose. Carla giura che ogni pezzo ha una storia, e su "
        "alcuni preferisce non dilungarsi.",
    ),
    "browning_gunsmith": (
        "Bottega di Charles Browning, Mastro Armaiolo",
        "garrison_sud",
        "armeria",
        "armeria",
        "Fucili da caccia e rivoltelle sono esposti con la cura di "
        "opere d'arte. Ultimamente, dice Browning, le vendite di "
        "munizioni d'argento sono aumentate in modo curioso.",
    ),
    "clarke_furniture": (
        "Mobili di Qualita' Clarke e Figli",
        "hyde_ovest",
        "mobilificio",
        "mobili",
        "Credenze intagliate e sedie imbottite riempiono la sala "
        "espositiva. L'odore di vernice fresca copre solo in parte "
        "quello del legno vecchio riciclato da altre case.",
    ),
    "eddies_bikes": (
        "L'Emporio delle Biciclette di Eddie",
        "peabody_sud",
        "biciclette",
        "eddie",
        "Biciclette lucide sono appese al soffitto e allineate contro "
        "le pareti. Eddie ripara qualunque cosa abbia due ruote, "
        "fischiettando sempre la stessa strana melodia.",
    ),
    "garricks_knickknacks": (
        "Ninnoli di Garrick",
        "crane_ovest",
        "ninnoli",
        "garrick",
        "Un caotico assortimento di soprammobili, bottoni e chincaglie "
        "riempie ogni ripiano. Trovare qualcosa di preciso qui è quasi "
        "impossibile - trovare qualcosa di inaspettato, garantito.",
    ),
    "jamisons_hunting": (
        "Forniture da Caccia Jamison",
        "boundary_sud",
        "forniture da caccia",
        "caccia",
        "Trappole, richiami e cartucce riempiono gli scaffali. Alcune "
        "trappole esposte in vetrina sembrano pensate per qualcosa di "
        "ben più grande della normale selvaggina locale.",
    ),
    "janson_hardware": (
        "Ferramenta e Forniture Famiglia Janson",
        "derby_ovest",
        "ferramenta",
        "ferramenta",
        "Chiodi, corde e attrezzi di ogni tipo sono ordinati in "
        "cassetti etichettati a mano. Il proprietario sa sempre "
        "esattamente cosa serve, spesso prima ancora che tu lo chieda.",
    ),
    "wingham_shipwright": (
        "Bottega di Harold Wingham, Mastro Carpentiere Navale",
        "french_hill_sud",
        "cantiere navale",
        "cantiere",
        "Modellini di navi e attrezzi da carpentiere riempiono la "
        "bottega, con l'odore di catrame e legno di quercia stagionato "
        "che si respira fin dall'ingresso.",
    ),
    "heaples_toys": (
        "Giocattoli e Giochi di Heaple",
        "washington_ovest",
        "giocattoli",
        "giocattoli",
        "Trenini a molla e bambole di porcellana riempiono le vetrine. "
        "Alcune bambole, esposte in un angolo poco illuminato, hanno "
        "occhi che sembrano seguire i visitatori.",
    ),
    "margarets_curio": (
        "Il Negozio di Curiosita' di Margaret",
        "curwen_ovest",
        "curiosita",
        "margaret",
        "Maschere tribali, pietre levigate e libri rilegati in modo "
        "insolito riempiono ogni angolo. Margaret non vende mai nulla "
        "a chi fa troppe domande sulla provenienza.",
    ),
    "marvins_tattoo": (
        "Lo Studio di Tatuaggi di Marvin",
        "fishe_nord",
        "tatuaggi",
        "tatuaggi",
        "Disegni di ancore, sirene e simboli meno convenzionali "
        "tappezzano le pareti. Marvin lavora in silenzio, e i suoi "
        "clienti abituali portano tutti lo stesso strano segno.",
    ),
    "mchughs_antiques": (
        "Antiquariato McHugh",
        "church_ovest",
        "antiquario mchugh",
        "mchugh",
        "Mobili d'epoca e specchi anneriti dal tempo riempiono la sala. "
        "Alcuni pezzi, dice il proprietario, sono tornati indietro piu' "
        "volte da clienti che non sapevano spiegarne il motivo.",
    ),
    "mcnally_motors": (
        "Veicoli a Motore McNally",
        "peabody_sud",
        "concessionaria",
        "mcnally",
        "Automobili lucide occupano la sala espositiva, il metallo "
        "cromato che riflette la luce del lampione fuori dalla "
        "vetrina.",
    ),
    "peabody_pets": (
        "Animali Peabody",
        "peabody_sud",
        "animali",
        "peabody",
        "Gabbie di uccelli canori e acquari di pesci tropicali riempiono "
        "il negozio di cinguettii. In fondo alla sala, una gabbia "
        "vuota reca ancora un'etichetta con un nome che nessuno vuole "
        "leggere ad alta voce.",
    ),
    "prentices_books": (
        "Libri e Tomi di Prentice",
        "derby_ovest",
        "libreria",
        "libreria",
        "Scaffali alti fino al soffitto custodiscono romanzi, manuali "
        "e qualche volume più antico tenuto sotto chiave dietro il "
        "bancone, disponibile solo a clienti di fiducia.",
    ),
    "prescotts_gems": (
        "La Gioielleria di Prescott",
        "washington_est",
        "gioielleria prescott",
        "prescott",
        "Pietre preziose scintillano sotto teche di vetro illuminate. "
        "Prescott valuta ogni pietra con una lente e uno sguardo che "
        "sembra vedere oltre la semplice purezza del taglio.",
    ),
    "princes_jewelry": (
        "La Galleria di Gioielli di Prince",
        "river_ovest",
        "gioielleria prince",
        "prince",
        "Anelli e collane sono disposti su velluto scuro, illuminati "
        "da lampade che ne esaltano ogni sfaccettatura.",
    ),
    "salters_antiques": (
        "Antiquariato Salter",
        "derby_ovest",
        "antiquario salter",
        "salter",
        "Orologi da parete fermi a orari diversi tappezzano una parete "
        "intera. Nessuno dei due proprietari, padre e figlio, ha mai "
        "spiegato perche' nessuno venga mai rimesso in moto.",
    ),
    "strausbergs_tobacco": (
        "La Tabaccheria Pregiata di Strausberg",
        "armitage_ovest",
        "tabaccheria",
        "tabacco",
        "L'aroma dolciastro del tabacco da pipa impregna l'aria. "
        "Strausberg vanta miscele importate da porti che pochi dei suoi "
        "clienti saprebbero indicare su una mappa.",
    ),
    "zimmerman_luggage": (
        "La Valigeria Zimmerman",
        "armitage_ovest",
        "valigeria",
        "valigie",
        "Bauli da viaggio e valigie di cuoio sono impilati fino al "
        "soffitto, pronti per chiunque debba lasciare Arkham - o per "
        "chi debba nasconderci qualcosa dentro.",
    ),

    # --- Luoghi di culto (7/7) ---
    "asbury_methodist": (
        "Chiesa Metodista-Episcopale Asbury",
        "boundary_sud",
        "chiesa metodista",
        "asbury",
        "Panche di legno scuro si allineano ordinate sotto vetrate "
        "semplici. Il pastore predica con voce ferma, come se sapesse "
        "esattamente contro cosa sta mettendo in guardia la sua "
        "congregazione.",
    ),
    "convent_st_teresa": (
        "Il Convento di Santa Teresa",
        "west_sud",
        "convento",
        "convento",
        "Un silenzio quasi assoluto regna dietro le sue mura di pietra. "
        "Le suore camminano a passo lento nei corridoi, pregando per "
        "l'anima di una città che forse non merita più preghiere.",
    ),
    "first_baptist": (
        "Prima Chiesa Battista di Arkham",
        "church_est",
        "chiesa battista",
        "battista",
        "Un semplice campanile bianco svetta sopra il tetto a "
        "capanna. All'interno, il coro prova gli inni della domenica "
        "con un fervore che rasenta la disperazione.",
    ),
    "miskatonic_synagogue": (
        "Sinagoga Miskatonic",
        "church_ovest",
        "sinagoga",
        "sinagoga",
        "La Stella di David decora il portale d'ingresso in legno "
        "scolpito. All'interno, antichi testi sono custoditi con una "
        "cura che va oltre il semplice rispetto religioso.",
    ),
    "st_genisius": (
        "Basilica di San Genesio",
        "parsonage_sud",
        "basilica",
        "basilica",
        "Guglie di pietra si innalzano sopra vetrate policrome. "
        "L'odore di incenso e cera d'api accoglie i fedeli fin dalla "
        "soglia della grande navata.",
    ),
    "st_stanislaus": (
        "Chiesa di San Stanislao",
        "derby_est",
        "chiesa di san stanislao",
        "stanislao",
        "Una piccola chiesa di mattoni rossi, frequentata soprattutto "
        "dalla comunità polacca della città. Le candele votive non si "
        "spengono mai del tutto, nemmeno di notte.",
    ),
    "st_toads_mission": (
        "Missione di San Rospo",
        "federal_nord",
        "missione",
        "missione",
        "Un edificio modesto che offre pasti caldi e un letto ai "
        "senzatetto della città. Il nome, dicono i più anziani, "
        "risale a una storia che è meglio non chiedere di raccontare "
        "due volte.",
    ),

    # --- Banche (2/2) ---
    "first_bank": (
        "Prima Banca di Arkham",
        "college_est",
        "prima banca",
        "banca",
        "Un caveau blindato domina il piano interrato, mentre al piano "
        "terra impiegati in gilet scuro contano banconote dietro "
        "sportelli di ottone lucidato.",
    ),
    "second_bank": (
        "Seconda Banca di Arkham",
        "church_ovest",
        "seconda banca",
        "seconda",
        "Una succursale piu' piccola, incastonata dentro i confini "
        "stessi del campus della Miskatonic University, usata "
        "soprattutto da docenti e studenti facoltosi.",
    ),

    # --- Alberghi (3/3) ---
    "dombrowski_boarding": (
        "La Pensione di Dombrowski",
        "pickman_est",
        "pensione",
        "pensione",
        "Camere modeste ma pulite, affittate soprattutto a operai e "
        "marinai di passaggio. La padrona di casa non fa mai troppe "
        "domande, purché l'affitto sia pagato in anticipo.",
    ),
    "grand_hotel": (
        "Il Grand Hotel di Arkham",
        "jenkin_nord",
        "grand hotel",
        "grandhotel",
        "Un atrio sfarzoso con lampadari di cristallo accoglie gli "
        "ospiti piu' facoltosi di passaggio ad Arkham. Il personale "
        "in livrea si muove con discrezione quasi innaturale.",
    ),
    "miskatonic_hotel": (
        "Hotel Miskatonic",
        "pickman_ovest",
        "hotel miskatonic",
        "hotel",
        "Un albergo di categoria media, popolare tra i visitatori "
        "dell'università. La hall profuma sempre vagamente di muffa, "
        "per quanto il personale si sforzi di mascherarlo.",
    ),

    # --- Luoghi all'aperto (3/3) ---
    "municipal_park": (
        "Parco Municipale di Arkham",
        "garrison_sud",
        "parco",
        "parco",
        "Vialetti ghiaiosi serpeggiano tra aiuole curate e vecchie "
        "querce. Di notte, pochi cittadini si avventurano oltre la "
        "prima fila di lampioni.",
    ),
    "assyrian_gardens": (
        "I Giardini Assiri",
        "powder_mill_sud",
        "giardini",
        "giardini",
        "Un giardino pubblico in stile esotico, con statue e fontane "
        "ispirate a un'antichità che ha ben poco a che fare con la "
        "Nuova Inghilterra.",
    ),
    "olde_towne_cemetery": (
        "Il Cimitero della Citta' Vecchia",
        "lich_est",
        "cimitero",
        "cimitero",
        "Lapidi consumate dal tempo si inclinano tra alberi secolari. "
        "Alcune tombe, le piu' antiche, portano nomi che compaiono "
        "ancora, di tanto in tanto, nei registri civici della città.",
    ),

    # --- Altri luoghi (14/16 - Mortis & Carver e la stazione radio
    # gestiti a parte piu' sotto, la prima perche' riusa una stanza
    # gia' esistente da rooms_newbie.py) ---
    "community_theatre": (
        "Teatro Comunale di Arkham",
        "garrison_nord",
        "teatro",
        "teatro",
        "Un modesto teatro che ospita rappresentazioni itineranti e "
        "recite scolastiche. Le poltrone in velluto rosso hanno visto "
        "tempi migliori.",
    ),
    "historical_society": (
        "La Societa' Storica di Arkham",
        "church_ovest",
        "societa storica",
        "storia",
        "Vetrine espongono documenti coloniali e ritratti di antenati "
        "arkhamiti dallo sguardo severo. Alcuni faldoni d'archivio "
        "restano permanentemente chiusi al pubblico.",
    ),
    "home_elderly": (
        "Casa di Riposo di Arkham",
        "derby_est",
        "casa di riposo",
        "riposo",
        "Un edificio tranquillo dove gli anziani della città "
        "trascorrono gli ultimi anni. Alcuni ospiti, dicono le "
        "infermiere, parlano nel sonno di cose che nessun manuale di "
        "medicina saprebbe spiegare.",
    ),
    "institute_of_art": (
        "Istituto d'Arte di Arkham",
        "washington_ovest",
        "istituto arte",
        "arte",
        "Corridoi luminosi espongono dipinti di paesaggi locali e "
        "ritratti. Una piccola sala sul retro, poco pubblicizzata, "
        "ospita opere che i curatori preferiscono non commentare.",
    ),
    "museum_history": (
        "Museo di Storia di Arkham",
        "college_ovest",
        "museo",
        "museo",
        "Teche di vetro custodiscono reperti coloniali e strumenti "
        "marittimi d'epoca. Un'ala del museo, chiusa da anni per "
        "restauro, non ha mai riaperto.",
    ),
    "observatory": (
        "Osservatorio di Arkham",
        "miskatonic_ovest",
        "osservatorio",
        "osservatorio",
        "Una grande cupola di rame ospita il telescopio principale "
        "dell'università. Gli astronomi qui di stanza lavorano spesso "
        "fino alle ore piccole, annotando posizioni celesti con "
        "un'attenzione quasi ossessiva.",
    ),
    "arkham_observer": (
        "L'Osservatore di Arkham",
        "college_est",
        "giornale",
        "giornale",
        "Il rumore delle rotative scuote leggermente il pavimento. I "
        "giornalisti qui dentro hanno imparato a non indagare troppo a "
        "fondo su certe sparizioni, per il bene della loro carriera.",
    ),
    "passenger_docks": (
        "Moli Passeggeri di Arkham",
        "french_hill_sud",
        "moli",
        "moli",
        "Piroscafi e pescherecci ormeggiano lungo banchine di legno "
        "consumato. L'odore di sale e catrame si mescola a quello, "
        "piu' sottile, di pesce lasciato marcire troppo a lungo.",
    ),
    "pugilists_club": (
        "Il Club dei Pugili di Arkham",
        "west_nord",
        "club pugilistico",
        "pugili",
        "Un ring consumato occupa il centro della sala, circondato da "
        "gradinate di legno. L'odore di sudore e liniment non se ne va "
        "mai del tutto.",
    ),
    "skeptical_minds": (
        "Societa' delle Menti Scettiche di Arkham",
        "college_ovest",
        "societa scettici",
        "scettici",
        "Un piccolo circolo di razionalisti si riunisce qui per "
        "smascherare medium e ciarlatani. Ultimamente, dicono i soci "
        "più anziani, e' sempre piu' difficile trovare qualcosa da "
        "smascherare con certezza.",
    ),
    "town_auction_hall": (
        "Sala Aste Comunale di Arkham",
        "bad_water_sud",
        "sala aste",
        "aste",
        "File di sedie pieghevoli fronteggiano un podio consumato. "
        "Certi lotti, quelli provenienti da proprietà rimaste a lungo "
        "disabitate, attirano sempre offerenti particolarmente "
        "insistenti.",
    ),
    "train_station": (
        "Stazione Ferroviaria di Arkham",
        "armitage_ovest",
        "stazione",
        "stazione",
        "Una tettoia di ferro battuto copre i binari, dove il fischio "
        "dei treni in arrivo da Boston e Providence riecheggia a ogni "
        "ora del giorno.",
    ),
    "old_guild_hall": (
        "La Vecchia Sala delle Gilde",
        "main_ovest",
        "sala delle gilde",
        "gilde",
        "Un edificio austero dove un tempo si riunivano le "
        "corporazioni artigiane della città. Oggi ospita perlopiu' "
        "riunioni civiche e, di tanto in tanto, incontri più "
        "riservati.",
    ),
    "christmas_grotto": (
        "La Grotta di Natale di Pearson e Figli",
        "garrison_nord",
        "grotta di natale",
        "grotta",
        "Decorazioni natalizie scintillano tutto l'anno in questa "
        "bottega stagionale, gestita da una famiglia che sembra non "
        "invecchiare mai quanto dovrebbe.",
    ),
}

# Mortis & Carver riusa la stanza-morgue gia' creata in
# world/rooms_newbie.py (stesso edificio, stesso nome italiano gia'
# coniato li'): non va duplicata, va solo agganciata alla sua via.
MORTIS_CARVER_STREET = "lich_est"
MORTIS_CARVER_EXIT = ("impresa funebre", "mortis")
MORTIS_CARVER_MORGUE_TAG = "arkham_miskatonic_morgue"

# WHPL Arkham Radio
RADIO_KEY = "whpl_radio"
RADIO_DATA = (
    "Radio WHPL Arkham",
    "peabody_nord",
    "radio",
    "radio",
    "Un piccolo studio gremito di apparecchiature elettriche "
    "ronzanti. Lo speaker legge le notizie della sera con voce "
    "impostata, tacendo accuratamente certi fatti di cronaca che "
    "tutta Arkham conosce comunque.",
)
BUILDINGS["whpl_radio"] = RADIO_DATA


def _get_or_create_building(chiave):
    """Trova la stanza-edificio <chiave>, o la crea e la collega alla sua via."""
    tag_key = f"building_{chiave}"
    nome = BUILDINGS[chiave][0]
    existing = search.search_tag(tag_key, category=TAG_CATEGORY)
    if existing:
        room = existing[0]
        room.db.orari = _ORARI_PER_NOME.get(nome)
        return room

    nome, via_chiave, uscita_dalla_via, alias, descrizione = BUILDINGS[chiave]
    via_room = _get_or_create_street(via_chiave)

    room = create.create_object("typeclasses.rooms.Room", key=nome)
    room.db.desc = descrizione
    room.db.orari = _ORARI_PER_NOME.get(nome)  # world/tempo.py - None se non e' un negozio o manca dalla fonte
    room.tags.add(tag_key, category=TAG_CATEGORY)

    create.create_object(
        "typeclasses.exits.Exit",
        key=uscita_dalla_via,
        aliases=[alias] if alias else [],
        location=via_room,
        destination=room,
    )
    create.create_object(
        "typeclasses.exits.Exit",
        key="fuori",
        aliases=["fu"],
        location=room,
        destination=via_room,
    )
    return room


def _collega_mortis_carver():
    """
    Aggancia la stanza-morgue dell'hub Miskatonic (gia' creata da
    world/rooms_newbie.py) alla via Lich Street, senza duplicarla.
    """
    morgue_rooms = search.search_tag(MORTIS_CARVER_MORGUE_TAG, category="start_room")
    if not morgue_rooms:
        # le stanze newbie non sono ancora state create: rimandiamo,
        # verra' ritentato alla prossima chiamata di crea_tutti_edifici()
        return None
    morgue_room = morgue_rooms[0]

    via = _get_or_create_street(MORTIS_CARVER_STREET)
    uscita, alias = MORTIS_CARVER_EXIT

    already_linked = any(
        e.destination and e.destination.id == morgue_room.id for e in via.exits
    )
    if not already_linked:
        create.create_object(
            "typeclasses.exits.Exit",
            key=uscita,
            aliases=[alias],
            location=via,
            destination=morgue_room,
        )
    already_back = any(
        e.destination and e.destination.id == via.id for e in morgue_room.exits
    )
    if not already_back:
        create.create_object(
            "typeclasses.exits.Exit",
            key="fuori",
            aliases=["fu"],
            location=morgue_room,
            destination=via,
        )
    return morgue_room


def crea_edifici_municipali():
    """Crea (se non esistono gia') i 7 edifici municipali. Idempotente."""
    chiavi = [
        "city_courthouse", "city_hall", "fire_department", "medical_center",
        "miskatonic_university", "police_station", "post_office",
    ]
    return {chiave: _get_or_create_building(chiave) for chiave in chiavi}


def crea_edifici_abbigliamento():
    """Crea (se non esistono gia') i 6 negozi di abbigliamento. Idempotente."""
    chiavi = [
        "bridal_boutique", "giovanni_clothing", "hans_yodin", "miss_ann",
        "carrington_milliner", "watkins_formal",
    ]
    return {chiave: _get_or_create_building(chiave) for chiave in chiavi}


def crea_edifici_cibo():
    """Crea (se non esistono gia') i 6 locali di cibo/svago. Idempotente."""
    chiavi = [
        "fish_market", "barlows_butcher", "black_dahlia", "blue_ballroom",
        "cat_and_fiddle", "dovers_groceries",
    ]
    return {chiave: _get_or_create_building(chiave) for chiave in chiavi}


def crea_edifici_negozi():
    """Crea (se non esistono gia') i 23 altri negozi. Idempotente."""
    chiavi = [
        "leatherworks", "medical_supplies", "burns_agricultural",
        "carlas_collectibles", "browning_gunsmith", "clarke_furniture",
        "eddies_bikes", "garricks_knickknacks", "jamisons_hunting",
        "janson_hardware", "wingham_shipwright", "heaples_toys",
        "margarets_curio", "marvins_tattoo", "mchughs_antiques",
        "mcnally_motors", "peabody_pets", "prentices_books",
        "prescotts_gems", "princes_jewelry", "salters_antiques",
        "strausbergs_tobacco", "zimmerman_luggage",
    ]
    return {chiave: _get_or_create_building(chiave) for chiave in chiavi}


def crea_edifici_culto():
    """Crea (se non esistono gia') i 7 luoghi di culto. Idempotente."""
    chiavi = [
        "asbury_methodist", "convent_st_teresa", "first_baptist",
        "miskatonic_synagogue", "st_genisius", "st_stanislaus",
        "st_toads_mission",
    ]
    return {chiave: _get_or_create_building(chiave) for chiave in chiavi}


def crea_edifici_banche():
    """Crea (se non esistono gia') le 2 banche. Idempotente."""
    chiavi = ["first_bank", "second_bank"]
    return {chiave: _get_or_create_building(chiave) for chiave in chiavi}


def crea_edifici_alberghi():
    """Crea (se non esistono gia') i 3 alberghi. Idempotente."""
    chiavi = ["dombrowski_boarding", "grand_hotel", "miskatonic_hotel"]
    return {chiave: _get_or_create_building(chiave) for chiave in chiavi}


def crea_edifici_aperto():
    """Crea (se non esistono gia') i 3 luoghi all'aperto. Idempotente."""
    chiavi = ["municipal_park", "assyrian_gardens", "olde_towne_cemetery"]
    return {chiave: _get_or_create_building(chiave) for chiave in chiavi}


def crea_edifici_altro():
    """
    Crea (se non esistono gia') i restanti 16 luoghi vari. Idempotente.
    Include il collegamento speciale di Mortis & Carver (riuso della
    stanza-morgue esistente) e WHPL Arkham Radio.
    """
    chiavi = [
        "community_theatre", "historical_society", "home_elderly",
        "institute_of_art", "museum_history", "observatory",
        "arkham_observer", "passenger_docks", "pugilists_club",
        "skeptical_minds", "town_auction_hall", "train_station",
        "old_guild_hall", "christmas_grotto", "whpl_radio",
    ]
    risultato = {chiave: _get_or_create_building(chiave) for chiave in chiavi}
    risultato["mortis_carver"] = _collega_mortis_carver()
    return risultato


def crea_tutti_edifici():
    """
    Crea (se non esistono gia') tutti i 73 edifici di Arkham, in tutte
    le 9 categorie del catalogo. Idempotente: si puo' rilanciare senza
    duplicare nulla.
    """
    risultato = {}
    risultato.update(crea_edifici_municipali())
    risultato.update(crea_edifici_abbigliamento())
    risultato.update(crea_edifici_cibo())
    risultato.update(crea_edifici_negozi())
    risultato.update(crea_edifici_culto())
    risultato.update(crea_edifici_banche())
    risultato.update(crea_edifici_alberghi())
    risultato.update(crea_edifici_aperto())
    risultato.update(crea_edifici_altro())
    return risultato
