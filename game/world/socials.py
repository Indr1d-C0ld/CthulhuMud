"""
Social (Fase G, undicesima e ultima tornata prima degli NPC ostili):
confermati dalla scansione esaustiva (info_socials.txt + le 21 pagine
socials/*.txt) come 203 comandi di puro testo di ambientazione, senza
alcuna meccanica (nessuno modifica stat, combattimento, o altro) - un
lavoro di VOLUME di contenuto, non di design.

Ogni social della fonte ha fino a 3 forme d'uso (senza bersaglio, su se
stessi, su un bersaglio) e fino a 4 prospettive per forma (S=sintassi,
A=attore, O=osservatori, T=bersaglio) - qui riprodotte come
"senza_bersaglio"/"su_se_stesso"/"su_bersaglio", ciascuna con le chiavi
"attore"/"osservatori"/["bersaglio"]. Alcuni social della fonte (es.
HUG, KISS, SLAP...) non hanno una forma libera: usarli senza bersaglio
mostra solo un prompt ("Whom do you wish to hug?").

Fase G (undicesima tornata) copriva 33 social. Fase J ha aggiunto il
resto in quattro tornate (2026-09-13), usando un parser dedicato sulle
21 pagine socials/*.txt per non perdere o storpiare nessuna voce su un
volume cosi' alto: +77 (lettere A-H), +75 (lettere I-Y), +19 (categoria
"sessuale" - KISS era gia' presente dalla prima tornata, corretto qui
sotto). **Con questo la trascrizione e' completa**: 204 social su 204
individuati nel corpus (un social in piu' dei 203 "ufficiali" elencati
in info_socials.txt - HIGHFIVE e SLOBBER esistono come pagine reali ma
non risultano nel conteggio dell'indice, inclusi comunque entrambi;
manca solo TWEAK, presente nell'indice ma assente dal corpus scaricato
- un vero buco della scansione, non un'omissione nostra: 204 e' quindi
il massimo raggiungibile con il materiale scaricato).

La categoria "sessuale" (20 social, di cui 19 aggiunti nella quarta
tornata + KISS) resta esplicitamente vietata ai newbie dalla fonte:
"their use is slightly restricted in that newbies cannot use them" -
applicato con il flag "vietato_newbie" per ogni voce (verificato in
commands/cthulhu_socials.py contro world.professions_newbie). Il
registro rimane comunque PG-13 come nella fonte: "Sexual socials do
not include any graphic or explicitly obscene content" - qui tradotti
mantenendo lo stesso registro allusivo, mai esplicito, dell'originale.
KISS era stato erroneamente costruito in Fase G come social libero/
amichevole: la fonte lo classifica sotto "Sexual Socials" - corretto
in Fase J aggiungendo "vietato_newbie".

Per i pronomi di genere nei messaggi in terza persona (es. "si guarda
allo specchio" vs "guarda se stessa"), si usa Character.db.genere
("m"/"f", default "m" - CmdGender in commands/cthulhu_socials.py).
"""

