# Il Mondo e i Suoi Luoghi

## Panoramica del mondo

Il mondo di gioco è ambientato negli anni '20 del XX secolo. Ad oggi le zone effettivamente costruite in gioco (stanze reali, non solo materiale di riferimento) sono le seguenti:

- **Arkham**, Massachusetts — la città universitaria del Miskatonic: una griglia di 36 vie e i suoi **73 edifici catalogati** (negozi, edifici municipali, luoghi di culto, banche, alberghi, luoghi all'aperto e altro), tutti costruiti e collegati. Fonte: `world/arkham_catalog.py`, guida ufficiale *cthulhumud.com/guides_arkham* (rilevazione settembre 2026).
- **Il Cairo** — 12 aree cittadine più i 7 negozi del Bazaar, raggiungibile da Arkham via nave dai Moli Passeggeri. Fonte: `world/rooms_cairo.py`, guida ufficiale *guides_cairo*.
- **Le Dreamlands** — la dimensione onirica, comprendente:
  - **Ulthar**, la città dei gatti (5 vie, la piazza-fontana, il tempio, la Fucina di Maro);
  - **Zoog Village**, il villaggio degli Zoog nel Bosco Incantato (19 location nominate);
  - un **connettivo regionale** di sentieri che collega le due zone e un tratto di Dylath-Leen (il crocevia, i sentieri verso Ulthar/il Bosco/il fiume Skai, e due punti di passaggio - Nir e Hatheg - nominati ma non ancora esplorabili).
- **Il relitto dello U-29** ("Nightmare Submarine"), un piccolo dungeon autoconclusivo di 23 stanze al largo della costa di Arkham.
- **L'Ufficio della Gilda dei Cacciatori di Taglie** a Dylath-Leen.

A queste si aggiungono quattro **hub di partenza** per altrettante professioni newbie che esistono finora solo come tre stanze placeholder (RECALL/RESPAWN/MORGUE), senza un'area esplorabile costruita intorno: Y'ha-nthlei (Profondi), la Nave Madre Mi-Go, la Struttura di Addestramento su Yuggoth (Mi-Go) e la Grande Biblioteca Yithiana. Sono segnalati più sotto, nella sezione "Altri luoghi", come lacuna dichiarata piuttosto che ambientazioni complete: a differenza di Arkham, Cairo, Ulthar, Zoog Village e del sommergibile, per questi quattro non esiste (ancora) alcuna guida di sito raccolta che ne descriva la geografia, quindi nessuna area è stata costruita oltre le tre stanze minime necessarie a far funzionare la creazione del personaggio.

Arkham stessa contiene anche l'hub di RECALL/RESPAWN/MORGUE della professione universitaria (Sala Comune della Miskatonic University / Infermeria del campus / Mortis & Carver): a differenza dei quattro hub sopra, qui l'area è pienamente integrata nella città vera e propria, non una stanza isolata.

## Arkham

Arkham è la zona più dettagliata del gioco: la guida ufficiale ne cataloga **73 edifici con indirizzo esatto**, tutti tradotti e costruiti (`world/arkham_catalog.py`, confermato: `assert len(ARKHAM_BUILDINGS) == 73`). La fonte specifica: *"Almost all the streets in Arkham run north/south or east/west. For the streets that run north/south, the Miskatonic River serves as the dividing point between north and south [...] For streets that run east/west, the dividing line is Garrison Street"* — la convenzione di numerazione civica della città.

### Convenzioni di traduzione (scelta di design)

- I nomi propri di via (Derby, Curwen, Hyde, Armitage, Garrison, Peabody, Federal, Fishe, Marsh, Whatley, Water, Goode, Apple, West, Jenkin, River, Main, Church, Crane, Boundary, Bad Water, Lich, Powder Mill, Parsonage, French Hill, College, Pickman, Miskatonic, Washington) restano invariati: molti sono riferimenti letterari lovecraftiani diretti (Curwen da *Il caso di Charles Dexter Ward*, Armitage e Whatley da *L'orrore di Dunwich*, Pickman da *Il modello di Pickman*).
- Il suffisso generico della via è italianizzato: Street → Via, Avenue → Viale, Road → Strada, Lane → Vicolo.
- I nomi propri di persona nelle attività commerciali (Giovanni, Hans Yodin, Margaret, Marvin, McHugh, Dombrowski...) restano invariati; solo la parte descrittiva del nome è tradotta.
- Gli orari sono conservati come stringa originale in inglese (es. "9am-9pm", "Always Open"), poi interpretati dal motore orari reale (vedi più sotto, §6).

### La griglia stradale (scelta di design)

Lo schema concordato è "una stanza per via": ogni via nominata diventa un'unica stanza percorribile. Dove il catalogo mostra edifici su entrambi i lati di un riferimento (Garrison Street per Est/Ovest, il fiume Miskatonic per Nord/Sud), la via è sdoppiata in due stanze (es. "Via Derby Est" e "Via Derby Ovest"). Il risultato, ricostruito analizzando il catalogo (`world/rooms_arkham.py`):

- **16 vie a un solo lato**: Armitage (O), Bad Water Road (S), Boundary (S), Crane (O), Curwen (O), Federal (N), Fishe (N), French Hill (S), Hyde (O), Jenkin (N), Lich (E), Main (O), Miskatonic Avenue (O), Parsonage (S), Powder Mill (S), River (O).
- **8 vie su due lati** (16 stanze): Church, College, Derby, Garrison, Peabody Avenue, Pickman, Washington, West Street.
- **4 vie di puro collegamento** senza esercizi catalogati ma necessarie a tenere la griglia percorribile: Whatley, Vicolo Goode, Vicolo Apple, Via Water.

Totale: **36 stanze-via**. Le tre vie che attraversano il fiume con un ponte — Garrison, Peabody Avenue, West Street (le uniche cui il catalogo assegna indirizzi sia a Nord che a Sud) — fanno da spina dorsale che tiene insieme Arkham Nord e Arkham Sud, coerentemente con le tre ponti visibili sulle mappe ufficiali (*arkham.gif* / *arkham-new.jpg*). La disposizione interna delle vie (quale via confina con quale) è una ricostruzione ragionevole basata sul catalogo e sull'ispezione delle mappe, non una topologia isolato-per-isolato attestata dalla fonte.

Ogni edificio è una singola stanza raggiungibile con un'uscita dedicata dalla via, con un'uscita di ritorno "fuori" (`world/rooms_arkham_edifici.py`).

### Gli edifici municipali (7)

| Nome | Indirizzo | Note |
|---|---|---|
| Tribunale Municipale | 250 Via College Ovest | Sede della giustizia cittadina. |
| Municipio | 1000 Via West Sud | L'edificio più imponente della città vecchia, con cupola di rame. |
| Caserma dei Vigili del Fuoco | 200 Via Garrison Sud | Autopompe e dormitori dei pompieri. |
| Centro Medico Regionale Miskatonic | 850 Via West Sud | L'ospedale cittadino. |
| Università Miskatonic (ingresso) | 450 Via Church Ovest | Cancello principale del campus; è anche l'hub di RECALL/RESPAWN della professione universitaria (Sala Comune / Infermeria del campus). |
| Commissariato di Polizia | 201 Viale Peabody Sud | Sede della polizia cittadina. |
| Ufficio Postale | 1012 Via Church Ovest | Caselle postali e sportelli. |

### Negozi di abbigliamento (6)

| Nome | Indirizzo | Orari |
|---|---|---|
| Boutique da Sposa di Arkham | 302 Via River Ovest | 11:00–22:00 |
| Abbigliamento da Uomo di Giovanni | 780 Via West Nord | 10:00–21:00 |
| Bottega di Hans Yodin, Mastro Calzolaio | 215 Via Fishe Nord | 9:00–22:00 |
| Moda da Donna di Miss Ann | 319 Via Church Ovest | 9:00–21:00 |
| Cappelleria di V. Carrington | 707 Via Main Ovest | 9:00–21:00 |
| Abiti Eleganti Watkins | 242 Via River Ovest | 9:00–21:00 |

### Cibo e locali (6)

| Nome | Indirizzo | Orari |
|---|---|---|
| Mercato del Pesce di Arkham | 362 Via Derby Ovest | Sempre aperto |
| Macelleria Barlow | 461 Via Church Ovest | 9:00–22:00 |
| Jazz Club Black Dahlia | 279 Via Jenkin Nord | Non specificati (locale notturno, si dice vi si trovi "molto più del solo contrabbando") |
| La Sala da Ballo Blu | 719 Via Washington Ovest | 20:00–4:00 |
| Il Pub Il Gatto e il Violino | 224 Via Derby Est | 11:00–Mezzanotte |
| Drogheria Dover | 577 Via Church Ovest | 6:00–22:00 |

### Altri negozi (23)

| Nome | Indirizzo | Orari |
|---|---|---|
| Lavorazione del Cuoio di Arkham | 486 Via College Ovest | Mezzogiorno–Mezzanotte |
| Forniture Mediche di Arkham | 494 Via Derby Est | 9:00–22:00 |
| Prodotti Agricoli Burns | 843 Via Main Ovest | 6:00–Mezzanotte |
| Da Collezione di Carla | 673 Via West Sud | 6:00–19:00 |
| Bottega di Charles Browning, Mastro Armaiolo | 650 Via Garrison Sud | 9:00–Mezzanotte |
| Mobili di Qualità Clarke e Figli | 215 Via Hyde Ovest | 8:00–22:00 |
| L'Emporio delle Biciclette di Eddie | 690 Via Peabody Sud | 8:00–19:00 |
| Ninnoli di Garrick | 245 Via Crane Ovest | Sempre aperto |
| Forniture da Caccia Jamison | 867 Via Boundary Sud | 8:00–19:00 |
| Ferramenta e Forniture Famiglia Janson | 242 Via Derby Ovest | 8:00–22:00 |
| Bottega di Harold Wingham, Mastro Carpentiere Navale | 132 Via French Hill Sud | 10:00–20:00 |
| Giocattoli e Giochi di Heaple | 485 Via Washington Ovest | 10:00–19:00 |
| Il Negozio di Curiosità di Margaret | 394 Via Curwen Ovest | 9:00–22:00 |
| Lo Studio di Tatuaggi di Marvin | 203 Via Fishe Nord | Sempre aperto |
| Antiquariato McHugh | 898 Via Church Ovest | Sempre aperto |
| Veicoli a Motore McNally | 412 Via Peabody Sud | 8:00–19:00 |
| Animali Peabody | 218 Viale Peabody Sud | Sempre aperto |
| Libri e Tomi di Prentice | 656 Via Derby Ovest | 8:00–19:00 |
| La Gioielleria di Prescott | 207 Via Washington Est | 7:00–20:00 |
| La Galleria di Gioielli di Prince | 490 Via River Ovest | 9:00–18:00 |
| Antiquariato Salter | 760 Via Derby Ovest | 8:00–22:00 |
| La Tabaccheria Pregiata di Strausberg | 295 Via Armitage Ovest | 8:00–23:00 |
| La Valigeria Zimmerman | 373 Via Armitage Ovest | 8:00–22:00 |

### Luoghi di culto (7 confessioni)

| Nome | Indirizzo |
|---|---|
| Chiesa Metodista-Episcopale Asbury | 401 Via Boundary Sud |
| Il Convento di Santa Teresa | 1472 Via West Sud |
| Prima Chiesa Battista di Arkham | 207 Via Church Est |
| Sinagoga Miskatonic | 247 Via Church Ovest |
| Basilica di San Genesio | 700 Via Parsonage Sud |
| Chiesa di San Stanislao | 600 Via Derby Est |
| Missione di San Rospo | 362 Via Federal Nord |

Nessuno dei sette ha un orario indicato dalla fonte: restano sempre visitabili.

### Banche (2)

| Nome | Indirizzo | Note |
|---|---|---|
| Prima Banca di Arkham | 425 Via College Est | Banca cittadina. |
| Seconda Banca di Arkham | 450 Via Church Ovest | Situata *dentro* il campus della Miskatonic University, usata soprattutto da docenti e studenti. |

### Alberghi (3, più 1 al Cairo)

| Nome | Indirizzo |
|---|---|
| La Pensione di Dombrowski | 667 Via Pickman Est |
| Il Grand Hotel di Arkham | 452 Via Jenkin Nord |
| Hotel Miskatonic | 742 Via Pickman Ovest |

Ognuno dei quattro alberghi del gioco (i tre di Arkham più l'Anubis Hotel del Cairo) ospita un NPC albergatore di ambientazione (senza inventario in vendita: la fonte non descrive un vero commercio in albergo) e il comando `ALLOGGIA` (`commands/cthulhu_inn.py`) permette di affittare una camera — meccanica di design costruita per dare un uso concreto agli edifici-albergo, in assenza di una descrizione meccanica dettagliata nella fonte.

### Luoghi all'aperto (3)

| Nome | Indirizzo |
|---|---|
| Parco Municipale di Arkham | 1200 Via Garrison Sud |
| I Giardini Assiri | 643 Via Powder Mill Sud |
| Il Cimitero della Città Vecchia | 431 Via Lich Est |

### Altri luoghi (16)

| Nome | Indirizzo | Note |
|---|---|---|
| Teatro Comunale di Arkham | 396 Via Garrison Nord | Rappresentazioni itineranti e recite scolastiche. |
| La Società Storica di Arkham | 759 Via Church Ovest | Documenti coloniali e ritratti. |
| Casa di Riposo di Arkham | 359 Via Derby Est | Ricovero per anziani. |
| Istituto d'Arte di Arkham | 869 Via Washington Ovest | Galleria cittadina. |
| Museo di Storia di Arkham | 550 Via College Ovest | Reperti coloniali e marittimi. |
| Osservatorio di Arkham | 268 Viale Miskatonic Ovest | Telescopio dell'università. |
| L'Osservatore di Arkham | 209 Via College Est | Il giornale cittadino. |
| Moli Passeggeri di Arkham | 800 Via French Hill Sud | Punto di imbarco per Il Cairo (uscita "nave") e per il relitto del sommergibile (uscita "largo"). |
| Il Club dei Pugili di Arkham | 723 Via West Nord | Palestra di pugilato. |
| Società delle Menti Scettiche di Arkham | 332 Via College Ovest | Circolo di razionalisti anti-occulto. |
| Sala Aste Comunale di Arkham | 193 Strada Bad Water Sud | Aste di oggetti, spesso di provenienza "insistente". |
| Stazione Ferroviaria di Arkham | 400 Via Armitage Ovest | Collegamenti verso Boston e Providence. |
| Mortis & Carver, Impresa di Pompe Funebri | 647 Via Lich Est | Riusa la stanza di MORGUE già creata per l'hub universitario: non duplicata, solo collegata alla via. |
| La Vecchia Sala delle Gilde | 339 Via Main Ovest | Un tempo sede delle corporazioni artigiane. |
| La Grotta di Natale di Pearson e Figli | 523 Via Garrison Nord | Bottega stagionale sempre allestita. |
| Radio WHPL Arkham | 722 Viale Peabody Nord | Stazione radio cittadina. |

**Totale verificato: 7 + 6 + 6 + 23 + 7 + 2 + 3 + 3 + 16 = 73/73**, tutti costruiti (`world/rooms_arkham_edifici.py:crea_tutti_edifici()`).

## Il Cairo

Il Cairo è ricostruito dalla guida testuale ufficiale (*cthulhumud.com/guides_cairo*), non da una mappa visiva (quella, *cairo.gif*, non è mai stata reperita durante la ricerca): *"Cairo is divided into 4 main areas: The Docks, The Bazaar, The Administrative Area, The Residential Area, The Slums."* A differenza di Arkham, la fonte parla di **aree**, non di singoli edifici con indirizzo: la fedeltà possibile è quindi a livello di quartiere (un'unica stanza per area), con l'eccezione del Bazaar, che la guida elenca esplicitamente con 7 esercizi nominati.

### Le aree cittadine (12)

| Area | Descrizione/funzione |
|---|---|
| **Il Bazaar del Cairo** | Il centro pulsante della città, gremito di venditori e mercanti; ospita i 7 negozi elencati sotto. |
| I Moli sul Nilo | Terminal per la pesca locale e per le navi dirette in America e Inghilterra — è il punto di collegamento con Arkham. |
| Le Porte della Città | Confine settentrionale, verso l'altopiano di Giza. |
| Le Piramidi di Giza | A nord della città, sull'altopiano di Giza (raggiungibili attraverso le Porte). |
| La Sfinge | A sud-est delle Piramidi. |
| L'Area Amministrativa | Uffici coloniali del Khedivè. |
| La Cittadella Britannica | Quartier generale delle forze del Khedivè, a est della città. |
| Quartiere Residenziale di Nord-Est | Case di mercanti e commercianti benestanti. |
| Quartiere Residenziale di Sud-Est | Quartiere simile, più tranquillo, di funzionari e piccoli proprietari. |
| Gli Slums | A sud-ovest, i quartieri più poveri; presenza di una missione copta. |
| La Strada Rialzata | Strada sopraelevata verso sud, oltre i confini della città. |
| La Grande Moschea | In fondo alla Strada Rialzata; il richiamo alla preghiera vi risuona cinque volte al giorno. |

### I 7 negozi del Bazaar

Tutti confermati nominalmente dalla guida ufficiale (*"Notable merchants include..."*); gli inventari di vendita sono farina di design del porting.

| Negozio | Cosa vende |
|---|---|
| Anubis Hotel | Alloggio (nessun mercante: stessa scelta di design degli alberghi di Arkham). |
| Mercante di Stoffe | Lino egiziano. |
| Bancarella dei Contadini | Frutta e verdura fresca (datteri, melograni, lenticchie, fichi, spezie, limoni, ceci). |
| Armeria di Abdul | Sciabole, pugnali, scudi, lance, corazze da soldato. |
| Bottega del Vinaio | Vini e birre locali. |
| Falcon Armory | Armi da fuoco europee moderne (pistole, fucili, munizioni). |
| Panetteria del Bazaar | Pane appena sfornato e dolci al miele. |

### Come si raggiunge

Il Cairo è collegato ad Arkham via nave, coerentemente con la guida ufficiale (*"vessels traveling to America and England"*): dai Moli Passeggeri di Arkham, l'uscita **"nave"** porta a "In Mare Aperto" (una stanza-transito che rappresenta settimane di navigazione), da cui si prosegue fino ai Moli sul Nilo del Cairo, e viceversa. La stanza intermedia e i due punti di aggancio esatti sono una scelta di design; il collegamento marittimo Egitto↔America in sé è confermato dalla fonte.

## Le Dreamlands

Le Dreamlands sono la dimensione onirica lovecraftiana. La fonte le descrive così (*helps/dreamlands.txt*): *"The Dreamlands are a separate reality from Earth with slightly different laws of physics and existence, rumored to have been formed from the collective unconscious dreams of humanity."*

### Come entrare: il comando DREAM

Il comando in gioco si chiama `DREAM` (alias `SOGNA`) — una deviazione minore dalla sintassi letterale della fonte (`DREAM WALK` / `DREAM AWAKEN`, citata in *helps/dreaming.txt*), mai discussa esplicitamente col committente e lasciata così per non rompere l'uso già consolidato nel porting.

La riuscita dipende dalla skill **Dreaming** (Sognare) e dall'attributo **Saggezza** — confermato dalla fonte: *"attempts to make this journey become easier as a character's rating in this skill increases [...] This skill is modified by the WISDOM attribute"* — e dalla **Sanity** del personaggio: più la mente è provata, più facilmente si scivola nel sogno, coerentemente con lo spirito cosmic horror del porting. La formula esatta (`commands/cthulhu_dream.py`) è una scelta di design:

```
probabilità = 15 + rating_dreaming × 0,4 + saggezza × 0,5 + (100 − percentuale_sanity) × 0,3
```

con un bonus di +20 se il personaggio è sotto l'effetto dell'incantesimo **Trance** (che, secondo la fonte, *"improves a character's dreaming ability"*), e un tetto tra 5% e 95%.

**Il rischio dell'incubo.** La fonte è esplicita: *"characters who attempt to travel in their dreams without developing this skill will often find themselves trapped in terrible nightmares that can be both dangerous and deadly."* Chi tenta di sognare senza alcun rating nella skill Dreaming e fallisce il tiro rischia (25% di probabilità — valore non specificato dalla fonte, scelta di design) di finire intrappolato in un incubo: perdita di Sanity (5–15 punti) e uno stato di paura temporaneo, prima di essere comunque proiettato nelle Dreamlands.

**La destinazione dipende da dove ci si addormenta.** Confermato dalla fonte: *"Dream walking from different locations will often result in traveling to different destinations."* Il porting implementa questo con una mappa (parziale, limitata alle zone già costruite) tra la zona di partenza nel mondo reale e il punto di ingresso nelle Dreamlands: chi si addormenta in una zona associata a Ulthar atterra sul sentiero verso Ulthar, chi lo fa in una zona associata a Zoog Village atterra al margine del Bosco Incantato, chi lo fa a Dylath-Leen atterra lungo il fiume Skai; chiunque altro atterra al Crocevia delle Dreamlands, lo snodo centrale.

**Fluttuazione delle skill.** La fonte aggiunge: *"a character's rating in various skills may fluctuate up or down while traveling between worlds."* Nessuna formula è data dalla fonte: il porting fa fluttuare casualmente 2 skill già possedute (rating > 0) di un valore tra −2 e +3, mai sotto zero.

### Come uscire: il comando WAKE

`WAKE` (alias `SVEGLIATI`/`SVEGLIA`) riporta il personaggio dalle Dreamlands alla propria stanza di RECALL nel mondo reale. Funziona anche su un altro personaggio addormentato nelle Dreamlands, correggendo un bug reale della prima implementazione (la logica di risveglio viveva solo dentro l'auto-risveglio). Fuori dalle Dreamlands, `WAKE` senza bersaglio equivale invece a rialzarsi in piedi (fa parte del sistema REST/SLEEP/STAND, vedi il capitolo su movimento e posizione).

**Morire nelle Dreamlands.** Il porting non introduce alcuna regola speciale: il comportamento di morte standard del gioco (il cadavere resta dove si muore, il respawn riporta sempre alla propria stanza RESPAWN nel mondo reale) produce già naturalmente l'effetto desiderato — morire in sogno lascia cadavere e oggetti nelle Dreamlands, irraggiungibili finché non ci si torna a sognare.

**L'ancoraggio.** Chi vuole tornare in un punto preciso delle Dreamlands (o del mondo reale) senza affidarsi al caso può usare gli incantesimi **Ancora Psichica** (che marca un luogo) e **Parola di Richiamo** (che vi apre un varco): i dettagli meccanici di questi incantesimi sono trattati nel capitolo dedicato alla magia.

### Ulthar, la Città dei Gatti

Confermato dalla fonte (*helps/ulthar.txt*): *"The city rests in the magical realm of the Dreamlands, standing atop a tall hill on the banks of the River Skai. It is the largest city in the Kingdom of Skai [...] its extremely large population of cats, who lie under the protection of Bast, the Patron Goddess of Ulthar."*

La pianta stradale è ricostruita dalla mappa ufficiale (*ulthar.jpg*): una città murata con cinque vie attorno a una piazza centrale con fontana, dominata da un grande tempio dal tetto rosso.

| Via/Luogo | Note |
|---|---|
| Hatheg Way | Via settentrionale; punto di collegamento col sentiero regionale verso il crocevia delle Dreamlands. |
| Barzai Street | Prende il nome dal saggio Barzai (citato in *The Other Gods* di Lovecraft), che salì troppo in alto per fare ritorno. |
| Xarnes Street | Via commerciale orientale; qui si affaccia la Fucina di Maro. |
| Atal Way | Dal nome del compagno di Barzai, l'unico tornato a raccontare cosa si trova oltre le vette proibite. |
| Calico Cross | Via meridionale, affollata di gatti maculati al crepuscolo; il tempio la domina verso nord. |
| La Piazza con la Fontana | Il mozzo centrale; coincide con la stanza di RECALL/RESPAWN dell'hub newbie (Tempio di Ulthar - La Fontana). |
| Il Grande Tempio di Ulthar | Interno del tempio, tra la piazza e la cripta sottostante. |
| La cripta | Coincide con la stanza di MORGUE dell'hub newbie (Tempio di Ulthar - Obitorio). |
| La Fucina di Maro | Bottega del fabbro Maro, con incudine per forgiare senza l'incantesimo Greater Creation — confermata dalla fonte (*guides_forging.txt*/*guides_better.txt*) come sede reale di questa meccanica, anche se non è tra le vie disegnate sulla mappa originale (aggiunta come bottega laterale su Xarnes Street). |

I nomi di Barzai e Atal non sono casuali: entrambi sono personaggi lovecraftiani legati al culto dei gatti e agli Dei della Terra proprio a Ulthar. La disposizione esatta dei collegamenti tra le vie (quale confina con quale, oltre al mozzo centrale) è una ricostruzione del porting, non attestata edificio per edificio dalla fonte.

### Il Villaggio degli Zoog

Ricostruito dalla mappa ufficiale del sito (*new_zoogville.gif*, attribuita a "Aemilia"), il villaggio è il punto di partenza delle professioni newbie legate alla razza Zoog (Mageling e Zephyr). La mappa originale è una fitta griglia con molte celle generiche senza nome; il porting mantiene fedelmente tutte le **19 location nominate** leggibili sulla mappa, collegate in una struttura più snella della griglia cella-per-cella originale (stessa semplificazione ragionata già usata per Arkham e il sommergibile):

| Location | Funzione |
|---|---|
| Il Cancello Settentrionale | Ingresso al villaggio; collegato al sentiero regionale verso il Crocevia. |
| Nello Stagno / Lo Stagno Accogliente | Aree comuni, radure e stagni. |
| L'Albero delle Anime | Luogo di offerte per i parenti scomparsi nel sogno. |
| L'Alto Tempio | Il tempio del villaggio. |
| La Camera degli Anziani | Sede delle decisioni comunitarie. |
| La Casa di Slorril / La Tana di Jhilorin / Il Tronco di Durnith / Presso Goryth | Abitazioni private di Zoog nominati (Slorril, Jhilorin, Durnith, Goryth). |
| La Bottega di Thussis, La Bottega di Klorl, La Bottega di Flaerr, Il Forno di Silaer, La Fucina di Chorl, La Caverna delle Gemme | Le 6 location commerciali, ciascuna con un mercante Zoog e inventario tematico (funghi e radici curative da Klorl, amuleti e ninnoli da Thussis, riparazioni da Flaerr, dolci onirici da Silaer, lame in miniatura da Chorl, cristalli onirici alla Caverna delle Gemme). |
| Nel Fungheto | Dimora solitaria di Hok, che "parla ai funghi". |
| Il Deposito degli Zoog | Custodito da Merith. |
| La Casa Vuota | Deliberatamente disabitata e priva di NPC — la sua stessa descrizione ("nessuno Zoog ammette volentieri di sapere dove porti") la vuole inquietante, non dimenticata; il suo cunicolo (zoogtunnel) si perde nel buio senza portare, per ora, da nessuna parte. |

"Open Glade" e "Tree Stump" sulla mappa originale corrispondono ai nomi già coniati per gli hub RESPAWN ("La Radura Aperta") e MORGUE ("Sulla Cima del Ceppo") dell'hub newbie: non duplicati, solo agganciati alla nuova struttura. "Sotto le Radici" (RECALL) non corrisponde a una cella specifica della mappa ed è stato inserito accanto alle altre tane private — scelta di design.

### Il connettivo regionale e Dylath-Leen

Il territorio che unisce le zone delle Dreamlands è ricostruito dalla mappa regionale ufficiale (*dlands1.jpg*, attribuita a "Ithaqua"), disegnata con un font runico stilizzato molto più difficile da leggere con certezza rispetto alle altre mappe. Il porting mantiene solo i nomi letti con ragionevole sicurezza:

- **Il Crocevia delle Dreamlands** — lo snodo centrale, punto di atterraggio predefinito per chi sogna senza un ingresso dedicato.
- **Il Sentiero di Ulthar** — verso le mura di Ulthar (Hatheg Way).
- **Il Margine del Bosco Incantato** — verso il Cancello Settentrionale di Zoog Village.
- **Lungo il Fiume Skai** — verso sud, in direzione di Dylath-Leen "dalle torri di basalto nero".
- **Nei Pressi di Nir** e **Nei Pressi di Hatheg** — punti di passaggio nominati (confermati dal canone di Lovecraft e dalla mappa), ma **non ancora città esplorabili**: restano segnalati come lacuna dichiarata, non costruiti.

**Dylath-Leen** ha già un hub newbie completo (Riformatorio Minorile con RECALL/RESPAWN/MORGUE) collegato alla rete stradale regionale e all'**Ufficio della Gilda dei Cacciatori di Taglie** (vedi sotto), ma il resto della città non è stato costruito: stesso approccio di rimando esplicito usato per Nir e Hatheg.

## Altri luoghi

### Il relitto dello U-29 ("Nightmare Submarine")

Un piccolo dungeon autoconclusivo ricostruito dalla mappa ufficiale (*submarine.gif*, attribuita a "Morgan"): un U-Boot della Grande Guerra affondato al largo della costa, coerente col tono anni '20 del gioco. Tutti i **23 nomi di stanza** (biblioteca, alloggio del comandante, tubi lanciasiluri di prua e poppa, torretta di comando, sale motori, infermeria...) sono presi identici dalla mappa e tradotti in italiano, così come il punto di partenza (Lato di Sinistra dello U-29), il punto di resurrezione dedicato (l'Infermeria) e il cadavere fisso nel buio (l'Angusto Tubo Lanciasiluri di Prua, l'unica stanza del gioco descritta dalla fonte come intrinsecamente buia: *"E' buio pesto qui dentro"*).

La topologia esatta dei collegamenti tra le 23 stanze è stata rivista e corretta durante un audit (13 settembre 2026) dopo un nuovo confronto attento con la mappa originale, che aveva rivelato alcuni errori reali nella prima stesura (non solo imprecisioni di dettaglio): un tubo lanciasiluri agganciato alla stanza sbagliata, un collegamento mancante tra due sale motori, il verso della dorsale centrale invertito, una diramazione fusa per errore con un'altra. Due punti di lettura restano dichiaratamente incerti (un collegamento trattato come corridoio laterale anziché cambio di ponte, e una linea tratteggiata sulla mappa il cui significato meccanico non è chiaro).

Il relitto si raggiunge dai Moli Passeggeri di Arkham tramite l'uscita **"largo"**, che porta alle Acque Scure al largo della costa e da lì, tramite le due boccaporte (poppa e prua), all'interno del relitto.

### L'Ufficio della Gilda dei Cacciatori di Taglie (Dylath-Leen)

Confermato dalla fonte (*helps/bounty.txt*): *"players can go on missions for the Dylath-Leen Bounty Hunters Guild."* L'ufficio, con il suo impiegato NPC che tiene un registro di taglie e missioni, è collegato alla stanza di RECALL del Riformatorio di Dylath-Leen, con lo stesso schema di bottega-satellite già usato per la Fucina di Maro a Ulthar.

### Hub non ancora sviluppati oltre le stanze minime

Quattro hub di partenza restano, per ora, tre semplici stanze placeholder (RECALL, RESPAWN, MORGUE) senza un'area esplorabile costruita intorno, per assenza di materiale di fonte raccolto finora sulla loro geografia:

- **Y'ha-nthlei** (Il Nido dei Profondi / Infermeria / Obitorio) — hub della professione dei Profondi.
- **La Nave Madre Mi-Go** (Corridoio / Impianto di Riciclaggio) — hub Mi-Go.
- **La Struttura di Addestramento Primario su Yuggoth** (Camera Medica) — secondo hub Mi-Go.
- **La Grande Biblioteca Yithiana** (Centro del Giardino a Cupola / Infermeria) — hub della professione Yithiana.

Sono segnalati qui, esplicitamente, come lacuna dichiarata: bastano a rendere funzionante la creazione del personaggio in quelle professioni, ma non sono ancora ambientazioni da esplorare.

## Giorno, notte e illuminazione

### L'orologio di gioco

Il gioco riusa l'orologio nativo di Evennia (`evennia.utils.gametime`), governato da `TIME_FACTOR` (`server/conf/settings.py`). Il valore scelto è:

```
TIME_FACTOR = 48.0   # 3600 secondi di gioco / 75 secondi reali
```

cioè un'ora di gioco ogni 75 secondi reali, un giorno di gioco intero ogni 30 minuti reali circa. Questo è il ritmo classico di default del motore **Merc** — confermato dalla fonte che *CthulhuMUD* è basato su Merc 2.2 (*helps/merc.txt*: *"This mud is based on Merc 2.2"*) — riprodotto in assenza di dati più specifici su un eventuale ritmo diverso scelto dal CthulhuMUD originale: una scelta di design dichiarata, non un valore confermato punto per punto dalla fonte.

Il comando `TIME` (confermato: *helps/time.txt*, *"The TIME command displays the current game time..."*) mostra l'ora di gioco corrente.

### Gli orari dei negozi

Confermato dalla fonte come meccanica reale, non semplice colore: *helps/buy.txt* / *helps/list.txt* / *helps/sell.txt* dichiarano che *"The HOURS command will show you when the shop is open"*, e che quindi comprare, vendere e consultare il listino sono soggetti all'orario di apertura.

Gli orari dei singoli negozi di Arkham (le stringhe tipo "9am-9pm", "8pm-4am", "Always Open" viste nelle tabelle sopra) sono presi dal catalogo ufficiale e agganciati alla **stanza** dell'edificio (non al mercante, per non toccare i moduli di popolamento negozi). Il comando `HOURS` interpreta questi orari e dice se il negozio è aperto in questo momento.

**Nota importante sui dati mancanti**: i negozi di Cairo e Zoog Village **non hanno mai avuto orari nella fonte raccolta finora** (la guida del Cairo è solo descrittiva, senza la tabella indirizzi/orari che ha invece quella di Arkham) — restano quindi sempre aperti. Questa è onestà sui dati mancanti dichiarata nel codice, non un'invenzione silenziosa: nessun negozio fuori da Arkham ha un orario "inventato".

### Buio e luce

Confermato dalla fonte come meccanica reale: l'incantesimo **Oscurità** (*helps/darkness.txt*) *"fills an entire room with a magical wave of darkness"*; i comandi `LIGHT`/`EXTINGUISH` (*helps/light.txt*) controllano un oggetto-luce (*"holding a light object automatically ignites it, and removing it automatically extinguishes it"*); l'incantesimo **Infravisione** (*helps/infravision.txt*) *"enables a character to see in the dark [...] provides the infrared affect, which allows you to see in pitch-black conditions"*; e la FAQ ufficiale conferma il collegamento: *"The room is dark and there's all these glowing red eyes!? [...] The room is affected by magical darkness. Get the spell infravision."*

**Nessun ciclo giorno/notte ambientale è confermato dalla fonte raccolta finora** (nessuna pagina su alba/tramonto o illuminazione diurna/notturna): il buio nel porting è quindi **solo magico** (l'incantesimo Oscurità, temporaneo) o **intrinseco a specifiche stanze** già descritte come tali nel testo originale — l'unico caso reale trovato è l'Angusto Tubo Lanciasiluri di Prua nel sommergibile ("E' buio pesto qui dentro"). Non esiste un meccanismo universale legato all'orario di gioco: è una scelta di design esplicita non inventare un ciclo solare non confermato dalla fonte.

**Chi può vedere al buio:**

- Chi ha l'effetto attivo di **Infravisione** (`vede_al_buio`).
- Chiunque si trovi in una stanza dove è attivo **Luce Continua** o **Luce del Mago** (incantesimi, rispettivamente permanente e temporaneo), o dove sia presente un oggetto-luce acceso (a terra, o portato/impugnato da qualcuno presente).
- Lo staff con `HOLYLIGHT` attivo (comando Immortal) bypassa sempre il buio.

**Cosa blocca il buio.** Semplificazione dichiarata (`world/illuminazione.py`, stesso principio già adottato per gli stati cieco/muto): il buio blocca solo la descrizione generale della stanza (LOOK/EXAMINE senza argomenti) — guardare un oggetto o un personaggio specifico per nome, se già noto, resta possibile anche al buio. Nessuna fonte specifica un elenco esaustivo di comandi bloccati dal buio, e il porting non lo estende oltre questo caso base per restare nello scope dichiarato. Il buio **non** influenza il combattimento: nessuna fonte conferma un malus a colpire per l'oscurità.
