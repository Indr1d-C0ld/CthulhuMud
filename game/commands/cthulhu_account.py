"""
Localizzazione dei comandi Account (OOC) di account.py - Fase C, terza
tornata: sono i comandi con cui ogni giocatore interagisce piu' spesso
fuori dal gioco vero e proprio (creazione/cancellazione personaggi,
entrare/uscire dal personaggio, opzioni client, password, stili).

Questi comandi vivono sull'Account, quindi self.caller e' sempre un
Account, non un Object/Character (a differenza della maggior parte dei
comandi altrove tradotti). Usano self.account per essere sicuri di
lavorare sempre sull'account anche quando invocati mentre si controlla
un personaggio.

`MuxAccountLookCommand` e' riusata cosi' com'e' da Evennia: e' solo
parsing (imposta la proprieta' `playable`), nessuna stringa rivolta al
giocatore.
"""

from codecs import lookup as codecs_lookup

from django.conf import settings

from evennia.commands.default.account import MuxAccountLookCommand
from evennia.commands.default.muxcommand import MuxCommand
from evennia.contrib.rpg.character_creator.character_creator import ContribCmdCharCreate
from evennia.utils import logger, search, utils

_MAX_NR_CHARACTERS = settings.MAX_NR_CHARACTERS
_AUTO_PUPPET_ON_LOGIN = settings.AUTO_PUPPET_ON_LOGIN


class CmdOOCLook(MuxAccountLookCommand):
    """
    guarda mentre sei fuori dal personaggio (OOC)

    Uso:
      look

    Guarda nello stato OOC.
    """

    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    help_category = "Generale"

    account_caller = True

    def func(self):
        """implementa il comando look OOC"""

        if self.session.puppet:
            self.msg("Al momento non hai la possibilita' di guardarti attorno.")
            return

        if _AUTO_PUPPET_ON_LOGIN and _MAX_NR_CHARACTERS == 1 and self.playable:
            self.msg("Sei fuori dal personaggio (OOC).\nUsa |wic|n per rientrare nel gioco.")
            return

        self.msg(self.account.at_look(target=self.playable, session=self.session))


class CmdCharCreate(ContribCmdCharCreate):
    """
    crea un nuovo personaggio (o riprendi quello in corso)

    Uso:
      charcreate

    Ti guida passo per passo nella creazione di un nuovo personaggio
    (razza, professione, nome - vedi world/chargen_menu.py). Se avevi
    gia' iniziato e non hai finito, riprende da dove eri rimasto/a.
    """

    # Fase K, ventesima tornata: sottoclasse invece di riusare
    # ContribCmdCharCreate direttamente solo per aggiungere il
    # controllo NEWLOCK (helps/wizlock.txt) - stesso schema di
    # "aggiungi un controllo, poi richiama super()" gia' visto altrove
    # in questo porting, invece di reimplementare la creazione (l'aver
    # duplicato/rimpiazzato questa logica in una tornata precedente
    # aveva reso l'intero chargen_menu.py IRRAGGIUNGIBILE - vedi la
    # nota nella stessa tornata che ha corretto il problema).
    def func(self):
        from evennia.server.models import ServerConfig
        in_progress = any(char.db.chargen_step for char in self.account.characters)
        if (
            not in_progress
            and ServerConfig.objects.conf("newlock", default=False)
            and not self.account.check_permstring("Builder")
        ):
            # NEWLOCK blocca solo la creazione di personaggi DAVVERO
            # nuovi (helps/wizlock.txt) - riprendere un chargen gia'
            # iniziato non e' "creare un nuovo personaggio".
            self.msg("La creazione di nuovi personaggi e' temporaneamente bloccata (NEWLOCK).")
            return
        super().func()


