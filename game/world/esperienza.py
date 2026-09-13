"""
Esperienza e livelli (Fase G, seconda tornata): il gap piu' strutturale
emerso dalla scansione esaustiva del sito originale (research/REPORT.md).
Prima di questa tornata, Character.db.professions[prof_id] (i "livelli
accumulati") non saliva MAI: uccidere un NPC non dava alcuna esperienza,
quindi practice/train non arrivavano mai oltre la dotazione iniziale.

Meccaniche confermate verbatim dalla fonte (helps/experience.txt,
helps/wisdom.txt, helps/righteouskill.txt):
- L'XP guadagnata uccidendo dipende dal DIVARIO di livello (effettivo)
  tra uccisore e vittima, non dai livelli assoluti: "a level-10 player
  killing a level-25 NPC will receive the same amount of XP as a
  level-150 player killing a level-165 NPC" (divario 15 in entrambi i
  casi).
- L'XP necessaria per il prossimo livello CRESCE con il livello.
- Allineamento: bonus di XP uccidendo il segno opposto, penalita'
  uccidendo lo stesso segno; gli effetti sono piu' marcati per un
  personaggio "buono" (allineamento positivo) che per uno "cattivo".
  Fase K, diciannovesima tornata: ogni uccisione ora sposta anche
  DAVVERO l'allineamento di chi uccide (RIGHTEOUSKILL, vedi
  sposta_allineamento) - fino a quella tornata l'allineamento non
  cambiava mai dopo la creazione, rendendo inerte questo bonus/malus
  per chiunque non l'avesse impostato a mano.
- INT molto alta da' un bonus fisso di XP per uccisione.
- CON -> piu' HP per livello, INT+WIS -> piu' mana, DEX -> piu'
  movimento, WIS -> piu' practice per livello (NON i train, la fonte lo
  specifica esplicitamente). I train per livello non sono legati a
  nessun attributo secondo la fonte: qui e' un valore fisso.

NON specificato dalla fonte (scelte di design esplicite, da ritarare):
- La formula esatta di XP-per-divario e di XP-necessaria-per-livello.
- I coefficienti esatti attributo->ricompensa di livello.
- I moltiplicatori esatti bonus/penalita' di allineamento e la soglia
  INT per il bonus fisso.
- Il "livello effettivo" (fighting level) e il "livello talento" (per
  gli oggetti, gia' in world/equipment.py) restano concettualmente
  distinti nella fonte ma qui coincidono entrambi con
  livello_personaggio(): una vera distinzione (es. buff/debuff
  temporanei sul fighting level) e' rimandata.
"""

import random

from world.colori import pericolo

XP_BASE_PER_LIVELLO = 100   # xp_necessaria(n) = XP_BASE_PER_LIVELLO * (n + 1)

XP_BASE_PER_DIVARIO = 20    # xp di base per ogni punto di divario di livello
XP_MINIMA = 1               # non si guadagna mai meno di questo, anche uccidendo molto sotto il proprio livello

SOGLIA_INT_BONUS = 16
BONUS_INT_DIVISORE = 2       # bonus_xp = (int - SOGLIA_INT_BONUS) // BONUS_INT_DIVISORE, se int >= soglia

# Moltiplicatori di allineamento (vedi helps/righteouskill.txt: gli
# effetti sono piu' marcati per chi e' "buono" che per chi e' "cattivo")
BONUS_ALLINEAMENTO_BUONO = 1.75    # buono uccide cattivo
PENALITA_ALLINEAMENTO_BUONO = 0.4  # buono uccide buono
BONUS_ALLINEAMENTO_CATTIVO = 1.25  # cattivo uccide buono
PENALITA_ALLINEAMENTO_CATTIVO = 0.7  # cattivo uccide cattivo

TRAINS_PER_LIVELLO = 2       # fisso: la fonte dice che WIS non influisce sui train

