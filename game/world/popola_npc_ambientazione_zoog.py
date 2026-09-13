"""
Popolamento NPC di ambientazione - Zoog Village (Fase F, undicesima
tornata): le 12 location non commerciali di Zoog Village che avevano
gia' un abitante NOMINATO nella propria descrizione (vedi
world/rooms_zoogvillage.py, ROOMS) restano scenografia vuota finche'
quell'abitante non viene davvero creato. Qui si chiude il cerchio:
Slorril, Jhilorin, Hok, Merith, Durnith e Goryth prendono vita, insieme
a qualche Zoog senza nome per le aree comuni (cancello, stagni, Albero
delle Anime, Alto Tempio, Camera degli Anziani).

"La Casa Vuota" (empty_house) resta deliberatamente priva di NPC: la
sua stessa descrizione ("nessuno Zoog ammette volentieri di sapere
dove porti") la vuole disabitata e leggermente inquietante, non
scenografia dimenticata.
"""

from evennia.utils import create

# (tag_chiave, nome, descrizione)
NPC_DA_CREARE = [
    ("zv_north_gate", "un giovane Zoog di guardia",
     "Uno Zoog che dondola appeso a testa in giu' da una radice "
     "dell'arco, tenendo d'occhio chiunque entri o esca dal villaggio "
     "con piu' curiosita' che diligenza."),
    ("zv_in_the_pond", "uno Zoog che sguazza nello stagno",
     "Uno Zoog fradicio fino alle orecchie, che rincorre le bolle che "
     "salgono dal fondo melmoso senza mai chiedersi da dove vengano."),
    ("zv_cozy_pond", "un vecchio Zoog assopito",
     "Uno Zoog rannicchiato tra le felci, che russa piano: si dice "
     "che qui racconti le storie piu' incredibili di tutto il "
     "villaggio, quando e' sveglio."),
    ("zv_tree_of_souls", "un giovane Zoog in silenziosa venerazione",
     "Uno Zoog che sistema con cura una piccola offerta ai piedi "
     "dell'albero, sussurrando un nome che non ripete a nessuno."),
    ("zv_high_temple", "un sacerdote Zoog",
     "Uno Zoog avvolto in una veste di muschio intrecciato, che si "
     "muove nella penombra del tempio con una solennita' insolita "
     "per la sua specie."),
    ("zv_chamber_elders", "un anziano Zoog",
     "Uno Zoog dal pelo brizzolato, che ride di una battuta che "
     "nessun altro nella camera sembra aver sentito."),
    ("zv_slorril_home", "Slorril",
     "Uno Zoog che riordina per l'ennesima volta la propria "
     "collezione di sassolini colorati, con un criterio comprensibile "
     "solo a lui."),
    ("zv_jhilorin_burrow", "Jhilorin",
     "Uno Zoog minuto, che si muove carponi nella propria tana bassa "
     "con la disinvoltura di chi ci e' nato dentro."),
    ("zv_in_the_fungus", "Hok",
     "Uno Zoog dall'aria distratta, che parla sottovoce ai funghi "
     "giganti come se ogni tanto, in effetti, rispondessero."),
    ("zv_deposito", "Merith",
     "Uno Zoog meticoloso, che tiene il conto di ogni chicco messo da "
     "parte con un'attenzione che nessun altro Zoog condivide."),
    ("zv_durnith_log", "Durnith",
     "Uno Zoog che intreccia nuovo muschio luminoso intorno "
     "all'ingresso del proprio tronco, soddisfatto del risultato."),
    ("zv_goryth", "Goryth",
     "Uno Zoog piu' silenzioso della media, che osserva il bosco "
     "senza mai spiegare cosa stia cercando."),
]


def _crea_npc(location, nome, descrizione):
    npc = create.create_object(
        "typeclasses.npcs.NPC",
        key=nome,
        location=location,
    )
    npc.db.desc = descrizione
    npc.db.ostile = False
    npc.db.is_practice_trainer = False
    return npc


def popola_npc_ambientazione_zoog():
    """Crea (se non esiste gia' un NPC nella stanza) un NPC di
    ambientazione per ognuna delle 12 location non commerciali di Zoog
    Village (escluso empty_house, deliberatamente disabitato)."""
    from evennia.utils import search

    creati = []
    saltati = []
    for tag_chiave, nome, descrizione in NPC_DA_CREARE:
        stanze = search.search_tag(tag_chiave, category="zoogvillage_room")
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
        creati.append(_crea_npc(stanza, nome, descrizione))
    return creati, saltati