class CmdCharDelete(MuxCommand):
    """
    elimina un personaggio - non si puo' annullare!

    Uso:
        chardelete <nomepersonaggio>

    Elimina permanentemente uno dei tuoi personaggi.
    """

    key = "chardelete"
    locks = "cmd:pperm(Player)"
    help_category = "Generale"

    def func(self):
        """elimina il personaggio"""
        account = self.account

        if not self.args:
            self.msg("Uso: chardelete <nomepersonaggio>")
            return

        match = [
            char
            for char in utils.make_iter(account.characters)
            if char.key.lower() == self.args.lower()
        ]
        if not match:
            self.msg("Non hai nessun personaggio con questo nome da eliminare.")
            return
        elif len(match) > 1:
            self.msg(
                "Annullato - ci sono due personaggi con lo stesso nome. Chiedi a un admin di "
                "eliminare quello giusto."
            )
            return
        else:
            from evennia.utils.evmenu import get_input

            def _callback(caller, callback_prompt, result):
                if result.lower() in ("si", "s", "yes", "y"):
                    delobj = caller.ndb._char_to_delete
                    key = delobj.key
                    caller.characters.remove(delobj)
                    delobj.delete()
                    self.msg(f"Il personaggio '{key}' e' stato eliminato permanentemente.")
                    logger.log_sec(
                        f"Character Deleted: {key} (Caller: {account}, IP: {self.session.address})."
                    )
                else:
                    self.msg("Eliminazione annullata.")
                del caller.ndb._char_to_delete

            match = match[0]
            account.ndb._char_to_delete = match

            if not match.access(account, "delete"):
                self.msg("Non hai il permesso di eliminare questo personaggio.")
                return

            prompt = (
                "|rQuesto distruggera' permanentemente '%s'. Non si puo' annullare.|n"
                " Continuare si/[no]?"
            )
            get_input(account, prompt % match.key, _callback)


class CmdIC(MuxCommand):
    """
    controlla un oggetto che hai il permesso di possedere (puppet)

    Uso:
      ic <personaggio>

    Entra in gioco (IC) come il personaggio indicato.

    Questo tentera' di farti "diventare" un oggetto diverso, ammesso che
    tu ne abbia il diritto. Nota che e' l'ACCOUNT a possedere i
    personaggi/oggetti, ed e' lui ad aver bisogno del permesso corretto!

    Non puoi diventare un oggetto gia' controllato da un altro account.
    In linea di principio <personaggio> puo' essere qualsiasi oggetto di
    gioco, purche' tu come account abbia il diritto di possederlo.
    """

    key = "ic"
    locks = "cmd:all()"
    aliases = "puppet"
    help_category = "Generale"

    account_caller = True

    def func(self):
        """Metodo principale di possesso (puppet)."""
        account = self.account
        session = self.session

        new_character = None
        character_candidates = []

        if not self.args:
            character_candidates = [account.db._last_puppet] if account.db._last_puppet else []
            if not character_candidates:
                self.msg("Uso: ic <personaggio>")
                return
        else:
            if playables := account.characters:
                character_candidates.extend(
                    utils.make_iter(
                        account.search(
                            self.args,
                            candidates=playables,
                            search_object=True,
                            quiet=True,
                        )
                    )
                )

            if account.locks.check_lockstring(account, "perm(Builder)"):
                if session.puppet:
                    character_candidates = [
                        char
                        for char in session.puppet.search(self.args, quiet=True)
                        if char.access(account, "puppet")
                    ]
                if not character_candidates:
                    character_candidates.extend(
                        [
                            char
                            for char in search.object_search(self.args)
                            if char.access(account, "puppet")
                        ]
                    )

        if not character_candidates:
            self.msg("Non e' una scelta di personaggio valida.")
            return
        if len(character_candidates) > 1:
            self.msg(
                "Piu' bersagli con lo stesso nome:\n %s"
                % ", ".join("%s(#%s)" % (obj.key, obj.id) for obj in character_candidates)
            )
            return
        else:
            new_character = character_candidates[0]

        try:
            account.puppet_object(session, new_character)
            account.db._last_puppet = new_character
            logger.log_sec(
                f"Puppet Success: (Caller: {account}, Target: {new_character}, IP:"
                f" {self.session.address})."
            )
        except RuntimeError as exc:
            self.msg(f"|rNon puoi diventare |C{new_character.name}|n: {exc}")
            logger.log_sec(
                f"Puppet Failed: %s (Caller: {account}, Target: {new_character}, IP:"
                f" {self.session.address})."
            )


class CmdOOC(MuxAccountLookCommand):
    """
    smetti di possedere il personaggio e torna OOC

    Uso:
      ooc

    Esci dal personaggio, andando fuori dal personaggio (OOC).

    Questo ti fara' lasciare il tuo personaggio attuale, mettendoti in
    uno stato OOC incorporeo.
    """

    key = "ooc"
    locks = "cmd:pperm(Player)"
    aliases = "unpuppet"
    help_category = "Generale"

    account_caller = True

    def func(self):
        """Implementa la funzione."""

        account = self.account
        session = self.session

        old_char = account.get_puppet(session)
        if not old_char:
            string = "Sei gia' fuori dal personaggio (OOC)."
            self.msg(string)
            return

        account.db._last_puppet = old_char

        try:
            account.unpuppet_object(session)
            self.msg("\n|GSei uscito dal personaggio (OOC).|n\n")

            if _AUTO_PUPPET_ON_LOGIN and _MAX_NR_CHARACTERS == 1 and self.playable:
                self.msg("Sei fuori dal personaggio (OOC).\nUsa |wic|n per rientrare nel gioco.")
                return

            self.msg(account.at_look(target=self.playable, session=session))

        except RuntimeError as exc:
            self.msg(f"|rImpossibile uscire da |c{old_char}|n: {exc}")


