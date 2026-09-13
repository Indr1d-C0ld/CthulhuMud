"""
Popolamento NPC di ambientazione (Fase F, ottava tornata): edifici
civici, religiosi e altri luoghi che non hanno una vera funzione di
compravendita ricevono comunque un NPC di presenza, per non restare
scenografia vuota. Nessuna meccanica speciale (a differenza di
mercanti/banca/locanda): solo un personaggio con cui la stanza prende
vita, esaminabile e con cui interagire tramite i comandi generali gia'
tradotti (say, whisper, pose...).

Copre: municipale (7), culto (7), altro senza negozio (15), aperto (3)
= 32 edifici. (Il Teatro Comunale era stato dimenticato nella prima
stesura: aggiunto in una correzione successiva.)
"""

from evennia.utils import create, search

# (tag_chiave, categoria_tag, nome_npc, descrizione)
NPC_DA_CREARE = [
    # --- Municipale (7) ---
    ("building_city_courthouse", "arkham_building", "un usciere del tribunale",
     "Un uomo dall'aria severa, che controlla i documenti dei visitatori "
     "con una lentezza esasperante, come se il tempo non gli importasse affatto."),
    ("building_city_hall", "arkham_building", "un impiegato comunale",
     "Un uomo dietro una scrivania sommersa di moduli, che risponde a "
     "ogni domanda proponendo un altro modulo da compilare."),
    ("building_fire_department", "arkham_building", "un vigile del fuoco di turno",
     "Un uomo in uniforme, che lucida l'ottone della pompa antincendio "
     "con una cura quasi devota."),
    ("building_medical_center", "arkham_building", "un'infermiera di turno",
     "Una donna dall'aria stanca ma gentile, che controlla una cartella "
     "clinica senza alzare lo sguardo."),
    ("building_miskatonic_university", "arkham_building", "uno studente universitario",
     "Un giovane con una pila di libri sotto il braccio, sempre di corsa "
     "verso la prossima lezione."),
    ("building_police_station", "arkham_building", "un sergente di polizia",
     "Un uomo corpulento dietro la scrivania, che osserva ogni visitatore "
     "con sospetto professionale."),
    ("building_post_office", "arkham_building", "un impiegato delle poste",
     "Un uomo minuto che timbra buste con un ritmo meccanico, quasi "
     "ipnotico."),

    # --- Luoghi di culto (7) ---
    ("building_asbury_methodist", "arkham_building", "il pastore Asbury",
     "Un uomo anziano dalla voce profonda, che sistema gli inni sul "
     "leggio prima della funzione."),
    ("building_convent_st_teresa", "arkham_building", "suor Agnese",
     "Una suora dagli occhi gentili, che prega in silenzio, muovendo "
     "appena le labbra."),
    ("building_first_baptist", "arkham_building", "il reverendo Miller",
     "Un uomo energico, che prova il sermone della domenica a voce alta, "
     "da solo nella navata vuota."),
    ("building_miskatonic_synagogue", "arkham_building", "il rabbino Cohen",
     "Un uomo anziano immerso nella lettura di un antico testo, che alza "
     "lo sguardo solo per un attimo."),
    ("building_st_genisius", "arkham_building", "un sacerdote",
     "Un uomo in tonaca nera, che accende candele votive una a una, con "
     "gesti lenti e misurati."),
    ("building_st_stanislaus", "arkham_building", "padre Wojcik",
     "Un sacerdote dall'accento marcato, molto amato dalla comunita' "
     "polacca della citta'."),
    ("building_st_toads_mission", "arkham_building", "un volontario della missione",
     "Un uomo dall'aria stanca ma paziente, che serve una zuppa calda "
     "senza fare domande."),

    # --- Altri luoghi senza negozio (14) ---
    ("building_historical_society", "arkham_building", "un archivista",
     "Un uomo con gli occhiali spessi, che maneggia documenti ingialliti "
     "con guanti di cotone bianco."),
    ("building_home_elderly", "arkham_building", "un'infermiera dell'ospizio",
     "Una donna paziente, che ascolta i racconti degli ospiti anche "
     "quando li ha gia' sentiti decine di volte."),
    ("building_institute_of_art", "arkham_building", "un curatore",
     "Un uomo elegante, che osserva ogni visitatore con la stessa "
     "attenzione critica riservata ai quadri."),
    ("building_museum_history", "arkham_building", "una guida del museo",
     "Una donna che recita la stessa spiegazione ai visitatori con un "
     "entusiasmo sempre identico, giorno dopo giorno."),
    ("building_observatory", "arkham_building", "un astronomo",
     "Un uomo con gli occhi arrossati dalle troppe notti passate al "
     "telescopio, che annota posizioni celesti su un taccuino."),
    ("building_arkham_observer", "arkham_building", "un giornalista",
     "Un uomo con le maniche arrotolate e le dita macchiate d'inchiostro, "
     "sempre alla ricerca della prossima notizia."),
    ("building_passenger_docks", "arkham_building", "un marinaio",
     "Un uomo dal passo ondeggiante, che carica casse fischiettando una "
     "melodia straniera."),
    ("building_pugilists_club", "arkham_building", "un allenatore di pugilato",
     "Un uomo con il naso rotto piu' di una volta, che osserva gli "
     "incontri immaginari con occhio esperto."),
    ("building_skeptical_minds", "arkham_building", "un membro della società",
     "Un uomo dall'aria compita, pronto a spiegare con dovizia di "
     "dettagli perche' l'ultimo fantasma avvistato in citta' sia solo un "
     "trucco di luce."),
    ("building_town_auction_hall", "arkham_building", "il banditore",
     "Un uomo dalla voce potente, che batte il martelletto con gesti "
     "teatrali anche quando la sala e' vuota."),
    ("building_train_station", "arkham_building", "un capostazione",
     "Un uomo con un orologio da tasca sempre in mano, che controlla gli "
     "orari con precisione ossessiva."),
    ("building_old_guild_hall", "arkham_building", "un custode",
     "Un uomo anziano che spazza il pavimento della sala, ricordando ad "
     "alta voce tempi che nessun altro sembra ricordare."),
    ("building_christmas_grotto", "arkham_building", "uno degli elfi di Pearson",
     "Una figura vestita di rosso e verde, che sorride sempre un po' "
     "troppo a lungo per essere del tutto rassicurante."),
    ("building_whpl_radio", "arkham_building", "uno speaker radiofonico",
     "Un uomo con una voce impostata da professionista, che prova le "
     "battute di apertura del notiziario serale davanti al microfono spento."),
    ("building_community_theatre", "arkham_building", "un attore di passaggio",
     "Un uomo che recita da solo un monologo sul palco vuoto, provando "
     "gesti ampi per una platea che questa sera non c'e' ancora."),

    # --- Luoghi all'aperto (3) ---
    ("building_municipal_park", "arkham_building", "un giardiniere",
     "Un uomo che pota le siepi con calma, ignorando i pettegolezzi che "
     "i passanti si scambiano nei suoi pressi."),
    ("building_assyrian_gardens", "arkham_building", "un custode dei giardini",
     "Un uomo silenzioso che innaffia le piante esotiche con un "
     "innaffiatoio consumato dal tempo."),
    ("building_olde_towne_cemetery", "arkham_building", "il custode del cimitero",
     "Un uomo curvo dagli anni, che conosce ogni nome inciso sulle "
     "lapidi meglio dei propri parenti."),
]


