"""
Criminale/MURDER/PK e sistema Taglie&Missioni (Fase G, decima tornata).
Confermato dalla scansione esaustiva (helps/murder.txt, helps/kill.txt,
helps/pk.txt, helps/criminal.txt, helps/bounty.txt):

- KILL su un NPC "protetto" (es. un poliziotto) si rifiuta e indirizza
  a MURDER; MURDER funziona sempre, ma se il bersaglio era protetto
  rende il personaggio un CRIMINALE.
- Un criminale puo' subire una taglia (BOUNTY <giocatore> <importo>,
  pagata da chi la mette); chi lo uccide incassa la taglia. BOUNTY
  BRIBE toglie la propria taglia pagando il doppio del suo importo.
  La morte rimuove sempre lo status di criminale.
- PK e' permesso SOLO con una ragione IC valida (guerra tra clan,
  taglia, furto subito...) - la fonte lascia la valutazione della
  legittimita' allo staff Immortal caso per caso: non e' qualcosa che
  si possa far rispettare automaticamente dal codice, quindi qui non
  viene imposto un divieto tecnico al PK in generale (sarebbe
  infedele: la fonte descrive CthulhuMUD come "a full PK game"),
  semplicemente MURDER/KILL restano disponibili tra personaggi come
  sempre, e le regole IC restano una questione di moderazione umana.
- MISSION: missioni casuali (corriere/recupero/caccia) alla Gilda dei
  Cacciatori di Taglie di Dylath-Leen (gia' costruita separatamente,
  vedi world/rooms_bounty_office.py), a cooldown, con ricompense in
  oro/practice/train/Fama (gia' esistente: Character.db.fame).

NON specificato dalla fonte (scelte di design esplicite): gli importi
esatti di taglia/ricompensa, la durata delle missioni, le percentuali
di successo. Semplificazione dichiarata: le missioni di caccia
scelgono come bersaglio un NPC "criminale" generato apposta (finche'
non esistono NPC ostili veri - milestone immediatamente successiva a
questa) invece di un giocatore o un mostro selvatico gia' nel mondo.

Fase K, ventiseiesima tornata - chiusi molti gap trovati dall'audit
(helps/death.txt, newbie.txt, bounty.txt, autokill.txt):
- Immunita' PK dei newbie (helps/newbie.txt: "a NEWBIE is officially
  defined as a non-remort player-character between the levels of 3
  and 14" - "you cannot attack them for ANY reason"): vedi e_newbie().
- Il cadavere di un GIOCATORE (non di un mostro) e' ora protetto:
  solo il proprietario o il suo gruppo puo' frugarci dentro (vedi
  world/combat.py:crea_cadavere, db.proprietario, e il controllo in
  commands/cthulhu.py:CmdGet._get_da_contenitore).
- MISSION COMPLETE ora richiede di essere all'Ufficio Taglie di
  Dylath-Leen, TRANNE per le missioni di corriere (helps/bounty.txt:
  "you must return to the Bounty Office... The exception to this is
  courier missions, in which case the person to whom you are
  delivering the item will give you reward").
- MISSION REQUEST ora ha una vera possibilita' di "nessuna missione
  disponibile" (prima ne generava sempre una) - helps/bounty.txt: "If
  you are told there are no missions currently available, you will
  have to wait 5 minutes before trying again." Introdotta una
  costante distinta per questo caso, separata da quella (gia'
  esistente ma riusata a sproposito) per una missione scaduta.
- MISSION LIST/BUY: la fonte dice solo "spent at the Bounty Office on
  various items and services" senza un listino - qui un piccolo
  catalogo dichiarato (CATALOGO_MISSION_BUY).
- BOUNTY ora mostra solo giocatori ONLINE (helps/bounty.txt: "a list
  of online players who have a bounty"), e accetta taglie solo su
  bersagli gia' marcati come criminali (helps/bounty.txt inquadra la
  taglia come strumento "to deal with players who are criminals").
- AUTOGOLD/AUTOLOOT/AUTOKILL/NOLOOT (helps/autokill.txt) come nuovi
  toggle in commands/cthulhu_pk.py. Semplificazione dichiarata per
  AUTOKILL: questo porting non ha mai avuto una risoluzione di
  combattimento "stordisci senza uccidere" (0 HP e' sempre morte reale,
  scelta di design fin dalla Fase F) - il toggle e' tracciato e
  visibile in AUTOLIST ma non altera ancora l'esito del combattimento,
  dato che costruire un vero percorso "stordito" in sicurezza
  attraverso tutti i sistemi che assumono "0 HP = morto" (taglie,
  cadaveri, missioni di caccia) e' un lavoro a se stante, non un
  semplice toggle. AUTOSAC deliberatamente NON implementato: dipende
  da un intero sistema WORSHIP/deita'/pieta' che questo porting non ha
  mai costruito (fuori scope per un audit di morte/cadaveri/PK).
"""