SOCIALS = {
    "aargh": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "AAAARRRRGGGGHHHH!!!!!!",
            "osservatori": "{attore} getta la testa all'indietro e ulula di pura frustrazione!",
        },
        "su_se_stesso": {
            "attore": "Urli di frustrazione contro la tua stessa stupidita'!",
            "osservatori": "{attore} urla di frustrazione contro {rif} stesso/a!",
        },
        "su_bersaglio": {
            "attore": "Urli di frustrazione e allunghi le mani verso la gola di {bersaglio}!",
            "osservatori": "{attore} ulula di frustrazione e si avventa su {bersaglio}, cercando di strangolarlo/a!",
            "bersaglio": "{attore} ti afferra alla gola con entrambe le mani, ululando di frustrazione!",
        },
    },
    "accuse": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Accusi tutti quanti!",
            "osservatori": "{attore} sembra avere la coscienza sporca.",
        },
        "su_se_stesso": {
            "attore": "Accusi te stesso/a.",
            "osservatori": "{attore} sembra avere la coscienza sporca con {rif} stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} con aria accusatoria.",
            "osservatori": "{attore} guarda {bersaglio} con aria accusatoria.",
            "bersaglio": "{attore} ti guarda con aria accusatoria.",
        },
    },
    "apologize": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Ti scusi profusamente con tutti.",
            "osservatori": "{attore} si scusa profusamente con tutti.",
        },
        "su_se_stesso": {
            "attore": "Ti scusi con te stesso/a. Non dovresti trattarti cosi' male.",
            "osservatori": "{attore} si scusa con {rif} stesso/a per qualcosa che a quanto pare ha fatto a se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Ti scusi sinceramente con {bersaglio}.",
            "osservatori": "{attore} si scusa sinceramente con {bersaglio}.",
            "bersaglio": "{attore} si scusa sinceramente con te, implorando il tuo perdono.",
        },
    },
    "applaud": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "CLAP! CLAP! CLAP! CLAP!",
            "osservatori": "{attore} applaude rumorosamente.",
        },
        "su_se_stesso": {
            "attore": "Sei ridotto/a ad applaudire te stesso/a.",
            "osservatori": "{attore} e' tristemente ridotto/a ad applaudire {rif} stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Fai un applauso a {bersaglio}.",
            "osservatori": "{attore} fa un fragoroso applauso a {bersaglio}.",
            "bersaglio": "{attore} ti fa un fragoroso applauso! Ottimo lavoro!",
        },
    },
    "beg": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Imploro gli Dei pieta'! Non trattenere il fiato...",
            "osservatori": "{attore} implora sciocchamente pieta' dagli Dei!",
        },
        "su_se_stesso": {
            "attore": "Implorare te stesso/a per pieta' non serve granche', vero?",
            "osservatori": "{attore} implora se stesso/a per pieta', senza molto senso.",
        },
        "su_bersaglio": {
            "attore": "Implori {bersaglio} per pieta'!",
            "osservatori": "{attore} implora {bersaglio} per pieta'!",
            "bersaglio": "{attore} ti implora per pieta'!",
        },
    },
    "blush": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Le tue guance bruciano mentre inizi ad arrossire.",
            "osservatori": "{attore} arrossisce.",
        },
        "su_se_stesso": {
            "attore": "Arrossisci per la tua stessa follia.",
            "osservatori": "{attore} arrossisce per le proprie azioni.",
        },
        "su_bersaglio": {
            "attore": "Inizi ad arrossire quando vedi {bersaglio}.",
            "osservatori": "{attore} guarda {bersaglio} e inizia ad arrossire.",
            "bersaglio": "{attore} inizia ad arrossire quando ti guarda.",
        },
    },
    "boast": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti vanti ad alta voce di tutte le tue straordinarie imprese.",
            "osservatori": "{attore} si vanta ad alta voce delle proprie \"straordinarie\" imprese.",
        },
        "su_se_stesso": {
            "attore": "Inizi a vantarti con te stesso/a delle tue imprese! Che pubblico ricettivo!",
            "osservatori": "{attore} inizia a vantarsi con se stesso/a delle proprie imprese.",
        },
        "su_bersaglio": {
            "attore": "Inizi a vantarti con {bersaglio} delle tue \"grandi\" gesta.",
            "osservatori": "{attore} inizia a vantarsi con {bersaglio} delle proprie \"grandi\" gesta.",
            "bersaglio": "{attore} inizia a vantarsi con te delle proprie \"grandi\" gesta.",
        },
    },
    "bow": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti inchini profondamente.",
            "osservatori": "{attore} si inchina profondamente.",
        },
        "su_se_stesso": {
            "attore": "Provi a inchinarti a te stesso/a e per poco non cadi.",
            "osservatori": "{attore} prova a inchinarsi a {rif} stesso/a e per poco non cade.",
        },
        "su_bersaglio": {
            "attore": "Ti inchini davanti a {bersaglio}.",
            "osservatori": "{attore} si inchina davanti a {bersaglio}.",
            "bersaglio": "{attore} si inchina davanti a te.",
        },
    },
    "cheer": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Esulti e balli mentre la gioia dentro di te esplode!",
            "osservatori": "{attore} esulta rumorosamente mentre la sua gioia travolgente esplode!",
        },
        "su_se_stesso": {
            "attore": "Esulti rumorosamente per te stesso/a, visto che nessun altro lo fara'.",
            "osservatori": "{attore} esulta rumorosamente per se stesso/a, visto che nessun altro lo fara'.",
        },
        "su_bersaglio": {
            "attore": "Esulti rumorosamente per {bersaglio}!",
            "osservatori": "{attore} inizia a esultare rumorosamente per {bersaglio}!",
            "bersaglio": "{attore} inizia a esultare rumorosamente per te!",
        },
    },
    "comfort": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Provi invano a confortare te stesso/a.",
            "osservatori": "{attore} prova invano a confortare {rif} stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Conforti {bersaglio}.",
            "osservatori": "{attore} conforta {bersaglio}.",
            "bersaglio": "{attore} ti conforta.",
        },
    },
    "cry": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Scoppi in lacrime! WAAAAAAAA!",
            "osservatori": "{attore} scoppia in lacrime!",
        },
        "su_se_stesso": {
            "attore": "Del tutto inconsolabile, inizi a piangere tra te e te.",
            "osservatori": "{attore} inizia a piangere tra se' e se', a quanto pare inconsolabile.",
        },
        "su_bersaglio": {
            "attore": "Corri da {bersaglio} e inizi a piangere sulla sua spalla!",
            "osservatori": "{attore} corre da {bersaglio} e inizia a piangere sulla sua spalla.",
            "bersaglio": "{attore} corre da te e inizia a piangere sulla tua spalla!",
        },
    },
    "dance": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Balli come un Boemo scatenato!",
            "osservatori": "{attore} balla come un Boemo scatenato!",
        },
        "su_se_stesso": {
            "attore": "Balli un ballo solitario con te stesso/a.",
            "osservatori": "{attore} balla un ballo triste e solitario con se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Prendi la mano di {bersaglio} e la fai volteggiare sulla pista da ballo!",
            "osservatori": "{attore} prende la mano di {bersaglio} e la fa volteggiare sulla pista da ballo!",
            "bersaglio": "{attore} prende la tua mano e ti fa volteggiare sulla pista da ballo!",
        },
    },
    "glare": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Guardi tutti con aria sospettosa.",
            "osservatori": "{attore} guarda tutti con aria sospettosa.",
        },
        "su_se_stesso": {
            "attore": "Guardi con rabbia le tue stesse azioni.",
            "osservatori": "{attore} guarda con rabbia le proprie azioni.",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} con freddezza.",
            "osservatori": "{attore} guarda {bersaglio} con freddezza.",
            "bersaglio": "{attore} ti guarda con freddezza.",
        },
    },
    "grin": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sogghigni in modo malvagio.",
            "osservatori": "{attore} sogghigna in modo malvagio.",
        },
        "su_se_stesso": {
            "attore": "Sogghigni per i tuoi stessi pensieri maliziosi.",
            "osservatori": "{attore} sogghigna per i propri pensieri.",
        },
        "su_bersaglio": {
            "attore": "Sogghigni in modo malvagio verso {bersaglio}.",
            "osservatori": "{attore} sogghigna in modo malvagio verso {bersaglio}.",
            "bersaglio": "{attore} ti sogghigna in modo malvagio.",
        },
    },
    "growl": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Ringhi minacciosamente.",
            "osservatori": "{attore} ringhia minacciosamente.",
        },
        "su_se_stesso": {
            "attore": "Ringhi per la tua stessa stupidita'.",
            "osservatori": "{attore} ringhia per la propria stupidita'.",
        },
        "su_bersaglio": {
            "attore": "Ringhi minacciosamente verso {bersaglio}!",
            "osservatori": "{attore} ringhia minacciosamente verso {bersaglio}!",
            "bersaglio": "{attore} ti ringhia contro minacciosamente!",
        },
    },
    "hug": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Hai solo te stesso/a da abbracciare. Che tristezza...",
            "osservatori": "{attore} abbraccia se stesso/a, non avendo nessun altro.",
        },
        "su_bersaglio": {
            "attore": "Abbracci {bersaglio} forte!",
            "osservatori": "{attore} abbraccia {bersaglio} forte!",
            "bersaglio": "{attore} ti abbraccia forte!",
        },
    },
    "kiss": {
        # Corretto in Fase J: la fonte (info_socials.txt) classifica KISS
        # sotto "Sexual Socials", non "Friendly" - qui erroneamente
        # trattato come amichevole/libero nella prima tornata (Fase G).
        # "categoria" resta descrittiva del tono (non e' esplicito ne'
        # osceno, coerente con "Sexual socials do not include any
        # graphic or explicitly obscene content"), ma vietato_newbie
        # applica ora la restrizione reale della fonte.
        "categoria": "amichevole",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Provi goffamente a baciare te stesso/a. Che tristezza...",
            "osservatori": "{attore} prova goffamente a baciare se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Dai a {bersaglio} un bacio appassionato!",
            "osservatori": "{attore} da' a {bersaglio} un bacio appassionato!",
            "bersaglio": "{attore} ti da' un bacio appassionato!",
        },
    },
    "laugh": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Cadi a terra dalle risate.",
            "osservatori": "{attore} cade a terra dalle risate.",
        },
        "su_se_stesso": {
            "attore": "Ridi rumorosamente di te stesso/a!",
            "osservatori": "{attore} ride rumorosamente di se stesso/a!",
        },
        "su_bersaglio": {
            "attore": "Ridi rumorosamente delle azioni di {bersaglio}!",
            "osservatori": "{attore} ride rumorosamente delle azioni di {bersaglio}!",
            "bersaglio": "{attore} ride rumorosamente delle tue azioni!",
        },
    },
    "nod": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Annuisci.",
            "osservatori": "{attore} annuisce.",
        },
        "su_se_stesso": {
            "attore": "Annuisci alle istruzioni delle voci nella tua testa.",
            "osservatori": "{attore} annuisce in silenzio alle voci nella propria testa.",
        },
        "su_bersaglio": {
            "attore": "Annuisci verso {bersaglio}.",
            "osservatori": "{attore} annuisce verso {bersaglio}.",
            "bersaglio": "{attore} ti fa un cenno d'assenso.",
        },
    },
    "pat": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti dai una pacca sulla testa per rassicurarti.",
            "osservatori": "{attore} si da' una pacca sulla testa per rassicurarsi.",
        },
        "su_bersaglio": {
            "attore": "Dai una pacca sulla testa a {bersaglio}.",
            "osservatori": "{attore} da' una pacca sulla testa a {bersaglio}.",
            "bersaglio": "{attore} ti da' una pacca sulla testa.",
        },
    },
    "ponder": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti siedi e rifletti sulla situazione. Hmmmm....",
            "osservatori": "{attore} si siede e riflette sulla situazione.",
        },
        "su_se_stesso": {
            "attore": "Ti siedi e rifletti sulla tua stessa domanda. Hmmmm....",
            "osservatori": "{attore} si siede e riflette sulla propria domanda.",
        },
        "su_bersaglio": {
            "attore": "Ti siedi e rifletti sulla domanda di {bersaglio}. Hmmmm....",
            "osservatori": "{attore} si siede e riflette sulla domanda di {bersaglio}.",
            "bersaglio": "{attore} si siede e riflette sulla tua domanda.",
        },
    },
    "poke": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti dai una gomitata nelle costole. OUCH!",
            "osservatori": "{attore} si da' una gomitata nelle costole.",
        },
        "su_bersaglio": {
            "attore": "Dai una gomitata nelle costole a {bersaglio}.",
            "osservatori": "{attore} da' una gomitata nelle costole a {bersaglio}.",
            "bersaglio": "{attore} ti da' una gomitata nelle costole.",
        },
    },
    "punch": {
        "categoria": "ostile",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti dai un pugno nello stomaco. Si', te lo meriti.",
            "osservatori": "{attore} si da' un pugno nello stomaco.",
        },
        "su_bersaglio": {
            "attore": "Dai a {bersaglio} un pugno scherzoso sul braccio!",
            "osservatori": "{attore} da' a {bersaglio} un pugno scherzoso sul braccio!",
            "bersaglio": "{attore} ti da' un pugno scherzoso sul braccio!",
        },
    },
    "salute": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Fai un saluto militare deciso.",
            "osservatori": "{attore} fa un saluto militare deciso.",
        },
        "su_se_stesso": {
            "attore": "Non puoi salutare te stesso/a.",
            "osservatori": "{attore} prova goffamente a salutare se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Saluti {bersaglio}.",
            "osservatori": "{attore} saluta {bersaglio}.",
            "bersaglio": "{attore} ti saluta.",
        },
    },
    "shrug": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Alzi le spalle.",
            "osservatori": "{attore} alza le spalle.",
        },
        "su_se_stesso": {
            "attore": "Alzi le spalle, impotente.",
            "osservatori": "{attore} alza le spalle, impotente.",
        },
        "su_bersaglio": {
            "attore": "Alzi le spalle verso {bersaglio}.",
            "osservatori": "{attore} alza le spalle verso {bersaglio}.",
            "bersaglio": "{attore} alza le spalle verso di te.",
        },
    },
    "sigh": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sospiri.",
            "osservatori": "{attore} sospira.",
        },
        "su_se_stesso": {
            "attore": "Sospiri piano tra te e te.",
            "osservatori": "{attore} sospira piano tra se' e se'.",
        },
        "su_bersaglio": {
            "attore": "Sospiri piano verso {bersaglio}.",
            "osservatori": "{attore} sospira piano verso {bersaglio}.",
            "bersaglio": "{attore} sospira piano verso di te.",
        },
    },
    "slap": {
        "categoria": "ostile",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti dai uno schiaffo da stordirti! OUCH!",
            "osservatori": "{attore} si da' uno schiaffo da stordirsi!",
        },
        "su_bersaglio": {
            "attore": "Dai uno schiaffo in pieno viso a {bersaglio}!",
            "osservatori": "{attore} da' uno schiaffo in pieno viso a {bersaglio}!",
            "bersaglio": "{attore} ti da' uno schiaffo in pieno viso!",
        },
    },
    "smile": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Sorridi felice.",
            "osservatori": "{attore} sorride felice.",
        },
        "su_se_stesso": {
            "attore": "Sorridi misteriosamente tra te e te.",
            "osservatori": "{attore} sorride misteriosamente tra se' e se'.",
        },
        "su_bersaglio": {
            "attore": "Sorridi a {bersaglio}.",
            "osservatori": "{attore} sorride a {bersaglio}.",
            "bersaglio": "{attore} ti sorride.",
        },
    },
    "spit": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Sputi con totale disgusto!",
            "osservatori": "{attore} sputa con totale disgusto!",
        },
        "su_se_stesso": {
            "attore": "Ti sputi sulle mani e ti prepari a lavorare!",
            "osservatori": "{attore} si sputa sulle mani e si prepara a lavorare!",
        },
        "su_bersaglio": {
            "attore": "Sputi ai piedi di {bersaglio}!",
            "osservatori": "{attore} sputa ai piedi di {bersaglio}!",
            "bersaglio": "{attore} sputa ai tuoi piedi!",
        },
    },
    "thank": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti ringrazi per essere cosi' incredibilmente talentuoso/a!",
            "osservatori": "{attore} ringrazia se stesso/a per essere cosi' talentuoso/a!",
        },
        "su_bersaglio": {
            "attore": "Ringrazi {bersaglio} di cuore.",
            "osservatori": "{attore} ringrazia {bersaglio} di cuore.",
            "bersaglio": "{attore} ti ringrazia di cuore.",
        },
    },
    "tickle": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Provi a fare il solletico a te stesso/a, ma non e' proprio lo stesso.",
            "osservatori": "{attore} prova a farsi il solletico da solo/a, senza molto successo.",
        },
        "su_bersaglio": {
            "attore": "Fai il solletico a {bersaglio}! TEE HEE!",
            "osservatori": "{attore} fa il solletico a {bersaglio}! TEE HEE!",
            "bersaglio": "{attore} ti fa il solletico! TEE HEE!",
        },
    },
    "wave": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Saluti con la mano.",
            "osservatori": "{attore} saluta con la mano.",
        },
        "su_se_stesso": {
            "attore": "Ti agiti la mano davanti alla faccia per controllare la vista.",
            "osservatori": "{attore} si agita la mano davanti alla faccia per controllare la vista.",
        },
        "su_bersaglio": {
            "attore": "Saluti {bersaglio} con la mano.",
            "osservatori": "{attore} saluta {bersaglio} con la mano.",
            "bersaglio": "{attore} ti saluta con la mano.",
        },
    },
    "wink": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Fai l'occhiolino in modo allusivo.",
            "osservatori": "{attore} fa l'occhiolino in modo allusivo.",
        },
        "su_se_stesso": {
            "attore": "Fai l'occhiolino in modo allusivo a...te stesso/a?!",
            "osservatori": "{attore} fa l'occhiolino in modo allusivo a se stesso/a?!",
        },
        "su_bersaglio": {
            "attore": "Fai l'occhiolino in modo allusivo a {bersaglio}.",
            "osservatori": "{attore} fa l'occhiolino a {bersaglio}.",
            "bersaglio": "{attore} ti fa l'occhiolino in modo allusivo.",
        },
    },

    # --- Seconda tornata (lettere A-H): 77 nuovi social, stesso metodo -----
    "adjust": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti guardi intorno, ti assicuri che nessuno stia guardando, e ti aggiusti gli \"attrezzi\".",
            "osservatori": "{attore} si guarda intorno furtivamente, sorride, poi si china e si \"aggiusta\"...",
        },
    },
    "air": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Afferri la tua chitarra immaginaria e suoni con tutta la forza che hai!",
            "osservatori": "{attore} afferra la sua chitarra immaginaria e suona con tutta la forza che ha!",
        },
        "su_se_stesso": {
            "attore": "Ti fai una serenata in solitaria con un assolo di chitarra immaginaria.",
            "osservatori": "{attore} inizia a suonare una chitarra immaginaria per se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Scateni il mondo di {bersaglio} con la tua chitarra immaginaria!",
            "osservatori": "{attore} cerca di scatenare il mondo di {bersaglio} con la sua chitarra immaginaria!",
            "bersaglio": "{attore} cerca di scatenare il tuo mondo con la sua chitarra immaginaria!",
        },
    },
    "aroo": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Inclini la testa con curiosita'.",
            "osservatori": "{attore} inclina la testa con curiosita'.",
        },
        "su_bersaglio": {
            "attore": "Inclini la testa con curiosita' verso {bersaglio}.",
            "osservatori": "{attore} inclina la testa con curiosita' verso {bersaglio}.",
            "bersaglio": "{attore} inclina la testa con curiosita' verso di te.",
        },
    },
    "babble": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Farfugli all'infinito, senza parlare di niente in particolare.",
            "osservatori": "{attore} farfuglia e farfuglia e farfuglia senza sosta...",
        },
        "su_se_stesso": {
            "attore": "Inizi a farfugliare tra te e te, felice di aver finalmente trovato qualcuno disposto ad ascoltarti!",
            "osservatori": "{attore} inizia a farfugliare tra se' e se', a bassa voce.",
        },
        "su_bersaglio": {
            "attore": "Farfugli senza sosta a {bersaglio}.",
            "osservatori": "{attore} farfuglia senza sosta alla povera {bersaglio}.",
            "bersaglio": "{attore} ti farfuglia addosso senza sosta, senza nemmeno fermarsi per respirare. Che orrore!",
        },
    },
    "bark": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Abbai forte come il cane che sei!",
            "osservatori": "{attore} inizia improvvisamente ad abbaiare come un cane!",
        },
        "su_se_stesso": {
            "attore": "Abbai forte contro te stesso/a e in qualche modo riesci a spaventarti!",
            "osservatori": "{attore} abbaia contro se stesso/a, spaventandosi a morte!",
        },
        "su_bersaglio": {
            "attore": "Abbai forte contro {bersaglio}!",
            "osservatori": "{attore} inizia improvvisamente ad abbaiare forte contro {bersaglio}!",
            "bersaglio": "{attore} inizia improvvisamente ad abbaiarti contro!",
        },
    },
    "bat": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Batti le ciglia con dolcezza.",
            "osservatori": "{attore} batte le ciglia con dolcezza.",
        },
        "su_se_stesso": {
            "attore": "Provi a batterti le ciglia da solo/a e quasi ti strappi un muscolo.",
            "osservatori": "{attore} prova a battersi le ciglia da solo/a e quasi si strappa un muscolo.",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} e batti le ciglia con dolcezza.",
            "osservatori": "{attore} guarda {bersaglio} e batte le ciglia con dolcezza.",
            "bersaglio": "{attore} ti guarda e batte le ciglia con dolcezza.",
        },
    },
    "bcatch": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Allunghi le mani e afferri al volo una bottiglia di birra in arrivo!",
            "osservatori": "{attore} allunga le mani e afferra al volo una bottiglia di birra in arrivo!",
        },
    },
    "bearhug": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Provi a stringere tutti insieme in un enorme abbraccio da orso!",
            "osservatori": "{attore} prova a stringere tutti insieme in un enorme abbraccio da orso!",
        },
        "su_se_stesso": {
            "attore": "Ti stringi forte in un solitario abbraccio da orso.",
            "osservatori": "{attore} si stringe in un triste e solitario abbraccio da orso.",
        },
        "su_bersaglio": {
            "attore": "Stringi {bersaglio} forte in un enorme abbraccio da orso!",
            "osservatori": "{attore} stringe {bersaglio} forte in un enorme abbraccio da orso!",
            "bersaglio": "{attore} ti stringe forte in un enorme abbraccio da orso!",
        },
    },
    "beckon": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Fai cenno a tutti di seguirti.",
            "osservatori": "{attore} fa cenno a tutti di seguirlo/a.",
        },
        "su_se_stesso": {
            "attore": "Fai cenno alla tua stessa ombra di seguirti.",
            "osservatori": "{attore} fa cenno alla propria ombra di seguirlo/a.",
        },
        "su_bersaglio": {
            "attore": "Pieghi un dito verso {bersaglio} e le/gli fai cenno di seguirti.",
            "osservatori": "{attore} piega un dito verso {bersaglio} e le/gli fa cenno di seguirlo/a.",
            "bersaglio": "{attore} piega un dito verso di te e ti fa cenno di seguirlo/a.",
        },
    },
    "beer": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Tiri fuori un six-pack di birra.",
            "osservatori": "{attore} tira fuori un six-pack di birra.",
        },
        "su_se_stesso": {
            "attore": "Stappi una birra e inizi a tracannarla.",
            "osservatori": "{attore} stappa una birra e inizia a tracannarla.",
        },
        "su_bersaglio": {
            "attore": "Lanci una bottiglia di birra verso {bersaglio}!",
            "osservatori": "{attore} lancia una bottiglia di birra verso {bersaglio}!",
            "bersaglio": "{attore} ti lancia una bottiglia di birra! Meglio che tu la prenda al volo!",
        },
    },
    "bird": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Fai il dito medio a tutto il mondo!",
            "osservatori": "{attore} fa il dito medio a tutto il mondo!",
        },
        "su_bersaglio": {
            "attore": "Fai il dito medio a {bersaglio}.",
            "osservatori": "{attore} fa il dito medio a {bersaglio}.",
            "bersaglio": "{attore} ti fa il dito medio! Che maleducato/a!",
        },
    },
    "bitchslap": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Ti guardi intorno in cerca di qualcuno da sottomettere...",
            "osservatori": "{attore} si guarda intorno in cerca di qualcuno da schiaffeggiare.",
        },
        "su_se_stesso": {
            "attore": "Per qualche ragione che solo tu comprendi, ti stordisci con un poderoso schiaffone!",
            "osservatori": "{attore} si schiaffeggia da solo/a e si stende a terra!",
        },
        "su_bersaglio": {
            "attore": "Schiaffeggi {bersaglio} con tutta la tua forza, scaraventandola/o dall'altra parte della stanza!",
            "osservatori": "{attore} si avventa e schiaffeggia {bersaglio}, scaraventandola/o dall'altra parte della stanza!",
            "bersaglio": "{attore} ti schiaffeggia senza preavviso, scaraventandoti dall'altra parte della stanza!",
        },
    },
    "bkiss": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Mandi un bacio a tutto il mondo!",
            "osservatori": "{attore} manda un bacio a tutto il mondo!",
        },
        "su_se_stesso": {
            "attore": "Mandi un bacio a... te stesso/a?!",
            "osservatori": "{attore} manda un bacio a se stesso/a?!",
        },
        "su_bersaglio": {
            "attore": "Mandi dolcemente un bacio a {bersaglio}.",
            "osservatori": "{attore} manda dolcemente un bacio a {bersaglio}. Che tenerezza!",
            "bersaglio": "{attore} ti manda dolcemente un bacio.",
        },
    },
    "bleed": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sanguini dappertutto, facendo un disastro terribile.",
            "osservatori": "{attore} sanguina copiosamente, formando dense pozze di sangue.",
        },
        "su_se_stesso": {
            "attore": "Ti spalmi il sangue su tutti i vestiti. Non andra' mai piu' via...",
            "osservatori": "{attore} si spalma il sangue su tutti i vestiti.",
        },
        "su_bersaglio": {
            "attore": "Fai schizzare qualche goccia di sangue su {bersaglio}.",
            "osservatori": "{attore} fa schizzare un po' del proprio sangue su {bersaglio}. Disgustoso!",
            "bersaglio": "{attore} fa schizzare un po' del proprio sangue su di te! Disgustoso!",
        },
    },
    "bling": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Mostri con orgoglio i tuoi gioielli d'oro a tutti!",
            "osservatori": "{attore} mostra i suoi gioielli d'oro.",
        },
        "su_se_stesso": {
            "attore": "Ammiri con orgoglio i tuoi stessi gioielli d'oro.",
            "osservatori": "{attore} ammira con orgoglio i propri gioielli d'oro.",
        },
        "su_bersaglio": {
            "attore": "Sfoggi con orgoglio i tuoi gioielli d'oro davanti a {bersaglio}.",
            "osservatori": "{attore} sfoggia con orgoglio i propri gioielli d'oro davanti a {bersaglio}.",
            "bersaglio": "{attore} sfoggia i propri gioielli d'oro perche' tu li veda.",
        },
    },
    "blink": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sbatti le palpebre, sorpreso/a.",
            "osservatori": "{attore} sbatte le palpebre, sorpreso/a.",
        },
        "su_se_stesso": {
            "attore": "Sbatti le palpebre, confuso/a.",
            "osservatori": "{attore} sbatte le palpebre, confuso/a.",
        },
        "su_bersaglio": {
            "attore": "Sbatti le palpebre sorpreso/a verso {bersaglio}.",
            "osservatori": "{attore} sbatte le palpebre sorpreso/a verso {bersaglio}.",
            "bersaglio": "{attore} sbatte le palpebre verso di te, sorpreso/a.",
        },
    },
    "boggle": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Resti sbalordito/a dal concetto.",
            "osservatori": "{attore} resta sbalordito/a dal concetto.",
        },
        "su_se_stesso": {
            "attore": "Resti sbalordito/a da te stesso/a, completamente confuso/a da tutto.",
            "osservatori": "{attore} resta sbalordito/a da se stesso/a, completamente confuso/a.",
        },
        "su_bersaglio": {
            "attore": "Resti sbalordito/a guardando {bersaglio}.",
            "osservatori": "{attore} resta sbalordito/a guardando {bersaglio}.",
            "bersaglio": "{attore} resta sbalordito/a guardando te.",
        },
    },
    "bonk": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti dai un colpetto in testa per essere stato/a cosi' sciocco/a.",
            "osservatori": "{attore} si da' un colpetto in testa per essere stato/a cosi' sciocco/a.",
        },
        "su_bersaglio": {
            "attore": "Dai un colpetto in testa a {bersaglio} per essere stato/a un tale idiota.",
            "osservatori": "{attore} da' un colpetto in testa a {bersaglio} per essere stato/a un tale idiota.",
            "bersaglio": "{attore} ti da' un colpetto in testa per essere stato/a cosi' sciocco/a.",
        },
    },
    "booty": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Indossi una benda sull'occhio e parti in cerca di un tesoro da saccheggiare! ARRR!",
            "osservatori": "{attore} indossa una benda sull'occhio e parte in cerca di un tesoro da saccheggiare! ARRR!",
        },
        "su_bersaglio": {
            "attore": "Indossi una benda sull'occhio e parti a saccheggiare il tesoro di {bersaglio}! ARRR!",
            "osservatori": "{attore} indossa una benda sull'occhio e parte a saccheggiare il tesoro di {bersaglio}! ARRR!",
            "bersaglio": "{attore} indossa una benda sull'occhio e parte a saccheggiare il TUO tesoro! ARRR!",
        },
    },
    "bounce": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Saltelli felice in giro.",
            "osservatori": "{attore} saltella felice in giro.",
        },
        "su_se_stesso": {
            "attore": "Provi a saltellarti in grembo e cadi a terra dolorosamente.",
            "osservatori": "{attore} prova a saltellarsi in grembo e cade a terra dolorosamente.",
        },
        "su_bersaglio": {
            "attore": "Saltelli in grembo a {bersaglio}.",
            "osservatori": "{attore} saltella in grembo a {bersaglio}.",
            "bersaglio": "{attore} ti saltella in grembo! UFF!",
        },
    },
    "brat": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Fai la linguaccia al mondo intero. NA NA!",
            "osservatori": "{attore} fa la linguaccia al mondo intero.",
        },
        "su_se_stesso": {
            "attore": "Non ha senso farti la linguaccia da solo/a.",
            "osservatori": "Non ha alcun senso che {attore} si faccia la linguaccia da solo/a.",
        },
        "su_bersaglio": {
            "attore": "Fai la linguaccia a {bersaglio}. NA NA!",
            "osservatori": "{attore} fa la linguaccia a {bersaglio}.",
            "bersaglio": "{attore} ti fa la linguaccia. Che maleducato/a!",
        },
    },
    "brb": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Alzi il cartello \"torno subito\" perche' tutti lo vedano.",
            "osservatori": "{attore} torna subito!",
        },
    },
    "brush": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti spazzoli i capelli con noncuranza.",
            "osservatori": "{attore} si spazzola i capelli con noncuranza.",
        },
        "su_bersaglio": {
            "attore": "Inizi a spazzolare i capelli di {bersaglio}, cercando di sciogliere tutti i nodi.",
            "osservatori": "{attore} cerca di sciogliere i nodi dai capelli di {bersaglio} con la spazzola.",
            "bersaglio": "{attore} ti spazzola i capelli, cercando di sciogliere tutti i nodi.",
        },
    },
    "burp": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Rutti rumorosamente.",
            "osservatori": "{attore} rutta rumorosamente.",
        },
        "su_se_stesso": {
            "attore": "Rutti rumorosamente contro te stesso/a. Ah, molto meglio...",
            "osservatori": "{attore} rutta rumorosamente contro se stesso/a. Si spera si senta meglio...",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} e rutti rumorosamente.",
            "osservatori": "{attore} guarda {bersaglio} e lascia andare un rutto rumoroso.",
            "bersaglio": "{attore} ti guarda e rutta rumorosamente.",
        },
    },
    "cackle": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ridacchi con gioia malvagia.",
            "osservatori": "{attore} getta la testa all'indietro e ridacchia con folle allegria!",
        },
        "su_se_stesso": {
            "attore": "Ridacchi di te stesso/a come un pazzo/a!",
            "osservatori": "{attore} ridacchia di se stesso/a come un pazzo/a!",
        },
        "su_bersaglio": {
            "attore": "Ridacchi con gioia malvagia verso {bersaglio}.",
            "osservatori": "{attore} ridacchia con gioia malvagia verso {bersaglio}.",
            "bersaglio": "{attore} ridacchia verso di te con folle allegria.",
        },
    },
    "charge": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Con un grido di battaglia, ti lanci a combattere il mondo intero!",
            "osservatori": "{attore} lancia un grido di battaglia e si getta a combattere il mondo intero!",
        },
        "su_se_stesso": {
            "attore": "Provi a caricare te stesso/a e sbatti la testa contro un muro! OUCH!",
            "osservatori": "{attore} prova a caricare se stesso/a e finisce a testa in avanti contro un muro! OUCH!",
        },
        "su_bersaglio": {
            "attore": "Urli forte e carichi {bersaglio}!",
            "osservatori": "{attore} urla forte e carica {bersaglio}!",
            "bersaglio": "{attore} urla forte e si lancia dritto/a contro di te!",
        },
    },
    "chuckle": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ridacchi piano.",
            "osservatori": "{attore} ridacchia piano.",
        },
        "su_se_stesso": {
            "attore": "Ridacchi piano di te stesso/a.",
            "osservatori": "{attore} ridacchia piano di se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Ridacchi piano delle azioni di {bersaglio}.",
            "osservatori": "{attore} ridacchia piano delle azioni di {bersaglio}.",
            "bersaglio": "{attore} ridacchia piano delle tue azioni.",
        },
    },
    "clap": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Batti le mani rumorosamente!",
            "osservatori": "{attore} batte le mani rumorosamente!",
        },
        "su_se_stesso": {
            "attore": "Applaudi la tua stessa prestazione.",
            "osservatori": "{attore} applaude la propria prestazione.",
        },
        "su_bersaglio": {
            "attore": "Applaudi la prestazione di {bersaglio}.",
            "osservatori": "{attore} applaude la prestazione di {bersaglio}.",
            "bersaglio": "{attore} applaude la tua prestazione.",
        },
    },
    "claw": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Mostri gli artigli con rabbia!",
            "osservatori": "{attore} mostra gli artigli con rabbia!",
        },
        "su_se_stesso": {
            "attore": "Ti strappi via gli occhi con gli artigli! OH DIO, IL SANGUE!",
            "osservatori": "{attore} si strappa via gli occhi con gli artigli! OH DIO, IL SANGUE!",
        },
        "su_bersaglio": {
            "attore": "Affondi gli artigli negli occhi di {bersaglio}! OH DIO, IL SANGUE!",
            "osservatori": "{attore} affonda gli artigli negli occhi di {bersaglio}! OH DIO, IL SANGUE!",
            "bersaglio": "{attore} ti affonda gli artigli negli occhi! OH DIO, IL SANGUE!",
        },
    },
    "collapse": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Crolli a terra per lo sfinimento!",
            "osservatori": "{attore} crolla improvvisamente a terra per lo sfinimento!",
        },
        "su_bersaglio": {
            "attore": "Crolli tra le braccia di {bersaglio}.",
            "osservatori": "{attore} crolla improvvisamente tra le braccia di {bersaglio}!",
            "bersaglio": "{attore} ti crolla improvvisamente tra le braccia per lo sfinimento!",
        },
    },
    "cough": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Tossisci rumorosamente.",
            "osservatori": "{attore} tossisce rumorosamente.",
        },
    },
    "cover": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti copri le orecchie per bloccare tutto il rumore.",
            "osservatori": "{attore} si copre le orecchie per bloccare tutto il rumore.",
        },
        "su_se_stesso": {
            "attore": "Ti copri le orecchie per bloccare tutto il rumore.",
            "osservatori": "{attore} si copre le orecchie per bloccare tutto il rumore.",
        },
        "su_bersaglio": {
            "attore": "Ti copri le orecchie per bloccare il rumore che fa {bersaglio}.",
            "osservatori": "{attore} si copre le orecchie per bloccare il rumore che fa {bersaglio}.",
            "bersaglio": "{attore} si copre le orecchie per bloccare il rumore che stai facendo.",
        },
    },
    "cower": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti rannicchi in un angolo e piagnucoli piano.",
            "osservatori": "{attore} si rannicchia in un angolo e piagnucola piano.",
        },
        "su_se_stesso": {
            "attore": "Guardi la tua stessa ombra e ti rannicchi impaurito/a!",
            "osservatori": "{attore} vede la propria ombra e si rannicchia impaurito/a!",
        },
        "su_bersaglio": {
            "attore": "Ti rannicchi lontano da {bersaglio}, piagnucolando piano.",
            "osservatori": "{attore} si rannicchia lontano da {bersaglio}, piagnucolando piano.",
            "bersaglio": "{attore} si rannicchia lontano da te, piagnucolando piano.",
        },
    },
    "cringe": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti ritrai in preda al terrore.",
            "osservatori": "{attore} si ritrae in preda al terrore!",
        },
        "su_se_stesso": {
            "attore": "Non ha senso provare a ritrarti da te stesso/a.",
            "osservatori": "Non ha alcun senso che {attore} provi a ritrarsi da se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Ti ritrai da {bersaglio} in preda al terrore piu' assoluto!",
            "osservatori": "{attore} si ritrae da {bersaglio} in preda al terrore piu' assoluto.",
            "bersaglio": "{attore} si ritrae da te in preda al terrore piu' assoluto.",
        },
    },
    "criticize": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Inizi a criticare aspramente chiunque.",
            "osservatori": "{attore} inizia a criticare aspramente chiunque.",
        },
        "su_se_stesso": {
            "attore": "Ti critichi duramente, sapendo che te lo meriti.",
            "osservatori": "{attore} si critica duramente, e certo se lo merita!",
        },
        "su_bersaglio": {
            "attore": "Inizi a criticare aspramente {bersaglio}.",
            "osservatori": "{attore} inizia improvvisamente a criticare ogni cosa di {bersaglio}!",
            "bersaglio": "{attore} inizia a criticarti aspramente! Che faccia tosta!",
        },
    },
    "cuddle": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti rannicchi contro... te stesso/a?! Ma cosa sei, un contorsionista?!",
            "osservatori": "{attore} prova invano a rannicchiarsi contro... se stesso/a?!",
        },
        "su_bersaglio": {
            "attore": "Ti rannicchi contro {bersaglio} con un sorriso malizioso.",
            "osservatori": "{attore} si rannicchia contro {bersaglio} con un sorriso malizioso.",
            "bersaglio": "{attore} si rannicchia contro di te con un sorriso malizioso.",
        },
    },
    "curse": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Alzi il pugno al cielo e maledici gli Dei! Meglio iniziare a correre...",
            "osservatori": "{attore} alza il pugno al cielo e maledice gli Dei! Meglio allontanarsi in fretta!",
        },
        "su_se_stesso": {
            "attore": "Maledici la tua stessa stupidita'!",
            "osservatori": "{attore} maledice la propria stupidita'!",
        },
        "su_bersaglio": {
            "attore": "Impreca contro {bersaglio} e getta una maledizione su tutta la sua casata!",
            "osservatori": "{attore} impreca contro {bersaglio} e getta una maledizione su tutta la sua casata!",
            "bersaglio": "{attore} impreca contro di te e getta una maledizione su tutta la tua casata!",
        },
    },
    "curtsey": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Fai un inchino con grazia a tutti.",
            "osservatori": "{attore} fa un inchino con grazia a tutti.",
        },
        "su_se_stesso": {
            "attore": "Provi a inchinarti a te stesso/a e per poco non cadi nel tentativo.",
            "osservatori": "{attore} prova invano a inchinarsi a se stesso/a e per poco non finisce a terra.",
        },
        "su_bersaglio": {
            "attore": "Fai un inchino educato a {bersaglio}.",
            "osservatori": "{attore} fa un inchino educato a {bersaglio}.",
            "bersaglio": "{attore} ti fa un inchino educato.",
        },
    },
    "daydream": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Il mondo reale svanisce mentre la tua mente vaga in un sogno ad occhi aperti.",
            "osservatori": "La mente di {attore} vaga via in un sogno ad occhi aperti.",
        },
        "su_bersaglio": {
            "attore": "Ti concedi un sogno ad occhi aperti su {bersaglio}.",
            "osservatori": "{attore} fissa {bersaglio} con sguardo vuoto, perso/a in un sogno ad occhi aperti.",
            "bersaglio": "{attore} ti fissa con sguardo vuoto, apparentemente perso/a in un sogno ad occhi aperti su di te.",
        },
    },
    "dogpile": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Non puoi fare un mucchio selvaggio su te stesso/a!",
            "osservatori": "{attore} non puo' fare un mucchio selvaggio su se stesso/a!",
        },
        "su_bersaglio": {
            "attore": "Urli \"MUCCHIO SELVAGGIO!\" e ti LANCI su {bersaglio}!",
            "osservatori": "{attore} urla \"MUCCHIO SELVAGGIO!\" e si LANCIA su {bersaglio}!",
            "bersaglio": "{attore} urla \"MUCCHIO SELVAGGIO!\" e ti si LANCIA addosso! UFF!",
        },
    },
    "drool": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Inizi a sbavare, facendo un disastro terribile sui tuoi vestiti.",
            "osservatori": "{attore} inizia a sbavare, facendo un disastro terribile sui propri vestiti.",
        },
        "su_se_stesso": {
            "attore": "Guardi in basso mentre sbavi tutto addosso a te stesso/a.",
            "osservatori": "{attore} guarda in basso con aria assente mentre sbava tutto addosso a se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Ti chini su {bersaglio} e inizi a sbavarle/gli addosso.",
            "osservatori": "{attore} si china su {bersaglio} e inizia a sbavarle/gli addosso. Che schifo!",
            "bersaglio": "{attore} si china su di te e inizia a sbavarti addosso! Che schifo...",
        },
    },
    "duck": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti abbassi sulla difensiva!",
            "osservatori": "{attore} si abbassa sulla difensiva.",
        },
        "su_bersaglio": {
            "attore": "Dai un'occhiata a {bersaglio} e ti abbassi sulla difensiva!",
            "osservatori": "{attore} da' un'occhiata a {bersaglio} e si abbassa sulla difensiva!",
            "bersaglio": "{attore} ti guarda un istante e improvvisamente si abbassa sulla difensiva!",
        },
    },
    "embrace": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Provi invano ad abbracciare tutti al mondo!",
            "osservatori": "{attore} prova invano ad abbracciare tutti al mondo!",
        },
        "su_se_stesso": {
            "attore": "Non hai nessuno da abbracciare all'infuori di te stesso/a. Che tristezza...",
            "osservatori": "{attore} abbraccia se stesso/a, non avendo nessun altro da abbracciare. Che tristezza...",
        },
        "su_bersaglio": {
            "attore": "Avvolgi {bersaglio} tra le braccia in un caldo e affettuoso abbraccio.",
            "osservatori": "{attore} avvolge {bersaglio} tra le braccia in un caldo e affettuoso abbraccio.",
            "bersaglio": "{attore} ti avvolge tra le braccia in un caldo e affettuoso abbraccio.",
        },
    },
    "eyebrow": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sollevi un sopracciglio con aria sorniona.",
            "osservatori": "{attore} solleva un sopracciglio con aria sorniona.",
        },
        "su_bersaglio": {
            "attore": "Sollevi un sopracciglio verso {bersaglio}.",
            "osservatori": "{attore} solleva un sopracciglio verso {bersaglio}.",
            "bersaglio": "{attore} solleva un sopracciglio verso di te.",
        },
    },
    "facepalm": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti nascondi il viso tra le mani e sospiri.",
            "osservatori": "{attore} si nasconde il viso tra le mani e sospira.",
        },
        "su_se_stesso": {
            "attore": "Ti nascondi il viso tra le mani, completamente imbarazzato/a dalle tue stesse azioni.",
            "osservatori": "{attore} si nasconde il viso tra le mani, completamente imbarazzato/a dalle proprie azioni.",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} per un istante, poi ti nascondi il viso tra le mani, sfinito/a.",
            "osservatori": "{attore} guarda {bersaglio} per un istante, poi si nasconde il viso tra le mani, sfinito/a.",
            "bersaglio": "{attore} ti guarda per un istante, poi si nasconde il viso tra le mani, sfinito/a.",
        },
    },
    "faint": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Svieni!",
            "osservatori": "{attore} sviene!",
        },
        "su_bersaglio": {
            "attore": "Dai un'occhiata a {bersaglio} e svieni all'istante!",
            "osservatori": "{attore} da' un'occhiata a {bersaglio} e sviene all'istante!",
            "bersaglio": "{attore} ti guarda un istante e sviene immediatamente!",
        },
    },
    "fart": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Lasci andare una scoreggia rumorosa e nauseabonda.",
            "osservatori": "{attore} molla una scoreggia oscena e rumorosa. Che schifo...",
        },
        "su_se_stesso": {
            "attore": "Scoreggi contro te stesso/a. Puah, che schifo...",
            "osservatori": "{attore} improvvisamente scoreggia addosso a se stesso/a. Meglio lui/lei che te...",
        },
        "su_bersaglio": {
            "attore": "Punti il fondoschiena verso {bersaglio} e scoreggi nella sua direzione!",
            "osservatori": "{attore} punta il fondoschiena verso {bersaglio} e scoreggia nella sua direzione!",
            "bersaglio": "{attore} punta il fondoschiena verso di te e lascia andare una scoreggia nauseabonda!",
        },
    },
    "flare": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Le tue narici si dilatano per la rabbia.",
            "osservatori": "Le narici di {attore} si dilatano per la rabbia.",
        },
        "su_se_stesso": {
            "attore": "Le tue narici si dilatano di rabbia per la tua stessa stupidita'.",
            "osservatori": "Le narici di {attore} si dilatano di rabbia per la propria stupidita'.",
        },
        "su_bersaglio": {
            "attore": "Le tue narici si dilatano di rabbia mentre guardi {bersaglio}.",
            "osservatori": "Le narici di {attore} si dilatano di rabbia mentre guarda {bersaglio}.",
            "bersaglio": "Le narici di {attore} si dilatano di rabbia mentre ti guarda.",
        },
    },
    "flash": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Spalanchi l'impermeabile e ti mostri al mondo intero!",
            "osservatori": "{attore} spalanca l'impermeabile e si mostra a tutti!",
        },
        "su_se_stesso": {
            "attore": "Vuoi mostrarti a... te stesso/a? Ma dici sul serio?",
            "osservatori": "{attore} prova disperatamente a mostrarsi a se stesso/a, ma non capisce come fare senza uno specchio.",
        },
        "su_bersaglio": {
            "attore": "Ti giri verso {bersaglio}, spalanchi l'impermeabile, e le/gli mostri quello che hai!",
            "osservatori": "{attore} si gira verso {bersaglio}, spalanca l'impermeabile, e le/gli mostra quello che ha!",
            "bersaglio": "{attore} si gira verso di te, spalanca l'impermeabile, e ti mostra quello che ha! OH MIO DIO!",
        },
    },
    "flex": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Fletti i muscoli con orgoglio!",
            "osservatori": "{attore} flette i muscoli, cercando di fare colpo.",
        },
        "su_bersaglio": {
            "attore": "Mostri i tuoi possenti muscoli a {bersaglio}!",
            "osservatori": "{attore} flette i muscoli per fare colpo su {bersaglio}.",
            "bersaglio": "{attore} flette i muscoli nel vano tentativo di fare colpo su di te.",
        },
    },
    "flinch": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Trasalisci dal dolore.",
            "osservatori": "{attore} trasalisce dal dolore.",
        },
        "su_se_stesso": {
            "attore": "Trasalisci di fronte alle tue stesse azioni.",
            "osservatori": "{attore} trasalisce di fronte alle proprie azioni.",
        },
        "su_bersaglio": {
            "attore": "Trasalisci improvvisamente e ti allontani da {bersaglio}!",
            "osservatori": "{attore} trasalisce improvvisamente e si allontana da {bersaglio}!",
            "bersaglio": "{attore} trasalisce improvvisamente e si allontana da te!",
        },
    },
    "flip": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Fai una capriola all'indietro per la gioia!",
            "osservatori": "{attore} fa una capriola all'indietro per la gioia!",
        },
        "su_se_stesso": {
            "attore": "Fai capriole per tutta la stanza, giubilante!",
            "osservatori": "{attore} fa capriole per tutta la stanza, giubilante!",
        },
        "su_bersaglio": {
            "attore": "Sollevi {bersaglio} sulla spalla e torni verso la tua caverna.",
            "osservatori": "{attore} solleva {bersaglio} sulla spalla e torna verso la propria caverna.",
            "bersaglio": "{attore} ti solleva sulla spalla! URRA'!",
        },
    },
    "flirt": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Inizi a flirtare con chiunque sia nella stanza.",
            "osservatori": "{attore} inizia a flirtare con chiunque sia nella stanza.",
        },
        "su_se_stesso": {
            "attore": "Inizi a flirtare con... te stesso/a?! MA COME?!",
            "osservatori": "{attore} inizia a flirtare con... se stesso/a?! MA COME?!",
        },
        "su_bersaglio": {
            "attore": "Offri a {bersaglio} un sorriso civettuolo mentre le/gli flirti.",
            "osservatori": "{attore} offre a {bersaglio} un sorriso civettuolo mentre flirta con lei/lui.",
            "bersaglio": "{attore} ti offre un sorriso civettuolo mentre flirta con te.",
        },
    },
    "flog": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti frusti senza pieta'! OUCH!",
            "osservatori": "{attore} si frusta senza pieta'!",
        },
        "su_bersaglio": {
            "attore": "Frusti {bersaglio} senza pieta'!",
            "osservatori": "{attore} frusta {bersaglio} senza pieta'!",
            "bersaglio": "{attore} ti frusta senza pieta'! OUCH!",
        },
    },
    "flop": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti accasci a terra per lo sfinimento.",
            "osservatori": "{attore} si accascia a terra per lo sfinimento.",
        },
    },
    "flutter": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Batti le ciglia con fare seducente.",
            "osservatori": "{attore} batte le ciglia con fare seducente.",
        },
        "su_bersaglio": {
            "attore": "Batti le ciglia con fare seducente verso {bersaglio}.",
            "osservatori": "{attore} batte le ciglia con fare seducente verso {bersaglio}.",
            "bersaglio": "{attore} batte le ciglia con fare seducente verso di te.",
        },
    },
    "frown": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Aggrotti la fronte, seccato/a.",
            "osservatori": "{attore} aggrotta la fronte, seccato/a.",
        },
        "su_se_stesso": {
            "attore": "Aggrotti la fronte per le tue stesse azioni.",
            "osservatori": "{attore} aggrotta la fronte per le proprie azioni.",
        },
        "su_bersaglio": {
            "attore": "Aggrotti la fronte verso {bersaglio}.",
            "osservatori": "{attore} aggrotta la fronte verso {bersaglio}.",
            "bersaglio": "{attore} aggrotta la fronte verso di te.",
        },
    },
    "fsm": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Preghi il Mostro di Spaghetti Volante per una guida divina.",
            "osservatori": "{attore} prega il Mostro di Spaghetti Volante per una guida divina.",
        },
        "su_se_stesso": {
            "attore": "Supplichi il Mostro di Spaghetti Volante di toccarti con la Sua Appendice di Tagliatella d'Amore!",
            "osservatori": "{attore} supplica il Mostro di Spaghetti Volante di toccarlo/a con la Sua Appendice di Tagliatella d'Amore!",
        },
        "su_bersaglio": {
            "attore": "Supplichi il Mostro di Spaghetti Volante di toccare {bersaglio} con la Sua Appendice di Tagliatella d'Amore!",
            "osservatori": "{attore} supplica il Mostro di Spaghetti Volante di toccare {bersaglio} con la Sua Appendice di Tagliatella d'Amore!",
            "bersaglio": "{attore} supplica il Mostro di Spaghetti Volante di toccarti con la Sua Appendice di Tagliatella d'Amore!",
        },
    },
    "fume": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Digrigni i denti e fremi di rabbia!",
            "osservatori": "{attore} digrigna i denti e freme di rabbia.",
        },
        "su_se_stesso": {
            "attore": "Fremi di rabbia per la tua stessa stupidita'.",
            "osservatori": "{attore} freme di rabbia per la propria stupidita'.",
        },
        "su_bersaglio": {
            "attore": "Digrigni i denti, fremendo di rabbia verso {bersaglio}!",
            "osservatori": "{attore} digrigna i denti, fremendo di rabbia verso {bersaglio}!",
            "bersaglio": "{attore} digrigna i denti, fremendo di rabbia verso di te!",
        },
    },
    "gasp": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sussulti dallo stupore.",
            "osservatori": "{attore} sussulta dallo stupore.",
        },
        "su_se_stesso": {
            "attore": "Ti guardi e sussulti!",
            "osservatori": "{attore} si guarda e sussulta dallo stupore!",
        },
        "su_bersaglio": {
            "attore": "Sussulti realizzando cosa ha fatto {bersaglio}.",
            "osservatori": "{attore} sussulta realizzando cosa ha fatto {bersaglio}.",
            "bersaglio": "{attore} sussulta realizzando cosa hai fatto.",
        },
    },
    "giggle": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Ridacchi.",
            "osservatori": "{attore} ridacchia.",
        },
        "su_se_stesso": {
            "attore": "Ridacchi di te stesso/a, il che ti fa ridacchiare ancora di piu'.",
            "osservatori": "{attore} ridacchia senza controllo di se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Ridacchi verso {bersaglio}.",
            "osservatori": "{attore} ridacchia verso {bersaglio}.",
            "bersaglio": "{attore} ridacchia verso di te.",
        },
    },
    "goose": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti pizzichi il sedere per qualche strana ragione.",
            "osservatori": "{attore} si pizzica il sedere per qualche ragione sconosciuta.",
        },
        "su_bersaglio": {
            "attore": "Ti avvicini furtivamente alle spalle di {bersaglio} e le/gli pizzichi il sedere!",
            "osservatori": "{attore} si avvicina furtivamente alle spalle di {bersaglio} e le/gli pizzica il sedere!",
            "bersaglio": "{attore} si avvicina furtivamente alle tue spalle e ti pizzica il sedere!",
        },
    },
    "grats": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_bersaglio": {
            "attore": "Ti congratuli calorosamente con {bersaglio}!",
            "osservatori": "{attore} si congratula calorosamente con {bersaglio}!",
            "bersaglio": "{attore} si congratula calorosamente con te! EVVIVA!",
        },
    },
    "grimace": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Fai una smorfia di dolore al solo pensiero.",
            "osservatori": "{attore} fa una smorfia di dolore al solo pensiero.",
        },
        "su_se_stesso": {
            "attore": "Fai una smorfia per i tuoi stessi pensieri.",
            "osservatori": "{attore} fa una smorfia per i propri pensieri.",
        },
        "su_bersaglio": {
            "attore": "Fai una smorfia verso {bersaglio}.",
            "osservatori": "{attore} fa una smorfia verso {bersaglio}.",
            "bersaglio": "{attore} fa una smorfia verso di te.",
        },
    },
    "groan": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Gemi rumorosamente.",
            "osservatori": "{attore} geme rumorosamente.",
        },
        "su_se_stesso": {
            "attore": "Gemi realizzando cosa hai fatto.",
            "osservatori": "{attore} geme realizzando cosa ha fatto.",
        },
        "su_bersaglio": {
            "attore": "Gemi rumorosamente verso {bersaglio}.",
            "osservatori": "{attore} geme rumorosamente verso {bersaglio}.",
            "bersaglio": "{attore} geme rumorosamente verso di te.",
        },
    },
    "grovel": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti prostri nella polvere.",
            "osservatori": "{attore} si prostra nella polvere.",
        },
        "su_se_stesso": {
            "attore": "E' impossibile prostrarsi davanti a se stessi. Mi dispiace.",
            "osservatori": "{attore} prova a prostrarsi davanti a se stesso/a, ma si rende conto che non ha alcun senso.",
        },
        "su_bersaglio": {
            "attore": "Ti prostri nella polvere davanti a {bersaglio}.",
            "osservatori": "{attore} si prostra nella polvere davanti a {bersaglio}.",
            "bersaglio": "{attore} si prostra nella polvere davanti a te.",
        },
    },
    "grumble": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Borbotti piano tra te e te.",
            "osservatori": "{attore} borbotta piano tra se' e se'.",
        },
        "su_se_stesso": {
            "attore": "Borbotti piano tra te e te.",
            "osservatori": "{attore} borbotta piano tra se' e se'.",
        },
        "su_bersaglio": {
            "attore": "Borbotti piano a {bersaglio}.",
            "osservatori": "{attore} borbotta piano a {bersaglio}.",
            "bersaglio": "{attore} ti borbotta piano.",
        },
    },
    "hand": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti baci la tua stessa mano.",
            "osservatori": "{attore} si bacia la propria mano.",
        },
        "su_bersaglio": {
            "attore": "Baci galantemente la mano di {bersaglio}.",
            "osservatori": "{attore} bacia galantemente la mano di {bersaglio}.",
            "bersaglio": "{attore} ti bacia galantemente la mano.",
        },
    },
    "handshake": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Hai gia' fatto la tua conoscenza.",
            "osservatori": "{attore} si rende conto di essersi gia' presentato/a da solo/a.",
        },
        "su_bersaglio": {
            "attore": "Stringi educatamente la mano di {bersaglio}.",
            "osservatori": "{attore} stringe educatamente la mano di {bersaglio}.",
            "bersaglio": "{attore} ti stringe educatamente la mano.",
        },
    },
    "headbutt": {
        "categoria": "ostile",
        "richiede_bersaglio": True,
        "su_bersaglio": {
            "attore": "Afferri {bersaglio} e le/gli SBATTI la testa proprio tra gli occhi! BAM!",
            "osservatori": "{attore} afferra {bersaglio} e le/gli SBATTE la testa proprio tra gli occhi! OUCH!",
            "bersaglio": "{attore} ti afferra e ti SBATTE la testa proprio tra gli occhi! OUCH!",
        },
    },
    "hiccup": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Hai un singhiozzo improvviso.",
            "osservatori": "{attore} ha un singhiozzo.",
        },
    },
    "highfive": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Salti in aria e dai freneticamente il cinque... al vuoto assoluto!",
            "osservatori": "{attore} salta in aria e da' il cinque al vuoto assoluto!",
        },
        "su_se_stesso": {
            "attore": "Provi a darti il cinque da solo/a e quasi ti strappi un muscolo.",
            "osservatori": "{attore} prova invano a darsi il cinque da solo/a, quasi strappandosi un muscolo nel tentativo.",
        },
        "su_bersaglio": {
            "attore": "Dai con entusiasmo un GRANDE cinque a {bersaglio}!",
            "osservatori": "{attore} da' con entusiasmo un GRANDE cinque a {bersaglio}!",
            "bersaglio": "{attore} ti da' con entusiasmo un GRANDE cinque!",
        },
    },
    "hop": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Saltelli in giro come un bambino piccolo.",
            "osservatori": "{attore} saltella in giro come un bambino piccolo.",
        },
    },
    "horn": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Corna ti spuntano dalla testa mentre ti cresce una lunga coda rossa appuntita!",
            "osservatori": "Corna spuntano dalla testa di {attore} mentre gli/le cresce una lunga coda rossa appuntita!",
        },
        "su_se_stesso": {
            "attore": "Corna ti spuntano dalla testa mentre ti cresce una lunga coda rossa appuntita!",
            "osservatori": "Corna spuntano dalla testa di {attore} mentre gli/le cresce una lunga coda rossa appuntita!",
        },
        "su_bersaglio": {
            "attore": "Sogghigni in modo diabolico verso {bersaglio} mentre ti spuntano corna aguzze e una coda rossa appuntita!",
            "osservatori": "{attore} sogghigna in modo diabolico verso {bersaglio} mentre gli/le spuntano corna aguzze e una coda rossa appuntita!",
            "bersaglio": "{attore} ti sogghigna in modo diabolico mentre gli/le spuntano corna aguzze e una coda rossa appuntita!",
        },
    },
    "howl": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Getti la testa all'indietro e ululi alla luna!",
            "osservatori": "{attore} getta la testa all'indietro e ulula alla luna!",
        },
        "su_bersaglio": {
            "attore": "Ululi con desiderio verso {bersaglio}!",
            "osservatori": "{attore} ulula con desiderio verso {bersaglio}!",
            "bersaglio": "{attore} ulula con desiderio verso di te!",
        },
    },
    "hum": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Canticchi piano una melodia distratta.",
            "osservatori": "{attore} canticchia piano una melodia distratta.",
        },
    },
    "hush": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Agiti le mani con impazienza per far tacere tutti.",
            "osservatori": "{attore} agita le mani per far tacere tutti.",
        },
        "su_se_stesso": {
            "attore": "Ti zittisci da solo/a per smettere di parlare.",
            "osservatori": "{attore} si zittisce da solo/a per smettere di parlare.",
        },
        "su_bersaglio": {
            "attore": "Fai educatamente cenno a {bersaglio} di fare silenzio.",
            "osservatori": "{attore} fa educatamente cenno a {bersaglio} di fare silenzio.",
            "bersaglio": "{attore} ti fa educatamente cenno di fare silenzio. Shhhh!",
        },
    },

    # --- Terza tornata (lettere I-Y): ultimi 75 social, stesso metodo ------
    "innocent": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti guardi intorno e fischietti con aria innocente.",
            "osservatori": "{attore} si guarda intorno e fischietta con aria innocente.",
        },
        "su_bersaglio": {
            "attore": "Distogli lo sguardo da {bersaglio} in fretta e fischietti con aria innocente.",
            "osservatori": "{attore} distoglie lo sguardo da {bersaglio} in fretta e fischietta con aria innocente.",
            "bersaglio": "{attore} distoglie lo sguardo da te in fretta e fischietta con aria innocente.",
        },
    },
    "insane": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Senti la tua sanita' mentale scivolare via...",
            "osservatori": "Puoi vedere la sanita' mentale di {attore} scivolare via, poco a poco.",
        },
    },
    "jig": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Balli una allegra giga!",
            "osservatori": "{attore} balla una allegra giga!",
        },
        "su_se_stesso": {
            "attore": "Balli una allegra giga!",
            "osservatori": "{attore} balla una allegra giga!",
        },
        "su_bersaglio": {
            "attore": "Afferri {bersaglio} e balli una allegra giga con lei/lui!",
            "osservatori": "{attore} afferra {bersaglio} e balla una allegra giga con lei/lui!",
            "bersaglio": "{attore} ti afferra e balla una allegra giga con te!",
        },
    },
    "knee": {
        "categoria": "ostile",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Cosa?! Sei impazzito/a?!",
            "osservatori": "{attore} si guarda intorno, confuso/a dalla stessa idea di colpirsi da solo/a.",
        },
        "su_bersaglio": {
            "attore": "Affondi brutalmente il ginocchio nell'inguine di {bersaglio}!",
            "osservatori": "{attore} flette il ginocchio, pronto/a a usarlo su qualcuno, poi lo affonda brutalmente nell'inguine di {bersaglio}! UFF!",
            "bersaglio": "{attore} ti affonda il ginocchio nell'inguine! OH DIO, CHE DOLORE!",
        },
    },
    "laces": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti leghi insieme i tuoi stessi lacci, poi cadi immediatamente a faccia in giu'. Ottimo lavoro!",
            "osservatori": "{attore} si lega insieme i propri lacci, poi cade immediatamente a faccia in giu'.",
        },
        "su_bersaglio": {
            "attore": "Con la furtivita' di un ninja, ti avvicini alle spalle di {bersaglio} e le/gli leghi insieme i lacci!",
            "osservatori": "Con la furtivita' di un ninja, {attore} si avvicina alle spalle di {bersaglio} e le/gli lega insieme i lacci!",
            "bersaglio": "Provi a fare un passo e cadi a faccia in giu'! Qualcuno ti ha legato insieme i lacci delle scarpe!",
        },
    },
    "lightbulb": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "*Ding!* Ispirazione!",
            "osservatori": "Una lampadina appare improvvisamente sopra la testa di {attore}!",
        },
    },
    "lol": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ridi a crepapelle!",
            "osservatori": "{attore} ride a crepapelle!",
        },
        "su_se_stesso": {
            "attore": "E' piuttosto scorretto ridere della propria arguzia.",
            "osservatori": "{attore} ride vistosamente della propria stessa arguzia.",
        },
        "su_bersaglio": {
            "attore": "Ridi a crepapelle per il commento di {bersaglio}!",
            "osservatori": "{attore} ride a crepapelle per il commento di {bersaglio}!",
            "bersaglio": "{attore} ride a crepapelle per il tuo commento!",
        },
    },
    "manicure": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sbadigli con noncuranza e inizi a limarti le unghie per la noia.",
            "osservatori": "{attore} sbadiglia con noncuranza e inizia a limarsi le unghie per la noia.",
        },
        "su_se_stesso": {
            "attore": "Ti prendi un momento per smaltarti le unghie di un bel rosso acceso. Molto carino!",
            "osservatori": "{attore} si prende un momento per smaltarsi le unghie di un bel rosso acceso.",
        },
        "su_bersaglio": {
            "attore": "Afferri le mani di {bersaglio} e inizi a farle/gli una manicure di qualita'.",
            "osservatori": "{attore} afferra le mani di {bersaglio} e inizia a farle/gli una manicure di qualita'.",
            "bersaglio": "{attore} ti afferra le mani e inizia a farti una manicure di qualita'. Molto carino!",
        },
    },
    "massage": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Provi a massaggiarti le spalle da solo/a e quasi ti disloghi un braccio!",
            "osservatori": "{attore} prova a massaggiarsi le spalle da solo/a e quasi si disloca un braccio!",
        },
        "su_bersaglio": {
            "attore": "Massaggi delicatamente le spalle di {bersaglio}.",
            "osservatori": "{attore} massaggia delicatamente le spalle di {bersaglio}.",
            "bersaglio": "{attore} ti massaggia delicatamente le spalle. Ahhh, molto rilassante...",
        },
    },
    "meditate": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Assumi una posizione molto comoda e inizi a meditare.",
            "osservatori": "{attore} si sistema in una posizione comoda e inizia a meditare, canticchiando piano.",
        },
    },
    "moo": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Rumini e muggisci lamentosamente. MUUUUU!",
            "osservatori": "{attore} rumina e lascia andare un lamentoso \"MUUUUU!\"",
        },
        "su_se_stesso": {
            "attore": "Ti sistemi nel pacifico centro del tuo Zen bovino. MUUUUU!",
            "osservatori": "{attore} inizia a muggire piano tra se' e se'.",
        },
        "su_bersaglio": {
            "attore": "Concentri tutto il tuo Zen bovino su {bersaglio} e lasci andare un sonoro \"MUUUUU!\"",
            "osservatori": "{attore} guarda {bersaglio} e lascia andare un sonoro \"MUUUUU!\"",
            "bersaglio": "{attore} ti guarda e lascia andare un sonoro \"MUUUUUUUU!\"",
        },
    },
    "moon": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Ti abbassi i pantaloni e mostri il fondoschiena a tutti nella stanza!",
            "osservatori": "{attore} si abbassa i pantaloni e regala a tutti un sorriso verticale!",
        },
        "su_se_stesso": {
            "attore": "Provi a mostrare il fondoschiena a te stesso/a, ma non riesci a vederlo abbastanza bene.",
            "osservatori": "{attore} rischia le convulsioni cercando di mostrarsi il fondoschiena da solo/a.",
        },
        "su_bersaglio": {
            "attore": "Ti pieghi in avanti e mostri il fondoschiena a {bersaglio}.",
            "osservatori": "{attore} si abbassa i pantaloni e mostra maleducatamente il fondoschiena a {bersaglio}!",
            "bersaglio": "{attore} si piega in avanti e ti regala un sorriso verticale!",
        },
    },
    "mosh": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti agiti per la stanza come un forsennato/a!",
            "osservatori": "{attore} inizia ad agitarsi per la stanza come un forsennato/a!",
        },
        "su_se_stesso": {
            "attore": "I tuoi tentativi di agitarti da solo/a finiscono in un moderato danno fisico.",
            "osservatori": "{attore} prova ad agitarsi da solo/a e rimbalza contro un muro!",
        },
        "su_bersaglio": {
            "attore": "Trascini {bersaglio} nella mischia e ti SCAGLI contro di lei/lui!",
            "osservatori": "{attore} trascina {bersaglio} nella mischia e si SCAGLIA contro di lei/lui!",
            "bersaglio": "{attore} ti trascina nella mischia e si SCAGLIA contro di te!",
        },
    },
    "mourn": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Piangi la tua stessa morte prematura.",
            "osservatori": "{attore} piange la propria morte prematura.",
        },
        "su_bersaglio": {
            "attore": "Piangi tristemente la morte di {bersaglio}.",
            "osservatori": "{attore} piange tristemente la morte di {bersaglio}.",
            "bersaglio": "{attore} piange la tua morte prematura.",
        },
    },
    "mutter": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Borbotti sottovoce.",
            "osservatori": "{attore} borbotta sottovoce.",
        },
        "su_se_stesso": {
            "attore": "Borbotti piano tra te e te.",
            "osservatori": "{attore} borbotta piano tra se' e se'.",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} e borbotti piano.",
            "osservatori": "{attore} guarda {bersaglio} e borbotta piano.",
            "bersaglio": "{attore} ti guarda e borbotta piano.",
        },
    },
    "noogie": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti strofini le nocche in testa da solo/a e crei elettricita' statica! Fico!",
            "osservatori": "{attore} si strofina le nocche in testa da solo/a e crea elettricita' statica!",
        },
        "su_bersaglio": {
            "attore": "Afferri {bersaglio}, la/lo blocchi con una presa alla testa, poi le/gli strofini le nocche sul cranio!",
            "osservatori": "{attore} afferra {bersaglio} in una presa alla testa e le/gli strofina le nocche sul cranio!",
            "bersaglio": "{attore} ti blocca in una presa alla testa e ti strofina le nocche sul cranio!",
        },
    },
    "nudge": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Provi a darti una gomitata da solo/a e finisci con un livido.",
            "osservatori": "{attore} prova a darsi una gomitata da solo/a e finisce con un livido.",
        },
        "su_bersaglio": {
            "attore": "Dai una gomitata a {bersaglio}.",
            "osservatori": "{attore} da' una gomitata a {bersaglio}.",
            "bersaglio": "{attore} ti da' una gomitata.",
        },
    },
    "passout": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "I tuoi occhi si rovesciano all'indietro e sveni!",
            "osservatori": "Gli occhi di {attore} si rovesciano all'indietro e sviene!",
        },
    },
    "peck": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Per quanto ci provi, non riesci proprio a portare le labbra alla tua guancia. ACCIDENTI!",
            "osservatori": "{attore} ha un'aria DAVVERO strana mentre prova a baciarsi la propria guancia.",
        },
        "su_bersaglio": {
            "attore": "Dai a {bersaglio} un dolce bacetto sulla guancia.",
            "osservatori": "{attore} da' a {bersaglio} un dolce bacetto sulla guancia.",
            "bersaglio": "{attore} ti da' un dolce bacetto sulla guancia.",
        },
    },
    "peer": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti guardi intorno con aria sospettosa.",
            "osservatori": "{attore} si guarda intorno con aria sospettosa.",
        },
        "su_se_stesso": {
            "attore": "Diventi strabico/a mentre provi a scrutare te stesso/a.",
            "osservatori": "{attore} diventa strabico/a mentre prova a scrutare se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Scruti {bersaglio} con attenzione.",
            "osservatori": "{attore} scruta {bersaglio} con attenzione.",
            "bersaglio": "{attore} ti scruta con attenzione.",
        },
    },
    "pie": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Raccogli una torta alla panna e inizi a cercare un bersaglio.",
            "osservatori": "{attore} raccoglie una torta alla panna e inizia a cercare un bersaglio.",
        },
        "su_se_stesso": {
            "attore": "Tanto per farlo, ti spiaccichi una torta dritta in FACCIA! Ooo, che panna!",
            "osservatori": "{attore} si spiaccica una torta dritta in FACCIA!",
        },
        "su_bersaglio": {
            "attore": "Lanci una torta a {bersaglio} e la colpisci dritta in FACCIA!",
            "osservatori": "{attore} lancia una torta a {bersaglio} e la colpisce dritta in FACCIA!",
            "bersaglio": "{attore} ti lancia una torta e ti colpisce dritta in FACCIA! Ooo, che panna!",
        },
    },
    "pinch": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti pizzichi per vedere se stai sognando.",
            "osservatori": "{attore} si pizzica per vedere se sta sognando.",
        },
        "su_bersaglio": {
            "attore": "Pizzichi {bersaglio} sul fondoschiena!",
            "osservatori": "{attore} pizzica {bersaglio} sul fondoschiena!",
            "bersaglio": "{attore} ti pizzica sul fondoschiena!",
        },
    },
    "point": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Punti eccitato/a il dito verso... NIENTE!",
            "osservatori": "{attore} punta eccitato/a il dito verso... NIENTE!",
        },
        "su_se_stesso": {
            "attore": "Punti il dito verso te stesso/a!",
            "osservatori": "{attore} punta il dito verso se stesso/a!",
        },
        "su_bersaglio": {
            "attore": "Punti eccitato/a il dito verso {bersaglio}.",
            "osservatori": "{attore} punta eccitato/a il dito verso {bersaglio}!",
            "bersaglio": "{attore} punta eccitato/a il dito verso di TE!",
        },
    },
    "pounce": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Sogghigni in modo maniacale e ti guardi intorno in cerca di qualcuno su cui balzare.",
            "osservatori": "{attore} sogghigna come un forsennato/a e si guarda intorno in cerca di qualcuno su cui balzare!",
        },
        "su_se_stesso": {
            "attore": "Corri in cerchio, provando invano a balzare su te stesso/a!",
            "osservatori": "{attore} corre in cerchio come un forsennato/a, provando invano a balzare su se stesso/a!",
        },
        "su_bersaglio": {
            "attore": "Ti accovacci, sogghigni come un pazzo/a, poi BALZI su {bersaglio} come una tigre affamata!",
            "osservatori": "{attore} si accovaccia, sogghigna come un pazzo/a, poi BALZA su {bersaglio} come una tigre affamata!",
            "bersaglio": "{attore} ti BALZA addosso con un grido maniacale!",
        },
    },
    "pout": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sporgi il labbro inferiore e fai il broncio, triste.",
            "osservatori": "{attore} fa il broncio, triste.",
        },
    },
    "propose": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Ti inginocchi su un ginocchio e cerchi qualcuno a cui fare una proposta.",
            "osservatori": "{attore} si inginocchia su un ginocchio e cerca qualcuno a cui fare una proposta.",
        },
        "su_se_stesso": {
            "attore": "Ti inginocchi su un ginocchio e fai una proposta a... te stesso/a?! E se dici di no?!",
            "osservatori": "{attore} si inginocchia su un ginocchio e fa una proposta a... se stesso/a?! Che tristezza...",
        },
        "su_bersaglio": {
            "attore": "Ti inginocchi su un ginocchio e fai una proposta a {bersaglio}!",
            "osservatori": "{attore} si inginocchia su un ginocchio e fa una proposta a {bersaglio}! Che romantico!",
            "bersaglio": "{attore} si inginocchia su un ginocchio e fa una proposta a TE!",
        },
    },
    "puke": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti afferri lo stomaco e vomiti dappertutto!",
            "osservatori": "{attore} si afferra lo stomaco e vomita dappertutto!",
        },
    },
    "purr": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Fai le fusa soddisfatto/a.",
            "osservatori": "{attore} fa le fusa soddisfatto/a.",
        },
        "su_se_stesso": {
            "attore": "Fai le fusa piano tra te e te.",
            "osservatori": "{attore} fa le fusa piano tra se' e se'.",
        },
        "su_bersaglio": {
            "attore": "Ti strofini contro {bersaglio} e fai le fusa soddisfatto/a.",
            "osservatori": "{attore} si strofina contro {bersaglio} e fa le fusa soddisfatto/a.",
            "bersaglio": "{attore} si strofina contro di te e fa le fusa soddisfatto/a.",
        },
    },
    "pwn": {
        "categoria": "ostile",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "uz1 i tu0i p0t3r1 l33t x sputtanart1 da s0l0/a!!!11 omgrotflmao!!!11uno",
            "osservatori": "{attore} usa i suoi poteri leet per sputtanarsi da solo/a!!!11 che imbarazzo!!!11uno",
        },
        "su_bersaglio": {
            "attore": "usi i tuoi poteri leet per sputtanare TOTALMENTE {bersaglio}!!!11 omgrotflmao!!!11uno",
            "osservatori": "{attore} usa i suoi poteri leet per sputtanare totalmente {bersaglio}!!!11 omgrotflmao!!!11uno",
            "bersaglio": "{attore} usa i suoi poteri leet per sputtanarti TOTALMENTE!!!11 omgrotflmao!!!11uno",
        },
    },
    "ramble": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Vai avanti a vanvera, parlando di niente in particolare.",
            "osservatori": "{attore} va avanti a vanvera, parlando di niente in particolare.",
        },
        "su_se_stesso": {
            "attore": "Vaneggi piano tra te e te, sottovoce.",
            "osservatori": "{attore} vaneggia piano tra se' e se', sottovoce.",
        },
        "su_bersaglio": {
            "attore": "Metti {bersaglio} all'angolo e la/lo bombardi con i tuoi noiosi vaneggiamenti.",
            "osservatori": "{attore} mette all'angolo la povera {bersaglio} e la bombarda di vaneggiamenti senza senso.",
            "bersaglio": "{attore} ti mette all'angolo e inizia a vaneggiare senza sosta...",
        },
    },
    "raspberry": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Tiri fuori la lingua e fai una pernacchia al mondo intero! Ecco fatto!",
            "osservatori": "{attore} tira fuori la lingua e fa una pernacchia al mondo intero!",
        },
        "su_se_stesso": {
            "attore": "Perche' disturbarsi? Finiresti solo con la saliva che ti cola giu' per il mento.",
            "osservatori": "{attore} valuta di farsi una pernacchia da solo/a, poi ci ripensa.",
        },
        "su_bersaglio": {
            "attore": "Tiri fuori la lingua verso {bersaglio} e le/gli fai una pernacchia!",
            "osservatori": "{attore} tira fuori la lingua verso {bersaglio} e le/gli fa una pernacchia! Che schifo...",
            "bersaglio": "Vieni schizzato/a di saliva mentre {attore} ti fa una pernacchia! Che schifo...",
        },
    },
    "rofl": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Crolli a terra e ti rotoli, ridendo istericamente!",
            "osservatori": "{attore} crolla a terra e si rotola, ridendo istericamente!",
        },
        "su_bersaglio": {
            "attore": "Ti rotoli a terra, ridendo delle buffonate di {bersaglio}!",
            "osservatori": "{attore} si rotola a terra, ridendo delle buffonate di {bersaglio}!",
            "bersaglio": "{attore} si rotola a terra, ridendo delle tue buffonate!",
        },
    },
    "roll": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Alzi gli occhi al cielo, esasperato/a.",
            "osservatori": "{attore} alza gli occhi al cielo, esasperato/a.",
        },
        "su_se_stesso": {
            "attore": "Perche' disturbarsi? Non riusciresti comunque a vederlo.",
            "osservatori": "{attore} valuta di alzare gli occhi al cielo verso se stesso/a, poi ci rinuncia.",
        },
        "su_bersaglio": {
            "attore": "Alzi gli occhi al cielo, esasperato/a, verso {bersaglio}.",
            "osservatori": "{attore} alza gli occhi al cielo, esasperato/a, verso {bersaglio}.",
            "bersaglio": "{attore} alza gli occhi al cielo verso di te, esasperato/a.",
        },
    },
    "rose": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Inspiri il dolce profumo della tua rosa.",
            "osservatori": "{attore} inspira il dolce profumo della propria rosa.",
        },
        "su_bersaglio": {
            "attore": "Regali una splendida rosa a {bersaglio}!",
            "osservatori": "{attore} regala una splendida rosa a {bersaglio}!",
            "bersaglio": "{attore} ti regala una splendida rosa!",
        },
    },
    "ruffle": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti scompigli i capelli per ottenere quella pettinatura perfetta. Molto chic!",
            "osservatori": "{attore} si scompiglia i capelli per ottenere quella pettinatura perfetta. Molto chic!",
        },
        "su_bersaglio": {
            "attore": "Scompigli i capelli di {bersaglio} in modo giocoso.",
            "osservatori": "{attore} scompiglia i capelli di {bersaglio} in modo giocoso.",
            "bersaglio": "{attore} ti scompiglia i capelli in modo giocoso.",
        },
    },
    "run": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Scappi via in preda al terrore piu' assoluto!",
            "osservatori": "{attore} scappa via in preda al terrore piu' assoluto!",
        },
        "su_se_stesso": {
            "attore": "Provi a scappare da te stesso/a, ma non puoi sfuggirti!",
            "osservatori": "{attore} prova a scappare da se stesso/a, ma non riesce a sfuggirsi!",
        },
        "su_bersaglio": {
            "attore": "Scappi via da {bersaglio} il piu' velocemente possibile!",
            "osservatori": "{attore} scappa via da {bersaglio} il piu' velocemente possibile!",
            "bersaglio": "{attore} scappa via da te il piu' velocemente possibile!",
        },
    },
    "scream": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Urli terrorizzato/a!",
            "osservatori": "{attore} urla terrorizzato/a!",
        },
    },
    "serenade": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Fai una serenata al mondo intero con la tua canzone!",
            "osservatori": "{attore} fa una serenata al mondo intero con la propria canzone!",
        },
        "su_se_stesso": {
            "attore": "Fai una serenata alle voci nella tua testa con la musica!",
            "osservatori": "{attore} fa una serenata alle voci nella propria testa con la musica!",
        },
        "su_bersaglio": {
            "attore": "Fai una serenata a {bersaglio} con una ballata romantica!",
            "osservatori": "{attore} fa una serenata a {bersaglio} con una ballata romantica!",
            "bersaglio": "{attore} ti fa una serenata con una ballata romantica!",
        },
    },
    "shake": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Scuoti la testa.",
            "osservatori": "{attore} scuote la testa.",
        },
        "su_se_stesso": {
            "attore": "Scuoti la testa per far tacere le voci.",
            "osservatori": "{attore} scuote la testa per far tacere le voci.",
        },
        "su_bersaglio": {
            "attore": "Scuoti la testa verso {bersaglio}.",
            "osservatori": "{attore} scuote la testa verso {bersaglio}.",
            "bersaglio": "{attore} scuote la testa verso di te.",
        },
    },
    "shiver": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Rabbrividisci a disagio.",
            "osservatori": "{attore} rabbrividisce a disagio.",
        },
        "su_se_stesso": {
            "attore": "Rabbrividisci per i pensieri nella tua testa.",
            "osservatori": "{attore} rabbrividisce per i propri pensieri.",
        },
        "su_bersaglio": {
            "attore": "Dai un'occhiata a {bersaglio} e rabbrividisci a disagio.",
            "osservatori": "{attore} da' un'occhiata a {bersaglio} e rabbrividisce a disagio.",
            "bersaglio": "{attore} ti guarda e rabbrividisce a disagio.",
        },
    },
    "skip": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Saltelli in giro allegramente!",
            "osservatori": "{attore} saltella in giro allegramente!",
        },
        "su_se_stesso": {
            "attore": "Saltelli in giro allegramente al ritmo della musica nella tua testa!",
            "osservatori": "{attore} saltella in giro allegramente al ritmo della musica nella propria testa!",
        },
        "su_bersaglio": {
            "attore": "Afferri la mano di {bersaglio} e saltelli in giro allegramente con lei/lui!",
            "osservatori": "{attore} afferra la mano di {bersaglio} e saltella in giro allegramente con lei/lui!",
            "bersaglio": "{attore} ti afferra la mano e saltella in giro allegramente con te!",
        },
    },
    "slobber": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sbavi tutto addosso a te stesso/a.",
            "osservatori": "{attore} sbava tutto addosso a se stesso/a.",
        },
    },
    "smirk": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sogghigni con aria complice.",
            "osservatori": "{attore} sogghigna con aria complice.",
        },
        "su_se_stesso": {
            "attore": "Sogghigni per i tuoi stessi pensieri maliziosi.",
            "osservatori": "{attore} sogghigna per i propri pensieri maliziosi.",
        },
        "su_bersaglio": {
            "attore": "Sogghigni con aria complice verso {bersaglio}.",
            "osservatori": "{attore} sogghigna con aria complice verso {bersaglio}.",
            "bersaglio": "{attore} ti sogghigna con aria complice.",
        },
    },
    "snap": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Schiocchi le dita! AH-HA!",
            "osservatori": "{attore} schiocca le dita! AH-HA!",
        },
        "su_se_stesso": {
            "attore": "Scatti sull'attenti! ATTENTI!",
            "osservatori": "{attore} scatta sull'attenti!",
        },
        "su_bersaglio": {
            "attore": "Schiocchi le dita per attirare l'attenzione di {bersaglio}.",
            "osservatori": "{attore} schiocca le dita per attirare l'attenzione di {bersaglio}.",
            "bersaglio": "{attore} schiocca le dita verso di te! Attenzione!",
        },
    },
    "snarl": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Ringhi con rabbia.",
            "osservatori": "{attore} ringhia con rabbia.",
        },
        "su_se_stesso": {
            "attore": "Ringhi per la tua stessa stupidita'.",
            "osservatori": "{attore} ringhia per la propria stupidita'.",
        },
        "su_bersaglio": {
            "attore": "Ringhi con rabbia verso {bersaglio}.",
            "osservatori": "{attore} ringhia con rabbia verso {bersaglio}.",
            "bersaglio": "{attore} ti ringhia contro con rabbia.",
        },
    },
    "sneeze": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Starnutisci rumorosamente! ETCIU'!",
            "osservatori": "{attore} starnutisce rumorosamente!",
        },
    },
    "snicker": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ridacchi piano.",
            "osservatori": "{attore} ridacchia piano.",
        },
        "su_se_stesso": {
            "attore": "Ridacchi per i tuoi stessi pensieri malvagi.",
            "osservatori": "{attore} ridacchia per i propri pensieri malvagi.",
        },
        "su_bersaglio": {
            "attore": "Ridacchi piano verso {bersaglio}.",
            "osservatori": "{attore} ridacchia piano verso {bersaglio}.",
            "bersaglio": "{attore} ridacchia piano verso di te.",
        },
    },
    "sniff": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Tiri su col naso, triste.",
            "osservatori": "{attore} tira su col naso, triste.",
        },
        "su_se_stesso": {
            "attore": "Tiri su col naso, triste per la tua stessa incompetenza.",
            "osservatori": "{attore} tira su col naso, triste per la propria incompetenza.",
        },
        "su_bersaglio": {
            "attore": "Tiri su col naso, rattristato/a dal modo in cui {bersaglio} ti tratta.",
            "osservatori": "{attore} tira su col naso, rattristato/a dal modo in cui {bersaglio} lo/la tratta.",
            "bersaglio": "{attore} tira su col naso, rattristato/a dal modo in cui lo/la stai trattando.",
        },
    },
    "snore": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Russi rumorosamente.",
            "osservatori": "{attore} russa rumorosamente.",
        },
    },
    "snort": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sbuffi con aria derisoria.",
            "osservatori": "{attore} sbuffa con aria derisoria.",
        },
        "su_se_stesso": {
            "attore": "Sbuffi per la tua stessa stupidita'.",
            "osservatori": "{attore} sbuffa per la propria stupidita'.",
        },
        "su_bersaglio": {
            "attore": "Sbuffi con aria derisoria verso {bersaglio}.",
            "osservatori": "{attore} sbuffa con aria derisoria verso {bersaglio}.",
            "bersaglio": "{attore} ti sbuffa contro con aria derisoria.",
        },
    },
    "snowball": {
        "categoria": "neutro",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Evochi una palla di neve dal nulla e inizi a mangiarla. Mmmm, neve...",
            "osservatori": "{attore} evoca una palla di neve dal nulla e inizia a mangiarla.",
        },
        "su_bersaglio": {
            "attore": "Evochi una palla di neve dal nulla e la lanci in faccia a {bersaglio}!",
            "osservatori": "{attore} evoca una palla di neve dal nulla e la lancia dritta in faccia a {bersaglio}!",
            "bersaglio": "{attore} evoca una palla di neve dal nulla e te la lancia dritta in faccia!",
        },
    },
    "snuggle": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti raggomitoli al tuo posto e ti prepari a dormire.",
            "osservatori": "{attore} si raggomitola al proprio posto e si prepara a dormire.",
        },
        "su_bersaglio": {
            "attore": "Ti raggomitoli accanto a {bersaglio}.",
            "osservatori": "{attore} si raggomitola accanto a {bersaglio}.",
            "bersaglio": "{attore} si raggomitola accanto a te.",
        },
    },
    "sob": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Singhiozzi miseramente.",
            "osservatori": "{attore} singhiozza miseramente.",
        },
        "su_se_stesso": {
            "attore": "Singhiozzi piano tra te e te.",
            "osservatori": "{attore} singhiozza piano tra se' e se'.",
        },
        "su_bersaglio": {
            "attore": "Singhiozzi miseramente sulla spalla di {bersaglio}.",
            "osservatori": "{attore} singhiozza miseramente sulla spalla di {bersaglio}.",
            "bersaglio": "{attore} singhiozza miseramente sulla tua spalla.",
        },
    },
    "squeal": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Strilli di gioia!",
            "osservatori": "{attore} lascia andare improvvisamente uno strillo di gioia!",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} e strilli di gioia!",
            "osservatori": "{attore} guarda {bersaglio} e strilla di gioia!",
            "bersaglio": "{attore} ti guarda e strilla di gioia!",
        },
    },
    "squeeze": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Stringi affettuosamente il tuo amico immaginario. Che tristezza...",
            "osservatori": "{attore} stringe affettuosamente il proprio amico immaginario. Che tristezza...",
        },
        "su_bersaglio": {
            "attore": "Stringi {bersaglio} affettuosamente.",
            "osservatori": "{attore} stringe {bersaglio} affettuosamente.",
            "bersaglio": "{attore} ti stringe affettuosamente.",
        },
    },
    "stagger": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Barcolli instabile per la stanza.",
            "osservatori": "{attore} barcolla instabile per la stanza.",
        },
        "su_bersaglio": {
            "attore": "Provi disperatamente a barcollare verso {bersaglio}!",
            "osservatori": "{attore} prova disperatamente a barcollare verso {bersaglio}!",
            "bersaglio": "{attore} prova disperatamente a barcollare verso di te!",
        },
    },
    "stare": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Fissi il cielo con sguardo assente.",
            "osservatori": "{attore} fissa il cielo con sguardo assente.",
        },
        "su_se_stesso": {
            "attore": "Ti fissi sognante. Stai bene!",
            "osservatori": "{attore} si fissa sognante.",
        },
        "su_bersaglio": {
            "attore": "Fissi {bersaglio} sognante, completamente perso/a nei suoi occhi.",
            "osservatori": "{attore} fissa {bersaglio} sognante.",
            "bersaglio": "{attore} ti fissa sognante, completamente perso/a nei tuoi occhi.",
        },
    },
    "stretch": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Inarchi la schiena e allunghi braccia e gambe con voluttuoso piacere. Ahhhh!",
            "osservatori": "{attore} inarca la schiena e allunga braccia e gambe con voluttuoso piacere.",
        },
    },
    "strut": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sfoggi tutto te stesso/a con orgoglio! Oh yeah! Fatti valere!",
            "osservatori": "{attore} sfoggia se stesso/a con orgoglio.",
        },
        "su_se_stesso": {
            "attore": "Sfoggi te stesso/a davanti a uno specchio. Stai bene!",
            "osservatori": "{attore} sfoggia se stesso/a davanti a uno specchio. Che tristezza...",
        },
        "su_bersaglio": {
            "attore": "Sfoggi te stesso/a proprio davanti a {bersaglio}. Impressionante!",
            "osservatori": "{attore} sfoggia se stesso/a proprio davanti a {bersaglio}.",
            "bersaglio": "{attore} sfoggia se stesso/a proprio davanti a te.",
        },
    },
    "sulk": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Fai il broncio nell'angolo.",
            "osservatori": "{attore} fa il broncio nell'angolo.",
        },
    },
    "swoon": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti senti mancare in un'estasi assoluta.",
            "osservatori": "{attore} si sente mancare in un'estasi assoluta.",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} e ti senti mancare dall'estasi.",
            "osservatori": "{attore} guarda {bersaglio} e si sente mancare dall'estasi.",
            "bersaglio": "{attore} ti guarda e si sente mancare dall'estasi.",
        },
    },
    "tackle": {
        "categoria": "amichevole",
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Non puoi placcare te stesso/a!",
            "osservatori": "{attore} si rende conto che non puo' placcare se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Placchi {bersaglio} in modo giocoso!",
            "osservatori": "{attore} placca {bersaglio} in modo giocoso!",
            "bersaglio": "{attore} ti placca a terra in modo giocoso!",
        },
    },
    "tag": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Ti guardi intorno in cerca di qualcuno con cui giocare ad acchiapparello.",
            "osservatori": "{attore} si guarda intorno in cerca di qualcuno con cui giocare ad acchiapparello.",
        },
        "su_se_stesso": {
            "attore": "Ovviamente confuso/a dalle regole del gioco, tocchi semplicemente te stesso/a.",
            "osservatori": "Ovviamente confuso/a dalle regole del gioco, {attore} tocca semplicemente se stesso/a.",
        },
        "su_bersaglio": {
            "attore": "Ti tuffi fuori dall'ombra e TOCCHI {bersaglio}! {bersaglio} e' IT!",
            "osservatori": "{attore} si tuffa fuori dall'ombra e TOCCA {bersaglio}. {bersaglio} E' IT!",
            "bersaglio": "{attore} si tuffa fuori dall'ombra e ti TOCCA! Sei TU l'IT!",
        },
    },
    "tap": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Batti il piede con impazienza.",
            "osservatori": "{attore} batte il piede con impazienza.",
        },
        "su_se_stesso": {
            "attore": "Ti batti la fronte per far tacere le voci nella tua testa.",
            "osservatori": "{attore} si batte la fronte per far tacere le voci nella propria testa.",
        },
        "su_bersaglio": {
            "attore": "Dai un colpetto sulla spalla a {bersaglio}.",
            "osservatori": "{attore} da' un colpetto sulla spalla a {bersaglio}.",
            "bersaglio": "{attore} ti da' un colpetto sulla spalla.",
        },
    },
    "threaten": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Alzi il pugno e minacci IL MONDO INTERO!",
            "osservatori": "{attore} alza il pugno e minaccia IL MONDO INTERO!",
        },
        "su_se_stesso": {
            "attore": "Minacci le voci nella tua testa per farle tacere!",
            "osservatori": "{attore} minaccia con rabbia le voci nella propria testa!",
        },
        "su_bersaglio": {
            "attore": "Alzi il pugno e minacci {bersaglio}!",
            "osservatori": "{attore} alza il pugno e minaccia {bersaglio}!",
            "bersaglio": "{attore} alza il pugno e minaccia TE!",
        },
    },
    "tip": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Ti tocchi galantemente il cappello.",
            "osservatori": "{attore} si tocca galantemente il cappello.",
        },
        "su_bersaglio": {
            "attore": "Ti tocchi il cappello verso {bersaglio}.",
            "osservatori": "{attore} si tocca galantemente il cappello verso {bersaglio}.",
            "bersaglio": "{attore} si tocca galantemente il cappello verso di te.",
        },
    },
    "twiddle": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Gira i pollici pazientemente.",
            "osservatori": "{attore} gira i pollici pazientemente.",
        },
    },
    "type": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Alzi le mani al cielo, disgustato/a dalle tue pessime doti di battitura! AARGH!",
            "osservatori": "{attore} alza le mani al cielo, disgustato/a dalle proprie pessime doti di battitura! AARGH!",
        },
    },
    "whine": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti lamenti in modo patetico come una bambina viziata. UAAAAAAA!",
            "osservatori": "{attore} si lamenta in modo patetico come una bambina viziata. UAAAAAAA!",
        },
        "su_se_stesso": {
            "attore": "Ti lamenti in modo patetico con te stesso/a. Finalmente! Qualcuno che ti ascolta!",
            "osservatori": "{attore} si lamenta in modo patetico con se stesso/a. Meglio che lamentarsi con te!",
        },
        "su_bersaglio": {
            "attore": "Ti lamenti in modo patetico con {bersaglio}, sperando che possa sistemare le cose.",
            "osservatori": "{attore} si lamenta in modo patetico con {bersaglio}.",
            "bersaglio": "{attore} si lamenta in modo patetico con te, apparentemente convinto/a che tu ci tenga davvero.",
        },
    },
    "whistle": {
        "categoria": "amichevole",
        "senza_bersaglio": {
            "attore": "Fischi con approvazione.",
            "osservatori": "{attore} fischia con approvazione.",
        },
        "su_se_stesso": {
            "attore": "Fischietti una piccola melodia tra te e te.",
            "osservatori": "{attore} fischietta una piccola melodia tra se' e se'.",
        },
        "su_bersaglio": {
            "attore": "Fischi alla vista di {bersaglio}!",
            "osservatori": "{attore} fischia alla vista di {bersaglio}!",
            "bersaglio": "{attore} fischia alla vista di te!",
        },
    },
    "wince": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Trasalisci d'agonia.",
            "osservatori": "{attore} trasalisce d'agonia.",
        },
    },
    "wonder": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti guardi intorno e ti chiedi cosa diavolo stia succedendo.",
            "osservatori": "{attore} si guarda intorno e si chiede cosa diavolo stia succedendo.",
        },
        "su_se_stesso": {
            "attore": "Inizi a chiederti cosa diavolo tu stia facendo qui.",
            "osservatori": "{attore} inizia a chiedersi quale sia il proprio posto nell'universo.",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} e ti chiedi cosa diavolo stia dicendo.",
            "osservatori": "{attore} guarda {bersaglio} con aria interrogativa.",
            "bersaglio": "{attore} ti guarda con aria interrogativa, chiedendosi cosa diavolo tu stia dicendo.",
        },
    },
    "worry": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Ti preoccupi per quello che sta per succedere.",
            "osservatori": "Un'espressione preoccupata attraversa improvvisamente il volto di {attore}. Cosa potrebbe esserci che non va?",
        },
        "su_se_stesso": {
            "attore": "Ti preoccupi per quello che sta per succedere.",
            "osservatori": "Un'espressione preoccupata attraversa improvvisamente il volto di {attore}. Cosa potrebbe esserci che non va?",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} con aria preoccupata.",
            "osservatori": "{attore} guarda {bersaglio} con sguardo preoccupato.",
            "bersaglio": "{attore} ti guarda con aria preoccupata.",
        },
    },
    "yae": {
        "categoria": "ostile",
        "senza_bersaglio": {
            "attore": "Sospiri, gravato/a dall'ennesimo idiota di turno.",
            "osservatori": "{attore} sospira, gravato/a dall'ennesimo idiota di turno.",
        },
        "su_se_stesso": {
            "attore": "Gemi, improvvisamente consapevole di essere tu stesso/a l'ennesimo idiota di turno.",
            "osservatori": "{attore} geme, rendendosi conto di essere l'ennesimo idiota di turno.",
        },
        "su_bersaglio": {
            "attore": "Sospiri, frustrato/a dal fatto che {bersaglio} sia l'ennesimo idiota di turno.",
            "osservatori": "{attore} sospira, frustrato/a dal fatto che {bersaglio} sia l'ennesimo idiota di turno.",
            "bersaglio": "{attore} sospira, frustrato/a dal fatto che tu sia l'ennesimo idiota di turno.",
        },
    },
    "yawn": {
        "categoria": "neutro",
        "senza_bersaglio": {
            "attore": "Sbadigli.",
            "osservatori": "{attore} sbadiglia.",
        },
    },

    # --- Quarta tornata: categoria "sessuale" (19 voci, KISS gia' fatto in
    # Fase G/corretto in Fase J). Confermato dalla fonte che restano PG-13:
    # "Sexual socials do not include any graphic or explicitly obscene
    # content" - qui tradotti mantenendo lo stesso registro allusivo ma
    # non esplicito dell'originale. Tutti con "vietato_newbie": True.
    "caress": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti accarezzi teneramente... da solo/a?!",
            "osservatori": "Le mani di {attore} si muovono nervose in cerca di qualcuno da accarezzare, poi si accarezza teneramente... da solo/a?!",
        },
        "su_bersaglio": {
            "attore": "Accarezzi teneramente {bersaglio}.",
            "osservatori": "{attore} accarezza teneramente {bersaglio}.",
            "bersaglio": "{attore} accarezza teneramente il tuo corpo.",
        },
    },
    "fondle": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti palpeggi affettuosamente... da solo/a?! Nessuno vuole vederlo!",
            "osservatori": "{attore} si palpeggia... da solo/a?! Che schifo...",
        },
        "su_bersaglio": {
            "attore": "Allunghi le mani e palpeggi affettuosamente {bersaglio}!",
            "osservatori": "{attore} allunga le mani e palpeggia affettuosamente {bersaglio}!",
            "bersaglio": "{attore} allunga le mani e ti palpeggia affettuosamente! CIAO!",
        },
    },
    "french": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Baci appassionatamente il dorso della tua stessa mano. Che tristezza...",
            "osservatori": "{attore} bacia appassionatamente il dorso della propria mano. Che tristezza...",
        },
        "su_bersaglio": {
            "attore": "Dai a {bersaglio} un bacio lungo, profondo e appassionato che sembra durare un'eternita'!",
            "osservatori": "{attore} da' a {bersaglio} un bacio lungo e appassionato!",
            "bersaglio": "{attore} ti da' un bacio lungo, profondo e appassionato che sembra durare un'eternita'!",
        },
    },
    "grope": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Non hai nessuno da palpare all'infuori di te stesso/a. Che tristezza...",
            "osservatori": "{attore} non ha nessuno da palpare all'infuori di se stesso/a. Che tristezza...",
        },
        "su_bersaglio": {
            "attore": "Palpi il corpo di {bersaglio} con desiderio!",
            "osservatori": "{attore} palpa il corpo di {bersaglio} con desiderio!",
            "bersaglio": "{attore} palpa il tuo corpo con desiderio!",
        },
    },
    "lick": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Ti lecchi le labbra e sorridi affamato/a.",
            "osservatori": "{attore} si lecca le labbra e sorride affamato/a.",
        },
        "su_se_stesso": {
            "attore": "Ti lecchi... da solo/a?!",
            "osservatori": "{attore} si lecca... da solo/a?!",
        },
        "su_bersaglio": {
            "attore": "Lecchi {bersaglio} in modo provocante.",
            "osservatori": "{attore} lecca {bersaglio} in modo provocante.",
            "bersaglio": "{attore} ti lecca in modo provocante.",
        },
    },
    "love": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Dichiari il tuo amore per il mondo intero!",
            "osservatori": "{attore} dichiara il proprio amore per il mondo intero!",
        },
        "su_se_stesso": {
            "attore": "Dichiari il tuo amore eterno per... te stesso/a?!",
            "osservatori": "{attore} dichiara il proprio amore eterno per... se stesso/a?!",
        },
        "su_bersaglio": {
            "attore": "Proclami il tuo amore eterno per {bersaglio}!",
            "osservatori": "{attore} proclama il proprio amore eterno per {bersaglio}!",
            "bersaglio": "{attore} proclama il proprio amore eterno per TE!",
        },
    },
    "lust": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Sei di umore molto lussurioso oggi.",
            "osservatori": "{attore} sembra essere di umore molto lussurioso oggi.",
        },
        "su_se_stesso": {
            "attore": "Desideri il tuo stesso corpo?! Che tristezza...",
            "osservatori": "{attore} desidera il proprio corpo. Che pena...",
        },
        "su_bersaglio": {
            "attore": "Desideri con passione lo squisito corpo di {bersaglio}!",
            "osservatori": "{attore} desidera il corpo di {bersaglio}.",
            "bersaglio": "{attore} desidera con passione il tuo squisito corpo! WOW!",
        },
    },
    "moan": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Gemi piano.",
            "osservatori": "{attore} geme piano.",
        },
        "su_se_stesso": {
            "attore": "Gemi tristemente per la scelta dei tuoi vestiti. Che pessimo completo!",
            "osservatori": "{attore} geme tristemente per la scelta dei propri vestiti. E con buona ragione...",
        },
        "su_bersaglio": {
            "attore": "Gemi piano nell'orecchio di {bersaglio}.",
            "osservatori": "{attore} geme piano nell'orecchio di {bersaglio}.",
            "bersaglio": "{attore} geme piano nel tuo orecchio.",
        },
    },
    "nibble": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Provi invano a mordicchiarti il tuo stesso orecchio e senti un forte *CRAC!* nel collo. Uh-oh...",
            "osservatori": "{attore} prova invano a mordicchiarsi il proprio orecchio e quasi si incrina il collo.",
        },
        "su_bersaglio": {
            "attore": "Mordicchi delicatamente l'orecchio di {bersaglio}.",
            "osservatori": "{attore} mordicchia delicatamente l'orecchio di {bersaglio}.",
            "bersaglio": "{attore} ti mordicchia delicatamente l'orecchio.",
        },
    },
    "nuzzle": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Non puoi strofinare il naso sul tuo stesso collo, per quanto tu ci provi.",
            "osservatori": "{attore} prova invano a strofinare il naso sul proprio collo.",
        },
        "su_bersaglio": {
            "attore": "Strofini dolcemente il naso sul collo di {bersaglio}.",
            "osservatori": "{attore} strofina dolcemente il naso sul collo di {bersaglio}.",
            "bersaglio": "{attore} strofina dolcemente il naso sul tuo collo.",
        },
    },
    "pant": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Ansimi per lo sfinimento.",
            "osservatori": "{attore} ansima pesantemente per lo sfinimento.",
        },
        "su_bersaglio": {
            "attore": "Dai un'occhiata a {bersaglio} e inizi ad ansimare con desiderio.",
            "osservatori": "{attore} da' un'occhiata a {bersaglio} e inizia ad ansimare con desiderio.",
            "bersaglio": "{attore} ti guarda e inizia ad ansimare con desiderio.",
        },
    },
    "rub": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Ti sfreghi le mani in avida attesa.",
            "osservatori": "{attore} si sfrega le mani in avida attesa.",
        },
        "su_se_stesso": {
            "attore": "Ti sfiori lentamente il corpo con le mani.",
            "osservatori": "{attore} si sfiora lentamente il corpo con le mani.",
        },
        "su_bersaglio": {
            "attore": "Regali a {bersaglio} un lungo e sensuale massaggio su tutto il corpo.",
            "osservatori": "{attore} regala a {bersaglio} un lungo e sensuale massaggio.",
            "bersaglio": "{attore} ti regala un lungo e sensuale massaggio, facendo scorrere le mani su tutto il tuo corpo.",
        },
    },
    "spank": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti dai una sculacciata per essere stato/a birichino/a!",
            "osservatori": "{attore} si da' una sculacciata per essere stato/a birichino/a!",
        },
        "su_bersaglio": {
            "attore": "Sculacci {bersaglio} in modo giocoso!",
            "osservatori": "{attore} sculaccia {bersaglio} in modo giocoso!",
            "bersaglio": "{attore} ti sculaccia in modo giocoso! OUCH!",
        },
    },
    "strip": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Inizi un lento e sensuale spogliarello per tutti...",
            "osservatori": "{attore} inizia un lento e sensuale spogliarello per tutti...",
        },
        "su_se_stesso": {
            "attore": "Inizi un lento e sensuale spogliarello per tutti...",
            "osservatori": "{attore} inizia un lento e sensuale spogliarello per tutti...",
        },
        "su_bersaglio": {
            "attore": "Fai scorrere le mani sul corpo di {bersaglio}, spogliandola/o lentamente...",
            "osservatori": "{attore} inizia a spogliare lentamente {bersaglio}...",
            "bersaglio": "{attore} fa scorrere le mani sul tuo corpo, spogliandoti lentamente...",
        },
    },
    "stroke": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Farai piangere gli angeli!",
            "osservatori": "{attore} fa qualcosa che farebbe piangere gli angeli.",
        },
        "su_bersaglio": {
            "attore": "Accarezzi dolcemente l'interno coscia di {bersaglio}.",
            "osservatori": "{attore} accarezza dolcemente l'interno coscia di {bersaglio}.",
            "bersaglio": "{attore} ti accarezza dolcemente l'interno coscia.",
        },
    },
    "tease": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Ti sfiori il corpo con una grande piuma rosa.",
            "osservatori": "{attore} si sfiora il corpo con una grande piuma rosa.",
        },
        "su_bersaglio": {
            "attore": "Sogghigni con malizia e sfiori {bersaglio} con una grande piuma rosa.",
            "osservatori": "{attore} sogghigna con malizia e sfiora {bersaglio} con una grande piuma rosa.",
            "bersaglio": "{attore} sogghigna con malizia e ti sfiora il corpo con una grande piuma rosa.",
        },
    },
    "tongue": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "richiede_bersaglio": True,
        "su_se_stesso": {
            "attore": "Avvolgi la lingua intorno... a te stesso/a?!",
            "osservatori": "{attore} avvolge la lingua intorno... a se stesso/a?!",
        },
        "su_bersaglio": {
            "attore": "Avvolgi la lingua intorno a {bersaglio} e la fai scivolare su tutto il suo corpo...",
            "osservatori": "{attore} fa scivolare la lingua sul corpo di {bersaglio}...",
            "bersaglio": "{attore} avvolge la lingua intorno a te e la fa scivolare su tutto il tuo corpo...",
        },
    },
    "undress": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Inizi a toglierti i vestiti. Brrrr, che freddo!",
            "osservatori": "{attore} sogghigna maliziosamente e inizia a togliersi i vestiti.",
        },
        "su_se_stesso": {
            "attore": "E' piu' divertente spogliare qualcun altro.",
            "osservatori": "{attore} valuta di spogliarsi da solo/a, poi ci ripensa: e' piu' divertente farlo a qualcun altro.",
        },
        "su_bersaglio": {
            "attore": "Guardi {bersaglio} e la/lo spogli lentamente con gli occhi... mmmmm...",
            "osservatori": "{attore} guarda {bersaglio} e la/lo spoglia lentamente con gli occhi.",
            "bersaglio": "Ti senti leggermente esposto/a mentre {attore} ti fissa con desiderio, spogliandoti lentamente con gli occhi...",
        },
    },
    "wiggle": {
        "categoria": "sessuale",
        "vietato_newbie": True,
        "senza_bersaglio": {
            "attore": "Dimeni il fondoschiena in modo giocoso.",
            "osservatori": "{attore} dimena il fondoschiena in modo giocoso.",
        },
        "su_bersaglio": {
            "attore": "Dimeni il fondoschiena in modo giocoso verso {bersaglio}!",
            "osservatori": "{attore} dimena il fondoschiena in modo giocoso verso {bersaglio}!",
            "bersaglio": "{attore} dimena il fondoschiena in modo giocoso verso di te!",
        },
    },
}


