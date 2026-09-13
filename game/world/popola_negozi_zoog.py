"""
Popolamento negozi - Zoog Village (Fase F, sesta tornata): le 6
location commerciali gia' costruite in world/rooms_zoogvillage.py
ricevono un mercante Zoog con inventario a tema onirico/boschivo.

Inventari ampliati in tornate successive fino a 7 articoli per
negozio (solo economico/di ambientazione: vedi nota in
world/popola_negozi.py).
"""

from evennia.utils import search

from world.economia import crea_mercante

NEGOZI = [
    (
        "zv_klorl_shop",
        "Klorl",
        "Uno Zoog basso e paffuto, che maneggia funghi e radici "
        "luminescenti con una destrezza sorprendente per le sue "
        "piccole zampe.",
        [
            {"chiave": "fungo", "nome": "un fungo luminoso", "prezzo": 4,
             "descrizione": "Un fungo che emette un debole bagliore verdastro.",
             "cibo": 15},
            {"chiave": "radice", "nome": "una radice curativa", "prezzo": 7,
             "descrizione": "Una radice nodosa, masticata dagli Zoog per calmare i dolori.",
             "cibo": 10},
            {"chiave": "muschio", "nome": "un ciuffo di muschio secco", "prezzo": 2,
             "descrizione": "Muschio essiccato, usato dagli Zoog per accendere il fuoco."},
            {"chiave": "spora", "nome": "una boccetta di spore addormentate", "prezzo": 6,
             "descrizione": "Spore che, se agitate, emettono una nube soporifera."},
            {"chiave": "bacca", "nome": "un pugno di bacche fosforescenti", "prezzo": 3,
             "descrizione": "Bacche che brillano debolmente al buio, dal sapore amaro.",
             "cibo": 10},
            {"chiave": "polline", "nome": "un sacchetto di polline dorato", "prezzo": 5,
             "descrizione": "Polline finissimo, che Klorl usa per tingere i suoi funghi."},
            {"chiave": "corteccia", "nome": "una striscia di corteccia curativa", "prezzo": 4,
             "descrizione": "Corteccia amara, masticata per lenire mal di testa."},
        ],
    ),
    (
        "zv_thussis_shop",
        "Thussis",
        "Uno Zoog dagli occhi grandi e curiosi, che tiene la sua "
        "merce appesa a fili di ragnatela intrecciata sotto il "
        "soffitto del tronco cavo.",
        [
            {"chiave": "amuleto", "nome": "un amuleto di legno intagliato", "prezzo": 9,
             "descrizione": "Un piccolo amuleto, inciso con simboli zoog."},
            {"chiave": "corda", "nome": "una corda di ragnatela intrecciata", "prezzo": 5,
             "descrizione": "Sottile ma sorprendentemente resistente."},
            {"chiave": "lanterna", "nome": "una lanterna di lucciole", "prezzo": 12,
             "descrizione": "Un piccolo vaso pieno di lucciole addormentate, che si "
                            "risvegliano al buio.",
             "luce": True},
            {"chiave": "piuma", "nome": "una piuma di pipistrello notturno", "prezzo": 4,
             "descrizione": "Una piuma scura e sottile, usata dagli Zoog come ornamento."},
            {"chiave": "collana", "nome": "una collana di semi colorati", "prezzo": 6,
             "descrizione": "Una collana rustica, infilata con semi di ogni colore del bosco."},
            {"chiave": "borsellino", "nome": "un borsellino di pelliccia", "prezzo": 5,
             "descrizione": "Un piccolo borsellino, cucito con la pelliccia di un animale del bosco."},
            {"chiave": "bracciale", "nome": "un bracciale di rametti intrecciati", "prezzo": 4,
             "descrizione": "Un bracciale rustico, intrecciato con piccoli rametti flessibili."},
        ],
    ),
    (
        "zv_flaerr_shop",
        "Flaerr",
        "Uno Zoog anziano dalle zampe tremule, che ripara oggetti "
        "recuperati da sogni altrui naufragati nel bosco con una "
        "pazienza infinita.",
        [
            {"chiave": "utensile", "nome": "un utensile riparato alla bell'e meglio", "prezzo": 6,
             "descrizione": "Un attrezzo di provenienza incerta, rimesso a nuovo da Flaerr."},
            {"chiave": "cianfrusaglia", "nome": "una cianfrusaglia onirica", "prezzo": 3,
             "descrizione": "Un piccolo oggetto sfuggito a un sogno altrui, di uso ignoto."},
            {"chiave": "campanellino", "nome": "un campanellino d'ottone", "prezzo": 4,
             "descrizione": "Un piccolo campanello dal suono cristallino."},
            {"chiave": "chiave", "nome": "una chiave arrugginita senza serratura", "prezzo": 2,
             "descrizione": "Flaerr giura che prima o poi trovera' la porta giusta."},
            {"chiave": "specchietto", "nome": "uno specchietto incrinato", "prezzo": 5,
             "descrizione": "Uno specchietto che riflette le cose con un istante di ritardo."},
            {"chiave": "ingranaggio", "nome": "un piccolo ingranaggio solitario", "prezzo": 3,
             "descrizione": "Un ingranaggio di ottone, senza il resto del meccanismo."},
            {"chiave": "boccetta", "nome": "una boccetta vuota etichettata male", "prezzo": 2,
             "descrizione": "L'etichetta dice qualcosa, ma nessuno riesce piu' a leggerla."},
        ],
    ),
    (
        "zv_bakery_silaer",
        "Silaer",
        "Uno Zoog dalle zampe infarinate, che sforna dolci con un "
        "ritmo instancabile, canticchiando tra se' e se'.",
        [
            {"chiave": "panemiele", "nome": "un panetto al miele di fiori onirici", "prezzo": 4,
             "descrizione": "Un pane dolce e appiccicoso, dal sapore che cambia leggermente "
                            "a ogni morso.",
             "cibo": 15},
            {"chiave": "dolcefungino", "nome": "un dolce a base di funghi zuccherati", "prezzo": 5,
             "descrizione": "Un dolce insolito, ma sorprendentemente gustoso.",
             "cibo": 15},
            {"chiave": "torta", "nome": "una piccola torta di bacche del bosco", "prezzo": 6,
             "descrizione": "Una torta soffice, ricoperta di bacche scure.",
             "cibo": 15},
            {"chiave": "biscottozoog", "nome": "un biscotto a forma di ghianda", "prezzo": 2,
             "descrizione": "Un biscotto croccante, cotto nella forma tipica zoog.",
             "cibo": 10},
            {"chiave": "sciroppo", "nome": "una fiala di sciroppo di resina dolce", "prezzo": 7,
             "descrizione": "Uno sciroppo denso e ambrato, estratto dagli alberi piu' antichi del bosco.",
             "bevanda": 10},
            {"chiave": "marmellata", "nome": "un vasetto di marmellata di bacche notturne", "prezzo": 5,
             "descrizione": "Una marmellata scura, dal sapore che cambia a seconda dell'ora in cui la assaggi.",
             "cibo": 15},
            {"chiave": "pandizenzero", "nome": "un pan di zenzero a forma di Zoog", "prezzo": 3,
             "descrizione": "Un biscotto speziato, decorato con occhietti di glassa."},
        ],
    ),
    (
        "zv_blacksmith_chorl",
        "Chorl",
        "Uno Zoog muscoloso (per gli standard zoog), che batte il "
        "metallo con una forza sorprendente, il volto arrossato dal "
        "calore della forgia.",
        [
            {"chiave": "lama", "nome": "una lama sottile come un ago", "prezzo": 15,
             "descrizione": "Una lama minuscola ma affilatissima, forgiata su misura zoog. "
                            "Funziona anche per mani non zoog, con un po' di destrezza.",
             "slot": "arma", "tipo_arma": "dagger", "dado_min": 1, "dado_max": 3,
             "bonus_danno": 0, "livello": 1},
            {"chiave": "punta", "nome": "una punta di freccia in metallo", "prezzo": 3,
             "descrizione": "Una punta di freccia ben bilanciata."},
            {"chiave": "chiodo", "nome": "un chiodo di ferro battuto", "prezzo": 1,
             "descrizione": "Un semplice chiodo, forgiato a mano."},
            {"chiave": "martelletto", "nome": "un piccolo martello da forgia", "prezzo": 8,
             "descrizione": "Un martello in miniatura, adatto alle mani zoog."},
            {"chiave": "catenella", "nome": "una catenella di ferro sottile", "prezzo": 5,
             "descrizione": "Una catena leggera, buona per appendere piccoli oggetti."},
            {"chiave": "tenaglia", "nome": "una piccola tenaglia da forgia", "prezzo": 6,
             "descrizione": "Una tenaglia in miniatura, con le punte annerite dal fuoco."},
            {"chiave": "fibbia", "nome": "una fibbia di metallo battuto", "prezzo": 3,
             "descrizione": "Una fibbia semplice, forgiata a colpi regolari."},
        ],
    ),
    (
        "zv_gem_cavern",
        "un vecchio Zoog custode",
        "Uno Zoog dal pelo grigio, che sorveglia i cristalli della "
        "caverna con aria annoiata, come se il loro luccichio avesse "
        "smesso di stupirlo secoli fa.",
        [
            {"chiave": "cristallo", "nome": "un cristallo onirico grezzo", "prezzo": 10,
             "descrizione": "Un cristallo che cattura la luce in modo innaturale."},
            {"chiave": "gemma", "nome": "una piccola gemma scintillante", "prezzo": 14,
             "descrizione": "Una gemma dai riflessi cangianti."},
            {"chiave": "scheggia", "nome": "una scheggia luminosa", "prezzo": 6,
             "descrizione": "Una scheggia di cristallo che emette una debole luce propria."},
            {"chiave": "geode", "nome": "un geode spaccato a meta'", "prezzo": 18,
             "descrizione": "Un geode che rivela all'interno una cavita' di cristalli viola."},
            {"chiave": "polvere", "nome": "una fiala di polvere di cristallo", "prezzo": 8,
             "descrizione": "Polvere finissima, che scintilla se agitata controluce."},
            {"chiave": "ametista", "nome": "un ciondolo di ametista grezza", "prezzo": 16,
             "descrizione": "Un cristallo viola, appeso a un filo di cuoio."},
            {"chiave": "roccia", "nome": "un frammento di roccia lunare", "prezzo": 20,
             "descrizione": "Almeno cosi' la chiama il vecchio custode: nessuno ha mai controllato."},
        ],
    ),
]


def popola_negozi_zoog():
    """Crea (se non esistono gia') i mercanti delle 6 location commerciali di Zoog Village."""
    creati = []
    for tag_chiave, nome, descrizione, inventario in NEGOZI:
        stanze = search.search_tag(tag_chiave, category="zoogvillage_room")
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
