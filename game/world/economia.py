"""
Sistema economico di base (Fase F, prima tornata): mercanti con un
inventario in vendita, comandi per comprare e vendere, valuta in Oro
(gia' esistente su Character come db.gold, mostrato su SCORE).

Un "mercante" e' semplicemente un NPC (typeclasses.npcs.NPC) con
l'attributo db.negozio impostato: una lista di dizionari

    {"chiave": "pane", "nome": "una pagnotta di pane",
     "prezzo": 5, "descrizione": "..."}

"chiave" e' quello che il giocatore digita con BUY/COMPRA; "nome" e'
il nome dell'oggetto creato quando viene comprato; "prezzo" e' in Oro.
Ogni oggetto acquistato porta con se' db.valore = prezzo, cosi' che
SELL/VENDI possa ricomprarlo a meta' prezzo (convenzione classica da
MUD) senza dover consultare l'inventario specifico del mercante da cui
proveniva - funziona con qualunque oggetto marcato con un valore,
anche in futuro bottino di mostri.

I mercanti non sono ostili e non insegnano skill (a differenza degli
NPC gia' usati in M2): sono NPC "civili" dedicati alla sola vendita.
"""

from evennia.utils import create


def crea_mercante(location, nome, descrizione, inventario):
    """
    Crea (o ritrova, se gia' presente per nome in quella stanza) un
    mercante NPC con l'inventario dato. Non e' pensato per essere
    invocato piu' volte sulla stessa stanza con lo stesso nome in modo
    massiccio: i moduli di building lo chiamano una volta per negozio,
    con lo stesso pattern idempotente (_get_or_create) gia' visto
    altrove, controllando prima se un mercante con quel tag esiste
    gia'.
    """
    mercante = create.create_object(
        "typeclasses.npcs.NPC",
        key=nome,
        location=location,
    )
    mercante.db.desc = descrizione
    mercante.db.negozio = inventario
    mercante.db.ostile = False
    mercante.db.is_practice_trainer = False
    mercante.locks.add("get:false()")
    return mercante


def trova_mercante(stanza):
    """Ritorna il primo NPC nella stanza che abbia un attributo 'negozio' impostato."""
    for obj in stanza.contents:
        if obj.attributes.has("negozio") and obj.db.negozio:
            return obj
    return None
