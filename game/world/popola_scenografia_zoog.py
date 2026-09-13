"""
Oggetti di scena di Zoog Village (Fase I, terza tornata): vedi
world/scenografia.py per il meccanismo e world/popola_scenografia.py /
world/popola_scenografia_arkham.py per le tranche precedenti. Ogni ED
e' radicato in un dettaglio GIA' presente nella descrizione originale
della stanza (world/rooms_zoogvillage.py).

Attenzione particolare in questa zona: quasi ogni stanza nomina uno
Zoog residente specifico (Slorril, Jhilorin, Thussis, Klorl, Flaerr,
Silaer, Chorl, Merith, Hok, Durnith, Goryth) quasi certamente gia'
presente come vero NPC di ambientazione, e diverse stanze sono botteghe
con veri oggetti in vendita - le parole chiave sono state scelte per
evitare entrambi (niente nomi propri, niente sostantivi che potrebbero
coincidere con articoli venduti), verificato con lo stesso controllo
di collisione dal vivo usato per Arkham.

Copertura: tutte le 19 stanze nominate della mappa. Deliberatamente
esclusi, come per le altre zone, gli hub newbie condivisi (Radura
Aperta/respawn, Ceppo/morgue, Sotto le Radici/recall).

Con questa tranche, le sei zone gia' esplorate (sommergibile, Dreamlands
overworld, Ulthar, Arkham, e ora Zoog Village) hanno tutte una prima
copertura di oggetti di scena; resta Cairo (19 stanze) per completare
l'elenco originale.
"""

from evennia.utils import search

from world.scenografia import aggiungi_ed

# {chiave_stanza: [(parole, testo), ...]}
ED_ZOOG = {
    "north_gate": [(["radici", "tende"], "Sottili e chiare, pendono dall'arco come tende vive, muovendosi appena anche quando non c'e' vento.")],
    "in_the_pond": [(["bolle", "fondo"], "Salgono di continuo dal fondo melmoso, in gruppetti irregolari, come se qualcosa la' sotto respirasse lentamente.")],
    "cozy_pond": [(["felci"], "Morbide al tatto, formano un cerchio quasi perfetto attorno all'acqua, come se qualcuno le avesse disposte cosi' apposta.")],
    "tree_of_souls": [(["tronco", "volti"], "Contorto in forme che ricordano vagamente volti - alcuni sembrano cambiare espressione, di poco, se li si osserva a lungo."), (["offerte"], "Piccoli oggetti lasciati alla base del tronco: sassolini, piume, cocci colorati, ciascuno con un nome sussurrato che nessuno ripete ad alta voce due volte.")],
    "high_temple": [(["rami", "muschio"], "Intrecciati con una precisione che non sembra casuale, formano pareti spesse che la luce del giorno non attraversa mai del tutto.")],
    "chamber_elders": [(["radici"], "Foderano ogni parete della cavita', spesse e contorte, quasi a formare sedili naturali attorno al centro della stanza.")],
    "slorril_home": [(["sassolini"], "Colorati, incastonati nelle pareti di terra battuta in un ordine che nessun visitatore e' mai riuscito a decifrare del tutto."), (["pareti"], "Terra battuta levigata con cura, fresca al tatto anche nelle giornate piu' calde.")],
    "jhilorin_burrow": [(["ingresso"], "Cosi' basso da costringere chiunque non sia uno Zoog a entrare carponi, la terra intorno consumata da innumerevoli passaggi.")],
    "thussis_shop": [(["tronco"], "Cavo, abbastanza ampio da ospitare l'intero emporio. Le pareti interne sono coperte di ripiani improvvisati, ciascuno stracolmo.")],
    "klorl_shop": [(["ceste"], "Intrecciate a mano, disposte in file ordinate lungo le pareti della piccola tana.")],
    "flaerr_shop": [(["chiosco"], "Costruito con assi recuperate da chissa' dove, incastrate insieme senza un vero progetto ma con sorprendente solidita'.")],
    "bakery_silaer": [(["odore"], "Pane caldo e miele di fiori onirici, un profumo che si insinua nei vestiti di chi si sofferma anche solo un momento.")],
    "blacksmith_chorl": [(["scintille", "calore"], "Volano a ogni colpo di martello, illuminando per un istante ogni angolo della piccola tana prima di spegnersi nel buio.")],
    "gem_cavern": [(["pareti"], "Scintillano di cristalli onirici a ogni movimento della luce, in un gioco di riflessi che cambia continuamente colore.")],
    "in_the_fungus": [(["funghi giganteschi", "bosco"], "Alcuni piu' alti di uno Zoog adulto, formano un bosco nel bosco - le loro cappelle oscurano quasi del tutto il cielo sopra il sentiero.")],
    "deposito": [(["cavita", "chiavi"], "La cavita' sotterranea e' fresca e asciutta, perfetta per conservare provviste. Un mazzo di chiavi di legno intagliato pende da un gancio vicino all'entrata.")],
    "durnith_log": [(["muschio"], "Cresce fitto attorno all'ingresso del tronco, punteggiato da funghi luminosi che pulsano debolmente nella penombra.")],
    "goryth": [(["radura"], "Piccola e silenziosa, l'erba schiacciata in un unico punto dove qualcuno siede, immobile, per ore ogni giorno.")],
    "empty_house": [(["cunicolo", "zoogtunnel"], "Si restringe rapidamente e si perde nel buio sottoterra. L'aria che ne esce e' piu' fredda di quella della tana, e porta un debole odore di terra smossa di recente.")],
}


def _imposta_eds(stanza, voci):
    for parole, testo in voci:
        aggiungi_ed(stanza, parole, testo)


def popola_eds_zoog():
    n = 0
    for chiave, voci in ED_ZOOG.items():
        stanze = search.search_tag(f"zv_{chiave}", category="zoogvillage_room")
        if not stanze:
            continue
        _imposta_eds(stanze[0], voci)
        n += 1
    return n
