"""
Cristalli Focus Yithiani (Fase K, settima tornata): confermati dalla
fonte (guides_yithianfaq.txt, la stessa pagina gia' usata per il resto
del sottosistema Yithian) come "rimandati" esplicitamente in
world/yithian.py fin dalla Fase G, nona tornata ("un sistema di
drenaggio passivo che meriterebbe un oggetto e una meccanica dedicati
a parte").

Meccanica confermata verbatim dalla fonte:
- Un cristallo, se tenuto in mano/inventario, "risucchia" skill dalle
  altre creature (NPC o giocatori) presenti nella stessa stanza, anche
  solo per la loro presenza passiva (non serve che usino la skill,
  anche se usarla aumenta l'assorbimento - qui semplificato: nessun
  bonus per skill "appena usata", vedi sotto).
- LORE <cristallo> (richiede la skill Lore) mostra le skill assorbite
  e il loro "livello" nel cristallo.
- USE <cristallo> trasferisce un sottoinsieme casuale delle skill
  assorbite al personaggio che lo usa: se non la conosce la impara, se
  la conosce gia' la migliora. C'e' sempre una componente casuale.
- Pensati per gli Yithiani: chiunque altro (compreso uno Yithiano che
  sta possedendo un corpo non-Yithiano, che percio' "e'" quel corpo ai
  fini di questo controllo) subisce una forte penalita' di riuscita.

NON specificato dalla fonte (scelte di design esplicite): le percentuali
esatte di assorbimento/trasferimento, il numero massimo di skill per
cristallo, la cadenza del tick passivo. Semplificazione dichiarata:
nessun bonus per una skill "appena usata in presenza del cristallo" -
richiederebbe di agganciare il tick a OGNI singolo controllo di skill
del gioco (combattimento, forgiatura, incantesimi...), un'invasivita'
sproporzionata rispetto al valore aggiunto; qui il tick passivo e'
uniforme per ogni creatura presente nella stanza.
"""

import random

LIVELLO_MASSIMO_CRISTALLO = 100
PROBABILITA_ASSORBIMENTO_PER_TICK = 15  # % per ogni altra creatura presente
ASSORBIMENTO_MIN, ASSORBIMENTO_MAX = 1, 3

COSTO_MOVIMENTO_LORE = 100


def avvia_cristalli_focus():
    """Crea lo script globale del tick di assorbimento se non e' gia' in
    esecuzione (idempotente, stesso pattern di avvia_sopravvivenza/avvia_repop)."""
    from evennia.scripts.models import ScriptDB

    esistente = ScriptDB.objects.filter(db_key="cristalli_focus")
    if esistente:
        return esistente[0]

    from evennia.utils import create
    return create.create_script("typeclasses.scripts.CristalliFocusScript")


def crea_cristallo(location, key="un cristallo focus"):
    from evennia.utils import create
    cristallo = create.create_object("typeclasses.objects.Object", key=key, location=location)
    cristallo.db.desc = (
        "Un cristallo violaceo dalle facce irregolari, che pulsa debolmente come se "
        "respirasse. Tenerlo in mano da' la strana sensazione di essere osservati "
        "dall'interno della propria stessa mente."
    )
    cristallo.db.tipo_oggetto = "cristallo_focus"
    cristallo.db.cristallo_skill = {}
    return cristallo


def e_cristallo(oggetto):
    return bool(getattr(oggetto, "db", None) and oggetto.db.tipo_oggetto == "cristallo_focus")


def tick_assorbimento_cristalli():
    """Chiamato periodicamente (vedi typeclasses.scripts.CristalliFocusScript):
    per ogni cristallo attualmente in mano a qualcuno, tenta di assorbire
    una skill casuale da ogni altra creatura vivente nella stessa stanza."""
    from evennia.objects.models import ObjectDB

    # Filtrare per attributo via query SQL sarebbe fragile (dipende dal
    # formato di serializzazione interno di Evennia): piu' sicuro (anche se
    # meno efficiente su un mondo enorme) iterare e controllare in Python.
    cristalli = [o for o in ObjectDB.objects.all() if e_cristallo(o)]

    for cristallo in cristalli:
        titolare = cristallo.location
        if not titolare or not getattr(titolare, "vivo", None):
            continue
        stanza = titolare.location
        if not stanza:
            continue
        presenti = [
            o for o in stanza.contents
            if o is not titolare and getattr(o, "vivo", None) and o.db.skills
        ]
        for creatura in presenti:
            skill_valide = [sid for sid, rating in (creatura.db.skills or {}).items() if rating > 0]
            if not skill_valide:
                continue
            if random.randint(1, 100) > PROBABILITA_ASSORBIMENTO_PER_TICK:
                continue
            skill_id = random.choice(skill_valide)
            contenuto = dict(cristallo.db.cristallo_skill or {})
            attuale = contenuto.get(skill_id, 0)
            if attuale >= LIVELLO_MASSIMO_CRISTALLO:
                continue
            guadagno = random.randint(ASSORBIMENTO_MIN, ASSORBIMENTO_MAX)
            contenuto[skill_id] = min(LIVELLO_MASSIMO_CRISTALLO, attuale + guadagno)
            cristallo.db.cristallo_skill = contenuto


def descrivi_cristallo(cristallo):
    contenuto = cristallo.db.cristallo_skill or {}
    if not contenuto:
        return "Il cristallo e' silenzioso: non ha ancora assorbito nulla."
    from world.skills import nome_skill
    righe = ["Il cristallo pulsa con frammenti di conoscenza altrui:"]
    for sid, livello in sorted(contenuto.items(), key=lambda x: -x[1]):
        righe.append(f"  {nome_skill(sid)}: {livello}")
    return "\n".join(righe)


def usa_cristallo(personaggio, cristallo):
    """USE <cristallo>. Ritorna (ok: bool, messaggio: str)."""
    contenuto = dict(cristallo.db.cristallo_skill or {})
    if not contenuto:
        return False, f"{cristallo.key} e' silenzioso: non c'e' nulla da assorbire."

    e_yithiano = personaggio.db.race == "yithian"
    skill_attuali = dict(personaggio.db.skills or {})
    guadagni = {}

    for skill_id, livello in contenuto.items():
        soglia = min(90, livello + 10) if e_yithiano else min(20, livello // 3)
        if random.randint(1, 100) > soglia:
            continue
        rating_attuale = skill_attuali.get(skill_id, 0)
        aumento = random.randint(1, max(1, livello // 10))
        nuovo_rating = min(100, rating_attuale + aumento) if rating_attuale > 0 else min(livello, random.randint(5, 15))
        skill_attuali[skill_id] = nuovo_rating
        guadagni[skill_id] = nuovo_rating - rating_attuale
        contenuto[skill_id] = max(0, livello - aumento)

    personaggio.db.skills = skill_attuali
    cristallo.db.cristallo_skill = {k: v for k, v in contenuto.items() if v > 0}

    if not guadagni:
        penalita = "" if e_yithiano else " (le tue origini non-Yithiane rendono il cristallo quasi inerte per te)"
        return True, f"Il cristallo pulsa, ma non riesci ad assorbire nulla di utile stavolta{penalita}."

    from world.skills import nome_skill
    righe = ["Frammenti di conoscenza altrui si riversano nella tua mente:"]
    for sid, delta in guadagni.items():
        righe.append(f"  {nome_skill(sid)} +{delta} (ora {skill_attuali[sid]}%)")
    return True, "\n".join(righe)
