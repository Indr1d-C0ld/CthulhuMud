"""
WORSHIP/SACRIFICE (Fase K, ventisettesima tornata): confermato dalla
scansione esaustiva (helps/sacrifice.txt/worship.txt/piety.txt, tutti
alias della stessa pagina canonica "SACRIFICE / WORSHIP") come un
sistema mai costruito in questo porting, nonostante fosse gia' citato
di striscio (professioni "priest_of_*", allineamento, world/pk.py:
AUTOSAC dichiarato "fuori scope perche' dipende da WORSHIP").

Confermato dalla fonte:
- SACRIFICE <oggetto> offre un oggetto alla divinita' che si adora
  attualmente, che PUO' (non deve) ricompensare l'offerta. Diverso da
  OFFER: non richiede un altare/idolo fisico (vedi sotto).
- AUTOSAC (gia' tracciato come toggle in world/pk.py/commands/
  cthulhu_pk.py) sacrifica automaticamente il cadavere di ogni NPC
  ucciso - ma questi sacrifici automatici NON contano per la pieta'.
- SACRIFICE ALL sacrifica tutto quello che si porta addosso.
- WORSHIP mostra le divinita' disponibili con il loro allineamento;
  WORSHIP <divinita> cambia fede; WORSHIP INFO <divinita> mostra i
  dettagli.
- La divinita' adorata e la pieta' attuale compaiono su SCORE. La
  pieta' cresce sacrificando oggetti di valore (non da AUTOSAC), e
  cresce lentamente per design ("do not get discouraged by slow
  progress" - nessuna cifra esatta dalla fonte).
- Il "mana pool" della divinita' cresce con i sacrifici regolari
  (anche automatici).

NON specificato dalla fonte: l'elenco esatto delle divinita' attive
(la fonte dice solo "use WIZLIST" per vederle - un elenco DINAMICO
legato a quali membri dello staff impersonano attivamente un dio nel
gioco originale, un concetto non riproducibile in questo porting su
scala ridotta). Scelta di design dichiarata: qui il roster e' quello
gia' stabilito dalle professioni "priest_of_*" gia' esistenti in
world/professions_avanzate.py (Bast, Dagon, Foxbird, Marduk,
Shub-Niggurath, Thanatos, Yog-Sothoth) - non se ne inventano di nuove,
si riusa solo cio' che il porting aveva gia' dichiarato. Allineamenti
assegnati per coerenza tematica col Mythos e con le descrizioni di
professione gia' esistenti (es. Marduk e' esplicitamente l'eroe
anti-Cthulhu dei "Guerrieri della Luce", vedi world/societies.py).

Deliberatamente NON implementato in questa tornata (dichiarato, non
dimenticato): OFFER/PRAY (helps/offer.txt/pray.txt) - richiedono
altari/idoli fisici piazzati nel mondo per ogni divinita', il
tracciamento delle "imprese" (deed) legate a offerte specifiche per le
professioni sacerdotali, e soprattutto "an active God or Goddess will
[occasionally] make a personal response to a prayer" - una meccanica
che nella fonte presume literalmente un membro dello staff che
impersona quel dio e risponde a mano. Costruire un sostituto
automatico credibile per questo e' un sistema a se stante, non una
semplice estensione di SACRIFICE/WORSHIP.
"""

import random

from world.colori import orrore

DIVINITA = {
    "bast": {
        "nome": "Bast",
        "allineamento": 400,
        "descrizione": "La Dea gattesca dell'Antico Egitto, protettrice silenziosa "
                       "di chi cammina nell'ombra con grazia e astuzia.",
    },
    "marduk": {
        "nome": "Marduk",
        "allineamento": 700,
        "descrizione": "Il Dio guerriero che uccise Tiamat: eroe dei Guerrieri della "
                       "Luce, attende il giorno in cui Grande Cthulhu si risvegliera'.",
    },
    "foxbird": {
        "nome": "Foxbird",
        "allineamento": 0,
        "descrizione": "Il Dio della Magia, patrono di chi cerca la conoscenza "
                       "arcana per la conoscenza stessa, senza fedelta' a bene o male.",
    },
    "thanatos": {
        "nome": "Thanatos",
        "allineamento": 0,
        "descrizione": "Il custode del ciclo naturale della vita e della morte: "
                       "non premia ne' punisce chi vive e muore secondo natura.",
    },
    "dagon": {
        "nome": "Dagon",
        "allineamento": -700,
        "descrizione": "Il Dio dei Profondi, venerato a Innsmouth: promette potere "
                       "a chi accetta di mescolare il proprio sangue col mare.",
    },
    "shub_niggurath": {
        "nome": "Shub-Niggurath",
        "allineamento": -800,
        "descrizione": "La Capra Nera dei Boschi dai Mille Cuccioli: fertilita' "
                       "mostruosa e proliferazione senza fine, indifferente all'ordine.",
    },
    "yog_sothoth": {
        "nome": "Yog-Sothoth",
        "allineamento": -600,
        "descrizione": "Colui-che-e'-la-Porta: onnisciente e alieno, la sua "
                       "conoscenza proibita corrompe chi la insegue troppo a lungo.",
    },
}

