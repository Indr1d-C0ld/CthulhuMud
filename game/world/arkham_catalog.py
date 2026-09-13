"""
Catalogo dei 73 edifici di Arkham, estratto dalla guida ufficiale
https://www.cthulhumud.com/guides_arkham (rilevazione settembre 2026).

Questo NON e' ancora building vero e proprio (nessuna Room viene creata
qui): e' il materiale grezzo di riferimento per quando affronteremo la
costruzione completa di Arkham, colmando la lacuna segnalata nel
Dossier Miskatonic ("73 edifici/negozi catalogati con indirizzo" - li
avevamo contati ma non elencati).

Convenzione di localizzazione italiana adottata (coerente con tutto il
resto del progetto, es. "Mortis & Carver, Impresa di Pompe Funebri" gia'
usata in rooms_newbie.py per questo stesso edificio):
- I nomi propri di via (Derby, Curwen, Hyde, Armitage, Garrison, Peabody,
  Federal, Fishe, Marsh, Whatley, Water, Goode, Apple, West, Jenkin,
  River, Main, Church, Crane, Boundary, Bad Water, Lich, Powder Mill,
  Parsonage, French Hill, College, Pickman, Miskatonic, Washington)
  RESTANO invariati: molti sono riferimenti letterari lovecraftiani
  diretti (Curwen da "Il caso di Charles Dexter Ward", Armitage e
  Whatley da "L'orrore di Dunwich", Pickman da "Il modello di Pickman")
  e vanno preservati come tali, non tradotti.
- Il suffisso generico della via viene italianizzato: Street -> Via,
  Avenue -> Viale, Road -> Strada, Lane -> Vicolo.
- I nomi propri di persona nelle attivita' commerciali (Giovanni, Hans
  Yodin, Margaret, Marvin, McHugh, Dombrowski, ecc.) restano invariati;
  la parte descrittiva del nome viene tradotta.
- Gli orari sono conservati come stringa originale in inglese (es.
  "9am-9pm", "Always Open") - agganciati alle stanze-edificio reali in
  world/rooms_arkham_edifici.py:_get_or_create_building() e usati dal
  vero sistema di orari costruito in Fase K, quindicesima tornata
  (vedi world/tempo.py, comandi TIME/HOURS, gating di LIST/BUY/SELL).

Struttura di ogni voce:
    (nome_originale, nome_italiano, indirizzo_originale, indirizzo_italiano,
     categoria, orari_o_None)
"""

