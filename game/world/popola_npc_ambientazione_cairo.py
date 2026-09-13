"""
Popolamento NPC di ambientazione - Cairo (Fase F, undicesima tornata):
le 12 aree di Cairo che non sono negozi (vedi world/rooms_cairo.py,
ROOMS) erano rimaste scenografia vuota - stesso problema gia' risolto
per Arkham con world/popola_npc_ambientazione.py, qui replicato.

Anubis Hotel resta senza NPC (albergo self-service, come gli hotel di
Arkham) e cosi' "In Mare Aperto" (stanza di solo transito verso
Arkham): nessuna delle due e' un'area "abitata".
"""

from evennia.utils import create

# (tag_chiave, nome, descrizione)
NPC_DA_CREARE = [
    ("cairo_bazaar", "un incantatore di serpenti",
     "Un uomo seduto a gambe incrociate, che suona un piffero stonato "
     "davanti a un cesto chiuso, con aria piu' annoiata che minacciosa."),
    ("cairo_docks", "un facchino",
     "Un uomo dalla schiena curva, che carica casse su piccole spalle "
     "scalze senza mai fermarsi a riprendere fiato."),
    ("cairo_city_gates", "una guardia di frontiera",
     "Un uomo in uniforme sbiadita dal sole, che controlla i "
     "documenti dei viaggiatori con un'attenzione ormai puramente "
     "meccanica."),
    ("cairo_pyramids", "una guida turistica",
     "Un uomo instancabile, che ripete la stessa spiegazione sulle "
     "piramidi a ogni gruppo di visitatori, con un entusiasmo sempre "
     "identico e sempre un po' esagerato."),
    ("cairo_sphinx", "uno studioso distratto",
     "Un uomo con taccuino e matita, che misura ostinatamente gli "
     "angoli del volto della Sfinge, come se cercasse una risposta "
     "che il monumento non da' volentieri."),
    ("cairo_administrative_area", "un impiegato coloniale",
     "Un uomo in giacca chiara sudata, che timbra documenti dietro "
     "una scrivania all'ombra di un ventilatore che gira troppo "
     "piano per essere utile."),
    ("cairo_british_citadel", "una sentinella britannica",
     "Un soldato immobile sull'attenti, che osserva ogni passante con "
     "un'espressione che non lascia spazio a domande."),
    ("cairo_residential_ne", "una donna che innaffia i gelsomini",
     "Una donna anziana, che si prende cura delle piante del cortile "
     "con una cura che sembra riservare solo a loro."),
    ("cairo_residential_se", "un funzionario in pensione",
     "Un uomo che siede all'ombra del proprio portico, a osservare la "
     "strada con l'aria di chi ha visto sfilare abbastanza vite per "
     "un'intera carriera."),
    ("cairo_slums", "un borsaiolo",
     "Un ragazzo magro dagli occhi svegli, che si tiene sempre a "
     "distanza di sicurezza, valutando ogni passante con interesse "
     "professionale."),
    ("cairo_causeway", "un cammelliere",
     "Un uomo dal volto scurito dal sole, che conduce un cammello "
     "carico verso sud, incurante del caldo."),
    ("cairo_great_mosque", "il muezzin",
     "Un uomo dalla voce profonda, che riposa all'ombra del minareto "
     "in attesa della prossima chiamata alla preghiera."),
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


def popola_npc_ambientazione_cairo():
    """Crea (se non esiste gia' un NPC nella stanza) un NPC di
    ambientazione per ognuna delle 12 aree non commerciali di Cairo."""
    from evennia.utils import search

    creati = []
    saltati = []
    for tag_chiave, nome, descrizione in NPC_DA_CREARE:
        stanze = search.search_tag(tag_chiave, category="cairo_room")
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
