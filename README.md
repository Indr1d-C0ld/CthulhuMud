# 🐙 CthulhuMud ITA Redux

**Porting italiano, fedele e open source, dello storico MUD lovecraftiano [CthulhuMUD](https://www.cthulhumud.com/)**, costruito sul motore [Evennia](https://www.evennia.com/) (Python/Twisted/Django).

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

---

## Indice

- [Cos'è questo progetto](#cosè-questo-progetto)
- [Fedeltà alla fonte e note legali](#fedeltà-alla-fonte-e-note-legali)
- [Caratteristiche principali](#caratteristiche-principali)
- [Giocare in italiano](#giocare-in-italiano)
- [Client grafici: mappa automatica per Mudlet](#client-grafici-mappa-automatica-per-mudlet)
- [Il Codex](#il-codex)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Primo avvio](#primo-avvio)
- [Ricostruire il mondo dal codice](#ricostruire-il-mondo-dal-codice)
- [Come viene collaudato](#come-viene-collaudato)
- [Distribuzione (systemd)](#distribuzione-systemd)
- [Struttura del progetto](#struttura-del-progetto)
- [Licenza](#licenza)

---

## Cos'è questo progetto

CthulhuMud ITA Redux ricostruisce da zero, in lingua italiana, le meccaniche e i contenuti dello storico MUD inglese CthulhuMUD, un mondo testuale multigiocatore ambientato nell'universo narrativo di H. P. Lovecraft. Nessun codice o testo del sito originale è stato copiato: la fonte è stata studiata in modo esaustivo (help file e guide pubbliche) per ricostruirne fedelmente regole e ambientazione, poi riscritta interamente su un motore moderno.

Il gioco è **classless** (crescita per skill, non per classi rigide), presenta una **sanità mentale** con vere conseguenze meccaniche (non un semplice numero cosmetico), **sottorazze permanenti** acquisibili in gioco (Lich, Vampiro, Licantropo), le **Dreamlands** come dimensione onirica esplorabile, un sistema di culto/sacrificio verso sette divinità del Mythos, e ambientazioni come Arkham e il Cairo ricostruite edificio per edificio.

## Fedeltà alla fonte e note legali

Ogni meccanica di questo porting rientra in una di due categorie, sempre dichiarate esplicitamente nei commenti del codice sorgente e nel [Codex](#il-codex):

- **Confermata dalla fonte**: attestata da un help file o una guida pubblica del sito originale (citato per riferimento).
- **Scelta di design del porting**: la fonte non specifica un dettaglio necessario per rendere la meccanica giocabile; il dettaglio è stato inventato per questo porting e dichiarato come tale.

Il corpus di ricerca usato durante lo sviluppo (una scansione della documentazione pubblica del sito originale) **non è incluso in questo repository pubblico** per ragioni di copyright, dato che non è materiale scritto da questo progetto.

## Caratteristiche principali

- Sistema di skill/progressione classless (PRACTICE, LEARN, DEBATE, TRAIN, RESEARCH) e REMORT (reincarnazione illimitata)
- 6 razze giocabili e 3 sottorazze permanenti (Lich, Vampiro, Licantropo), ciascuna con una propria disciplina di poteri
- Oltre 235 incantesimi
- Combattimento con Second/Third/Fourth Attack automatici, fuga, PK/taglie, PERMAPK opzionale
- Sanità mentale con azioni erratiche automatiche a bassa sanity
- IA dei mostri: aggro, assist tra mob, inseguimento multi-stanza, pattugliamento, sensibilità alla fase lunare
- Economia a 5 valute con cambio, banche, negozi, forgiatura d'armi/armature
- Società/Clan, gruppi con assist automatico, addomesticamento NPC
- **Istruttori e mercanti intoccabili**: nessun giocatore può ucciderli, stregarli o portarli via, così botteghe e scuole restano sempre aperte
- WORSHIP/SACRIFICE verso 7 divinità del Mythos
- Dreamlands esplorabili (Ulthar, Villaggio degli Zoog) con rischio di incubi
- Arkham (73 edifici) e il Cairo ricostruiti in dettaglio, raggiungibili l'uno dall'altro via nave
- Sistemi speciali: Yithian/Mindtransfer, bambole voodoo, Focus Crystal
- Interfaccia colorata a tema lovecraftiano (ANSI/Xterm256): rosso cupo per il pericolo, verde spettrale per orrore/magia, viola per le Dreamlands, grigio/ciano per l'ambientazione
- 204 comandi social/emote, canali OOC multipli, messaggistica privata
- **Comandi in italiano**: ogni comando si può scrivere in italiano o in inglese, e un prontuario in gioco (`COMANDI`) li elenca tutti per categoria con descrizione
- **Dati GMCP** per i client grafici: mappa automatica e barre di stato, con pacchetto Mudlet pronto in `client/mudlet/`
- **Il mondo è codice**: un unico punto d'ingresso (`COSTRUISCIMONDO`) ricostruisce le 240 stanze e le 492 uscite da un database vuoto

## Giocare in italiano

Il gioco è interamente in italiano: stanze, oggetti, messaggi e pagine di
aiuto. Anche i **comandi** hanno un nome italiano, che si affianca a quello
inglese ereditato dalla fonte: `GUARDA` e `LOOK` sono lo stesso comando,
come `ABBRACCIA` e `HUG` o `ATTACCA` e `KILL`. Nessun nome inglese è stato
rimosso, quindi chi li conosce già non deve reimpararli.

Centosessanta comandi più duecento social sono tanti, e la pagina di aiuto
di uno alla volta non aiuta a farsene un'idea d'insieme. Per quello c'è il
prontuario:

| comando | cosa mostra |
|---|---|
| `comandi` | le categorie disponibili |
| `comandi <categoria>` | i comandi di quella categoria, con descrizione |
| `comandi tutto` | l'elenco completo |
| `comandi cerca <parola>` | cerca fra nomi e descrizioni |

Il prontuario non duplica nulla: legge nomi, descrizioni e categorie dai
comandi stessi, quindi un comando aggiunto domani vi compare da solo.

## Client grafici: mappa automatica per Mudlet

Il server pubblica due pacchetti GMCP — la stanza corrente a ogni
spostamento e i valori vitali a ogni variazione — che un client grafico può
usare per disegnare la mappa e tenere delle barre di stato.

In [`client/mudlet/`](client/mudlet/) c'è un pacchetto pronto per
[Mudlet](https://www.mudlet.org/), confermato funzionante su Mudlet 5.0.1:
mappatura automatica mentre cammini,
barre di stato (Vita, Mana, Movimento, Sanità mentale) e tre comandi —
`mappa`, `mappadiag` per la diagnostica, `barre on|off`. Istruzioni in
[`client/mudlet/README.md`](client/mudlet/README.md).

Il pacchetto ha un proprio banco di prova (`prova_mapper.lua`), che rifà in
Lua puro le funzioni di Mudlet e ci fa passare dentro pacchetti GMCP veri
catturati dal server: verifica la logica del mappatore senza bisogno di
avere Mudlet installato.

Un avvertimento onesto sulla resa: poco più della metà delle uscite del
mondo ha un nome proprio (`tribunale`, `navata`, `fuori`) invece di una
direzione cardinale — è una caratteristica del MUD originale. Mudlet sa
disporre sulla griglia solo le direzioni cardinali, quindi il server manda
le uscite divise in due gruppi e il pacchetto tratta le altre come
collegamenti speciali: cliccabili e utilizzabili per lo speedwalk, ma senza
posizione geometrica. Le vie di Arkham e il relitto dello U-29 vengono
ordinati, gli interni degli edifici pendono di lato.

## Il Codex

[`codex/codex_cthulhumud.pdf`](codex/codex_cthulhumud.pdf) è il manuale di gioco completo: 147 pagine che coprono ogni sistema (personaggio, magia, combattimento, economia, luoghi, comunicazione, strumenti di staff), con fonti citate e distinzione esplicita fonte/scelta di design. Rigenerabile da sorgente con `bash codex/build.sh` (richiede `pandoc` e `weasyprint`).

## Requisiti

- Python 3.11+
- Le dipendenze elencate in `game/requirements.txt` (principalmente [Evennia](https://www.evennia.com/))

## Installazione

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r game/requirements.txt
cd game
evennia migrate
evennia start
```

Alla prima esecuzione ti verrà chiesto di creare un superuser. Per connetterti in gioco:

- **Telnet**: `localhost`, porta configurata in `game/server/conf/settings.py` (`TELNET_PORTS`)
- **Client web**: `http://localhost:4001` (porta di default Evennia; il sito web è servito sulla porta configurata in settings)

## Primo avvio

Il file `game/server/conf/secret_settings.py` (non incluso in questo repository, vedi `.gitignore`) può contenere segreti locali come le credenziali SMTP per la notifica email di nuove registrazioni — vedi i commenti in `game/server/conf/settings.py` per i placeholder e le istruzioni.

## Ricostruire il mondo dal codice

Il mondo non è un file di database da custodire: è codice. Il comando di
staff `COSTRUISCIMONDO` esegue, nell'ordine giusto, tutte le fasi di
costruzione e popolamento sparse in `game/world/`
(vedi `game/world/costruisci_mondo.py`).

È **idempotente**: su un mondo già costruito non crea nulla, il che lo
rende anche uno strumento di verifica — qualunque oggetto creato segnala
qualcosa che manca rispetto a ciò che il codice prevede.

Il mondo è stato ricostruito per intero a partire da un database vuoto,
ottenendo **240 stanze e 492 uscite identiche** a quelle in esercizio,
senza errori.

L'ultima fase è di manutenzione: completa gli attributi di base mancanti
di personaggi e NPC nati prima che certi valori predefiniti esistessero,
senza toccare quelli che un valore ce l'hanno già. È così che il Dr.
Armitage, l'istruttore della stanza di partenza, ha riavuto i punti vita
che non aveva mai avuto.

```
costruiscimondo           esegue tutte le fasi
costruiscimondo/elenco    mostra le fasi senza eseguirle
```

## Come viene collaudato

Il gioco è passato per più audit completi, l'ultimo dei quali non si è
limitato a leggere il codice ma ha **eseguito ogni sua parte** dentro il
server vivo, con personaggi usa-e-getta in stanze temporanee e un confronto
dello stato globale prima e dopo:

| cosa | esito |
|---|---|
| ogni comando, social compresi, senza argomenti e su un bersaglio (768 esecuzioni) | nessun errore imprevisto |
| ogni incantesimo in ogni situazione raggiungibile da `CAST` (696 esecuzioni) | nessun errore |
| un personaggio per ciascuna delle 16 professioni di partenza | tutti nascono in un luogo completo e percorribile |
| ricostruzione del mondo da un database vuoto | 240 stanze e 492 uscite identiche |
| analisi statica di tutto il codice | nessun nome indefinito |
| log della partita reale | letti e ricondotti alla causa uno per uno |

Quell'audit ha trovato e corretto, fra gli altri, un difetto grave: quattro
incantesimi pensati per gli oggetti potevano, con una certa probabilità,
**cancellare dal database il personaggio** su cui venivano lanciati — anche
quello di un altro giocatore. E un exploit di duplicazione: un'arma ceduta
a un compagno restava impugnata anche da chi l'aveva data.

Il resoconto completo, compresi i falsi allarmi e un errore commesso
dall'audit stesso, sta nel capitolo dello staff del
[Codex](codex/codex_cthulhumud.pdf).

## Distribuzione (systemd)

`deploy/systemd/` contiene le unit systemd pronte per l'uso (avvio al boot + watchdog di restart automatico) e uno script di installazione: vedi `deploy/systemd/install.sh`.

## Struttura del progetto

```
game/       codice del porting (Evennia): typeclasses, comandi, logica di gioco (world/)
codex/      sorgenti Markdown e PDF compilato del manuale di gioco
client/     pacchetti per i client di gioco (mappa automatica per Mudlet)
deploy/     unit systemd per l'esecuzione in produzione
```

## Licenza

Questo progetto è distribuito sotto licenza **GNU General Public License v3.0** — vedi [LICENSE](LICENSE). Costruito su [Evennia](https://www.evennia.com/), a sua volta rilasciato con licenza BSD.