# Fase K, diciannovesima tornata: confermato dalla fonte (helps/
# righteouskill.txt) che ogni uccisione sposta l'allineamento di chi
# uccide - di default sempre verso il male, o con RIGHTEOUSKILL attivo
# verso l'opposto dell'allineamento della vittima. Fino a questa
# tornata l'allineamento non cambiava MAI dopo la creazione del
# personaggio, rendendo di fatto inerte il bonus/malus XP da
# allineamento gia' presente in _modificatore_allineamento per
# chiunque non l'avesse impostato a mano. Nessuna cifra esatta e' data
# dalla fonte per l'entita' dello spostamento - scelta di design
# esplicita, facile da ritarare.
SPOSTAMENTO_ALLINEAMENTO = 10
# "turning this option off will result in a small reduction in the
# amount of experience that you receive" - nessuna percentuale esatta
# data dalla fonte.
RIDUZIONE_XP_SENZA_RIGHTEOUSKILL = 0.95

# Perdita di XP alla morte (helps/death.txt, helps/experience.txt): "As a
# low-level character, you will not lose much experience from dying.
# However, after a certain point, you will lose a set amount of
# experience from each death, so it is possible to lose a level from
# dying." Soglia e quantita' non specificate dalla fonte - scelte di
# design esplicite.
SOGLIA_LIVELLO_PERDITA_MORTE = 10
XP_PERSA_PER_MORTE = 200


def xp_necessaria(livello_attuale):
    """XP per passare da livello_attuale a livello_attuale + 1."""
    return XP_BASE_PER_LIVELLO * (livello_attuale + 1)


def livello_effettivo(personaggio):
    """Vedi nota in cima al file: qui coincide con livello_personaggio()
    per i personaggi, o db.livello per gli NPC."""
    return personaggio.livello_per_equip()


def _modificatore_allineamento(uccisore, vittima):
    allineamento_u = uccisore.db.alignment or 0
    allineamento_v = vittima.db.alignment or 0
    if allineamento_u == 0:
        return 1.0
    stesso_segno = (allineamento_u > 0) == (allineamento_v > 0) if allineamento_v != 0 else False
    if allineamento_u > 0:
        return PENALITA_ALLINEAMENTO_BUONO if stesso_segno else BONUS_ALLINEAMENTO_BUONO
    return PENALITA_ALLINEAMENTO_CATTIVO if stesso_segno else BONUS_ALLINEAMENTO_CATTIVO


def sposta_allineamento(uccisore, vittima):
    """Ogni uccisione sposta l'allineamento di chi uccide (confermato
    dalla fonte, helps/righteouskill.txt): con RIGHTEOUSKILL attivo,
    verso l'opposto dell'allineamento della vittima; altrimenti sempre
    verso il male. Una vittima neutrale (allineamento 0) non sposta
    nulla con RIGHTEOUSKILL attivo - la fonte non specifica un default
    per questo caso, e spostare comunque verso il male vanificherebbe
    lo scopo dichiarato dell'opzione ("push your alignment toward
    good"/"toward evil" a seconda dell'allineamento della vittima)."""
    if not hasattr(uccisore, "db"):
        return
    if uccisore.db.righteouskill:
        allineamento_vittima = (getattr(vittima, "db", None) and vittima.db.alignment) or 0
        if allineamento_vittima > 0:
            spostamento = -SPOSTAMENTO_ALLINEAMENTO
        elif allineamento_vittima < 0:
            spostamento = SPOSTAMENTO_ALLINEAMENTO
        else:
            return
    else:
        spostamento = -SPOSTAMENTO_ALLINEAMENTO
    uccisore.db.alignment = max(-1000, min(1000, (uccisore.db.alignment or 0) + spostamento))


