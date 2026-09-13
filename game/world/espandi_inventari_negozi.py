"""
Espansione inventari (Fase F, nona tornata): i 47 negozi gia'
popolati nelle tornate precedenti avevano tutti esattamente 3 articoli
ciascuno. Nessuna fonte originale verificabile indica un numero esatto
di articoli per negozio nel CthulhuMud originale (vedi nota in
world/economia.py e nei singoli moduli popola_negozi_*.py) - qui si
amplia semplicemente la varieta' a 5 articoli per negozio, riusando lo
stesso stile e la stessa coerenza tematica gia' adottati.

Le funzioni popola_negozi_*() sono idempotenti "in creazione": se un
mercante esiste gia' nella stanza, lo restituiscono senza toccarne
l'inventario. Per questo serve una funzione a parte che AGGIORNI
l'inventario dei mercanti gia' esistenti con le liste NEGOZI ora
ampliate nei rispettivi moduli.
"""

from evennia.utils import search

from world.popola_negozi import NEGOZI_DA_POPOLARE
from world.popola_negozi_abbigliamento import NEGOZI as NEGOZI_ABBIGLIAMENTO
from world.popola_negozi_cibo import NEGOZI as NEGOZI_CIBO
from world.popola_negozi_generici import NEGOZI as NEGOZI_GENERICI
from world.popola_negozi_cairo import NEGOZI as NEGOZI_CAIRO
from world.popola_negozi_zoog import NEGOZI as NEGOZI_ZOOG

# Elenco unificato: (tag_categoria, tag_chiave, inventario)
_TUTTI = []
for tag_categoria, tag_chiave, _nome, _descrizione, inventario in NEGOZI_DA_POPOLARE:
    _TUTTI.append((tag_categoria, tag_chiave, inventario))
for tag_chiave, _nome, _descrizione, inventario in NEGOZI_ABBIGLIAMENTO:
    _TUTTI.append(("arkham_building", tag_chiave, inventario))
for tag_chiave, _nome, _descrizione, inventario in NEGOZI_CIBO:
    _TUTTI.append(("arkham_building", tag_chiave, inventario))
for tag_chiave, _nome, _descrizione, inventario in NEGOZI_GENERICI:
    _TUTTI.append(("arkham_building", tag_chiave, inventario))
for tag_chiave, _nome, _descrizione, inventario in NEGOZI_CAIRO:
    _TUTTI.append(("cairo_room", tag_chiave, inventario))
for tag_chiave, _nome, _descrizione, inventario in NEGOZI_ZOOG:
    _TUTTI.append(("zoogvillage_room", tag_chiave, inventario))


def espandi_inventari_negozi():
    """
    Per ognuno dei 47 negozi, trova il mercante gia' esistente nella
    stanza e ne aggiorna db.negozio con la lista di articoli ampliata
    (5 invece di 3). Se non trova ne' la stanza ne' un mercante, lo
    segnala separatamente invece di crearne uno nuovo (questa funzione
    aggiorna soltanto, non popola).
    """
    aggiornati = []
    non_trovati = []
    for tag_categoria, tag_chiave, inventario in _TUTTI:
        stanze = search.search_tag(tag_chiave, category=tag_categoria)
        if not stanze:
            non_trovati.append(tag_chiave)
            continue
        stanza = stanze[0]
        mercanti = [
            obj for obj in stanza.contents
            if obj.attributes.has("negozio") and obj.db.negozio
        ]
        if not mercanti:
            non_trovati.append(tag_chiave)
            continue
        mercante = mercanti[0]
        mercante.db.negozio = inventario
        aggiornati.append((mercante.key, len(inventario)))
    return aggiornati, non_trovati
