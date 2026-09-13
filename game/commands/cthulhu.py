"""
Comandi di base di CthulhuMUD ITA Redux (M2): SCORE, TRAIN, PRACTICE,
LEARN, DEBATE, PROF LIST/CHANGE.

Nessuna magia qui (arriva con M5): questi comandi coprono solo
l'acquisizione e la crescita delle skill non magiche, piu' la gestione
della professione attiva.
"""

import re
import time

from django.conf import settings

import evennia
from evennia import Command
from evennia import utils as evennia_utils
from evennia.commands.default.general import CmdSay as DefaultCmdSay
from evennia.commands.default.muxcommand import MuxCommand
from evennia.objects.objects import DefaultObject

from world.skills import (
    SKILLS, nome_skill, descrizione_skill,
    GRUPPI_SKILLS, CATEGORIE_GENERALI, skills_conosciute, professioni_con_skill,
)
from world.professions_newbie import NEWBIE_PROFESSIONS, nome_professione
from world.combat import valuta_forza_relativa, tenta_fuga
from world.events import EventContext, EventDispatcher
from world.spells import SPELLS
from world.magic import lancia_incantesimo


def _trova_skill_per_nome(testo):
    """Trova una skill per chiave interna o per nome italiano (anche parziale)."""
    testo = testo.strip().lower()
    if testo in SKILLS:
        return testo
    for sid, dati in SKILLS.items():
        if dati["nome"].lower() == testo:
            return sid
    for sid, dati in SKILLS.items():
        if testo in dati["nome"].lower():
            return sid
    return None


def _trova_professione_per_nome(testo):
    """Trova una professione newbie per chiave interna o per nome italiano."""
    testo = testo.strip().lower()
    if testo in NEWBIE_PROFESSIONS:
        return testo
    for pid, dati in NEWBIE_PROFESSIONS.items():
        if testo in (dati["nome_m"].lower(), dati["nome_f"].lower()):
            return pid
    for pid, dati in NEWBIE_PROFESSIONS.items():
        if testo in dati["nome_m"].lower() or testo in dati["nome_f"].lower():
            return pid
    return None


def _estrai_incantesimo_e_bersaglio(args):
    """'nome incantesimo' resto  oppure  nomeincantesimo resto (come CAST originale)."""
    args = args.strip()
    m = re.match(r"""^['"](.+?)['"]\s*(.*)$""", args)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    parti = args.split(None, 1)
    nome = parti[0] if parti else ""
    resto = parti[1] if len(parti) > 1 else ""
    return nome, resto


_INCANTESIMI_BERSAGLIO_GLOBALE = {
    "gate", "summon", "teleport",
    # Fase K, ottava tornata: Evoca Antico teletrasporta un Antico (staff)
    # da qualunque parte del mondo, per sua stessa natura. Anima Arma
    # serve esplicitamente a recuperare un'arma persa "altrove nel
    # mondo" (fonte: "particularly useful if the weapon has been lost"):
    # senza ricerca globale non potrebbe mai raggiungere il suo scopo.
    "summon_old", "animate_weapon",
    # Fase K, decima tornata: Agonia colpisce chiunque nell'area senza
    # bisogno di condividere la stanza; Incognito maschera il lanciatore
    # con l'aspetto di un NPC che non deve trovarsi nella stessa stanza.
    "agony", "incognito",
}


def _trova_incantesimo_per_nome(testo):
    testo = testo.strip().lower()
    if testo in SPELLS:
        return testo
    for sid, dati in SPELLS.items():
        if dati["nome"].lower() == testo:
            return sid
    return None


ATTRIBUTI_MAPPA = {
    "forza": "str", "str": "str",
    "intelligenza": "int", "int": "int",
    "saggezza": "wis", "wis": "wis",
    "destrezza": "dex", "dex": "dex",
    "costituzione": "con", "con": "con",
    "fortuna": "luck", "luck": "luck",
    "carisma": "cha", "cha": "cha",
}


class CmdScore(Command):
    """
    Mostra la scheda del personaggio.

    Uso:
      score
    """
    key = "score"
    aliases = ["sc"]
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if hasattr(caller, "scheda"):
            caller.msg(caller.scheda())
            return
        # Un giocatore puo' trovarsi a controllare un NPC (Yithian
        # MINDTRANSFER, vedi world/yithian.py): quel corpo non ha una
        # scheda completa come un Character, solo i valori di base.
        righe = [f"|w{caller.key}|n (corpo posseduto)"]
        righe.append(f"HP {caller.db.hp}/{caller.db.hp_max}  Mana {caller.db.mana}/{caller.db.mana_max}  "
                      f"Movimento {caller.db.move}/{caller.db.move_max}")
        if caller.db.yithian_originale:
            righe.append(f"Corpo Yithiano originale: {caller.db.yithian_originale.key} (usa RETURN per tornare)")
        caller.msg("\n".join(righe))


class CmdExperience(Command):
    """
    Mostra livello, esperienza ed effetti collegati.

    Uso:
      experience
      xp
    """
    key = "experience"
    aliases = ["xp"]
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        from world.esperienza import xp_necessaria, livello_effettivo

        caller = self.caller
        if not caller.db.active_profession:
            caller.msg("Non hai ancora una professione attiva: nessuna esperienza da mostrare.")
            return
        livello = caller.livello_professione(caller.db.active_profession)
        necessaria = xp_necessaria(livello)
        percentuale = 100 * (caller.db.xp or 0) / necessaria if necessaria else 0
        righe = [
            f"Livello: {livello}",
            f"Livello effettivo (combattimento): {livello_effettivo(caller)}",
            f"Livello talento (oggetti utilizzabili, +10): vedi EQUIPMENT",
            f"Esperienza: {caller.db.xp or 0}/{necessaria} ({percentuale:.1f}% al prossimo livello)",
        ]
        resistenze = caller.db.resistenze_paura or {}
        if resistenze:
            dettaglio = ", ".join(f"{tipo}: {v}" for tipo, v in sorted(resistenze.items()))
            righe.append(f"Resistenza a paura/perdita di sanity per tipo: {dettaglio}")
        else:
            righe.append("Resistenza a paura/perdita di sanity per tipo: nessuna ancora")
        caller.msg("\n".join(righe))


