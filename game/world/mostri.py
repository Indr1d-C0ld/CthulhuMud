"""
Bestiario di NPC ostili (Fase H, prima tornata): finora tutte le zone
costruite (Arkham, Cairo, Zoog Village, Ulthar, Dreamlands, sommergibile)
erano scenograficamente vive (negozianti, NPC di ambientazione) ma senza
un solo nemico - "un mondo navigabile ma inerte", come notato nel primo
elenco di lacune di questo progetto.

Confermato dalla scansione esaustiva del sito originale
(research/REPORT.md): il database di help e' tutto materiale rivolto al
giocatore (skill/incantesimi/comandi/social) - NESSUN bestiario o
scheda mostri e' mai stato pubblicato (normale: un sito non svela le
statistiche dei propri nemici). Le uniche creature del Mythos citate
nell'intero corpus sono di striscio, dentro descrizioni di incantesimi
(es. CURSE OF THE HUNTER evoca una "Hunting Horror", helps/breath_magic
parla di soffi elementali, ecc.) - non abbastanza per ricostruire un
bestiario vero.

Per esplicita richiesta dell'utente, qui il bestiario e' costruito di
sana pianta nello spirito dell'ambientazione lovecraftiana, radicato
nelle creature canoniche del Mythos (Ghoul, Profondi, Cani di Tindalos,
Byakhee, Shoggoth, Gug, Bestie Lunari, Cacciatori Notturni...) e
calibrato sulle meccaniche gia' costruite in questa sessione (livello,
skill di combattimento, allineamento per world/esperienza.py, orrore
per world/sanita.py). Ogni voce e' quindi una scelta di design
originale, non una trascrizione da fonte - il contrario delle tornate
precedenti, ed e' dichiarato esplicitamente qui invece che spacciato
per materiale originale.

db.attacca_a_vista (vedi typeclasses/rooms.py) distingue i predatori
che aggrediscono chi entra nella stanza dai mostri piu' passivi che
reagiscono solo se attaccati (db.ostile gestisce gia' il contrattacco).

Fase H, terza tornata - IA di movimento/pattugliamento e "mob
programs": vedi world/mostri_movimento.py per la logica di
vagabondaggio/battute ambientali. I campi aggiunti qui sotto
traducono in dati i flag della fonte (immhelp_flags.txt):
- "sentinella": equivalente al flag SENTINEL - il mostro non vaga mai
  (riservato ai guardiani di un luogo preciso).
- "wimpy_soglia": equivalente al flag WIMPY - percentuale di HP sotto
  la quale il mostro tenta di fuggire (0 = non fugge mai, riutilizza
  il meccanismo gia' esistente per i personaggi giocanti, vedi
  typeclasses/living.py/world/combat.py:_controlla_wimpy).
- "insegue_chi_fugge": equivalente ai flag HUNTER/TRACKER - il mostro
  insegue nella stanza di destinazione un bersaglio che gli fugge da
  sotto (vedi world/combat.py:tenta_fuga).
- "frasi_ambiente": battute atmosferiche recitate a caso quando il
  mostro non si sposta - l'equivalente in spirito del comando MPECHO
  della fonte (immhelp_mobcommands.txt), qui semplice testo invece di
  un vero motore di scripting generico (scelta di design condivisa
  con l'utente: niente VM MOBprogram-like, comportamenti scritti
  direttamente in Python dato che non esistono altri builder che
  scriverebbero script).

MARGINE_AGGRESSIONE traduce la semantica del flag AGGRESSIVE della
fonte ("The mob will attack everyone who's not very superior in
level"): un mostro con attacca_a_vista non aggredisce piu' un
personaggio il cui livello effettivo superi il proprio di oltre
questo margine. Il valore numerico non e' specificato dalla fonte -
scelta di design esplicita.

"sensibile_luna" (Fase K, pre-release): il sistema di fase lunare
(world/sottorazze.py:luna_piena(), gia' confermato dalla fonte per
immhelp_conditions.txt) era finora cablato solo sulle sottorazze Were
giocanti. Trovato in audit come gap reale: la fonte tratta "moon" come
una condizione di mondo generica, utilizzabile da qualunque mob, e il
nostro stesso bestiario include gia' creature esplicitamente legate
alla luna ("bestia lunare", al servizio dei "mercanti lunari"). Un
mostro con sensibile_luna=True riceve un bonus al danno durante la
luna piena (BONUS_DANNO_LUNA_PIENA sotto) - valore e meccanismo non
specificati dalla fonte, scelta di design esplicita che rispecchia lo
stesso tema gia' usato per i buff temporanei Were.
"""

