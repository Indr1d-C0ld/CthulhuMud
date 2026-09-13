"""
Mosse speciali di combattimento (Fase K, ventiduesima tornata):
confermate dalla fonte come comandi reali e distinti, non semplici
skill passive - helps/kick.txt, bash.txt, trip.txt, disarm.txt,
dirt_kicking.txt, backstab.txt. Gia' assegnate a moltissime professioni
(world/professions_newbie.py, world/professions_avanzate.py, gia'
descritte in world/skills.py) ma prive di qualunque comando o effetto
meccanico fino a questa tornata.

Ognuna inizia il combattimento se non gia' in corso (helps/kill.txt
elenca esplicitamente BACKSTAB/KICK tra le "specialized forms of
attack" che, come le magie offensive, avviano la lotta da sole).

Nessuna formula esatta di probabilita'/danno e' data dalla fonte per
nessuna di queste mosse: le costanti qui sotto sono scelte di design
esplicite, facili da ritarare, pensate per restare coerenti con le
formule gia' esistenti in typeclasses/living.py.

BASH e TRIP condividono lo stesso stato "a_terra" (a terra/sbilanciato)
per l'effetto "aumenta la vulnerabilita' e impedisce di fuggire finche'
non ci si rialza" - confermato da helps/wimpy.txt ("if the character
has been knocked down by a TRIP or BASH, they will not be able to FLEE
until they stand back up"), agganciato in typeclasses/living.py
(calcola_hit_chance) e world/combat.py (tenta_fuga).
"""

import random

from world.effetti import applica_stato


DURATA_A_TERRA = 8         # secondi - "until they stand back up", nessuna cifra esatta data
DURATA_SBILANCIATO = 6     # secondi - malus a colpire dopo un KICK fallito
DURATA_CIECO_DIRT = 15     # secondi - "a slight advantage", piu' breve dei 60s di Accecamento (incantesimo)


def _avvia_se_non_in_corso(attaccante, difensore):
    if attaccante.db.combat_target is not difensore:
        attaccante.avvia_combattimento(difensore)


