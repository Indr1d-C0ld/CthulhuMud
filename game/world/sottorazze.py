"""
Sottorazze permanenti: Lich, Vampiri, Licantropi ("Were") - Fase G,
ottava tornata. Confermate dalla scansione esaustiva (helps/subraces.txt,
helps/liches.txt, helps/vampires.txt, helps/weres.txt, helps/lineage.txt)
come un intero sistema non ancora costruito.

Meccaniche comuni a tutte e tre (confermate verbatim dalla fonte):
- Trasformazione PERMANENTE e irreversibile - un giocatore deve essere
  avvertito chiaramente prima di sceglierla.
- Si inizia alla 4a generazione. Un membro esistente puo' "iniziare" un
  nuovo membro (LICH BESTOW / VAMPIRE EMBRACE / WERE BITE): il nuovo
  membro riceve generazione = generazione del maestro + 1, e ne eredita
  la casa/gilda. Piu' ci si avvicina alla 1a generazione (piu' "puri"),
  piu' le abilita' sono forti e piu' risorse (sangue/lumen/potere) si
  possono accumulare.
- LINEAGE mostra razza/sottorazza/generazione/ascendenza/casa di tutti i
  personaggi connessi (terminologia della fonte: Progeny/Blood/Scion/
  Child per un discendente minore, Kin/House/Dynasty/People per il
  gruppo, a seconda del tipo).

NON specificato dalla fonte per Lich e Vampiro: come si diventa la
PRIMA volta un Lich/Vampiro (nessuna pagina descrive un rituale o una
quest d'ingresso per questi due) - qui e' un'azione riservata allo
staff (vedi commands/cthulhu_sottorazze.py, CmdSubrace, permesso
Builder+). **Correzione (ventiseiesima tornata, audit sottorazze)**:
questo NON vale per i Were - helps/weres.txt/wolfbite.txt descrivono
l'incantesimo CAST WOLFBITE (nessuna nota "disabled", a differenza di
CAST LICH) come rituale d'ingresso reale e giocabile, gia' costruito
(world/magic.py:_effetto_wolfbite) - SUBRACE resta comunque disponibile
come scorciatoia per lo staff, ma per i Were la fonte descrive anche
una via ordinaria.

Le formule numeriche esatte di ogni comando/abilita' non sono
specificate dalla fonte: scelte di design esplicite documentate nei
singoli comandi.

Gap chiusi nella ventiseiesima tornata (vedi anche
commands/cthulhu_sottorazze.py per i comandi):
- Tetto al pool (sangue/lumen/potere) legato alla generazione (helps/
  subraces.txt: "the more blood and power you can accumulate" - prima
  nessun tetto esisteva). Vedi pool_massimo().
- LICH TOUCH/VAMPIRE SUCK richiedono ora una vittima addormentata
  (helps/lich.txt/vampires.txt: "sleeping or STUNNED victim" - questo
  porting non ha mai avuto una meccanica di stordimento reale, gia'
  dichiarato altrove (world/pk.py) per AUTOKILL: qui si controlla solo
  il sonno, l'unico dei due stati che esiste davvero).
- LICH DOMINATE ora ha una vera probabilita' legata al divario di
  livello (helps/lich.txt: "the bigger the difference... the harder").
- LICH EMPOWER/ENHANCE ora hanno effetti REALI e DISTINTI: EMPOWER
  alza davvero la percentuale di successo degli incantesimi (nuovo
  campo db.bonus_incantesimi, letto da world/magic.py) e impedisce
  l'uso di armi (letto da typeclasses/living.py); ENHANCE alza
  Intelligenza e Saggezza per davvero (mod_temp_int/mod_temp_wis, gia'
  usati da altri incantesimi, mai da qui).
- VAMPIRE MAJESTY ora alza davvero la classe armatura (letta da
  world/equipment.py) e spaventa via i nemici piu' deboli presenti.
- VAMPIRE MISTFORM ora impedisce davvero di colpire e di essere
  colpiti facilmente (letto da typeclasses/living.py).
- Nuovo comando BITE (helps/bite.txt): attacco di combattimento per
  chi ha le zanne fuori, basato sulla skill Corpo a Corpo.
- WERE HEAL non spende piu' lumen oltre il necessario (helps/were.txt:
  "any amount over the base is not spent" - bug reale, spendeva tutto
  il dichiarato anche in eccesso).
- Il pool lumen dei Were ora si ricarica per davvero (helps/weres.txt:
  "in your were form and in moonlight... every 10 seconds... ~3
  lumens") - agganciato al tick di rigenerazione gia' esistente
  (world/posizione.py), approssimato a "di notte" per mancanza di un
  concetto di "outdoor" in questo porting (nessuna pagina lo descrive).
- WERE CHANGE: solo i Were piu' "esperti" (qui: generazione bassa, la
  stessa metrica di "purezza" gia' usata per moltiplicatore_generazione)
  possono trasformarsi A VOLONTA' (helps/weres.txt: "more experienced
  and powerful weres can perform this change at will") - gli altri
  possono farlo solo a luna piena.
- WERE FURY ora scala con la generazione (helps/weres.txt: "boosted an
  amount appropriate to your generation and lumen pool expenditure" -
  prima solo il lumen speso contava).
- WERE GROWL ora spaventa davvero le creature piu' deboli presenti
  (helps/weres.txt: "anyone nearby who hears your growling may panic
  and run away in fear").
- LINEAGE ora mostra tutti i personaggi connessi, non solo quelli
  nella stanza (helps/lineage.txt: "all currently connected players").
- Nuovo comando PRIVACY (helps/lineage.txt lo cita: "use the PRIVACY
  command to hide it") per nascondere la propria riga da LINEAGE altrui.
"""

