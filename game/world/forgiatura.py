"""
Forgiatura: FORGE/FIX/REFIT (Fase G, terza tornata) - sostituisce il
precedente REPAIR a pagamento in Oro (commands/cthulhu_equip.py,
CmdRepair, rimosso), risultato non fedele alla fonte una volta letta
per intero (research/REPORT.md). Confermato verbatim dalla fonte
(guides_forging.txt, helps/forging.txt):

    "You must be holding the raw material you wish to use, and you
    must be standing in a room that contains an anvil or a forge...
    Using the FORGE command costs 200 movement points... FIX...
    costs 80 movement points... REFIT... costs 100 movement points."

Anche confermato: FORGE non puo' creare un oggetto di livello superiore
al proprio; la qualita' dipende da livello, qualita' del materiale e
rating in Forgiatura; FIX rischia di rompere l'oggetto (rischio che
scende salendo di rating); un blacksmith con incudine (es. Maro a
Ulthar, citato esplicitamente dalla fonte) permette di forgiare senza
sapere l'incantesimo Greater Creation per crearsi un'incudine.

NON specificato dalla fonte (scelte di design esplicite): le formule
numeriche esatte di danno/classe armatura risultanti, le percentuali
di successo/rottura, i tipi esatti di materiale e il loro valore.
GUNSMITH (armi da fuoco/munizioni, richiede anche Esplosivi e Chimica)
e' costruito a parte in world/munizioni.py (Fase K, settima tornata),
con lo stesso schema di rischio/qualita' legato al rating.
"""

import random

from world.equipment import CONDIZIONE_INIZIALE

COSTO_FORGE = 200
COSTO_FIX = 80
COSTO_REFIT = 100

# tipo (come da FORGE <tipo>) -> (slot, tipo_arma/None, dado_min, dado_max, bonus_danno_base, classe_armatura_base)
TIPI_FORGIABILI = {
    "dagger": ("arma", "dagger", 1, 4, 0, 0),
    "sword": ("arma", "sword", 2, 6, 0, 0),
    "mace": ("arma", "mace", 1, 5, 0, 0),
    "spear": ("arma", "spear", 2, 5, 0, 0),
    "whip": ("arma", "whip", 1, 4, 0, 0),
    "flail": ("arma", "flail", 2, 6, 0, 0),
    "axe": ("arma", "axe", 2, 6, 0, 0),
    "polearm": ("arma", "polearm", 2, 7, 0, 0),
    "bow": ("arma", "bow", 1, 6, 0, 0),
    "armor": ("corpo", None, 0, 0, 0, 4),
    "shield": ("scudo", None, 0, 0, 0, 3),
    "helmet": ("testa", None, 0, 0, 0, 2),
}

# chiave materiale -> (nome, qualita')
MATERIALI = {
    "cristallo": ("un cristallo grezzo", 10),
    "oro": ("una pepita d'oro", 20),
    "diamante": ("un diamante grezzo", 35),
    "mithril": ("una scheggia di mithril", 50),
}


def c_e_incudine(stanza):
    """C'e' un'incudine o una forgia in questa stanza?"""
    if not stanza:
        return False
    return any(obj.db.incudine for obj in stanza.contents)


def _rating_forgiatura(personaggio):
    return personaggio.skill_rating("forging")


