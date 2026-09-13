# Comunicazione, Fede e Poteri Speciali

## Canali di comunicazione OOC

Tutte le comunicazioni descritte in questa sezione sono **fuori personaggio** (OOC, *Out-Of-Character*): la fonte originale (*helps/ooc.txt*) è esplicita sul punto — i messaggi mandati con questi comandi vanno intesi come se provenissero "da qualcuno seduto al computer", non dal personaggio nel mondo di gioco.

La tabella seguente elenca tutti i canali confermati dalla fonte, con la relativa scorciatoia e chi vi ha accesso:

| Canale | Scorciatoia | Chi può usarlo | Note |
|---|---|---|---|
| `GOSSIP` | `.` | Tutti | Il canale OOC primario del gioco. |
| `INVESTIGATORTALK` | `-` | Dal 51º livello in su | |
| `HERO` | `+` | Dal 101º livello in su | |
| `REMTALK` | `&` | Solo chi ha completato almeno un remort | |
| `IMMTALK` | — | Solo Immortali/staff | Nel porting: permesso `Builder` o superiore. |
| `QUESTION` / `ANSWER` | — | Tutti | Sono lo **stesso canale**, con due nomi diversi per lo stesso scopo (fare/rispondere a domande sul gioco). |
| `MUSIC` | — | Tutti | Per chi vuole cantare/suonare in OOC. |
| `CHAT` | — | Tutti, incluse le sessioni non ancora autenticate | Confermato dalla fonte come pensato per rispondere "alle domande di curiosi che stanno dando un'occhiata al gioco" prima ancora del login. |

Tutti questi canali (tranne CHAT) sono confermati verbatim dalla fonte, soglie di livello incluse. Nel porting, ogni canale ha un **comando dedicato** (`gossip`, `investigatortalk`, `hero`, ecc. — `/data/claude/CthulhuMud/game/commands/cthulhu_canali.py`) invece di appoggiarsi al sistema generico di alias di canale di Evennia: questo garantisce che la sintassi esatta della fonte funzioni da subito, senza bisogno di configurazione manuale da parte del giocatore.

**Alias GOSSIP/OOC non replicato**: la fonte permette di scrivere su GOSSIP anche con il comando `OOC <messaggio>`. Nel porting questo alias è stato deliberatamente **omesso**: `ooc` è già il comando che serve per uscire dal personaggio (`commands/cthulhu_account.py`), un uso più fondamentale che non si voleva rompere.

**Social ed emote sui canali OOC (non riportato nel porting)**: la fonte specifica che GOSSIP, INVESTIGATORTALK, HERO e REMTALK permettono di usare social ed emote direttamente sul canale, anteponendo un cancelletto (`#<social>`) o una virgola (`,<emote>`) al testo (*helps/ooc.txt*, *helps/socials.txt*: "`GOSSIP #<social>`", "`HERO #<social>`"...). Questa scorciatoia non è stata implementata nei comandi-canale del porting, che inoltrano sempre il testo grezzo al canale: i social restano quindi utilizzabili solo con il proprio comando dedicato (vedi sezione successiva), non con il prefisso `#` sui canali OOC.

Il comando `@channel` (alias `@chan`, `@channels`) resta disponibile per la gestione avanzata: alias personali, mute/unmute, cronologia, creazione di canali extra, amministrazione (ban/boot). `channels` (alias `canali`) mostra lo stato delle proprie iscrizioni.

### QUIET, REPLY, IGNORE

- **`QUIET`**: silenzia **tutti** i canali OOC a cui si è iscritti in un solo colpo (equivalente a un `mute` di massa). Confermato dalla fonte: "the QUIET command will silence all of your OOC channels".
- **`REPLY <messaggio>`**: risponde automaticamente all'ultima persona che ha inviato un `TELL`/`PAGE` al personaggio, anche senza conoscerne il nome. Confermato dalla fonte. Nel porting riusa la logica già esistente di `PAGE` (vedi sotto) invece di duplicarla.
- **`IGNORE <nome>`** / **`IGNORE <nome> CLEAR`**: blocca i `TELL`/`PAGE` provenienti da un account; l'opzione `CLEAR` rimuove il blocco in seguito. Confermato dalla fonte. Nel porting la lista di ignorati vive sull'**account** (non sul personaggio), perché il sistema PAGE/TELL comunica tra account, non tra personaggi — un giocatore che ignora un altro lo ignora a prescindere da quale personaggio quest'ultimo stia interpretando.