class CmdSessions(MuxCommand):
    """
    controlla le tue sessioni connesse

    Uso:
      sessions

    Elenca le sessioni attualmente connesse al tuo account.
    """

    key = "sessions"
    locks = "cmd:all()"
    help_category = "Generale"

    account_caller = True

    def func(self):
        """Implementa la funzione."""
        account = self.account
        sessions = account.sessions.all()
        table = self.styled_table(
            "|wsessid", "|wprotocollo", "|whost", "|wpuppet/personaggio", "|wposizione"
        )
        for sess in sorted(sessions, key=lambda x: x.sessid):
            char = account.get_puppet(sess)
            table.add_row(
                str(sess.sessid),
                str(sess.protocol_key),
                isinstance(sess.address, tuple) and sess.address[0] or sess.address,
                char and str(char) or "Nessuno",
                char and str(char.location) or "N/D",
            )
            self.msg(f"|wLe tue sessioni attuali:|n\n{table}")


class CmdOption(MuxCommand):
    """
    imposta un'opzione dell'account

    Uso:
      option[/save] [nome = valore]

    Switch:
      save - salva le impostazioni attuali per i prossimi login.
      clear - cancella le opzioni salvate.

    Questo comando permette di vedere e impostare le opzioni
    dell'interfaccia client. Nota che le opzioni salvate potrebbero non
    essere utilizzabili se in seguito ti connetti con un client dalle
    capacita' diverse.
    """

    key = "option"
    aliases = "options"
    switch_options = ("save", "clear")
    locks = "cmd:all()"

    account_caller = True

    def func(self):
        """Implementa il comando."""
        if self.session is None:
            return

        flags = self.session.protocol_flags

        if not self.args:
            if "save" in self.switches:
                self.caller.db._saved_protocol_flags = flags
                self.msg("|gTutte le opzioni sono state salvate. Usa option/clear per rimuoverle.|n")
            if "clear" in self.switches:
                self.caller.db._saved_protocol_flags = {}
                self.msg("|gTutte le opzioni salvate sono state cancellate.")

            options = dict(flags)
            saved_options = dict(self.caller.attributes.get("_saved_protocol_flags", default={}))

            if "SCREENWIDTH" in options:
                if len(options["SCREENWIDTH"]) == 1:
                    options["SCREENWIDTH"] = options["SCREENWIDTH"][0]
                else:
                    options["SCREENWIDTH"] = "  \n".join(
                        "%s : %s" % (screenid, size)
                        for screenid, size in options["SCREENWIDTH"].items()
                    )
            if "SCREENHEIGHT" in options:
                if len(options["SCREENHEIGHT"]) == 1:
                    options["SCREENHEIGHT"] = options["SCREENHEIGHT"][0]
                else:
                    options["SCREENHEIGHT"] = "  \n".join(
                        "%s : %s" % (screenid, size)
                        for screenid, size in options["SCREENHEIGHT"].items()
                    )
            options.pop("TTYPE", None)

            header = ("Nome", "Valore", "Salvata") if saved_options else ("Nome", "Valore")
            table = self.styled_table(*header)
            for key in sorted(options):
                row = [key, options[key]]
                if saved_options:
                    saved = " |YSi|n" if key in saved_options else ""
                    changed = (
                        "|y*|n" if key in saved_options and flags[key] != saved_options[key] else ""
                    )
                    row.append("%s%s" % (saved, changed))
                table.add_row(*row)
            self.msg(f"|wImpostazioni client ({self.session.protocol_key}):|n\n{table}|n")

            return

        if not self.rhs:
            self.msg("Uso: option [nome = [valore]]")
            return

        def validate_encoding(new_encoding):
            try:
                codecs_lookup(new_encoding)
            except LookupError:
                raise RuntimeError(f"La codifica '|w{new_encoding}|n' non e' valida. ")
            return val

        def validate_size(new_size):
            return {0: int(new_size)}

        def validate_bool(new_bool):
            return True if new_bool.lower() in ("true", "on", "1") else False

        def update(new_name, new_val, validator):
            try:
                old_val = flags.get(new_name, False)
                new_val = validator(new_val)
                if old_val == new_val:
                    self.msg(f"L'opzione |w{new_name}|n e' rimasta '|w{old_val}|n'.")
                else:
                    flags[new_name] = new_val

                    if new_name in ["SCREENWIDTH", "SCREENHEIGHT"]:
                        flags["AUTORESIZE"] = False

                    self.msg(
                        f"L'opzione |w{new_name}|n e' cambiata da '|w{old_val}|n' a"
                        f" '|w{new_val}|n'."
                    )
                return {new_name: new_val}
            except Exception as err:
                self.msg(f"|rImpossibile impostare l'opzione |w{new_name}|r:|n {err}")
                return False

        validators = {
            "ANSI": validate_bool,
            "CLIENTNAME": utils.to_str,
            "ENCODING": validate_encoding,
            "MCCP": validate_bool,
            "NOGOAHEAD": validate_bool,
            "NOPROMPTGOAHEAD": validate_bool,
            "MXP": validate_bool,
            "NOCOLOR": validate_bool,
            "NOPKEEPALIVE": validate_bool,
            "OOB": validate_bool,
            "RAW": validate_bool,
            "SCREENHEIGHT": validate_size,
            "SCREENWIDTH": validate_size,
            "AUTORESIZE": validate_bool,
            "SCREENREADER": validate_bool,
            "TERM": utils.to_str,
            "UTF-8": validate_bool,
            "XTERM256": validate_bool,
            "INPUTDEBUG": validate_bool,
            "FORCEDENDLINE": validate_bool,
            "LOCALECHO": validate_bool,
            "TRUECOLOR": validate_bool,
            "ISTYPING": validate_bool,
        }

        name = self.lhs.upper()
        val = self.rhs.strip()
        optiondict = False
        if val and name in validators:
            optiondict = update(name, val, validators[name])
        else:
            self.msg("|rNessuna opzione chiamata '|w%s|r'." % name)
        if optiondict:
            if "save" in self.switches:
                saved_options = self.account.attributes.get("_saved_protocol_flags", default={})
                saved_options.update(optiondict)
                self.account.attributes.add("_saved_protocol_flags", saved_options)
                for key in optiondict:
                    self.msg(f"|gOpzione {key} salvata.|n")
            if "clear" in self.switches:
                for key in optiondict:
                    self.account.attributes.get("_saved_protocol_flags", {}).pop(key, None)
                    self.msg(f"|g{key} rimossa dai salvataggi.")
            self.session.update_flags(**optiondict)