def xp_da_uccisione(uccisore, vittima):
    """XP guadagnata da uccisore per aver ucciso vittima."""
    divario = livello_effettivo(vittima) - livello_effettivo(uccisore)
    base = XP_BASE_PER_DIVARIO * max(0, divario + 5)  # +5: anche prede leggermente sotto il tuo livello danno un minimo
    base *= _modificatore_allineamento(uccisore, vittima)
    if hasattr(uccisore, "db") and not uccisore.db.righteouskill:
        base *= RIDUZIONE_XP_SENZA_RIGHTEOUSKILL

    intelligenza = 0
    if hasattr(uccisore, "valore_attributo"):
        intelligenza = uccisore.valore_attributo("int")
    if intelligenza >= SOGLIA_INT_BONUS:
        base += (intelligenza - SOGLIA_INT_BONUS) // BONUS_INT_DIVISORE

    return max(XP_MINIMA, round(base))


def guadagna_xp(personaggio, quantita):
    """Aggiunge XP; gestisce eventuali salite di livello a catena.
    Ritorna la lista di messaggi di livello guadagnato (vuota se
    nessuna salita)."""
    if not personaggio.db.active_profession:
        return []

    personaggio.db.xp = (personaggio.db.xp or 0) + quantita
    messaggi = []
    while True:
        livello_attuale = personaggio.livello_professione(personaggio.db.active_profession)
        necessaria = xp_necessaria(livello_attuale)
        if personaggio.db.xp < necessaria:
            break
        personaggio.db.xp -= necessaria
        messaggi.append(sale_di_livello(personaggio))
    return messaggi


def skill_al_livello(prof_id, livello):
    """Le skill previste ESATTAMENTE a quel livello (non cumulative) dalla
    tabella skill_per_livello della professione, newbie o avanzata che sia."""
    from world.professions_newbie import NEWBIE_PROFESSIONS
    from world.professions_avanzate import PROFESSIONI_AVANZATE
    entry = NEWBIE_PROFESSIONS.get(prof_id) or PROFESSIONI_AVANZATE.get(prof_id)
    if not entry:
        return []
    return entry.get("skill_per_livello", {}).get(livello, [])


def sincronizza_skill_professioni(personaggio):
    """Utility di migrazione (Fase K, nona tornata): assegna a rating 0 tutte
    le skill dei livelli gia' raggiunti in passato, per OGNI professione mai
    giocata (non solo quella attiva - coerente con lo stesso modello
    multi-classing gia' usato da valore_attributo()). Serve solo per
    personaggi creati/livellati PRIMA della correzione del bug in
    sale_di_livello (che fino a questa tornata non assegnava mai le skill
    oltre il livello 0): un personaggio creato dopo la correzione non ne ha
    mai bisogno, perche' le riceve gia' man mano che sale di livello.
    Ritorna la lista delle skill effettivamente aggiunte."""
    skills = personaggio.db.skills or {}
    aggiunte = []
    for prof_id, livello_raggiunto in (personaggio.db.professions or {}).items():
        for livello in range(livello_raggiunto + 1):
            for skill_id in skill_al_livello(prof_id, livello):
                if skill_id not in skills:
                    skills[skill_id] = 0
                    aggiunte.append(skill_id)
    personaggio.db.skills = skills
    return aggiunte