from world.colori import pericolo

MARGINE_AGGRESSIONE = 5
BONUS_DANNO_LUNA_PIENA = 4

BESTIARIO = {
    "ghoul": {
        "nome": "un ghoul",
        "descrizione": (
            "Una creatura canina e umanoide insieme, la pelle grigiastra tesa "
            "sulle ossa, le unghie annerite e spezzate dallo scavare tra le "
            "tombe. Ringhia sommessamente, mostrando denti troppo numerosi "
            "per una bocca umana."
        ),
        "livello": 8, "hp_max": 79, "allineamento": -400, "orrore": 8, "tipo_orrore": "non_morti",
        "attacca_a_vista": True, "non_morto": True,
        "skills": {"hand_to_hand": 45, "dodge": 25, "strangle": 20, "crush": 15},
        "frasi_ambiente": [
            "Il ghoul scava con le unghie annerite tra la terra smossa.",
            "Un ringhio sommesso sale dalla gola del ghoul.",
        ],
    },
    "cultista": {
        "nome": "un cultista incappucciato",
        "descrizione": (
            "Una figura avvolta in una tonaca scura, il volto nascosto da un "
            "cappuccio. Stringe tra le mani un pugnale ricurvo inciso con "
            "simboli che feriscono la vista a fissarli troppo a lungo."
        ),
        "livello": 5, "hp_max": 55, "allineamento": -600, "orrore": 4, "tipo_orrore": "occulto",
        "attacca_a_vista": False,
        "skills": {"hand_to_hand": 30, "dodge": 20, "dagger": 35},
        "frasi_ambiente": [
            "Il cultista mormora un cantico in una lingua che ferisce l'orecchio.",
            "Il cultista traccia simboli nell'aria con un dito tremante.",
        ],
    },
    "ibrido_profondo": {
        "nome": "un ibrido dei Profondi",
        "descrizione": (
            "Un uomo dagli occhi sporgenti e privi di palpebre, la pelle "
            "squamosa e umida attorno al collo, dove qualcosa che assomiglia "
            "a delle branchie si apre e si chiude a ogni respiro affannoso."
        ),
        "livello": 10, "hp_max": 95, "allineamento": -300, "orrore": 6, "tipo_orrore": "profondi",
        "attacca_a_vista": False,
        "skills": {"hand_to_hand": 50, "dodge": 20, "crush": 30, "strong_grip": 25},
        "wimpy_soglia": 25,
        "frasi_ambiente": [
            "L'ibrido dei Profondi annusa l'aria umida, in cerca dell'odore del mare.",
            "Un suono gutturale, quasi un canto, sfugge alle sue branchie.",
        ],
    },
    "mummia_custode": {
        "nome": "una mummia custode",
        "descrizione": (
            "Bende ingiallite dai millenni avvolgono un corpo che non "
            "dovrebbe piu' potersi muovere, eppure cammina, lento e "
            "inesorabile, gli occhi due pozzi di ambra scura nel volto avvolto."
        ),
        "livello": 12, "hp_max": 111, "allineamento": -200, "orrore": 9, "tipo_orrore": "non_morti",
        "attacca_a_vista": True, "non_morto": True,
        "skills": {"hand_to_hand": 55, "crush": 35, "dodge": 10, "enhanced_damage": 20},
        "sentinella": True,
        "frasi_ambiente": [
            "La mummia custode volge lo sguardo verso l'ingresso, immobile.",
            "Un fruscio di bende accompagna ogni suo minimo movimento.",
        ],
    },
    "sciacallo_mutato": {
        "nome": "uno sciacallo mutato",
        "descrizione": (
            "Uno sciacallo dal pelo rado e a chiazze, con un secondo paio di "
            "occhi vestigiali che si aprono appena sopra i primi. Si muove a "
            "scatti innaturali, come se il proprio corpo gli fosse estraneo."
        ),
        "livello": 6, "hp_max": 63, "allineamento": -100, "orrore": 3, "tipo_orrore": "sconosciuto",
        "attacca_a_vista": True,
        "skills": {"hand_to_hand": 35, "dodge": 30, "second_attack": 15},
        "wimpy_soglia": 25,
        "frasi_ambiente": [
            "Lo sciacallo mutato fiuta il terreno con il suo secondo paio di occhi.",
            "Uno scatto innaturale attraversa il corpo dello sciacallo.",
        ],
    },
    "cane_di_tindalos": {
        "nome": "un cane di Tindalos",
        "descrizione": (
            "Una forma sottile e angolosa emerge dall'angolo piu' vicino della "
            "stanza, come se lo spigolo stesso si fosse aperto per lasciarla "
            "passare. Non ha una forma fissa: solo linee spezzate e una fame "
            "che viene da fuori del tempo."
        ),
        "livello": 20, "hp_max": 175, "allineamento": -800, "orrore": 18, "tipo_orrore": "esterni",
        "attacca_a_vista": True,
        "skills": {"hand_to_hand": 70, "dodge": 50, "backstab": 40, "enhanced_damage": 40},
        "insegue_chi_fugge": True,
        "frasi_ambiente": [
            "Il cane di Tindalos scivola da un angolo all'altro della stanza.",
            "Uno stridio che viene da fuori del tempo increspa l'aria.",
        ],
    },
    "byakhee": {
        "nome": "un byakhee",
        "descrizione": (
            "Un'enorme forma alata, in parte uccello e in parte insetto e in "
            "parte qualcos'altro che la mente rifiuta di catalogare, plana "
            "silenziosa sopra la testa prima di ripiegare le ali e planare "
            "all'attacco."
        ),
        "livello": 15, "hp_max": 135, "allineamento": -500, "orrore": 12, "tipo_orrore": "esterni",
        "attacca_a_vista": True,
        "skills": {"hand_to_hand": 60, "dodge": 45, "circle": 30, "second_attack": 20},
        "frasi_ambiente": [
            "Il byakhee piega le ali enormi, scrutando l'orizzonte.",
            "Un frullio secco e innaturale accompagna ogni suo movimento.",
        ],
    },
    "shoggoth_minore": {
        "nome": "un piccolo shoggoth",
        "descrizione": (
            "Una massa nera e lucida, grande quanto un carro, che scorre "
            "sul pavimento formando e riassorbendo occhi e bocche a caso "
            "sulla propria superficie. \"Tekeli-li\", sembra mormorare, "
            "in una parodia delle voci che ha divorato."
        ),
        "livello": 25, "hp_max": 223, "allineamento": -700, "orrore": 20, "tipo_orrore": "antichi",
        "attacca_a_vista": True,
        "skills": {"hand_to_hand": 75, "crush": 60, "strangle": 40, "enhanced_damage": 45},
        "sentinella": True,
        "frasi_ambiente": [
            "\"Tekeli-li\", mormora la massa nera, riassorbendo un'altra bocca casuale.",
            "Il piccolo shoggoth scorre lentamente sul pavimento, lasciando una scia lucida.",
        ],
    },
    "gug": {
        "nome": "un gug",
        "descrizione": (
            "Un gigante peloso alto quanto due uomini, con una bocca verticale "
            "che si apre dall'attaccatura dei capelli al mento, orlata di "
            "zanne. Le braccia enormi terminano in artigli capaci di aprire "
            "in due un corpo umano con un solo colpo."
        ),
        "livello": 18, "hp_max": 159, "allineamento": -450, "orrore": 14, "tipo_orrore": "onirici",
        "attacca_a_vista": True,
        "skills": {"hand_to_hand": 65, "crush": 50, "bash": 35, "enhanced_damage": 30},
        "frasi_ambiente": [
            "Il gug apre la sua bocca verticale in un ringhio silenzioso.",
            "Le enormi braccia del gug raschiano contro le pareti di pietra.",
        ],
    },
    "bestia_lunare": {
        "nome": "una bestia lunare",
        "descrizione": (
            "Una forma grigiastra e informe, vagamente a forma di rospo, che "
            "grugnisce con una voce che ricorda troppo da vicino il riso di "
            "un uomo. Serve i mercanti lunari in luoghi che nessun essere "
            "sano vorrebbe visitare."
        ),
        "livello": 16, "hp_max": 143, "allineamento": -550, "orrore": 13, "tipo_orrore": "onirici",
        "attacca_a_vista": False,
        "sensibile_luna": True,
        "skills": {"hand_to_hand": 58, "dodge": 20, "crush": 40, "strong_grip": 30},
        "frasi_ambiente": [
            "La bestia lunare grugnisce con un suono che ricorda una risata umana.",
            "Un tremito percorre la sua forma grigiastra e informe.",
        ],
    },
    "cacciatore_notturno": {
        "nome": "un cacciatore notturno",
        "descrizione": (
            "Una figura alata nera e senza volto, la pelle liscia e lucida "
            "come corno levigato. Non emette suono alcuno, nemmeno quando "
            "afferra la sua preda tra le braccia e si solleva in volo."
        ),
        "livello": 14, "hp_max": 127, "allineamento": -350, "orrore": 15, "tipo_orrore": "onirici",
        "attacca_a_vista": True,
        "skills": {"hand_to_hand": 55, "dodge": 40, "strong_grip": 35, "circle": 25},
        "insegue_chi_fugge": True,
        "frasi_ambiente": [
            "Il cacciatore notturno dispiega le ali nere senza il minimo rumore.",
            "Una presenza silenziosa aleggia nell'aria, in attesa.",
        ],
    },
    "marinaio_annegato": {
        "nome": "un marinaio annegato",
        "descrizione": (
            "Un cadavere gonfio d'acqua, l'uniforme marcia incollata alla "
            "pelle livida. Si muove a scatti, come se ancora obbedisse a "
            "ordini impartiti da un ufficiale morto da tempo."
        ),
        "livello": 7, "hp_max": 71, "allineamento": -250, "orrore": 7, "tipo_orrore": "non_morti",
        "attacca_a_vista": True,
        "skills": {"hand_to_hand": 38, "crush": 25, "dodge": 10},
        "frasi_ambiente": [
            "Il marinaio annegato ripete un ordine incomprensibile, con voce gorgogliante.",
            "Acqua scura gocciola dall'uniforme marcia del marinaio annegato.",
        ],
    },
}