## Comunicazione privata: PAGE/TELL

Il comando `page` (alias `tell`) invia un messaggio privato a un altro account, ovunque si trovi nel mondo:

```
page <account> <messaggio>
page <account>,<account>,... = <messaggio>
tell <account> <messaggio>
page <numero>
page/last
```

Caratteristiche del porting (`/data/claude/CthulhuMud/game/commands/cthulhu_comms.py`):

- **Cronologia**: senza argomenti, `page` mostra la cronologia degli ultimi messaggi inviati e ricevuti, con formattazione differenziata per i messaggi in uscita (`>`) e in entrata (`<`); un numero come argomento (`page 20`) limita la cronologia mostrata alle ultime N voci.
- **`page/last`**: mostra a chi si è scritto per ultimo.
- **Invio multiplo**: è possibile indicare più destinatari separati da virgola prima del segno `=` (`page Mario,Luigi = messaggio`).
- **Notifica di destinatario offline**: se il destinatario non ha sessioni connesse, il mittente viene avvisato che il messaggio verrà visto solo quando l'altro tornerà a controllare i propri messaggi ricevuti — il messaggio resta comunque salvato e recuperabile dalla cronologia.
- **Rispetto di IGNORE**: se il destinatario ha messo il mittente nella propria lista IGNORE, il messaggio non viene recapitato e il mittente ne viene informato.

## I Social

Un **social** (detto anche *emote sociale*) è un comando che produce un messaggio predefinito e ambientato, che descrive un'azione o un'espressione del personaggio (es. sorridere, salutare, applaudire, insultare): non modifica nessuna statistica, non ha effetti meccanici, serve solo per il roleplay e l'interazione sociale visibile a chi si trova nella stessa stanza.

**Numero totale**: il porting implementa **204 social** (`/data/claude/CthulhuMud/game/world/socials.py`), a fronte dei **203 "ufficiali"** elencati nell'indice della fonte (*info_socials.txt*). Il social in più deriva da due voci (`HIGHFIVE` e `SLOBBER`) che esistono come pagine reali nel corpus scaricato ma non risultano nel conteggio dell'indice originale: sono state incluse comunque. Manca invece `TWEAK`, presente nell'indice della fonte ma assente dal corpus effettivamente scansionato — un buco della scansione disponibile, non un'omissione del porting.

Ogni social può avere fino a tre forme d'uso, ciascuna con il proprio messaggio per l'attore e per gli osservatori (e, quando applicabile, per il bersaglio):

- **senza bersaglio** (es. `SMILE` da solo);
- **su se stessi** (es. `SMILE` rivolto al proprio personaggio);
- **su un bersaglio** (es. `SMILE <personaggio>`).