import random

from world.colori import pericolo

DURATA_MISSIONE_SECONDI = 20 * 60
COOLDOWN_COMPLETAMENTO_SECONDI = 30 * 60
COOLDOWN_NESSUNA_MISSIONE_SECONDI = 5 * 60  # "no missions available": attendi 5 minuti
COOLDOWN_MISSIONE_SCADUTA_SECONDI = 5 * 60  # missione scaduta senza completarla
COSTO_ABORT_FAMA = 5
PROBABILITA_NESSUNA_MISSIONE = 20  # % - non specificato dalla fonte

TIPI_MISSIONE = ("corriere", "recupero", "caccia")

LIVELLO_NEWBIE_MIN = 3
LIVELLO_NEWBIE_MAX = 14

CATALOGO_MISSION_BUY = {
    "practice": ("1 practice", 5),
    "train": ("1 train", 10),
    "oro": ("50 oro", 8),
}


def e_newbie(personaggio):
    """helps/newbie.txt: "a NEWBIE is officially defined as a non-remort
    player-character between the levels of 3 and 14." Chi ha gia'
    remortato non conta piu' come newbie, indipendentemente dal
    livello raggiunto dopo il remort."""
    if not hasattr(personaggio, "db") or personaggio.db.remortato:
        return False
    if not hasattr(personaggio, "livello_personaggio"):
        return False
    livello = personaggio.livello_personaggio()
    return LIVELLO_NEWBIE_MIN <= livello <= LIVELLO_NEWBIE_MAX


def diventa_criminale(personaggio):
    personaggio.db.criminale = True
    personaggio.msg(pericolo("Sei diventato/a un criminale.") + " Altri potranno mettere una taglia sulla tua testa.")


def rimuovi_status_criminale(personaggio):
    personaggio.db.criminale = False


def uccidi_o_murder(attaccante, bersaglio, comando_murder):
    """Logica condivisa da KILL/MURDER (vedi commands/cthulhu_pk.py):
    ritorna (ok: bool, messaggio: str|None). Se ok, il chiamante avvia
    normalmente il combattimento con avvia_combattimento()."""
    # NPC di servizio (NPC.intoccabile): nemmeno MURDER (a differenza di db.protetto,
    # che si puo' forzare diventando criminali).
    if e_intoccabile(bersaglio):
        return False, messaggio_intoccabile(bersaglio)
    if (
        attaccante.is_typeclass("typeclasses.characters.Character", exact=False)
        and bersaglio.is_typeclass("typeclasses.characters.Character", exact=False)
        and e_newbie(bersaglio)
    ):
        return False, f"{bersaglio.key} e' un newbie: non puoi attaccarlo/a per nessun motivo."
    protetto = getattr(bersaglio.db, "protetto", False)
    if protetto and not comando_murder:
        return False, (
            f"{bersaglio.key} e' protetto/a: per attaccarlo/a devi usare MURDER "
            "(diventerai un criminale)."
        )
    if protetto and comando_murder:
        diventa_criminale(attaccante)
    return True, None


