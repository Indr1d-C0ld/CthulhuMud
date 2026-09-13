"""
Registro delle skill di CthulhuMUD ITA Redux.

Le chiavi interne restano in inglese/snake_case (stabili, tracciabili al
materiale originale); il nome mostrato al giocatore ("nome") e' in italiano.

Copre le 282 skill effettivamente usate dalle 15 professioni newbie
(world/professions_newbie.py) e dalle 39 avanzate (world/professions_avanzate.py).

Categorie usate: combattimento, arma, lingua, accademica, occulta,
furtiva, sopravvivenza, sociale, conoscenza (lore di luogo), utilita,
artigianato, musicale (Fase K, terza tornata: strumenti/performance
delle professioni avanzate - nessuna delle altre categorie calzava).

Fase K, quinta tornata: ogni skill ha ora una "descrizione" in italiano
per il comando RESEARCH (limite dichiarato fin dalla Fase G: "il nostro
registro non ha ancora descrizioni testuali"). Tradotte verbatim dalle
963 pagine helps/*.txt individuali del corpus (una scoperta della Fase
K, quarta tornata, riusata qui su scala ancora piu' ampia): 180 hanno
una propria voce "descrizione" qui; le altre 102 sono skill che sono
ANCHE incantesimi lanciabili con lo stesso ID (es. "sleep", "poison") e
non duplicano il testo - vedi descrizione_skill() sotto, che recupera
la descrizione da world.spells.SPELLS quando manca qui. Un piccolo
numero di voci (anthropology, chaos_magic, form_mastery, hieroglyphics,
identity, master_dreamer - nessuna pagina nel corpus scansionato, stesso
tipo di buco gia' incontrato per TWEAK/guides_beamage/alcuni incantesimi)
ha una descrizione dichiarata come scelta di design per analogia con
voci sorelle gia' documentate, non come fatto verificato dalla fonte.
"""

