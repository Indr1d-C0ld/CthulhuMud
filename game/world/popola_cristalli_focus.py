"""
Popolamento dei Cristalli Focus Yithiani (Fase K, settima tornata):
la fonte non specifica come uno Yithiano ottenga il PRIMO cristallo
(nessuna pagina descrive un negozio o un drop specifico) - scelta di
design esplicita: alcuni cristalli "di partenza" sono lasciati nel
Giardino a Cupola della Grande Biblioteca Yithiana, l'hub newbie della
razza, cosi' che un nuovo personaggio Yithiano possa semplicemente
raccoglierne uno.
"""

from world.focus_crystal import crea_cristallo
from world.rooms_newbie import stanza_per_ruolo


def popola_cristalli_focus():
    stanza = stanza_per_ruolo("yithian_library", "recall")
    if not stanza:
        return []
    esistenti = [o for o in stanza.contents if o.db.tipo_oggetto == "cristallo_focus"]
    if esistenti:
        return esistenti
    return [crea_cristallo(stanza) for _ in range(3)]