def incassa_taglia(uccisore, vittima):
    """Se la vittima era un criminale con una taglia, l'uccisore la
    incassa. Ritorna l'importo incassato (0 se nessuna taglia)."""
    taglia = vittima.db.taglia_oro or 0
    if taglia <= 0:
        return 0
    vittima.db.taglia_oro = 0
    uccisore.db.gold = (uccisore.db.gold or 0) + taglia
    uccisore.msg(f"Incassi una taglia di {taglia} oro per la morte di {vittima.key}.")
    return taglia


def metti_taglia(pagante, bersaglio, importo):
    if not bersaglio.db.criminale:
        return False, f"{bersaglio.key} non e' un criminale: non puoi mettere una taglia su di lui/lei."
    oro = pagante.db.gold or 0
    if importo <= 0:
        return False, "Devi indicare un importo positivo."
    if oro < importo:
        return False, f"Non hai {importo} oro."
    pagante.db.gold = oro - importo
    bersaglio.db.taglia_oro = (bersaglio.db.taglia_oro or 0) + importo
    return True, f"Metti una taglia di {importo} oro sulla testa di {bersaglio.key} (totale: {bersaglio.db.taglia_oro})."


def paga_bribe(personaggio):
    taglia = personaggio.db.taglia_oro or 0
    if taglia <= 0:
        return False, "Non hai nessuna taglia sulla tua testa."
    costo = taglia * 2
    oro = personaggio.db.gold or 0
    if oro < costo:
        return False, f"Toglierti la taglia costerebbe {costo} oro (il doppio della taglia): non ne hai abbastanza."
    personaggio.db.gold = oro - costo
    personaggio.db.taglia_oro = 0
    return True, f"Paghi {costo} oro ai Cacciatori di Taglie: la taglia sulla tua testa sparisce."


def genera_missione(personaggio):
    """MISSION REQUEST: genera una missione casuale. Ritorna (ok, messaggio)."""
    if personaggio.db.missione:
        return False, "Hai gia' una missione in corso."
    adesso = _adesso()
    prossima = personaggio.db.missione_prossima_disponibile or 0
    if adesso < prossima:
        return False, f"Devi aspettare ancora {int(prossima - adesso)} secondi prima di una nuova missione."

    if random.randint(1, 100) <= PROBABILITA_NESSUNA_MISSIONE:
        # helps/bounty.txt: "If you are told there are no missions
        # currently available, you will have to wait 5 minutes."
        personaggio.db.missione_prossima_disponibile = adesso + COOLDOWN_NESSUNA_MISSIONE_SECONDI
        return False, "Al momento non ci sono missioni disponibili. Riprova tra qualche minuto."

    tipo = random.choice(TIPI_MISSIONE)
    missione = {"tipo": tipo, "scadenza": adesso + DURATA_MISSIONE_SECONDI, "stato": "in corso"}

    if tipo == "caccia":
        from evennia.utils import create
        bersaglio = create.create_object(
            "typeclasses.npcs.NPC", key="un fuggitivo ricercato", location=personaggio.location,
        )
        bersaglio.db.livello = max(1, personaggio.livello_per_equip())
        bersaglio.db.ostile = True
        bersaglio.db.bersaglio_missione_di = personaggio.key
        missione["bersaglio_dbref"] = bersaglio.dbref
        messaggio = f"Missione di caccia: elimina {bersaglio.key} (appena apparso/a nei paraggi)."
    elif tipo == "corriere":
        from evennia.utils import create
        pacco = create.create_object(
            "typeclasses.objects.Object", key="un pacco sigillato", location=personaggio,
        )
        pacco.db.desc = "Un pacco avvolto in tela cerata, da consegnare a destinazione."
        pacco.db.pacco_missione_di = personaggio.key
        missione["oggetto_dbref"] = pacco.dbref
        messaggio = "Missione di corriere: consegna il pacco sigillato che hai ricevuto (usa DELIVER <npc>)."
    else:
        from evennia.utils import create
        oggetto = create.create_object(
            "typeclasses.objects.Object", key="un oggetto rubato", location=personaggio.location,
        )
        oggetto.db.desc = "Un oggetto di valore, chiaramente rubato a qualcuno."
        oggetto.db.oggetto_missione_di = personaggio.key
        missione["oggetto_dbref"] = oggetto.dbref
        messaggio = f"Missione di recupero: trova {oggetto.key} e riportalo all'Ufficio Taglie."

    personaggio.db.missione = missione
    return True, messaggio


