"""
Il relitto dello U-29 ("Nightmare Submarine"), ricostruito dalla mappa
del sito ufficiale (submarine.gif, attribuita a "Morgan" nel Dossier
Miskatonic). E' un piccolo dungeon autoconclusivo: un U-Boot della
Grande Guerra affondato al largo della costa, coerente col tono anni
'20 del gioco.

Fedelta' alla mappa originale: tutti i 23 nomi di stanza, il punto di
partenza (Portside of the U-29), il punto di resurrezione dedicato
(Infirmary) e il cadavere fisso nel buio (Cramped Torpedo Tube Bow)
sono presi identici dalla mappa e tradotti in italiano.

Topologia dei collegamenti (CONNECTIONS) riletta e corretta il
2026-09-13 confrontando di nuovo, con attenzione, la mappa originale
("Nightmare Submarine", ghetto map di Morgan) - la prima stesura
(Fase F) aveva alcuni errori reali, non solo imprecisioni di dettaglio:
- Il tubo lanciasiluri d'uscita di poppa (21) era agganciato alla
  stanza 6 invece che alla 4 ("Tubi Lanciasiluri di Poppa") - la mappa
  mostra chiaramente la stessa struttura del lato prua (22 agganciato a
  11, "Tubi Lanciasiluri di Prua"): stesso nome, stessa logica, lato
  opposto.
- Mancava del tutto il collegamento 19-20 (Sala Motori Elettrici/Sala
  Compressori d'Aria): la sequenza delle sale motori 17-18-19-20 e'
  chiaramente una catena continua sulla mappa, non un vicolo cieco a 19.
- La direzione dell'intera dorsale centrale 8-10-11 era invertita
  (la mappa disegna 8, la Scaletta della Torretta di Comando - "diversi
  corridoi si diramano da questo punto" - SOPRA la stanza di partenza
  1, non sotto) - la prima stesura aveva la catena 1->7->8 quando in
  realta' e' 8->1->7.
- La Cambusa (14) si dirama da Sala Mensa (13, adiacenza logica
  cucina/mensa), non dallo snodo 8: le due ramificazioni erano state
  fuse per errore.
Rimangono scelte di lettura non certe al 100%, dichiarate qui: la
connessione 8-23 (Infermeria) e' trattata come corridoio laterale
(ovest) anziche' come cambio di ponte (su/giu), anche se la legenda
della mappa raggruppa l'Infermeria fra le stanze "Below" insieme alle
sale motori e ai tubi lanciasiluri d'uscita; la linea tratteggiata fra
15 e 16 sulla mappa e' trattata come un passaggio normale, non essendo
chiaro se indichi qualcosa di meccanicamente diverso (porta bloccata,
passaggio segreto). Se in futuro emergesse altro materiale sulla mappa,
questi due punti sono i primi da rivedere.

Non ancora collegato al resto del mondo di gioco (Arkham non esiste
ancora come stanze): le due boccaporte di uscita (21 e 22) portano a
un'unica stanza "acque aperte" in attesa che la costa di Arkham venga
costruita.
"""

from evennia.utils import create, search

TAG_CATEGORY = "submarine_room"

