"""
Porte chiuse a chiave (Fase K, nona tornata): confermate dalla fonte
(helps/open.txt, unica pagina condivisa da OPEN/CLOSE/LOCK/UNLOCK) -
"For doors, players must specify the direction of the door, not its
name" (quindi OPEN NORTH, non OPEN DOOR) e "LOCK and UNLOCK... the
player must have the appropriate key to do this". PICK LOCK (skill gia'
esistente in world/skills.py, mai agganciata a nulla) permette di
scassinare senza chiave.

Semplificazione dichiarata: la fonte cita anche "trunks, chest,
lockers" come oggetti apribili/chiudibili - nessun oggetto del genere
esiste ancora nel nostro mondo (nessuna pagina specifica quali/dove), e
costruire un intero sistema di contenitori chiudibili senza un solo
caso d'uso reale sarebbe stato inventare piu' del necessario: questa
tornata si limita alle PORTE (uscite), che sono anche l'unico
collegamento gia' presente con l'incantesimo Pass Door
(world/magic.py:_effetto_pass_door, world/spells.py) - il vero motivo
per cui questo gap era rimasto aperto.

Qualunque uscita del mondo puo' diventare una porta chiudibile la prima
volta che viene chiusa con CLOSE: non serve marcarla in anticipo. Il
lock dinamico "traverse:porta_aperta()" (server/conf/lockfuncs.py) viene
aggiunto automaticamente in quel momento, se non gia' presente.
"""

import random

COSTO_SCASSO = 50  # movimento per tentativo di PICK LOCK, scelta di design (non specificato dalla fonte)


def trova_uscita(personaggio, direzione):
    """Trova un'uscita della stanza attuale che corrisponda a
    <direzione> (chiave o alias, es. 'nord'/'n')."""
    stanza = personaggio.location
    if not stanza:
        return None
    direzione = direzione.strip().lower()
    for uscita in stanza.exits:
        nomi = [uscita.key.lower()] + [a.lower() for a in uscita.aliases.all()]
        if direzione in nomi:
            return uscita
    return None


def _assicura_lock_porta(uscita):
    # Sostituisce il lock "traverse" invece di aggiungerlo in OR: quasi
    # tutte le uscite del mondo hanno il lock di default "traverse:all()"
    # (accesso sempre concesso), e un OR con qualcosa di sempre vero
    # renderebbe porta_aperta() ininfluente (bug scoperto testando: la
    # porta chiusa restava attraversabile da chiunque). porta_aperta()
    # gia' da sola si comporta come "all()" quando la porta e' aperta,
    # quindi non serve preservare il lock precedente - semplificazione
    # dichiarata: se in futuro un'uscita avesse un lock "traverse" piu'
    # articolato (es. legato a un livello minimo), andrebbe combinato qui
    # invece di essere sostituito.
    if "porta_aperta" in uscita.locks.get("traverse"):
        return
    uscita.locks.add("traverse:porta_aperta()")


def apri(personaggio, uscita):
    """OPEN <direzione>. Ritorna (ok, messaggio)."""
    if not uscita.db.chiusa:
        return False, f"{uscita.key} e' gia' aperta/o."
    if uscita.db.bloccata:
        return False, f"{uscita.key} e' chiusa/o a chiave."
    uscita.db.chiusa = False
    return True, f"Apri {uscita.key}."


def chiudi(personaggio, uscita):
    """CLOSE <direzione>. Ritorna (ok, messaggio)."""
    if uscita.db.chiusa:
        return False, f"{uscita.key} e' gia' chiusa/o."
    _assicura_lock_porta(uscita)
    uscita.db.chiusa = True
    return True, f"Chiudi {uscita.key}."


def blocca(personaggio, uscita, chiave):
    """LOCK <direzione>, tenendo in mano <chiave>. Ritorna (ok, messaggio)."""
    if not uscita.db.chiusa:
        return False, f"{uscita.key} deve prima essere chiusa/o."
    if uscita.db.bloccata:
        return False, f"{uscita.key} e' gia' chiusa/o a chiave."
    if not chiave or not chiave.db.e_chiave:
        return False, "Non tieni in mano una chiave."
    if chiave.db.apre and chiave.db.apre != uscita:
        return False, f"{chiave.key} apre gia' un'altra serratura."
    chiave.db.apre = uscita
    uscita.db.bloccata = True
    uscita.db.chiave_id = chiave.dbref
    return True, f"Chiudi a chiave {uscita.key} con {chiave.key}."


def sblocca(personaggio, uscita, chiave):
    """UNLOCK <direzione>, tenendo in mano <chiave>. Ritorna (ok, messaggio)."""
    if not uscita.db.bloccata:
        return False, f"{uscita.key} non e' chiusa/o a chiave."
    if not chiave or chiave.db.apre != uscita:
        return False, f"{chiave.key if chiave else 'quello che tieni in mano'} non apre questa serratura."
    uscita.db.bloccata = False
    return True, f"Apri la serratura di {uscita.key} con {chiave.key}."


def tenta_scasso(personaggio, uscita):
    """PICK <direzione>: scassina senza chiave, con probabilita' legata
    al rating in Scasso (skill "pick_lock", finora mai agganciata a
    nulla). Formula non specificata dalla fonte: scelta di design
    esplicita, facile da ritarare. Ritorna (ok, messaggio)."""
    if not uscita.db.bloccata:
        return False, f"{uscita.key} non e' chiusa/o a chiave."
    rating = personaggio.skill_rating("pick_lock")
    if rating <= 0:
        return False, "Non conosci la skill Scasso."
    if (personaggio.db.move or 0) < COSTO_SCASSO:
        return False, "Sei troppo stanco per tentare uno scasso."
    personaggio.db.move -= COSTO_SCASSO
    probabilita = min(90, 20 + rating // 2)
    if random.uniform(0, 100) <= probabilita:
        uscita.db.bloccata = False
        return True, f"Scassini la serratura di {uscita.key}!"
    return False, f"Il tentativo di scassinare {uscita.key} fallisce."
