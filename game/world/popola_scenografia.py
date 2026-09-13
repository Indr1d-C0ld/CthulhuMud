"""
Popolamento degli oggetti di scena (Fase I, prima tornata): vedi
world/scenografia.py per il meccanismo. Ogni voce qui sotto e'
radicata in un dettaglio GIA' presente nella descrizione della stanza
(coerente con la fonte: "Prominent features in your room description
should be given their own extended description").

Prima tranche (di quattro): il relitto del sommergibile (23 stanze -
la piu' ricca di dettagli atmosferici gia' scritti), le Dreamlands
overworld (6) e Ulthar (7) = 36 stanze. Le tornate successive (Fase I,
seconda-quarta) hanno completato anche Arkham (world/popola_scenografia_arkham.py,
108 stanze), Zoog Village (world/popola_scenografia_zoog.py, 19) e
Cairo (world/popola_scenografia_cairo.py, 19): tutte e sei le zone
sono complete, 182 stanze totali.
"""

from evennia.utils import search

from world.scenografia import aggiungi_ed

# {numero_stanza: [(parole, testo), ...]}
ED_SOMMERGIBILE = {
    1: [
        (["scafo"], "Il metallo e' piegato ma non squarciato, in questo tratto: le lamiere gemono appena sotto il peso dell'acqua, come se il relitto respirasse ancora, lentissimamente."),
        (["fondale", "fondo"], "Uno strato di limo grigiastro copre ogni superficie orizzontale, indisturbato da decenni. Qualcosa vi ha lasciato solchi paralleli, troppo regolari per essere corrente."),
    ],
    2: [
        (["scaffali"], "Il metallo arrugginito si sgretola al tocco. Un tempo reggevano ordinatamente manuali e carte nautiche; ora reggono solo poltiglia."),
        (["manuali", "mappe", "carte"], "Pagine fuse in un unico blocco fradicio. Qui e la' si intravede ancora un frammento di rotta tracciata a matita, diretta verso un punto del mare senza nome."),
    ],
    3: [
        (["cuccetta"], "Stretta e rigida, ancora rifatta con cura militare. Le coperte sono rigonfie d'acqua ma intatte, come se il loro occupante potesse tornare da un momento all'altro."),
        (["scrivania"], "Avvitata al pavimento per resistere al moto ondoso. I cassetti sono bloccati dalla ruggine, tranne uno: vuoto, aperto, come svuotato in fretta."),
        (["diario", "diario di bordo"], "L'inchiostro e' sbiadito in macchie illeggibili, tranne l'ultima pagina scritta: poche righe frenetiche, poi nulla. Alcune pagine successive sono state strappate, non marcite."),
    ],
    4: [
        (["tubi", "tubi lanciasiluri"], "Il metallo e' freddo al tatto anche attraverso i guanti. Uno dei due tubi porta ancora inciso, a stento leggibile, un numero di serie."),
        (["oscurita"], "Oltre lo squarcio nello scafo non si vede altro che nero assoluto - l'acqua qui e' piu' fonda di quanto la luce di una torcia possa mai rivelare."),
    ],
    5: [
        (["lamiere"], "Contorte verso l'interno, come piegate da una pressione applicata dall'esterno piuttosto che da un'esplosione dall'interno."),
    ],
    6: [
        (["boccaporto"], "La ruggine ha saldato la ghiera di chiusura in una massa unica e informe. Nessuna quantita' di forza sembra sufficiente a smuoverla."),
    ],
    7: [
        (["ruota", "timone"], "I raggi di ottone sono ancora lucidi al tatto, stranamente privi della patina verde che ricopre ogni altro metallo qui intorno. Qualcuno, o qualcosa, la tiene pulita."),
    ],
    8: [
        (["scaletta"], "I pioli sono corrosi ma solidi. In alto, un cerchio di luce piu' scura si apre verso la torretta; in basso, l'oscurita' del corridoio principale."),
    ],
    9: [
        (["periscopio"], "L'ottica e' incrinata da cima a fondo. Guardandoci dentro si vede solo il proprio occhio riflesso, ingrandito e distorto."),
    ],
    10: [
        (["budello", "corridoio"], "Appena piu' largo delle spalle di un uomo. Le pareti portano graffi orizzontali, all'altezza di una mano, ripetuti per tutta la lunghezza del corridoio."),
    ],
    11: [
        (["tubi", "grilletto"], "I meccanismi di lancio sono ancora armati. Un cartellino d'ordinanza, ormai illeggibile, pende da un anello vicino al grilletto piu' vicino."),
    ],
    12: [
        (["brande"], "Sovrapposte su tre livelli. Alcune sono sfatte come se nessuno le avesse mai toccate; altre, inspiegabilmente, sono rifatte con angoli militari perfetti."),
    ],
    13: [
        (["tavolo"], "Lungo abbastanza per l'intero equipaggio. Incisioni di noia - iniziali, piccole scacchiere, un calendario contato a graffi - ne coprono la superficie."),
        (["piatti"], "Di latta, impilati o sparsi a seconda di dove la pendenza del pavimento li ha fatti scivolare. In uno, ancora, i resti anneriti di un pasto mai finito."),
    ],
    14: [
        (["fornelli"], "Il metallo e' incrostato di ruggine e sale. Una pentola e' ancora al suo posto sul fornello, il contenuto ridotto a una crosta nerastra."),
        (["barattoli", "conserve"], "Gonfi fino quasi a scoppiare, alcuni gia' spaccati. L'odore, a distanza di decenni, resta inspiegabilmente presente nell'aria stagnante."),
    ],
    15: [
        (["falla", "squarcio"], "I bordi del metallo sono piegati verso l'esterno, non verso l'interno - qualunque cosa sia successa qui, ha spinto da dentro verso fuori, oppure e' entrata con una forza enorme."),
    ],
    16: [
        (["cappotto"], "Un cappotto d'ordinanza da ufficiale, ancora appeso a un gancio. I bottoni d'ottone sono anneriti ma intatti; le tasche, vuote."),
    ],
    17: [
        (["motori"], "Due blocchi diesel enormi, silenziosi da decenni. Le valvole sono bloccate a meta' ciclo, come se il motore si fosse fermato di colpo, non gradualmente."),
    ],
    18: [
        (["batterie"], "File di celle corrose, alcune spaccate. L'odore acre che ancora impregna l'aria non dovrebbe, per chimica, essere ancora presente dopo tutto questo tempo."),
    ],
    19: [
        (["alghe"], "Un sottile strato fosforescente ricopre i motori elettrici, pulsando debolmente nel buio - troppo regolare per essere naturale, quasi un respiro."),
    ],
    20: [
        (["compressori"], "Immobili e silenziosi. Uno dei manometri, inspiegabilmente, segna ancora una pressione residua, l'ago fermo un poco sopra lo zero."),
    ],
    21: [
        (["fessura"], "Una crepa sottile nello scafo, da cui l'acqua nera filtra goccia a goccia verso l'esterno - o forse verso l'interno, e' difficile dirlo osservandola a lungo."),
    ],
    22: [
        (["parete", "tubo"], "Il metallo curvo del tubo e' freddo e umido. Impronte di unghie, poco profonde ma innegabili, corrono lungo la parete per tutta la sua lunghezza."),
    ],
    23: [
        (["branda", "cinghie"], "Le cinghie di contenimento sono consumate al centro, non ai bordi - come se qualcuno vi si fosse dibattuto contro, ripetutamente, per molto tempo."),
    ],
}

