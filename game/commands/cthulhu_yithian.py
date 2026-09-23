"""
Comandi Yithiani (Fase G, nona tornata): MINDTRANSFER, RETURN, YITH
ADAPT, YITH ABDUCT. Vedi world/yithian.py per la logica e le citazioni
della fonte originale (guides_yithianfaq.txt).
"""

import random

from evennia.commands.default.muxcommand import MuxCommand

from world.yithian import (
    costo_mindtransfer, possibilita_successo_mindtransfer, puo_adattare,
)


class CmdMindtransfer(MuxCommand):
    """
    sposta la tua mente Yithiana nel corpo di un NPC

    Uso:
      mindtransfer <npc>

    Solo per personaggi Yithiani. Costa mana E movimento, entrambi pari
    a 10 volte il livello dell'NPC. Molto difficile (quasi impossibile)
    su un NPC di livello superiore al tuo; se fallisci contro un NPC
    piu' forte, l'NPC si risveglia ostile e ti attacca. Il tuo corpo
    Yithiano originale resta immobile finche' non usi RETURN.
    """

    key = "mindtransfer"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if caller.db.race != "yithian":
            caller.msg("Solo uno Yithiano puo' usare MINDTRANSFER.")
            return
        if not self.args:
            caller.msg("Uso: mindtransfer <npc>")
            return
        npc = caller.search(self.args, quiet=True)
        npc = npc[0] if npc else None
        if not npc or not npc.is_typeclass("typeclasses.npcs.NPC", exact=False):
            caller.msg("Bersaglio non valido.")
            return
        if npc.db.yithian_originale or npc.account:
            caller.msg(f"{npc.key} e' gia' occupato/a da qualcun altro.")
            return
        # NPC di servizio (NPC.intoccabile): possederli li porterebbe via dal loro
        # posto (e YITHABDUCT fino alla Biblioteca Yithiana)
        from world.pk import e_intoccabile, messaggio_intoccabile
        if e_intoccabile(npc):
            caller.msg(messaggio_intoccabile(npc))
            return

        costo = costo_mindtransfer(npc)
        if (caller.db.mana or 0) < costo or (caller.db.move or 0) < costo:
            caller.msg(f"Ti servono {costo} mana e {costo} movimento per tentare il trasferimento.")
            return
        caller.db.mana -= costo
        caller.db.move -= costo

        percentuale = possibilita_successo_mindtransfer(caller, npc)
        if random.uniform(0, 100) > percentuale:
            caller.msg(f"Il tentativo di possedere {npc.key} fallisce.")
            if npc.livello_per_equip() > caller.livello_per_equip():
                npc.db.ostile = True
                caller.location.msg_contents(
                    f"{npc.key} si risveglia furioso/a e attacca {caller.key}!"
                )
                npc.avvia_combattimento(caller)
            return

        sessioni = caller.sessions.get()
        if not sessioni:
            caller.msg("Errore interno: nessuna sessione attiva.")
            return
        account = caller.account

        npc.db.yithian_originale = caller
        npc.locks.add(f"puppet:id({account.id}) or perm(Developer)")
        # world/quest.py: impresa deed_83 ("Andato oltre le frontiere
        # della natura umana") - basta averlo fatto una volta.
        caller.db.ha_mindtransferito = True
        caller.msg(
            f"La tua mente scivola nel corpo di {npc.key}. Il tuo corpo Yithiano "
            "resta immobile e privo di sensi finche' non torni."
        )
        account.puppet_object(sessioni[0], npc)


class CmdReturn(MuxCommand):
    """
    torna al tuo corpo Yithiano originale, o al tuo corpo fisico se sei
    in astrale

    Uso:
      return

    Confermato dalla fonte anche per l'incantesimo Cammino Astrale
    (helps/astral_walk.txt: per tornare al proprio corpo fisico si usa
    il comando RETURN) - stesso comando gia' usato per MINDTRANSFER
    (Fase G, terza tornata), qui esteso a gestire anche il secondo caso
    invece di crearne uno nuovo in conflitto. Fase K, ventesima tornata:
    esteso ancora per lo staff che ha usato SWITCH
    (commands/cthulhu_staff.py) - helps/switch.txt conferma che RETURN
    si usa anche per tornare al proprio corpo dopo uno SWITCH.
    """

    key = "return"
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        from world.effetti import ha_stato, rimuovi_stato
        if ha_stato(caller, "astrale"):
            rimuovi_stato(caller, "astrale")
            caller.msg("|mLa tua mente rientra bruscamente nel tuo corpo fisico.|n")
            return
        proprietario_switch = caller.db.switchato_da
        if proprietario_switch:
            sessioni = caller.sessions.get()
            if not sessioni:
                caller.msg("Errore interno: nessuna sessione attiva.")
                return
            account = caller.account
            caller.attributes.remove("switchato_da")
            caller.locks.add("puppet:false()")
            account.puppet_object(sessioni[0], proprietario_switch)
            proprietario_switch.msg(f"Torni al tuo corpo, lasciando {caller.key}.")
            return
        yithiano = caller.db.yithian_originale
        if not yithiano:
            caller.msg("Non stai possedendo nessun corpo, ne' vagando in astrale.")
            return
        sessioni = caller.sessions.get()
        if not sessioni:
            caller.msg("Errore interno: nessuna sessione attiva.")
            return
        account = caller.account
        veicolo = caller

        veicolo.db.yithian_originale = None
        account.puppet_object(sessioni[0], yithiano)
        veicolo.locks.add("puppet:false()")
        yithiano.msg("La tua mente torna al tuo corpo Yithiano.")


