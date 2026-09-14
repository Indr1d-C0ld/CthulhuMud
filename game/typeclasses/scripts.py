"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from evennia.scripts.scripts import DefaultScript


class Script(DefaultScript):
    """
    This is the base TypeClass for all Scripts. Scripts describe
    all entities/systems without a physical existence in the game world
    that require database storage (like an economic system or
    combat tracker). They
    can also have a timer/ticker component.

    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties (check docs for full listing, this could be
      outdated).

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     create(key, **kwargs)
     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - ATTENZIONE: contrariamente a quanto diceva questo docstring
               (ereditato da una vecchia versione di Evennia e corretto
               nell'audit globale pre-beta), stop() NON cancella lo script:
               si limita a mettere is_active=False lasciando la riga nel
               database. Per rimuoverlo davvero serve delete(). La versione
               sbagliata di questa riga ha gia' causato due bug reali in
               questo progetto: accumulo illimitato di righe e resurrezione
               di effetti annullati. Vedi la nota estesa in world/effetti.py.
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_pause()
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_script_delete()
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.
      at_server_start()

    """

    pass


class CombatRoundScript(Script):
    """
    Un round di combattimento per il personaggio/NPC a cui e' agganciato
    (self.obj). Vedi world/combat.py per la logica vera e propria: qui c'e'
    solo il timer. Ogni combattente engaged ha la propria istanza: se A e B
    si combattono a vicenda, girano due script separati, uno per lato.
    """

    def at_script_creation(self):
        self.key = "combat_round"
        self.interval = 3
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        from world.combat import risolvi_round
        risolvi_round(self.obj)


class BlessExpireScript(Script):
    """Fa scadere il bonus temporaneo di Benedizione dopo 60 secondi."""

    def at_script_creation(self):
        self.key = "bless_expire"
        self.interval = 60
        self.persistent = True
        self.start_delay = True
        self.repeats = 1

    def at_repeat(self):
        if self.obj and self.obj.pk:
            self.obj.db.bonus_colpire = 0
            self.obj.msg("L'effetto della Benedizione svanisce.")


class InteresseBancarioScript(Script):
    """
    Interesse mensile sui conti in banca (Fase F, decima tornata):
    confermato dal sito originale ("accounts earn a little interest each
    month"), qui applicato a tutti i personaggi con Oro in banca.

    Non essendoci un calendario di gioco, "un mese" e' qui un intervallo
    di tempo reale arbitrario (scelta di design esplicita, facile da
    ritarare) invece che un mese di calendario in-game.
    """

    def at_script_creation(self):
        self.key = "interesse_bancario"
        self.interval = 24 * 60 * 60   # un giorno reale = "un mese" di gioco
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        from world.banca import applica_interesse_a_tutti
        applica_interesse_a_tutti()


class SopravvivenzaScript(Script):
    """
    Tick periodico di fame/sete per tutti i personaggi (Fase G, prima
    tornata): confermato dalla fonte come meccanica reale, non solo un
    consiglio (vedi world/sopravvivenza.py). Nessuna cadenza esatta e'
    specificata dalla fonte: qui un tick ogni 10 minuti reali e' una
    scelta di design esplicita, facile da ritarare.
    """

    def at_script_creation(self):
        self.key = "sopravvivenza"
        self.interval = 10 * 60
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        from world.sopravvivenza import applica_tick_sopravvivenza
        from world.combat import gestisci_morte
        from evennia.objects.models import ObjectDB

        personaggi = ObjectDB.objects.filter(
            db_typeclass_path="typeclasses.characters.Character"
        )
        for personaggio in personaggi:
            if not personaggio.location or (personaggio.db.hp or 0) <= 0:
                continue
            morto = applica_tick_sopravvivenza(personaggio)
            if morto:
                gestisci_morte(personaggio, None)