# {chiave_stanza: [(parole, testo), ...]}
ED_DREAMLANDS = {
    "crocevia": [
        (["segnavia", "segnali"], "Il legno e' consumato dal tempo onirico, non dagli agenti atmosferici. Le scritte cambiano leggermente ogni volta che si distoglie lo sguardo - mai abbastanza da perdersi, ma abbastanza da non fidarsi mai del tutto."),
    ],
    "verso_ulthar": [
        (["gatti"], "Decine di occhi, di ogni colore, osservano dai cespugli senza mai ammiccare. Nessuno di questi gatti sembra avere fretta, ne' paura."),
        (["mura", "ulthar"], "Le mura di Ulthar, ancora lontane, sembrano piu' vicine ogni volta che si smette di fissarle direttamente."),
    ],
    "presso_nir": [
        (["campi"], "File ordinate di grano dorato che nessuno sembra mai raccogliere, e che pure non marcisce mai sui gambi."),
        (["nir", "citta"], "I tetti di Nir spuntano appena oltre il declivio, troppo lontani per distinguerne i dettagli - e forse e' meglio cosi'."),
    ],
    "verso_bosco": [
        (["alberi", "tronchi"], "Corteccia grigia, quasi metallica al tatto. Alcuni tronchi portano incisioni che assomigliano a volti, cancellati a meta' da chi li aveva iniziati."),
        (["chiacchiericcio", "zoog"], "Un brusio sommesso, fatto di voci troppo acute per essere umane, che si interrompe di colpo ogni volta che ci si ferma ad ascoltare."),
    ],
    "presso_hatheg": [
        (["ponte"], "Pietra levigata da secoli di passi, eppure priva di crepe o cedimenti. Nessuno ricorda chi l'abbia costruito."),
        (["hatheg", "tetti"], "I tetti di Hatheg, ai piedi del lontano Monte Hatheg-Kla, hanno lo stesso rosso cupo del tempio di Ulthar - una coincidenza che nessun viandante ha mai saputo spiegare."),
    ],
    "lungofiume_skai": [
        (["fiume", "skai", "acque"], "La corrente scorre in una direzione che non corrisponde mai del tutto alla pendenza visibile del terreno. L'acqua e' fredda, scura, e stranamente silenziosa."),
        (["dylath-leen", "torri"], "In lontananza, appena visibili contro il cielo, si stagliano le torri di basalto nero di Dylath-Leen - troppo regolari, troppo alte, per essere state innalzate da mani umane."),
    ],
}