SKILLS = {
    # --- utilita' ---
    "recall": {"nome": "Richiamo", "categoria": "utilita", "descrizione": "Trasporta immediatamente il personaggio alla stanza RECALL designata della zona attuale (nelle aree per principianti di solito un luogo sicuro vicino a cibo e acqua, con rigenerazione piu' rapida). Costa meta' dei punti movimento; alcune stanze bloccano il comando. Usarlo in combattimento richiede un buon rating in questa skill e comporta comunque una piccola perdita di esperienza come penalita'."},
    "refresh": {"nome": "Ristoro", "categoria": "utilita", "descrizione": "Skill richiesta per gli incantesimi Ristoro e Passo Leggero: Ristoro recupera una quantita' minima di movimento e rimuove gli effetti dell'affaticamento (che puo' scattare se il lancio di un incantesimo viene interrotto); Passo Leggero recupera piu' movimento ma non cura l'affaticamento."},

    # --- combattimento ---
    "dodge": {"nome": "Schivata", "categoria": "combattimento", "descrizione": "Aumenta i riflessi naturali per evitare gli attacchi in combattimento, aiutata dalla Destrezza: skill automatica, nessun comando necessario."},
    "parry": {"nome": "Parata", "categoria": "combattimento", "descrizione": "Permette di parare o deviare i colpi in arrivo: come Schivata e' automatica, ma ha piu' successo, specie se ci si difende con un'arma (funziona anche a mani nude, con danno ridotto anziche' nullo). Il successo massimo si ha quando si conosce bene sia la propria arma sia quella dell'avversario."},
    "shield_block": {"nome": "Blocco con lo Scudo", "categoria": "combattimento", "descrizione": "Capacita' di parare gli attacchi con uno scudo: senza questa skill, tenere uno scudo riduce ben poco il danno subito. I mazzafrusti ignorano completamente lo scudo, le fruste possono aggirarlo, le asce possono spaccarlo in due. Skill automatica."},
    "kick": {"nome": "Calcio", "categoria": "combattimento", "descrizione": "Concede un attacco extra a calci in combattimento; un tentativo fallito puo' sbilanciare chi lo tenta. Sintassi: KICK <bersaglio>."},
    "bash": {"nome": "Spallata", "categoria": "combattimento", "descrizione": "Un attacco brutale che mira a mandare l'avversario in ginocchio: il successo dipende dal rating, dal proprio peso e dalla stazza del nemico (sconsigliato contro un Antico Dio). Sintassi: BASH <bersaglio>."},
    "disarm": {"nome": "Disarmo", "categoria": "combattimento", "descrizione": "Permette di far cadere l'arma di mano al nemico: il successo migliora se si conoscono bene sia la propria arma sia quella avversaria, ed e' influenzato da Forza e Destrezza di entrambi. Alcune armi non si possono disarmare. Sintassi: DISARM <bersaglio>."},
    "backstab": {"nome": "Pugnalata alle Spalle", "categoria": "combattimento", "descrizione": "Il metodo d'attacco preferito da ladri, assassini e furfanti: funziona con qualsiasi arma, ma e' piu' efficace con armi da punta. Il danno dipende dal livello, dalla skill dell'arma usata, dal rating in questa skill e dalla potenza del bersaglio. Sintassi: BACKSTAB <bersaglio>."},
    "crush": {"nome": "Schiacciamento", "categoria": "combattimento", "descrizione": "Sfrutta la propria stazza fisica per schiantarsi contro l'avversario: particolarmente utile per personaggi di grandi dimensioni, poiche' la stazza determina il danno da schiacciamento. Sintassi: CRUSH <bersaglio>."},
    "strangle": {"nome": "Strangolamento", "categoria": "combattimento", "descrizione": "Infligge danno stordente (perdita di movimento) invece del normale danno (perdita di punti ferita), utilizzabile sia a inizio combattimento sia durante. Sintassi: STRANGLE <bersaglio>."},
    "circle": {"nome": "Aggiramento", "categoria": "combattimento", "descrizione": "Tentativo di sgusciare temporaneamente fuori dalla vista del nemico per colpirlo da un lato scoperto: riesce solo se il bersaglio e' accecato o distratto, quindi piu' facile in gruppo. Funziona con qualsiasi arma, meglio con una da punta. Sintassi: CIRCLE <bersaglio>."},
    "trip": {"nome": "Sgambetto", "categoria": "combattimento", "descrizione": "Sbilancia l'avversario facendolo cadere a terra, aumentandone la vulnerabilita': molto difficile contro personaggi enormi, e un'alta Destrezza aiuta a evitarlo. Sintassi: TRIP <bersaglio>."},
    "dirt_kicking": {"nome": "Terra negli Occhi", "categoria": "combattimento", "descrizione": "Acceca temporaneamente il nemico tirandogli terra negli occhi: puo' sembrare vigliacco, ma da' un piccolo vantaggio finche' l'avversario non si ripulisce. La Destrezza aiuta sia a eseguirlo sia a evitarlo. Sintassi: DIRT <bersaglio>."},
    "second_attack": {"nome": "Secondo Attacco", "categoria": "combattimento", "descrizione": "Permette di sferrare un attacco aggiuntivo per round di combattimento; agisce automaticamente con un rating sufficiente, aiutata dalla Destrezza."},
    "third_attack": {"nome": "Terzo Attacco", "categoria": "combattimento", "descrizione": "Come Secondo Attacco, un ulteriore attacco per round di combattimento; automatico, aiutato dalla Destrezza."},
    "fourth_attack": {"nome": "Quarto Attacco", "categoria": "combattimento", "descrizione": "Come Secondo/Terzo Attacco, un quarto attacco per round di combattimento; automatico, aiutato dalla Destrezza."},
    "enhanced_damage": {"nome": "Danno Potenziato", "categoria": "combattimento", "descrizione": "Moltiplica per 2 il danno inflitto (la piu' debole della serie, con Danno Estremo x3 e Danno Letale x4): agisce automaticamente, con probabilita' crescente all'aumentare del rating."},
    "ultra_damage": {"nome": "Danno Estremo", "categoria": "combattimento", "descrizione": "Moltiplica per 3 il danno inflitto (tra Danno Potenziato x2 e Danno Letale x4): agisce automaticamente, con probabilita' crescente all'aumentare del rating."},
    "lethal_damage": {"nome": "Danno Letale", "categoria": "combattimento", "descrizione": "Moltiplica per 4 il danno inflitto (la piu' potente della serie, dopo Danno Potenziato x2 e Danno Estremo x3): agisce automaticamente, con probabilita' crescente all'aumentare del rating."},
    "berserk": {"nome": "Furia Berserk", "categoria": "combattimento", "descrizione": "Manda il guerriero in una furia insana: effetti simili all'incantesimo Frenesia, con un grande incremento delle capacita' di combattimento e resistenza alla magia, ma anche incapacita' di ritirarsi anche in fin di vita. Consuma meta' del movimento e non si puo' disattivare volontariamente: svanisce col tempo o con la morte. Sintassi: BERSERK."},
    "martial_arts": {"nome": "Arti Marziali", "categoria": "combattimento", "descrizione": "La maestria avanzata del Corpo a Corpo (l'equivalente disarmato delle maestrie con le armi): aumenta i tiri offensivi e difensivi quando si combatte a mani nude, aiutata dalla Destrezza. Sblocca a sua volta Cintura Nera."},
    "black_belt": {"nome": "Cintura Nera", "categoria": "combattimento", "descrizione": "La versione ancora piu' avanzata di Arti Marziali: permette di combattere secondo diversi stili avanzati (vedi il sistema STYLE)."},
    "form_mastery": {"nome": "Maestria della Forma", "categoria": "combattimento", "descrizione": "Una maestria di combattimento aggiuntiva legata alle forme/stili avanzati (pagina originale assente dal corpus scansionato: descrizione scelta per analogia con Arti Marziali/Cintura Nera, con cui condivide la tabella della professione in cui compare)."},
    "strong_grip": {"nome": "Presa Salda", "categoria": "combattimento", "descrizione": "Aumenta le probabilita' di resistere a un tentativo di disarmo: agisce automaticamente."},
    "brawling": {"nome": "Rissa", "categoria": "combattimento", "descrizione": "Una forma specializzata di combattimento disarmato che infligge danno stordente invece del normale danno letale: agisce automaticamente."},
    "hand_to_hand": {"nome": "Corpo a Corpo", "categoria": "combattimento", "descrizione": "La conoscenza base del combattimento disarmato: la skill di combattimento fondamentale del gioco, preziosa quando ci si ritrova senza equipaggiamento. La sua maestria avanzata e' Arti Marziali."},
    "rescue": {"nome": "Soccorso", "categoria": "combattimento", "descrizione": "Permette di intervenire in un combattimento in corso per difendere un alleato dai suoi nemici: il successo dipende dal rating, dalla differenza di livello, Destrezza e velocita' tra i due personaggi. Va usato sul personaggio da salvare, non sul mostro - rubare uccisioni ad altri giocatori e' vietato e punito severamente. Sintassi: RESCUE <personaggio>."},

    # --- armi e armature ---
    "dagger": {"nome": "Pugnale", "categoria": "arma", "descrizione": "Uso di armi da taglio piccole, da coltelli a stiletti."},
    "mace": {"nome": "Mazza", "categoria": "arma", "descrizione": "Uso di armi contundenti, come clave e martelli."},
    "sword": {"nome": "Spada", "categoria": "arma", "descrizione": "Uso di armi da taglio lunghe: rapiere, spadoni, claymore."},
    "spear": {"nome": "Lancia", "categoria": "arma", "descrizione": "Uso di armi in asta a punta, come le lance."},
    "handgun": {"nome": "Pistola", "categoria": "arma", "descrizione": "Uso di armi da fuoco piccole, come pistole e revolver."},
    "gun": {"nome": "Arma da Fuoco", "categoria": "arma", "descrizione": "Uso di fucili, fucili a pompa e altre armi da fuoco lunghe."},
    "armor": {"nome": "Uso dell'Armatura", "categoria": "arma", "descrizione": "Capacita' di indossare un'armatura pesante senza esserne rallentati o penalizzati in combattimento: la skill base per l'equipaggiamento difensivo, distinta dalle maestrie specifiche con le singole armi (nella fonte il nome 'Armor' e' condiviso anche da un incantesimo di rinforzo dell'armatura, CAST ARMOR - costruito in Fase K, decima tornata come 'Incantesimo d'Armatura' per evitare ambiguita' col nome di questa skill - qui si descrive solo la skill di proficiency)."},
    "whip": {"nome": "Frusta", "categoria": "arma", "descrizione": "Uso di armi lunghe e flessibili, come catene e fruste."},
    "flail": {"nome": "Mazzafrusto", "categoria": "arma", "descrizione": "Uso di armi a palla e catena, come i flagelli da guerra."},
    "axe": {"nome": "Ascia", "categoria": "arma", "descrizione": "Uso di armi da taglio a manico, dalle piccole asce alle grandi asce bipenni (non comprende le alabarde)."},
    "polearm": {"nome": "Arma in Asta", "categoria": "arma", "descrizione": "Uso di armi in asta con lama, come le alabarde."},
    "bow": {"nome": "Arco", "categoria": "arma", "descrizione": "Uso di armi a proiettile con corda, dagli archi lunghi alle balestre."},
    "dagger_master": {"nome": "Maestria col Pugnale", "categoria": "arma", "descrizione": "Maestria avanzata dell'arma Pugnale: aumenta i tiri offensivi e difensivi quando lo si impugna, aiutata dalla Destrezza. Una delle maestrie-arma del gioco (vedi anche Maestria con la Spada/Ascia/Mazza/Lancia/Frusta/Flagello/Arma in Asta, Maestro Arciere per gli archi, Tiratore Scelto per le armi da fuoco)."},

    # --- artigianato (Fase G, terza tornata: FORGE/FIX/REFIT) ---
    "forging": {"nome": "Forgiatura", "categoria": "artigianato", "descrizione": "Permette di creare armi e armature da materiali grezzi (comando FORGE, richiede un'incudine o una forgia, costa 200 movimento) e di ripararle gratuitamente (FIX, 80 movimento, ogni tentativo rischia di danneggiare o distruggere l'oggetto) o ridimensionarle per un personaggio piu' piccolo o grande (REFIT, 100 movimento). Governa anche GUNSMITH, la creazione di armi da fuoco e munizioni (richiede anche Esplosivi e Chimica, oltre alla polvere da sparo come materiale)."},
    "gunsmith": {"nome": "Armaiolo", "categoria": "artigianato", "descrizione": "La parte della Forgiatura dedicata alla creazione di armi da fuoco e munizioni col comando GUNSMITH: per le munizioni servono anche le skill Esplosivi e Chimica, oltre alla polvere da sparo come materia prima."},
    "explosives": {"nome": "Esplosivi", "categoria": "artigianato", "descrizione": "Conoscenza delle sostanze chimiche instabili e delle tecniche necessarie a produrre un'esplosione controllata: serve per costruire bombe, e insieme a Chimica e Forgiatura per fabbricare munizioni."},
    # "chemistry" e "lore" sono gia' registrate piu' sotto (accademiche/occulta)

    # --- lingue ---
    "english": {"nome": "Inglese", "categoria": "lingua", "descrizione": "Conoscenza della lingua inglese, lingua germanica occidentale: in CthulhuMUD e' la lingua nativa di tutti i personaggi umani, indipendentemente da dove abbiano iniziato."},
    "old_english": {"nome": "Inglese Antico", "categoria": "lingua", "descrizione": "Conoscenza dell'inglese antico (anglosassone), la forma della lingua inglese usata dalla meta' del V secolo fino all'inizio del XII."},
    "german": {"nome": "Tedesco", "categoria": "lingua", "descrizione": "Conoscenza della lingua tedesca, comprese le varianti del tedesco standard parlate in Germania, Austria e Svizzera."},
    "french": {"nome": "Francese", "categoria": "lingua", "descrizione": "Conoscenza della lingua francese, lingua romanza nativa della Francia, parlata anche in parti di Svizzera, Belgio e altri territori un tempo sotto influenza francese."},
    "latin": {"nome": "Latino", "categoria": "lingua", "descrizione": "Conoscenza della lingua latina, lingua degli antichi Romani: oggi considerata una lingua morta, fu la lingua piu' importante dell'Europa occidentale fino alla fine del XVII secolo ed e' alla base delle lingue romanze come francese, italiano, spagnolo e portoghese."},
    "greek": {"nome": "Greco", "categoria": "lingua", "descrizione": "Conoscenza della lingua greca, ramo ellenico delle lingue indoeuropee nativo della Grecia, un tempo diffusa in tutto il mondo antico."},
    "spanish": {"nome": "Spagnolo", "categoria": "lingua", "descrizione": "Conoscenza della lingua spagnola, lingua romanza nativa della Spagna, parlata in varie forme anche in gran parte dell'America centrale e meridionale."},
    "italian": {"nome": "Italiano", "categoria": "lingua", "descrizione": "Conoscenza della lingua italiana, lingua romanza nativa dell'Italia e una delle lingue ufficiali della Svizzera."},
    "chinese": {"nome": "Cinese", "categoria": "lingua", "descrizione": "Conoscenza della lingua cinese (ramo sinitico della famiglia sino-tibetana, con numerose varianti come mandarino, cantonese, taiwanese e fujianese): in CthulhuMUD e' anche la lingua nativa della razza dei Mi-Go."},
    "japanese": {"nome": "Giapponese", "categoria": "lingua", "descrizione": "Conoscenza della lingua giapponese, scritta sia in kana sia in caratteri cinesi, forse imparentata con la famiglia altaica."},
    "arabic": {"nome": "Arabo", "categoria": "lingua", "descrizione": "Conoscenza della lingua araba, lingua semitica con numerose varianti, principale lingua della penisola arabica, del Medio Oriente e di parte del Nordafrica."},
    "hebrew": {"nome": "Ebraico", "categoria": "lingua", "descrizione": "Conoscenza della lingua semitica della religione giudaica e dei suoi fedeli."},
    "gaelic": {"nome": "Gaelico", "categoria": "lingua", "descrizione": "Conoscenza della lingua gaelica, ramo celtico piu' diffuso negli altopiani scozzesi."},
    "polish": {"nome": "Polacco", "categoria": "lingua", "descrizione": "Conoscenza della lingua polacca, lingua slava nativa della Polonia."},
    "romany": {"nome": "Romani", "categoria": "lingua", "descrizione": "Conoscenza della lingua romani, lingua indica nativa parlata da molte comunita' rom europee."},
    "mayan": {"nome": "Maya", "categoria": "lingua", "descrizione": "Conoscenza della famiglia di lingue Maya, parlate da alcune culture native dell'America centrale."},
    "hieroglyphics": {"nome": "Geroglifici", "categoria": "lingua", "descrizione": "Conoscenza del sistema di scrittura geroglifico dell'antico Egitto (pagina originale assente dal corpus scansionato: descrizione scelta per analogia con le altre lingue gia' documentate)."},

    # --- accademiche ---
    "education": {"nome": "Istruzione", "categoria": "accademica", "descrizione": "Conoscenza generale ed esperienza nei metodi formali di istruzione superiore. Non collegata a un comando specifico, ma richiesta da diverse professioni, imprese e altre skill."},
    "ancient_history": {"nome": "Storia Antica", "categoria": "accademica", "descrizione": "Conoscenza degli eventi e delle vicende di un remoto passato. Non collegata a un comando specifico, ma richiesta da alcune professioni, quest o imprese."},
    "ancient_geography": {"nome": "Geografia Antica", "categoria": "accademica", "descrizione": "Conoscenza della forma fisica e delle caratteristiche del mondo antico. Non collegata a un comando specifico, ma richiesta da alcune professioni, quest o imprese."},
    "modern_history": {"nome": "Storia Moderna", "categoria": "accademica", "descrizione": "Conoscenza degli eventi recenti che hanno plasmato lo stato attuale del mondo, e delle cause politiche, religiose e culturali che li hanno influenzati. Non collegata a un comando specifico, ma richiesta da varie professioni, quest e imprese."},
    "world_geography": {"nome": "Geografia Mondiale", "categoria": "accademica", "descrizione": "Conoscenza delle caratteristiche fisiche del pianeta Terra: dimensioni e posizione di nazioni, catene montuose, oceani, laghi, isole e altri elementi geografici. Non collegata a un comando specifico, ma richiesta da varie imprese o quest."},
    "world_affairs": {"nome": "Affari Mondiali", "categoria": "accademica", "descrizione": "Conoscenza degli eventi importanti in corso nel mondo, del perche' siano significativi, di cosa li abbia causati e delle loro possibili ripercussioni politiche e culturali. Non collegata a un comando specifico, ma richiesta da varie imprese o quest."},
    "physics": {"nome": "Fisica", "categoria": "accademica", "descrizione": "Conoscenza della scienza della materia, dell'energia e delle loro interazioni: dai principi fondamentali di acustica, ottica, meccanica e termodinamica fino a campi piu' avanzati come elettromagnetismo, criogenia e fisica nucleare. Non collegata a un comando specifico, ma richiesta da varie professioni e altre skill."},
    "chemistry": {"nome": "Chimica", "categoria": "accademica", "descrizione": "Conoscenza della scienza della composizione, struttura, proprieta' e reazioni della materia, in particolare a livello atomico e molecolare. Non collegata a un comando specifico, ma richiesta da alcune professioni, quest o imprese."},
    "biology": {"nome": "Biologia", "categoria": "accademica", "descrizione": "Conoscenza della scienza della vita e degli organismi viventi: struttura, funzione, crescita, origine, evoluzione e distribuzione. Non collegata a un comando specifico, ma richiesta da alcune professioni, quest o altre skill."},
    "geology": {"nome": "Geologia", "categoria": "accademica", "descrizione": "Conoscenza dello studio scientifico dell'origine, della storia e della struttura della materia solida di un corpo celeste. Non collegata a un comando specifico, ma richiesta da alcune professioni o imprese."},
    "anthropology": {"nome": "Antropologia", "categoria": "accademica", "descrizione": "Conoscenza dello studio delle culture umane, passate e presenti, e della loro evoluzione sociale (pagina originale assente dal corpus scansionato: descrizione scelta per analogia con le altre skill accademiche gia' documentate, tutte con lo stesso schema - 'non collegata a un comando specifico, richiesta da alcune professioni')."},
    "debating": {"nome": "Dibattito", "categoria": "accademica", "descrizione": "Permette di sfidare un altro personaggio a dibattito (DEBATE <personaggio> [skill]) per guadagnare esperienza e migliorare una skill senza cacciare mostri: ogni round consuma movimento, e chi vince guadagna esperienza mentre chi perde la perde. Funziona meglio contro chi ha un rating simile nella skill Dibattito; troppo piu' alto e gli argomenti risultano incomprensibili, troppo piu' basso e l'avversario si arrende subito. STAND interrompe il dibattito, ma equivale a una resa."},
    "theology": {"nome": "Teologia", "categoria": "accademica", "descrizione": "Conoscenza sistematica delle religioni, delle loro influenze e delle diverse concezioni della verita' religiosa: base di tutte le professioni sacerdotali, richiesta anche per comandi come MARRY e SERMONIZE."},
    "astronomy": {"nome": "Astronomia", "categoria": "accademica", "descrizione": "Conoscenza scientifica della materia nello spazio: posizione, dimensione, distribuzione, moto, composizione ed evoluzione dei corpi celesti. Non collegata a un comando specifico, ma richiesta da alcune professioni, quest o imprese."},
    "dissertation": {"nome": "Dissertazione", "categoria": "accademica", "descrizione": "Capacita' di scrivere un trattato accademico che avanza un nuovo punto di vista frutto di ricerca, di norma un requisito per un titolo accademico avanzato. Non collegata a un comando specifico, ma richiesta da alcune professioni, quest o imprese."},

    # --- occulte / supporto magico ---
    "occult": {"nome": "Occultismo", "categoria": "occulta", "descrizione": "Conoscenza delle influenze e dei fenomeni soprannaturali, oltre la normale comprensione umana: una skill puramente accademica che non aiuta direttamente a lanciare incantesimi, ma e' richiesta da quasi tutte le professioni avanzate con abilita' magiche, oltre che da numerose imprese e quest. Richiesta anche per il comando RITUALIZE, che facilita il lancio degli incantesimi."},
    "spell_casting": {"nome": "Lancio degli Incantesimi", "categoria": "occulta", "descrizione": "La skill di base necessaria per lanciare qualsiasi incantesimo: senza, non si puo' lanciare nulla. Un rating piu' alto riduce le probabilita' di perdere la concentrazione o di fallire il lancio (aiutata dall'Intelligenza) e abbassa il costo in mana insieme al rating nella skill specifica dell'incantesimo. STAND o lasciare la stanza interrompe il lancio; un'interruzione (specie in combattimento) rischia di causare affaticamento, curabile con l'incantesimo Ristoro. Sintassi: CAST <incantesimo> [bersaglio], SPELL <incantesimo>, SPELLS, SKILLS MAGIC."},
    "meditation": {"nome": "Meditazione", "categoria": "occulta", "descrizione": "Aumenta il recupero di mana mentre si dorme o ci si riposa, in modo simile a Guarigione Rapida per i punti ferita: un controllo casuale ad ogni tick decide se si applica il bonus. Non e' collegata al social MEDITATE (che e' solo una posa senza effetto meccanico)."},
    "mask_self": {"nome": "Maschera di Se'", "categoria": "occulta"},
    "scrolls": {"nome": "Pergamene", "categoria": "occulta", "descrizione": "Permette di usare pergamene, libri e tomi magici col comando RECITE. Fa parte di un gruppo di skill per oggetti magici (vedi anche Bastoni per i bastoni magici con BRANDISH, Bacchette per le bacchette con ZAP, Amanuense per crearle): un tentativo senza la skill adeguata rischia di distruggere l'oggetto."},
    "staves": {"nome": "Bastoni", "categoria": "occulta", "descrizione": "Permette di usare bastoni magici e oggetti simili col comando BRANDISH (diversa dalla skill Bastone per usarli come arma da mischia). Fa parte dello stesso gruppo di skill di Pergamene/Bacchette: un tentativo senza la skill adeguata rischia di distruggere l'oggetto."},
    "wands": {"nome": "Bacchette", "categoria": "occulta", "descrizione": "Permette di usare bacchette magiche col comando ZAP: simile ai Bastoni, ma una skill separata perche' le bacchette, piu' piccole, producono di norma magie piu' deboli ma piu' mirate. Un tentativo senza la skill adeguata rischia di distruggere l'oggetto."},
    "lore": {"nome": "Sapienza Arcana", "categoria": "occulta", "descrizione": "Permette di scoprire informazioni dettagliate su un oggetto (le stesse rivelate dall'incantesimo Identificare, ma qui il successo dipende solo dal rating in questa skill, non anche da Lancio degli Incantesimi). Ogni tentativo costa 100 movimento. Sintassi: LORE <oggetto>."},
    "detect_evil": {"nome": "Rilevare il Male", "categoria": "occulta", "descrizione": "Permette di scoprire l'allineamento di un altro personaggio semplicemente guardandolo: i malvagi appaiono circondati da un'aura rossa, i benevoli da una verde. Sintassi: CAST 'DETECT EVIL'/'DETECT GOOD' (vedi anche Rilevare il Bene, la controparte)."},
    "detect_good": {"nome": "Rilevare il Bene", "categoria": "occulta", "descrizione": "Permette di scoprire l'allineamento di un altro personaggio semplicemente guardandolo: i benevoli appaiono circondati da un'aura verde, i malvagi da una rossa. Sintassi: CAST 'DETECT GOOD'/'DETECT EVIL' (vedi anche Rilevare il Male, la controparte)."},
    "detect_magic": {"nome": "Rilevare la Magia", "categoria": "occulta"},
    "cure_light": {"nome": "Cura Leggera", "categoria": "occulta"},
    "bless": {"nome": "Benedizione", "categoria": "occulta"},
    "shocking_grasp": {"nome": "Presa Folgorante", "categoria": "occulta"},
    "dreaming": {"nome": "Arte del Sogno", "categoria": "occulta", "descrizione": "Capacita' di controllare direttamente i propri sogni durante il sonno, viaggiando tra le Terre del Sogno e il Mondo della Veglia (comandi DREAM WALK/DREAM AWAKEN): un rating basso rischia di intrappolare in incubi pericolosi. Aiutata dalla Saggezza; le skill del personaggio possono fluttuare viaggiando tra i due mondi."},
    "clairvoyance": {"nome": "Chiaroveggenza", "categoria": "occulta"},
    "sound_crystal": {"nome": "Cristallo Sonoro", "categoria": "occulta", "descrizione": "Cristallo Sonoro, uno strumento musicale alieno: uno degli strumenti suonabili con PLAY - vedi Musica per il sistema completo."},
    "self_discipline": {"nome": "Autodisciplina", "categoria": "occulta", "descrizione": "Aumenta la forza mentale del personaggio: non alza direttamente alcun attributo, ma da' bonus in situazioni specifiche (resistenza alla magia, agli interrogatori, alla paura, all'intimidazione, tra le altre). Agisce automaticamente."},
    "psychology": {"nome": "Psicologia", "categoria": "occulta", "descrizione": "Permette di ripristinare la sanity perduta di un altro personaggio (PSYCHOLOGY <personaggio>): il successo dipende molto dalla sanity attuale di entrambi, e un tentativo fallito puo' danneggiare la sanity di chi lo esegue. Costa 300 movimento e circa 30 secondi. Chi non ha questa skill puo' rivolgersi a un NPC terapeuta (vedi Terapia)."},
    "teach": {"nome": "Insegnamento", "categoria": "occulta", "descrizione": "Permette di insegnare una skill a un altro personaggio che sta seguendo l'insegnante, spendendo le sue practice (opzione COUNT per specificarne il numero) e pagando automaticamente l'insegnante in denaro. Funziona bene solo se il rating 'effettivo' dell'insegnante (rating in Insegnamento moltiplicato per il rating nella skill insegnata, diviso 100) supera il rating grezzo dell'allievo in quella skill. Bisogna essere Maestri in una skill prima di poterla insegnare. Sintassi: TEACH <giocatore> <skill> [numero]."},
    "scribe": {"nome": "Amanuense", "categoria": "occulta", "descrizione": "Permette di creare una pergamena di un incantesimo gia' conosciuto (deve essere idoneo alla trascrizione): richiede un costo in denaro e mana, occasionalmente un componente, e un foglio di vellum vuoto per ogni copia. Il successo dipende dal rating in questa skill; le pergamene create non sono permanenti e decadono se non usate (si attivano con RECITE). Sintassi: SCRIBE <incantesimo>."},
    "taumathurgy": {"nome": "Taumaturgia", "categoria": "occulta", "descrizione": "Skill-prerequisito per una famiglia di incantesimi di incantamento e manipolazione di armi e oggetti (Anima Arma, Consistenza, Permanenza, Ricarica, Universalita' - ciascuno una voce a se')."},
    "spell_mastery": {"nome": "Maestria negli Incantesimi", "categoria": "occulta", "descrizione": "Come le maestrie con le armi rendono un personaggio piu' efficace in combattimento, questa skill rende piu' potenti ed efficaci gli incantesimi lanciati: maggiore probabilita' di successo, effetti piu' forti e piu' duraturi. Agisce automaticamente ed e' solo uno dei tanti fattori: un personaggio di 5o livello lancera' comunque incantesimi deboli, con o senza questa skill."},
    "ritual_mastery": {"nome": "Maestria nei Rituali", "categoria": "occulta", "descrizione": "Permette di lanciare incantesimi col comando RITUAL al posto di CAST: normalmente non c'e' differenza, ma se ci si raggruppa (GROUP) con altri possessori di questa skill, RITUAL produce incantesimi piu' potenti - tanto piu' quanti sono i membri del gruppo. Sintassi: RITUAL <incantesimo>."},
    "channeling": {"nome": "Incanalamento", "categoria": "occulta", "descrizione": "Riduce sia il costo in mana sia la difficolta' di lanciare incantesimi in ambienti sfavorevoli alla magia (stanze o zone a bassa energia magica). Agisce automaticamente."},
    "elder_magic": {"nome": "Magia degli Antichi", "categoria": "occulta", "descrizione": "Skill-prerequisito per una coppia di incantesimi legati agli Antichi (Armatura di Ygolonac, Maledizione del Cacciatore - ciascuno una voce a se')."},
    "voodoo": {"nome": "Vudu'", "categoria": "occulta", "descrizione": "Conoscenza della religione voodoo (nata dalla fusione di riti cattolici romani con l'animismo e la magia degli schiavi dell'Africa occidentale), qui incentrata sulla bambola voodoo: servono un rating sufficiente, una bambola vuota e dei capelli del bersaglio (vedi CUT) per lanciare l'incantesimo Consacra Bambola e crearne una personalizzata. Una volta pronta, VOODOO STAB da' solo un avvertimento doloroso, VOODOO TWIST infligge danno sia alla bambola sia alla vittima, VOODOO TEAR distrugge la bambola infliggendo dolore e danno gravissimi, potenzialmente letali, ovunque si trovi la vittima."},

    # --- skill abbinate 1:1 ai nuovi incantesimi (Fase G, quinta tornata:
    # world/spells.py) - ogni incantesimo richiede sia "spell_casting" sia
    # la skill omonima, vedi world/magic.py ---
    "absorb_magic": {"nome": "Assorbimento Magico", "categoria": "occulta"},
    "blindness": {"nome": "Accecamento", "categoria": "occulta"},
    "brand": {"nome": "Marchiatura", "categoria": "occulta"},
    "burning_hands": {"nome": "Mani Ardenti", "categoria": "occulta"},
    "call_lightning": {"nome": "Richiamo del Fulmine", "categoria": "occulta"},
    "calm": {"nome": "Calma", "categoria": "occulta"},
    "cancellation": {"nome": "Cancellazione", "categoria": "occulta"},
    "charm_person": {"nome": "Ammaliare", "categoria": "occulta"},
    "continual_light": {"nome": "Luce Continua", "categoria": "occulta"},
    "create_food": {"nome": "Creare Cibo", "categoria": "occulta"},
    "create_spring": {"nome": "Creare Sorgente", "categoria": "occulta"},
    "detect_hidden": {"nome": "Rilevare il Nascosto", "categoria": "occulta"},
    "detect_invis": {"nome": "Rilevare l'Invisibile", "categoria": "occulta"},
    "dispel_magic": {"nome": "Dissolvere la Magia", "categoria": "occulta"},
    "elemental_shield": {"nome": "Scudo Elementale", "categoria": "occulta"},
    "enchant_armor": {"nome": "Incantare Armatura", "categoria": "occulta"},
    "enchant_weapon": {"nome": "Incantare Arma", "categoria": "occulta"},
    "faerie_fire": {"nome": "Fuoco Fatato", "categoria": "occulta"},
    "faerie_fog": {"nome": "Nebbia Fatata", "categoria": "occulta"},
    "fire_breath": {"nome": "Soffio di Fuoco", "categoria": "occulta"},
    "fireball": {"nome": "Palla di Fuoco", "categoria": "occulta"},
    "fly": {"nome": "Volo", "categoria": "occulta"},
    "frost_breath": {"nome": "Soffio Gelido", "categoria": "occulta"},
    "greater_possession": {"nome": "Possessione Maggiore", "categoria": "occulta"},
    "harden_skin": {"nome": "Pelle Indurita", "categoria": "occulta"},
    "haste": {"nome": "Fretta", "categoria": "occulta"},
    "identify": {"nome": "Identificare", "categoria": "occulta"},
    "invis": {"nome": "Invisibilita'", "categoria": "occulta"},
    "lesser_possession": {"nome": "Possessione Minore", "categoria": "occulta"},
    "magic_missile": {"nome": "Missile Magico", "categoria": "occulta"},
    "mass_invis": {"nome": "Invisibilita' di Massa", "categoria": "occulta"},
    "mute": {"nome": "Ammutolire", "categoria": "occulta"},
    "negate_alignment": {"nome": "Negare l'Allineamento", "categoria": "occulta"},
    "pass_door": {"nome": "Attraversare le Porte", "categoria": "occulta"},
    "portal": {"nome": "Portale", "categoria": "occulta"},
    "remove_invis": {"nome": "Rimuovere Invisibilita'", "categoria": "occulta"},
    "shield": {"nome": "Scudo Magico", "categoria": "occulta"},
    "sleep": {"nome": "Sonno", "categoria": "occulta"},
    "strength": {"nome": "Forza (incantesimo)", "categoria": "occulta"},
    "summon": {"nome": "Evocazione", "categoria": "occulta"},
    "summon_familier": {"nome": "Evocare Famiglio", "categoria": "occulta"},
    "ventriloquate": {"nome": "Ventriloquio", "categoria": "occulta"},
    "water_breathing": {"nome": "Respirare in Acqua", "categoria": "occulta"},
    "word_of_recall": {"nome": "Parola di Richiamo", "categoria": "occulta"},
    "teleport": {"nome": "Teletrasporto", "categoria": "occulta"},

    # --- furtive / percezione ---
    "sneak": {"nome": "Furtivita'", "categoria": "furtiva", "descrizione": "Permette di restare nascosti anche mentre ci si muove (a differenza di Nascondersi, che funziona solo restando fermi): probabilita' di successo piu' bassa, ma aiutata da un'alta Destrezza. VISIBLE per tornare visibili."},
    "hide": {"nome": "Nascondersi", "categoria": "furtiva", "descrizione": "Permette di nascondersi per evitare di essere notati: probabilita' di successo molto alta, ma funziona solo restando fermi (per restare nascosti anche muovendosi serve Furtivita'). VISIBLE per tornare visibili."},
    "steal": {"nome": "Furto", "categoria": "furtiva", "descrizione": "Permette di tentare di sottrarre oggetti dall'inventario di un altro personaggio senza permesso (STEAL <personaggio> <oggetto>): se riesce, la vittima non se ne accorge; se fallisce, viene avvisata. Funziona anche su NPC e negozianti, che pero' tendono a reagire con violenza."},
    "pick_lock": {"nome": "Scasso", "categoria": "furtiva", "descrizione": "Permette di scassinare una porta chiusa a chiave senza possederne la chiave (PICK <direzione>/<oggetto>): favorita da un'alta Intelligenza, ma la difficolta' della singola serratura conta molto. STAND per interrompere il tentativo."},
    "search": {"nome": "Ricerca", "categoria": "furtiva", "descrizione": "Aumenta le probabilita' di trovare oggetti o uscite nascoste con SEARCH, usabile su un'intera stanza (continua finche' non si trova qualcosa o si usa STAND) o su un singolo contenitore (una sola ricerca). Alcune uscite nascoste richiedono invece la skill Percezione o un marchingegno."},
    "detection": {"nome": "Percezione", "categoria": "furtiva", "descrizione": "Aumenta l'acume percettivo, permettendo talvolta di vedere oggetti o uscite nascosti senza dover cercare o usare l'incantesimo Rilevare il Nascosto; alcuni elementi del gioco sono visibili solo con un rating sufficiente in questa skill."},

    # --- sopravvivenza / cura ---
    "climb": {"nome": "Arrampicata", "categoria": "sopravvivenza", "descrizione": "Capacita' di trovare appigli su rocce e pendii scoscesi, permettendo di scalare altezze pericolose senza rischio di cadere: skill passiva, calcolata automaticamente senza bisogno di comandi dedicati."},
    "swim": {"nome": "Nuoto", "categoria": "sopravvivenza", "descrizione": "Essenziale per nuotare in laghi o sott'acqua: senza, ci si limita a sguazzare fino allo sfinimento. Calcolata automaticamente nel movimento, aiutata dalla Costituzione: basta continuare a muoversi nella direzione voluta."},
    "riding": {"nome": "Equitazione", "categoria": "sopravvivenza", "descrizione": "Permette di cavalcare biciclette o animali (comando RIDE, entrambi trattati come animali domestici, ma le biciclette non combattono); mentre si cavalca non si puo' entrare in sotterranei o edifici, ma si risparmia molto movimento. STAND per smontare."},
    "tracking": {"nome": "Tracciamento", "categoria": "sopravvivenza", "descrizione": "Permette di esaminare i dettagli minimi di una zona per scoprire chi vi e' passato di recente e in che direzione (comando TRACKS/TRACK <personaggio>): funziona solo in ambienti naturali, non in citta'."},
    "traps": {"nome": "Trappole", "categoria": "sopravvivenza", "descrizione": "Permette di piazzare, disinnescare e riconoscere trappole (TRAP LAY <tipo> in una stanza o su un contenitore: Lama/danno, Groviglio/immobilizza, Dardo/veleno, Mistica/danno solo a chi e' vicino al livello di chi l'ha posta, Spavento/perdita di sanity, Metamorfosi, Ruggine/danneggia l'equipaggiamento; TRAP LAY FOCUS incorpora un incantesimo gia' noto). TRAP DISARM/INFO/TRIGGER completano il set. Un buon rating aiuta anche a individuare ed evitare le trappole altrui. Vietato nelle aree per principianti."},
    "tame": {"nome": "Addomesticamento", "categoria": "sopravvivenza", "descrizione": "Tenta di controllare una creatura (non funziona su NPC senzienti, non-morti o con un minimo di intelligenza naturale), che se domata segue come animale domestico e si comanda con ORDER. Richiede 200 movimento. Sintassi: TAME <personaggio>."},
    "fast_healing": {"nome": "Guarigione Rapida", "categoria": "sopravvivenza", "descrizione": "Aumenta la velocita' di guarigione naturale delle ferite: un controllo casuale ad ogni tick decide se si applica il bonus quella volta; un rating piu' alto riduce le probabilita' di fallimento. Agisce automaticamente."},
    "bandage": {"nome": "Bendaggio", "categoria": "sopravvivenza", "descrizione": "Permette di curare ferite senza incantesimi ne' kit di pronto soccorso, particolarmente efficace contro il sanguinamento (lo interrompe del tutto, a differenza di un incantesimo che restituisce solo punti ferita che il sanguinamento continua a togliere). Costa 50 movimento e un breve ritardo mentre si benda. Sintassi: BANDAGE <personaggio>."},
    "surgery": {"nome": "Chirurgia", "categoria": "sopravvivenza", "descrizione": "Conoscenza della branca della medicina che tratta diagnosi e cura di ferite, deformita' e malattie con mezzi manuali e strumentali, inclusa la capacita' di operare per rimuovere o sostituire un organo malato. In CthulhuMUD serve specificamente a installare impianti biotecnologici (vedi Biotecnologia)."},

    # --- sociali / mestieri ---
    "streetwise": {"nome": "Fiuto di Strada", "categoria": "sociale", "descrizione": "Conoscenza generica delle abilita' che si imparano vivendo per strada in un ambiente urbano: elemosinare, truffare, parlare in fretta, dimestichezza con la malavita. Non collegata a un comando specifico, ma richiesta da alcune professioni."},
    "haggle": {"nome": "Contrattazione", "categoria": "sociale", "descrizione": "Permette di contrattare il prezzo di un articolo con un negoziante, agendo su HAGGLE (attivabile anche in automatico) subito dopo un tentativo di BUY. Alcuni negozianti tollerano poco la contrattazione e possono interrompere la trattativa o cacciare il cliente."},
    "gambling": {"nome": "Azzardo", "categoria": "sociale", "descrizione": "Conoscenza delle regole e delle probabilita' dei giochi d'azzardo, e capacita' di barare ai dadi: THROW <dado> LOW/HIGH/<numero> per tentare di controllare il lancio (rischiando di farsi notare), FAKE DIE per truccare permanentemente un dado (con rischio di distruggerlo se il tentativo fallisce). THROW serve anche per lanciare granate e altre armi."},
    "music": {"nome": "Musica", "categoria": "sociale", "descrizione": "Conoscenza dei principi base della musica (armonia, tonalita', struttura): con un rating sufficiente permette di usare PLAY per suonare vari strumenti (ciascuno una skill a se': Percussioni, Corde, Flauto, Ottoni, Pianoforte, Organo, Cristallo Sonoro) e di sbloccare Canto per cantare stili come blues, jazz, gospel, cori e salmodie con SING. Entrambi costano un po' di movimento; STAND per fermarsi. PLAY puo' anche azionare un jukebox (PLAY LIST per l'elenco, PLAY <canzone> per sceglierne una: i testi vengono trasmessi sul canale MUSICA)."},
    "accounting": {"nome": "Contabilita'", "categoria": "sociale", "descrizione": "Conoscenza delle tecniche contabili per registrare transazioni finanziarie e preparare bilanci. Non collegata a un comando specifico, ma richiesta da alcune professioni, imprese o quest."},
    "tailor": {"nome": "Sartoria", "categoria": "sociale", "descrizione": "Permette di creare un pezzo di armatura dal cadavere di una creatura uccisa (TAILOR <cadavere> <armatura>): statistiche e materiale dipendono dal cadavere di partenza. TAN conserva la pelle di un cadavere in decomposizione per un uso successivo con TAILOR."},
    # "forging" e' registrata sotto "artigianato" (Fase G, terza tornata)

    # --- conoscenza di luogo (lore regionale) ---
    "arkham": {"nome": "Conoscenza di Arkham", "categoria": "conoscenza", "descrizione": "Conoscenza della storia e della cultura di Arkham, Massachusetts, la citta' piu' grande della regione del Miskatonic, alla foce del fiume omonimo sull'Atlantico. Non collegata a un comando specifico, richiesta da alcune professioni."},
    "ulthar": {"nome": "Conoscenza di Ulthar", "categoria": "conoscenza", "descrizione": "Conoscenza della storia e della cultura di Ulthar, la piu' grande citta' del Regno di Skai nelle Terre del Sogno, su una collina lungo il fiume Skai, nota per l'enorme popolazione di gatti protetta da Bast. Richiesta da diverse professioni."},
    "innsmouth": {"nome": "Conoscenza di Innsmouth", "categoria": "conoscenza", "descrizione": "Conoscenza della storia e della cultura di Innsmouth, Massachusetts, cittadina costiera dal passato oscuro e misterioso, le cui voci su creature disumane emerse dal mare portarono un tempo all'intervento dei Marines. Richiesta da diverse professioni."},
    "atlantean": {"nome": "Conoscenza Atlantidea", "categoria": "conoscenza", "descrizione": "Conoscenza della lingua Atlantidea, lingua nativa di varie creature marine come i Profondi."},
    "cthonic": {"nome": "Conoscenza Ctonia", "categoria": "conoscenza", "descrizione": "Conoscenza della lingua Ctonia, parlata da molte razze delle Terre del Sogno incluse diverse Razze Antiche, lingua nativa degli Zoog."},
    "dylath": {"nome": "Conoscenza di Dylath-Leen", "categoria": "conoscenza", "descrizione": "Conoscenza della storia e della cultura di Dylath-Leen, citta' portuale delle Terre del Sogno alla foce del fiume Skai sul Mare del Sud, fiorente ma retta con pugno di ferro dal suo Autocrate. Richiesta da diverse professioni."},
    "stygian": {"nome": "Conoscenza Stigia", "categoria": "conoscenza", "descrizione": "Conoscenza della lingua Stigia, lingua nativa della razza Yithiana."},
    "yuggoth": {"nome": "Conoscenza di Yuggoth", "categoria": "conoscenza", "descrizione": "Conoscenza della storia e della cultura di Yuggoth (il pianeta noto agli umani come Plutone), avamposto principale dei Mi-Go, da cui partono le loro spedizioni esplorative verso la Terra. Richiesta da diverse professioni."},
    "dreamlands": {"nome": "Conoscenza delle Terre del Sogno", "categoria": "conoscenza", "descrizione": "Conoscenza della storia e della cultura delle Terre del Sogno, realta' parallela alla Terra nata (secondo la leggenda) dal sogno collettivo dell'umanita', con leggi fisiche leggermente diverse e una civilta' propria. Richiesta da diverse professioni."},

    # --- Fase K, terza tornata: skill/incantesimi delle tabelle di
    # livello delle 37 professioni avanzate ancora incomplete (fonte:
    # research/site_corpus/info_profs.txt). Tre nomi della fonte sono
    # refusi/varianti di skill gia' registrate sopra e NON vengono
    # duplicati qui: "Anthrapology" (Journeyman) -> "anthropology",
    # "Magis Missile" (Mage) -> "magic_missile", "Staff" (Priest of
    # Foxbird) -> "staves".

    # occulta (incantesimi/poteri)
    "acid_blast": {"nome": "Getto Acido", "categoria": "occulta"},
    "acid_breath": {"nome": "Soffio Acido", "categoria": "occulta"},
    "age": {"nome": "Invecchiamento", "categoria": "occulta"},
    "aura": {"nome": "Aura", "categoria": "occulta"},
    "body_control": {"nome": "Controllo del Corpo", "categoria": "occulta", "descrizione": "Skill-prerequisito per un gruppo di dieci effetti legati al controllo del proprio corpo (Ascetismo, Fardello di Ciccia, Sete Ardente, Cambia Taglia, Grog Libero, Sobrieta' Spettrale, Fame Rodente, Allucina, Rilassati, Linee Snelle - ciascuno una voce a se')."},
    "cause_critical": {"nome": "Causa Ferita Critica", "categoria": "occulta"},
    "cause_light": {"nome": "Causa Ferita Leggera", "categoria": "occulta"},
    "cause_serious": {"nome": "Causa Ferita Grave", "categoria": "occulta"},
    "chain_lightning": {"nome": "Fulmine a Catena", "categoria": "occulta"},
    "chaos_magic": {"nome": "Magia del Caos", "categoria": "occulta", "descrizione": "Skill-prerequisito per una famiglia di incantesimi legati alla magia del caos (pagina originale assente dal corpus scansionato: descrizione scelta per analogia con le altre skill-prerequisito di famiglie di incantesimi, come Magia Naturale/Necromanzia/Via della Natura, gia' documentate)."},
    "chill_touch": {"nome": "Tocco Gelido", "categoria": "occulta"},
    "clerical_magic": {"nome": "Magia Clericale", "categoria": "occulta", "descrizione": "Skill-prerequisito per due incantesimi: Simbolo Clericale (trasforma un comune gioiello in un simbolo sacro) ed Esorcismo (infligge gravi danni ai non-morti)."},
    "way_of_the_conjurer": {"nome": "Via dell'Evocatore", "categoria": "occulta", "descrizione": "Skill-prerequisito per una famiglia di incantesimi di evocazione minore (Richiama Animale, Crea Statuetta, Sacca Dimensionale, Guardiano degli Antichi, Evoca Spirito, Creazione Minore, Creazione Maggiore - ciascuno una voce a se')."},
    "voice": {"nome": "Voce", "categoria": "occulta", "descrizione": "Skill-prerequisito per l'incantesimo Urlo Primordiale, che amplifica magicamente la voce del lanciatore in un grido capace di infliggere danno."},
    "stun_breath": {"nome": "Soffio Stordente", "categoria": "occulta", "descrizione": "Uno dei soffi elementali (famiglia Magia del Soffio): stordisce il bersaglio invece di infliggere danno diretto."},
    "flamestrike": {"nome": "Colonna di Fuoco", "categoria": "occulta", "descrizione": "Incantesimo d'attacco che fa scendere sul bersaglio un'enorme colonna di fiamme."},
    "true_invis": {"nome": "Vera Invisibilita'", "categoria": "occulta", "descrizione": "Versione potenziata di Invisibilita': dura di piu', resiste anche a chi puo' rilevare l'invisibilita' normale, e non svanisce entrando in combattimento."},
    "restore_limb": {"nome": "Ripristina Arto", "categoria": "occulta", "descrizione": "Ripristina la funzionalita' di un arto ferito o menomato (in questo porting, semplificata come una guarigione aggiuntiva: nessun sistema di danno separato per arto esiste)."},
    "colour_spray": {"nome": "Spruzzo Cromatico", "categoria": "occulta"},
    "control_weather": {"nome": "Controllo del Tempo", "categoria": "occulta"},
    "create_buffet": {"nome": "Crea Banchetto", "categoria": "occulta"},
    "create_water": {"nome": "Crea Acqua", "categoria": "occulta"},
    "cure_blindness": {"nome": "Cura Cecita'", "categoria": "occulta"},
    "cure_critical": {"nome": "Cura Ferita Critica", "categoria": "occulta"},
    "cure_disease": {"nome": "Cura Malattia", "categoria": "occulta"},
    "cure_poison": {"nome": "Cura Veleno", "categoria": "occulta"},
    "cure_serious": {"nome": "Cura Ferita Grave", "categoria": "occulta"},
    "curse": {"nome": "Maledizione", "categoria": "occulta"},
    "demonfire": {"nome": "Fuoco Demoniaco", "categoria": "occulta"},
    "detect_poison": {"nome": "Rileva Veleno", "categoria": "occulta"},
    "dispel_evil": {"nome": "Dissolvi Male", "categoria": "occulta"},
    "dispel_good": {"nome": "Dissolvi Bene", "categoria": "occulta"},
    "divine_magic": {"nome": "Magia Divina", "categoria": "occulta", "descrizione": "Skill-prerequisito per un gruppo di nove incantesimi di magia divina (tra cui Mortalizza, Evoca Antico, Guardia dell'Anima - ciascuno una voce a se')."},
    "dream_magic": {"nome": "Magia Onirica", "categoria": "occulta", "descrizione": "Skill-prerequisito per una famiglia di incantesimi onirici: Trance migliora la capacita' di sognare, Vera Dormienza trasporta il corpo fisico dentro il sogno recidendo il legame col mondo reale, Risveglio Brusco riporta indietro chi sogna, Sogno Ricorrente rimanda al punto in cui si sognava l'ultima volta, Sonno Incantato immerge in un sonno profondo e sicuro che porta dritti nelle Terre del Sogno, Sonno Maledetto fa lo stesso ma in un incubo pericoloso."},
    "earthquake": {"nome": "Terremoto", "categoria": "occulta"},
    "elemental_combat": {"nome": "Combattimento Elementale", "categoria": "occulta", "descrizione": "Skill-prerequisito per una famiglia di incantesimi che rendono un bersaglio piu' vulnerabile a un elemento specifico: Vendetta di Cthugha (fuoco), Vendetta di Ithaqua (freddo), Vendetta di Tsathoggua (armi), Vendetta di Yog (fulmine) - ciascuno una voce a se'."},
    "energy_drain": {"nome": "Drenaggio d'Energia", "categoria": "occulta"},
    "gas_breath": {"nome": "Soffio di Gas", "categoria": "occulta"},
    "gate": {"nome": "Varco Dimensionale", "categoria": "occulta"},
    "harm": {"nome": "Danno Divino", "categoria": "occulta"},
    "heal": {"nome": "Guarigione", "categoria": "occulta"},
    "holy_word": {"nome": "Parola Sacra", "categoria": "occulta"},
    "know_alignment": {"nome": "Percepisci Allineamento", "categoria": "occulta"},
    "lesser_protection": {"nome": "Protezione Minore", "categoria": "occulta"},
    "lightning_bolt": {"nome": "Fulmine", "categoria": "occulta"},
    "lightning_breath": {"nome": "Soffio Fulminante", "categoria": "occulta"},
    "locate_object": {"nome": "Localizza Oggetto", "categoria": "occulta"},
    "magefire": {"nome": "Fuoco Arcano", "categoria": "occulta"},
    "mass_healing": {"nome": "Guarigione di Massa", "categoria": "occulta"},
    "master_dreamer": {"nome": "Maestro Sognatore", "categoria": "occulta", "descrizione": "Il culmine della conoscenza della Magia Onirica, analogo alle maestrie-arma ma per il sognare (pagina originale assente dal corpus scansionato: descrizione scelta per analogia con le maestrie gia' documentate, coerente col fatto che compaia proprio nelle tabelle accanto a Magia Onirica)."},
    "mental_magic": {"nome": "Magia Mentale", "categoria": "occulta", "descrizione": "Skill-prerequisito per un terzetto di incantesimi mentali (Esplosione Astrale, Cammino Astrale, Fusione Mentale - ciascuno una voce a se'). Fusione Mentale e' una scoperta successiva: la sua pagina nel corpus era duplicata sotto un nome diverso e non era stata notata come terzo incantesimo della famiglia."},
    "natural_magic": {"nome": "Magia Naturale", "categoria": "occulta", "descrizione": "Conoscenza e comprensione delle forze arcane grezze che governano le azioni fondamentali della vita. Non collegata direttamente a una skill specifica, ma richiesta da alcune imprese o quest."},
    "necromancy": {"nome": "Negromanzia", "categoria": "occulta", "descrizione": "Skill-prerequisito per un gruppo di incantesimi legati alla creazione e al controllo dei morti e dei non-morti (Anima Morto, Lich, Oscurita', Mummifica, Profana, Lama dell'Anima, Sosia, Sorgente di Sangue, Pugno di Azathoth, Inquietudine - ciascuno una voce a se')."},
    "plague": {"nome": "Peste", "categoria": "occulta"},
    "poison": {"nome": "Veleno (incantesimo)", "categoria": "occulta"},
    "protection_evil": {"nome": "Protezione dal Male", "categoria": "occulta"},
    "protection_good": {"nome": "Protezione dal Bene", "categoria": "occulta"},
    "protective_magic": {"nome": "Magia Protettiva", "categoria": "occulta", "descrizione": "Skill-prerequisito per due incantesimi difensivi: Globo di Protezione avvolge il lanciatore in una sfera che migliora drasticamente la classe armatura, Santuario riduce del 50% tutto il danno subito dal bersaglio; se lanciati entrambi sullo stesso personaggio, gli effetti si sommano."},
    "psychic_anchor": {"nome": "Ancora Psichica", "categoria": "occulta"},
    "regeneration": {"nome": "Rigenerazione", "categoria": "occulta"},
    "remove_curse": {"nome": "Rimuovi Maledizione", "categoria": "occulta"},
    "remove_fear": {"nome": "Rimuovi Paura", "categoria": "occulta"},
    "scrying": {"nome": "Scrutare", "categoria": "occulta", "descrizione": "Permette di spiare brevemente un altro personaggio (NPC o giocatore), a patto di avere un oggetto adatto e un rating sufficiente: piu' difficile contro chi ha un livello superiore, impossibile contro certi NPC legati a quest (come bersagli di taglia), e bloccata dalla natura magica di alcune stanze. Un alto rating in Fortuna aiuta il bersaglio ad accorgersi di chi lo spia. Se riesce, mostra il bersaglio, la stanza in cui si trova e chi/cosa altro c'e' li'. Sintassi: SCRY <personaggio>."},
    "vision": {"nome": "Visione", "categoria": "occulta"},
    "way_of_nature": {"nome": "Via della Natura", "categoria": "occulta", "descrizione": "Skill-prerequisito per un gruppo di incantesimi legati alle forze mistiche grezze della natura (Crea Seme, Drena Vitalita', Maledizione degli Insetti, Morso di Lupo - ciascuno una voce a se')."},
    "weaken": {"nome": "Indebolisci", "categoria": "occulta"},
    "youth": {"nome": "Giovinezza", "categoria": "occulta"},

    # arma (maestrie e armi da fuoco/lancio)
    "artillery": {"nome": "Artiglieria", "categoria": "arma", "descrizione": "Uso di armamenti pesanti a bombardamento esplosivo, azionati col comando FIRE."},
    "axe_master": {"nome": "Maestria con l'Ascia", "categoria": "arma", "descrizione": "Maestria avanzata dell'arma Ascia: aumenta i tiri offensivi e difensivi quando la si impugna, aiutata dalla Destrezza."},
    "blackjack": {"nome": "Manganello", "categoria": "arma", "descrizione": "Un attacco pensato per stordire l'avversario al primo colpo invece di ucciderlo: se riesce e' un modo rapido di disfarsi di un nemico, se fallisce si passa al combattimento normale. Infligge solo danno stordente. Sintassi: BLACKJACK <bersaglio>."},
    "dual": {"nome": "Doppia Arma", "categoria": "arma", "descrizione": "Permette di impugnare due armi contemporaneamente al posto della combinazione arma-e-scudo (valgono le normali regole di ingombro): modifica colpire e danno con la seconda arma, ma con un rating basso i risultati sono modesti. Sintassi: DUAL <arma>."},
    "flail_master": {"nome": "Maestria col Flagello", "categoria": "arma", "descrizione": "Maestria avanzata dell'arma Mazzafrusto: aumenta i tiri offensivi e difensivi quando lo si impugna, aiutata dalla Destrezza."},
    "mace_master": {"nome": "Maestria con la Mazza", "categoria": "arma", "descrizione": "Maestria avanzata dell'arma Mazza: aumenta i tiri offensivi e difensivi quando la si impugna, aiutata dalla Destrezza."},
    "machinegun": {"nome": "Mitragliatrice", "categoria": "arma", "descrizione": "Uso di mitragliatrici medie e pesanti."},
    "marksman": {"nome": "Tiratore Scelto", "categoria": "arma", "descrizione": "La maestria principale per le armi da fuoco: aumenta i tiri offensivi e difensivi quando si spara, aiutata dalla Destrezza."},
    "master_archer": {"nome": "Maestro Arciere", "categoria": "arma", "descrizione": "Maestria avanzata per tutte le armi ad arco: aumenta i tiri offensivi e difensivi quando si tira, aiutata dalla Destrezza."},
    "net": {"nome": "Rete", "categoria": "arma", "descrizione": "Permette di intrappolare un nemico con una rete: HOLD per impugnarla e THROW <bersaglio> per lanciarla. Se riesce, il bersaglio resta impigliato e immobilizzato (movimento portato a -50) finche' non si rigenera; se fallisce, il bersaglio si ritrova la rete in inventario e non sara' contento."},
    "polearm_master": {"nome": "Maestria con l'Arma in Asta", "categoria": "arma", "descrizione": "Maestria avanzata dell'arma in Asta: aumenta i tiri offensivi e difensivi quando la si impugna, aiutata dalla Destrezza."},
    "sniper": {"nome": "Cecchino", "categoria": "arma", "descrizione": "Maestria specializzata per i fucili di precisione, usati col comando SNIPE: aumenta ulteriormente i tiri offensivi rispetto al semplice Tiratore Scelto."},
    "spear_master": {"nome": "Maestria con la Lancia", "categoria": "arma", "descrizione": "Maestria avanzata dell'arma Lancia: aumenta i tiri offensivi e difensivi quando la si impugna, aiutata dalla Destrezza."},
    "submachinegun": {"nome": "Mitra", "categoria": "arma", "descrizione": "Uso di mitra e altre armi da fuoco automatiche leggere."},
    "sword_master": {"nome": "Maestria con la Spada", "categoria": "arma", "descrizione": "Maestria avanzata dell'arma Spada: aumenta i tiri offensivi e difensivi quando la si impugna, aiutata dalla Destrezza."},
    "whip_master": {"nome": "Maestria con la Frusta", "categoria": "arma", "descrizione": "Maestria avanzata dell'arma Frusta: aumenta i tiri offensivi e difensivi quando la si impugna, aiutata dalla Destrezza."},

    # furtiva
    "assassinate": {"nome": "Assassinio", "categoria": "furtiva", "descrizione": "La skill maestra dell'uccisione silenziosa e rapida: offre un netto vantaggio nel primo attacco, sia nella probabilita' di colpire sia nel danno inflitto, ulteriormente aumentato se si usa un'arma da fuoco (ancora di piu' con un fucile di precisione). Sintassi: ASSASSINATE <bersaglio>."},
    "envenom": {"nome": "Avvelenare", "categoria": "furtiva", "descrizione": "Permette di ricoprire un'arma con un sottile strato di veleno, trasferito al nemico colpito in combattimento; l'effetto non e' permanente e svanisce col tempo. Utilizzabile anche per avvelenare cibo o bevande. Sintassi: ENVENOM <oggetto>."},
    "forgery": {"nome": "Falsificazione", "categoria": "furtiva", "descrizione": "Permette di creare un passaporto falso. Sintassi: FAKE PASSPORT [personaggio]."},
    "identity": {"nome": "Identita' Falsa", "categoria": "furtiva", "descrizione": "Rappresenta la capacita' di assumere e mantenere un'identita' fittizia in societa' (pagina originale assente dal corpus scansionato: descrizione scelta per analogia con Falsificazione, gia' documentata, e col contesto della tabella dell'Apprendista Provetto in cui compare)."},
    "peek": {"nome": "Sbirciare", "categoria": "furtiva", "descrizione": "Aumenta le capacita' percettive, dando una migliore possibilita' di vedere gli oggetti nell'inventario di un bersaglio (funziona meglio contro chi ha una bassa Intelligenza); agisce automaticamente con LOOK, senza bisogno di un comando dedicato."},

    # combattimento
    "frenzy": {"nome": "Frenesia", "categoria": "combattimento"},
    "rotate": {"nome": "Rotazione", "categoria": "combattimento", "descrizione": "Permette di spostare il proprio bersaglio durante un combattimento gia' in corso, per concentrare gli sforzi su un nemico specifico tra quelli gia' impegnati (non su chi non e' ancora entrato nello scontro): utile contro piu' avversari, per colpire il piu' pericoloso. Dipende da Destrezza, differenza di livello col bersaglio e rating. Sintassi: ROTATE <bersaglio>."},
    "way_of_the_duellant": {"nome": "Via del Duellante", "categoria": "combattimento", "descrizione": "Skill-prerequisito per una famiglia di incantesimi di combattimento arcano (Duello Magico, Scudo Mentale, Psi Twister, Telecinesi, Terrore degli Antichi, Ira di Cthugha, Ira di Ithaqua - ciascuno una voce a se')."},

    # sociale
    "interrogate": {"nome": "Interrogatorio", "categoria": "sociale", "descrizione": "Permette di scoprire esattamente quali argomenti un NPC e' programmato per discutere, utilizzabili poi con ASK o TALK. Sintassi: INTERROGATE <personaggio>."},
    "intimidate": {"nome": "Intimidire", "categoria": "sociale", "descrizione": "Atto di intimidire un altro personaggio per farlo fuggire dalla stanza in una direzione casuale; se fallisce, il bersaglio potrebbe arrabbiarsi e attaccare. Sintassi: INTIMIDATE <personaggio>."},
    "leadership": {"nome": "Comando", "categoria": "sociale", "descrizione": "Concede bonus di combattimento aggiuntivi a un intero gruppo se il suo capogruppo ha un buon rating in questa skill (bonus a colpire, difesa e danno per tutti i membri): agisce automaticamente, nessun comando dedicato."},
    "manipulation": {"nome": "Manipolazione", "categoria": "sociale", "descrizione": "Skill-prerequisito per una famiglia di incantesimi mentali (Agonia, Paura, Paralisi - ciascuno una voce a se')."},
    "recruit": {"nome": "Reclutare", "categoria": "sociale", "descrizione": "Permette di attrarre spontaneamente nuovi seguaci mentre si viaggia per il mondo, in proporzione al rating: agisce automaticamente. I seguaci ottenuti sono completamente leali e si comandano con ORDER."},
    "tactics": {"nome": "Tattica", "categoria": "sociale", "descrizione": "Aumenta la conoscenza di metodi di combattimento coordinato: usando DISTRACT <bersaglio> per attirare l'attenzione del nemico su di se', il resto del gruppo ottiene bonus a colpire e ferire quel bersaglio."},

    # artigianato
    "brew": {"nome": "Preparare Pozioni", "categoria": "artigianato", "descrizione": "Permette di tentare di preparare una pozione di un incantesimo che il personaggio gia' conosce (in linea di massima solo per incantesimi non d'attacco): richiede componenti specifici, un costo in denaro e in mana. Le pozioni ottenute non sono permanenti e evaporano se non usate. Sintassi: BREW <incantesimo>."},
    "goldsmith": {"nome": "Orafo", "categoria": "artigianato", "descrizione": "Versione piu' delicata della Forgiatura: invece di armi e armature, crea gioielli da gemme grezze, con gli stessi requisiti (incudine o forgia, 200 movimento a tentativo)."},
    "sharpen": {"nome": "Affilare", "categoria": "artigianato", "descrizione": "Migliora un'arma da taglio affilandone la lama: un tentativo riuscito le da' il flag Affilata, e in rari casi anche quello Vorpal; uno fallito puo' lasciarla invariata o smussarla oltre riparazione. Il successo dipende da livello, rating, Destrezza e Forza."},

    # accademica
    "biotechnology": {"nome": "Biotecnologia", "categoria": "accademica", "descrizione": "Permette di creare un impianto cibernetico da installare chirurgicamente nel cervello di un personaggio per aumentarne un attributo: chi crea l'impianto deve avere questa skill e mille monete d'oro in materiali, chi lo installa deve avere la skill Chirurgia, ed entrambi devono trovarsi in un laboratorio attrezzato. Un intervento del genere e' un'esperienza traumatica per il corpo."},

    # sopravvivenza
    "survival": {"nome": "Sopravvivenza", "categoria": "sopravvivenza", "descrizione": "Conoscenza delle tecniche per sopravvivere in ambienti privi di comodita' moderne: permette di costruire un fuoco da campo efficace (comando CAMP, solo all'aperto) che accelera la rigenerazione mentre si riposa nella stanza."},

    # musicale (strumenti e performance - Bardo/Musicista)
    "brass": {"nome": "Ottoni", "categoria": "musicale", "descrizione": "Ottoni (tromba, trombone, tuba...): uno degli strumenti suonabili con PLAY - vedi Musica per il sistema completo."},
    "flute": {"nome": "Flauto", "categoria": "musicale", "descrizione": "Flauti e flauti dolci: uno degli strumenti suonabili con PLAY - vedi Musica per il sistema completo."},
    "organ": {"nome": "Organo", "categoria": "musicale", "descrizione": "L'organo: uno degli strumenti suonabili con PLAY - vedi Musica per il sistema completo."},
    "percussion": {"nome": "Percussioni", "categoria": "musicale", "descrizione": "Percussioni (tamburi e simili): uno degli strumenti suonabili con PLAY - vedi Musica per il sistema completo."},
    "piano": {"nome": "Pianoforte", "categoria": "musicale", "descrizione": "Il pianoforte: uno degli strumenti suonabili con PLAY - vedi Musica per il sistema completo."},
    "singing": {"nome": "Canto", "categoria": "musicale", "descrizione": "Permette di cantare vari stili (blues, jazz, gospel, cori, salmodie...) col comando SING, sbloccata da un buon rating in Musica - vedi Musica per il sistema completo."},
    "strings": {"nome": "Corde", "categoria": "musicale", "descrizione": "Strumenti a corda (violino, violoncello...): uno degli strumenti suonabili con PLAY - vedi Musica per il sistema completo."},

    # Fase K, quarta tornata: due skill riclassificate da "artigianato"/
    # "musicale" a "occulta" dopo aver letto la pagina reale del corpus
    # (mai controllata prima d'ora): entrambe sono in realta' incantesimi
    # magici, non skill di mestiere/musica come si era assunto per
    # somiglianza del nome - "create_potion" (helps/create_potion.txt: "This
    # SPELL enables a character to mix together random herbs...") e
    # "vocalize" (helps/vocalize.txt: "This SPELL enables the target
    # character to cast spells without... verbal incantations" - compare
    # anche dove compare davvero nelle tabelle, Mentalista liv.7 insieme a
    # Rilevare il Nascosto, non nel Musicista). Vedi world/spells.py.
    "create_potion": {"nome": "Crea Pozione", "categoria": "occulta"},
    "vocalize": {"nome": "Vocalizzo", "categoria": "occulta"},
}