class RigenerazioneScript(Script):
    """
    Tick periodico di rigenerazione HP/Mana/Movimento (Fase K,
    quattordicesima tornata; cadenza corretta in ventiduesima tornata):
    confermato dalla fonte come meccanica reale legata a REST/SLEEP
    (vedi world/posizione.py, helps/rest.txt - "REST and SLEEP result
    in increased regeneration rates"). La cadenza esatta e' confermata
    da helps/tick.txt: "The tick on CthulhuMUD averages 30 seconds of
    real time, but the actual interval varies randomly within a range
    from 15 seconds to 45 seconds" - fino alla ventiduesima tornata
    questo script usava un intervallo fisso di 5 minuti (mai
    controllata quella pagina): 10 volte piu' lento del vero ritmo
    della fonte. Ora ogni tick si ri-arma con un nuovo intervallo
    casuale in quel range, invece di uno fisso.
    """

    def at_script_creation(self):
        self.key = "rigenerazione"
        self.interval = 30
        self.persistent = True
        self.start_delay = True

    def _riarma_con_intervallo_casuale(self):
        """Ri-arma il timer con un nuovo intervallo nel range della fonte.

        DEVE essere chiamata fuori da at_repeat (vedi la nota li' sotto)."""
        import random

        if self.pk:
            self.start(interval=random.randint(15, 45), force_restart=True)

    def at_repeat(self):
        from evennia.utils import delay
        from world.posizione import applica_tick_rigenerazione
        from evennia.objects.models import ObjectDB

        # BUG REALE trovato nell'audit globale pre-beta: qui c'era una
        # chiamata diretta a self.start(..., force_restart=True). Ri-armare
        # il timer dall'INTERNO del proprio callback ferma e ricrea il task
        # mentre il task stesso e' in esecuzione (vedi
        # evennia/scripts/scripts.py:_start_task -> _stop_task, e l'assert
        # "Tried to start an already running ExtendedLoopingCall"): il
        # risultato e' uno script che resta is_active=True ma senza alcun
        # timer armato, cioe' morto. In produzione la rigenerazione di
        # HP/mana/movimento era completamente ferma, e il difetto era
        # invisibile perche' `is_active` continuava a dire True.
        # delay(0, ...) rinvia il ri-armo al giro successivo del reattore,
        # cioe' a callback concluso, conservando la variabilita' casuale
        # dell'intervallo confermata dalla fonte (helps/tick.txt).
        delay(0, self._riarma_con_intervallo_casuale)

        personaggi = ObjectDB.objects.filter(
            db_typeclass_path="typeclasses.characters.Character"
        )
        for personaggio in personaggi:
            if not personaggio.location or (personaggio.db.hp or 0) <= 0:
                continue
            applica_tick_rigenerazione(personaggio)


class SottorazzaBuffExpireScript(Script):
    """
    Fa scadere un potenziamento temporaneo delle sottorazze (Lich
    EMPOWER/ENHANCE/STRIKE-block, Vampire ENHANCE/MAJESTY/MISTFORM, Were
    RAGE/FURY/REGEN - vedi world/sottorazze.py, commands/cthulhu_lich.py,
    cthulhu_vampire.py, cthulhu_were.py). Generico: memorizza in
    self.db.campo/valore_precedente cosa ripristinare.
    """

    def at_script_creation(self):
        self.key = "sottorazza_buff_expire"
        self.persistent = True
        self.start_delay = True
        self.repeats = 1

    def at_repeat(self):
        obj = self.obj
        if not obj or not obj.pk:
            return
        campo = self.db.campo
        if campo:
            setattr(obj.db, campo, self.db.valore_precedente)
        if self.db.messaggio_scadenza:
            obj.msg(self.db.messaggio_scadenza)


class CorpseDecayScript(Script):
    """Fa sparire un cadavere dopo db.decadimento_minuti minuti (default 15,
    confermato dalla fonte: "~30 game-hours, 15 minuti reali" - vedi
    world.combat.DURATA_DECADIMENTO_MINUTI). Il contenuto del cadavere NON
    sparisce con lui: cade nella stanza, dove chiunque puo' raccoglierlo (di
    nuovo come da fonte: solo dopo il decadimento gli oggetti diventano
    liberi per tutti)."""

    def at_script_creation(self):
        self.key = "decadimento"
        minuti = (self.obj.db.decadimento_minuti or 15) if self.obj else 15
        self.interval = minuti * 60
        self.persistent = True
        self.start_delay = True
        self.repeats = 1

    def at_repeat(self):
        # self.obj potrebbe essere gia' stato rimosso da un altro percorso
        # (es. saccheggio del cadavere, o la cancellazione dell'NPC che lo
        # ha generato). Audit globale pre-beta: il controllo difensivo
        # `if not obj or not obj.pk` NON bastava, perche' in Evennia e' il
        # semplice ACCESSO a self.obj a sollevare l'eccezione quando
        # l'oggetto e' stato cancellato ("This object was already
        # deleted!"). Nei log di produzione questo script e' infatti la
        # prima causa di errori, con tre sintomi diversi
        # (already deleted / campo id mancante / FOREIGN KEY constraint).
        # Qui si intercetta qualunque problema e ci si limita a rimuovere
        # lo script, che a quel punto non ha piu' nulla da fare.
        try:
            obj = self.obj
            if not obj or not obj.pk:
                self.delete()
                return
            stanza = obj.location
            if stanza:
                for contenuto in list(obj.contents):
                    contenuto.move_to(stanza, quiet=True, move_type="drop")
                stanza.msg_contents(f"{obj.key} si dissolve in polvere.")
            obj.delete()
        except Exception:
            from evennia.utils import logger
            logger.log_trace("CorpseDecayScript: cadavere gia' rimosso, script eliminato.")
            try:
                self.delete()
            except Exception:
                pass


