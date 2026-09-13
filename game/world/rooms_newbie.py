"""
Stanze di partenza per le professioni newbie (RECALL / RESPAWN / MORGUE).

Placeholder minimi: non sono ancora l'area completa (quella arrivera' in
una fase successiva di building, fedele ai 73 edifici di Arkham catalogati
nel Dossier Miskatonic), ma bastano a rendere la creazione del personaggio
completamente funzionante, con le tre stanze previste dal design originale.

Ogni stanza viene taggata con category="start_room" e uno dei tre ruoli
("recall", "respawn", "morgue") cosi' da poterla ritrovare da codice senza
dipendere dal suo dbref. Quando RECALL e RESPAWN coincidono (come
nell'originale, per diversi hub), viene creata una sola stanza con
entrambi i tag.
"""

from evennia.utils import create, search

# hub -> {ruolo: (nome, descrizione)}
# se recall e respawn condividono la stessa voce di dizionario (stesso nome),
# viene creata una sola stanza con entrambi i tag.
HUBS = {
    "arkham_miskatonic": {
        "recall": (
            "Universita' Miskatonic - Sala Comune",
            "Poltrone di pelle consunta e scaffali di libri di testo riempiono "
            "questa sala comune per studenti, nel cuore della Miskatonic "
            "University di Arkham. E' qui che molte carriere accademiche, e "
            "non solo, hanno inizio.",
        ),
        "respawn": (
            "Universita' Miskatonic - Infermeria",
            "L'infermeria del campus, con letti ordinati e un forte odore di "
            "disinfettante. Chi ci si risveglia sa di essere sopravvissuto "
            "a qualcosa di brutto.",
        ),
        "morgue": (
            "Mortis & Carver, Impresa di Pompe Funebri",
            "Un'elegante impresa di pompe funebri nel centro di Arkham, dove "
            "finiscono - insieme a tutti i loro averi - i corpi di chi non "
            "e' stato altrettanto fortunato.",
        ),
    },
    "yhanthlei": {
        "recall": (
            "Il Nido dei Profondi",
            "Una vasta caverna sommersa, le cui pareti pulsano di una debole "
            "bioluminescenza verdastra. E' il cuore pulsante di Y'ha-nthlei.",
        ),
        "respawn": (
            "Infermeria di Y'ha-nthlei",
            "Una sacca d'aria naturale nella roccia sommersa, adattata a "
            "infermeria per i Profondi feriti.",
        ),
        "morgue": (
            "Obitorio di Y'ha-nthlei",
            "Una fredda camera di roccia dove i corpi vengono lasciati prima "
            "di essere restituiti al mare, o a Padre Dagon.",
        ),
    },
    "migo_mothership": {
        "recall": (
            "Corridoio della Nave Madre Mi-Go",
            "Un corridoio organico dalle pareti fungine, illuminato da una "
            "luce fredda e innaturale. Il ronzio di macchinari incomprensibili "
            "riempie l'aria.",
        ),
        "respawn": (
            "Corridoio della Nave Madre Mi-Go",
            "Un corridoio organico dalle pareti fungine, illuminato da una "
            "luce fredda e innaturale. Il ronzio di macchinari incomprensibili "
            "riempie l'aria.",
        ),
        "morgue": (
            "Impianto di Riciclaggio",
            "Qui i Mi-Go riducono a componenti utili cio' che resta di chi "
            "non sopravvive. Meglio non indugiare a guardare troppo da vicino.",
        ),
    },
    "yuggoth_training": {
        "recall": (
            "Struttura di Addestramento Primario",
            "Un'ampia sala su Yuggoth dove i giovani Mi-Go vengono istruiti "
            "nelle scienze e nella chirurgia. Strumenti dalla funzione "
            "incerta sono allineati lungo le pareti.",
        ),
        "respawn": (
            "Struttura di Addestramento Primario",
            "Un'ampia sala su Yuggoth dove i giovani Mi-Go vengono istruiti "
            "nelle scienze e nella chirurgia. Strumenti dalla funzione "
            "incerta sono allineati lungo le pareti.",
        ),
        "morgue": (
            "Camera Medica del Centro di Addestramento",
            "Una camera asettica dove vengono portati gli studenti feriti "
            "durante gli esperimenti - e, talvolta, i loro resti.",
        ),
    },
    "ulthar_temple": {
        "recall": (
            "Tempio di Ulthar - La Fontana",
            "Una fontana di pietra bianca zampilla al centro del cortile del "
            "tempio, circondata - come vuole la legge di Ulthar - da gatti "
            "che sonnecchiano al sole delle Dreamlands.",
        ),
        "respawn": (
            "Tempio di Ulthar - La Fontana",
            "Una fontana di pietra bianca zampilla al centro del cortile del "
            "tempio, circondata - come vuole la legge di Ulthar - da gatti "
            "che sonnecchiano al sole delle Dreamlands.",
        ),
        "morgue": (
            "Tempio di Ulthar - Obitorio",
            "Una piccola cripta sotto il tempio, dove i sacerdoti vegliano "
            "i caduti prima che i loro sogni si dissolvano per sempre.",
        ),
    },
    "dylath_reformatory": {
        "recall": (
            "Dylath-Leen - Riformatorio Minorile",
            "Un edificio di basalto nero, uno dei tanti che caratterizzano "
            "l'architettura inquietante di Dylath-Leen. Qui vengono rinchiusi "
            "i giovani discoli della citta' onirica.",
        ),
        "respawn": (
            "Riformatorio - Infermeria",
            "Una stanza spoglia con brande di ferro, dove i ragazzi feriti "
            "vengono lasciati a riprendersi.",
        ),
        "morgue": (
            "Riformatorio - Camera Mortuaria",
            "Una cella fredda in fondo al corridoio, di cui nessuno parla "
            "volentieri.",
        ),
    },
    "zoog_village": {
        "recall": (
            "Sotto le Radici",
            "Un cunicolo accogliente scavato tra le enormi radici di un "
            "albero del Bosco Incantato, cuore del villaggio degli Zoog.",
        ),
        "respawn": (
            "La Radura Aperta",
            "Una radura soleggiata nel folto del Bosco Incantato, dove gli "
            "Zoog feriti vengono portati a riprendersi tra risate nervose.",
        ),
        "morgue": (
            "Sulla Cima del Ceppo",
            "La cima piatta di un enorme ceppo cavo, usata dagli Zoog come "
            "luogo - poco cerimonioso - per i loro morti.",
        ),
    },
    "yithian_library": {
        "recall": (
            "Centro del Giardino a Cupola",
            "Un giardino coperto da un'immensa cupola trasparente, nel cuore "
            "della Grande Biblioteca Yithiana. File infinite di scaffali si "
            "perdono all'orizzonte artificiale.",
        ),
        "respawn": (
            "Centro del Giardino a Cupola",
            "Un giardino coperto da un'immensa cupola trasparente, nel cuore "
            "della Grande Biblioteca Yithiana. File infinite di scaffali si "
            "perdono all'orizzonte artificiale.",
        ),
        "morgue": (
            "Infermeria della Grande Biblioteca",
            "Una sala di cura Yithiana, dove corpi - propri o presi in "
            "prestito - vengono lasciati quando non rispondono piu'.",
        ),
    },
}

