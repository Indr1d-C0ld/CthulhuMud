"""
Oggetti di scena del Cairo (Fase I, quarta e ultima tornata): vedi
world/scenografia.py per il meccanismo e le tranche precedenti per il
metodo. Ogni ED e' radicato in un dettaglio GIA' presente nella
descrizione originale della stanza (world/rooms_cairo.py).

Zona a rischio collisioni quanto Zoog Village: tutte e 12 le aree
generali hanno un NPC di ambientazione nominato (facchino, guida
turistica, sentinella, donna che innaffia i gelsomini, muezzin...) e
tutte e 7 le botteghe del Bazaar hanno un negoziante reale e veri
articoli in vendita (sciabole, vino, pane...). Parole chiave scelte
per evitare entrambi, verificato con lo stesso controllo dal vivo
usato per Arkham e Zoog Village.

Copertura: tutte le 19 stanze (12 aree + 7 botteghe del Bazaar). Con
questa tranche, tutte e sei le zone della lista originale hanno una
prima copertura di oggetti di scena (182 stanze in totale: 23+6+7+
108+19+19).
"""

from evennia.utils import search

from world.scenografia import aggiungi_ed

# {chiave_area: [(parole, testo), ...]}
ED_AREE = {
    "bazaar": [(["spezie"], "Sacchi aperti di cumino, cannella e zafferano colorano l'aria di polvere dorata a ogni colpo di vento."), (["narghile"], "Il fumo dolciastro si arrotola pigro sopra le teste della folla, mai abbastanza denso da coprire del tutto l'odore di spezie e sudore.")],
    "docks": [(["battelli"], "Ormeggiati fianco a fianco lungo la riva fangosa, scricchiolano appena a ogni onda sollevata dal passaggio dei piroscafi piu' grandi."), (["casse"], "Impilate sotto il sole, alcune segnate con destinazioni lontane - Boston, Providence, Londra - altre senza alcuna etichetta.")],
    "city_gates": [(["arco"], "Pietra massiccia, consumata da secoli di carovane in transito. Iscrizioni troppo antiche per essere lette restano incise vicino alla sommita'."), (["foschia"], "Si alza dall'altopiano oltre le porte, tremolante nel calore, abbastanza densa da inghiottire ogni sagoma a poca distanza.")],
    "pyramids": [(["vento"], "Caldo e costante, porta con se' un silenzio innaturale che nessuna guida turistica riesce mai a descrivere davvero.")],
    "sphinx": [(["volto"], "Consumato dal tempo e dalla sabbia, gli occhi di pietra sembrano fissare un punto ben preciso dell'orizzonte, non l'orizzonte in generale."), (["orizzonte"], "Piatto e bruciato dal sole, interrotto solo dalla sagoma lontana delle piramidi.")],
    "administrative_area": [(["facciate"], "Imbiancate di fresco, gia' segnate da crepe sottili che l'intonaco non riesce a nascondere del tutto.")],
    "british_citadel": [(["pietra"], "Chiara e squadrata, tagliata con una precisione che tradisce mani e strumenti non locali.")],
    "residential_ne": [(["balconi"], "Intagliati a mano in motivi geometrici complessi, si affacciano su cortili interni all'ombra."), (["cortili"], "Freschi anche nelle ore piu' calde del giorno, nascosti alla vista dalla strada principale.")],
    "residential_se": [(["case"], "Piu' modeste di quelle a nord-est, ma curate con la stessa dignitosa attenzione da chi le abita.")],
    "slums": [(["vicoli"], "Stretti abbastanza da toccare entrambe le pareti allargando le braccia, si intrecciano in un labirinto che nessuna mappa ufficiale registra per intero."), (["case"], "Fatiscenti, alcune sorrette da travi di fortuna che sembrano poter cedere da un momento all'altro.")],
    "causeway": [(["inondazioni"], "I segni lasciati dalle piene annuali del Nilo sono visibili come linee scure sulla pietra della strada rialzata, sempre piu' in alto di quanto ci si aspetterebbe.")],
    "great_mosque": [(["minareti"], "Svettano contro il cielo, la pietra chiara quasi accecante sotto il sole di mezzogiorno.")],
    "anubis_hotel": [(["statua"], "Anubi a grandezza naturale, lo sguardo rivolto verso l'ingresso. Alcuni ospiti giurano che muova la testa quando nessuno guarda direttamente.")],
    "cloth_merchant": [(["soffitto"], "Basso abbastanza da sfiorare la testa dei clienti piu' alti, a stento visibile sotto le pile di stoffa che arrivano quasi a toccarlo.")],
    "farmers_stall": [(["teli"], "Colorati, stesi a terra con cura per proteggere il raccolto dalla polvere sollevata dal viavai del bazaar.")],
    "abduls_armoury": [(["pareti"], "Coperte fino all'ultimo centimetro libero, ogni oggetto appeso con un ordine che tradisce anni di pratica.")],
    "winemakers_shop": [(["scaffali"], "Di legno scuro, piegano leggermente sotto il peso di decine di anfore allineate con cura.")],
    "falcon_armory": [(["europa"], "Le casse di importazione portano ancora etichette doganali europee, alcune scritte in lingue che i clienti abituali non sanno leggere.")],
    "bakery": [(["odore"], "Pane caldo e miele si mescolano in una nube che si sente ben prima di vedere l'ingresso della panetteria, richiamando chiunque passi nel raggio di qualche isolato.")],
}


def _imposta_eds(stanza, voci):
    for parole, testo in voci:
        aggiungi_ed(stanza, parole, testo)


def popola_eds_cairo():
    n = 0
    for chiave, voci in ED_AREE.items():
        tag = f"cairo_shop_{chiave}" if chiave in (
            "anubis_hotel", "cloth_merchant", "farmers_stall",
            "abduls_armoury", "winemakers_shop", "falcon_armory", "bakery",
        ) else f"cairo_{chiave}"
        stanze = search.search_tag(tag, category="cairo_room")
        if not stanze:
            continue
        _imposta_eds(stanze[0], voci)
        n += 1
    return n