class CmdRighteouskill(Command):
    """
    Alterna l'opzione RIGHTEOUSKILL.

    Uso:
      righteouskill

    Se attiva, uccidere NPC malvagi sposta il tuo allineamento verso il
    bene e uccidere NPC buoni lo sposta verso il male; se disattiva,
    ogni uccisione sposta il tuo allineamento verso il male (e l'XP
    guadagnata e' leggermente inferiore).
    """
    key = "righteouskill"
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.righteouskill = not caller.db.righteouskill
        stato = "attiva" if caller.db.righteouskill else "disattiva"
        caller.msg(f"L'opzione RIGHTEOUSKILL ora e' {stato}.")


class CmdResearch(Command):
    """
    Mostra informazioni su una skill.

    Uso:
      research <skill>
    """
    key = "research"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: research <skill>")
            return
        skill_id = _trova_skill_per_nome(self.args)
        if not skill_id:
            caller.msg("Skill sconosciuta.")
            return
        dati = SKILLS[skill_id]
        rating = (caller.db.skills or {}).get(skill_id)
        righe = [
            f"|w{dati['nome']}|n ({dati['categoria']})",
            f"Il tuo rating: {rating}%" if rating is not None else "Non conosci ancora questa skill.",
            "",
            descrizione_skill(skill_id) or "Nessuna descrizione disponibile.",
        ]
        caller.msg("\n".join(righe))


_TRAIN_EXTRA_MAPPA = {
    "hp": "hp", "salute": "hp",
    "mana": "mana",
    "movimento": "move", "move": "move",
    "practice": "practice", "practices": "practice",
    "sanity": "sanity", "sanita": "sanity",
}


class CmdTrain(Command):
    """
    Spende i train guadagnati salendo di livello.

    Uso:
      train
      train <attributo>
      train hp|mana|movimento|practice|sanity

    Attributi: forza, intelligenza, saggezza, destrezza, costituzione,
    carisma - il costo sale di 1 train ogni volta che alleni lo stesso
    attributo. La Fortuna NON si puo' allenare (confermato dalla fonte,
    helps/attributes.txt). Le altre opzioni (HP/mana/movimento/practice/
    sanity) costano sempre 1 train.
    """
    key = "train"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        arg = self.args.strip().lower()
        if not arg:
            righe = [f"Hai {caller.db.trains} train disponibili.", "", "Attributi attuali (costo per il prossimo train):"]
            for nome, chiave in [("Forza", "str"), ("Intelligenza", "int"), ("Saggezza", "wis"),
                                  ("Destrezza", "dex"), ("Costituzione", "con"),
                                  ("Fortuna", "luck"), ("Carisma", "cha")]:
                if chiave == "luck":
                    righe.append(f"  {nome}: {caller.valore_attributo(chiave)} (non allenabile)")
                else:
                    righe.append(
                        f"  {nome}: {caller.valore_attributo(chiave)} "
                        f"(costo: {caller.costo_train_attributo(chiave)})"
                    )
            righe.append("")
            righe.append("Altre opzioni (1 train ciascuna): HP, Mana, Movimento, Practice, Sanity")
            righe.append("Uso: train <attributo|opzione>")
            caller.msg("\n".join(righe))
            return
        chiave_extra = _TRAIN_EXTRA_MAPPA.get(arg)
        if chiave_extra:
            ok, msg = caller.train_extra(chiave_extra)
            caller.msg(msg)
            return
        chiave = ATTRIBUTI_MAPPA.get(arg)
        if not chiave:
            caller.msg("Attributo sconosciuto. Scegli tra: forza, intelligenza, saggezza, "
                        "destrezza, costituzione, fortuna, carisma, oppure hp/mana/movimento/"
                        "practice/sanity.")
            return
        ok, msg = caller.train_attributo(chiave)
        caller.msg(msg)


class CmdPractice(Command):
    """
    Pratica una skill che gia' conosci, da solo (senza insegnante).

    Uso:
      practice
      practice <skill>
    """
    key = "practice"
    aliases = ["prac"]
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        arg = self.args.strip()
        skills = caller.db.skills or {}
        if not arg:
            if not skills:
                caller.msg("Non conosci ancora nessuna skill.")
                return
            righe = [f"Hai {caller.db.practices} practice disponibili.", "", "Le tue skill:"]
            for sid, rating in sorted(skills.items(), key=lambda kv: nome_skill(kv[0])):
                righe.append(f"  {nome_skill(sid)}: {rating}%")
            caller.msg("\n".join(righe))
            return
        skill_id = _trova_skill_per_nome(arg)
        if not skill_id:
            caller.msg("Skill sconosciuta.")
            return
        ok, msg = caller.pratica_skill(skill_id)
        caller.msg(msg)


class CmdLearn(Command):
    """
    Impara o migliora una skill da un insegnante presente nella stanza.

    Uso:
      learn <insegnante>
      learn <insegnante> <skill>
    """
    key = "learn"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        if not args:
            caller.msg("Uso: learn <insegnante> [skill]")
            return
        parti = args.split(None, 1)
        insegnante = caller.search(parti[0])
        if not insegnante:
            return
        insegnabili = insegnante.db.skills_insegnabili or []
        if not insegnabili:
            caller.msg(f"{insegnante.key} non ha nulla da insegnarti.")
            return
        if len(parti) == 1:
            righe = [f"{insegnante.key} puo' insegnarti:"]
            for sid in insegnabili:
                righe.append(f"  {nome_skill(sid)}")
            caller.msg("\n".join(righe))
            return
        skill_id = _trova_skill_per_nome(parti[1])
        if not skill_id:
            caller.msg("Skill sconosciuta.")
            return
        ok, msg = caller.impara_da_insegnante(insegnante, skill_id)
        caller.msg(msg)


class CmdSkills(Command):
    """
    elenca le tue skill

    Uso:
      skills
      skills <gruppo>
      skills all

    Gruppi (confermati da helps/skills.txt): combat, magic, lang, mlang,
    alang, clang, nolang, academic, cng, production. Senza argomenti
    mostra le skill generali e di combattimento; ALL mostra ogni skill
    che possiedi, di qualunque categoria.
    """
    key = "skills"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        gruppo = self.args.strip().lower()
        if not gruppo:
            righe_skill = skills_conosciute(caller, CATEGORIE_GENERALI)
            titolo = "Skill generali e di combattimento"
        elif gruppo == "all":
            righe_skill = skills_conosciute(caller)
            titolo = "Tutte le tue skill"
        elif gruppo == "nolang":
            righe_skill = skills_conosciute(caller, set(CATEGORIE_GENERALI) | {"occulta"})
            titolo = "Skill (tutte tranne le lingue)"
        elif gruppo in GRUPPI_SKILLS:
            righe_skill = skills_conosciute(caller, GRUPPI_SKILLS[gruppo])
            titolo = f"Skill: {gruppo}"
        else:
            caller.msg(
                "Gruppo sconosciuto. Uso: skills [combat|magic|lang|mlang|alang|"
                "clang|nolang|academic|cng|production|all]"
            )
            return
        if not righe_skill:
            caller.msg("Nessuna skill da mostrare.")
            return
        righe = [titolo + ":"]
        for sid, rating in righe_skill:
            righe.append(f"  {nome_skill(sid)}: {rating}")
        caller.msg("\n".join(righe))


