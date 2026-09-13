# Economia, Società e Gruppo

Questo capitolo copre tutto ciò che riguarda il denaro (le cinque valute, le banche, i negozi), l'equipaggiamento (forgiatura, riparazione, armadietti) e le forme di aggregazione tra personaggi: società/clan, gruppi di combattimento e seguaci addomesticati.

Come nel resto di questo Codex, ogni sezione distingue esplicitamente cosa è **confermato dalla fonte originale** (cthulhumud.com) e cosa è invece una **scelta di design del porting** — distinzione che nel codice sorgente compare sistematicamente nei commenti di modulo, e che qui viene riportata fedelmente.

## 1. Le cinque valute

La fonte originale (`helps/money.txt`, il cui testo è alias identico di `dollars.txt`, `gold.txt`, `crowns.txt`, `copper.txt` e `yuggos.txt` — sono la stessa identica pagina raggiungibile con cinque nomi diversi) è inequivocabile: CthulhuMUD non ha una sola valuta, ma cinque, ciascuna nativa di una particolare regione del mondo:

> "DOLLARS are used in most areas of the Waking World, GOLD is used in certain civilized areas of the Dreamlands (such as Ulthar), CROWNS are used almost exclusively in the city of Dylath-Leen, COPPER is used in many non-human areas, and YUGGOS are used in areas controlled by the Mi-Go."

| Valuta | Nome interno (`db.*`) | Zona di riferimento nella fonte |
|---|---|---|
| Dollari | `db.dollari` | La maggior parte del Waking World (es. Arkham) |
| Oro | `db.gold` | Aree civilizzate delle Dreamlands (es. Ulthar) |
| Corone | `db.corone` | Quasi esclusivamente Dylath-Leen |
| Rame | `db.rame` | Molte aree non umane |
| Yuggos | `db.yuggos` | Aree controllate dai Mi-Go |

**Nota implementativa importante (dichiarata nel codice, `world/valute.py`):** l'Oro (`db.gold`) esisteva già in tutto il codice fin dalle prime fasi del porting come valuta unica e universale — usata da negozi, banca, taglie, quote di clan e circa altri 27 punti del codice. Piuttosto che riscrivere da zero tutti questi punti (rischio alto di regressioni per un beneficio proporzionalmente piccolo), la scelta di design è stata: l'Oro resta la valuta "oro" della fonte, invariata in tutti i suoi usi preesistenti; le altre quattro valute (Dollari, Corone, Rame, Yuggos) sono state aggiunte come nuovi campi separati sul personaggio, realmente possedibili, visualizzabili e scambiabili in banca — ma **non ancora imposte come requisito d'acquisto nei negozi**, che continuano tutti ad accettare Oro. Rendere davvero necessaria la valuta locale in ogni negozio già costruito avrebbe richiesto una migrazione di contenuto sproporzionata (tutti i punti vendita di Arkham, Cairo e Zoog Village), non giustificata da un audit di chiusura-gap.

### Mappatura zona → valuta locale

Nessuna fonte fornisce un elenco esaustivo zona per zona: solo i cinque esempi generali sopra, più l'esempio esplicito "DOLLARS in Arkham, GOLD in Ulthar, CROWNS in Dylath-Leen". Il porting **estende per analogia dichiarata** questa mappatura alle altre zone già costruite:

| Valuta | Zone/tag associati (scelta di design per analogia) |
|---|---|
| Dollari (default) | Arkham (stanze/edifici), Il Cairo, e ogni zona non altrimenti classificata |
| Oro | Ulthar (Tempio), Dreamlands in generale |
| Corone | Riformatorio di Dylath-Leen |
| Rame | Y'ha-nthlei, Villaggio degli Zoog, Biblioteca Yithiana (aree non umane) |
| Yuggos | Nave madre dei Mi-Go, addestramento a Yuggoth |

La valuta di default generale, quando nessun tag di zona corrisponde, è **Dollari** ("most areas of the Waking World").

### MONEY / WORTH

Confermato dalla fonte: la scheda personaggio (`score`) mostra **solo** la valuta di default della zona in cui ci si trova al momento, e questa visualizzazione cambia man mano che ci si sposta — ma **questo non cambia quanto denaro si possiede realmente**, solo cosa viene mostrato. Per vedere il totale completo in tutte e cinque le valute si usa:

