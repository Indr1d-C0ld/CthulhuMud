"""
Popolamento delle quattro aree di partenza non umane.

Struttura voluta, uguale per tutte e quattro: un NUCLEO SICURO attorno
alla stanza di nascita - abitanti, sacerdoti, bottegai - e una
PROFONDITA' PERICOLOSA raggiungibile solo oltre una stanza-soglia, la
cui descrizione avverte esplicitamente (il Pozzo Cieco, il Condotto
Inferiore, la Cava Esterna, il Corridoio Discendente).

Questo risolve la tensione fra due esigenze entrambe legittime: le
creature ostili devono comportarsi da ostili - e qui conservano
l'aggressivita' che il bestiario assegna loro - ma non devono trovarsi
dove un personaggio appena creato mette i piedi senza averlo scelto. La
separazione e' SPAZIALE, non una deroga al loro comportamento: chi
oltrepassa la soglia ha letto l'avvertimento e ha deciso.

Gli abitanti non ostili hanno ora delle frasi_ambiente. Prima ogni NPC
di scenografia del gioco era fermo e muto: il tick che recita le battute
atmosferiche serviva le sole creature del bestiario ed e' stato esteso
a loro (vedi world/mostri_movimento.py).

Fonti dei contenuti - come per il resto di queste aree il sito originale
non pubblica nulla, e ci si appoggia ai testi: l'oro di Innsmouth che i
Profondi trattano come sabbia e il consiglio dei vecchi ("La maschera di
Innsmouth"); i cilindri metallici, le ali da riparare dopo i passaggi
nell'etere e lo scambio di materiali terrestri ("Colui che sussurrava
nelle tenebre"); il metallo tok'l estratto su Yuggoth e le colture
fungine (Fungi from Yuggoth e Miti espansi); le lastre metalliche, gli
stili e le macchine della Grande Razza, piu' cio' che e' stato murato ai
livelli inferiori e che la citta' non ha mai sconfitto ("L'ombra venuta
dal tempo").

NOTA: la stanza di RECALL di ogni hub ha gia' il proprio terapeuta
(world/popola_terapeuti.py) e non viene toccata qui.
"""

from evennia.utils import create, search

TAG_CATEGORY_STANZE = "hub_alieno_room"
TAG_NPC = "hub_alieno_npc"