class CmdYithAdapt(MuxCommand):
    """
    adatta al tuo corpo Yithiano una skill dell'NPC che possiedi

    Uso:
      yith adapt
      yith adapt <skill> [volte]

    Disponibile solo mentre possiedi un NPC (MINDTRANSFER). Spende le
    practice del tuo corpo Yithiano, non quelle del veicolo. Il rating
    di base e' la media tra il tuo e quello dell'NPC in quella skill,
    modificato dalla media del vostro rating in Insegnamento; solo le
    skill con un rating finale sopra il 25% compaiono nella lista.
    """

    key = "yith"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        yithiano = caller.db.yithian_originale
        if not yithiano:
            caller.msg("Devi possedere un NPC (MINDTRANSFER) per usare questo comando.")
            return
        parti = self.args.split() if self.args else []
        if not parti or parti[0].lower() != "adapt":
            caller.msg("Uso: yith adapt [skill] [volte]")
            return
        resto = parti[1:]

        skill_npc = caller.db.skills or {}
        skill_yithian = yithiano.db.skills or {}
        teach_npc = skill_npc.get("teach", 0)
        teach_yithian = skill_yithian.get("teach", 0)

        if not resto:
            righe = ["Skill adattabili da questo NPC:"]
            from world.skills import nome_skill
            for skill_id, rating_npc in skill_npc.items():
                rating_yithian = skill_yithian.get(skill_id, 0)
                finale = puo_adattare(rating_npc, rating_yithian, teach_npc, teach_yithian)
                if finale is not None:
                    righe.append(f"  {nome_skill(skill_id)}: {finale:.0f}%")
            if len(righe) == 1:
                righe.append("  (nessuna, per ora - serve piu' Insegnamento da una parte o dall'altra)")
            caller.msg("\n".join(righe))
            return

        skill_id = resto[0].lower()
        volte = int(resto[1]) if len(resto) > 1 and resto[1].isdigit() else 1

        if skill_id not in skill_npc:
            caller.msg(f"{caller.key} non conosce questa skill.")
            return
        finale = puo_adattare(skill_npc[skill_id], skill_yithian.get(skill_id, 0), teach_npc, teach_yithian)
        if finale is None:
            caller.msg("Questa skill non e' ancora adattabile (serve piu' Insegnamento).")
            return

        from world.skills import nome_skill
        speso = 0
        for _ in range(volte):
            if (yithiano.db.practices or 0) < 1:
                break
            attuale = skill_yithian.get(skill_id, 0)
            if attuale >= finale:
                break
            yithiano.db.practices -= 1
            guadagno = min(int(finale) - attuale, random.randint(3, 8))
            skill_yithian[skill_id] = attuale + max(1, guadagno)
            speso += 1
        yithiano.db.skills = skill_yithian

        if speso == 0:
            caller.msg("Non hai potuto adattare nulla (practice esaurite o gia' al limite).")
        else:
            caller.msg(
                f"Il tuo corpo Yithiano adatta {nome_skill(skill_id)}: ora al "
                f"{skill_yithian[skill_id]}% (speso {speso} practice)."
            )


class CmdYithAbduct(MuxCommand):
    """
    trasporta l'NPC che possiedi alla Biblioteca Yithiana

    Uso:
      yithabduct
    """

    key = "yithabduct"
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        if not caller.db.yithian_originale:
            caller.msg("Devi possedere un NPC (MINDTRANSFER) per usare questo comando.")
            return
        from world.rooms_newbie import stanza_per_ruolo

        destinazione = stanza_per_ruolo("yithian_library", "respawn")
        if not destinazione:
            caller.msg("La Biblioteca Yithiana non e' ancora stata costruita.")
            return
        caller.location.msg_contents(f"{caller.key} svanisce in un lampo di luce.", exclude=caller)
        caller.move_to(destinazione, quiet=True)
        caller.msg("Vieni trasportato/a nella Biblioteca Yithiana.")
        caller.execute_cmd("look")
