# Il Personaggio

Questo capitolo copre tutto ciò che definisce un personaggio giocante in *CthulhuMud ITA Redux*: le razze giocabili, i sette attributi, le tre sottorazze permanenti (Lich, Vampiro, Licantropo), le professioni (newbie e avanzate) e il sistema di skill, esperienza e progressione, incluso il REMORT.

Come ricorda l'Introduzione, ogni regola e ogni numero riportati qui sotto sono etichettati come **confermati dalla fonte** (con il file `helps/…` o `info_…` del corpus originale citato) oppure come **scelta di design del porting** (quando la fonte non specifica un dettaglio necessario per rendere la meccanica giocabile).

## Razze giocabili

Il sito originale cataloga sei razze giocabili (`research/site_corpus/info_races.txt`). **Confermato dalla fonte**: nessuna di esse riceve bonus o malus numerici diretti agli attributi — quelli dipendono esclusivamente dalla professione di partenza scelta (vedi la sezione Professioni), non dalla razza in sé. Il registro delle razze vive in `world/races.py`.

| Razza | Nome plurale | Difficoltà consigliata | Descrizione |
|---|---|---|---|
| **Umano** (`human`) | Umani | Consigliata ai nuovi giocatori | Discendenti delle scimmie, orgogliosi di progressi tecnologici minuscoli. |
| **Profondo** (`deep_one`) | Profondi | Normale | Razza anfibia al servizio di Padre Dagon e Madre Hydra, con forti legami anche con Cthulhu. Ignota nelle acque dolci, vive in città sommerse come Y'ha-nthlei; spesso impiega gli Shoggoth come servitori. |
| **Mi-Go** (`mi_go`) | Mi-Go | Normale | "Funghi di Yuggoth", specie interstellare in cerca di minerali rari. Grandi ingegneri e chirurghi: si narra di cervelli umani spediti vivi su Yuggoth per lavorare come schiavi nelle miniere. |
| **Shoggoth** (`shuggoth`) | Shoggoth | Difficile | Esseri amorfi mutaforma creati dagli Elder Things come servitori, poi ribellatisi. Il loro corpo non offre slot per l'equipaggiamento: fanno affidamento solo sul combattimento a mani nude. |
| **Yithiano** (`yithian`) | Yithiani | Molto difficile | Membri della Grande Razza di Yith, viaggiatori nel tempo che occupano corpi ospiti altrui. Il cambio di corpo (MINDTRANSFER) è complesso e il corpo originale è fragile: sconsigliati ai principianti assoluti. |
| **Zoog** (`zoog`) | Zoog | Normale | Piccoli umanoidi blu delle Dreamlands, chiassosi e dispettosi. Si narra che i bambini cattivi morti nel sonno diventino Zoog. |

Tutti e sei i dati (nome, descrizione, difficoltà) sono **confermati dalla fonte** (`info_races.txt`): il corpus originale descrive letteralmente Umani come "razza raccomandata a chi è nuovo al gioco", i Profondi come legati a Dagon/Hydra/Cthulhu e agli Shoggoth come servitori, i Mi-Go come ingegneri interstellari che spediscono cervelli umani a Yuggoth, gli Shoggoth come ex-servitori ribelli degli Elder Things privi di slot d'equipaggiamento, gli Yithiani come viaggiatori mentali nel tempo "estremamente difficili da giocare", e gli Zoog come piccoli umanoidi dispettosi delle Dreamlands.

Ogni razza è associata a una o più professioni newbie di partenza (vedi sotto), che ne determinano il luogo di partenza effettivo in gioco.

## Attributi

I sette attributi (`world/races.py` non li tocca; sono gestiti da `typeclasses/characters.py` e usati da `typeclasses/living.py`) sono, nell'ordine usato internamente dal codice: **STR** (Forza), **INT** (Intelligenza), **WIS** (Saggezza), **DEX** (Destrezza), **CON** (Costituzione), **LUCK** (Fortuna), **CHA** (Carisma). Non esiste un settimo attributo "Fortitude": il codice usa la sigla `FOR.` come abbreviazione a schermo di **Fortuna** (luck), non di un ipotetico "Fortitude".

Il valore finale di un attributo (`Character.valore_attributo()`) è: **valore grezzo tirato in creazione** (3d6, tramite `tira_3d6()`) + **somma dei modificatori di TUTTE le professioni mai giocate** (non solo quella attiva — coerente con il modello di multi-classing cumulativo, vedi sotto) + eventuali **modificatori temporanei** da incantesimi (Forza, Indebolisci, Invecchiamento, Giovinezza, Fretta, e i buff delle sottorazze come LICH ENHANCE).

**Confermato dalla fonte** (`helps/attributes.txt`) — cosa influenza ciascun attributo:

| Attributo | Effetti confermati dalla fonte |
|---|---|
| **STR** (Forza) | Aumenta la probabilità di colpire in combattimento, il danno inflitto, la taglia massima d'arma utilizzabile e la capacità di carico. |
| **DEX** (Destrezza) | Aiuta ad attaccare più spesso, con danno potenziato, con armi migliori e a sfruttare meglio le skill di maestria d'arma; aiuta a schivare/parare; dà più movimento per livello e lo rigenera più in fretta a riposo/dormendo. |
| **INT** (Intelligenza) | Rende più efficaci l'apprendimento e la pratica delle skill; aumenta la probabilità di migliorare una skill con l'uso normale; a valori molto alti dà più esperienza per uccisione; aiuta la skill Lancio Incantesimi (Spell Casting); dà più mana per livello. |
| **WIS** (Saggezza) | Determina quante *practice* si ottengono per livello (NON i *train*, la fonte lo specifica esplicitamente); dà più mana per livello; migliora la skill Sognare (Dreaming). |
| **CON** (Costituzione) | Determina quanti HP si ottengono per livello. |
| **LUCK** (Fortuna) | Aggiunge danno extra sparando con un'arma da fuoco; una Fortuna alta dà la possibilità di identificare chi tenta di scrutarti (SCRY). Unico attributo che **non si può allenare** con TRAIN. |
| **CHA** (Carisma) | Aumenta la probabilità di ammaliare (charm) con successo NPC e altri personaggi. |

Nel codice, queste relazioni sono implementate in punti precisi: `Character.costo_train_attributo()`/`train_attributo()` (`typeclasses/characters.py`) per l'allenamento; `Character.calcola_hit_chance()`/`calcola_danno()` (`typeclasses/living.py`) per STR/DEX in combattimento (l'arma impugnata usa la skill del suo tipo, es. `sword`, non `hand_to_hand` — confermato dalla fonte); `world/esperienza.py:sale_di_livello()` per CON→HP, INT+WIS→mana, DEX→movimento, WIS→practice per livello; `world/esperienza.py:xp_da_uccisione()` per il bonus XP da INT molto alta (soglia 16, **scelta di design**: la soglia esatta e il divisore del bonus non sono specificati dalla fonte).

**Scelta di design del porting**: il tiro di base (3d6 per attributo, media 10.5) e il tetto anti-minmax `SOMMA_MASSIMA_ATTRIBUTI = 85` (la somma attesa di sette tiri 3d6 è 73.5; 85 lascia margine a un buon tiro senza permettere che tutti gli attributi siano alti insieme) non sono documentati dal sito originale, che però conferma esplicitamente il *principio* (`guides_newbieschool.txt`: "The MUD is coded to prevent any new character from having high scores in all attributes").

## Sottorazze permanenti

Oltre alle sei razze base, un personaggio può diventare — in modo **permanente e irreversibile** — un **Lich**, un **Vampiro** o un **Licantropo** (Were). Il sistema è documentato in `world/sottorazze.py` (logica) e `commands/cthulhu_sottorazze.py` (comandi), ed è confermato punto per punto dalla fonte (`helps/subraces.txt`, `helps/liches.txt`/`lich.txt`, `helps/vampires.txt`, `helps/weres.txt`/`were.txt`, `helps/lineage.txt`).

### Meccaniche comuni

**Confermato dalla fonte** (`helps/subraces.txt`):

- La trasformazione è **permanente**: "Once you decide to make your character undead [o were], there is no going back, no turning around, and absolutely no way to remove it." Un giocatore deve essere avvertito chiaramente prima di sceglierla — cosa che i comandi di gioco fanno esplicitamente.
- Si inizia sempre alla **4ª generazione**. Un membro già esistente della sottorazza può "iniziare" un nuovo membro con il proprio comando dedicato (**LICH BESTOW**, **VAMPIRE EMBRACE**, **WERE BITE**): il nuovo membro riceve `generazione = generazione del maestro + 1` e ne eredita la casa/gilda. Questi comandi **non creano** una sottorazza dal nulla: agiscono solo su chi è già di quel tipo.
- Più ci si avvicina alla 1ª generazione (più "puri"), più le abilità sono forti e più risorse (sangue/lumen/potere) si possono accumulare: "the closer to the being the purest of your subrace you get, the stronger your abilities will become and the more blood and power you can accumulate."
- **LINEAGE** mostra razza, sottorazza, generazione e ascendenza di **tutti** i personaggi attualmente connessi (non solo quelli nella tua stanza), con questa terminologia della fonte:

| Tipo | Discendente minore | Gruppo |
|---|---|---|
| Licantropo (Were) | Progenie (Progeny) | Branco (Kin) |
| Vampiro | Sangue (Blood) | Casata (House) |
| Lich | Scion | Dinastia (Dynasty) |
| Razza base | Figlio (Child) | Popolo (People) |

- **PRIVACY**: chi lo attiva scompare dall'elenco di LINEAGE altrui (`helps/lineage.txt`: "If you don't want this information displayed, use the PRIVACY command to hide it").

**Non specificato dalla fonte per Lich e Vampiro**: nessuna pagina descrive un rituale o una quest d'ingresso per diventare la *prima volta* un Lich o un Vampiro. **Scelta di design del porting**: qui è un'azione riservata allo staff, tramite il comando `SUBRACE <personaggio> <lich|vampire|were>` (permesso Builder+, `commands/cthulhu_sottorazze.py:CmdSubrace`) — i giocatori poi si espandono da soli con BESTOW/EMBRACE/BITE.

