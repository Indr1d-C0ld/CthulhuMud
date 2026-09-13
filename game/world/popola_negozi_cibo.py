"""
Popolamento negozi - categoria Cibo e locali (Fase F, terza tornata): i
5 locali rimanenti di questa categoria ad Arkham (il Mercato del Pesce
era gia' stato popolato nella prima dimostrazione). Jazz Club, Sala da
Ballo e Pub sono trattati come locande/taverne: vendono da bere e da
mangiare, oltre a un ingresso simbolico per i due locali notturni.

Inventari ampliati in tornate successive fino a 7 articoli per
negozio (solo economico/di ambientazione: vedi nota in
world/popola_negozi.py). Fase G: gli articoli effettivamente
commestibili/bevibili hanno ricevuto "cibo"/"bevanda" (vedi
world/sopravvivenza.py) - oggetti puramente di ambientazione
(ingressi, sigari, dadi, candele...) restano senza.
"""

from evennia.utils import search

from world.economia import crea_mercante

NEGOZI = [
    (
        "building_barlows_butcher",
        "Barlow",
        "Un uomo massiccio dal grembiule macchiato, che maneggia la "
        "mannaia con la disinvoltura di chi lo fa da una vita.",
        [
            {"chiave": "manzo", "nome": "un taglio di carne di manzo", "prezzo": 6,
             "descrizione": "Un taglio di manzo fresco, ancora umido di sangue.",
             "cibo": 25},
            {"chiave": "salsicce", "nome": "una treccia di salsicce", "prezzo": 4,
             "descrizione": "Salsicce speziate, legate a treccia.",
             "cibo": 20},
            {"chiave": "prosciutto", "nome": "un prosciutto stagionato", "prezzo": 10,
             "descrizione": "Un intero prosciutto, stagionato a dovere.",
             "cibo": 25},
            {"chiave": "pollo", "nome": "un pollo intero spennato", "prezzo": 5,
             "descrizione": "Un pollo pronto per la pentola, ancora freddo di cella.",
             "cibo": 25},
            {"chiave": "lardo", "nome": "un blocco di lardo salato", "prezzo": 3,
             "descrizione": "Lardo bianco, avvolto in carta da macellaio.",
             "cibo": 15},
            {"chiave": "agnello", "nome": "un cosciotto d'agnello", "prezzo": 9,
             "descrizione": "Un cosciotto ben frollato, legato con spago da cucina.",
             "cibo": 25},
            {"chiave": "trippa", "nome": "un sacchetto di trippa", "prezzo": 3,
             "descrizione": "Trippa gia' pulita, pronta per essere cucinata a lungo.",
             "cibo": 20},
        ],
    ),
    (
        "building_black_dahlia",
        "Il barista del Black Dahlia",
        "Un uomo dall'aria complice, che serve i drink senza fare "
        "troppe domande su chi li ordina o perche'.",
        [
            {"chiave": "whiskey", "nome": "un bicchiere di whiskey di contrabbando", "prezzo": 8,
             "descrizione": "Whiskey chiaramente non tassato, ma di ottima qualita'.",
             "bevanda": 15},
            {"chiave": "sigaretta", "nome": "un pacchetto di sigarette", "prezzo": 3,
             "descrizione": "Sigarette dall'aroma forte, avvolte in carta sottile."},
            {"chiave": "ingresso", "nome": "un gettone d'ingresso al Black Dahlia", "prezzo": 5,
             "descrizione": "Un piccolo gettone di metallo, necessario per entrare nelle sere piu' esclusive."},
            {"chiave": "gin", "nome": "un bicchierino di gin scadente", "prezzo": 4,
             "descrizione": "Gin distillato in qualche retrobottega, meglio non chiedere dove.",
             "bevanda": 15},
            {"chiave": "noccioline", "nome": "una ciotola di noccioline salate", "prezzo": 1,
             "descrizione": "Noccioline tostate, offerte gratis solo ai clienti abituali.",
             "cibo": 10},
            {"chiave": "assenzio", "nome": "un bicchiere di assenzio verde", "prezzo": 10,
             "descrizione": "Un liquore torbido e forte, servito con un cucchiaino forato.",
             "bevanda": 15},
            {"chiave": "carte", "nome": "un mazzo di carte da gioco usato", "prezzo": 3,
             "descrizione": "Un mazzo consumato, buono per una partita a poker al bancone."},
        ],
    ),
    (
        "building_blue_ballroom",
        "Il maitre della Sala da Ballo Blu",
        "Un uomo in frac impeccabile, che valuta ogni ospite con un "
        "solo sguardo prima di decidere quanto essere cordiale.",
        [
            {"chiave": "champagne", "nome": "una coppa di champagne", "prezzo": 12,
             "descrizione": "Champagne freddo, servito in una coppa di cristallo.",
             "bevanda": 15},
            {"chiave": "biglietto", "nome": "un biglietto d'ingresso alla Sala Blu", "prezzo": 15,
             "descrizione": "Un cartoncino elegante che garantisce l'accesso alla serata."},
            {"chiave": "fiore", "nome": "un fiore all'occhiello", "prezzo": 4,
             "descrizione": "Un piccolo fiore bianco, perfetto per un'occasione elegante."},
            {"chiave": "sigaro", "nome": "un sigaro da fumatoio", "prezzo": 9,
             "descrizione": "Un sigaro fine, da fumare tra una danza e l'altra."},
            {"chiave": "programma", "nome": "un programma di sala stampato", "prezzo": 2,
             "descrizione": "Un elegante foglio con l'ordine delle danze della serata."},
            {"chiave": "cioccolatini", "nome": "una scatola di cioccolatini", "prezzo": 8,
             "descrizione": "Cioccolatini ripieni, in una scatola con fiocco di raso.",
             "cibo": 15},
            {"chiave": "guantielegan", "nome": "un paio di guanti da ballo", "prezzo": 6,
             "descrizione": "Guanti corti, in raso bianco immacolato."},
        ],
    ),
    (
        "building_cat_and_fiddle",
        "Il taverniere",
        "Un uomo robusto con un grembiule da lavoro, che asciuga "
        "boccali con uno straccio sempre un po' troppo sporco per "
        "essere davvero utile.",
        [
            {"chiave": "birra", "nome": "un boccale di birra scura", "prezzo": 3,
             "descrizione": "Birra scura e corposa, servita fino all'orlo.",
             "bevanda": 15},
            {"chiave": "stufato", "nome": "una scodella di stufato", "prezzo": 5,
             "descrizione": "Uno stufato denso, di carne e patate.",
             "cibo": 30},
            {"chiave": "sidro", "nome": "un boccale di sidro", "prezzo": 3,
             "descrizione": "Sidro di mele, dolce e frizzante.",
             "bevanda": 15},
            {"chiave": "pane", "nome": "una pagnotta di pane casereccio", "prezzo": 2,
             "descrizione": "Pane rustico, buono per fare la scarpetta nello stufato.",
             "cibo": 15},
            {"chiave": "formaggio", "nome": "un tagliere di formaggi locali", "prezzo": 6,
             "descrizione": "Un assortimento di formaggi stagionati, serviti con miele.",
             "cibo": 20},
            {"chiave": "torta", "nome": "una fetta di torta di mele", "prezzo": 4,
             "descrizione": "Una fetta generosa, ancora tiepida di forno.",
             "cibo": 15},
            {"chiave": "dadi", "nome": "un set di dadi da taverna", "prezzo": 3,
             "descrizione": "Dadi consumati, buoni per una partita mentre si aspetta lo stufato."},
        ],
    ),
    (
        "building_dovers_groceries",
        "Dover",
        "Un uomo anziano dai modi gentili, che conosce ogni cliente "
        "per nome e non manca mai di chiedere notizie della famiglia.",
        [
            {"chiave": "farina", "nome": "un sacco di farina", "prezzo": 4,
             "descrizione": "Farina bianca macinata di fresco."},
            {"chiave": "conserve", "nome": "un vasetto di conserve", "prezzo": 3,
             "descrizione": "Conserve di frutta, fatte in casa secondo una vecchia ricetta.",
             "cibo": 15},
            {"chiave": "uova", "nome": "una dozzina di uova", "prezzo": 2,
             "descrizione": "Uova fresche, ancora tiepide.",
             "cibo": 15},
            {"chiave": "latte", "nome": "una bottiglia di latte fresco", "prezzo": 2,
             "descrizione": "Latte appena consegnato, ancora freddo di ghiacciaia.",
             "bevanda": 15},
            {"chiave": "zucchero", "nome": "un sacchetto di zucchero", "prezzo": 3,
             "descrizione": "Zucchero bianco raffinato, in un sacchetto di carta."},
            {"chiave": "caffe", "nome": "un sacchetto di caffe' macinato", "prezzo": 4,
             "descrizione": "Caffe' tostato di fresco, dall'aroma intenso.",
             "bevanda": 10},
            {"chiave": "candela", "nome": "una candela di sego", "prezzo": 1,
             "descrizione": "Una candela semplice, buona per illuminare la dispensa.",
             "luce": True},
        ],
    ),
]


def popola_negozi_cibo():
    """Crea (se non esistono gia') i mercanti dei 5 locali di cibo/svago rimanenti."""
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
