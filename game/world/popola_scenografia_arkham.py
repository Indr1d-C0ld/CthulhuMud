"""
Oggetti di scena di Arkham (Fase I, seconda tornata): vedi
world/scenografia.py per il meccanismo e world/popola_scenografia.py
per la prima tranche (sommergibile/Dreamlands/Ulthar). Ogni ED qui
sotto e' radicato in un dettaglio GIA' presente nella descrizione
originale della via o dell'edificio (world/rooms_arkham.py,
world/rooms_arkham_edifici.py) - stesso metodo della prima tranche.

Copertura: tutte le 36 vie e tutti i 72 edifici con una propria
descrizione in world/rooms_arkham_edifici.py. Esclusa deliberatamente
"Mortis & Carver" (riusa la stanza-morgue dell'hub newbie, gia' fuori
scope per gli oggetti di scena come gli altri hub). Con questo, Arkham
e' completa; restano Cairo (19) e Zoog Village (19) per la prossima
tranche.
"""

from evennia.utils import search

from world.scenografia import aggiungi_ed

# {chiave_via: [(parole, testo), ...]}
ED_VIE = {
    "garrison_nord": [(["ponte", "miskatonic"], "Il fiume scorre lento sotto le arcate di pietra. Sulla sponda opposta, appena visibile, la città vecchia sembra sempre un poco più scura del previsto.")],
    "garrison_sud": [(["carrozze", "automobili", "traffico"], "Il viavai di carrozze e automobili non si ferma mai del tutto, nemmeno a tarda notte - come se la città avesse fretta di essere altrove.")],
    "peabody_nord": [(["osservatorio"], "La cupola di rame dell'osservatorio spunta oltre i tetti, verso ovest, sempre rivolta verso un punto del cielo che nessun astronomo ha mai voluto precisare.")],
    "peabody_sud": [(["passanti", "viavai"], "Impiegati e agenti in uniforme si incrociano senza quasi guardarsi, diretti verso il commissariato con la stessa espressione stanca.")],
    "west_nord": [(["fiume"], "La via scende dolcemente verso l'acqua, dove la corrente del Miskatonic scorre piu' scura che altrove.")],
    "west_sud": [(["edifici"], "Edifici pubblici e case signorili si alternano senza un vero ordine, come se la via non riuscisse a decidere cosa vuole essere.")],
    "derby_ovest": [(["negozi"], "Vetrine di ogni genere si affiancano senza soluzione di continuità, illuminate a giorno anche nelle ore più buie.")],
    "derby_est": [(["case"], "Le case qui hanno giardini piu' curati e finestre piu' silenziose del tratto occidentale della stessa via.")],
    "curwen_ovest": [(["case"], "Le facciate sono più vecchie che altrove in città, con pietre annerite da un tempo che sembra essersi fermato un po' prima che altrove.")],
    "hyde_ovest": [(["negozi"], "Vetrine di mobili e forniture per la casa si susseguono in un silenzio quasi compassato.")],
    "armitage_ovest": [(["fischio", "treni"], "Il fischio dei treni in arrivo si sente distintamente da qui, un lamento metallico che rimbalza tra le facciate.")],
    "federal_nord": [(["porto"], "L'odore di salsedine e catrame arriva dal porto poco distante, portato da un vento che sembra sempre soffiare nella stessa direzione.")],
    "fishe_nord": [(["molo"], "Il molo si intravede in fondo alla via, tra le insegne degli artigiani, e con esso un lieve, costante odore di pesce.")],
    "jenkin_nord": [(["incrocio"], "L'incrocio e' dominato dalla facciata del Grand Hotel, le cui luci restano accese ben oltre l'ora in cui le altre si spengono.")],
    "whatley_nord": [(["nome", "famiglia"], "Il nome della via non compare su nessuna targa ufficiale della città - solo su quelle piu' vecchie, quasi a volerlo dimenticare senza cancellarlo del tutto.")],
    "goode_nord": [(["riva"], "La riva del fiume e' vicina abbastanza da sentirne il gorgoglio, anche di notte, quando ogni altro suono cittadino tace.")],
    "apple_nord": [(["meli"], "I meli piantati lungo il vicolo non danno frutti da anni, eppure nessuno li ha mai tagliati.")],
    "water_nord": [(["ponti"], "I tre ponti che collegano le due sponde del Miskatonic si vedono da qui in fila, uno dietro l'altro, come tre archi di un unico disegno.")],
    "river_ovest": [(["fiume"], "L'acqua scorre appena oltre i ponti, piu' silenziosa qui che altrove lungo il suo corso cittadino.")],
    "main_ovest": [(["negozi"], "Le insegne si susseguono senza interruzione, l'arteria commerciale piu' trafficata della città vecchia.")],
    "church_ovest": [(["negozi", "case di culto"], "Negozi e case di culto si affacciano fianco a fianco sulla stessa via, il commercio e la fede che si dividono lo stesso marciapiede.")],
    "church_est": [(["french hill"], "La via sale dolcemente verso il quartiere di French Hill, sempre più residenziale a ogni passo.")],
    "college_ovest": [(["edifici"], "Edifici pubblici e istituzioni cittadine si allineano con una uniformità quasi militare, tutti costruiti nello stesso decennio.")],
    "college_est": [(["insegna", "lettere"], "L'insegna della prima banca di Arkham e' visibile in fondo alla via, le sue lettere dorate mai completamente lucide.")],
    "pickman_ovest": [(["nome"], "Il nome della via evoca, per chi conosce certe voci sulla città, associazioni che pochi residenti sono disposti a discutere apertamente.")],
    "pickman_est": [(["porto"], "Il tratto orientale conduce dritto al porto passeggeri, l'odore di mare che si fa piu' insistente a ogni passo.")],
    "miskatonic_ovest": [(["cupola"], "La cupola dell'osservatorio domina la vista in fondo al viale, un punto fisso attorno a cui tutto il resto sembra ruotare.")],
    "washington_ovest": [(["case"], "Case tranquille, per lo piu' silenziose anche di giorno, come se i loro abitanti preferissero non farsi notare.")],
    "washington_est": [(["istituto", "arte"], "La facciata dell'Istituto d'Arte si intravede poco oltre, le sue finestre sempre illuminate anche a tarda sera.")],
    "bad_water_sud": [(["nome"], "Nessuno in città ricorda con certezza da dove venga il nome di questa strada, ne' perche' l'acqua qui evocata non sia mai stata vista da nessuno.")],
    "boundary_sud": [(["confine"], "Un vecchio cippo di pietra, quasi illeggibile, segna ancora il punto in cui un tempo finiva la città vecchia.")],
    "crane_ovest": [(["quiete"], "Un silenzio insolito avvolge questa via anche nelle ore piu' animate della giornata, come se i suoni preferissero non attraversarla.")],
    "lich_est": [(["muri", "cinta", "edera"], "I muri di cinta del vecchio cimitero cittadino corrono lungo un intero lato della via, coperti di edera che nessuno sembra mai potare.")],
    "powder_mill_sud": [(["mulino"], "Delle fondamenta dell'antico mulino da polvere da sparo restano solo pietre sparse tra l'erba, che nessuno ha mai pensato di rimuovere del tutto.")],
    "parsonage_sud": [(["guglie"], "Le guglie della basilica di San Genesio svettano poco distante, visibili sopra i tetti piu' bassi della via.")],
    "french_hill_sud": [(["collina"], "I moli passeggeri si vedono in lontananza, oltre la salita, le sagome dei piroscafi appena distinguibili contro il cielo.")],
}