class RepopScript(Script):
    """
    Repop/reset periodico dei mostri ostili uccisi (Fase H, seconda
    tornata): vedi world/repop.py per la logica completa e la
    giustificazione dalla fonte (immhelp_resets.txt - un'area si
    ripopola piu' in fretta se vuota di giocatori, piu' lentamente se
    occupata). Controlla ogni minuto reale quali zone hanno superato
    il proprio intervallo e le ripopola.
    """

    def at_script_creation(self):
        self.key = "repop_mostri"
        self.interval = 60
        self.persistent = True
        self.start_delay = True
        self.db.ultimo_reset = {}

    def at_repeat(self):
        from world.repop import controlla_e_ripopola_tutte_le_zone
        controlla_e_ripopola_tutte_le_zone(self.db.ultimo_reset)


class MostriMovimentoScript(Script):
    """
    Tick periodico di vagabondaggio/battute ambientali per i mostri
    ostili (Fase H, terza tornata): vedi world/mostri_movimento.py per
    la logica completa e la giustificazione dalla fonte
    (SENTINEL/STAY-AREA in immhelp_flags.txt, condizione
    random+evento pulse in immhelp_conditions.txt).
    """

    def at_script_creation(self):
        self.key = "mostri_movimento"
        self.interval = 30
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        from world.mostri_movimento import tick_movimento_mostri
        tick_movimento_mostri()


class StatoScadenzaScript(Script):
    """
    Fase K, sesta tornata: fa scadere uno stato temporaneo (booleano) in
    self.db.stati - il generico usato dagli incantesimi (Accecamento,
    Ammutolire, Sonno, Paura, Invisibilita', Rilevare l'Invisibile, ecc.,
    vedi world/effetti.py). Analogo a SottorazzaBuffExpireScript ma per
    voci del dizionario db.stati invece di un singolo campo numerico.
    """

    def at_script_creation(self):
        self.key = "stato_scadenza"
        self.persistent = True
        self.start_delay = True
        self.repeats = 1

    def at_repeat(self):
        obj = self.obj
        if not obj or not obj.pk:
            return
        stato = self.db.stato
        if stato and obj.db.stati:
            stati = obj.db.stati
            stati.pop(stato, None)
            obj.db.stati = stati
        campo_bool = self.db.campo_bool
        if campo_bool:
            # variante per flag booleani fuori da db.stati (es. db.invisibile
            # per Invisibilita'/Invisibilita' di Massa - Fase K, sesta tornata)
            setattr(obj.db, campo_bool, False)
        if self.db.messaggio_scadenza:
            obj.msg(self.db.messaggio_scadenza)


class EffettoPeriodicoScript(Script):
    """
    Fase K, sesta tornata: infligge danno a intervalli regolari per un
    numero fisso di colpi (Veleno, Peste/Malattia) - vedi
    world/effetti.py:applica_danno_periodico(). Si autodistrugge da solo
    dopo l'ultimo colpo (self.repeats configurato alla creazione).
    """

    def at_script_creation(self):
        self.key = "effetto_periodico"
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        obj = self.obj
        if not obj or not obj.pk or not getattr(obj, "vivo", True):
            self.stop()
            return
        import random
        quantita = self.db.danno_min
        if self.db.danno_max and self.db.danno_max > self.db.danno_min:
            quantita = random.randint(self.db.danno_min, self.db.danno_max)

        if self.db.cura:
            # Fase K, sesta tornata: modalita' cura (es. Rigenerazione) -
            # stesso script, segno opposto, nessuna gestione morte.
            prima = obj.db.hp or 0
            obj.db.hp = min(obj.db.hp_max, prima + quantita)
            quantita = obj.db.hp - prima
            if self.db.messaggio_tick and quantita:
                obj.msg(self.db.messaggio_tick.format(danno=quantita))
            morto = False
        else:
            if self.db.messaggio_tick:
                obj.msg(self.db.messaggio_tick.format(danno=quantita))
            morto = obj.subisci_danno(quantita, fisico=False)

        self.db.tick_fatti = (self.db.tick_fatti or 0) + 1
        if morto:
            from world.combat import gestisci_morte
            gestisci_morte(obj, None)
            return
        if self.db.tick_fatti >= (self.db.tick_totali or 1):
            # ultimo colpo: rimuovi anche lo stato associato (es. "avvelenato")
            if self.db.stato and obj.db.stati:
                stati = obj.db.stati
                stati.pop(self.db.stato, None)
                obj.db.stati = stati
            if self.db.messaggio_fine:
                obj.msg(self.db.messaggio_fine)
            self.stop()


class CristalliFocusScript(Script):
    """
    Tick periodico globale di assorbimento passivo per i Cristalli Focus
    Yithiani (Fase K, settima tornata): vedi world/focus_crystal.py.
    """

    def at_script_creation(self):
        self.key = "cristalli_focus"
        self.interval = 60
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        from world.focus_crystal import tick_assorbimento_cristalli
        tick_assorbimento_cristalli()
