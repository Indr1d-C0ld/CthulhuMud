"""
Palette colori a tema lovecraftiano (Fase K, pre-release, punto 8 della
checklist dell'utente). Scelta di design esplicita, approvata
dall'utente prima dell'implementazione (nessuna fonte originale
descrive una palette): quattro famiglie semantiche, ciascuna sul
sistema Xterm256 di Evennia (tag |RGB con cifre 0-5) per ottenere toni
precisi non disponibili negli 8 colori ANSI di base.

- ORRORE_MAGIA: verde tossico/spettrale, per gli effetti del Mythos e
  per la magia (stessa famiglia cromatica per entrambi, come da
  indicazione dell'utente).
- DREAMLANDS: viola/indaco, per l'ambientazione onirica.
- PERICOLO: rosso cupo, per combattimento e situazioni di pericolo.
- AMBIENTE: grigio/ciano smorzato, per testo atmosferico/descrittivo
  non legato a un evento specifico (battute ambientali dei mostri,
  descrizioni di orario/meteo, ecc.).

Applicata finora solo a un sottoinsieme rappresentativo di messaggi
(vedi world/combat.py, world/sanita.py, world/magic.py,
world/dreamlands.py, world/mostri_movimento.py) in attesa di conferma
dell'utente dopo una demo dal vivo, prima di estenderla a tutto il
gioco.
"""

ORRORE_MAGIA = "|140"
DREAMLANDS = "|304"
PERICOLO = "|300"
AMBIENTE = "|233"
RESET = "|n"


def colora(testo, colore):
    return f"{colore}{testo}{RESET}"


def orrore(testo):
    return colora(testo, ORRORE_MAGIA)


def magia(testo):
    return colora(testo, ORRORE_MAGIA)


def onirico(testo):
    return colora(testo, DREAMLANDS)


def pericolo(testo):
    return colora(testo, PERICOLO)


def ambiente(testo):
    return colora(testo, AMBIENTE)
