# Iniziare a Giocare

## Connettersi

CthulhuMud si gioca tramite un client telnet (o tramite il client web integrato, se disponibile sul server a cui ti connetti). Alla connessione viene mostrata la schermata di benvenuto, che spiega i due comandi fondamentali:

```
connect <nomeutente> <password>
```

per accedere a un account già esistente, oppure

```
create <nomeutente> <password>
```

per crearne uno nuovo. Se il nome utente o la password contengono spazi, vanno racchiusi tra virgolette doppie.

Una volta creato l'account sei in stato **OOC** (Out Of Character, fuori dal personaggio): da qui puoi creare un nuovo personaggio con `charcreate`, eliminarne uno con `chardelete <nome>`, oppure entrare in gioco con uno già esistente tramite `ic <nome>` (o semplicemente `ic` per riprendere l'ultimo personaggio usato). Un account può gestire più personaggi.

## Creare un personaggio

Il comando `charcreate` avvia un menu guidato a più passaggi, che si può interrompere e riprendere in qualsiasi momento richiamando di nuovo `charcreate`. Ti vengono proposte tre modalità:

- **Guidata**: scegli tu, passo per passo, prima la razza e poi la professione di partenza (le professioni disponibili sono filtrate in base alla razza scelta, dato che non tutte le combinazioni razza/professione hanno senso narrativo).
- **Preimpostato**: scegli tra una serie di personaggi già pronti, uno per ogni professione di partenza disponibile — un modo rapido per iniziare subito senza passare per ogni scelta.
- **Casuale**: razza, professione, attributi e nome vengono tirati a caso per te. Se il risultato non ti convince puoi rigenerare tutto da capo quante volte vuoi, prima di accettarlo definitivamente.

In tutti e tre i casi, alla fine del processo ti viene sempre proposto un nome per il personaggio: puoi accettare quello suggerito o sceglierne uno tu. Il nome deve contenere solo lettere, essere lungo almeno tre caratteri, e non essere già preso — e "già preso" non significa soltanto da un altro giocatore: **non puoi chiamarti come un personaggio non giocante già esistente nel mondo**. Se scegli, per dire, il nome del gioielliere di Arkham, il gioco te lo rifiuterà con un messaggio dedicato. La ragione è concreta: in un mondo testuale ci si riferisce alle persone per nome, e due abitanti omonimi renderebbero ambiguo ogni `look`, `kill` o `give` rivolto a quel nome. Vale anche per i nomi proposti dalla modalità casuale, che vengono verificati con lo stesso criterio prima di esserti offerti.

La **professione di partenza** determina non solo il punto di partenza nel mondo (ogni professione ha una propria stanza/area di respawn e, in molti casi, una propria stanza MORGUE dove finiscono i tuoi cadaveri) ma anche l'insieme iniziale di skill allenabili. Cambiare professione più avanti nel gioco resta comunque sempre possibile (vedi il capitolo *Il Personaggio* per il comando PROF).

Al termine della creazione il personaggio parte con un piccolo pacchetto di risorse iniziali (HP, mana, movimento, qualche punto Practice/Train) pronto per essere allenato da subito.

## I primi comandi utili

Una volta in gioco, alcuni comandi ti torneranno utili da subito:

- `look` — mostra di nuovo la stanza in cui ti trovi.
- `score` — la tua scheda personaggio completa (attributi, HP/mana/movimento, sanity, valuta locale, eventuale divinità/pietà se già scelta una fede, eventuale sottorazza).
- `help` — l'indice degli argomenti di aiuto, organizzati per categoria.
- `help <comando>` — l'aiuto specifico su un comando.
- `who` — chi altro è connesso in questo momento.
- `quit` — esce dalla sessione corrente (o da tutte le sessioni, a seconda della sintassi usata).

I capitoli successivi di questo Codex approfondiscono ogni sistema di gioco nel dettaglio: razze e sottorazze, professioni e progressione delle skill, magia, combattimento, economia, comunicazione e i luoghi del mondo.

## I comandi si scrivono in italiano

Ogni comando del gioco si può scrivere **sia in italiano sia in inglese**:
sono lo stesso comando. `GUARDA` e `LOOK` fanno la stessa cosa, come
`ABBRACCIA` e `HUG`, `ATTACCA` e `KILL`, `SCHEDA` e `SCORE`.