def crea_mostro(chiave_bestiario, location, zona=None):
    """Crea un'istanza del mostro chiave_bestiario in location. Non
    idempotente per design (i mostri, a differenza di negozianti/NPC di
    ambientazione, sono pensati per essere uccisi e ricomparire tramite
    il repop, vedi world/repop.py): chiamare una sola volta per
    popolamento iniziale o dal sistema di reset. zona (es. "arkham",
    vedi world/popola_mostri.py) e' usata da world/mostri_movimento.py
    per vincolare il vagabondare del mostro alla propria area
    (equivalente al flag STAY-AREA della fonte)."""
    from evennia.utils import create

    dati = BESTIARIO.get(chiave_bestiario)
    if not dati:
        raise KeyError(f"Mostro sconosciuto: {chiave_bestiario}")

    mostro = create.create_object("typeclasses.npcs.NPC", key=dati["nome"], location=location)
    mostro.db.desc = dati["descrizione"]
    mostro.db.livello = dati["livello"]
    mostro.db.hp_max = dati["hp_max"]
    mostro.db.hp = dati["hp_max"]
    mostro.db.alignment = dati["allineamento"]
    mostro.db.orrore = dati["orrore"]
    mostro.db.tipo_orrore = dati.get("tipo_orrore", "sconosciuto")
    mostro.db.ostile = True
    mostro.db.attacca_a_vista = dati.get("attacca_a_vista", False)
    mostro.db.skills = dict(dati["skills"])
    mostro.db.bestiario_chiave = chiave_bestiario
    mostro.db.zona = zona
    mostro.db.sentinella = dati.get("sentinella", False)
    mostro.db.wimpy_soglia = dati.get("wimpy_soglia", 0)
    mostro.db.insegue_chi_fugge = dati.get("insegue_chi_fugge", False)
    mostro.db.frasi_ambiente = list(dati.get("frasi_ambiente", []))
    mostro.db.non_morto = dati.get("non_morto", False)
    mostro.db.sensibile_luna = dati.get("sensibile_luna", False)
    return mostro


