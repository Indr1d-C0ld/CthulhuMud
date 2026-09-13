"""
Localizzazione di CmdChannel (Fase C, quarta tornata), rimasta per
lungo tempo senza canali reali - colmato in Fase K, settima tornata
(vedi world/canali.py, commands/cthulhu_canali.py): GOSSIP,
INVESTIGATORTALK, HERO, REMTALK, IMMTALK, QUESTION/ANSWER, MUSIC ora
esistono davvero, ciascuno con un comando-scorciatoia dedicato che
rispecchia la sintassi della fonte. Questo comando @channel resta
comunque disponibile per la gestione avanzata (alias personali,
mute/unmute, cronologia, creazione di canali extra, amministrazione).

CmdObjectChannel e' un parent quasi vuoto per uso su Character/Object
(nessuna stringa propria) - lo riportiamo cosi' com'e'.
"""

from evennia.comms.comms import DefaultChannel
from evennia.commands.default.muxcommand import MuxCommand
from evennia.locks.lockhandler import LockException
from evennia.utils import class_from_module, create, logger
from evennia.utils.evmenu import ask_yes_no
from evennia.utils.logger import tail_log_file
from evennia.utils.utils import strip_unsafe_input
from django.conf import settings

CHANNEL_DEFAULT_TYPECLASS = class_from_module(
    settings.BASE_CHANNEL_TYPECLASS, fallback=settings.FALLBACK_CHANNEL_TYPECLASS
)
_DEFAULT_WIDTH = settings.CLIENT_DEFAULT_WIDTH