# (chiave_stanza, nome, descrizione, [frasi ambientali])
NPC_AMBIENTAZIONE = [
    # ---------------- Y'ha-nthlei ----------------
    ("yhanthlei_terrazze", "un Profondo dalle scaglie annerite",
     "Uno dei piu' anziani abitanti della citta': le scaglie hanno perso il "
     "verde e sono diventate quasi nere, segno - dicono qui - di chi ha "
     "smesso di contare gli anni perche' non finiranno.",
     ["Il Profondo dalle scaglie annerite resta immobile cosi' a lungo che un pesce gli si posa sul braccio.",
      "Il Profondo dalle scaglie annerite dice qualcosa in una lingua fatta di gorgoglii, senza rivolgerla a nessuno.",
      "Il Profondo dalle scaglie annerite conta lentamente le colonne, come se una potesse mancare."]),
    ("yhanthlei_tempio_dagon", "un sacerdote di Padre Dagon",
     "Ha le braccia segnate da incisioni rituali e non si volta quando entri: "
     "continua a disporre offerte sull'altare, con la calma di chi sa che il "
     "suo dio non ha alcuna fretta.",
     ["Il sacerdote depone un'altra offerta sull'altare e attende, come se aspettasse risposta.",
      "Il sacerdote intona un canto basso che l'acqua trasporta piu' lontano di quanto dovrebbe.",
      "Qualcosa di enorme si sposta oltre il limite della luce, e il sacerdote sorride."]),
    ("yhanthlei_tempio_hydra", "una custode delle uova",
     "Sorveglia le file di uova opalescenti spostandole di tanto in tanto di "
     "qualche centimetro, secondo un criterio che non spiega. Quando ti "
     "guarda, conta anche te.",
     ["La custode sposta un uovo di pochi centimetri, ci ripensa, e lo rimette dov'era.",
      "Un uovo opalescente si contrae piano. La custode lo accarezza senza guardarlo.",
      "La custode ti osserva a lungo, poi torna alle uova: qualunque cosa cercasse, non l'ha trovata."]),
    ("yhanthlei_barriera", "un Profondo di vedetta",
     "Immobile appena sotto il pelo dell'acqua, osserva le luci delle "
     "imbarcazioni che passano al largo. Non le teme: le annota.",
     ["La vedetta segue con lo sguardo una luce lontana finche' non sparisce.",
      "La vedetta incide un segno sulla roccia: un'altra barca, un'altra notte.",
      "Dalla superficie arriva il rumore di un motore. La vedetta non si muove."]),
    ("yhanthlei_consiglio", "il piu' vecchio dei Vecchi",
     "Una figura cosi' antica che le incrostazioni l'hanno saldata al proprio "
     "seggio. Le branchie si muovono appena. Ricorda Innsmouth quando aveva "
     "ancora un porto, e ricorda cosa c'era prima di Innsmouth.",
     ["Il piu' vecchio dei Vecchi pronuncia un nome che nessuno usa da duecento anni.",
      "Le branchie del piu' vecchio dei Vecchi si muovono appena: sta ancora decidendo qualcosa.",
      "Il piu' vecchio dei Vecchi dice: \"Il mare e' paziente. Noi siamo il mare.\""]),

    # ---------------- Nave madre Mi-Go ----------------
    ("migo_mothership_volta_cilindri", "un Mi-Go archivista",
     "Una forma fungina irta di appendici che scorre gli scaffali toccando un "
     "cilindro dopo l'altro. A ogni contatto una voce metallica comincia a "
     "parlare, e viene zittita quasi subito.",
     ["L'archivista tocca un cilindro. Una voce metallica dice \"...vi prego, da quanto...\" prima di essere zittita.",
      "L'archivista sposta un cilindro dallo scaffale alto a quello basso, e annota il cambiamento.",
      "Un cilindro in fondo alla volta emette un ticchettio ostinato. L'archivista lo ignora."]),
    ("migo_mothership_sala_chirurgica", "un assistente operatorio Mi-Go",
     "Dispone gli strumenti in un ordine che cambia ogni volta e che non "
     "sbaglia mai. Le sue chele si muovono con una delicatezza che rende la "
     "scena molto peggiore.",
     ["L'assistente dispone gli strumenti in un ordine nuovo, e sembra soddisfatto.",
      "L'assistente pulisce il tavolo inclinato con una cura eccessiva.",
      "L'assistente ti misura con lo sguardo, come si misura un vestito."]),
    ("migo_mothership_blister", "un navigatore Mi-Go",
     "Sta affacciato alla bolla trasparente, immobile, con le ali membranose "
     "ripiegate. Fissa un punto preciso del cielo: se segui il suo sguardo non "
     "trovi nulla, ma lui continua a guardarlo.",
     ["Il navigatore corregge impercettibilmente la rotta con un ronzio.",
      "Il navigatore indica una stella che da qui non dovrebbe essere visibile.",
      "Sotto di voi le luci di una citta' umana scorrono lente, e il navigatore non le degna."]),
    ("migo_mothership_camera_ali", "un Mi-Go dalle ali lacerate",
     "Tiene ripiegata una membrana squarciata e con l'altra si sostiene. Il "
     "passaggio nell'etere costa, e non a tutti allo stesso modo. Sulla "
     "rastrelliera dietro di lui ci sono ali che non aspettano lui.",
     ["Il Mi-Go dalle ali lacerate prova a distenderle. Non ci riesce, e ripiega.",
      "L'odore di ozono e di organico bruciato si fa piu' intenso.",
      "Il Mi-Go dalle ali lacerate guarda la rastrelliera, poi guarda te."]),

    # ---------------- Yuggoth ----------------
    ("yuggoth_training_terrazze_nere", "un sorvegliante Mi-Go",
     "Percorre le terrazze con volo basso e regolare, come una ronda. Si ferma "
     "quando ti vede, il tempo necessario a decidere che non sei ancora un "
     "problema.",
     ["Il sorvegliante compie un altro giro di ronda, sempre alla stessa quota.",
      "Il sorvegliante si ferma a mezz'aria, ti osserva, e prosegue.",
      "Un ronzio di risposta arriva da una terrazza piu' in basso."]),
    ("yuggoth_training_giardini_fungini", "un coltivatore Mi-Go",
     "Lavora fra i funghi alti come alberi, potandoli con gesti brevi. Alcune "
     "delle forme che raccoglie si contraggono; lui non se ne cura, o forse e' "
     "proprio quello il criterio.",
     ["Il coltivatore recide un fungo. Il moncone si richiude da solo in pochi istanti.",
      "Una delle forme raccolte si contrae nel cesto. Il coltivatore non guarda.",
      "Il coltivatore misura l'altezza di un fungo contro il proprio corpo, e annuisce."]),
    ("yuggoth_training_torre", "una voce dalla torre",
     "Non c'e' nessuno da vedere: la voce arriva dalla pietra stessa, in una "
     "lingua fatta di ronzii, e si interrompe quando ti fermi ad ascoltare. "
     "Riprende appena riprendi a camminare.",
     ["La voce nella pietra riprende, poi tace di colpo.",
      "Per un istante la voce pronuncia qualcosa che somiglia a una parola umana.",
      "Il ronzio dentro la torre cambia ritmo, come se avesse cambiato argomento."]),

    # ---------------- Biblioteca Yithiana ----------------
    ("yithian_library_navata", "un Yithiano in consultazione",
     "Un enorme cono rugoso alto quattro metri, sormontato da quattro appendici "
     "flessibili. Due di esse reggono un volume, una scrive, la quarta e' "
     "puntata verso di te per tutto il tempo.",
     ["Lo Yithiano volta una lastra metallica con un suono di campana sorda.",
      "La quarta appendice dello Yithiano resta puntata su di te anche mentre legge.",
      "Lo Yithiano confronta due volumi, poi ne ripone uno con evidente fastidio."]),
    ("yithian_library_archivi", "uno scriba della Grande Razza",
     "Trascrive senza sosta su lastre metalliche. Se ti avvicini abbastanza "
     "noti che la mano corre molto piu' veloce di quanto qualunque cosa possa "
     "essere letta: non sta copiando, sta ricordando.",
     ["Lo scriba incide una data. La riconosci, e preferiresti non averla letta.",
      "Lo scriba termina una lastra, la depone, e ne comincia un'altra senza pause.",
      "Per un istante lo scriba si ferma, come se il ricordo si fosse interrotto."]),
    ("yithian_library_torre_basalto", "un osservatore delle ere",
     "Sta affacciato oltre il parapetto curvo, rivolto al deserto. Non guarda "
     "il paesaggio: guarda, si direbbe, *quando* sara' il paesaggio a cambiare.",
     ["L'osservatore indica un punto del deserto dove non c'e' nulla. Non ancora.",
      "L'osservatore misura l'ombra della torre e la confronta con una lastra.",
      "L'osservatore dice, senza voltarsi: \"Anche tu sarai stato qui.\""]),
    ("yithian_library_macchine", "un manutentore delle macchine",
     "Si accosta ogni tanto a un congegno alto come una casa e vi corregge "
     "qualcosa di impercettibile. Alla domanda su cosa misurino risponderebbe "
     "- se rispondesse - che misurano quanto manca.",
     ["Il manutentore corregge qualcosa di impercettibile. Il ronzio cala di un tono.",
      "Una delle macchine accelera per qualche istante. Il manutentore si irrigidisce.",
      "Il manutentore controlla tre congegni di fila, e solo il terzo lo soddisfa."]),
]