def forgia(personaggio, tipo, materiale, livello=None):
    """FORGE <tipo> [livello]: crea un'arma o un pezzo d'armatura dal
    materiale tenuto in mano. Ritorna (ok, messaggio, oggetto_o_None)."""
    from evennia.utils import create

    tipo = tipo.lower()
    if tipo not in TIPI_FORGIABILI:
        tipi = ", ".join(TIPI_FORGIABILI)
        return False, f"Tipo sconosciuto. Scegli tra: {tipi}.", None
    if not c_e_incudine(personaggio.location):
        return False, "Ti serve un'incudine o una forgia per forgiare qualcosa.", None
    if _rating_forgiatura(personaggio) <= 0:
        return False, "Non conosci la skill Forgiatura.", None
    if (personaggio.db.move or 0) < COSTO_FORGE:
        return False, "Sei troppo stanco per forgiare (serve piu' movimento).", None
    if not materiale or not materiale.db.materiale_forgiatura:
        return False, "Devi tenere in mano un materiale da forgiare.", None

    livello_proprio = personaggio.livello_per_equip()
    if livello is None:
        livello = livello_proprio
    if livello > livello_proprio:
        return False, f"Non puoi forgiare qualcosa di livello superiore al tuo ({livello_proprio}).", None

    personaggio.db.move -= COSTO_FORGE
    slot, tipo_arma, dado_min, dado_max, bonus_base, classe_base = TIPI_FORGIABILI[tipo]
    qualita = materiale.db.materiale_forgiatura
    rating = _rating_forgiatura(personaggio)

    scala = livello // 10 + qualita // 10 + rating // 25
    materiale.delete()

    oggetto = create.create_object(
        "typeclasses.objects.Object",
        key=f"{tipo} forgiato da {personaggio.key}",
        location=personaggio,
    )
    oggetto.db.desc = f"Un oggetto forgiato a mano, di fattura {'pregiata' if qualita >= 35 else 'robusta'}."
    oggetto.db.slot = slot
    oggetto.db.livello = livello
    oggetto.db.condizione = CONDIZIONE_INIZIALE
    if tipo_arma:
        oggetto.db.tipo_arma = tipo_arma
        oggetto.db.dado_min = dado_min
        oggetto.db.dado_max = dado_max
        oggetto.db.bonus_danno = bonus_base + scala
    else:
        oggetto.db.classe_armatura = classe_base + scala

    return True, f"Forgi {oggetto.key}.", oggetto


def ripara(personaggio, oggetto):
    """FIX <oggetto>: ripara un pezzo di equipaggiamento danneggiato,
    con rischio di romperlo (rischio che scende salendo di rating in
    Forgiatura). Ritorna (ok, messaggio)."""
    from world.equipment import e_equipaggiabile, condizione_di

    if not e_equipaggiabile(oggetto):
        return False, f"{oggetto.key} non e' il genere di oggetto che si ripara."
    if not c_e_incudine(personaggio.location):
        return False, "Ti serve un'incudine o una forgia per riparare qualcosa."
    if condizione_di(oggetto) >= CONDIZIONE_INIZIALE:
        return False, f"{oggetto.key} e' gia' in perfette condizioni."
    if (personaggio.db.move or 0) < COSTO_FIX:
        return False, "Sei troppo stanco per tentare una riparazione."

    personaggio.db.move -= COSTO_FIX
    rating = _rating_forgiatura(personaggio)

    rischio_rottura = max(2, 20 - rating // 5)
    if random.randint(1, 100) <= rischio_rottura:
        nome = oggetto.key
        oggetto.delete()
        return False, f"Il tentativo va storto: {nome} si spezza in mille pezzi!"

    recupero = 30 + rating // 5
    oggetto.db.condizione = min(CONDIZIONE_INIZIALE, condizione_di(oggetto) + recupero)
    return True, f"Ripari parzialmente {oggetto.key} (condizione ora {oggetto.db.condizione})."


def refit(personaggio, oggetto, nuovo_livello):
    """REFIT <oggetto> <livello>: adatta il livello minimo richiesto da
    un pezzo di equipaggiamento, con rischio di romperlo. Ritorna
    (ok, messaggio)."""
    from world.equipment import e_equipaggiabile

    if not e_equipaggiabile(oggetto):
        return False, f"{oggetto.key} non e' il genere di oggetto che si adatta."
    if not c_e_incudine(personaggio.location):
        return False, "Ti serve un'incudine o una forgia per adattare qualcosa."
    if (personaggio.db.move or 0) < COSTO_REFIT:
        return False, "Sei troppo stanco per tentare un adattamento."
    if nuovo_livello < 1:
        return False, "Il livello deve essere almeno 1."

    personaggio.db.move -= COSTO_REFIT
    rating = _rating_forgiatura(personaggio)

    rischio_rottura = max(3, 25 - rating // 4)
    if random.randint(1, 100) <= rischio_rottura:
        nome = oggetto.key
        oggetto.delete()
        return False, f"L'adattamento fallisce: {nome} si rompe!"

    oggetto.db.livello = nuovo_livello
    return True, f"Adatti {oggetto.key} al livello {nuovo_livello}."
