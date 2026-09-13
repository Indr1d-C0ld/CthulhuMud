"""
Localizzazione dei comandi di comunicazione privata (Fase C).

CmdPage (tell) e' tradotto per intero qui sotto: e' l'unico comando di
comms.py con un impiego realistico gia' ora (messaggistica privata tra
account). CmdChannel resta volutamente NON tradotto in QUESTO file:
sono oltre 1250 righe che implementano un intero mini-linguaggio a
switch (create/destroy/alias/ban/mute/lock/...) con testo di aiuto
incorporato nel docstring - tradotto poi per intero in Fase C, quarta
tornata, vedi commands/cthulhu_channels.py (i canali reali sono
arrivati ancora dopo, in Fase K settima tornata: world/canali.py).
"""

from django.db.models import Q

from evennia.commands.default.muxcommand import MuxCommand
from evennia.comms.models import Msg
from evennia.utils import create, utils as evennia_utils


class CmdPage(MuxCommand):
    """
    manda un messaggio privato a un altro account

    Uso:
      page <account> <messaggio>
      page[/switch] [<account>,<account>,... = <messaggio>]
      tell        ''
      page <numero>

    Switch:
      last - mostra a chi hai scritto per ultimo
      list - mostra gli ultimi <numero> messaggi (predefinito)

    Manda un messaggio all'account bersaglio (se online). Senza argomenti,
    mostra la lista dei tuoi ultimi messaggi. Il segno = serve per piu'
    destinatari o per un bersaglio con spazi nel nome.
    """

    key = "page"
    aliases = ["tell"]
    switch_options = ("last", "list")
    locks = "cmd:not pperm(page_banned)"
    help_category = "Comunicazioni"

    account_caller = True

    def func(self):
        caller = self.caller

        pages_we_sent = Msg.objects.get_messages_by_sender(caller).order_by("-db_date_created")
        pages_we_sent = pages_we_sent.filter(
            Q(db_tags__db_key__iexact="page", db_tags__db_category__iexact="comms")
            | Q(db_tags__isnull=True)
        )
        pages_we_sent = [msg for msg in pages_we_sent if msg.access(caller, "read", default=True)]

        pages_we_got = Msg.objects.get_messages_by_receiver(caller).order_by("-db_date_created")
        pages_we_got = pages_we_got.filter(
            Q(db_tags__db_key__iexact="page", db_tags__db_category__iexact="comms")
            | Q(db_tags__isnull=True)
        )
        pages_we_got = [msg for msg in pages_we_got if msg.access(caller, "read", default=True)]

        targets, message, number = [], None, None

        if "last" in self.switches:
            if pages_we_sent:
                recv = ",".join(obj.key for obj in pages_we_sent[0].receivers)
                self.msg(f"Il tuo ultimo messaggio a |c{recv}|n:{pages_we_sent[0].message}")
                return
            else:
                self.msg("Non hai ancora scritto a nessuno.")
                return

        if self.args:
            if self.rhs:
                for target in self.lhslist:
                    target_obj = self.caller.search(target)
                    if not target_obj:
                        return
                    targets.append(target_obj)
                message = self.rhs.strip()
            else:
                target, *message = self.args.split(" ", 1)
                if target and target.isnumeric():
                    number = int(target)
                elif message:
                    target_obj = self.caller.search(target, quiet=True)
                    if target_obj:
                        targets = [target_obj[0]]
                        message = message[0].strip()
                    else:
                        message = self.args.strip()
                else:
                    message = self.args.strip()

        pages = list(pages_we_sent) + list(pages_we_got)
        pages = sorted(pages, key=lambda page: page.date_created)

        if message:
            if not targets:
                if pages_we_sent:
                    targets = pages_we_sent[0].receivers
                else:
                    self.msg("A chi vuoi scrivere?")
                    return

            header = f"|wAccount|n |c{caller.key}|n |wscrive:|n"
            if message.startswith(":"):
                message = f"{caller.key} {message.strip(':').strip()}"

            target_perms = " or ".join([f"id({target.id})" for target in targets + [caller]])
            create.create_message(
                caller,
                message,
                receivers=targets,
                locks=(
                    f"read:{target_perms} or perm(Admin);"
                    f"delete:id({caller.id}) or perm(Admin);"
                    f"edit:id({caller.id}) or perm(Admin)"
                ),
                tags=[("page", "comms")],
            )

            received = []
            rstrings = []
            for target in targets:
                if not target.access(caller, "msg"):
                    rstrings.append(f"Non ti e' permesso scrivere a {target}.")
                    continue
                # Fase K, settima tornata: IGNORE (commands/cthulhu_canali.py) -
                # confermato dalla fonte (helps/ooc.txt).
                if caller.key in (getattr(target, "db", None) and target.db.ignora or set()):
                    rstrings.append(f"{target} non riceve i tuoi messaggi.")
                    continue
                target.msg(f"{header} {message}")
                if hasattr(target, "sessions") and not target.sessions.count():
                    received.append(f"|C{target.name}|n")
                    rstrings.append(
                        f"{received[-1]} e' offline. Vedra' il tuo messaggio quando "
                        "controllera' i suoi messaggi ricevuti."
                    )
                else:
                    received.append(f"|c{target.name}|n")
            if rstrings:
                self.msg("\n".join(rstrings))
            self.msg("Hai scritto a %s: '%s'." % (", ".join(received), message))
            return

        else:
            if number is not None and len(pages) > number:
                lastpages = pages[-number:]
            else:
                lastpages = pages
            to_template = "|w{date}{clr} {sender}|na{clr}{receiver}|n:> {message}"
            from_template = "|w{date}{clr} {receiver}|nda{clr}{sender}|n:< {message}"
            listing = []
            prev_selfsend = False
            for page in lastpages:
                multi_send = len(page.senders) > 1
                multi_recv = len(page.receivers) > 1
                sending = self.caller in page.senders
                selfsend = sending and self.caller in page.receivers
                if selfsend:
                    if prev_selfsend:
                        sending = False
                        prev_selfsend = False
                    else:
                        prev_selfsend = True

                clr = "|c" if sending else "|g"

                sender = f"|n,{clr}".join(obj.key for obj in page.senders)
                receiver = f"|n,{clr}".join([obj.name for obj in page.receivers])
                if sending:
                    template = to_template
                    sender = f"{sender} " if multi_send else ""
                    receiver = f" {receiver}" if multi_recv else f" {receiver}"
                else:
                    template = from_template
                    receiver = f"{receiver} " if multi_recv else ""
                    sender = f" {sender} " if multi_send else f" {sender}"

                listing.append(
                    template.format(
                        date=evennia_utils.datetime_format(page.date_created),
                        clr=clr,
                        sender=sender,
                        receiver=receiver,
                        message=page.message,
                    )
                )
            lastpages = "\n ".join(listing)

            if lastpages:
                string = f"I tuoi ultimi messaggi:\n {lastpages}"
            else:
                string = "Non hai ancora inviato o ricevuto messaggi privati."
            self.msg(string)
            return
