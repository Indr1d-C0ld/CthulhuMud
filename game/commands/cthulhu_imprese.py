"""
Comandi DEED e QUEST (Fase K, prima tornata): confermati dalla fonte
(helps/deed.txt = helps/quest.txt = helps/quests.txt - stessa pagina
"DEED / QUEST"). Sintassi della fonte: DEED, DEED <character>,
DEED BRAG <deed number>, QUEST.

QUEST START/COMPLETE <id> sono un'estensione nostra (la fonte descrive
solo QUEST come comando di sola lettura, poiche' l'avanzamento vero
avviene tramite MPQUEST lato mob/script - non replicato qui, vedi la
discussione con l'utente su mob programs in Fase H) - il modo piu'
diretto, dato che non abbiamo un motore di dialogo NPC generico, per
far avanzare le quest costruite in world/quest.py.
"""

from evennia import Command

from world.imprese import elenco_imprese, rendi_pubblica
from world.quest import (
    inizia_risveglio, completa_risveglio, QUEST_RISVEGLIO_ID,
    completa_quest_semplice, QUESTS_SEMPLICI,
)


def _numero_deed(deed_id):
    return deed_id.split("_", 1)[1] if "_" in deed_id else deed_id


class CmdDeed(Command):
    """
    mostra le imprese compiute da te o da un altro personaggio

    Uso:
      deed
      deed <personaggio>
      deed brag <numero>
    """

    key = "deed"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if args.lower().startswith("brag"):
            resto = args[4:].strip()
            if not resto.isdigit():
                caller.msg("Uso: deed brag <numero>")
                return
            ok, messaggio = rendi_pubblica(caller, f"deed_{resto}")
            caller.msg(messaggio)
            return

        if not args:
            voci = elenco_imprese(caller)
            if not voci:
                caller.msg("Non hai ancora compiuto imprese degne di nota.")
                return
            righe = [f"  #{_numero_deed(did):<6} {titolo}" for did, titolo, _, _ in voci]
            caller.msg("Le tue imprese:\n" + "\n".join(righe))
            return

        bersaglio = caller.search(args)
        if not bersaglio:
            return
        voci = elenco_imprese(bersaglio, per_altri=True)
        if not voci:
            caller.msg(f"{bersaglio.key} non ha imprese pubbliche note.")
            return
        righe = [f"  #{_numero_deed(did):<6} {titolo}" for did, titolo, _, _ in voci]
        caller.msg(f"Le imprese di {bersaglio.key}:\n" + "\n".join(righe))


class CmdQuest(Command):
    """
    mostra le quest in corso, o ne avvia/completa una

    Uso:
      quest
      quest start <id>
      quest complete <id>
    """

    key = "quest"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            progresso = caller.db.quest_progress or {}
            if not progresso:
                caller.msg("Non hai quest in corso.")
                return
            righe = [f"  {quest_id}: tappa {tappa}" for quest_id, tappa in progresso.items()]
            caller.msg("Le tue quest in corso:\n" + "\n".join(righe))
            return

        sotto, _, resto = args.partition(" ")
        sotto = sotto.lower()
        resto = resto.strip().lower()

        if sotto == "start" and resto == QUEST_RISVEGLIO_ID:
            _, messaggio = inizia_risveglio(caller)
            caller.msg(messaggio)
            return
        if sotto == "complete":
            if resto == QUEST_RISVEGLIO_ID:
                _, messaggio = completa_risveglio(caller)
                caller.msg(messaggio)
                return
            if resto in QUESTS_SEMPLICI:
                _, messaggio = completa_quest_semplice(caller, resto)
                caller.msg(messaggio)
                return

        caller.msg("Uso: quest | quest start <id> | quest complete <id>")