# fmt: off
ARKHAM_BUILDINGS = [
    # --- Edifici municipali (7) ---
    ("City Courthouse", "Tribunale Municipale", "250 West College Street", "250 Via College Ovest", "municipale", None),
    ("City Hall", "Municipio", "1000 South West Street", "1000 Via West Sud", "municipale", None),
    ("Fire Department", "Caserma dei Vigili del Fuoco", "200 South Garrison Street", "200 Via Garrison Sud", "municipale", None),
    ("Miskatonic Regional Medical Center", "Centro Medico Regionale Miskatonic", "850 South West Street", "850 Via West Sud", "municipale", None),
    ("Miskatonic University", "Universita' Miskatonic", "450 West Church Street", "450 Via Church Ovest", "municipale", None),
    ("Police Station", "Commissariato di Polizia", "201 South Peabody Avenue", "201 Viale Peabody Sud", "municipale", None),
    ("U.S. Post Office", "Ufficio Postale", "1012 West Church Street", "1012 Via Church Ovest", "municipale", None),

    # --- Negozi di abbigliamento (6) ---
    ("Arkham Bridal Boutique", "Boutique da Sposa di Arkham", "302 West River Street", "302 Via River Ovest", "abbigliamento", "11am-10pm"),
    ("Giovanni's Clothing for Men", "Abbigliamento da Uomo di Giovanni", "780 North West Street", "780 Via West Nord", "abbigliamento", "10am-9pm"),
    ("Hans Yodin, Master Cobbler", "Hans Yodin, Mastro Calzolaio", "215 North Fishe Street", "215 Via Fishe Nord", "abbigliamento", "9am-10pm"),
    ("Miss Ann's Fashions for Ladies", "Moda da Donna di Miss Ann", "319 West Church Street", "319 Via Church Ovest", "abbigliamento", "9am-9pm"),
    ("V. Carrington, Expert Milliner", "V. Carrington, Cappellaia Esperta", "707 West Main Street", "707 Via Main Ovest", "abbigliamento", "9am-9pm"),
    ("Watkins' Formal Wear", "Abiti Eleganti Watkins", "242 West River Street", "242 Via River Ovest", "abbigliamento", "9am-9pm"),

    # --- Cibo e locali (6) ---
    ("Arkham Fish Market", "Mercato del Pesce di Arkham", "362 West Derby Street", "362 Via Derby Ovest", "cibo", "Always Open"),
    ("Barlow's Butcher Shop", "Macelleria Barlow", "461 West Church Street", "461 Via Church Ovest", "cibo", "9am-10pm"),
    ("Black Dahlia Jazz Club", "Jazz Club Black Dahlia", "279 North Jenkin Street", "279 Via Jenkin Nord", "cibo", None),
    ("The Blue Ballroom", "La Sala da Ballo Blu", "719 West Washington Street", "719 Via Washington Ovest", "cibo", "8pm-4am"),
    ("The Cat and Fiddle Pub", "Il Pub Il Gatto e il Violino", "224 East Derby Street", "224 Via Derby Est", "cibo", "11am-Midnight"),
    ("Dover's Groceries", "Drogheria Dover", "577 West Church Street", "577 Via Church Ovest", "cibo", "6am-10pm"),

    # --- Altri negozi (23) ---
    ("Arkham Leatherworks", "Lavorazione del Cuoio di Arkham", "486 West College Street", "486 Via College Ovest", "negozio", "Noon-Midnight"),
    ("Arkham Medical Supplies", "Forniture Mediche di Arkham", "494 East Derby Street", "494 Via Derby Est", "negozio", "9am-10pm"),
    ("Burns Agricultural Goods", "Prodotti Agricoli Burns", "843 West Main Street", "843 Via Main Ovest", "negozio", "6am-Midnight"),
    ("Carla's Collectibles", "Da Collezione di Carla", "673 South West Street", "673 Via West Sud", "negozio", "6am-7pm"),
    ("Charles Browning - Master Gun Smith", "Charles Browning - Mastro Armaiolo", "650 South Garrison Street", "650 Via Garrison Sud", "negozio", "9am-Midnight"),
    ("Clarke and Sons Quality Furniture", "Mobili di Qualita' Clarke e Figli", "215 West Hyde Street", "215 Via Hyde Ovest", "negozio", "8am-10pm"),
    ("Eddie's Bike Emporium", "L'Emporio delle Biciclette di Eddie", "690 South Peabody Street", "690 Via Peabody Sud", "negozio", "8am-7pm"),
    ("Garrick's Knick-knacks", "Ninnoli di Garrick", "245 West Crane Street", "245 Via Crane Ovest", "negozio", "Always Open"),
    ("Jamison's Hunting Supplies", "Forniture da Caccia Jamison", "867 South Boundary Street", "867 Via Boundary Sud", "negozio", "8am-7pm"),
    ("Janson Family Hardware and Supplies", "Ferramenta e Forniture Famiglia Janson", "242 West Derby Street", "242 Via Derby Ovest", "negozio", "8am-10pm"),
    ("Harold Wingham - Master Shipwright", "Harold Wingham - Mastro Carpentiere Navale", "132 South French Hill Street", "132 Via French Hill Sud", "negozio", "10am-8pm"),
    ("Heaple's Toys and Games", "Giocattoli e Giochi di Heaple", "485 West Washington Street", "485 Via Washington Ovest", "negozio", "10am-7pm"),
    ("Margaret's Curio Shop", "Il Negozio di Curiosita' di Margaret", "394 West Curwen Street", "394 Via Curwen Ovest", "negozio", "9am-10pm"),
    ("Marvin's Tattoo Parlor", "Lo Studio di Tatuaggi di Marvin", "203 North Fishe Street", "203 Via Fishe Nord", "negozio", "Always Open"),
    ("McHugh's Antiques", "Antiquariato McHugh", "898 West Church Street", "898 Via Church Ovest", "negozio", "Always Open"),
    ("McNally Motor Vehicles", "Veicoli a Motore McNally", "412 South Peabody Street", "412 Via Peabody Sud", "negozio", "8am-7pm"),
    ("Peabody Pets", "Animali Peabody", "218 South Peabody Avenue", "218 Viale Peabody Sud", "negozio", "Always Open"),
    ("Prentice's Books and Tomes", "Libri e Tomi di Prentice", "656 West Derby Street", "656 Via Derby Ovest", "negozio", "8am-7pm"),
    ("Prescott's Gem Shop", "La Gioielleria di Prescott", "207 East Washington Street", "207 Via Washington Est", "negozio", "7am-8pm"),
    ("Prince's Jewelry Galleria", "La Galleria di Gioielli di Prince", "490 West River Street", "490 Via River Ovest", "negozio", "9am-6pm"),
    ("Salter's Antiques", "Antiquariato Salter", "760 West Derby Street", "760 Via Derby Ovest", "negozio", "8am-10pm"),
    ("Strausberg's Fine Tobacco Shop", "La Tabaccheria Pregiata di Strausberg", "295 West Armitage Street", "295 Via Armitage Ovest", "negozio", "8am-11pm"),
    ("Zimmerman Luggage Shop", "La Valigeria Zimmerman", "373 West Armitage Street", "373 Via Armitage Ovest", "negozio", "8am-10pm"),

    # --- Luoghi di culto (7 confessioni) ---
    ("Asbury Methodist-Episcopal Church", "Chiesa Metodista-Episcopale Asbury", "401 South Boundary Street", "401 Via Boundary Sud", "culto", None),
    ("The Convent of St. Teresa", "Il Convento di Santa Teresa", "1472 South West Street", "1472 Via West Sud", "culto", None),
    ("First Baptist Church of Arkham", "Prima Chiesa Battista di Arkham", "207 East Church Street", "207 Via Church Est", "culto", None),
    ("Miskatonic Synagogue", "Sinagoga Miskatonic", "247 West Church Street", "247 Via Church Ovest", "culto", None),
    ("St. Genisius' Basilica", "Basilica di San Genesio", "700 South Parsonage Street", "700 Via Parsonage Sud", "culto", None),
    ("St. Stanislaus' Church", "Chiesa di San Stanislao", "600 East Derby Street", "600 Via Derby Est", "culto", None),
    ("St. Toad's Mission", "Missione di San Rospo", "362 North Federal Street", "362 Via Federal Nord", "culto", None),

    # --- Banche (2) ---
    ("First Bank of Arkham", "Prima Banca di Arkham", "425 East College Street", "425 Via College Est", "banca", None),
    ("Second Bank of Arkham", "Seconda Banca di Arkham", "450 West Church Street (inside M.U.)", "450 Via Church Ovest (dentro l'Universita' Miskatonic)", "banca", None),

    # --- Alberghi (3) ---
    ("Dombrowski's Boarding House", "La Pensione di Dombrowski", "667 East Pickman Street", "667 Via Pickman Est", "albergo", None),
    ("The Grand Hotel of Arkham", "Il Grand Hotel di Arkham", "452 North Jenkin Street", "452 Via Jenkin Nord", "albergo", None),
    ("Miskatonic Hotel", "Hotel Miskatonic", "742 West Pickman Street", "742 Via Pickman Ovest", "albergo", None),

    # --- Luoghi all'aperto (3) ---
    ("Arkham Municipal Park", "Parco Municipale di Arkham", "1200 South Garrison Street", "1200 Via Garrison Sud", "aperto", None),
    ("Assyrian Gardens", "I Giardini Assiri", "643 South Powder Mill Street", "643 Via Powder Mill Sud", "aperto", None),
    ("Olde Towne Cemetery", "Il Cimitero della Citta' Vecchia", "431 East Lich Street", "431 Via Lich Est", "aperto", None),

    # --- Altri luoghi (16) ---
    ("Arkham Community Theatre", "Teatro Comunale di Arkham", "396 North Garrison Street", "396 Via Garrison Nord", "altro", None),
    ("The Arkham Historical Society", "La Societa' Storica di Arkham", "759 West Church Street", "759 Via Church Ovest", "altro", None),
    ("Arkham Home for the Elderly", "Casa di Riposo di Arkham", "359 East Derby Street", "359 Via Derby Est", "altro", None),
    ("Arkham Institute of Art", "Istituto d'Arte di Arkham", "869 West Washington Street", "869 Via Washington Ovest", "altro", None),
    ("Arkham Museum of History", "Museo di Storia di Arkham", "550 West College Street", "550 Via College Ovest", "altro", None),
    ("Arkham Observatory", "Osservatorio di Arkham", "268 West Miskatonic Avenue", "268 Viale Miskatonic Ovest", "altro", None),
    ("The Arkham Observer", "L'Osservatore di Arkham (giornale)", "209 East College Street", "209 Via College Est", "altro", None),
    ("Arkham Passenger Docks", "Moli Passeggeri di Arkham", "800 South French Hill Street", "800 Via French Hill Sud", "altro", None),
    ("Arkham Pugilists' Club", "Il Club dei Pugili di Arkham", "723 North West Street", "723 Via West Nord", "altro", None),
    ("Arkham Society of Skeptical Minds", "Societa' delle Menti Scettiche di Arkham", "332 West College Street", "332 Via College Ovest", "altro", None),
    ("Arkham Town Auction Hall", "Sala Aste Comunale di Arkham", "193 South Bad Water Road", "193 Strada Bad Water Sud", "altro", None),
    ("Arkham Train Station", "Stazione Ferroviaria di Arkham", "400 West Armitage Street", "400 Via Armitage Ovest", "altro", None),
    ("Mortis & Carver, Undertakers", "Mortis & Carver, Impresa di Pompe Funebri", "647 East Lich Street", "647 Via Lich Est", "altro", None),
    ("Old Guild Hall", "La Vecchia Sala delle Gilde", "339 West Main Street", "339 Via Main Ovest", "altro", None),
    ("Pearson and Sons' Christmas Grotto", "La Grotta di Natale di Pearson e Figli", "523 North Garrison Street", "523 Via Garrison Nord", "altro", None),
    ("WHPL Arkham Radio", "Radio WHPL Arkham", "722 North Peabody Avenue", "722 Viale Peabody Nord", "altro", None),
]
# fmt: on

assert len(ARKHAM_BUILDINGS) == 73, f"Attesi 73 edifici, trovati {len(ARKHAM_BUILDINGS)}"