I nomi inglesi vengono dalla fonte originale e restano validi per sempre:
chi li conosce già non deve reimpararli, chi comincia adesso non deve
impararli affatto.

### Il prontuario

Centosessanta comandi più duecento social sono tanti, e la pagina di
aiuto di uno alla volta non aiuta a farsene un'idea d'insieme. Per quello
c'è il prontuario:

| comando | cosa mostra |
|---|---|
| `comandi` | le categorie disponibili |
| `comandi <categoria>` | tutti i comandi di quella categoria, con descrizione |
| `comandi tutto` | l'elenco completo |
| `comandi cerca <parola>` | cerca fra nomi e descrizioni |

Per ogni comando il prontuario mostra il nome italiano, quello inglese
fra parentesi e una riga di descrizione. `PRONTUARIO` funziona come
sinonimo di `COMANDI`.

Resta valido `HELP <nome>` per l'aiuto completo di un singolo comando: il
prontuario dà la mappa, HELP dà il dettaglio.

### I social

I duecentoquattro social hanno anch'essi un nome italiano: `SORRIDI`,
`INCHINATI`, `PERNACCHIA`, `SBADIGLIA`, `ABBRACCIA`. Non compaiono nel
prontuario — sarebbero più numerosi di tutto il resto messo insieme — e
si consultano con `HELP`.

## Giocare con un client grafico: la mappa automatica

CthulhuMUD Redux si gioca benissimo con un semplice telnet, ma se usi
[Mudlet](https://www.mudlet.org/) il server è in grado di disegnarti la
mappa mentre cammini e di tenere quattro barre di stato sempre aggiornate.

Il pacchetto da importare si trova in `client/mudlet/` nel repository.

### Installazione

1. **Toolbox → Package Manager → Install**, e scegli
   `CthulhuMudRedux.xml`.
2. Riconnettiti. Deve comparire la riga *"CthulhuMUD Redux: pacchetto
   attivo"*.
3. Scrivi `mappa` per aprire la finestra della mappa.

Il GMCP in Mudlet 5 è acceso di serie: non c'è nulla da abilitare. La
prova che funzioni è immediata — se dopo il collegamento vedi i valori di
Vita e Mana nel pannello laterale, i dati stanno già arrivando.

### I comandi del pacchetto

| comando | cosa fa |
|---|---|
| `mappa` | apre (o riaggancia) la finestra della mappa |
| `mappadiag` | diagnostica: dice cosa arriva e dove si è inceppato |
| `barre on` | barre di stato in fondo, **con la Sanità mentale** |
| `barre off` | le nasconde (impostazione di partenza) |

Le barre in fondo sono spente di serie perché il pannello laterale di
Mudlet mostra già Vita, Mana e Movimento, e delle barre in basso
coprirebbero l'ultima riga di testo. Restano disponibili per un motivo
solo: il pannello laterale non conosce la Sanità mentale.

### Cosa fa

Il server manda fuori banda due pacchetti: la stanza corrente a ogni
spostamento (numero, nome, area e uscite) e i valori vitali al collegamento
e a ogni variazione. Il pacchetto li traduce in una mappa che si costruisce
da sola e in quattro barre — Vita, Mana, Movimento e Sanità mentale.

### Perché una parte della mappa resta storta

Nel mondo di CthulhuMUD poco più della metà delle uscite ha un **nome
proprio** (`tribunale`, `navata`, `fuori`) invece di una direzione
cardinale, e solo 69 stanze su 239 hanno esclusivamente uscite cardinali.
È una caratteristica del MUD originale, che questo porting ha conservato.

Mudlet sa disporre sulla griglia solo le direzioni cardinali. Il server
manda perciò le uscite **divise in due gruppi**, e il pacchetto le tratta
di conseguenza: le cardinali vanno sulla griglia, quelle con nome proprio
diventano collegamenti speciali — cliccabili e utilizzabili per lo
speedwalk, ma senza una posizione geometrica.

In pratica le vie di Arkham e il relitto dello U-29 vengono disegnati
ordinatamente, mentre gli interni degli edifici pendono di lato. Le stanze
si possono trascinare a mano dove si preferisce: Mudlet salva la posizione.

Un collegamento viene tracciato solo quando **entrambe** le stanze sono
già state visitate: finché non hai messo piede nella destinazione,
l'uscita esiste nel gioco ma non ancora sulla mappa.
