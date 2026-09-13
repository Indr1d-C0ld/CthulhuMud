"""
Popolamento negozi - categoria Abbigliamento (Fase F, seconda tornata):
i 6 negozi di abbigliamento di Arkham, tutti gia' costruiti in
world/rooms_arkham_edifici.py, ricevono ora un mercante con inventario
reale.

Inventari ampliati in tornate successive fino a 7 articoli per
negozio (solo economico/di ambientazione: vedi nota in
world/popola_negozi.py sul perche' non ci sono ancora slot
WEAR/WIELD).
"""

from evennia.utils import search

from world.economia import crea_mercante

NEGOZI = [
    (
        "building_bridal_boutique",
        "Madame Duval, la sarta da sposa",
        "Una donna elegante dai modi misurati, che valuta ogni cliente "
        "con occhio esperto prima ancora che apra bocca.",
        [
            {"chiave": "velo", "nome": "un velo da sposa ricamato", "prezzo": 25,
             "descrizione": "Un velo di pizzo finissimo, orlato a mano."},
            {"chiave": "abito", "nome": "un abito da sposa color avorio", "prezzo": 120,
             "descrizione": "Un abito elegante, cucito su misura per l'occasione piu' importante."},
            {"chiave": "guanti", "nome": "un paio di guanti di pizzo", "prezzo": 10,
             "descrizione": "Guanti lunghi fino al gomito, delicati al tatto."},
            {"chiave": "scarpette", "nome": "un paio di scarpette da sposa in raso", "prezzo": 18,
             "descrizione": "Scarpette bianche, con un piccolo tacco e una fibbia di perle."},
            {"chiave": "diadema", "nome": "un diadema di fiori d'arancio finti", "prezzo": 14,
             "descrizione": "Un piccolo diadema, da portare sotto il velo."},
            {"chiave": "giarrettiera", "nome": "una giarrettiera di raso azzurro", "prezzo": 6,
             "descrizione": "\"Qualcosa di blu\", come vuole la tradizione."},
            {"chiave": "bouquet", "nome": "un bouquet di fiori di seta", "prezzo": 9,
             "descrizione": "Un mazzo di fiori artificiali, che non appassira' mai."},
        ],
    ),
    (
        "building_giovanni_clothing",
        "Giovanni",
        "Un sarto energico dall'accento italiano marcato, che misura "
        "ogni cliente con un metro da sarto sempre al collo.",
        [
            {"chiave": "completo", "nome": "un completo di lana pettinata", "prezzo": 45,
             "descrizione": "Un completo elegante da uomo, taglio moderno."},
            {"chiave": "bombetta", "nome": "un cappello a bombetta", "prezzo": 12,
             "descrizione": "Un cappello rigido dalla tesa curva, molto in voga."},
            {"chiave": "cravatta", "nome": "una cravatta di seta", "prezzo": 8,
             "descrizione": "Una cravatta dai colori sobri, adatta a ogni occasione."},
            {"chiave": "camicia", "nome": "una camicia di cotone bianco", "prezzo": 10,
             "descrizione": "Una camicia inamidata, con i polsini rigidi."},
            {"chiave": "gilet", "nome": "un gilet a righe sottili", "prezzo": 16,
             "descrizione": "Un gilet elegante, da abbinare al completo."},
            {"chiave": "bretelle", "nome": "un paio di bretelle in pelle", "prezzo": 5,
             "descrizione": "Bretelle robuste, con fibbie regolabili in ottone."},
            {"chiave": "fazzoletto", "nome": "un fazzoletto da taschino", "prezzo": 3,
             "descrizione": "Un fazzoletto di seta, piegato con cura in tre punte."},
        ],
    ),
    (
        "building_hans_yodin",
        "Hans Yodin",
        "Un calzolaio dalle mani segnate dal lavoro, che giudica il "
        "carattere delle persone dalle loro scarpe, o cosi' dice lui.",
        [
            {"chiave": "scarpe", "nome": "un paio di scarpe in cuoio", "prezzo": 18,
             "descrizione": "Scarpe robuste, cucite a mano con cura maniacale."},
            {"chiave": "stivali", "nome": "un paio di stivali da lavoro", "prezzo": 22,
             "descrizione": "Stivali pesanti, pensati per durare anni."},
            {"chiave": "lucido", "nome": "un barattolo di lucido da scarpe", "prezzo": 2,
             "descrizione": "Lucido nero, dall'odore intenso di cera."},
            {"chiave": "lacci", "nome": "un paio di lacci di ricambio", "prezzo": 1,
             "descrizione": "Lacci di cuoio robusto, tagliati su misura."},
            {"chiave": "solette", "nome": "un paio di solette imbottite", "prezzo": 3,
             "descrizione": "Solette di feltro, per rendere le scarpe piu' comode."},
            {"chiave": "ghette", "nome": "un paio di ghette in tela", "prezzo": 7,
             "descrizione": "Ghette chiare, da abbottonare sopra la caviglia."},
            {"chiave": "pantofole", "nome": "un paio di pantofole di feltro", "prezzo": 6,
             "descrizione": "Pantofole morbide, comode per le sere fredde."},
        ],
    ),
    (
        "building_miss_ann",
        "Miss Ann",
        "Una donna dal sorriso professionale, che consiglia ogni "
        "cliente con un tono che non ammette repliche.",
        [
            {"chiave": "vestito", "nome": "un vestito da giorno", "prezzo": 20,
             "descrizione": "Un vestito pratico ma elegante, adatto a ogni occasione."},
            {"chiave": "cappellino", "nome": "un cappellino con veletta", "prezzo": 15,
             "descrizione": "Un piccolo cappello con una veletta scura, molto alla moda."},
            {"chiave": "ventaglio", "nome": "un ventaglio dipinto a mano", "prezzo": 9,
             "descrizione": "Un ventaglio di seta con motivi floreali."},
            {"chiave": "borsetta", "nome": "una borsetta di pelle scamosciata", "prezzo": 12,
             "descrizione": "Una piccola borsetta con chiusura a scatto d'ottone."},
            {"chiave": "calze", "nome": "un paio di calze di seta", "prezzo": 6,
             "descrizione": "Calze sottilissime, confezionate in una scatola di carta velina."},
            {"chiave": "scialle", "nome": "uno scialle di lana leggera", "prezzo": 14,
             "descrizione": "Uno scialle morbido, con le frange annodate a mano."},
            {"chiave": "spilla", "nome": "una spilla a forma di farfalla", "prezzo": 8,
             "descrizione": "Una spilla smaltata, dai colori vivaci."},
        ],
    ),
    (
        "building_carrington_milliner",
        "V. Carrington",
        "Un uomo dai modi affettati, che parla di cappelli come altri "
        "parlerebbero d'arte.",
        [
            {"chiave": "cilindro", "nome": "un cappello a cilindro", "prezzo": 30,
             "descrizione": "Un cilindro nero lucente, per le occasioni piu' formali."},
            {"chiave": "cappello", "nome": "un elegante cappello da donna", "prezzo": 24,
             "descrizione": "Un cappello a tesa larga, decorato con nastri."},
            {"chiave": "spilla", "nome": "una spilla per cappello", "prezzo": 6,
             "descrizione": "Una spilla d'argento a forma di libellula."},
            {"chiave": "coppola", "nome": "una coppola di tweed", "prezzo": 9,
             "descrizione": "Un berretto morbido, adatto alla vita di tutti i giorni."},
            {"chiave": "piuma", "nome": "una piuma decorativa", "prezzo": 4,
             "descrizione": "Una piuma colorata, da applicare su qualsiasi cappello."},
            {"chiave": "nastro", "nome": "un nastro di raso colorato", "prezzo": 3,
             "descrizione": "Un nastro lucido, da annodare intorno alla falda."},
            {"chiave": "velino", "nome": "un piccolo velo da cappello", "prezzo": 7,
             "descrizione": "Un velo corto, da appuntare sul bordo della tesa."},
        ],
    ),
    (
        "building_watkins_formal",
        "Watkins",
        "Un uomo compassato in abito scuro, che sistema gli smoking "
        "sugli appendini con precisione militare.",
        [
            {"chiave": "smoking", "nome": "uno smoking nero", "prezzo": 60,
             "descrizione": "Uno smoking impeccabile, per le serate piu' importanti."},
            {"chiave": "papillon", "nome": "un papillon bianco", "prezzo": 5,
             "descrizione": "Un papillon di seta bianca, perfettamente stirato."},
            {"chiave": "guantibianchi", "nome": "un paio di guanti bianchi", "prezzo": 7,
             "descrizione": "Guanti bianchi immacolati, da abbinare allo smoking."},
            {"chiave": "gemelli", "nome": "un paio di gemelli d'argento", "prezzo": 14,
             "descrizione": "Piccoli gemelli da polsino, incisi con iniziali non tue."},
            {"chiave": "sciarpa", "nome": "una sciarpa di seta bianca", "prezzo": 11,
             "descrizione": "Una sciarpa lunga, da portare sopra il cappotto da sera."},
            {"chiave": "bastone", "nome": "un bastone da passeggio con pomo d'argento", "prezzo": 25,
             "descrizione": "Un accessorio elegante, piu' che un vero sostegno."},
            {"chiave": "mantello", "nome": "un mantello da sera foderato di seta", "prezzo": 40,
             "descrizione": "Un mantello nero, caldo e teatrale."},
        ],
    ),
]


def popola_negozi_abbigliamento():
    """Crea (se non esistono gia') i mercanti dei 6 negozi di abbigliamento."""
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
