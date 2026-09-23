"""
Seguaci: TAME/RECRUIT/ORDER (Fase K, nona tornata). Confermati dalla
fonte (helps/tame.txt, helps/recruit.txt, helps/order.txt) - segnalati
come gap esplicito fin dalla Fase K settima tornata ("un vero sistema di
seguaci/ORDER per le skill Tame/Recruit"), perche' Ammaliare (Charm
Person, world/magic.py) si appoggiava a una versione semplificata senza
un vero elenco di seguaci ne' un modo per comandarli.

TAME (skill, 200 movimento): confermato dalla fonte che NON funziona su
"sentient NPCs, undead NPCs, and NPCs with even a small amount of
natural intelligence" - qui interpretato cosi': il nostro bestiario
(world/mostri.py) e' fatto interamente di orrori del Mythos senzienti o
non-morti (Ghoul, cultisti, Profondi, mummie, Cani di Tindalos,
Byakhee, Shoggoth, Gug, Bestie Lunari, marinai annegati) - NESSUNO di
questi e' quindi addomesticabile per definizione, coerente con la
fonte. TAME funziona solo su NPC di ambientazione "animaleschi" (senza
db.ostile/db.attacca_a_vista/db.sottorazza), come i pochi gia' presenti
nel mondo (es. "un topo enorme").

RECRUIT (skill passiva, "no special command... works automatically"):
agganciata a typeclasses/rooms.py:Room.at_object_receive() - la stessa
sede gia' usata per l'aggro dei mostri - controllata ogni volta che un
personaggio entra in una stanza, con probabilita' legata al rating.

ORDER (comando): confermato dalla fonte - "you are responsible for the
actions of your followers", qui si limita a inoltrare il comando al
seguace con execute_cmd(), nessuna restrizione aggiuntiva (la fonte
stessa affida la responsabilita' al giocatore, non al sistema).
"""

import random

from evennia.utils import create

COSTO_TAME = 200  # movimento, confermato dalla fonte ("REQUIRES: 200 movement points")
PROBABILITA_RECRUIT_BASE = 2   # percentuale per tick di ingresso in stanza, per punto di rating oltre non serve altro

NOMI_SEGUACI_RECRUIT = (
    "un cane randagio affezionato",
    "un mendicante silenzioso",
    "un gatto mezzo selvatico",
    "un marinaio in congedo senza meta",
)


def e_addomesticabile(npc):
    """Vero se npc puo' essere bersaglio di TAME - vedi nota di modulo:
    nessun mostro senziente/non-morto del bestiario lo e' mai."""
    if not npc or not npc.is_typeclass("typeclasses.npcs.NPC", exact=False):
        return False
    if npc.db.ostile or npc.db.attacca_a_vista or npc.db.sottorazza:
        return False
    if npc.db.negozio or npc.db.incudine:
        return False
    # istruttori compresi (NPC.intoccabile): il controllo sul negozio qui
    # sopra c'era gia', ma il Dr. Armitage si poteva addomesticare
    if getattr(npc, "intoccabile", False):
        return False
    return True


def tenta_tame(personaggio, npc):
    """TAME <bersaglio>. Ritorna (ok, messaggio)."""
    rating = personaggio.skill_rating("tame")
    if rating <= 0:
        return False, "Non conosci la skill Domare."
    if not e_addomesticabile(npc):
        return False, f"{npc.key} non puo' essere addomesticato/a."
    if npc.db.padrone:
        return False, f"{npc.key} ha gia' un padrone."
    if (personaggio.db.move or 0) < COSTO_TAME:
        return False, "Sei troppo stanco per tentare di addomesticare una creatura."
    personaggio.db.move -= COSTO_TAME

    probabilita = min(90, 15 + rating // 2)
    if random.uniform(0, 100) > probabilita:
        return False, f"Il tentativo di addomesticare {npc.key} fallisce."

    npc.db.padrone = personaggio
    npc.db.ostile = False
    seguaci = personaggio.db.seguaci or []
    seguaci.append(npc)
    personaggio.db.seguaci = seguaci
    return True, f"{npc.key} e' ora completamente leale a te."


def tenta_recruit(personaggio):
    """Chiamata da Room.at_object_receive() a ogni ingresso in stanza:
    possibilita' automatica di attrarre un seguace, legata al rating in
    Reclutare. Nessun comando dedicato (confermato dalla fonte: "no
    special command to use... It works automatically")."""
    rating = personaggio.skill_rating("recruit")
    if rating <= 0:
        return None
    probabilita = min(15, rating // 10)
    if random.uniform(0, 100) > probabilita:
        return None

    nome = random.choice(NOMI_SEGUACI_RECRUIT)
    seguace = create.create_object("typeclasses.npcs.NPC", key=nome, location=personaggio.location)
    seguace.db.desc = f"{nome.capitalize()}, che ti segue ovunque ora."
    seguace.db.padrone = personaggio
    seguace.db.ostile = False
    seguaci = personaggio.db.seguaci or []
    seguaci.append(seguace)
    personaggio.db.seguaci = seguaci
    personaggio.msg(f"|c{nome.capitalize()} inizia a seguirti spontaneamente.|n")
    return seguace


def sposta_seguaci(personaggio):
    """Da chiamare quando personaggio cambia stanza: i seguaci lo
    seguono automaticamente (confermato implicitamente dalla fonte:
    ORDER li tratta come sempre presenti al fianco del padrone)."""
    seguaci = personaggio.db.seguaci or []
    validi = []
    for seguace in seguaci:
        # "is None" e non solo ".pk": un seguace cancellato (un animale
        # addomesticato che muore, per esempio) diventa None nella lista,
        # e il solo `.pk` sollevava AttributeError. Essendo questa
        # funzione chiamata da at_post_move, bastava un seguace morto per
        # rompere ogni spostamento successivo del padrone.
        if seguace is None or not seguace.pk:
            continue
        validi.append(seguace)
        if seguace.location != personaggio.location and getattr(seguace, "vivo", True):
            seguace.move_to(personaggio.location, quiet=True, move_type="follow")
    if validi != seguaci:
        personaggio.db.seguaci = validi


def ordina(personaggio, testo):
    """ORDER <seguace> <comando> / ORDER ALL <comando>. Ritorna (ok, messaggio)."""
    # vedi la nota in sposta_seguaci: un seguace cancellato diventa
    # None nella lista, e il solo .pk solleverebbe AttributeError.
    seguaci = [s for s in (personaggio.db.seguaci or []) if s is not None and s.pk]
    personaggio.db.seguaci = seguaci
    if not seguaci:
        return False, "Non hai nessun seguace."
    parti = testo.split(None, 1)
    if len(parti) != 2:
        return False, "Uso: order <seguace>/all <comando>"
    bersaglio_testo, comando = parti

    if bersaglio_testo.lower() == "all":
        for seguace in seguaci:
            seguace.execute_cmd(comando)
        return True, f"Ordini a tutti i tuoi seguaci di: {comando}"

    bersaglio = next((s for s in seguaci if bersaglio_testo.lower() in s.key.lower()), None)
    if not bersaglio:
        return False, f"Non hai un seguace chiamato '{bersaglio_testo}'."
    bersaglio.execute_cmd(comando)
    return True, f"Ordini a {bersaglio.key} di: {comando}"
