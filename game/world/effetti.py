"""
Meccaniche generiche per gli effetti degli incantesimi (Fase K, sesta
tornata): fino a questa tornata solo 6 incantesimi su 102 avevano un
vero effetto meccanico in world/magic.py (gli altri 96 mostravano solo
un messaggio di successo senza conseguenze reali - limite dichiarato
esplicitamente fin dalla Fase G). Qui non ci sono formule pubblicate
dal sito originale (come gia' per tutto il resto del combattimento,
vedi typeclasses/living.py): le percentuali/quantita' sono scelte di
design esplicite, scelte per coerenza con le formule gia' esistenti.

Tre meccanismi generici, riusati da decine di incantesimi diversi
invece di scrivere un sistema ad hoc per ciascuno:

- applica_buff_temporaneo (gia' esistente in world/sottorazze.py, qui
  solo re-importata: e' un +delta additivo su un qualunque campo db.*,
  con ripristino automatico dopo N secondi. Usata per bonus/malus di
  colpire, danno, classe armatura, attributi.
- applica_stato / rimuovi_stato / ha_stato: un flag booleano in
  db.stati (dict), con scadenza automatica. Usato per condizioni
  discrete come cieco/muto/addormentato/impaurito/vede_invisibile.
  I punti d'aggancio nel resto del motore: typeclasses/living.py
  (calcola_hit_chance legge "cieco"), world/combat.py:risolvi_round
  (legge "addormentato"/"paralizzato"/"impaurito"), commands/cthulhu.py
  (CmdSay/CmdCast leggono "muto"), server/conf/lockfuncs.py
  (invisibilita_permessa legge db.invisibile e "vede_invisibile").
- applica_danno_periodico: N colpi di danno a intervalli regolari
  (Veleno, Peste) - si autodistrugge da solo dopo l'ultimo colpo.

NOTA sulla terminazione degli script (audit globale pre-beta): qui si
usa sempre `.delete()` e MAI `.stop()`. In Evennia 6.1 `.stop()` si
limita a mettere `is_active=False` lasciando la riga nel database
(nonostante il docstring ereditato dalla classe base affermi il
contrario). Le righe cosi' abbandonate causavano due problemi reali:
si accumulavano senza limite, e venivano RESUSCITATE a ogni riavvio
dal workaround in server/conf/at_server_startstop.py - che quindi
rimetteva in moto anche effetti annullati di proposito (una cecita'
gia' curata, i buff azzerati alla morte del personaggio). `.delete()`
dis-arma il timer e rimuove davvero la riga.

Semplificazione dichiarata: nessuno di questi stati impedisce di per
se' l'esecuzione di ALTRI comandi oltre a quelli esplicitamente
elencati sopra (es. "cieco" non blocca LOOK, "muto" non blocca i
social muti come EMOTE) - la fonte non specifica un elenco esaustivo
di comandi bloccati per ogni condizione, quindi si e' scelto di
agganciare solo i punti piu' rilevanti per il gameplay (il colpire in
combattimento, il parlare, il lanciare incantesimi) invece di
inseguire ogni possibile interazione.
"""

from world.sottorazze import applica_buff_temporaneo  # noqa: F401 (re-esportata)


def applica_stato(personaggio, stato, secondi, messaggio_scadenza=None):
    """Imposta db.stati[stato] = True e programma la rimozione automatica.
    Riassegna esplicitamente db.stati dopo la mutazione (stessa cautela
    gia' usata altrove nel progetto, es. world/yithian.py:YITH ADAPT, per
    garantire che la modifica venga davvero salvata).

    Bug reale corretto (audit globale pre-beta): assegnare `script.interval`
    come semplice attributo NON arma il timer del reattore - lo script
    resta con is_active=False e time_until_next_repeat()=None, quindi lo
    stato non scadeva MAI (fino al primo riavvio del server, dove il
    workaround in server/conf/at_server_startstop.py lo riattivava). E'
    la stessa classe di bug gia' corretta due volte in questo progetto
    (RigenerazioneScript, poi applica_buff_temporaneo e _mistform/_rage):
    la cura e' chiamare .start(interval=..., force_restart=True).
    Corretto qui anche il rinnovo: riapplicare uno stato gia' attivo
    creava un SECONDO script, e la scadenza del primo rimuoveva lo stato
    mentre il secondo era ancora in corso."""
    for vecchio in personaggio.scripts.get(f"stato_{stato}"):
        vecchio.delete()
    stati = personaggio.db.stati or {}
    stati[stato] = True
    personaggio.db.stati = stati
    script = personaggio.scripts.add(
        "typeclasses.scripts.StatoScadenzaScript",
        key=f"stato_{stato}",
    )
    script.db.stato = stato
    script.db.messaggio_scadenza = messaggio_scadenza
    script.start(interval=secondi, force_restart=True)


def rimuovi_stato(personaggio, stato):
    """Rimuove uno stato immediatamente (es. Cura Cecita' su Accecamento)."""
    stati = personaggio.db.stati
    if stati and stato in stati:
        stati.pop(stato, None)
        personaggio.db.stati = stati
    for script in personaggio.scripts.get(f"stato_{stato}"):
        script.delete()


CAMPI_BUFF_NUMERICI = (
    "bonus_ca_temp", "bonus_danno_temp", "bonus_colpire",
    "riduzione_danno_temp", "riduzione_danno_temp2",
    "riduzione_danno_magico_temp", "riduzione_danno_magico_temp2",
    "riflesso_danno_temp", "wimpy_soglia_ignorata_temp",
)


