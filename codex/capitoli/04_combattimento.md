# Combattimento, Sopravvivenza e Pericoli

## 1. Il combattimento

### Come si entra in combattimento

Il modo diretto di iniziare uno scontro è il comando `kill <bersaglio>` (`commands/cthulhu.py:CmdKill`), che avvia il combattimento chiamando `avvia_combattimento()` sul chiamante. Se il bersaglio è un NPC marcato come **protetto** (`db.protetto`, tipicamente forze dell'ordine — poliziotti, guardie di frontiera, sentinelle), `KILL` si rifiuta e indirizza a `murder <bersaglio>`: usare `MURDER` funziona sempre, ma se il bersaglio era protetto rende chi attacca un **criminale** (vedi §4). Questa distinzione KILL/MURDER e le sue conseguenze sono confermate dalla fonte (*helps/murder.txt*, *helps/criminal.txt*): *"Players who use MURDER to kill protected NPCs will automatically become criminals"*.

**Chi offre un servizio ai giocatori è intoccabile** (scelta di design del porting, non della fonte): istruttori, mercanti, terapeuti, albergatori e l'impiegato dell'Ufficio Taglie. Nessun giocatore può far loro del male né impadronirsene, in nessun modo: `KILL` e `MURDER` rifiutano — a differenza degli NPC protetti, qui nemmeno diventando criminali —, e così le mosse speciali, il morso del vampiro, la bambola vudù, `TAME`, la possessione Yithiana, il dominio del Lich e **qualunque incantesimo** mirato su di loro, anche quelli senza danno (Ammaliare li trasformerebbe in seguaci e li porterebbe via dalla bottega, Teletrasporto li sposterebbe altrove). Gli incantesimi ad area colpiscono chiunque altro nella stanza, ma non loro, e un intoccabile non entra mai in combattimento. Il rifiuto arriva prima del lancio, quindi il mana non viene speso.

Il motivo è pratico: il gioco dipende da loro. Morto un mercante sparisce la sua bottega; morto il Dr. Armitage, la stanza di partenza di Arkham resta senza l'unico istruttore di incantesimi; morto un terapeuta, in quella città non si cura più la sanità. La protezione è ricavata dal **ruolo** (chi ha un negozio, insegna, cura la mente, gestisce un albergo o l'Ufficio Taglie), quindi vale da sola anche per chi verrà aggiunto in futuro. Lo staff conserva `SLAY`.

