# Pacchetto Mudlet per CthulhuMUD Redux

Mappatore automatico e barre di stato per il client [Mudlet](https://www.mudlet.org/).

**Stato:** funzionante, confermato sul campo con Mudlet 5.0.1 su Debian.
La logica del mappatore ha anche un banco di prova automatico (vedi in
fondo), che però usa funzioni di Mudlet simulate: la prova che conta
resta quella dentro il client vero.

## Installazione

1. **Toolbox → Package Manager → Install**
2. Scegli `CthulhuMudRedux.xml`
3. Riconnettiti al gioco

Alla connessione compare la riga *"CthulhuMUD Redux: pacchetto attivo"*.

Il GMCP in Mudlet 5 è **acceso di serie**: non c'è nulla da abilitare. Se
vuoi controllare, sta in **Opzioni → Preferenze → Generale**, ma la prova
vera è più semplice — se dopo il login vedi i valori di Vita e Mana nel
pannello laterale, il GMCP sta già funzionando.

## Dati di connessione

| | |
|---|---|
| Indirizzo | l'IP o l'hostname del server |
| Porta | `8889` |
| Protocollo | Telnet semplice, nessun SSL |

## Comandi

| comando | cosa fa |
|---|---|
| `mappa` | apre (o riaggancia) la finestra della mappa |
| `mappadiag` | diagnostica: dice cosa arriva, cosa manca e dove si è inceppato |
| `barre on` | mostra le barre di stato in fondo, **con la Sanità mentale** |
| `barre off` | le nasconde (impostazione di partenza) |

### Perché le barre in basso sono spente di serie

Il pannello laterale di Mudlet mostra già Vita, Mana e Movimento, leggendoli
dagli stessi dati GMCP che manda il server. Delle barre in fondo alla
finestra principale sarebbero quindi un doppione, e coprirebbero l'ultima
riga di testo dell'ambientazione.

Restano disponibili con `barre on` per un motivo solo: il pannello laterale
non conosce la **Sanità mentale**, che in questo gioco è una statistica con
conseguenze meccaniche vere. Quando le accendi, lo spazio in fondo viene
riservato con `setBorderBottom`, così le barre non coprono più nulla.

## Cosa fa il pacchetto

**Mappa.** Ogni volta che cambi stanza il server manda il pacchetto GMCP
`Room.Info` con numero, nome, area e uscite; lo script crea la stanza sulla
mappa se non esiste, la posiziona accanto a quella da cui arrivi e traccia i
collegamenti.

**Barre di stato.** Il pacchetto `Char.Vitals` alimenta quattro barre: Vita,
Mana, Movimento e Sanità mentale.

## Una cosa da sapere sulla mappa

Nel mondo di CthulhuMUD poco più della metà delle uscite ha un nome proprio
(`tribunale`, `navata`, `fuori`) invece di una direzione cardinale, e solo 69
stanze su 239 hanno esclusivamente uscite cardinali. È una caratteristica del
MUD originale, non un limite del pacchetto.

Di conseguenza il server manda le uscite **divise in due campi** — `exits`
per quelle cardinali, `specials` per le altre — e lo script le tratta
diversamente:

- le **cardinali** vengono disposte sulla griglia, con la geometria che ci si
  aspetta da una mappa;
- quelle con **nome proprio** diventano *special exits*: restano cliccabili e
  utilizzabili dallo speedwalk, ma non hanno una posizione geometrica.

In pratica le vie di Arkham e il relitto dello U-29 vengono disegnati
ordinatamente, mentre gli interni degli edifici pendono di lato. Le stanze si
possono sempre trascinare a mano: Mudlet salva la posizione.

Nota: un collegamento viene tracciato solo quando **entrambe** le stanze sono
già state visitate. Finché non hai messo piede nella stanza di destinazione,
l'uscita c'è nel gioco ma non ancora sulla mappa.

## Se qualcosa non funziona

Il primo passo è sempre **`mappadiag`**: dice se i pacchetti arrivano, quante
stanze e aree esistono nella mappa, e qual è stato l'ultimo errore del
mappatore.

| sintomo | causa probabile |
|---|---|
| Nessun `Room.Info` ricevuto | GMCP spento nel client, o non ti sei ancora mosso |
| I dati arrivano ma la mappa è vuota | la finestra non è agganciata: usa `mappa` |
| Le stanze finiscono una sopra l'altra | ci si è spostati con un'uscita dal nome proprio, di cui non si può dedurre una direzione: trascinale dove vuoi, restano lì |
| Voglio ricominciare da capo | **Toolbox → Map → Clear map**, poi riconnettiti |

Se compare una riga rossa `[mappa] errore: ...`, è il mappatore che segnala
un guasto invece di tacere: quel testo dice esattamente dove.

## Come è fatto

| file | cosa è |
|---|---|
| `cthulhumud_mapper.lua` | il sorgente leggibile, da modificare |
| `CthulhuMudRedux.xml` | il pacchetto importabile, generato dal Lua |
| `prova_mapper.lua` | banco di prova (vedi sotto) |
| `stanze_prova.lua` | pacchetti `Room.Info` veri, catturati dal server |

### Il banco di prova

```bash
texlua prova_mapper.lua cthulhumud_mapper.lua stanze_prova.lua
```

Rifà in Lua puro le funzioni di Mudlet che il mappatore usa e ci fa passare
dentro pacchetti `Room.Info` veri, catturati dal server. Non sostituisce una
prova dentro Mudlet — le funzioni sono finte — ma verifica la logica, e
soprattutto **controlla che le direzioni passate a `setExit` siano fra quelle
che Mudlet accetta davvero**.

Quel controllo esiste per un motivo preciso. La prima versione convertiva
`n` in `"north"` prima di passarlo a `setExit`, ma Mudlet accetta solo le
sigle brevi (`n`, `ne`, `up`…). E `setExit` non solleva un errore: restituisce
`false` e basta. Risultato: la mappa restava vuota senza che nulla lo
segnalasse. Il banco di prova ora rende impossibile ripetere quell'errore
senza accorgersene.

`texlua` arriva con TeX Live ed è un interprete Lua a tutti gli effetti;
va bene qualunque altro (`lua5.4`, `luajit`).

### Rigenerare il pacchetto

Se modifichi il Lua devi rigenerare l'XML. Il nome dello script nell'XML deve
combaciare con il nome della funzione di smistamento (`cthulhuEvento`),
perché Mudlet chiama la funzione che ha lo stesso nome dello script: se i due
divergono il pacchetto si carica senza errori e semplicemente non fa nulla.

Lato server i pacchetti GMCP sono prodotti da
[`game/world/gmcp.py`](../../game/world/gmcp.py).
