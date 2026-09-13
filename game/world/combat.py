"""
Combattimento minimo (M3): risoluzione dei round, fuga, morte, cadaveri.
Armi/armatura (Fase F, decima tornata): vedi world/equipment.py.

Vedi typeclasses/living.py per le formule di colpire/danno (anch'esse
scelte di design non documentate dal sito originale).

Fase K, ventiduesima tornata: Second/Third/Fourth Attack (helps/
second_attack.txt - "automatic skills... if you have the skill at a
sufficiently high rating, you will automatically perform additional
attacks. A high rating in Dexterity also assists") sono ora vere:
risolvi_round() puo' concedere fino a 3 colpi extra nello stesso round,
riusando _esegui_attacco() per ciascuno invece di duplicare la logica
del colpo singolo. Semplificazione dichiarata: il controllo/consumo
munizioni di un'arma da fuoco resta legato solo al PRIMO colpo del
round, non ripetuto per ogni attacco extra (la fonte non specifica
come i due sistemi interagiscano).
"""

import random

from evennia.utils import create
from world.colori import pericolo, orrore

# "A high rating in the Dexterity attribute also assists in launching
# additional attacks" (helps/second_attack.txt) - nessun coefficiente
# esatto dato dalla fonte, scelta di design esplicita.
BONUS_DEX_ATTACCHI_EXTRA_DIVISORE = 10


def risolvi_round(attaccante):
    """Un round di combattimento di `attaccante` contro il suo bersaglio.
    Bassa sanity puo' scatenare un'azione erratica al posto del normale
    attacco (confermato dalla fonte, vedi world/sanita.py)."""
    from world.equipment import arma_equipaggiata
    from world.sanita import azione_erratica_possibile, applica_azione_erratica

    difensore = attaccante.db.combat_target
    if not difensore or not getattr(difensore, "vivo", True) or \
            difensore.location != attaccante.location:
        attaccante.ferma_combattimento()
        return

    stati = attaccante.db.stati or {}
    if stati.get("addormentato") or stati.get("paralizzato"):
        # Fase K, sesta tornata: Sonno/incantesimi immobilizzanti - il
        # personaggio perde semplicemente il turno, non puo' nemmeno fuggire.
        attaccante.location.msg_contents(
            pericolo(f"{attaccante.key} non riesce a fare nulla!"), exclude=[attaccante]
        )
        attaccante.msg(pericolo("Non riesci a muoverti!"))
        return
    if stati.get("impaurito"):
        # Fase K, sesta tornata: incantesimo Paura - stesso trattamento
        # della fuga forzata da azione erratica (world/sanita.py).
        tenta_fuga(attaccante)
        return

    if stati.get("allucinato") and random.randint(1, 100) <= 40:
        # Fase K, settima tornata: incantesimo Allucina - confermato
        # pericoloso "per il lanciatore e per chiunque incontri le
        # allucinazioni": il colpo devia su un bersaglio a caso presente
        # nella stanza, alleati inclusi.
        altri = [
            o for o in attaccante.location.contents
            if o is not attaccante and getattr(o, "vivo", None)
        ]
        if altri:
            bersaglio_reale = random.choice(altri)
            attaccante.location.msg_contents(
                pericolo(f"{attaccante.key}, in preda alle allucinazioni, attacca {bersaglio_reale.key} a caso!")
            )
            difensore = bersaglio_reale

    if attaccante.db.sanity is not None:
        azione = azione_erratica_possibile(attaccante)
        if azione:
            applica_azione_erratica(attaccante, azione)
            if azione in ("attacca_a_caso", "fugge", "vaga"):
                return

    arma_da_fuoco = arma_equipaggiata(attaccante)
    if arma_da_fuoco:
        from world.munizioni import e_arma_da_fuoco
        if e_arma_da_fuoco(arma_da_fuoco):
            if (arma_da_fuoco.db.munizioni_caricate or 0) <= 0:
                # Fase K, settima tornata: GUNSMITH/RELOAD hanno senso solo se
                # restare senza colpi ha davvero un effetto in combattimento.
                attaccante.location.msg_contents(
                    pericolo(f"{attaccante.key} preme il grilletto: solo uno scatto a vuoto!")
                )
                return
            arma_da_fuoco.db.munizioni_caricate -= 1

    morto = _esegui_attacco(attaccante, difensore)
    if morto:
        return

    # Fase K, ventiduesima tornata: Second/Third/Fourth Attack - fino a
    # 3 colpi extra nello stesso round, ciascuno condizionato al
    # successo del precedente (coerente con l'idea di "attacchi in
    # catena": se non scatta il secondo, il terzo/quarto non hanno
    # senso di essere tirati).
    destrezza = attaccante.valore_attributo("dex") if hasattr(attaccante, "valore_attributo") else 0
    bonus_dex = destrezza // BONUS_DEX_ATTACCHI_EXTRA_DIVISORE
    for skill_attacco_extra in ("second_attack", "third_attack", "fourth_attack"):
        if not getattr(difensore, "vivo", False) or difensore.location != attaccante.location:
            break
        chance = attaccante.skill_rating(skill_attacco_extra) + bonus_dex
        if chance <= 0 or random.randint(1, 100) > chance:
            break
        morto = _esegui_attacco(attaccante, difensore)
        if morto:
            return