def sale_di_livello(personaggio):
    """Applica le ricompense di un singolo livello guadagnato (vedi
    helps/wisdom.txt per quale attributo influisce su cosa).

    Bug corretto (Fase K, nona tornata): fino a questa tornata, salire di
    livello uccidendo non assegnava MAI le nuove skill previste dalla
    tabella skill_per_livello della professione attiva - quella tabella
    veniva letta solo alla creazione del personaggio o cambiando
    esplicitamente professione (PROF CHANGE), mai durante la normale
    progressione per XP. Corretto assegnando qui le skill del nuovo
    livello a rating 0 (come fa gia' applica_professione_newbie per il
    livello 0), cosi' che PRACTICE/LEARN/TRAIN possano davvero farle
    salire."""
    professions = personaggio.db.professions or {}
    prof_id = personaggio.db.active_profession
    nuovo_livello = professions.get(prof_id, 0) + 1
    professions[prof_id] = nuovo_livello
    personaggio.db.professions = professions

    skills = personaggio.db.skills or {}
    nuove_skill = [s for s in skill_al_livello(prof_id, nuovo_livello) if s not in skills]
    for skill_id in nuove_skill:
        skills.setdefault(skill_id, 0)
    personaggio.db.skills = skills

    costituzione = personaggio.valore_attributo("con")
    intelligenza = personaggio.valore_attributo("int")
    saggezza = personaggio.valore_attributo("wis")
    destrezza = personaggio.valore_attributo("dex")

    bonus_hp = 2 + costituzione // 5
    bonus_mana = 1 + (intelligenza + saggezza) // 10
    bonus_move = 2 + destrezza // 5
    bonus_practice = 2 + saggezza // 5
    from world.sanita import bonus_sanita_livello
    bonus_sanity = bonus_sanita_livello(saggezza)

    personaggio.db.hp_max = (personaggio.db.hp_max or 0) + bonus_hp
    personaggio.db.hp = (personaggio.db.hp or 0) + bonus_hp
    personaggio.db.mana_max = (personaggio.db.mana_max or 0) + bonus_mana
    personaggio.db.mana = (personaggio.db.mana or 0) + bonus_mana
    personaggio.db.move_max = (personaggio.db.move_max or 0) + bonus_move
    personaggio.db.move = (personaggio.db.move or 0) + bonus_move
    personaggio.db.practices = (personaggio.db.practices or 0) + bonus_practice
    personaggio.db.trains = (personaggio.db.trains or 0) + TRAINS_PER_LIVELLO
    personaggio.db.sanity_max = (personaggio.db.sanity_max or 0) + bonus_sanity
    personaggio.db.sanity = (personaggio.db.sanity or 0) + bonus_sanity

    messaggio = (
        f"|gSali di livello! Ora sei al livello {nuovo_livello} "
        f"(+{bonus_hp} HP, +{bonus_mana} mana, +{bonus_move} movimento, "
        f"+{bonus_practice} practice, +{bonus_sanity} sanity, +{TRAINS_PER_LIVELLO} train).|n"
    )
    if nuove_skill:
        from world.skills import nome_skill
        nomi = ", ".join(nome_skill(s) for s in nuove_skill)
        messaggio += f"\n|cHai accesso a nuove skill: {nomi}.|n"
    return messaggio


def perdi_xp_morte(personaggio, moltiplicatore=1.0):
    """Applica la perdita di XP alla morte (helps/death.txt): nessuna
    perdita sotto SOGLIA_LIVELLO_PERDITA_MORTE, altrimenti una quantita'
    fissa che puo' far perdere un livello. Ritorna un messaggio da
    mostrare alla vittima, o None se non e' successo nulla.

    `moltiplicatore` (di default 1.0): confermato dalla fonte
    (guides_yithianfaq.txt) che uno Yithiano che possiede un NPC morto
    perde MENO XP del normale - qui la meta', vedi
    world/yithian.py:PENALITA_XP_MORTE_YITHIAN."""
    if not personaggio.db.active_profession:
        return None
    prof_id = personaggio.db.active_profession
    livello = personaggio.livello_professione(prof_id)
    if livello < SOGLIA_LIVELLO_PERDITA_MORTE:
        return None

    perdita = int(XP_PERSA_PER_MORTE * moltiplicatore)
    xp_attuale = personaggio.db.xp or 0
    deficit = perdita - xp_attuale
    if deficit <= 0:
        personaggio.db.xp = xp_attuale - perdita
        return f"Perdi {perdita} punti esperienza."

    nuovo_livello = max(0, livello - 1)
    professions = personaggio.db.professions or {}
    professions[prof_id] = nuovo_livello
    personaggio.db.professions = professions
    personaggio.db.xp = max(0, xp_necessaria(nuovo_livello) - deficit)
    return pericolo(f"La morte ti costa cara: perdi un livello (ora {nuovo_livello}).")