def info_missione(personaggio):
    missione = personaggio.db.missione
    if not missione:
        return "Non sei in missione."
    rimanente = int(missione["scadenza"] - _adesso())
    return f"Missione di tipo '{missione['tipo']}', {max(0, rimanente)} secondi rimanenti."


def tempo_missione(personaggio):
    if personaggio.db.missione:
        rimanente = int(personaggio.db.missione["scadenza"] - _adesso())
        return max(0, rimanente)
    prossima = personaggio.db.missione_prossima_disponibile or 0
    rimanente = int(prossima - _adesso())
    return max(0, rimanente)


def stato_missione(personaggio):
    """Il campo MSTATUS di SCORE (helps/bounty.txt): MISSION/WAITING/READY."""
    if personaggio.db.missione:
        return "MISSION"
    prossima = personaggio.db.missione_prossima_disponibile or 0
    if _adesso() < prossima:
        return "WAITING"
    return "READY"


def _all_ufficio_taglie(stanza):
    from world.rooms_bounty_office import TAG_UFFICIO, TAG_CATEGORY
    return bool(stanza and stanza.tags.has(TAG_UFFICIO, category=TAG_CATEGORY))


def completa_missione(personaggio):
    missione = personaggio.db.missione
    if not missione:
        return False, "Non sei in missione."
    if _adesso() > missione["scadenza"]:
        personaggio.db.missione = None
        personaggio.db.missione_prossima_disponibile = _adesso() + COOLDOWN_MISSIONE_SCADUTA_SECONDI
        return False, "La missione e' scaduta."

    # helps/bounty.txt: "you must return to the Bounty Office and use
    # MISSION COMPLETE... The exception to this is courier missions, in
    # which case the person to whom you are delivering the item will
    # give you reward" - per il corriere la consegna stessa (DELIVER)
    # gia' chiama questa funzione sul posto, senza bisogno dell'ufficio.
    if missione["tipo"] != "corriere" and not _all_ufficio_taglie(personaggio.location):
        return False, "Devi essere all'Ufficio Taglie di Dylath-Leen per completare la missione."

    completata = False
    if missione["tipo"] == "caccia":
        completata = missione.get("bersaglio_ucciso", False)
    elif missione["tipo"] == "recupero":
        oggetto = _risolvi_dbref(missione.get("oggetto_dbref"))
        completata = bool(oggetto and oggetto.location == personaggio)
    elif missione["tipo"] == "corriere":
        completata = missione.get("pacco_consegnato", False)

    if not completata:
        return False, "Non hai ancora completato gli obiettivi della missione."

    ricompensa_oro = random.randint(20, 60)
    ricompensa_practice = random.randint(1, 3)
    ricompensa_fama = random.randint(3, 10)
    personaggio.db.gold = (personaggio.db.gold or 0) + ricompensa_oro
    personaggio.db.practices = (personaggio.db.practices or 0) + ricompensa_practice
    personaggio.db.fame = (personaggio.db.fame or 0) + ricompensa_fama
    personaggio.db.missione = None
    personaggio.db.missione_prossima_disponibile = _adesso() + COOLDOWN_COMPLETAMENTO_SECONDI

    return True, (
        f"Missione completata! Ricevi {ricompensa_oro} oro, {ricompensa_practice} practice "
        f"e {ricompensa_fama} punti Fama."
    )


