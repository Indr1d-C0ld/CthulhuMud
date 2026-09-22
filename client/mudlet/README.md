# Pacchetto Mudlet per CthulhuMUD Redux

Mappatore automatico e barre di stato per il client [Mudlet](https://www.mudlet.org/).

## Installazione

1. In Mudlet: **Toolbox → Package Manager → Install**
2. Scegli `CthulhuMudRedux.xml`
3. Riconnettiti al gioco

Alla connessione compare la riga *"CthulhuMUD Redux: mappatore e barre di
stato attivi"*, e da quel momento la mappa si disegna da sola mentre
cammini.

## Dati di connessione

| | |
|---|---|
| Indirizzo | l'IP o l'hostname del server |
| Porta | `8889` |
| Protocollo | Telnet semplice, nessun SSL |

## Cosa fa

**Mappa.** Ogni volta che cambi stanza il server manda il pacchetto GMCP
`Room.Info` con numero, nome, area e uscite della stanza; lo script crea
la stanza sulla mappa se non esiste, la posiziona accanto a quella da cui
arrivi e traccia i collegamenti.

**Barre di stato.** Il pacchetto `Char.Vitals` alimenta quattro barre in
fondo alla finestra: Vita, Mana, Movimento e Sanità mentale.

## Una cosa da sapere sulla mappa

Nel mondo di CthulhuMUD poco più della metà delle uscite ha un nome
proprio (`tribunale`, `navata`, `fuori`) invece di una direzione
cardinale, e solo 69 stanze su 239 hanno esclusivamente uscite cardinali.
È una caratteristica del MUD originale, non un limite del pacchetto.

Di conseguenza il server manda le uscite **divise in due campi** —
`exits` per quelle cardinali, `specials` per le altre — e lo script le
tratta diversamente:

- le **cardinali** vengono disposte sulla griglia, con la geometria che
  ci si aspetta da una mappa;
- quelle con **nome proprio** diventano *special exits*: restano
  cliccabili e utilizzabili dallo speedwalk, ma non hanno una posizione
  geometrica.

In pratica le vie di Arkham e il relitto dello U-29 vengono disegnati
ordinatamente, mentre gli interni degli edifici pendono di lato come
collegamenti speciali. Le stanze si possono sempre trascinare a mano per
sistemare il disegno: Mudlet salva la posizione.

## Se qualcosa non funziona

**La mappa resta vuota.** Controlla che il GMCP sia attivo in Mudlet:
*Settings → Protocols → Enable GMCP*. Il server lo offre e lo dichiara
già nel proprio MSSP.

**Le stanze finiscono una sopra l'altra.** Succede quando ci si sposta
con un'uscita dal nome proprio: lo script non può dedurne una direzione e
mette la stanza di fianco. Trascinala dove ti pare, resta lì.

**Voglio ricominciare la mappa da zero.** *Toolbox → Map → Clear map*,
poi riconnettiti.

## Come è fatto

- `cthulhumud_mapper.lua` — il sorgente leggibile, da modificare
- `CthulhuMudRedux.xml` — il pacchetto importabile, generato dal Lua

Se cambi il Lua devi rigenerare l'XML: il nome dello script nell'XML deve
combaciare con il nome della funzione di smistamento (`cthulhuEvento`),
perché Mudlet chiama la funzione che ha lo stesso nome dello script. Se i
due divergono il pacchetto si carica senza errori e semplicemente non fa
nulla.

Lato server i pacchetti GMCP sono prodotti da
[`game/world/gmcp.py`](../../game/world/gmcp.py).
