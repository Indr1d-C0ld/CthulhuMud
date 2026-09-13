"""
REST/SLEEP/STAND/WAKE (Fase K, quattordicesima tornata): sistema di
posizione del personaggio, confermato dalla fonte come meccanica
reale (helps/rest.txt), non semplice colore:

    "These commands allow a player to change the position of their
    character. REST and SLEEP result in increased regeneration rates
    for hit points, mana, and movement points, but the character is
    also more vulnerable to attack in these positions. In addition,
    if a character goes to SLEEP, they will be unaware of many
    actions that are occurring in the room around them. STAND and
    WAKE bring the character back to a default, upright position.
    WAKE can also be used to awaken other sleeping characters, but
    characters who are put to SLEEP by magical means may find it
    much more difficult to wake up. The STAND command can also be
    used to stop performing other actions, such as searching a room,
    picking a lock, debating, etc."

Scoperta durante questa tornata: il comando REST gia' presente in
commands/cthulhu_inn.py (affitta una stanza in albergo, ripristino
istantaneo a pagamento) occupava il nome "rest" senza che questa
pagina fosse mai stata controllata - e' stato rinominato in ALLOGGIA
(vedi commands/cthulhu_inn.py) per lasciare il vero REST della fonte
libero di essere costruito qui.

Nessuna cifra esatta e' data dalla fonte per il moltiplicatore di
rigenerazione o per la vulnerabilita' aggiuntiva: le costanti qui
sotto sono una scelta di design esplicita, facile da ritarare.
"""

import random

IN_PIEDI = "in_piedi"
RIPOSO = "riposo"
DORMENDO = "dormendo"

# world/posizione.py e' anche l'unico posto che conosce i tag delle 4
# stanze albergo (usati sia da commands/cthulhu_inn.py per ALLOGGIA sia
# da questo modulo per popolare gli albergatori NPC).
ALBERGHI_TAGS = (
    ("building_dombrowski_boarding", "arkham_building"),
    ("building_grand_hotel", "arkham_building"),
    ("building_miskatonic_hotel", "arkham_building"),
    ("cairo_shop_anubis_hotel", "cairo_room"),
)

# helps/rest.txt non da' numeri: +15/+30 alla probabilita' di essere
# colpiti sono una scelta di design esplicita.
BONUS_VULNERABILITA = {
    IN_PIEDI: 0,
    RIPOSO: 15,
    DORMENDO: 30,
}

# moltiplicatore sul tick base di rigenerazione (world/posizione.py:
# applica_tick_rigenerazione) - scelta di design esplicita.
MOLTIPLICATORE_REGEN = {
    IN_PIEDI: 1,
    RIPOSO: 3,
    DORMENDO: 6,
}

REGEN_BASE_HP = 1
REGEN_BASE_MANA = 1
REGEN_BASE_MOVE = 1

# probabilita' di FALLIRE il tentativo di svegliare qualcuno addormentato
# per via magica (Sonno/Sonno Incantato/Maledetto) invece che di suo
# volere - "may find it much more difficult to wake up", nessuna cifra
# esatta data dalla fonte.
PROBABILITA_FALLIMENTO_WAKE_MAGICO = 0.5


def _posizione(personaggio):
    return personaggio.db.posizione or IN_PIEDI


def bonus_vulnerabilita_posizione(difensore):
    """Bonus alla probabilita' di essere colpiti, in base alla propria
    posizione (usato da typeclasses/living.py:calcola_hit_chance)."""
    if not getattr(difensore, "db", None):
        return 0
    return BONUS_VULNERABILITA.get(_posizione(difensore), 0)


def moltiplicatore_regen(personaggio):
    return MOLTIPLICATORE_REGEN.get(_posizione(personaggio), 1)


def applica_tick_rigenerazione(personaggio):
    """Rigenera HP/Mana/Movimento in base alla posizione attuale. Da
    chiamare periodicamente (vedi typeclasses/scripts.py:
    RigenerazioneScript) su ogni Character vivo."""
    moltiplicatore = moltiplicatore_regen(personaggio)

    hp_max = personaggio.db.hp_max or 0
    if hp_max and (personaggio.db.hp or 0) < hp_max:
        personaggio.db.hp = min(hp_max, (personaggio.db.hp or 0) + REGEN_BASE_HP * moltiplicatore)

    mana_max = personaggio.db.mana_max or 0
    if mana_max and (personaggio.db.mana or 0) < mana_max:
        personaggio.db.mana = min(mana_max, (personaggio.db.mana or 0) + REGEN_BASE_MANA * moltiplicatore)

    move_max = personaggio.db.move_max or 0
    if move_max and (personaggio.db.move or 0) < move_max:
        personaggio.db.move = min(move_max, (personaggio.db.move or 0) + REGEN_BASE_MOVE * moltiplicatore)

    if personaggio.db.sottorazza:
        # Fase K, ventiseiesima tornata: il pool lumen dei Were non si
        # ricaricava mai (gap trovato dall'audit sottorazze).
        from world.sottorazze import tenta_ricarica_lumen
        tenta_ricarica_lumen(personaggio)