def nome_skill(skill_id):
    """Ritorna il nome italiano di una skill, o la chiave stessa se manca."""
    entry = SKILLS.get(skill_id)
    return entry["nome"] if entry else skill_id


def descrizione_skill(skill_id):
    """Ritorna la descrizione italiana di una skill (Fase K, quinta tornata).

    La maggior parte delle voci ha una propria "descrizione"; le ~102 che
    sono anche incantesimi lanciabili (stesso ID in world/spells.py, es.
    "sleep"/"shield"/"poison") non la duplicano qui - il testo, identico
    concettualmente, si legge gia' dalla voce di world.spells.SPELLS.
    """
    entry = SKILLS.get(skill_id)
    if not entry:
        return None
    if "descrizione" in entry:
        return entry["descrizione"]
    from world.spells import SPELLS
    spell = SPELLS.get(skill_id)
    if spell:
        return spell["descrizione"]
    return None


# Fase K, ventitreesima tornata: comandi SKILLS/SKILL (helps/skills.txt),
# generali a TUTTE le skill del gioco, non solo a quelle magiche - un
# gap distinto (ma correlato) trovato durante l'audit del sistema di
# magia. Mappa i gruppi della fonte alle "categoria" gia' presenti in
# SKILLS. Semplificazione dichiarata: questo porting non distingue le
# lingue in moderne/antiche/criptiche (mlang/alang/clang della fonte),
# quindi i tre gruppi collassano tutti sull'intera categoria "lingua".
# "SKILLS" senza argomenti mostra le skill "generali e di combattimento"
# (helps/skills.txt): qui interpretato come tutte le categorie tranne
# magia e lingue, che la fonte elenca come gruppi a se stanti.
CATEGORIE_GENERALI = tuple(
    c for c in {e.get("categoria") for e in SKILLS.values()} - {"occulta", "lingua"} if c
)