def abort_missione(personaggio):
    if not personaggio.db.missione:
        return False, "Non sei in missione."
    if (personaggio.db.fame or 0) < COSTO_ABORT_FAMA:
        return False, f"Abbandonare la missione costa {COSTO_ABORT_FAMA} Fama: non ne hai abbastanza."
    personaggio.db.fame -= COSTO_ABORT_FAMA
    personaggio.db.missione = None
    return True, f"Abbandoni la missione (costo: {COSTO_ABORT_FAMA} Fama)."


def lista_mission_buy():
    """MISSION LIST: helps/bounty.txt non da' un listino - catalogo
    dichiarato, spendibile solo all'Ufficio Taglie (vedi mission_buy)."""
    return [(chiave, nome, costo) for chiave, (nome, costo) in CATALOGO_MISSION_BUY.items()]


def mission_buy(personaggio, chiave):
    if not _all_ufficio_taglie(personaggio.location):
        return False, "Devi essere all'Ufficio Taglie di Dylath-Leen per comprare qualcosa."
    voce = CATALOGO_MISSION_BUY.get(chiave)
    if not voce:
        return False, "Oggetto sconosciuto. Usa MISSION LIST per vedere cosa e' disponibile."
    nome, costo = voce
    if (personaggio.db.fame or 0) < costo:
        return False, f"{nome.capitalize()} costa {costo} Fama: non ne hai abbastanza."
    personaggio.db.fame -= costo
    if chiave == "practice":
        personaggio.db.practices = (personaggio.db.practices or 0) + 1
    elif chiave == "train":
        personaggio.db.trains = (personaggio.db.trains or 0) + 1
    elif chiave == "oro":
        personaggio.db.gold = (personaggio.db.gold or 0) + 50
    return True, f"Compri {nome} per {costo} Fama."


def permapk_attivo():
    """PERMAPK (helps/permapk.txt, comando Immortale, Livello IMPLEMENTOR):
    toggle globale - se attivo, la morte di un GIOCATORE cancella il
    personaggio dal database (vedi world/combat.py:_morte_personaggio)."""
    from evennia.server.models import ServerConfig
    return ServerConfig.objects.conf("permapk", default=False)


def _adesso():
    import time
    return time.time()


def _risolvi_dbref(dbref):
    if not dbref:
        return None
    from evennia.utils import search
    risultati = search.search_object(dbref)
    return risultati[0] if risultati else None


# NPC gia' costruiti in tornate precedenti che si prestano bene al
# ruolo di "protetto" (forze dell'ordine/militari) secondo l'esempio
# canonico della fonte ("killing a police officer... is understandably
# against the law"): marcati qui invece che ricreati da zero.
CHIAVI_NPC_PROTETTI = (
    "un sergente di polizia",
    "una guardia di frontiera",
    "una sentinella britannica",
)


def marca_npc_protetti():
    """Segna come protetto=True gli NPC gia' esistenti il cui nome
    combacia con CHIAVI_NPC_PROTETTI. Idempotente: puo' essere
    richiamata piu' volte senza effetti collaterali."""
    from evennia.objects.models import ObjectDB

    marcati = []
    for npc in ObjectDB.objects.filter(db_typeclass_path="typeclasses.npcs.NPC"):
        if npc.key in CHIAVI_NPC_PROTETTI and not npc.db.protetto:
            npc.db.protetto = True
            marcati.append(npc.key)
    return marcati


# ---------------------------------------------------------------------
# NPC di servizio intoccabili (scelta di design, vedi
# typeclasses/npcs.py:NPC.intoccabile)
# ---------------------------------------------------------------------

def e_intoccabile(obj):
    """Vero se obj e' un NPC che nessun giocatore puo' danneggiare ne'
    fare suo. Sicura su qualunque oggetto: chi non ha la proprieta' non e'
    intoccabile."""
    return bool(getattr(obj, "intoccabile", False))


def messaggio_intoccabile(obj):
    """Lo stesso messaggio ovunque la regola scatti, cosi' il giocatore
    capisce che e' una regola del gioco e non un guasto."""
    return (f"Non puoi fare del male a {obj.key}: istruttori, mercanti, "
            "terapeuti, albergatori e l'Ufficio Taglie sono intoccabili.")
