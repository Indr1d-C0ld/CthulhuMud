"""
Comando ED (Fase I, prima tornata): equivalente builder-facing del
comando della fonte per gestire gli "oggetti di scena" (dettagli
d'arredo esaminabili ma non raccoglibili - vedi world/scenografia.py).
Confermato dalla fonte (immhelp_roombuilding.txt): "ED ADD/CHANGE/SHOW/
EDIT/DELETE". Qui semplificato ad ADD/LIST/DELETE - nessuna delle
nostre stanze usa condizioni o deed sugli ED (ED COND/DEED/FORMAT della
fonte), quindi non sono stati implementati.
"""

from evennia import Command

from world.scenografia import aggiungi_ed, rimuovi_ed, elenca_eds


class CmdED(Command):
    """
    aggiunge/rimuove/elenca gli oggetti di scena della stanza corrente

    Uso:
      ed list
      ed add <parola1>,<parola2>,... = <testo>
      ed delete <parola>

    Riservato ai builder. Un oggetto di scena e' un dettaglio d'arredo
    esaminabile con LOOK/EXAMINE <parola> ma non un vero oggetto.
    """

    key = "ed"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        stanza = caller.location
        if not stanza:
            caller.msg("Non hai una posizione.")
            return

        args = self.args.strip()
        if not args or args.split()[0].lower() == "list":
            voci = elenca_eds(stanza)
            if not voci:
                caller.msg("Nessun oggetto di scena in questa stanza.")
                return
            righe = [
                f"- {'/'.join(parole)}: {testo[:60]}{'...' if len(testo) > 60 else ''}"
                for parole, testo in voci
            ]
            caller.msg("Oggetti di scena:\n" + "\n".join(righe))
            return

        sotto, _, resto = args.partition(" ")
        sotto = sotto.lower()

        if sotto == "add":
            if "=" not in resto:
                caller.msg("Uso: ed add <parola1>,<parola2>,... = <testo>")
                return
            parole_str, _, testo = resto.partition("=")
            parole = [p.strip() for p in parole_str.split(",") if p.strip()]
            testo = testo.strip()
            if not parole or not testo:
                caller.msg("Uso: ed add <parola1>,<parola2>,... = <testo>")
                return
            aggiungi_ed(stanza, parole, testo)
            caller.msg(f"Oggetto di scena aggiunto: {'/'.join(parole)}.")
            return

        if sotto == "delete":
            parola = resto.strip()
            if not parola:
                caller.msg("Uso: ed delete <parola>")
                return
            if rimuovi_ed(stanza, parola):
                caller.msg(f"Oggetto di scena '{parola}' rimosso.")
            else:
                caller.msg(f"Nessun oggetto di scena con la parola '{parola}'.")
            return

        caller.msg("Uso: ed list | ed add <parole> = <testo> | ed delete <parola>")