GRUPPI_SKILLS = {
    "combat": ("combattimento", "arma"),
    "magic": ("occulta",),
    "lang": ("lingua",),
    "mlang": ("lingua",),
    "alang": ("lingua",),
    "clang": ("lingua",),
    "academic": ("accademica",),
    "production": ("artigianato",),
    # "combat and general" (helps/skills.txt): stessa selezione della
    # SKILLS senza argomenti, dato che generale gia' include combat/arma.
    "cng": CATEGORIE_GENERALI,
}


def skills_conosciute(personaggio, categorie=None):
    """Ritorna [(skill_id, rating)] delle skill con rating > 0 possedute
    da personaggio, ordinate per nome italiano; se categorie e' dato,
    filtra solo le skill di quelle categorie."""
    skills = personaggio.db.skills or {}
    risultato = []
    for sid, rating in skills.items():
        if rating <= 0:
            continue
        if categorie is not None:
            entry = SKILLS.get(sid)
            if not entry or entry.get("categoria") not in categorie:
                continue
        risultato.append((sid, rating))
    return sorted(risultato, key=lambda t: nome_skill(t[0]))


def professioni_con_skill(skill_id):
    """SKILL PROFS <skill> (helps/skills.txt): [(nome_professione, livello)]
    per ogni professione (newbie o avanzata) che sblocca skill_id a un
    certo livello, ordinate per livello poi nome."""
    from world.professions_newbie import NEWBIE_PROFESSIONS, nome_professione
    from world.professions_avanzate import PROFESSIONI_AVANZATE, nome_professione_avanzata

    risultati = []
    for pid, dati in NEWBIE_PROFESSIONS.items():
        for livello, lista in (dati.get("skill_per_livello") or {}).items():
            if skill_id in lista:
                risultati.append((nome_professione(pid), livello))
    for pid, dati in PROFESSIONI_AVANZATE.items():
        for livello, lista in (dati.get("skill_per_livello") or {}).items():
            if skill_id in lista:
                risultati.append((nome_professione_avanzata(pid), livello))
    return sorted(risultati, key=lambda t: (t[1], t[0]))