# (chiave_stanza, nome, descrizione, inventario, [frasi])
MERCANTI = [
    ("yhanthlei_mercato", "una Profonda dai monili d'oro",
     "Tiene banco fra cumuli d'oro di Innsmouth trattato come sabbia, e "
     "soppesa cio' che le porti con l'aria di chi ha gia' visto tutto due volte.",
     [
        {"chiave": "diadema", "nome": "un diadema d'oro di Innsmouth", "prezzo": 45,
         "descrizione": "Oro che non annerisce, lavorato in motivi che l'occhio segue male."},
        {"chiave": "arpione", "nome": "un arpione da profondita'", "prezzo": 30,
         "descrizione": "Asta d'osso con punta ricavata da un dente che non e' di squalo."},
        {"chiave": "conchiglia", "nome": "una conchiglia che trattiene l'aria", "prezzo": 18,
         "descrizione": "Portata alla bocca restituisce una boccata d'aria salmastra. Una sola."},
        {"chiave": "alga", "nome": "un fascio di alghe nutrienti", "prezzo": 5,
         "descrizione": "Alghe carnose, sapore di ferro. Sostengono a lungo.", "cibo": 25},
        {"chiave": "perla", "nome": "una perla nera scaramantica", "prezzo": 22,
         "descrizione": "I Profondi la portano addosso quando scendono oltre il Pozzo Cieco."},
     ],
     ["La Profonda soppesa un monile e lo rimette sul mucchio.",
      "La Profonda dice: \"L'oro qui non compra nulla. Serve a ricordare chi eravamo.\"",
      "La Profonda separa le conchiglie intere da quelle incrinate, senza guardarle."]),

    ("migo_mothership_deposito", "un Mi-Go registratore",
     "Tiene il conto di cio' che entra e di cio' che esce dalla nave. Scambia "
     "volentieri: la Terra produce materiali che su Yuggoth non crescono.",
     [
        {"chiave": "cilindro", "nome": "un cilindro vuoto", "prezzo": 60,
         "descrizione": "Metallo lucido, tre attacchi filettati. Vuoto, per ora."},
        {"chiave": "lente", "nome": "una lente per vedere altrove", "prezzo": 40,
         "descrizione": "Guardandovi attraverso la stanza e' la stessa, ma con qualcosa in piu'."},
        {"chiave": "bisturi", "nome": "un bisturi Mi-Go", "prezzo": 28,
         "descrizione": "Pensato per chele. In una mano umana e' scomodo, ma taglia lo stesso."},
        {"chiave": "resina", "nome": "una fiala di resina rigenerante", "prezzo": 25,
         "descrizione": "Riempie gli squarci delle membrane. Sulla pelle umana brucia, ma chiude."},
        {"chiave": "polvere", "nome": "una dose di polvere di tok'l", "prezzo": 15,
         "descrizione": "Polvere nera che assorbe la luce e restituisce un tepore ostinato."},
     ],
     ["Il registratore annota un'entrata su una lastra sottile.",
      "Il registratore ronza una cifra. Se non sai ronzare, quella e' la cifra.",
      "Il registratore soppesa un cilindro vuoto e lo rimette a posto con cura."]),

    ("yuggoth_training_mercato_fungino", "un Mi-Go coltivatore anziano",
     "Sotto la volta di miceli intrecciati scambia colture e sostanze. Non "
     "contratta a voce: il prezzo viene ronzato, e chi non sa ronzare paga "
     "quello che gli viene detto.",
     [
        {"chiave": "fungo", "nome": "un fungo luminoso di Yuggoth", "prezzo": 8,
         "descrizione": "Emette una luce fredda e pulsante. Si volta piano verso chi lo tiene.",
         "cibo": 20},
        {"chiave": "spora", "nome": "una capsula di spore soporifere", "prezzo": 14,
         "descrizione": "Schiacciata rilascia una nube che rallenta anche cio' che non respira."},
        {"chiave": "micelio", "nome": "una matassa di micelio filante", "prezzo": 10,
         "descrizione": "Fibra resistente, usata dai Mi-Go per legature e suture."},
        {"chiave": "pece", "nome": "un'ampolla di pece nera", "prezzo": 12,
         "descrizione": "Fredda al punto da sembrare ferma. Attaccata alla pelle non si stacca."},
        {"chiave": "maschera", "nome": "una maschera da estrazione", "prezzo": 35,
         "descrizione": "Filtra la polvere nera delle miniere. Chi scende senza, risale peggio."},
     ],
     ["Il coltivatore anziano ronza una cifra e attende.",
      "Il coltivatore anziano recide un fungo maturo e lo aggiunge al banco.",
      "Una capsula di spore si apre da sola sul banco. Il coltivatore la copre con una ciotola."]),

    ("yithian_library_curatori", "un curatore della Grande Razza",
     "Fornisce a chi consulta gli strumenti necessari. Nulla viene regalato: "
     "ogni cosa e' annotata, e l'annotazione durera' piu' di te.",
     [
        {"chiave": "lastra", "nome": "una lastra metallica vergine", "prezzo": 20,
         "descrizione": "Metallo chiaro e sottile. Non si corrode, non si piega, non si perde."},
        {"chiave": "stilo", "nome": "uno stilo da incisione", "prezzo": 16,
         "descrizione": "Punta durissima, impugnatura pensata per quattro appendici."},
        {"chiave": "lente", "nome": "una lente dei curatori", "prezzo": 30,
         "descrizione": "Ingrandisce le incisioni piu' fini. A volte mostra righe che non avevi visto."},
        {"chiave": "indice", "nome": "un indice delle ere", "prezzo": 26,
         "descrizione": "Elenca cosa e' archiviato e dove. Le ultime voci sono lasciate in bianco."},
        {"chiave": "sigillo", "nome": "un sigillo di cera antica", "prezzo": 18,
         "descrizione": "La Grande Razza lo usa per chiudere cio' che preferisce non riaprire."},
     ],
     ["Il curatore annota la tua presenza su una lastra. L'annotazione restera'.",
      "Il curatore allinea gli stili per lunghezza, per la terza volta.",
      "Il curatore dice: \"Prendi pure. E' gia' scritto che l'avrai preso.\""]),
]

