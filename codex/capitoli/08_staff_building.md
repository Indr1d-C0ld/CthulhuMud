# Appendice: Strumenti per Staff e Builder

Questo capitolo documenta i comandi riservati allo staff (i tre livelli di permesso Evennia usati in questo porting: **Builder**, **Admin**, **Developer**, dal meno al più potente) e la filosofia con cui viene costruito il contenuto ostile del gioco (il bestiario). È un'appendice tecnica, non rivolta ai giocatori normali, ma fa parte integrante del Codex perché descrive meccaniche realmente presenti nel codice.

La fonte originale (`research/site_corpus/immhelp_commands.txt`) elenca sei gradi nominali per gli Immortali — Hero, Creator, Lesser God, God, Greater God, Implementor — più una manciata di "flag" trasversali (admin, builder, enforcer, questor) che concedevano l'accesso a comandi specifici indipendentemente dal grado. Questo porting ha un solo amministratore reale, non uno staff a più persone: replicare l'intera scala a sei gradini avrebbe aggiunto complessità senza beneficio pratico. La scelta di design dichiarata (`world/staff.py`) è di mappare ogni comando sul livello Evennia più vicino **per potere**, non per nome: quello che conta è cosa fa ogni comando, non l'etichetta esatta del suo gradino originale. Per lo stesso motivo, molti comandi tradotti da `evennia/commands/default/` portano ancora un lock del tipo `cmd:perm(nomecomando) or perm(Livello)`: il permesso puntuale (`perm(boot)`, `perm(dig)`, ecc.) non viene mai assegnato singolarmente in questa installazione, quindi in pratica il requisito effettivo è sempre e solo il permesso di livello generico indicato nella colonna "Permesso" delle tabelle seguenti.

## Moderazione e gestione account

Comandi di `commands/cthulhu_admin.py`, tradotti dal set amministrativo standard di Evennia per completezza, anche se in questo deployment sono usati da un solo moderatore.