class CmdPassword(MuxCommand):
    """
    cambia la tua password

    Uso:
      password <vecchia password> = <nuova password>

    Cambia la tua password. Assicurati di sceglierne una sicura.
    """

    key = "password"
    locks = "cmd:pperm(Player)"

    account_caller = True

    def func(self):
        """funzione hook."""

        account = self.account
        if not self.rhs:
            self.msg("Uso: password <vecchiapass> = <nuovapass>")
            return
        oldpass = self.lhslist[0]
        newpass = self.rhslist[0]

        validated, error = account.validate_password(newpass)

        if not account.check_password(oldpass):
            self.msg("La vecchia password indicata non e' corretta.")
        elif not validated:
            errors = [e for suberror in error.messages for e in error.messages]
            string = "\n".join(errors)
            self.msg(string)
        else:
            account.set_password(newpass)
            account.save()
            self.msg("Password cambiata.")
            logger.log_sec(
                f"Password Changed: {account} (Caller: {account}, IP: {self.session.address})."
            )


class CmdColorTest(MuxCommand):
    """
    verifica quali colori supporta il tuo client

    Uso:
      color ansi | xterm256 | truecolor

    Stampa una mappa colori insieme ai codici colore interni al mud da
    usare per produrli. Verifica anche cosa e' supportato dal tuo
    client. Le scelte sono: ansi a 16 colori (supportato dalla
    maggior parte dei mud), lo standard xterm256 a 256 colori, oppure
    truecolor. Non viene fatto nessun controllo per determinare se il
    tuo client supporta i colori - in caso contrario vedrai caratteri
    senza senso.
    """

    key = "color"
    locks = "cmd:all()"
    help_category = "Generale"

    account_caller = True

    slice_bright_fg = slice(13, 21)
    slice_dark_fg = slice(21, 29)
    slice_dark_bg = slice(-8, None)
    slice_bright_bg = slice(None, None)

    def table_format(self, table):
        """Metodo di supporto per formattare le tabelle ansi/xterm256."""
        if not table:
            return [[]]

        extra_space = 1
        max_widths = [max([len(str(val)) for val in col]) for col in table]
        ftable = []
        for irow in range(len(table[0])):
            ftable.append(
                [
                    str(col[irow]).ljust(max_widths[icol]) + " " * extra_space
                    for icol, col in enumerate(table)
                ]
            )
        return ftable

    def make_hex_color_from_column(self, column_number, count):
        r = 255 - column_number * 255 / count
        g = column_number * 510 / count
        b = column_number * 255 / count

        if g > 255:
            g = 510 - g

        return (
            f"#{hex(round(r))[2:].zfill(2)}{hex(round(g))[2:].zfill(2)}{hex(round(b))[2:].zfill(2)}"
        )

    def func(self):
        """Mostra le tabelle colore."""

        if self.args.startswith("a"):
            from evennia.utils import ansi

            ap = ansi.ANSI_PARSER
            bright_fg = [
                "%s%s|n" % (code, code.replace("|", "||"))
                for code, _ in ap.ansi_map[self.slice_bright_fg]
            ]
            dark_fg = [
                "%s%s|n" % (code, code.replace("|", "||"))
                for code, _ in ap.ansi_map[self.slice_dark_fg]
            ]
            dark_bg = [
                "%s%s|n" % (code.replace("\\", ""), code.replace("|", "||").replace("\\", ""))
                for code, _ in ap.ansi_map[self.slice_dark_bg]
            ]
            bright_bg = [
                "%s%s|n" % (code.replace("\\", ""), code.replace("|", "||").replace("\\", ""))
                for code, _ in ap.ansi_xterm256_bright_bg_map[self.slice_bright_bg]
            ]
            dark_fg.extend(["" for _ in range(len(bright_fg) - len(dark_fg))])
            table = utils.format_table([bright_fg, dark_fg, bright_bg, dark_bg])
            string = "Colori ANSI:"
            for row in table:
                string += "\n " + " ".join(row)
            self.msg(string)
            self.msg(
                "||X : nero. ||/ : a capo, ||- : tab, ||_ : spazio, ||* : inverti, ||u :"
                " sottolineato\n"
                "Per combinare sfondo e primo piano, aggiungi il marcatore di sfondo per ultimo,"
                " es. ||r||[B.\n"
                "Nota: gli sfondi vivaci come ||[r richiedono che il tuo client gestisca i colori"
                " Xterm256."
            )

        elif self.args.startswith("x"):
            table = [[], [], [], [], [], [], [], [], [], [], [], []]
            for ir in range(6):
                for ig in range(6):
                    for ib in range(6):
                        table[ir].append("|%i%i%i%s|n" % (ir, ig, ib, "||%i%i%i" % (ir, ig, ib)))
                        table[6 + ir].append(
                            "|%i%i%i|[%i%i%i%s|n"
                            % (5 - ir, 5 - ig, 5 - ib, ir, ig, ib, "||[%i%i%i" % (ir, ig, ib))
                        )
            table = self.table_format(table)
            string = (
                "Colori Xterm256 (se non vedi tutte le sfumature, il tuo client potrebbe non"
                " segnalare di gestire xterm256):"
            )
            string += "\n" + "\n".join("".join(row) for row in table)
            table = [[], [], [], [], [], [], [], [], [], [], [], []]
            for ibatch in range(4):
                for igray in range(6):
                    letter = chr(97 + (ibatch * 6 + igray))
                    inverse = chr(122 - (ibatch * 6 + igray))
                    table[0 + igray].append("|=%s%s |n" % (letter, "||=%s" % letter))
                    table[6 + igray].append("|=%s|[=%s%s |n" % (inverse, letter, "||[=%s" % letter))
            for igray in range(6):
                if igray < 2:
                    letter = chr(121 + igray)
                    inverse = chr(98 - igray)
                    fg = "|=%s%s |n" % (letter, "||=%s" % letter)
                    bg = "|=%s|[=%s%s |n" % (inverse, letter, "||[=%s" % letter)
                else:
                    fg, bg = " ", " "
                table[0 + igray].append(fg)
                table[6 + igray].append(bg)
            table = self.table_format(table)
            string += "\n" + "\n".join("".join(row) for row in table)
            self.msg(string)

        elif self.args.startswith("t"):
            string = (
                "\n"
                "Truecolor (se non vedi una transizione arcobaleno fluida, il tuo client potrebbe"
                " non segnalare di gestire il truecolor): \n"
            )
            display_width = self.client_width()
            num_colors = display_width * 1
            color_block = [
                f"|[{self.make_hex_color_from_column(i, num_colors)} " for i in range(num_colors)
            ]
            color_block = [
                "".join(color_block[iline : iline + display_width])
                for iline in range(0, num_colors, display_width)
            ]
            string += "\n".join(color_block)

            string += (
                "\n|nfg: |#FF0000||#FF0000|n (|#F00||#F00|n) fino a |#0000FF||#0000FF|n"
                " (|#00F||#00F|n)"
                "\n|nbg: |[#FF0000||[#FF0000|n (|[#F00||[#F00|n) fino a"
                " |n|[#0000FF||[#0000FF |n(|[#00F||[#00F|n)"
            )

            self.msg(string)

        else:
            self.msg("Uso: color ansi || xterm256 || truecolor")


