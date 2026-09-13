"""
Comando REMORT (Fase K, nona tornata): vedi world/remort.py per le note
sulla fonte e sulle scelte di design. Confermato come comando IMMORTAL,
non self-service (helps/remort2.txt) - stesso pattern gia' usato per
SUBRACE (commands/cthulhu_sottorazze.py).
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.remort import remort


class CmdRemort(MuxCommand):
    """
    (staff) remorta un personaggio che ha raggiunto il livello richiesto

    Uso:
      remort <personaggio>

    Riporta il personaggio al livello 3, dimezzandone HP/mana/movimento
    massimi, intaccando leggermente qualche skill a caso, ma mantenendo
    oro/equipaggiamento/clan e sbloccando l'accesso al canale REMTALK.
    Disconnette la sessione del giocatore al termine: come da fonte, alla
    riconnessione il personaggio si ritrova di nuovo al livello 3.
    """

    key = "remort"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: remort <personaggio>")
            return
        bersaglio = caller.search(self.args.strip())
        if not bersaglio:
            return
        ok, messaggio = remort(bersaglio)
        caller.msg(messaggio)
        if not ok:
            return
        bersaglio.msg(
            "|mQualcosa dentro di te si spezza e si riforma: la tua carriera ricomincia, "
            "piu' leggera ma non da zero. Sarai disconnesso/a a breve.|n"
        )
        account = bersaglio.account
        if account:
            for sessione in list(account.sessions.all()):
                sessione.msg("Il processo di remort e' completo. Riconnettiti per continuare.")
                account.disconnect_session_from_account(sessione)
