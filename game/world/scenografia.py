"""
Oggetti di scena (Fase I, prima tornata): dettagli d'arredo esaminabili
ma non reali oggetti raccoglibili/in vendita.

Confermato dalla fonte (immhelp_roombuilding.txt, sezione "ED" - Extra
Descriptions): "This is where you make your money as a builder.
Extended descriptions add depth and flavor to your rooms. Players,
especially those exploring your area for the first time, will want to
look around and examine everything. Prominent features in your room
description should be given their own extended description... There
can be, and often warranted, multiple keywords for an extended
description" (l'esempio della fonte: "memo" e "pads" come sinonimi
dello stesso ED). Lato giocatore, EXAMINE e' confermato sinonimo di
LOOK (helps/look.txt, helps/examine.txt).

Storage: room.db.eds = [{"parole": [...], "testo": "..."}, ...] - una
lista di voci, ciascuna con una o piu' parole chiave che puntano allo
stesso testo, esattamente come il modello a sinonimi della fonte.
"""


def trova_ed(stanza, parola):
    """Cerca parola (case-insensitive) tra le parole chiave di ogni ED
    della stanza. Ritorna il testo se trovato, altrimenti None."""
    if not stanza or not stanza.db.eds:
        return None
    parola = parola.strip().lower()
    for voce in stanza.db.eds:
        if parola in (p.lower() for p in voce.get("parole", [])):
            return voce.get("testo")
    return None


def aggiungi_ed(stanza, parole, testo):
    """Aggiunge un ED alla stanza (parole: lista di stringhe). Se una
    delle parole coincide con un ED gia' esistente, quella voce viene
    sovrascritta (stesso comportamento di ED CHANGE nella fonte)."""
    eds = stanza.db.eds or []
    parole_lower = [p.lower() for p in parole]
    eds = [v for v in eds if not any(p.lower() in parole_lower for p in v.get("parole", []))]
    eds.append({"parole": list(parole), "testo": testo})
    stanza.db.eds = eds


def rimuovi_ed(stanza, parola):
    """Rimuove l'ED che contiene parola. Ritorna True se ne ha rimosso uno."""
    eds = stanza.db.eds or []
    parola = parola.strip().lower()
    nuovi = [v for v in eds if parola not in (p.lower() for p in v.get("parole", []))]
    if len(nuovi) == len(eds):
        return False
    stanza.db.eds = nuovi
    return True


def elenca_eds(stanza):
    """Lista di (parole, testo) per ogni ED della stanza - usata da ED LIST."""
    return [(v.get("parole", []), v.get("testo", "")) for v in (stanza.db.eds or [])]
