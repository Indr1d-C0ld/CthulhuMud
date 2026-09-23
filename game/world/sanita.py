"""
Sanity con conseguenze meccaniche vere (Fase G, sesta tornata).
Confermato dalla scansione esaustiva (helps/sanity.txt, helps/therapy.txt,
helps/psychology.txt) che la sanity NON era un semplice stat cosmetico
come nel porting fino a questo punto:

    "As your character's sanity erodes, they will begin to act
    strangely. They will perform random actions without your
    commands. They may randomly attack an NPC for no reason, or
    randomly flee from a fight they are winning. Conversely, they may
    refuse to flee from a fight they are losing. They may grumble,
    mutter, laugh, cry, or simply wander around."

Il recupero era via THERAPY (NPC dedicato, a pagamento, non garantito)
o la skill PSYCHOLOGY (costa 300 movimento, ~30 secondi, puo' ritorcersi
contro chi la usa).

NON specificato dalla fonte (scelte di design esplicite): le soglie
esatte di sanity per ogni comportamento erratico, quanto scende la
sanity vedendo un orrore, i costi/percentuali di THERAPY/PSYCHOLOGY.

Fase K, venticinquesima tornata - chiusi 4 gap trovati nell'audit,
tutti confermati dalla fonte (helps/sanity.txt, psychology.txt):
- Mancava "ridere" tra le reazioni erratiche elencate dalla fonte
  ("grumble, mutter, laugh, cry, or simply wander").
- "Training your Intelligence decreases your sanity, while training
  your Wisdom increases it" - mai agganciato a TRAIN (vedi
  typeclasses/characters.py:train_attributo).
- "Gaining a level increases your sanity" - mai agganciato a
  sale_di_livello() (world/esperienza.py).
- "casting certain spells decreases it" - vedi
  FAMIGLIE_MAGIA_PROIBITA in world/magic.py: nessuna lista dalla
  fonte, qui una scelta dichiarata (le famiglie di incantesimi piu'
  esplicitamente orrorifiche/proibite del registro: Negromanzia,
  Magia degli Antichi, Magia del Caos, Via dell'Evocatore, Voodoo,
  Magia Divina - quest'ultima per via di Evoca Antico).
- PSYCHOLOGY ora impiega davvero i ~30 secondi dichiarati dalla fonte
  invece di risolversi all'istante (world/skills.py aveva gia' la
  costante DURATA_PSYCHOLOGY_SECONDI, mai usata). La fonte descrive
  un'interruzione (STAND/uscire dalla stanza/colpo subito) solo per lo
  SPELL CASTING, non per PSYCHOLOGY: qui non se ne inventa una
  analoga non descritta, si aggiunge solo il ritardo.
- Resistenza alla paura ora PER TIPO (db.resistenze_paura, un dict)
  invece di un singolo contatore generico, come richiede la fonte
  ("resistance to CERTAIN TYPES of fear"). Il "tipo" viene dal nuovo
  campo dati["tipo_orrore"] di ogni mostro in world/mostri.py (bestiario
  gia' dichiarato come invenzione originale in quel modulo, quindi
  categorizzarlo per tipo di orrore Mythos e' nello stesso spirito):
  non_morti, profondi, esterni, antichi, onirici, o "sconosciuto" come
  ripiego per chi non ha ancora un tipo assegnato.
"""

import random

from world.colori import orrore

SOGLIA_ERRATICO = 30      # sotto questa sanity, rischio di azioni erratiche
SOGLIA_GRAVE = 10         # sotto questa, il rischio raddoppia

COSTO_PSYCHOLOGY_MOVIMENTO = 300
DURATA_PSYCHOLOGY_SECONDI = 30

BONUS_SANITA_LIVELLO = 2          # + (saggezza // 10), coerente con bonus_practice
DELTA_SANITA_TRAIN_INT = -2       # allenare Intelligenza riduce la sanity
DELTA_SANITA_TRAIN_WIS = 2        # allenare Saggezza la aumenta