# (chiave_stanza, chiave_bestiario, quanti, zona)
#
# SOLO stanze oltre la soglia. Qui gli ostili conservano l'aggressivita'
# che il bestiario assegna loro: si comportano da cio' che sono. A
# proteggere il nuovo giocatore e' la distanza, piu' l'avvertimento
# esplicito nella descrizione della stanza-soglia - non una deroga al
# comportamento delle creature.
#
#   Y'ha-nthlei  soglia: Il Pozzo Cieco          -> abisso, rovine
#   Nave madre   soglia: Il Condotto Inferiore   -> stiva
#   Yuggoth      soglia: La Cava Esterna         -> miniere, fondo
#   Biblioteca   soglia: Il Corridoio Discendente-> botola, livelli inferiori
MOSTRI = [
    ("yhanthlei_abisso", "shoggoth_minore", 1, "yhanthlei"),
    ("yhanthlei_rovine", "ibrido_profondo", 2, "yhanthlei"),
    ("migo_mothership_stiva", "byakhee", 1, "migo_mothership"),
    ("yuggoth_training_miniere", "ibrido_profondo", 1, "yuggoth_training"),
    ("yuggoth_training_fondo", "shoggoth_minore", 1, "yuggoth_training"),
    ("yithian_library_botola", "cane_di_tindalos", 1, "yithian_library"),
    ("yithian_library_livelli_inferiori", "gug", 1, "yithian_library"),
]