def _esegui_attacco(attaccante, difensore):
    """Un singolo colpo (base o extra da Second/Third/Fourth Attack) di
    attaccante contro difensore. Ritorna True se difensore e' morto per
    questo colpo."""
    from world.equipment import arma_equipaggiata, classe_armatura_totale, degrada

    if random.uniform(0, 100) <= attaccante.calcola_hit_chance(difensore):
        danno_grezzo = attaccante.calcola_danno()
        if getattr(attaccante.db, "sensibile_luna", False):
            from world.sottorazze import luna_piena
            from world.mostri import BONUS_DANNO_LUNA_PIENA
            if luna_piena():
                danno_grezzo += BONUS_DANNO_LUNA_PIENA
        ca_difensore = classe_armatura_totale(difensore) + (difensore.db.bonus_ca_temp or 0)
        riduzione = ca_difensore // 4
        danno = max(1, danno_grezzo - riduzione)
        attaccante.location.msg_contents(
            pericolo(f"{attaccante.key} colpisce {difensore.key} per {danno} danni!")
        )

        arma = arma_equipaggiata(attaccante)
        if arma:
            degrada(arma)
        for oggetto in (difensore.db.equip or {}).values():
            if oggetto:
                degrada(oggetto)

        riflesso = difensore.db.riflesso_danno_temp or 0
        if riflesso:
            # Fase K, decima tornata: Scudo di Fuoco/Gelo/Fulmine
            # (elemental_shield) - "inflicts a small amount of damage to a
            # foe every time the foe strikes the caster".
            attaccante.location.msg_contents(
                f"Lo scudo di {difensore.key} respinge parte del colpo su {attaccante.key}!"
            )
            attaccante.subisci_danno(riflesso, fisico=False)

        morto = difensore.subisci_danno(danno)
        if morto:
            gestisci_morte(difensore, attaccante)
            return True
        if not difensore.db.combat_target:
            # contrattacco automatico, anche se non e' stato il difensore a
            # digitare "kill" per primo
            difensore.avvia_combattimento(attaccante)
        _controlla_wimpy(difensore)
        return False
    else:
        attaccante.location.msg_contents(pericolo(f"{attaccante.key} manca {difensore.key}."))
        return False


def _controlla_wimpy(personaggio):
    if personaggio.db.wimpy_soglia_ignorata_temp:
        # azione erratica da bassa sanity: "refuse to flee from a fight
        # they are losing" - vedi world/sanita.py
        personaggio.db.wimpy_soglia_ignorata_temp = False
        return
    soglia = personaggio.db.wimpy_soglia or 0
    if soglia <= 0:
        return
    hp_max = personaggio.db.hp_max or 1
    hp_pct = 100 * (personaggio.db.hp or 0) / hp_max
    if hp_pct <= soglia:
        tenta_fuga(personaggio, personaggio.db.wimpy_direzione)


XP_PERSA_PER_FUGA = 5  # "a small loss of experience" (helps/flee.txt) - nessuna cifra esatta data