Non tutti i social supportano tutte e tre le forme (alcune azioni, come singhiozzare, non hanno senso dirette a un'altra persona).

I 204 social sono divisi in **quattro categorie**, in linea con la fonte:

| Categoria | Social nel porting |
|---|---|
| Neutro | 115 |
| Amichevole | 47 |
| Ostile | 23 |
| Sessuale | 19 |

**Il flag `vietato_newbie`**: la fonte è esplicita sulla categoria "sessuale" — pur restando un registro allusivo e mai esplicitamente osceno ("*Sexual socials do not include any graphic or explicitly obscene content*"), il loro uso è "leggermente ristretto in quanto i newbie non possono usarli" (*"their use is slightly restricted in that newbies cannot use them"*, info_socials.txt). Nel porting questo si traduce nel flag `vietato_newbie` su ogni voce della categoria sessuale, controllato a runtime contro la professione attiva del personaggio (`world.professions_newbie.NEWBIE_PROFESSIONS`): un personaggio con una professione newbie attiva riceve un rifiuto se prova a usare uno di questi social. In totale 20 social portano questo flag: i 19 della categoria sessuale più `KISS`, che nella fonte è classificato esplicitamente tra i "Sexual Socials" nonostante nella prima bozza del porting fosse stato erroneamente trattato come social libero/amichevole (poi corretto).

**Come scoprire i social in gioco**: questo Codex non elenca i 204 nomi uno per uno (un elenco nominale sarebbe eccessivo e poco utile su carta). Il modo previsto per esplorarli è direttamente in gioco: digitando `help <nome del social>` (es. `help smile`, `help bow`, `help slobber`) si ottiene una risposta nella forma "*emote sociale: `<nome>`*" con la sintassi d'uso, dato che ogni comando-social genera il proprio help automaticamente a partire dalla sua voce in `world/socials.py`. Non esiste (ancora) un comando `SOCIALS` che ne stampi l'elenco completo a schermo, a differenza della fonte originale.

### CmdGender

Poiché i messaggi dei social usano pronomi di terza persona che dipendono dal genere del personaggio (es. "si guarda allo specchio" contro "guarda se stessa"), il comando `gender` (alias `genere`) imposta il genere usato in questi messaggi:

```
gender m
gender f
```

Il valore è salvato su `Character.db.genere` (default `"m"`) e viene letto da ogni social al momento di comporre i messaggi in terza persona.

## WORSHIP e SACRIFICE

Il sistema di fede è confermato dalla fonte come un'unica pagina di aiuto condivisa da tre nomi diversi (*helps/sacrifice.txt*, *helps/worship.txt*, *helps/piety.txt* sono, verbatim, la stessa pagina "SACRIFICE / WORSHIP").

### Le sette divinità

Il porting adotta un roster di **sette divinità** (`/data/claude/CthulhuMud/game/world/worship.py:DIVINITA`):

| Divinità | Allineamento | Descrizione |
|---|---|---|
| Marduk | +700 | Il Dio guerriero che uccise Tiamat: eroe dei Guerrieri della Luce, attende il risveglio di Grande Cthulhu. |
| Bast | +400 | La Dea gattesca dell'Antico Egitto, protettrice silenziosa di chi cammina nell'ombra con grazia e astuzia. |
| Foxbird | 0 | Il Dio della Magia, patrono di chi cerca la conoscenza arcana per se stessa, senza fedeltà a bene o male. |
| Thanatos | 0 | Il custode del ciclo naturale di vita e morte: non premia né punisce chi vive e muore secondo natura. |
| Yog-Sothoth | -600 | Colui-che-è-la-Porta: onnisciente e alieno, la sua conoscenza proibita corrompe chi la insegue troppo a lungo. |
| Dagon | -700 | Il Dio dei Profondi, venerato a Innsmouth: promette potere a chi accetta di mescolare il proprio sangue col mare. |
| Shub-Niggurath | -800 | La Capra Nera dei Boschi dai Mille Cuccioli: fertilità mostruosa e proliferazione senza fine, indifferente all'ordine. |

**Scelta di design dichiarata**: la fonte non specifica un elenco fisso di divinità attive — dice solo di usare `WIZLIST` per vederle, un elenco *dinamico* legato a quali membri dello staff impersonano attivamente un dio nel gioco originale (un concetto non riproducibile in un porting su scala ridotta). Il roster sopra riutilizza semplicemente le professioni sacerdotali "priest_of_*" già esistenti nel porting (`world/professions_avanzate.py`), senza inventarne di nuove; gli allineamenti numerici sono stati assegnati per coerenza tematica col Mythos e con le descrizioni di professione già presenti (es. Marduk è esplicitamente l'eroe anti-Cthulhu dei "Guerrieri della Luce" in `world/societies.py`).

### Scegliere una divinità: WORSHIP

```
worship                    → elenca le divinità disponibili con il loro allineamento
worship <divinità>         → cambia fede
worship info <divinità>    → mostra la descrizione estesa e il mana attuale della divinità
```

Cambiare divinità azzera la pietà accumulata con la precedente: la fonte non specifica questo comportamento in modo esplicito, ma è la lettura più coerente col fatto che la pietà è definita come fedeltà alla divinità *attuale* — quindi è una **scelta di design** dichiarata nel codice, non un dato certo della fonte.

### Pietà

La pietà è una misura di quanto un personaggio sia stato fedele e generoso verso la propria divinità. Cresce **solo** sacrificando oggetti di valore con `SACRIFICE` (non con `AUTOSAC`, vedi sotto), e la fonte avverte esplicitamente che cresce lentamente: "*it takes some time and patience to raise your piety, so do not get discouraged by slow progress*" — nessuna cifra esatta è data dalla fonte. Divinità e pietà correnti compaiono su `SCORE`, confermato dalla fonte.

### SACRIFICE

```
sacrifice <oggetto>
sacrifice all
```

`SACRIFICE` offre un oggetto alla divinità attualmente adorata, che *può* (non deve) ricompensare l'offerta. A differenza di `OFFER`, non richiede la presenza di un altare o di un idolo fisico — dettaglio confermato dalla fonte. `SACRIFICE ALL` sacrifica tutto ciò che il personaggio porta con sé.

Meccanica di ricompensa (parametri non specificati numericamente dalla fonte, quindi scelte di design dichiarate nel codice):

- l'oggetto deve avere un valore almeno pari a **30** (`SOGLIA_RICOMPENSA_VALORE`);
- l'allineamento del personaggio deve essere nella stessa direzione (segno) di quello della divinità;
- se entrambe le condizioni sono soddisfatte, c'è una probabilità del **15%** di ricevere una ricompensa in oro, pari a un valore casuale tra metà e l'intero valore dell'oggetto sacrificato.

### Il mana delle divinità

Ogni sacrificio (anche automatico, tramite AUTOSAC) alimenta un "pool di mana" globale per la divinità coinvolta, confermato dalla fonte ("*the mana pool of active deities increases with regular sacrifices*"). Nel porting questo mana è un contatore persistente per divinità (salvato via `ServerConfig`), che cresce di una quantità casuale tra 1 e 5 a ogni sacrificio, e viene mostrato da `worship info <divinità>`.

### AUTOSAC

Il toggle `AUTOSAC` (già tracciato in `world/pk.py`/`commands/cthulhu_pk.py`) fa sì che il personaggio sacrifichi automaticamente il cadavere di ogni NPC ucciso. Confermato dalla fonte: **i sacrifici automatici non contribuiscono alla pietà**, ma alimentano comunque il mana della divinità.

### Cosa è dichiarato fuori scope

Il codice dichiara esplicitamente **non implementati** in questo porting:

- **`OFFER`/`PRAY`**: richiederebbero altari o idoli fisici piazzati nel mondo per ogni divinità, il tracciamento di "imprese" (deed) legate a offerte specifiche per le professioni sacerdotali, e soprattutto la meccanica per cui "*an active God or Goddess will [occasionally] make a personal response to a prayer*" — nella fonte, questo presuppone letteralmente un membro dello staff che impersona quella divinità e risponde a mano. Costruire un sostituto automatico credibile per questa parte è considerato un sistema a sé, non una semplice estensione di WORSHIP/SACRIFICE.

## Yithian e Mindtransfer

Gli **Yithiani** (Great Race of Yith) sono, secondo la fonte (*guides_yithianfaq.txt*, *helps/yithian.txt*), una razza aliena avanzata che ha imparato a viaggiare nel tempo e nello spazio scambiando le proprie menti con quelle di altre creature, per raccogliere conoscenza da immagazzinare nella Grande Biblioteca. Fisicamente sono corpi conici con quattro tentacoli (due artigliati, uno a forma di tromba, uno con un organo sensoriale a sfera) — e sono, per esplicita ammissione della fonte, "*la razza più difficile da giocare su CthulhuMUD*", sconsigliata ai principianti.

Fisicamente deboli, gli Yithiani passano la maggior parte del tempo a possedere corpi di NPC invece di esplorare nel proprio corpo. Il porting implementa questo sottosistema in `/data/claude/CthulhuMud/game/commands/cthulhu_yithian.py` e `world/yithian.py`.

### MINDTRANSFER

```
mindtransfer <npc>
```

Trasferisce la mente del personaggio Yithiano in un corpo NPC bersaglio. Confermato dalla fonte:

- **Costo**: mana **e** movimento, entrambi pari a **10 volte il livello dell'NPC**.
- È molto difficile, quasi impossibile, possedere un NPC di livello superiore al proprio.
- Se il tentativo fallisce contro un NPC più forte, l'NPC si risveglia ostile e attacca.
- Mentre si possiede un NPC, il corpo Yithiano originale resta immobile e privo di qualunque informazione sensoriale nella stanza dove si trovava — chiunque potrebbe rubargli l'equipaggiamento, parlargli senza risposta, o persino ucciderlo, e lo Yithiano non lo saprebbe fino al ritorno.
- L'esperienza da uccisione, mentre si possiede un NPC, si divide a metà tra il corpo Yithiano e il corpo posseduto: entrambi salgono di livello, ma più lentamente.

La formula esatta di successo (`possibilita_successo_mindtransfer`, in funzione del divario di livello) non è specificata numericamente dalla fonte, che parla solo di "molto difficile, se non impossibile": è quindi una scelta di design del porting.

### RETURN

```
return
```

Riporta la mente al corpo Yithiano originale in qualunque momento. Nel porting, lo stesso comando è stato esteso (senza crearne uno nuovo in conflitto) a gestire anche il ritorno dal Cammino Astrale (*helps/astral_walk.txt* conferma che si usa `RETURN` per tornare al proprio corpo fisico) e il ritorno dello staff dopo un `SWITCH` (*helps/switch.txt*).

### Se il corpo posseduto muore

Confermato dalla fonte:

- la mente torna automaticamente al corpo Yithiano;
- la perdita di esperienza alla morte è **minore** di quella normale (nel porting: dimezzata, `PENALITA_XP_MORTE_YITHIAN = 0.5`);
- il cadavere dell'NPC **non** viene trasportato alla morgue (resta dove è morto — comportamento di default già previsto per gli NPC);
- gli oggetti che l'NPC portava restano sul cadavere: non tornano al corpo Yithiano, ed è quindi possibile perderli se qualcun altro li saccheggia o li sacrifica per primo.

### YITH ADAPT

```
yith adapt
yith adapt <skill> [volte]
```

Disponibile solo mentre si possiede un NPC. Spende le *practice* del corpo Yithiano (non quelle del veicolo posseduto) per innalzare una skill del corpo Yithiano. Il rating base disponibile è la **media** tra il rating dell'NPC e quello dello Yithiano in quella skill, poi modificato dalla media del rating "Insegnamento" (Teach) di entrambi i corpi; solo le skill con un rating finale sopra **25** compaiono nella lista — tutti dettagli confermati dalla fonte.

### YITH ABDUCT

```
yithabduct
```

Disponibile solo mentre si possiede un NPC: lo trasporta nella Biblioteca Yithiana, permettendo di equipaggiarlo o operare su di lui in un luogo relativamente sicuro. Confermato dalla fonte.

## Voodoo

Il sistema voodoo (`/data/claude/CthulhuMud/game/commands/cthulhu_voodoo.py`) è confermato verbatim dalla fonte (*helps/consecrate_doll.txt*, *helps/voodoo.txt*) come parte della skill Vudù, che descrive la creazione e manipolazione di bambole voodoo personalizzate.

Procedura confermata dalla fonte:

1. **`CUT <bersaglio>`**: taglia una ciocca di capelli al bersaglio (necessaria per l'incantesimo successivo).
2. **`CAST 'CONSECRATE DOLL' <bersaglio>`**: combina una bambola vuota con la ciocca di capelli, creando una bambola voodoo personalizzata legata a quel bersaglio.
3. Una volta pronta, la bambola agisce **a distanza**, ovunque si trovi la vittima, tramite `VOODOO STAB/TWIST/TEAR`:

| Comando | Effetto sulla vittima | Effetto sulla bambola |
|---|---|---|
| `VOODOO STAB <bambola>` | Solo un avvertimento doloroso, nessun danno reale | Nessuno |
| `VOODOO TWIST <bambola>` | Danno (nel porting: 8-16 punti) | Si deteriora (perde integrità, 5-10 punti); se l'integrità arriva a zero si sgretola |
| `VOODOO TEAR <bambola>` | Danno grave, potenzialmente letale (nel porting: 30-55 punti) | Distrutta immediatamente |

Le fasce numeriche di danno e di deterioramento non sono specificate dalla fonte (che parla solo di "warning"/"damage"/"severe pain and injury, perhaps even to the point of death") e sono quindi scelte di design del porting.

## Focus Crystal

I Cristalli Focus Yithiani (`world/focus_crystal.py`, `commands/cthulhu_focus_crystal.py`) sono confermati dalla fonte (*guides_yithianfaq.txt*) come oggetti pensati per gli Yithiani, che permettono di assorbire skill dalle creature circostanti.

- **Assorbimento passivo**: un cristallo tenuto in mano/inventario "risucchia" gradualmente skill da NPC o giocatori presenti nella stessa stanza, anche solo per la loro presenza (la fonte specifica che l'uso attivo della skill ne aumenta l'assorbimento; il porting semplifica questo aspetto con un tick passivo uniforme, senza bonus per skill "appena usata" — scelta di design dichiarata).
- **`LORE <cristallo>`**: richiede la skill Lore e mostra le skill assorbite dal cristallo con il loro livello interno.
- **`USE <cristallo>`**: trasferisce un sottoinsieme casuale delle skill assorbite al personaggio che lo usa — se non la conosce, la impara; se la conosce già, la migliora. C'è sempre una componente casuale, confermata dalla fonte.
- **Penalità ai non-Yithiani**: i cristalli sono pensati per gli Yithiani; chiunque altro (incluso uno Yithiano che sta possedendo un corpo non-Yithiano) subisce una forte penalità di riuscita nell'uso — confermato dalla fonte.

Le percentuali esatte di assorbimento e trasferimento, il numero massimo di skill per cristallo e la cadenza del tick passivo non sono specificate dalla fonte e sono quindi scelte di design esplicite del porting.

`LORE` funziona anche su qualunque altro oggetto (non solo i cristalli), mostrando le stesse informazioni dell'incantesimo Identificare: confermato dalla fonte, ogni tentativo costa **100 punti movimento**, e a differenza dell'incantesimo Identificare dipende solo dal rating nella skill Lore, non anche dalla skill di Lancio degli Incantesimi. `USE` resta invece specifico per i Cristalli Focus e per le statuette create con l'incantesimo Crea Statuetta; su qualunque altro oggetto risponde con un messaggio onesto invece di far finta di funzionare.

## Porte e serrature

Il sistema `OPEN`/`CLOSE`/`LOCK`/`UNLOCK`/`PICK` (`world/porte.py`, `commands/cthulhu_porte.py`) è confermato dalla fonte (*helps/open.txt*), con una semplificazione dichiarata: la fonte cita anche "trunks, chest, lockers" (bauli, casse, armadietti) come oggetti apribili/chiudibili, ma il porting si limita alle **porte** (uscite), perché nessun contenitore di quel tipo esiste ancora nel mondo di gioco — costruire un intero sistema di contenitori chiudibili senza un solo caso d'uso reale sarebbe stato aggiungere più del necessario.

Confermato dalla fonte: "*for doors, players must specify the direction of the door, not its name*" — quindi `OPEN NORTH` funziona, `OPEN DOOR` no. I comandi del porting accettano quindi sempre e solo una direzione:

```
open <direzione>
close <direzione>
lock <direzione>       (serve tenere in mano la chiave giusta; la porta deve essere già chiusa)
unlock <direzione>     (serve tenere in mano la chiave giusta)
pick <direzione>       (scassinare senza chiave; richiede la skill Scasso)
```

Dettagli del porting:

- Qualunque uscita del mondo può diventare una porta chiudibile alla prima `CLOSE`: non serve marcarla in anticipo, il lock dinamico necessario viene aggiunto automaticamente in quel momento.
- `LOCK`/`UNLOCK` richiedono di tenere in mano la chiave giusta, confermato dalla fonte ("*the player must have the appropriate key to do this*"); nel porting, ogni chiave è legata a un'unica serratura (`chiave.db.apre`).
- `PICK <direzione>` (skill Scasso) tenta lo scasso senza chiave: nel porting costa 50 punti movimento per tentativo e ha una probabilità di successo legata al rating nella skill (fascia 20-90%). Questi numeri non sono specificati dalla fonte e sono quindi scelte di design esplicite.

La fonte rimanda anche a `HELP SMASH` come alternativa per forzare porte/oggetti chiusi: questo comando non è trattato in questo capitolo.
