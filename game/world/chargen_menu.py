"""
Menu di creazione personaggio (EvMenu) di CthulhuMUD ITA Redux.

Basato sul contrib evennia.contrib.rpg.character_creator: `caller` qui e'
la sessione di gioco, e `caller.new_char` e' il personaggio in corso di
creazione (vedi ContribCmdCharCreate).

Flusso: benvenuto -> scelta modalita' (guidata/preimpostato/casuale) ->
  - guidata: scelta razza -> scelta professione (filtrata per razza)
  - preimpostato: scelta di uno dei 16 personaggi pronti (world/
    personaggi_preimpostati.py, Fase K diciottesima tornata - aggiunta
    dichiaratamente NUOVA, non presente nella fonte)
  - casuale: professione/attributi/nome tirati a caso, con possibilita'
    di "rigenera" (world/generazione_casuale.py, stessa tornata)
-> scelta/conferma del nome -> conferma -> fine (spawn nella stanza di
RECALL).
"""

from django.conf import settings
from evennia.utils import dedent
from evennia.objects.models import ObjectDB

from typeclasses.characters import Character
from world.races import RACES
from world.professions_newbie import NEWBIE_PROFESSIONS
from world.personaggi_preimpostati import lista_preset, applica_preset, PRESET_NOME_M, PRESET_NOME_F
from world.generazione_casuale import genera_personaggio_casuale
from world.nomi_generazione import genera_descrizione_estesa


def _professioni_per_razza(race_id):
    return [pid for pid, prof in NEWBIE_PROFESSIONS.items() if prof["razza"] == race_id]


#########################################################
#                     Benvenuto
#########################################################

def menunode_welcome(caller):
    caller.new_char.db.chargen_step = "menunode_welcome"
    text = dedent("""\
        |wBenvenuto in CthulhuMud ITA Redux|n

        Stai per creare un personaggio nel Mythos di H.P. Lovecraft: un mondo
        di orrore cosmico, culti nascosti e conoscenza proibita, ambientato
        negli anni '20.

        Potrai interrompere e riprendere la creazione in qualsiasi momento
        con il comando |wcharcreate|n.
    """)
    options = {"desc": "Cominciamo!", "goto": "menunode_modalita"}
    return text, options


#########################################################
#                  Scelta Modalita'
#########################################################

def menunode_modalita(caller, raw_string="", **kwargs):
    caller.new_char.db.chargen_step = "menunode_modalita"
    text = dedent("""\
        |wCome vuoi creare il tuo personaggio?|n

        - |cGuidata|n: scegli tu, passo per passo, razza e professione di partenza.
        - |cPreimpostato|n: scegli tra 16 personaggi gia' pronti, uno per ogni
          professione di partenza - un aiuto rapido per chi vuole iniziare subito.
        - |cCasuale|n: razza, professione, attributi e nome vengono tirati a
          caso per te (puoi rigenerare finche' non sei soddisfatto/a).

        In ogni caso, alla fine potrai sempre scegliere o cambiare il nome.
    """)
    options = [
        {"desc": "Guidata", "goto": "menunode_razza"},
        {"desc": "Preimpostato", "goto": "menunode_preset_lista"},
        {"desc": "Casuale", "goto": _avvia_casuale},
    ]
    return text, options


#########################################################
#                    Scelta Razza
#########################################################

def menunode_razza(caller, raw_string="", **kwargs):
    caller.new_char.db.chargen_step = "menunode_razza"
    text = dedent("""\
        |wScelta della razza|n

        Ogni razza ha una propria lore e un proprio set di professioni di
        partenza disponibili. Scegline una per vederne la descrizione.
    """)
    options = []
    for race_id, race in RACES.items():
        options.append({
            "desc": f"|c{race['nome_plurale']}|n ({race['difficolta']})",
            "goto": ("menunode_info_razza", {"race_id": race_id}),
        })
    options.append({
        "key": ("(Indietro)", "indietro", "b"),
        "desc": "Torna alla scelta della modalita' di creazione",
        "goto": "menunode_modalita",
    })
    return text, options


def menunode_info_razza(caller, raw_string="", race_id=None, **kwargs):
    if not race_id or race_id not in RACES:
        return "menunode_razza"
    race = RACES[race_id]
    text = f"|w{race['nome_plurale']}|n\n\n{race['descrizione']}\n\n" \
           f"Difficolta' di gioco: {race['difficolta']}."
    options = [
        {"desc": f"Scegli {race['nome_plurale']}", "goto": (_set_razza, {"race_id": race_id})},
        {"key": ("(Indietro)", "indietro", "b"), "desc": "Torna alla lista delle razze",
         "goto": "menunode_razza"},
    ]
    return text, options


