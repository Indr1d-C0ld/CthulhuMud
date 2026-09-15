"""
Le quattro aree dei punti di partenza non umani (audit pre-beta).

Perche' esiste questo modulo. Le stanze di RECALL/RESPAWN/MORGUE create
da world/rooms_newbie.py nascevano senza alcuna uscita, e la creazione
del personaggio vi colloca il giocatore: chi sceglieva una professione
legata a Profondi, Mi-Go, Yuggoth o Yithiani nasceva in una stanza da
cui era letteralmente impossibile muoversi. L'hub umano della Miskatonic
e' stato agganciato alla Arkham gia' costruita (vedi
world/rooms_newbie.py:collega_hub_al_mondo); questi quattro invece non
avevano alcuna area a cui agganciarsi, e vengono costruiti qui.

NOTA DI METODO, come per Arkham, Ulthar e il sottomarino: il sito
originale non pubblica alcuna mappa di queste zone. Le stanze sono
percio' una scelta di design di questo porting, costruita sui testi di
Lovecraft invece che su materiale della fonte:

- Y'ha-nthlei e' la citta' ciclopica sommersa al largo della Barriera
  del Diavolo, davanti a Innsmouth, dove regnano Padre Dagon e Madre
  Hydra ("La maschera di Innsmouth").
- I Mi-Go sono i funghi di Yuggoth che trasportano cervelli umani dentro
  cilindri metallici, e operano in luoghi appartati ("Colui che
  sussurrava nelle tenebre"): da qui l'attracco sopra un cimitero.
- Yuggoth e' il loro mondo d'origine ai margini del sistema solare, di
  terrazze nere, fiumi di pece e torri senza finestre (Fungi from
  Yuggoth).
- La Grande Razza di Yith custodisce negli archivi della propria citta'
  la storia di ogni epoca, e sotto alcune botole sigillate tiene chiuso
  cio' che non ha mai saputo sconfiggere ("L'ombra venuta dal tempo").

Gli agganci al resto del mondo sono anch'essi scelte dichiarate: la
Barriera del Diavolo emerge nel mare aperto gia' costruito fra Arkham e
il Cairo; la nave madre staziona sopra il cimitero della Citta' Vecchia
di Arkham; Yuggoth si raggiunge dalla nave, come vuole la sua stessa
natura di vascello interplanetario; la biblioteca Yithiana, che nel
tempo profondo non sarebbe raggiungibile a piedi, si apre invece sulle
Dreamlands - l'unico luogo del gioco in cui la distanza e' mentale
prima che fisica.
"""

from evennia.utils import create, search

TAG_CATEGORY = "hub_alieno_room"

# ---------------------------------------------------------------------
# Definizione delle quattro aree
#
# Ogni area dichiara:
#   "stanze":  chiave_tag -> (nome, descrizione)
#   "collegamenti": (chiave_a, chiave_b, nome_uscita_a_b, nome_uscita_b_a)
#       dove una chiave puo' essere anche "hub:<ruolo>" per riferirsi
#       alla stanza di recall/respawn/morgue gia' creata in rooms_newbie
#   "ancora": (nome della stanza del mondo, chiave locale,
#              nome uscita verso il mondo, nome uscita di ritorno)
# ---------------------------------------------------------------------