class CmdSkill(Command):
    """
    mostra i dettagli di una singola skill, o le professioni che la offrono

    Uso:
      skill <skill>
      skill profs <skill>

    Confermato da helps/skills.txt: SKILL <skill> mostra il tuo rating
    (e la descrizione); SKILL PROFS <skill> mostra quali professioni la
    offrono e a quale livello.
    """
    key = "skill"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        if not args:
            caller.msg("Uso: skill <skill>  oppure  skill profs <skill>")
            return
        parti = args.split(None, 1)
        if parti[0].lower() == "profs" and len(parti) == 2:
            skill_id = _trova_skill_per_nome(parti[1])
            if not skill_id:
                caller.msg("Skill sconosciuta.")
                return
            professioni = professioni_con_skill(skill_id)
            if not professioni:
                caller.msg(f"Nessuna professione offre {nome_skill(skill_id)}.")
                return
            righe = [f"Professioni che offrono {nome_skill(skill_id)}:"]
            for nome_prof, livello in professioni:
                righe.append(f"  {nome_prof} (livello {livello})")
            caller.msg("\n".join(righe))
            return

        skill_id = _trova_skill_per_nome(args)
        if not skill_id:
            caller.msg("Skill sconosciuta.")
            return
        rating = caller.skill_rating(skill_id)
        entry = SKILLS.get(skill_id, {})
        righe = [
            nome_skill(skill_id),
            f"Categoria: {entry.get('categoria', '?')}",
            f"Il tuo rating: {rating}",
        ]
        descrizione = descrizione_skill(skill_id)
        if descrizione:
            righe.append(descrizione)
        caller.msg("\n".join(righe))


class CmdDebate(Command):
    """
    Dibatti gratuitamente una skill che gia' conosci con un personaggio
    presente nella stanza (richiede di conoscere la skill Dibattito).

    Uso:
      debate <personaggio> <skill>
    """
    key = "debate"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        parti = args.split(None, 1)
        if len(parti) < 2:
            caller.msg("Uso: debate <personaggio> <skill>")
            return
        bersaglio = caller.search(parti[0])
        if not bersaglio:
            return
        skill_id = _trova_skill_per_nome(parti[1])
        if not skill_id:
            caller.msg("Skill sconosciuta.")
            return
        ok, msg = caller.dibatti_skill(bersaglio, skill_id)
        caller.msg(msg)


class CmdProf(Command):
    """
    Gestisce la professione del personaggio.

    Uso:
      prof list
      prof list <professione>
      prof change <professione>
      prof advanced
      prof advanced <professione>

    "prof advanced" elenca le 40 professioni avanzate (accesso non
    libero: servono condizioni di livello/razza/allineamento/skill, a
    volte imprese non ancora tracciabili - vedi
    world/professions_avanzate.py). "prof change" funziona sia per le
    professioni newbie sia, se le condizioni sono soddisfatte, per
    quelle avanzate.
    """
    key = "prof"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        parti = self.args.strip().split(None, 1)
        if not parti:
            caller.msg("Uso: prof list | prof list <professione> | prof change <professione> | prof advanced [professione]")
            return
        sotto = parti[0].lower()
        resto = parti[1] if len(parti) > 1 else ""

        if sotto == "list" and not resto:
            self._lista(caller)
        elif sotto == "list":
            self._dettaglio(caller, resto)
        elif sotto == "change":
            self._cambia(caller, resto)
        elif sotto in ("advanced", "avanzate") and not resto:
            self._lista_avanzate(caller)
        elif sotto in ("advanced", "avanzate"):
            self._dettaglio_avanzata(caller, resto)
        else:
            caller.msg("Uso: prof list | prof list <professione> | prof change <professione> | prof advanced [professione]")

    def _trova_avanzata_per_nome(self, testo):
        from world.professions_avanzate import PROFESSIONI_AVANZATE
        testo = testo.strip().lower()
        if testo in PROFESSIONI_AVANZATE:
            return testo
        for pid, prof in PROFESSIONI_AVANZATE.items():
            if testo in (prof["nome"].lower(), prof["nome_originale"].lower()):
                return pid
        for pid, prof in PROFESSIONI_AVANZATE.items():
            if testo in prof["nome"].lower():
                return pid
        return None

    def _lista_avanzate(self, caller):
        from world.professions_avanzate import PROFESSIONI_AVANZATE, valuta_condizioni

        righe = ["Professioni avanzate (|gverde|n = condizioni gia' soddisfatte):"]
        for pid, prof in PROFESSIONI_AVANZATE.items():
            ok, _ = valuta_condizioni(caller, pid)
            colore = "|g" if ok else "|y"
            attivo = " |w(attiva)|n" if pid == caller.db.active_profession else ""
            righe.append(f"  {colore}{prof['nome']}|n ({prof['nome_originale']}){attivo}")
        caller.msg("\n".join(righe))

    def _dettaglio_avanzata(self, caller, nome):
        from world.professions_avanzate import PROFESSIONI_AVANZATE, valuta_condizioni

        pid = self._trova_avanzata_per_nome(nome)
        if not pid:
            caller.msg("Professione avanzata sconosciuta.")
            return
        prof = PROFESSIONI_AVANZATE[pid]
        attr = prof["modificatori_attributi"]
        ok, mancanti = valuta_condizioni(caller, pid)
        righe = [
            f"|w{prof['nome']}|n ({prof['nome_originale']})",
            "",
            prof["descrizione"],
            "",
            f"Attributo primario: {prof['attributo_primario'].upper()}",
            f"Modificatori: STR {attr['str']}  INT {attr['int']}  WIS {attr['wis']}  "
            f"DEX {attr['dex']}  CON {attr['con']}  FOR.{attr['luck']}  CAR.{attr['cha']}",
            "",
        ]
        if ok:
            righe.append("|gCondizioni soddisfatte.|n")
        else:
            righe.append("Condizioni mancanti:")
            righe += [f"  - {m}" for m in mancanti]
        tabella_livelli = prof.get("skill_per_livello") or prof.get("spell_per_livello")
        if tabella_livelli:
            righe.append("")
            righe.append("Skill/incantesimi per livello (albero completo):")
            for lvl, skills in sorted(tabella_livelli.items()):
                nomi = ", ".join(nome_skill(s) for s in skills)
                righe.append(f"  {lvl}: {nomi}")
        else:
            righe.append("")
            righe.append("(Albero skill/incantesimi completo non ancora trascritto per questa professione.)")
        caller.msg("\n".join(righe))

    def _lista(self, caller):
        razza = caller.db.race
        righe = ["Professioni disponibili (|gverde|n = compatibile con la tua razza):"]
        for pid, prof in NEWBIE_PROFESSIONS.items():
            colore = "|g" if prof["razza"] == razza else "|y"
            attivo = " |w(attiva)|n" if pid == caller.db.active_profession else ""
            righe.append(f"  {colore}{prof['nome_m']}|n — {prof['luogo']}{attivo}")
        caller.msg("\n".join(righe))

    def _dettaglio(self, caller, nome):
        pid = _trova_professione_per_nome(nome)
        if not pid:
            caller.msg("Professione sconosciuta.")
            return
        prof = NEWBIE_PROFESSIONS[pid]
        attr = prof["attributi"]
        righe = [
            f"|w{prof['nome_m']} / {prof['nome_f']}|n",
            "",
            prof["descrizione"],
            "",
            f"Luogo di partenza: {prof['luogo']}",
            f"Attributo primario: {attr['primario'].upper()}",
            f"Modificatori: STR {attr['str']}  INT {attr['int']}  WIS {attr['wis']}  "
            f"DEX {attr['dex']}  CON {attr['con']}  FOR.{attr['luck']}  CAR.{attr['cha']}",
            "",
            "Skill per livello:",
        ]
        for lvl, skills in sorted(prof["skill_per_livello"].items()):
            nomi = ", ".join(nome_skill(s) for s in skills)
            righe.append(f"  {lvl}: {nomi}")
        caller.msg("\n".join(righe))

    def _cambia(self, caller, nome):
        pid = _trova_professione_per_nome(nome)
        if pid:
            if pid == caller.db.active_profession:
                caller.msg("Sei gia' in quella professione.")
                return
            ok, msg = caller.cambia_professione_newbie(pid)
            caller.msg(msg)
            return

        pid_avanzata = self._trova_avanzata_per_nome(nome)
        if not pid_avanzata:
            caller.msg("Professione sconosciuta.")
            return
        if pid_avanzata == caller.db.active_profession:
            caller.msg("Sei gia' in quella professione.")
            return
        ok, msg = caller.cambia_professione_avanzata(pid_avanzata)
        caller.msg(msg)


