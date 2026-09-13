"""
REMORT (Fase K, nona tornata): confermato dalla fonte (helps/remort1.txt,
il "player option" descrittivo; helps/remort2.txt, il comando IMMORTAL
vero e proprio - "Authority: NONE Level: LESSER GOD... used to remort
players who have reached the required level"). Come Societies/Clan
(world/societies.py) e le sottorazze permanenti (world/sottorazze.py),
la fonte stessa lo descrive come un processo mediato dallo staff, MAI
self-service: implementarlo come comando per il giocatore sarebbe stato
infedele, non un gap da colmare.

Regole confermate verbatim dalla fonte:
- Eleggibile al livello 201 la prima volta, poi di nuovo ogni volta che
  si raggiunge il livello 300 (non cumulativo: si riparte da 3 ogni
  volta, quindi la soglia resta 300, non 201+300*n).
- Riporta il personaggio al livello 3, dimezza HP/mana/movimento attuali
  E massimi, mantiene oltre il 95% delle skill agli stessi rating (qui:
  5% di probabilita' per ogni skill di perdere una piccola quantita' di
  punti), mantiene oro/equipaggiamento/appartenenza al clan.
- Sconsigliato (non vietato) su un personaggio affamato/assetato o
  "switched" (es. Yithian che sta possedendo un corpo - vedi
  world/yithian.py): qui il secondo caso e' bloccato esplicitamente
  (i livelli guadagnati andrebbero applicati al corpo sbagliato), il
  primo resta solo un avviso, come dice la fonte stessa ("should not
  have any negative effects").
- Alla fine l'account viene disconnesso (confermato dalla fonte: "When
  the player reconnects, they will once again find themselves at level
  3 and the remort process will be complete").

NON specificato dalla fonte (scelte di design esplicite): come conciliare
il "livello 3" con il nostro modello di multi-classing (world/esperienza.py,
livello_personaggio() = somma dei livelli di TUTTE le professioni mai
giocate) - qui si azzera la cronologia di ogni professione tranne quella
attiva, portata a 3: un vero "si riparte da capo", coerente con lo spirito
della fonte anche se il dettaglio tecnico e' un'interpretazione necessaria.
L'immtitle personalizzato citato dalla fonte non viene costruito (nessuna
infrastruttura di titoli esiste ancora in questo porting): db.remortato
sblocca comunque l'accesso reale al canale REMTALK (world/canali.py,
server/conf/lockfuncs.py:e_remortato), il beneficio concreto gia' pronto.
"""

import random

LIVELLO_PRIMO_REMORT = 201
LIVELLO_REMORT_SUCCESSIVO = 300
LIVELLO_DOPO_REMORT = 3
PROBABILITA_PERDITA_SKILL = 5   # percentuale, per singola skill
PERDITA_SKILL_MIN, PERDITA_SKILL_MAX = 1, 10


def puo_remortare(personaggio):
    volte = personaggio.db.remort_count or 0
    soglia = LIVELLO_PRIMO_REMORT if volte == 0 else LIVELLO_REMORT_SUCCESSIVO
    return personaggio.livello_personaggio() >= soglia


def remort(personaggio):
    """Esegue il remort. Ritorna (ok: bool, messaggio: str)."""
    if personaggio.db.yithian_originale:
        return False, (
            f"{personaggio.key} sta attualmente possedendo un altro corpo (MINDTRANSFER): "
            "va fatto tornare al proprio corpo prima di poter remortare."
        )
    if not puo_remortare(personaggio):
        volte = personaggio.db.remort_count or 0
        soglia = LIVELLO_PRIMO_REMORT if volte == 0 else LIVELLO_REMORT_SUCCESSIVO
        return False, f"{personaggio.key} non ha ancora raggiunto il livello richiesto ({soglia})."

    avviso_fame = ""
    if (personaggio.db.appetito or 0) > 0 or (personaggio.db.sete or 0) > 0:
        avviso_fame = " (nota: il personaggio soffriva fame/sete al momento del remort - la fonte dice che non dovrebbe avere effetti negativi, ma tienilo d'occhio)"

    prof_attiva = personaggio.db.active_profession
    professions = personaggio.db.professions or {}
    for prof_id in list(professions):
        professions[prof_id] = LIVELLO_DOPO_REMORT if prof_id == prof_attiva else 0
    personaggio.db.professions = professions
    personaggio.db.xp = 0

    personaggio.db.hp_max = max(1, (personaggio.db.hp_max or 2) // 2)
    personaggio.db.hp = personaggio.db.hp_max
    personaggio.db.mana_max = (personaggio.db.mana_max or 0) // 2
    personaggio.db.mana = personaggio.db.mana_max
    personaggio.db.move_max = max(1, (personaggio.db.move_max or 2) // 2)
    personaggio.db.move = personaggio.db.move_max

    skills = personaggio.db.skills or {}
    perse = []
    for skill_id, rating in list(skills.items()):
        if rating > 0 and random.randint(1, 100) <= PROBABILITA_PERDITA_SKILL:
            perdita = min(rating, random.randint(PERDITA_SKILL_MIN, PERDITA_SKILL_MAX))
            skills[skill_id] = rating - perdita
            perse.append(skill_id)
    personaggio.db.skills = skills

    personaggio.db.remortato = True
    personaggio.db.remort_count = (personaggio.db.remort_count or 0) + 1

    messaggio = (
        f"{personaggio.key} ha remortato (remort n.{personaggio.db.remort_count}): "
        f"tornato/a al livello {LIVELLO_DOPO_REMORT}, HP/mana/movimento dimezzati, "
        f"{len(perse)} skill lievemente intaccate su {len(skills)}. "
        f"Oro, equipaggiamento e clan restano invariati.{avviso_fame}"
    )
    return True, messaggio
