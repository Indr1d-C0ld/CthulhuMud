"""
Comandi di sopravvivenza (Fase G, prima tornata): eat/mangia,
drink/bevi, feed/nutri - sintassi confermata verbatim dal sito
originale (helps/eat.txt): "DRINK <object> / EAT <object> /
FEED <character> <object>".

FEED richiede che il bersaglio abbia attivato la ricezione forzata
(db.accetta_feed): la fonte dice solo "assuming that character has
that option toggled" senza descrivere l'opzione - qui e' un semplice
interruttore personale (comando FEEDME/ACCETTAFEED), scelta di design
esplicita.

Fase K, diciassettesima tornata: mangia()/bevi() (world/sopravvivenza.py)
ora rifiutano se il bersaglio e' in combattimento, confermato dalla
fonte ("You can eat and drink while debating and casting spells, but
not during combat") - CmdFeed controlla davvero (ok, messaggio) invece
di ignorarli (bug preesistente: mostrava sempre "Nutri X con Y" anche
quando mangia()/bevi() rifiutavano, senza consumare l'oggetto).
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.sopravvivenza import mangia, bevi


class CmdEat(MuxCommand):
    """
    mangia qualcosa

    Uso:
      eat <oggetto>
      mangia <oggetto>
    """

    key = "eat"
    aliases = ["mangia"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Mangiare cosa?")
            return
        oggetto = caller.search(self.args, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{self.args}'.")
            return
        ok, messaggio = mangia(caller, oggetto)
        caller.msg(messaggio)


class CmdDrink(MuxCommand):
    """
    bevi qualcosa

    Uso:
      drink <oggetto>
      bevi <oggetto>
    """

    key = "drink"
    aliases = ["bevi"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Bere cosa?")
            return
        oggetto = caller.search(self.args, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{self.args}'.")
            return
        ok, messaggio = bevi(caller, oggetto)
        caller.msg(messaggio)


class CmdFeed(MuxCommand):
    """
    nutri forzatamente un altro personaggio

    Uso:
      feed <personaggio> <oggetto>
      nutri <personaggio> <oggetto>

    Funziona solo se il bersaglio ha attivato la ricezione forzata con
    FEEDME/ACCETTAFEED.
    """

    key = "feed"
    aliases = ["nutri"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        parti = self.args.split(None, 1) if self.args else []
        if len(parti) != 2:
            caller.msg("Uso: feed <personaggio> <oggetto>")
            return
        nome_bersaglio, nome_oggetto = parti

        bersaglio = caller.search(nome_bersaglio, quiet=True)
        bersaglio = bersaglio[0] if bersaglio else None
        if not bersaglio:
            caller.msg(f"Non vedi '{nome_bersaglio}' qui.")
            return
        if not bersaglio.db.accetta_feed:
            caller.msg(f"{bersaglio.key} non accetta di essere nutrito/a a forza.")
            return

        oggetto = caller.search(nome_oggetto, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{nome_oggetto}'.")
            return

        if oggetto.db.cibo:
            ok, messaggio = mangia(bersaglio, oggetto)
        elif oggetto.db.bevanda:
            ok, messaggio = bevi(bersaglio, oggetto)
        else:
            caller.msg(f"{oggetto.key} non e' ne' cibo ne' bevanda.")
            return

        if not ok:
            # Fase K, diciassettesima tornata: ok/messaggio da mangia()/bevi()
            # venivano ignorati - un feed su un bersaglio in combattimento (o
            # su qualunque altro rifiuto futuro) mostrava comunque "Nutri X
            # con Y" come se fosse riuscito, senza consumare davvero
            # l'oggetto: bug scoperto verificando la coerenza con la fonte
            # (helps/eat.txt, "not during combat").
            caller.msg(messaggio)
            return

        caller.msg(f"Nutri {bersaglio.key} con {oggetto.key}.")
        bersaglio.msg(f"{caller.key} ti nutre con {oggetto.key}.")


class CmdFeedMe(MuxCommand):
    """
    accetta o rifiuta di essere nutrito a forza da altri

    Uso:
      feedme
      accettafeed
    """

    key = "feedme"
    aliases = ["accettafeed"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.accetta_feed = not caller.db.accetta_feed
        stato = "ora accetti" if caller.db.accetta_feed else "non accetti piu'"
        caller.msg(f"{stato.capitalize()} di essere nutrito/a a forza da altri.")
