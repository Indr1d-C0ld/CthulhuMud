"""
FOLLOW/GROUP (Fase K, tredicesima tornata): vedi world/gruppo.py per le
note sulla fonte e sulle scelte di design.
"""

from evennia import Command

from world.gruppo import (
    tenta_follow, tenta_nofollow, tenta_group, gtell, dividi_oro,
)


class CmdFollow(Command):
    """
    segui un altro personaggio

    Uso:
      follow <personaggio>
      follow me

    Ti mette al seguito di un altro personaggio, spostandoti con lui/lei
    da una stanza all'altra. FOLLOW ME (o te stesso/a) per smettere.
    """

    key = "follow"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        ok, messaggio = tenta_follow(caller, self.args.strip())
        if messaggio:
            caller.msg(messaggio)


class CmdNofollow(Command):
    """
    rifiuta nuovi seguaci, o allontana chi ti segue

    Uso:
      nofollow
      nofollow <personaggio>

    Senza argomenti, alterna se accetti o meno nuovi FOLLOW su di te
    (congedando anche chi gia' ti segue). Con un nome, allontana solo
    quel seguace.
    """

    key = "nofollow"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        ok, messaggio = tenta_nofollow(caller, self.args.strip())
        if messaggio:
            caller.msg(messaggio)


class CmdGroup(Command):
    """
    gestisci il tuo gruppo

    Uso:
      group
      group <personaggio>

    Senza argomenti, mostra chi fa parte del tuo gruppo. Con un nome,
    aggiunge al gruppo un personaggio che ti sta gia' seguendo, o lo
    espelle se ne fa gia' parte.
    """

    key = "group"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        ok, messaggio = tenta_group(caller, self.args.strip())
        if messaggio:
            caller.msg(messaggio)


class CmdGtell(Command):
    """
    parla con il tuo gruppo

    Uso:
      gtell <messaggio>
    """

    key = "gtell"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: gtell <messaggio>")
            return
        ok, messaggio = gtell(caller, self.args.strip())
        if messaggio:
            caller.msg(messaggio)


class CmdSplit(Command):
    """
    dividi il tuo oro con il gruppo

    Uso:
      split
    """

    key = "split"
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        ok, messaggio = dividi_oro(caller)
        caller.msg(messaggio)


class CmdAutosplit(Command):
    """
    alterna la divisione automatica del bottino nel gruppo

    Uso:
      autosplit
    """

    key = "autosplit"
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.autosplit = not caller.db.autosplit
        stato = "attivo" if caller.db.autosplit else "disattivo"
        caller.msg(f"Autosplit ora {stato}.")


class CmdAutoassist(Command):
    """
    alterna l'assistenza automatica ai compagni di gruppo

    Uso:
      autoassist
    """

    key = "autoassist"
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.autoassist = not caller.db.autoassist
        stato = "attivo" if caller.db.autoassist else "disattivo"
        caller.msg(f"Autoassist ora {stato}.")