def _set_razza(caller, raw_string, race_id=None, **kwargs):
    if not race_id:
        return "menunode_razza"
    caller.new_char.imposta_razza(race_id)
    return ("menunode_professione", {"race_id": race_id})


#########################################################
#                  Scelta Professione
#########################################################

def menunode_professione(caller, raw_string="", race_id=None, **kwargs):
    char = caller.new_char
    char.db.chargen_step = "menunode_professione"
    race_id = race_id or char.db.race
    disponibili = _professioni_per_razza(race_id)

    razza_nome = RACES[race_id]["nome_plurale"]
    text = dedent(f"""\
        |wScelta della professione ({razza_nome})|n

        La professione scelta determina il tuo punto di partenza nel mondo,
        i tuoi modificatori agli attributi e le prime skill che potrai
        allenare. Cambiare professione piu' avanti nel gioco sara' sempre
        possibile.
    """)
    options = []
    for prof_id in disponibili:
        prof = NEWBIE_PROFESSIONS[prof_id]
        options.append({
            "desc": f"|c{prof['nome_m']}|n — {prof['luogo']}",
            "goto": ("menunode_info_professione", {"prof_id": prof_id, "race_id": race_id}),
        })
    options.append({
        "key": ("(Indietro)", "indietro", "b"),
        "desc": "Torna alla scelta della razza",
        "goto": "menunode_razza",
    })
    return text, options


def menunode_info_professione(caller, raw_string="", prof_id=None, race_id=None, **kwargs):
    if not prof_id or prof_id not in NEWBIE_PROFESSIONS:
        return "menunode_professione"
    prof = NEWBIE_PROFESSIONS[prof_id]
    attr = prof["attributi"]
    primario = attr["primario"].upper()
    text = dedent(f"""\
        |w{prof['nome_m']} / {prof['nome_f']}|n

        {prof['descrizione']}

        Luogo di partenza: {prof['luogo']}
        Attributo primario: {primario}
        Modificatori: STR {attr['str']}  INT {attr['int']}  WIS {attr['wis']}  \
DEX {attr['dex']}  CON {attr['con']}  FOR.{attr['luck']}  CAR.{attr['cha']}
    """)
    options = [
        {"desc": f"Diventa {prof['nome_m']}",
         "goto": (_set_professione, {"prof_id": prof_id})},
        {"key": ("(Indietro)", "indietro", "b"), "desc": "Torna alla lista delle professioni",
         "goto": ("menunode_professione", {"race_id": race_id})},
    ]
    return text, options


def _set_professione(caller, raw_string, prof_id=None, **kwargs):
    char = caller.new_char
    if not prof_id:
        return "menunode_professione"
    char.tira_attributi_base()
    char.applica_professione_newbie(prof_id)
    return "menunode_scegli_nome"


#########################################################
#         Personaggio Preimpostato (Fase K, 18a tornata)
#########################################################

def menunode_preset_lista(caller, raw_string="", **kwargs):
    caller.new_char.db.chargen_step = "menunode_preset_lista"
    text = dedent("""\
        |wPersonaggi preimpostati|n

        Un personaggio pronto per ogni professione di partenza - scegline
        uno per vederne i dettagli.
    """)
    options = []
    for prof_id, _nome_m, _nome_f, nome_prof, race_id, _descrizione in lista_preset():
        razza_nome = RACES[race_id]["nome_plurale"]
        options.append({
            "desc": f"|c{nome_prof}|n ({razza_nome})",
            "goto": ("menunode_preset_info", {"prof_id": prof_id}),
        })
    options.append({
        "key": ("(Indietro)", "indietro", "b"),
        "desc": "Torna alla scelta della modalita' di creazione",
        "goto": "menunode_modalita",
    })
    return text, options


def menunode_preset_info(caller, raw_string="", prof_id=None, **kwargs):
    if not prof_id or prof_id not in NEWBIE_PROFESSIONS:
        return "menunode_preset_lista"
    prof = NEWBIE_PROFESSIONS[prof_id]
    razza_nome = RACES[prof["razza"]]["nome_plurale"]
    nome_m = PRESET_NOME_M.get(prof_id, prof["nome_m"])
    nome_f = PRESET_NOME_F.get(prof_id, prof["nome_f"])
    esteso_m = genera_descrizione_estesa(prof_id, nome_m)
    riga_nome = f"Nome proposto: |c{esteso_m or nome_m}|n"
    if nome_m != nome_f:
        riga_nome += f" (o |c{nome_f}|n, se preferisci la versione femminile)"
    text = dedent(f"""\
        |w{prof['nome_m']}|n ({razza_nome})

        {prof['descrizione']}

        Luogo di partenza: {prof['luogo']}
        {riga_nome}
    """)
    options = [
        {"desc": f"Scegli {nome_m}",
         "goto": (_set_preset, {"prof_id": prof_id, "genere": "m"})},
    ]
    if nome_m != nome_f:
        options.append({
            "desc": f"Scegli {nome_f}",
            "goto": (_set_preset, {"prof_id": prof_id, "genere": "f"}),
        })
    options.append({
        "key": ("(Indietro)", "indietro", "b"),
        "desc": "Torna alla lista dei preimpostati",
        "goto": "menunode_preset_lista",
    })
    return text, options


