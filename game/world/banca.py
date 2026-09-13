"""
Interesse bancario mensile (Fase F, decima tornata): vedi
typeclasses/scripts.py (InteresseBancarioScript) per il timer e
commands/cthulhu_bank.py per i comandi deposit/withdraw/balance.

TASSO_INTERESSE confermato ESATTO dalla scansione esaustiva del sito
originale (2026-09-12, vedi research/REPORT.md): l'1% al mese non era
una scelta di design arbitraria come pensavamo, ma il valore vero.
"""

TASSO_INTERESSE = 0.01  # 1% al "mese" (vedi InteresseBancarioScript) - confermato dalla fonte


def applica_interesse_a_tutti():
    """Aggiunge l'interesse all'Oro in banca di ogni personaggio che ne
    ha. Chiamata dal tick di InteresseBancarioScript."""
    from evennia.objects.models import ObjectDB

    personaggi = ObjectDB.objects.filter(
        db_typeclass_path="typeclasses.characters.Character"
    )
    for personaggio in personaggi:
        saldo = personaggio.db.banca or 0
        if saldo <= 0:
            continue
        interesse = max(1, int(saldo * TASSO_INTERESSE))
        personaggio.db.banca = saldo + interesse
        personaggio.msg(
            f"La tua banca accredita {interesse} oro di interessi "
            f"(nuovo saldo: {personaggio.db.banca})."
        )


def avvia_interesse_bancario():
    """Crea lo script globale se non e' gia' in esecuzione (idempotente,
    come tutti i builder di questa fase)."""
    from evennia.scripts.models import ScriptDB

    esistente = ScriptDB.objects.filter(db_key="interesse_bancario")
    if esistente:
        return esistente[0]

    from evennia.utils import create
    return create.create_script("typeclasses.scripts.InteresseBancarioScript")
