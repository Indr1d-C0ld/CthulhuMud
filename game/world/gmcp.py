"""
GMCP: dati fuori banda per i client MUD (fase 2 e 3 del lavoro
sull'interfaccia).

A COSA SERVE
------------
Un client come Mudlet non puo' disegnare una mappa leggendo il testo
delle stanze: gli serve un canale separato che gli dica, a ogni
spostamento, dove si trova il giocatore e quali uscite ci sono. Quel
canale e' GMCP (Generic MUD Communication Protocol), che Evennia
supporta gia' e che il nostro MSSP annuncia gia' come disponibile
(server/conf/mssp.py, "GMCP": "1").

Qui si manda quello che serve a due cose:

  Room.Info   - la stanza corrente: numero, nome, area, uscite. E'
                il pacchetto che il mapper generico di Mudlet (in stile
                IRE) si aspetta, con gli stessi nomi di campo.
  Char.Vitals - HP, mana, movimento e sanita' mentale, per le barre di
                stato del client.

COME EVENNIA FORMA IL NOME DEL PACCHETTO
----------------------------------------
session.msg(oob=("room_info", [], {...})) diventa il pacchetto GMCP
"Room.Info": evennia/server/portal/gmcp_utils.py trasforma gli
underscore in punti e mette le iniziali maiuscole. Non serve quindi
nessuna modifica a Evennia: basta scegliere il nome giusto.

UNA COSA DA SAPERE SULLA MAPPA
------------------------------
Nel nostro mondo il 54% delle uscite ha un nome proprio ("tribunale",
"navata", "fuori") invece di una direzione cardinale, e solo 69 stanze
su 239 hanno esclusivamente uscite cardinali. Mudlet dispone sulla
griglia le uscite cardinali e tratta le altre come "special exits":
restano cliccabili e utilizzabili per lo speedwalk, ma non vengono
posizionate geometricamente. E' una conseguenza di com'e' fatto il mondo
della fonte, non un limite di questo modulo: per questo le uscite
vengono mandate in DUE campi separati, cosi' il client puo' distinguerle
invece di doverle indovinare.
"""

# Direzioni che Mudlet sa disporre sulla griglia. Le chiavi sono i nomi
# italiani usati nel mondo, i valori le sigle che il mapper si aspetta.
DIREZIONI_CARDINALI = {
    "nord": "n", "n": "n",
    "sud": "s", "s": "s",
    "est": "e", "e": "e",
    "ovest": "w", "o": "w",
    "nordest": "ne", "nordovest": "nw",
    "sudest": "se", "sudovest": "sw",
    "su": "up", "giu": "down",
    "alto": "up", "basso": "down",
    "dentro": "in", "fuori": "out",
}

# tag di zona -> nome leggibile dell'area, per il pannello aree di Mudlet.
AREE = {
    "arkham_street": "Arkham - Vie",
    "arkham_building": "Arkham - Edifici",
    "arkham_location": "Arkham - Luoghi",
    "cairo_room": "Il Cairo",
    "submarine_room": "Relitto dello U-29",
    "ulthar_room": "Ulthar",
    "zoogvillage_room": "Villaggio degli Zoog",
    "dreamlands_overworld": "Dreamlands",
    "hub_alieno_room": "Aree non umane",
    "start_room": "Luoghi di partenza",
}


def _area_di(stanza):
    """Nome dell'area a cui appartiene la stanza, dai suoi tag."""
    for tag in stanza.tags.all(return_objs=True):
        nome = AREE.get(tag.db_category)
        if nome:
            return nome
    return "Altrove"


def dati_stanza(personaggio):
    """Il dizionario Room.Info per la stanza in cui si trova.

    Ritorna None se il personaggio non e' da nessuna parte (per esempio
    mentre e' scollegato).

    Campi:
      num       identificativo stabile della stanza (il dbref di Evennia)
      name      nome della stanza
      area      area di appartenenza
      exits     {direzione_mudlet: num} - solo le uscite cardinali, che
                Mudlet puo' disporre sulla griglia
      specials  {nome: num} - le uscite con nome proprio, che Mudlet
                gestisce come collegamenti speciali
    """
    stanza = personaggio.location
    if not stanza:
        return None

    cardinali, speciali = {}, {}
    for uscita in stanza.exits:
        if not uscita.destination:
            continue
        chiave = DIREZIONI_CARDINALI.get(uscita.key.lower())
        if chiave:
            cardinali[chiave] = uscita.destination.id
        else:
            speciali[uscita.key] = uscita.destination.id

    return {
        "num": stanza.id,
        "name": stanza.key,
        "area": _area_di(stanza),
        "exits": cardinali,
        "specials": speciali,
    }


def dati_vitali(personaggio):
    """Il dizionario Char.Vitals per le barre di stato del client."""
    return {
        "hp": personaggio.db.hp or 0,
        "maxhp": personaggio.db.hp_max or 0,
        "mana": personaggio.db.mana or 0,
        "maxmana": personaggio.db.mana_max or 0,
        "mv": personaggio.db.move or 0,
        "maxmv": personaggio.db.move_max or 0,
        "sanity": personaggio.db.sanity if personaggio.db.sanity is not None else 0,
        "maxsanity": personaggio.db.sanity_max or 100,
    }


def _invia(personaggio, nome_oob, dati):
    """Manda un pacchetto OOB a tutte le sessioni del personaggio.

    Silenzioso per chi non e' connesso o usa un client senza GMCP: il
    protocollo prevede che il client dichiari cosa supporta, e Evennia
    scarta da sola i pacchetti verso chi non li ha chiesti. Un errore
    qui non deve mai impedire un movimento, quindi si ingoia."""
    if dati is None:
        return
    try:
        sessioni = personaggio.sessions.all()
    except Exception:
        return
    for sessione in sessioni:
        try:
            sessione.msg(**{nome_oob: ((), dati)})
        except Exception:
            pass


def invia_stanza(personaggio):
    """Manda Room.Info. Da chiamare a ogni cambio di stanza."""
    _invia(personaggio, "room_info", dati_stanza(personaggio))


def invia_vitali(personaggio):
    """Manda Char.Vitals. Da chiamare quando HP/mana/movimento/sanita'
    cambiano in modo visibile."""
    _invia(personaggio, "char_vitals", dati_vitali(personaggio))


def invia_tutto(personaggio):
    """Entrambi i pacchetti: usata al login e dopo un teletrasporto."""
    invia_stanza(personaggio)
    invia_vitali(personaggio)
