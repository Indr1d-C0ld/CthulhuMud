"""
GUNSMITH/RELOAD (Fase K, settima tornata): confermati dalla fonte
(helps/forging.txt: "The GUNSMITH command is used to create guns and
ammunition... GUNSMITH <gun> <caliber> [level] / GUNSMITH AMMO
<caliber>"; helps/reload.txt: "RELOAD... perform the REMOVE and WIELD
actions necessary to load and/or clean a gun weapon... If a character
has a clip of the wrong size, this command will only partially load
the weapon") - dichiarati esplicitamente rimandati in
world/forgiatura.py fin dalla Fase G, terza tornata ("il nostro
sistema non modella ancora calibro/munizioni").

Riusa lo stesso schema di world/forgiatura.py (incudine richiesta,
costo in movimento, rischio/qualita' legati al rating) invece di un
sistema separato. NON specificato dalla fonte (scelte di design
esplicite): calibri concreti, capacita' dei caricatori, quantita' di
colpi per tentativo di GUNSMITH AMMO, ed EFFETTIVAMENTE far si' che le
armi da fuoco restino senza colpi in combattimento (la fonte descrive
solo la creazione/ricarica, non se e come le munizioni si esauriscono
in combattimento - qui si e' scelto di renderlo un vincolo vero,
altrimenti GUNSMITH/RELOAD sarebbero pura scenografia senza alcun
impatto di gioco).
"""

import random

from world.equipment import CONDIZIONE_INIZIALE

COSTO_GUNSMITH = 200
COSTO_GUNSMITH_AMMO = 120
COSTO_RELOAD = 20

CALIBRI_VALIDI = (".22", ".38", ".45", "9mm", "12 gauge")

# tipo -> (tipo_arma/skill, dado_min, dado_max, bonus_danno_base, capacita_caricatore)
TIPI_ARMI_DA_FUOCO = {
    "handgun": ("handgun", 2, 6, 0, 6),
    "gun": ("gun", 2, 8, 1, 5),
    "machinegun": ("machinegun", 2, 6, 0, 30),
    "submachinegun": ("submachinegun", 1, 5, 0, 20),
}


def e_arma_da_fuoco(oggetto):
    return bool(getattr(oggetto, "db", None) and oggetto.db.tipo_arma in TIPI_ARMI_DA_FUOCO)


def _rating(personaggio, skill_id):
    return personaggio.skill_rating(skill_id)


def gunsmith_arma(personaggio, tipo, calibro, materiale, livello=None):
    """GUNSMITH <tipo> <calibro> [livello]. Ritorna (ok, messaggio, oggetto_o_None)."""
    from evennia.utils import create
    from world.forgiatura import c_e_incudine

    tipo = tipo.lower()
    if tipo not in TIPI_ARMI_DA_FUOCO:
        return False, f"Tipo sconosciuto. Scegli tra: {', '.join(TIPI_ARMI_DA_FUOCO)}.", None
    calibro = calibro.lower()
    if calibro not in CALIBRI_VALIDI:
        return False, f"Calibro sconosciuto. Scegli tra: {', '.join(CALIBRI_VALIDI)}.", None
    if not c_e_incudine(personaggio.location):
        return False, "Ti serve un'incudine o una forgia per costruire un'arma da fuoco.", None
    if _rating(personaggio, "forging") <= 0:
        return False, "Non conosci la skill Forgiatura.", None
    if (personaggio.db.move or 0) < COSTO_GUNSMITH:
        return False, "Sei troppo stanco per lavorare al banco (serve piu' movimento).", None
    if not materiale or not materiale.db.materiale_forgiatura:
        return False, "Devi tenere in mano un materiale grezzo da lavorare.", None

    livello_proprio = personaggio.livello_per_equip()
    if livello is None:
        livello = livello_proprio
    if livello > livello_proprio:
        return False, f"Non puoi costruire qualcosa di livello superiore al tuo ({livello_proprio}).", None

    personaggio.db.move -= COSTO_GUNSMITH
    tipo_arma, dado_min, dado_max, bonus_base, capacita = TIPI_ARMI_DA_FUOCO[tipo]
    qualita = materiale.db.materiale_forgiatura
    rating = _rating(personaggio, "forging")
    scala = livello // 10 + qualita // 10 + rating // 25
    materiale.delete()

    arma = create.create_object(
        "typeclasses.objects.Object", key=f"{tipo} calibro {calibro} di {personaggio.key}",
        location=personaggio,
    )
    arma.db.desc = f"Un'arma da fuoco forgiata a mano, camerata per munizioni calibro {calibro}."
    arma.db.slot = "arma"
    arma.db.livello = livello
    arma.db.condizione = CONDIZIONE_INIZIALE
    arma.db.tipo_arma = tipo_arma
    arma.db.dado_min = dado_min
    arma.db.dado_max = dado_max
    arma.db.bonus_danno = bonus_base + scala
    arma.db.calibro = calibro
    arma.db.capacita_caricatore = capacita
    arma.db.munizioni_caricate = 0
    return True, f"Assembli {arma.key}. E' scarica: usa GUNSMITH AMMO e RELOAD prima di impugnarla.", arma


