"""
Comandi WORSHIP/SACRIFICE (Fase K, ventisettesima tornata). Vedi
world/worship.py per la logica e le citazioni della fonte originale.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.worship import DIVINITA, nome_divinita, adora, sacrifica, info_divinita


class CmdWorship(MuxCommand):
    """
    scegli o consulta la divinita' che adori

    Uso:
      worship
      worship <divinita>
      worship info <divinita>

    Senza argomenti, elenca le divinita' disponibili e il loro
    allineamento. Con un nome, cambia la tua fede (azzera la pieta'
    accumulata con la divinita' precedente).
    """

    key = "worship"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip() if self.args else ""

        if not args:
            righe = ["Divinita' che si possono adorare:"]
            for did, dati in DIVINITA.items():
                righe.append(f"  {dati['nome']} (allineamento {dati['allineamento']:+d})")
            caller.msg("\n".join(righe))
            return

        parti = args.split(None, 1)
        if parti[0].lower() == "info" and len(parti) == 2:
            did = self._trova(parti[1])
            if not did:
                caller.msg("Divinita' sconosciuta.")
                return
            caller.msg(info_divinita(did))
            return

        did = self._trova(args)
        if not did:
            caller.msg("Divinita' sconosciuta. Usa WORSHIP per vedere l'elenco.")
            return
        ok, messaggio = adora(caller, did)
        caller.msg(messaggio)

    def _trova(self, nome):
        nome = nome.strip().lower().replace(" ", "_").replace("-", "_")
        if nome in DIVINITA:
            return nome
        for did, dati in DIVINITA.items():
            if nome == dati["nome"].lower().replace("-", "_"):
                return did
        return None


class CmdSacrifice(MuxCommand):
    """
    sacrifica un oggetto alla divinita' che adori

    Uso:
      sacrifice <oggetto>
      sacrifice all

    Confermato dalla fonte (helps/sacrifice.txt): non richiede un
    altare, a differenza di OFFER. Oggetti piu' preziosi aumentano di
    piu' la tua pieta' e hanno una piccola possibilita' di guadagnarti
    una ricompensa, se la tua divinita' apprezza il gesto.
    """

    key = "sacrifice"
    aliases = ["sacrifica"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: sacrifice <oggetto> | sacrifice all")
            return

        testo = self.args.strip()
        if testo.lower() in ("all", "tutto"):
            oggetti = list(caller.contents)
            if not oggetti:
                caller.msg("Non hai nulla da sacrificare.")
                return
            for oggetto in oggetti:
                ok, messaggio = sacrifica(caller, oggetto)
                if not ok:
                    caller.msg(messaggio)
                    return
                caller.msg(messaggio)
            return

        oggetto = caller.search(testo, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{testo}'.")
            return
        ok, messaggio = sacrifica(caller, oggetto)
        caller.msg(messaggio)