```
money
worth
```

(sono alias dello stesso comando). L'output elenca sempre tutte e cinque le valute con il saldo corrispondente, indipendentemente da dove ci si trova.

Un dettaglio confermato dalla fonte e riportato fedelmente: **non si perde mai denaro morendo** — il denaro resta con il personaggio, non sul cadavere, proprio per permettere di comprare nuovo equipaggiamento se il cadavere non è recuperabile.

## 2. Banche

### Deposito e prelievo

Le banche (edifici taggati come tali ad Arkham) permettono di mettere il proprio Oro al sicuro. I comandi sono:

```
deposit <quantità>     / deposita <quantità>
withdraw <quantità>    / preleva <quantità>
balance                / saldo
```

Funzionano solo se ci si trova fisicamente in una banca. Il saldo depositato vive separato dall'Oro portato addosso (`Character.db.banca` contro `Character.db.gold`).

**Nota sulla fonte**: il sistema bancario di base (deposito/prelievo) **non risulta documentato da nessuna fonte originale reperita** nella scansione del sito. È una convenzione quasi universale nei MUD derivati da Diku, qui giustificata anche narrativamente dal fatto che la skill Furto esiste già nel gioco: l'Oro in banca è al sicuro da eventuali furti di altri giocatori, a differenza di quello portato addosso (non protegge invece dalla morte, perché — come detto sopra — non si perde mai denaro morendo, né in banca né fuori).

Da notare comunque che la pagina `helps/bank.txt` esiste davvero e conferma l'esistenza generale delle banche con sintassi leggermente diversa da quella implementata: `BANK BALANCE`, `BANK DEPOSIT <amount> <currency>`, `BANK WITHDRAW <amount> <currency>`, `BANK CHANGE <amount> <old currency> <new currency>` — un unico comando ombrello `BANK` con sottocomandi. Il porting sceglie invece **comandi separati** (`deposit`/`withdraw`/`balance`/`exchange`), scelta di design più idiomatica per l'interfaccia a comandi di Evennia, mantenendo però intatta la semantica descritta dalla fonte.

### Il tasso di interesse

> "Money that is deposited in a bank will earn 1% interest per game-month that passes." (`helps/bank.txt`)

Il tasso dell'1% mensile applicato in gioco è **confermato ESATTO dalla fonte** (non una scelta di design arbitraria, come inizialmente si era ipotizzato durante lo sviluppo — la scansione esaustiva del sito lo ha confermato testualmente). Poiché il porting non ha un calendario di gioco strutturato in mesi, "un mese" è stato tradotto in un intervallo di tempo reale arbitrario — un giorno reale — **scelta di design esplicita e dichiaratamente facile da ritarare** in futuro. L'interesse viene applicato automaticamente a tutti i personaggi con Oro depositato, tramite uno script persistente lato server.

### EXCHANGE (cambio valuta)

```
exchange <quantità> <valuta_da> <valuta_a>
cambia <quantità> <valuta_da> <valuta_a>
```

Esempio: `exchange 50 dollari oro`. Funziona solo in banca.

La fonte conferma il meccanismo ma non i numeri:

> "You can change one currency to another at a bank, but not all banks accept all forms of currency, and the exact exchange rate will vary from location to location."

Il porting applica qui due semplificazioni dichiarate:

- **Tasso di cambio**: un tasso unico 1:1 per ogni coppia di valute, invece di inventare tassi diversi senza alcuna indicazione dalla fonte su quali dovrebbero essere più o meno favorevoli.
- **Accettazione delle valute**: la fonte prevede esplicitamente che non tutte le banche accettino tutte le forme di valuta ("not all banks accept all forms of currency"). Per semplicità, **tutte le banche già costruite nel porting accettano tutte e cinque le valute** — non è quindi ancora modellata la restrizione per singola banca prevista dall'originale.

## 3. Negozi

Un "mercante" nel porting è semplicemente un NPC civile (non ostile, non insegna skill) con un attributo `db.negozio`: una lista di voci `{chiave, nome, prezzo, descrizione, ...}`. La fonte descrive un sistema di negozi molto più ricco (`helps/list.txt`/`buy.txt`/`sell.txt`, un unico gruppo di comandi condiviso):