Prima di poter attaccare un **newbie** (personaggio non-remortato tra livello 3 e 14, *helps/newbie.txt*/*helps/newbies.txt*), sia `KILL` sia `MURDER` vengono bloccati incondizionatamente (`world/pk.py:uccidi_o_murder`, `e_newbie()`) — protezione confermata dalla fonte: *"you cannot attack them for ANY reason"*.

Oltre all'attacco volontario, il combattimento può iniziare automaticamente:

- **Aggro a vista**: un mostro con `db.attacca_a_vista` attacca un personaggio non appena questo entra nella sua stanza (`typeclasses/rooms.py:at_object_receive`), oppure quando è il mostro a vagare in una stanza già occupata (`world/mostri_movimento.py`, tramite la stessa funzione condivisa `world/mostri.py:tenta_aggro`). Vedi §7 per il dettaglio del margine di livello.
- **Contrattacco automatico**: se un colpo va a segno e il difensore non aveva ancora un bersaglio di combattimento proprio, contrattacca automaticamente (`world/combat.py:_esegui_attacco`), anche se non è stato lui a digitare `KILL` per primo.
- **AUTOASSIST**: se un membro del proprio gruppo viene attaccato, chi ha attivato `AUTOASSIST` si getta automaticamente nella mischia (`world/gruppo.py:assist_automatico`) — confermato dalla fonte (*helps/follow.txt*: *"If one member of the group is attacked, all the members of the group will automatically join the fight"*).
- **ASSIST tra mostri**: quando un mostro del bestiario viene attaccato, ogni altro mostro ostile presente nella stessa stanza e non già impegnato si unisce contro lo stesso aggressore (`world/mostri.py:tenta_assist`, equivalente al flag `ASSIST-ALL` della fonte, *immhelp_flags.txt*). Vedi §7 per i dettagli e per cosa **non** è implementato di questa famiglia di flag.

`avvia_combattimento()` (`typeclasses/living.py`) gestisce anche alcuni effetti collaterali dell'ingaggio: un corpo in **Cammino Astrale** (`db.stati["astrale"]`) non può essere ingaggiato normalmente (*"most mobs cannot attack astral bodies"*, confermato dalla fonte — solo l'incantesimo Esplosione Astrale lo colpisce); l'invisibilità magica normale svanisce entrando in combattimento (confermato dalla fonte), ma la **Vera Invisibilità** no (*"does not immediately wear off when a character engages in combat"*, confermato); chi era `REST`/`SLEEP` si rialza in piedi per poter combattere; e affrontare un bersaglio con `db.orrore` impostato (cioè un mostro spaventoso) costa immediatamente **sanity** — meccanica reale, non cosmetica, confermata dalla fonte (vedi §5).

### Risoluzione dei round

Ogni round di combattimento è governato da `world/combat.py:risolvi_round()`, eseguito periodicamente da uno script (`CombatRoundScript`) per ogni combattente. In ordine:

1. **Controllo del bersaglio**: se il bersaglio non esiste più, non è vivo, o non è più nella stessa stanza, il combattimento si ferma.
2. **Stati che bloccano completamente il turno**: se il personaggio è **addormentato** o **paralizzato** (`db.stati`), perde semplicemente il turno e non può nemmeno tentare di fuggire (*"Fase K, sesta tornata: Sonno/incantesimi immobilizzanti"* — scelta di design del porting, coerente con la logica generale degli effetti di stato).
3. **Impaurito**: equivalente a una fuga forzata, tramite la stessa funzione `tenta_fuga()` usata da `FLEE` (effetto dell'incantesimo Paura — scelta di design del porting).
4. **Allucinato**: il 40% delle volte (scelta di design), il colpo devia su un bersaglio a caso presente nella stanza — alleati inclusi. Questo è confermato in linea di principio dalla fonte per l'incantesimo Allucina, descritto come pericoloso *"per il lanciatore e per chiunque incontri le allucinazioni"*; la percentuale esatta (40%) è una scelta di design.
5. **Azione erratica da bassa sanity**: se la sanity del personaggio è sotto soglia, può scattare un'azione erratica automatica al posto dell'attacco normale (borbottare, ridere, piangere, vagare, attaccare a caso, fuggire) — meccanica reale confermata dalla fonte (vedi §5). Se l'azione è `attacca_a_caso`, `fugge` o `vaga`, il round finisce lì.
6. **Arma da fuoco senza munizioni**: se l'arma equipaggiata è da fuoco e non ha colpi in canna, il round si risolve in uno scatto a vuoto, senza consumare il turno per altro.
7. **Colpo base**: si esegue `_esegui_attacco()` (vedi sotto). Se il difensore muore, il round finisce.
8. **Second/Third/Fourth Attack**: fino a 3 colpi extra nello stesso round (vedi sotto).

### Hit chance e danno

La formula di colpire (`typeclasses/living.py:calcola_hit_chance`) e quella di danno (`calcola_danno`) **non sono documentate dal sito originale** (nessuna pagina di help specifica percentuali o dadi esatti): sono dichiarate esplicitamente nel codice come scelte di design del porting, pensate per essere facili da ritarare. È invece **confermato dalla fonte** (vedi `world/equipment.py`) che l'arma impugnata usa la skill del proprio tipo (es. `sword`, non genericamente `hand_to_hand`) e che l'armatura indossata del difensore conta davvero in combattimento.

La probabilità di colpire (limitata tra 5 e 95%) parte da una base di 50 e viene modificata da:

| Fattore | Effetto |
|---|---|
| Skill dell'arma impugnata (o `hand_to_hand` a mani nude) | aggiunge il proprio rating |
| Skill Dodge + Classe Armatura del difensore (metà valore) | li sottrae come difesa |
| Bonus temporanei a colpire (`db.bonus_colpire`, es. Benedizione) | si sommano |
| Bonus di gruppo (`+2` per alleato vivo presente nella stanza) | si somma (`world/gruppo.py:bonus_gruppo_colpire` — nessuna formula esatta data dalla fonte) |
| Fame/sete gravi o critiche | malus (confermato dalla fonte: *"seriously weaken your character"* — vedi §6) |
| Cieco | −25 (Incantesimo Accecamento) |
| Sbilanciato (KICK fallito) | −10 |
| Affaticato (lancio interrotto) | −8 |
| Forma di Nebbia (attaccante) | −60 (Vampire Mistform: *"cannot perform any actions that require physical interaction"*, confermato) |
| Forma di Nebbia (difensore) | −40 (*"cannot easily be hurt"*, confermato) |
| Posizione vulnerabile del difensore (REST/SLEEP) | bonus a favore dell'attaccante (confermato dalla fonte, *helps/rest.txt*) |
| Difensore a terra (BASH/TRIP) | +20 (*"increasing their vulnerability to attack"*, confermato, *helps/trip.txt*) |

Tutti i valori numerici sopra (tranne dove segnalato "confermato") sono scelte di design esplicite del porting.

Il danno di un colpo (`calcola_danno`) è: il dado dell'arma impugnata (min-max, o 1-4 a mani nude) + il bonus fisso dell'arma + un bonus da Forza (Forza // 5) + un bonus dalla skill `enhanced_damage` (rating // 25) + eventuali bonus danno temporanei da incantesimo. Il danno finale subito dal difensore è ridotto dalla sua Classe Armatura totale (riduzione = CA // 4, minimo 1 danno comunque inflitto). Colpire e subire un colpo degrada l'equipaggiamento coinvolto (arma dell'attaccante, tutto l'equip del difensore). Un mostro **sensibile alla luna** (`db.sensibile_luna`) riceve un bonus di danno fisso durante la luna piena (vedi §7).

### Second/Third/Fourth Attack

Confermato dalla fonte (*helps/second_attack.txt*): *"These skills enable a character to launch more attacks during each round of combat... automatic skills that do not require any specific special commands... A high rating in the Dexterity attribute also assists in launching additional attacks."* Il porting le implementa come fino a **3 colpi extra nello stesso round**, uno ciascuno per `second_attack`, `third_attack`, `fourth_attack`: dopo il colpo base, per ciascuna di queste skill si tira un `random(1,100)` contro `rating_skill + (Destrezza // 10)` (il divisore 10 è una scelta di design, la fonte non dà un coefficiente esatto); se il tiro fallisce, la catena si interrompe (niente terzo colpo se il secondo non è scattato — scelta di design coerente con l'idea di "attacchi in catena"). Ogni attacco extra riusa la stessa `_esegui_attacco()` del colpo singolo, quindi può anch'esso uccidere il bersaglio.

Semplificazione dichiarata: il controllo e il consumo delle munizioni di un'arma da fuoco restano legati solo al **primo** colpo del round, non ripetuti per ogni attacco extra (la fonte non specifica come i due sistemi debbano interagire).

### Effetti di stato che bloccano l'azione

Riassumendo quanto sopra, gli stati che alterano o impediscono l'azione in combattimento sono:

| Stato | Effetto |
|---|---|
| Addormentato / Paralizzato | perde il turno, non può nemmeno fuggire |
| Impaurito | fuga forzata (come `FLEE`) |
| Allucinato | 40% di probabilità che il colpo devii su un bersaglio a caso nella stanza |
| Sanity critica/erratica | può scatenare azioni erratiche automatiche invece dell'attacco (vedi §5) |
| A terra (da BASH/TRIP) | non può fuggire finché non si rialza; più vulnerabile ai colpi |
| Cieco | forte malus a colpire |
| Forma di Nebbia | fortissimo malus a colpire (attivo) e a subire colpi (passivo) |

## 2. WIMPY e FLEE

### WIMPY

Il comando `wimpy` (`commands/cthulhu.py:CmdWimpy`) imposta la soglia percentuale di HP sotto la quale si tenta automaticamente la fuga. Sintassi e comportamento di default sono confermati verbatim dalla fonte (*helps/wimpy.txt*):

```
wimpy
wimpy <percentuale>
wimpy <percentuale> <direzione>
wimpy off
```

Usato da solo, imposta la soglia al **20%** degli HP massimi (valore di default confermato dalla fonte). Con un valore esplicito la soglia è forzata tra 0 e 99; `wimpy off` la disattiva del tutto. Il controllo (`world/combat.py:_controlla_wimpy`) avviene dopo ogni colpo subito: se la percentuale di HP residui scende sotto la soglia, scatta `tenta_fuga()` nella direzione eventualmente impostata con `WIMPY`. La fonte descrive inoltre alcuni limiti che il porting rispetta: mentre si sta lanciando un incantesimo o eseguendo `TRIP`/`BASH` non si tenta la fuga finché quei comandi non si sono risolti, e da **a terra** non si può fuggire finché non ci si rialza.

Anche i **mostri** possono avere una soglia WIMPY (`db.wimpy_soglia` nel bestiario, vedi §7): equivalente al flag `WIMPY` della fonte (*immhelp_flags.txt*: *"The mob will flee if seriously hurt"*), riusa lo stesso meccanismo dei personaggi giocanti.

Un'azione erratica da bassa sanity può impostare `wimpy_soglia_ignorata_temp`, facendo sì che il personaggio **rifiuti di fuggire** anche sotto soglia per un turno (vedi §5, *"refuse to flee from a fight they are losing"*, confermato dalla fonte).

### FLEE

Il comando `flee [direzione]` (`CmdFlee`) richiede di essere in combattimento. La logica (`world/combat.py:tenta_fuga`) è:

- Se il personaggio è **a terra**, la fuga è impossibile finché non si rialza (confermato dalla fonte, *helps/wimpy.txt*).
- Se non ci sono uscite libere (nessuna, o tutte bloccate da porte chiuse), la fuga fallisce.
- Se è specificata una direzione valida e libera, si tenta quella; altrimenti (nessuna direzione data, direzione non trovata, o bloccata) **si sceglie un'uscita a caso** — confermato dalla fonte (*helps/wimpy.txt*: *"if your character cannot flee in the specified direction for some reason (no exit, closed door, etc.), another direction will be chosen at random"*).
- La fuga ha il **25% di probabilità di fallire** (scelta di design esplicita: la fonte conferma solo che *"An attempt to flee is not always successful"*, senza dare una percentuale — *helps/flee.txt*).
- Una fuga riuscita **ferma il combattimento**, sposta il personaggio nella stanza di destinazione ed esegue automaticamente `look`.
- Costa **5 punti XP fissi** (`XP_PERSA_PER_FUGA`, scelta di design — la fonte conferma solo *"a small loss of experience"*, senza cifra esatta, *helps/flee.txt*) e **danneggia un pezzo di equipaggiamento a caso** tra quelli indossati (confermato in linea di principio dalla fonte: *"a small loss of experience and/or some minor damage to your equipment"*). A differenza della perdita di XP da morte (§3), questa perdita fissa non fa mai retrocedere di livello.

Un mostro con `insegue_chi_fugge` (equivalente ai flag `HUNTER`/`TRACKER` della fonte) può inseguire la vittima nella stanza di destinazione: questo comportamento è stato generalizzato (vedi §7) a **qualunque** uscita dalla stanza, non solo a un `FLEE` esplicito, tramite `typeclasses/rooms.py:at_object_leave` — quindi anche il semplice `move_to()` di una fuga riuscita lo innesca automaticamente, senza bisogno di duplicare la logica dentro `tenta_fuga()`.

## 3. Morte

Quando gli HP di un'entità scendono a 0 o meno, `subisci_danno()` segnala la morte e il chiamante invoca `world/combat.py:gestisci_morte(vittima, uccisore)`. Questa funzione ferma il combattimento di entrambe le parti e poi si dirama: gli NPC hanno un proprio `at_death()`; i personaggi giocanti seguono la procedura descritta sotto (`_morte_personaggio`).

### Morte di un personaggio giocante

Confermato dalla fonte (*helps/death.txt*), alla morte:

- **Nessuna perdita di denaro**: *"You keep all of your money after death"* — confermato, il denaro non finisce mai nel cadavere.
- **Tutti gli effetti magici vengono rimossi immediatamente** (*"all spell affects are instantly removed at the instant of death"* — confermato). "Tutti" va inteso alla lettera, e comprende quattro categorie distinte: gli **stati** attivi (cecità, sonno, paura, paralisi…, cioè le voci di `db.stati`); i **danni periodici** in corso come veleno e peste, che smettono di colpire; i **bonus e malus numerici temporanei** (colpire, danno, classe armatura…), azzerati *insieme ai loro timer di scadenza*, perché altrimenti quei timer sarebbero scattati più tardi rimettendo i valori di prima della morte; e l'**invisibilità magica**, che vive in un campo separato dagli stati e sopravviveva quindi alla morte, facendoti rinascere invisibile. Le ultime due categorie sono state allineate a questa regola durante l'audit precedente al rilascio in beta.
- **Lo status di criminale viene sempre rimosso** (*helps/criminal.txt*: *"Death removes a character's criminal status"* — confermato).
- Se la vittima aveva una **taglia** attiva, chi l'ha uccisa la **incassa** in oro (`world/pk.py:incassa_taglia`).
- Il **cadavere** viene creato con tutto l'inventario e l'equipaggiamento della vittima dentro, e normalmente trasportato nella **stanza MORGUE** della professione della vittima (assegnata in chargen) — confermato dalla fonte come principio generale (*"Your character's corpse is transported to the area's MORGUE room"*), anche se il porting lega la morgue alla *professione* del personaggio piuttosto che all'*area* di morte (scelta di design: la fonte descrive il concetto zona/area, che nel porting non ha un analogo 1:1 già costruito per ogni luogo).
  - **Eccezione `no_morgue`**: se la stanza dove si muore ha `db.no_morgue=True`, il cadavere resta lì invece di essere spostato — confermato dalla fonte (*helps/death.txt*: *"some areas are flagged as no_morgue, which means your character's corpse stays in the room where you died"*, verificabile in gioco con `RAFFECTS`). Nessuna area del mondo attuale ha ancora questo flag impostato: il meccanismo è pronto per quando verrà applicato a qualche zona.
- **Il cadavere di un giocatore è protetto**: solo il proprietario o il suo gruppo può frugarci dentro, confermato dalla fonte (*"Only you or someone from your group can retrieve the objects from your corpse"*) — i cadaveri di **mostri**, invece, restano liberi per chiunque (la fonte parla solo del "tuo" cadavere, quindi non c'è motivo di estendere la protezione ai mostri).
- Il cadavere **decade** dopo circa **15 minuti reali** (confermato dalla fonte: *"Player corpses last approximately 30 game-hours (15 minutes of real time)"*); quando decade, il contenuto cade nella stanza invece di sparire all'istante — anch'esso confermato (*"once your corpse decays, your items will be left in the same room, where they can be picked up by anyone who finds them"*).
- **Perdita di esperienza** legata al livello (vedi sotto).
- **Respawn a piena salute** (HP, mana e movimento ripristinati al massimo) nella RESPAWN room associata al personaggio.

### Perdita di XP alla morte

`world/esperienza.py:perdi_xp_morte()` applica la regola confermata dalla fonte (*helps/death.txt*, *helps/experience.txt*): *"As a low-level character, you will not lose much experience from dying. However, after a certain point, you will lose a set amount of experience from each death, so it is possible to lose a level from dying."* Nel porting: sotto il livello 10 (`SOGLIA_LIVELLO_PERDITA_MORTE`, scelta di design) non si perde nulla; da lì in su si perdono 200 XP fissi (`XP_PERSA_PER_MORTE`, scelta di design), che possono far retrocedere di un livello se l'XP accumulata non basta a coprirli. Soglia e quantità esatte non sono specificate dalla fonte. Uno Yithiano che possiede un NPC morto perde la metà del normale (confermato dalla fonte per gli Yithian, vedi *guides_yithianfaq.txt*).

### PERMAPK

`world/pk.py:permapk_attivo()` legge un toggle globale, attivabile da un Immortale di livello IMPLEMENTOR, confermato dalla fonte (*helps/permapk.txt*): *"This command toggles the permadeath PK mode throughout the entire game. With this option toggled, a player's death will result in the deletion of their character from the database."*

Quando PERMAPK è attiva, la morte di un personaggio giocante **non** segue la procedura normale sopra: niente cadavere, niente respawn — il personaggio viene **cancellato definitivamente dal database** (`vittima.delete()`). Si tratta quindi di una meccanica esplicitamente distruttiva e irreversibile. Il codice segnala questo come una semplificazione dichiarata: *"la fonte non descrive questo caso limite nel dettaglio"* riguardo all'assenza di cadavere/respawn in questa modalità — il principio (cancellazione) è confermato, i dettagli di contorno sono una scelta di design.

## 4. Sistema PK e criminali

CthulhuMUD è dichiaratamente *"a full PK game"* (confermato dalla fonte): il porting non impone alcun divieto tecnico generale al combattimento tra giocatori, coerentemente con questo principio. La legittimità in-character di un dato PK (guerra tra clan, vendetta per un furto, eccetera) resta una questione di moderazione umana da parte dello staff, non qualcosa che il codice possa arbitrare.

### Diventare criminali

Confermato dalla fonte (*helps/criminal.txt*): uccidere un NPC **protetto** (es. un poliziotto) richiede il comando `MURDER` anziché `KILL`; usare `MURDER` per farlo rende automaticamente il personaggio un **criminale** (`world/pk.py:diventa_criminale`). Essere criminali è una distinzione puramente in-character, non contro le regole del MUD: *"there is no rule against being a criminal on CthulhuMUD"* — ma comporta conseguenze meccaniche reali:

- Alcuni NPC (le **guardie**, marcate `db.protetto`) attaccano un criminale a vista (confermato dalla fonte: *"There are some NPCs that will automatically attack a criminal on sight"* — vedi §7 per l'implementazione).
- Altri giocatori possono mettere una **taglia** sulla sua testa.
- La morte rimuove sempre lo status di criminale (vedi §3).

### Taglie (BOUNTY)

Il comando `bounty` (`commands/cthulhu_pk.py:CmdBounty`) implementa la sintassi confermata dalla fonte (*helps/bounty.txt*):

```
bounty
bounty <giocatore> <importo>
bounty bribe
```

- `BOUNTY` da solo mostra la lista delle taglie **in corso su giocatori online** (`world/pk.py:metti_taglia`/lista) — confermato dalla fonte: *"a list of online players who have a bounty on their heads"*.
- `BOUNTY <giocatore> <importo>` mette una taglia in oro su un bersaglio, ma **solo se è già marcato come criminale** (la fonte inquadra la taglia come strumento *"to deal with players who are criminals"*).
- `BOUNTY BRIBE` toglie la taglia dalla propria testa pagando **il doppio** del suo importo (confermato dalla fonte: *"the cost is twice as much as the amount of your bounty"*).
- Chi uccide un criminale con una taglia attiva la **incassa automaticamente** in oro (`world/pk.py:incassa_taglia`).

Gli importi esatti di taglia e ricompensa non sono specificati dalla fonte: sono scelte di design del porting.

### Missioni (MISSION) e i comandi AUTO*

Il sistema di missioni della **Gilda dei Cacciatori di Taglie di Dylath-Leen** (`commands/cthulhu_pk.py:CmdMission`, `CmdDeliver`) implementa `mission request|info|time|complete|abort|points|list|buy` come confermato dalla fonte (*helps/bounty.txt*), con tre tipi casuali: **corriere** (consegna un pacco, tramite `DELIVER <npc>`), **recupero** (ritrova un oggetto rubato) e **caccia** (uccide un NPC criminale generato apposta). Dettagli confermati dalla fonte: `MISSION COMPLETE` richiede di tornare all'Ufficio Taglie **tranne** per le missioni di corriere, dove la consegna stessa dà la ricompensa; un tentativo di richiesta può risolversi in *"nessuna missione disponibile"*, con un'attesa di 5 minuti prima di riprovare; dopo aver completato una missione si attende 30 minuti reali prima della successiva; `MISSION ABORT` costa 5 punti Fama. Importi di ricompensa, durata delle missioni e percentuali di successo non sono specificati dalla fonte (scelte di design). Semplificazione dichiarata: il bersaglio delle missioni di caccia è sempre un NPC criminale generato ad hoc, non un giocatore o un mostro selvatico già presente nel mondo.

I comandi `AUTO*` legati al combattimento/PK, tutti confermati come elenco dalla fonte (*helps/autokill.txt*, elenco `AUTO COMMANDS`), sono implementati in `commands/cthulhu_pk.py` come semplici toggle booleani, consultabili con `AUTOLIST`:

| Comando | Stato nel porting |
|---|---|
| `AUTOGOLD` | tracciato e mostrato in `AUTOLIST`, ma **non ha ancora effetto**: il porting non fa mai cadere oro dall'uccisione di un mostro (semplificazione dichiarata) |
| `AUTOLOOT` | tracciato ma **non ha ancora effetto**: gli NPC non mettono equipaggiamento nel proprio cadavere (nessun sistema di bottino da mostri) |
| `AUTOKILL` | tracciato ma **non ha ancora effetto sull'esito**: il porting non ha mai avuto una risoluzione "stordisci senza uccidere" — 0 HP significa sempre morte reale, scelta di design fin dalle prime fasi del combattimento |
| `NOLOOT` | **pienamente funzionale**: il cadavere è già protetto di default (solo proprietario/gruppo), `NOLOOT` attivo esclude anche il proprio gruppo |
| `AUTOSAC` | il **toggle** esiste ed è tracciato, ma la funzionalità **non è implementata**: dipende da un intero sistema WORSHIP/divinità/pietà che questo porting non ha mai costruito — dichiaratamente fuori scope |
| `AUTOASSIST` | pienamente funzionale (vedi §1) |
| `AUTOSPLIT` | tracciato in `AUTOLIST` (dettaglio distributivo tra gruppo non approfondito in questo capitolo) |

## 5. Sanità mentale

La sanity ha conseguenze meccaniche reali, confermate dalla scansione esaustiva della fonte (*helps/sanity.txt*, *helps/therapy.txt*, *helps/psychology.txt*) — non un semplice stat cosmetico:

> *"As your character's sanity erodes, they will begin to act strangely. They will perform random actions without your commands. They may randomly attack an NPC for no reason, or randomly flee from a fight they are winning. Conversely, they may refuse to flee from a fight they are losing. They may grumble, mutter, laugh, cry, or simply wander around."*

### Come si perde sanity

`world/sanita.py:perdi_sanita()` viene chiamata quando un personaggio ingaggia un mostro con `db.orrore` impostato (`typeclasses/living.py:avvia_combattimento`). La quantità persa è attutita da una **resistenza per tipo di orrore** (`db.resistenze_paura`, un dizionario), che cresce leggermente a ogni esposizione (assuefazione) — confermato dalla fonte: *"as your character is exposed to certain horrors, they eventually build up a resistance to that particular type of fear"*, visibile in gioco con `EXPERIENCE`. I tipi di orrore usati (`db.tipo_orrore` nel bestiario, vedi §7) sono: `non_morti`, `profondi`, `esterni`, `antichi`, `onirici`, o `sconosciuto` come ripiego. L'incantesimo **Relax** (`db.stati["rilassato"]`) dimezza ulteriormente la perdita per la sua durata.

La fonte conferma anche altre fonti di variazione della sanity, tutte agganciate nel porting:

- **Allenare Intelligenza** la riduce; **allenare Saggezza** la aumenta (confermato: *"Training your Intelligence decreases your sanity, while training your Wisdom increases it"*).
- **Salire di livello** la aumenta (confermato: *"Gaining a level increases your sanity"* — `world/esperienza.py:sale_di_livello` chiama `bonus_sanita_livello`).
- **Lanciare certi incantesimi** la riduce (confermato in linea di principio: *"casting certain spells decreases it"*) — la lista esatta delle famiglie di magia "proibita" che la riducono (Negromanzia, Magia degli Antichi, Magia del Caos, Via dell'Evocatore, Voodoo, Magia Divina) non è data dalla fonte ed è una scelta di design del porting.

Le soglie esatte, l'entità della perdita per ogni orrore e i costi/percentuali di THERAPY/PSYCHOLOGY **non sono specificati dalla fonte**: sono scelte di design esplicite.

### Soglie critiche e azioni erratiche

Sotto **30 punti sanity** (`SOGLIA_ERRATICO`, scelta di design) scatta un rischio di azione erratica del 7% per round di combattimento; sotto **10** (`SOGLIA_GRAVE`) il rischio raddoppia al 15%. Quando scatta, l'azione erratica **sostituisce** l'attacco normale del round. Le azioni possibili (`world/sanita.py:applica_azione_erratica`), tutte elencate testualmente dalla fonte:

| Azione | Effetto |
|---|---|
| `borbotta` | messaggio ambientale, nessun effetto meccanico |
| `ride` | messaggio ambientale (aggiunto in un audit successivo per allinearsi alla fonte, che cita esplicitamente "laugh") |
| `piange` | messaggio ambientale |
| `vaga` | il personaggio si sposta in un'uscita a caso della stanza |
| `attacca_a_caso` | attacca un bersaglio vivo a caso nella stanza (anche un innocente) |
| `fugge` | tenta una fuga forzata, anche se il personaggio sta vincendo lo scontro |
| `non_fugge` | rifiuta di fuggire per un turno anche se la soglia WIMPY sarebbe superata |

Sotto la soglia grave (≤10), il personaggio riceve anche un avviso testuale (*"La tua mente vacilla sull'orlo del baratro"*).

### Recupero: THERAPY e PSYCHOLOGY

**THERAPY** (`world/sanita.py:esegui_therapy`): a pagamento presso un NPC terapeuta, con tre trattamenti (base/intensiva/completa, costi e recuperi crescenti) — confermato dalla fonte che esistono più trattamenti a pagamento e che il risultato **non è garantito** (*"the therapist will not give you a refund if it fails"*); nel porting c'è un 20% di probabilità che la seduta non sortisca alcun effetto (scelta di design, percentuale non data dalla fonte). Nomi dei trattamenti, costi esatti e quantità di recupero sono scelte di design.

**PSYCHOLOGY** (`world/sanita.py:esegui_psychology`): skill gratuita ma che costa **300 punti movimento** e richiede circa **30 secondi** per risolversi (entrambi confermati dalla fonte: *"Each psychology session costs 300 movement points, and it takes approximately 30 seconds to complete"*). L'esito dipende dal rating della skill (o di `self_discipline`) e dal divario di sanity tra curatore e bersaglio; un fallimento può **ritorcersi contro il curatore**, facendogli perdere sanity (confermato: *"a failed attempt could even damage the sanity of the player"*). La fonte non descrive un'interruzione della seduta (a differenza del lancio di incantesimi): il porting non ne inventa una analoga non documentata.

## 6. Fame e sete

Confermato dalla fonte (*helps/eat.txt*): *"hunger and/or thirst can seriously weaken your character, eventually leading to death"* — non un semplice consiglio di buon senso, ma una meccanica reale con conseguenze concrete. I nomi degli attributi nel porting sono **appetito** e **sete** (0 = sazio/idratato, 100 = morente); il termine "fame" non è stato riusato perché già occupato da `Character.db.fame` (i punti Fama/reputazione, concetto distinto nell'originale).

### Soglie

| Soglia | Valore | Effetto |
|---|---|---|
| Avviso | 50 | solo un messaggio ("hai fame"/"hai sete"), nessuna penalità |
| Penalità | 80 | malus meccanico a colpire |
| Critica | 100 | danno periodico |

Le soglie esatte, la velocità di aumento e l'entità della penalità/danno **non sono specificate dalla fonte**: sono scelte di design esplicite, facili da ritarare.

### Conseguenze meccaniche

- **Malus a colpire**: +15 di penalità a `calcola_hit_chance` per ciascuno tra appetito e sete che sia in stato "grave" o "critico" (fino a −30 cumulativo se entrambi sono critici) — confermato in linea di principio dalla fonte (*"seriously weaken your character"*).
- **Danno periodico**: oltre soglia critica, 3 danni per tick per ciascuno tra fame e sete (fino a 6 cumulativo), applicati come danno non fisico — può portare fino alla morte, confermato dalla fonte (*"eventually leading to death"*).
- L'incantesimo **Ascetismo** sospende del tutto il bisogno di cibo/acqua per la sua durata.

### Comandi EAT/DRINK/FEED/FEEDME

Sintassi confermata verbatim dalla fonte (*helps/eat.txt*): `DRINK <object> / EAT <object> / FEED <character> <object>`.

- `eat`/`mangia <oggetto>` (`CmdEat`): consuma un oggetto con valore nutritivo (`db.cibo`), riducendo l'appetito; funziona anche su oggetti con `db.mana_ripristino` (pillole di mana).
- `drink`/`bevi <oggetto>` (`CmdDrink`): consuma un oggetto con valore idratante (`db.bevanda`), riducendo la sete; se l'oggetto è stato benedetto, applica anche il beneficio di Benedizione (o infligge danno a chi beve se non-morto).
- Entrambi si **rifiutano durante il combattimento**, confermato dalla fonte: *"You can eat and drink while debating and casting spells, but not during combat"*.
- `feed`/`nutri <personaggio> <oggetto>` (`CmdFeed`): nutre forzatamente un altro personaggio, ma solo se questo ha attivato la ricezione forzata — confermato dalla fonte (*"assuming that character has that option toggled"*, senza descrivere l'opzione). Nel porting l'opzione si attiva con `feedme`/`accettafeed` (`CmdFeedMe`), un semplice interruttore personale: nome e comando esatti sono una scelta di design, dato che la fonte non li specifica.

## 7. Il bestiario e l'IA dei mostri

### Origine del bestiario

Il sito originale **non ha mai pubblicato** un bestiario o delle schede mostri (normale: un sito non svela le statistiche dei propri nemici). Le uniche creature del Mythos citate nell'intero corpus compaiono di striscio dentro descrizioni di incantesimi (es. *Curse of the Hunter* evoca una "Hunting Horror"). Il bestiario di `world/mostri.py` è quindi dichiaratamente **costruito di sana pianta** dal team di porting, su richiesta esplicita dell'utente, nello spirito dell'ambientazione lovecraftiana e calibrato sulle meccaniche già esistenti (livello, skill, allineamento, orrore) — ogni voce è una scelta di design originale, non una trascrizione dalla fonte.

### Il bestiario (BESTIARIO in world/mostri.py)

| Chiave | Nome | Livello | HP max | Allineamento | Orrore | Tipo orrore | Comportamenti |
|---|---|---|---|---|---|---|---|
| `ghoul` | un ghoul | 8 | 79 | −400 | 8 | non_morti | attacca a vista, non-morto |
| `cultista` | un cultista incappucciato | 5 | 55 | −600 | 4 | occulto | passivo (reagisce solo se attaccato) |
| `ibrido_profondo` | un ibrido dei Profondi | 10 | 95 | −300 | 6 | profondi | wimpy 25% |
| `mummia_custode` | una mummia custode | 12 | 111 | −200 | 9 | non_morti | attacca a vista, non-morto, sentinella (non vaga) |
| `sciacallo_mutato` | uno sciacallo mutato | 6 | 63 | −100 | 3 | sconosciuto | attacca a vista, wimpy 25% |
| `cane_di_tindalos` | un cane di Tindalos | 20 | 175 | −800 | 18 | esterni | attacca a vista, insegue chi fugge |
| `byakhee` | un byakhee | 15 | 135 | −500 | 12 | esterni | attacca a vista |
| `shoggoth_minore` | un piccolo shoggoth | 25 | 223 | −700 | 20 | antichi | attacca a vista, sentinella |
| `gug` | un gug | 18 | 159 | −450 | 14 | onirici | attacca a vista |
| `bestia_lunare` | una bestia lunare | 16 | 143 | −550 | 13 | onirici | passivo, sensibile alla luna piena |
| `cacciatore_notturno` | un cacciatore notturno | 14 | 127 | −350 | 15 | onirici | attacca a vista, insegue chi fugge |
| `marinaio_annegato` | un marinaio annegato | 7 | 71 | −250 | 7 | non_morti | attacca a vista |

Ogni voce include anche una descrizione testuale, un set di skill di combattimento e alcune frasi ambientali (vedi sotto). Nessuna delle voci sopra ha `sentinella=True` insieme ad `attacca_a_vista=False`, tranne dove indicato in tabella.

### Aggro a vista

Un mostro con `attacca_a_vista=True` attacca automaticamente un personaggio che entra nella sua stanza, ma solo se il **livello effettivo** del personaggio non supera il livello del mostro di oltre un margine (`MARGINE_AGGRESSIONE = 5`, scelta di design): questo traduce il flag `AGGRESSIVE` della fonte (*immhelp_flags.txt*: *"The mob will attack everyone who's not very superior in level"*) — un personaggio molto più forte del mostro non viene aggredito. La logica è centralizzata in `world/mostri.py:tenta_aggro()`, riusata sia quando è il **personaggio** a entrare nella stanza (`typeclasses/rooms.py:at_object_receive`) sia quando è il **mostro** a vagare in una stanza già occupata (`world/mostri_movimento.py`) — un bug reale trovato in audit: `move_to()` non passa da `at_object_receive` lato NPC, quindi prima di questa correzione un mostro aggressivo che vagava in una stanza con giocatori fermi non li attaccava mai.

### Guardie contro i criminali

La stessa funzione `tenta_aggro()` gestisce anche il caso guardia: un NPC marcato `db.protetto` attacca a vista un personaggio marcato `db.criminale`, indipendentemente dal proprio flag `attacca_a_vista` — confermato dalla fonte (*helps/criminal.txt*: *"There are some NPCs that will automatically attack a criminal on sight"*).

### Assist tra mostri

`world/mostri.py:tenta_assist()` implementa il flag `ASSIST-ALL` della fonte (*immhelp_flags.txt*: *"The mob assists all mobs against players"*): quando un mostro del bestiario viene attaccato, ogni altro mostro ostile nella stessa stanza, non già impegnato, si unisce contro lo stesso aggressore. Scelta di scope dichiarata: la fonte distingue anche `ASSIST-ALIGN`/`ASSIST-RACE`/`ASSIST-GUARD` (assistenza ristretta per allineamento/razza/gruppo di guardia) — **non implementate separatamente**, perché `ASSIST-ALL` (la più ampia) copre già il caso di gameplay più visibile. Per evitare cascate mostro-contro-mostro (es. un famiglio addomesticato che attacca un mostro ostile, innescando un assist che richiama ricorsivamente altro assist), la funzione si attiva solo se l'aggressore **non** è a sua volta un mostro del bestiario.

### Movimento e pattugliamento

`world/mostri_movimento.py` implementa un'IA di vagabondaggio ispirata al flag `SENTINEL` della fonte (*immhelp_flags.txt*: *"doesn't do random movement"*) e al meccanismo di innesco documentato per i mob generici (*immhelp_conditions.txt*: una condizione valutata a ogni tick periodico — non un vero pathfinding). Un mostro **non** marcato `sentinella` ha, a ogni tick (30 secondi reali, scelta di design), una probabilità del 25% (scelta di design) di spostarsi in un'uscita a caso; se non si sposta, ha invece una probabilità del 15% di recitare una battuta ambientale presa da `db.frasi_ambiente` — l'equivalente in spirito del comando `MPECHO` della fonte (*immhelp_mobcommands.txt*: *"issues the text string as an echo event"*), qui semplice testo invece di un vero motore di scripting generico (scelta di design condivisa: niente VM MOBprogram-like, dato che non esistono altri builder che scriverebbero contenuti in un linguaggio dedicato). Un mostro **sentinella** (es. la mummia custode, il piccolo shoggoth) non vaga mai, riservato ai guardiani di un luogo preciso.

Il vagabondare è vincolato all'**area** di origine del mostro: le uscite candidate sono ristrette alle sole stanze che condividono una categoria di tag con la zona del mostro (`world/popola_mostri.py:ZONA_CATEGORIE`) — equivalente al flag `STAY-AREA` della fonte (*"The mob will not leave its area"*).

### Hunter/Tracker

Un mostro con `insegue_chi_fugge=True` (es. il cane di Tindalos, il cacciatore notturno) è l'equivalente dei flag `HUNTER`/`TRACKER` della fonte (*immhelp_flags.txt*: *"Basic mob memory. The mob remembers who attacked it"* / *"A hunter who tracks his enemy"*). Punto importante: questo comportamento è stato **generalizzato** a qualunque uscita della vittima dalla stanza, non solo alla fuga esplicita con `FLEE` — implementato tramite `typeclasses/rooms.py:at_object_leave`, che chiama `world/mostri.py:tenta_inseguimento()` per ogni personaggio che lascia una stanza. Prima di questa generalizzazione, un giocatore poteva seminare un predatore semplicemente camminando via normalmente (senza `FLEE`), dato che la logica viveva solo dentro `tenta_fuga()`: un gap reale trovato in audit. L'inseguimento resta comunque **"a un salto per volta"** (il mostro si sposta nella stanza di destinazione e basta): **non** implementa le varianti più estreme `TELETRACKER`/`TELEHUNTER` della fonte (mostri che inseguono teletrasportandosi), scelta di scope proporzionata dato l'impatto già alto della sola estensione multi-stanza.

### Bonus danno per luna piena

Un mostro con `sensibile_luna=True` (nel bestiario attuale, solo la bestia lunare) riceve un bonus di danno fisso (`BONUS_DANNO_LUNA_PIENA = 4`, scelta di design) quando è luna piena (`world/sottorazze.py:luna_piena()`). Il concetto di fase lunare come condizione di mondo è confermato dalla fonte (*immhelp_conditions.txt*), ma applicarlo ai mostri (anziché solo alle sottorazze Were giocanti, dove era già cablato) è una scelta di design del porting, motivata dal fatto che il bestiario include già creature esplicitamente legate alla luna.

### Comportamenti della fonte NON implementati

Il codice dichiara esplicitamente fuori scope, per questo bestiario, le seguenti varianti descritte da *immhelp_flags.txt*:

| Flag della fonte | Perché non implementato |
|---|---|
| `ASSIST-ALIGN` / `ASSIST-RACE` / `ASSIST-GUARD` | `ASSIST-ALL` (più ampio) copre già il caso di gameplay più visibile |
| `NIGHT_ACTIVE` (il mob scompare di giorno) | non implementato in questo bestiario |
| `SCAVENGER` (il mob raccoglie oggetti a terra) | non implementato |
| `STAY-SUBAREA` | implementato solo a livello di area (`STAY-AREA`), non di sotto-area |
| `SOCIAL` (i mob tendono a raggrupparsi con i propri simili, comportamento da branco) | non implementato |
| `HUNTER`/`TRACKER` con teletrasporto (`TELETRACKER`/`TELEHUNTER`) | l'inseguimento implementato resta "a un salto per volta"; le varianti con teletrasporto sono dichiaratamente fuori scope |

## Riepilogo delle scelte di design principali di questo capitolo

Per chiarezza, le principali cifre e meccaniche **non** confermate dalla fonte originale e quindi scelte di design esplicite del porting:

- Le formule esatte di hit chance e danno (struttura generale e tutti i coefficienti numerici).
- Il divisore Destrezza→attacchi extra (10) per Second/Third/Fourth Attack.
- La percentuale di fallimento di FLEE (25%) e il costo fisso in XP (5).
- Le soglie di sanity per le azioni erratiche (30/10) e le relative probabilità (7%/15%).
- Le soglie di fame/sete (50/80/100) e l'entità di malus/danno.
- Costi e percentuali di THERAPY (trattamenti, tassi di fallimento).
- Le soglie e importi di perdita XP alla morte (livello 10, 200 XP).
- Importi di taglie/ricompense missione e percentuali/tempistiche del sistema missioni.
- L'intero bestiario (creature, statistiche, skill assegnate) e i parametri della sua IA (margine di aggressione, probabilità/frequenza di movimento e battute ambientali, bonus danno da luna piena).
