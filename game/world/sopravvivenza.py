"""
Fame e sete (Fase G, prima tornata): confermato dalla scansione
esaustiva del sito originale (research/REPORT.md, helps/eat.txt) come
meccanica REALE, non solo un consiglio di buon senso come pensavamo
prima di leggere la fonte per intero:

    "hunger and/or thirst can seriously weaken your character,
    eventually leading to death."

La fonte non specifica pero' i numeri esatti (soglie, velocita' di
aumento, entita' della penalita', danno da fame/sete acuta): quelli
qui sotto sono scelte di design esplicite, facili da ritarare.

Nomi degli attributi: NON "fame" (gia' usato da Character.db.fame per
i punti Fama/reputazione, un concetto completamente diverso
nell'originale) - qui si usa "appetito" (bisogno di cibo) e "sete"
(bisogno di acqua), entrambi 0 (sazio/idratato) - 100 (morente).

Incantesimi confermati dalla fonte, poi implementati in tornate
successive (world/magic.py): CREATE FOOD/CREATE BUFFET, CREATE
WATER/CREATE SPRING (Fase K, sesta tornata); ASCETICISM (sospende il
bisogno), BURNING THIRST/GNAWING HUNGER (infliggono fame/sete al
bersaglio - Fase K, settima tornata).
"""

from world.colori import pericolo

SOGLIA_AVVISO = 50       # "hai fame"/"hai sete" - solo messaggio
SOGLIA_PENALITA = 80     # penalita' meccanica (vedi typeclasses/living.py)
SOGLIA_CRITICA = 100     # inizia il danno periodico

PENALITA_COLPIRE = 15    # malus a calcola_hit_chance oltre SOGLIA_PENALITA
DANNO_CRITICO = 3        # danno per tick oltre SOGLIA_CRITICA (per fame E sete)

AUMENTO_PER_TICK = 5     # quanto sale appetito/sete a ogni tick di sopravvivenza


def stato_bisogno(valore):
    """Descrizione testuale di un livello di appetito/sete (0-100)."""
    if valore >= SOGLIA_CRITICA:
        return "critico"
    if valore >= SOGLIA_PENALITA:
        return "grave"
    if valore >= SOGLIA_AVVISO:
        return "presente"
    return "nessuno"


def penalita_fame_sete(personaggio):
    """Malus totale a calcola_hit_chance per fame e/o sete gravi/critiche
    (usato da typeclasses/living.py)."""
    malus = 0
    if (personaggio.db.appetito or 0) >= SOGLIA_PENALITA:
        malus += PENALITA_COLPIRE
    if (personaggio.db.sete or 0) >= SOGLIA_PENALITA:
        malus += PENALITA_COLPIRE
    return malus


def applica_tick_sopravvivenza(personaggio):
    """Fa avanzare fame/sete di un personaggio di un tick; applica danno
    critico se necessario. Ritorna True se il personaggio e' morto per
    fame/sete in questo tick (per lasciare che il chiamante gestisca la
    morte con world.combat.gestisci_morte)."""
    if (personaggio.db.stati or {}).get("ascetismo"):
        # Fase K, settima tornata: incantesimo Ascetismo - sospende del
        # tutto il bisogno di cibo/acqua per la sua durata.
        return False
    appetito = min(100, (personaggio.db.appetito or 0) + AUMENTO_PER_TICK)
    sete = min(100, (personaggio.db.sete or 0) + AUMENTO_PER_TICK)
    appetito_prima = personaggio.db.appetito or 0
    sete_prima = personaggio.db.sete or 0
    personaggio.db.appetito = appetito
    personaggio.db.sete = sete

    if appetito_prima < SOGLIA_AVVISO <= appetito:
        personaggio.msg("Ti brontola lo stomaco: hai fame.")
    if sete_prima < SOGLIA_AVVISO <= sete:
        personaggio.msg("Hai la gola secca: hai sete.")

    danno = 0
    if appetito >= SOGLIA_CRITICA:
        personaggio.msg(pericolo("Lo stomaco vuoto ti sta divorando dal di dentro."))
        danno += DANNO_CRITICO
    if sete >= SOGLIA_CRITICA:
        personaggio.msg(pericolo("La sete ti sta prosciugando."))
        danno += DANNO_CRITICO

    if danno:
        return personaggio.subisci_danno(danno, fisico=False)
    return False


