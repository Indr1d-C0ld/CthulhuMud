"""
Sistema di imprese/deed (Fase K, prima tornata).

Confermato dalla fonte (helps/deed.txt = helps/quest.txt =
helps/quests.txt: la stessa identica pagina "DEED / QUEST"): il
comando DEED elenca le imprese compiute da un personaggio nella sua
vita. Esistono tre livelli di visibilita': Segrete (invisibili anche a
chi le ha compiute - "most often used as controlling mechanisms in
quests"), Private (visibili solo al proprio giocatore) e Pubbliche
(visibili a chiunque usi DEED su quel personaggio) - DEED BRAG rende
pubblica un'impresa privata. Le imprese buone sono elencate in verde,
quelle cattive in rosso nella fonte (qui riprodotto come campo
"allineamento": "buono"/"cattivo"/None per neutro/non specificato).

I 18 ID di imprese referenziati come condizione d'accesso dalle
professioni avanzate (world/professions_avanzate.py, campo "imprese")
sono stati confermati uno per uno nella fonte: ogni tabella dei
requisiti in info_profs.txt riporta anche il titolo e il numero reale
della deed (es. "Deed 59 - Something has awakened within!"). Il
REGISTRO_IMPRESE qui sotto usa quindi titoli tradotti VERBATIM dalla
fonte, non inventati - solo la visibilita'/allineamento (non
specificati dalla fonte per questi 18 casi) sono scelte di design
ragionevoli. Le tappe per OTTENERE ciascuna impresa (le quest vere e
proprie) sono un'altra questione: vedi world/quest.py.
"""

import time

# {deed_id: (titolo_verbatim_dalla_fonte, visibilita', allineamento)}
# visibilita': "pubblico" | "privato" | "segreto"
REGISTRO_IMPRESE = {
    "deed_56": ("Laureato alla Miskatonic University", "pubblico", None),
    "deed_57": ("Sacerdote di Marduk", "pubblico", "cattivo"),
    "deed_59": ("Qualcosa si e' risvegliato dentro di te!", "pubblico", None),
    "deed_60": ("Ha completato un capolavoro", "pubblico", None),
    "deed_81": ("Supporto da Ammiraglio per la Scuola Ufficiali", "pubblico", None),
    "deed_82": ("Ha risolto il suo primo caso", "pubblico", None),
    "deed_83": ("Andato oltre le frontiere della natura umana", "privato", "cattivo"),
    "deed_84": ("Apprendista Druido", "pubblico", None),
    "deed_85": ("Avatar del Sole", "pubblico", "buono"),
    "deed_86": ("Avatar di Dagon", "pubblico", "cattivo"),
    "deed_1309": ("Sacerdote di Yog-Sothoth", "pubblico", "cattivo"),
    "deed_1319": ("Sacerdote di Dagon", "pubblico", "cattivo"),
    "deed_1329": ("Sacerdote di Shub-Niggurath", "pubblico", "cattivo"),
    "deed_3796": ("Ha compiuto un sacrificio degno a Thanatos", "privato", "cattivo"),
    "deed_4316": ("Ha completato un Sentiero degli Eletti", "pubblico", None),
    "deed_9004": ("Seguace di Bast", "pubblico", None),
    "deed_9061": ("Si e' dimostrato/a valoroso/a in combattimento", "pubblico", "buono"),
    "deed_9071": ("Cavaliere di Ulthar!", "pubblico", "buono"),
}


def assegna_impresa(personaggio, deed_id):
    """Concede un'impresa a personaggio, se non gia' posseduta. Ritorna
    True se e' stata appena concessa, False se gia' presente o
    sconosciuta."""
    if deed_id not in REGISTRO_IMPRESE:
        return False
    imprese = personaggio.db.imprese or set()
    if deed_id in imprese:
        return False
    imprese.add(deed_id)
    personaggio.db.imprese = imprese
    dettagli = personaggio.db.deed_dettagli or {}
    dettagli[deed_id] = {"quando": time.time(), "resa_pubblica": False}
    personaggio.db.deed_dettagli = dettagli
    return True


def elenco_imprese(personaggio, per_altri=False):
    """Ritorna [(deed_id, titolo, visibilita', allineamento), ...] delle
    imprese di personaggio. Se per_altri=True (DEED <character> usato
    da un altro giocatore), esclude le Segrete e le Private non rese
    pubbliche con BRAG."""
    imprese = personaggio.db.imprese or set()
    dettagli = personaggio.db.deed_dettagli or {}
    risultato = []
    for deed_id in imprese:
        voce = REGISTRO_IMPRESE.get(deed_id)
        if not voce:
            continue
        titolo, visibilita, allineamento = voce
        resa_pubblica = dettagli.get(deed_id, {}).get("resa_pubblica", False)
        if per_altri:
            if visibilita == "segreto":
                continue
            if visibilita == "privato" and not resa_pubblica:
                continue
        risultato.append((deed_id, titolo, visibilita, allineamento))
    return risultato


def rendi_pubblica(personaggio, deed_id):
    """DEED BRAG <numero>: rende pubblica un'impresa privata. Ritorna
    (ok, messaggio)."""
    imprese = personaggio.db.imprese or set()
    if deed_id not in imprese:
        return False, "Non hai compiuto questa impresa."
    voce = REGISTRO_IMPRESE.get(deed_id)
    if not voce:
        return False, "Impresa sconosciuta."
    titolo, visibilita, _ = voce
    if visibilita == "segreto":
        return False, "Questa impresa non puo' essere resa pubblica."
    dettagli = personaggio.db.deed_dettagli or {}
    dettagli.setdefault(deed_id, {})["resa_pubblica"] = True
    personaggio.db.deed_dettagli = dettagli
    return True, f"La tua impresa \"{titolo}\" e' ora pubblica."
