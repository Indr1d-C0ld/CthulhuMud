"""
Lancio degli incantesimi (M5). Vedi world/spells.py per il registro e la
nota sulle formule non documentate dal sito originale.

Nota sugli script di stato: quando un incantesimo curativo annulla una
condizione (veleno, malattia, maledizione, invisibilita'...) il relativo
script va rimosso con `.delete()` e MAI con `.stop()`. In Evennia 6.1
`.stop()` disattiva lo script ma ne lascia la riga nel database: prima
dell'audit qui c'erano nove `.stop()`, e ogni cura lanciata in partita
lasciava dietro di se' una riga morta. Stessa regola gia' documentata in
world/effetti.py e world/sottorazze.py.

Requisiti per lanciare (Dossier Miskatonic §4, Newbie School):
  1. skill "spell_casting" > 0
  2. skill specifica dell'incantesimo > 0
  3. mana sufficiente (il costo base scala in giu' con la skill, vedi
     _costo_effettivo)
Il successo dipende dalla media delle due skill (piu' un piccolo
contributo di Maestria negli Incantesimi); il mana si consuma anche in
caso di fallimento o interruzione (scelta di design, come da
convenzione DikuMUD).

Fase K, ventitreesima tornata - meccanica di lancio non istantanea
(confermata da helps/spell_casting.txt, mai implementata prima d'ora
nonostante fosse gia' descritta verbatim in world/skills.py alla voce
"spell_casting"): lanciare un incantesimo ora richiede TEMPO_LANCIO_SECONDI
di "canalizzazione" (db.incantesimo_in_corso) prima che l'effetto si
risolva davvero. Durante questo intervallo:
  - STAND interrompe il lancio (vedi world/posizione.py:tenta_stand);
  - cambiare stanza lo interrompe (vedi typeclasses/living.py:at_after_move);
  - subire un colpo in combattimento puo' interromperlo (vedi
    typeclasses/living.py:subisci_danno - probabilita' dichiarata,
    nessuna formula nella fonte).
Un'interruzione ha una probabilita' (anch'essa dichiarata) di lasciare
il lanciatore "affaticato" (stato temporaneo, curabile anzitempo con
l'incantesimo Ristoro - vedi _effetto_refresh). Da non confondere con
l'incantesimo offensivo "fatigue" (_effetto_fatigue), che indebolisce
un NEMICO drenandogli movimento e Forza: due meccaniche diverse che
condividono solo il nome italiano.

Tiro salvezza del bersaglio (confermato da helps/spell_casting.txt: "the
target character will usually make a saving roll... and the effectiveness
... will be modified accordingly"): applicato solo agli incantesimi
marcati "ostile": True in world/spells.py (bersaglio non consenziente).
Semplificazione dichiarata: qui il salvataggio e' un tutto-o-niente
(resiste = nessun effetto) invece di una riduzione percentuale continua
dell'efficacia - ritoccare l'entita' esatta del danno/durata avrebbe
richiesto aggiungere un parametro a tutte le ~235 funzioni _effetto_*,
sproporzionato rispetto al guadagno di fedelta'.

Costo in sanity per certi incantesimi (Fase K, venticinquesima tornata,
audit del sistema di sanity - confermato da helps/sanity.txt: "casting
certain spells decreases it"): la fonte non elenca quali. Qui si e'
scelto di farlo costare alle famiglie di incantesimi piu' esplicitamente
legate a conoscenza proibita/orrore cosmico nel registro (vedi
FAMIGLIE_MAGIA_PROIBITA) - una scelta di design dichiarata, a livello di
FAMIGLIA (skill_richiesta) e non di singolo incantesimo, diversamente
dal tag "ostile" che e' per singolo incantesimo. Costa alla sola
CANALIZZAZIONE (fase 1, insieme al mana), non al successo dell'effetto -
stessa logica del mana speso anche in caso di fallimento/interruzione.
"""

import random

from world.spells import SPELLS, nome_incantesimo
from world.skills import nome_skill
from world.colori import magia, onirico, orrore, pericolo

TEMPO_LANCIO_SECONDI = 2
PROBABILITA_INTERRUZIONE_COMBATTIMENTO = 40
PROBABILITA_AFFATICAMENTO_SU_INTERRUZIONE = 50
DURATA_AFFATICAMENTO_SECONDI = 60
RIDUZIONE_MANA_MASSIMA = 0.5  # -50% al costo base con skill specifica 100+
BONUS_RITUALE_PER_MEMBRO = 5  # % successo extra per alleato con Maestria nei Rituali in stanza

FAMIGLIE_MAGIA_PROIBITA = {
    "necromancy", "elder_magic", "chaos_magic",
    "way_of_the_conjurer", "voodoo", "divine_magic",
}
COSTO_SANITA_MAGIA_PROIBITA = (1, 3)


def _costo_sanita_proibita(spell):
    if spell["skill_richiesta"] in FAMIGLIE_MAGIA_PROIBITA:
        return random.randint(*COSTO_SANITA_MAGIA_PROIBITA)
    return 0


def _costo_effettivo(caster, spell):
    """Il costo in mana scende con la skill specifica dell'incantesimo
    (confermato dalla fonte), fino a RIDUZIONE_MANA_MASSIMA a rating 100+.
    Nessuna formula pubblicata: proporzione lineare scelta per coerenza
    con le altre formule non documentate del progetto."""
    rating_specifico = caster.skill_rating(spell["skill_richiesta"])
    riduzione = min(rating_specifico, 100) / 100 * RIDUZIONE_MANA_MASSIMA
    return max(1, round(spell["costo_mana"] * (1 - riduzione)))


def _bonus_rituale(caster):
    """RITUAL (helps/ritual_mastery.txt): piu' potente lanciato in GROUP
    con altri possessori di Maestria nei Rituali, tanto piu' quanti sono.
    Nessuna formula nella fonte: qui e' un bonus percentuale al successo,
    +BONUS_RITUALE_PER_MEMBRO per ogni alleato con la skill presente
    nella stanza - stessa scelta di design di world/gruppo.py:
    bonus_gruppo_colpire (bonus fisso per membro, niente di piu' fine)."""
    from world.gruppo import membri_gruppo
    alleati = [
        m for m in membri_gruppo(caster)
        if m is not caster and m.location == caster.location and m.skill_rating("ritual_mastery") > 0
    ]
    return BONUS_RITUALE_PER_MEMBRO * len(alleati)


def tiro_salvezza(bersaglio, caster, spell_id):
    """Tiro salvezza opposto (stessa filosofia generale dei controlli di
    skill descritta da helps/skills.txt: "an open-ended d100 roll... is
    compared to... a skill roll made by your opponent"). Il bersaglio usa
    Autodisciplina (gia' descritta in world/skills.py come fonte di
    "resistenza alla magia", mai agganciata a nulla finora) piu' meta'
    della Saggezza; il lanciatore usa la stessa media di skill che decide
    il successo del lancio. True se il bersaglio resiste.

    Difetto corretto in audit: qui si leggeva `bersaglio.db.wis`, un
    attributo che nessuno scrive mai - gli attributi del personaggio
    stanno in `attributes.get("stat_<nome>", category="cthulhu")` e si
    leggono con valore_attributo(). Il risultato era che la Saggezza
    valeva sempre 10 per chiunque: un personaggio con Saggezza 18
    resisteva alla magia esattamente come uno con Saggezza 3, e la meta'
    "Saggezza" del tiro salvezza descritta qui sopra non esisteva.
    Il ripiego a 10 resta per i bersagli privi del metodo (gli NPC non
    hanno attributi tirati), come gia' si fa in typeclasses/living.py."""
    spell = SPELLS[spell_id]
    rating_lanciatore = (caster.skill_rating("spell_casting") + caster.skill_rating(spell["skill_richiesta"])) / 2
    tiro_lanciatore = random.uniform(0, 100) + rating_lanciatore
    saggezza = (bersaglio.valore_attributo("wis")
                if hasattr(bersaglio, "valore_attributo") else 10)
    tiro_bersaglio = (
        random.uniform(0, 100)
        + bersaglio.skill_rating("self_discipline")
        + saggezza / 2
    )
    return tiro_bersaglio > tiro_lanciatore


def lancia_incantesimo(caster, spell_id, bersaglio=None, testo=None, rituale=False):
    """Avvia il lancio (fase 1): valida i requisiti, addebita il mana e
    programma la risoluzione dopo TEMPO_LANCIO_SECONDI. Ritorna
    (ok: bool, messaggio_per_il_caster: str|None)."""
    spell = SPELLS.get(spell_id)
    if not spell:
        return False, "Incantesimo sconosciuto."

    if caster.db.incantesimo_in_corso:
        return False, "Stai gia' lanciando un incantesimo."

    if caster.skill_rating("spell_casting") <= 0:
        return False, "Non conosci l'arte del Lancio degli Incantesimi."

    skill_id = spell["skill_richiesta"]
    rating_specifico = caster.skill_rating(skill_id)
    if rating_specifico <= 0:
        return False, f"Non conosci ancora {nome_skill(skill_id)}."

    if rituale and caster.skill_rating("ritual_mastery") <= 0:
        return False, "Non conosci la Maestria nei Rituali."

    if spell.get("bersaglio_richiesto") and not bersaglio:
        return False, "Questo incantesimo richiede un bersaglio."
    if spell.get("richiede_testo") and not testo:
        return False, "Questo incantesimo richiede un'indicazione (es. una direzione)."

    costo = _costo_effettivo(caster, spell)
    if (caster.db.mana or 0) < costo:
        return False, "Non hai abbastanza mana."
    caster.db.mana -= costo

    costo_sanita = _costo_sanita_proibita(spell)
    if costo_sanita and caster.db.sanity is not None:
        caster.db.sanity = max(0, (caster.db.sanity or 0) - costo_sanita)
        caster.msg(
            magia(
                f"Il solo canalizzare {nome_incantesimo(spell_id)} ti scuote nel profondo "
                f"(-{costo_sanita} sanity)."
            )
        )

    caster.db.incantesimo_in_corso = {
        "spell_id": spell_id, "bersaglio": bersaglio, "testo": testo, "rituale": rituale,
    }
    verbo = "un rituale per lanciare" if rituale else "a lanciare"
    caster.location.msg_contents(
        magia(f"{caster.key} comincia {verbo} {nome_incantesimo(spell_id)}.")
    )

    from evennia.utils import delay
    delay(TEMPO_LANCIO_SECONDI, _completa_lancio, caster)
    return True, None


def _completa_lancio(caster):
    """Fase 2, eseguita dopo TEMPO_LANCIO_SECONDI: se il lancio non e'
    stato interrotto nel frattempo (db.incantesimo_in_corso azzerato da
    interrompi_lancio), risolve successo/fallimento e l'eventuale tiro
    salvezza del bersaglio."""
    dati = caster.db.incantesimo_in_corso
    if not dati:
        return
    caster.db.incantesimo_in_corso = None
    spell_id, bersaglio, testo = dati["spell_id"], dati["bersaglio"], dati["testo"]
    spell = SPELLS[spell_id]
    if bersaglio is not None and not bersaglio.pk:
        caster.msg("Il bersaglio non e' piu' disponibile.")
        return

    rating_casting = caster.skill_rating("spell_casting")
    rating_specifico = caster.skill_rating(spell["skill_richiesta"])
    rating_mastery = caster.skill_rating("spell_mastery")
    # world/sottorazze.py: LICH EMPOWER - "empowers all of your spells"
    # (Fase K, ventiseiesima tornata: prima un campo mai letto da nessuno).
    bonus_lich = caster.db.bonus_incantesimi or 0
    percentuale_successo = max(5, min(95, (rating_casting + rating_specifico) / 2 + rating_mastery / 10 + bonus_lich))
    if dati.get("rituale"):
        percentuale_successo = min(95, percentuale_successo + _bonus_rituale(caster))
    if random.uniform(0, 100) > percentuale_successo:
        caster.location.msg_contents(magia(
            f"{caster.key} tenta di lanciare {nome_incantesimo(spell_id)}, ma l'incantesimo fallisce."
        ))
        return

    if spell.get("ostile") and bersaglio is not None and bersaglio is not caster:
        if tiro_salvezza(bersaglio, caster, spell_id):
            bersaglio.msg(magia(f"Resisti agli effetti di {nome_incantesimo(spell_id)}!"))
            caster.msg(magia(f"{bersaglio.key} resiste al tuo incantesimo."))
            return

    _esegui_effetto(spell_id, caster, bersaglio, testo)


def interrompi_lancio(caster, messaggio_caster=None):
    """Annulla un lancio in corso (STAND, cambio stanza, colpo subito in
    combattimento). Ritorna True se c'era davvero un lancio da annullare.
    Il mana speso non viene restituito (stessa convenzione del fallimento
    normale). Applica una possibilita' di affaticamento."""
    if not caster.db.incantesimo_in_corso:
        return False
    caster.db.incantesimo_in_corso = None
    if messaggio_caster:
        caster.msg(messaggio_caster)
    if random.uniform(0, 100) <= PROBABILITA_AFFATICAMENTO_SU_INTERRUZIONE:
        from world.effetti import applica_stato
        applica_stato(caster, "affaticato", DURATA_AFFATICAMENTO_SECONDI, "Non sei piu' affaticato/a.")
        caster.msg(magia("L'interruzione ti lascia affaticato/a."))
    return True


def _esegui_effetto(spell_id, caster, bersaglio, testo):
    funzione = _EFFETTI.get(spell_id)
    if funzione:
        funzione(caster, bersaglio, testo)
    else:
        # Fase K, sesta tornata: tutti i 102 incantesimi registrati hanno
        # ormai una funzione in _EFFETTI - questo ramo resta solo come rete
        # di sicurezza per un futuro incantesimo aggiunto a world/spells.py
        # senza ancora una funzione dedicata (meglio un messaggio onesto
        # che un lancio silenzioso senza alcun effetto visibile).
        caster.location.msg_contents(magia(
            f"{caster.key} lancia {nome_incantesimo(spell_id)} con successo, ma la sua "
            "meccanica completa non e' ancora stata implementata in questo porting."
        ))


def _effetto_cure_light(caster, bersaglio, testo):
    cura = random.randint(4, 10)
    bersaglio.db.hp = min(bersaglio.db.hp_max, (bersaglio.db.hp or 0) + cura)
    if bersaglio is caster:
        caster.location.msg_contents(magia(
            f"Una luce calda avvolge {caster.key}, che recupera {cura} HP."
        ))
    else:
        caster.location.msg_contents(magia(
            f"{caster.key} lancia Cura Leggera su {bersaglio.key}, che recupera {cura} HP."
        ))


def _effetto_shocking_grasp(caster, bersaglio, testo):
    danno = random.randint(6, 14)
    caster.location.msg_contents(magia(
        f"{caster.key} scarica un fulmine dalle dita su {bersaglio.key} per {danno} danni!"
    ))
    morto = bersaglio.subisci_danno(danno, fisico=False)
    if morto:
        from world.combat import gestisci_morte
        gestisci_morte(bersaglio, caster)
    elif not bersaglio.db.combat_target:
        bersaglio.avvia_combattimento(caster)


def _effetto_bless(caster, bersaglio, testo):
    bersaglio.db.bonus_colpire = (bersaglio.db.bonus_colpire or 0) + 15
    if not bersaglio.scripts.get("bless_expire"):
        bersaglio.scripts.add("typeclasses.scripts.BlessExpireScript")
    caster.location.msg_contents(magia(
        f"{bersaglio.key} viene avvolto/a da una luce dorata: colpira' con piu' facilita'."
    ))


def _effetto_detect_magic(caster, bersaglio, testo):
    caster.msg(
        "Ti concentri, ma per ora non percepisci nulla di magicamente significativo nei "
        "dintorni. (il sistema di oggetti magici arrivera' in una fase successiva)"
    )


def _effetto_mask_self(caster, bersaglio, testo):
    if caster.db.maschera:
        caster.db.maschera = None
        caster.location.msg_contents(magia(f"L'illusione attorno a {caster.key} svanisce."))
    else:
        caster.db.maschera = "una figura incappucciata dai lineamenti indistinti"
        caster.location.msg_contents(magia(
            f"{caster.key} si avvolge in un'illusione che ne offusca l'aspetto."
        ))


def _effetto_clairvoyance(caster, bersaglio, testo):
    stanza = caster.location
    uscita = None
    for e in stanza.exits:
        nomi = [e.key.lower()] + [a.lower() for a in e.aliases.all()]
        if testo.lower() in nomi:
            uscita = e
            break
    if not uscita:
        caster.msg("Non vedi nulla di particolare in quella direzione.")
        return
    dest = uscita.destination
    caster.msg(magia(f"Con la mente vedi: |w{dest.key}|n\n{dest.db.desc}"))