class CmdQuell(MuxCommand):
    """
    usa i permessi del personaggio invece di quelli dell'account

    Uso:
      quell
      unquell

    Normalmente, quando possiedi (puppet) un Personaggio/Oggetto, viene
    usato il livello di permesso dell'Account per determinare l'accesso.
    Questo comando passa il sistema di lock a usare invece i permessi
    dell'oggetto posseduto. E' utile soprattutto per fare test.
    Il quelling dei permessi gerarchici funziona solo verso il basso,
    quindi un Account non puo' usare un Personaggio con permessi
    superiori per elevare il proprio livello di permesso.
    Usa il comando unquell per tornare al funzionamento normale.
    """

    key = "quell"
    aliases = ["unquell"]
    locks = "cmd:pperm(Player)"
    help_category = "Generale"

    account_caller = True

    def _recache_locks(self, account):
        """Metodo di supporto per azzerare la cache dei lock su un oggetto gia' posseduto."""
        if self.session:
            char = self.session.puppet
            if char:
                char.locks.reset()
        account.locks.reset()

    def func(self):
        """Esegue il comando."""
        account = self.account
        permstr = (
            account.is_superuser and "(superuser)" or "(%s)" % ", ".join(account.permissions.all())
        )
        if self.cmdstring in ("unquell", "unquell"):
            if not account.attributes.get("_quell"):
                self.msg(f"Stai gia' usando i normali permessi dell'Account {permstr}.")
            else:
                account.attributes.remove("_quell")
                self.msg(f"Permessi dell'Account {permstr} ripristinati.")
        else:
            if account.attributes.get("_quell"):
                self.msg(f"Stai gia' facendo il quelling dei permessi dell'Account {permstr}.")
                return
            account.attributes.add("_quell", True)
            puppet = self.session.puppet if self.session else None
            if puppet:
                cpermstr = "(%s)" % ", ".join(puppet.permissions.all())
                cpermstr = f"Quelling ai permessi del puppet attuale {cpermstr}."
                cpermstr += (
                    f"\n(Nota: se questi sono superiori ai permessi dell'Account {permstr},"
                    " verra' usato il piu' basso dei due.)"
                )
                cpermstr += "\nUsa unquell per tornare all'uso normale dei permessi."
                self.msg(cpermstr)
            else:
                self.msg(
                    f"Quelling dei permessi dell'Account {permstr}. Usa unquell per riaverli."
                )
        self._recache_locks(account)


class CmdStyle(MuxCommand):
    """
    opzioni di stile in gioco

    Uso:
      style
      style <opzione> = <valore>

    Configura lo stile di elementi visivi in gioco come i bordi delle
    tabelle, le voci di help, ecc. Usa senza argomenti per vedere tutte
    le opzioni disponibili.
    """

    key = "style"
    switch_options = ["clear"]

    def func(self):
        if not self.args:
            self.list_styles()
            return
        self.set()

    def list_styles(self):
        table = self.styled_table("Opzione", "Descrizione", "Tipo", "Valore", width=78)
        for op_key in self.account.options.options_dict.keys():
            op_found = self.account.options.get(op_key, return_obj=True)
            table.add_row(
                op_key, op_found.description, op_found.__class__.__name__, op_found.display()
            )
        self.msg(str(table))

    def set(self):
        try:
            result = self.account.options.set(self.lhs, self.rhs)
        except ValueError as e:
            self.msg(str(e))
            return
        self.msg(f"Stile {result.key} impostato a {result.display()}")