# numero_mappa -> (nome, descrizione)
ROOMS = {
    1: (
        "Lato di Sinistra dello U-29",
        "Il relitto giace inclinato sul fondale, e questo tratto di scafo "
        "e' quello meno danneggiato. E' da qui che chiunque si avventuri "
        "nel relitto finisce per ritrovarsi, senza sapere bene come.",
    ),
    2: (
        "Vano Biblioteca",
        "Scaffali di metallo arrugginito, un tempo pieni di manuali "
        "tecnici e mappe nautiche, ora ridotti a poltiglia di carta "
        "marcita.",
    ),
    3: (
        "Alloggio del Comandante",
        "Una cuccetta stretta, una scrivania avvitata al pavimento, un "
        "diario di bordo ormai illeggibile. Qualcosa qui dentro non "
        "vuole essere trovato.",
    ),
    4: (
        "Tubi Lanciasiluri di Poppa",
        "Due lunghi tubi metallici puntano verso l'oscurita' oltre lo "
        "scafo squarciato. Uno dei due sembra ancora carico.",
    ),
    5: (
        "Un Altro Stretto Corridoio",
        "Il corridoio si restringe ulteriormente qui, costringendo a "
        "muoversi di lato tra le lamiere contorte.",
    ),
    6: (
        "Sotto il Doppio Boccaporto",
        "Un boccaporto sopra la testa e' saldato dalla ruggine e non si "
        "apre. Qualunque cosa ci fosse sopra, e' rimasta lassu' per "
        "sempre.",
    ),
    7: (
        "Postazione del Timoniere",
        "La ruota del timone e' bloccata a meta' corsa, come se l'ultimo "
        "ordine impartito non fosse mai stato completato.",
    ),
    8: (
        "Scaletta della Torretta di Comando",
        "Una scaletta verticale arrugginita sale verso la torretta di "
        "comando. Diversi corridoi si diramano da questo punto.",
    ),
    9: (
        "Torretta di Comando",
        "Il periscopio e' piegato su se stesso, inutile. Da qui il "
        "comandante avrebbe dovuto vedere il nemico avvicinarsi.",
    ),
    10: (
        "Corridoio Stretto",
        "Un budello di metallo che corre lungo l'asse dello scafo, "
        "appena largo abbastanza per una persona alla volta.",
    ),
    11: (
        "Tubi Lanciasiluri di Prua",
        "I tubi di prua, ancora innescati. Meglio non toccare nulla che "
        "sembri un grilletto.",
    ),
    12: (
        "Alloggi dell'Equipaggio",
        "File di brande sovrapposte, alcune ancora stranamente rifatte, "
        "come se qualcuno si aspettasse di tornare a dormirci.",
    ),
    13: (
        "Sala Mensa",
        "Un tavolo lungo e stretto, piatti di latta sparsi sul "
        "pavimento inclinato. Il pasto e' rimasto incompiuto.",
    ),
    14: (
        "La Cambusa",
        "Fornelli arrugginiti e barattoli di conserve gonfi, pronti a "
        "esplodere al minimo urto.",
    ),
    15: (
        "Lato di Dritta dello U-29",
        "Lo scafo qui e' squarciato verso l'esterno: qualcosa e' uscito "
        "da questa falla, oppure qualcosa e' entrato.",
    ),
    16: (
        "Alloggi degli Ufficiali",
        "Piu' spaziosi delle brande dell'equipaggio, ma altrettanto "
        "vuoti. Un cappotto d'ordinanza pende ancora da un gancio.",
    ),
    17: (
        "Sala Motori Diesel",
        "Due enormi motori diesel, silenziosi da decenni, dominano "
        "questo ambiente stretto e claustrofobico.",
    ),
    18: (
        "Sala Batterie",
        "File di batterie corrose riempiono l'aria di un odore acre "
        "che non dovrebbe piu' esistere dopo tutto questo tempo.",
    ),
    19: (
        "Sala Motori Elettrici",
        "I motori elettrici di propulsione silenziosa, usati in "
        "immersione, sono ricoperti da un sottile strato di alghe "
        "fosforescenti.",
    ),
    20: (
        "Sala Compressori d'Aria",
        "I compressori che un tempo rifornivano d'aria l'intero "
        "equipaggio giacciono immobili, avvolti in un silenzio "
        "innaturale.",
    ),
    21: (
        "Angusto Tubo Lanciasiluri (Poppa)",
        "Uno stretto tubo lanciasiluri di poppa, abbastanza largo da "
        "farci passare una persona magra. L'acqua scura filtra da "
        "una fessura verso l'esterno.",
    ),
    22: (
        "Angusto Tubo Lanciasiluri (Prua)",
        "E' buio pesto qui dentro. Un cadavere giace rannicchiato "
        "contro la parete del tubo, da chissa' quanto tempo.",
    ),
    23: (
        "Infermeria",
        "Una branda di metallo con cinghie di contenimento occupa il "
        "centro della stanza. Chi muore nel relitto si risveglia "
        "sempre qui, senza sapere perche'.",
    ),
}

NOMI_PER_NUMERO = {num: nome for num, (nome, _desc) in ROOMS.items()}

# (numero_a, direzione_da_a_a_b, numero_b) - l'uscita di ritorno viene generata
# automaticamente nella direzione opposta.
CONNECTIONS = [
    # Cluster di prua, in cima alla mappa
    (11, "ovest", 12),
    (11, "est", 13),
    (11, "su", 22),        # boccaporto di prua, verso l'esterno
    (11, "sud", 10),
    (13, "sud", 14),
    (14, "sud", 15),
    (15, "sud", 16),
    # Corridoio centrale e scaletta della torretta di comando
    (10, "sud", 8),
    (10, "giu", 17),       # scaletta verso il ponte inferiore (sale motori)
    (8, "su", 9),          # scaletta verso la torretta di comando
    (8, "ovest", 23),
    (8, "sud", 1),
    # Dalla stanza di partenza verso poppa
    (1, "est", 7),
    (1, "sud", 2),
    (2, "sud", 3),
    (7, "sud", 6),
    (6, "sud", 4),
    (4, "est", 5),
    (4, "sud", 21),        # boccaporto di poppa, verso l'esterno
    (5, "giu", 20),
    # Ponte inferiore: sale motori in sequenza
    (17, "sud", 18),
    (18, "sud", 19),
    (19, "sud", 20),
]

OPPOSTA = {
    "nord": "sud", "sud": "nord",
    "est": "ovest", "ovest": "est",
    "su": "giu", "giu": "su",
}

START_ROOM_NUM = 1
RESURRECT_ROOM_NUM = 23
CORPSE_ROOM_NUM = 22
OUT_ROOM_NUMS = (21, 22)

WATERS_TAG = "submarine_waters"


# Fase K, sedicesima tornata (world/illuminazione.py): l'unica stanza
# gia' descritta nel testo come intrinsecamente buia ("E' buio pesto
# qui dentro") - le altre menzioni di buio nel porting sono su
# corridoi/cunicoli non visitabili oltre l'uscita, non sulla stanza
# corrente.
NUMERI_BUIO_PERMANENTE = (22,)


