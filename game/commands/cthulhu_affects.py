"""
AFFECTS/RAFFECTS (Fase K, nona tornata): confermati dalla fonte
(helps/raffects.txt, pagina unica per entrambi i comandi). AFFECTS elenca
i modificatori temporanei attivi sul personaggio (incantesimi, veleno,
malattia, ecc.); RAFFECTS fa lo stesso per la stanza/area attuale (es.
no_morgue - vedi world/combat.py:_morte_personaggio). Fino a questa
tornata non esisteva alcun modo per il giocatore di vedere i propri
stati/buff attivi, nonostante il sistema (world/effetti.py, Fase K sesta
tornata) li gestisse gia' tutti con una scadenza reale.

Implementazione generica: legge direttamente gli Script di scadenza gia'
esistenti (StatoScadenzaScript/SottorazzaBuffExpireScript/
EffettoPeriodicoScript) invece di mantenere un registro parallelo -
qualunque nuovo incantesimo che li riusa appare automaticamente qui senza
bisogno di aggiungere nulla apposta.
"""

from evennia import Command

_NOMI_STATI = {
    "cieco": "Accecato/a",
    "muto": "Ammutolito/a",
    "addormentato": "Addormentato/a",
    "impaurito": "Impaurito/a",
    "vede_invisibile": "Vede l'Invisibile",
    "assorbe_magia": "Assorbimento Magico",
    "allucinato": "Allucinato/a",
    "vocalizzato": "Vocalizzo",
    "attraversa_porte": "Attraversa le Porte",
    "duello_magico": "In Duello Magico",
    "astrale": "Corpo Astrale",
    "trance": "Trance",
    "mortalizzato": "Mortalizzato/a",
    "anima_protetta": "Guardia dell'Anima",
    "ascetismo": "Ascetismo",
    "rilassato": "Rilassato/a",
}

_NOMI_CAMPI = {
    "bonus_ca_temp": "Classe Armatura",
    "bonus_danno_temp": "Danno in Combattimento",
    "bonus_colpire": "Precisione",
    "riduzione_danno_temp": "Resistenza al Danno Fisico",
    "riduzione_danno_magico_temp": "Resistenza al Danno Magico",
    "mod_temp_str": "Forza", "mod_temp_int": "Intelligenza", "mod_temp_wis": "Saggezza",
    "mod_temp_dex": "Destrezza", "mod_temp_con": "Costituzione",
    "mod_temp_luck": "Fortuna", "mod_temp_cha": "Carisma",
}

_NOMI_CAMPI_BOOL = {
    "invisibile": "Invisibilita'",
}


def _tempo_leggibile(secondi):
    secondi = max(0, int(secondi))
    if secondi < 60:
        return f"{secondi}s"
    return f"{secondi // 60}m{secondi % 60:02d}s"


class CmdAffects(Command):
    """
    mostra i modificatori temporanei attivi sul tuo personaggio

    Uso:
      affects

    Elenca incantesimi, veleni, malattie e altri effetti che ti stanno
    influenzando in questo momento, con il tempo restante quando
    disponibile.
    """

    key = "affects"
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        righe = []

        for stato in sorted((caller.db.stati or {}).keys()):
            nome = _NOMI_STATI.get(stato, stato.replace("_", " ").capitalize())
            righe.append(f"  {nome}")

        # Nota tecnica (Fase K, nona tornata): il .key di questi script viene
        # sempre sovrascritto al momento della creazione (es. key=f"buff_
        # {campo}", key=f"stato_{stato}") - identificarli per TIPO
        # (is_typeclass) invece che per .key, che qui non e' affidabile.
        for script in caller.scripts.all():
            if script.is_typeclass("typeclasses.scripts.SottorazzaBuffExpireScript", exact=False):
                campo = script.db.campo
                nome = _NOMI_CAMPI.get(campo, campo)
                resto = _tempo_leggibile(script.time_until_next_repeat() or 0)
                righe.append(f"  {nome} (scade tra {resto})")
            elif script.is_typeclass("typeclasses.scripts.StatoScadenzaScript", exact=False) and script.db.campo_bool:
                nome = _NOMI_CAMPI_BOOL.get(script.db.campo_bool, script.db.campo_bool)
                resto = _tempo_leggibile(script.time_until_next_repeat() or 0)
                righe.append(f"  {nome} (scade tra {resto})")
            elif script.is_typeclass("typeclasses.scripts.EffettoPeriodicoScript", exact=False):
                stato = script.db.stato
                nome = _NOMI_STATI.get(stato, stato.replace("_", " ").capitalize() if stato else "Effetto periodico")
                rimasti = (script.db.tick_totali or 0) - (script.db.tick_fatti or 0)
                righe.append(f"  {nome} ({rimasti} colpi rimasti)")

        if not righe:
            caller.msg("Non hai alcun effetto attivo al momento.")
            return
        caller.msg("Effetti attivi su di te:\n" + "\n".join(righe))


_FLAG_STANZA = {
    "no_morgue": "no_morgue (i cadaveri restano dove si muore, invece di finire in morgue)",
}


class CmdRaffects(Command):
    """
    mostra gli effetti/flag attivi sulla stanza attuale

    Uso:
      raffects

    Elenca le proprieta' speciali della stanza in cui ti trovi, come
    no_morgue.
    """

    key = "raffects"
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        stanza = caller.location
        if not stanza:
            caller.msg("Non sei da nessuna parte.")
            return
        righe = [
            descrizione for campo, descrizione in _FLAG_STANZA.items()
            if getattr(stanza.db, campo, False)
        ]
        if not righe:
            caller.msg("Questa stanza non ha effetti speciali attivi.")
            return
        caller.msg("Effetti attivi su questa stanza:\n  " + "\n  ".join(righe))
