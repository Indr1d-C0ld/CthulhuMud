"""
Popolamento negozi - Cairo, resto del Bazaar (Fase F, quinta tornata):
i 4 negozi rimanenti tra i 7 elencati nella guida ufficiale (Bakery e
Cloth Merchant erano gia' stati popolati nella prima dimostrazione).
Anubis Hotel resta senza mercante: e' un albergo (meccanica di
alloggio, non di compravendita), coerente con la stessa scelta gia'
fatta per gli alberghi di Arkham. La meccanica di alloggio (e un NPC
albergatore, non un mercante) e' stata costruita in Fase K,
quattordicesima tornata: vedi world/popola_alberghi.py,
world/posizione.py, commands/cthulhu_inn.py ALLOGGIA.

Inventari ampliati in tornate successive fino a 7 articoli per
negozio (solo economico/di ambientazione: vedi nota in
world/popola_negozi.py).
"""

from evennia.utils import search

from world.economia import crea_mercante

NEGOZI = [
    (
        "cairo_shop_farmers_stall",
        "un contadino",
        "Un uomo dalla pelle scurita dal sole, che grida i prezzi "
        "della sua merce con voce roca, contrattando volentieri con "
        "chiunque si fermi abbastanza a lungo.",
        [
            {"chiave": "datteri", "nome": "un cesto di datteri", "prezzo": 3,
             "descrizione": "Datteri dolcissimi, appena raccolti.",
             "cibo": 15},
            {"chiave": "melograno", "nome": "un melograno maturo", "prezzo": 2,
             "descrizione": "Un melograno dai chicchi rosso rubino.",
             "cibo": 15},
            {"chiave": "lenticchie", "nome": "un sacchetto di lenticchie", "prezzo": 2,
             "descrizione": "Lenticchie secche, ottime per una zuppa.",
             "cibo": 20},
            {"chiave": "fichi", "nome": "un cesto di fichi secchi", "prezzo": 3,
             "descrizione": "Fichi essiccati al sole, appiccicosi e dolcissimi.",
             "cibo": 15},
            {"chiave": "spezie", "nome": "un sacchetto di spezie miste", "prezzo": 5,
             "descrizione": "Un misto di cumino, coriandolo e cannella, dall'odore intenso."},
            {"chiave": "limoni", "nome": "una rete di limoni", "prezzo": 2,
             "descrizione": "Limoni piccoli e profumati, dalla buccia sottile.",
             "cibo": 10},
            {"chiave": "ceci", "nome": "un sacchetto di ceci secchi", "prezzo": 2,
             "descrizione": "Ceci di ottima qualita', perfetti per l'hummus.",
             "cibo": 20},
        ],
    ),
    (
        "cairo_shop_abduls_armoury",
        "Abdul",
        "Un uomo robusto con i baffi ben curati, che rifornisce "
        "soldati e viaggiatori senza fare troppe domande su chi sia "
        "davvero il cliente.",
        [
            {"chiave": "sciabola", "nome": "una sciabola curva", "prezzo": 35,
             "descrizione": "Una sciabola dalla lama ricurva, affilata di recente.",
             "slot": "arma", "tipo_arma": "sword", "dado_min": 2, "dado_max": 6,
             "bonus_danno": 1, "livello": 5},
            {"chiave": "pugnale", "nome": "un pugnale cerimoniale", "prezzo": 18,
             "descrizione": "Un pugnale dall'elsa decorata, piu' bello che pratico.",
             "slot": "arma", "tipo_arma": "dagger", "dado_min": 1, "dado_max": 4,
             "bonus_danno": 0, "livello": 1},
            {"chiave": "scudo", "nome": "un piccolo scudo di cuoio", "prezzo": 20,
             "descrizione": "Uno scudo leggero, rinforzato con borchie di ottone.",
             "slot": "scudo", "classe_armatura": 3, "livello": 1},
            {"chiave": "lancia", "nome": "una lancia corta da caccia", "prezzo": 15,
             "descrizione": "Una lancia leggera, con la punta di ferro ben forgiata.",
             "slot": "arma", "tipo_arma": "spear", "dado_min": 2, "dado_max": 5,
             "bonus_danno": 0, "livello": 3},
            {"chiave": "corazza", "nome": "una corazza di cuoio borchiato", "prezzo": 28,
             "descrizione": "Una protezione leggera, adatta a chi viaggia nel deserto.",
             "slot": "corpo", "classe_armatura": 5, "livello": 3},
            {"chiave": "elmo", "nome": "un elmo di cuoio rinforzato", "prezzo": 22,
             "descrizione": "Un elmo semplice, con una striscia di metallo lungo la fronte.",
             "slot": "testa", "classe_armatura": 2, "livello": 1},
            {"chiave": "faretra", "nome": "una faretra con frecce", "prezzo": 16,
             "descrizione": "Una faretra di cuoio, piena di frecce dalle piume colorate."},
        ],
    ),
    (
        "cairo_shop_winemakers_shop",
        "il vinaio",
        "Un uomo dal naso rubizzo, che decanta le qualita' del suo "
        "vino con un entusiasmo forse un po' eccessivo per un "
        "prodotto locale.",
        [
            {"chiave": "vino", "nome": "un'anfora di vino egiziano", "prezzo": 10,
             "descrizione": "Vino locale, dal sapore forte e un po' aspro.",
             "bevanda": 15},
            {"chiave": "birraegizia", "nome": "una brocca di birra d'orzo", "prezzo": 4,
             "descrizione": "Una birra scura, prodotta secondo un'antica ricetta.",
             "bevanda": 15},
            {"chiave": "coppa", "nome": "una coppa decorata", "prezzo": 6,
             "descrizione": "Una coppa di ceramica dipinta a mano."},
            {"chiave": "brandy", "nome": "una bottiglia di brandy di datteri", "prezzo": 14,
             "descrizione": "Un distillato dolce e forte, ottenuto dai datteri fermentati.",
             "bevanda": 15},
            {"chiave": "otre", "nome": "un otre di pelle per il vino", "prezzo": 5,
             "descrizione": "Un otre robusto, utile per portare il vino durante i viaggi."},
            {"chiave": "narghile", "nome": "un narghile' d'ottone", "prezzo": 18,
             "descrizione": "Una pipa ad acqua elaborata, con tubi di cuoio intrecciato."},
            {"chiave": "melassa", "nome": "una brocca di melassa di canna", "prezzo": 4,
             "descrizione": "Uno sciroppo scuro e denso, usato per dolcificare il te'.",
             "cibo": 10},
        ],
    ),
    (
        "cairo_shop_falcon_armory",
        "il mercante d'armi europee",
        "Un uomo con un accento straniero marcato, che tratta le sue "
        "armi da fuoco con un rispetto quasi reverenziale.",
        [
            {"chiave": "pistola", "nome": "una pistola semi-automatica", "prezzo": 50,
             "descrizione": "Un'arma moderna, importata dall'Europa a caro prezzo.",
             "slot": "arma", "tipo_arma": "handgun", "dado_min": 3, "dado_max": 8,
             "bonus_danno": 1, "livello": 9},
            {"chiave": "fucile", "nome": "un fucile da guerra", "prezzo": 70,
             "descrizione": "Un fucile militare, di provenienza non del tutto chiara.",
             "slot": "arma", "tipo_arma": "gun", "dado_min": 4, "dado_max": 10,
             "bonus_danno": 2, "livello": 12},
            {"chiave": "proiettili", "nome": "una scatola di proiettili", "prezzo": 12,
             "descrizione": "Munizioni moderne, di fabbricazione europea."},
            {"chiave": "fondina", "nome": "una fondina di cuoio", "prezzo": 9,
             "descrizione": "Una fondina robusta, cucita per adattarsi a diverse pistole."},
            {"chiave": "binocolo", "nome": "un binocolo da campo", "prezzo": 22,
             "descrizione": "Un binocolo ottico di precisione, con lenti tedesche."},
            {"chiave": "baionetta", "nome": "una baionetta da fucile", "prezzo": 17,
             "descrizione": "Una lama lunga e sottile, pensata per essere innestata su un fucile.",
             "slot": "arma", "tipo_arma": "dagger", "dado_min": 2, "dado_max": 5,
             "bonus_danno": 0, "livello": 7},
            {"chiave": "cartuccera", "nome": "una cartucciera da cintura", "prezzo": 11,
             "descrizione": "Una cintura con alloggi per munizioni, in cuoio consumato."},
        ],
    ),
]


def popola_negozi_cairo():
    """Crea (se non esistono gia') i mercanti dei 4 negozi rimanenti del Bazaar."""
    creati = []
    for tag_chiave, nome, descrizione, inventario in NEGOZI:
        stanze = search.search_tag(tag_chiave, category="cairo_room")
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
