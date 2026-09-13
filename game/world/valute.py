"""
Cinque valute regionali (Fase K, ventisettesima tornata): confermato
dalla fonte (helps/money.txt, alias identico di dollars.txt/gold.txt/
crowns.txt/copper.txt/yuggos.txt) che l'Oro usato ovunque in questo
porting fin dalla Fase F e' in realta' solo UNA delle cinque valute
della fonte:

    "DOLLARS are used in most areas of the Waking World, GOLD is used
    in certain civilized areas of the Dreamlands (such as Ulthar),
    CROWNS are used almost exclusively in the city of Dylath-Leen,
    COPPER is used in many non-human areas, and YUGGOS are used in
    areas controlled by the Mi-Go."

MONEY/WORTH mostra tutte e cinque; la SCORE SHEET mostra solo quella
"di default" della zona in cui ci si trova al momento - "This does not
change how much money you actually have", solo cosa viene mostrato.

Scelta di design dichiarata per non riscrivere da capo i ~27 punti del
codice che gia' usano `db.gold` (negozi, banca, taglie, quote clan,
ecc., tutti gia' corretti e testati): l'Oro (db.gold, gia' esistente)
resta la valuta "oro" della fonte senza alcuna modifica ai chiamanti
esistenti; le altre quattro sono NUOVI campi (db.dollari/db.corone/
db.rame/db.yuggos), realmente scambiabili in banca ma NON ancora
imposte come requisito d'acquisto nei negozi (vedi sotto).

Mappa zona -> valuta locale: nessuna fonte da' un elenco esaustivo
zona per zona, solo i 5 esempi sopra piu' l'esempio esplicito "DOLLARS
in Arkham, GOLD in Ulthar, CROWNS in Dylath-Leen" - qui estesa alle
altre zone gia' costruite in questo porting per analogia dichiarata
(Mi-Go=yuggos, aree non umane come Y'ha-nthlei/Villaggio degli
Zoog/Biblioteca Yithiana=rame, tutto il resto=dollari come "default
della maggior parte del Waking World").

Deliberatamente NON implementato in questa tornata (dichiarato, non
dimenticato): forzare i negozi ad accettare SOLO la valuta locale
("most shops will only accept the default currency of the area").
Farlo davvero avrebbe richiesto riscrivere ogni punto vendita gia'
costruito (world/economia.py e tutti i mercanti gia' popolati nelle
varie zone) per convertirli dall'Oro universale a valute specifiche
per zona - una migrazione di contenuto ad alto rischio di regressione,
sproporzionata rispetto a un audit di chiusura-gap. Qui si aggiunge il
sistema di valute REALE (possederle, vederle, cambiarle in banca), non
si smantella l'economia esistente basata sull'Oro.
"""

NOMI_VALUTE = {
    "dollari": "Dollari",
    "oro": "Oro",
    "corone": "Corone",
    "rame": "Rame",
    "yuggos": "Yuggos",
}

CAMPO_PER_VALUTA = {
    "dollari": "dollari",
    "oro": "gold",
    "corone": "corone",
    "rame": "rame",
    "yuggos": "yuggos",
}

# hub_id (world/rooms_newbie.py, categoria "start_room") e categorie di
# tag di zona (world/rooms_arkham.py, rooms_dreamlands_overworld.py,
# ecc.) mappate alla valuta locale di quella zona.
PREFISSI_VALUTA = {
    "dollari": ("arkham_miskatonic",),
    "oro": ("ulthar_temple",),
    "corone": ("dylath_reformatory",),
    "rame": ("yhanthlei", "zoog_village", "yithian_library"),
    "yuggos": ("migo_mothership", "yuggoth_training"),
}
CATEGORIE_VALUTA = {
    "dollari": ("arkham_street", "arkham_building", "cairo_room"),
    "oro": ("ulthar_room", "dreamlands_overworld"),
    "rame": ("zoogvillage_room", "submarine_room"),
}

VALUTA_DEFAULT = "dollari"  # "most areas of the Waking World"


def saldo(personaggio, valuta_id):
    campo = CAMPO_PER_VALUTA.get(valuta_id)
    if not campo:
        return 0
    return getattr(personaggio.db, campo, 0) or 0


def aggiungi(personaggio, valuta_id, quantita):
    campo = CAMPO_PER_VALUTA.get(valuta_id)
    if not campo:
        return
    setattr(personaggio.db, campo, saldo(personaggio, valuta_id) + quantita)


def valuta_locale(stanza):
    """La valuta di default della zona (helps/money.txt) - mostrata su
    SCORE, non necessariamente l'unica che si possiede."""
    if not stanza:
        return VALUTA_DEFAULT
    for valuta_id, tag_arrivo in PREFISSI_VALUTA.items():
        for tag in stanza.tags.get(category="start_room", return_list=True) or []:
            if isinstance(tag, str) and tag.startswith(tag_arrivo):
                return valuta_id
    for valuta_id, categorie in CATEGORIE_VALUTA.items():
        for categoria in categorie:
            if stanza.tags.get(category=categoria):
                return valuta_id
    return VALUTA_DEFAULT


def cambia_valuta(personaggio, valuta_da, valuta_a, quantita, tasso):
    """BANK EXCHANGE: nessun tasso esatto dalla fonte ("the exact
    exchange rate will vary from location to location") - il tasso e'
    passato dal chiamante (vedi commands/cthulhu_bank.py, dichiarato)."""
    if valuta_da not in NOMI_VALUTE or valuta_a not in NOMI_VALUTE:
        return False, "Valuta sconosciuta."
    if valuta_da == valuta_a:
        return False, "Non puoi cambiare una valuta con se stessa."
    if saldo(personaggio, valuta_da) < quantita:
        return False, f"Non hai {quantita} {NOMI_VALUTE[valuta_da]}."
    ricevuto = max(1, int(quantita * tasso))
    aggiungi(personaggio, valuta_da, -quantita)
    aggiungi(personaggio, valuta_a, ricevuto)
    return True, (
        f"Cambi {quantita} {NOMI_VALUTE[valuta_da]} in {ricevuto} {NOMI_VALUTE[valuta_a]} "
        f"(tasso {tasso})."
    )
