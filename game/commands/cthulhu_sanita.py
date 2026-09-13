"""
Comandi di recupero sanity (Fase G, sesta tornata): therapy/terapia,
psychology/psicologia. Vedi world/sanita.py per la logica e le
citazioni della fonte originale.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.sanita import (
    terapia_disponibile, TRATTAMENTI_THERAPY, esegui_therapy, esegui_psychology,
)


class CmdTherapy(MuxCommand):
    """
    recupera sanity da un terapeuta, a pagamento

    Uso:
      therapy
      therapy <trattamento>
      terapia
      terapia <trattamento>

    Senza argomenti, mostra i trattamenti disponibili e il costo. Il
    risultato non e' garantito: il terapeuta non rimborsa se fallisce.
    """

    key = "therapy"
    aliases = ["terapia"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        terapeuti = terapia_disponibile(caller.location)
        if not terapeuti:
            caller.msg("Non c'e' nessun terapeuta qui.")
            return
        terapeuta = terapeuti[0]

        if not self.args:
            righe = [f"|w{terapeuta.key} offre:|n"]
            for tid, (nome, costo, recupero_max) in TRATTAMENTI_THERAPY.items():
                righe.append(f"  {tid:<12s} {nome:<30s} {costo} oro (fino a {recupero_max} sanity)")
            caller.msg("\n".join(righe))
            return

        ok, messaggio = esegui_therapy(caller, terapeuta, self.args.strip().lower())
        caller.msg(messaggio)


class CmdPsychology(MuxCommand):
    """
    aiuta un altro personaggio a recuperare sanity (skill Psicologia)

    Uso:
      psychology <personaggio>
      psicologia <personaggio>

    Costa 300 movimento e puo' ritorcersi contro chi la usa.
    """

    key = "psychology"
    aliases = ["psicologia"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: psychology <personaggio>")
            return
        bersaglio = caller.search(self.args, quiet=True)
        bersaglio = bersaglio[0] if bersaglio else None
        if not bersaglio:
            caller.msg(f"Non vedi '{self.args}' qui.")
            return
        ok, messaggio = esegui_psychology(caller, bersaglio)
        caller.msg(messaggio)
