"""
Armadietti (Fase F, decima tornata): come confermato dal sito originale,
un armadietto economico serve a tenere un set di scorta al sicuro (in
particolare equipaggiamento, nel caso quello indossato vada perso alla
morte - vedi world/combat.py).

Semplificazione dichiarata rispetto all'originale: la' gli armadietti
erano oggetti fisici in luoghi specifici del mondo, con una chiave da
comprare. Qui l'armadietto e' invece personale e disponibile ovunque
(un "deposito" astratto, come la banca per l'oro): niente
posizionamento fisico ne' oggetto-chiave, per restare nello scopo di
questa tornata.
Gli oggetti depositati vengono spostati fuori dal mondo di gioco
(location=None) e tracciati in Character.db.locker.
"""

from evennia.commands.default.muxcommand import MuxCommand

CAPACITA_ARMADIETTO = 20


class CmdLocker(MuxCommand):
    """
    gestisci il tuo armadietto personale

    Uso:
      locker
      locker store <oggetto>
      locker retrieve <oggetto>
      armadietto
      armadietto deposita <oggetto>
      armadietto preleva <oggetto>

    Un armadietto economico (disponibile ovunque tu sia) per tenere al
    sicuro un set di scorta: capacita' massima 20 oggetti.
    """

    key = "locker"
    aliases = ["armadietto"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        contenuto = caller.db.locker or []

        if not self.args:
            if not contenuto:
                caller.msg("Il tuo armadietto e' vuoto.")
            else:
                righe = [f"|wNel tuo armadietto ({len(contenuto)}/{CAPACITA_ARMADIETTO}):|n"]
                righe += [f"  {o.key}" for o in contenuto]
                caller.msg("\n".join(righe))
            return

        parti = self.args.split(None, 1)
        sottocomando = parti[0].lower()
        resto = parti[1] if len(parti) > 1 else ""

        if sottocomando in ("store", "deposita") and resto:
            self._deposita(caller, resto, contenuto)
        elif sottocomando in ("retrieve", "preleva") and resto:
            self._preleva(caller, resto, contenuto)
        else:
            caller.msg("Uso: locker store <oggetto> | locker retrieve <oggetto>")

    def _deposita(self, caller, oggetto_spec, contenuto):
        if len(contenuto) >= CAPACITA_ARMADIETTO:
            caller.msg(f"Il tuo armadietto e' pieno (massimo {CAPACITA_ARMADIETTO} oggetti).")
            return
        oggetto = caller.search(oggetto_spec, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{oggetto_spec}'.")
            return
        if oggetto.db.indossato:
            caller.msg(f"Devi prima togliere {oggetto.key}.")
            return

        oggetto.move_to(None, quiet=True, to_none=True)
        contenuto.append(oggetto)
        caller.db.locker = contenuto
        caller.msg(f"Depositi {oggetto.key} nell'armadietto.")

    def _preleva(self, caller, oggetto_spec, contenuto):
        oggetto = caller.search(oggetto_spec, location=None, candidates=contenuto, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{oggetto_spec}' nell'armadietto.")
            return

        contenuto.remove(oggetto)
        caller.db.locker = contenuto
        oggetto.move_to(caller, quiet=True, move_type="get")
        caller.msg(f"Prelevi {oggetto.key} dall'armadietto.")