def tenta_kick(attaccante, difensore):
    """KICK: concede un attacco extra a calci. Un tentativo fallito
    sbilancia chi lo tenta (helps/kick.txt)."""
    _avvia_se_non_in_corso(attaccante, difensore)
    chance = max(5, min(95, 30 + attaccante.skill_rating("kick") // 2))
    if random.uniform(0, 100) > chance:
        applica_stato(attaccante, "sbilanciato", DURATA_SBILANCIATO, "Ritrovi l'equilibrio.")
        attaccante.location.msg_contents(
            f"{attaccante.key} tenta un calcio a {difensore.key} ma perde l'equilibrio!"
        )
        return False

    from world.equipment import classe_armatura_totale
    forza = attaccante.valore_attributo("str") if hasattr(attaccante, "valore_attributo") else 10
    danno_grezzo = random.randint(2, 6) + forza // 5
    riduzione = (classe_armatura_totale(difensore) + (difensore.db.bonus_ca_temp or 0)) // 4
    danno = max(1, danno_grezzo - riduzione)
    attaccante.location.msg_contents(
        f"{attaccante.key} sferra un calcio a {difensore.key} per {danno} danni!"
    )
    morto = difensore.subisci_danno(danno)
    if morto:
        from world.combat import gestisci_morte
        gestisci_morte(difensore, attaccante)
    return True


def tenta_bash(attaccante, difensore):
    """BASH: tenta di mandare il bersaglio in ginocchio (helps/bash.txt:
    "success depends on your rating in the BASH skill, your weight, and
    the size of your foe"). Nessuna statistica di peso/stazza esiste in
    questo porting: usati gli HP massimi come proxy della "stazza",
    scelta di design esplicita."""
    _avvia_se_non_in_corso(attaccante, difensore)
    stazza_attaccante = attaccante.db.hp_max or 20
    stazza_difensore = difensore.db.hp_max or 20
    rapporto_stazza = stazza_attaccante / max(1, stazza_difensore)
    chance = max(5, min(95, 25 + attaccante.skill_rating("bash") // 2 + (rapporto_stazza - 1) * 20))
    if random.uniform(0, 100) > chance:
        attaccante.location.msg_contents(f"{attaccante.key} tenta una spallata a {difensore.key} ma fallisce!")
        return False

    applica_stato(difensore, "a_terra", DURATA_A_TERRA, f"{difensore.key} si rialza in piedi.")
    attaccante.location.msg_contents(
        f"{attaccante.key} manda {difensore.key} in ginocchio con una spallata!"
    )
    return True


def tenta_trip(attaccante, difensore):
    """TRIP: sbilancia il bersaglio facendolo cadere (helps/trip.txt:
    "very difficult to trip very large characters, and a higher
    Dexterity... will enable a character to avoid this")."""
    _avvia_se_non_in_corso(attaccante, difensore)
    dex_attaccante = attaccante.valore_attributo("dex") if hasattr(attaccante, "valore_attributo") else 10
    dex_difensore = difensore.valore_attributo("dex") if hasattr(difensore, "valore_attributo") else 10
    chance = max(5, min(95, 30 + attaccante.skill_rating("trip") // 2 + (dex_attaccante - dex_difensore) // 2))
    if random.uniform(0, 100) > chance:
        attaccante.location.msg_contents(f"{attaccante.key} tenta uno sgambetto a {difensore.key} ma fallisce!")
        return False

    applica_stato(difensore, "a_terra", DURATA_A_TERRA, f"{difensore.key} si rialza in piedi.")
    attaccante.location.msg_contents(
        f"{attaccante.key} fa cadere {difensore.key} a terra con uno sgambetto!"
    )
    return True


def tenta_disarm(attaccante, difensore):
    """DISARM: fa cadere l'arma di mano al bersaglio (helps/disarm.txt:
    "best chance... comes when you are skilled in both your weapon type
    AND the type of weapon your opponent is using... Strength and
    Dexterity of both combatants are also factors... Some special
    weapons cannot be disarmed")."""
    from world.equipment import arma_equipaggiata, skill_arma

    _avvia_se_non_in_corso(attaccante, difensore)
    arma_difensore = arma_equipaggiata(difensore)
    if not arma_difensore:
        attaccante.location.msg_contents(f"{difensore.key} non impugna nulla da disarmare.")
        return False
    if arma_difensore.db.non_disarmabile:
        attaccante.location.msg_contents(f"Non riesci a strappare {arma_difensore.key} dalle mani di {difensore.key}.")
        return False

    skill_propria = attaccante.skill_rating(skill_arma(attaccante) or "hand_to_hand")
    skill_avversaria = attaccante.skill_rating(skill_arma(difensore) or "hand_to_hand")
    str_attaccante = attaccante.valore_attributo("str") if hasattr(attaccante, "valore_attributo") else 10
    str_difensore = difensore.valore_attributo("str") if hasattr(difensore, "valore_attributo") else 10
    chance = max(5, min(95,
        20 + attaccante.skill_rating("disarm") // 2
        + skill_propria // 10 + skill_avversaria // 10
        + (str_attaccante - str_difensore) // 2
    ))
    if random.uniform(0, 100) > chance:
        attaccante.location.msg_contents(f"{attaccante.key} tenta di disarmare {difensore.key} ma non ci riesce!")
        return False

    slot = next((s for s, o in (difensore.db.equip or {}).items() if o is arma_difensore), None)
    if slot:
        equip = difensore.db.equip
        equip.pop(slot, None)
        difensore.db.equip = equip
    arma_difensore.move_to(difensore.location, quiet=True)
    attaccante.location.msg_contents(
        f"{attaccante.key} disarma {difensore.key}: {arma_difensore.key} cade a terra!"
    )
    return True


def tenta_dirt_kicking(attaccante, difensore):
    """DIRT KICKING (sintassi DIRT nella fonte): acceca temporaneamente
    il bersaglio (helps/dirt_kicking.txt) - riusa lo stato "cieco" gia'
    esistente (Accecamento), ma per una durata piu' breve, coerente con
    "a slight advantage" invece di un vero incantesimo."""
    _avvia_se_non_in_corso(attaccante, difensore)
    dex_attaccante = attaccante.valore_attributo("dex") if hasattr(attaccante, "valore_attributo") else 10
    dex_difensore = difensore.valore_attributo("dex") if hasattr(difensore, "valore_attributo") else 10
    chance = max(5, min(95, 30 + attaccante.skill_rating("dirt_kicking") // 2 + (dex_attaccante - dex_difensore) // 2))
    if random.uniform(0, 100) > chance:
        attaccante.location.msg_contents(f"{attaccante.key} tira della terra verso {difensore.key} ma lo/la manca!")
        return False

    applica_stato(difensore, "cieco", DURATA_CIECO_DIRT, "Riesci finalmente a ripulirti gli occhi.")
    attaccante.location.msg_contents(
        f"{attaccante.key} tira una manciata di terra negli occhi di {difensore.key}!"
    )
    return True


def tenta_backstab(attaccante, difensore):
    """BACKSTAB: danno molto piu' alto del normale (helps/backstab.txt:
    "damage inflicted... determined by the attacker's level, the
    attacker's weapon skill, the attacker's BACKSTAB skill, and the
    power of the target"). La probabilita' di andare a segno resta
    quella normale (la fonte non descrive un tiro per colpire
    separato, solo la scala del danno)."""
    from world.equipment import classe_armatura_totale

    _avvia_se_non_in_corso(attaccante, difensore)
    if random.uniform(0, 100) > attaccante.calcola_hit_chance(difensore):
        attaccante.location.msg_contents(f"{attaccante.key} tenta di pugnalare alle spalle {difensore.key} ma fallisce!")
        return False

    moltiplicatore = 1 + attaccante.skill_rating("backstab") / 50 + attaccante.livello_per_equip() / 20
    danno_grezzo = round(attaccante.calcola_danno() * moltiplicatore)
    riduzione = (classe_armatura_totale(difensore) + (difensore.db.bonus_ca_temp or 0)) // 4
    danno = max(1, danno_grezzo - riduzione)
    attaccante.location.msg_contents(
        f"{attaccante.key} pugnala alle spalle {difensore.key} per {danno} danni!"
    )
    morto = difensore.subisci_danno(danno)
    if morto:
        from world.combat import gestisci_morte
        gestisci_morte(difensore, attaccante)
    return True
