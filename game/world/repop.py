"""
Repop/reset dei mostri uccisi (Fase H, seconda tornata).

Confermato dalla fonte (immhelp_resets.txt): un'area con giocatori
uccisi/mostri saccheggiati si ripopola tramite dei "resets" periodici,
con una regola qualitativa esplicita: un'area si ripopola PIU' IN
FRETTA quando e' vuota di giocatori, e PIU' LENTAMENTE quando ce ne
sono ("The delayed reset while players are present is to prevent them
from becoming overwhelmed by a continually regenerating army of
mobiles"). Ogni mob-reset ha anche un massimo per stanza (MRESET
[VNUM] [MAX #], default 1 se non specificato).

Gli intervalli numerici esatti non sono mai pubblicati (dipendevano dal
file .are del builder originale, mai reso pubblico) - sono quindi una
scelta di design esplicita, in linea con gli altri tick reali gia'
scelti in questa sessione (fame/sete 10 min, decadimento cadavere 15
min, missioni 5/30 min).

Fase H, terza tornata (world/mostri_movimento.py): da quando i mostri
vagano davvero, il conteggio di presenza e' fatto per ZONA (non piu'
per singola stanza) - fedele a quanto dice esplicitamente la fonte su
MRESET: "This regulator works, even if mobs wander off". Se contassimo
solo la stanza canonica, un mostro che si e' allontanato in
pattugliamento farebbe sembrare vuoto il suo slot e ne verrebbe creato
un secondo altrove, gonfiando la popolazione nel tempo - esattamente
il problema che la fonte dice di prevenire.
"""

import time

from evennia.utils import search

INTERVALLO_ZONA_VUOTA = 300       # 5 minuti reali
INTERVALLO_ZONA_OCCUPATA = 1800   # 30 minuti reali
MASSIMO_PER_STANZA = 1            # MRESET di default nella fonte


def zone():
    """Ritorna l'insieme delle zone note nella tabella di reset."""
    from world.popola_mostri import TABELLA_RESET

    return sorted({zona for _, _, _, zona in TABELLA_RESET})


def _voci_zona(zona):
    from world.popola_mostri import TABELLA_RESET

    return [voce for voce in TABELLA_RESET if voce[3] == zona]


def zona_occupata(zona):
    """True se almeno un giocatore connesso si trova in una delle
    stanze coperte dalle voci di reset di questa zona."""
    for _, tag_stanza, categoria, _ in _voci_zona(zona):
        for stanza in search.search_tag(tag_stanza, category=categoria):
            for oggetto in stanza.contents:
                if oggetto.has_account:
                    return True
    return False


def _presenti_per_chiave_in_zona(zona):
    """Quanti esemplari vivi di ciascuna bestiario_chiave si trovano
    OVUNQUE nella zona in questo momento (non solo nella loro stanza
    canonica) - cosi' un mostro che ha vagato altrove viene comunque
    contato, come il MRESET della fonte."""
    from evennia.objects.models import ObjectDB

    conteggio = {}
    for o in ObjectDB.objects.filter(db_typeclass_path="typeclasses.npcs.NPC"):
        if o.db.zona == zona and o.db.bestiario_chiave and (o.db.hp or 0) > 0:
            conteggio[o.db.bestiario_chiave] = conteggio.get(o.db.bestiario_chiave, 0) + 1
    return conteggio


def esegui_reset_zona(zona):
    """Ripopola le voci mancanti della zona. Una voce viene ricreata solo
    se (a) la zona nel suo complesso ha meno esemplari di quella
    bestiario_chiave di quanti previsti dalla tabella (MASSIMO_PER_STANZA
    per voce - il "quorum" della zona), e (b) la sua stanza canonica
    specifica non ne ha gia' uno. Ritorna la lista dei mostri creati."""
    from world.mostri import crea_mostro

    voci = _voci_zona(zona)
    quorum = {}
    for chiave_bestiario, _, _, _ in voci:
        quorum[chiave_bestiario] = quorum.get(chiave_bestiario, 0) + MASSIMO_PER_STANZA

    presenti = _presenti_per_chiave_in_zona(zona)

    creati = []
    for chiave_bestiario, tag_stanza, categoria, _ in voci:
        if presenti.get(chiave_bestiario, 0) >= quorum.get(chiave_bestiario, MASSIMO_PER_STANZA):
            continue
        stanze = search.search_tag(tag_stanza, category=categoria)
        if not stanze:
            continue
        stanza = stanze[0]
        gia_in_questa_stanza = any(
            o.db.bestiario_chiave == chiave_bestiario for o in stanza.contents
        )
        if gia_in_questa_stanza:
            continue
        creati.append(crea_mostro(chiave_bestiario, stanza, zona=zona))
        presenti[chiave_bestiario] = presenti.get(chiave_bestiario, 0) + 1
    return creati


def controlla_e_ripopola_tutte_le_zone(ultimo_reset):
    """Chiamata dal tick di RepopScript (typeclasses/scripts.py).
    ultimo_reset e' un dict persistente {zona: timestamp_ultimo_reset}
    mutato in place. Ritorna [(zona, [mostri_creati]), ...] per le sole
    zone effettivamente ripopolate in questo giro (utile per log/test)."""
    ora = time.time()
    risultati = []
    for zona in zone():
        intervallo = (
            INTERVALLO_ZONA_OCCUPATA if zona_occupata(zona) else INTERVALLO_ZONA_VUOTA
        )
        if ora - ultimo_reset.get(zona, 0) < intervallo:
            continue
        creati = esegui_reset_zona(zona)
        ultimo_reset[zona] = ora
        if creati:
            risultati.append((zona, creati))

    # Le quattro aree di partenza non umane hanno un ripopolamento
    # proprio (world/popola_hub_alieni.py): non passano dalla
    # TABELLA_RESET perche' le loro creature richiedono accorgimenti che
    # crea_mostro() da solo non applica - devono restare sentinella, o
    # risalirebbero oltre la soglia fin dentro il nucleo sicuro attorno
    # alla stanza di nascita. Stessa cadenza delle altre zone.
    from world.popola_hub_alieni import ripopola_hub_alieni

    intervallo = (
        INTERVALLO_ZONA_OCCUPATA if zona_occupata_hub_alieni() else INTERVALLO_ZONA_VUOTA
    )
    if ora - ultimo_reset.get("hub_alieni", 0) >= intervallo:
        n = ripopola_hub_alieni()
        ultimo_reset["hub_alieni"] = ora
        if n:
            risultati.append(("hub_alieni", n))

    return risultati


def zona_occupata_hub_alieni():
    """Vero se c'e' almeno un personaggio giocante nelle quattro aree.
    Stessa logica di zona_occupata(), ma su una categoria di tag sola."""
    from evennia.objects.models import ObjectDB

    for r in ObjectDB.objects.filter(db_typeclass_path="typeclasses.rooms.Room"):
        if not r.tags.get(category="hub_alieno_room"):
            continue
        for o in r.contents:
            if o.is_typeclass("typeclasses.characters.Character", exact=False):
                return True
    return False


def avvia_repop():
    """Avvia lo script globale di repop, se non gia' attivo (idempotente,
    stesso pattern di world/sopravvivenza.py:avvia_sopravvivenza)."""
    from evennia.scripts.models import ScriptDB
    from evennia.utils import create

    esistente = ScriptDB.objects.filter(db_key="repop_mostri")
    if esistente:
        return esistente[0]
    return create.create_script("typeclasses.scripts.RepopScript")
