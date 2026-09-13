"""
Comandi staff specifici di CthulhuMUD (Fase K, ventesima tornata): vedi
world/staff.py per le note sulla fonte e sulla scelta di mappare i 6
livelli nominali della fonte (Hero/Creator/Lesser God/God/Greater God/
Implementor) sui 3 permessi Evennia piu' vicini per potere (Builder/
Admin/Developer).
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.staff import restaura, ferma_tutti_i_combattimenti, avanza_personaggio


class CmdHolylight(MuxCommand):
    """
    alterna HOLYLIGHT (vedi al buio e attraverso l'invisibilita')

    Uso:
      holylight

    Comodita' da staff (Creators, immhelp_commands.txt): mentre attivo,
    nessuna oscurita' (world/illuminazione.py) ne' invisibilita' ti
    nasconde piu' nulla.
    """
    key = "holylight"
    locks = "cmd:perm(Builder)"
    help_category = "Staff"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.holylight = not caller.db.holylight
        stato = "attivo" if caller.db.holylight else "disattivo"
        caller.msg(f"HOLYLIGHT ora e' {stato}.")


class CmdRestore(MuxCommand):
    """
    ripristina HP/mana/movimento (e cura veleno/peste/cecita')

    Uso:
      restore
      restore room
      restore <personaggio>
      restore all

    Senza argomenti (o con ROOM) restaura tutti i presenti nella
    stanza; con un bersaglio, solo lui/lei; ALL restaura chiunque sia
    connesso in questo momento (helps/restore.txt: nella fonte
    riservato ai soli Immortali di 300o livello - qui e' comunque
    riservato al permesso piu' alto, Developer, per la stessa cautela).
    """
    key = "restore"
    locks = "cmd:perm(Admin)"
    help_category = "Staff"

    def func(self):
        caller = self.caller
        arg = self.args.strip()

        if arg.lower() == "all":
            if not caller.permissions.check("Developer"):
                caller.msg("RESTORE ALL richiede il permesso Developer.")
                return
            from evennia.objects.models import ObjectDB
            ripristinati = []
            for personaggio in ObjectDB.objects.filter(db_typeclass_path="typeclasses.characters.Character"):
                if personaggio.has_account and personaggio.sessions.count():
                    restaura(personaggio)
                    ripristinati.append(personaggio.key)
            caller.msg(f"Ripristinati {len(ripristinati)} personaggi connessi: {', '.join(ripristinati)}.")
            return

        if not arg or arg.lower() == "room":
            if not caller.location:
                caller.msg("Non sei da nessuna parte.")
                return
            ripristinati = []
            for presente in caller.location.contents:
                if getattr(presente, "db", None) and presente.db.hp_max:
                    restaura(presente)
                    ripristinati.append(presente.key)
            caller.msg(f"Ripristinati nella stanza: {', '.join(ripristinati) or 'nessuno'}.")
            return

        bersaglio = caller.search(arg)
        if not bersaglio:
            return
        if not getattr(bersaglio, "db", None) or not bersaglio.db.hp_max:
            caller.msg(f"{bersaglio.key} non ha punti ferita da ripristinare.")
            return
        restaura(bersaglio)
        caller.msg(f"{bersaglio.key} ripristinato/a completamente.")
        bersaglio.msg(f"{caller.key} ti restituisce tutte le forze.")


class CmdAdvance(MuxCommand):
    """
    alza o abbassa il livello di un personaggio

    Uso:
      advance <personaggio> <livello>

    Assegna anche i train/practice/HP/mana/movimento/skill guadagnati
    normalmente salendo di livello (helps/advance.txt) - vedi
    world/staff.py:avanza_personaggio() per le scelte di design su come
    funziona scendendo di livello.
    """
    key = "advance"
    locks = "cmd:perm(Developer)"
    help_category = "Staff"

    def func(self):
        caller = self.caller
        parti = self.args.split() if self.args else []
        if len(parti) != 2:
            caller.msg("Uso: advance <personaggio> <livello>")
            return
        nome, livello_testo = parti
        try:
            nuovo_livello = int(livello_testo)
        except ValueError:
            caller.msg("Il livello deve essere un numero.")
            return
        if nuovo_livello < 0:
            caller.msg("Il livello non puo' essere negativo.")
            return

        bersaglio = caller.search(nome, global_search=True)
        if not bersaglio:
            return
        ok, messaggio = avanza_personaggio(bersaglio, nuovo_livello)
        caller.msg(messaggio)
        if ok:
            bersaglio.msg(f"{caller.key} altera la tua esperienza: ora sei al livello {nuovo_livello}.")


class CmdSlay(MuxCommand):
    """
    uccidi un personaggio all'istante

    Uso:
      slay <personaggio>

    Nessun tiro, nessuna classe armatura, nessuna magia difensiva puo'
    salvare il bersaglio (helps/slay.txt). Usalo con cautela.
    """
    key = "slay"
    locks = "cmd:perm(Admin)"
    help_category = "Staff"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: slay <personaggio>")
            return
        bersaglio = caller.search(self.args.strip(), global_search=True)
        if not bersaglio:
            return
        if bersaglio is caller:
            caller.msg("Non puoi usare SLAY su te stesso/a.")
            return
        from world.combat import gestisci_morte
        caller.msg(f"Colpisci a morte {bersaglio.key} con la sola forza di volonta'.")
        if bersaglio.location:
            bersaglio.location.msg_contents(
                f"{bersaglio.key} crolla morto/a all'istante, senza una ragione visibile.",
                exclude=[bersaglio],
            )
        gestisci_morte(bersaglio, caller)


class CmdFreeze(MuxCommand):
    """
    alterna il blocco comandi di un personaggio

    Uso:
      freeze <personaggio>

    Il personaggio congelato non puo' piu' inserire comandi (ma
    continua a vedere quello che succede intorno a lui/lei) finche' non
    lo/la scongeli richiamando di nuovo il comando (helps/freeze.txt).
    """
    key = "freeze"
    locks = "cmd:perm(Admin)"
    help_category = "Staff"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: freeze <personaggio>")
            return
        bersaglio = caller.search(self.args.strip(), global_search=True)
        if not bersaglio:
            return
        bersaglio.db.frozen = not bersaglio.db.frozen
        if bersaglio.db.frozen:
            caller.msg(f"{bersaglio.key} e' ora congelato/a: non puo' piu' inserire comandi.")
            bersaglio.msg("|rSei stato/a congelato/a da uno Immortale: non puoi piu' agire.|n")
        else:
            caller.msg(f"{bersaglio.key} e' stato/a scongelato/a.")
            bersaglio.msg("|gPuoi di nuovo agire.|n")


class CmdPeace(MuxCommand):
    """
    ferma tutti i combattimenti nella stanza

    Uso:
      peace
    """
    key = "peace"
    locks = "cmd:perm(Builder)"
    help_category = "Staff"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        if not caller.location:
            caller.msg("Non sei da nessuna parte.")
            return
        fermati = ferma_tutti_i_combattimenti(caller.location)
        if fermati:
            nomi = ", ".join(o.key for o in fermati)
            caller.location.msg_contents(f"Una pace improvvisa scende sulla stanza: {nomi} smettono di combattere.", exclude=[])
        else:
            caller.msg("Nessun combattimento in corso qui.")


class CmdWizinvis(MuxCommand):
    """
    alterna WIZINVIS (invisibile a tutti i mortali, ovunque)

    Uso:
      wizinvis
    """
    key = "wizinvis"
    locks = "cmd:perm(Builder)"
    help_category = "Staff"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.wizinvis = not caller.db.wizinvis
        if caller.db.wizinvis:
            caller.db.cloak = False
        stato = "attivo" if caller.db.wizinvis else "disattivo"
        caller.msg(f"WIZINVIS ora e' {stato}.")


class CmdCloak(MuxCommand):
    """
    alterna CLOAK (invisibile a chi non e' nella tua stessa stanza)

    Uso:
      cloak
    """
    key = "cloak"
    locks = "cmd:perm(Builder)"
    help_category = "Staff"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.cloak = not caller.db.cloak
        if caller.db.cloak:
            caller.db.wizinvis = False
        stato = "attivo" if caller.db.cloak else "disattivo"
        caller.msg(f"CLOAK ora e' {stato}.")


class CmdWizlock(MuxCommand):
    """
    alterna il blocco degli accessi ai soli mortali

    Uso:
      wizlock

    Impedisce a chiunque non abbia almeno il permesso Builder di
    connettersi (helps/wizlock.txt) - da usare in caso di bug gravi,
    mentre si sistema il problema.
    """
    key = "wizlock"
    locks = "cmd:perm(Admin)"
    help_category = "Staff"
    arg_regex = r"$"

    def func(self):
        from evennia.server.models import ServerConfig
        attivo = not ServerConfig.objects.conf("wizlock", default=False)
        ServerConfig.objects.conf("wizlock", attivo)
        stato = "attivo" if attivo else "disattivo"
        self.caller.msg(f"WIZLOCK ora e' {stato}.")


class CmdNewlock(MuxCommand):
    """
    alterna il blocco della creazione di nuovi personaggi

    Uso:
      newlock
    """
    key = "newlock"
    locks = "cmd:perm(Admin)"
    help_category = "Staff"
    arg_regex = r"$"

    def func(self):
        from evennia.server.models import ServerConfig
        attivo = not ServerConfig.objects.conf("newlock", default=False)
        ServerConfig.objects.conf("newlock", attivo)
        stato = "attivo" if attivo else "disattivo"
        self.caller.msg(f"NEWLOCK ora e' {stato}.")


class CmdSwitch(MuxCommand):
    """
    prendi temporaneamente il controllo di un NPC

    Uso:
      switch <npc>

    Usa RETURN per tornare al tuo personaggio. Come da fonte
    (helps/switch.txt), non si puo' usare SWITCH per entrare nel
    personaggio di un altro giocatore. Utile per gestire quest
    ed eventi in prima persona. Stesso schema gia' usato per
    MINDTRANSFER (commands/cthulhu_yithian.py): lock "puppet" scoped
    al solo account chiamante invece di aprirlo a chiunque, cosi' da
    non lasciare l'NPC puppettabile da altri per errore.
    """
    key = "switch"
    locks = "cmd:perm(Admin)"
    help_category = "Staff"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: switch <npc>")
            return
        bersaglio = caller.search(self.args.strip(), global_search=True)
        if not bersaglio:
            return
        if bersaglio.is_typeclass("typeclasses.characters.Character", exact=False):
            caller.msg("Non puoi usare SWITCH su un personaggio giocante.")
            return
        if not hasattr(bersaglio, "db"):
            caller.msg(f"{bersaglio.key} non e' un NPC valido.")
            return

        sessioni = caller.sessions.get()
        if not sessioni:
            caller.msg("Errore interno: nessuna sessione attiva.")
            return
        account = caller.account

        bersaglio.db.switchato_da = caller
        bersaglio.locks.add(f"puppet:id({account.id}) or perm(Developer)")
        caller.msg(f"Prendi il controllo di {bersaglio.key}. Usa RETURN per tornare al tuo corpo.")
        account.puppet_object(sessioni[0], bersaglio)


class CmdIncarnate(MuxCommand):
    """
    alterna lo stato di incarnazione (RP)

    Uso:
      incarnate

    In questo porting lo staff non ha mai avuto un'invulnerabilita'
    automatica da rimuovere (nessun controllo di questo tipo esiste nel
    combattimento): INCARNATE qui disattiva WIZINVIS/CLOAK e segnala lo
    stato, a fini di roleplay, invece di scavalcare una protezione che
    non esiste - semplificazione dichiarata rispetto a helps/incarnate.txt.
    """
    key = "incarnate"
    locks = "cmd:perm(Admin)"
    help_category = "Staff"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.incarnato = not caller.db.incarnato
        if caller.db.incarnato:
            caller.db.wizinvis = False
            caller.db.cloak = False
            caller.msg("Ti spogli della tua natura immortale: sei ora incarnato/a.")
            if caller.location:
                caller.location.msg_contents(f"{caller.key} appare all'improvviso, ora del tutto mortale.", exclude=[caller])
        else:
            caller.msg("Riprendi la tua natura immortale.")


class CmdGoto(MuxCommand):
    """
    teletrasportati istantaneamente

    Uso:
      goto <stanza o personaggio>

    Usa i messaggi personalizzati impostati con BAMFIN/BAMFOUT, se
    presenti (helps/goto.txt).
    """
    key = "goto"
    locks = "cmd:perm(Builder)"
    help_category = "Staff"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: goto <stanza o personaggio>")
            return
        destinazione = caller.search(self.args.strip(), global_search=True)
        if not destinazione:
            return
        posizione = destinazione if destinazione.location is None else destinazione.location
        if posizione is caller.location:
            caller.msg("Sei gia' li'.")
            return

        messaggio_uscita = caller.db.bamfout or f"{caller.key} scompare in una nuvola di fumo."
        messaggio_arrivo = caller.db.bamfin or f"{caller.key} appare in una nuvola di fumo."

        origine = caller.location
        caller.move_to(posizione, quiet=True)
        if origine:
            origine.msg_contents(messaggio_uscita, exclude=[caller])
        if posizione:
            posizione.msg_contents(messaggio_arrivo, exclude=[caller])
        caller.msg(f"Ti teletrasporti a {posizione.key if posizione else 'nessun luogo'}.")
        caller.execute_cmd("look")


class CmdBamfin(MuxCommand):
    """
    imposta il tuo messaggio d'arrivo personalizzato per GOTO

    Uso:
      bamfin <testo>
      bamfin

    Senza argomenti, ripristina il messaggio di default.
    """
    key = "bamfin"
    locks = "cmd:perm(Builder)"
    help_category = "Staff"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.db.bamfin = None
            caller.msg("Messaggio d'arrivo ripristinato al default.")
            return
        caller.db.bamfin = self.args.strip()
        caller.msg(f"Messaggio d'arrivo impostato: {caller.db.bamfin}")


class CmdBamfout(MuxCommand):
    """
    imposta il tuo messaggio di partenza personalizzato per GOTO

    Uso:
      bamfout <testo>
      bamfout

    Senza argomenti, ripristina il messaggio di default.
    """
    key = "bamfout"
    locks = "cmd:perm(Builder)"
    help_category = "Staff"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.db.bamfout = None
            caller.msg("Messaggio di partenza ripristinato al default.")
            return
        caller.db.bamfout = self.args.strip()
        caller.msg(f"Messaggio di partenza impostato: {caller.db.bamfout}")


class CmdPermapk(MuxCommand):
    """
    alterna la modalita' permadeath in tutto il gioco

    Uso:
      permapk

    ATTENZIONE (helps/permapk.txt, comando riservato ad autorita' di
    livello Implementor): con questa modalita' attiva, la morte di un
    GIOCATORE cancella per sempre il personaggio dal database. Da
    maneggiare con estrema cautela.
    """
    key = "permapk"
    locks = "cmd:perm(Developer)"
    help_category = "Staff"
    arg_regex = r"$"

    def func(self):
        from evennia.server.models import ServerConfig
        attivo = not ServerConfig.objects.conf("permapk", default=False)
        ServerConfig.objects.conf("permapk", attivo)
        stato = "|rATTIVA|n" if attivo else "disattivata"
        self.caller.msg(f"Modalita' PERMAPK ora {stato} in tutto il gioco.")