import random

from world.colori import pericolo

GENERAZIONE_INIZIALE = 4

TERMINOLOGIA = {
    "lich": {"discendente": "scion", "gruppo": "dinastia", "pool": "potere"},
    "vampire": {"discendente": "sangue", "gruppo": "casata", "pool": "sangue"},
    "were": {"discendente": "progenie", "gruppo": "branco", "pool": "lumen"},
}

NOMI_SOTTORAZZA = {"lich": "Lich", "vampire": "Vampiro", "were": "Licantropo"}


def diventa_sottorazza(personaggio, tipo, casa=None):
    """Azione PERMANENTE e irreversibile: rende personaggio un membro di
    tipo ('lich'/'vampire'/'were') alla generazione iniziale (4a)."""
    if tipo not in TERMINOLOGIA:
        return False, "Sottorazza sconosciuta."
    if personaggio.db.sottorazza:
        return False, f"{personaggio.key} e' gia' {NOMI_SOTTORAZZA[personaggio.db.sottorazza]}."
    personaggio.db.sottorazza = tipo
    personaggio.db.generazione = GENERAZIONE_INIZIALE
    personaggio.db.pool_sottorazza = 0
    personaggio.db.casa_sottorazza = casa
    personaggio.db.genitore_sottorazza = None
    if tipo == "were":
        personaggio.db.in_forma_animale = False
    return True, f"{personaggio.key} e' ora {NOMI_SOTTORAZZA[tipo]} (generazione {GENERAZIONE_INIZIALE})."


def induce(maestro, vittima, tipo):
    """LICH BESTOW / VAMPIRE EMBRACE / WERE BITE: porta un membro gia'
    esistente della sottorazza (o una vittima "grezza" gia' resa tale)
    un passo piu' vicino al maestro nella catena. La fonte specifica che
    questi comandi NON creano una nuova sottorazza dal nulla: agiscono
    solo su chi e' gia' di quel tipo."""
    if maestro.db.sottorazza != tipo:
        return False, f"Non sei {NOMI_SOTTORAZZA[tipo]}."
    if vittima.db.sottorazza != tipo:
        return False, f"{vittima.key} non e' {NOMI_SOTTORAZZA[tipo]}."
    vittima.db.generazione = (maestro.db.generazione or GENERAZIONE_INIZIALE) + 1
    vittima.db.casa_sottorazza = maestro.db.casa_sottorazza
    vittima.db.genitore_sottorazza = maestro.key
    return True, (
        f"{vittima.key} e' ora alla generazione {vittima.db.generazione}, "
        f"{TERMINOLOGIA[tipo]['discendente']} di {maestro.key}."
    )


