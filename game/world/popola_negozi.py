"""
Prima tornata di popolamento negozi (Fase F): un piccolo gruppo di 5
negozi (Arkham + Cairo) riceve per primo un mercante NPC con
inventario reale in vendita, a dimostrazione del sistema di
compravendita (world/economia.py, commands/cthulhu_shop.py).

Tornate successive (Fase F, quarta-nona; vedi world/popola_negozi_cibo.py,
_abbigliamento.py, _generici.py, _cairo.py, _zoog.py,
world/espandi_inventari_negozi.py) hanno completato TUTTI i restanti
negozi: 35/35 ad Arkham (cibo, abbigliamento, negozio), 6/7 a Cairo
(manca solo Anubis Hotel, escluso di proposito: e' un albergo, una
meccanica di alloggio diversa dalla compravendita - stessa scelta per
i 3 alberghi di Arkham; la meccanica di alloggio e' stata poi
costruita in Fase K, quattordicesima tornata: vedi
world/popola_alberghi.py, world/posizione.py, commands/cthulhu_inn.py
ALLOGGIA), 6/6 a Zoog Village. 47 mercanti in tutto (a cui si aggiunge Maro, il fabbro di
Ulthar, costruito a parte per la Forgiatura). Inventari ampliati fino
a 7 articoli per negozio (nessuna fonte originale verificabile sul
numero esatto di articoli per negozio: vedi nota in
world/economia.py). Confermato invece dal sito originale
(guides_equipment/guides_newbieschool) che nell'originale gli oggetti
avevano anche un uso meccanico reale (WEAR/WIELD, usura, riparazione):
per gli articoli di questi negozi che sono armi/armature vere (es.
Abdul a Cairo, Chorl a Zoog Village) i campi slot/tipo_arma/dado_min/
dado_max/bonus_danno/classe_armatura/livello sono gia' impostati e
funzionano con world/equipment.py - per il resto (cibo, ninnoli,
vestiti) restano solo economici/di ambientazione, coerentemente con la
loro natura.
"""

from evennia.utils import search

from world.economia import crea_mercante