> "There are dozens of shops scattered all over the world [...] The HOURS command will show you when the shop is open. The LIST command will display the items [...] The APPRAISE command will give you detailed information [...] The BUY command will purchase a particular item [...] The SELL command can be used by a player to sell an item to the shop."

### LIST / BUY / SELL

```
list        / lista        — mostra la merce in vendita dal mercante presente nella stanza, con il prezzo in Oro
buy <chiave>  / compra <chiave>  — acquista un articolo (deve esserci abbastanza Oro)
sell <oggetto> / vendi <oggetto> — vende un oggetto al mercante, per metà del suo valore originale
```

`SELL` funziona solo con oggetti che portano un attributo di valore assegnato (`db.valore`), di norma quelli comprati da un mercante — non un sistema generico di valutazione di qualunque oggetto trovato nel mondo.

**Elementi della fonte non ancora implementati** (gap dichiarati, non nascosti): `APPRAISE` (informazioni dettagliate su un articolo, al costo di 1/10 del suo prezzo), la skill `HAGGLE` per negoziare i prezzi, `RESTRING` (i negozi come unico luogo dove rinominare/descrivere oggetti), e il modificatore `#.`/`#*` per comprare articoli multipli o specifici tra doppioni con lo stesso nome.

Ogni oggetto acquistato eredita `db.valore = prezzo`, così che `SELL` possa ricomprarlo a metà prezzo senza dover consultare l'inventario specifico del mercante di provenienza — una convenzione classica da MUD che funziona anche con eventuale bottino futuro di mostri. Se la voce di negozio include campi di equipaggiamento (`slot`, `tipo_arma`, `dado_min/max`, `bonus_danno`, `classe_armatura`, `livello`, `materiale_forgiatura`, ecc.) o alimentari (`cibo`, `bevanda`), questi vengono copiati sull'oggetto creato — in caso contrario resta un oggetto puramente di ambientazione.