AREE = {
    # -----------------------------------------------------------------
    "yhanthlei": {
        "stanze": {
            "terrazze": (
                "Le Terrazze Ciclopiche di Y'ha-nthlei",
                "Gradoni di basalto troppo vasti per mani umane scendono nel buio "
                "verde dell'oceano, incrostati di conchiglie e di un oro che non "
                "annerisce mai. Sagome pallide sciamano fra le colonne, e nessuna "
                "di esse ha piu' bisogno di risalire a respirare.",
            ),
            "tempio_dagon": (
                "Il Tempio di Padre Dagon",
                "Una sala sommersa dove l'acqua stessa sembra piu' densa. "
                "Sull'altare, offerte di pesce e di cose che pesce non sono. "
                "Qualcosa di enorme si muove appena, oltre il limite della luce, "
                "e preferiresti credere che sia una corrente.",
            ),
            "tempio_hydra": (
                "Il Tempio di Madre Hydra",
                "Gemello del tempio di Dagon, ma tappezzato di uova opalescenti "
                "disposte in file ordinate come in un archivio. Chi nasce qui "
                "somiglia a un uomo per i primi anni, poi sempre meno.",
            ),
            "giardini": (
                "I Giardini di Corallo Nero",
                "Rami di corallo scuro come ferro battuto formano un labirinto "
                "lento, dove i Profondi coltivano molluschi grandi quanto un "
                "uomo. Fra i rami si intravedono ossa, alcune con ancora "
                "addosso brandelli di lana cerata.",
            ),
            "barriera": (
                "La Barriera del Diavolo",
                "La cresta rocciosa che affiora appena sotto la superficie, al "
                "largo di Innsmouth. Da qui l'acqua sale verso la luce e il "
                "rumore delle onde; verso il basso, invece, si apre il pozzo "
                "scuro che porta alla citta'. I pescatori del continente sanno "
                "di non gettare le reti da queste parti.",
            ),
            "mercato": (
                "Il Mercato delle Conchiglie",
                "Banchi di pietra levigata dove i Profondi barattano cio' che "
                "l'oceano concede e cio' che le navi perdono. L'oro di Innsmouth "
                "e' ammucchiato con la noncuranza che si riserva alla sabbia: "
                "qui vale come ornamento, non come ricchezza.",
            ),
            "consiglio": (
                "La Sala del Consiglio dei Vecchi",
                "Seggi di basalto disposti in cerchio, quasi tutti occupati da "
                "figure cosi' antiche e cosi' immobili che le incrostazioni le "
                "hanno saldate al proprio posto. Nessuno di loro dorme: "
                "semplicemente, non hanno piu' nulla da dirsi in fretta.",
            ),
            "pozzo": (
                "Il Pozzo Cieco",
                "Un varco circolare nella roccia, oltre il quale la "
                "bioluminescenza della citta' non arriva. I Profondi vi hanno "
                "inciso attorno un segno che, in qualunque lingua lo si legga, "
                "vuol dire la stessa cosa: piu' in la' non si torna a nuoto. "
                "Chi attraversa ha gia' deciso.",
            ),
            "rovine": (
                "Le Rovine Pre-Umane",
                "Cio' che resta di una citta' che era antica quando Y'ha-nthlei "
                "fu fondata sopra di essa. Gli angoli delle mura non tornano, "
                "come se la geometria di chi le innalzo' non fosse la stessa "
                "che regge quest'acqua. Qualcosa qui sotto e' rimasto.",
            ),
            "abisso": (
                "L'Orlo dell'Abisso",
                "Oltre l'ultima terrazza il fondale finisce di colpo e comincia "
                "una fossa senza fondo conosciuto. Dal basso sale un tepore che "
                "l'acqua profonda non dovrebbe avere, e un suono lentissimo, "
                "regolare, che somiglia troppo a un respiro.",
            ),
        },
        "collegamenti": [
            ("hub:recall", "terrazze", "terrazze", "nido"),
            ("terrazze", "tempio_dagon", "tempio di dagon", "terrazze"),
            ("terrazze", "tempio_hydra", "tempio di hydra", "terrazze"),
            ("terrazze", "giardini", "giardini", "terrazze"),
            ("terrazze", "barriera", "su", "giu"),
            ("terrazze", "mercato", "mercato", "terrazze"),
            ("terrazze", "consiglio", "consiglio", "terrazze"),
            ("giardini", "pozzo", "pozzo cieco", "indietro"),
            ("pozzo", "abisso", "abisso", "pozzo"),
            ("pozzo", "rovine", "rovine", "pozzo"),
            ("hub:respawn", "terrazze", "fuori", "infermeria"),
            ("hub:morgue", "terrazze", "fuori", "obitorio"),
        ],
        "ancora": ("In Mare Aperto", "barriera", "emergi", "immergiti"),
    },
    # -----------------------------------------------------------------
    "migo_mothership": {
        "stanze": {
            "volta_cilindri": (
                "La Volta dei Cilindri",
                "Scaffalature metalliche salgono oltre la portata dello sguardo, "
                "ciascuna piena di cilindri lucidi grandi quanto un secchio. A "
                "ognuno sono avvitati tre strumenti: uno per udire, uno per "
                "parlare, uno per vedere. Quasi tutti sono spenti. Quasi.",
            ),
            "sala_chirurgica": (
                "Sala Chirurgica Mi-Go",
                "Un tavolo inclinato, scanalature per il drenaggio, e strumenti "
                "posati in ordine perfetto - tutti pensati per chele, non per "
                "dita. L'operazione, assicurano i ronzii, non e' fatale: il "
                "corpo e' semplicemente la parte che non viene portata via.",
            ),
            "blister": (
                "Blister di Osservazione",
                "Una bolla trasparente sporgente dallo scafo. Sotto, la campagna "
                "del Massachusetts di notte; sopra, stelle che da qui non "
                "formano piu' le costellazioni che credevi di conoscere. Una di "
                "esse, molto fioca e molto lontana, e' casa per chi pilota.",
            ),
            "deposito": (
                "Il Deposito dei Congegni",
                "File di contenitori aperti, ciascuno con dentro strumenti che "
                "non hanno un nome umano. Un Mi-Go tiene il registro di cio' che "
                "entra e di cio' che esce, e talvolta scambia volentieri: la "
                "Terra produce materiali che su Yuggoth non crescono.",
            ),
            "camera_ali": (
                "La Camera delle Ali",
                "Qui i Mi-Go riparano le proprie membrane dopo i passaggi "
                "nell'etere. L'aria sa di ozono e di qualcosa di organico che "
                "brucia piano. Sulle rastrelliere, ali di ricambio - e non tutte "
                "appartenevano a chi le indossera'.",
            ),
            "condotto": (
                "Il Condotto Inferiore",
                "Un passaggio stretto che scende verso la stiva. Il ronzio "
                "cambia tono qui: diventa piu' basso, quasi un avvertimento. "
                "Sulla paratia, simboli incisi che l'equipaggio evita di "
                "guardare mentre passa.",
            ),
            "stiva": (
                "La Stiva dei Campioni",
                "Gabbie e vasche allineate, alcune vuote, alcune no. I campioni "
                "provengono da mondi diversi e sono tenuti vivi perche' morti "
                "non servirebbero. Qualcuno di loro, dietro il vetro, ti guarda "
                "con un'espressione che riconosci troppo bene.",
            ),
            "baia": (
                "Baia di Attracco",
                "Il portellone inferiore della nave madre, aperto sul vuoto. Le "
                "ali membranose non servono qui dentro: ci si lascia semplicemente "
                "cadere verso il basso, o si entra nel condotto che porta altrove "
                "nel sistema solare.",
            ),
        },
        "collegamenti": [
            ("hub:recall", "volta_cilindri", "volta", "corridoio"),
            ("volta_cilindri", "sala_chirurgica", "sala chirurgica", "volta"),
            ("volta_cilindri", "blister", "blister", "volta"),
            ("hub:recall", "baia", "baia", "corridoio"),
            ("volta_cilindri", "deposito", "deposito", "volta"),
            ("volta_cilindri", "camera_ali", "camera delle ali", "volta"),
            ("baia", "condotto", "condotto inferiore", "baia"),
            ("condotto", "stiva", "stiva", "condotto"),
            ("hub:morgue", "volta_cilindri", "fuori", "riciclaggio"),
        ],
        "ancora": ("Il Cimitero della Citta' Vecchia", "baia", "discendi", "risali"),
    },
    # -----------------------------------------------------------------
    "yuggoth_training": {
        "stanze": {
            "terrazze_nere": (
                "Le Terrazze Nere di Yuggoth",
                "Gradinate di pietra scura si rincorrono fino all'orizzonte "
                "vicinissimo di un mondo piccolo e freddo. Il sole e' una stella "
                "fra le altre, appena piu' luminosa. Nulla qui e' stato "
                "costruito per essere guardato da occhi.",
            ),
            "fiume_pece": (
                "Il Fiume di Pece",
                "Un corso nero e lentissimo attraversa le terrazze, cosi' freddo "
                "che scorrere sembra una sua concessione. Sulla superficie "
                "galleggiano forme che si disfano e si ricompongono, e non e' "
                "chiaro se siano vive o soltanto molto pazienti.",
            ),
            "giardini_fungini": (
                "I Giardini Fungini",
                "Distese di funghi alti come alberi, coltivati in file "
                "geometriche. Alcuni emettono una luce debole e pulsante; altri "
                "si voltano piano al tuo passaggio, benche' non abbiano nulla "
                "con cui voltarsi.",
            ),
            "mercato_fungino": (
                "Il Mercato Fungino",
                "Sotto una volta di miceli intrecciati, i Mi-Go scambiano "
                "colture, utensili e sostanze. Nessuno contratta a voce: il "
                "prezzo viene ronzato, e chi non sa ronzare paga quello che gli "
                "viene detto.",
            ),
            "miniere": (
                "Le Miniere di Tok'l",
                "Gallerie scavate nella pietra nera per estrarre il metallo con "
                "cui i Mi-Go costruiscono i loro cilindri. Il minerale non "
                "riflette la luce: la assorbe, e restituisce al suo posto un "
                "leggero tepore che sulle dita resta per ore.",
            ),
            "cava": (
                "La Cava Esterna",
                "L'imboccatura a cielo aperto delle miniere, dove il vento "
                "sottile di Yuggoth solleva polvere nera. Le squadre di "
                "estrazione si fermano sempre qui prima di scendere, e chi "
                "risale conta i compagni prima di togliersi la maschera.",
            ),
            "fondo": (
                "Il Fondo della Miniera",
                "L'ultimo livello, dove lo scavo si e' fermato di colpo e non e' "
                "mai ripreso. La parete di fondo non e' pietra: e' liscia, "
                "curva, e cede appena sotto la mano, come se dall'altra parte "
                "qualcosa respirasse contro di essa.",
            ),
            "torre": (
                "La Torre Senza Finestre",
                "Un cilindro di pietra nera che sale per centinaia di metri, "
                "senza un'apertura, senza una giuntura. Chi la abita non ha "
                "bisogno di vedere fuori: sa gia' cosa c'e', avendolo in gran "
                "parte messo li'.",
            ),
        },
        "collegamenti": [
            ("hub:recall", "terrazze_nere", "fuori", "struttura"),
            ("terrazze_nere", "fiume_pece", "fiume", "terrazze"),
            ("terrazze_nere", "giardini_fungini", "giardini", "terrazze"),
            ("terrazze_nere", "torre", "torre", "terrazze"),
            ("terrazze_nere", "mercato_fungino", "mercato", "terrazze"),
            ("terrazze_nere", "cava", "cava", "terrazze"),
            ("cava", "miniere", "miniere", "cava"),
            ("miniere", "fondo", "fondo", "miniere"),
            ("hub:morgue", "terrazze_nere", "fuori", "camera medica"),
        ],
        # Yuggoth si raggiunge dalla nave madre: e' il vascello a fare la
        # spola, come nei testi.
        "ancora_interna": ("migo_mothership", "baia", "terrazze_nere", "condotto", "nave madre"),
    },
    # -----------------------------------------------------------------
    "yithian_library": {
        "stanze": {
            "navata": (
                "La Grande Biblioteca - Navata Centrale",
                "Corridoi di basalto larghi come strade, fiancheggiati da casse "
                "metalliche alte tre volte un uomo. Ogni cassa contiene il "
                "resoconto di un'epoca, scritto da qualcuno che quell'epoca "
                "l'ha visitata di persona, occupando corpi presi in prestito.",
            ),
            "archivi": (
                "Gli Archivi delle Ere",
                "Qui sono raccolti i volumi delle ere che non sono ancora "
                "avvenute. Alcuni dorsi portano date che riconosceresti; uno di "
                "essi, se lo cercassi, porterebbe la tua. La Grande Razza "
                "considera scortese impedirtelo, e altrettanto scortese "
                "avvertirti.",
            ),
            "torre_basalto": (
                "La Torre di Basalto",
                "Dall'alto della torre si vede la citta' estendersi fino al "
                "deserto: cupole, rampe curve al posto delle scale, e non una "
                "sola linea retta dove un essere umano ne metterebbe una. Il "
                "cielo ha un colore che non ricorderai bene, dopo.",
            ),
            "curatori": (
                "Il Banco dei Curatori",
                "Un lungo piano di metallo dove la Grande Razza fornisce a chi "
                "consulta gli strumenti necessari: lastre vergini, stili, "
                "lenti. Nulla viene regalato - ogni cosa e' annotata, e "
                "l'annotazione durera' piu' di te.",
            ),
            "macchine": (
                "La Sala delle Macchine Ronzanti",
                "Congegni alti come case, di funzione ignota, che ronzano a un "
                "ritmo lentissimo e regolare. Un Yithiano vi si accosta ogni "
                "tanto per correggere qualcosa di impercettibile. Si dice che "
                "misurino quanto manca.",
            ),
            "discesa": (
                "Il Corridoio Discendente",
                "Una rampa curva che scende sotto il livello degli archivi. Le "
                "lastre alle pareti, qui, non raccontano ere: sono avvisi. La "
                "Grande Razza non usa avvisi per le cose che sa di poter "
                "gestire.",
            ),
            "livelli_inferiori": (
                "I Livelli Inferiori",
                "Corridoi che la citta' ha murato e riaperto piu' volte, sempre "
                "dall'alto. L'aria si muove senza che ci sia una corrente, e in "
                "alcuni punti la polvere sul pavimento e' stata spostata da "
                "qualcosa di largo che non ha lasciato impronte.",
            ),
            "botola": (
                "La Botola Sigillata",
                "Una lastra circolare di pietra chiusa da sigilli piu' antichi "
                "della citta' stessa, in un corridoio che nessuno percorre "
                "volentieri. La Grande Razza ha vinto ogni guerra tranne una, e "
                "quella che non ha vinto e' stata soltanto rinchiusa. Di tanto "
                "in tanto, da sotto, arriva un soffio d'aria.",
            ),
        },
        "collegamenti": [
            ("hub:recall", "navata", "biblioteca", "giardino"),
            ("navata", "archivi", "archivi", "navata"),
            ("navata", "torre_basalto", "torre", "navata"),
            ("navata", "curatori", "curatori", "navata"),
            ("navata", "macchine", "macchine", "navata"),
            ("navata", "discesa", "corridoio discendente", "navata"),
            ("discesa", "botola", "botola", "discesa"),
            ("discesa", "livelli_inferiori", "livelli inferiori", "discesa"),
            ("hub:morgue", "navata", "fuori", "infermeria"),
        ],
        "ancora": ("Il Crocevia delle Dreamlands", "torre_basalto", "varco", "biblioteca yithiana"),
    },
}


