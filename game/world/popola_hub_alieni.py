"""
Popolamento delle quattro aree di partenza non umane (audit pre-beta).

Le 18 stanze create da world/rooms_hub_alieni.py erano scenografia
deserta: descrizioni evocative e nessun abitante. Qui prendono vita,
con lo stesso schema gia' usato per Zoog Village e il sommergibile
(world/popola_npc_ambientazione_zoog.py): un NPC nominato dove la
descrizione della stanza ne evoca gia' uno, piu' qualche creatura
ostile dove l'ambientazione la richiede.

Le creature ostili sono prese dal bestiario esistente (world/mostri.py)
invece di inventarne di nuove, e scelte per coerenza con i testi:
- gli ibridi dei Profondi popolano i giardini di Y'ha-nthlei, dove la
  citta' coltiva il proprio cibo;
- gli Shoggoth furono creati dagli Antichi e poi impiegati dai Profondi:
  uno di essi sorveglia l'orlo dell'abisso, e un altro striscia lungo il
  fiume di pece di Yuggoth;
- i Byakhee attraversano lo spazio interstellare e stazionano quindi
  nella baia di attracco della nave madre;
- i Cani di Tindalos entrano dagli angoli del tempo: nessuna creatura si
  addice di piu' al corridoio della botola sigillata, nella citta' di una
  razza che nel tempo viaggia abitualmente.

NOTA: la stanza di RECALL di ogni hub ha gia' il proprio terapeuta
(world/popola_terapeuti.py) e non viene toccata qui, per non
sovrappopolarla.
"""

from evennia.utils import create, search

TAG_CATEGORY_STANZE = "hub_alieno_room"
TAG_NPC = "hub_alieno_npc"

# (chiave_stanza, nome, descrizione)
NPC_AMBIENTAZIONE = [
    # --- Y'ha-nthlei ---
    ("yhanthlei_terrazze", "un Profondo dalle scaglie annerite",
     "Uno dei piu' anziani abitanti della citta': le scaglie hanno perso "
     "il verde e sono diventate quasi nere, segno - dicono qui - di chi "
     "ha smesso di contare gli anni perche' non finiranno."),
    ("yhanthlei_tempio_dagon", "un sacerdote di Padre Dagon",
     "Ha le braccia segnate da incisioni rituali e non si volta quando "
     "entri: continua a disporre offerte sull'altare, con la calma di "
     "chi sa che il suo dio non ha alcuna fretta."),
    ("yhanthlei_tempio_hydra", "una custode delle uova",
     "Sorveglia le file di uova opalescenti spostandole di tanto in tanto "
     "di qualche centimetro, secondo un criterio che non spiega. Quando "
     "ti guarda, conta anche te."),
    ("yhanthlei_barriera", "un Profondo di vedetta",
     "Immobile appena sotto il pelo dell'acqua, osserva le luci delle "
     "imbarcazioni che passano al largo. Non le teme: le annota."),

    # --- Nave madre Mi-Go ---
    ("migo_mothership_volta_cilindri", "un Mi-Go archivista",
     "Una forma fungina irta di appendici che scorre gli scaffali "
     "toccando un cilindro dopo l'altro. A ogni contatto una voce "
     "metallica comincia a parlare, e viene zittita quasi subito."),
    ("migo_mothership_sala_chirurgica", "un assistente operatorio Mi-Go",
     "Dispone gli strumenti in un ordine che cambia ogni volta e che "
     "non sbaglia mai. Le sue chele si muovono con una delicatezza che "
     "rende la scena molto peggiore."),
    ("migo_mothership_blister", "un navigatore Mi-Go",
     "Sta affacciato alla bolla trasparente, immobile, con le ali "
     "membranose ripiegate. Fissa un punto preciso del cielo: se segui "
     "il suo sguardo non trovi nulla, ma lui continua a guardarlo."),

    # --- Yuggoth ---
    ("yuggoth_training_terrazze_nere", "un sorvegliante Mi-Go",
     "Percorre le terrazze con volo basso e regolare, come una ronda. "
     "Si ferma quando ti vede, il tempo necessario a decidere che non "
     "sei ancora un problema."),
    ("yuggoth_training_giardini_fungini", "un coltivatore Mi-Go",
     "Lavora fra i funghi alti come alberi, potandoli con gesti brevi. "
     "Alcune delle forme che raccoglie si contraggono; lui non se ne "
     "cura, o forse e' proprio quello il criterio."),
    ("yuggoth_training_torre", "una voce dalla torre",
     "Non c'e' nessuno da vedere: la voce arriva dalla pietra stessa, "
     "in una lingua fatta di ronzii, e si interrompe quando ti fermi "
     "ad ascoltare. Riprende appena riprendi a camminare."),

    # --- Biblioteca Yithiana ---
    ("yithian_library_navata", "un Yithiano in consultazione",
     "Un enorme cono rugoso alto quattro metri, sormontato da quattro "
     "appendici flessibili. Due di esse reggono un volume, una scrive, "
     "la quarta e' puntata verso di te per tutto il tempo."),
    ("yithian_library_archivi", "uno scriba della Grande Razza",
     "Trascrive senza sosta su lastre metalliche. Se ti avvicini "
     "abbastanza noti che la mano corre molto piu' veloce di quanto "
     "qualunque cosa possa essere letta: non sta copiando, sta "
     "ricordando."),
    ("yithian_library_torre_basalto", "un osservatore delle ere",
     "Sta affacciato oltre il parapetto curvo, rivolto al deserto. Non "
     "guarda il paesaggio: guarda, si direbbe, *quando* sara' il "
     "paesaggio a cambiare."),
]