**Ampiezza del catalogo attuale**: 47 mercanti in tutto — 35/35 ad Arkham (cibo, abbigliamento, negozi generici), 6/7 a Cairo (manca solo l'Anubis Hotel, escluso di proposito: è un albergo, meccanica di alloggio distinta da quella di compravendita), 6/6 a Zoog Village, più Maro, il fabbro di Ulthar, costruito a parte per la Forgiatura. Il numero esatto di articoli per negozio (fino a 7) non ha riscontro puntuale nella fonte: è una scelta di design.

### Orari di apertura (HOURS)

Confermato dalla fonte come meccanica reale, non semplice colore:

> "The HOURS command will show you when the shop is open."

Il porting riusa l'orologio di gioco nativo di Evennia (governato da `TIME_FACTOR`, che scala 3600 secondi di gioco in 75 secondi reali) invece di costruire un sistema a parte. Gli orari dei singoli negozi di Arkham (stringhe come "9am-9pm", "8pm-4am", "Always Open") vengono dal catalogo ufficiale delle location di Arkham e sono agganciati alla **stanza**, non al mercante. `LIST`/`BUY`/`SELL` verificano ora l'orario e rifiutano l'operazione a negozio chiuso, indicando di usare `HOURS` per sapere quando riapre; `HOURS` stesso resta sempre disponibile.

I negozi di Cairo e Zoog Village **non hanno mai avuto orari nella documentazione raccolta**: restano quindi sempre aperti (nessun vincolo impostato) — dichiaratamente per onestà sui dati mancanti, non un'invenzione arbitraria di orari fittizi.

## 4. Forgiatura ed equipaggiamento

### FORGE, FIX, REFIT

La skill Forgiatura e i suoi comandi sono confermati **verbatim** dalla fonte (`guides_forging.txt`, `helps/forging.txt`):

> "You must be holding the raw material you wish to use, and you must be standing in a room that contains an anvil or a forge... Using the FORGE command costs 200 movement points... FIX... costs 80 movement points... REFIT... costs 100 movement points."

| Comando | Costo (movimento) | Effetto |
|---|---|---|
| `forge <tipo> [livello]` / `forgia` | 200 | Crea un'arma o pezzo d'armatura dal materiale grezzo tenuto in mano |
| `fix <oggetto>` / `ripara` | 80 | Ripara parzialmente un oggetto danneggiato, con rischio di romperlo |
| `refit <oggetto> <livello>` / `adatta` | 100 | Adatta il livello minimo richiesto dall'oggetto, con rischio di romperlo |

Punti confermati dalla fonte:

- **Non serve oro**: si consuma materiale grezzo tenuto in mano, non denaro — a differenza di un precedente comando `CmdRepair` (rimosso) che era a pagamento in Oro, giudicato in fase di audit **infedele alla fonte** una volta letta la pagina originale per intero.
- Serve un'incudine o una forgia nella stanza (es. la bottega di un fabbro — la fonte cita esplicitamente Maro a Ulthar, presente anche nel porting, oltre alla Fucina di Chorl a Zoog Village).
- `FORGE` non può creare un oggetto di livello superiore al proprio; la qualità dipende da livello, qualità del materiale e rating in Forgiatura.
- `FIX` rischia di rompere l'oggetto anziché ripararlo; il rischio scende salendo di rating in Forgiatura.
- `REFIT` ha lo stesso tipo di rischio, per ridimensionare l'oggetto a un livello diverso.

Non specificato dalla fonte (scelte di design esplicite): le formule numeriche esatte di danno/classe armatura risultanti, le percentuali precise di successo/rottura, i tipi esatti di materiale grezzo disponibili (cristallo, oro, diamante, mithril, con "qualità" crescente) e il loro valore in negozio.

### GUNSMITH e RELOAD (armi da fuoco)

Confermati dalla fonte (`helps/forging.txt` per GUNSMITH, `helps/reload.txt` per RELOAD):

> "The GUNSMITH command is used to create guns and ammunition [...] GUNSMITH AMMO <caliber>" — "RELOAD [...] perform the REMOVE and WIELD actions necessary to load and/or clean a gun weapon [...] If a character has a clip of the wrong size, this command will only partially load the weapon."

```
gunsmith <tipo> <calibro> [livello]   — costruisce un'arma da fuoco (200 movimento)
gunsmith ammo <calibro>               — fabbrica un caricatore di munizioni (120 movimento)
reload / ricarica                     — carica l'arma impugnata con un caricatore compatibile nell'inventario
```

Costruire munizioni richiede, oltre alla Forgiatura, anche le skill **Esplosivi** e **Chimica** (confermato dalla fonte), e materiale grezzo da lavorare come polvere da sparo. `RELOAD` cerca automaticamente nell'inventario un caricatore dello stesso calibro dell'arma impugnata; se il caricatore contiene meno colpi della capacità residua, la ricarica è solo parziale — dettaglio testuale confermato dalla fonte.

Non specificato dalla fonte (scelte di design esplicite): i calibri concreti disponibili (`.22`, `.38`, `.45`, `9mm`, `12 gauge`), la capacità dei caricatori per tipo d'arma, la quantità di colpi prodotti per tentativo di `GUNSMITH AMMO`, e soprattutto **il fatto che le armi da fuoco restino davvero senza colpi in combattimento**: la fonte descrive solo creazione e ricarica, non se e come le munizioni si esauriscono durante un combattimento. Il porting ha scelto di renderlo un vincolo reale — altrimenti `GUNSMITH`/`RELOAD` sarebbero pura scenografia senza alcun impatto meccanico.

### Equipaggiamento: WEAR, WIELD, REMOVE, EQUIPMENT

```
wear <oggetto>   / indossa   — indossa armature/scudi/amuleti ecc.
wield <oggetto>  / impugna   — impugna un'arma
remove <oggetto> / rimuovi   — toglie qualcosa che si indossa o impugna
equipment / eq                — mostra tutto ciò che si indossa/impugna, per slot
```

Confermato dalla fonte: `WEAR` e `WIELD` sono comandi distinti; l'efficacia in combattimento dipende dalla **skill legata al tipo di arma impugnata** ("it doesn't matter which weapon you prefer, as long as you're good at whichever one you're carrying"), non dall'arma in sé; gli oggetti hanno un livello massimo d'uso fino a 10 livelli sopra il proprio, estendibile con "talent raising items" (oggetti che alzano temporaneamente il livello effettivo); l'equipaggiamento si deteriora e va riparato.

Non specificato dalla fonte (scelte di design esplicite): lo slot esatto per ogni tipo di oggetto (nel porting: arma, scudo, testa, corpo, mani, gambe, piedi, amuleto — un sottoinsieme ragionevole rispetto ai 20+ slot tipici di molti MUD Diku-derivati), e le formule numeriche precise di danno/classe armatura/degrado.

### Degrado in combattimento

Ogni colpo andato a segno in combattimento consuma un po' di condizione (`db.condizione`, 0–100) dell'arma dell'attaccante e di **tutti** i pezzi indossati dal difensore, con un piccolo valore casuale per colpo. Un oggetto che arriva a condizione 0 si rompe (annuncio in stanza) e resta equipaggiato ma **non dà più alcun bonus** (né danno né classe armatura) finché non viene riparato con `FIX`. Anche una fuga riuscita (`FLEE`) può danneggiare un pezzo di equipaggiamento a caso indossato — dettaglio confermato dalla fonte (`helps/flee.txt`: "a small loss of experience and/or some minor damage to your equipment").

## 5. Armadietti

```
locker                          / armadietto
locker store <oggetto>          / armadietto deposita <oggetto>
locker retrieve <oggetto>       / armadietto preleva <oggetto>
```

Un armadietto economico, con capacità massima di 20 oggetti, per tenere al sicuro un set di scorta — utile in particolare nel caso l'equipaggiamento indossato vada perso alla morte. Gli oggetti depositati vengono spostati fuori dal mondo di gioco e tracciati sul personaggio, recuperabili in qualunque momento con `retrieve`/`preleva` (non è necessario tornare in un luogo specifico).

**Semplificazione dichiarata rispetto all'originale**: nella fonte gli armadietti erano oggetti fisici in luoghi specifici del mondo, apribili con una chiave da acquistare. Nel porting l'armadietto è invece **personale e disponibile ovunque** — un "deposito" astratto, sullo stesso modello della banca per il denaro — senza posizionamento fisico né oggetto-chiave, per restare nello scopo circoscritto della milestone che lo ha introdotto.

## 6. Società e Clan

### Cosa dice la fonte

La scansione esaustiva del sito (`societies_list.txt`, `societies_newclans.txt`, `societies_upgrades.txt`, `helps/societies.txt`) conferma che nell'originale i clan **non erano affatto un sistema self-service per i giocatori**. Fondarne uno richiedeva:

- essere almeno di livello **HERO**;
- avere due co-fondatori (di cui almeno uno di livello **INVESTIGATOR**);
- disporre di **500.000 di Oro**;
- e soprattutto ottenere l'**approvazione manuale dello staff Immortal**, tramite richiesta sulla bacheca in gioco o via email.

Anche gli "upgrade" di società (stanze extra, porte, guardie e altri NPC di clan, tutti listati con un prezzario dettagliato in `societies_upgrades.txt`) erano acquisti mediati dallo staff, non un negozio self-service in gioco.

**Per questo il porting NON implementa** un comando per "fondare il proprio clan" né un negozio di potenziamenti self-service: farlo sarebbe stato **infedele alla fonte**, non semplicemente un gap da colmare. È stato invece implementato tutto ciò che è realmente giocabile senza intervento dello staff: appartenenza, ruolo/rango, consultazione dell'elenco società.

La fonte elenca esplicitamente sei clan pubblici (esistono anche "dozzine" di clan più piccoli e segreti, mai resi pubblici — il porting non inventa nomi per questi ultimi):

| Società | Leader "di lore" nella fonte |
|---|---|
| Loggia Massonica di Arkham | nessuno (inattivo) |
| Cabal Du Quixotic | Wod |
| Ordine Esoterico di Dagon | nessuno (inattivo) |
| Squarciatori del Velo | Aemilia |
| Arcanuum di Ulthar | Thistle |
| Guerrieri della Luce | nessuno (inattivo) |

### Il comando CLAN

```
clan                                    — mostra le proprie appartenenze e ranghi
clan list                               — elenco delle società pubbliche note
clan info <società>                     — descrizione e leader di una società
clan members <società>                  — elenco dei membri con rango
clan research <personaggio>             — a quali società appartiene un personaggio
clan tell <società> <messaggio>         — messaggio a tutti i membri online della società
clan invite <personaggio> <società>     — richiede rango consiglio o superiore
clan promote <personaggio> <società>    — richiede rango leader
clan demote <personaggio> <società>     — richiede rango leader
clan expel <personaggio> <società>      — richiede rango leader
clan leave <società>
```

I ranghi, confermati dalla fonte come bitflag, sono: **invitato** (1), **membro** (2), **consiglio** (4), **leader** (8). `demote` su un membro al rango minimo lo espelle direttamente (stesso effetto di `expel`, che nella fonte era prima disponibile solo come effetto collaterale di `demote` ripetuto — nel porting è stato aggiunto come azione diretta).

Un dettaglio importante **confermato dalla fonte**: un personaggio può appartenere a **più società contemporaneamente** ("SOCIETY INFO will show you a list of the societies you are currently in", al plurale) — nel porting questo è modellato con un dizionario `{società: rango}` per personaggio, non un singolo campo clan/rango.

**Elementi della fonte deliberatamente non implementati** (dichiarato, non dimenticato): l'intera suite di governance/economia di clan citata dalla stessa pagina fonte — `SOCIETY POLITICS`, `REVOLT`, `CHALLENGE`, `VOTE`, `LAW`, `BANK`, `TAX`, `FOE`/`PARDON`, `AUTH`, `SIGN`, `SUBSCRIBE`, `RESET`, `TEST`, `CLEANUP`. Costruire anche solo un sottoinsieme credibile di elezioni/tasse/diplomazia tra clan sarebbe un sistema a sé stante, delle dimensioni dell'intero resto di questo modulo. Allo stesso modo, `SOCIETY LIST <group>` (categorizzazione tematica dei clan) non è implementato: nessuna fonte fornisce una tassonomia dei sei clan pubblici, e inventarne una sarebbe arbitrario.

## 7. Gruppi

### Cosa dice la fonte

`helps/follow.txt` è l'unica pagina condivisa da `FOLLOW`/`GROUP`/`NOFOLLOW`, ed è molto dettagliata:

> "The FOLLOW command will force your character to tag along behind another character [...] To stop following someone else, simply FOLLOW yourself. The GROUP command forms a single fighting group with a player who is following you. Characters who fight in a group fight combine their various strengths into a more powerful fighting force, share the experience from killing, and may communicate with each other with the GTELL command. The SPLIT command divides up any money that is taken from dead monsters amongst your group, but you can set this action to occur automatically with the AUTOSPLIT option. **If one member of the group is attacked, all the members of the group will automatically join the fight (assuming that the characters have the AUTOASSIST option toggled).** The GROUP command will also boot a character out of your group, or they can leave voluntarily by using the FOLLOW command [...] the NOFOLLOW command will stop someone who currently follows you from following you and prevent you from getting new followers."

### Comandi

```
follow <personaggio>    — segui un altro personaggio da stanza a stanza
follow me               — smetti di seguire chi stai seguendo
nofollow                — alterna (toggle) se accetti nuovi seguaci; congeda anche i seguaci attuali
nofollow <personaggio>  — allontana solo quel seguace specifico, senza attivare il toggle
group                   — mostra chi fa parte del tuo gruppo (con HP/Mana)
group <personaggio>     — aggiunge al gruppo chi ti sta già seguendo, oppure lo espelle se già membro
gtell <messaggio>       — comunica con tutto il gruppo
split                   — dividi il tuo oro attuale con i compagni di gruppo presenti nella stanza
autosplit                — alterna la divisione automatica
autoassist               — alterna l'assistenza automatica ai compagni di gruppo
```

Solo il **leader** del gruppo (chi ha altri membri sotto di sé) può aggiungere o espellere membri con `group <personaggio>`; un membro può sempre uscire volontariamente smettendo di seguire (`follow me`).

### AUTOASSIST

Confermato letteralmente dalla fonte: se un membro del gruppo viene attaccato, tutti gli altri membri presenti nella stessa stanza con `AUTOASSIST` attivo si uniscono automaticamente al combattimento contro l'aggressore.

### Condivisione dell'esperienza

Confermato **qualitativamente** dalla fonte ("share the experience from killing"), ma senza una formula precisa: il porting divide l'esperienza guadagnata dall'uccisore in parti uguali tra tutti i membri del gruppo presenti nella stessa stanza (uccisore incluso) — scelta di design esplicita per la formula di divisione, non la sola cosa confermata dalla fonte (che è il principio di condivisione in sé).

### Bonus di combattimento di gruppo

La fonte afferma che i personaggi in gruppo "combinano le proprie forze in una forza da combattimento più potente", ma non fornisce alcuna formula. Il porting traduce questo in un piccolo bonus a colpire (+2) per ogni altro membro del gruppo vivo presente nella stessa stanza — scelta di design dichiarata.

### SPLIT/AUTOSPLIT: una semplificazione dichiarata

La fonte descrive `SPLIT`/`AUTOSPLIT` come la divisione "del denaro preso dai mostri morti" — ma questo porting **non ha mai implementato un drop automatico di oro dall'uccisione di un mostro** (l'oro arriva solo da taglie/missioni). Costruire quel sistema sarebbe andato ben oltre lo scope della milestone di `FOLLOW`/`GROUP`. Per questo, nel porting, `SPLIT` divide semplicemente l'oro **attualmente posseduto dal chiamante** tra i membri del gruppo presenti nella stanza; `AUTOSPLIT` resta un interruttore già pronto per quando (e se) un sistema di bottino in oro verrà costruito in futuro.