# ---------------------------------------------------------------------
# Costruzione (idempotente)
# ---------------------------------------------------------------------

def _get_or_create_room(hub_id, chiave, nome, descrizione):
    tag_key = f"{hub_id}_{chiave}"
    esistenti = search.search_tag(tag_key, category=TAG_CATEGORY)
    if esistenti:
        return esistenti[0]
    room = create.create_object("typeclasses.rooms.Room", key=nome)
    room.db.desc = descrizione
    room.tags.add(tag_key, category=TAG_CATEGORY)
    return room


def _get_or_create_exit(origine, destinazione, nome):
    """Non duplica un'uscita gia' esistente verso la stessa destinazione.
    Evita anche i nomi omonimi nella stessa stanza, che renderebbero
    ambiguo il comando di movimento."""
    for e in origine.exits:
        if e.destination and e.destination.id == destinazione.id:
            return e, False
    if any(e.key == nome for e in origine.exits):
        nome = f"{nome} 2"
    uscita = create.create_object(
        "typeclasses.exits.Exit", key=nome,
        location=origine, destination=destinazione,
    )
    return uscita, True


def _risolvi(hub_id, chiave, stanze_create):
    """Risolve una chiave di collegamento in una stanza vera."""
    if chiave.startswith("hub:"):
        from world.rooms_newbie import stanza_per_ruolo
        return stanza_per_ruolo(hub_id, chiave.split(":", 1)[1])
    return stanze_create.get(chiave)