def gunsmith_munizioni(personaggio, calibro, materiale):
    """GUNSMITH AMMO <calibro>. Ritorna (ok, messaggio, oggetto_o_None)."""
    from evennia.utils import create
    from world.forgiatura import c_e_incudine

    calibro = calibro.lower()
    if calibro not in CALIBRI_VALIDI:
        return False, f"Calibro sconosciuto. Scegli tra: {', '.join(CALIBRI_VALIDI)}.", None
    if not c_e_incudine(personaggio.location):
        return False, "Ti serve un'incudine o una forgia per fabbricare munizioni.", None
    if _rating(personaggio, "explosives") <= 0 or _rating(personaggio, "chemistry") <= 0:
        return False, "Ti servono sia Esplosivi sia Chimica per fabbricare munizioni.", None
    if (personaggio.db.move or 0) < COSTO_GUNSMITH_AMMO:
        return False, "Sei troppo stanco per lavorare al banco (serve piu' movimento).", None
    if not materiale or not materiale.db.materiale_forgiatura:
        return False, "Devi tenere in mano della polvere da sparo (o materiale grezzo equivalente).", None

    personaggio.db.move -= COSTO_GUNSMITH_AMMO
    qualita = materiale.db.materiale_forgiatura
    rating_medio = (_rating(personaggio, "explosives") + _rating(personaggio, "chemistry")) // 2
    colpi = 4 + qualita // 10 + rating_medio // 20
    materiale.delete()

    clip = create.create_object(
        "typeclasses.objects.Object", key=f"un caricatore calibro {calibro}", location=personaggio,
    )
    clip.db.desc = f"Un caricatore di munizioni artigianali, calibro {calibro}."
    clip.db.tipo_oggetto = "munizioni"
    clip.db.calibro = calibro
    clip.db.colpi = colpi
    return True, f"Fabbrichi {clip.key} ({colpi} colpi).", clip


def ricarica(personaggio):
    """RELOAD: trova un'arma da fuoco impugnata e un caricatore dello
    stesso calibro nell'inventario, trasferisce i colpi (parzialmente
    se il caricatore ne contiene piu' della capacita' residua)."""
    arma = (personaggio.db.equip or {}).get("arma")
    if not arma or not e_arma_da_fuoco(arma):
        return False, "Non stai impugnando un'arma da fuoco."

    spazio = (arma.db.capacita_caricatore or 0) - (arma.db.munizioni_caricate or 0)
    if spazio <= 0:
        return False, f"{arma.key} e' gia' carica."

    caricatore = next(
        (o for o in personaggio.contents
         if o.db.tipo_oggetto == "munizioni" and o.db.calibro == arma.db.calibro and (o.db.colpi or 0) > 0),
        None,
    )
    if not caricatore:
        return False, f"Non hai un caricatore calibro {arma.db.calibro} da usare."

    trasferiti = min(spazio, caricatore.db.colpi)
    arma.db.munizioni_caricate = (arma.db.munizioni_caricate or 0) + trasferiti
    caricatore.db.colpi -= trasferiti
    if caricatore.db.colpi <= 0:
        caricatore.delete()

    # confermato dalla fonte: un caricatore piu' piccolo della capacita'
    # residua dell'arma la ricarica solo parzialmente.
    nota = "" if arma.db.munizioni_caricate >= arma.db.capacita_caricatore else \
        " Il caricatore era troppo piccolo per riempirla del tutto."
    return True, f"Ricarichi {arma.key}: ora {arma.db.munizioni_caricate}/{arma.db.capacita_caricatore} colpi.{nota}"