def _set_preset(caller, raw_string, prof_id=None, genere="m", **kwargs):
    char = caller.new_char
    if not prof_id:
        return "menunode_preset_lista"
    char.db.genere = genere
    nome_suggerito = applica_preset(char, prof_id, genere=genere)
    return ("menunode_nome_suggerito", {"nome_suggerito": nome_suggerito})


#########################################################
#          Personaggio Casuale (Fase K, 18a tornata)
#########################################################

def _avvia_casuale(caller, raw_string="", **kwargs):
    char = caller.new_char
    prof_id, nome, genere = genera_personaggio_casuale(char)
    return ("menunode_casuale_risultato", {"prof_id": prof_id, "nome": nome, "genere": genere})


def menunode_casuale_risultato(caller, raw_string="", prof_id=None, nome=None, genere=None, **kwargs):
    char = caller.new_char
    # Bug reale scoperto testando dal vivo via telnet (Fase K, ventunesima
    # tornata): questo nodo ha bisogno di prof_id/nome/genere per essere
    # renderizzato, ma chargen_step salva solo il NOME del nodo, non i suoi
    # argomenti - riprendere qui dopo una disconnessione (charcreate di
    # nuovo) richiamava questa funzione con prof_id=None, andando in
    # KeyError. NON impostiamo chargen_step qui: resta a "menunode_modalita"
    # (l'ultimo nodo scritto prima di arrivarci), cosi' un'eventuale ripresa
    # torna li' invece di rompersi - basta rigenerare di nuovo, costa un
    # secondo.
    prof = NEWBIE_PROFESSIONS[prof_id]
    razza_nome = RACES[prof["razza"]]["nome_plurale"]
    attr = prof["attributi"]
    esteso = genera_descrizione_estesa(prof_id, nome)
    text = dedent(f"""\
        |wPersonaggio casuale|n

        Razza: |c{razza_nome}|n
        Professione: |c{prof['nome_f'] if genere == 'f' else prof['nome_m']}|n
        Luogo di partenza: {prof['luogo']}
        Nome proposto: |c{esteso or nome}|n

        Attributi grezzi tirati (STR {char.attributes.get('stat_str', category='cthulhu')} \
INT {char.attributes.get('stat_int', category='cthulhu')} \
WIS {char.attributes.get('stat_wis', category='cthulhu')} \
DEX {char.attributes.get('stat_dex', category='cthulhu')} \
CON {char.attributes.get('stat_con', category='cthulhu')} \
FOR.{char.attributes.get('stat_luck', category='cthulhu')} \
CAR.{char.attributes.get('stat_cha', category='cthulhu')})

        Non ti convince? Puoi rigenerare tutto da capo.
    """)
    options = [
        {"desc": "Accetta questo personaggio",
         "goto": ("menunode_nome_suggerito", {"nome_suggerito": nome})},
        {"desc": "Rigenera", "goto": _avvia_casuale},
        {"key": ("(Indietro)", "indietro", "b"),
         "desc": "Torna alla scelta della modalita' di creazione",
         "goto": "menunode_modalita"},
    ]
    return text, options


#########################################################
#                  Scelta del Nome
#########################################################

def menunode_scegli_nome(caller, raw_string="", **kwargs):
    char = caller.new_char
    char.db.chargen_step = "menunode_scegli_nome"

    if error := kwargs.get("error"):
        prompt = f"{error}. Inserisci un nome diverso."
    else:
        prompt = "Scrivi qui il nome del tuo personaggio per verificarne la disponibilita'."

    text = dedent(f"""\
        |wScelta del nome|n

        {prompt}
    """)
    options = {"key": "_default", "goto": _check_nome}
    return text, options