def tenta_aggro(npc, personaggio):
    """Se npc e' ostile "a vista" (o guardia protetta) e le condizioni
    di aggro sono soddisfatte contro personaggio, avvia il combattimento
    e ritorna True. Fattorizzata qui (Fase K, pre-release) per essere
    riusata sia quando e' il PERSONAGGIO a entrare nella stanza
    (typeclasses/rooms.py:at_object_receive) sia quando e' il MOSTRO a
    vagare in una stanza gia' occupata (world/mostri_movimento.py) -
    bug reale trovato in audit: prima di questa modifica un mostro
    aggressivo che vagava dentro una stanza con giocatori fermi non li
    attaccava mai, perche' move_to() non passa da at_object_receive lato
    NPC. Stessa semantica gia' dichiarata in rooms.py, solo centralizzata."""
    if not getattr(npc, "vivo", False) or npc.db.combat_target:
        return False
    from world.esperienza import livello_effettivo

    if (
        npc.db.attacca_a_vista
        and livello_effettivo(personaggio) <= (npc.db.livello or 1) + MARGINE_AGGRESSIONE
    ):
        npc.location.msg_contents(pericolo(f"{npc.key} si avventa su {personaggio.key}!"), exclude=[])
        npc.avvia_combattimento(personaggio)
        return True
    if personaggio.db.criminale and npc.db.protetto:
        npc.location.msg_contents(
            pericolo(f"{npc.key} riconosce {personaggio.key} come un criminale e lo attacca!"), exclude=[]
        )
        npc.avvia_combattimento(personaggio)
        return True
    return False