def tenta_fuga(personaggio, direzione=None):
    """FLEE: 25% di possibilita' di fallire; scappa per un'uscita scelta
    (o casuale se non specificata/non trovata/bloccata da una porta
    chiusa - helps/wimpy.txt: "if your character cannot flee in the
    specified direction for some reason (no exit, closed door, etc.),
    another direction will be chosen at random"). Una fuga riuscita
    costa un po' di esperienza e puo' danneggiare l'equipaggiamento
    (helps/flee.txt: "a small loss of experience and/or some minor
    damage to your equipment"). Ritorna True se riuscita."""
    stanza = personaggio.location
    if (personaggio.db.stati or {}).get("a_terra"):
        # Fase K, ventiduesima tornata: BASH/TRIP (helps/wimpy.txt: "if
        # the character has been knocked down... they will not be able
        # to FLEE until they stand back up").
        personaggio.msg("Sei a terra: non puoi fuggire finche' non ti rialzi!")
        return False

    uscite = [e for e in (stanza.exits if stanza else []) if not (getattr(e, "db", None) and e.db.chiusa)]
    if not uscite:
        personaggio.msg("Non c'e' via di fuga da qui!")
        return False

    uscita = None
    if direzione:
        direzione = direzione.lower()
        for e in uscite:
            nomi = [e.key.lower()] + [a.lower() for a in e.aliases.all()]
            if direzione in nomi:
                uscita = e
                break
    if not uscita:
        uscita = random.choice(uscite)

    if random.randint(1, 100) <= 25:
        personaggio.msg("Provi a fuggire ma non ci riesci!")
        return False

    personaggio.ferma_combattimento()
    stanza.msg_contents(pericolo(f"{personaggio.key} fugge verso {uscita.key}!"), exclude=[personaggio])
    personaggio.msg(pericolo(f"Fuggi verso {uscita.key}!"))

    if personaggio.db.active_profession:
        # Solo una piccola perdita fissa, senza cascata di retrocessione
        # di livello (a differenza della perdita da morte, world/
        # esperienza.py:perdi_xp_morte - la fonte non lascia intendere
        # che fuggire possa mai far perdere un livello).
        personaggio.db.xp = max(0, (personaggio.db.xp or 0) - XP_PERSA_PER_FUGA)
    equipaggiati = [o for o in (personaggio.db.equip or {}).values() if o]
    if equipaggiati:
        from world.equipment import degrada
        degrada(random.choice(equipaggiati))

    # db.insegue_chi_fugge (world/mostri.py:tenta_inseguimento): equivalente
    # ai flag HUNTER/TRACKER della fonte (immhelp_flags.txt) - Fase K,
    # pre-release: la logica e' stata generalizzata in
    # typeclasses/rooms.py:at_object_leave (scatta per QUALUNQUE uscita
    # dalla stanza, non solo per una FLEE esplicita come qui), quindi
    # questo stesso move_to la innesca automaticamente senza bisogno di
    # duplicarla in questa funzione.
    personaggio.move_to(uscita.destination, quiet=True)
    personaggio.execute_cmd("look")
    return True


def valuta_forza_relativa(osservatore, bersaglio):
    """Testo qualitativo per CONSIDER, basato su HP massimi + somma delle skill."""
    potenza_o = (osservatore.db.hp_max or 1) + sum((osservatore.db.skills or {}).values())
    potenza_b = (bersaglio.db.hp_max or 1) + sum((bersaglio.db.skills or {}).values())
    rapporto = potenza_b / max(1, potenza_o)

    if rapporto < 0.5:
        return f"{bersaglio.key} sembra una preda facile."
    if rapporto < 0.8:
        return f"{bersaglio.key} sembra alla tua portata."
    if rapporto < 1.2:
        return f"{bersaglio.key} sembra un avversario alla pari."
    if rapporto < 1.8:
        return f"{bersaglio.key} sembra piu' forte di te. Attenzione."
    return f"{bersaglio.key} ti farebbe a pezzi. Scappa finche' puoi."


DURATA_DECADIMENTO_MINUTI = 15  # confermato dalla fonte: "~30 game-hours (15 minuti reali)"


def crea_cadavere(entita, contenuto_da=None, location=None):
    """Crea un cadavere (decade da solo dopo DURATA_DECADIMENTO_MINUTI - vedi
    typeclasses.scripts.CorpseDecayScript) nella stanza indicata (default: la
    stanza dell'entita' morta). Se contenuto_da e' dato, vi sposta dentro
    tutto cio' che quell'entita' ha addosso (inventario ed equipaggiamento):
    come da sito originale, se non lo recuperi prima che il cadavere decada
    lo perdi - ma non del tutto: quando il cadavere si dissolve, il suo
    contenuto cade nella stanza (chiunque puo' raccoglierlo), non sparisce
    all'istante. Non si perde mai denaro, che resta sul personaggio."""
    cadavere = create.create_object(
        "typeclasses.objects.Corpse",
        key=f"il cadavere di {entita.key}",
        location=location or entita.location,
    )
    cadavere.db.desc = f"I resti senza vita di {entita.key}."
    cadavere.db.decadimento_minuti = DURATA_DECADIMENTO_MINUTI
    if entita.is_typeclass("typeclasses.characters.Character", exact=False):
        # Fase K, ventiseiesima tornata: helps/death.txt - "Only you or
        # someone from your group can retrieve the objects from your
        # corpse." Solo i cadaveri di GIOCATORI sono protetti cosi': i
        # cadaveri di mostri restano liberi per chiunque, come da
        # convenzione MUD (la fonte parla solo del "TUO" cadavere).
        cadavere.db.proprietario = entita
    if contenuto_da:
        for oggetto in list(contenuto_da.contents):
            oggetto.move_to(cadavere, quiet=True, move_type="drop")
        contenuto_da.db.equip = {}
    return cadavere