TAG_CATEGORY = "start_room"


def _get_or_create_room(nome, descrizione, tag_key):
    """Trova la stanza gia' taggata con tag_key, o la crea."""
    existing = search.search_tag(tag_key, category=TAG_CATEGORY)
    if existing:
        return existing[0]
    room = create.create_object("typeclasses.rooms.Room", key=nome)
    room.db.desc = descrizione
    room.tags.add(tag_key, category=TAG_CATEGORY)
    return room


def crea_stanze_newbie():
    """
    Crea (se non esistono gia') tutte le stanze di RECALL/RESPAWN/MORGUE
    degli 8 hub newbie. Idempotente: si puo' rilanciare senza duplicare nulla.

    Ritorna un dizionario {hub_id: {"recall": Room, "respawn": Room, "morgue": Room}}.
    """
    risultato = {}
    for hub_id, ruoli in HUBS.items():
        nome_recall, desc_recall = ruoli["recall"]
        nome_respawn, desc_respawn = ruoli["respawn"]
        nome_morgue, desc_morgue = ruoli["morgue"]

        recall_tag = f"{hub_id}_recall"
        respawn_tag = f"{hub_id}_respawn"
        morgue_tag = f"{hub_id}_morgue"

        if nome_recall == nome_respawn:
            # stessa stanza: la creiamo una volta e le mettiamo entrambi i tag
            room = _get_or_create_room(nome_recall, desc_recall, recall_tag)
            if not room.tags.get(respawn_tag, category=TAG_CATEGORY):
                room.tags.add(respawn_tag, category=TAG_CATEGORY)
            recall_room = respawn_room = room
        else:
            recall_room = _get_or_create_room(nome_recall, desc_recall, recall_tag)
            respawn_room = _get_or_create_room(nome_respawn, desc_respawn, respawn_tag)

        morgue_room = _get_or_create_room(nome_morgue, desc_morgue, morgue_tag)

        risultato[hub_id] = {
            "recall": recall_room,
            "respawn": respawn_room,
            "morgue": morgue_room,
        }
    return risultato


def stanza_per_ruolo(hub_id, ruolo):
    """Cerca la stanza di un hub per ruolo ('recall', 'respawn', 'morgue')."""
    tag_key = f"{hub_id}_{ruolo}"
    trovate = search.search_tag(tag_key, category=TAG_CATEGORY)
    return trovate[0] if trovate else None
