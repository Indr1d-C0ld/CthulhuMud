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
