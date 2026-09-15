"""
IA di movimento/pattugliamento per i mostri ostili (Fase H, terza
tornata).

Confermato dalla fonte (immhelp_flags.txt: SENTINEL = "doesn't do
random movement"; STAY-AREA = "will not leave its area") che un mob
vaga casualmente tra le stanze della propria area a meno di essere
SENTINEL (fermo). Il meccanismo di innesco documentato
(immhelp_conditions.txt: una condizione "random 0..1023" valutata ad
ogni evento "pulse", cioe' un tick periodico) e' esattamente "ad ogni
tick, una probabilita' casuale di spostarsi in un'uscita a caso" - non
un pathfinding. STAY-AREA vieta di lasciare la propria zona: qui
applicato restringendo le uscite valide alle sole stanze che
condividono una delle categorie di tag della zona di origine del
mostro (vedi world/popola_mostri.py:ZONA_CATEGORIE). Le stanze fuori
da queste categorie (hub newbie compresi, tag category "start_room",
mai condivisa con le zone di gioco) sono percio' gia' escluse per
costruzione, senza bisogno di un equivalente esplicito del flag
NO_MOB.

Frequenza del tick e probabilita' di movimento non sono mai
pubblicate dalla fonte (dipendevano dal file .are originale, mai reso
pubblico): 30 secondi reali e 25% sono scelte di design esplicite.

Quando un mostro NON si sposta in un dato tick, ha anche una piccola
probabilita' di recitare una battuta ambientale (world/mostri.py,
campo frasi_ambiente) - l'equivalente in spirito del comando MPECHO
della fonte (immhelp_mobcommands.txt: "issues the text string as an
echo event"), qui come semplice testo di colore invece di un vero
motore di scripting generico (scelta di design condivisa con
l'utente: comportamenti scritti direttamente in Python invece di una
VM MOBprogram-like, dato che non esistono altri builder che
scriverebbero contenuti in un linguaggio di scripting).
"""

import random

from evennia.objects.models import ObjectDB

from world.popola_mostri import ZONA_CATEGORIE
from world.colori import ambiente

PROBABILITA_MOVIMENTO = 0.25
PROBABILITA_FRASE_AMBIENTE = 0.15


def _npc_del_tick():
    """Una sola interrogazione, due insiemi.

    - "mostri": le creature del bestiario, che vagano e parlano;
    - "scenografia": gli NPC non ostili (bottegai, sacerdoti, custodi...)
      a cui e' stata data una lista di frasi_ambiente. Prima non
      esisteva alcun modo perche' costoro dicessero o facessero nulla:
      restavano fermi e muti in ogni stanza del gioco. Qui ricevono le
      stesse battute atmosferiche delle creature, senza pero' vagare -
      un bottegaio che si allontanasse dalla propria bottega sarebbe un
      guaio, non un abbellimento."""
    mostri, scenografia = [], []
    for o in ObjectDB.objects.filter(db_typeclass_path="typeclasses.npcs.NPC"):
        if (o.db.hp or 0) <= 0:
            continue
        if o.attributes.has("bestiario_chiave"):
            mostri.append(o)
        elif o.db.frasi_ambiente:
            scenografia.append(o)
    return mostri, scenografia


def _mostri_vivi():
    """Compatibilita' con il codice e i test che gia' la usavano."""
    return _npc_del_tick()[0]


def tenta_movimento_mostro(npc):
    """Ritorna True se il mostro si e' spostato in questo tick."""
    if npc.db.sentinella or npc.db.combat_target or not npc.location:
        return False
    if random.random() > PROBABILITA_MOVIMENTO:
        return False

    categorie = ZONA_CATEGORIE.get(npc.db.zona)
    if not categorie:
        return False

    candidati = []
    for uscita in npc.location.exits:
        dest = uscita.destination
        if dest and any(dest.tags.get(category=cat) for cat in categorie):
            candidati.append((uscita, dest))
    if not candidati:
        return False

    uscita, dest = random.choice(candidati)
    origine = npc.location
    origine.msg_contents(f"{npc.key} se ne va verso {uscita.key}.", exclude=[])
    npc.move_to(dest, quiet=True)
    dest.msg_contents(f"{npc.key} arriva.", exclude=[])

    # Bug reale trovato in audit (Fase K, pre-release): move_to() non
    # passa da at_object_receive lato NPC, quindi un mostro aggressivo
    # che vagava in una stanza gia' occupata da giocatori non li
    # attaccava mai. world.mostri.tenta_aggro e' la stessa logica gia'
    # usata quando e' il personaggio a entrare (typeclasses/rooms.py),
    # qui applicata nel verso opposto.
    from world.mostri import tenta_aggro

    for personaggio in dest.contents:
        if personaggio.is_typeclass("typeclasses.characters.Character", exact=False):
            if tenta_aggro(npc, personaggio):
                break
    return True


def tenta_frase_ambiente(npc):
    """MPECHO-equivalente: una battuta atmosferica nella stanza corrente."""
    frasi = npc.db.frasi_ambiente or []
    if not frasi or not npc.location:
        return False
    if random.random() > PROBABILITA_FRASE_AMBIENTE:
        return False
    npc.location.msg_contents(ambiente(random.choice(frasi)), exclude=[])
    return True


def tick_movimento_mostri():
    """Chiamata dal tick di MostriMovimentoScript (typeclasses/scripts.py)."""
    mostri, scenografia = _npc_del_tick()
    for npc in mostri:
        if npc.db.combat_target:
            continue
        if not tenta_movimento_mostro(npc):
            tenta_frase_ambiente(npc)
    # gli NPC di scenografia non si spostano mai: parlano e basta
    for npc in scenografia:
        tenta_frase_ambiente(npc)


def avvia_movimento_mostri():
    """Avvia lo script globale di movimento, se non gia' attivo
    (idempotente, stesso pattern di world/repop.py:avvia_repop)."""
    from evennia.scripts.models import ScriptDB
    from evennia.utils import create

    esistente = ScriptDB.objects.filter(db_key="mostri_movimento")
    if esistente:
        return esistente[0]
    return create.create_script("typeclasses.scripts.MostriMovimentoScript")
