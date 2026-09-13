"""
Sistema di locanda (Fase F, settima tornata): affitta una stanza per
riposare e recuperare pienamente HP/Mana/Movimento, a pagamento, in uno
degli alberghi di Arkham o del Cairo. Come per il sistema bancario,
nessuna fonte originale reperita finora ne descrive il funzionamento
esatto di un servizio a pagamento in albergo: e' una convenzione
standard da MUD, qui implementata nella forma piu' semplice (nessun
tracciamento del tempo reale di permanenza).

Rinominato da REST ad ALLOGGIA in Fase K, quattordicesima tornata:
helps/rest.txt (controllato solo in quella tornata, non a questa)
rivela che REST e' in realta' un comando universale di posizione
(REST/SLEEP/STAND/WAKE, vedi world/posizione.py), non un servizio
alberghiero - il nome andava restituito al vero significato della
fonte. ALLOGGIA resta un'aggiunta dichiaratamente inventata, distinta
dal vero REST: paga per un ripristino istantaneo invece del recupero
graduale (ma piu' rapido) che REST/SLEEP offrono ovunque, gratis.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.posizione import ALBERGHI_TAGS

PREZZO_NOTTE = 10


def _trova_albergo(stanza):
    if not stanza:
        return False
    for tag, categoria in ALBERGHI_TAGS:
        if stanza.tags.get(tag, category=categoria):
            return True
    return False


class CmdAlloggia(MuxCommand):
    """
    affitta una stanza in albergo e recupera le forze all'istante

    Uso:
      alloggia
      affittacamera

    Se ti trovi in un albergo, paga il prezzo di una notte
    (10 oro) e recupera immediatamente HP, Mana e Movimento al
    massimo. Meccanica dichiaratamente inventata (vedi modulo): per
    il vero comando di posizione della fonte, usa REST o SLEEP.
    """

    key = "alloggia"
    aliases = ["affittacamera"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not _trova_albergo(caller.location):
            caller.msg("Non sei in un albergo.")
            return

        oro = caller.db.gold or 0
        if oro < PREZZO_NOTTE:
            caller.msg(
                f"Una stanza per la notte costa {PREZZO_NOTTE} oro, ma ne hai solo {oro}."
            )
            return

        caller.db.gold = oro - PREZZO_NOTTE
        caller.db.hp = caller.db.hp_max
        caller.db.mana = caller.db.mana_max
        caller.db.move = caller.db.move_max
        caller.db.posizione = "in_piedi"

        caller.msg(
            f"Paghi {PREZZO_NOTTE} oro per una stanza e ti concedi una notte di riposo. "
            "Ti risvegli completamente ristorato."
        )
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} si ritira in una stanza per la notte.", exclude=caller
            )
