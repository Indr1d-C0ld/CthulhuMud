"""
Comando MONEY/WORTH (Fase K, ventisettesima tornata). Vedi
world/valute.py per la logica e le citazioni della fonte originale.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.valute import NOMI_VALUTE, saldo


class CmdMoney(MuxCommand):
    """
    mostra tutto il denaro che possiedi, in ogni valuta

    Uso:
      money
      worth

    Confermato dalla fonte (helps/money.txt): la scheda personaggio
    (SCORE) mostra solo la valuta di default della zona in cui ti
    trovi - usa questo comando per vedere il totale completo.
    """

    key = "money"
    aliases = ["worth"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        righe = ["Il tuo denaro:"]
        for valuta_id, nome in NOMI_VALUTE.items():
            righe.append(f"  {nome}: {saldo(caller, valuta_id)}")
        caller.msg("\n".join(righe))
