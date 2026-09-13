"""
Motore reattivo NPC (M4): EventContext, EventDispatcher, trigger.

Vedi Architettura Balthasar §06. Prima implementazione concreta, validata
su due verbi soli (say, kill) prima di estendere a tutti i comandi:

- SAY -> evento "icc/say", solo fase REACTION (un NPC puo' reagire a una
  parola pronunciata, non puo' impedirti di parlare)
- KILL -> evento "attack/kill", fase CHALLENGE (un NPC puo' impedire che
  l'azione avvenga, es. per autoproteggersi) e fase REACTION

Un trigger e' un semplice dizionario su `npc.db.triggers`:
    {
        "fase": "challenge" | "reaction",
        "tipo": "icc" | "attack" | ...,           # come nel Dossier §14
        "sottotipo": "say" | "kill" | ...,
        "template": "parola1|parola2&parola3",    # opzionale, & = AND, | = OR
        "condizione": {...} | None,                # opzionale, vedi _valuta_condizione
        "solo_se_vittima": bool,                   # scatta solo se l'NPC e' ctx.victim
        "dice": "testo con {attore}",              # cosa dice/fa l'NPC
        "blocca": bool,                             # solo per "challenge": nega l'azione
    }
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EventContext:
    """Corrisponde al 'context' del Dossier §10."""
    tipo: str
    sottotipo: str = ""
    actor: Any = None
    victim: Any = None
    observer: Any = None
    pobj: Any = None
    sobj: Any = None
    location: Any = None
    number: int = 0
    text: str = ""


def _valuta_template(template, testo):
    """AND (&) e OR (|), con AND a precedenza piu' alta - come nel Dossier §14."""
    if not template:
        return True
    testo = (testo or "").lower()
    for gruppo_or in template.lower().split("|"):
        parole = [p.strip() for p in gruppo_or.split("&") if p.strip()]
        if parole and all(p in testo for p in parole):
            return True
    return False


def _valuta_condizione(cond, ctx):
    """Registro minimo di condizioni (Dossier §9), estendibile in seguito."""
    if not cond:
        return True
    soggetto = getattr(ctx, cond.get("soggetto", "actor"), None)
    tipo = cond.get("tipo")
    if tipo == "skill" and soggetto is not None:
        rating = soggetto.skill_rating(cond["chiave"]) if hasattr(soggetto, "skill_rating") else 0
        return rating >= cond.get("min", 0)
    return True


def _trigger_corrisponde(trig, ctx, npc):
    if trig.get("tipo") != ctx.tipo:
        return False
    sottotipo = trig.get("sottotipo")
    if sottotipo and sottotipo != ctx.sottotipo:
        return False
    if trig.get("solo_se_vittima") and ctx.victim is not npc:
        return False
    if not _valuta_template(trig.get("template"), ctx.text):
        return False
    return True


def _esegui_dice(trig, ctx, npc):
    dice = trig.get("dice")
    if dice and npc.location:
        attore = ctx.actor.key if ctx.actor else "qualcuno"
        testo = dice.format(attore=attore)
        npc.location.msg_contents(f'{npc.key} dice, "{testo}"')


def _candidati_stanza(ctx):
    if not ctx.location:
        return []
    return [o for o in ctx.location.contents if o.attributes.has("triggers")]


class EventDispatcher:
    """Dispatcher centrale: due fasi, come nel Dossier §8."""

    @staticmethod
    def emit_challenge(ctx):
        """Ritorna False se un trigger nega l'azione (si ferma al primo veto)."""
        for npc in _candidati_stanza(ctx):
            if npc is ctx.actor:
                continue
            for trig in npc.db.triggers or []:
                if trig.get("fase") != "challenge":
                    continue
                if not _trigger_corrisponde(trig, ctx, npc):
                    continue
                if not _valuta_condizione(trig.get("condizione"), ctx):
                    continue
                _esegui_dice(trig, ctx, npc)
                if trig.get("blocca", True):
                    return False
        return True

    @staticmethod
    def emit_reaction(ctx):
        """Notifica tutti i trigger di reazione validi (nessuna interruzione)."""
        for npc in _candidati_stanza(ctx):
            if npc is ctx.actor:
                continue
            for trig in npc.db.triggers or []:
                if trig.get("fase", "reaction") != "reaction":
                    continue
                if not _trigger_corrisponde(trig, ctx, npc):
                    continue
                if not _valuta_condizione(trig.get("condizione"), ctx):
                    continue
                _esegui_dice(trig, ctx, npc)
