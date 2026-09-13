"""
Orologio di gioco e orari dei negozi (Fase K, quindicesima tornata):
confermato dalla fonte come meccanica reale, non semplice colore.
helps/time.txt: "The TIME command displays the current game time, the
time at which the MUD was last started, and the current local time of
the host computer." helps/buy.txt/list.txt/sell.txt (gruppo comandi
negozio): "The HOURS command will show you when the shop is open."

Riusa l'orologio di gioco NATIVO di Evennia (evennia.utils.gametime,
governato da settings.TIME_FACTOR - vedi server/conf/settings.py per
la scelta del valore) invece di costruire uno Script separato da
zero: e' esattamente lo strumento pensato per questo, persistente tra
i reload.

Gli orari dei singoli negozi di Arkham (stringhe come "9am-9pm",
"8pm-4am", "Always Open") vengono dal catalogo ufficiale gia' raccolto
in world/arkham_catalog.py e agganciati alla STANZA (non al mercante,
cosi' i moduli di popolamento negozi restano intatti) in
world/rooms_arkham_edifici.py:_get_or_create_building(). I negozi di
Cairo e Zoog Village non hanno mai avuto orari nella fonte raccolta
finora (guides_cairo.txt e' solo descrittivo, senza la tabella
indirizzi/orari che ha invece guides_arkham) - restano quindi sempre
aperti (db.orari assente = nessun vincolo): e' onesta' sui dati
mancanti, non un'invenzione.
"""

from datetime import datetime

from evennia.utils import gametime


def ora_di_gioco():
    """Ora corrente di gioco (0-23), dall'orologio nativo di Evennia."""
    return datetime.fromtimestamp(gametime.gametime(absolute=True)).hour


def _ora_a_24h(testo):
    """'9am' -> 9, '10pm' -> 22, '12am' -> 0, '12pm' -> 12,
    'Midnight' -> 0, 'Noon' -> 12 (formati osservati in
    world/arkham_catalog.py)."""
    testo = testo.strip().lower()
    if testo == "midnight":
        return 0
    if testo == "noon":
        return 12
    meridiano = testo[-2:]
    numero = int(testo[:-2])
    if meridiano == "am":
        return 0 if numero == 12 else numero
    return 12 if numero == 12 else numero + 12


def _parse_orari(orari):
    """Ritorna (apertura, chiusura) in ore 0-23, o None se il negozio
    non ha vincoli orari (sempre aperto, o nessun dato dalla fonte)."""
    if not orari or orari.strip().lower() == "always open":
        return None
    apertura_testo, chiusura_testo = orari.split("-")
    return _ora_a_24h(apertura_testo), _ora_a_24h(chiusura_testo)


def negozio_aperto(stanza, ora=None):
    """True se il negozio nella stanza data e' aperto all'ora di gioco
    corrente (o a `ora`, 0-23, se specificata - usato dai test).
    Nessun db.orari sulla stanza = sempre aperto."""
    if not stanza:
        return True
    intervallo = _parse_orari(stanza.db.orari)
    if intervallo is None:
        return True
    apertura, chiusura = intervallo
    ora = ora_di_gioco() if ora is None else ora
    if apertura <= chiusura:
        return apertura <= ora < chiusura
    return ora >= apertura or ora < chiusura  # attraversa la mezzanotte (es. 8pm-4am)


def descrivi_orari(stanza):
    """Messaggio del comando HOURS per il negozio nella stanza data."""
    orari = stanza.db.orari if stanza else None
    if not orari or orari.strip().lower() == "always open":
        return "Aperto a qualunque ora."
    apertura, chiusura = _parse_orari(orari)
    stato = "Aperto ora." if negozio_aperto(stanza) else "Chiuso ora."
    return f"Aperto dalle {apertura}:00 alle {chiusura}:00 (ora di gioco). {stato}"