Eccezione importante per i **Were**: la fonte descrive anche una via ordinaria e giocabile, l'incantesimo **CAST WOLFBITE** (`helps/wolfbite.txt`: "The spell turns the target character into a werewolf. It requires the WAY OF NATURE skill.") — a differenza dell'incantesimo CAST LICH, che la fonte segnala esplicitamente come "currently disabled" e che quindi resta non implementato in questo porting. WOLFBITE è invece realmente costruito (`world/magic.py:_effetto_wolfbite`). SUBRACE resta comunque disponibile come scorciatoia per lo staff anche per i Were.

Il pool massimo di ciascuna sottorazza (`pool_massimo()`) è legato alla generazione: **confermato dalla fonte** che un tetto esiste ("the more blood and power you can accumulate"); la formula esatta — `max(20, 150 - generazione * 10)` — è una **scelta di design** esplicita, lineare, con un minimo per non punire troppo chi è lontano dalla 1ª generazione. Allo stesso modo, il moltiplicatore di generazione (`moltiplicatore_generazione()`, usato per scalare gli effetti dei vari comandi) è una scelta di design: 1ª generazione = x2, ogni generazione in più riduce il moltiplicatore del 10%, minimo x0.5.

### Lich

Comando: `LICH`, `LICH <sottocomando> [argomenti]`.

| Sottocomando | Sintassi | Effetto |
|---|---|---|
| `TOUCH` | `lich touch <vittima>` | Drena mana da una vittima **addormentata** (in questo porting: sonno naturale o magico) per riempire il pool di Potere. La vittima non deve essere già non-morta. |
| `DOMINATE` | `lich dominate <npc>` | Trasforma un NPC non-morto e non ostile in un seguace fedele. Probabilità di successo legata al divario di livello: più il livello della vittima supera quello del Lich, più è difficile. |
| `EMPOWER` | `lich empower <quantità>` | Potenzia tutti i propri incantesimi (percentuale di successo di lancio) per una durata proporzionale alla quantità spesa; mentre attivo, non si possono usare armi. |
| `STRIKE` | `lich strike <vittima> <quantità>` | Danno grezzo diretto alla vittima, senza resistenze applicate, proporzionale al Potere speso. |
| `ENHANCE` | `lich enhance <quantità>` | Potenzia temporaneamente Intelligenza e Saggezza. |
| `BESTOW` | `lich bestow <vittima>` | Inizia un Lich già esistente un passo più vicino a sé nella catena di generazione (vedi sopra). |

Tutte le meccaniche sopra sono **confermate dalla fonte** (`helps/liches.txt`), incluso il requisito "sleeping or STUNNED victim" per TOUCH — **scelta di design del porting**: questo porting non ha mai avuto una vera meccanica di stordimento (dichiarato altrove in `world/pk.py` per AUTOKILL), quindi qui si controlla solo il sonno, l'unico dei due stati realmente esistente. Le **formule numeriche esatte** (quanto mana si drena, la percentuale base di DOMINATE al 70% con -5% per livello di divario, i bonus di EMPOWER/ENHANCE) non sono specificate dalla fonte e sono scelte di design esplicite, documentate nei singoli comandi.

### Vampiro

Comando: `VAMPIRE`, `VAMPIRE <sottocomando> [argomenti]`.

| Sottocomando | Sintassi | Effetto |
|---|---|---|
| `SUCK` | `vampire suck <vittima>` | Drena sangue da una vittima **addormentata**, danneggiandola, e lo aggiunge al pool di Sangue. La quantità dipende dal divario di livello. |
| `FANGS` | `vampire fangs` | Mostra/nasconde le zanne (necessarie per usare BITE, vedi sotto). |
| `MESMERIZE` | `vampire mesmerize <npc> <comando>` | Controlla le azioni di un NPC con un singolo comando. **Scelta di design più prudente della fonte**: qui limitato a soli NPC e a comandi innocui (say/pose/look), mai ad altri giocatori né a comandi distruttivi — la fonte originale lo permetteva teoricamente anche tra vampiri. |
| `ENHANCE` | `vampire enhance <sangue>` | Potenzia forza e saggezza; entità legata alla generazione, durata alla quantità di sangue speso. |
| `MAJESTY` | `vampire majesty <sangue>` | Avvolge il vampiro in un'aura che alza davvero la classe armatura e spaventa via i nemici NPC più deboli presenti. |
| `MISTFORM` | `vampire mistform <sangue>` | Trasforma il vampiro in nebbia: non può compiere né subire facilmente azioni fisiche finché dura. |
| `EMBRACE` | `vampire embrace <vittima>` | Inizia un Vampiro già esistente un passo più vicino a sé nella catena di generazione. |

Inoltre, **BITE** (`bite <bersaglio>`, `commands/cthulhu_sottorazze.py:CmdBite`) è un comando di combattimento a sé stante, disponibile a chiunque abbia le zanne visibili (non solo ai Vampiri "in scena" con VAMPIRE FANGS attivo), basato sulla skill Corpo a Corpo — **confermato dalla fonte** (`helps/bite.txt`).