def _crea_npc_ambientazione(location, nome, descrizione):
    npc = create.create_object(
        "typeclasses.npcs.NPC",
        key=nome,
        location=location,
    )
    npc.db.desc = descrizione
    npc.db.ostile = False
    npc.db.is_practice_trainer = False
    return npc


def popola_npc_ambientazione():
    """
    Crea (se non esiste gia' un NPC in quella stanza) un NPC di
    ambientazione per ognuno dei 31 edifici elencati. Idempotente:
    controlla se la stanza ha gia' un NPC prima di crearne uno nuovo
    (a prescindere che sia un mercante o un NPC di ambientazione - una
    stanza non deve avere piu' di un abitante fisso).
    """
    creati = []
    saltati = []
    for tag_chiave, categoria, nome, descrizione in NPC_DA_CREARE:
        stanze = search.search_tag(tag_chiave, category=categoria)
        if not stanze:
            continue
        stanza = stanze[0]
        esistente = [
            obj for obj in stanza.contents
            if obj.is_typeclass("typeclasses.npcs.NPC", exact=False)
        ]
        if esistente:
            saltati.append((stanza.key, esistente[0].key))
            creati.append(esistente[0])
            continue
        creati.append(_crea_npc_ambientazione(stanza, nome, descrizione))
    return creati, saltati