######################################################################
# Fase K, sesta tornata: effetti meccanici reali per i 96 incantesimi
# che fino a questa tornata mostravano solo un messaggio di successo
# senza conseguenze (limite dichiarato dalla Fase G in poi). Nessuna
# formula qui e' pubblicata dalla fonte (stesso caso di tutto il resto
# del combattimento, vedi typeclasses/living.py): numeri scelti per
# coerenza di scala con gli incantesimi/skill gia' calibrati. Vedi
# world/effetti.py per i tre meccanismi generici riusati qui
# (modificatori temporanei, stati con scadenza, danno/cura periodici)
# e server/conf/lockfuncs.py per l'invisibilita' vera via lock.
######################################################################

from world.effetti import (
    applica_buff_temporaneo, applica_stato, rimuovi_stato, ha_stato,
    applica_danno_periodico, applica_cura_periodica, rendi_invisibile,
)


def _infliggi_danno_magico(caster, bersaglio, danno, verbo):
    """Helper condiviso da tutti gli incantesimi d'attacco: applica la
    riduzione della classe armatura (fisica + scudi magici temporanei)
    e dell'eventuale Assorbimento Magico, poi gestisce morte/ingaggio -
    la stessa logica che _effetto_shocking_grasp gia' scriveva a mano,
    centralizzata per non ripeterla in 30 funzioni diverse."""
    from world.equipment import classe_armatura_totale
    riduzione = (classe_armatura_totale(bersaglio) + (bersaglio.db.bonus_ca_temp or 0)) // 4
    danno_finale = max(1, danno - riduzione)
    if ha_stato(bersaglio, "assorbe_magia"):
        danno_finale = max(1, danno_finale // 2)
    caster.location.msg_contents(magia(f"{bersaglio.key} {verbo} per {danno_finale} danni!"))
    morto = bersaglio.subisci_danno(danno_finale, fisico=False)
    if morto:
        from world.combat import gestisci_morte
        gestisci_morte(bersaglio, caster)
    elif not bersaglio.db.combat_target and bersaglio is not caster:
        bersaglio.avvia_combattimento(caster)
    return danno_finale


def _danno_area(caster, danno_min, danno_max, verbo, includi_caster=False):
    """Colpisce tutti i presenti vivi nella stanza (Fulmine a Catena,
    Richiamo del Fulmine, Soffio di Gas, Terremoto)."""
    stanza = caster.location
    presenti = [o for o in list(stanza.contents) if getattr(o, "vivo", None) is not None]
    for bersaglio in presenti:
        if bersaglio is caster and not includi_caster:
            continue
        if not bersaglio.vivo:
            continue
        danno = random.randint(danno_min, danno_max)
        _infliggi_danno_magico(caster, bersaglio, danno, verbo)


def _cura(caster, bersaglio, quantita, nome_incant):
    prima = bersaglio.db.hp or 0
    bersaglio.db.hp = min(bersaglio.db.hp_max, prima + quantita)
    guarito = bersaglio.db.hp - prima
    if bersaglio is caster:
        caster.location.msg_contents(magia(f"Una luce calda avvolge {caster.key}, che recupera {guarito} HP."))
    else:
        caster.location.msg_contents(magia(
            f"{caster.key} lancia {nome_incant} su {bersaglio.key}, che recupera {guarito} HP."
        ))


def _cura_area(caster, quantita_min, quantita_max, nome_incant):
    """Cura tutti i presenti nella stanza tranne i nemici diretti del
    lanciatore - una euristica piu' ampia del solo gruppo (world/gruppo.py,
    Fase K tredicesima tornata), scelta perche' la fonte non limita
    esplicitamente le cure d'area ai soli compagni di gruppo."""
    stanza = caster.location
    for bersaglio in list(stanza.contents):
        if not getattr(bersaglio, "vivo", None):
            continue
        if bersaglio is caster.db.combat_target or bersaglio.db.combat_target is caster:
            continue
        _cura(caster, bersaglio, random.randint(quantita_min, quantita_max), nome_incant)


# --- incantesimi d'attacco, bersaglio singolo -----------------------

def _effetto_acid_blast(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(15, 25), "viene ustionato/a da un getto d'acido")


def _effetto_acid_breath(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(18, 26), "viene investito/a da un soffio d'acido")


def _effetto_burning_hands(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(10, 18), "viene avvolto/a da una vampata di fiamme")


def _effetto_cause_light(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(5, 10), "viene colpito/a da una fitta di dolore")


def _effetto_cause_serious(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(12, 20), "viene colpito/a da un'ondata di dolore")


def _effetto_cause_critical(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(20, 30), "viene straziato/a da un dolore atroce")


def _effetto_harm(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(30, 45), "viene devastato/a da un dolore insopportabile")


def _effetto_chill_touch(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(8, 14), "viene raggelato/a da un tocco gelido")
    applica_buff_temporaneo(bersaglio, "mod_temp_str", -3, 30,
                             f"{bersaglio.key} riprende la propria Forza.")


def _effetto_colour_spray(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(12, 20), "viene investito/a da lampi di colore accecanti")


def _effetto_demonfire(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(20, 30), "viene dilaniato/a da un'orda di demoni")


def _effetto_fire_breath(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(18, 26), "viene investito/a da un soffio infuocato")


def _effetto_frost_breath(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(18, 26), "viene investito/a da un soffio gelido")


def _effetto_lightning_breath(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(18, 26), "viene investito/a da un soffio fulminante")


def _effetto_fireball(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(25, 35), "viene investito/a da una palla di fuoco")


def _effetto_lightning_bolt(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(15, 25), "viene colpito/a da un fulmine crepitante")


def _effetto_magic_missile(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(10, 16), "viene colpito/a da una raffica di missili magici")


def _effetto_magefire(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(20, 30), "viene bruciato/a da energia arcana")
    # confermato dalla fonte: rimuove le protezioni magiche attive sul bersaglio
    bersaglio.db.bonus_colpire = 0
    bersaglio.db.bonus_danno_temp = 0
    bersaglio.db.bonus_ca_temp = 0


def _effetto_energy_drain(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(10, 16), "sente la propria energia vitale defluire")
    bersaglio.db.mana = max(0, (bersaglio.db.mana or 0) - 15)
    bersaglio.db.move = max(0, (bersaglio.db.move or 0) - 15)
    if bersaglio.db.xp:
        bersaglio.db.xp = max(0, bersaglio.db.xp - 20)


def _effetto_dispel_evil(caster, bersaglio, testo):
    if (bersaglio.db.alignment or 0) >= 0:
        caster.msg(f"{bersaglio.key} non e' abbastanza malvagio/a perche' l'incantesimo abbia effetto.")
        return
    _infliggi_danno_magico(caster, bersaglio, random.randint(15, 25), "viene bruciato/a dalla collera divina")


def _effetto_dispel_good(caster, bersaglio, testo):
    if (bersaglio.db.alignment or 0) <= 0:
        caster.msg(f"{bersaglio.key} non e' abbastanza benevolo/a perche' l'incantesimo abbia effetto.")
        return
    _infliggi_danno_magico(caster, bersaglio, random.randint(15, 25), "viene bruciato/a dalla collera divina")


# --- incantesimi d'attacco ad area -----------------------------------

def _effetto_call_lightning(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} richiama un fulmine dal cielo!"))
    _danno_area(caster, 15, 25, "viene colpito/a dal fulmine")


def _effetto_chain_lightning(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} scatena un fulmine che rimbalza per la stanza!"))
    _danno_area(caster, 10, 18, "viene colpito/a dal fulmine a catena", includi_caster=True)


def _effetto_gas_breath(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} esala una nube di gas tossico!"))
    _danno_area(caster, 15, 22, "viene soffocato/a dal gas")


def _effetto_earthquake(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} scatena un violento terremoto!"))
    _danno_area(caster, 15, 25, "viene travolto/a dallo sconquasso")


# --- guarigione -------------------------------------------------------

def _effetto_cure_serious(caster, bersaglio, testo):
    _cura(caster, bersaglio, random.randint(15, 25), "Cura Ferita Grave")


def _effetto_cure_critical(caster, bersaglio, testo):
    _cura(caster, bersaglio, random.randint(25, 38), "Cura Ferita Critica")


def _effetto_heal(caster, bersaglio, testo):
    _cura(caster, bersaglio, random.randint(40, 60), "Guarigione")


def _effetto_mass_healing(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} irradia energia curativa in ogni direzione!"))
    _cura_area(caster, 15, 25, "Guarigione di Massa")


def _effetto_regeneration(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{bersaglio.key} inizia a guarire a vista d'occhio."))
    applica_cura_periodica(bersaglio, 5, 10, 10, 6, messaggio_tick="Ti senti rigenerare ({danno} HP).")


# --- buff (modificatori temporanei) -----------------------------------

def _effetto_haste(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "mod_temp_dex", 8, 60,
                             f"{bersaglio.key} rallenta, tornando alla propria velocita' naturale.")
    caster.location.msg_contents(magia(f"{bersaglio.key} si muove all'improvviso con innaturale rapidita'."))


def _effetto_strength(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "mod_temp_str", 5, 60,
                             f"{bersaglio.key} riprende la propria Forza naturale.")
    caster.location.msg_contents(magia(f"I muscoli di {bersaglio.key} si gonfiano di forza innaturale."))


def _effetto_weaken(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "mod_temp_str", -6, 30,
                             f"{bersaglio.key} riprende la propria Forza.")
    caster.location.msg_contents(magia(f"{bersaglio.key} sente le proprie forze abbandonarlo/a."))
    if not bersaglio.db.combat_target and bersaglio is not caster:
        bersaglio.avvia_combattimento(caster)


def _effetto_age(caster, bersaglio, testo):
    danno = random.randint(4, 8)
    _infliggi_danno_magico(caster, bersaglio, danno, "invecchia visibilmente, sentendo le ossa scricchiolare")
    applica_buff_temporaneo(bersaglio, "mod_temp_con", -4, 120,
                             f"{bersaglio.key} riprende vigore, tornando alla propria eta'.")


def _effetto_youth(caster, bersaglio, testo):
    rimuovi_stato(bersaglio, "invecchiato")  # per simmetria, se mai impostato altrove
    for script in bersaglio.scripts.get("buff_mod_temp_con"):
        script.delete()
    bersaglio.db.mod_temp_con = 0
    _cura(caster, bersaglio, random.randint(10, 20), "Giovinezza")
    caster.location.msg_contents(magia(f"{bersaglio.key} ringiovanisce a vista d'occhio."))


def _effetto_harden_skin(caster, bersaglio, testo):
    # Fase K, sesta tornata, correzione: "bersaglio_richiesto" e' False per
    # tutti i buff auto-lanciabili (CmdCast non imposta bersaglio=caster
    # a meno che sia True) - qui il default e' sempre il lanciatore stesso,
    # a meno che sia stato specificato un bersaglio testuale (un alleato).
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 15, 90,
                             f"La pelle indurita di {bersaglio.key} torna normale.")
    caster.location.msg_contents(magia(f"La pelle di {bersaglio.key} si indurisce come corteccia."))


def _effetto_elemental_shield(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 20, 90,
                             f"Lo scudo elementale attorno a {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Un velo elementale avvolge {bersaglio.key}."))


def _effetto_shield(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 30, 90,
                             f"Lo scudo magico attorno a {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Una sfera di energia arcana avvolge {bersaglio.key}."))


def _effetto_lesser_protection(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 10, 90,
                             f"La protezione minore attorno a {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Una debole aura protettiva avvolge {bersaglio.key}."))


def _effetto_absorb_magic(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_stato(bersaglio, "assorbe_magia", 90,
                  f"{bersaglio.key} non e' piu' protetto/a dall'Assorbimento Magico.")
    caster.location.msg_contents(magia(f"{bersaglio.key} si avvolge in un velo che assorbe la magia."))


def _effetto_protection_evil(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_stato(bersaglio, "protetto_da_male", 120,
                  f"La Protezione dal Male attorno a {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Un'aura sacra avvolge {bersaglio.key}, respingendo il male."))


def _effetto_protection_good(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_stato(bersaglio, "protetto_da_bene", 120,
                  f"La Protezione dal Bene attorno a {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Un'aura oscura avvolge {bersaglio.key}, respingendo il bene."))


def _effetto_frenzy(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "bonus_colpire", 20, 60,
                             f"{bersaglio.key} si calma, uscendo dalla frenesia.")
    applica_buff_temporaneo(bersaglio, "bonus_danno_temp", 6, 60, None)
    applica_stato(bersaglio, "furia", 60, None)
    caster.location.msg_contents(magia(f"{bersaglio.key} viene colto/a da una furia insana!"))


def _effetto_fly(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_stato(bersaglio, "vola", 300, f"{bersaglio.key} ridiscende a terra.")
    caster.location.msg_contents(magia(f"{bersaglio.key} si solleva lentamente da terra."))


def _effetto_water_breathing(caster, bersaglio, testo):
    applica_stato(bersaglio, "respira_in_acqua", 300, f"{bersaglio.key} non puo' piu' respirare sott'acqua.")
    caster.location.msg_contents(magia(f"{bersaglio.key} potra' respirare sott'acqua per un po'."))


def _effetto_vocalize(caster, bersaglio, testo):
    applica_stato(bersaglio, "vocalizzato", 300, f"{bersaglio.key} torna a dover parlare per lanciare incantesimi.")
    caster.location.msg_contents(magia(f"{bersaglio.key} ora puo' lanciare incantesimi senza pronunciare parola."))


# --- debuff / stati negativi -------------------------------------------

def _effetto_blindness(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(2, 5), "viene accecato/a da un lampo di luce")
    applica_stato(bersaglio, "cieco", 60, f"{bersaglio.key} recupera la vista.")


def _effetto_cure_blindness(caster, bersaglio, testo):
    if not ha_stato(bersaglio, "cieco"):
        caster.msg(f"{bersaglio.key} non e' accecato/a.")
        return
    rimuovi_stato(bersaglio, "cieco")
    caster.location.msg_contents(magia(f"{bersaglio.key} recupera la vista."))


def _effetto_curse(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "bonus_colpire", -15, 90,
                             f"La maledizione su {bersaglio.key} svanisce.")
    applica_stato(bersaglio, "maledetto", 90, None)
    caster.location.msg_contents(magia(f"L'anima di {bersaglio.key} si macchia di una maledizione."))


def _effetto_remove_curse(caster, bersaglio, testo):
    if not ha_stato(bersaglio, "maledetto"):
        caster.msg(f"{bersaglio.key} non e' maledetto/a.")
        return
    rimuovi_stato(bersaglio, "maledetto")
    for script in bersaglio.scripts.get("buff_bonus_colpire"):
        script.delete()
    caster.location.msg_contents(magia(f"La maledizione su {bersaglio.key} viene spezzata."))


def _effetto_mute(caster, bersaglio, testo):
    applica_stato(bersaglio, "muto", 60, f"{bersaglio.key} ritrova la voce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} scopre di non riuscire piu' a parlare!"))


def _effetto_sleep(caster, bersaglio, testo):
    applica_stato(bersaglio, "addormentato", 30, f"{bersaglio.key} si risveglia di soprassalto.")
    caster.location.msg_contents(magia(f"{bersaglio.key} crolla in un sonno innaturale."))


def _effetto_charm_person(caster, bersaglio, testo):
    # Fase K, nona tornata: ora si aggancia al vero sistema di seguaci/
    # ORDER (world/seguaci.py) - il bersaglio segue davvero il lanciatore
    # ed e' comandabile con ORDER, non solo "non ostile", per la durata
    # dell'incantesimo (rimosso dai seguaci alla scadenza).
    if bersaglio.db.combat_target is caster:
        bersaglio.ferma_combattimento()
    bersaglio.db.ostile = False
    bersaglio.db.padrone = caster
    seguaci = caster.db.seguaci or []
    if bersaglio not in seguaci:
        seguaci.append(bersaglio)
    caster.db.seguaci = seguaci

    def _fine_ammaliamento():
        if bersaglio.pk:
            bersaglio.db.padrone = None
            seguaci_attuali = [s for s in (caster.db.seguaci or []) if s is not bersaglio]
            caster.db.seguaci = seguaci_attuali
        bersaglio.msg(magia(f"{bersaglio.key} torna diffidente nei tuoi confronti."))

    applica_stato(bersaglio, "ammaliato", 180, None)
    from evennia.utils import delay
    delay(180, _fine_ammaliamento)
    caster.location.msg_contents(magia(f"Lo sguardo di {bersaglio.key} si fa vitreo e ammaliato: ora ti segue."))


def _effetto_calm(caster, bersaglio, testo):
    # A differenza degli altri buff senza bersaglio esplicito, Calma per
    # sua natura serve a placare un NEMICO (riduce la sua furia/capacita'
    # di colpire) - se non specificato, il default sensato e' il proprio
    # avversario attuale, non se stessi.
    bersaglio = bersaglio or caster.db.combat_target
    if not bersaglio:
        caster.msg("Non stai combattendo nessuno da calmare.")
        return
    if bersaglio.db.combat_target:
        bersaglio.ferma_combattimento()
    rimuovi_stato(bersaglio, "furia")
    rimuovi_stato(bersaglio, "impaurito")
    applica_buff_temporaneo(bersaglio, "bonus_colpire", -10, 30, None)
    caster.location.msg_contents(magia(f"Un'onda di quiete pervade {bersaglio.key}, che si calma."))


def _effetto_remove_fear(caster, bersaglio, testo):
    if not ha_stato(bersaglio, "impaurito"):
        caster.msg(f"{bersaglio.key} non e' impaurito/a.")
        return
    rimuovi_stato(bersaglio, "impaurito")
    caster.location.msg_contents(magia(f"{bersaglio.key} ritrova il coraggio."))


def _effetto_poison(caster, bersaglio, testo):
    applica_danno_periodico(bersaglio, "avvelenato", 3, 6, 15, 4,
                             messaggio_tick="Il veleno ti morde dall'interno ({danno} danni).",
                             messaggio_fine=f"{bersaglio.key} smette di soffrire per il veleno.")
    caster.location.msg_contents(magia(f"{bersaglio.key} viene avvelenato/a!"))
    if not bersaglio.db.combat_target and bersaglio is not caster:
        bersaglio.avvia_combattimento(caster)


def _effetto_cure_poison(caster, bersaglio, testo):
    if not ha_stato(bersaglio, "avvelenato"):
        caster.msg(f"{bersaglio.key} non e' avvelenato/a.")
        return
    for script in bersaglio.scripts.get("periodico_avvelenato"):
        script.delete()
    rimuovi_stato(bersaglio, "avvelenato")
    caster.location.msg_contents(magia(f"Il veleno abbandona il corpo di {bersaglio.key}."))


def _effetto_plague(caster, bersaglio, testo):
    applica_danno_periodico(bersaglio, "malato", 4, 8, 20, 5,
                             messaggio_tick="La malattia ti consuma ({danno} danni).",
                             messaggio_fine=f"{bersaglio.key} guarisce spontaneamente dalla malattia.")
    caster.location.msg_contents(magia(f"{bersaglio.key} viene infettato/a da una malattia virulenta!"))
    if not bersaglio.db.combat_target and bersaglio is not caster:
        bersaglio.avvia_combattimento(caster)


def _effetto_cure_disease(caster, bersaglio, testo):
    if not ha_stato(bersaglio, "malato"):
        caster.msg(f"{bersaglio.key} non e' malato/a.")
        return
    for script in bersaglio.scripts.get("periodico_malato"):
        script.delete()
    rimuovi_stato(bersaglio, "malato")
    caster.location.msg_contents(magia(f"La malattia abbandona il corpo di {bersaglio.key}."))


def _effetto_faerie_fire(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", -20, 60,
                             f"Il bagliore fatato attorno a {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Un bagliore fatato avvolge {bersaglio.key}, rendendolo/a un bersaglio piu' facile."))