def tenta_assist(npc_attaccato, attaccante):
    """ASSIST-ALL (immhelp_flags.txt): se un mostro ostile viene
    attaccato, ogni altro mostro ostile presente nella stessa stanza, non
    gia' impegnato altrove, si unisce contro lo stesso aggressore. Scelta
    di design (Fase K, pre-release): la fonte distingue anche
    ASSIST-ALIGN/RACE/GUARD (assistenza solo tra mob dello stesso
    allineamento/razza/gruppo di guardia) - qui non implementate
    separatamente, dato che ASSIST-ALL (la piu' ampia) copre gia' il
    caso di gameplay piu' visibile: un gruppo di mostri nella stessa
    stanza che reagisce in blocco quando uno di loro viene attaccato.

    Bug reale trovato testando questa stessa funzione (Fase K,
    pre-release): se l'aggressore e' A SUA VOLTA un mostro del
    bestiario (es. un famiglio addomesticato, world/seguaci.py, che
    attacca un mostro ostile), l'assist puo' scatenare una cascata
    mostro-contro-mostro (il secondo mostro che assiste richiama a sua
    volta avvia_combattimento, che richiama ancora tenta_assist,
    trattando l'aggressore come se fosse lui stesso sotto attacco).
    Per restare fedele allo spirito della fonte (mob che si coalizzano
    contro UN aggressore esterno, tipicamente un giocatore) l'assist
    scatta solo se l'aggressore NON e' un mostro del bestiario."""
    if attaccante.attributes.has("bestiario_chiave"):
        return
    if not npc_attaccato.attributes.has("bestiario_chiave") or not npc_attaccato.location:
        return
    for altro in list(npc_attaccato.location.contents):
        if (
            altro is not npc_attaccato
            and altro is not attaccante
            and altro.attributes.has("bestiario_chiave")
            and getattr(altro, "vivo", False)
            and altro.db.ostile
            and not altro.db.combat_target
        ):
            altro.location.msg_contents(
                pericolo(f"{altro.key} si unisce alla difesa di {npc_attaccato.key}!"), exclude=[]
            )
            altro.avvia_combattimento(attaccante)


def tenta_inseguimento(cacciatore, vittima, destinazione):
    """HUNTER/TRACKER (immhelp_flags.txt: db.insegue_chi_fugge) esteso a
    QUALUNQUE movimento della vittima fuori dalla stanza, non solo alla
    fuga esplicita col comando FLEE - Fase K, pre-release, chiude un gap
    trovato in audit: prima di questa modifica bastava camminare
    normalmente (senza usare FLEE) per seminare un predatore che aveva
    gia' agganciato l'inseguimento, perche' la logica viveva solo dentro
    world/combat.py:tenta_fuga. Richiamata da
    typeclasses/rooms.py:at_object_leave per ogni personaggio che esce da
    una stanza. Resta comunque un inseguimento "a un salto per volta"
    (non teletrasporto): non implementa le varianti piu' estreme
    TELETRACKER/TELEHUNTER della fonte, scelta di design proporzionata
    dato l'impatto gia' alto della sola estensione multi-stanza."""
    if not (
        getattr(cacciatore, "db", None)
        and cacciatore.db.insegue_chi_fugge
        and cacciatore.db.combat_target == vittima
        and getattr(cacciatore, "vivo", False)
    ):
        return False
    cacciatore.location.msg_contents(pericolo(f"{cacciatore.key} insegue {vittima.key}!"), exclude=[])
    cacciatore.move_to(destinazione, quiet=True)
    destinazione.msg_contents(pericolo(f"{cacciatore.key} arriva all'inseguimento!"), exclude=[])
    cacciatore.avvia_combattimento(vittima)
    return True