def moltiplicatore_generazione(personaggio):
    """Piu' la generazione e' bassa (vicina a 1), piu' forte l'effetto -
    scelta di design esplicita: 1a generazione = x2, ogni generazione
    in piu' riduce il moltiplicatore del 10% (minimo x0.5)."""
    generazione = personaggio.db.generazione or GENERAZIONE_INIZIALE
    return max(0.5, 2.0 - (generazione - 1) * 0.1)


def spendi_pool(personaggio, quantita):
    pool = personaggio.db.pool_sottorazza or 0
    if quantita > pool:
        return False
    personaggio.db.pool_sottorazza = pool - quantita
    return True


def pool_massimo(personaggio):
    """helps/subraces.txt: "the more blood and power you can accumulate"
    - piu' bassa la generazione (piu' vicina a 1, la piu' pura), piu'
    alto il tetto. Nessuna formula dalla fonte: scelta di design
    esplicita, lineare, con un minimo per non punire troppo chi e'
    lontano dalla 1a generazione."""
    generazione = personaggio.db.generazione or GENERAZIONE_INIZIALE
    return max(20, 150 - generazione * 10)


def guadagna_pool(personaggio, quantita):
    """Aggiunge quantita' al pool, rispettando il tetto di pool_massimo."""
    massimo = pool_massimo(personaggio)
    attuale = personaggio.db.pool_sottorazza or 0
    personaggio.db.pool_sottorazza = min(massimo, attuale + quantita)
    return personaggio.db.pool_sottorazza - attuale


def vittima_vulnerabile_a_drenaggio(vittima):
    """helps/lich.txt/vampires.txt: LICH TOUCH/VAMPIRE SUCK richiedono
    una vittima "sleeping or stunned" - questo porting non ha mai avuto
    una meccanica di stordimento reale (dichiarato in world/pk.py per
    AUTOKILL), quindi qui si controlla solo il sonno (naturale o
    magico)."""
    from world.posizione import DORMENDO
    from world.effetti import ha_stato
    return (vittima.db.posizione or "in_piedi") == DORMENDO or ha_stato(vittima, "addormentato")


PROBABILITA_BASE_DOMINATE = 70
PENALITA_DOMINATE_PER_LIVELLO_DIVARIO = 5


def probabilita_dominate(maestro, npc):
    """helps/lich.txt: "The bigger the difference between your level and
    the victim's the harder it will be" - qui inteso come il livello
    dell'NPC che supera quello del Lich: nessuna formula dalla fonte."""
    divario = max(0, (npc.db.livello or 1) - maestro.livello_per_equip())
    return max(5, PROBABILITA_BASE_DOMINATE - divario * PENALITA_DOMINATE_PER_LIVELLO_DIVARIO)


SOGLIA_GENERAZIONE_WERE_ESPERTO = 5


def were_puo_trasformarsi_a_volonta(personaggio):
    """helps/weres.txt: "more experienced and powerful weres can perform
    this change at will" (gli altri, implicitamente, solo a luna piena
    - vedi CmdWere._change). "Esperienza/potenza" qui e' la stessa
    metrica di "purezza" gia' usata per moltiplicatore_generazione:
    nessuna soglia esatta dalla fonte."""
    generazione = personaggio.db.generazione or GENERAZIONE_INIZIALE
    return generazione <= SOGLIA_GENERAZIONE_WERE_ESPERTO


LUMEN_PER_TICK_MIN, LUMEN_PER_TICK_MAX = 2, 5


def tenta_ricarica_lumen(personaggio):
    """helps/weres.txt: "To recharge your lumen pool you must be in your
    were form and in moonlight... every 10 seconds... approximately 3
    lumens plus some variable amount." Agganciato al tick di
    rigenerazione gia' esistente (world/posizione.py), non a un timer
    di 10 secondi dedicato: l'intervallo reale del tick varia (15-45s,
    vedi typeclasses.scripts.RigenerazioneScript), quindi qui si
    approssima con un guadagno per tick invece che per 10 secondi
    esatti. "In moonlight" e' approssimato a "di notte" (world/tempo.py:
    ora_di_gioco) perche' questo porting non ha un concetto di stanza
    "outdoor" da incrociare con la fase lunare - nessuna pagina della
    fonte lo specifica comunque in dettaglio."""
    if personaggio.db.sottorazza != "were" or not personaggio.db.in_forma_animale:
        return
    from world.tempo import ora_di_gioco
    ora = ora_di_gioco()
    e_notte = ora >= 20 or ora < 6
    if not e_notte:
        return
    guadagna_pool(personaggio, random.randint(LUMEN_PER_TICK_MIN, LUMEN_PER_TICK_MAX))