# --- dissoluzioni / dispel ------------------------------------------

def _dissolvi_tutto(bersaglio):
    bersaglio.db.bonus_colpire = 0
    bersaglio.db.bonus_danno_temp = 0
    bersaglio.db.bonus_ca_temp = 0
    for attr in ("str", "dex", "con", "int", "wis"):
        setattr(bersaglio.db, f"mod_temp_{attr}", 0)
    for stato in list((bersaglio.db.stati or {}).keys()):
        for script in bersaglio.scripts.get(f"stato_{stato}"):
            script.delete()
        for script in bersaglio.scripts.get(f"periodico_{stato}"):
            script.delete()
    bersaglio.db.stati = {}


def _effetto_dispel_magic(caster, bersaglio, testo):
    _dissolvi_tutto(bersaglio)
    caster.location.msg_contents(magia(f"Gli effetti magici su {bersaglio.key} si dissolvono."))


def _effetto_cancellation(caster, bersaglio, testo):
    _dissolvi_tutto(bersaglio)
    caster.location.msg_contents(magia(f"Ogni magia attiva su {bersaglio.key} viene cancellata."))


def _effetto_negate_alignment(caster, bersaglio, testo):
    # Semplificazione dichiarata: nessun oggetto nel porting attuale
    # blocca l'uso in base all'allineamento (nessuna aura-lock
    # implementata), quindi l'effetto e' per ora solo di scena.
    bersaglio.db.allineamento_richiesto = None
    caster.msg(magia(f"Un bagliore neutro avvolge {bersaglio.key}: qualunque aura legata all'allineamento svanisce."))


# --- rilevamento / informazioni ---------------------------------------

def _effetto_detect_hidden(caster, bersaglio, testo):
    applica_stato(caster, "vede_invisibile", 120, "Non percepisci piu' cio' che e' nascosto.")
    caster.msg(magia("I tuoi sensi si affinano: percepisci cio' che altri non vedono."))


def _effetto_detect_invis(caster, bersaglio, testo):
    applica_stato(caster, "vede_invisibile", 120, "Non vedi piu' attraverso l'invisibilita'.")
    caster.msg(magia("I tuoi occhi si velano di una luce arcana: ora vedi anche l'invisibile."))


def _effetto_faerie_fog(caster, bersaglio, testo):
    stanza = caster.location
    caster.location.msg_contents(magia(f"{caster.key} libera una nebbia fatata che rivela ogni cosa nascosta!"))
    for presente in list(stanza.contents):
        if getattr(presente, "vivo", None) is not None:
            applica_stato(presente, "vede_invisibile", 60, None)


def _effetto_detect_poison(caster, bersaglio, testo):
    cibo = next((o for o in caster.contents if o.db.cibo is not None or o.db.bevanda is not None), None)
    if not cibo:
        caster.msg("Non hai cibo o bevande con te da controllare.")
        return
    if cibo.db.avvelenato:
        caster.msg(magia(f"{cibo.key} emana un debole miasma: e' avvelenato/a!"))
    else:
        caster.msg(magia(f"{cibo.key} sembra sicuro/a da consumare."))


def _effetto_know_alignment(caster, bersaglio, testo):
    valore = bersaglio.db.alignment or 0
    if valore >= 350:
        etichetta = "risplende di un'aura benevola"
    elif valore <= -350:
        etichetta = "e' avvolto/a da un'aura malvagia"
    else:
        etichetta = "ha un'aura neutra, ne' buona ne' malvagia"
    caster.msg(magia(f"{bersaglio.key} {etichetta} (allineamento {valore})."))


def _effetto_identify(caster, bersaglio, testo):
    righe = [f"|w{bersaglio.key}|n"]
    if bersaglio.db.tipo_arma:
        righe.append(f"Arma ({bersaglio.db.tipo_arma}): {bersaglio.db.dado_min}-{bersaglio.db.dado_max} danni, "
                      f"bonus {bersaglio.db.bonus_danno or 0}")
    if bersaglio.db.classe_armatura:
        righe.append(f"Armatura: classe {bersaglio.db.classe_armatura}")
    if bersaglio.db.livello:
        righe.append(f"Livello oggetto: {bersaglio.db.livello}")
    if bersaglio.db.condizione is not None:
        righe.append(f"Condizione: {bersaglio.db.condizione}/100")
    if bersaglio.db.marchio:
        righe.append(f"Marchio: {bersaglio.db.marchio}")
    if len(righe) == 1:
        righe.append("Nessuna proprieta' magica o di combattimento rilevabile.")
    caster.msg("\n".join(righe))


def _effetto_vision(caster, bersaglio, testo):
    from typeclasses.rooms import Room
    stanze = [s for s in Room.objects.all() if s.db.desc]
    if not stanze:
        caster.msg("Non vedi nulla.")
        return
    stanza = random.choice(stanze)
    caster.msg(magia(f"Con la mente scorgi un luogo lontano: |w{stanza.key}|n\n{stanza.db.desc}"))


def _effetto_locate_object(caster, bersaglio, testo):
    from evennia.objects.models import ObjectDB
    trovati = list(ObjectDB.objects.filter(db_key__icontains=testo)[:10])
    if not trovati:
        caster.msg(f"Non trovi traccia di '{testo}' da nessuna parte.")
        return
    righe = [f"Oggetti che corrispondono a '{testo}':"]
    for o in trovati:
        luogo = o.location.key if o.location else "da nessuna parte (non esiste piu')"
        righe.append(f"  {o.key} - {luogo}")
    caster.msg("\n".join(righe))


def _effetto_continual_light(caster, bersaglio, testo):
    # Fase K, sedicesima tornata: ora un vero effetto sulla stanza
    # (world/illuminazione.py) invece di un semplice messaggio di colore
    # - "an arcane ball of light that cannot be extinguished, providing
    # a light source that lasts indefinitely" (helps/continual_light.txt):
    # permanente per davvero, nessun comando per rimuoverlo, coerente
    # con "cannot be extinguished".
    caster.location.db.luce_permanente = True
    caster.location.msg_contents(magia(f"{caster.key} crea una sfera di luce arcana che non si spegnera' mai."))


def _effetto_aura(caster, bersaglio, testo):
    valore = caster.db.alignment or 0
    colore = "dorata" if valore >= 350 else "livida e oscura" if valore <= -350 else "grigia e incerta"
    caster.location.msg_contents(magia(f"Un'aura {colore} circonda {caster.key}."))


# --- invisibilita' -----------------------------------------------------

def _effetto_invis(caster, bersaglio, testo):
    rendi_invisibile(bersaglio, 300, f"{bersaglio.key} ridiventa visibile.")
    caster.location.msg_contents(magia(f"{bersaglio.key} svanisce alla vista!"))


def _effetto_mass_invis(caster, bersaglio, testo):
    stanza = caster.location
    nemico = caster.db.combat_target
    presenti = [caster] + [
        o for o in list(stanza.contents)
        if getattr(o, "vivo", None) and o is not caster and o is not nemico and o.db.combat_target is not caster
    ]
    for personaggio in presenti:
        rendi_invisibile(personaggio, 300, f"{personaggio.key} ridiventa visibile.")
    caster.location.msg_contents(magia(f"{caster.key} e chi gli/le sta vicino svaniscono alla vista!"))


def _effetto_remove_invis(caster, bersaglio, testo):
    """La fonte descrive questo incantesimo su un OGGETTO nell'inventario
    ('Rimuove l'invisibilita' da un oggetto...'), ma il nostro porting
    non ha un modo per rendere invisibile un oggetto (nessun incantesimo
    tra i 39 alberi delle professioni lo fa) - reinterpretato per
    lavorare su un personaggio bersaglio, molto piu' utile in pratica e
    coerente con "bersaglio_richiesto" gia' impostato su True."""
    if not bersaglio.db.invisibile:
        caster.msg(f"{bersaglio.key} non e' invisibile.")
        return
    bersaglio.db.invisibile = False
    for script in bersaglio.scripts.get("invis_scadenza"):
        script.delete()
    caster.location.msg_contents(magia(f"{bersaglio.key} ridiventa visibile."))


# --- movimento / teletrasporto -----------------------------------------

def _stanza_privata(stanza):
    return bool(stanza and stanza.tags.get("privata", category="restrizioni_stanza"))


def _effetto_teleport(caster, bersaglio, testo):
    from typeclasses.rooms import Room
    stanze = [s for s in Room.objects.all() if s.db.desc and not _stanza_privata(s)]
    if not stanze:
        caster.msg("Non funziona.")
        return
    destinazione = random.choice(stanze)
    origine = bersaglio.location
    if origine:
        origine.msg_contents(f"{bersaglio.key} svanisce in un lampo di luce!", exclude=[bersaglio])
    bersaglio.move_to(destinazione, quiet=True)
    bersaglio.msg(magia("Il mondo si contorce attorno a te... e poi sei altrove."))
    bersaglio.execute_cmd("look")


def _effetto_gate(caster, bersaglio, testo):
    destinazione = bersaglio.location
    if not destinazione or _stanza_privata(destinazione):
        caster.msg("Non riesci a raggiungere quel luogo.")
        return
    origine = caster.location
    if origine:
        origine.msg_contents(f"{caster.key} svanisce in un varco dimensionale!", exclude=[caster])
    caster.move_to(destinazione, quiet=True)
    caster.msg(magia(f"Ti materializzi accanto a {bersaglio.key}."))
    caster.execute_cmd("look")


def _effetto_psychic_anchor(caster, bersaglio, testo):
    if _stanza_privata(caster.location):
        caster.msg("Non puoi ancorare questo luogo.")
        return
    caster.db.ancora_psichica = caster.location
    caster.msg(magia("Lasci un'impronta psichica in questo luogo: potrai tornarci con Parola di Richiamo."))


def _effetto_word_of_recall(caster, bersaglio, testo):
    # Fase K, decima tornata: se e' presente un'Ancora Materiale, ha la
    # precedenza su quella Psichica (confermato dalla fonte) e non si
    # consuma all'uso - ma un recall azzera SEMPRE l'ancora psichica,
    # anche quando si e' usata quella materiale (confermato dalla fonte).
    ancora = caster.db.ancora_materiale or caster.db.ancora_psichica
    if not ancora or not ancora.pk:
        caster.msg("Non hai ancora ancorato nessun luogo.")
        return
    origine = caster.location
    if origine:
        origine.msg_contents(f"{caster.key} svanisce, richiamato/a verso la propria ancora!", exclude=[caster])
    caster.move_to(ancora, quiet=True)
    caster.msg(magia("Vieni trasportato/a verso il luogo che avevi ancorato."))
    caster.db.ancora_psichica = None
    caster.execute_cmd("look")


def _effetto_portal(caster, bersaglio, testo):
    ancora = caster.db.ancora_psichica
    if not ancora or not ancora.pk:
        caster.msg("Devi prima ancorare un luogo con Ancora Psichica per aprire un varco verso di esso.")
        return
    from evennia.utils import create, delay
    origine = caster.location
    andata = create.create_object(
        "typeclasses.exits.Exit", key="un varco arcano", location=origine, destination=ancora,
    )
    ritorno = create.create_object(
        "typeclasses.exits.Exit", key="un varco arcano", location=ancora, destination=origine,
    )
    caster.location.msg_contents(magia(f"{caster.key} apre un varco arcano scintillante!"))

    def _chiudi():
        for uscita in (andata, ritorno):
            if uscita.pk:
                if uscita.location:
                    uscita.location.msg_contents(magia(f"{uscita.key} si richiude e svanisce."))
                uscita.delete()
    delay(120, _chiudi)


def _effetto_pass_door(caster, bersaglio, testo):
    # Fase K, nona tornata: ora ha un vero effetto - vedi world/porte.py e
    # server/conf/lockfuncs.py:porta_aperta() (lock "traverse" delle
    # uscite chiuse), che controllano proprio questo stato.
    applica_stato(caster, "attraversa_porte", 60, "Non riesci piu' ad attraversare le porte chiuse.")
    caster.msg(magia("Il tuo corpo si fa etereo: potrai attraversare porte chiuse per un po'."))


def _effetto_ventriloquate(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f'{bersaglio.key} dice, "{testo}"'))
    caster.msg(magia(f"(in realta' sei stato/a tu a dirlo, gettando la voce)"))


# --- possessione (riusa world/yithian.py) -------------------------------

def _tenta_possessione(caster, npc, consente_forti):
    from world.yithian import possibilita_successo_mindtransfer
    if not npc or not npc.is_typeclass("typeclasses.npcs.NPC", exact=False):
        caster.msg("Puoi possedere solo un NPC.")
        return
    if npc.db.yithian_originale or npc.account:
        caster.msg(f"{npc.key} e' gia' occupato/a da qualcun altro.")
        return
    if not consente_forti and npc.livello_per_equip() > caster.livello_per_equip():
        caster.msg(f"{npc.key} e' troppo forte: ti servirebbe Possessione Maggiore.")
        return
    percentuale = possibilita_successo_mindtransfer(caster, npc)
    if random.uniform(0, 100) > percentuale:
        caster.msg(f"Il tentativo di possedere {npc.key} fallisce.")
        if npc.livello_per_equip() > caster.livello_per_equip():
            npc.db.ostile = True
            caster.location.msg_contents(magia(f"{npc.key} si risveglia furioso/a e attacca {caster.key}!"))
            npc.avvia_combattimento(caster)
        return
    sessioni = caster.sessions.get()
    if not sessioni:
        return
    account = caster.account
    npc.db.yithian_originale = caster  # campo condiviso con MINDTRANSFER, vedi world/yithian.py
    npc.locks.add(f"puppet:id({account.id}) or perm(Developer)")
    caster.msg(magia(f"La tua mente scivola nel corpo di {npc.key}."))
    account.puppet_object(sessioni[0], npc)


def _effetto_lesser_possession(caster, bersaglio, testo):
    _tenta_possessione(caster, bersaglio, consente_forti=False)


def _effetto_greater_possession(caster, bersaglio, testo):
    _tenta_possessione(caster, bersaglio, consente_forti=True)


# --- evocazioni ----------------------------------------------------------

