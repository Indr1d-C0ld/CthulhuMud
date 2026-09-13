# Introduzione

## Cos'è CthulhuMud

*CthulhuMud ITA Redux* è un porting integrale, in lingua italiana, dello storico MUD in lingua inglese *CthulhuMUD* (cthulhumud.com), un mondo testuale multigiocatore ambientato nell'universo narrativo di H. P. Lovecraft. Il porting è costruito sul motore open source **Evennia** (Python), e mira alla fedeltà più stretta possibile alle meccaniche, ai contenuti e allo spirito dell'originale, pur essendo un'opera scritta interamente da zero: nessun file, nessuna riga di codice del CthulhuMUD originale è stata copiata o riutilizzata, solo la sua documentazione pubblica (help file, guide, pagine per Immortal/builder) è stata studiata in modo esaustivo per ricostruirne fedelmente le regole.

## Filosofia del porting

Ogni meccanica descritta in questo Codex rientra in una di due categorie, sempre dichiarate esplicitamente nel codice sorgente e, dove rilevante, in questo stesso documento:

- **Confermata dalla fonte**: la regola, il numero o il comportamento sono attestati da un help file, una guida o una pagina Immortal del sito originale. In questi casi il Codex cita la fonte (es. *helps/wimpy.txt*) e, quando utile, riporta la formulazione originale in inglese accanto alla sua traduzione/applicazione italiana.
- **Scelta di design del porting**: la fonte non specifica un dettaglio (un numero esatto, una probabilità, una soglia) necessario per implementare comunque la meccanica in modo giocabile. In questi casi il Codex lo segnala esplicitamente come tale, invece di spacciarlo per materiale originale.

Questa distinzione è il principio guida che ha accompagnato l'intero sviluppo e che rende questo Codex, oltre che un manuale di gioco, anche un resoconto onesto di cosa viene dalla fonte e cosa è stato inventato per completarla.

## Il mondo di gioco

Il gioco è ambientato negli anni '20 del XX secolo, nell'omonimo universo cosmico-orrorifico di Lovecraft. Le ambientazioni esplorabili includono, tra le altre:

- **Arkham**, Massachusetts: la cittadina universitaria del Miskatonic, cuore pulsante della narrativa lovecraftiana, con decine di edifici visitabili (negozi, l'Università Miskatonic, la Seconda Banca, abitazioni, vicoli).
- **Il Cairo**: incluso il Bazaar con i suoi mercanti, le Piramidi di Giza e la Sfinge, raggiungibile da Arkham via nave.
- **Le Dreamlands**: la dimensione onirica lovecraftiana, raggiungibile tramite la skill Dreaming o incantesimi dedicati, che include luoghi come Ulthar (la città dei gatti) e il Villaggio degli Zoog.
- Un sommergibile e altre ambientazioni minori.

## Filosofia meccanica

CthulhuMud è un gioco **classless** (senza classi rigide): la crescita del personaggio passa attraverso l'acquisizione libera di *skill* (abilità) tramite PRACTICE, LEARN, DEBATE, TRAIN e RESEARCH, non attraverso un albero di classe prestabilito. Alla creazione si sceglie una *professione* di partenza (newbie o avanzata), ma il personaggio può nel tempo apprendere skill al di fuori della propria professione.

La **sanità mentale** (sanity) non è un semplice numero cosmetico: scendere sotto certe soglie causa azioni erratiche automatiche (fuga immotivata, attacchi a caso, borbottii, pianto isterico) che il giocatore non controlla direttamente — un'meccanica fedele allo spirito dell'orrore cosmico lovecraftiano, dove la mente del personaggio non è mai del tutto sotto il suo controllo.

Il gioco supporta **reincarnazioni illimitate** tramite il sistema REMORT, e permette di diventare permanentemente qualcosa di non del tutto umano tramite le tre sottorazze acquisibili in gioco: **Lich** (non-morto incantatore), **Vampire** e **Were** (licantropo), ciascuna con una propria disciplina di poteri.

## Come leggere questo Codex

I capitoli che seguono sono organizzati per area di gioco (razze, magia, combattimento, economia, luoghi, eccetera) e non necessariamente nell'ordine in cui un nuovo giocatore li incontrerebbe in gioco. Chi è alla prima connessione può concentrarsi sui capitoli 1 (Iniziare), 2 (Razze e Sottorazze) e 3 (Professioni e Skill) prima di addentrarsi nel resto.

Le sezioni di comando riportano sempre la sintassi esatta digitabile in gioco in formato `codice`, e ogni capitolo indica, dove pertinente, quali meccaniche sono già presenti nella versione attuale e quali sono dichiaratamente escluse dallo scope del porting (con la relativa motivazione).
