# 🐙 CthulhuMud ITA Redux

**Porting italiano, fedele e open source, dello storico MUD lovecraftiano [CthulhuMUD](https://www.cthulhumud.com/)**, costruito sul motore [Evennia](https://www.evennia.com/) (Python/Twisted/Django).

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

---

## Indice

- [Cos'è questo progetto](#cosè-questo-progetto)
- [Fedeltà alla fonte e note legali](#fedeltà-alla-fonte-e-note-legali)
- [Caratteristiche principali](#caratteristiche-principali)
- [Il Codex](#il-codex)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Primo avvio](#primo-avvio)
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
- WORSHIP/SACRIFICE verso 7 divinità del Mythos
- Dreamlands esplorabili (Ulthar, Villaggio degli Zoog) con rischio di incubi
- Arkham (73 edifici) e il Cairo ricostruiti in dettaglio, raggiungibili l'uno dall'altro via nave
- Sistemi speciali: Yithian/Mindtransfer, bambole voodoo, Focus Crystal
- Interfaccia colorata a tema lovecraftiano (ANSI/Xterm256): rosso cupo per il pericolo, verde spettrale per orrore/magia, viola per le Dreamlands, grigio/ciano per l'ambientazione
- 204 comandi social/emote, canali OOC multipli, messaggistica privata

## Il Codex

[`codex/codex_cthulhumud.pdf`](codex/codex_cthulhumud.pdf) è il manuale di gioco completo: oltre 130 pagine che coprono ogni sistema (personaggio, magia, combattimento, economia, luoghi, comunicazione, strumenti di staff), con fonti citate e distinzione esplicita fonte/scelta di design. Rigenerabile da sorgente con `bash codex/build.sh` (richiede `pandoc` e `weasyprint`).

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

## Distribuzione (systemd)

`deploy/systemd/` contiene le unit systemd pronte per l'uso (avvio al boot + watchdog di restart automatico) e uno script di installazione: vedi `deploy/systemd/install.sh`.

## Struttura del progetto

```
game/       codice del porting (Evennia): typeclasses, comandi, logica di gioco (world/)
codex/      sorgenti Markdown e PDF compilato del manuale di gioco
deploy/     unit systemd per l'esecuzione in produzione
```

## Licenza

Questo progetto è distribuito sotto licenza **GNU General Public License v3.0** — vedi [LICENSE](LICENSE). Costruito su [Evennia](https://www.evennia.com/), a sua volta rilasciato con licenza BSD.