Tutte le meccaniche di base sono **confermate dalla fonte** (`helps/vampires.txt`). Le formule esatte (quantità di sangue drenato, entità dei bonus) sono scelte di design.

### Licantropo (Were)

Comando: `WERE`, `WERE <sottocomando> [argomenti]`.

| Sottocomando | Sintassi | Effetto |
|---|---|---|
| `CHANGE` | `were change` | Trasforma tra forma umana e forma animale. Non si può tornare umani durante la luna piena o mentre si è in rabbia (WERE RAGE attivo). |
| `RAGE` | `were rage [lumen]` | Furia frenetica: bonus a colpire e danno (HR e DR nella terminologia della fonte), utilizzabile solo in forma animale; intrappola nella forma animale finché dura. |
| `GROWL` | `were growl` | Ringhio minaccioso: gli NPC più deboli presenti possono fuggire terrorizzati. |
| `DESC` | `were desc <breve\|lunga\|descrizione> <testo>` | Personalizza le descrizioni della forma animale (si applicano dal prossimo cambio forma). |
| `BITE` | `were bite <vittima>` | Inizia un Licantropo già esistente un passo più vicino a sé nella catena di generazione. |
| `FURY` | `were fury <lumen>` | Aumenta le capacità di combattimento; entità scalata sia sul lumen speso sia sulla generazione. |
| `HEAL` | `were heal [lumen]` | Cura HP; il costo base è 1/3 del livello, ed è confermato dalla fonte che qualunque quantità oltre la base **non viene spesa**. |
| `REGEN` | `were regen <lumen>` | Applica un effetto di rigenerazione nel tempo, analogo all'incantesimo Rigenerazione. |
| `SENSE` | `were sense` | Rivela la fase lunare attuale, anche se non visibile. |

Tutte queste meccaniche sono **confermate dalla fonte** (`helps/weres.txt`). Alcuni dettagli meritano nota:

- **Trasformazione a volontà**: la fonte dice che "more experienced and powerful weres can perform this change at will", implicando che gli altri debbano aspettare la luna piena. **Scelta di design**: qui "esperienza/potenza" è tradotta nella stessa metrica di "purezza" già usata per il moltiplicatore di generazione — generazione ≤ 5 può trasformarsi liberamente, gli altri solo a luna piena.
- **Ricarica del pool lumen**: confermato dalla fonte che avviene "in your were form and in moonlight... every 10 seconds... approximately 3 lumens". **Scelta di design**: agganciata al tick di rigenerazione già esistente (variabile, 15-45 secondi) invece di un timer dedicato di 10 secondi esatti, e "moonlight" è approssimato a "di notte" per mancanza di un concetto di stanza "esterna" in questo porting.

**Fase lunare**: calcolata su un ciclo di **28 giorni di gioco** — **confermato dalla fonte** (`immhelp_conditions.txt`: "standard 28 day cycle", nello stesso paragrafo che ancora ogni altra condizione temporale al tempo di gioco, con "1 hour gametime is 30 seconds real time"). Un ciclo completo dura quindi 28×24×30 = 20.160 secondi reali (circa 5,6 ore reali) — **non** i ~29,5 giorni *reali* usati per errore in una prima implementazione, poi corretti. L'epoca di riferimento (l'istante reale in cui il calendario di gioco segna "luna nuova") non è specificata dalla fonte ed è una scelta di design arbitraria. Le otto fasi sono: nuova, crescente, primo quarto, gibbosa crescente, **piena**, gibbosa calante, ultimo quarto, calante.

## Professioni

A differenza delle razze, che non danno bonus diretti, sono le **professioni** a determinare i modificatori di attributo, il luogo di partenza e l'insieme di skill accessibili nel tempo. Il sistema distingue nettamente due categorie.

### Professioni newbie

Sono le professioni disponibili in **creazione personaggio**, senza condizioni d'accesso oltre alla razza. Il sito originale (`info_newbieprofs.txt`) dichiara "15 newbie professions", ma la sua stessa tabella ne elenca 16 — refuso della fonte, non del porting, verificato contando le righe della tabella "PROFESSION/RACE/STARTING LOCATION/PRIMARY ATTRIBUTE". Il registro (`world/professions_newbie.py`) le riproduce tutte e 16:

| Professione | Razza | Luogo di partenza | Attributo primario | Descrizione |
|---|---|---|---|---|
| Apprendista | Umano | Università Miskatonic, Arkham | DEX | Lavora e studia sotto un maestro di un mestiere; skill pratiche ed educative. |
| Cacciatore/Cacciatrice di Cervelli | Mi-Go | Nave Madre della Forza di Spedizione Mi-Go | INT | Esploratore Mi-Go che cerca cervelli umani freschi; addestrato in travestimento e chirurgia cerebrale. |
| Cadetto/Cadetta | Umano | Università Miskatonic, Arkham | CON | In addestramento militare o per le forze dell'ordine; skill fisiche ed educazione. |
| Cacciatore/Cacciatrice di Molluschi | Profondo | Nido dei Profondi, Y'ha-nthlei | STR | Profondo in addestramento come guerriero; skill fisiche. |
| Studente/Studentessa Conventuale | Umano | Università Miskatonic, Arkham | WIS | Educazione ricevuta in convento; skill oscure ed esoteriche. |
| Teppista | Umano | Università Miskatonic, Arkham | STR | Cresciuto per strada tra bande criminali; skill fisiche. |
| Iniziato/Iniziata | Umano | Tempio di Ulthar, Dreamlands | WIS | Studia le arti arcane a Ulthar; skill oscure ed esoteriche. |
| Maghetto/Maghetta | Zoog | Villaggio degli Zoog, Bosco Incantato | INT | Zoog che studia le arti arcane. |
| Scienziato/Scienziata Mi-Go | Mi-Go | Struttura di Addestramento Primario, Yuggoth | INT | Resta su Yuggoth invece di cacciare cervelli; base per diventare chirurgo cerebrale. |
| Scudiero/Scudiera | Umano | Tempio di Ulthar, Dreamlands | CON | In addestramento come guerriero a Ulthar; skill fisiche. |
| Melma | Shoggoth | Nido dei Profondi, Y'ha-nthlei | CON | Shoggoth ex-servitore degli Old Ones, indipendente; inglobano vittime per assorbirne skill. |
| Tentacolo di Dagon | Profondo | Nido dei Profondi, Y'ha-nthlei | WIS | Profondo che studia per diventare Sacerdote di Dagon. |
| Universitario/Universitaria | Umano | Università Miskatonic, Arkham | INT | Studente generalista alla Miskatonic; buon background in svariate skill. |
| Monello/Monella | Umano | Riformatorio Minorile, Dylath-Leen, Dreamlands | STR | Cresciuto per strada a Dylath-Leen tra bande criminali; skill fisiche. |
| Esploratore/Esploratrice Yithiano/a | Yithiano | Grande Biblioteca Yithiana | WIS | Aspira a scoprire i segreti dell'universo; forte background scientifico; progressione molto lunga (fino al 60° livello). |
| Zefiro | Zoog | Villaggio degli Zoog, Bosco Incantato | DEX | Impara i modi delle foreste selvagge delle Dreamlands; skill fisiche. |