def perdi_sanita(personaggio, quantita, fonte=None, tipo=None):
    """Riduce la sanity di `personaggio` per aver visto/affrontato
    qualcosa di orrorifico. La resistenza accumulata PER TIPO (vedi
    db.resistenze_paura) attutisce leggermente il colpo, e cresce un
    po' a ogni esposizione (assuefazione). `tipo` e' una delle chiavi
    usate da world/mostri.py (o None/"generico" per chi non lo indica)."""
    tipo = tipo or "generico"
    resistenze = personaggio.db.resistenze_paura or {}
    resistenza = resistenze.get(tipo, 0)
    quantita_effettiva = max(1, quantita - resistenza // 10)
    if (personaggio.db.stati or {}).get("rilassato"):
        # Fase K, settima tornata: incantesimo Relax - aumenta la
        # resistenza alla perdita di sanity per la sua durata.
        quantita_effettiva = max(1, quantita_effettiva // 2)
    personaggio.db.sanity = max(0, (personaggio.db.sanity or 0) - quantita_effettiva)
    resistenze[tipo] = min(100, resistenza + 1)
    personaggio.db.resistenze_paura = resistenze

    if fonte:
        personaggio.msg(orrore(f"La vista di {fonte} ti scuote nel profondo."))
    if (personaggio.db.sanity or 0) <= SOGLIA_GRAVE:
        personaggio.msg(orrore("La tua mente vacilla sull'orlo del baratro."))


def sanita_da_train_attributo(personaggio, attr):
    """Da chiamare da Character.train_attributo() dopo un TRAIN riuscito
    su INT o WIS (helps/sanity.txt, vedi nota di modulo)."""
    if attr == "int":
        delta = DELTA_SANITA_TRAIN_INT
    elif attr == "wis":
        delta = DELTA_SANITA_TRAIN_WIS
    else:
        return
    massimo = personaggio.db.sanity_max or 100
    personaggio.db.sanity = max(0, min(massimo, (personaggio.db.sanity or 0) + delta))


def bonus_sanita_livello(saggezza):
    """Quanta sanity (massima e attuale) si guadagna salendo di livello
    (helps/sanity.txt: "Gaining a level increases your sanity") - stessa
    forma delle altre ricompense di livello in world/esperienza.py, che
    gia' legano Saggezza a bonus_practice."""
    return BONUS_SANITA_LIVELLO + saggezza // 10


def azione_erratica_possibile(personaggio):
    """Controlla se scatta un'azione erratica in questo round di
    combattimento (vedi world/combat.py). Ritorna una stringa che
    descrive l'azione da eseguire, o None."""
    sanity = personaggio.db.sanity or 0
    if sanity > SOGLIA_ERRATICO:
        return None

    rischio = 15 if sanity <= SOGLIA_GRAVE else 7
    if random.randint(1, 100) > rischio:
        return None

    return random.choice([
        "attacca_a_caso", "fugge", "non_fugge", "borbotta", "ride", "piange", "vaga",
    ])


def applica_azione_erratica(personaggio, azione):
    """Esegue l'azione erratica scelta da azione_erratica_possibile."""
    if azione == "borbotta":
        personaggio.location.msg_contents(orrore(f"{personaggio.key} borbotta qualcosa di incomprensibile."))
    elif azione == "ride":
        personaggio.location.msg_contents(orrore(f"{personaggio.key} scoppia in una risata isterica."))
    elif azione == "piange":
        personaggio.location.msg_contents(orrore(f"{personaggio.key} scoppia improvvisamente in lacrime."))
    elif azione == "vaga":
        stanza = personaggio.location
        uscite = stanza.exits if stanza else []
        if uscite:
            uscita = random.choice(uscite)
            personaggio.msg(orrore(f"Vaghi senza meta e finisci per andare verso {uscita.key}."))
            personaggio.move_to(uscita.destination, quiet=True)
    elif azione == "attacca_a_caso":
        stanza = personaggio.location
        candidati = [
            o for o in stanza.contents
            if o is not personaggio and getattr(o, "vivo", False)
        ] if stanza else []
        if candidati:
            bersaglio = random.choice(candidati)
            personaggio.location.msg_contents(
                orrore(f"{personaggio.key}, sopraffatto/a dalla follia, attacca {bersaglio.key} senza motivo!")
            )
            personaggio.avvia_combattimento(bersaglio)
    elif azione == "fugge":
        from world.combat import tenta_fuga
        personaggio.msg(orrore("Un panico improvviso ti spinge a fuggire, anche se stai vincendo."))
        tenta_fuga(personaggio)
    elif azione == "non_fugge":
        personaggio.db.wimpy_soglia_ignorata_temp = True
        personaggio.msg(orrore("Qualcosa dentro di te rifiuta di fuggire, qualunque cosa succeda."))


def terapia_disponibile(stanza):
    """C'e' un terapeuta in questa stanza?"""
    if not stanza:
        return []
    return [o for o in stanza.contents if o.db.terapeuta]


TRATTAMENTI_THERAPY = {
    "base": ("una seduta di base", 20, 15),
    "intensiva": ("una seduta intensiva", 60, 40),
    "completa": ("una seduta completa", 150, 100),
}


def esegui_therapy(personaggio, terapeuta, trattamento_id):
    """THERAPY <trattamento>: a pagamento, non garantita."""
    trattamento = TRATTAMENTI_THERAPY.get(trattamento_id)
    if not trattamento:
        return False, "Trattamento sconosciuto. Usa THERAPY per vedere la lista."
    nome, costo, recupero_max = trattamento
    oro = personaggio.db.gold or 0
    if oro < costo:
        return False, f"{nome.capitalize()} costa {costo} oro: non ne hai abbastanza."

    personaggio.db.gold = oro - costo
    if random.randint(1, 100) <= 20:
        return False, f"{terapeuta.key} fa del proprio meglio, ma {nome} non sortisce alcun effetto."

    recupero = random.randint(recupero_max // 2, recupero_max)
    personaggio.db.sanity = min(personaggio.db.sanity_max or 100, (personaggio.db.sanity or 0) + recupero)
    return True, f"{terapeuta.key} ti somministra {nome}: recuperi {recupero} sanity."


def esegui_psychology(guaritore, bersaglio):
    """PSYCHOLOGY <personaggio>: gratuita ma costa 300 movimento. Fase 1:
    valida e avvia la seduta, che si risolve da sola dopo
    DURATA_PSYCHOLOGY_SECONDI (~30s, confermato dalla fonte - la
    costante esisteva gia' ma non era mai stata usata). Ritorna
    (ok, messaggio_immediato); l'esito finale arriva via guaritore.msg()
    da _completa_psychology. La fonte non descrive un'interruzione per
    PSYCHOLOGY (a differenza dello spell casting): qui non se ne inventa
    una non documentata."""
    if guaritore.skill_rating("self_discipline") <= 0 and guaritore.skill_rating("psychology") <= 0:
        return False, "Non conosci la skill Psicologia."
    if guaritore.db.sessione_psicologia_in_corso:
        return False, "Stai gia' conducendo una seduta di psicologia."
    if (guaritore.db.move or 0) < COSTO_PSYCHOLOGY_MOVIMENTO:
        return False, "Non hai abbastanza movimento per una seduta di psicologia."

    guaritore.db.move -= COSTO_PSYCHOLOGY_MOVIMENTO
    guaritore.db.sessione_psicologia_in_corso = {"bersaglio": bersaglio}

    from evennia.utils import delay
    delay(DURATA_PSYCHOLOGY_SECONDI, _completa_psychology, guaritore)
    return True, f"Cominci una seduta di psicologia con {bersaglio.key}..."


def _completa_psychology(guaritore):
    # callback programmata: chi cura puo' non esistere piu' quando arriva
    if not guaritore.pk:
        return
    dati = guaritore.db.sessione_psicologia_in_corso
    if not dati:
        return
    guaritore.db.sessione_psicologia_in_corso = None
    bersaglio = dati["bersaglio"]
    if not bersaglio.pk:
        guaritore.msg("Il bersaglio della tua seduta di psicologia non e' piu' disponibile.")
        return

    rating = max(guaritore.skill_rating("psychology"), guaritore.skill_rating("self_discipline"))

    sanity_guaritore = guaritore.db.sanity or 0
    sanity_bersaglio = bersaglio.db.sanity or 0
    percentuale_successo = max(5, min(95, rating - max(0, sanity_guaritore - sanity_bersaglio) // 5))

    if random.randint(1, 100) > percentuale_successo:
        contraccolpo = random.randint(2, 8)
        guaritore.db.sanity = max(0, sanity_guaritore - contraccolpo)
        guaritore.msg(
            f"Il tentativo di aiutare {bersaglio.key} ti si ritorce contro: "
            f"perdi {contraccolpo} sanity."
        )
        return

    recupero = random.randint(5, 15)
    bersaglio.db.sanity = min(bersaglio.db.sanity_max or 100, sanity_bersaglio + recupero)
    guaritore.msg(f"Aiuti {bersaglio.key} a recuperare {recupero} sanity.")