def rimuovi_tutti_gli_effetti_magici(personaggio):
    """Fase K, ventiseiesima tornata: helps/death.txt - "all spell
    affects are instantly removed at the instant of death." Ferma ogni
    stato attivo (incluse le sue eventuali scadenze/danni periodici, non
    solo la voce in db.stati - stessa cautela di world/staff.py:restaura,
    qui estesa a TUTTI gli stati invece del sottoinsieme curabile da
    RESTORE) e azzera i buff/malus numerici temporanei.

    Completato nell'audit globale pre-beta. Mancavano tre cose perche'
    "tutti gli effetti" fosse davvero vero:
    1. i campi numerici venivano azzerati, ma gli script di scadenza dei
       buff restavano vivi: piu' tardi sarebbero scattati RIPRISTINANDO i
       valori precedenti, annullando cioe' la pulizia appena fatta;
    2. l'invisibilita' magica (db.invisibile, che non vive in db.stati)
       sopravviveva alla morte, quindi si rinasceva ancora invisibili;
    3. restava vivo anche il suo script di scadenza."""
    stati = personaggio.db.stati or {}
    for stato in list(stati.keys()):
        for script in personaggio.scripts.get(f"periodico_{stato}"):
            script.delete()
        for script in personaggio.scripts.get(f"stato_{stato}"):
            script.delete()
    personaggio.db.stati = {}

    # buff numerici: prima si eliminano gli script, poi si azzerano i campi
    # (l'ordine conta: al contrario, uno script che scattasse nel frattempo
    # rimetterebbe il valore precedente)
    for campo in CAMPI_BUFF_NUMERICI:
        for script in personaggio.scripts.get(f"buff_{campo}"):
            script.delete()
    for campo in CAMPI_BUFF_NUMERICI:
        setattr(personaggio.db, campo, 0)

    # invisibilita' magica: flag fuori da db.stati, con script dedicato
    for script in personaggio.scripts.get("invis_scadenza"):
        script.delete()
    personaggio.db.invisibile = False


def ha_stato(personaggio, stato):
    return bool((personaggio.db.stati or {}).get(stato))


def rendi_invisibile(personaggio, secondi, messaggio_scadenza=None):
    """Invisibilita' magica vera (Invisibilita'/Invisibilita' di Massa):
    usa i lock dinamici "view"/"search" gia' impostati in
    at_living_creation() (vedi server/conf/lockfuncs.py), non un
    semplice messaggio - il personaggio sparisce davvero dalle liste
    di LOOK e dalla ricerca dei comandi (kill, cast, ecc.), salvo per
    chi ha un livello sufficientemente piu' alto o lo stato
    "vede_invisibile" attivo."""
    for vecchio in personaggio.scripts.get("invis_scadenza"):
        vecchio.delete()
    personaggio.db.invisibile = True
    script = personaggio.scripts.add(
        "typeclasses.scripts.StatoScadenzaScript",
        key="invis_scadenza",
    )
    script.db.campo_bool = "invisibile"
    script.db.messaggio_scadenza = messaggio_scadenza
    # vedi applica_stato() per il bug del timer mai armato corretto qui
    script.start(interval=secondi, force_restart=True)


def applica_danno_periodico(bersaglio, stato, danno_min, danno_max, secondi_tick,
                             numero_tick, messaggio_tick=None, messaggio_fine=None):
    """Infligge danno (danno_min..danno_max) ogni secondi_tick, per
    numero_tick colpi totali (Veleno, Peste); imposta anche lo stato
    (es. "avvelenato") per la durata dell'effetto, rimosso alla fine."""
    for vecchio in bersaglio.scripts.get(f"periodico_{stato}"):
        vecchio.delete()
    stati = bersaglio.db.stati or {}
    stati[stato] = True
    bersaglio.db.stati = stati
    script = bersaglio.scripts.add(
        "typeclasses.scripts.EffettoPeriodicoScript",
        key=f"periodico_{stato}",
    )
    script.db.danno_min = danno_min
    script.db.danno_max = danno_max
    script.db.tick_totali = numero_tick
    script.db.tick_fatti = 0
    script.db.stato = stato
    script.db.messaggio_tick = messaggio_tick
    script.db.messaggio_fine = messaggio_fine
    # vedi applica_stato() per il bug del timer mai armato corretto qui:
    # prima di questa correzione veleno/peste non infliggevano MAI danno
    script.start(interval=secondi_tick, force_restart=True)


def applica_cura_periodica(bersaglio, cura_min, cura_max, secondi_tick, numero_tick,
                            messaggio_tick=None):
    """Variante 'cura' di applica_danno_periodico, per incantesimi come
    Rigenerazione: nessuno stato associato (una guarigione extra non ha
    bisogno di essere rimossa esplicitamente, si esaurisce da sola)."""
    for vecchio in bersaglio.scripts.get("periodico_rigenerazione"):
        vecchio.delete()
    script = bersaglio.scripts.add(
        "typeclasses.scripts.EffettoPeriodicoScript",
        key="periodico_rigenerazione",
    )
    script.db.danno_min = cura_min
    script.db.danno_max = cura_max
    script.db.tick_totali = numero_tick
    script.db.tick_fatti = 0
    script.db.cura = True
    script.db.messaggio_tick = messaggio_tick
    # vedi applica_stato() per il bug del timer mai armato corretto qui
    script.start(interval=secondi_tick, force_restart=True)