def pronomi(personaggio):
    """(riflessivo, "se stesso"/"se stessa")."""
    genere = getattr(personaggio.db, "genere", "m") or "m"
    return "se stessa" if genere == "f" else "se stesso"


def esegui_social(attore, social_id, bersaglio=None):
    """Esegue un social: manda i messaggi giusti ad attore/osservatori/
    bersaglio. Ritorna (ok: bool, messaggio_errore: str|None)."""
    dati = SOCIALS.get(social_id)
    if not dati:
        return False, "Social sconosciuto."

    rif = pronomi(attore)
    stanza = attore.location

    nome_comando = social_id.upper()

    if bersaglio is None:
        if dati.get("richiede_bersaglio"):
            return False, f"Chi vuoi bersagliare con {nome_comando}?"
        sezione = dati.get("senza_bersaglio")
        if not sezione:
            return False, f"{nome_comando} richiede un bersaglio."
        attore.msg(sezione["attore"].format(attore=attore.key, rif=rif))
        if stanza:
            stanza.msg_contents(
                sezione["osservatori"].format(attore=attore.key, rif=rif), exclude=attore
            )
        return True, None

    if bersaglio == attore:
        sezione = dati.get("su_se_stesso")
        if not sezione:
            return False, f"Non puoi usare {nome_comando} su te stesso/a."
        attore.msg(sezione["attore"].format(attore=attore.key, rif=rif))
        if stanza:
            stanza.msg_contents(
                sezione["osservatori"].format(attore=attore.key, rif=rif), exclude=attore
            )
        return True, None

    sezione = dati.get("su_bersaglio")
    if not sezione:
        return False, f"Non puoi usare {nome_comando} su qualcun altro."
    attore.msg(sezione["attore"].format(attore=attore.key, bersaglio=bersaglio.key, rif=rif))
    bersaglio.msg(sezione["bersaglio"].format(attore=attore.key, bersaglio=bersaglio.key, rif=rif))
    if stanza:
        stanza.msg_contents(
            sezione["osservatori"].format(attore=attore.key, bersaglio=bersaglio.key, rif=rif),
            exclude=[attore, bersaglio],
        )
    return True, None