## 8. Seguaci e Addomesticamento

### TAME

Confermato dalla fonte (`helps/tame.txt`):

> "This skill enables a character to attempt to control a creature. If successful, the creature will act as if charmed and follow the character as a pet. **Sentient NPCs, undead NPCs, and NPCs with even a small amount of natural intelligence cannot be controlled with this skill.** [...] REQUIRES: 200 movement points."

```
tame <bersaglio>
```

Nel bestiario del porting, **tutte** le creature (Ghoul, cultisti, Profondi, mummie, Cani di Tindalos, Byakhee, Shoggoth, Gug, Bestie Lunari, marinai annegati, ecc.) sono orrori del Mythos senzienti o non-morti: nessuna di esse è quindi addomesticabile per definizione, coerentemente con la fonte. `TAME` funziona solo sui pochi NPC di ambientazione "animaleschi" presenti nel mondo (es. "un topo enorme"), privi di aggressività o sottorazza. Il tentativo costa 200 movimento (valore esatto confermato dalla fonte) e ha una probabilità di successo legata al rating nella skill Addomesticamento.

### RECRUIT

Confermato dalla fonte (`helps/recruit.txt`) come skill **puramente passiva**:

> "There is no special command to use and no specific way to turn this skill off or on. It works automatically. The higher your rating in this skill, the better your odds of randomly acquiring followers as you travel around the world."

Nel porting è agganciata all'ingresso in una nuova stanza: ogni volta che un personaggio con questa skill entra in una stanza, c'è una probabilità (legata al rating) di attrarre spontaneamente un nuovo seguace scelto da un piccolo elenco di figure di ambientazione (un cane randagio, un mendicante, un gatto mezzo selvatico, un marinaio senza meta).

### ORDER

Confermato dalla fonte (`helps/order.txt`):

> "This command enables a player to force one or all of their charmed followers (including pets) to perform a specific command [...] you are responsible for the actions of your followers."

```
order <seguace> <comando>
order all <comando>
```

Il comando viene semplicemente inoltrato al seguace, che lo esegue come se lo avesse digitato lui stesso — nessuna restrizione aggiuntiva sui comandi ordinabili, coerente con il fatto che la fonte stessa affida la responsabilità delle azioni al giocatore, non a un filtro del sistema.

I seguaci (sia addomesticati con `TAME` sia ottenuti con `RECRUIT`) seguono automaticamente il proprio padrone da una stanza all'altra, in modo analogo (ma distinto nel modello dati) ai personaggi giocanti che usano `FOLLOW`.
