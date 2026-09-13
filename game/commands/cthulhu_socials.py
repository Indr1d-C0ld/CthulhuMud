"""
Comandi social (Fase G, undicesima tornata, esteso in Fase J): un
comando per ogni voce di world/socials.py, generato dinamicamente,
piu' CmdGender per impostare il genere usato nei messaggi in terza
persona.

I social con "vietato_newbie": True (categoria "sessuale" della fonte:
"their use is slightly restricted in that newbies cannot use them") non
sono utilizzabili da chi ha ancora una professione newbie attiva.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.socials import SOCIALS, esegui_social


def _e_newbie(personaggio):
    from world.professions_newbie import NEWBIE_PROFESSIONS

    return (personaggio.db.active_profession or None) in NEWBIE_PROFESSIONS


def _crea_comando_social(social_id):
    """Fabbrica di comandi: una classe MuxCommand per ogni social."""

    class CmdSocialGenerico(MuxCommand):
        __doc__ = f"emote sociale: {social_id}\n\nUso:\n  {social_id} [bersaglio]"
        key = social_id
        locks = "cmd:all()"

        def func(self):
            caller = self.caller
            dati = SOCIALS.get(self.key, {})
            if dati.get("vietato_newbie") and _e_newbie(caller):
                caller.msg(f"{self.key.upper()} non e' disponibile per i personaggi newbie.")
                return
            bersaglio = None
            if self.args:
                trovato = caller.search(self.args.strip(), quiet=True)
                bersaglio = trovato[0] if trovato else None
                if not bersaglio:
                    caller.msg(f"Non vedi '{self.args.strip()}' qui.")
                    return
            ok, messaggio = esegui_social(caller, self.key, bersaglio)
            if not ok:
                caller.msg(messaggio)

    CmdSocialGenerico.__name__ = f"CmdSocial_{social_id}"
    return CmdSocialGenerico


COMANDI_SOCIAL = [_crea_comando_social(social_id) for social_id in SOCIALS]


class CmdGender(MuxCommand):
    """
    imposta il genere usato nei messaggi in terza persona

    Uso:
      gender m
      gender f
    """

    key = "gender"
    aliases = ["genere"]
    locks = "cmd:all()"

    def func(self):
        arg = self.args.strip().lower() if self.args else ""
        if arg not in ("m", "f"):
            caller_genere = self.caller.db.genere or "m"
            self.msg(f"Genere attuale: {caller_genere}. Uso: gender m|f")
            return
        self.caller.db.genere = arg
        self.msg(f"Genere impostato a '{arg}'.")