# {chiave_edificio: [(parole, testo), ...]}
ED_EDIFICI = {
    "city_courthouse": [(["colonne"], "Granito grigio, freddo al tatto anche nelle giornate piu' calde. Non un graffio ne' una crepa, come se fossero state posate ieri."), (["corridoi"], "Marmo lucido che amplifica ogni passo. In fondo a uno di essi, una porta senza targa resta perennemente chiusa.")],
    "city_hall": [(["cupola"], "Rame ossidato in un verde uniforme, visibile da quasi ogni punto della città vecchia."), (["sportelli"], "Legno scuro consumato dai gomiti di generazioni di richiedenti, ciascuno con la propria pratica mai del tutto risolta.")],
    "fire_department": [(["autopompe"], "Rosse e perfettamente lucidate, pronte a scattare in ogni momento - eppure gli allarmi, dicono i pompieri più anziani, sono sempre meno frequenti di quanto dovrebbero."), (["palo"], "Ottone lucido, scivoloso al punto giusto. Generazioni di pompieri lo hanno reso liscio come vetro.")],
    "medical_center": [(["infermiere"], "Si muovono rapide e silenziose, con la stessa espressione professionale indipendentemente da cosa le attenda dietro la prossima porta."), (["pazienti"], "Alcuni fissano il soffitto senza battere ciglio, per intervalli di tempo che le infermiere hanno smesso di misurare.")],
    "miskatonic_university": [(["cancello"], "Ferro battuto lavorato con motivi vegetali che, osservati da vicino, non assomigliano piu' del tutto a piante."), (["biblioteca"], "Si intravede appena oltre il cortile. Alcuni scaffali dell'ala riservata non compaiono in nessun catalogo pubblico.")],
    "police_station": [(["scrivania"], "Ingombra di rapporti mai archiviati, alcuni risalenti a decenni prima, tutti timbrati allo stesso modo: 'caso chiuso senza spiegazione'."), (["tenente"], "Alza lo sguardo solo quanto basta per registrare un volto, poi torna alle sue carte con l'aria di chi ha smesso di aspettarsi sorprese.")],
    "post_office": [(["caselle"], "Ottone lucidato, ciascuna con una targhetta di ottone consumata. Alcune non vengono aperte da anni, eppure la posta continua ad accumularvisi."), (["orologio"], "Il pendolo scandisce il tempo con una precisione quasi innaturale, mai un secondo avanti o indietro rispetto ai timbri postali.")],
    "bridal_boutique": [(["manichini"], "Senza volto, disposti come in una processione silenziosa. Qualcuno giurerebbe che cambino leggermente posizione tra una visita e l'altra.")],
    "giovanni_clothing": [(["cappelli"], "A bombetta, allineati su mensole di legno scuro, ciascuno esattamente identico al successivo."), (["metro"], "Da sarto, consumato dall'uso. Giovanni lo usa con una precisione che sembra misurare più del semplice girovita.")],
    "hans_yodin": [(["banco"], "Curvo e consumato dal peso di decenni di scarpe riparate, ciascuna raccontando a Hans una storia diversa."), (["scarpe"], "Impilate in attesa di riparazione. Hans giura di poter leggere il carattere di un uomo dalla suola consumata delle sue scarpe.")],
    "miss_ann": [(["seta", "merletto"], "Impilati fino al soffitto, in rotoli di colori che sembrano cambiare leggermente sotto luci diverse."), (["commesse"], "Sussurrano tra loro ogni volta che una cliente distoglie lo sguardo, per poi tornare immediatamente sorridenti.")],
    "carrington_milliner": [(["cappelli"], "Di ogni foggia immaginabile, posati su teste di legno allineate come un pubblico silenzioso e composto."), (["teste"], "Di legno, levigate al punto da sembrare quasi vive sotto la luce giusta.")],
    "watkins_formal": [(["smoking"], "Neri, impeccabili, esposti con una cura maniacale su manichini rigidi."), (["papillon"], "Bianchi, perfettamente annodati, in file ordinate come soldatini in parata.")],
    "fish_market": [(["banchi"], "Di ghiaccio, che non si scioglie mai del tutto nemmeno nelle giornate piu' calde dell'estate."), (["squame"], "Alcuni esemplari, pescati piu' al largo del solito, le hanno di una lucentezza che i pescivendoli preferiscono non commentare ad alta voce.")],
    "barlows_butcher": [(["carcasse"], "Appese a ganci di ferro, ondeggiano appena a ogni apertura di porta, come mosse da un'aria che non viene da fuori."), (["coltelli"], "Affilati con un ritmo costante che mette involontariamente a disagio chiunque si soffermi ad ascoltarlo troppo a lungo.")],
    "black_dahlia": [(["tromba"], "Le sue note si sentono fin sulla via, in una melodia che non sembra mai ripetersi esattamente allo stesso modo."), (["contrabbando"], "Si dice che qui si possa comprare molto piu' del solo alcol proibito, per chi sa esattamente chi chiedere e come.")],
    "blue_ballroom": [(["lampadario"], "Cristallo che proietta riflessi azzurrastri sulla pista sottostante, mai illuminato dalla stessa angolazione due sere di fila."), (["orchestra"], "Suona fino all'alba, senza mai sembrare stanca, per un pubblico che ha sempre di che pagare l'ingresso.")],
    "cat_and_fiddle": [(["marinai"], "Raccontano storie di mare che gli avventori abituali fingono, con convinzione decrescente ogni sera, di non credere."), (["birra"], "Scura, versata senza mai riempire davvero il boccale fino all'orlo.")],
    "dovers_groceries": [(["barattoli"], "Di conserve, impilati con un ordine quasi militare che non lascia mai un solo centimetro fuori posto."), (["proprietario"], "Conosce per nome ogni famiglia della via - e, si dice, anche ogni loro segreto e ogni loro debito non saldato.")],
    "leatherworks": [(["valigie"], "Di ogni dimensione, appese insieme a cinture e finimenti da cavallo lungo pareti che non lasciano un centimetro libero."), (["odore"], "Di cuoio conciato, cosi' intenso da far lacrimare gli occhi ai clienti meno abituati fin dalla soglia.")],
    "medical_supplies": [(["strumenti"], "Chirurgici, lucidati fino a riflettere la luce delle vetrine come specchi. Alcuni, in fondo alla vetrina, non sembrano avere un uso medico convenzionale."), (["boccette"], "Etichettate a mano, con una grafia che cambia leggermente da una boccetta all'altra, come scritte in momenti diversi da persone diverse.")],
    "burns_agricultural": [(["sacchi"], "Di sementi, impilati fino al soffitto in un ordine che lascia appena spazio per muoversi."), (["campi"], "Il proprietario ne parla volentieri, tranne che di certi appezzamenti ai margini della città che nessuno vuole piu' coltivare.")],
    "carlas_collectibles": [(["francobolli", "monete"], "Riempiono vetrinette polverose, ciascuno etichettato con una data e una provenienza su cui Carla preferisce non dilungarsi troppo."), (["vetrinette"], "Il vetro e' opaco in alcuni punti, come appannato dall'interno piu' che dall'esterno.")],
    "browning_gunsmith": [(["fucili"], "Da caccia, esposti con la cura riservata di solito alle opere d'arte, ciascuno lucidato fino a scintillare."), (["munizioni"], "D'argento, le cui vendite sono aumentate ultimamente in un modo che Browning stesso trova, a suo dire, curioso.")],
    "clarke_furniture": [(["credenze"], "Intagliate a mano, con motivi che si ripetono in modo quasi ipnotico se osservati troppo a lungo."), (["odore"], "Di vernice fresca, che copre solo in parte quello, piu' antico, del legno riciclato da altre case della città.")],
    "eddies_bikes": [(["ruote", "pareti"], "Lucide, appese al soffitto e allineate contro le pareti in un ordine perfetto che Eddie difende con orgoglio."), (["melodia"], "Eddie la fischietta sempre uguale, lavorando, senza mai sembrare accorgersi di ripeterla.")],
    "garricks_knickknacks": [(["soprammobili"], "Un assortimento caotico che riempie ogni ripiano, senza un ordine apparente ne' un catalogo che ne tenga traccia."), (["chincaglie"], "Bottoni, spille, piccoli oggetti di cui nessuno ricorda piu' l'uso originale.")],
    "jamisons_hunting": [(["trappole"], "Alcune esposte in vetrina sembrano pensate per qualcosa di ben piu' grande della normale selvaggina locale."), (["cartucce"], "Ordinate per calibro su scaffali etichettati a mano, alcuni dei quali non corrispondono a nessuna arma comunemente in vendita.")],
    "janson_hardware": [(["chiodi"], "Ordinati per dimensione in cassetti etichettati a mano, senza un solo chiodo fuori dal proprio scomparto."), (["cassetti"], "Il proprietario sa sempre esattamente in quale si trova ciò che serve, spesso prima ancora che venga chiesto.")],
    "wingham_shipwright": [(["modellini"], "Di navi, costruiti con un dettaglio ossessivo - alcuni raffigurano imbarcazioni che nessun cantiere ha mai varato ufficialmente."), (["catrame"], "Il suo odore, mescolato a quello del legno di quercia stagionato, impregna ogni angolo della bottega.")],
    "heaples_toys": [(["trenini"], "A molla, disposti su binari in miniatura che percorrono l'intera vetrina in un circuito perfetto."), (["bambole"], "Di porcellana, esposte in un angolo poco illuminato. I loro occhi sembrano seguire i visitatori da qualunque punto della stanza.")],
    "margarets_curio": [(["maschere"], "Tribali, appese alle pareti con lo sguardo vuoto rivolto verso il centro della stanza."), (["libri"], "Rilegati in modo insolito - alcuni con una copertina che non sembra ne' pelle ne' stoffa. Margaret non li vende mai a chi fa troppe domande.")],
    "marvins_tattoo": [(["disegni"], "Ancore, sirene e simboli meno convenzionali tappezzano ogni parete dello studio."), (["segno"], "I clienti abituali di Marvin portano tutti, da qualche parte sulla pelle, lo stesso strano simbolo.")],
    "mchughs_antiques": [(["specchi"], "Anneriti dal tempo, che restituiscono un riflesso leggermente piu' scuro di quanto la stanza dovrebbe permettere."), (["mobili"], "D'epoca, alcuni dei quali sono tornati indietro piu' volte da clienti che non sapevano spiegarne il motivo.")],
    "mcnally_motors": [(["automobili"], "Lucide, il metallo cromato che riflette la luce del lampione fuori dalla vetrina in modo quasi accecante."), (["cromato"], "Il metallo e' talmente lucidato da restituire un riflesso distorto di chi vi si specchia.")],
    "peabody_pets": [(["gabbie"], "Di uccelli canori, il cui cinguettio riempie ogni angolo del negozio a qualunque ora."), (["etichetta"], "Su una gabbia vuota, in fondo alla sala, reca ancora un nome che nessuno dei commessi vuole leggere ad alta voce.")],
    "prentices_books": [(["scaffali"], "Alti fino al soffitto, custodiscono romanzi e manuali in un ordine alfabetico rigoroso."), (["volume"], "Piu' antico degli altri, tenuto sotto chiave dietro il bancone, disponibile solo a clienti di comprovata fiducia.")],
    "prescotts_gems": [(["pietre"], "Preziose, scintillano sotto teche di vetro illuminate da lampade orientate con precisione chirurgica."), (["lente"], "Prescott la usa per valutare ogni pietra con uno sguardo che sembra vedere oltre la semplice purezza del taglio.")],
    "princes_jewelry": [(["anelli", "collane"], "Disposti su velluto scuro, illuminati da lampade che ne esaltano ogni sfaccettatura senza lasciare ombre.")],
    "salters_antiques": [(["orologi"], "Da parete, fermi ciascuno a un orario diverso. Nessuno dei due proprietari ha mai spiegato perche' nessuno venga rimesso in moto.")],
    "strausbergs_tobacco": [(["miscele"], "Importate da porti che pochi clienti di Strausberg saprebbero indicare su una mappa, anche volendo."), (["aroma"], "Dolciastro, impregna l'aria del negozio ben oltre la soglia d'ingresso.")],
    "zimmerman_luggage": [(["bauli"], "Da viaggio, impilati fino al soffitto, alcuni con serrature abbastanza robuste da far dubitare del loro reale contenuto."), (["valigie"], "Di cuoio, pronte per chiunque debba lasciare Arkham in fretta - o per chi debba nasconderci qualcosa dentro.")],
    "asbury_methodist": [(["panche"], "Legno scuro, allineate ordinatamente sotto vetrate semplici prive di decorazioni superflue."), (["vetrate"], "Semplici, prive di decorazioni superflue, lasciano filtrare una luce grigia e uniforme su tutta la navata.")],
    "convent_st_teresa": [(["mura"], "Pietra spessa, che smorza ogni suono dall'esterno in un silenzio quasi assoluto."), (["suore"], "Camminano a passo lento nei corridoi, pregando per l'anima di una città che forse non merita più preghiere.")],
    "first_baptist": [(["campanile"], "Bianco e semplice, svetta sopra il tetto a capanna senza un solo ornamento superfluo."), (["coro"], "Prova gli inni della domenica con un fervore che rasenta, ad ascoltarlo da vicino, la disperazione.")],
    "miskatonic_synagogue": [(["stella"], "Di David, scolpita nel legno del portale con una precisione che tradisce ore di lavoro artigianale."), (["testi"], "Antichi, custoditi con una cura che va ben oltre il semplice rispetto religioso.")],
    "st_genisius": [(["guglie"], "Di pietra, si innalzano sopra vetrate policrome che filtrano la luce in disegni sempre diversi a seconda dell'ora."), (["incenso"], "Il suo odore, mescolato a quello della cera d'api, accoglie i fedeli fin dalla soglia della grande navata.")],
    "st_stanislaus": [(["candele"], "Votive, non si spengono mai del tutto, nemmeno nelle ore piu' buie della notte.")],
    "st_toads_mission": [(["nome"], "Risale, dicono i piu' anziani della città, a una storia che e' meglio non chiedere di raccontare due volte.")],
    "first_bank": [(["caveau"], "Blindato, domina l'intero piano interrato con una porta d'acciaio spessa quanto un braccio."), (["sportelli"], "Ottone lucidato, dietro cui impiegati in gilet scuro contano banconote con gesti meccanici e ripetitivi.")],
    "second_bank": [(["succursale"], "Piu' piccola della sede principale, usata soprattutto da docenti e studenti facoltosi del vicino campus.")],
    "dombrowski_boarding": [(["camere"], "Modeste ma pulite, affittate soprattutto a operai e marinai di passaggio senza troppe domande."), (["padrona"], "Di casa, non chiede mai troppo, purché l'affitto sia pagato puntualmente e in anticipo.")],
    "grand_hotel": [(["lampadari"], "Di cristallo, illuminano un atrio sfarzoso pensato per impressionare gli ospiti piu' facoltosi di passaggio."), (["personale"], "In livrea, si muove con una discrezione quasi innaturale, mai visto ne' sentito finche' non serve.")],
    "miskatonic_hotel": [(["hall"], "Profuma sempre vagamente di muffa, per quanto il personale si sforzi di mascherarlo con fiori freschi.")],
    "municipal_park": [(["vialetti"], "Ghiaiosi, serpeggiano tra aiuole curate con una precisione che tradisce una cura quasi ossessiva del giardiniere."), (["querce"], "Vecchie, le cui chiome si intrecciano sopra i vialetti in un baldacchino che pochi cittadini attraversano dopo il tramonto.")],
    "assyrian_gardens": [(["statue"], "In stile esotico, raffigurano figure che hanno ben poco a che fare con la Nuova Inghilterra circostante."), (["fontane"], "L'acqua scorre con un gorgoglio costante, stranamente limpida nonostante l'età evidente delle vasche.")],
    "olde_towne_cemetery": [(["lapidi"], "Consumate dal tempo, si inclinano tra alberi secolari in file che un tempo dovevano essere ordinate."), (["tombe"], "Le piu' antiche portano nomi che compaiono ancora, di tanto in tanto, nei registri civici della città - come se i loro proprietari non fossero mai davvero scomparsi.")],
    "community_theatre": [(["poltrone"], "Velluto rosso ormai consumato, hanno visto tempi migliori e pubblici piu' numerosi.")],
    "historical_society": [(["documenti"], "Coloniali, esposti in vetrine accanto a ritratti di antenati arkhamiti dallo sguardo severo."), (["faldoni"], "D'archivio, alcuni restano permanentemente chiusi al pubblico senza alcuna spiegazione ufficiale.")],
    "home_elderly": [(["ospiti"], "Trascorrono gli ultimi anni in un edificio tranquillo. Alcuni, dicono le infermiere, parlano nel sonno di cose che nessun manuale di medicina saprebbe spiegare.")],
    "institute_of_art": [(["dipinti"], "Paesaggi locali e ritratti riempiono corridoi luminosi, ben curati e ben illuminati."), (["sala"], "Sul retro, poco pubblicizzata, ospita opere che i curatori preferiscono non commentare con i visitatori occasionali.")],
    "museum_history": [(["teche"], "Di vetro, custodiscono reperti coloniali e strumenti marittimi d'epoca disposti con cura museale."), (["ala"], "Chiusa da anni per restauro, non ha mai riaperto - e nessuno sembra ricordare esattamente perché.")],
    "observatory": [(["cupola"], "Di rame, ospita il telescopio principale dell'università, orientabile in ogni direzione del cielo."), (["astronomi"], "Lavorano spesso fino alle ore piccole, annotando posizioni celesti con un'attenzione che rasenta l'ossessione.")],
    "arkham_observer": [(["rotative"], "Il loro rumore scuote leggermente il pavimento a ogni edizione, un tremito quasi impercettibile ma costante."), (["giornalisti"], "Hanno imparato a non indagare troppo a fondo su certe sparizioni, per il bene della propria carriera.")],
    "passenger_docks": [(["banchine"], "Legno consumato da decenni di passi e carichi, scricchiolano a ogni onda che le lambisce."), (["odore"], "Sale e catrame si mescolano a quello, piu' sottile, di pesce lasciato marcire un po' troppo a lungo.")],
    "pugilists_club": [(["ring"], "Consumato al centro della sala, le corde allentate da innumerevoli incontri combattuti fino all'ultimo round."), (["gradinate"], "Di legno, l'odore di sudore e liniment che non se ne va mai del tutto anche a sale vuota.")],
    "skeptical_minds": [(["circolo"], "Si riunisce per smascherare medium e ciarlatani. Ultimamente, ammettono i soci piu' anziani, e' sempre piu' difficile trovare qualcosa da smascherare con certezza.")],
    "town_auction_hall": [(["podio"], "Consumato dall'uso, fronteggiato da file di sedie pieghevoli mai del tutto allineate."), (["lotti"], "Quelli provenienti da proprietà rimaste a lungo disabitate attirano sempre offerenti particolarmente insistenti.")],
    "train_station": [(["tettoia"], "Ferro battuto annerito dal fumo di decenni di locomotive, copre binari che si perdono in entrambe le direzioni."), (["binari"], "Il fischio dei treni in arrivo da Boston e Providence riecheggia lungo di essi a ogni ora del giorno.")],
    "old_guild_hall": [(["edificio"], "Austero, dove un tempo si riunivano le corporazioni artigiane della città. Oggi ospita perlopiu' riunioni civiche.")],
    "christmas_grotto": [(["decorazioni"], "Scintillano tutto l'anno, indipendentemente dalla stagione, in questa bottega che non chiude mai davvero."), (["famiglia"], "Gestisce la bottega da generazioni, e sembra non invecchiare mai quanto dovrebbe secondo il calendario.")],
    "whpl_radio": [(["apparecchiature", "cavi", "quadranti"], "Elettriche, ronzano ininterrottamente in un piccolo studio gremito di cavi e quadranti.")],
}


def _imposta_eds(stanza, voci):
    for parole, testo in voci:
        aggiungi_ed(stanza, parole, testo)


def popola_eds_vie():
    n = 0
    for chiave, voci in ED_VIE.items():
        stanze = search.search_tag(f"street_{chiave}", category="arkham_street")
        if not stanze:
            continue
        _imposta_eds(stanze[0], voci)
        n += 1
    return n


def popola_eds_edifici():
    n = 0
    for chiave, voci in ED_EDIFICI.items():
        stanze = search.search_tag(f"building_{chiave}", category="arkham_building")
        if not stanze:
            continue
        _imposta_eds(stanze[0], voci)
        n += 1
    return n


def popola_tutto():
    return {"vie": popola_eds_vie(), "edifici": popola_eds_edifici()}