SECONDI_REALI_PER_ORA_DI_GIOCO = 30   # confermato dalla fonte, immhelp_conditions.txt
GIORNI_CICLO_LUNARE = 28              # confermato dalla fonte: "standard 28 day cycle"

FASI_LUNARI = (
    "nuova", "crescente", "primo quarto", "gibbosa crescente",
    "piena", "gibbosa calante", "ultimo quarto", "calante",
)


def fase_lunare(quando=None):
    """Fase lunare calcolata sul calendario di GIOCO accelerato, non su
    quello reale. Confermato dalla fonte (immhelp_conditions.txt): la
    condizione "moon low high" segue "a standard 28 day cycle" - nello
    stesso paragrafo in cui ogni altra condizione temporale (hour_of_day,
    day_of_month, ecc.) e' esplicitamente ancorata al tempo di GIOCO, con
    "1 hour gametime is 30 seconds real time". Un ciclo di 28 giorni di
    gioco dura quindi 28*24*30 = 20160 secondi reali (~5,6 ore reali),
    non i ~29,5 giorni REALI usati per errore nella prima implementazione
    di questo sistema (Fase G, ottava tornata) - scoperto durante una
    rilettura del codex, corretto qui su richiesta esplicita dell'utente.
    L'epoca (istante reale in cui il calendario di gioco segna "giorno 0,
    luna nuova") non e' specificata dalla fonte: scelta di design
    esplicita, arbitraria."""
    import datetime

    quando = quando or datetime.datetime.utcnow()
    epoca_calendario = datetime.datetime(2000, 1, 6)
    secondi_reali_trascorsi = (quando - epoca_calendario).total_seconds()
    secondi_reali_per_giorno_di_gioco = 24 * SECONDI_REALI_PER_ORA_DI_GIOCO
    giorni_di_gioco_trascorsi = secondi_reali_trascorsi / secondi_reali_per_giorno_di_gioco
    frazione_ciclo = (giorni_di_gioco_trascorsi % GIORNI_CICLO_LUNARE) / GIORNI_CICLO_LUNARE
    return FASI_LUNARI[round(frazione_ciclo * 8) % 8]


def luna_piena():
    return fase_lunare() == "piena"