# tag_categoria, tag_chiave -> (nome_mercante, descrizione, inventario)
NEGOZI_DA_POPOLARE = [
    (
        "arkham_building", "building_fish_market",
        "Sarah, la pescivendola",
        "Una donna robusta dalle mani callose, che pesa il pesce con "
        "gesti rapidi e sicuri, senza mai smettere di guardare i "
        "clienti negli occhi.",
        [
            {"chiave": "pesce", "nome": "un pesce fresco", "prezzo": 3,
             "descrizione": "Un pesce dagli occhi ancora lucidi, pescato questa mattina.",
             "cibo": 20},
            {"chiave": "aringa", "nome": "un'aringa affumicata", "prezzo": 2,
             "descrizione": "Un'aringa dall'odore intenso, avvolta in carta oleata.",
             "cibo": 15},
            {"chiave": "ostriche", "nome": "un cesto di ostriche", "prezzo": 8,
             "descrizione": "Un cesto di ostriche fresche, ancora chiuse.",
             "cibo": 20},
            {"chiave": "granchio", "nome": "un granchio vivo in un secchio", "prezzo": 5,
             "descrizione": "Un granchio che continua a muovere le chele, poco convinto della sua sorte.",
             "cibo": 20},
            {"chiave": "olio", "nome": "una boccetta di olio di fegato di merluzzo", "prezzo": 4,
             "descrizione": "Un tonico dal sapore terribile, che Sarah giura faccia miracoli."},
            {"chiave": "anguilla", "nome": "un'anguilla affumicata", "prezzo": 6,
             "descrizione": "Un'anguilla intera, affumicata con legno di melo.",
             "cibo": 20},
            {"chiave": "esca", "nome": "un secchiello di esche vive", "prezzo": 2,
             "descrizione": "Vermi e piccoli crostacei, buoni per chi vuole pescare da solo."},
        ],
    ),
    (
        "arkham_building", "building_prentices_books",
        "Prentice, il libraio",
        "Un uomo magro con gli occhiali spessi, che sistema i volumi "
        "con una cura quasi religiosa. Alcuni scaffali dietro il "
        "bancone restano sempre chiusi a chiave.",
        [
            {"chiave": "romanzo", "nome": "un romanzo economico", "prezzo": 4,
             "descrizione": "Un romanzo d'appendice dalla copertina consumata."},
            {"chiave": "manuale", "nome": "un manuale di storia locale", "prezzo": 12,
             "descrizione": "Una storia di Arkham scritta da uno storico dilettante."},
            {"chiave": "tomo", "nome": "un tomo dall'aria proibita", "prezzo": 50,
             "descrizione": "Un tomo rilegato in pelle scura, senza titolo sul dorso. "
                            "Prentice te lo vende solo dopo averti fissato a lungo negli occhi."},
            {"chiave": "mappa", "nome": "una mappa di Arkham e dintorni", "prezzo": 6,
             "descrizione": "Una mappa stampata di recente, con le vie della citta' vecchia segnate a inchiostro."},
            {"chiave": "rivista", "nome": "un numero arretrato di un pulp d'avventura", "prezzo": 2,
             "descrizione": "Una rivista dalla copertina sgargiante, pagine ingiallite."},
            {"chiave": "penna", "nome": "una penna stilografica", "prezzo": 8,
             "descrizione": "Una penna elegante, con il pennino leggermente consumato."},
            {"chiave": "segnalibro", "nome": "un segnalibro di seta ricamato", "prezzo": 1,
             "descrizione": "Un piccolo segnalibro, con una nappa dorata."},
        ],
    ),
    (
        "arkham_building", "building_strausbergs_tobacco",
        "Strausberg, il tabaccaio",
        "Un uomo dai baffi curati, che avvolge ogni acquisto con la "
        "stessa lentezza cerimoniosa, come se il tempo non contasse "
        "affatto nella sua bottega.",
        [
            {"chiave": "sigari", "nome": "una scatola di sigari pregiati", "prezzo": 15,
             "descrizione": "Sigari avvolti in foglie scure, dall'aroma intenso."},
            {"chiave": "pipa", "nome": "una pipa di radica", "prezzo": 20,
             "descrizione": "Una pipa intagliata a mano, dal fornello ben stagionato."},
            {"chiave": "tabacco", "nome": "un sacchetto di tabacco aromatico", "prezzo": 6,
             "descrizione": "Tabacco trinciato fine, dal profumo dolciastro."},
            {"chiave": "accendino", "nome": "un accendino a benzina", "prezzo": 5,
             "descrizione": "Un accendino d'ottone lucido, con lo scatto secco e affidabile."},
            {"chiave": "portasigari", "nome": "un portasigari in pelle", "prezzo": 9,
             "descrizione": "Un astuccio rigido, foderato di legno di cedro."},
            {"chiave": "fiammiferi", "nome": "una scatola di fiammiferi", "prezzo": 1,
             "descrizione": "Fiammiferi di legno, in una scatola scorrevole di cartone."},
            {"chiave": "portatabacco", "nome": "un portatabacco impermeabile", "prezzo": 4,
             "descrizione": "Una sacca di gomma, per tenere il tabacco al riparo dall'umidita'."},
        ],
    ),
    (
        "cairo_room", "cairo_shop_bakery",
        "Yusuf, il fornaio",
        "Un uomo dal sorriso facile, sempre coperto di farina fino ai "
        "gomiti. Il forno alle sue spalle non smette mai di lavorare.",
        [
            {"chiave": "pane", "nome": "una pagnotta di pane arabo", "prezzo": 2,
             "descrizione": "Pane appena sfornato, ancora caldo al tatto.",
             "cibo": 15},
            {"chiave": "dolce", "nome": "un dolce al miele", "prezzo": 3,
             "descrizione": "Un dolce appiccicoso, fradicio di miele e acqua di rose.",
             "cibo": 10},
            {"chiave": "baklava", "nome": "un vassoio di baklava", "prezzo": 10,
             "descrizione": "Strati sottilissimi di pasta, miele e pistacchi tritati.",
             "cibo": 15},
            {"chiave": "biscotti", "nome": "un sacchetto di biscotti al sesamo", "prezzo": 3,
             "descrizione": "Biscotti croccanti, ricoperti di semi di sesamo tostati.",
             "cibo": 10},
            {"chiave": "te", "nome": "un bricco di te' alla menta", "prezzo": 2,
             "descrizione": "Te' verde bollente, servito con foglie di menta fresca.",
             "bevanda": 10},
            {"chiave": "formaggio", "nome": "una forma di formaggio fresco di capra", "prezzo": 3,
             "descrizione": "Formaggio bianco e morbido, avvolto in un panno umido.",
             "cibo": 15},
            {"chiave": "olive", "nome": "un vasetto di olive in salamoia", "prezzo": 2,
             "descrizione": "Olive nere, conservate in una salamoia speziata.",
             "cibo": 10},
        ],
    ),
    (
        "cairo_room", "cairo_shop_cloth_merchant",
        "Fatima, la mercante di stoffe",
        "Una donna dagli occhi attenti, che misura ogni taglio di "
        "stoffa con un metro di legno consumato dall'uso.",
        [
            {"chiave": "lino", "nome": "un taglio di lino egiziano", "prezzo": 8,
             "descrizione": "Lino leggerissimo, ideale per il caldo del deserto."},
            {"chiave": "seta", "nome": "una sciarpa di seta colorata", "prezzo": 15,
             "descrizione": "Una sciarpa dai colori vivaci, morbidissima al tatto."},
            {"chiave": "tappeto", "nome": "un piccolo tappeto tessuto a mano", "prezzo": 40,
             "descrizione": "Un tappeto con motivi geometrici intricati, tessuto a mano."},
            {"chiave": "cotone", "nome": "un rotolo di cotone grezzo", "prezzo": 6,
             "descrizione": "Cotone semplice, robusto, adatto a ogni uso quotidiano."},
            {"chiave": "turbante", "nome": "un turbante di lino bianco", "prezzo": 10,
             "descrizione": "Un copricapo avvolto con cura, adatto a proteggersi dal sole."},
            {"chiave": "veloda", "nome": "un velo da testa ricamato", "prezzo": 12,
             "descrizione": "Un velo leggero, orlato con fili dorati."},
            {"chiave": "bottoni", "nome": "una scatola di bottoni di madreperla", "prezzo": 4,
             "descrizione": "Piccoli bottoni iridescenti, tagliati da conchiglie del Mar Rosso."},
        ],
    ),
]


def popola_negozi_demo():
    """
    Crea (se non esiste gia') un mercante con inventario in ognuno dei
    5 negozi scelti per questa prima tornata. Idempotente: controlla
    per ogni stanza se esiste gia' un mercante prima di crearne uno
    nuovo.
    """
    creati = []
    for tag_categoria, tag_chiave, nome, descrizione, inventario in NEGOZI_DA_POPOLARE:
        stanze = search.search_tag(tag_chiave, category=tag_categoria)
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
        mercante = crea_mercante(stanza, nome, descrizione, inventario)
        creati.append(mercante)
    return creati
