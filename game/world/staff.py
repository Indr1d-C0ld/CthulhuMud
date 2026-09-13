"""
Comandi e vantaggi esclusivi dello staff (Fase K, ventesima tornata):
confermati dalla fonte (immhelp_commands.txt, il catalogo ufficiale dei
comandi immortali per livello - Hero/Creator/Lesser God/God/Greater
God/Implementor - e le singole pagine helps/<comando>.txt) come
meccaniche REALI dello staff, non semplice colore. Fino a questa
tornata l'unico livello staff costruito era il generico toolkit admin
di Evennia tradotto (commands/cthulhu_admin.py: boot/ban/perm/emit/
wall/force) - nessuno dei verbi specifici di CthulhuMUD (RESTORE, SLAY,
FREEZE, ADVANCE, PEACE, WIZINVIS/CLOAK, SWITCH, INCARNATE, WIZLOCK/
NEWLOCK, GOTO/BAMFIN/BAMFOUT, HOLYLIGHT) esisteva.

Scelta di design esplicita sulla gerarchia: la fonte ha 6 livelli
nominali (Hero/Creator/Lesser God/God/Greater God/Implementor) con
inoltre dei "flag" trasversali (admin/builder/enforcer/questor) - qui
si mappa ciascun comando sul livello Evennia (Builder/Admin/Developer)
piu' vicino per POTERE, invece di introdurre 6 nuovi permessi paralleli:
questo progetto ha un solo amministratore reale, non uno staff a piu'
persone, quindi replicare l'intera scala nominale aggiungerebbe
complessita' senza reale beneficio - la fedelta' che conta qui e' su
COSA fa ogni comando, non sul nome esatto del suo gradino.
"""

from world.esperienza import sale_di_livello, skill_al_livello

ATTRIBUTI_CURA = ("cieco", "avvelenato", "malato")  # "poison, plague, and blindness" (helps/restore.txt)


def restaura(personaggio):
    """RESTORE su un singolo personaggio: HP/mana/movimento al massimo,
    cura veleno/peste/cecita' (helps/restore.txt: "heals poison, plague,
    and blindness affects"). Veleno/peste sono danno periodico
    (world/effetti.py:applica_danno_periodico, script
    "periodico_<stato>") - rimuovere solo la voce da db.stati non
    basta, lo script continuerebbe a infliggere danno ai tick
    successivi: va anche fermato esplicitamente."""
    personaggio.db.hp = personaggio.db.hp_max
    personaggio.db.mana = personaggio.db.mana_max
    personaggio.db.move = personaggio.db.move_max
    stati = personaggio.db.stati or {}
    for stato in ATTRIBUTI_CURA:
        stati.pop(stato, None)
        for script in personaggio.scripts.get(f"periodico_{stato}"):
            script.stop()
        for script in personaggio.scripts.get(f"stato_{stato}"):
            script.stop()
    personaggio.db.stati = stati


def ferma_tutti_i_combattimenti(stanza):
    """PEACE: interrompe ogni combattimento in corso nella stanza
    (helps/peace.txt)."""
    fermati = []
    for presente in list(stanza.contents):
        if getattr(presente, "db", None) and presente.db.combat_target:
            presente.ferma_combattimento()
            fermati.append(presente)
    return fermati


def avanza_personaggio(personaggio, nuovo_livello):
    """ADVANCE <personaggio> <livello>: alza o abbassa il livello nella
    professione ATTIVA fino al valore dato (helps/advance.txt: "awards
    or deducts trains and practices just as if the character had
    gained the levels through normal means").

    Salire: richiama sale_di_livello() una volta per ogni livello, la
    STESSA funzione usata dalla progressione normale per XP - stessi
    bonus HP/mana/movimento/practice/train, stesse skill sbloccate.

    Scendere: nessuna fonte descrive come "retrocedere" un personaggio
    in modo esatto (il caso reale della fonte e' quasi sempre salire,
    per portare un nuovo Immortale al livello richiesto) - qui ci si
    limita a riportare il numero di livello nella professione attiva e
    a rimuovere le skill ancora a rating 0 concesse SOLO dai livelli
    tolti (stessa logica gia' usata da cambia_professione_newbie),
    SENZA cercare di sottrarre con precisione i bonus HP/mana/
    movimento/practice/train gia' accumulati (impossibile da invertire
    con certezza, dato che nel frattempo l'utente potrebbe aver speso
    TRAIN su quegli stessi pool) - scelta di design esplicita,
    dichiarata anche nel messaggio mostrato allo staff.

    Ritorna (ok: bool, messaggio: str)."""
    if not personaggio.db.active_profession:
        return False, f"{personaggio.key} non ha una professione attiva."
    prof_id = personaggio.db.active_profession
    professions = personaggio.db.professions or {}
    livello_attuale = professions.get(prof_id, 0)

    if nuovo_livello == livello_attuale:
        return False, f"{personaggio.key} e' gia' al livello {nuovo_livello}."

    if nuovo_livello > livello_attuale:
        messaggi = []
        while professions.get(prof_id, 0) < nuovo_livello:
            messaggi.append(sale_di_livello(personaggio))
            professions = personaggio.db.professions or {}
        personaggio.db.xp = 0
        return True, (
            f"{personaggio.key} avanzato dal livello {livello_attuale} al {nuovo_livello}.\n"
            + "\n".join(messaggi)
        )

    skills = personaggio.db.skills or {}
    for livello in range(nuovo_livello + 1, livello_attuale + 1):
        for skill_id in skill_al_livello(prof_id, livello):
            if skills.get(skill_id, 0) == 0:
                skills.pop(skill_id, None)
    personaggio.db.skills = skills
    professions[prof_id] = nuovo_livello
    personaggio.db.professions = professions
    personaggio.db.xp = 0
    return True, (
        f"{personaggio.key} riportato dal livello {livello_attuale} al {nuovo_livello} "
        f"(nota: HP/mana/movimento/practice/train massimi NON vengono ridotti automaticamente - "
        f"nessuna fonte descrive come farlo con precisione; regolali a mano se necessario)."
    )