| Comando | Sintassi | Permesso | Cosa fa |
|---|---|---|---|
| `boot` | `boot[/switch] <account> [: motivo]` | Admin | Espelle un account dal server disconnettendo tutte le sue sessioni attive. Switch `quiet` (non avvisa l'utente) e `sid` (bersaglio per id di sessione invece che per nome). Registra l'azione nel log di sicurezza. |
| `ban` | `ban [<nome o ip> [: motivo]]` (alias `bans`) | Developer | Impedisce il login a un account per nome, oppure blocca un indirizzo IP o un'intera sottorete (con wildcard `*`). Senza argomenti mostra l'elenco numerato dei ban attivi. Chiede conferma prima di applicare il ban. |
| `unban` | `unban <idban>` | Developer | Rimuove un ban precedentemente impostato, individuato tramite l'id numerico mostrato da `ban`. Chiede conferma. |
| `userpassword` | `userpassword <account> = <nuova password>` | Admin | Reimposta la password di un account, con la validazione standard della password Django/Evennia. |
| `perm` | `perm[/switch] <oggetto o *account> [= <permesso>[,<permesso>...]]` (alias `setperm`) | Developer | Assegna o rimuove (`/del`) singole stringhe di permesso su un oggetto o, con `*nome`/`/account`, su un account. Senza lato destro, elenca i permessi già presenti. Non permette di assegnare un permesso superiore al proprio. |
| `wall` | `wall <messaggio>` | Admin | Manda un annuncio a tutte le sessioni connesse al server, incluse quelle non ancora autenticate. |

## Comunicazione e forzatura da builder

Comandi ancora in `cthulhu_admin.py`, ma con soglia di permesso più bassa perché utili anche durante la costruzione ordinaria di contenuti (per testare reazioni di NPC, inviare messaggi scenici, ecc.).

| Comando | Sintassi | Permesso | Cosa fa |
|---|---|---|---|
| `emit` | `emit[/switch] [<obj>, <obj>, ... =] <messaggio>` (alias `pemit`, `remit`) | Builder | Emette un messaggio arbitrario verso una o più stanze/account, o verso i propri dintorni se non viene indicato un bersaglio. Switch `contents` per inviarlo anche al contenuto degli oggetti bersaglio; `remit` e `pemit` sono forme già ristrette rispettivamente a stanze e ad account. |
| `force` | `force <oggetto>=<stringa di comando>` | Builder | Costringe un oggetto (tipicamente un NPC) a eseguire un comando come se lo avesse digitato lui stesso — utile per far agire un mostro o un NPC a scopo di test o di scena, senza dover scrivere logica dedicata. |

## Costruzione del mondo: stanze e uscite

Nucleo essenziale di `commands/cthulhu_building.py`. La fonte (`evennia/commands/default/building.py`) offre 25 comandi di building per un totale di oltre 4600 righe: qui è stato tradotto solo il nucleo che serve davvero a costruire stanze/uscite/oggetti a mano; il resto (attributi, typeclass, lock, ricerca, prototipi...) è in `cthulhu_building_advanced.py` (sezione successiva).

| Comando | Sintassi | Permesso | Cosa fa |
|---|---|---|---|
| `@create` | `create[/drop] <nome>[;alias;alias...][:typeclass]` | Builder | Crea uno o più nuovi oggetti, opzionalmente come istanza di una typeclass specifica. `/drop` lo deposita subito nella propria posizione invece che nel proprio inventario. |
| `@desc` | `desc[/edit] [<obj> =] <descrizione>` | Builder | Imposta la descrizione di un oggetto (o della stanza attuale, se omesso). `/edit` apre un editor di riga persistente (EvEditor) per testi lunghi. |
| `@destroy` (`@delete`, `@del`) | `destroy[/override/force] [obj, obj2, [dbref-dbref], ...]` | Builder | Elimina definitivamente uno o più oggetti, anche per intervalli di dbref. Chiede conferma salvo `/force`; per default rifiuta di eliminare oggetti posseduti da un account attivo (serve `/override`) e protegge sempre `settings.DEFAULT_HOME`. |
| `@dig` | `dig[/teleport] <stanza>[;alias][:typeclass] [= <uscita>[,<uscita_ritorno>]]` | Builder | Crea una nuova stanza e, opzionalmente, un'uscita verso di essa e una di ritorno dalla posizione attuale. `/teleport` sposta subito il chiamante nella stanza appena creata. |
| `@tunnel` (`@tun`) | `tunnel[/oneway/tel] <direzione>[:typeclass] [= <nomestanza>]` | Builder | Scorciatoia di `@dig` limitata alle direzioni cardinali/verticali/dentro-fuori (nord, sud, su, giù, dentro, fuori...), con i nomi delle uscite già tradotti in italiano. `/oneway` non crea l'uscita di ritorno. |
| `@link` | `link[/twoway] <oggetto> [= <bersaglio>]` | Builder | Imposta la destinazione di un'uscita esistente. Senza lato destro mostra la destinazione attuale; con `=` vuoto la azzera (come `unlink`). `/twoway` collega a due vie due uscite già esistenti. |
| `unlink` | `unlink <oggetto>` | Builder | Scollega un'uscita dalla sua destinazione (sottoclasse di `@link` con il lato destro forzato a vuoto). |
| `@sethome` | `sethome <obj> [= <posizione_home>]` | Builder | Imposta la "home" di sicurezza di un oggetto: la posizione in cui viene rispedito se la sua posizione attuale smette di esistere. |
| `@name` (`@rename`) | `name <obj> = <nuovonome>;alias1;alias2` | Builder | Rinomina un oggetto e/o gli assegna alias. Con `*nomeaccount` rinomina invece un account. |
| `@open` | `open <uscita>[;alias][:typeclass][,<uscita_ritorno>] = <destinazione>` | Builder | Apre una nuova uscita dalla stanza attuale verso la destinazione indicata, con uscita di ritorno opzionale. |

## Costruzione del mondo: attributi, typeclass e prototipi

Comandi più avanzati, da `commands/cthulhu_building_advanced.py`.

| Comando | Sintassi | Permesso | Cosa fa |
|---|---|---|---|
| `@alias` (`setobjalias`) | `alias[/category/delete] <obj> [= alias[,alias,...]]` | Builder | Gestisce gli alias permanenti di un oggetto (diversi dai nick personali creati con `nick`: questi modificano l'oggetto stesso, visibili a chiunque). `/category` li raggruppa sotto una categoria; `/delete` rimuove un alias specifico. |
| `@copy` | `copy <originale> [= <nuovonome>[;alias][:posizione][,<nuovonome2>...]]` | Builder | Duplica un oggetto e le sue proprietà. Senza bersaglio esplicito crea una copia chiamata `*_copy`. |
| `@cpattr` | `cpattr[/move] <obj>/<attr> = <obj1>/<attr1>[,...]` | Builder | Copia un attributo da un oggetto a uno o più altri. `/move` lo elimina dalla sorgente dopo la copia (equivale a `@mvattr`). |
| `@mvattr` | `mvattr[/copy] <obj>/<attr> = <obj1>/<attr1>[,...]` | Builder | Sposta un attributo tra oggetti; è un semplice wrapper su `@cpattr`/move. |
| `@set` | `set[/switch] <obj>/<attr>[:categoria] = <valore>` | Builder | Imposta, elimina (`=` vuoto) o mostra (senza `=`) un attributo su un oggetto o, con `*account`, su un account. Accetta anche strutture Python primitive (liste, dizionari, tuple) e riferimenti a oggetti tramite `$dbref(#nn)` o `$search(chiave)`. Switch dedicati per script, canali, account e ricerca globale per stanza/uscita/personaggio. |
| `@typeclass` (`@type`, `@parent`, `@swap`, `@update`, `@typeclasses`) | `typeclass[/switch] <oggetto> [= percorso.typeclass]` | Builder | Mostra o cambia la typeclass di un oggetto. `/update` riesegue solo la creazione iniziale; `/reset` ripulisce tutti gli attributi rendendolo di fatto nuovo; `/prototype` lo sovrascrive con un prototipo salvato; `/list` elenca le typeclass disponibili. |
| `@wipe` | `wipe <oggetto>[/<attr>[/<attr>...]]` | Builder | Elimina tutti gli attributi di un oggetto, o solo quelli indicati. |
| `@lock` (`@locks`) | `lock <oggetto o *account> [= <stringa_di_lock>]` | Builder | Imposta o mostra le stringhe di lock (i permessi di accesso, es. `get: id(25) or perm(Admin)`) di un oggetto o account. Più tipi di accesso si separano con `;`. `/del` rimuove un tipo di accesso. |
| `@spawn` (`@olc`) | `spawn[/switch] <chiave_prototipo>` oppure `spawn <dizionario_prototipo>` | Builder | Genera oggetti da un prototipo salvato o definito inline. Include un intero sotto-set di switch per cercare (`/search`), elencare (`/list`), ispezionare (`/show`), salvare (`/save`), aggiornare oggetti già generati (`/update`) o aprire un editor a menu (`/edit`, alias `olc`). |

## Debug e sviluppo

Sempre da `cthulhu_building_advanced.py`: strumenti di ispezione del database e dello stato del server, più utili in fase di sviluppo/debug che di building quotidiano.

| Comando | Sintassi | Permesso | Cosa fa |
|---|---|---|---|
| `@examine` (`@ex`, `@exam`) | `examine [<oggetto>[/attributo]]` | Builder | Mostra informazioni dettagliate su un oggetto (attributi, permessi, lock, typeclass, cmdset...) e, opzionalmente, su un singolo attributo. Con `*account` esamina un account; switch per script e canali. Senza argomenti esamina la stanza attuale. |
| `@find` (`@search`, `@locate`) | `find[/switch] <nome o dbref o *account> [= dbrefmin[-dbrefmax]]` | Builder | Cerca nel database un oggetto per nome (parziale o esatto) o dbref, opzionalmente ristretto a un intervallo di dbref. Filtri per tipo (`room`, `exit`, `char`); `/loc` mostra anche la posizione del risultato. |
| `@tag` (`@tags`) | `tag[/del/search] <obj> [= <tag>[:categoria]]` | Builder | Assegna, elenca o rimuove tag di raggruppamento su un oggetto; `/search` trova tutti gli oggetti con un dato tag. Usati internamente anche dal sistema di popolamento delle zone (`world/popola_mostri.py`). |
| `@scripts` (`@script`) | `script[/switch] [oggetto, chiave, percorso.script]` | Builder | Elenca tutti gli script (timer) attivi nel gioco, oppure quelli assegnati a un oggetto specifico. Permette di creare, avviare, fermare, mettere in pausa o eliminare script globali o legati a un oggetto. |
| `@objects` | `objects [<nr>]` | Builder | Statistiche di massima sul database: quanti personaggi, stanze, uscite e altri oggetti esistono (in percentuale sul totale) e l'elenco degli ultimi `<nr>` oggetti creati (default 10). |
| `@teleport` (`@tel`) | `tel[/switch] [<oggetto> to||=] <posizione bersaglio>` | Builder | Teletrasporta un oggetto (o se stessi, se non ne viene indicato uno) altrove. Rispetta i lock `teleport` (sull'oggetto spostato) e `teleport_here` (sulla destinazione), ma Admin e permessi superiori li superano sempre. `/tonone` sposta l'oggetto fuori da qualunque posizione (recuperabile solo per dbref). |

## Poteri e comodità immortali

Comandi specifici di CthulhuMUD (non del toolkit generico Evennia), da `commands/cthulhu_staff.py`, confermati dal catalogo ufficiale della fonte per livello immortale (`immhelp_commands.txt`) e dalle singole pagine `helps/<comando>.txt`. Vedi la nota a inizio capitolo sulla scelta di mappare i sei gradi nominali della fonte sui tre permessi Evennia.

| Comando | Sintassi | Permesso | Cosa fa |
|---|---|---|---|
| `holylight` | `holylight` | Builder | Alterna una comodità da staff: mentre attivo, nessuna oscurità né invisibilità nasconde più nulla a chi la usa. |
| `restore` | `restore` \| `restore room` \| `restore <personaggio>` \| `restore all` | Admin (`all` richiede Developer) | Ripristina HP/mana/movimento al massimo e cura veleno, peste e cecità. Senza argomenti (o con `room`) agisce su tutti i presenti nella stanza; con un bersaglio, solo su di lui; `all` su ogni personaggio attualmente connesso. Nella fonte (`helps/restore.txt`) era riservato ai soli Immortali di 300° livello: qui riservato al permesso più alto per la stessa cautela. |
| `advance` | `advance <personaggio> <livello>` | Developer | Alza o abbassa il livello di un personaggio, assegnando (o ritirando) i guadagni di train/practice/HP/mana/movimento/skill normalmente ottenuti salendo di livello. |
| `slay` | `slay <personaggio>` | Admin | Uccide un bersaglio all'istante: nessun tiro, classe armatura o magia difensiva può salvarlo. Non utilizzabile su se stessi. |
| `freeze` | `freeze <personaggio>` | Admin | Alterna il blocco dei comandi in ingresso di un personaggio: chi è congelato continua a vedere ciò che accade intorno a sé ma non può più agire, finché non viene scongelato richiamando di nuovo il comando. |
| `peace` | `peace` | Builder | Ferma immediatamente tutti i combattimenti in corso nella stanza attuale. |
| `wizinvis` | `wizinvis` | Builder | Alterna l'invisibilità totale verso i mortali, ovunque nel gioco (disattiva `cloak` se era attivo). |
| `cloak` | `cloak` | Builder | Alterna l'invisibilità verso chi non condivide la stessa stanza (disattiva `wizinvis` se era attivo). |
| `wizlock` | `wizlock` | Admin | Alterna il blocco degli accessi ai soli account con permesso Builder o superiore — da usare in caso di bug gravi, mentre si interviene. |
| `newlock` | `newlock` | Admin | Alterna il blocco della creazione di nuovi personaggi. |
| `switch` | `switch <npc>` | Admin | Prende temporaneamente il controllo diretto di un NPC (mai di un personaggio giocante, per esplicita scelta della fonte). `return` per tornare al proprio personaggio. Il lock di puppet viene ristretto al solo account chiamante, cosí da non lasciare l'NPC "aperto" ad altri per errore — lo stesso schema usato per MINDTRANSFER (`commands/cthulhu_yithian.py`). |
| `incarnate` | `incarnate` | Admin | Alterna uno stato di roleplay: disattiva `wizinvis`/`cloak` e ne segnala l'ingresso in gioco "da mortale". Semplificazione dichiarata rispetto alla fonte: qui non esiste un'invulnerabilità automatica per lo staff da rimuovere, quindi il comando non toglie protezioni che non esistono. |
| `goto` | `goto <stanza o personaggio>` | Builder | Teletrasporto istantaneo, con messaggi di arrivo/partenza personalizzabili tramite `bamfin`/`bamfout` se impostati. |
| `bamfin` / `bamfout` | `bamfin [<testo>]` / `bamfout [<testo>]` | Builder | Impostano il messaggio personalizzato di arrivo/partenza mostrato dagli altri quando si usa `goto`. Senza argomenti ripristinano il messaggio di default. |
| `permapk` | `permapk` | Developer | Attiva/disattiva la modalità permadeath in tutto il gioco: con questa attiva, la morte di un **giocatore** ne cancella per sempre il personaggio dal database. Riservato nella fonte ad autorità di livello Implementor; da maneggiare con estrema cautela. |

## Gestione PK: taglie, missioni e toggle automatici

Il sistema di PK/criminalità/taglie vive in `world/pk.py` e `commands/cthulhu_pk.py`. L'unico comando di *quella* famiglia che richiede un permesso da staff è `permapk`, già descritto sopra: attiva o disattiva il permadeath per l'intero gioco. Tutto il resto in `cthulhu_pk.py` (`murder`, `bounty`, `mission`, `deliver`) è gioco normale, aperto a chiunque (`cmd:all()`), e non rientra in questa appendice.

Vale però la pena segnalare allo staff i toggle personali **AUTO\*** — anch'essi `cmd:all()`, quindi impostabili da qualunque giocatore su se stesso, non comandi da staff — perché fanno parte dello stesso sottosistema di morte/PK e perché il loro stato incide su cosa lo staff osserva succedere ai personaggi:

| Comando | Sintassi | Cosa fa |
|---|---|---|
| `autogold` | `autogold` | Alterna il prelievo automatico dell'oro dalle proprie uccisioni. Semplificazione dichiarata (`helps/autokill.txt`): questo porting non fa mai cadere oro dall'uccisione di un mostro (l'oro arriva solo da taglie/missioni), quindi il toggle è tracciato ma per ora non ha effetto pratico — pronto per quando (e se) un sistema di bottino in oro verrà costruito. |
| `autoloot` | `autoloot` | Alterna il prelievo automatico dell'equipaggiamento dalle proprie uccisioni. Stessa semplificazione dichiarata: gli NPC non mettono ancora il proprio equipaggiamento nel cadavere alla morte. |
| `autokill` | `autokill` | Alterna se tentare di uccidere invece di stordire i nemici in combattimento. Semplificazione dichiarata: questo porting non ha mai avuto una risoluzione "stordisci senza uccidere" — 0 HP resta sempre morte reale, a prescindere dal toggle. |
| `noloot` | `noloot` | Alterna se il proprio cadavere può essere saccheggiato anche dal proprio gruppo (di default è già protetto da chiunque altro, per `helps/death.txt`). |
| `autosac` | `autosac` | Alterna il sacrificio automatico del cadavere delle proprie uccisioni. Confermato dalla fonte (`helps/autokill.txt`/`helps/sacrifice.txt`): richiede di adorare già una divinità (`worship <divinita>`); i sacrifici automatici non aumentano la pietà. |
| `autolist` | `autolist` | Mostra lo stato corrente di tutti i toggle automatici del personaggio (inclusi `autosplit` e `autoassist`, gestiti altrove nel codice). |

## Filosofia di building del bestiario

La fonte originale di CthulhuMUD costruiva ogni comportamento di NPC con un vero motore di scripting generico integrato nel server: **MOBprogram**. Un builder senza accesso al codice C del mud poteva, tramite l'OLC (*On-Line Creation*, l'editor testuale in gioco), scrivere **script** composti da comandi dedicati (le decine di istruzioni `MPxxx` documentate in `immhelp_mobcommands.txt` — `MPECHO`, `MPKILL`, `MPTRANSFER`, `MPQUEST`, `MPHURT`, `MPSANITY` e molte altre) e agganciarli a **trigger** (`immhelp_triggers.txt`): eventi di tipo "sfida" (che potevano impedire un'azione altrui) o "reazione" (che scattavano dopo che qualcosa era già successo), a loro volta filtrabili con **condizioni** (`immhelp_conditions.txt`: confronti su livello, allineamento, fase lunare, ora del gioco, inventario del bersaglio...) valutate contro un **contesto** (`immhelp_contexts.txt`) derivato da un **evento** (`immhelp_events.txt`) generato e instradato dal motore del mud a ogni azione rilevante. A completare il quadro, i **flag** (`immhelp_flags.txt`) impostavano i comportamenti di base del mob (sentinella, aggressivo, vaga per l'area...) senza bisogno di scrivere nessuno script, e i **reset** (`immhelp_resets.txt`) governavano quando e quanti esemplari ricomparissero in un'area dopo che i giocatori l'avevano ripulita.

Questo porting **non reimplementa quel motore**. Non esiste un linguaggio di scripting dedicato ai mob, non esiste un editor OLC in gioco per scrivere trigger/condizioni/script, e non esiste un formato dati separato che descriva un mostro senza toccare codice Python. I comportamenti dei nemici sono scritti direttamente in Python, in due file:

- **`world/mostri.py`**: contiene il dizionario `BESTIARIO`, con una voce per ogni tipo di mostro (chiave testuale, es. `"ghoul"`, `"cane_di_tindalos"`). Ogni voce definisce nome, descrizione, livello, HP, allineamento, orrore/tipo di orrore, skill di combattimento e una manciata di campi che traducono in dati i flag della fonte: `attacca_a_vista` (equivalente ad AGGRESSIVE), `non_morto`, `sentinella` (equivalente a SENTINEL), `wimpy_soglia` (equivalente a WIMPY), `insegue_chi_fugge` (equivalente a HUNTER/TRACKER), `sensibile_luna` (bonus se evocato sotto l'omonima condizione di mondo `moon` già usata altrove) e `frasi_ambiente` — l'equivalente in spirito di `MPECHO`, ma come semplice lista di battute testuali invece che come istruzione di uno script generico. La funzione `crea_mostro()` nello stesso file istanzia un NPC a partire da una chiave del dizionario.
- **`world/mostri_movimento.py`**: implementa il pattugliamento/vagabondaggio periodico (equivalente al comportamento "non-SENTINEL" della fonte: a ogni tick, una probabilità casuale di spostarsi in un'uscita valida) e la recita occasionale di una `frase_ambiente` quando il mostro non si sposta.

La scelta è deliberata, non un compromesso per mancanza di tempo: il motore MOBprogram/trigger/condizioni della fonte esiste per servire un pubblico di **builder che non toccano il codice sorgente del mud** — spesso volontari con accesso solo all'OLC, mai al C sottostante. Questo progetto non ha quel pubblico: esiste un solo sviluppatore, che è anche l'unico "builder" possibile, e ha già accesso completo al codice Python del gioco. Costruire un intero linguaggio di scripting dati (parser, VM, editor OLC dedicato) per essere poi l'unico a scriverci contenuto sarebbe overhead puro, senza nessun beneficio pratico: lo stesso risultato si ottiene aggiungendo una voce a un dizionario Python.

**Implicazione pratica per chi vorrà aggiungere un nuovo mostro in futuro**: non esiste (e non è previsto) un comando in gioco tipo `MEDIT` o un equivalente OLC per creare nemici. Occorre invece:

1. Aprire `world/mostri.py` e aggiungere una nuova voce al dizionario `BESTIARIO`, seguendo lo schema delle voci esistenti (nome, descrizione, statistiche, skill, e gli eventuali campi opzionali di comportamento elencati sopra).
2. Se il mostro richiede un comportamento di movimento o reazione che i campi esistenti non coprono già (qualcosa di più elaborato di "vaga, insegue chi scappa, recita battute a caso, è sensibile alla luna piena"), estendere direttamente `world/mostri_movimento.py` (o il punto del codice di combattimento pertinente) con la nuova logica in Python — non esiste un modo dati-soltanto per farlo.
3. Popolare il mondo con il nuovo mostro tramite il sistema di popolamento/reset dell'area (`world/popola_mostri.py` e affini), che richiama `crea_mostro()` con la nuova chiave.

In altre parole: **aggiungere un mostro è una modifica di codice**, sottoposta allo stesso ciclo di revisione/deploy di qualunque altra funzionalità del gioco, non un'attività di "contenuto" separata riservata a un ruolo di builder senza accesso al sorgente — perché quel ruolo, in questo progetto, semplicemente non esiste.

## Salute del server: il controllo del "battito"

Dieci secondi dopo ogni avvio, il gioco verifica da solo che i sei
**script globali** — quelli che fanno letteralmente battere il cuore del
mondo — stiano davvero girando: rigenerazione di HP/mana/movimento,
fame e sete, ripopolamento dei mostri, vagabondaggio dei mostri,
cristalli focus e interesse bancario. Se ne trova uno fermo, lo riavvia
e lascia nel log una riga di avviso come questa:

```
[WW] battito: RigenerazioneScript era fermo (nessun timer armato) ed e' stato riavviato.
```

**Vedere questa riga non è di per sé un allarme**: è il controllo che
fa il proprio lavoro. Nella configurazione attuale compare in modo
sistematico per `RigenerazioneScript` dopo ogni riavvio, perché quello
script si ri-arma da solo con un intervallo casuale (15-45 secondi, come
da fonte) e il motore non lo ripristina spontaneamente dopo un riavvio.
Se invece la riga comparisse per **altri** script globali, varrebbe la
pena indagare: significherebbe che qualcos'altro si è inceppato.

Il motivo per cui questo controllo esiste merita di essere conosciuto da
chi amministra il gioco. Un difetto di questa famiglia è **silenzioso**:
uno script può risultare "attivo" in ogni interrogazione al database e
al tempo stesso non avere alcun timer in funzione, quindi non eseguirsi
mai. Prima del rilascio in beta era esattamente la condizione in cui si
trovava la rigenerazione: nessun personaggio recuperava HP, mana o
movimento, e nulla nell'interfaccia lo segnalava.

Da qui due regole pratiche per chi diagnostica problemi:

- **Il campo "attivo" di uno script non è una prova che stia girando.**
  L'unica verifica attendibile è che manchi poco al suo prossimo scatto
  (`time_until_next_repeat()` diverso da "nessuno").
- **Le verifiche sugli script vanno fatte dentro il server in esecuzione**
  (per esempio con `@py` da una sessione di gioco), non da una shell
  separata: una shell non condivide i timer del processo del server e
  mostrerebbe come fermi anche script perfettamente sani.

Allo stesso avvio il gioco elimina anche gli script effimeri rimasti
orfani del proprio oggetto (per esempio quelli di un cadavere nel
frattempo rimosso), che altrimenti produrrebbero errori quando scattano.

## Ricostruire il mondo dal codice

Il mondo di CthulhuMUD è stato costruito nel tempo chiamando a mano, una
per una, decine di funzioni sparse nei moduli di `world/`. Finché il
database esiste la cosa non si nota; ma se il database andasse perso,
l'ordine di quelle chiamate esisterebbe solo nella memoria di chi le ha
fatte. Il comando `costruiscimondo` mette quell'ordine per iscritto, in
forma eseguibile:

- `costruiscimondo` esegue tutte le fasi di costruzione e popolamento;
- `costruiscimondo/elenco` mostra le fasi senza eseguirle.

Il comando è **idempotente**: su un mondo già costruito non crea nulla.
Questo lo rende anche uno strumento di verifica, perché qualunque
oggetto creato segnala qualcosa che nel mondo manca rispetto a ciò che
il codice prevede. Alla sua prima esecuzione, per esempio, ha fatto
comparire un sergente di polizia che nel Commissariato non c'era mai
stato.

Il mondo è stato ricostruito per intero a partire da un database vuoto,
ottenendo **240 stanze e 488 uscite identiche** a quelle del mondo in
esercizio, senza un solo errore. Le poche differenze residue sono scorie
di gioco e di collaudo (oggetti di prova, equipaggiamento generato
durante i test, un mostro che aveva vagato fuori dalla propria stanza),
non contenuto mancante.

### Tre trappole che il modulo disinnesca

Chi dovesse ricostruire il mondo a mano incontrerebbe tre insidie, tutte
documentate in `world/costruisci_mondo.py`:

1. Esistono **tre funzioni diverse chiamate `popola_tutto()`**, in
   `popola_mostri`, `popola_scenografia` e `popola_scenografia_arkham`,
   e coprono cose diverse. Chiamarne una sola sembra aver fatto tutto.
2. `popola_mostri.popola_tutto()` **non è idempotente**: rigenera
   l'intera tabella di reset a ogni chiamata, aggiungendo una settantina
   di mostri per volta. Per ripopolare un mondo esistente si usa
   `repop.popola_tutte_le_zone_mancanti()`, che crea solo ciò che manca.
3. I popolatori di NPC di ambientazione saltano una stanza se contiene
   già **un NPC qualsiasi** — e i mostri sono NPC. Vanno quindi eseguiti
   *prima* dei mostri, altrimenti gli NPC di ambientazione delle stanze
   contese non nascono affatto.

L'ordine delle fasi tiene conto anche delle dipendenze fra zone: gli hub
newbie per primi, le Dreamlands dopo Ulthar e Zoog che collegano,
l'aggancio degli hub al mondo per ultimo. Una seconda passata sulla
topologia chiude eventuali collegamenti rimandati; se crea qualcosa,
significa che l'ordine va rivisto, e il comando lo segnala.

## Audit approfondito: tre difetti silenziosi

Un audit successivo alla ricostruzione del mondo ha cercato
sistematicamente le classi di difetto che il porting aveva gia' incontrato
in passato. Ne sono emersi tre, tutti invisibili nell'uso normale: nessuno
produceva un messaggio d'errore, e ciascuno richiedeva di trovarsi in una
situazione precisa per accorgersene.

### La trappola del Riformatorio di Dylath-Leen

Sette hub di nascita su otto davano almeno un'uscita alle proprie stanze
di respawn e obitorio. Il Riformatorio di Dylath-Leen no: non avendo un
modulo d'area che glieli collegasse, l'Infermeria e la Camera Mortuaria
erano rimaste **senza alcuna uscita**. Le conseguenze erano due:

- chi moriva con una professione di Dylath-Leen veniva teletrasportato
  nell'Infermeria e vi restava chiuso per sempre — non esiste un comando
  RECALL, e l'unica via d'uscita sarebbe stata Parola di Richiamo, che un
  neofita appena morto non conosce e non avrebbe il mana per lanciare;
- il cadavere finiva nella Camera Mortuaria, altrettanto irraggiungibile:
  tutto cio' che il personaggio portava con se' spariva dal gioco.

La correzione non e' una toppa per Dylath-Leen ma un invariante generale
(`world/rooms_newbie.py:collega_ruoli_isolati_agli_hub`): nessuna stanza in
cui il gioco puo' spedire un giocatore o il suo cadavere deve essere priva
di uscite. La funzione interviene solo dove non c'e' *nessuna* uscita,
cosi' non disturba gli hub gia' collegati, e vale anche per gli hub che
verranno aggiunti in futuro.

### La Saggezza che non contava nulla

Il tiro salvezza contro gli incantesimi e' descritto come "Autodisciplina
piu' meta' della Saggezza". Leggeva pero' `db.wis`, un attributo che
nessuno scrive mai: gli attributi del personaggio stanno in
`attributes.get("stat_<nome>", category="cthulhu")` e si leggono con
`valore_attributo()`. Il ripiego faceva si' che la Saggezza valesse
**sempre 10 per chiunque**: un personaggio con Saggezza 18 resisteva alla
magia esattamente come uno con Saggezza 3. Lo stesso errore era presente
nel viaggio onirico (`commands/cthulhu_dream.py`).

Dopo la correzione, misurato dal vivo su 600 tiri per parte: 414
resistenze con Saggezza 18 contro 382 con Saggezza 3.

### Nove cure che lasciavano righe morte

La regola "usa `.delete()` e MAI `.stop()`" — in Evennia 6.1 `.stop()`
disattiva lo script ma ne lascia la riga nel database — era gia'
documentata e applicata in `world/effetti.py`, `world/sottorazze.py` e
`typeclasses/living.py`. In `world/magic.py` era invece rimasta
disattesa in nove punti, e in `world/staff.py` in due: ogni Cura Veleno,
Cura Malattia, Spezza Maledizione, Giovinezza, Dissolvi Magie e ogni
RESTORE da staff lasciava dietro di se' una riga inerte, per sempre.

### Cosa NON era un difetto

Vale la pena registrare anche i falsi allarmi, perche' torneranno a
sembrare difetti a chi rileggera' il codice:

- le skill senza `descrizione` sono quelle che sono anche incantesimi: il
  testo arriva da `SPELLS` tramite `descrizione_skill()`;
- `db.negozio` **e'** il listino del mercante, non un flag, ed Evennia lo
  restituisce come `_SaverList`, che non e' una sottoclasse di `list`;
- `NOFOLLOW` non smette di seguire qualcuno: rifiuta nuovi seguaci. Per
  smettere si usa `FOLLOW ME`, come nella convenzione DikuMUD;
- l'esperienza da uccisione e' subordinata a `active_profession`, quindi
  un personaggio creato a mano senza professione non ne guadagna: e' una
  guardia voluta;
- Limbo resta senza uscite e irraggiungibile: e' la stanza di default di
  Evennia, deliberatamente fuori dal mondo di gioco.

## Lo strato italiano dei comandi, e il rischio che nasconde

I nomi italiani dei comandi stanno in due tabelle:
`world/comandi_italiano.py` (127 alias per 163 comandi di gioco) e
`world/socials_italiano.py` (204, uno per social). Gli alias vengono
applicati a fine `at_cmdset_creation()`, quando tutti i comandi sono già
stati aggiunti.

Non basta appendere a `cmd.aliases`: Evennia costruisce da chiave e alias
due strutture di ricerca (`_matchset` e `_keyaliases`) al momento della
definizione della classe, ed è su quelle che avviene la corrispondenza.
Per questo `applica_alias_italiani()` richiama `_init_command()` dopo
avere aggiunto i nomi. Senza quel passaggio gli alias comparirebbero
nell'elenco e non verrebbero mai riconosciuti — un guasto che sembra
funzionare finché non lo si prova davvero.

### Il rischio: un'uscita vince sempre su un comando

In Evennia il cmdset di un'uscita ha priorità **101**, quello del
personaggio **0**. Un alias che si chiami come un'uscita del mondo viene
quindi oscurato in ogni stanza che ha quell'uscita — e in silenzio,
senza alcun messaggio d'errore.

Non è teoria: il primo giro di traduzione proponeva `taglie` per BOUNTY e
`missione` per MISSION, e sono esattamente i nomi di due uscite (verso
l'Ufficio Taglie nel Riformatorio di Dylath-Leen, e su Via Federal Nord).
Entrambi avrebbero rotto il comando senza dirlo. Sono diventati
`cacciataglie` e `missioni`.

Per questo esiste `verifica_collisioni()`, che confronta tutti i 331
alias con i nomi delle uscite realmente presenti nel mondo, con i nomi
già occupati nei cmdset e fra loro. L'audit la esegue: se un domani
qualcuno costruisce un'uscita chiamata `guarda`, il controllo lo segnala
prima che diventi un difetto.

## Dati GMCP per i client grafici

Il server manda due pacchetti fuori banda (`world/gmcp.py`):

- `Room.Info` a ogni cambio di stanza — numero, nome, area e uscite;
- `Char.Vitals` al login e a ogni variazione di vita — HP, mana,
  movimento e sanità mentale.

`session.msg(room_info=((), dati))` diventa il pacchetto GMCP `Room.Info`
da solo: Evennia trasforma gli underscore in punti e mette le iniziali
maiuscole. Non serve alcuna modifica a Evennia, basta scegliere il nome
giusto per l'outputfunc.

Le uscite vengono mandate **divise in due campi**, `exits` per quelle
cardinali e `specials` per quelle con nome proprio, perché nel nostro
mondo il 54% è del secondo tipo e un client non ha modo di distinguerle
da solo. Il pacchetto Mudlet in `client/mudlet/` dispone le prime sulla
griglia e tratta le seconde come collegamenti speciali.

## Audit totale: eseguire tutto, non solo leggerlo

Gli audit precedenti controllavano strutture dati, metadati e un campione
di meccaniche dal vivo. Questo ha fatto un passo in più: **eseguire
davvero** ogni parte del gioco dentro il server, e leggere i log della
partita reale.

| cosa | quante esecuzioni | esito |
|---|---|---|
| ogni comando, social compresi, senza argomenti e su un bersaglio | 768 | un solo traceback residuo, voluto (vedi sotto) |
| ogni incantesimo, in ogni situazione raggiungibile da CAST | 696 | zero guasti |
| nascita di un personaggio per ciascuna professione di partenza | 16 | tutte in un hub completo e percorribile |
| meccaniche toccate dalle correzioni | 35 controlli | tutti superati |
| ricostruzione del mondo da un database vuoto | — | 240 stanze e 492 uscite identiche |
| analisi statica di tutto il codice (pyflakes) | — | zero nomi indefiniti |

Ogni corsa gira in una stanza temporanea con personaggi usa-e-getta,
annota l'id massimo del database prima di cominciare e alla fine cancella
tutto ciò che ha id superiore; poi confronta il numero di script, di voci
d'aiuto, di canali, di account e un'impronta di ServerConfig con quelli di
partenza. Una stanza cancellata sposta il proprio contenuto in Limbo invece
di distruggerlo: senza la pulizia per id, i residui dei test sarebbero
finiti lì.

### I difetti trovati

**Incantesimi che cancellavano personaggi.** Il più grave di tutti gli
audit. Consistenza, Permanenza, Universalità e Lama della Furia hanno
`bersaglio_richiesto=True` e non verificavano il tipo del bersaglio;
la funzione che simula il rischio di "distruggere l'oggetto" chiamava
`delete()` su qualunque cosa ricevesse. `CAST CONSISTENCE` senza argomenti
mirava al lanciatore stesso, e con una probabilità fra il 5 e il 35% il
personaggio veniva **cancellato dal database**; con un nome, poteva
cancellare un altro giocatore, senza tiro salvezza né protezione PK. È
emerso perché il personaggio di prova è sparito a metà della corsa.
Corretto su due livelli: il flag `solo_oggetti` in SPELLS, verificato da
`lancia_incantesimo` prima di scalare il mana, e la funzione
`e_oggetto_inanimato()` come ultimo argine dentro la funzione che
distrugge — usata anche da `sacrifica()`, che non era raggiungibile dal
comando (cerca solo nell'inventario) ma è chiamata anche da altri percorsi.

**Equipaggiamento duplicabile.** Nessuno toglieva un oggetto
dall'equipaggiamento quando lasciava il personaggio. Verificato dal vivo:
una corazza lasciata con DROP continuava a contare nella classe armatura,
una spada ceduta con GIVE restava impugnata anche da chi l'aveva data.
Corretto in un punto solo, `LivingMixin.at_object_leave`, che Evennia
chiama per qualunque uscita di un oggetto — DROP, GIVE, furti, contenitori,
e qualunque percorso futuro.

**Ventriloquio non si poteva lanciare.** È l'unico incantesimo che chiede
insieme un bersaglio e un testo, ma CAST gestiva solo l'uno o l'altro:
tutto ciò che seguiva il nome diventava testo, il bersaglio restava vuoto,
e il lancio veniva rifiutato. Ora la prima parola è il bersaglio.

**Il bersaglio in fuga veniva colpito comunque.** Se il bersaglio lasciava
la stanza durante i due secondi di canalizzazione, l'incantesimo lo
raggiungeva ovunque fosse. Ora si disperde, tranne per gli incantesimi a
raggio mondiale (lo stesso elenco con cui CAST decide di cercare il
bersaglio in tutto il mondo).

**Il Dr. Armitage senza punti vita.** L'unico istruttore di incantesimi
della stanza di partenza è fra i primissimi oggetti del mondo (`#29`),
creato prima che esistessero i valori di base degli NPC: aveva
`hp=None`. Ogni cura su di lui sollevava un errore, e `subisci_danno`
l'avrebbe ucciso al primo colpo — basta un neofita che provi *Presa
Folgorante*, che Armitage stesso insegna, proprio su Armitage. Il trigger
"Niente violenza nella sala di lettura" blocca solo KILL. Corretto con
`completa_default_mancanti()`, che assegna i valori di base solo ai campi
che mancano senza toccare gli altri, e che ora è una fase di
`costruiscimondo`: ha completato 183 entità nate prima di certi default.

**Sei incantesimi rotti sugli NPC.** Ristoro, Passo Leggero, Trasferisci
Mana, Cura Leggera, Falò Magico e Drena Vitalità facevano
`min(bersaglio.db.X_max, …)`, ma gli NPC non hanno mana, movimento né
sanità massimi. `CAST REFRESH <npc>` finiva in un errore. L'aiutante
`_ricarica()` tratta un massimo assente come "questa riserva non esiste".
Stesso difetto nel cibo magico dato con FEED a un NPC e nello script di
rigenerazione.

**Callback programmate su oggetti spariti.** Cinque `delay(N, x.delete)`
provavano a cancellare un oggetto già sparito — un alleato evocato ucciso,
il cibo creato per magia e poi mangiato prima dei suoi trenta minuti — e
tre callback (fine di Ammaliare, completamento del lancio, fine della
seduta di Psicologia) non controllavano che il personaggio esistesse
ancora. Tutto finiva nel log come "Unhandled error in Deferred".

**Un refuso dentro Evennia.** In `evennia/server/inputfuncs.py` la funzione
del `REPORT` MSDP contiene `kwargs["outputfunc_name":"report"]`, con i due
punti al posto di `] =`. Mudlet la invoca a ogni connessione: 14 errori nel
log in una settimana. Corretto nel nostro `server/conf/inputfuncs.py`, che
Evennia carica dopo il proprio e che sostituisce le funzioni omonime — una
patch dentro la libreria sparirebbe al primo aggiornamento. Nello stesso
file sono ora gestiti i quattro messaggi che Mudlet manda alla connessione
e che Evennia non riconosceva.

**Minori.** IGNORE e REPLY eseguiti da un NPC con ORDER (senza account);
lo schermo del personaggio casuale che non mostrava i modificatori della
professione; una guardia contro un arrivo senza argomenti nello stesso
schermo.

### Un errore dell'audit stesso

Per lanciare le corse mi collegavo come admin e lo incarnavo. `ic admin`
lo faceva ricomparire dov'era — una via di Arkham con mostri erranti — e
mentre il server eseguiva le corse lo hanno attaccato: 45 punti vita, 11 di
sanità e 5 di esperienza persi. È stato ripristinato ai valori precedenti,
e da allora le corse si lanciano **fuori dal personaggio**: `@py` funziona
anche a livello di account, e il personaggio non entra mai in gioco. Le
tre suite dei turni precedenti che hanno bisogno di incarnarlo fotografano
prima lo stato di admin e lo ripristinano dopo, con verifica campo per campo.

### Cosa non era un difetto

- `@scripts manichino` registra un traceback **di proposito**:
  "manichino" non è uno script noto, il comando prova a crearne uno con
  quel percorso, fallisce e lo annota con `log_trace()` prima di rispondere.
- Le 183 entità senza `posizione` e `stati`, e le 78 senza `equip`, non
  rischiavano nulla: ogni lettura di quei campi è difesa con `or {}`.
- `/accounts/login/` e `/password-reset/` rispondono 404 perché non
  esistono: il login di Evennia sta in `/auth/login/`. Tutti gli 11 link
  realmente presenti nelle pagine pubbliche rispondono.

### Controlli che rendono irripetibili questi difetti

L'audit statico ha ora una sezione di regressioni: ogni incantesimo che
può distruggere il bersaglio deve essere marcato `solo_oggetti`; ogni
entità vivente deve avere i punti vita; un incantesimo che chiede
bersaglio e testo deve trovare CAST pronto a gestirlo; e nessuna
cancellazione programmata può essere un `delay(N, x.delete)` nudo — quest'ultima
analizzata sull'albero sintattico, perché una docstring che descrive il
vecchio difetto non deve far scattare il controllo.

## NPC di servizio intoccabili: dove sta la regola

La protezione è la proprietà `NPC.intoccabile` (`typeclasses/npcs.py`),
ricavata dal ruolo e non da un flag da ricordarsi: è vera per chi ha uno
degli attributi elencati in `NPC.RUOLI_INTOCCABILI`, ciascuno impostato
dal proprio script di popolamento.

| Ruolo | Attributo | Chi lo imposta | Nel mondo |
|---|---|---|---|
| mercante | `db.negozio` | gli script `popola_negozi*` | 52 |
| istruttore | `db.is_practice_trainer` | Dr. Armitage, Maro il fabbro | 2 |
| terapeuta | `db.terapeuta` | `world/popola_terapeuti.py` | 8 |
| albergatore | `db.albergatore` | `world/popola_alberghi.py` | 4 |
| impiegato dell'Ufficio Taglie | `db.impiegato_taglie` | `world/rooms_bounty_office.py` | 1 |

Oggi gli intoccabili sono 66, perché Maro il fabbro è sia mercante sia
istruttore. Nessuno dei 79 mostri del bestiario lo è. La prima versione
della regola copriva solo istruttori e mercanti; terapeuti, albergatori e
l'impiegato delle taglie sono stati aggiunti subito dopo, per la stessa
ragione: senza di loro un servizio del gioco sparisce. Un nuovo ruolo di
servizio si protegge aggiungendo il suo attributo a `RUOLI_INTOCCABILI`;
un singolo NPC qualunque, impostando `db.intoccabile = True` dal gioco,
senza toccare il codice.

Invece di bloccare i comandi uno per uno, la regola sta nei **punti di
passaggio obbligati**, così copre anche i percorsi che verranno aggiunti:

- `LivingMixin.subisci_danno` — tutte le morti del gioco passano da qui
  (armi, incantesimi, mosse speciali, vudù, effetti ad area, danni
  periodici), eccetto `SLAY` dello staff;
- `LivingMixin.avvia_combattimento` — un intoccabile non si ingaggia e non
  ingaggia mai nessuno;
- `world/pk.py:uccidi_o_murder` — il cancello di `KILL` e `MURDER`;
- `world/magic.py:lancia_incantesimo` — nessun incantesimo altrui, prima di
  scalare il mana; e `_infliggi_danno_magico`, l'aiutante di una trentina di
  incantesimi d'attacco, che li salta negli effetti ad area.

I pochi punti in più servono a dare un messaggio chiaro invece di un danno
annunciato e poi annullato: `_trova_bersaglio` delle mosse speciali (che
copre anche sgambetto, disarmo e terra negli occhi, che non fanno danno),
`tenta_bite`, `CUT` del vudù, `TAME`, `MINDTRANSFER`, `LICH DOMINATE`, e
Sommossa, che senza la guardia avrebbe reso il bottegaio ostile per sempre.

Il collaudo ha trovato un caso che solo l'esecuzione poteva mostrare:
`_infliggi_danno_magico`, dopo il danno, fa contrattaccare il bersaglio.
Con il danno annullato ma il contrattacco ancora attivo, un Terremoto
faceva entrare il mercante in combattimento contro il giocatore. Da qui la
regola che un intoccabile non ingaggia mai nessuno.