def _crea_alleato_temporaneo(caster, nome, livello, hp, skills, secondi_vita, bersaglio_iniziale=None):
    from evennia.utils import create, delay
    alleato = create.create_object("typeclasses.npcs.NPC", key=nome, location=caster.location)
    alleato.db.desc = f"Un'entita' evocata da {caster.key}."
    alleato.db.livello = livello
    alleato.db.hp_max = hp
    alleato.db.hp = hp
    alleato.db.alignment = caster.db.alignment or 0
    alleato.db.skills = dict(skills)
    alleato.db.ostile = False
    alleato.db.evocato_da = caster
    if bersaglio_iniziale and getattr(bersaglio_iniziale, "vivo", False):
        alleato.avvia_combattimento(bersaglio_iniziale)
    delay(secondi_vita, alleato.delete)
    return alleato


def _effetto_summon_familier(caster, bersaglio, testo):
    valore = caster.db.alignment or 0
    if valore >= 350:
        nome = "uno spirito guardiano luminoso"
    elif valore <= -350:
        nome = "un famiglio dalle forme contorte"
    else:
        nome = "un famiglio dall'aspetto mutevole"
    _crea_alleato_temporaneo(caster, nome, caster.livello_per_equip(), 30,
                              {"hand_to_hand": 40}, 1800)
    caster.location.msg_contents(magia(f"{caster.key} evoca {nome}, che si materializza al suo fianco."))


def _effetto_holy_word(caster, bersaglio, testo):
    nemico = caster.db.combat_target
    _crea_alleato_temporaneo(caster, "un angelo vendicatore", caster.livello_per_equip() + 5, 60,
                              {"sword": 60, "hand_to_hand": 50}, 120, bersaglio_iniziale=nemico)
    caster.location.msg_contents(magia(f"{caster.key} evoca un angelo vendicatore in un lampo di luce sacra!"))


def _effetto_summon(caster, bersaglio, testo):
    from world.yithian import possibilita_successo_mindtransfer
    percentuale = possibilita_successo_mindtransfer(caster, bersaglio)
    if random.uniform(0, 100) > percentuale:
        caster.msg(magia(f"{bersaglio.key} resiste al richiamo."))
        return
    origine = bersaglio.location
    if origine:
        origine.msg_contents(f"{bersaglio.key} svanisce, richiamato/a altrove!", exclude=[bersaglio])
    bersaglio.move_to(caster.location, quiet=True)
    bersaglio.msg(magia(f"Vieni improvvisamente trasportato/a accanto a {caster.key}!"))
    caster.location.msg_contents(magia(f"{bersaglio.key} si materializza davanti a {caster.key}."), exclude=[bersaglio])


# --- incantamento oggetti (riusa lo spirito di world/forgiatura.py) -------