def _get_or_create_room(numero):
    """Trova la stanza del sommergibile numero <numero>, o la crea."""
    tag_key = f"sub_{numero}"
    existing = search.search_tag(tag_key, category=TAG_CATEGORY)
    if existing:
        room = existing[0]
        room.db.buio_permanente = numero in NUMERI_BUIO_PERMANENTE
        return room
    nome, descrizione = ROOMS[numero]
    room = create.create_object("typeclasses.rooms.Room", key=nome)
    room.db.desc = descrizione
    room.db.buio_permanente = numero in NUMERI_BUIO_PERMANENTE
    room.tags.add(tag_key, category=TAG_CATEGORY)
    return room


def _get_or_create_waters_room():
    """Stanza-placeholder delle acque aperte fuori dal relitto."""
    existing = search.search_tag(WATERS_TAG, category=TAG_CATEGORY)
    if existing:
        return existing[0]
    room = create.create_object("typeclasses.rooms.Room", key="Acque Scure al Largo della Costa")
    room.db.desc = (
        "Acqua nera e gelida in ogni direzione. In lontananza, appena "
        "visibile, si intuisce la sagoma spezzata di un vecchio "
        "sommergibile adagiato sul fondale. Verso nord-ovest, oltre le "
        "onde, si distinguono le luci dei Moli Passeggeri di Arkham."
    )
    room.tags.add(WATERS_TAG, category=TAG_CATEGORY)
    return room


def _get_or_create_exit(origine, destinazione, chiave, alias):
    """Crea un'uscita da origine a destinazione se non esiste gia'."""
    for obj in origine.exits:
        if obj.destination and obj.destination.id == destinazione.id:
            return obj
    return create.create_object(
        "typeclasses.exits.Exit",
        key=chiave,
        aliases=[alias] if alias else [],
        location=origine,
        destination=destinazione,
    )


def _collega_arkham(acque_room):
    """
    Collega le acque aperte del relitto ai Moli Passeggeri di Arkham
    (world/rooms_arkham_edifici.py), se quell'edificio esiste gia'.
    Idempotente; se Arkham non e' ancora stata costruita, non fa nulla
    e viene ritentato alla prossima chiamata di crea_sottomarino().
    """
    docks = search.search_tag("building_passenger_docks", category="arkham_building")
    if not docks:
        return
    docks_room = docks[0]

    _get_or_create_exit(docks_room, acque_room, "largo", "mare")
    _get_or_create_exit(acque_room, docks_room, "moli", "molo")


def crea_sottomarino():
    """
    Crea (se non esiste gia') l'intero relitto dello U-29: 23 stanze,
    tutti i collegamenti, la stanza delle acque aperte fuori dalle due
    boccaporte, il cadavere fisso nel tubo di prua, e il tag di
    resurrezione sull'infermeria. Idempotente.

    Ritorna il dizionario {numero: Room} di tutte le 23 stanze.
    """
    stanze = {numero: _get_or_create_room(numero) for numero in ROOMS}

    for num_a, direzione, num_b in CONNECTIONS:
        room_a = stanze[num_a]
        room_b = stanze[num_b]
        direzione_opposta = OPPOSTA[direzione]
        alias_a = direzione[0] if direzione not in ("su", "giu") else direzione
        alias_b = direzione_opposta[0] if direzione_opposta not in ("su", "giu") else direzione_opposta
        _get_or_create_exit(room_a, room_b, direzione, alias_a)
        _get_or_create_exit(room_b, room_a, direzione_opposta, alias_b)

    acque = _get_or_create_waters_room()
    for numero in OUT_ROOM_NUMS:
        stanza = stanze[numero]
        _get_or_create_exit(stanza, acque, "fuori", "fu")
        _get_or_create_exit(acque, stanza, f"dentro il relitto ({NOMI_PER_NUMERO[numero].lower()})", None)

    _collega_arkham(acque)

    resurrect_room = stanze[RESURRECT_ROOM_NUM]
    if not resurrect_room.tags.get("submarine_resurrect", category=TAG_CATEGORY):
        resurrect_room.tags.add("submarine_resurrect", category=TAG_CATEGORY)

    corpse_room = stanze[CORPSE_ROOM_NUM]
    cadavere_esistente = [
        obj for obj in corpse_room.contents
        if obj.tags.get("submarine_fixed_corpse", category=TAG_CATEGORY)
    ]
    if not cadavere_esistente:
        cadavere = create.create_object(
            "typeclasses.objects.Object",
            key="un vecchio cadavere",
            location=corpse_room,
        )
        cadavere.db.desc = (
            "I resti di un marinaio, rannicchiati contro la parete curva "
            "del tubo lanciasiluri. L'uniforme e' quasi del tutto "
            "disfatta. E' impossibile dire da quanto tempo sia qui."
        )
        cadavere.locks.add("get:false()")
        cadavere.tags.add("submarine_fixed_corpse", category=TAG_CATEGORY)

    return stanze