def mangia(personaggio, oggetto):
    """EAT: consuma un oggetto con db.cibo impostato (valore nutritivo), o
    con db.mana_ripristino (Fase K, decima tornata: Riserva di Mana -
    pillola di mana creata da CAST 'MANA STORAGE'). Ritorna (ok, messaggio).
    Confermato dalla fonte (helps/eat.txt): "You can eat and drink while
    debating and casting spells, but not during combat" - da qui il
    controllo qui sotto, condiviso anche da FEED (commands/
    cthulhu_sopravvivenza.py) dato che entrambi passano da questa
    funzione."""
    if getattr(personaggio, "in_combattimento", False):
        return False, "Non puoi mangiare mentre sei in combattimento."
    if oggetto.db.mana_ripristino:
        # FEED puo' far mangiare un NPC, che non ha mana_max: in quel caso
        # l'oggetto si consuma senza effetto invece di sollevare TypeError.
        if personaggio.db.mana_max is not None:
            personaggio.db.mana = min(personaggio.db.mana_max, (personaggio.db.mana or 0) + oggetto.db.mana_ripristino)
        oggetto.delete()
        return True, f"Mangi {oggetto.key} e senti il mana rifluire in te."
    valore = oggetto.db.cibo
    if not valore:
        return False, f"{oggetto.key} non si puo' mangiare."
    personaggio.db.appetito = max(0, (personaggio.db.appetito or 0) - valore)
    oggetto.delete()
    return True, f"Mangi {oggetto.key}."


def bevi(personaggio, oggetto):
    """DRINK: consuma un oggetto con db.bevanda impostato (valore
    idratante). Se l'oggetto e' stato benedetto (Fase K, decima tornata:
    CAST 'BESTOW BLESSING') applica anche il beneficio di Benedizione, o
    danno se chi beve e' non-morto. Ritorna (ok, messaggio). Stesso
    controllo di mangia() sul combattimento (helps/eat.txt)."""
    if getattr(personaggio, "in_combattimento", False):
        return False, "Non puoi bere mentre sei in combattimento."
    valore = oggetto.db.bevanda
    if not valore:
        return False, f"{oggetto.key} non si puo' bere."
    personaggio.db.sete = max(0, (personaggio.db.sete or 0) - valore)
    messaggio_extra = ""
    if oggetto.db.benedizione:
        e_non_morto = bool(
            getattr(personaggio, "db", None)
            and (personaggio.db.non_morto or personaggio.db.sottorazza in ("lich", "vampire"))
        )
        if e_non_morto:
            import random
            danno = random.randint(10, 18)
            personaggio.subisci_danno(danno, fisico=False)
            messaggio_extra = " La benedizione ti brucia dall'interno!"
        else:
            personaggio.db.bonus_colpire = (personaggio.db.bonus_colpire or 0) + 15
            if not personaggio.scripts.get("bless_expire"):
                personaggio.scripts.add("typeclasses.scripts.BlessExpireScript")
            messaggio_extra = " Ti senti improvvisamente benedetto/a."
    oggetto.delete()
    return True, f"Bevi {oggetto.key}.{messaggio_extra}"


def avvia_sopravvivenza():
    """Crea lo script globale del tick fame/sete se non e' gia' in
    esecuzione (idempotente, come tutti i builder di questa fase)."""
    from evennia.scripts.models import ScriptDB

    esistente = ScriptDB.objects.filter(db_key="sopravvivenza")
    if esistente:
        return esistente[0]

    from evennia.utils import create
    return create.create_script("typeclasses.scripts.SopravvivenzaScript")