# (chiave_stanza, chiave_bestiario, quanti)
#
# ATTENZIONE - queste sono AREE DI PARTENZA: qui nasce un personaggio di
# livello 0 con 20 punti ferita. Le creature scelte hanno livelli fra 10 e
# 25 e diverse di esse, nel bestiario, aggrediscono a vista; poiche' un
# mostro attacca chiunque non gli sia molto superiore di livello (vedi
# world/mostri.py, MARGINE_AGGRESSIONE), un nuovo giocatore che si
# affacciasse nella stanza sbagliata verrebbe ucciso all'istante, e in un
# caso - la baia di attracco - la stanza e' perfino adiacente a quella di
# nascita.
#
# Le istanze create qui hanno percio' attacca_a_vista disattivato: restano
# presenti, descritte e pericolosissime se provocate (db.ostile resta
# vero, quindi contrattaccano), ma non tendono un agguato a chi sta
# ancora imparando a muoversi. L'orrore di vedere uno Shoggoth sull'orlo
# dell'abisso resta intatto; a decidere se avvicinarsi e' il giocatore.
MOSTRI = [
    ("yhanthlei_giardini", "ibrido_profondo", 2),
    ("yhanthlei_abisso", "shoggoth_minore", 1),
    ("migo_mothership_baia", "byakhee", 1),
    ("yuggoth_training_fiume_pece", "shoggoth_minore", 1),
    ("yithian_library_botola", "cane_di_tindalos", 1),
]


def _stanza(chiave):
    trovate = search.search_tag(chiave, category=TAG_CATEGORY_STANZE)
    return trovate[0] if trovate else None


def popola_hub_alieni():
    """Popola le quattro aree. Idempotente: non duplica nulla.

    Gli NPC di ambientazione sono riconosciuti dal tag TAG_NPC; i mostri
    dalla loro chiave di bestiario gia' presente nella stanza (sono
    comunque soggetti al repop, vedi world/repop.py, quindi qui si
    controlla solo che non ne esistano gia' troppi)."""
    from world.mostri import crea_mostro

    npc_creati, mostri_creati = 0, 0

    for chiave, nome, descrizione in NPC_AMBIENTAZIONE:
        stanza = _stanza(chiave)
        if not stanza:
            continue
        gia_presente = any(
            o.tags.get(chiave, category=TAG_NPC) for o in stanza.contents
        )
        if gia_presente:
            continue
        npc = create.create_object("typeclasses.npcs.NPC", key=nome, location=stanza)
        npc.db.desc = descrizione
        npc.db.livello = 1
        npc.db.hp = npc.db.hp_max = 20
        npc.db.ostile = False
        npc.db.attacca_a_vista = False
        npc.db.sentinella = True          # scenografia: non deve vagare via
        npc.tags.add(chiave, category=TAG_NPC)
        npc_creati += 1

    for chiave, chiave_bestiario, quanti in MOSTRI:
        stanza = _stanza(chiave)
        if not stanza:
            continue
        presenti = sum(
            1 for o in stanza.contents
            if o.attributes.has("bestiario_chiave")
            and o.db.bestiario_chiave == chiave_bestiario
        )
        for _ in range(max(0, quanti - presenti)):
            m = crea_mostro(chiave_bestiario, stanza, zona=chiave.split("_")[0])
            # vedi la nota sopra MOSTRI: niente agguati nelle aree di partenza
            m.db.attacca_a_vista = False
            mostri_creati += 1

    return {"npc_creati": npc_creati, "mostri_creati": mostri_creati}


# ---------------------------------------------------------------------
# LIMITE NOTO: queste aree non sono nel ciclo di repop
#
# world/repop.py ripopola solo le zone elencate nella propria tabella di
# reset, e queste quattro non vi compaiono: le creature uccise qui non
# ricompaiono da sole, e l'area si "svuota" dopo la prima ripulita.
#
# E' una scelta consapevole, non una dimenticanza. Aggiungerle al repop
# richiederebbe anche insegnargli a NON rendere aggressive le istanze che
# ricrea: il repop chiama crea_mostro() direttamente, e i mostri
# rigenerati tornerebbero ad attaccare a vista, annullando la protezione
# descritta sopra e rimettendo un aggressore di livello 25 accanto alla
# stanza di nascita. Se un domani si vorra' il ripopolamento anche qui,
# va affrontato prima quel punto.
