"""
Popolamento negozi - categoria "altri negozi" (Fase F, quarta tornata):
i 21 negozi rimanenti di questa categoria ad Arkham (Prentice's Books
e Strausberg's Tobacco erano gia' stati popolati nella prima
dimostrazione).

Inventari ampliati in tornate successive fino a 7 articoli per
negozio (solo economico/di ambientazione: vedi nota in
world/popola_negozi.py).
"""

from evennia.utils import search

from world.economia import crea_mercante

NEGOZI = [
    (
        "building_leatherworks",
        "il conciapelli",
        "Un uomo dalle mani indurite dal lavoro, che valuta ogni "
        "pezzo di cuoio strofinandolo tra le dita prima di venderlo.",
        [
            {"chiave": "valigia", "nome": "una valigia di cuoio", "prezzo": 22,
             "descrizione": "Una valigia robusta, rifinita con cura."},
            {"chiave": "cintura", "nome": "una cintura in cuoio", "prezzo": 6,
             "descrizione": "Una cintura semplice ma resistente."},
            {"chiave": "finimenti", "nome": "un set di finimenti da cavallo", "prezzo": 30,
             "descrizione": "Finimenti completi, cuciti a mano."},
            {"chiave": "borsello", "nome": "un borsello di cuoio scuro", "prezzo": 9,
             "descrizione": "Un piccolo borsello con fibbia d'ottone."},
            {"chiave": "guanti", "nome": "un paio di guanti di cuoio da lavoro", "prezzo": 7,
             "descrizione": "Guanti robusti, rinforzati sul palmo."},
            {"chiave": "grembiule", "nome": "un grembiule di cuoio spesso", "prezzo": 11,
             "descrizione": "Un grembiule robusto, gia' segnato da tagli e macchie di tintura."},
            {"chiave": "fodero", "nome": "un fodero di cuoio vuoto", "prezzo": 8,
             "descrizione": "Un fodero cucito su misura, senza la lama che dovrebbe contenere."},
        ],
    ),
    (
        "building_medical_supplies",
        "il farmacista",
        "Un uomo pallido in camice bianco, che parla di strumenti "
        "chirurgici con un entusiasmo un po' fuori luogo.",
        [
            {"chiave": "bende", "nome": "un rotolo di bende", "prezzo": 3,
             "descrizione": "Bende pulite, ancora nella confezione originale."},
            {"chiave": "tintura", "nome": "una boccetta di tintura di iodio", "prezzo": 5,
             "descrizione": "Un disinfettante dall'odore pungente."},
            {"chiave": "bisturi", "nome": "un bisturi chirurgico", "prezzo": 14,
             "descrizione": "Una lama sottilissima, perfettamente affilata."},
            {"chiave": "sali", "nome": "un flacone di sali da fiuto", "prezzo": 4,
             "descrizione": "Sali pungenti, utili contro gli svenimenti."},
            {"chiave": "siringa", "nome": "una siringa di vetro con ago d'ottone", "prezzo": 10,
             "descrizione": "Una siringa d'epoca, custodita in un astuccio imbottito."},
            {"chiave": "termometro", "nome": "un termometro a mercurio", "prezzo": 6,
             "descrizione": "Un termometro in un tubicino di vetro, con la scala incisa a mano."},
            {"chiave": "aspirina", "nome": "una scatoletta di compresse contro il mal di testa", "prezzo": 3,
             "descrizione": "Piccole compresse bianche, in una scatola di latta."},
        ],
    ),
    (
        "building_burns_agricultural",
        "Burns",
        "Un uomo dalle mani grosse e il viso abbronzato, che parla di "
        "raccolti con un entusiasmo che vacilla solo quando si "
        "menzionano certi campi fuori citta'.",
        [
            {"chiave": "sementi", "nome": "un sacchetto di sementi", "prezzo": 4,
             "descrizione": "Sementi selezionate, pronte per la semina."},
            {"chiave": "vanga", "nome": "una vanga da lavoro", "prezzo": 9,
             "descrizione": "Una vanga robusta dal manico consumato."},
            {"chiave": "fieno", "nome": "una balla di fieno", "prezzo": 3,
             "descrizione": "Fieno secco, profumato di campo."},
            {"chiave": "falce", "nome": "una falce ben affilata", "prezzo": 11,
             "descrizione": "Una falce dalla lama curva, perfetta per la mietitura."},
            {"chiave": "concime", "nome": "un sacco di concime", "prezzo": 5,
             "descrizione": "Concime organico, dall'odore inconfondibile."},
            {"chiave": "rastrello", "nome": "un rastrello da giardino", "prezzo": 6,
             "descrizione": "Un rastrello robusto, dai denti leggermente storti."},
            {"chiave": "innaffiatoio", "nome": "un innaffiatoio di latta", "prezzo": 5,
             "descrizione": "Un innaffiatoio bucherellato in modo uniforme, gia' un po' arrugginito."},
        ],
    ),
    (
        "building_carlas_collectibles",
        "Carla",
        "Una donna dagli occhi vivaci, che racconta la storia di ogni "
        "pezzo della sua collezione con dovizia di dettagli sempre "
        "meno verificabili.",
        [
            {"chiave": "francobolli", "nome": "un album di francobolli", "prezzo": 8,
             "descrizione": "Un album pieno di francobolli di paesi lontani."},
            {"chiave": "monete", "nome": "una monetina d'epoca", "prezzo": 6,
             "descrizione": "Una moneta consumata, di provenienza incerta."},
            {"chiave": "cartolina", "nome": "una cartolina d'epoca", "prezzo": 2,
             "descrizione": "Una cartolina ingiallita, mai spedita."},
            {"chiave": "distintivo", "nome": "un distintivo militare arrugginito", "prezzo": 9,
             "descrizione": "Un distintivo di provenienza sconosciuta, forse straniera."},
            {"chiave": "fotografia", "nome": "una vecchia fotografia in cornice", "prezzo": 5,
             "descrizione": "Il ritratto sbiadito di una famiglia che nessuno ricorda piu'."},
            {"chiave": "medaglia", "nome": "una medaglia commemorativa", "prezzo": 7,
             "descrizione": "Una medaglia di metallo scuro, per un evento che nessuno ricorda piu'."},
            {"chiave": "biglia", "nome": "una biglia di vetro colorata", "prezzo": 2,
             "descrizione": "Una biglia con un vortice di colore intrappolato all'interno."},
        ],
    ),
    (
        "building_browning_gunsmith",
        "Charles Browning",
        "Un uomo dallo sguardo attento, che pulisce le armi esposte "
        "con la cura di chi sa esattamente a cosa servono davvero.",
        [
            {"chiave": "fucile", "nome": "un fucile da caccia", "prezzo": 55,
             "descrizione": "Un fucile a doppia canna, ben oliato.",
             "slot": "arma", "tipo_arma": "gun", "dado_min": 3, "dado_max": 9,
             "bonus_danno": 1, "livello": 8},
            {"chiave": "rivoltella", "nome": "una rivoltella a sei colpi", "prezzo": 40,
             "descrizione": "Un'arma compatta, adatta alla difesa personale.",
             "slot": "arma", "tipo_arma": "handgun", "dado_min": 2, "dado_max": 7,
             "bonus_danno": 0, "livello": 6},
            {"chiave": "munizioni", "nome": "una scatola di munizioni", "prezzo": 10,
             "descrizione": "Munizioni standard, in una scatola di cartone."},
            {"chiave": "coltello", "nome": "un coltello da caccia", "prezzo": 12,
             "descrizione": "Un coltello robusto, con il fodero di cuoio.",
             "slot": "arma", "tipo_arma": "dagger", "dado_min": 1, "dado_max": 5,
             "bonus_danno": 0, "livello": 2},
            {"chiave": "kitpulizia", "nome": "un kit di pulizia per armi", "prezzo": 8,
             "descrizione": "Scovolini, olio e panni, tutto l'occorrente per la manutenzione."},
            {"chiave": "cartucciera", "nome": "una cartucciera da spalla", "prezzo": 13,
             "descrizione": "Una cartucciera di cuoio, con alloggi cuciti per le cartucce."},
            {"chiave": "bersaglio", "nome": "un bersaglio di carta stampato", "prezzo": 2,
             "descrizione": "Un bersaglio a cerchi concentrici, gia' bucherellato da qualche cliente."},
        ],
    ),
    (
        "building_clarke_furniture",
        "Clarke",
        "Un uomo distinto che accarezza ogni mobile come se fosse un "
        "vecchio amico, elencandone i pregi con orgoglio paterno.",
        [
            {"chiave": "sedia", "nome": "una sedia imbottita", "prezzo": 18,
             "descrizione": "Una sedia comoda, rivestita in velluto verde."},
            {"chiave": "credenza", "nome": "una credenza intagliata", "prezzo": 60,
             "descrizione": "Una credenza in legno di quercia, finemente intagliata."},
            {"chiave": "specchio", "nome": "uno specchio con cornice dorata", "prezzo": 25,
             "descrizione": "Uno specchio elegante, la cornice decorata a foglia d'oro."},
            {"chiave": "lampada", "nome": "una lampada da tavolo con paralume", "prezzo": 15,
             "descrizione": "Una lampada elegante, con paralume di stoffa plissettata."},
            {"chiave": "tavolino", "nome": "un tavolino da the' intarsiato", "prezzo": 22,
             "descrizione": "Un piccolo tavolino, con intarsi in legni di diverso colore."},
            {"chiave": "libreria", "nome": "una piccola libreria in legno di ciliegio", "prezzo": 45,
             "descrizione": "Una libreria a quattro ripiani, dalle rifiniture curate."},
            {"chiave": "cuscino", "nome": "un cuscino ricamato", "prezzo": 8,
             "descrizione": "Un cuscino morbido, con una fodera ricamata a motivi floreali."},
        ],
    ),
    (
        "building_eddies_bikes",
        "Eddie",
        "Un giovane sempre con le mani sporche di grasso, che "
        "fischietta la stessa melodia mentre ripara le ruote.",
        [
            {"chiave": "bicicletta", "nome": "una bicicletta da città", "prezzo": 35,
             "descrizione": "Una bicicletta robusta, perfetta per le vie di Arkham."},
            {"chiave": "campanello", "nome": "un campanello da bicicletta", "prezzo": 2,
             "descrizione": "Un piccolo campanello di ottone."},
            {"chiave": "kit", "nome": "un kit di riparazione per gomme", "prezzo": 4,
             "descrizione": "Toppe e colla per riparare le forature."},
            {"chiave": "lucchetto", "nome": "un lucchetto con catena", "prezzo": 6,
             "descrizione": "Un lucchetto robusto, con una catena rivestita di gomma."},
            {"chiave": "fanale", "nome": "un fanale a carburo per bicicletta", "prezzo": 9,
             "descrizione": "Un piccolo fanale che illumina la strada con una fiamma viva."},
            {"chiave": "pompa", "nome": "una pompa manuale per gomme", "prezzo": 5,
             "descrizione": "Una piccola pompa, con un manometro un po' impreciso."},
            {"chiave": "cestello", "nome": "un cestello anteriore in vimini", "prezzo": 7,
             "descrizione": "Un cestello robusto, fissato con cinghie di cuoio al manubrio."},
        ],
    ),
    (
        "building_garricks_knickknacks",
        "Garrick",
        "Un uomo dall'aria distratta, circondato da uno scaffale cosi' "
        "disordinato che sembra impossibile trovarci qualcosa - "
        "eppure lui ci riesce sempre.",
        [
            {"chiave": "ninnolo", "nome": "un ninnolo di vetro colorato", "prezzo": 3,
             "descrizione": "Un piccolo oggetto decorativo, di uso incerto."},
            {"chiave": "bottone", "nome": "una scatola di bottoni assortiti", "prezzo": 2,
             "descrizione": "Bottoni di ogni forma e colore, in disordine."},
            {"chiave": "chincaglia", "nome": "una chincaglia dall'uso misterioso", "prezzo": 5,
             "descrizione": "Nemmeno Garrick sa piu' bene a cosa serva."},
            {"chiave": "gomitolo", "nome": "un gomitolo di spago", "prezzo": 1,
             "descrizione": "Spago robusto, buono per mille usi diversi."},
            {"chiave": "scatolina", "nome": "una scatolina di latta arrugginita", "prezzo": 2,
             "descrizione": "Una scatola vuota, che pero' Garrick vende come 'contenitore d'epoca'."},
            {"chiave": "lente", "nome": "una lente d'ingrandimento incrinata", "prezzo": 6,
             "descrizione": "Funziona ancora, se la si tiene con l'angolazione giusta."},
            {"chiave": "portachiavi", "nome": "un portachiavi con un ciondolo strano", "prezzo": 3,
             "descrizione": "Garrick non ricorda da dove venga, ne' cosa apra la chiave."},
        ],
    ),
    (
        "building_jamisons_hunting",
        "Jamison",
        "Un uomo silenzioso vestito di tela cerata, che osserva i "
        "clienti con l'attenzione di chi e' abituato a studiare le "
        "prede prima di sparare.",
        [
            {"chiave": "trappola", "nome": "una trappola da caccia", "prezzo": 12,
             "descrizione": "Una trappola d'acciaio, dai denti affilati."},
            {"chiave": "richiamo", "nome": "un richiamo per uccelli", "prezzo": 5,
             "descrizione": "Un fischietto di legno intagliato."},
            {"chiave": "cartucce", "nome": "una scatola di cartucce da caccia", "prezzo": 9,
             "descrizione": "Cartucce standard per fucile da caccia."},
            {"chiave": "borraccia", "nome": "una borraccia di metallo", "prezzo": 4,
             "descrizione": "Una borraccia robusta, con la cinghia di cuoio."},
            {"chiave": "mantella", "nome": "una mantella mimetica", "prezzo": 14,
             "descrizione": "Una mantella verde-marrone, utile per non farsi notare nel bosco."},
            {"chiave": "coltellotasca", "nome": "un coltellino tascabile multiuso", "prezzo": 7,
             "descrizione": "Un coltellino pieghevole, con diverse lame e un cavatappi."},
            {"chiave": "stivali", "nome": "un paio di stivali da palude", "prezzo": 16,
             "descrizione": "Stivali alti, impermeabili fino al ginocchio."},
        ],
    ),
    (
        "building_janson_hardware",
        "Janson",
        "Un uomo pratico e diretto, che sa sempre dove trovare "
        "l'attrezzo giusto tra centinaia di cassetti etichettati a "
        "mano.",
        [
            {"chiave": "chiodi", "nome": "un sacchetto di chiodi", "prezzo": 2,
             "descrizione": "Chiodi di varie misure, in un sacchetto di tela."},
            {"chiave": "martello", "nome": "un martello da carpentiere", "prezzo": 8,
             "descrizione": "Un martello robusto dal manico in frassino. Non e' pensato "
                            "per combattere, ma in mancanza di meglio fa il suo.",
             "slot": "arma", "tipo_arma": "mace", "dado_min": 1, "dado_max": 5,
             "bonus_danno": 0, "livello": 1},
            {"chiave": "corda", "nome": "un rotolo di corda", "prezzo": 4,
             "descrizione": "Corda robusta, buona per ogni evenienza."},
            {"chiave": "cacciavite", "nome": "un cacciavite a taglio", "prezzo": 3,
             "descrizione": "Un cacciavite robusto, con l'impugnatura di legno."},
            {"chiave": "lanterna", "nome": "una lanterna a petrolio", "prezzo": 10,
             "descrizione": "Una lanterna affidabile, con il vetro protetto da una gabbia metallica.",
             "luce": True},
            {"chiave": "sega", "nome": "una sega a mano", "prezzo": 9,
             "descrizione": "Una sega con i denti ben affilati, pronta per il legno duro."},
            {"chiave": "vite", "nome": "una scatola di viti assortite", "prezzo": 2,
             "descrizione": "Viti di varie misure, ordinate per grandezza in scomparti separati."},
        ],
    ),
    (
        "building_wingham_shipwright",
        "Harold Wingham",
        "Un vecchio lupo di mare con le mani coperte di calli, che "
        "parla di navi come altri parlerebbero di vecchi amici.",
        [
            {"chiave": "bussola", "nome": "una bussola nautica", "prezzo": 25,
             "descrizione": "Una bussola di ottone, precisa e ben tarata."},
            {"chiave": "corda", "nome": "una cima da ormeggio", "prezzo": 7,
             "descrizione": "Una robusta cima catramata."},
            {"chiave": "modellino", "nome": "un modellino di nave", "prezzo": 18,
             "descrizione": "Un piccolo modellino intagliato a mano, dettagliatissimo."},
            {"chiave": "ancora", "nome": "una piccola ancora da imbarcazione", "prezzo": 20,
             "descrizione": "Un'ancora in miniatura, robusta abbastanza per una barca da pesca."},
            {"chiave": "cannocchiale", "nome": "un cannocchiale da capitano", "prezzo": 30,
             "descrizione": "Un cannocchiale d'ottone estensibile, con lenti ben pulite."},
            {"chiave": "remo", "nome": "un remo di frassino", "prezzo": 14,
             "descrizione": "Un remo lungo, con la pala rinforzata da una fascia di rame."},
            {"chiave": "salvagente", "nome": "un salvagente di sughero", "prezzo": 9,
             "descrizione": "Un anello galleggiante, rivestito di corda intrecciata."},
        ],
    ),
    (
        "building_heaples_toys",
        "Heaple",
        "Un uomo dal sorriso allegro, circondato da giocattoli di "
        "ogni tipo - anche se alcuni, in un angolo poco illuminato, "
        "non sembrano fatti per far ridere nessuno.",
        [
            {"chiave": "trenino", "nome": "un trenino a molla", "prezzo": 10,
             "descrizione": "Un trenino di latta, con una chiave per caricarlo."},
            {"chiave": "bambola", "nome": "una bambola di porcellana", "prezzo": 15,
             "descrizione": "Una bambola dagli occhi di vetro, forse un po' troppo realistici."},
            {"chiave": "palla", "nome": "una palla di gomma colorata", "prezzo": 2,
             "descrizione": "Una semplice palla, per giocare all'aperto."},
            {"chiave": "soldatini", "nome": "una scatola di soldatini di piombo", "prezzo": 8,
             "descrizione": "Piccoli soldatini dipinti a mano, schierati in ordine di battaglia."},
            {"chiave": "aquilone", "nome": "un aquilone di carta colorata", "prezzo": 6,
             "descrizione": "Un aquilone leggero, con una lunga coda di stoffa."},
            {"chiave": "yoyo", "nome": "uno yo-yo di legno dipinto", "prezzo": 2,
             "descrizione": "Uno yo-yo verniciato a righe, con lo spago un po' consumato."},
            {"chiave": "puzzle", "nome": "un puzzle di legno incompleto", "prezzo": 4,
             "descrizione": "Un puzzle raffigurante un veliero, a cui manca un pezzo (forse)."},
        ],
    ),
    (
        "building_margarets_curio",
        "Margaret",
        "Una donna dallo sguardo penetrante, che non vende mai nulla "
        "a chi fa troppe domande sulla provenienza dei suoi oggetti.",
        [
            {"chiave": "maschera", "nome": "una maschera tribale", "prezzo": 20,
             "descrizione": "Una maschera di legno scuro, dall'espressione inquietante."},
            {"chiave": "pietra", "nome": "una pietra levigata dal mare", "prezzo": 60,
             "descrizione": "Una pietra liscia, incisa con simboli consumati. Chi la porta "
                            "addosso giura di sentirsi piu' pronto ad affrontare cio' che "
                            "normalmente lo supererebbe.",
             "slot": "amuleto", "bonus_livello_equip": 5, "livello": 1},
            {"chiave": "libro", "nome": "un libro rilegato in modo insolito", "prezzo": 35,
             "descrizione": "Un libro la cui rilegatura e' meglio non osservare troppo da vicino."},
            {"chiave": "teschio", "nome": "un piccolo teschio di animale", "prezzo": 12,
             "descrizione": "Margaret assicura che sia di animale, ma non specifica quale."},
            {"chiave": "boccetta", "nome": "una boccetta di liquido scuro sigillata", "prezzo": 18,
             "descrizione": "Un liquido denso e opaco, che Margaret non ha mai voluto descrivere."},
            {"chiave": "statuetta", "nome": "una statuetta scolpita in una pietra ignota", "prezzo": 22,
             "descrizione": "Una figura accovacciata, dai contorni che sembrano sbagliati a guardarli a lungo."},
            {"chiave": "diario", "nome": "un diario con le ultime pagine strappate", "prezzo": 15,
             "descrizione": "Una calligrafia nervosa, che si interrompe a meta' di una frase."},
        ],
    ),
    (
        "building_marvins_tattoo",
        "Marvin",
        "Un uomo silenzioso, coperto lui stesso di tatuaggi che "
        "sembrano muoversi appena, se lo si guarda con la coda "
        "dell'occhio.",
        [
            {"chiave": "ancora", "nome": "un tatuaggio a forma di ancora", "prezzo": 15,
             "descrizione": "Un classico tatuaggio marinaresco."},
            {"chiave": "sirena", "nome": "un tatuaggio a forma di sirena", "prezzo": 18,
             "descrizione": "Una sirena disegnata con inchiostro blu scuro."},
            {"chiave": "simbolo", "nome": "un tatuaggio con un simbolo sconosciuto", "prezzo": 30,
             "descrizione": "Un simbolo che Marvin dice di aver visto 'in sogno'."},
            {"chiave": "rondine", "nome": "un tatuaggio a forma di rondine", "prezzo": 12,
             "descrizione": "Una piccola rondine, disegnata con inchiostro nero."},
            {"chiave": "inchiostro", "nome": "un flacone di inchiostro da tatuaggio", "prezzo": 8,
             "descrizione": "Inchiostro nero denso, in un flacone di vetro scuro."},
            {"chiave": "ago", "nome": "un ago da tatuaggio sterilizzato", "prezzo": 4,
             "descrizione": "Un ago sottile, ancora nella confezione sigillata."},
            {"chiave": "teschiotatoo", "nome": "un tatuaggio a forma di teschio sorridente", "prezzo": 20,
             "descrizione": "Un teschio stilizzato, con un ghigno che sembra seguirti con lo sguardo."},
        ],
    ),
    (
        "building_mchughs_antiques",
        "McHugh",
        "Un uomo anziano che si muove lentamente tra i suoi mobili "
        "d'epoca, come se ogni pezzo custodisse un ricordo che "
        "preferisce non condividere.",
        [
            {"chiave": "orologio", "nome": "un orologio da parete fermo", "prezzo": 20,
             "descrizione": "Un orologio antico, fermo a un'ora imprecisata."},
            {"chiave": "specchio", "nome": "uno specchio annerito dal tempo", "prezzo": 28,
             "descrizione": "Uno specchio la cui superficie riflette tutto con un leggero ritardo."},
            {"chiave": "baule", "nome": "un baule antico", "prezzo": 33,
             "descrizione": "Un baule di legno scuro, chiuso da una serratura arrugginita."},
            {"chiave": "candelabro", "nome": "un candelabro d'argento annerito", "prezzo": 26,
             "descrizione": "Un candelabro a tre bracci, che McHugh non pulisce mai del tutto.",
             "luce": True},
            {"chiave": "ritratto", "nome": "un ritratto a olio di uno sconosciuto", "prezzo": 24,
             "descrizione": "Un dipinto il cui soggetto nessuno e' mai riuscito a identificare."},
            {"chiave": "vaso", "nome": "un vaso di ceramica screpolata", "prezzo": 19,
             "descrizione": "Un vaso antico, con una crepa che corre lungo tutto il collo."},
            {"chiave": "portapenne", "nome": "un calamaio con portapenne d'ottone", "prezzo": 17,
             "descrizione": "Un calamaio secco da decenni, ma ancora elegante."},
        ],
    ),
    (
        "building_mcnally_motors",
        "McNally",
        "Un uomo energico in tuta da meccanico, che parla di motori "
        "con la stessa passione con cui altri parlerebbero d'amore.",
        [
            {"chiave": "automobile", "nome": "un'automobile usata ma affidabile", "prezzo": 400,
             "descrizione": "Un'automobile di seconda mano, revisionata di recente."},
            {"chiave": "clacson", "nome": "un clacson di ricambio", "prezzo": 6,
             "descrizione": "Un clacson a bulbo, dal suono acuto."},
            {"chiave": "benzina", "nome": "una tanica di benzina", "prezzo": 8,
             "descrizione": "Una tanica piena, pronta all'uso."},
            {"chiave": "manovella", "nome": "una manovella d'avviamento", "prezzo": 10,
             "descrizione": "Una manovella robusta, per avviare il motore a mano."},
            {"chiave": "candela", "nome": "una scatola di candele per motore", "prezzo": 5,
             "descrizione": "Candele di ricambio, confezionate in una piccola scatola di cartone."},
            {"chiave": "pneumatico", "nome": "un pneumatico di ricambio", "prezzo": 18,
             "descrizione": "Una gomma nuova, ancora odorosa di caucciu'."},
            {"chiave": "cric", "nome": "un cric da officina", "prezzo": 9,
             "descrizione": "Un sollevatore meccanico, un po' arrugginito ma funzionante."},
        ],
    ),
    (
        "building_peabody_pets",
        "il commesso di Peabody Pets",
        "Un giovane che passa piu' tempo a parlare con gli animali "
        "che con i clienti, il che forse spiega perche' gli animali "
        "sembrino cosi' affezionati a lui.",
        [
            {"chiave": "canarino", "nome": "un canarino in gabbia", "prezzo": 12,
             "descrizione": "Un canarino giallo vivace, dal canto instancabile."},
            {"chiave": "pescerosso", "nome": "un pesce rosso in una boccia", "prezzo": 4,
             "descrizione": "Un pesce rosso che nuota in tondo, instancabile."},
            {"chiave": "mangime", "nome": "un sacchetto di mangime per uccelli", "prezzo": 2,
             "descrizione": "Semi misti per uccelli da voliera."},
            {"chiave": "guinzaglio", "nome": "un guinzaglio di cuoio", "prezzo": 5,
             "descrizione": "Un guinzaglio robusto, con moschettone d'ottone."},
            {"chiave": "cuccia", "nome": "una piccola cuccia imbottita", "prezzo": 9,
             "descrizione": "Una cuccia morbida, adatta a un cane di piccola taglia."},
            {"chiave": "gabbia", "nome": "una gabbia per piccoli animali", "prezzo": 11,
             "descrizione": "Una gabbia di filo metallico, con una porticina scorrevole."},
            {"chiave": "collare", "nome": "un collare con campanellino", "prezzo": 4,
             "descrizione": "Un collare regolabile, con un piccolo campanello tintinnante."},
        ],
    ),
    (
        "building_prescotts_gems",
        "Prescott",
        "Un uomo con una lente sempre a portata di mano, che esamina "
        "ogni pietra come se cercasse qualcosa di piu' del semplice "
        "valore commerciale.",
        [
            {"chiave": "rubino", "nome": "un piccolo rubino", "prezzo": 45,
             "descrizione": "Un rubino dal colore intenso, tagliato con precisione."},
            {"chiave": "zaffiro", "nome": "uno zaffiro blu", "prezzo": 50,
             "descrizione": "Uno zaffiro dalle sfumature profonde."},
            {"chiave": "quarzo", "nome": "un cristallo di quarzo grezzo", "prezzo": 8,
             "descrizione": "Un cristallo non lavorato, dalla forma irregolare."},
            {"chiave": "smeraldo", "nome": "un piccolo smeraldo", "prezzo": 48,
             "descrizione": "Uno smeraldo verde intenso, quasi privo di inclusioni."},
            {"chiave": "opale", "nome": "un opale iridescente", "prezzo": 38,
             "descrizione": "Un opale che cambia colore a seconda della luce."},
            {"chiave": "topazio", "nome": "un topazio dorato", "prezzo": 30,
             "descrizione": "Una pietra calda al tatto, dal colore del miele."},
            {"chiave": "ambra", "nome": "un frammento d'ambra con un insetto intrappolato", "prezzo": 25,
             "descrizione": "Prescott lo osserva sempre un attimo di troppo, prima di venderlo."},
        ],
    ),
    (
        "building_princes_jewelry",
        "Prince",
        "Un uomo elegante che illustra ogni gioiello con la voce "
        "suadente di chi vende sogni, non solo oro e pietre.",
        [
            {"chiave": "anello", "nome": "un anello d'oro", "prezzo": 35,
             "descrizione": "Un semplice anello d'oro, ben rifinito."},
            {"chiave": "collana", "nome": "una collana di perle", "prezzo": 60,
             "descrizione": "Una collana di perle bianche, perfettamente sferiche."},
            {"chiave": "bracciale", "nome": "un bracciale d'argento", "prezzo": 20,
             "descrizione": "Un bracciale sottile, decorato con piccole incisioni."},
            {"chiave": "orecchini", "nome": "un paio di orecchini d'oro", "prezzo": 28,
             "descrizione": "Piccoli orecchini a goccia, dal design elegante."},
            {"chiave": "spilla", "nome": "una spilla con pietra centrale", "prezzo": 32,
             "descrizione": "Una spilla raffinata, con una pietra colorata al centro."},
            {"chiave": "fermacravatta", "nome": "un fermacravatta d'oro", "prezzo": 18,
             "descrizione": "Un piccolo fermaglio, inciso con un motivo a spirale."},
            {"chiave": "orologiotasca", "nome": "un orologio da taschino placcato oro", "prezzo": 55,
             "descrizione": "Un orologio elegante, con una catena dello stesso metallo."},
        ],
    ),
    (
        "building_salters_antiques",
        "Salter",
        "Un uomo e suo figlio gestiscono insieme la bottega, "
        "scambiandosi occhiate ogni volta che qualcuno chiede degli "
        "orologi fermi alla parete.",
        [
            {"chiave": "lanterna", "nome": "una lanterna d'ottone antica", "prezzo": 14,
             "descrizione": "Una lanterna funzionante, dal vetro leggermente opaco.",
             "luce": True},
            {"chiave": "mappa", "nome": "una vecchia mappa nautica", "prezzo": 22,
             "descrizione": "Una mappa ingiallita, con alcune zone segnate a mano."},
            {"chiave": "moneta", "nome": "una moneta antica", "prezzo": 16,
             "descrizione": "Una moneta di provenienza incerta, dal metallo scurito."},
            {"chiave": "sestante", "nome": "un sestante d'ottone", "prezzo": 26,
             "descrizione": "Uno strumento di navigazione, ancora perfettamente funzionante."},
            {"chiave": "medaglione", "nome": "un medaglione inciso", "prezzo": 19,
             "descrizione": "Un medaglione con un'incisione ormai illeggibile."},
            {"chiave": "clessidra", "nome": "una clessidra di legno e vetro", "prezzo": 15,
             "descrizione": "La sabbia scorre un po' piu' lentamente di quanto dovrebbe."},
            {"chiave": "penna", "nome": "una penna d'oca con calamaio da viaggio", "prezzo": 8,
             "descrizione": "Una penna intagliata a mano, con il calamaio a incastro."},
        ],
    ),
    (
        "building_zimmerman_luggage",
        "Zimmerman",
        "Un uomo metodico, che sistema ogni valigia per dimensione "
        "con precisione quasi ossessiva.",
        [
            {"chiave": "baule", "nome": "un baule da viaggio", "prezzo": 28,
             "descrizione": "Un grande baule rinforzato agli angoli."},
            {"chiave": "valigetta", "nome": "una valigetta di cuoio", "prezzo": 16,
             "descrizione": "Una valigetta compatta, adatta a brevi viaggi."},
            {"chiave": "etichetta", "nome": "un set di etichette da bagaglio", "prezzo": 3,
             "descrizione": "Etichette di carta rigida, da legare alle maniglie."},
            {"chiave": "borsone", "nome": "un borsone da viaggio in tela cerata", "prezzo": 12,
             "descrizione": "Un borsone capiente, impermeabile e leggero."},
            {"chiave": "lucchettovaligia", "nome": "un piccolo lucchetto a combinazione", "prezzo": 4,
             "descrizione": "Un lucchetto compatto, per proteggere i bagagli durante il viaggio."},
            {"chiave": "cappelliera", "nome": "una cappelliera rigida", "prezzo": 14,
             "descrizione": "Una scatola cilindrica rivestita di cuoio, per proteggere i cappelli in viaggio."},
            {"chiave": "cinghia", "nome": "un set di cinghie da bagaglio", "prezzo": 6,
             "descrizione": "Cinghie robuste con fibbie, per rinforzare un baule gia' pieno."},
        ],
    ),
]


def popola_negozi_generici():
    """Crea (se non esistono gia') i mercanti dei 21 negozi generici rimanenti."""
    creati = []
    for tag_chiave, nome, descrizione, inventario in NEGOZI:
        stanze = search.search_tag(tag_chiave, category="arkham_building")
        if not stanze:
            continue
        stanza = stanze[0]
        esistente = [
            obj for obj in stanza.contents
            if obj.attributes.has("negozio") and obj.db.negozio
        ]
        if esistente:
            creati.append(esistente[0])
            continue
        creati.append(crea_mercante(stanza, nome, descrizione, inventario))
    return creati