class CmdAccess(Command):
    """
    mostra il tuo accesso attuale al gioco

    Uso:
      access

    Questo comando mostra la gerarchia dei permessi e a quali gruppi di
    permessi appartieni.
    """

    key = "access"
    aliases = ["groups", "hierarchy"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """Carica i gruppi di permessi."""

        caller = self.caller
        hierarchy_full = settings.PERMISSION_HIERARCHY
        string = "\n|wGerarchia dei permessi|n (in salita):\n %s" % ", ".join(hierarchy_full)

        if caller.account and caller.account.is_superuser:
            cperms = "<Superuser>"
            pperms = "<Superuser>"
        else:
            cperms = ", ".join(caller.permissions.all())
            if caller.account:
                pperms = ", ".join(caller.account.permissions.all())
            else:
                pperms = "<Nessun account>"

        string += "\n|wIl tuo accesso|n:"
        string += f"\nPersonaggio |c{caller.key}|n: {cperms}"
        if evennia_utils.inherits_from(caller, DefaultObject) and caller.account:
            string += f"\nAccount |c{caller.account.key}|n: {pperms}"
        caller.msg(string)


class CmdSay(DefaultCmdSay):
    """
    Parla ad alta voce nella stanza (con motore reattivo: gli NPC presenti
    possono reagire a parole specifiche - vedi Architettura Balthasar §06).

    Uso:
      say <messaggio>
    """

    def func(self):
        caller = self.caller
        testo = self.args.strip() if self.args else ""
        if not testo:
            caller.msg("Dire cosa?")
            return
        if (caller.db.stati or {}).get("muto"):
            # Fase K, sesta tornata: incantesimo Ammutolire.
            caller.msg("Non riesci a emettere alcun suono!")
            return
        ctx = EventContext(
            tipo="icc", sottotipo="say",
            actor=caller, location=caller.location, text=testo,
        )
        EventDispatcher.emit_challenge(ctx)  # nessun trigger "say" blocca, per ora
        super().func()
        EventDispatcher.emit_reaction(ctx)


class CmdConsider(Command):
    """
    Valuta la forza di un potenziale avversario prima di attaccarlo.

    Uso:
      consider <bersaglio>
    """
    key = "consider"
    aliases = ["con"]
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: consider <bersaglio>")
            return
        bersaglio = caller.search(self.args.strip())
        if not bersaglio:
            return
        if bersaglio == caller:
            caller.msg("Guardarti allo specchio non ti dice molto sulle tue capacita' di combattimento.")
            return
        caller.msg(valuta_forza_relativa(caller, bersaglio))


class CmdKill(Command):
    """
    Attacca un bersaglio, iniziando il combattimento.

    Uso:
      kill <bersaglio>
    """
    key = "kill"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: kill <bersaglio>")
            return
        bersaglio = caller.search(self.args.strip())
        if not bersaglio:
            return
        if bersaglio == caller:
            caller.msg("Non puoi attaccare te stesso.")
            return
        if not hasattr(bersaglio, "avvia_combattimento"):
            caller.msg("Non puoi attaccare questo.")
            return
        if caller.db.combat_target == bersaglio:
            caller.msg(f"Stai gia' attaccando {bersaglio.key}.")
            return

        from world.pk import uccidi_o_murder
        ok, messaggio = uccidi_o_murder(caller, bersaglio, comando_murder=False)
        if not ok:
            caller.msg(messaggio)
            return

        ctx = EventContext(
            tipo="attack", sottotipo="kill",
            actor=caller, victim=bersaglio, location=caller.location,
        )
        if not EventDispatcher.emit_challenge(ctx):
            return

        caller.msg(f"Attacchi {bersaglio.key}!")
        caller.location.msg_contents(
            f"{caller.key} attacca {bersaglio.key}!", exclude=[caller]
        )
        caller.avvia_combattimento(bersaglio)


class CmdFlee(Command):
    """
    Fuggi dal combattimento per un'uscita a caso, o in una direzione data.

    Uso:
      flee
      flee <direzione>
    """
    key = "flee"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not caller.in_combattimento:
            caller.msg("Non sei in combattimento.")
            return
        tenta_fuga(caller, self.args.strip() or None)


# Valore di default confermato dalla fonte (helps/wimpy.txt): la soglia WIMPY
# viene impostata automaticamente al 20% degli HP massimi.
class CmdWimpy(Command):
    """
    Imposta la soglia (in percentuale di HP) sotto la quale tenti di
    fuggire automaticamente dal combattimento.

    Uso:
      wimpy
      wimpy <percentuale>
      wimpy <percentuale> <direzione>
      wimpy off

    Da solo, imposta la soglia al 20% dei tuoi HP massimi.
    """
    key = "wimpy"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    SOGLIA_DEFAULT = 20

    def func(self):
        caller = self.caller
        arg = self.args.strip()
        if not arg:
            caller.db.wimpy_soglia = self.SOGLIA_DEFAULT
            caller.msg(f"Wimpy impostato al {self.SOGLIA_DEFAULT}% (il default).")
            return
        parti = arg.split(None, 1)
        if parti[0].lower() == "off":
            caller.db.wimpy_soglia = 0
            caller.db.wimpy_direzione = None
            caller.msg("Wimpy disattivato.")
            return
        try:
            soglia = int(parti[0])
        except ValueError:
            caller.msg("Uso: wimpy <percentuale> [direzione] | wimpy off")
            return
        soglia = max(0, min(99, soglia))
        caller.db.wimpy_soglia = soglia
        caller.db.wimpy_direzione = parti[1] if len(parti) > 1 else None
        caller.msg(f"Wimpy impostato al {soglia}%.")


def _lista_incantesimi_conosciuti(caller):
    skills = caller.db.skills or {}
    conosciuti = [sid for sid, dati in SPELLS.items() if dati["skill_richiesta"] in skills]
    if not conosciuti:
        caller.msg("Non conosci ancora nessun incantesimo.")
        return
    righe = [f"Mana: {caller.db.mana}/{caller.db.mana_max}", "", "Incantesimi conosciuti:"]
    for sid in conosciuti:
        righe.append(f"  {SPELLS[sid]['nome']} (costo mana: {SPELLS[sid]['costo_mana']})")
    caller.msg("\n".join(righe))


def _esegui_cast(caller, args, rituale=False):
    """Logica condivisa da CAST e RITUAL (Fase K, ventitreesima tornata:
    helps/cast.txt - "For those characters that have the RITUAL MASTERY
    skill, the RITUAL command may be used in place of CAST")."""
    if not args.strip():
        _lista_incantesimi_conosciuti(caller)
        return

    nome, resto = _estrai_incantesimo_e_bersaglio(args)
    spell_id = _trova_incantesimo_per_nome(nome)
    if not spell_id:
        caller.msg("Incantesimo sconosciuto.")
        return
    stati = caller.db.stati or {}
    if stati.get("muto") and not stati.get("vocalizzato"):
        # Fase K, sesta tornata: Ammutolire impedisce di lanciare
        # incantesimi con componente verbale, a meno di avere anche
        # l'effetto di Vocalizzo attivo (confermato dalla fonte).
        caller.msg("Sei muto/a e non riesci a pronunciare le parole dell'incantesimo!")
        return

    spell = SPELLS[spell_id]
    bersaglio = None
    testo = None
    if spell.get("richiede_testo"):
        testo = resto or None
    elif resto:
        # Fase K, sesta tornata: Varco Dimensionale/Evocazione/Teletrasporto
        # per loro stessa natura raggiungono un bersaglio altrove nel
        # mondo - la ricerca va estesa oltre la sola stanza del lanciatore.
        globale = spell_id in _INCANTESIMI_BERSAGLIO_GLOBALE
        bersaglio = caller.search(resto, global_search=globale)
        if not bersaglio:
            return
    elif spell.get("bersaglio_richiesto"):
        # Fase K, ventitreesima tornata: helps/spell_casting.txt - "During
        # combat, the code will usually select an appropriate target
        # character if you do not specify one" - vale per gli incantesimi
        # ostili (per quelli benefici/su se stessi, il default resta se
        # stessi, come gia' prima).
        if spell.get("ostile") and caller.db.combat_target:
            bersaglio = caller.db.combat_target
        else:
            bersaglio = caller

    ok, msg = lancia_incantesimo(caller, spell_id, bersaglio, testo, rituale=rituale)
    if msg:
        caller.msg(msg)


class CmdCast(Command):
    """
    Lancia un incantesimo. Richiede di conoscere sia il Lancio degli
    Incantesimi sia la skill specifica dell'incantesimo (impara entrambe
    con LEARN o PRACTICE).

    Uso:
      cast
      cast <incantesimo>
      cast <incantesimo> <bersaglio>
      cast 'nome incantesimo con piu parole' <bersaglio>
    """
    key = "cast"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        _esegui_cast(self.caller, self.args)


class CmdRitual(Command):
    """
    lancia un incantesimo in forma di rituale (richiede Maestria nei Rituali)

    Uso:
      ritual <incantesimo>
      ritual <incantesimo> <bersaglio>

    Come CAST, ma se sei in GROUP con altri possessori della skill
    Maestria nei Rituali presenti nella stanza, l'incantesimo risulta
    piu' potente (confermato da helps/ritual_mastery.txt).
    """
    key = "ritual"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        _esegui_cast(self.caller, self.args, rituale=True)


class CmdSpell(Command):
    """
    mostra informazioni dettagliate su un incantesimo

    Uso:
      spell <incantesimo>

    Mostra i dettagli di un incantesimo specifico (confermato da
    helps/spell_casting.txt).
    """
    key = "spell"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Uso: spell <incantesimo>")
            return
        nome, _ = _estrai_incantesimo_e_bersaglio(self.args)
        spell_id = _trova_incantesimo_per_nome(nome)
        if not spell_id:
            caller.msg("Incantesimo sconosciuto.")
            return
        spell = SPELLS[spell_id]
        rating = caller.skill_rating(spell["skill_richiesta"])
        righe = [
            spell["nome"],
            f"Skill richiesta: {nome_skill(spell['skill_richiesta'])} (il tuo rating: {rating})",
            f"Costo mana base: {spell['costo_mana']}",
            f"Bersaglio richiesto: {'si' if spell.get('bersaglio_richiesto') else 'no'}",
        ]
        if spell.get("descrizione"):
            righe.append(spell["descrizione"])
        caller.msg("\n".join(righe))


class CmdSpells(Command):
    """
    elenca gli incantesimi che conosci

    Uso:
      spells

    Mostra l'elenco degli incantesimi che conosci e il relativo costo in
    mana (confermato da helps/spell_casting.txt). Equivalente a CAST
    senza argomenti.
    """
    key = "spells"
    locks = "cmd:all()"
    help_category = "CthulhuMud"
    arg_regex = r"$"

    def func(self):
        _lista_incantesimi_conosciuti(self.caller)


class CmdDuel(Command):
    """
    modifica il tuo assetto durante un Duello Magico

    Uso:
      duel off <mana>
      duel def <mana>

    Confermato dalla fonte (helps/magical_duel.txt): durante un Duello
    Magico i contendenti possono spendere mana per rafforzare i propri
    attacchi (OFF) o le proprie difese (DEF) invece di usare tecniche di
    combattimento normali. Disponibile solo mentre sei in un duello
    magico attivo (vedi world/magic.py:_effetto_magical_duel). Versione
    semplificata dichiarata: la fonte lascia intendere un vero e proprio
    sotto-sistema di combattimento alternativo, qui si traduce come un
    bonus temporaneo a colpire/CA proporzionale al mana speso, riusando
    i campi bonus_colpire/bonus_ca_temp gia' esistenti invece di
    costruire una seconda modalita' di combattimento da zero.
    """

    key = "duel"
    locks = "cmd:all()"
    help_category = "CthulhuMud"

    def func(self):
        caller = self.caller
        stati = caller.db.stati or {}
        if not stati.get("duello_magico"):
            caller.msg("Non sei impegnato/a in un Duello Magico.")
            return
        parti = self.args.split()
        if len(parti) != 2 or parti[0].lower() not in ("off", "def") or not parti[1].isdigit():
            caller.msg("Uso: duel off <mana>  oppure  duel def <mana>")
            return
        modalita = parti[0].lower()
        costo = int(parti[1])
        if costo <= 0 or costo > (caller.db.mana or 0):
            caller.msg("Non hai cosi' tanto mana.")
            return
        caller.db.mana -= costo
        bonus = max(1, costo // 5)
        from world.effetti import applica_buff_temporaneo
        if modalita == "off":
            applica_buff_temporaneo(caller, "bonus_colpire", bonus, 300, None)
            caller.msg(f"Concentri {costo} mana nell'attacco: +{bonus} a colpire per 5 minuti.")
        else:
            applica_buff_temporaneo(caller, "bonus_ca_temp", bonus, 300, None)
            caller.msg(f"Concentri {costo} mana nella difesa: +{bonus} alla classe armatura per 5 minuti.")


######################################################################
# Fase B della localizzazione: sovrascritture dei comandi di default di
# Evennia, che (a differenza del "motore" - login, EvMenu, editor, lock -
# gia' tradotto in world/... e nel catalogo gettext) non passano affatto
# da un sistema di traduzione: sono testo fisso in inglese nel codice.
# Qui replichiamo fedelmente la logica originale (vedi
# evennia/commands/default/general.py e account.py) con stringhe italiane.
#
# HELP (evennia/commands/default/help.py) resta volutamente fuori da
# questa fase: e' un sistema di ~1100 righe che pesca anche dai docstring
# di ogni comando (a loro volta tutti in inglese). Fase C ha poi tradotto
# la sua INTERFACCIA (titoli, indice, messaggi di sistema - vedi
# commands/cthulhu_help.py): il CONTENUTO di ogni singolo help (i
# docstring dei comandi non ancora localizzati) resta invece in inglese,
# lacuna dichiarata li' esplicitamente, non qui.
######################################################################

class CmdHome(Command):
    """
    vai alla tua casa

    Uso:
      home
    """
    key = "home"
    locks = "cmd:perm(home) or perm(Builder)"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        home = caller.home
        if not home:
            caller.msg("Non hai una casa!")
        elif home == caller.location:
            caller.msg("Sei gia' a casa!")
        else:
            caller.msg("Casa, dolce casa...")
            caller.move_to(home, move_type="teleport")


class CmdLook(Command):
    """
    guarda la tua posizione o un oggetto

    Uso:
      look
      look <oggetto>
      examine <oggetto>

    EXAMINE e' sinonimo di LOOK (confermato dalla fonte,
    helps/look.txt/examine.txt). Se <oggetto> non e' un oggetto/
    personaggio/uscita reale, la stanza viene controllata per un
    "oggetto di scena" (dettaglio d'arredo esaminabile ma non
    raccoglibile - vedi world/scenografia.py) prima di arrendersi.
    """
    key = "look"
    aliases = ["l", "ls", "examine", "exa"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("Non hai una posizione da osservare!")
                return
        else:
            target = caller.search(self.args, quiet=True)
            if isinstance(target, list):
                if len(target) > 1:
                    caller.msg("Ci sono piu' cose con quel nome. Sii piu' specifico.")
                    return
                target = target[0] if target else None
            if not target:
                from world.scenografia import trova_ed
                testo = trova_ed(caller.location, self.args)
                if testo:
                    caller.msg(testo)
                    return
                caller.msg(f"Non riesci a trovare '{self.args.strip()}'.")
                return
        desc = caller.at_look(target)
        self.msg(text=(desc, {"type": "look"}), options=None)


class CmdInventory(Command):
    """
    mostra il tuo inventario

    Uso:
      inventory
      inv
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        # gli oggetti indossati/impugnati si vedono con EQUIPMENT, non qui
        items = [o for o in self.caller.contents if not o.db.indossato]
        if not items:
            string = "Non hai nulla con te."
        else:
            from evennia.utils.ansi import raw as raw_ansi
            table = self.styled_table(border="header")
            for key, desc, _n in evennia_utils.group_objects_by_key_and_desc(
                items, caller=self.caller
            ):
                table.add_row(
                    f"|C{key}|n",
                    "{}|n".format(evennia_utils.crop(raw_ansi(desc or ""), width=50) or ""),
                )
            string = f"|wStai portando con te:|n\n{table}"
        self.msg(text=(string, {"type": "inventory"}))


class NumberedTargetCommand(MuxCommand):
    """Estrae un eventuale numero iniziale (es. '2 pugnale') - vedi CmdGet/Drop/Give."""

    def parse(self):
        super().parse()
        self.number = 0
        if getattr(self, "lhs", None):
            count, *args = self.lhs.split(maxsplit=1)
            if args and count.isdecimal():
                self.number = int(count)
                self.lhs = args[0]
        if self.args:
            count, *args = self.args.split(maxsplit=1)
            if args and count.isdecimal():
                self.args = args[0]
                if not self.number:
                    self.number = int(count)


class CmdGet(NumberedTargetCommand):
    """
    raccogli un oggetto

    Uso:
      get <oggetto>
      get <oggetto> <contenitore>

    La seconda forma serve a prendere qualcosa da dentro un contenitore
    (es. un cadavere): "get spada cadavere" prende la spada dal cadavere
    presente nella stanza. "get all cadavere" prende tutto il contenuto.
    """
    key = "get"
    aliases = ["grab"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller
        if not self.args:
            self.msg("Prendere cosa?")
            return

        oggetto_spec = self.args
        contenitore = None
        parti = self.args.rsplit(None, 1)
        if len(parti) == 2:
            possibile_oggetto, possibile_contenitore = parti
            trovato = caller.search(possibile_contenitore, location=caller.location, quiet=True)
            trovato = trovato[0] if trovato else None
            if trovato and trovato not in (caller,) and hasattr(trovato, "contents"):
                contenitore = trovato
                oggetto_spec = possibile_oggetto

        if contenitore:
            self._get_da_contenitore(caller, oggetto_spec, contenitore)
            return

        objs = caller.search(self.args, location=caller.location, stacked=self.number)
        if not objs:
            return
        objs = objs if isinstance(objs, list) else [objs]

        if len(objs) == 1 and caller == objs[0]:
            self.msg("Non puoi prendere te stesso.")
            return

        for obj in objs:
            if not obj.access(caller, "get"):
                if obj.db.get_err_msg:
                    self.msg(obj.db.get_err_msg)
                else:
                    self.msg("Non puoi raccoglierlo.")
                return
            if not obj.at_pre_get(caller):
                return

        moved = []
        for obj in objs:
            if obj.move_to(caller, quiet=True, move_type="get"):
                moved.append(obj)
                obj.at_get(caller)

        if not moved:
            self.msg("Non puo' essere raccolto.")
        else:
            obj_name = moved[0].get_numbered_name(len(moved), caller, return_string=True)
            caller.msg(f"Raccogli {obj_name}.")
            caller.location.msg_contents(
                f"{caller.key} raccoglie {obj_name}.", exclude=[caller]
            )

    def _get_da_contenitore(self, caller, oggetto_spec, contenitore):
        proprietario = contenitore.db.proprietario
        if proprietario and proprietario.pk and caller is not proprietario:
            if proprietario.db.noloot:
                # NOLOOT (helps/autokill.txt): nega l'accesso anche al
                # proprio gruppo, non solo agli estranei.
                caller.msg(f"{proprietario.key} ha attivato NOLOOT: nessuno puo' frugare in {contenitore.key}.")
                return
            from world.gruppo import membri_gruppo
            if caller not in membri_gruppo(proprietario):
                caller.msg(f"Solo {proprietario.key} o il suo gruppo puo' frugare in {contenitore.key}.")
                return
        if oggetto_spec.strip().lower() in ("all", "tutto"):
            objs = list(contenitore.contents)
            if not objs:
                caller.msg(f"{contenitore.key} e' vuoto/a.")
                return
        else:
            objs = caller.search(oggetto_spec, location=contenitore, quiet=True)
            if not objs:
                caller.msg(f"Non trovi '{oggetto_spec}' dentro {contenitore.key}.")
                return
            objs = objs if isinstance(objs, list) else [objs]

        moved = []
        for obj in objs:
            if not obj.access(caller, "get"):
                continue
            if not obj.at_pre_get(caller):
                continue
            if obj.move_to(caller, quiet=True, move_type="get"):
                moved.append(obj)
                obj.at_get(caller)

        if not moved:
            caller.msg(f"Non riesci a prendere nulla da {contenitore.key}.")
        else:
            nomi = ", ".join(o.key for o in moved)
            caller.msg(f"Prendi {nomi} da {contenitore.key}.")
            caller.location.msg_contents(
                f"{caller.key} fruga in {contenitore.key}.", exclude=[caller]
            )


class CmdDrop(NumberedTargetCommand):
    """
    lascia a terra un oggetto

    Uso:
      drop <oggetto>
    """
    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Lasciare cosa?")
            return
        objs = caller.search(
            self.args,
            location=caller,
            nofound_string=f"Non hai con te '{self.args}'.",
            multimatch_string=f"Hai con te più di un oggetto simile a '{self.args}':",
            stacked=self.number,
        )
        if not objs:
            return
        objs = objs if isinstance(objs, list) else [objs]

        for obj in objs:
            if not obj.at_pre_drop(caller):
                return

        moved = []
        for obj in objs:
            if obj.move_to(caller.location, quiet=True, move_type="drop"):
                moved.append(obj)
                obj.at_drop(caller)

        if not moved:
            self.msg("Non puo' essere lasciato a terra.")
        else:
            obj_name = moved[0].get_numbered_name(len(moved), caller, return_string=True)
            caller.msg(f"Lasci a terra {obj_name}.")
            caller.location.msg_contents(
                f"{caller.key} lascia a terra {obj_name}.", exclude=[caller]
            )


class CmdGive(NumberedTargetCommand):
    """
    dai un oggetto a qualcuno

    Uso:
      give <oggetto> = <bersaglio>
      give <oggetto> a <bersaglio>
    """
    key = "give"
    rhs_split = ("=", " a ")
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Uso: give <oggetto> = <bersaglio>")
            return
        to_give = caller.search(
            self.lhs,
            location=caller,
            nofound_string=f"Non hai con te '{self.lhs}'.",
            multimatch_string=f"Hai con te più di un oggetto simile a '{self.lhs}':",
            stacked=self.number,
        )
        if not to_give:
            return
        target = caller.search(self.rhs)
        if not target:
            return
        to_give = to_give if isinstance(to_give, list) else [to_give]

        singular, plural = to_give[0].get_numbered_name(len(to_give), caller)
        if target == caller:
            caller.msg(f"Tieni {plural if len(to_give) > 1 else singular} per te.")
            return

        for obj in to_give:
            if not obj.at_pre_give(caller, target):
                return

        moved = []
        for obj in to_give:
            if obj.move_to(target, quiet=True, move_type="give"):
                moved.append(obj)
                obj.at_give(caller, target)

        if not moved:
            caller.msg(f"Non hai potuto darlo a {target.get_display_name(caller)}.")
        else:
            obj_name = to_give[0].get_numbered_name(len(moved), caller, return_string=True)
            caller.msg(f"Dai {obj_name} a {target.get_display_name(caller)}.")
            target.msg(f"{caller.get_display_name(target)} ti da' {obj_name}.")


class CmdSetDesc(Command):
    """
    descrivi te stesso

    Uso:
      setdesc <descrizione>
    """
    key = "setdesc"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        if not self.args:
            self.msg("Devi fornire una descrizione.")
            return
        self.caller.db.desc = self.args.strip()
        self.msg("Descrizione impostata.")


class CmdWhisper(MuxCommand):
    """
    sussurra qualcosa a qualcuno

    Uso:
      whisper <personaggio> = <messaggio>
      whisper <pers1>, <pers2> = <messaggio>
    """
    key = "whisper"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.lhs or not self.rhs:
            caller.msg("Uso: whisper <personaggio> = <messaggio>")
            return
        receivers = [r.strip() for r in self.lhs.split(",")]
        receivers = [caller.search(r) for r in set(receivers)]
        receivers = [r for r in receivers if r]
        speech = self.rhs
        if not speech or not receivers:
            return
        speech = caller.at_pre_say(speech, whisper=True, receivers=receivers)
        msg_self = None if caller in receivers else True
        caller.at_say(speech, msg_self=msg_self, receivers=receivers, whisper=True)


class CmdPose(Command):
    """
    atteggiati in una posa

    Uso:
      pose <testo>
      pose's <testo>
    """
    key = "pose"
    aliases = [":", "emote"]
    locks = "cmd:all()"
    arg_regex = None

    def parse(self):
        args = self.args
        if args and not args[0] in ["'", ",", ":"]:
            args = " %s" % args.strip()
        self.args = args

    def func(self):
        if not self.args:
            self.msg("Cosa vuoi fare?")
        else:
            msg = f"{self.caller.name}{self.args}"
            self.caller.location.msg_contents(text=(msg, {"type": "pose"}), from_obj=self.caller)


class CmdWho(Command):
    """
    mostra chi e' online

    Uso:
      who
    """
    key = "who"
    aliases = ["doing"]
    locks = "cmd:all()"
    account_caller = True

    def func(self):
        account = self.account
        session_list = sorted(
            evennia.SESSION_HANDLER.get_sessions(), key=lambda o: o.account.key
        )

        if self.cmdstring == "doing":
            show_session_data = False
        else:
            show_session_data = account.check_permstring(
                "Developer"
            ) or account.check_permstring("Admins")

        naccounts = evennia.SESSION_HANDLER.account_count()
        if show_session_data:
            table = self.styled_table(
                "|wNome Account", "|wConnesso da", "|wInattivo da", "|wPersonaggio",
                "|wStanza", "|wComandi", "|wProtocollo", "|wHost",
            )
            for session in session_list:
                if not session.logged_in:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                session_account = session.get_account()
                puppet = session.get_puppet()
                location = puppet.location.key if puppet and puppet.location else "Nessuna"
                table.add_row(
                    evennia_utils.crop(session_account.get_display_name(account), width=25),
                    evennia_utils.time_format(delta_conn, 0),
                    evennia_utils.time_format(delta_cmd, 1),
                    evennia_utils.crop(
                        puppet.get_display_name(account) if puppet else "Nessuno", width=25
                    ),
                    evennia_utils.crop(location, width=25),
                    session.cmd_total,
                    session.protocol_key,
                    isinstance(session.address, tuple) and session.address[0] or session.address,
                )
        else:
            table = self.styled_table("|wNome Account", "|wConnesso da", "|wInattivo da")
            for session in session_list:
                if not session.logged_in:
                    continue
                delta_cmd = time.time() - session.cmd_last_visible
                delta_conn = time.time() - session.conn_time
                session_account = session.get_account()
                table.add_row(
                    evennia_utils.crop(session_account.get_display_name(account), width=25),
                    evennia_utils.time_format(delta_conn, 0),
                    evennia_utils.time_format(delta_cmd, 1),
                )
        if naccounts == 1:
            riepilogo = "Un account unico connesso."
        else:
            riepilogo = f"{naccounts} account unici connessi."
        self.msg(f"|wAccount:|n\n{table}\n{riepilogo}")


class CmdQuit(MuxCommand):
    """
    esci dal gioco

    Uso:
      quit

    Switch:
      all - disconnette tutte le sessioni connesse
    """
    key = "quit"
    switch_options = ("all",)
    locks = "cmd:all()"
    account_caller = True

    def func(self):
        account = self.account
        if "all" in self.switches:
            account.msg(
                "|RUscita|n da tutte le sessioni. Alla prossima!", session=self.session
            )
            reason = "quit/all"
            for session in account.sessions.all():
                account.disconnect_session_from_account(session, reason)
        else:
            nsess = len(account.sessions.all())
            reason = "quit"
            if nsess == 2:
                account.msg(
                    "|RUscita.|n Un'altra sessione e' ancora connessa.", session=self.session
                )
            elif nsess > 2:
                account.msg(
                    f"|RUscita.|n Altre {nsess - 1} sessioni sono ancora connesse.",
                    session=self.session,
                )
            else:
                account.msg("|RUscita.|n Alla prossima!", session=self.session)
            account.disconnect_session_from_account(self.session, reason)


class CmdAbout(Command):
    """
    mostra informazioni sul motore di gioco (Evennia)

    Uso:
      about

    Sostituisce l'@about di default di Evennia (in inglese) con una
    versione in italiano: e' l'unico comando di sistema di default
    lasciato accessibile a tutti i giocatori, quindi va tradotto.
    """

    key = "@about"
    aliases = ["@version"]
    locks = "cmd:all()"
    help_category = "Sistema"

    def func(self):
        import os
        import sys

        import django
        import twisted

        stringa = """
         |cEvennia|n - motore di sviluppo MU* (in inglese: MU* development system)

         |wVersione Evennia|n: {version}
         |wSistema operativo|n: {os}
         |wPython|n: {python}
         |wTwisted|n: {twisted}
         |wDjango|n: {django}

         |wSito ufficiale|n https://evennia.com
         |wCodice sorgente|n https://github.com/evennia/evennia
         |wLicenza|n https://opensource.org/licenses/BSD-3-Clause

         Questo gioco (|gCthulhuMUD ITA Redux|n) e' un porting in italiano,
         costruito su Evennia, del MUD lovecraftiano CthulhuMUD.
        """.format(
            version=evennia_utils.get_evennia_version(),
            os=os.name,
            python=sys.version.split()[0],
            twisted=twisted.version.short(),
            django=django.get_version(),
        )
        self.caller.msg(stringa)