Ogni voce riproduce fedelmente i dati del sito originale (razza compatibile, luogo di partenza, e l'intero albero di skill per livello di professione, dove il livello 0 indica le skill disponibili subito, a rating 0, pronte per essere allenate con PRACTICE). I **modificatori ai sette attributi** (aggiunti al tiro di base 3d6) sono anch'essi presi punto per punto dal sito originale; la loro applicazione a un tiro di base 3d6 anziché a un valore fisso è l'unica **scelta di design** non documentata dalla fonte in questa sezione.

### Professioni avanzate

Sono 39 professioni ulteriori (il comando in gioco, per storico refuso di conteggio ereditato dalla documentazione interna, le presenta talvolta come "40" nell'help testuale — il registro dati ne contiene esattamente 39), a cui **l'accesso non è libero**: richiedono di soddisfare condizioni verificate da `valuta_condizioni()` (`world/professions_avanzate.py`) — combinazioni di livello minimo, razza, cult, intervallo di allineamento, rating minimo in certe skill, e talvolta "imprese" (deed) completate. Tutti i dati (descrizione, attributo primario, modificatori di attributo, condizioni e l'intero albero skill/incantesimo per livello) sono presi punto per punto dalla fonte (`info_profs.txt`).

| Professione | Nome originale | Attributo primario | Tema |
|---|---|---|---|
| Avventuriero | Adventurer | CON | Esplorazione e segreti nascosti; abilità fisiche con un po' di istruzione. |
| Maestro d'Armi | Arms Master | STR | Combattimento armato e disarmato ai massimi livelli. |
| Artista | Artist | LUCK | Arti creative; focus educativo e occulto. |
| Druido | Druid | WIS | Poteri magici legati alla natura. |
| Avatar Malvagio | Evil Avatar | WIS | Sacerdote/sacerdotessa incarnazione mortale di una divinità oscura. |
| Spettro della Foresta | Forest Ghost | DEX | Zoog esperto di sopravvivenza nelle Dreamlands. |
| Gangster | Gangster | DEX | Autorità nel sottobosco criminale. |
| Camminatore Spettrale | Ghost Walker | INT | Zoog dedito a magia, occultismo e incantesimi. |
| Avatar Benevolo | Good Avatar | WIS | Sacerdote/sacerdotessa incarnazione mortale di una divinità benevola. |
| Apprendista Provetto | Journeyman | DEX | Esperienza moderata in un mestiere, in cerca dell'eccellenza. |
| Mago | Mage | INT | Poteri magici, occultismo e incantesimi. |
| Maestro degli Abissi | Master of the Deep | STR | Elite dei combattenti Profondi, assassini e signori della guerra. |
| Medico | Medic | INT | Arte della guarigione; abilità mediche e accademiche. |
| Mentalista | Mentalist | WIS | Magia tessuta con la sola mente; incantesimi mentali avanzati. |
| Chirurgo Mi-Go | Migo Surgeon | INT | Mi-Go esperto in materiali grezzi; medico capace e killer spietato. |
| Musicista | Musician | DEX | Esecuzione musicale e il segreto potere delle incantagioni. |
| Negromante | Necromancer | INT | Poteri per risvegliare e comandare i morti. |
| Maestro dell'Occulto | Occult Master | INT | Studi occulti avanzati; skill arcane e incantesimi. |
| Occultista | Occultist | INT | Poteri magici risvegliati; conoscenza magica e arcana. |
| Ufficiale | Officer | STR | Comando di un'unità militare; forma fisica e leadership. |
| Paladino | Paladin | WIS | Combattimento al servizio del bene; retto e legale. |
| Poliziotto | Policeman | CON | Applicazione della legge; focus fisico con abilità educative. |
| Laureato Specializzando | Postgraduate | INT | Prosegue gli studi universitari dopo la laurea; focus accademico. |
| Sacerdote di Bast | Priest of Bast | WIS | Servizio alla Dea Bast; conoscenza religiosa e incantesimi. |
| Sacerdote di Dagon | Priest of Dagon | WIS | Servizio al Dio Dagon; conoscenza religiosa e incantesimi. |
| Sacerdote di Foxbird | Priest of Foxbird | INT | Servizio a Foxbird, Dio della Magia; conoscenza magica e incantesimi. |
| Sacerdote di Marduk | Priest of Marduk | WIS | Servizio al Dio Marduk; conoscenza religiosa e incantesimi. |
| Sacerdote di Shub-Niggurath | Priest of Shub-Niggurath | WIS | Servizio al Dio Shub-Niggurath; conoscenza religiosa e incantesimi. |
| Sacerdote di Thanatos | Priest of Thanatos | WIS | Servizio a Thanatos e al ciclo naturale della vita; equilibrio mondano/mistico. |
| Sacerdote di Yog-Sothoth | Priest of Yog-Sothoth | WIS | Servizio al Dio Yog-Sothoth; conoscenza religiosa e incantesimi. |
| Investigatore Privato | Private Investigator | CON | Investigatore in stile Raymond Chandler. |
| Professore | Professor | INT | Facoltà della Miskatonic University; selezione severissima. |
| Ranger | Ranger | DEX | Combattimento nelle foreste selvagge delle Dreamlands. |
| Esploratore | Scout | DEX | Tracciamento, esplorazione, combattimento e criminalità. |
| Soldato | Soldier | STR | Arte della battaglia, armata e disarmata. |
| Evocatore di Spiriti | Spirit Summoner | WIS | Zoog maestro di magia arcana avanzata. |
| Cacciatore di Calamari | Squid Hunter | STR | Guerriero Profondo altamente addestrato in battaglia. |
| Ladro | Thief | DEX | Abilità di furto raffinate; focus fisico con un po' di istruzione. |
| Guerriero | Warrior | STR | Arte della battaglia, armata e disarmata, con forte focus fisico e di combattimento. |

Alcune condizioni di accesso citano "imprese" (deed) — es. Deed 59, "Il Risveglio" — che sono tutte tracciabili in gioco tramite il sistema di quest (`world/quest.py`, `world/imprese.py`): nessuna delle 39 professioni avanzate resta irraggiungibile per mancanza del sistema di imprese.

### I comandi PROF

Confermato dalla fonte (`helps/prof.txt`):

- **`PROF LIST`**: elenca tutte le professioni; quelle compatibili con la propria razza appaiono in un colore diverso da quelle non compatibili.
- **`PROF LIST <professione>`**: dettaglio di una professione — descrizione, condizioni (colorate in base a se sono soddisfatte), e l'albero di skill per livello (il numero accanto a ogni skill è il livello di professione al quale diventa disponibile per PRACTICE).
- **`PROF CHANGE <professione>`**: cambia la professione attiva. Confermato dalla fonte: costa **3 practice** ed è disponibile "at any time or any place", a patto di aver già raggiunto "a minimum number of levels" nella professione attuale — la fonte non specifica quel numero minimo, qui fissato a **1 livello** (`LIVELLO_MINIMO_CAMBIO_PROFESSIONE`), scelta di design esplicita (impedisce solo di cambiare professione a livello 0 appena creato).
- **`PROF ADVANCED [professione]`**: comando aggiuntivo di questo porting per navigare specificamente le professioni avanzate (la fonte le presenta in un'unica lista con PROF LIST; qui sono separate per praticità di consultazione, ma PROF CHANGE funziona in entrambi i casi).
- **`SKILL PROFS <skill>`**: elenca quali professioni offrono una data skill e a quale livello (implementato come `SKILL PROFS`, confermato dalla fonte).

**PROF CHANGE**, cambiando professione, applica una regola di continuità **confermata dalla fonte**: le skill già portate sopra rating 0 restano per sempre; solo le skill ancora a rating 0 concesse esclusivamente dalla professione che si lascia spariscono dalla lista disponibile. I livelli di professione sono **cumulativi**: tornare a una professione già giocata in passato ne riprende il livello da dove era rimasto (vedi "multi-classing" più sotto).

## Skill e progressione

### I cinque comandi di crescita

| Comando | Uso | Costo | Effetto |
|---|---|---|---|
| **TRAIN** | `train`, `train <attributo>`, `train hp\|mana\|movimento\|practice\|sanity` | *Train* (guadagnati salendo di livello) | Aumenta un attributo di 1 punto (il costo sale di 1 train ogni volta che si allena lo stesso attributo: 1ª volta 1 train, 2ª volta 2, ecc. — confermato dalla fonte, `helps/train.txt`), oppure aumenta HP/mana/movimento/practice/sanity massimi. **Fortuna non è allenabile** (confermato dalla fonte: "Luck cannot even be trained"). |
| **PRACTICE** | `practice`, `practice <skill>` | 1 *practice* | Migliora da soli una skill già posseduta (anche a rating 0), senza insegnante. Guadagno casuale (in questo porting 1-5 punti), fino a un tetto di **75%** (`CAP_PRACTICE`) oltre il quale serve un insegnante. |
| **LEARN** | `learn <insegnante> [skill]` | 1 *practice* | Impara o migliora una skill da un NPC insegnante presente nella stanza (o da un altro giocatore con la skill Insegnare/TEACH, secondo la fonte). Senza argomento skill, elenca cosa l'insegnante può insegnare. Può introdurre skill mai possedute prima. Tetto in questo porting: **90%** (`CAP_LEARN`); un insegnante non può comunque portare oltre il proprio stesso rating. |
| **DEBATE** | `debate <personaggio> <skill>` | Gratuito in practice, ma **drena movimento** (15 punti a round in questo porting) | Dibattito gratuito con un altro personaggio/NPC su una skill già conosciuta da entrambi; richiede di conoscere la skill Dibattito (Debating). Vince chi ha il rating di Dibattito più alto (con una componente casuale); il vincitore guadagna XP e pratica la skill, il perdente ne perde un po'. Tetto in questo porting: **50%** (`CAP_DEBATE`). |
| **RESEARCH** | `research <skill>` | Gratuito | Mostra nome, categoria, il proprio rating attuale e la descrizione di una skill — nessuna crescita, solo consultazione. |

I tre tetti numerici (75/90/50%) e i guadagni casuali per PRACTICE/LEARN non sono specificati con cifre esatte dalla fonte (che pure conferma l'esistenza di una gerarchia PRACTICE < LEARN < insegnamento tra giocatori in efficacia) e sono **scelte di design del porting**, facili da ritarare.

Anche le dotazioni iniziali di *practice* e *train* (`PRACTICES_INIZIALI = 5`, `TRAINS_INIZIALI = 5`) sono scelte di design: la fonte non specifica la dotazione di partenza.

### SCORE, EXPERIENCE e il livello

Il comando **`SCORE`** (alias `sc`) mostra la scheda completa: razza, professione attiva e livello, livello personaggio complessivo, i sette attributi, HP/mana/movimento, bonus temporanei di colpire/danno, sanity, fama, valuta locale, stato missione taglie, eventuale divinità venerata e pietà, stato di fame/sete, practice e train disponibili.

Il comando **`EXPERIENCE`** (alias `xp`) mostra livello, **livello effettivo** (di combattimento) e **livello talento** (per gli oggetti utilizzabili — vedi il capitolo sull'Equipaggiamento), percentuale di esperienza verso il prossimo livello, e la resistenza a paura/perdita di sanity per tipo. **Confermato dalla fonte** (`helps/experience.txt`) che livello, livello effettivo e livello talento sono concettualmente distinti; in questo porting, però, livello effettivo e livello talento **coincidono entrambi** con `livello_personaggio()` — una vera distinzione (es. buff/debuff temporanei sul solo "fighting level") è dichiarata come non ancora implementata.

Il **"livello personaggio"** (`livello_personaggio()`) è la **somma dei livelli accumulati in tutte le professioni mai giocate**: un vero sistema di multi-classing cumulativo. Passare da una professione all'altra con PROF CHANGE non azzera mai i progressi fatti in quella lasciata: se torni a giocarla in futuro, riprende dal livello dove l'avevi lasciata.

**Esperienza guadagnata uccidendo** (`world/esperienza.py`, `xp_da_uccisione()`) — **confermato dalla fonte** (`helps/experience.txt`):

- L'XP dipende dal **divario di livello effettivo** tra uccisore e vittima, non dai livelli assoluti: "a level-10 player killing a level-25 NPC will receive the same amount of XP as a level-150 player killing a level-165 NPC" (divario 15 in entrambi i casi).
- L'XP necessaria per il prossimo livello **cresce** con il livello (in questo porting: `XP_BASE_PER_LIVELLO * (livello + 1)`, con `XP_BASE_PER_LIVELLO = 100` — la formula esatta è una scelta di design, il principio di crescita è confermato).
- **Allineamento**: bonus di XP uccidendo il segno opposto, penalità uccidendo lo stesso segno; gli effetti sono più marcati per un personaggio "buono" che per uno "cattivo" (confermato testualmente dalla fonte).
- **RIGHTEOUSKILL** (opzione attivabile col comando omonimo): se attiva, uccidere NPC malvagi sposta l'allineamento verso il bene e viceversa; se disattiva, ogni uccisione sposta l'allineamento verso il male, e l'XP guadagnata è "leggermente inferiore" (in questo porting: -5%, `RIDUZIONE_XP_SENZA_RIGHTEOUSKILL`).
- **INT molto alta** dà un bonus fisso di XP per uccisione (soglia e divisore sono scelte di design).

**Scelta di design** rilevante segnalata nel codice: fino a una correzione recente, l'allineamento non cambiava mai dopo la creazione del personaggio, rendendo di fatto inerte il bonus/malus XP da allineamento per chi non l'avesse impostato a mano; ora ogni uccisione sposta davvero l'allineamento (`sposta_allineamento()`), coerente con `helps/righteouskill.txt`.

### Perdita di XP: morte e fuga

**Alla morte** (`world/esperienza.py:perdi_xp_morte()`), **confermato dalla fonte** (`helps/death.txt`, `helps/experience.txt`): "As a low-level character, you will not lose much experience from dying. However, after a certain point, you will lose a set amount of experience from each death, so it is possible to lose a level from dying." La soglia di livello sotto la quale non si perde nulla (10) e la quantità fissa persa (200 XP) sono **scelte di design** esplicite, non specificate dalla fonte. Se la perdita supera l'XP accumulata nel livello corrente, si retrocede di un livello. Uno Yithiano che possiede un NPC morto perde **la metà** del normale (`world/yithian.py`).

**Alla fuga** (`world/combat.py:tenta_fuga()`, comando **FLEE**), confermato dalla fonte (`helps/flee.txt`): "a small loss of experience and/or some minor damage to your equipment." In questo porting: perdita fissa di 5 XP (`XP_PERSA_PER_FUGA`, scelta di design) più eventuale degrado di un pezzo di equipaggiamento a caso — **senza mai** far perdere un livello (a differenza della morte), perché la fonte non lascia intendere che fuggire possa arrivare a tanto. FLEE ha inoltre il 25% di probabilità base di fallire, e se la direzione scelta non è percorribile ne viene selezionata una casuale tra le uscite disponibili.

### REMORT

Il **REMORT** (`world/remort.py`, comando `commands/cthulhu_remort.py:CmdRemort`) è il sistema di "reincarnazione" che permette a un personaggio che ha raggiunto un livello altissimo di ricominciare la propria carriera mantenendo parte dei progressi. È **confermato dalla fonte** (`helps/remort1.txt`, descrittivo per i giocatori; `helps/remort2.txt`, il comando immortal vero e proprio) che si tratta di un processo **mediato dallo staff**, mai self-service: come per le sottorazze e per Societies/Clan, implementarlo come comando libero per il giocatore sarebbe stato infedele alla fonte, non un gap da colmare.

**Regole confermate verbatim dalla fonte:**

- Eleggibile al **livello 201** la prima volta, poi di nuovo ogni volta che si raggiunge il **livello 300** (non cumulativo: si riparte sempre da 3, quindi la soglia resta 300 e non "201 + 300×n").
- Il personaggio torna al **livello 3**; HP, mana e movimento attuali e massimi vengono **dimezzati**.
- Si mantiene **oltre il 95%** delle skill agli stessi rating: in questo porting, il 5% di probabilità **per ogni singola skill** di perdere una piccola quantità di punti (1-10, valore casuale).
- Si mantengono **oro, equipaggiamento e appartenenza al clan**.
- Sconsigliato (non vietato) su un personaggio affamato/assetato o "switched" (per esempio uno Yithiano che sta possedendo un corpo altrui): in questo porting il secondo caso è **bloccato esplicitamente** (i livelli guadagnati andrebbero applicati al corpo sbagliato), mentre il primo resta solo un avviso testuale, come dice la fonte stessa ("should not have any negative effects").
- Al termine, l'account viene **disconnesso**: "When the player reconnects, they will once again find themselves at level 3 and the remort process will be complete."
- Il personaggio remortato mantiene l'accesso al canale Hero e **sblocca l'accesso al canale REMTALK**.

**Non specificato dalla fonte (scelte di design esplicite)**: come conciliare il "livello 3" post-remort con il modello di multi-classing di questo porting, dove il livello personaggio è la somma di tutte le professioni mai giocate. Qui il remort **azzera la cronologia di ogni professione tranne quella attiva**, portata a 3: un vero "si riparte da capo", coerente con lo spirito della fonte anche se il dettaglio tecnico è un'interpretazione necessaria. L'"immtitle" personalizzato citato dalla fonte (un titolo scelto liberamente dal giocatore remortato) **non è ancora implementato**: non esiste infrastruttura di titoli personalizzati in questo porting; il beneficio concreto già disponibile è l'accesso reale al canale REMTALK.

Il comando riservato allo staff è:

```
remort <personaggio>
```

(permesso Builder+ in questo porting; la fonte lo classifica come comando "Lesser God"). Non esiste alcun equivalente self-service: un giocatore non può mai remortare se stesso senza l'intervento di un membro dello staff.

Il sistema REMORT è approfondito ulteriormente, per gli aspetti che esulano dalla creazione/progressione del personaggio (canali, titoli, cultura di gioco attorno ai remort), in un capitolo successivo dedicato.