def gestisci_morte(vittima, uccisore=None):
    """Dispatcher di morte: gli NPC hanno un proprio at_death(); i
    personaggi giocanti seguono la procedura di respawn qui sotto."""
    vittima.ferma_combattimento()
    if uccisore:
        uccisore.ferma_combattimento()

    if hasattr(vittima, "at_death"):
        vittima.at_death(uccisore)
    else:
        _morte_personaggio(vittima, uccisore)


def _morte_personaggio(vittima, uccisore=None):
    """Morte di un personaggio giocante: come da sito originale
    (helps/death.txt), il cadavere viene "trasportato" nella stanza MORGUE
    della propria professione (assegnata in chargen, vedi
    Character.applica_professione_newbie) - non resta sul posto. Nessuna
    perdita di denaro. Respawn a piena salute nella stanza di RESPAWN della
    propria professione.

    La morte rimuove sempre lo status di criminale (helps/criminal.txt);
    se la vittima aveva una taglia, chi l'ha uccisa la incassa
    (world/pk.py). Perdita di XP legata al livello: vedi
    world/esperienza.py, perdi_xp_morte().

    Fase K, nona tornata: il flag "no_morgue" (confermato dalla fonte,
    helps/death.txt: "some areas are flagged as no_morgue, which means
    your character's corpse stays in the room where you died", verificabile
    con RAFFECTS - vedi commands/cthulhu_affects.py) e' ora rispettato: se
    la STANZA dove si muore ha db.no_morgue=True, il cadavere resta li'
    invece di essere spostato nella morgue. Nessuna area del nostro mondo
    ha ancora questo flag impostato (la fonte non specifica quali zone lo
    abbiano): pronto per quando decideremo di applicarlo a qualche zona."""
    from world.esperienza import perdi_xp_morte
    from world.pk import incassa_taglia, rimuovi_status_criminale, permapk_attivo
    from world.effetti import rimuovi_tutti_gli_effetti_magici

    if permapk_attivo():
        # helps/permapk.txt: "a player's death will result in the
        # deletion of their character from the database." Nessun
        # cadavere/respawn in questo caso - semplificazione dichiarata,
        # la fonte non descrive questo caso limite nel dettaglio.
        if vittima.location:
            vittima.location.msg_contents(pericolo(f"{vittima.key} muore, per sempre."), exclude=[vittima])
        vittima.msg(pericolo("PERMAPK e' attiva: la tua morte e' permanente. Il personaggio viene cancellato."))
        vittima.delete()
        return

    rimuovi_status_criminale(vittima)
    rimuovi_tutti_gli_effetti_magici(vittima)
    if uccisore is not None and hasattr(uccisore, "db"):
        incassa_taglia(uccisore, vittima)
        if uccisore.db.active_profession:
            # world/quest.py: contatore per l'impresa deed_3796 ("Ha
            # compiuto un sacrificio degno a Thanatos") - solo le uccisioni
            # di un altro personaggio giocante contano.
            uccisore.db.omicidi_pk = (uccisore.db.omicidi_pk or 0) + 1

    luogo_morte = vittima.location
    if luogo_morte and luogo_morte.db.no_morgue:
        destinazione_cadavere = luogo_morte
    else:
        destinazione_cadavere = vittima.db.morgue_room or luogo_morte
    cadavere = crea_cadavere(vittima, contenuto_da=vittima, location=destinazione_cadavere)
    if luogo_morte:
        if destinazione_cadavere != luogo_morte:
            luogo_morte.msg_contents(pericolo(f"{vittima.key} muore! Il corpo viene portato via."))
        else:
            luogo_morte.msg_contents(pericolo(f"{vittima.key} muore!"))

    messaggio_xp = perdi_xp_morte(vittima)
    if messaggio_xp:
        vittima.msg(messaggio_xp)
    if destinazione_cadavere and destinazione_cadavere != luogo_morte:
        destinazione_cadavere.msg_contents(f"{cadavere.key} arriva.")

    vittima.msg(orrore("Sei morto! Il mondo si dissolve in un vortice di follia..."))

    vittima.db.hp = vittima.db.hp_max
    vittima.db.mana = vittima.db.mana_max
    vittima.db.move = vittima.db.move_max

    destinazione = vittima.db.respawn_room or vittima.db.recall_room
    if destinazione:
        vittima.move_to(destinazione, quiet=True)
    vittima.msg("Ti risvegli, vivo ma scosso.")
    vittima.execute_cmd("look")
