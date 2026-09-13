"""
OPEN/CLOSE/LOCK/UNLOCK/PICK (Fase K, nona tornata): vedi world/porte.py
per le note sulla fonte e sulla semplificazione dichiarata (solo porte/
uscite, non contenitori - nessuno esiste ancora nel nostro mondo).

Confermato dalla fonte (helps/open.txt): "players must specify the
direction of the door, not its name" - qui i comandi accettano quindi
sempre e solo una direzione, mai un nome di stanza o di oggetto.
"""

from evennia import Command

from world.porte import trova_uscita, apri, chiudi, blocca, sblocca, tenta_scasso


class CmdOpenPorta(Command):
    """
    apri una porta

    Uso:
      open <direzione>
    """

    key = "open"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: open <direzione>")
            return
        uscita = trova_uscita(caller, self.args.strip())
        if not uscita:
            caller.msg("Non c'e' nessuna porta in quella direzione.")
            return
        ok, messaggio = apri(caller, uscita)
        if ok:
            caller.location.msg_contents(f"{caller.key} apre {uscita.key}.", exclude=[caller])
        caller.msg(messaggio)


class CmdClosePorta(Command):
    """
    chiudi una porta

    Uso:
      close <direzione>
    """

    key = "close"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: close <direzione>")
            return
        uscita = trova_uscita(caller, self.args.strip())
        if not uscita:
            caller.msg("Non c'e' nessuna porta in quella direzione.")
            return
        ok, messaggio = chiudi(caller, uscita)
        if ok:
            caller.location.msg_contents(f"{caller.key} chiude {uscita.key}.", exclude=[caller])
        caller.msg(messaggio)


class CmdLockPorta(Command):
    """
    chiudi a chiave una porta

    Uso:
      lock <direzione>

    Devi tenere in mano la chiave e la porta deve essere gia' chiusa.
    """

    key = "lock"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: lock <direzione>")
            return
        uscita = trova_uscita(caller, self.args.strip())
        if not uscita:
            caller.msg("Non c'e' nessuna porta in quella direzione.")
            return
        chiave = next((o for o in caller.contents if o.db.e_chiave), None)
        ok, messaggio = blocca(caller, uscita, chiave)
        caller.msg(messaggio)


class CmdUnlockPorta(Command):
    """
    apri la serratura di una porta

    Uso:
      unlock <direzione>

    Devi tenere in mano la chiave giusta.
    """

    key = "unlock"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: unlock <direzione>")
            return
        uscita = trova_uscita(caller, self.args.strip())
        if not uscita:
            caller.msg("Non c'e' nessuna porta in quella direzione.")
            return
        chiave = next((o for o in caller.contents if o.db.e_chiave and o.db.apre == uscita), None)
        ok, messaggio = sblocca(caller, uscita, chiave)
        caller.msg(messaggio)


class CmdPick(Command):
    """
    scassina una serratura senza chiave

    Uso:
      pick <direzione>

    Richiede la skill Scasso. STAND per interrompere il tentativo (non
    e' un'azione che si prolunga nel tempo in questo porting).
    """

    key = "pick"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: pick <direzione>")
            return
        uscita = trova_uscita(caller, self.args.strip())
        if not uscita:
            caller.msg("Non c'e' nessuna porta in quella direzione.")
            return
        ok, messaggio = tenta_scasso(caller, uscita)
        caller.msg(messaggio)