def _stanza(chiave):
    trovate = search.search_tag(chiave, category=TAG_CATEGORY_STANZE)
    return trovate[0] if trovate else None


def _npc_esistente(stanza, chiave):
    """L'NPC gia' installato in questa stanza per questa voce, se c'e'."""
    for o in stanza.contents:
        if o.tags.get(chiave, category=TAG_NPC):
            return o
    return None


def popola_hub_alieni():
    """Popola le quattro aree. Idempotente: non duplica nulla."""
    from world.mostri import crea_mostro
    from world.economia import crea_mercante

    npc_creati = mercanti_creati = mostri_creati = 0
    aggiornati_ref = [0]          # battute/descrizioni rinfrescate

    for chiave, nome, descrizione, frasi in NPC_AMBIENTAZIONE:
        stanza = _stanza(chiave)
        if not stanza:
            continue
        gia = _npc_esistente(stanza, chiave)
        if gia:
            # Non si ricrea, ma si AGGIORNA: cosi' arricchire questo file
            # (nuove battute, descrizione ritoccata) ha effetto anche sugli
            # abitanti gia' presenti nel mondo, invece di riguardare solo
            # le installazioni future.
            if gia.db.desc != descrizione:
                gia.db.desc = descrizione
            if list(gia.db.frasi_ambiente or []) != list(frasi):
                gia.db.frasi_ambiente = list(frasi)
                aggiornati_ref[0] += 1
            continue
        npc = create.create_object("typeclasses.npcs.NPC", key=nome, location=stanza)
        npc.db.desc = descrizione
        npc.db.livello = 1
        npc.db.hp = npc.db.hp_max = 20
        npc.db.ostile = False
        npc.db.attacca_a_vista = False
        npc.db.sentinella = True       # scenografia: non deve allontanarsi
        npc.db.frasi_ambiente = list(frasi)
        npc.tags.add(chiave, category=TAG_NPC)
        npc_creati += 1

    for chiave, nome, descrizione, inventario, frasi in MERCANTI:
        stanza = _stanza(chiave)
        if not stanza:
            continue
        gia = _npc_esistente(stanza, chiave)
        if gia:
            if list(gia.db.frasi_ambiente or []) != list(frasi):
                gia.db.frasi_ambiente = list(frasi)
                aggiornati_ref[0] += 1
            if gia.db.negozio != inventario:
                gia.db.negozio = inventario
            continue
        mercante = crea_mercante(stanza, nome, descrizione, inventario)
        mercante.db.frasi_ambiente = list(frasi)
        mercante.db.sentinella = True
        mercante.tags.add(chiave, category=TAG_NPC)
        mercanti_creati += 1

    for chiave, chiave_bestiario, quanti, zona in MOSTRI:
        stanza = _stanza(chiave)
        if not stanza:
            continue
        presenti = sum(
            1 for o in stanza.contents
            if o.attributes.has("bestiario_chiave")
            and o.db.bestiario_chiave == chiave_bestiario
        )
        for _ in range(max(0, quanti - presenti)):
            m = crea_mostro(chiave_bestiario, stanza, zona=zona)
            # Sentinella per necessita', non per estetica: tutte e quattro
            # le aree condividono la stessa categoria di tag, quindi un
            # mostro lasciato libero di vagare potrebbe attraversare la
            # soglia AL CONTRARIO ed entrare nel nucleo sicuro, vanificando
            # l'intera separazione. Qui restano dove sono stati posti.
            m.db.sentinella = True
            mostri_creati += 1

    return {"npc_creati": npc_creati, "mercanti_creati": mercanti_creati,
            "mostri_creati": mostri_creati, "aggiornati": aggiornati_ref[0]}


def ripopola_hub_alieni():
    """Aggancio al ciclo di repop (world/repop.py).

    Non si usa la TABELLA_RESET generica perche' quella richiama
    crea_mostro() direttamente, e le istanze ricreate perderebbero i due
    accorgimenti che tengono in piedi il progetto di queste aree: la
    sentinella (senza cui un mostro risalirebbe nel nucleo sicuro) e la
    collocazione oltre la soglia. popola_hub_alieni() e' gia' idempotente
    e ricrea solo cio' che manca, quindi svolge esattamente il compito di
    un reset di zona, con le regole giuste.

    Ritorna il numero di creature ricomparse."""
    return popola_hub_alieni()["mostri_creati"]