def applica_buff_temporaneo(personaggio, campo, delta, durata_secondi, messaggio_scadenza=None):
    """Applica +delta a db.<campo> (o crea il campo se assente) e
    programma il ripristino al valore precedente dopo durata_secondi
    (vedi typeclasses.scripts.SottorazzaBuffExpireScript).

    Bug reale corretto (Fase K, ventiseiesima tornata, scoperto testando
    dal vivo LICH EMPOWER due volte di fila): se il buff viene rinnovato
    mentre uno precedente sullo stesso campo e' ancora attivo, il
    "valore originale" da ripristinare deve restare quello di PRIMA del
    PRIMO buff, non quello (gia' alterato) al momento del rinnovo -
    altrimenti il campo resta alterato per sempre anche dopo la
    scadenza. Lo script precedente va anche fermato esplicitamente,
    altrimenti scadrebbe comunque al suo orario originale e
    ripristinerebbe il campo troppo presto, a meta' del rinnovo.

    Attenzione (seconda correzione, stesso test dal vivo): `scripts.get()`
    per chiave ritorna ANCHE gli script gia' scaduti/fermati in passato
    per lo stesso campo (il "quirk" gia' noto di accumulo - vedi
    world/effetti.py:rimuovi_stato - .stop() disattiva ma non cancella
    la riga). Bisogna quindi filtrare esplicitamente solo quelli ancora
    DAVVERO attivi, altrimenti si rischia di agganciarsi al
    valore_precedente stantio di uno script vecchio invece che a quello
    del buff realmente in corso (o di trattare un rinnovo come se non
    ci fosse nulla di attivo, quando invece c'e')."""
    # Quarta correzione (audit globale pre-beta): `.stop()` lasciava la riga
    # nel database (vedi la nota in world/effetti.py), da cui sia l'accumulo
    # descritto sopra sia il rischio che il workaround di riavvio la
    # resuscitasse ripristinando un valore_precedente ormai stantio.
    # Con `.delete()` il filtro su is_active qui sotto diventa una semplice
    # cintura di sicurezza per le righe gia' presenti nel database.
    esistenti = [s for s in personaggio.scripts.get(f"buff_{campo}") if s.is_active]
    if esistenti:
        valore_precedente = esistenti[0].db.valore_precedente
    else:
        valore_precedente = getattr(personaggio.db, campo, 0) or 0
    for script_vecchio in personaggio.scripts.get(f"buff_{campo}"):
        script_vecchio.delete()
    setattr(personaggio.db, campo, (getattr(personaggio.db, campo, 0) or 0) + delta)
    script = personaggio.scripts.add(
        "typeclasses.scripts.SottorazzaBuffExpireScript",
        key=f"buff_{campo}",
    )
    script.db.campo = campo
    script.db.valore_precedente = valore_precedente
    script.db.messaggio_scadenza = messaggio_scadenza
    # Terza correzione, stesso test dal vivo: assegnare .interval come
    # semplice attributo NON riarma il timer gia' avviato da .add() -
    # stesso identico problema gia' risolto per RigenerazioneScript in
    # ventiduesima tornata (typeclasses/scripts.py). Va richiamato
    # esplicitamente .start(), altrimenti lo script non scade mai nel
    # tempo dichiarato (scoperto solo ora perche' nessun uso precedente
    # di questa funzione era mai stato verificato con un'attesa reale).
    script.start(interval=durata_secondi, force_restart=True)


def tenta_bite(vampiro, vittima):
    """BITE (helps/bite.txt): "This combat command... can only be used
    by characters who have fangs [visibili, VAMPIRE FANGS]...
    effectiveness is based off... HAND TO HAND skill." Nessuna formula
    di danno dalla fonte: qui un colpo disarmato con le zanne come arma
    naturale, indipendente da qualunque arma impugnata."""
    if vampiro.db.sottorazza != "vampire":
        return False, "Non sei un Vampiro."
    if not vampiro.db.zanne_visibili:
        return False, "Devi prima scoprire le zanne (VAMPIRE FANGS)."
    # NPC di servizio (NPC.intoccabile): altrimenti il morso annuncerebbe un danno che
    # subisci_danno poi annulla
    from world.pk import e_intoccabile, messaggio_intoccabile
    if e_intoccabile(vittima):
        return False, messaggio_intoccabile(vittima)
    if vampiro.db.combat_target is not vittima:
        vampiro.avvia_combattimento(vittima)
    if random.uniform(0, 100) > vampiro.calcola_hit_chance(vittima, forza_disarmato=True):
        vampiro.location.msg_contents(pericolo(f"{vampiro.key} tenta di morsicare {vittima.key}, ma manca."))
        return True, None
    forza = vampiro.valore_attributo("str") if hasattr(vampiro, "valore_attributo") else 10
    danno = random.randint(2, 6) + forza // 5 + vampiro.skill_rating("enhanced_damage") // 25
    vampiro.location.msg_contents(pericolo(f"{vampiro.key} morde {vittima.key} per {danno} danni!"))
    morto = vittima.subisci_danno(danno)
    if morto:
        from world.combat import gestisci_morte
        gestisci_morte(vittima, vampiro)
    return True, None


def lineage_di(personaggio):
    """Una riga di LINEAGE per un personaggio."""
    from world.races import nome_razza

    razza = nome_razza(personaggio.db.race) if personaggio.db.race else "?"
    riga = f"{personaggio.key} - {razza}"
    tipo = personaggio.db.sottorazza
    if tipo:
        info = TERMINOLOGIA[tipo]
        riga += f", {NOMI_SOTTORAZZA[tipo]} generazione {personaggio.db.generazione}"
        if personaggio.db.casa_sottorazza:
            riga += f" ({info['gruppo']}: {personaggio.db.casa_sottorazza})"
        if personaggio.db.genitore_sottorazza:
            riga += f" - {info['discendente']} di {personaggio.db.genitore_sottorazza}"
    return riga