def _effetto_enchant_weapon(caster, bersaglio, testo):
    from world.equipment import arma_equipaggiata
    arma = arma_equipaggiata(caster)
    if not arma:
        caster.msg("Devi impugnare un'arma per incantarla.")
        return
    tentativi = (arma.db.tentativi_incantamento or 0)
    rischio = max(5, 40 - caster.skill_rating("enchant_weapon") // 3 + tentativi * 5)
    if random.randint(1, 100) <= rischio:
        arma.db.condizione = max(0, (arma.db.condizione or 100) - random.randint(15, 30))
        caster.location.msg_contents(magia(f"L'incantesimo destabilizza {arma.key}, danneggiandola!"))
        return
    arma.db.livello = (arma.db.livello or 1) + 1
    arma.db.bonus_danno = (arma.db.bonus_danno or 0) + 1
    arma.db.tentativi_incantamento = tentativi + 1
    caster.location.msg_contents(magia(f"{arma.key} risplende per un istante: e' piu' potente di prima!"))


def _effetto_enchant_armor(caster, bersaglio, testo):
    equip = caster.db.equip or {}
    corazza = next((o for o in equip.values() if o and o.db.classe_armatura), None)
    if not corazza:
        caster.msg("Devi indossare un'armatura per incantarla.")
        return
    tentativi = (corazza.db.tentativi_incantamento or 0)
    rischio = max(5, 40 - caster.skill_rating("enchant_armor") // 3 + tentativi * 5)
    if random.randint(1, 100) <= rischio:
        corazza.db.condizione = max(0, (corazza.db.condizione or 100) - random.randint(15, 30))
        caster.location.msg_contents(magia(f"L'incantesimo destabilizza {corazza.key}, danneggiandola!"))
        return
    corazza.db.livello = (corazza.db.livello or 1) + 1
    corazza.db.classe_armatura = (corazza.db.classe_armatura or 0) + 1
    corazza.db.tentativi_incantamento = tentativi + 1
    caster.location.msg_contents(magia(f"{corazza.key} risplende per un istante: e' piu' resistente di prima!"))


def _effetto_brand(caster, bersaglio, testo):
    from world.equipment import arma_equipaggiata
    arma = bersaglio if getattr(bersaglio, "db", None) and bersaglio.db.tipo_arma else arma_equipaggiata(caster)
    if not arma or not arma.db.tipo_arma:
        caster.msg("Devi indicare un'arma da marchiare.")
        return
    if arma.db.marchio:
        caster.msg(f"{arma.key} porta gia' il marchio {arma.db.marchio}.")
        return
    if random.randint(1, 100) <= 20:
        caster.location.msg_contents(magia(f"L'energia del marchio va fuori controllo: {arma.key} viene distrutta!"))
        arma.delete()
        return
    marchio = random.choice(["Fiamma", "Gelo", "Acido", "Fulmine"])
    arma.db.marchio = marchio
    arma.db.bonus_danno = (arma.db.bonus_danno or 0) + 2
    caster.location.msg_contents(magia(f"{arma.key} arde per un istante e ne emerge marchiata di {marchio}."))


# --- creazione di oggetti --------------------------------------------

def _crea_oggetto_consumabile(location, key, desc, cibo=None, bevanda=None):
    from evennia.utils import create
    oggetto = create.create_object("typeclasses.objects.Object", key=key, location=location)
    oggetto.db.desc = desc
    if cibo is not None:
        oggetto.db.cibo = cibo
    if bevanda is not None:
        oggetto.db.bevanda = bevanda
    return oggetto


def _effetto_create_food(caster, bersaglio, testo):
    _crea_oggetto_consumabile(caster, "un fagotto di frutta e verdura",
                               "Frutta e verdura fresca, appena creata dal nulla.", cibo=20)
    caster.location.msg_contents(magia(f"{caster.key} forma un fagotto di cibo dal nulla."))


def _effetto_create_buffet(caster, bersaglio, testo):
    numero = 2 + caster.skill_rating("create_buffet") // 30
    for _ in range(numero):
        _crea_oggetto_consumabile(caster, "un fagotto di frutta e verdura",
                                   "Frutta e verdura fresca, appena creata dal nulla.", cibo=20)
    caster.location.msg_contents(magia(f"{caster.key} fa apparire un intero banchetto dal nulla!"))


def _effetto_create_water(caster, bersaglio, testo):
    if not getattr(bersaglio, "db", None) or bersaglio.db.tipo_arma or bersaglio.db.classe_armatura:
        caster.msg("Ti serve un contenitore vuoto.")
        return
    bersaglio.db.bevanda = 15
    caster.msg(magia(f"{bersaglio.key} si riempie d'acqua limpida."))


def _effetto_create_spring(caster, bersaglio, testo):
    from evennia.utils import delay
    sorgente = _crea_oggetto_consumabile(
        caster.location, "una sorgente scintillante",
        "Una sorgente magica d'acqua limpida, sgorgata dal nulla.", bevanda=999,
    )
    caster.location.msg_contents(magia(f"{caster.key} evoca una sorgente d'acqua scintillante dal terreno."))
    delay(600, sorgente.delete)


def _effetto_create_potion(caster, bersaglio, testo):
    from evennia.utils import create
    conosciuti = [sid for sid, dati in SPELLS.items() if dati["skill_richiesta"] in (caster.db.skills or {})]
    spell_id = random.choice(conosciuti) if conosciuti else None
    nome_effetto = nome_incantesimo(spell_id) if spell_id else "un effetto sconosciuto"
    pozione = create.create_object("typeclasses.objects.Object", key="una pozione magica", location=caster)
    pozione.db.desc = f"Un liquido dai riflessi cangianti. Sembra contenere l'incantesimo {nome_effetto}."
    pozione.db.pozione_spell = spell_id
    caster.msg(magia(f"Mescoli erbe e ingredienti: ottieni {pozione.key}!"))


# --- famiglia Controllo del Corpo (Fase K, settima tornata) ------------

def _effetto_asceticism(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_stato(bersaglio, "ascetismo", 600,
                  f"{bersaglio.key} torna ad avvertire fame e sete.")
    caster.location.msg_contents(magia(f"{bersaglio.key} non sentira' piu' fame ne' sete per un po'."))


def _effetto_burden_of_blubber(caster, bersaglio, testo):
    applica_stato(bersaglio, "obeso", 300, None)
    applica_buff_temporaneo(bersaglio, "mod_temp_dex", -6, 300,
                             f"{bersaglio.key} ritrova la propria agilita'.")
    caster.location.msg_contents(magia(f"{bersaglio.key} si gonfia improvvisamente di grasso!"))


def _effetto_slender_lines(caster, bersaglio, testo):
    if not ha_stato(bersaglio, "obeso"):
        caster.msg(f"{bersaglio.key} non soffre di questo problema.")
        return
    rimuovi_stato(bersaglio, "obeso")
    for script in bersaglio.scripts.get("buff_mod_temp_dex"):
        script.delete()
    bersaglio.db.mod_temp_dex = 0
    caster.location.msg_contents(magia(f"{bersaglio.key} perde all'istante ogni traccia di grasso in eccesso."))


def _effetto_burning_thirst(caster, bersaglio, testo):
    bersaglio.db.sete = min(100, (bersaglio.db.sete or 0) + 70)
    caster.location.msg_contents(magia(f"{bersaglio.key} sente la gola seccarsi all'improvviso!"))


def _effetto_gnawing_hunger(caster, bersaglio, testo):
    bersaglio.db.appetito = min(100, (bersaglio.db.appetito or 0) + 70)
    caster.location.msg_contents(magia(f"Una fame feroce assale improvvisamente {bersaglio.key}!"))


def _effetto_change_size(caster, bersaglio, testo):
    bersaglio = caster
    if testo and testo.strip().lower() in ("maggiore", "grande", "larger"):
        applica_buff_temporaneo(bersaglio, "mod_temp_str", 4, 180,
                                 f"{bersaglio.key} torna alla propria taglia normale.")
        applica_buff_temporaneo(bersaglio, "mod_temp_dex", -2, 180, None)
        caster.location.msg_contents(magia(f"{bersaglio.key} cresce visibilmente di taglia!"))
    else:
        applica_buff_temporaneo(bersaglio, "mod_temp_dex", 4, 180,
                                 f"{bersaglio.key} torna alla propria taglia normale.")
        applica_buff_temporaneo(bersaglio, "mod_temp_str", -2, 180, None)
        caster.location.msg_contents(magia(f"{bersaglio.key} si rimpicciolisce visibilmente!"))


def _effetto_free_grog(caster, bersaglio, testo):
    applica_stato(bersaglio, "ubriaco", 180, None)
    applica_buff_temporaneo(bersaglio, "bonus_colpire", -10, 180,
                             f"{bersaglio.key} torna sobrio/a.")
    caster.location.msg_contents(magia(f"{bersaglio.key} barcolla, improvvisamente ubriaco/a fradicio/a!"))


def _effetto_ghastly_sobriety(caster, bersaglio, testo):
    if ha_stato(bersaglio, "ubriaco"):
        rimuovi_stato(bersaglio, "ubriaco")
        for script in bersaglio.scripts.get("buff_bonus_colpire"):
            script.delete()
        bersaglio.db.bonus_colpire = 0
    applica_buff_temporaneo(bersaglio, "bonus_colpire", -3, 120,
                             f"{bersaglio.key} smaltisce finalmente il mal di testa.")
    caster.location.msg_contents(magia(f"{bersaglio.key} torna di colpo sobrio/a - con un terribile mal di testa."))


def _effetto_hallucinate(caster, bersaglio, testo):
    applica_stato(bersaglio, "allucinato", 60,
                  f"{bersaglio.key} smette finalmente di vedere cose che non ci sono.")
    caster.location.msg_contents(magia(f"Lo sguardo di {bersaglio.key} si perde in visioni che nessun altro vede."))


def _effetto_relax(caster, bersaglio, testo):
    applica_stato(bersaglio, "rilassato", 180,
                  f"{bersaglio.key} torna alla propria normale fragilita' mentale.")
    caster.location.msg_contents(magia(f"{bersaglio.key} si distende, piu' resistente all'orrore."))


# --- meteo -------------------------------------------------------------

def _effetto_control_weather(caster, bersaglio, testo):
    # Semplificazione dichiarata: puramente di scena, nessuna meccanica
    # di gioco legge ancora il meteo di una stanza (nessun malus da
    # pioggia/tempesta, nessuna area "al chiuso" che lo impedisca).
    if testo and testo.strip().lower() in ("peggiore", "peggio", "worse"):
        caster.location.db.meteo = "tempestoso"
        caster.location.msg_contents(magia("Il cielo si oscura: nubi nere si addensano e inizia a tuonare."))
    else:
        caster.location.db.meteo = "sereno"
        caster.location.msg_contents(magia("Le nubi si diradano: il cielo torna sereno e luminoso."))


# ==========================================================================
# Fase K, ottava tornata: i "fratelli" delle famiglie di incantesimi
# Necromanzia/Magia Divina/Magia Onirica/Magia Mentale/Via della Natura/
# Via del Duellante/Taumaturgia/Magia degli Antichi - vedi world/spells.py
# per la nota introduttiva e i riferimenti alla fonte di ciascuno.
# ==========================================================================

# --- Necromanzia ----------------------------------------------------------

def _crea_non_morto_obbediente(caster, cadavere, nome):
    """Base condivisa di Anima Morto/Mummifica: rianima un cadavere in un
    servo obbediente, riusando lo stesso schema di alleato temporaneo gia'
    scritto per Familiare/Parola Sacra invece di duplicarlo. Durata lunga
    (2 ore) perche' qui non e' un evocato "di supporto" ma un vero servitore."""
    if not cadavere or not cadavere.is_typeclass("typeclasses.objects.Corpse", exact=False):
        caster.msg("Puoi lanciare questo incantesimo solo su un cadavere.")
        return
    origine = cadavere.key
    cadavere.delete()
    rating = caster.skill_rating("necromancy")
    servo = _crea_alleato_temporaneo(
        caster, nome, caster.livello_per_equip(), 40 + rating,
        {"hand_to_hand": 30 + rating // 2}, 7200,
    )
    servo.db.non_morto = True  # Fase K, decima tornata: bersaglio valido per Esorcismo/Benedizione Oscura
    caster.location.msg_contents(magia(f"{origine} si rialza come {servo.key}, totalmente obbediente a {caster.key}."))


def _effetto_animate_dead(caster, bersaglio, testo):
    _crea_non_morto_obbediente(caster, bersaglio, "uno zombie senz'anima")


def _effetto_mummify(caster, bersaglio, testo):
    _crea_non_morto_obbediente(caster, bersaglio, "una mummia bendata")


def _effetto_lich(caster, bersaglio, testo):
    # La fonte stessa segnala questo incantesimo come disabilitato
    # ("NOTE: This spell is currently disabled") - onorato qui invece di
    # implementarlo comunque: diventare Lich resta possibile solo tramite
    # il comando SUBRACE riservato allo staff (world/sottorazze.py).
    caster.msg(
        "Inizi a pronunciare il rituale, ma qualcosa blocca l'incantesimo a meta': "
        "questo potere resta oltre la tua portata per ora."
    )


def _effetto_darkness(caster, bersaglio, testo):
    # Fase K, sedicesima tornata: ora un vero effetto sulla STANZA
    # (world/illuminazione.py), non piu' un "cieco" applicato a tutti i
    # presenti (semplificazione della sesta tornata, di prima che
    # esistesse un sistema di illuminazione) - questo e' cio' che rende
    # INFRAVISIONE davvero utile contro Oscurita', come conferma la
    # fonte (guides_advice.txt: "The room is affected by magical
    # darkness. Get the spell infravision").
    applica_stato(caster.location, "buio_magico", 30, None)
    caster.location.msg_contents(magia(
        f"{caster.key} scatena un'ondata di oscurita' magica: la stanza sprofonda nel buio piu' totale!"
    ))


def _effetto_desecrate(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} profana la stanza: un'aura malvagia impregna ogni cosa!"))
    for presente in list(caster.location.contents):
        if not getattr(presente, "vivo", False) or presente is caster:
            continue
        if (presente.db.alignment or 0) > 100:
            danno = random.randint(8, 16)
            presente.msg(pericolo(f"Il terreno sconsacrato ti brucia l'anima per {danno} danni!"))
            morto = presente.subisci_danno(danno, fisico=False)
            if morto:
                from world.combat import gestisci_morte
                gestisci_morte(presente, caster)


def _effetto_soul_blade(caster, bersaglio, testo):
    from evennia.utils import create
    spada = create.create_object("typeclasses.objects.Object", key="una lama dell'anima", location=caster)
    spada.db.desc = "Una spada forgiata dalla stessa essenza spirituale di chi l'ha evocata."
    spada.db.slot = "arma"
    spada.db.tipo_arma = "sword"
    spada.db.dado_min = 2
    spada.db.dado_max = 8
    rating = caster.skill_rating("necromancy")
    spada.db.bonus_danno = 1 + rating // 25
    spada.db.livello = caster.livello_per_equip()
    from world.equipment import CONDIZIONE_INIZIALE
    spada.db.condizione = CONDIZIONE_INIZIALE
    caster.msg(magia(f"Dal tuo stesso spirito prende forma {spada.key}."))


def _effetto_doppelganger(caster, bersaglio, testo):
    sosia = _crea_alleato_temporaneo(
        caster, f"un sosia non-morto di {caster.key}", caster.livello_per_equip(), 35,
        {"hand_to_hand": 35}, 3600,
    )
    sosia.db.non_morto = True
    caster.location.msg_contents(magia(f"{caster.key} plasma dalla propria ombra {sosia.key}."))


def _effetto_spring_of_blood(caster, bersaglio, testo):
    from evennia.utils import create, delay
    fontana = create.create_object("typeclasses.objects.Object", key="una sorgente di sangue fresco", location=caster.location)
    fontana.db.desc = "Un magico zampillo di sangue fresco, che presto si prosciughera'."
    fontana.db.bevanda = 25
    delay(600, fontana.delete)
    caster.location.msg_contents(magia(f"{caster.key} evoca {fontana.key}, che presto si prosciughera'."))


def _effetto_fist_of_azathoth(caster, bersaglio, testo):
    rating = caster.skill_rating("necromancy")
    probabilita_morte_istantanea = min(15, 3 + rating // 15)
    if random.uniform(0, 100) <= probabilita_morte_istantanea:
        caster.location.msg_contents(magia(
            f"{caster.key} scandisce il Pugno di Azathoth: {bersaglio.key} viene annientato/a all'istante!"
        ))
        morto = bersaglio.subisci_danno(bersaglio.db.hp_max or 999, fisico=False)
        if morto:
            from world.combat import gestisci_morte
            gestisci_morte(bersaglio, caster)
        return
    danno = random.randint(25, 45)
    _infliggi_danno_magico(caster, bersaglio, danno, "e' investito/a dal Pugno di Azathoth")


def _effetto_unrest(caster, bersaglio, testo):
    cadaveri = [o for o in caster.location.contents if o.is_typeclass("typeclasses.objects.Corpse", exact=False)]
    if not cadaveri:
        caster.msg("L'aura di inquietudine si diffonde, ma non ci sono cadaveri da risvegliare qui.")
        return
    caster.location.msg_contents(magia(f"{caster.key} diffonde un'aura maligna: l'aria stessa sembra fremere di malvagita'!"))
    for cadavere in cadaveri:
        if random.randint(1, 100) <= 40:
            origine = cadavere.key
            cadavere.delete()
            mostro = _crea_alleato_temporaneo(
                caster, "uno zombie rianimato spontaneamente", caster.livello_per_equip(), 30,
                {"hand_to_hand": 25}, 1800,
            )
            mostro.db.ostile = True
            mostro.db.evocato_da = None
            caster.location.msg_contents(magia(f"{origine} si rialza da solo/a come {mostro.key}, ostile a chiunque!"))


# --- Magia Divina -----------------------------------------------------

def _effetto_mortalize(caster, bersaglio, testo):
    if not (bersaglio.account and bersaglio.account.check_permstring("Builder")):
        caster.msg(f"{bersaglio.key} non e' un Antico: l'incantesimo non ha alcun effetto.")
        return
    # Nessuna vera invulnerabilita' da staff esiste in questo porting (il
    # combattimento non controlla mai i permessi): l'incantesimo resta
    # percio' un marcatore narrativo pronto per un futuro sistema, non ha
    # una conseguenza meccanica aggiuntiva da rimuovere - semplificazione
    # dichiarata esplicitamente.
    applica_stato(bersaglio, "mortalizzato", 300, f"{bersaglio.key} riacquista la propria natura divina.")
    caster.location.msg_contents(magia(f"{caster.key} pronuncia Mortalizza su {bersaglio.key}: per un momento, sembra piu' fragile."))


def _effetto_summon_old(caster, bersaglio, testo):
    if not (bersaglio.account and bersaglio.account.check_permstring("Builder")):
        caster.msg(f"{bersaglio.key} non e' un Antico: l'incantesimo non ha alcun effetto.")
        return
    origine = bersaglio.location
    if origine:
        origine.msg_contents(f"{bersaglio.key} svanisce in un lampo, richiamato/a altrove!", exclude=[bersaglio])
    bersaglio.move_to(caster.location, quiet=True)
    bersaglio.msg(magia(f"Vieni improvvisamente trascinato/a accanto a {caster.key}!"))
    caster.location.msg_contents(magia(f"{bersaglio.key} si materializza davanti a {caster.key}."), exclude=[bersaglio])


def _effetto_soul_guard(caster, bersaglio, testo):
    # world/esperienza.py legge db.alignment per il moltiplicatore XP, ma
    # nessuna azione di gioco lo MODIFICA mai dinamicamente in questo
    # porting (resta fisso al valore di creazione) - non esiste quindi
    # ancora nulla da proteggere per davvero: come per Mortalizza, un
    # marcatore pronto per un futuro sistema di deriva d'allineamento,
    # semplificazione dichiarata esplicitamente.
    applica_stato(bersaglio, "anima_protetta", 1800, f"La Guardia dell'Anima di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{caster.key} avvolge l'anima di {bersaglio.key} in un velo protettivo."))


# --- Magia Onirica (si aggancia a world/dreamlands.py) ---------------------

def _effetto_trance(caster, bersaglio, testo):
    # world/dreamlands.py:CmdDream legge questo stato per un bonus reale
    # alla probabilita' di sognare (BONUS_TRANCE) - prima non veniva mai
    # controllato da nessuna parte (gap trovato dall'audit).
    applica_stato(bersaglio, "trance", 600, f"L'effetto di Trance su {bersaglio.key} svanisce.")
    bersaglio.msg(onirico("La tua mente si affina: sognare ti sembra ora piu' facile e naturale."))


def _effetto_true_dreaming(caster, bersaglio, testo):
    from world.dreamlands import get_crocevia
    crocevia = get_crocevia()
    if not crocevia:
        caster.msg("Il sogno non prende forma: le Dreamlands non sono ancora state costruite.")
        return
    caster.location.msg_contents(onirico(f"{bersaglio.key} si dissolve in vortici di colore, trascinato/a nel proprio sogno!"), exclude=[bersaglio])
    bersaglio.move_to(crocevia, quiet=True, move_type="teleport")
    bersaglio.msg(onirico("Il mondo si dissolve: sei altrove, in un luogo che esiste solo perche' lo sogni."))
    bersaglio.msg(bersaglio.at_look(bersaglio.location))


def _effetto_rude_awakening(caster, bersaglio, testo):
    from world.dreamlands import in_dreamlands
    if not in_dreamlands(bersaglio.location):
        caster.msg(f"{bersaglio.key} non sta sognando.")
        return
    destinazione = bersaglio.db.recall_room or bersaglio.db.respawn_room
    if not destinazione:
        caster.msg(onirico(f"{bersaglio.key} si sveglia di soprassalto, ma non ha un posto dove tornare."))
        return
    bersaglio.msg(onirico("Vieni strappato/a bruscamente dal sogno, il cuore che batte forte."))
    bersaglio.move_to(destinazione, quiet=True, move_type="teleport")
    bersaglio.msg(bersaglio.at_look(bersaglio.location))
    caster.location.msg_contents(magia(f"{caster.key} pronuncia Risveglio Brusco: {bersaglio.key} scompare di colpo."))


def _effetto_recurring_dream(caster, bersaglio, testo):
    from world.dreamlands import in_dreamlands, get_crocevia
    if in_dreamlands(bersaglio.location):
        caster.msg(f"{bersaglio.key} sta gia' sognando.")
        return
    destinazione = bersaglio.db.ultimo_sogno or get_crocevia()
    if not destinazione:
        caster.msg("Il sogno non prende forma: le Dreamlands non sono ancora state costruite.")
        return
    caster.location.msg_contents(onirico(f"{bersaglio.key} scivola via, riportato/a nel proprio sogno di prima!"), exclude=[bersaglio])
    bersaglio.move_to(destinazione, quiet=True, move_type="teleport")
    bersaglio.msg(onirico("Il sogno ricomincia esattamente da dove l'avevi lasciato."))
    bersaglio.msg(bersaglio.at_look(bersaglio.location))


def _effetto_enchanted_sleep(caster, bersaglio, testo):
    from world.dreamlands import get_crocevia
    crocevia = get_crocevia()
    applica_stato(bersaglio, "addormentato", 60, f"{bersaglio.key} si risveglia.")
    if crocevia:
        bersaglio.move_to(crocevia, quiet=True, move_type="teleport")
        bersaglio.msg(onirico("Sprofondi in un sonno profondissimo e ti ritrovi subito immerso/a in un sogno sicuro e tranquillo."))
        bersaglio.msg(bersaglio.at_look(bersaglio.location))
    else:
        bersaglio.msg(onirico("Sprofondi in un sonno profondissimo e senza sogni."))
    caster.location.msg_contents(magia(f"{caster.key} lancia Sonno Incantato su {bersaglio.key}."))


def _effetto_accursed_sleep(caster, bersaglio, testo):
    from world.dreamlands import get_crocevia
    crocevia = get_crocevia()
    applica_stato(bersaglio, "addormentato", 60, f"{bersaglio.key} si risveglia di soprassalto.")
    applica_stato(bersaglio, "impaurito", 90, None)
    if crocevia:
        bersaglio.move_to(crocevia, quiet=True, move_type="teleport")
        bersaglio.msg(orrore("Sprofondi in un sonno immediato e ti ritrovi intrappolato/a in un incubo terribile!"))
        bersaglio.msg(bersaglio.at_look(bersaglio.location))
    else:
        bersaglio.msg(orrore("Sprofondi in un sonno immediato, tormentato/a da un incubo terribile."))
    caster.location.msg_contents(magia(f"{caster.key} lancia Sonno Maledetto su {bersaglio.key}!"))


# --- Magia Mentale ---------------------------------------------------------

def _effetto_astral_walk(caster, bersaglio, testo):
    if ha_stato(caster, "astrale"):
        caster.msg("Sei gia' distaccato/a nel tuo corpo astrale.")
        return
    applica_stato(caster, "astrale", 3600, None)
    caster.msg(magia(
        "Ti distacchi dal tuo corpo fisico: puoi ancora muoverti e guardarti attorno, ma la "
        "maggior parte delle creature non puo' piu' colpirti - salvo Esplosione Astrale. "
        "Usa RETURN per tornare al tuo corpo."
    ))


def _effetto_astral_blast(caster, bersaglio, testo):
    if not ha_stato(bersaglio, "astrale"):
        caster.msg(f"{bersaglio.key} non e' in forma astrale: questo incantesimo non ha effetto.")
        return
    danno = random.randint(10, 20)
    caster.location.msg_contents(magia(f"{caster.key} scaglia un'Esplosione Astrale contro il corpo astrale di {bersaglio.key}!"))
    morto = bersaglio.subisci_danno(danno, fisico=False)
    if morto:
        from world.combat import gestisci_morte
        gestisci_morte(bersaglio, caster)


def _effetto_mind_meld(caster, bersaglio, testo):
    danno = random.randint(8, 16)
    _infliggi_danno_magico(caster, bersaglio, danno, "si contorce sotto un colpo psionico")
    applica_buff_temporaneo(bersaglio, "mod_temp_int", -5, 120,
                             f"La mente di {bersaglio.key} torna limpida.")


# --- Via della Natura -------------------------------------------------

def _effetto_create_seed(caster, bersaglio, testo):
    from evennia.utils import create
    seme = create.create_object("typeclasses.objects.Object", key="il seme di un albero", location=caster)
    seme.db.desc = (
        "Un piccolo seme che pulsa di energia vitale. Nessun terreno coltivabile esiste "
        "ancora in questo mondo per piantarlo davvero (nessun comando PLANT): per ora "
        "resta un oggetto vero ma di scena."
    )
    caster.msg(magia(f"Fai germogliare dal nulla {seme.key}."))


def _effetto_drain_vitality(caster, bersaglio, testo):
    e_albero = getattr(bersaglio, "db", None) and (bersaglio.db.albero or "albero" in bersaglio.key.lower())
    if not e_albero:
        caster.msg(f"{bersaglio.key} non e' un albero: non c'e' vitalita' da drenare.")
        return
    quantita = random.randint(15, 30)
    caster.db.mana = min(caster.db.mana_max, (caster.db.mana or 0) + quantita)
    caster.location.msg_contents(magia(f"{caster.key} drena {quantita} mana da {bersaglio.key}, che appassisce leggermente."))


def _effetto_insect_curse(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} scatena sciami di insetti che infestano la stanza!"))
    for presente in list(caster.location.contents):
        if not getattr(presente, "vivo", False) or presente is caster:
            continue
        applica_danno_periodico(presente, "punto_da_insetti", 1, 4, 15, 4,
                                 messaggio_tick="Gli insetti ti pungono ovunque, infliggendoti {danno} danni.")


def _effetto_wolfbite(caster, bersaglio, testo):
    from world.sottorazze import diventa_sottorazza
    if bersaglio.db.sottorazza:
        caster.msg(f"{bersaglio.key} e' gia' {bersaglio.db.sottorazza}: il morso non ha effetto.")
        return
    caster.location.msg_contents(magia(f"{caster.key} morde selvaggiamente {bersaglio.key}!"))
    ok, messaggio = diventa_sottorazza(bersaglio, "were")
    bersaglio.msg(orrore("Un dolore lancinante ti attraversa: qualcosa di ferino si e' risvegliato dentro di te..."))
    caster.location.msg_contents(magia(messaggio))


# --- Via del Duellante ------------------------------------------------

def _effetto_magical_duel(caster, bersaglio, testo):
    applica_stato(caster, "duello_magico", 300, "Il tuo Duello Magico si conclude.")
    applica_stato(bersaglio, "duello_magico", 300, "Il tuo Duello Magico si conclude.")
    caster.avvia_combattimento(bersaglio)
    bersaglio.avvia_combattimento(caster)
    caster.location.msg_contents(magia(
        f"{caster.key} sfida {bersaglio.key} a un Duello Magico! (usa DUEL OFF/DEF <mana> per modificare il tuo assetto)"
    ))


def _effetto_mental_shield(caster, bersaglio, testo):
    applica_buff_temporaneo(caster, "bonus_ca_temp", 15, 120,
                             f"Lo Scudo Mentale di {caster.key} svanisce.")
    caster.msg(magia("Un'aura mistica ti avvolge, pronta ad assorbire attacchi mentali e magici."))


def _effetto_psi_twister(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} scatena uno Psi Twister: un'onda mentale travolge la stanza!"))
    _danno_area(caster, 10, 18, "viene travolto/a dallo Psi Twister")


def _effetto_telekinesis(caster, bersaglio, testo):
    if not testo:
        caster.msg("Uso: cast telecinesi <oggetto> <direzione>")
        return
    parti = testo.rsplit(" ", 1)
    if len(parti) != 2:
        caster.msg("Uso: cast telecinesi <oggetto> <direzione>")
        return
    nome_oggetto, direzione = parti
    direzione = direzione.lower()
    uscita = None
    for e in caster.location.exits:
        nomi = [e.key.lower()] + [a.lower() for a in e.aliases.all()]
        if direzione in nomi:
            uscita = e
            break
    if not uscita or not uscita.destination:
        caster.msg(f"Non c'e' nessuna uscita verso '{direzione}'.")
        return
    oggetto = uscita.destination.search(nome_oggetto, quiet=True)
    oggetto = oggetto[0] if oggetto else None
    if not oggetto:
        caster.msg(f"Non vedi '{nome_oggetto}' in quella direzione.")
        return
    if not oggetto.access(caster, "get", default=True):
        caster.msg(f"{oggetto.key} non puo' essere spostato con la telecinesi.")
        return
    oggetto.move_to(caster.location, quiet=True)
    caster.location.msg_contents(magia(f"{oggetto.key} fluttua improvvisamente nella stanza, spinto/a dalla mente di {caster.key}."))


def _effetto_terror_of_the_old(caster, bersaglio, testo):
    caster.location.msg_contents(magia(
        f"{caster.key} evoca l'immagine spettrale di Hastur l'Innominabile davanti a {bersaglio.key}!"
    ))
    applica_stato(bersaglio, "impaurito", 60, f"L'immagine di Hastur svanisce: {bersaglio.key} si riprende dal terrore.")


def _effetto_wrath_of_cthugha(caster, bersaglio, testo):
    danno = random.randint(30, 55)
    if random.randint(1, 100) <= 8:
        caster.msg(pericolo("La palla di fuoco ti sfugge di mano ed esplode troppo presto!"))
        _infliggi_danno_magico(bersaglio, caster, danno // 2, "viene ustionato/a dalla propria stessa magia")
        return
    _infliggi_danno_magico(caster, bersaglio, danno, "viene avvolto/a da una palla di fuoco")


def _effetto_wrath_of_ithaqua(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} scaglia una gigantesca palla di neve contro {bersaglio.key}!"))
    applica_stato(bersaglio, "paralizzato", 20, f"{bersaglio.key} si riprende dallo stordimento gelido.")


# --- Taumaturgia + Personalizza Arma -----------------------------------

def _rischio_distrugge_oggetto(caster, oggetto, skill_id, rischio_base=35):
    """Rischio condiviso da Anima Arma/Consistenza/Permanenza/Universalita'/
    Personalizza Arma (confermato dalla fonte per tutti: "carries a chance
    of destroying the object"), stesso schema gia' visto in
    _effetto_enchant_weapon/enchant_armor: il rischio scende con la skill."""
    rischio = max(5, rischio_base - caster.skill_rating(skill_id) // 3)
    if random.randint(1, 100) <= rischio:
        caster.location.msg_contents(magia(f"L'energia sfugge al controllo: {oggetto.key} viene distrutto!"))
        oggetto.delete()
        return True
    return False


def _effetto_animate_weapon(caster, bersaglio, testo):
    if not bersaglio.db.personalizzata_da:
        caster.msg(f"{bersaglio.key} non e' stata personalizzata: Anima Arma non puo' richiamarla.")
        return
    if bersaglio.db.personalizzata_da != caster:
        caster.msg(f"{bersaglio.key} e' stata personalizzata da qualcun altro/a.")
        return
    if _rischio_distrugge_oggetto(caster, bersaglio, "taumathurgy"):
        return
    origine = bersaglio.location
    bersaglio.move_to(caster, quiet=True)
    caster.msg(magia(f"{bersaglio.key} vola verso di te attraverso lo spazio e ti si materializza in mano."))
    if origine and origine != caster.location:
        origine.msg_contents(f"{bersaglio.key} svanisce improvvisamente.")


def _effetto_consistence(caster, bersaglio, testo):
    if _rischio_distrugge_oggetto(caster, bersaglio, "taumathurgy"):
        return
    bersaglio.db.non_deperibile = True
    caster.msg(magia(f"{bersaglio.key} smette di deteriorarsi: la decomposizione si e' fermata."))


def _effetto_permanence(caster, bersaglio, testo):
    if _rischio_distrugge_oggetto(caster, bersaglio, "taumathurgy"):
        return
    bersaglio.db.indistruttibile = True
    caster.msg(magia(f"{bersaglio.key} risplende per un istante: e' ora praticamente indistruttibile."))


def _effetto_recharge(caster, bersaglio, testo):
    if bersaglio.db.cariche_max is None:
        caster.msg(f"{bersaglio.key} non e' il genere di oggetto che si ricarica a cariche.")
        return
    if _rischio_distrugge_oggetto(caster, bersaglio, "taumathurgy", rischio_base=15):
        return
    bersaglio.db.cariche = bersaglio.db.cariche_max
    caster.msg(magia(f"{bersaglio.key} torna a brillare di energia: le sue cariche sono di nuovo piene."))


def _effetto_universality(caster, bersaglio, testo):
    if _rischio_distrugge_oggetto(caster, bersaglio, "taumathurgy"):
        return
    # Nessuna restrizione di zona esiste in questo porting da rimuovere:
    # l'incantesimo non ha un effetto meccanico reale, resta di scena -
    # semplificazione dichiarata esplicitamente (vedi world/spells.py).
    caster.msg(magia(f"{bersaglio.key} risplende per un istante, come se potesse esistere ovunque."))


def _effetto_personalize_weapon(caster, bersaglio, testo):
    if not bersaglio.db.tipo_arma:
        caster.msg(f"{bersaglio.key} non e' un'arma.")
        return
    if _rischio_distrugge_oggetto(caster, bersaglio, "enchant_weapon"):
        return
    bersaglio.db.personalizzata_da = caster
    caster.msg(magia(f"Imbui {bersaglio.key} con parte della tua stessa forza vitale: solo tu potrai richiamarla con Anima Arma."))


# --- Magia degli Antichi -----------------------------------------------

def _effetto_armor_of_ygolonac(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "riduzione_danno_temp", 0.75, 180,
                             f"L'Armatura di Ygolonac di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{caster.key} avvolge {bersaglio.key} in uno scudo arcano che respinge i colpi fisici."))


def _effetto_curse_of_the_hunter(caster, bersaglio, testo):
    if bersaglio.livello_per_equip() <= caster.livello_per_equip():
        caster.msg(f"{bersaglio.key} non e' abbastanza forte da giustificare la Maledizione del Cacciatore.")
        return
    orrore = _crea_alleato_temporaneo(
        caster, "un Orrore Cacciatore", caster.livello_per_equip() + 10, 80,
        {"hand_to_hand": 70}, 300, bersaglio_iniziale=bersaglio,
    )
    caster.location.msg_contents(magia(f"{caster.key} evoca {orrore.key}, scagliandolo contro {bersaglio.key}!"))


# --- Fase K, nona tornata: clerical_magic/elemental_combat/protective_magic,
# mancate per una svista durante l'audit della ottava tornata (stesso
# identico pattern "requires the X skill" di quella tornata - vedi la nota
# in cima a world/spells.py). ---

def _effetto_clerical_symbol(caster, bersaglio, testo):
    bersaglio.db.simbolo_clericale = True
    caster.location.msg_contents(magia(f"{caster.key} consacra {bersaglio.key}, trasformandolo/a in un simbolo sacro."))


def _effetto_revenge_of_cthugha(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp", -0.5, 120,
                             f"{bersaglio.key} non e' piu' vulnerabile al fuoco.")
    caster.location.msg_contents(magia(f"{caster.key} maledice {bersaglio.key}, rendendolo/a vulnerabile al fuoco."))


def _effetto_revenge_of_ithaqua(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp", -0.5, 120,
                             f"{bersaglio.key} non e' piu' vulnerabile al freddo.")
    caster.location.msg_contents(magia(f"{caster.key} maledice {bersaglio.key}, rendendolo/a vulnerabile al freddo."))


def _effetto_revenge_of_yog(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp", -0.5, 120,
                             f"{bersaglio.key} non e' piu' vulnerabile al fulmine.")
    caster.location.msg_contents(magia(f"{caster.key} maledice {bersaglio.key}, rendendolo/a vulnerabile al fulmine."))


def _effetto_revenge_of_tsathoggua(caster, bersaglio, testo):
    # Unica delle quattro Vendette a colpire il danno FISICO (armi), non
    # quello magico - la fonte lo specifica esplicitamente ("to weapons").
    applica_buff_temporaneo(bersaglio, "riduzione_danno_temp", -0.5, 120,
                             f"{bersaglio.key} non e' piu' vulnerabile alle armi.")
    caster.location.msg_contents(magia(f"{caster.key} maledice {bersaglio.key}, rendendolo/a vulnerabile alle armi."))


def _effetto_globe_of_protection(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 45, 120,
                             f"Il Globo di Protezione attorno a {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Una sfera di energia protettiva avvolge {bersaglio.key}, migliorandone drasticamente la classe armatura."))


def _effetto_sanctuary(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "riduzione_danno_temp", 0.5, 120,
                             None)
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp", 0.5, 120,
                             f"Il Santuario attorno a {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{caster.key} avvolge {bersaglio.key} in un Santuario che dimezza ogni danno subito."))


def _effetto_armor(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 15, 120,
                             f"L'Incantesimo d'Armatura su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{caster.key} rinforza magicamente l'armatura di {bersaglio.key}."))


# ==========================================================================
# Fase K, decima tornata: ~74 incantesimi scoperti tramite l'indice
# completo ALLSPELLS (helps/allspells.txt) - vedi la nota introduttiva in
# world/spells.py. Organizzati per famiglia come le pagine sorgente.
# ==========================================================================

def _e_non_morto(bersaglio):
    return bool(
        getattr(bersaglio, "db", None)
        and (bersaglio.db.non_morto or bersaglio.db.sottorazza in ("lich", "vampire"))
    )


# -- Pelle Indurita: i quattro livelli veri --

def _effetto_bark_skin(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 8, 90, f"Pelle di Corteccia di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"La pelle di {bersaglio.key} si indurisce come corteccia."))


def _effetto_stone_skin(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 16, 90, f"Pelle di Pietra di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"La pelle di {bersaglio.key} si indurisce come pietra."))


def _effetto_iron_skin(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 24, 90, f"Pelle di Ferro di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"La pelle di {bersaglio.key} si indurisce come ferro."))


def _effetto_steel_skin(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 32, 90, f"Pelle d'Acciaio di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"La pelle di {bersaglio.key} si indurisce come acciaio."))


# -- Benedizione: le due sorelle --

def _effetto_dark_blessing(caster, bersaglio, testo):
    if _e_non_morto(bersaglio):
        applica_buff_temporaneo(bersaglio, "bonus_colpire", 15, 120, f"La Benedizione Oscura su {bersaglio.key} svanisce.")
        caster.location.msg_contents(magia(f"Un'aura oscura avvolge {bersaglio.key}, che colpira' con piu' facilita'."))
    else:
        danno = random.randint(10, 18)
        _infliggi_danno_magico(caster, bersaglio, danno, "viene bruciato/a dalla Benedizione Oscura")


def _effetto_bestow_blessing(caster, bersaglio, testo):
    bersaglio.db.benedizione = True
    if not bersaglio.db.bevanda:
        bersaglio.db.bevanda = 15
    caster.location.msg_contents(magia(f"{caster.key} pone una benedizione su {bersaglio.key}: chi vi berra' ne trarra' beneficio."))


# -- Frenesia --

def _effetto_blade_of_fury(caster, bersaglio, testo):
    if _rischio_distrugge_oggetto(caster, bersaglio, "frenzy", rischio_base=20):
        return
    bersaglio.db.bonus_danno = (bersaglio.db.bonus_danno or 0) + 4
    delay_sec = 90
    from evennia.utils import delay

    def _fine():
        if bersaglio.pk:
            bersaglio.db.bonus_danno = max(0, (bersaglio.db.bonus_danno or 0) - 4)
    delay(delay_sec, _fine)
    caster.location.msg_contents(magia(f"{bersaglio.key} arde di fiamme furiose, infliggendo molto piu' danno!"))


# -- Scudo Elementale: scudi-riflesso, benedizioni di immunita', parole di
# resistenza. Semplificazione dichiarata: la fonte impone "un solo scudo/
# una sola benedizione/una sola parola alla volta", ma i campi che
# rappresentano questi effetti (riflesso_danno_temp, riduzione_danno_temp/
# _magico_temp) sono condivisi anche da OGNI altro incantesimo difensivo
# gia' costruito (Pelle Indurita, Armatura di Ygolonac, Santuario...) - un
# tentativo iniziale di applicare l'esclusivita' rimuovendo "il buff
# precedente sullo stesso campo" cancellava per errore anche quei buff
# non correlati (bug trovato testando: Scudo di Mana aveva AZZERATO Pelle
# di Pietra/Ferro/Acciaio attive). Qui i tre livelli si limitano quindi a
# sommarsi tra loro come qualunque altro buff, invece di sostituirsi. --

def _effetto_fire_shield(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riflesso_danno_temp", 5, 120, f"Lo Scudo di Fuoco di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Fiamme guizzano attorno a {bersaglio.key}."))


def _effetto_frost_shield(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riflesso_danno_temp", 5, 120, f"Lo Scudo di Gelo di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Schegge di ghiaccio orbitano attorno a {bersaglio.key}."))


def _effetto_lightning_shield(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riflesso_danno_temp", 5, 120, f"Lo Scudo di Fulmine di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Scintille elettriche crepitano attorno a {bersaglio.key}."))


def _effetto_blessing_of_cthugha(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp", 1.0, 120, f"La Benedizione di Cthugha su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} diventa immune al fuoco."))


def _effetto_blessing_of_ithaqua(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp", 1.0, 120, f"La Benedizione di Ithaqua su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} diventa immune al freddo."))


def _effetto_blessing_of_yog(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp", 1.0, 120, f"La Benedizione di Yog su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} diventa immune al fulmine."))


def _effetto_blessing_of_tsathoggua(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riduzione_danno_temp", 1.0, 120, f"La Benedizione di Tsathoggua su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} diventa immune alle armi."))


def _effetto_word_of_cthugha(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp2", 0.4, 120, f"La Parola di Cthugha su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} diventa resistente al fuoco."))


def _effetto_word_of_ithaqua(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp2", 0.4, 120, f"La Parola di Ithaqua su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} diventa resistente al freddo."))


def _effetto_word_of_yog(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riduzione_danno_magico_temp2", 0.4, 120, f"La Parola di Yog su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} diventa resistente al fulmine."))


def _effetto_word_of_tsathoggua(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    applica_buff_temporaneo(bersaglio, "riduzione_danno_temp2", 0.4, 120, f"La Parola di Tsathoggua su {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"{bersaglio.key} diventa resistente alle armi."))


# -- Magia del Soffio: manca solo Stordente --

def _effetto_stun_breath(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} esala un soffio concussivo contro {bersaglio.key}!"))
    applica_stato(bersaglio, "paralizzato", 15, f"{bersaglio.key} si riprende dallo stordimento.")


# -- Via dell'Evocatore --

def _effetto_call_pet(caster, bersaglio, testo):
    seguaci = [s for s in (caster.db.seguaci or []) if s.pk]
    caster.db.seguaci = seguaci
    lontani = [s for s in seguaci if s.location != caster.location]
    if not lontani:
        caster.msg("Nessuno dei tuoi seguaci e' perso o separato da te.")
        return
    for seguace in lontani:
        seguace.move_to(caster.location, quiet=True)
    caster.location.msg_contents(magia(f"{caster.key} richiama a se' {', '.join(s.key for s in lontani)}."))


def _effetto_create_figurine(caster, bersaglio, testo):
    seguaci = caster.db.seguaci or []
    if bersaglio not in seguaci:
        caster.msg(f"{bersaglio.key} non e' un tuo seguace.")
        return
    from evennia.utils import create
    figurina = create.create_object("typeclasses.objects.Object", key=f"una statuetta di {bersaglio.key}", location=caster)
    figurina.db.desc = "Una piccola statuetta, comoda da trasportare. USE per farla tornare in vita."
    figurina.db.seguace_racchiuso = bersaglio
    caster.db.seguaci = [s for s in seguaci if s is not bersaglio]
    bersaglio.move_to(None, quiet=True)
    caster.msg(magia(f"{bersaglio.key} si rimpicciolisce e si trasforma in {figurina.key}."))


def _effetto_dimensional_pouch(caster, bersaglio, testo):
    caster.msg(magia("Uno squarcio si apre nello spazio, dandoti accesso immediato al tuo armadietto:"))
    caster.execute_cmd("armadietto")


def _effetto_elder_watcher(caster, bersaglio, testo):
    guardiano = _crea_alleato_temporaneo(
        caster, "un Guardiano degli Antichi", caster.livello_per_equip() + 10, 90,
        {"hand_to_hand": 60}, 600,
    )
    guardiano.db.evocato_da = None
    guardiano.db.ostile = True
    guardiano.db.attacca_a_vista = True
    guardiano.db.guardiano_elder = caster
    caster.location.msg_contents(magia(f"{caster.key} evoca {guardiano.key} a sorvegliare la stanza!"))


def _effetto_summon_spirit(caster, bersaglio, testo):
    spirito = _crea_alleato_temporaneo(
        caster, "uno spirito arcano evocato", caster.livello_per_equip(), 40,
        {"hand_to_hand": 30, "magic_missile": 40}, 900,
    )
    caster.location.msg_contents(magia(f"{caster.key} evoca {spirito.key}, senziente e capace di lanciare incantesimi."))


_OGGETTI_CREAZIONE_MINORE = {"boat": "una barca", "barca": "una barca", "bag": "una sacca", "sacca": "una sacca", "tool": "una vanga", "vanga": "una vanga"}
_OGGETTI_CREAZIONE_MAGGIORE = {"anvil": "un'incudine", "incudine": "un'incudine", "amber": "una scaglia d'ambra", "ambra": "una scaglia d'ambra", "chains": "delle catene", "catene": "delle catene", "shield": "uno scudo", "scudo": "uno scudo"}


def _effetto_lesser_creation(caster, bersaglio, testo):
    scelta = _OGGETTI_CREAZIONE_MINORE.get((testo or "").strip().lower())
    if not scelta:
        caster.msg("Scegli tra: barca, sacca, vanga.")
        return
    from evennia.utils import create, delay
    oggetto = create.create_object("typeclasses.objects.Object", key=scelta, location=caster)
    oggetto.db.desc = f"{scelta.capitalize()}, formata dal nulla. Non e' permanente."
    delay(1800, oggetto.delete)
    caster.msg(magia(f"Formi dal nulla {scelta}."))


def _effetto_greater_creation(caster, bersaglio, testo):
    scelta = _OGGETTI_CREAZIONE_MAGGIORE.get((testo or "").strip().lower())
    if not scelta:
        caster.msg("Scegli tra: incudine, ambra, catene, scudo.")
        return
    from evennia.utils import create, delay
    oggetto = create.create_object("typeclasses.objects.Object", key=scelta, location=caster)
    oggetto.db.desc = f"{scelta.capitalize()}, formata dal nulla. Non e' permanente."
    if scelta == "un'incudine":
        oggetto.db.incudine = True
    delay(1800, oggetto.delete)
    caster.msg(magia(f"Formi dal nulla {scelta}."))


# -- Magia del Caos --

def _effetto_cause_riot(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} scatena le forze del caos: la follia si diffonde nell'aria!"))
    for npc in list(caster.location.contents):
        if npc.is_typeclass("typeclasses.npcs.NPC", exact=False) and getattr(npc, "vivo", False):
            npc.db.ostile = True
            npc.db.attacca_a_vista = True


def _effetto_change_sex(caster, bersaglio, testo):
    from evennia.utils import delay
    originale = bersaglio.db.genere or "m"
    bersaglio.db.genere = "f" if originale == "m" else "m"
    caster.location.msg_contents(magia(f"{caster.key} muta temporaneamente il genere di {bersaglio.key}!"))

    def _fine():
        if bersaglio.pk:
            bersaglio.db.genere = originale
    delay(180, _fine)


def _effetto_chaos(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} apre un canale verso le pure forze del caos: la stanza intera viene lacerata!"))
    _danno_area(caster, 15, 28, "viene ferito/a dal Caos", includi_caster=True)


def _effetto_entropy(caster, bersaglio, testo):
    oggetti = [o for o in (bersaglio.db.equip or {}).values() if o]
    if not oggetti:
        caster.msg(f"{bersaglio.key} non indossa o impugna nulla da danneggiare.")
        return
    for oggetto in oggetti:
        oggetto.db.condizione = max(0, (oggetto.db.condizione or 100) - random.randint(15, 30))
    caster.location.msg_contents(magia(f"Un campo di energia avvolge {bersaglio.key}, corrodendo il suo equipaggiamento."))


# -- singoli --

def _effetto_acid_rain(caster, bersaglio, testo):
    if caster.location.db.meteo != "tempestoso":
        caster.msg("L'area deve gia' soffrire di maltempo perche' questo incantesimo funzioni.")
        return
    caster.location.msg_contents(magia(f"{caster.key} scatena una pioggia acida sull'intera area!"))
    _danno_area(caster, 15, 25, "viene ustionato/a dalla pioggia acida")
    for presente in list(caster.location.contents):
        for oggetto in (getattr(presente, "db", None) and presente.db.equip or {}).values():
            if oggetto:
                oggetto.db.condizione = max(0, (oggetto.db.condizione or 100) - random.randint(5, 15))


def _effetto_agony(caster, bersaglio, testo):
    danno = random.randint(20, 32)
    _infliggi_danno_magico(caster, bersaglio, danno, "e' scosso/a da un dolore agonizzante")


def _effetto_fear(caster, bersaglio, testo):
    if bersaglio.db.combat_target is not caster and caster.db.combat_target is not bersaglio:
        caster.msg(f"Puoi lanciare Paura solo su chi e' impegnato in combattimento con te.")
        return
    applica_stato(bersaglio, "impaurito", 60, f"{bersaglio.key} si riprende dalla paura.")
    caster.location.msg_contents(magia(f"{bersaglio.key} viene colto/a da un terrore incontrollabile!"))


def _effetto_paralysis(caster, bersaglio, testo):
    applica_stato(bersaglio, "paralizzato", 30, f"{bersaglio.key} torna a potersi muovere.")
    caster.location.msg_contents(magia(f"{bersaglio.key} si irrigidisce, incapace di fare altro che difendersi."))


def _effetto_confuse_hunters(caster, bersaglio, testo):
    # Semplificazione dichiarata: nessun sistema di inseguimento/tracciamento
    # dei mostri in fuga esiste ancora in questo porting - lo stato resta
    # pronto per quando esistera'.
    applica_stato(caster, "traccia_nascosta", 300, "Le tue tracce tornano visibili.")
    caster.msg(magia("Copri le tue tracce con un velo magico."))


def _effetto_consecrate_doll(caster, bersaglio, testo):
    bambola_vuota = next((o for o in caster.contents if o.db.bambola_vuota), None)
    if not bambola_vuota:
        caster.msg("Devi tenere in mano una bambola voodoo vuota.")
        return
    capelli = next((o for o in caster.contents if o.db.capelli_di is bersaglio), None)
    if not capelli:
        caster.msg(f"Devi prima tagliare dei capelli di {bersaglio.key} con CUT.")
        return
    bambola_vuota.delete()
    capelli.delete()
    from evennia.utils import create
    bambola = create.create_object("typeclasses.objects.Object", key=f"una bambola voodoo di {bersaglio.key}", location=caster)
    bambola.db.desc = f"Una bambola personalizzata, legata a {bersaglio.key} da un filo invisibile."
    bambola.db.bambola_di = bersaglio
    bambola.db.integrita = 100
    caster.msg(magia(f"Combini capelli e bambola: {bambola.key} e' ora pronta."))


def _effetto_counter_magic(caster, bersaglio, testo):
    # Semplificazione dichiarata: a differenza di Cancellazione/Dissolvere
    # la Magia (che rimuovono tutto insieme), la fonte descrive Contromagia
    # come mirata a un singolo effetto per nome - qui, non avendo un
    # registro di effetti "nominabili" dal giocatore, si rimuove un solo
    # effetto scelto a caso tra quelli attivi invece di tutti insieme.
    stati = list((bersaglio.db.stati or {}).keys())
    if stati:
        rimuovi_stato(bersaglio, random.choice(stati))
        caster.location.msg_contents(magia(f"{caster.key} dissolve un singolo effetto magico su {bersaglio.key}."))
    else:
        caster.msg(f"{bersaglio.key} non ha effetti magici rimuovibili in questo modo.")


def _effetto_dispel_room(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} tenta di dissolvere ogni effetto magico nella stanza."))
    for presente in list(caster.location.contents):
        if getattr(presente, "vivo", False):
            _dissolvi_tutto(presente)


def _effetto_create_grimoire(caster, bersaglio, testo):
    from evennia.utils import create
    libro = create.create_object("typeclasses.objects.Object", key="un grimorio", location=caster)
    libro.db.desc = "Un libro magico su cui annotare le Discipline scoperte in giro per il mondo."
    caster.msg(magia(f"{libro.key} si materializza tra le tue mani."))


def _effetto_curse_of_the_mummy(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "bonus_colpire", -25, 120, f"La Maledizione della Mummia su {bersaglio.key} svanisce.")
    applica_stato(bersaglio, "maledetto", 120, None)
    caster.location.msg_contents(magia(f"L'anima di {bersaglio.key} si macchia di un'antica maledizione."))


def _trova_uscita_portale(caster, testo):
    from world.porte import trova_uscita
    return trova_uscita(caster, (testo or "").strip()) if testo else None


def _effetto_destroy_portal(caster, bersaglio, testo):
    if not bersaglio or "varco arcano" not in getattr(bersaglio, "key", ""):
        caster.msg("Non e' un portale.")
        return
    stanza = bersaglio.location
    bersaglio.delete()
    if stanza:
        stanza.msg_contents("Un portale si richiude e svanisce.")


def _effetto_dispel_portals(caster, bersaglio, testo):
    chiusi = 0
    for uscita in list(caster.location.exits):
        if "varco arcano" in uscita.key:
            uscita.delete()
            chiusi += 1
    caster.location.msg_contents(magia(f"{caster.key} dissolve {chiusi} portali nella stanza." if chiusi else f"{caster.key} non trova portali da dissolvere."))


def _effetto_divine_portal(caster, bersaglio, testo):
    if (caster.db.fame or 0) < 10:
        caster.msg("Ti servono almeno 10 punti Fama per questo incantesimo.")
        return
    ancora = caster.db.ancora_psichica
    if not ancora or not ancora.pk:
        caster.msg("Devi prima ancorare un luogo con Ancora Psichica per aprire un varco verso di esso.")
        return
    caster.db.fame -= 10
    from evennia.utils import create, delay
    origine = caster.location
    andata = create.create_object("typeclasses.exits.Exit", key="un varco arcano", location=origine, destination=ancora)
    ritorno = create.create_object("typeclasses.exits.Exit", key="un varco arcano", location=ancora, destination=origine)
    caster.location.msg_contents(magia(f"{caster.key} apre un Portale Divino, capace di attraversare i confini di zona!"))

    def _chiudi():
        for uscita in (andata, ritorno):
            if uscita.pk:
                if uscita.location:
                    uscita.location.msg_contents(magia(f"{uscita.key} si richiude e svanisce."))
                uscita.delete()
    delay(120, _chiudi)


def _effetto_personalize_portal(caster, bersaglio, testo):
    if not bersaglio or "varco arcano" not in getattr(bersaglio, "key", ""):
        caster.msg("Non e' un portale.")
        return
    bersaglio.locks.add(f"traverse:id({caster.id}) or perm(Builder)")
    caster.msg(magia(f"{bersaglio.key} e' ora personalizzato: solo tu puoi attraversarlo."))


def _aura_allineamento(personaggio):
    valore = personaggio.db.alignment or 0
    if valore > 100:
        return "verde"
    if valore < -100:
        return "rossa"
    return None


def _effetto_detect_evil(caster, bersaglio, testo):
    righe = []
    for presente in caster.location.contents:
        if getattr(presente, "vivo", False) and (presente.db.alignment or 0) < -100:
            righe.append(f"  {presente.key} e' avvolto/a da un'aura rossa.")
    caster.msg("\n".join(righe) if righe else "Non percepisci nessuna aura malvagia nei dintorni.")


def _effetto_detect_good(caster, bersaglio, testo):
    righe = []
    for presente in caster.location.contents:
        if getattr(presente, "vivo", False) and (presente.db.alignment or 0) > 100:
            righe.append(f"  {presente.key} e' avvolto/a da un'aura verde.")
    caster.msg("\n".join(righe) if righe else "Non percepisci nessuna aura benevola nei dintorni.")


def _effetto_exorcism(caster, bersaglio, testo):
    if not _e_non_morto(bersaglio):
        caster.msg(f"{bersaglio.key} non e' non-morto/a: l'Esorcismo non ha alcun effetto.")
        return
    danno = random.randint(35, 55)
    _infliggi_danno_magico(caster, bersaglio, danno, "viene investito/a da una raffica di energia sacra")


def _effetto_farsight(caster, bersaglio, testo):
    stanza = bersaglio.location if bersaglio else caster.location
    righe = [f"Vista Lunga da {stanza.key}:"]
    for uscita in stanza.exits:
        if uscita.destination:
            altre_uscite = [u.key for u in uscita.destination.exits]
            righe.append(f"  verso {uscita.key}: {uscita.destination.key} (uscite: {', '.join(altre_uscite) or 'nessuna'})")
    caster.msg("\n".join(righe))


def _effetto_fatigue(caster, bersaglio, testo):
    bersaglio.db.move = max(0, (bersaglio.db.move or 0) - random.randint(50, 100))
    applica_buff_temporaneo(bersaglio, "mod_temp_str", -4, 60, f"{bersaglio.key} riprende la propria Forza.")
    caster.location.msg_contents(magia(f"{bersaglio.key} sente la propria vitalita' prosciugarsi."))
    if not bersaglio.db.combat_target and bersaglio is not caster:
        bersaglio.avvia_combattimento(caster)


def _effetto_flamestrike(caster, bersaglio, testo):
    danno = random.randint(35, 55)
    _infliggi_danno_magico(caster, bersaglio, danno, "viene investito/a da una colonna di fuoco")


def _effetto_giant_strength(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "mod_temp_str", 9, 60, f"{bersaglio.key} riprende la propria Forza naturale.")
    caster.location.msg_contents(magia(f"{bersaglio.key} sente la forza di un gigante scorrere nelle proprie membra."))


def _effetto_godlike_strength(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "mod_temp_str", 14, 60, f"{bersaglio.key} riprende la propria Forza naturale.")
    caster.location.msg_contents(magia(f"{bersaglio.key} sente una forza quasi divina scorrere nelle proprie membra."))


def _effetto_heatstrike(caster, bersaglio, testo):
    from world.equipment import arma_equipaggiata
    arma = arma_equipaggiata(bersaglio)
    if not arma:
        caster.msg(f"{bersaglio.key} non impugna nessuna arma da colpire.")
        return
    arma.db.condizione = max(0, (arma.db.condizione or 100) - random.randint(15, 30))
    caster.location.msg_contents(magia(f"{caster.key} dirige un getto di calore contro l'arma di {bersaglio.key}!"))
    if not arma.db.nodrop and random.randint(1, 100) <= 25:
        equip = bersaglio.db.equip or {}
        for slot, oggetto in list(equip.items()):
            if oggetto is arma:
                equip[slot] = None
        bersaglio.db.equip = equip
        arma.move_to(bersaglio.location, quiet=True)
        caster.location.msg_contents(magia(f"{arma.key} cade a terra, troppo rovente per essere impugnata!"))


def _effetto_incognito(caster, bersaglio, testo):
    if caster.db.maschera:
        caster.db.maschera = None
        caster.location.msg_contents(magia(f"L'illusione attorno a {caster.key} svanisce."))
        return
    caster.db.maschera = bersaglio.key
    caster.msg(magia(f"Assumi l'aspetto di {bersaglio.key}, ovunque esso si trovi realmente."))


def _effetto_metamorphosis(caster, bersaglio, testo):
    # La fonte segnala esplicitamente questo incantesimo come disabilitato
    # ("THIS SPELL HAS BEEN TEMPORARILY DISABLED") - onorato come Lich/Metamorfosi.
    caster.msg("Inizi a mutare forma, ma l'incantesimo si blocca a meta': questo potere resta oltre la tua portata per ora.")


def _effetto_infravision(caster, bersaglio, testo):
    # Fase K, sedicesima tornata: rimossa la vecchia "cura" dello stato
    # "cieco" - era un rattoppo per la versione precedente di Oscurita'
    # (che accecava tutti invece di scurire davvero la stanza, vedi
    # _effetto_darkness); ora che Oscurita' non tocca piu' "cieco",
    # curarlo qui sarebbe scorretto (Infravisione non e' una cura per
    # Accecamento, la fonte non lo suggerisce in nessun modo).
    caster.msg(magia(f"{bersaglio.key} potra' vedere anche nell'oscurita' piu' totale."))
    applica_stato(bersaglio, "vede_al_buio", 600, f"{bersaglio.key} non vede piu' al buio.")


_MESSAGGI_ORACOLO = [
    "'Cio' che cerchi giace dove l'ombra e' piu' lunga.'",
    "'Non tutte le porte si aprono con una chiave.'",
    "'Il tempo scorre diversamente per chi ha visto troppo.'",
    "'Guarda oltre cio' che sembra, non cio' che e'.'",
]


def _effetto_lesser_oracle(caster, bersaglio, testo):
    caster.msg(magia(f"Uno spirito oracolare appare per un istante, sussurrando: {random.choice(_MESSAGGI_ORACOLO)}"))


def _effetto_mage_light(caster, bersaglio, testo):
    # Fase K, sedicesima tornata: ora un vero effetto sulla stanza
    # (world/illuminazione.py), tramite lo stesso schema stato-con-
    # scadenza gia' usato per Oscurita' - prima impostava solo un flag
    # (db.meteo_luce_temp) mai letto da nessuno, e usava evennia.utils.delay
    # (non persistente: si sarebbe perso a un reload del server). 1800
    # secondi (30 minuti) e' la stessa durata gia' scelta in
    # precedenza per "a very long-lasting source of light"
    # (helps/continual_light.txt) - nessuna fonte da' un numero esatto.
    applica_stato(caster.location, "luce_magica", 1800, None)
    caster.msg(magia("Raccogli la luce attorno a te in una piccola sfera luminosa."))


def _effetto_zap(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(4, 8), "viene colpito/a da un fascio di energia viola")


def _effetto_magic_zapper(caster, bersaglio, testo):
    _infliggi_danno_magico(caster, bersaglio, random.randint(20, 32), "viene crivellato/a da una raffica di energia")


def _effetto_magical_campfire(caster, bersaglio, testo):
    ripristino = 15
    caster.db.hp = min(caster.db.hp_max, caster.db.hp + ripristino)
    caster.db.mana = min(caster.db.mana_max, caster.db.mana + ripristino)
    caster.db.move = min(caster.db.move_max, caster.db.move + ripristino * 2)
    caster.location.msg_contents(magia(f"{caster.key} accende un falo' arcano, recuperando immediatamente le forze."))


def _effetto_mana_shield(caster, bersaglio, testo):
    bersaglio = bersaglio or caster
    # Semplificazione dichiarata: la fonte impone "non si possono avere
    # entrambi Scudo di Mana e Scudo Magico attivi insieme", ma
    # bonus_ca_temp e' condiviso da troppi altri incantesimi difensivi per
    # azzerarlo in sicurezza (vedi nota su Scudo Elementale piu' sopra) -
    # qui si somma semplicemente come qualunque altro buff.
    applica_buff_temporaneo(bersaglio, "bonus_ca_temp", 15, 90, f"Lo Scudo di Mana di {bersaglio.key} svanisce.")
    caster.location.msg_contents(magia(f"Una debole sfera di energia avvolge {bersaglio.key}."))


def _effetto_mana_storage(caster, bersaglio, testo):
    mana_totale = caster.db.mana or 0
    if mana_totale <= 0:
        caster.msg("Non hai mana da immagazzinare.")
        return
    pillola_valore = max(1, mana_totale // 5)
    caster.db.mana = 0
    from evennia.utils import create
    pillola = create.create_object("typeclasses.objects.Object", key="una pillola di mana", location=caster)
    pillola.db.desc = "Una piccola pillola che pulsa di energia arcana repressa."
    pillola.db.mana_ripristino = pillola_valore
    caster.msg(magia(f"Consumi tutto il tuo mana per creare {pillola.key} (ripristinera' {pillola_valore} mana)."))


def _effetto_mana_transfer(caster, bersaglio, testo):
    quantita = min(caster.db.mana or 0, 20)
    if quantita <= 0:
        caster.msg("Non hai mana da trasferire.")
        return
    caster.db.mana -= quantita
    bersaglio.db.mana = min(bersaglio.db.mana_max, (bersaglio.db.mana or 0) + quantita)
    caster.location.msg_contents(magia(f"{caster.key} trasferisce parte del proprio mana a {bersaglio.key}."))


def _effetto_material_anchor(caster, bersaglio, testo):
    caster.db.ancora_materiale = caster.location
    caster.msg(magia(f"Crei un'ancora materiale permanente in {caster.location.key}."))


def _effetto_power_word(caster, bersaglio, testo):
    # Confermato dalla fonte: "By itself, it does nothing" - nessuna quest
    # di questo porting controlla ancora una parola/stanza specifica.
    caster.msg(f"Pronunci '{testo}', ma per ora non succede nulla.")


def _effetto_primal_scream(caster, bersaglio, testo):
    danno = random.randint(18, 30)
    caster.location.msg_contents(magia(f"{caster.key} emette un urlo arcano assordante!"))
    _infliggi_danno_magico(caster, bersaglio, danno, "viene scosso/a dall'urlo")


def _effetto_refresh(caster, bersaglio, testo):
    bersaglio.db.move = min(bersaglio.db.move_max, (bersaglio.db.move or 0) + random.randint(20, 40))
    from world.effetti import rimuovi_stato
    rimuovi_stato(bersaglio, "affaticato")
    caster.location.msg_contents(magia(f"{bersaglio.key} si sente un po' piu' riposato/a."))


def _effetto_restore_limb(caster, bersaglio, testo):
    _cura(caster, bersaglio, random.randint(15, 25), "Ripristina Arto")


def _effetto_silence(caster, bersaglio, testo):
    caster.location.msg_contents(magia(f"{caster.key} ammutolisce l'intera stanza!"))
    for presente in list(caster.location.contents):
        if getattr(presente, "vivo", False):
            applica_stato(presente, "muto", 45, f"{presente.key} ritrova la voce.")


def _effetto_slow(caster, bersaglio, testo):
    applica_buff_temporaneo(bersaglio, "mod_temp_dex", -8, 60, f"{bersaglio.key} riprende la propria velocita' naturale.")
    caster.location.msg_contents(magia(f"{bersaglio.key} rallenta innaturalmente."))
    if not bersaglio.db.combat_target and bersaglio is not caster:
        bersaglio.avvia_combattimento(caster)


def _effetto_step_lightly(caster, bersaglio, testo):
    bersaglio.db.move = min(bersaglio.db.move_max, (bersaglio.db.move or 0) + random.randint(60, 100))
    caster.location.msg_contents(magia(f"{bersaglio.key} si sente molto piu' riposato/a."))


def _effetto_true_invis(caster, bersaglio, testo):
    applica_stato(caster, "vera_invisibilita", 900, None)
    rendi_invisibile(caster, 900, f"{caster.key} ridiventa visibile.")
    caster.msg(magia("Ti dissolvi quasi completamente: nemmeno chi sa Rilevare l'Invisibile potra' vederti, nemmeno in combattimento."))


def _effetto_true_sight(caster, bersaglio, testo):
    applica_stato(caster, "vede_attraverso_maschere", 300, "Non riesci piu' a vedere attraverso le illusioni.")
    caster.msg(magia(f"I tuoi occhi si affinano: per un po' vedrai attraverso ogni illusione, inclusa quella di {bersaglio.key}."))


_EFFETTI = {
    "cure_light": _effetto_cure_light,
    "shocking_grasp": _effetto_shocking_grasp,
    "bless": _effetto_bless,
    "detect_magic": _effetto_detect_magic,
    "mask_self": _effetto_mask_self,
    "clairvoyance": _effetto_clairvoyance,

    "acid_blast": _effetto_acid_blast,
    "acid_breath": _effetto_acid_breath,
    "burning_hands": _effetto_burning_hands,
    "cause_light": _effetto_cause_light,
    "cause_serious": _effetto_cause_serious,
    "cause_critical": _effetto_cause_critical,
    "harm": _effetto_harm,
    "chill_touch": _effetto_chill_touch,
    "colour_spray": _effetto_colour_spray,
    "demonfire": _effetto_demonfire,
    "fire_breath": _effetto_fire_breath,
    "frost_breath": _effetto_frost_breath,
    "lightning_breath": _effetto_lightning_breath,
    "fireball": _effetto_fireball,
    "lightning_bolt": _effetto_lightning_bolt,
    "magic_missile": _effetto_magic_missile,
    "magefire": _effetto_magefire,
    "energy_drain": _effetto_energy_drain,
    "dispel_evil": _effetto_dispel_evil,
    "dispel_good": _effetto_dispel_good,

    "call_lightning": _effetto_call_lightning,
    "chain_lightning": _effetto_chain_lightning,
    "gas_breath": _effetto_gas_breath,
    "earthquake": _effetto_earthquake,

    "cure_serious": _effetto_cure_serious,
    "cure_critical": _effetto_cure_critical,
    "heal": _effetto_heal,
    "mass_healing": _effetto_mass_healing,
    "regeneration": _effetto_regeneration,

    "haste": _effetto_haste,
    "strength": _effetto_strength,
    "weaken": _effetto_weaken,
    "age": _effetto_age,
    "youth": _effetto_youth,
    "harden_skin": _effetto_harden_skin,
    "elemental_shield": _effetto_elemental_shield,
    "shield": _effetto_shield,
    "lesser_protection": _effetto_lesser_protection,
    "absorb_magic": _effetto_absorb_magic,
    "protection_evil": _effetto_protection_evil,
    "protection_good": _effetto_protection_good,
    "frenzy": _effetto_frenzy,
    "fly": _effetto_fly,
    "water_breathing": _effetto_water_breathing,
    "vocalize": _effetto_vocalize,

    "blindness": _effetto_blindness,
    "cure_blindness": _effetto_cure_blindness,
    "curse": _effetto_curse,
    "remove_curse": _effetto_remove_curse,
    "mute": _effetto_mute,
    "sleep": _effetto_sleep,
    "charm_person": _effetto_charm_person,
    "calm": _effetto_calm,
    "remove_fear": _effetto_remove_fear,
    "poison": _effetto_poison,
    "cure_poison": _effetto_cure_poison,
    "plague": _effetto_plague,
    "cure_disease": _effetto_cure_disease,
    "faerie_fire": _effetto_faerie_fire,

    "dispel_magic": _effetto_dispel_magic,
    "cancellation": _effetto_cancellation,
    "negate_alignment": _effetto_negate_alignment,

    "detect_hidden": _effetto_detect_hidden,
    "detect_invis": _effetto_detect_invis,
    "faerie_fog": _effetto_faerie_fog,
    "detect_poison": _effetto_detect_poison,
    "know_alignment": _effetto_know_alignment,
    "identify": _effetto_identify,
    "vision": _effetto_vision,
    "locate_object": _effetto_locate_object,
    "continual_light": _effetto_continual_light,
    "aura": _effetto_aura,

    "invis": _effetto_invis,
    "mass_invis": _effetto_mass_invis,
    "remove_invis": _effetto_remove_invis,

    "teleport": _effetto_teleport,
    "gate": _effetto_gate,
    "psychic_anchor": _effetto_psychic_anchor,
    "word_of_recall": _effetto_word_of_recall,
    "portal": _effetto_portal,
    "pass_door": _effetto_pass_door,
    "ventriloquate": _effetto_ventriloquate,

    "lesser_possession": _effetto_lesser_possession,
    "greater_possession": _effetto_greater_possession,

    "summon_familier": _effetto_summon_familier,
    "holy_word": _effetto_holy_word,
    "summon": _effetto_summon,

    "enchant_weapon": _effetto_enchant_weapon,
    "enchant_armor": _effetto_enchant_armor,
    "brand": _effetto_brand,

    "create_food": _effetto_create_food,
    "create_buffet": _effetto_create_buffet,
    "create_water": _effetto_create_water,
    "create_spring": _effetto_create_spring,
    "create_potion": _effetto_create_potion,

    "control_weather": _effetto_control_weather,

    "asceticism": _effetto_asceticism,
    "burden_of_blubber": _effetto_burden_of_blubber,
    "slender_lines": _effetto_slender_lines,
    "burning_thirst": _effetto_burning_thirst,
    "gnawing_hunger": _effetto_gnawing_hunger,
    "change_size": _effetto_change_size,
    "free_grog": _effetto_free_grog,
    "ghastly_sobriety": _effetto_ghastly_sobriety,
    "hallucinate": _effetto_hallucinate,
    "relax": _effetto_relax,

    "animate_dead": _effetto_animate_dead,
    "lich": _effetto_lich,
    "darkness": _effetto_darkness,
    "mummify": _effetto_mummify,
    "desecrate": _effetto_desecrate,
    "soul_blade": _effetto_soul_blade,
    "doppelganger": _effetto_doppelganger,
    "spring_of_blood": _effetto_spring_of_blood,
    "fist_of_azathoth": _effetto_fist_of_azathoth,
    "unrest": _effetto_unrest,

    "mortalize": _effetto_mortalize,
    "summon_old": _effetto_summon_old,
    "soul_guard": _effetto_soul_guard,

    "trance": _effetto_trance,
    "true_dreaming": _effetto_true_dreaming,
    "rude_awakening": _effetto_rude_awakening,
    "recurring_dream": _effetto_recurring_dream,
    "enchanted_sleep": _effetto_enchanted_sleep,
    "accursed_sleep": _effetto_accursed_sleep,

    "astral_walk": _effetto_astral_walk,
    "astral_blast": _effetto_astral_blast,
    "mind_meld": _effetto_mind_meld,

    "create_seed": _effetto_create_seed,
    "drain_vitality": _effetto_drain_vitality,
    "insect_curse": _effetto_insect_curse,
    "wolfbite": _effetto_wolfbite,

    "magical_duel": _effetto_magical_duel,
    "mental_shield": _effetto_mental_shield,
    "psi_twister": _effetto_psi_twister,
    "telekinesis": _effetto_telekinesis,
    "terror_of_the_old": _effetto_terror_of_the_old,
    "wrath_of_cthugha": _effetto_wrath_of_cthugha,
    "wrath_of_ithaqua": _effetto_wrath_of_ithaqua,

    "animate_weapon": _effetto_animate_weapon,
    "consistence": _effetto_consistence,
    "permanence": _effetto_permanence,
    "recharge": _effetto_recharge,
    "universality": _effetto_universality,
    "personalize_weapon": _effetto_personalize_weapon,

    "armor_of_ygolonac": _effetto_armor_of_ygolonac,
    "curse_of_the_hunter": _effetto_curse_of_the_hunter,

    "clerical_symbol": _effetto_clerical_symbol,
    "revenge_of_cthugha": _effetto_revenge_of_cthugha,
    "revenge_of_ithaqua": _effetto_revenge_of_ithaqua,
    "revenge_of_tsathoggua": _effetto_revenge_of_tsathoggua,
    "revenge_of_yog": _effetto_revenge_of_yog,
    "globe_of_protection": _effetto_globe_of_protection,
    "sanctuary": _effetto_sanctuary,
    "armor": _effetto_armor,

    "bark_skin": _effetto_bark_skin,
    "stone_skin": _effetto_stone_skin,
    "iron_skin": _effetto_iron_skin,
    "steel_skin": _effetto_steel_skin,

    "dark_blessing": _effetto_dark_blessing,
    "bestow_blessing": _effetto_bestow_blessing,

    "blade_of_fury": _effetto_blade_of_fury,

    "fire_shield": _effetto_fire_shield,
    "frost_shield": _effetto_frost_shield,
    "lightning_shield": _effetto_lightning_shield,
    "blessing_of_cthugha": _effetto_blessing_of_cthugha,
    "blessing_of_ithaqua": _effetto_blessing_of_ithaqua,
    "blessing_of_yog": _effetto_blessing_of_yog,
    "blessing_of_tsathoggua": _effetto_blessing_of_tsathoggua,
    "word_of_cthugha": _effetto_word_of_cthugha,
    "word_of_ithaqua": _effetto_word_of_ithaqua,
    "word_of_yog": _effetto_word_of_yog,
    "word_of_tsathoggua": _effetto_word_of_tsathoggua,

    "stun_breath": _effetto_stun_breath,

    "call_pet": _effetto_call_pet,
    "create_figurine": _effetto_create_figurine,
    "dimensional_pouch": _effetto_dimensional_pouch,
    "elder_watcher": _effetto_elder_watcher,
    "summon_spirit": _effetto_summon_spirit,
    "lesser_creation": _effetto_lesser_creation,
    "greater_creation": _effetto_greater_creation,

    "cause_riot": _effetto_cause_riot,
    "change_sex": _effetto_change_sex,
    "chaos": _effetto_chaos,
    "entropy": _effetto_entropy,

    "acid_rain": _effetto_acid_rain,
    "agony": _effetto_agony,
    "fear": _effetto_fear,
    "paralysis": _effetto_paralysis,
    "confuse_hunters": _effetto_confuse_hunters,
    "consecrate_doll": _effetto_consecrate_doll,
    "counter_magic": _effetto_counter_magic,
    "dispel_room": _effetto_dispel_room,
    "create_grimoire": _effetto_create_grimoire,
    "curse_of_the_mummy": _effetto_curse_of_the_mummy,
    "destroy_portal": _effetto_destroy_portal,
    "dispel_portals": _effetto_dispel_portals,
    "divine_portal": _effetto_divine_portal,
    "personalize_portal": _effetto_personalize_portal,
    "detect_evil": _effetto_detect_evil,
    "detect_good": _effetto_detect_good,
    "exorcism": _effetto_exorcism,
    "farsight": _effetto_farsight,
    "fatigue": _effetto_fatigue,
    "flamestrike": _effetto_flamestrike,
    "giant_strength": _effetto_giant_strength,
    "godlike_strength": _effetto_godlike_strength,
    "heatstrike": _effetto_heatstrike,
    "incognito": _effetto_incognito,
    "metamorphosis": _effetto_metamorphosis,
    "infravision": _effetto_infravision,
    "lesser_oracle": _effetto_lesser_oracle,
    "mage_light": _effetto_mage_light,
    "zap": _effetto_zap,
    "magic_zapper": _effetto_magic_zapper,
    "magical_campfire": _effetto_magical_campfire,
    "mana_shield": _effetto_mana_shield,
    "mana_storage": _effetto_mana_storage,
    "mana_transfer": _effetto_mana_transfer,
    "material_anchor": _effetto_material_anchor,
    "power_word": _effetto_power_word,
    "primal_scream": _effetto_primal_scream,
    "refresh": _effetto_refresh,
    "restore_limb": _effetto_restore_limb,
    "silence": _effetto_silence,
    "slow": _effetto_slow,
    "step_lightly": _effetto_step_lightly,
    "true_invis": _effetto_true_invis,
    "true_sight": _effetto_true_sight,
}