def costruisci_hub_alieni():
    """Costruisce le quattro aree e le collega agli hub e al mondo.

    Idempotente: si puo' rilanciare senza duplicare nulla. Ritorna un
    riepilogo (stanze create, uscite create) per i log di popolamento."""
    from evennia.objects.models import ObjectDB

    stanze_tot, uscite_tot = 0, 0
    per_area = {}

    for hub_id, area in AREE.items():
        create_qui = {}
        for chiave, (nome, desc) in area["stanze"].items():
            prima = search.search_tag(f"{hub_id}_{chiave}", category=TAG_CATEGORY)
            room = _get_or_create_room(hub_id, chiave, nome, desc)
            create_qui[chiave] = room
            if not prima:
                stanze_tot += 1
        per_area[hub_id] = create_qui

        for a, b, nome_ab, nome_ba in area["collegamenti"]:
            ra = _risolvi(hub_id, a, create_qui)
            rb = _risolvi(hub_id, b, create_qui)
            if not ra or not rb:
                continue
            _, nuova1 = _get_or_create_exit(ra, rb, nome_ab)
            _, nuova2 = _get_or_create_exit(rb, ra, nome_ba)
            uscite_tot += int(nuova1) + int(nuova2)

    # agganci al mondo gia' costruito
    for hub_id, area in AREE.items():
        if "ancora" in area:
            nome_mondo, chiave_locale, verso_mondo, ritorno = area["ancora"]
            ancora = ObjectDB.objects.filter(
                db_key=nome_mondo, db_typeclass_path="typeclasses.rooms.Room"
            ).first()
            locale = per_area[hub_id].get(chiave_locale)
            if ancora and locale:
                _, n1 = _get_or_create_exit(locale, ancora, verso_mondo)
                _, n2 = _get_or_create_exit(ancora, locale, ritorno)
                uscite_tot += int(n1) + int(n2)
        if "ancora_interna" in area:
            altro_hub, chiave_altro, chiave_locale, verso, ritorno = area["ancora_interna"]
            a = per_area.get(altro_hub, {}).get(chiave_altro)
            b = per_area[hub_id].get(chiave_locale)
            if a and b:
                _, n1 = _get_or_create_exit(a, b, verso)
                _, n2 = _get_or_create_exit(b, a, ritorno)
                uscite_tot += int(n1) + int(n2)

    return {"stanze_create": stanze_tot, "uscite_create": uscite_tot}