def _errore_validita_nome(caller, nome):
    """None se il nome e' valido e disponibile, altrimenti un messaggio
    d'errore. Non modifica nulla - vedi _check_nome/_accetta_nome_suggerito
    per chi poi assegna davvero char.key.

    Bug reale corretto (audit globale pre-beta, scoperto collaudando la
    registrazione di un giocatore nuovo): il controllo guardava solo
    `Character.objects.filter_family()`, che NON comprende gli NPC -
    nel progetto `NPC` e `Character` sono classi sorelle, non una
    sottoclasse dell'altra. Il generatore di nomi casuali propose cosi'
    "Prescott", che e' anche il nome del gioielliere di Arkham: il
    personaggio venne creato lo stesso e da quel momento ogni ricerca
    per nome (LOOK, KILL, GIVE, e l'ingresso in gioco stesso) diventava
    ambigua fra il giocatore e l'NPC. Ora si verificano entrambe le
    famiglie, cosi' un giocatore non puo' piu' prendere il nome di un
    personaggio non giocante gia' esistente nel mondo."""
    if not nome or not nome.isalpha() or len(nome) < 3:
        return "Il nome deve contenere solo lettere ed essere lungo almeno 3 caratteri"
    from typeclasses.npcs import NPC

    if Character.objects.filter_family(db_key__iexact=nome).exists():
        return f"|w{nome}|n non e' disponibile"
    if NPC.objects.filter_family(db_key__iexact=nome).exists():
        return f"|w{nome}|n e' gia' il nome di un abitante di questo mondo"
    return None


def _check_nome(caller, raw_string, **kwargs):
    nome = raw_string.strip()
    nome = caller.account.normalize_username(nome)

    errore = _errore_validita_nome(caller, nome)
    if errore:
        return ("menunode_scegli_nome", {"error": errore})

    caller.new_char.key = nome
    return "menunode_conferma_nome"


#########################################################
#           Nome suggerito (preset/casuale)
#########################################################

def menunode_nome_suggerito(caller, raw_string="", nome_suggerito=None, **kwargs):
    """Passo intermedio usato da preimpostato/casuale: propone un nome
    gia' pronto invece di partire da un campo vuoto, ma lascia comunque
    la possibilita' di sceglierne uno diverso (nessuna fonte da
    rispettare qui, e' un'aggiunta nuova - vedi world/nomi_generazione.py)."""
    char = caller.new_char
    # Stesso motivo di menunode_casuale_risultato: nome_suggerito non
    # sopravvivrebbe a una ripresa (chargen_step salva solo il nome del
    # nodo) - non lo impostiamo qui, resta al nodo precedente.
    text = dedent(f"""\
        |wNome proposto|n

        Ti proponiamo il nome |w{nome_suggerito}|n. Vuoi tenerlo, o preferisci
        sceglierne un altro?
    """)
    options = [
        {"desc": f"Tieni '{nome_suggerito}'",
         "goto": (_accetta_nome_suggerito, {"nome_suggerito": nome_suggerito})},
        {"desc": "Scegli un altro nome", "goto": "menunode_scegli_nome"},
    ]
    return text, options


def _accetta_nome_suggerito(caller, raw_string, nome_suggerito=None, **kwargs):
    errore = _errore_validita_nome(caller, nome_suggerito)
    if errore:
        # caso raro (es. un altro giocatore ha appena preso lo stesso nome
        # generato a caso): si passa comunque alla scelta libera invece di
        # bloccare la creazione.
        return ("menunode_scegli_nome", {"error": errore})
    caller.new_char.key = nome_suggerito
    return "menunode_conferma_nome"


def menunode_conferma_nome(caller, raw_string="", **kwargs):
    char = caller.new_char
    text = f"|w{char.key}|n e' disponibile! Confermi?"
    options = [
        {"key": ("Si'", "si", "s", "y"), "goto": "menunode_fine"},
        {"key": ("No", "n"), "goto": "menunode_scegli_nome"},
    ]
    return text, options


#########################################################
#                        Fine
#########################################################

def menunode_fine(caller, raw_string="", **kwargs):
    char = caller.new_char

    start_room = char.db.recall_room
    if start_room:
        char.location = start_room
        char.db.prelogout_location = start_room
    else:
        char.db.prelogout_location = ObjectDB.objects.get_id(settings.START_LOCATION)

    char.attributes.remove("chargen_step")

    # caller e' la SESSIONE (vedi il docstring del modulo): caller.account
    # e' gia' valido a questo punto, a differenza di char.account (il
    # personaggio non e' ancora "puppettato" da nessuno finche' il menu
    # non si chiude - vedi world/canali.py:iscrivi_a_gossip per i dettagli
    # del bug scoperto testando dal vivo).
    from world.canali import iscrivi_a_gossip
    iscrivi_a_gossip(caller.account)

    text = dedent(f"""\
        |wBenvenuto/a, {char.key}!|n

        Il tuo personaggio e' pronto:

        {char.scheda()}

        Buon gioco - e ricorda: prima o poi morirai. Accettalo e aspettatelo.
    """)
    return text, None
