"""
Terapeuti (Fase G, sesta tornata): confermato dalla fonte
("Most newbie areas have a therapist, and there are several others
scattered throughout the game" - helps/therapy.txt) che ogni area
newbie ha il proprio NPC per il recupero sanity. Qui: uno per ognuno
degli 8 hub newbie gia' costruiti (world/rooms_newbie.py), nella
stanza di RECALL (il luogo dove i personaggi tornano piu' spesso).
"""

from evennia.utils import create

from world.rooms_newbie import HUBS, stanza_per_ruolo

DESCRIZIONI_TERAPEUTA = {
    "arkham_miskatonic": ("il dottor Wilmarth", "Un uomo dallo sguardo gentile ma stanco, che "
                          "ascolta ogni paziente con la pazienza di chi ne ha sentite di ogni tipo."),
    "yhanthlei": ("un anziano cantore Profondo", "Una figura anfibia che intona litanie sommesse, "
                  "capaci di calmare le menti piu' turbate."),
    "migo_mothership": ("un chirurgo mentale Mi-Go", "Una creatura fungina che osserva i pensieri "
                         "altrui con strumenti che nessun umano saprebbe nominare."),
    "yuggoth_training": ("un istruttore Mi-Go", "Una creatura paziente, abituata a ricomporre menti "
                         "spezzate dal viaggio interstellare."),
    "ulthar_temple": ("un sacerdote del tempio", "Un uomo in veste bianca, che accarezza un gatto "
                      "addormentato mentre ascolta i tormenti dei visitatori."),
    "dylath_reformatory": ("un custode del riformatorio", "Un uomo severo ma non scortese, che ha "
                           "visto passare piu' menti spezzate di quante ne ricordi."),
    "zoog_village": ("un vecchio Zoog saggio", "Uno Zoog dal pelo grigio, che ascolta le paure "
                     "altrui con un'attenzione insolita per la sua specie."),
    "yithian_library": ("un bibliotecario Yithiano", "Un'entita' che scandisce pensieri come pagine, "
                        "cercando quelli fuori posto da rimettere in ordine."),
}


def popola_terapeuti():
    """Crea (se non esiste gia' un terapeuta) un NPC terapeuta nella
    stanza di RECALL di ognuno degli 8 hub newbie. Idempotente."""
    creati = []
    saltati = []
    for hub_id in HUBS:
        stanza = stanza_per_ruolo(hub_id, "recall")
        if not stanza:
            continue
        esistente = [obj for obj in stanza.contents if obj.db.terapeuta]
        if esistente:
            saltati.append((stanza.key, esistente[0].key))
            creati.append(esistente[0])
            continue
        nome, descrizione = DESCRIZIONI_TERAPEUTA.get(
            hub_id, ("un terapeuta", "Una figura tranquilla, pronta ad ascoltare.")
        )
        npc = create.create_object("typeclasses.npcs.NPC", key=nome, location=stanza)
        npc.db.desc = descrizione
        npc.db.ostile = False
        npc.db.is_practice_trainer = False
        npc.db.terapeuta = True
        creati.append(npc)
    return creati, saltati