# {chiave_stanza: [(parole, testo), ...]}
ED_ULTHAR = {
    "hatheg_way": [
        (["gatti"], "Sonnecchiano sui davanzali di pietra in ogni colore immaginabile, aprendo un occhio solo quanto basta per verificare che il passante non porti cattive intenzioni."),
        (["case", "davanzali"], "Pietra grigia levigata da secoli di zampe e code. Ogni davanzale sembra scolpito apposta per ospitare comodamente un gatto addormentato."),
    ],
    "barzai_street": [
        (["acciottolato"], "Le pietre sono lisce e irregolari, disposte in un motivo che a tratti ricorda, se osservato da certi angoli, una costellazione."),
        (["barzai"], "Il nome del saggio che salio' troppo in alto per fare ritorno e' inciso, quasi cancellato dal tempo, su una piccola targa all'inizio della via."),
    ],
    "xarnes_street": [
        (["mercanti", "merci"], "Bancarelle traboccanti di oggetti che sfidano una facile descrizione: bottiglie che contengono nuvole, chiavi che aprono porte inesistenti, specchi che riflettono un istante prima del dovuto."),
    ],
    "atal_way": [
        (["atal"], "Una statua modesta, quasi dimessa, raffigura il compagno di Barzai - l'unico tornato dalle vette proibite. Il suo sguardo di pietra e' rivolto verso il basso, non verso l'alto."),
    ],
    "calico_cross": [
        (["gatti"], "Al crepuscolo si radunano a decine, maculati di ogni sfumatura possibile, in un silenzio quasi cerimoniale rivolto verso il grande tempio a nord."),
        (["tempio"], "Il tetto di tegole rosse domina la vista da qui, visibile sopra i tetti piu' bassi della via come un faro immobile."),
    ],
    "ulthar_temple_interior": [
        (["colonne"], "Pietra bianca, lucidata fino a sembrare quasi calda al tocco nonostante la penombra del tempio."),
        (["statue", "gatti"], "Gatti di pietra, accovacciati lungo ogni parete, scolpiti con un realismo che a tratti fa dubitare che siano davvero solo statue."),
        (["incenso"], "Il profumo e' dolce in superficie, ma sotto si avverte una nota piu' antica e mineraria - non del tutto sgradevole, ma innegabilmente estranea."),
    ],
    "ulthar_fucina_maro": [
        (["incudine"], "Annerita da anni di calore e colpi, la superficie porta i solchi di innumerevoli forgiature - alcune, a giudicare dalla forma, per lame che nessun fabbro umano forgerebbe piu'."),
        (["attrezzi"], "Appesi con una precisione quasi ossessiva, ciascuno nel proprio posto esatto, come se il minimo disordine fosse per Maro un affronto personale."),
    ],
}


def _imposta_eds(stanza, voci):
    for parole, testo in voci:
        aggiungi_ed(stanza, parole, testo)


def popola_eds_sommergibile():
    """Ritorna il numero di stanze aggiornate."""
    n = 0
    for numero, voci in ED_SOMMERGIBILE.items():
        stanze = search.search_tag(f"sub_{numero}", category="submarine_room")
        if not stanze:
            continue
        _imposta_eds(stanze[0], voci)
        n += 1
    return n


def popola_eds_dreamlands():
    n = 0
    for chiave, voci in ED_DREAMLANDS.items():
        stanze = search.search_tag(f"dlo_{chiave}", category="dreamlands_overworld")
        if not stanze:
            continue
        _imposta_eds(stanze[0], voci)
        n += 1
    return n


def popola_eds_ulthar():
    n = 0
    for chiave, voci in ED_ULTHAR.items():
        if chiave == "ulthar_temple_interior":
            stanze = search.search_tag(chiave, category="ulthar_room")
        elif chiave == "ulthar_fucina_maro":
            stanze = search.search_tag(chiave, category="ulthar_room")
        else:
            stanze = search.search_tag(f"street_{chiave}", category="ulthar_room")
        if not stanze:
            continue
        _imposta_eds(stanze[0], voci)
        n += 1
    return n


def popola_tutto():
    return {
        "sommergibile": popola_eds_sommergibile(),
        "dreamlands": popola_eds_dreamlands(),
        "ulthar": popola_eds_ulthar(),
    }