class CmdChannel(MuxCommand):
    """
    usa e gestisci i canali di gioco

    Uso:
      channel nomecanale <msg>
      channel nome canale = <msg>
      channel        (mostra tutte le iscrizioni)
      channel/all    (mostra i canali disponibili)
      channel/alias nomecanale = alias[;alias...]
      channel/unalias alias
      channel/who nomecanale
      channel/history nomecanale [= indice]
      channel/sub nomecanale [= alias[;alias...]]
      channel/unsub nomecanale[,nomecanale, ...]
      channel/mute nomecanale[,nomecanale,...]
      channel/unmute nomecanale[,nomecanale,...]

      channel/create nomecanale[;alias;alias[:typeclass]] [= descrizione]
      channel/destroy nomecanale [= motivo]
      channel/desc nomecanale = descrizione
      channel/lock nomecanale = stringa_di_lock
      channel/unlock nomecanale = stringa_di_lock
      channel/ban nomecanale   (elenca i ban)
      channel/ban[/quiet] nomecanale[, nomecanale, ...] = nomeutente [: motivo]
      channel/unban[/quiet] nomecanale[, nomecanale, ...] = nomeutente
      channel/boot[/quiet] nomecanale[,nomecanale,...] = nomeutente [: motivo]

    # sotto-argomenti

    ## invio messaggi

    Uso: channel nomecanale msg
         channel nome canale = msg  (con spazi nel nome del canale)

    Invia un messaggio al canale. Nota che userai raramente il comando
    in questa forma; di solito puoi usare la scorciatoia

        nomecanale <msg>
        aliascanale <msg>

    Per esempio

        pubblico Ciao a tutti
        pub Ciao a tutti

    (questa scorciatoia non funziona per alias che contengono spazi)

    Vedi channel/alias per l'aiuto sull'impostazione degli alias di canale.

    ## alias e unalias

    Uso: channel/alias canale = alias[;alias[;alias...]]
         channel/unalias alias
         channel    - elenca le tue iscrizioni e i tuoi alias per ogni canale

    Imposta uno o piu' alias personali per fare riferimento a un
    canale. Per esempio:

        channel/alias gilda dei guerrieri = guerriero;gguerra;canaleguerra;gilda guerrieri

    Ora puoi inviare al canale usando tutte queste forme:

        gilda dei guerrieri Ciao
        guerriero Ciao
        gguerra Ciao
        canaleguerra Ciao

    Nota che questo non funziona se l'alias contiene uno spazio. Quindi
    l'alias 'gilda guerrieri' va usato con il comando `channel`:

        channel gilda guerrieri = Ciao

    Gli alias di canale possono essere rimossi uno alla volta, con lo
    switch '/unalias'.

    ## who

    Uso: channel/who nomecanale

    Elenca gli iscritti al canale. Mostra chi e' attualmente offline o
    sta silenziando il canale. Gli iscritti che stanno 'silenziando'
    non vedranno i messaggi inviati al canale (usa channel/mute per
    silenziare un canale).

    ## history

    Uso: channel/history canale [= indice]

    Mostra le ultime |c20|n righe della cronologia del canale. Fornendo
    un numero indice, tornerai indietro di quel numero di righe prima
    di vedere quelle 20 righe.

    Per esempio:

        channel/history pubblico = 35

    tornera' indietro di 35 righe e mostrera' le 20 righe precedenti a
    partire da quel punto (quindi le righe da -35 a -55).

    ## sub e unsub

    Uso: channel/sub canale [=alias[;alias;...]]
         channel/unsub canale

    Ti iscrive a un canale e opzionalmente ti assegna scorciatoie
    personali da usare per inviare a quel canale (vedi alias). Quando ti
    disiscrivi, anche tutti i tuoi alias personali vengono rimossi.

    ## mute e unmute

    Uso: channel/mute nomecanale
         channel/unmute nomecanale

    Silenziare azzera tutto l'output dal canale senza disiscriverti
    davvero. Gli altri membri del canale vedranno che sei silenziato
    nell'elenco /who. Inviare un messaggio al canale ti silenzia
    automaticamente di nuovo (nota: cosi' come nell'originale, inviare
    un messaggio in realta' NON toglie il silenziamento - il testo
    dell'aiuto originale a monte e' impreciso su questo punto, lo
    riportiamo com'e' per fedelta').

    ## create e destroy

    Uso: channel/create nomecanale[;alias;alias[:typeclass]] [= descrizione]
         channel/destroy nomecanale [= motivo]

    Crea un nuovo canale (o distrugge uno che controlli). Ti iscriverai
    automaticamente al canale che crei, e tutti verranno espulsi e
    perderanno tutti gli alias verso un canale distrutto.

    ## lock e unlock

    Uso: channel/lock nomecanale = stringa_di_lock
         channel/unlock nomecanale = stringa_di_lock

    Nota: questo e' un comando da admin.

    Una stringa di lock e' nella forma tipolock:funzionelock(). I
    canali comprendono tre tipi di lock:
        listen - chi puo' ascoltare o entrare nel canale.
        send - chi puo' inviare messaggi al canale
        control - chi controlla il canale. Di solito e' chi lo ha creato.

    Le funzioni di lock comuni sono all() e perm(). Per rendere un
    canale ascoltabile da tutti ma dove solo i builder possono parlare:

        listen:all()
        send: perm(Builders)

    ## boot e ban

    Uso:
           channel/boot[/quiet] nomecanale[,nomecanale,...] = nomeutente [: motivo]
           channel/ban nomecanale[, nomecanale, ...] = nomeutente [: motivo]
           channel/unban nomecanale[, nomecanale, ...] = nomeutente
           channel/unban nomecanale
           channel/ban nomecanale    (elenca i ban)

    Espellere (boot) caccia temporaneamente un iscritto nominato dal/i
    canale/i. Il 'motivo' verra' comunicato all'utente espulso. A meno
    che non venga usato lo switch /quiet, il canale verra' informato
    dell'azione. Un utente espulso puo' comunque ricollegarsi, ma dovra'
    reimpostare i suoi alias.

    Bannare mette un utente in una lista nera che gli impedisce di
    (ri)entrare nei canali indicati. Lo espellera' anche da quei canali
    se era gia' connesso. 'motivo' e '/quiet' funzionano come per
    l'espulsione.

    Esempio:
        boot canale1 = UtenteCattivo : Ti caccio un attimo per farti calmare.
        ban canale1,canale2 = UtenteCattivo : Bannato per spam.
    """

    key = "@channel"
    aliases = ["@chan", "@channels"]
    help_category = "Comunicazioni"
    locks = "cmd:not pperm(channel_banned);admin:all();manage:all();changelocks:perm(Admin)"
    switch_options = (
        "list",
        "all",
        "history",
        "sub",
        "unsub",
        "mute",
        "unmute",
        "alias",
        "unalias",
        "create",
        "destroy",
        "desc",
        "lock",
        "unlock",
        "boot",
        "ban",
        "unban",
        "who",
    )
    account_caller = True

    def search_channel(self, channelname, exact=False, handle_errors=True):
        """Funzione di supporto per cercare un singolo canale, con gestione errori."""
        caller = self.caller
        channelname = caller.nicks.get(key=channelname, category="channel") or channelname

        channels = CHANNEL_DEFAULT_TYPECLASS.objects.channel_search(channelname, exact=True)

        if not channels and not exact:
            channels = CHANNEL_DEFAULT_TYPECLASS.objects.channel_search(channelname, exact=exact)

        channels = [
            channel
            for channel in channels
            if channel.access(caller, "listen") or channel.access(caller, "control")
        ]

        if handle_errors:
            if not channels:
                self.msg(
                    f"Nessun canale trovato che corrisponda a '{channelname}' "
                    "(potrebbe anche essere per mancanza di accesso)."
                )
                return None
            elif len(channels) > 1:
                self.msg(
                    f"Piu' possibili canali/alias corrispondenti per '{channelname}':\n"
                    + ", ".join(chan.key for chan in channels)
                )
                return None
            return channels[0]
        else:
            if not channels:
                return []
            elif len(channels) > 1:
                return list(channels)
            return [channels[0]]

    def msg_channel(self, channel, message, **kwargs):
        """Invia un messaggio a un dato canale, controllando il permesso 'send'."""
        if not channel.access(self.caller, "send"):
            self.msg(f"Non hai il permesso di inviare messaggi al canale {channel}")
            return

        message = strip_unsafe_input(message, self.session)

        channel.msg(message, senders=self.caller, **kwargs)

    def get_channel_history(self, channel, start_index=0):
        """Mostra la cronologia di un canale."""
        caller = self.caller
        log_file = channel.get_log_filename()

        def send_msg(lines):
            return self.msg(
                "".join(line.split("[-]", 1)[1] if "[-]" in line else line for line in lines)
            )

        tail_log_file(log_file, start_index, 20, callback=send_msg)

    def sub_to_channel(self, channel):
        """Iscrive al canale. I permessi vanno controllati prima di questa chiamata."""
        caller = self.caller

        if channel.has_connection(caller):
            return False, f"Sei gia' in ascolto sul canale {channel.key}."

        result = channel.connect(caller)

        return (
            result,
            "" if result else f"Non ti era permesso iscriverti al canale {channel.key}",
        )

    def unsub_from_channel(self, channel, **kwargs):
        """Disiscrive dal canale. I permessi vanno controllati prima di questa chiamata."""
        caller = self.caller

        if not channel.has_connection(caller):
            return False, f"Non sei in ascolto sul canale {channel.key}."

        result = channel.disconnect(caller)

        return (
            result,
            "" if result else f"Non e' stato possibile disiscriversi dal canale {channel.key}",
        )

    def add_alias(self, channel, alias, **kwargs):
        """Aggiunge un nuovo alias (nick) personale per questo canale."""
        channel.add_user_channel_alias(self.caller, alias, **kwargs)

    def remove_alias(self, alias, **kwargs):
        """Rimuove un alias da un canale."""
        if self.caller.nicks.has(alias, category="channel", **kwargs):
            DefaultChannel.remove_user_channel_alias(self.caller, alias)
            return True, ""
        return False, "Non e' stato definito nessun alias del genere."

    def get_channel_aliases(self, channel):
        """Ottiene gli alias personali dell'utente per un dato canale."""
        chan_key = channel.key.lower()
        nicktuples = self.caller.nicks.get(category="channel", return_tuple=True, return_list=True)
        if nicktuples:
            return [tup[2] for tup in nicktuples if tup[3].lower() == chan_key]
        return []

    def mute_channel(self, channel):
        """Silenzia temporaneamente un canale."""
        if channel.mute(self.caller):
            return True, ""
        return False, f"Il canale {channel.key} era gia' silenziato."

    def unmute_channel(self, channel):
        """Toglie il silenziamento a un canale."""
        if channel.unmute(self.caller):
            return True, ""
        return False, f"Il canale {channel.key} non era silenziato."

    def create_channel(self, name, description, typeclass=None, aliases=None):
        """Crea un nuovo canale. Il nome non deve gia' esistere (senza distinzione maiuscole)."""
        caller = self.caller
        if typeclass:
            typeclass = class_from_module(typeclass)
        else:
            typeclass = CHANNEL_DEFAULT_TYPECLASS

        if typeclass.objects.channel_search(name, exact=True):
            return False, f"Il canale {name} esiste gia'."

        lockstring = "send:all();listen:all();control:id(%s)" % caller.id

        new_chan = create.create_channel(
            name, aliases=aliases, desc=description, locks=lockstring, typeclass=typeclass
        )
        self.sub_to_channel(new_chan)
        return new_chan, ""

    def destroy_channel(self, channel, message=None):
        """Distrugge un canale esistente. I permessi vanno controllati prima di chiamare questa funzione."""
        caller = self.caller

        channel_key = channel.key
        if message is None:
            message = (
                f"|rIl canale {channel_key} sta per essere distrutto. "
                "Assicurati di ripulire eventuali alias del canale.|n"
            )
        if message:
            channel.msg(message, senders=caller, bypass_mute=True)
        channel.delete()
        logger.log_sec(f"Channel {channel_key} was deleted by {caller}")

    def set_lock(self, channel, lockstring):
        """Imposta una stringa di lock su un canale. I permessi vanno gia' controllati."""
        try:
            channel.locks.add(lockstring)
        except LockException as err:
            return False, err
        return True, ""

    def unset_lock(self, channel, lockstring):
        """Rimuove i lock in una stringa di lock su un canale. I permessi vanno gia' controllati."""
        try:
            channel.locks.remove(lockstring)
        except LockException as err:
            return False, err
        return True, ""

    def set_desc(self, channel, description):
        """Imposta la descrizione di un canale, mostrata negli elenchi."""
        channel.db.desc = description

    def boot_user(self, channel, target, quiet=False, reason=""):
        """Espelle un utente da un canale, con motivo opzionale."""
        if not channel.subscriptions.has(target):
            return False, f"{target} non e' connesso al canale {channel.key}."
        for nick in [
            nick
            for nick in target.nicks.get(category="channel", return_tuple=True) or []
            if nick.value[3].lower() == channel.key
        ]:
            nick.delete()
        channel.disconnect(target)
        reason = f" Motivo: {reason}" if reason else ""
        target.msg(f"Sei stato espulso dal canale {channel.key} da {self.caller.key}.{reason}")
        if not quiet:
            channel.msg(f"{target.key} e' stato espulso dal canale da {self.caller.key}.{reason}")

        logger.log_sec(
            f"Channel Boot: {target} (Channel: {channel}, "
            f"Reason: {reason.strip()}, Caller: {self.caller}"
        )
        return True, ""

    def ban_user(self, channel, target, quiet=False, reason=""):
        """Banna un utente da un canale, bloccandogli l'accesso. Lo espelle anche se connesso."""
        self.boot_user(channel, target, quiet=quiet, reason=reason)
        if channel.ban(target):
            return True, ""
        return False, f"{target} e' gia' bannato da questo canale."

    def unban_user(self, channel, target):
        """Rimuove il ban di un utente da un canale."""
        if channel.unban(target):
            return True, ""
        return False, f"{target} non era bannato da questo canale."

    def channel_list_bans(self, channel):
        """Mostra i ban di un canale."""
        return [banned.key for banned in channel.banlist]

    def channel_list_who(self, channel):
        """Mostra l'elenco degli iscritti a un canale, online o meno."""
        caller = self.caller
        mute_list = list(channel.mutelist)
        online_list = channel.subscriptions.online()
        if channel.access(caller, "control"):
            all_subs = list(channel.subscriptions.all())
        else:
            all_subs = online_list

        who_list = []
        for subscriber in all_subs:
            name = subscriber.get_display_name(caller)
            conditions = (
                "silenzia" if subscriber in mute_list else "",
                "offline" if subscriber not in online_list else "",
            )
            conditions = [cond for cond in conditions if cond]
            cond_text = "(" + ", ".join(conditions) + ")" if conditions else ""
            who_list.append(f"{name}{cond_text}")

        return who_list

    def list_channels(self, channelcls=CHANNEL_DEFAULT_TYPECLASS):
        """Restituisce i canali disponibili (iscritti e non)."""
        caller = self.caller
        subscribed_channels = list(channelcls.objects.get_subscriptions(caller))
        unsubscribed_available_channels = [
            chan
            for chan in channelcls.objects.get_all_channels()
            if chan not in subscribed_channels and chan.access(caller, "listen")
        ]
        return subscribed_channels, unsubscribed_available_channels

    def display_subbed_channels(self, subscribed):
        """Mostra i canali a cui si e' iscritti."""
        comtable = self.styled_table(
            "id",
            "canale",
            "miei alias",
            "lock",
            "descrizione",
            align="l",
            maxwidth=_DEFAULT_WIDTH,
        )
        for chan in subscribed:
            locks = "-"
            chanid = "-"
            if chan.access(self.caller, "control"):
                locks = chan.locks
                chanid = chan.id

            my_aliases = ", ".join(self.get_channel_aliases(chan))
            comtable.add_row(
                *(
                    chanid,
                    "{key}{aliases}".format(
                        key=chan.key,
                        aliases=";" + ";".join(chan.aliases.all()) if chan.aliases.all() else "",
                    ),
                    my_aliases,
                    locks,
                    chan.db.desc,
                )
            )
        return comtable

    def display_all_channels(self, subscribed, available):
        """Mostra tutti i canali disponibili."""
        caller = self.caller

        comtable = self.styled_table(
            "iscr.",
            "canale",
            "alias",
            "miei alias",
            "descrizione",
            maxwidth=_DEFAULT_WIDTH,
        )
        channels = subscribed + available

        for chan in channels:
            if chan not in subscribed:
                substatus = "|rNo|n"
            elif caller in chan.mutelist:
                substatus = "|rSilenziato|n"
            else:
                substatus = "|gSi|n"
            my_aliases = ", ".join(self.get_channel_aliases(chan))
            comtable.add_row(
                *(
                    substatus,
                    chan.key,
                    ",".join(chan.aliases.all()) if chan.aliases.all() else "",
                    my_aliases,
                    chan.db.desc,
                )
            )
        comtable.reformat_column(0, width=8)

        return comtable

    def func(self):
        """Funzionalita' principale del comando."""

        caller = self.caller
        switches = self.switches
        channel_names = [name for name in self.lhslist if name]

        if "all" in switches:
            subscribed, available = self.list_channels()
            table = self.display_all_channels(subscribed, available)

            self.msg(
                "\n|wCanali disponibili|n (usa senza argomenti per "
                f"mostrare solo le tue iscrizioni)\n{table}"
            )
            return

        if not channel_names:
            subscribed, _ = self.list_channels()
            table = self.display_subbed_channels(subscribed)

            self.msg(f"\n|wIscrizioni ai canali|n (usa |w/all|n per vedere tutti i disponibili):\n{table}")
            return

        if not self.switches and not self.args:
            self.msg("Uso[/switch]: channel [= messaggio]")
            return

        if "create" in switches:
            if not self.access(caller, "manage"):
                self.msg("Non hai accesso per usare channel/create.")
                return

            config = self.lhs
            if not config:
                self.msg("Per creare: channel/create nome[;alias][:typeclass] [= descrizione]")
                return
            name, *typeclass = config.rsplit(":", 1)
            typeclass = typeclass[0] if typeclass else None
            name, *aliases = name.rsplit(";")
            description = self.rhs or ""
            chan, err = self.create_channel(name, description, typeclass=typeclass, aliases=aliases)
            if chan:
                self.msg(f"Creato (e a cui ti sei iscritto) il nuovo canale '{chan.key}'.")
            else:
                self.msg(err)
            return

        if "unalias" in switches:
            alias = self.args.strip()
            if not alias:
                self.msg("Indica l'alias da rimuovere come channel/unalias <alias>")
                return
            success, err = self.remove_alias(alias)
            if success:
                self.msg(f"Rimosso il tuo alias di canale '{alias}'.")
            else:
                self.msg(err)
            return

        possible_lhs_message = ""
        if not self.rhs and self.args and " " in self.args:
            no_rhs_channel_name = self.args.split(" ", 1)[0]
            possible_lhs_message = self.args[len(no_rhs_channel_name) :]
            if possible_lhs_message.strip() == "=":
                possible_lhs_message = ""
            channel_names.append(no_rhs_channel_name)

        channels = []
        errors = []
        for channel_name in channel_names:
            found_channels = self.search_channel(channel_name, exact=False, handle_errors=False)
            if not found_channels:
                errors.append(
                    f"Nessun canale trovato che corrisponda a '{channel_name}' "
                    "(potrebbe anche essere per mancanza di accesso)."
                )
            elif len(found_channels) > 1:
                errors.append(
                    f"Piu' possibili canali/alias corrispondenti per '{channel_name}':\n"
                    + ", ".join(chan.key for chan in found_channels)
                )
            else:
                channels.append(found_channels[0])

        if not channels:
            self.msg("\n".join(errors))
            return

        channel = channels[0]

        if not switches:
            if self.rhs:
                self.msg_channel(channel, self.rhs.strip())
            elif channel and possible_lhs_message:
                self.msg_channel(channel, possible_lhs_message.strip())
            else:
                subscribed, available = self.list_channels()
                if channel in subscribed:
                    table = self.display_subbed_channels([channel])
                    header = f"Canale |w{channel.key}|n"
                    self.msg(
                        f"{header}\n(usa |w{channel.key} <msg>|n (o un alias di canale) "
                        "per chattare, e il comando 'channel' "
                        f"per personalizzare)\n{table}"
                    )
                elif channel in available:
                    table = self.display_all_channels([], [channel])
                    self.msg(
                        "\n|wNon sei iscritto a questo canale|n (usa /list per "
                        f"mostrare tutte le iscrizioni)\n{table}"
                    )
            return

        if "history" in switches or "hist" in switches:
            index = self.rhs or 0
            try:
                index = max(0, int(index))
            except ValueError:
                self.msg(
                    "L'indice della cronologia (quante righe tornare indietro) "
                    "deve essere un intero >= 0."
                )
                return
            self.get_channel_history(channel, start_index=index)
            return

        if "sub" in switches:
            aliases = []
            if self.rhs:
                aliases = set(alias.strip().lower() for alias in self.rhs.split(";"))
            success, err = self.sub_to_channel(channel)
            if success:
                for alias in aliases:
                    self.add_alias(channel, alias)
                alias_txt = ", ".join(aliases)
                alias_txt = f" usando l'alias/gli alias {alias_txt}" if aliases else ""
                self.msg(
                    "Ora sei iscritto "
                    f"al canale {channel.key}{alias_txt}. Usa /alias per "
                    "aggiungere altri alias per riferirti al canale."
                )
            else:
                self.msg(err)
            return

        if "unsub" in switches:
            success, err = self.unsub_from_channel(channel)
            if success:
                self.msg(f"Ti sei disiscritto dal canale {channel.key}. Tutti gli alias sono stati rimossi.")
            else:
                self.msg(err)
            return

        if "alias" in switches:
            alias = self.rhs
            if not alias:
                self.msg("Indica l'alias come channel/alias nomecanale = alias")
                return
            self.add_alias(channel, alias)
            self.msg(f"Aggiunto/aggiornato il tuo alias '{alias}' per il canale {channel.key}.")
            return

        if "mute" in switches:
            success, err = self.mute_channel(channel)
            if success:
                self.msg(f"Silenziato il canale {channel.key}.")
            else:
                self.msg(err)
            return

        if "unmute" in switches:
            success, err = self.unmute_channel(channel)
            if success:
                self.msg(f"Tolto il silenziamento al canale {channel.key}.")
            else:
                self.msg(err)
            return

        if "destroy" in switches or "delete" in switches:
            if not self.access(caller, "manage"):
                self.msg("Non hai accesso per usare channel/destroy.")
                return

            if not channel.access(caller, "control"):
                self.msg("Puoi eliminare solo i canali che controlli.")
                return

            reason = self.rhs or None

            def _perform_delete(caller, *args, **kwargs):
                self.destroy_channel(channel, message=reason)
                self.msg(f"Il canale {channel.key} e' stato eliminato con successo.")

            ask_yes_no(
                caller,
                prompt=(
                    f"Sei sicuro di voler eliminare il canale '{channel.key}' "
                    "(assicurati che il nome sia corretto!)?\nQuesto disconnettera' e "
                    "rimuovera' gli alias di tutti gli utenti. {options}?"
                ),
                yes_action=_perform_delete,
                no_action="Annullato.",
                default="N",
            )

        if "desc" in switches:
            if not self.access(caller, "manage"):
                self.msg("Non hai accesso per usare channel/desc.")
                return

            if not channel.access(caller, "control"):
                self.msg("Puoi cambiare la descrizione solo dei canali che controlli.")
                return

            desc = self.rhs.strip()

            if not desc:
                self.msg("Uso: /desc canale = descrizione")
                return

            self.set_desc(channel, desc)
            self.msg("Descrizione del canale aggiornata.")

        if "lock" in switches:
            if not self.access(caller, "changelocks"):
                self.msg("Non hai accesso per usare channel/lock.")
                return

            if not channel.access(caller, "control"):
                self.msg("Ti serve l'accesso 'control' per cambiare i lock su questo canale.")
                return

            lockstring = self.rhs.strip()

            if not lockstring:
                self.msg("Uso: channel/lock nomecanale = stringa_di_lock")
                return

            success, err = self.set_lock(channel, self.rhs)
            if success:
                self.msg("Lock aggiunto/aggiornato sul canale.")
            else:
                self.msg(f"Impossibile aggiungere/aggiornare il lock: {err}")
            return

        if "unlock" in switches:
            if not self.access(caller, "changelocks"):
                self.msg("Non hai accesso per usare channel/unlock.")
                return

            if not channel.access(caller, "control"):
                self.msg("Ti serve l'accesso 'control' per cambiare i lock su questo canale.")
                return

            lockstring = self.rhs.strip()

            if not lockstring:
                self.msg("Uso: channel/unlock nomecanale = stringa_di_lock")
                return

            success, err = self.unset_lock(channel, self.rhs)
            if success:
                self.msg("Lock rimosso dal canale.")
            else:
                self.msg(f"Impossibile rimuovere il lock: {err}")
            return

        if "boot" in switches:
            if not self.access(caller, "admin"):
                self.msg("Non hai accesso per usare channel/boot.")
                return

            if not self.rhs:
                self.msg("Uso: channel/boot canale[,canale,...] = nomeutente [:motivo]")
                return

            target_str, *reason = self.rhs.rsplit(":", 1)
            reason = reason[0].strip() if reason else ""

            for chan in channels:
                if not chan.access(caller, "control"):
                    self.msg(f"Ti serve l'accesso 'control' per espellere un utente da {chan.key}.")
                    return

                target = caller.search(target_str, candidates=chan.subscriptions.all())
                if not target:
                    self.msg(f"Impossibile espellere '{target_str}' - non e' nel canale {chan.key}.")
                    return

            def _boot_user(caller, *args, **kwargs):
                for chan in channels:
                    success, err = self.boot_user(chan, target, quiet=False, reason=reason)
                    if success:
                        self.msg(f"Espulso {target.key} dal canale {chan.key}.")
                    else:
                        self.msg(f"Impossibile espellere {target.key} dal canale {chan.key}: {err}")

            channames = ", ".join(chan.key for chan in channels)
            reasonwarn = (
                ". Nota anche che il motivo verra' comunicato al canale" if reason else ""
            )
            ask_yes_no(
                caller,
                prompt=(
                    f"Sei sicuro di voler espellere l'utente {target.key} dal/dai "
                    f"canale/i {channames} (assicurati che nome/canali siano corretti{reasonwarn}). "
                    "{options}?"
                ),
                yes_action=_boot_user,
                no_action="Annullato.",
                default="Y",
            )
            return

        if "ban" in switches:
            if not self.access(caller, "admin"):
                self.msg("Non hai accesso per usare channel/ban.")
                return

            if not self.rhs:
                if not channel.access(caller, "control"):
                    self.msg(f"Ti serve l'accesso 'control' per vedere i ban sul canale {channel.key}")
                    return

                bans = [
                    "Ban del canale "
                    "(per bannare, usa channel/ban canale[,canale,...] = nomeutente [:motivo]"
                ]
                bans.extend(self.channel_list_bans(channel))
                self.msg("\n".join(bans))
                return

            target_str, *reason = self.rhs.rsplit(":", 1)
            reason = reason[0].strip() if reason else ""

            for chan in channels:
                if not chan.access(caller, "control"):
                    self.msg(f"Non hai accesso per bannare utenti sul canale {chan.key}")
                    return

                target = caller.search(target_str, candidates=chan.subscriptions.all())

                if not target:
                    self.msg(f"Impossibile bannare '{target_str}' - non e' nel canale {chan.key}.")
                    return

            def _ban_user(caller, *args, **kwargs):
                for chan in channels:
                    success, err = self.ban_user(chan, target, quiet=False, reason=reason)
                    if success:
                        self.msg(f"Bannato {target.key} dal canale {chan.key}.")
                    else:
                        self.msg(f"Impossibile espellere {target.key} dal canale {chan.key}: {err}")

            channames = ", ".join(chan.key for chan in channels)
            reasonwarn = (
                ". Nota anche che il motivo verra' comunicato al canale" if reason else ""
            )
            ask_yes_no(
                caller,
                (
                    f"Sei sicuro di voler bannare l'utente {target.key} dal/dai "
                    f"canale/i {channames} (assicurati che nome/canali siano corretti{reasonwarn}) "
                    "{options}?"
                ),
                _ban_user,
                "Annullato.",
            )
            return

        if "unban" in switches:
            if not self.access(caller, "admin"):
                self.msg("Non hai accesso per usare channel/unban.")
                return

            target_str = self.rhs.strip()

            if not target_str:
                self.msg("Uso: canale[,canale,...] = utente")
                return

            banlists = []
            for chan in channels:
                if not chan.access(caller, "control"):
                    self.msg(f"Non hai accesso per rimuovere ban sul canale {chan.key}")
                    return
                banlists.extend(chan.banlist)

            target = caller.search(target_str, candidates=banlists)
            if not target:
                self.msg(f"Impossibile trovare un utente bannato '{target_str}' nel/nei canale/i indicato/i.")
                return

            for chan in channels:
                success, err = self.unban_user(channel, target)
                if success:
                    self.msg(f"Rimosso il ban di {target_str} dal canale {chan.key}")
                else:
                    self.msg(err)
            return

        if "who" in switches:
            who_list = [f"Iscritti a {channel.key}:"]
            who_list.extend(self.channel_list_who(channel))
            self.msg("\n".join(who_list))
            return


class CmdObjectChannel(CmdChannel):
    account_caller = False