def tenta_rest(personaggio):
    posizione = _posizione(personaggio)
    if posizione == RIPOSO:
        return False, "Ti stai gia' riposando."
    personaggio.db.posizione = RIPOSO
    if personaggio.location:
        personaggio.location.msg_contents(
            f"{personaggio.key} si siede a riposare.", exclude=personaggio
        )
    return True, "Ti siedi a riposare. Recuperi le forze piu' in fretta, ma sei piu' vulnerabile."


def tenta_sleep(personaggio):
    posizione = _posizione(personaggio)
    if posizione == DORMENDO:
        return False, "Stai gia' dormendo."
    personaggio.db.posizione = DORMENDO
    if personaggio.location:
        personaggio.location.msg_contents(
            f"{personaggio.key} si addormenta.", exclude=personaggio
        )
    return True, "Ti addormenti. Recuperi le forze molto piu' in fretta, ma non ti accorgerai di quasi nulla intorno a te, e sei piu' vulnerabile."


def tenta_stand(personaggio):
    if personaggio.db.incantesimo_in_corso:
        # helps/spell_casting.txt: "You can stop casting a spell by
        # using the STAND command" - vale anche se sei gia' in piedi.
        from world.magic import interrompi_lancio
        interrompi_lancio(personaggio, None)
        return True, "Interrompi il lancio dell'incantesimo."
    posizione = _posizione(personaggio)
    if posizione == IN_PIEDI:
        return False, "Sei gia' in piedi."
    personaggio.db.posizione = IN_PIEDI
    verbo = "ti svegli e ti alzi in piedi" if posizione == DORMENDO else "ti alzi in piedi"
    if personaggio.location:
        personaggio.location.msg_contents(
            f"{personaggio.key} {verbo}.", exclude=personaggio
        )
    return True, f"Ti alzi in piedi."


def tenta_wake(personaggio, testo):
    """WAKE senza bersaglio: alzati (come STAND). WAKE <bersaglio>: prova
    a svegliare qualcun altro - se e' addormentato per via magica
    (db.stati['addormentato'], vedi world/effetti.py), la fonte dice che
    e' "molto piu' difficile" svegliarlo: qui un tiro a probabilita'
    fissa (vedi PROBABILITA_FALLIMENTO_WAKE_MAGICO)."""
    testo = (testo or "").strip()
    if not testo:
        ok, messaggio = tenta_stand(personaggio)
        return messaggio

    bersaglio = personaggio.search(testo)
    if not bersaglio:
        return ""
    if bersaglio is personaggio:
        ok, messaggio = tenta_stand(personaggio)
        return messaggio
    if not getattr(bersaglio, "db", None):
        return f"Non puoi svegliare {bersaglio.key}."

    addormentato_magicamente = bool((bersaglio.db.stati or {}).get("addormentato"))
    if _posizione(bersaglio) != DORMENDO and not addormentato_magicamente:
        return f"{bersaglio.key} non sta dormendo."

    if addormentato_magicamente and random.random() < PROBABILITA_FALLIMENTO_WAKE_MAGICO:
        personaggio.msg(f"Provi a svegliare {bersaglio.key}, ma non si muove: il suo sonno non e' naturale.")
        return ""

    bersaglio.db.posizione = IN_PIEDI
    if addormentato_magicamente:
        stati = bersaglio.db.stati or {}
        stati.pop("addormentato", None)
        bersaglio.db.stati = stati

    # Fase K, ventiseiesima tornata: bug reale trovato dall'audit
    # Dreamlands - WAKE su un ALTRO personaggio non lo riportava mai dal
    # sogno al mondo reale, solo in piedi sul posto. Vedi world/dreamlands.py.
    from world.dreamlands import in_dreamlands, sveglia_da_sogno
    if in_dreamlands(bersaglio.location):
        sveglia_da_sogno(bersaglio, None)
        bersaglio.msg(f"{personaggio.key} ti scuote finche' non ti svegli di soprassalto, riportandoti dal sogno.")
        if bersaglio.location:
            bersaglio.location.msg_contents(f"{bersaglio.key} riemerge da un sogno.", exclude=[bersaglio])
        return f"Svegli {bersaglio.key}, che riemerge dal sogno."

    bersaglio.msg(f"{personaggio.key} ti scuote finche' non ti svegli di soprassalto.")
    if bersaglio.location:
        bersaglio.location.msg_contents(
            f"{bersaglio.key} si sveglia di soprassalto.", exclude=[personaggio, bersaglio]
        )
    return f"Svegli {bersaglio.key}."


def avvia_rigenerazione():
    """Crea lo script globale del tick di rigenerazione se non e' gia'
    in esecuzione (idempotente, come avvia_sopravvivenza in
    world/sopravvivenza.py)."""
    from evennia.scripts.models import ScriptDB

    esistente = ScriptDB.objects.filter(db_key="rigenerazione")
    if esistente:
        return esistente[0]
    from evennia.utils import create
    return create.create_script("typeclasses.scripts.RigenerazioneScript")