SOGLIA_RICOMPENSA_VALORE = 30
PROBABILITA_RICOMPENSA = 15  # % - non specificato dalla fonte
GUADAGNO_MANA_DIVINITA_PER_SACRIFICIO = (1, 5)


def nome_divinita(divinita_id):
    entry = DIVINITA.get(divinita_id)
    return entry["nome"] if entry else divinita_id


def adora(personaggio, divinita_id):
    """WORSHIP <divinita>: cambia allegianza. Cambiare divinita' non
    azzera la pieta' accumulata (nessuna indicazione contraria dalla
    fonte) ma la pieta' e' comunque intesa come fedelta' alla divinita'
    ATTUALE, quindi qui viene azzerata per coerenza - scelta di design
    dichiarata, dato che la fonte non specifica il comportamento."""
    if divinita_id not in DIVINITA:
        return False, "Divinita' sconosciuta."
    personaggio.db.divinita = divinita_id
    personaggio.db.pieta = 0
    return True, orrore(f"Ora adori {nome_divinita(divinita_id)}.")


def _mana_divinita(divinita_id):
    from evennia.server.models import ServerConfig
    return ServerConfig.objects.conf(f"worship_mana_{divinita_id}", default=0)


def _cresci_mana_divinita(divinita_id, quantita):
    from evennia.server.models import ServerConfig
    attuale = _mana_divinita(divinita_id)
    ServerConfig.objects.conf(f"worship_mana_{divinita_id}", attuale + quantita)


def sacrifica(personaggio, oggetto, automatico=False):
    """SACRIFICE <oggetto>. Se automatico=True (AUTOSAC su un cadavere
    di NPC), il sacrificio non aumenta la pieta' (confermato dalla
    fonte: "Items that are automatically sacrificed... do not help
    your piety") ma alimenta comunque il mana della divinita'."""
    divinita_id = personaggio.db.divinita
    if not divinita_id:
        return False, "Non adori nessuna divinita': usa WORSHIP <divinita> per sceglierne una."
    if oggetto is personaggio:
        return False, "Non puoi sacrificare te stesso."
    # Ultimo argine (audit totale): SACRIFICE cerca solo nell'inventario, ma
    # questa funzione e' chiamata anche da altri percorsi (AUTOSAC sui
    # cadaveri) e cancella cio' che riceve. Un essere vivente, una stanza o
    # un'uscita non devono mai poterci arrivare - vedi lo stesso difetto,
    # reale, trovato in world/magic.py:_rischio_distrugge_oggetto.
    from world.magic import e_oggetto_inanimato
    if not e_oggetto_inanimato(oggetto):
        return False, f"{getattr(oggetto, 'key', 'Quello')} non e' qualcosa che si possa sacrificare."

    valore = getattr(oggetto.db, "valore", None)
    if not valore:
        valore = 1
    nome_oggetto = oggetto.key
    oggetto.delete()

    _cresci_mana_divinita(divinita_id, random.randint(*GUADAGNO_MANA_DIVINITA_PER_SACRIFICIO))

    if automatico:
        return True, orrore(f"{personaggio.key} sacrifica {nome_oggetto} a {nome_divinita(divinita_id)}.")

    personaggio.db.pieta = (personaggio.db.pieta or 0) + valore
    messaggio = f"Sacrifichi {nome_oggetto} a {nome_divinita(divinita_id)} (pieta' ora {personaggio.db.pieta})."

    allineamento_pg = personaggio.db.alignment or 0
    allineamento_divinita = DIVINITA[divinita_id]["allineamento"]
    stesso_verso = (allineamento_pg >= 0) == (allineamento_divinita >= 0)
    if (
        valore >= SOGLIA_RICOMPENSA_VALORE
        and stesso_verso
        and random.randint(1, 100) <= PROBABILITA_RICOMPENSA
    ):
        ricompensa = random.randint(valore // 2, valore)
        personaggio.db.gold = (personaggio.db.gold or 0) + ricompensa
        messaggio += f" {nome_divinita(divinita_id)} gradisce l'offerta: ricevi {ricompensa} oro."

    return True, orrore(messaggio)


def sacrifica_automatico_cadavere(uccisore, cadavere):
    """AUTOSAC (world/pk.py:db.autosac): da chiamare alla morte di un
    NPC se l'uccisore ha il toggle attivo. Non fa nulla se l'uccisore
    non adora ancora nessuna divinita' (silenzioso, come un AUTO*
    disattivo - niente da forzare)."""
    if not uccisore.db.divinita:
        return False
    ok, _ = sacrifica(uccisore, cadavere, automatico=True)
    return ok


def info_divinita(divinita_id):
    entry = DIVINITA.get(divinita_id)
    if not entry:
        return None
    return (
        f"|w{entry['nome']}|n\n\n{entry['descrizione']}\n\n"
        f"Allineamento: {entry['allineamento']}\n"
        f"Mana della divinita' (da sacrifici recenti): {_mana_divinita(divinita_id)}"
    )
