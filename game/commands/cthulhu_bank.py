"""
Sistema bancario (Fase F, settima tornata): deposita/preleva oro in
una delle banche di Arkham. Non e' documentato da nessuna fonte
originale reperita finora (vedi nota in world/economia.py) - e' una
convenzione quasi universale nei MUD derivati da Diku, qui giustificata
anche dal fatto che la skill "Furto" (world/skills.py: "steal") esiste
gia' nel catalogo skill assegnato ad alcune professioni: l'oro in banca
e' al sicuro da eventuali furti da altri giocatori, a differenza di
quello portato addosso. Non protegge dalla morte, perche' il sito
originale conferma che non si perde MAI denaro morendo.

Il saldo in banca vive su Character.db.banca (Oro depositato),
separato da Character.db.gold (Oro portato addosso, gia' esistente).

Confermato dal sito originale ("accounts earn a little interest each
month"): vedi world/banca.py e typeclasses/scripts.py
(InteresseBancarioScript) per l'interesse periodico applicato qui sopra.
"""

from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils import search

from world.valute import NOMI_VALUTE, cambia_valuta

BANCHE_TAGS = ("building_first_bank", "building_second_bank")

# Fase K, ventisettesima tornata: helps/money.txt - "You can change one
# currency to another at a bank... the exact exchange rate will vary
# from location to location." Nessun numero dalla fonte: qui un tasso
# 1:1 unico e dichiarato per ogni coppia, invece di inventare 20 tassi
# diversi senza alcun indizio su quali dovrebbero essere piu' o meno
# favorevoli.
TASSO_CAMBIO_DICHIARATO = 1.0


def _in_banca(stanza):
    if not stanza:
        return False
    for tag in BANCHE_TAGS:
        if stanza.tags.get(tag, category="arkham_building"):
            return True
    return False


class CmdDeposit(MuxCommand):
    """
    deposita oro in banca

    Uso:
      deposit <quantita>
      deposita <quantita>

    Deposita l'oro indicato nel tuo conto in banca. Funziona solo se
    ti trovi in una banca. L'oro depositato e' al sicuro da eventuali
    furti - la morte invece non fa mai perdere denaro, in banca o no.
    """

    key = "deposit"
    aliases = ["deposita"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not _in_banca(caller.location):
            caller.msg("Non sei in una banca.")
            return
        if not self.args or not self.args.strip().isdigit():
            caller.msg("Uso: deposit <quantita>")
            return

        quantita = int(self.args.strip())
        oro = caller.db.gold or 0
        if quantita <= 0:
            caller.msg("Devi indicare una quantita' positiva.")
            return
        if quantita > oro:
            caller.msg(f"Non hai {quantita} oro con te (ne hai {oro}).")
            return

        caller.db.gold = oro - quantita
        caller.db.banca = (caller.db.banca or 0) + quantita
        caller.msg(
            f"Depositi {quantita} oro. Saldo in banca: {caller.db.banca} oro "
            f"(oro con te: {caller.db.gold})."
        )


class CmdWithdraw(MuxCommand):
    """
    preleva oro dalla banca

    Uso:
      withdraw <quantita>
      preleva <quantita>

    Preleva l'oro indicato dal tuo conto in banca. Funziona solo se ti
    trovi in una banca.
    """

    key = "withdraw"
    aliases = ["preleva"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not _in_banca(caller.location):
            caller.msg("Non sei in una banca.")
            return
        if not self.args or not self.args.strip().isdigit():
            caller.msg("Uso: withdraw <quantita>")
            return

        quantita = int(self.args.strip())
        banca = caller.db.banca or 0
        if quantita <= 0:
            caller.msg("Devi indicare una quantita' positiva.")
            return
        if quantita > banca:
            caller.msg(f"Non hai {quantita} oro in banca (ne hai {banca}).")
            return

        caller.db.banca = banca - quantita
        caller.db.gold = (caller.db.gold or 0) + quantita
        caller.msg(
            f"Prelevi {quantita} oro. Oro con te: {caller.db.gold} "
            f"(saldo in banca: {caller.db.banca})."
        )


class CmdBalance(MuxCommand):
    """
    mostra il tuo saldo in banca e l'oro che porti con te

    Uso:
      balance
      saldo
    """

    key = "balance"
    aliases = ["saldo"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        caller.msg(
            f"Oro con te: {caller.db.gold or 0}\n"
            f"Oro in banca: {caller.db.banca or 0}"
        )


class CmdExchange(MuxCommand):
    """
    cambia una valuta in un'altra, in banca

    Uso:
      exchange <quantita> <valuta_da> <valuta_a>
      cambia <quantita> <valuta_da> <valuta_a>

    Esempio: exchange 50 dollari oro
    Funziona solo se ti trovi in una banca. La fonte (helps/money.txt)
    prevede che non tutte le banche accettino tutte le valute; per
    semplicita' qui tutte le banche gia' costruite le accettano tutte.
    """

    key = "exchange"
    aliases = ["cambia"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not _in_banca(caller.location):
            caller.msg("Non sei in una banca.")
            return
        parti = self.args.split() if self.args else []
        if len(parti) != 3 or not parti[0].isdigit():
            caller.msg("Uso: exchange <quantita> <valuta_da> <valuta_a>")
            return
        quantita = int(parti[0])
        valuta_da = parti[1].lower()
        valuta_a = parti[2].lower()
        if valuta_da not in NOMI_VALUTE or valuta_a not in NOMI_VALUTE:
            caller.msg(f"Valute disponibili: {', '.join(NOMI_VALUTE.values())}")
            return
        ok, messaggio = cambia_valuta(caller, valuta_da, valuta_a, quantita, TASSO_CAMBIO_DICHIARATO)
        caller.msg(messaggio)
