"""
Sistema di equipaggiamento (Fase F, decima tornata): WEAR/WIELD reali,
con effetti meccanici in combattimento, non solo economici/di
ambientazione. Vedi world/popola_negozi.py per la nota generale sulla
fase precedente (solo economia) e la ricerca da cui nasce questa
milestone (guides_newbieschool/guides_equipment sul sito originale).

Confermato dalla fonte originale:
- WEAR (armatura/vestiti) e WIELD (armi) sono comandi distinti, con
  EQUIPMENT/EQ a mostrare cosa e' indossato/impugnato.
- L'efficacia in combattimento dipende dalla skill legata al TIPO di
  arma ("it doesn't matter which weapon you prefer, as long as you're
  good at whichever one you're carrying"), non dall'arma in se'.
- Gli oggetti hanno un livello massimo d'uso (fino a 10 livelli sopra
  il proprio), estendibile con "talent raising items".
- L'equipaggiamento si deteriora e va riparato (REPAIR/FIX).

NON specificato dalla fonte (scelte di design esplicite, come per le
formule di combattimento in typeclasses/living.py):
- Lo slot esatto per ogni tipo di oggetto (qui: arma, scudo, testa,
  corpo, mani, gambe, piedi, amuleto - un sottoinsieme ragionevole,
  non i ~20 e piu' slot di molti MUD Diku-derivati).
- Le formule numeriche di danno arma / classe armatura / degrado.
- Se REPAIR richieda un fabbro o sia self-service: qui e' self-service
  ovunque, a pagamento in Oro proporzionale al danno da riparare.
"""

import random

from world.skills import SKILLS

# Slot disponibili. "arma" e' l'unico slot di WIELD; il resto e' WEAR.
SLOT_ARMA = "arma"
SLOTS = {
    "arma": "impugnato in mano",
    "scudo": "portato come scudo",
    "testa": "indossato in testa",
    "corpo": "indossato sul corpo",
    "mani": "indossato sulle mani",
    "gambe": "indossato sulle gambe",
    "piedi": "indossato ai piedi",
    "amuleto": "indossato come amuleto",
}

CONDIZIONE_INIZIALE = 100
LIVELLO_MASSIMO_RELATIVO = 10   # puoi usare oggetti fino a 10 livelli sopra il tuo
COSTO_RIPARAZIONE_PER_PUNTO = 1  # oro per punto di condizione da recuperare


def nome_slot(slot):
    return SLOTS.get(slot, slot)


def e_arma(oggetto):
    return bool(oggetto and oggetto.db.slot == SLOT_ARMA)


def e_equipaggiabile(oggetto):
    return bool(oggetto and oggetto.db.slot in SLOTS)


def puo_equipaggiare(personaggio):
    """Alcune razze (Shoggoth) non hanno slot per l'equipaggiamento: solo
    combattimento a mani nude (vedi world/races.py)."""
    from world.races import RACES
    razza = RACES.get(getattr(personaggio.db, "race", None), {})
    return not razza.get("niente_equipaggiamento", False)


def livello_effettivo(personaggio):
    """Livello per i controlli di utilizzo oggetti: livello base del
    personaggio + bonus di eventuali 'talent raising items' indossati."""
    base = personaggio.livello_per_equip()
    bonus = sum(
        (obj.db.bonus_livello_equip or 0)
        for obj in (personaggio.db.equip or {}).values()
        if obj
    )
    return base + bonus


def puo_usare_oggetto(personaggio, oggetto):
    """Controlla il livello massimo d'uso (fino a 10 livelli sopra il
    proprio, esteso da eventuali talent raising items gia' indossati)."""
    richiesto = oggetto.db.livello or 1
    return livello_effettivo(personaggio) + LIVELLO_MASSIMO_RELATIVO >= richiesto


def condizione_di(oggetto):
    if oggetto.db.condizione is None:
        return CONDIZIONE_INIZIALE
    return oggetto.db.condizione


def descrizione_condizione(oggetto):
    c = condizione_di(oggetto)
    if c <= 0:
        return " |r(rotto)|n"
    if c < 30:
        return " |r(molto danneggiato)|n"
    if c < 70:
        return " |y(danneggiato)|n"
    return ""


def degrada(oggetto, quantita=None):
    """Consuma un po' di condizione dell'oggetto per l'uso in combattimento.
    Un oggetto rotto (condizione 0) resta equipaggiato ma non da' piu'
    alcun bonus, finche' non viene riparato."""
    if not e_equipaggiabile(oggetto):
        return
    quantita = quantita if quantita is not None else random.randint(0, 2)
    attuale = condizione_di(oggetto)
    nuova = max(0, attuale - quantita)
    if attuale > 0 and nuova == 0 and oggetto.location:
        oggetto.location.msg_contents(f"{oggetto.key} si rompe!")
    oggetto.db.condizione = nuova


def costo_riparazione(oggetto):
    """Costo in Oro per riportare l'oggetto alla condizione massima (senza
    applicare nulla): usato per controllare che il giocatore possa pagare
    prima di eseguire davvero la riparazione."""
    mancante = CONDIZIONE_INIZIALE - condizione_di(oggetto)
    return mancante * COSTO_RIPARAZIONE_PER_PUNTO


def ripara(oggetto):
    """Applica la riparazione (condizione al massimo). Chiamare solo dopo
    aver gia' verificato/scalato il costo da costo_riparazione()."""
    oggetto.db.condizione = CONDIZIONE_INIZIALE


def bonus_arma_attivo(oggetto):
    """Un'arma rotta non da' piu' il proprio bonus di danno."""
    return e_arma(oggetto) and condizione_di(oggetto) > 0


def classe_armatura_totale(personaggio):
    """Somma la classe armatura di tutti i pezzi indossati (non rotti),
    piu' l'eventuale aura di VAMPIRE MAJESTY (world/sottorazze.py,
    Fase K ventiseiesima tornata - prima un campo mai letto da nessuno)."""
    totale = 0
    for slot, obj in (personaggio.db.equip or {}).items():
        if obj and slot != SLOT_ARMA and condizione_di(obj) > 0:
            totale += obj.db.classe_armatura or 0
    totale += getattr(personaggio.db, "classe_armatura_maesta", 0) or 0
    return totale


def arma_equipaggiata(personaggio):
    return (personaggio.db.equip or {}).get(SLOT_ARMA)


def skill_arma(personaggio):
    """La skill di competenza per l'arma impugnata (se esiste e non e'
    rotta), altrimenti None: il chiamante ricadra' su 'hand_to_hand'."""
    arma = arma_equipaggiata(personaggio)
    if arma and bonus_arma_attivo(arma) and arma.db.tipo_arma in SKILLS:
        return arma.db.tipo_arma
    return None
