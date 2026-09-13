"""
Popolamento dei 4 alberghi (Fase K, quattordicesima tornata): fino a
questa tornata i 4 edifici albergo (Dombrowski's Boarding House,
Grand Hotel, Miskatonic Hotel ad Arkham; Anubis Hotel al Cairo)
restavano senza alcun NPC, per scelta deliberata documentata in
world/popola_negozi.py/world/popola_negozi_cairo.py legata
all'assenza di una meccanica di alloggio - ora costruita (vedi
commands/cthulhu_inn.py ALLOGGIA e world/posizione.py REST/SLEEP/
STAND/WAKE). Coerenza con tutti gli altri edifici del gioco (che
hanno gia' un NPC a tema): qui un albergatore per edificio, puro NPC
di ambientazione senza inventario in vendita (nessun db.negozio -
ALLOGGIA non richiede la presenza dell'NPC, controlla solo il tag
della stanza, ma la fonte non descrive comunque un vero commercio in
albergo).
"""

from evennia.utils import create, search

from world.posizione import ALBERGHI_TAGS

# stesso ordine di ALBERGHI_TAGS (world/posizione.py) -> (nome, descrizione)
NOMI_DESCRIZIONI = [
    (
        "Signora Dombrowski, la locandiera",
        "Una donna anziana dallo sguardo severo ma non scortese, che "
        "tiene un registro degli ospiti sempre aperto sul bancone e "
        "un mazzo di chiavi appeso alla cintola.",
    ),
    (
        "Un portiere in livrea",
        "Un uomo dai modi impeccabili, in una livrea leggermente "
        "lisa ai gomiti, che accoglie ogni ospite con un inchino "
        "appena percettibile.",
    ),
    (
        "Un impiegato alla reception",
        "Un giovane con gli occhiali storti, che passa piu' tempo a "
        "leggere riviste accademiche dietro il bancone che a badare "
        "agli ospiti.",
    ),
    (
        "Un albergatore dal turbante bianco",
        "Un uomo dai modi cordiali, che offre te alla menta a ogni "
        "ospite prima ancora di chiedere il nome, e tiene un occhio "
        "sempre vigile sulle valigie dei viaggiatori stranieri.",
    ),
]


def popola_alberghi():
    """
    Crea (se non esiste gia') un albergatore NPC in ognuno dei 4
    alberghi. Idempotente: controlla per ogni stanza se esiste gia'
    un NPC con l'attributo albergatore=True prima di crearne uno
    nuovo.
    """
    creati = []
    for (tag_chiave, tag_categoria), (nome, descrizione) in zip(ALBERGHI_TAGS, NOMI_DESCRIZIONI):
        stanze = search.search_tag(tag_chiave, category=tag_categoria)
        if not stanze:
            continue
        stanza = stanze[0]
        esistente = [
            obj for obj in stanza.contents
            if obj.attributes.has("albergatore") and obj.db.albergatore
        ]
        if esistente:
            creati.append(esistente[0])
            continue
        albergatore = create.create_object(
            "typeclasses.npcs.NPC",
            key=nome,
            location=stanza,
        )
        albergatore.db.desc = descrizione
        albergatore.db.albergatore = True
        albergatore.db.ostile = False
        albergatore.db.is_practice_trainer = False
        albergatore.locks.add("get:false()")
        creati.append(albergatore)
    return creati
