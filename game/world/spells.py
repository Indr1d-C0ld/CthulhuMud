"""
Registro incantesimi di CthulhuMUD ITA Redux.

Come per le professioni newbie (§Dossier Miskatonic, sezione 4): il sito
originale non documenta le formule esatte di successo/danno/guarigione di
nessun incantesimo - solo che il successo dipende da rating in Spell
Casting, rating nello skill specifico, salute e fattori ambientali. Le
percentuali/quantita' qui sono scelte di design esplicite (vedi
world/magic.py), facili da ritarare.

Ogni incantesimo richiede: la skill "spell_casting" (generica) + la skill
specifica con lo stesso id dell'incantesimo (entrambe in world/skills.py).

Fase G, quinta tornata: aggiunti 44 incantesimi emersi dagli alberi
Mage/Occult Master (world/professions_avanzate.py) durante la scansione
esaustiva del sito originale - descrizioni tradotte verbatim dalle
rispettive pagine helps/*.txt dove trovate (vedi research/site_corpus/),
altrimenti segnalate esplicitamente come scelta di design (pagina
originale vuota/non significativa: cancellation, dispel_magic,
elemental_shield). NON tutti hanno ancora un effetto meccanico
implementato in world/magic.py (es. invisibilita' vera, portali,
possessione NPC, evocazione famigli: sistemi di supporto che non
esistono ancora) - _esegui_effetto() gestisce il caso con un messaggio
di fallback onesto invece di fallire silenziosamente.

Fase K, quarta tornata: aggiunti altri 51 incantesimi emersi dalle
tabelle di livello delle 37 professioni avanzate completate in Fase K,
terza tornata (world/skills.py aveva gia' tutti questi ID come skill,
ma senza renderli lanciabili con CAST). Verificato pagina per pagina in
research/site_corpus/helps/: 47 hanno una pagina reale con "Syntax: CAST
'<NOME>' ..." che cita il nome ESATTO dell'ID (quindi genuinamente
lanciabili sotto quel nome); 4 ID che sembravano incantesimi a prima
vista (clerical_magic, dream_magic, elemental_combat, protective_magic)
si sono rivelati invece SKILL-prerequisito per una famiglia di
incantesimi con nomi DIVERSI (es. la pagina di "dream_magic" descrive
CAST TRANCE/TRUE DREAMING/RUDE AWAKENING/..., mai CAST 'DREAM MAGIC') -
lasciati fuori da questo registro in questa tornata (Fase K, ottava
tornata ha aggiunto i "fratelli" di dream_magic assieme a molte altre
famiglie, ma per una svista non ha controllato anche clerical_magic/
elemental_combat/protective_magic, corretto solo nella nona tornata -
vedi piu' sotto), coerenti con necromancy/natural_magic/way_of_nature,
allo stesso modo non ancora affrontate qui. 4 incantesimi (earthquake, heal, lesser_protection,
vision) sono un caso particolare: "heal" ha una pagina reale ma
condivisa con l'intera famiglia CURE LIGHT/SERIOUS/CRITICAL (testo
riusato correttamente); gli altri 3 non hanno alcuna pagina nel corpus
scansionato (un buco della scansione originale, come gia' capitato per
TWEAK/guides_beamage) - dichiarati esplicitamente come scelta di
design per analogia con incantesimi simili gia' esistenti. Come per la
tornata precedente, nessuno di questi 51 ha ancora un effetto meccanico
dedicato in world/magic.py - stesso fallback onesto.
"""

SPELLS = {
    "cure_light": {
        "nome": "Cura Leggera",
        "skill_richiesta": "cure_light",
        "costo_mana": 8,
        "bersaglio_richiesto": True,
        "descrizione": "Un incantesimo di guarigione di base.",
    },
    "shocking_grasp": {
        "ostile": True,
        "nome": "Presa Folgorante",
        "skill_richiesta": "shocking_grasp",
        "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Scarica un fulmine attraverso il tocco, danneggiando il bersaglio.",
    },
    "bless": {
        "nome": "Benedizione",
        "skill_richiesta": "bless",
        "costo_mana": 6,
        "bersaglio_richiesto": True,
        "descrizione": "Migliora temporaneamente la capacita' di colpire in combattimento.",
    },
    "detect_magic": {
        "nome": "Rilevare la Magia",
        "skill_richiesta": "detect_magic",
        "costo_mana": 5,
        "bersaglio_richiesto": False,
        "descrizione": "Percepisce la presenza di magia nei dintorni.",
    },
    "mask_self": {
        "nome": "Maschera di Se'",
        "skill_richiesta": "mask_self",
        "costo_mana": 6,
        "bersaglio_richiesto": False,
        "descrizione": "Offusca il proprio aspetto con un'illusione (si lancia di nuovo per toglierla).",
    },
    "clairvoyance": {
        "nome": "Chiaroveggenza",
        "skill_richiesta": "clairvoyance",
        "costo_mana": 10,
        "bersaglio_richiesto": False,
        "richiede_testo": True,
        "descrizione": "Vede a distanza in una direzione, senza spostarsi.",
    },

    # --- Fase G, quinta tornata: 44 incantesimi da Mage/Occult Master ---
    "absorb_magic": {
        "nome": "Assorbimento Magico", "skill_richiesta": "absorb_magic", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Concede protezione extra dagli attacchi magici, assorbendo e "
                       "dissipando parte degli incantesimi diretti contro il lanciatore.",
    },
    "blindness": {
        "ostile": True,
        "nome": "Accecamento", "skill_richiesta": "blindness", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Rende il bersaglio incapace di vedere. Trattato come incantesimo d'attacco.",
    },
    "brand": {
        "nome": "Marchiatura", "skill_richiesta": "brand", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Imprime su un'arma non ancora marchiata un elemento scelto a caso "
                       "(Fiamma, Gelo, Acido o Fulmine), permanente se il tentativo riesce - "
                       "ma l'arma rischia di essere distrutta nel tentativo.",
    },
    "burning_hands": {
        "ostile": True,
        "nome": "Mani Ardenti", "skill_richiesta": "burning_hands", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Scaglia una vampata di fiamme dalle mani, infliggendo danno da fuoco.",
    },
    "call_lightning": {
        "ostile": True,
        "nome": "Richiamo del Fulmine", "skill_richiesta": "call_lightning", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Richiama un fulmine su ogni personaggio all'aperto nella stessa area "
                       "del lanciatore - funziona solo all'aperto, con il maltempo.",
    },
    "calm": {
        "nome": "Calma", "skill_richiesta": "calm", "costo_mana": 10,
        "bersaglio_richiesto": False,
        "descrizione": "Riduce paura e furia, puo' interrompere un combattimento e riduce "
                       "temporaneamente la capacita' di colpire e il danno.",
    },
    "cancellation": {
        "nome": "Cancellazione", "skill_richiesta": "cancellation", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove gli effetti magici attivi su un bersaglio (pagina originale "
                       "priva di dettagli: effetto qui scelto per analogia con Dissolvere la Magia).",
    },
    "charm_person": {
        "ostile": True,
        "nome": "Ammaliare", "skill_richiesta": "charm_person", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Asservisce una vittima, che seguira' e obbedira' agli ordini del "
                       "lanciatore se l'incantesimo riesce.",
    },
    "continual_light": {
        "nome": "Luce Continua", "skill_richiesta": "continual_light", "costo_mana": 8,
        "bersaglio_richiesto": False,
        "descrizione": "Crea una sfera di luce arcana che non si spegne mai, fornendo "
                       "illuminazione indefinita.",
    },
    "create_food": {
        "nome": "Creare Cibo", "skill_richiesta": "create_food", "costo_mana": 10,
        "bersaglio_richiesto": False,
        "descrizione": "Forma un fagotto di frutta e verdura commestibile dal nulla.",
    },
    "create_spring": {
        "nome": "Creare Sorgente", "skill_richiesta": "create_spring", "costo_mana": 12,
        "bersaglio_richiesto": False,
        "descrizione": "Evoca una sorgente magica d'acqua scintillante, non permanente.",
    },
    "detect_hidden": {
        "nome": "Rilevare il Nascosto", "skill_richiesta": "detect_hidden", "costo_mana": 8,
        "bersaglio_richiesto": False,
        "descrizione": "Permette di vedere oggetti e creature nascosti o occultati, di "
                       "livello pari o inferiore al lanciatore.",
    },
    "detect_invis": {
        "nome": "Rilevare l'Invisibile", "skill_richiesta": "detect_invis", "costo_mana": 8,
        "bersaglio_richiesto": False,
        "descrizione": "Permette di vedere oggetti e creature invisibili, di livello pari o "
                       "inferiore al lanciatore.",
    },
    "dispel_magic": {
        "nome": "Dissolvere la Magia", "skill_richiesta": "dispel_magic", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove gli effetti magici attivi su un bersaglio (pagina originale "
                       "priva di dettagli: effetto qui scelto per coerenza col nome).",
    },
    "elemental_shield": {
        "nome": "Scudo Elementale", "skill_richiesta": "elemental_shield", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Avvolge il lanciatore in una protezione contro un elemento (pagina "
                       "originale priva di dettagli: scelta di design in analogia con le "
                       "altre magie difensive elementali).",
    },
    "enchant_armor": {
        "nome": "Incantare Armatura", "skill_richiesta": "enchant_armor", "costo_mana": 20,
        # Audit pre-beta: non serve indicare un bersaglio - l'effetto agisce
        # sull'arma impugnata / sull'armatura indossata da chi lancia (vedi
        # world/magic.py). Dichiararlo obbligava a nominare un bersaglio che
        # veniva poi ignorato, e senza il quale il lancio era rifiutato.
        "bersaglio_richiesto": False,
        "descrizione": "Potenzia un'armatura con magia protettiva: ogni lancio riuscito ne "
                       "alza il livello di 1 e ne migliora la classe armatura di 1-2 punti, ma "
                       "un tentativo fallito rischia di danneggiarla o distruggerla (il rischio "
                       "sale a ogni lancio riuscito successivo).",
    },
    "enchant_weapon": {
        "nome": "Incantare Arma", "skill_richiesta": "enchant_weapon", "costo_mana": 20,
        # Audit pre-beta: non serve indicare un bersaglio - l'effetto agisce
        # sull'arma impugnata / sull'armatura indossata da chi lancia (vedi
        # world/magic.py). Dichiararlo obbligava a nominare un bersaglio che
        # veniva poi ignorato, e senza il quale il lancio era rifiutato.
        "bersaglio_richiesto": False,
        "descrizione": "Potenzia un'arma con magia: ogni lancio riuscito ne migliora colpire "
                       "e danno e ne alza il livello di 1; piu' lanci sono possibili sulla "
                       "stessa arma, ma il rischio di danneggiarla sale a ogni successo.",
    },
    "faerie_fire": {
        "ostile": True,
        "nome": "Fuoco Fatato", "skill_richiesta": "faerie_fire", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Incantesimo d'attacco che alza la classe armatura della vittima (la "
                       "rende piu' facile da colpire) di 2 punti per livello del lanciatore.",
    },
    "faerie_fog": {
        "nome": "Nebbia Fatata", "skill_richiesta": "faerie_fog", "costo_mana": 10,
        "bersaglio_richiesto": False,
        "descrizione": "Rivela personaggi e oggetti invisibili o nascosti nella stanza.",
    },
    "fire_breath": {
        "ostile": True,
        "nome": "Soffio di Fuoco", "skill_richiesta": "fire_breath", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Un potente soffio infuocato contro un bersaglio (parte della "
                       "famiglia 'Magie del Soffio': Acido/Fuoco/Gelo/Gas, ognuna piu' o meno "
                       "efficace contro immunita' naturali diverse).",
    },
    "fireball": {
        "ostile": True,
        "nome": "Palla di Fuoco", "skill_richiesta": "fireball", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Crea una grande sfera di fuoco lanciata contro il bersaglio: il danno "
                       "viene sia dall'impatto sia dal calore delle fiamme.",
    },
    "fly": {
        "nome": "Volo", "skill_richiesta": "fly", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Permette di fluttuare in aria: il movimento diventa piu' facile e "
                       "meno faticoso, ma non si puo' volare sott'acqua.",
    },
    "frost_breath": {
        "ostile": True,
        "nome": "Soffio Gelido", "skill_richiesta": "frost_breath", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Un potente soffio gelido contro un bersaglio (famiglia 'Magie del "
                       "Soffio', vedi Soffio di Fuoco).",
    },
    "greater_possession": {
        "ostile": True,
        "nome": "Possessione Maggiore", "skill_richiesta": "greater_possession", "costo_mana": 30,
        "bersaglio_richiesto": True,
        "descrizione": "Come Possessione Minore, ma funziona anche su NPC piu' potenti: "
                       "sposta la mente del lanciatore nel corpo di un NPC, utilizzabile come "
                       "proprio finche' non torna con il comando RETURN o quel corpo muore.",
    },
    "harden_skin": {
        "nome": "Pelle Indurita", "skill_richiesta": "harden_skin", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Il primo di una serie di incantesimi difensivi (Pelle di Corteccia / "
                       "di Pietra / di Ferro / d'Acciaio) che induriscono la pelle del "
                       "lanciatore, rendendolo piu' resistente ai danni; ciascuno della serie "
                       "e' piu' difficile e costoso in mana del precedente.",
    },
    "haste": {
        "nome": "Fretta", "skill_richiesta": "haste", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Aumenta temporaneamente la Destrezza del bersaglio, rendendolo piu' "
                       "rapido e agile in combattimento (l'opposto, Lentezza, la riduce).",
    },
    "identify": {
        "nome": "Identificare", "skill_richiesta": "identify", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Rivela le statistiche grezze di un oggetto, eventuali effetti "
                       "magici, flag speciali e le zone d'origine - le stesse informazioni "
                       "della skill Sapienza Arcana (LORE), ma dipende anche dal Lancio degli Incantesimi.",
    },
    "invis": {
        "nome": "Invisibilita'", "skill_richiesta": "invis", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Rende invisibile il bersaglio; l'effetto svanisce entrando in "
                       "combattimento, e i personaggi di livello piu' alto possono comunque vederlo.",
    },
    "lesser_possession": {
        "ostile": True,
        "nome": "Possessione Minore", "skill_richiesta": "lesser_possession", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Sposta la mente del lanciatore nel corpo di un NPC debole, "
                       "utilizzabile come proprio; se il corpo posseduto muore la mente torna "
                       "incolume al proprio corpo (anche a comando, con RETURN).",
    },
    "magic_missile": {
        "ostile": True,
        "nome": "Missile Magico", "skill_richiesta": "magic_missile", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Scaglia numerosi proiettili di energia contro il bersaglio (versione "
                       "intermedia della famiglia Zap/Missile Magico/Zappatore Magico, in "
                       "ordine crescente di potenza).",
    },
    "mass_invis": {
        "nome": "Invisibilita' di Massa", "skill_richiesta": "mass_invis", "costo_mana": 30,
        "bersaglio_richiesto": False,
        "descrizione": "Rende invisibile ogni personaggio nel gruppo del lanciatore, "
                       "lanciatore incluso.",
    },
    "mute": {
        "ostile": True,
        "nome": "Ammutolire", "skill_richiesta": "mute", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Rende muta la vittima, impedendole di lanciare incantesimi con "
                       "componente verbale e di usare le comunicazioni IC finche' l'effetto non svanisce.",
    },
    "negate_alignment": {
        "nome": "Negare l'Allineamento", "skill_richiesta": "negate_alignment", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove le aure legate all'allineamento su un oggetto, permettendo "
                       "ad altri personaggi di usarlo.",
    },
    "pass_door": {
        "nome": "Attraversare le Porte", "skill_richiesta": "pass_door", "costo_mana": 12,
        "bersaglio_richiesto": False,
        "descrizione": "Permette al lanciatore di attraversare la maggior parte delle porte chiuse.",
    },
    "portal": {
        "nome": "Portale", "skill_richiesta": "portal", "costo_mana": 25,
        "bersaglio_richiesto": False,
        "descrizione": "Crea un varco arcano bidirezionale nello spazio, simile per funzione "
                       "all'incantesimo Gate ma piu' comodo per chi deve fare la spola tra due luoghi.",
    },
    "remove_invis": {
        "nome": "Rimuovere Invisibilita'", "skill_richiesta": "remove_invis", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove l'invisibilita' da un oggetto nell'inventario del lanciatore, "
                       "rendendolo di nuovo visibile a tutti.",
    },
    "shield": {
        "nome": "Scudo Magico", "skill_richiesta": "shield", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Versione piu' potente di Scudo di Mana: avvolge il lanciatore in una "
                       "sfera di energia arcana che migliora la classe armatura e riduce il "
                       "danno subito (non si puo' avere entrambi gli scudi attivi insieme).",
    },
    "sleep": {
        "ostile": True,
        "nome": "Sonno", "skill_richiesta": "sleep", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Fa sprofondare il bersaglio in un sonno profondo, da cui puo' essere "
                       "molto difficile risvegliarlo.",
    },
    "strength": {
        "nome": "Forza (incantesimo)", "skill_richiesta": "strength", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Aumenta temporaneamente la Forza del bersaglio.",
    },
    "summon": {
        "ostile": True,
        "nome": "Evocazione", "skill_richiesta": "summon", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Trasporta un personaggio da un'altra stanza fino alla posizione del "
                       "lanciatore; e' molto difficile evocare un personaggio di livello "
                       "superiore, e alcune stanze non permettono di essere evocati ne' di evocare.",
    },
    "summon_familier": {
        "nome": "Evocare Famiglio", "skill_richiesta": "summon_familier", "costo_mana": 25,
        "bersaglio_richiesto": False,
        "descrizione": "Richiama una creatura al servizio del lanciatore, completamente "
                       "obbediente ai suoi ordini; il tipo di creatura dipende dall'allineamento del lanciatore.",
    },
    "ventriloquate": {
        "nome": "Ventriloquio", "skill_richiesta": "ventriloquate", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "richiede_testo": True,
        "descrizione": "Getta la voce del lanciatore, facendo sembrare che sia stato un "
                       "altro personaggio a dire il messaggio specificato.",
    },
    "water_breathing": {
        "nome": "Respirare in Acqua", "skill_richiesta": "water_breathing", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Permette a chi non e' nativo di ambienti acquatici di respirare "
                       "sott'acqua senza subire danni per mancanza d'ossigeno.",
    },
    "word_of_recall": {
        "nome": "Parola di Richiamo", "skill_richiesta": "word_of_recall", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Funziona insieme a Ancora Psichica o Ancora Materiale: una volta "
                       "ancorata una stanza, questo incantesimo trasporta il lanciatore li'.",
    },
    "teleport": {
        "ostile": True,
        "nome": "Teletrasporto", "skill_richiesta": "teleport", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Trasporta il bersaglio in un luogo casuale del mondo: un modo "
                       "interessante, e potenzialmente letale, di esplorare.",
    },

    # --- Fase K, quarta tornata: 51 incantesimi dalle tabelle delle 37 professioni ---
    "acid_blast": {
        "ostile": True,
        "nome": "Getto Acido", "skill_richiesta": "acid_blast", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Scaglia un potente getto d'acido contro un nemico, causando gravi "
                       "ustioni chimiche e danno.",
    },
    "acid_breath": {
        "ostile": True,
        "nome": "Soffio Acido", "skill_richiesta": "acid_breath", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Un potente soffio d'acido contro un bersaglio (famiglia 'Magie del "
                       "Soffio': Acido/Fuoco/Gelo/Gas/Fulmine, ognuna piu' o meno efficace "
                       "contro immunita' naturali diverse - vedi Soffio di Fuoco/Gelo/Gas).",
    },
    "gas_breath": {
        "ostile": True,
        "nome": "Soffio di Gas", "skill_richiesta": "gas_breath", "costo_mana": 22,
        "bersaglio_richiesto": False,
        "descrizione": "A differenza degli altri Soffi (mirati a un bersaglio), questo "
                       "colpisce chiunque nella stanza tranne il lanciatore.",
    },
    "lightning_breath": {
        "ostile": True,
        "nome": "Soffio Fulminante", "skill_richiesta": "lightning_breath", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Un potente soffio elettrico contro un bersaglio (famiglia 'Magie del "
                       "Soffio', vedi Soffio Acido/di Fuoco/Gelo/Gas).",
    },
    "age": {
        "ostile": True,
        "nome": "Invecchiamento", "skill_richiesta": "age", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Aumenta l'eta' del bersaglio: dato che a CthulhuMUD si puo' morire "
                       "di vecchiaia, e' trattato come un incantesimo d'attacco vero e "
                       "proprio, e la vittima si difende.",
    },
    "youth": {
        "nome": "Giovinezza", "skill_richiesta": "youth", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Riduce l'eta' del bersaglio: l'opposto di Invecchiamento.",
    },
    "aura": {
        "nome": "Aura", "skill_richiesta": "aura", "costo_mana": 10,
        "bersaglio_richiesto": False,
        "descrizione": "Circonda il lanciatore di un bagliore che riflette il proprio "
                       "allineamento attuale; puo' incutere paura in chi ha un allineamento "
                       "diverso dal proprio.",
    },
    "cause_light": {
        "ostile": True,
        "nome": "Causa Ferita Leggera", "skill_richiesta": "cause_light", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Il piu' debole della famiglia Causa Ferita: un'esplosione di dolore "
                       "che danneggia gli organi interni della vittima dall'interno.",
    },
    "cause_serious": {
        "ostile": True,
        "nome": "Causa Ferita Grave", "skill_richiesta": "cause_serious", "costo_mana": 16,
        "bersaglio_richiesto": True,
        "descrizione": "Versione intermedia della famiglia Causa Ferita: piu' dolorosa di "
                       "Causa Ferita Leggera, ma anche piu' difficile da lanciare.",
    },
    "cause_critical": {
        "ostile": True,
        "nome": "Causa Ferita Critica", "skill_richiesta": "cause_critical", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Il piu' potente della famiglia Causa Ferita prima di Danno Divino: "
                       "gravi danni interni, molto difficile da lanciare con successo.",
    },
    "harm": {
        "ostile": True,
        "nome": "Danno Divino", "skill_richiesta": "harm", "costo_mana": 28,
        "bersaglio_richiesto": True,
        "descrizione": "Il culmine della famiglia Causa Ferita (dopo Leggera/Grave/Critica): "
                       "la piu' potente e la piu' difficile da lanciare con successo.",
    },
    "chain_lightning": {
        "ostile": True,
        "nome": "Fulmine a Catena", "skill_richiesta": "chain_lightning", "costo_mana": 25,
        "bersaglio_richiesto": False,
        "descrizione": "Crea un fulmine che rimbalza per la stanza, colpendo ripetutamente "
                       "ogni presente (lanciatore incluso) finche' non esaurisce la carica.",
    },
    "chill_touch": {
        "ostile": True,
        "nome": "Tocco Gelido", "skill_richiesta": "chill_touch", "costo_mana": 14,
        "bersaglio_richiesto": True,
        "descrizione": "Infligge danno alla vittima e ne riduce contemporaneamente la Forza "
                       "con un tocco gelido.",
    },
    "colour_spray": {
        "ostile": True,
        "nome": "Spruzzo Cromatico", "skill_richiesta": "colour_spray", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Spara vividi lampi di colore dalle dita del lanciatore, abbagliando "
                       "il nemico e infliggendo il tipo di danno elementale a cui e' piu' "
                       "vulnerabile.",
    },
    "control_weather": {
        "nome": "Controllo del Tempo", "skill_richiesta": "control_weather", "costo_mana": 15,
        "bersaglio_richiesto": False, "richiede_testo": True,
        "descrizione": "Altera le condizioni meteo attuali, rendendole MIGLIORI (sereno e "
                       "soleggiato) o PEGGIORI (nuvoloso e tempestoso) a seconda "
                       "dell'indicazione fornita.",
    },
    "create_buffet": {
        "nome": "Crea Banchetto", "skill_richiesta": "create_buffet", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Versione potenziata di Creare Cibo: forma numerosi fagotti di frutta "
                       "e verdura commestibile, tanti quanto piu' alta e' la skill del "
                       "lanciatore.",
    },
    "create_water": {
        "nome": "Crea Acqua", "skill_richiesta": "create_water", "costo_mana": 8,
        "bersaglio_richiesto": True,
        "descrizione": "Riempie un contenitore vuoto con acqua pura.",
    },
    "cure_blindness": {
        "nome": "Cura Cecita'", "skill_richiesta": "cure_blindness", "costo_mana": 14,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove la cecita' da un personaggio, permettendogli di vedere di "
                       "nuovo.",
    },
    "cure_critical": {
        "nome": "Cura Ferita Critica", "skill_richiesta": "cure_critical", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Il piu' potente dei classici incantesimi di guarigione prima di "
                       "Guarigione: ripristina grandi quantita' di punti ferita, ma costa "
                       "piu' mana e richiede piu' tempo di Cura Leggera/Grave.",
    },
    "heal": {
        "nome": "Guarigione", "skill_richiesta": "heal", "costo_mana": 28,
        "bersaglio_richiesto": True,
        "descrizione": "Il culmine della famiglia Cura Leggera/Grave/Critica: ripristina la "
                       "maggior quantita' possibile di punti ferita tra questi incantesimi, "
                       "ma e' anche il piu' difficile da lanciare con successo.",
    },
    "cure_disease": {
        "nome": "Cura Malattia", "skill_richiesta": "cure_disease", "costo_mana": 16,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove una malattia infettiva da un personaggio, guarendo gli "
                       "effetti debilitanti di un incantesimo come Peste.",
    },
    "cure_poison": {
        "nome": "Cura Veleno", "skill_richiesta": "cure_poison", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Guarisce un personaggio avvelenato, rimuovendone gli effetti "
                       "negativi.",
    },
    "cure_serious": {
        "nome": "Cura Ferita Grave", "skill_richiesta": "cure_serious", "costo_mana": 16,
        "bersaglio_richiesto": True,
        "descrizione": "Versione intermedia della famiglia di guarigione: piu' efficace di "
                       "Cura Leggera, ma anche piu' difficile da lanciare.",
    },
    "curse": {
        "ostile": True,
        "nome": "Maledizione", "skill_richiesta": "curse", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Rende impura e indebolita l'anima della vittima, riducendone la "
                       "capacita' di colpire e la resistenza agli incantesimi.",
    },
    "demonfire": {
        "ostile": True,
        "nome": "Fuoco Demoniaco", "skill_richiesta": "demonfire", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Evoca un'orda di demoni dagli abissi infernali per infliggere gravi "
                       "danni al bersaglio.",
    },
    "detect_poison": {
        "nome": "Rileva Veleno", "skill_richiesta": "detect_poison", "costo_mana": 6,
        "bersaglio_richiesto": False,
        "descrizione": "Percepisce la presenza di veleno in cibo o bevande a portata di mano.",
    },
    "dispel_evil": {
        "ostile": True,
        "nome": "Dissolvi Male", "skill_richiesta": "dispel_evil", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Richiama la collera divina per infliggere danno a un nemico "
                       "malvagio (vedi anche Dissolvi Bene, la controparte).",
    },
    "dispel_good": {
        "ostile": True,
        "nome": "Dissolvi Bene", "skill_richiesta": "dispel_good", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Richiama la collera divina per infliggere danno a un nemico "
                       "benevolo (vedi anche Dissolvi Male, la controparte).",
    },
    "earthquake": {
        "ostile": True,
        "nome": "Terremoto", "skill_richiesta": "earthquake", "costo_mana": 28,
        "bersaglio_richiesto": False,
        "descrizione": "Scuote violentemente il terreno sotto ogni presente nella stanza, "
                       "lanciatore escluso, infliggendo danno da impatto a tutti (pagina "
                       "originale assente dal corpus scansionato: effetto scelto per "
                       "analogia con Fulmine a Catena/Richiamo del Fulmine, altri incantesimi "
                       "d'area gia' documentati).",
    },
    "energy_drain": {
        "ostile": True,
        "nome": "Drenaggio d'Energia", "skill_richiesta": "energy_drain", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Assorbe esperienza, mana e movimento dal bersaglio.",
    },
    "gate": {
        "nome": "Varco Dimensionale", "skill_richiesta": "gate", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Trasporta istantaneamente il lanciatore nella stessa stanza di un "
                       "personaggio bersaglio (alcune stanze private o Immortali non sono "
                       "raggiungibili in questo modo).",
    },
    "holy_word": {
        "nome": "Parola Sacra", "skill_richiesta": "holy_word", "costo_mana": 28,
        "bersaglio_richiesto": False,
        "descrizione": "Evoca un potente angelo che combatte al fianco del lanciatore contro "
                       "un nemico malvagio.",
    },
    "know_alignment": {
        "nome": "Percepisci Allineamento", "skill_richiesta": "know_alignment", "costo_mana": 8,
        "bersaglio_richiesto": True,
        "descrizione": "Rivela l'allineamento attuale del bersaglio.",
    },
    "lesser_protection": {
        "nome": "Protezione Minore", "skill_richiesta": "lesser_protection", "costo_mana": 10,
        "bersaglio_richiesto": False,
        "descrizione": "Una difesa magica di base, precedente e piu' economica di Globo di "
                       "Protezione/Santuario (pagina originale assente dal corpus "
                       "scansionato: effetto scelto per analogia con la serie Pelle "
                       "Indurita, altri incantesimi difensivi 'a gradini' gia' documentati).",
    },
    "lightning_bolt": {
        "ostile": True,
        "nome": "Fulmine", "skill_richiesta": "lightning_bolt", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Scaglia un fulmine crepitante contro il bersaglio.",
    },
    "locate_object": {
        "nome": "Localizza Oggetto", "skill_richiesta": "locate_object", "costo_mana": 12,
        # Audit pre-beta: dichiarava "bersaglio_richiesto" ed era quindi
        # ROTTO. L'effetto cerca per NOME nel mondo intero (world/magic.py),
        # ma il comando CAST valorizza "testo" solo per gli incantesimi con
        # richiede_testo: qui restava None e la ricerca nel database falliva
        # con "Cannot use None as a query value" a ogni lancio. Per giunta
        # obbligava a indicare un bersaglio presente nella stanza, cioe' un
        # oggetto che per definizione non c'e' bisogno di localizzare.
        "bersaglio_richiesto": False, "richiede_testo": True,
        "descrizione": "Rivela la posizione di tutti gli oggetti che corrispondono al nome "
                       "specificato, ovunque nel mondo (non specifica se sono trasportati da "
                       "qualcuno, e alcuni oggetti sono invisibili a questo incantesimo).",
    },
    "magefire": {
        "ostile": True,
        "nome": "Fuoco Arcano", "skill_richiesta": "magefire", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Scaglia una o piu' scariche di energia arcana, ciascuna capace di "
                       "rimuovere le protezioni magiche attive sul bersaglio.",
    },
    "mass_healing": {
        "nome": "Guarigione di Massa", "skill_richiesta": "mass_healing", "costo_mana": 30,
        "bersaglio_richiesto": False,
        "descrizione": "Invia energia curativa che guarisce tutti gli alleati e amici del "
                       "lanciatore in una vasta area.",
    },
    "plague": {
        "ostile": True,
        "nome": "Peste", "skill_richiesta": "plague", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Infetta la vittima con una malattia altamente contagiosa: riduce le "
                       "sue capacita' di combattimento e rischia di diffondersi ad altri.",
    },
    "poison": {
        "ostile": True,
        "nome": "Veleno (incantesimo)", "skill_richiesta": "poison", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Indebolisce la vittima e ne riduce le capacita' di combattimento "
                       "infliggendole il veleno.",
    },
    "protection_evil": {
        "nome": "Protezione dal Male", "skill_richiesta": "protection_evil", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Protegge il lanciatore dagli attacchi di nemici malvagi, riducendo "
                       "di un quarto il danno subito da quell'allineamento (vedi anche "
                       "Protezione dal Bene, la controparte).",
    },
    "protection_good": {
        "nome": "Protezione dal Bene", "skill_richiesta": "protection_good", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Protegge il lanciatore dagli attacchi di nemici benevoli, riducendo "
                       "di un quarto il danno subito da quell'allineamento (vedi anche "
                       "Protezione dal Male, la controparte).",
    },
    "psychic_anchor": {
        "nome": "Ancora Psichica", "skill_richiesta": "psychic_anchor", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Lascia parte dell'essenza psichica del lanciatore in una stanza, "
                       "creando un'ancora a cui tornare con Parola di Richiamo (le stanze "
                       "private non si possono ancorare; l'ancora si spezza alla morte, alla "
                       "disconnessione o non appena viene usata).",
    },
    "regeneration": {
        "nome": "Rigenerazione", "skill_richiesta": "regeneration", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Aumenta la velocita' di guarigione naturale del bersaglio per tutta "
                       "la durata dell'incantesimo.",
    },
    "remove_curse": {
        "nome": "Rimuovi Maledizione", "skill_richiesta": "remove_curse", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove una maledizione attiva su un personaggio.",
    },
    "remove_fear": {
        "nome": "Rimuovi Paura", "skill_richiesta": "remove_fear", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Annulla gli effetti dell'incantesimo Paura su un personaggio, che "
                       "altrimenti fuggirebbe (o resterebbe incapace di attaccare) finche' "
                       "l'effetto non svanisce da solo.",
    },
    "vision": {
        "nome": "Visione", "skill_richiesta": "vision", "costo_mana": 12,
        "bersaglio_richiesto": False,
        "descrizione": "Concede al lanciatore un breve scorcio, sfocato ma reale, di un "
                       "luogo lontano (pagina originale assente dal corpus scansionato: "
                       "effetto scelto per analogia con Chiaroveggenza/Scrutare, altri "
                       "incantesimi di percezione a distanza gia' documentati).",
    },
    "weaken": {
        "ostile": True,
        "nome": "Indebolisci", "skill_richiesta": "weaken", "costo_mana": 14,
        "bersaglio_richiesto": True,
        "descrizione": "Riduce temporaneamente la Forza del bersaglio, indebolendone le "
                       "capacita' offensive in combattimento.",
    },
    "frenzy": {
        "nome": "Frenesia", "skill_richiesta": "frenzy", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Manda il bersaglio in una furia insana durante il combattimento: "
                       "effetti simili a Furia Berserk, con un grande incremento delle "
                       "capacita' di combattimento e resistenza alla magia, ma anche "
                       "incapacita' di ritirarsi anche quando in fin di vita.",
    },
    "create_potion": {
        "nome": "Crea Pozione", "skill_richiesta": "create_potion", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Mescola erbe e ingredienti nella speranza di ottenere qualcosa di "
                       "utile: crea una pozione magica casuale con effetti casuali, senza "
                       "possibilita' di scegliere quali.",
    },
    "vocalize": {
        "nome": "Vocalizzo", "skill_richiesta": "vocalize", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Permette al bersaglio di lanciare incantesimi senza componente "
                       "verbale: anche se reso muto, potra' continuare a lanciarli finche' "
                       "possiede anche questo effetto.",
    },

    # --- Fase K, settima tornata: i "dieci sotto-incantesimi" citati dalla
    # descrizione stessa della skill Controllo del Corpo (world/skills.py) -
    # ognuna delle rispettive pagine helps/*.txt conferma "requires the BODY
    # CONTROL skill" verbatim, quindi condividono tutti lo stesso
    # skill_richiesta invece di avere ciascuno una skill dedicata.
    "asceticism": {
        "nome": "Ascetismo", "skill_richiesta": "body_control", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Sospende temporaneamente il bisogno di cibo e acqua del lanciatore, "
                       "che non soffrira' gli effetti di fame o sete per la durata dell'effetto.",
    },
    "burden_of_blubber": {
        "ostile": True,
        "nome": "Fardello di Ciccia", "skill_richiesta": "body_control", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Fa ingrassare immediatamente il bersaglio, infliggendogli una serie "
                       "di effetti negativi tipici dell'obesita'.",
    },
    "burning_thirst": {
        "ostile": True,
        "nome": "Sete Ardente", "skill_richiesta": "body_control", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Estrae gran parte dell'umidita' dal corpo della vittima, "
                       "disidratandola e infliggendole una sete terribile.",
    },
    "change_size": {
        "nome": "Cambia Taglia", "skill_richiesta": "body_control", "costo_mana": 12,
        "bersaglio_richiesto": False, "richiede_testo": True,
        "descrizione": "Permette al lanciatore di aumentare o diminuire la taglia del "
                       "proprio corpo fisico.",
    },
    "free_grog": {
        "ostile": True,
        "nome": "Grog Libero", "skill_richiesta": "body_control", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Rende immediatamente ubriaco il bersaglio.",
    },
    "ghastly_sobriety": {
        "ostile": True,
        "nome": "Sobrieta' Spettrale", "skill_richiesta": "body_control", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove immediatamente ogni alcol dal sangue e dal cervello del "
                       "bersaglio, annullando all'istante gli effetti dell'ubriachezza - "
                       "lasciandolo pero' con un violento mal di testa.",
    },
    "gnawing_hunger": {
        "ostile": True,
        "nome": "Fame Rodente", "skill_richiesta": "body_control", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Infligge al bersaglio una fame potente e feroce, causandogli grave "
                       "debolezza e altri effetti negativi.",
    },
    "hallucinate": {
        "ostile": True,
        "nome": "Allucina", "skill_richiesta": "body_control", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Confonde gravemente la mente del bersaglio, dando vita a figmenti "
                       "della sua immaginazione con la magia arcana: le allucinazioni possono "
                       "essere pericolose sia per lui sia per chiunque gli sia vicino.",
    },
    "relax": {
        "nome": "Rilassati", "skill_richiesta": "body_control", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Aumenta la resistenza del bersaglio alla perdita di sanity.",
    },
    "slender_lines": {
        "nome": "Linee Snelle", "skill_richiesta": "body_control", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove una grande quantita' di grasso dal bersaglio, curandone "
                       "l'obesita' e rimuovendone gli effetti negativi.",
    },

    # --- Fase K, ottava tornata: i "fratelli" delle famiglie di
    # incantesimi Necromanzia/Magia Divina/Magia Onirica/Magia Mentale/
    # Via della Natura/Via del Duellante/Taumaturgia/Magia degli Antichi -
    # confermati dalla fonte come skill-prerequisito condiviso (stesso
    # pattern gia' visto per Controllo del Corpo), scoperti durante
    # quella tornata ma non ancora costruiti. Magia Naturale (Natural
    # Magic) resta l'unica esclusa: la sua stessa pagina in
    # world/skills.py conferma "non collegata direttamente a una skill
    # specifica" - nessun incantesimo la richiede.

    # -- Necromanzia (10) --
    "animate_dead": {
        "nome": "Anima Morto", "skill_richiesta": "necromancy", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Rianima un cadavere, creando uno zombie senz'anima e totalmente "
                       "obbediente al lanciatore.",
    },
    "lich": {
        "nome": "Lich", "skill_richiesta": "necromancy", "costo_mana": 40,
        "bersaglio_richiesto": False,
        "descrizione": "Trasformerebbe permanentemente il lanciatore in un Lich non-morto. "
                       "La fonte stessa segnala questo incantesimo come DISABILITATO "
                       "(\"NOTE: This spell is currently disabled\") - diventare un Lich "
                       "resta possibile solo tramite il comando SUBRACE riservato allo "
                       "staff (vedi world/sottorazze.py), mai lanciando questo incantesimo.",
    },
    "darkness": {
        "ostile": True,
        "nome": "Oscurita'", "skill_richiesta": "necromancy", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Riempie l'intera stanza di un'ondata magica di oscurita' per "
                       "30 secondi: chi vi si trova non riesce piu' a vedere la stanza "
                       "(LOOK), a meno di avere con se' una fonte di luce accesa o "
                       "l'incantesimo Infravisione (vedi world/illuminazione.py).",
    },
    "mummify": {
        "nome": "Mummifica", "skill_richiesta": "necromancy", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Rianima un cadavere, creando una mummia senz'anima e totalmente "
                       "obbediente al lanciatore.",
    },
    "desecrate": {
        "ostile": True,
        "nome": "Profana", "skill_richiesta": "necromancy", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Riempie l'intera stanza di un'aura malvagia, trasformandola "
                       "temporaneamente in terra sconsacrata: i personaggi di allineamento "
                       "buono presenti subiscono danno per il solo fatto di trovarcisi.",
    },
    "soul_blade": {
        "nome": "Lama dell'Anima", "skill_richiesta": "necromancy", "costo_mana": 22,
        "bersaglio_richiesto": False,
        "descrizione": "Crea una spada magica incantata, forgiata dalla stessa anima "
                       "del lanciatore.",
    },
    "doppelganger": {
        "nome": "Sosia", "skill_richiesta": "necromancy", "costo_mana": 25,
        "bersaglio_richiesto": False,
        "descrizione": "Crea una replica non-morta del lanciatore, utilizzabile come "
                       "un famiglio al suo fianco.",
    },
    "spring_of_blood": {
        "nome": "Sorgente di Sangue", "skill_richiesta": "necromancy", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Evoca una fontana magica di sangue fresco. Non e' permanente: "
                       "col tempo si prosciughera' e sparira'.",
    },
    "fist_of_azathoth": {
        "ostile": True,
        "nome": "Pugno di Azathoth", "skill_richiesta": "necromancy", "costo_mana": 40,
        "bersaglio_richiesto": True,
        "descrizione": "Un potente incantesimo d'attacco capace di uccidere istantaneamente "
                       "il bersaglio. Anche quando non uccide, infligge comunque un danno "
                       "considerevole.",
    },
    "unrest": {
        "ostile": True,
        "nome": "Inquietudine", "skill_richiesta": "necromancy", "costo_mana": 22,
        "bersaglio_richiesto": False,
        "descrizione": "Diffonde un'aura malvagia nell'area, aumentando la probabilita' "
                       "che i cadaveri presenti si rianimino spontaneamente in mostri "
                       "non-morti. L'effetto non e' permanente e svanira' col tempo.",
    },

    # -- Magia Divina (3 di 9 - le altre 6 non hanno lasciato traccia nel
    # corpus scaricato, stesso tipo di buco gia' incontrato piu' volte in
    # questa sessione: TWEAK, guides_beamage, alcuni incantesimi minori) --
    "mortalize": {
        "ostile": True,
        "nome": "Mortalizza", "skill_richiesta": "divine_magic", "costo_mana": 35,
        "bersaglio_richiesto": True,
        "descrizione": "Rimuove la natura divina e invulnerabile di un Antico (staff). "
                       "Anche se e' davvero possibile uccidere un Antico dopo questo "
                       "incantesimo, sarebbe bene riflettere a lungo sulle possibili "
                       "conseguenze prima di tentarlo.",
    },
    "summon_old": {
        "ostile": True,
        "nome": "Evoca Antico", "skill_richiesta": "divine_magic", "costo_mana": 30,
        "bersaglio_richiesto": True,
        "descrizione": "Teletrasporta un Antico (staff) specifico nella posizione attuale "
                       "del lanciatore. Conviene pensarci bene prima di spostare un Antico "
                       "per motivi personali.",
    },
    "soul_guard": {
        "nome": "Guardia dell'Anima", "skill_richiesta": "divine_magic", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Protegge l'anima del bersaglio dagli effetti delle proprie azioni: "
                       "il suo allineamento non verra' influenzato, ad esempio uccidendo "
                       "personaggi di vari allineamenti.",
    },

    # -- Magia Onirica (6) - si aggancia al sistema Dreamlands gia'
    # esistente (commands/cthulhu_dream.py, Fase E) --
    "trance": {
        "nome": "Trance", "skill_richiesta": "dream_magic", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Migliora la capacita' onirica del bersaglio, rendendo piu' "
                       "probabile scivolare nelle Dreamlands sognando.",
    },
    "true_dreaming": {
        "ostile": True,
        "nome": "Vera Dormienza", "skill_richiesta": "dream_magic", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Trascina il bersaglio interamente nel mondo dei propri sogni: il "
                       "corpo fisico viene proiettato nelle Dreamlands, recidendo il "
                       "legame col mondo reale.",
    },
    "rude_awakening": {
        "nome": "Risveglio Brusco", "skill_richiesta": "dream_magic", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Respinge un bersaglio addormentato fuori dal proprio sogno, "
                       "svegliandolo di soprassalto e riportandolo nel mondo reale.",
    },
    "recurring_dream": {
        "ostile": True,
        "nome": "Sogno Ricorrente", "skill_richiesta": "dream_magic", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Rimanda un bersaglio sveglio al punto esatto in cui si trovava "
                       "l'ultima volta che sognava.",
    },
    "enchanted_sleep": {
        "ostile": True,
        "nome": "Sonno Incantato", "skill_richiesta": "dream_magic", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Immerge il bersaglio in un sonno profondissimo, che lo fa "
                       "attraversare immediatamente nel regno dei propri sogni. Questi "
                       "sogni sono normalmente sicuri e privi di incubi.",
    },
    "accursed_sleep": {
        "ostile": True,
        "nome": "Sonno Maledetto", "skill_richiesta": "dream_magic", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Come Sonno Incantato, immerge il bersaglio in un sonno profondo e "
                       "immediato - ma lo scaraventa in un incubo pericoloso invece che "
                       "in un sogno sicuro.",
    },

    # -- Magia Mentale (3 - Mind Meld e' una scoperta di questa tornata:
    # la sua pagina reale nel corpus e' identica a quella condivisa
    # "mental.txt", mai notata prima come terzo incantesimo della coppia
    # gia' documentata) --
    "astral_walk": {
        "nome": "Cammino Astrale", "skill_richiesta": "mental_magic", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Distacca la mente del lanciatore dal corpo fisico, trasferendola "
                       "nel proprio corpo astrale. Esplorare in forma astrale e' "
                       "estremamente sicuro, dato che la maggior parte delle creature non "
                       "puo' attaccare un corpo astrale - ma resta vulnerabile a Esplosione "
                       "Astrale. Per tornare al proprio corpo fisico si usa il comando RETURN.",
    },
    "astral_blast": {
        "ostile": True,
        "nome": "Esplosione Astrale", "skill_richiesta": "mental_magic", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Infligge danno a un corpo astrale - l'unico modo per colpire "
                       "qualcuno mentre e' distaccato nel Cammino Astrale.",
    },
    "mind_meld": {
        "ostile": True,
        "nome": "Fusione Mentale", "skill_richiesta": "mental_magic", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Un potente incantesimo d'attacco che sferra un possente colpo "
                       "psionico alla mente del bersaglio, azzoppandola temporaneamente: "
                       "infligge una penalita' di -5 all'Intelligenza e rende difficile "
                       "ogni attivita' che richieda concentrazione profonda finche' "
                       "l'effetto non svanisce.",
    },

    # -- Via della Natura (4) --
    "create_seed": {
        "nome": "Crea Seme", "skill_richiesta": "way_of_nature", "costo_mana": 10,
        "bersaglio_richiesto": False,
        "descrizione": "Crea il seme di un albero. Nella fonte puo' essere piantato col "
                       "comando PLANT: nessun sistema di coltivazione esiste ancora in "
                       "questo porting (scelta di design dichiarata), quindi qui il seme "
                       "resta un oggetto reale ma puramente di scena.",
    },
    "drain_vitality": {
        "nome": "Drena Vitalita'", "skill_richiesta": "way_of_nature", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Drena mana da un albero, trasferendolo al lanciatore.",
    },
    "insect_curse": {
        "ostile": True,
        "nome": "Maledizione degli Insetti", "skill_richiesta": "way_of_nature", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Evoca numerosi sciami di insetti di basso livello a infestare "
                       "l'area attuale, tormentando chiunque vi si trovi.",
    },
    "wolfbite": {
        "ostile": True,
        "nome": "Morso di Lupo", "skill_richiesta": "way_of_nature", "costo_mana": 30,
        "bersaglio_richiesto": True,
        "descrizione": "Trasforma il bersaglio in un licantropo. Riusa lo stesso sistema "
                       "di generazioni condiviso di WERE BITE (world/sottorazze.py): il "
                       "bersaglio diventa un Licantropo di prima generazione rispetto al "
                       "lanciatore, se il lanciatore stesso lo e' gia'.",
    },

    # -- Via del Duellante (7) --
    "magical_duel": {
        "ostile": True,
        "nome": "Duello Magico", "skill_richiesta": "way_of_the_duellant", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Avvia un duello arcano con un nemico: invece delle normali tecniche "
                       "di combattimento, i due contendenti usano la pura forza dei propri "
                       "poteri magici per sopraffarsi a vicenda. Durante il duello si puo' "
                       "usare il comando DUEL OFF/DEF <mana> per rafforzare attacco o difesa.",
    },
    "mental_shield": {
        "nome": "Scudo Mentale", "skill_richiesta": "way_of_the_duellant", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Avvolge il lanciatore in un'aura mistica che assorbe alcune forme "
                       "di attacco mentale e magico.",
    },
    "psi_twister": {
        "ostile": True,
        "nome": "Psi Twister", "skill_richiesta": "way_of_the_duellant", "costo_mana": 28,
        "bersaglio_richiesto": False,
        "descrizione": "Un potente incantesimo d'attacco che scatena la forza della mente "
                       "del lanciatore, infliggendo danno significativo a chiunque altro "
                       "si trovi nella stanza.",
    },
    "telekinesis": {
        "nome": "Telecinesi", "skill_richiesta": "way_of_the_duellant", "costo_mana": 15,
        "bersaglio_richiesto": False, "richiede_testo": True,
        "descrizione": "Usa la forza della mente per spostare un oggetto da una stanza "
                       "adiacente fino alla propria posizione attuale. Non funziona su "
                       "oggetti che normalmente non si possono prendere (fontane, mobili, "
                       "ecc.) ne' attraverso porte chiuse. Sintassi: CAST TELECINESI "
                       "<oggetto> <direzione>.",
    },
    "terror_of_the_old": {
        "ostile": True,
        "nome": "Terrore degli Antichi", "skill_richiesta": "way_of_the_duellant", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Crea l'immagine terrificante di Hastur l'Innominabile. Anche se "
                       "e' solo un'illusione, la sua sola vista e' capace di colpire il "
                       "bersaglio con una paura terribile.",
    },
    "wrath_of_cthugha": {
        "ostile": True,
        "nome": "Ira di Cthugha", "skill_richiesta": "way_of_the_duellant", "costo_mana": 35,
        "bersaglio_richiesto": True,
        "descrizione": "Scatena una potente palla di fuoco contro il bersaglio. La fonte "
                       "descrive la possibilita' di raccoglierla e lanciarla con THROW in "
                       "un'altra stanza (nessun comando THROW esiste in questo porting: "
                       "semplificazione dichiarata, colpisce direttamente il bersaglio "
                       "indicato). Il danno dipende da livello e rating del lanciatore ed "
                       "e' capace di infliggere quantita' di danno estremamente alte - "
                       "attenzione, piu' di un giocatore si e' fatto saltare in aria da "
                       "solo cercando di padroneggiarlo.",
    },
    "wrath_of_ithaqua": {
        "ostile": True,
        "nome": "Ira di Ithaqua", "skill_richiesta": "way_of_the_duellant", "costo_mana": 30,
        "bersaglio_richiesto": True,
        "descrizione": "Molto simile a Ira di Cthugha, ma crea una grande palla di neve "
                       "che infligge danno stordente invece che letale: mette fuori "
                       "combattimento invece di uccidere.",
    },

    # -- Taumaturgia (5) + Personalizza Arma (skill Incantare Arma, gia'
    # esistente e gia' usata da CAST ENCHANT WEAPON - qui aggiunta come
    # suo prerequisito naturale, confermato dalla fonte di Anima Arma
    # stessa: "the weapon in question must first be personalized
    # through use of the PERSONALIZE WEAPON spell") --
    "animate_weapon": {
        "nome": "Anima Arma", "skill_richiesta": "taumathurgy", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Richiama un'arma al suo proprietario, particolarmente utile se "
                       "l'arma e' stata persa o il proprietario e' morto di recente. Perche' "
                       "funzioni, l'arma deve prima essere stata personalizzata con "
                       "Personalizza Arma. C'e' anche una probabilita' che l'incantesimo "
                       "distrugga l'arma nel tentativo. Nota tecnica: essendo una ricerca "
                       "globale (l'arma puo' trovarsi ovunque nel mondo), Evennia richiede "
                       "di scriverne il nome ESATTO e completo, articolo incluso "
                       "(es. 'un pugnale forgiato da Carter').",
    },
    "consistence": {
        "nome": "Consistenza", "skill_richiesta": "taumathurgy", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Stabilizza un oggetto in decomposizione, impedendogli di "
                       "deperire ulteriormente. Come gli altri incantesimi di Taumaturgia, "
                       "c'e' una probabilita' di distruggere l'oggetto nel tentativo.",
    },
    "permanence": {
        "nome": "Permanenza", "skill_richiesta": "taumathurgy", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Rende un oggetto magico resistente a ogni forma di danno, "
                       "quasi indistruttibile. C'e' una probabilita' di distruggere "
                       "l'oggetto nel tentativo.",
    },
    "recharge": {
        "nome": "Ricarica", "skill_richiesta": "taumathurgy", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Riempie di nuove cariche un oggetto magico a cariche finite "
                       "(come alcune bacchette o alcuni bastoni), rendendolo di nuovo "
                       "utilizzabile.",
    },
    "universality": {
        "nome": "Universalita'", "skill_richiesta": "taumathurgy", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Permette a un oggetto di esistere in ogni zona e area. Questo "
                       "porting non impone alcuna restrizione di zona sul trasporto di "
                       "oggetti: l'incantesimo non ha percio' alcun effetto meccanico "
                       "reale da rimuovere, resta puramente di scena (scelta di design "
                       "dichiarata). C'e' comunque una probabilita' di distruggere "
                       "l'oggetto nel tentativo, come per gli altri due incantesimi della "
                       "stessa famiglia.",
    },
    "personalize_weapon": {
        "nome": "Personalizza Arma", "skill_richiesta": "enchant_weapon", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Imbue un'arma con parte della forza vitale del lanciatore, "
                       "impedendo a chiunque altro di poterla usare. C'e' una probabilita' "
                       "che l'incantesimo distrugga l'arma nel tentativo.",
    },

    # -- Magia degli Antichi (2) --
    "armor_of_ygolonac": {
        "nome": "Armatura di Ygolonac", "skill_richiesta": "elder_magic", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Crea uno scudo arcano attorno al bersaglio, che riduce del 75% "
                       "il danno fisico da combattimento (semplificazione dichiarata: la "
                       "fonte limita la riduzione ai soli danni da taglio/perforazione/"
                       "impatto, ma questo porting non distingue i tipi di danno fisico).",
    },
    "curse_of_the_hunter": {
        "ostile": True,
        "nome": "Maledizione del Cacciatore", "skill_richiesta": "elder_magic", "costo_mana": 35,
        "bersaglio_richiesto": True,
        "descrizione": "Evoca un Orrore Cacciatore a combattere contro i nemici del "
                       "lanciatore. Puo' pero' essere usato solo contro un nemico piu' "
                       "forte e potente del lanciatore stesso.",
    },

    # --- Fase K, nona tornata: le famiglie clerical_magic/elemental_combat/
    # protective_magic, mancate per una svista durante l'audit della
    # ottava tornata (stesso identico pattern "requires the X skill" gia'
    # visto per le altre famiglie di quella tornata) - vedi la nota
    # aggiornata in cima a questo file.
    "clerical_symbol": {
        "nome": "Simbolo Clericale", "skill_richiesta": "clerical_magic", "costo_mana": 12,
        "bersaglio_richiesto": True,
        "descrizione": "Trasforma un comune gioiello in un simbolo sacro.",
    },
    "revenge_of_cthugha": {
        "ostile": True,
        "nome": "Vendetta di Cthugha", "skill_richiesta": "elemental_combat", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Rende il bersaglio piu' vulnerabile al danno di fuoco.",
    },
    "revenge_of_ithaqua": {
        "ostile": True,
        "nome": "Vendetta di Ithaqua", "skill_richiesta": "elemental_combat", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Rende il bersaglio piu' vulnerabile al danno da freddo.",
    },
    "revenge_of_tsathoggua": {
        "ostile": True,
        "nome": "Vendetta di Tsathoggua", "skill_richiesta": "elemental_combat", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Rende il bersaglio piu' vulnerabile al danno da armi.",
    },
    "revenge_of_yog": {
        "ostile": True,
        "nome": "Vendetta di Yog", "skill_richiesta": "elemental_combat", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Rende il bersaglio piu' vulnerabile al danno da fulmine.",
    },
    "globe_of_protection": {
        "nome": "Globo di Protezione", "skill_richiesta": "protective_magic", "costo_mana": 25,
        "bersaglio_richiesto": False,
        "descrizione": "Avvolge il lanciatore in una sfera di energia protettiva che "
                       "migliora drasticamente la classe armatura. Cumulativo con Santuario "
                       "se lanciati entrambi sullo stesso personaggio.",
    },
    "sanctuary": {
        "nome": "Santuario", "skill_richiesta": "protective_magic", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Riduce del 50% tutto il danno subito dal bersaglio. Cumulativo con "
                       "Globo di Protezione se lanciati entrambi sullo stesso personaggio.",
    },
    "armor": {
        "nome": "Incantesimo d'Armatura", "skill_richiesta": "protective_magic", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Migliora la classe armatura complessiva del bersaglio. La pagina "
                       "originale non specifica una skill richiesta (unico caso tra gli "
                       "incantesimi difensivi): raggruppato per analogia sotto Magia "
                       "Protettiva, la stessa famiglia di Globo di Protezione/Santuario, "
                       "scelta di design dichiarata. Nome italiano diverso dalla skill "
                       "mondana 'Uso dell'Armatura' (stesso nome inglese 'Armor' nella "
                       "fonte, ma tutt'altro significato) per evitare ambiguita'.",
    },

    # ==========================================================================
    # Fase K, decima tornata: ~79 incantesimi scoperti tramite l'indice
    # completo ALLSPELLS (helps/allspells.txt, 234 nomi) mai controllato
    # prima d'ora - molti erano gia' impliciti nelle descrizioni delle
    # skill/incantesimi "capostipite" gia' costruiti (es. Pelle Indurita
    # gia' diceva "il primo di una serie", Scudo Magico "versione piu'
    # potente di Scudo di Mana") ma le loro sorelle non erano mai state
    # aggiunte. Organizzati per famiglia come le pagine sorgente.
    # ==========================================================================

    # -- Pelle Indurita: veri quattro livelli (Corteccia/Pietra/Ferro/Acciaio) --
    "bark_skin": {
        "nome": "Pelle di Corteccia", "skill_richiesta": "harden_skin", "costo_mana": 10,
        "bersaglio_richiesto": False,
        "descrizione": "Il piu' debole ed economico dei quattro incantesimi di indurimento "
                       "della pelle (Corteccia/Pietra/Ferro/Acciaio), ciascuno piu' difficile "
                       "e costoso del precedente.",
    },
    "stone_skin": {
        "nome": "Pelle di Pietra", "skill_richiesta": "harden_skin", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Il secondo livello di indurimento della pelle, piu' efficace di "
                       "Pelle di Corteccia.",
    },
    "iron_skin": {
        "nome": "Pelle di Ferro", "skill_richiesta": "harden_skin", "costo_mana": 26,
        "bersaglio_richiesto": False,
        "descrizione": "Il terzo livello di indurimento della pelle, piu' efficace di "
                       "Pelle di Pietra.",
    },
    "steel_skin": {
        "nome": "Pelle d'Acciaio", "skill_richiesta": "harden_skin", "costo_mana": 34,
        "bersaglio_richiesto": False,
        "descrizione": "Il quarto e piu' potente livello di indurimento della pelle.",
    },

    # -- Benedizione: le due sorelle di Benedizione (bless) --
    "dark_blessing": {
        "ostile": True,
        "nome": "Benedizione Oscura", "skill_richiesta": "bless", "costo_mana": 6,
        "bersaglio_richiesto": True,
        "descrizione": "Come Benedizione, ma per i non-morti: se lanciata su un vivente "
                       "agisce invece come incantesimo d'attacco, infliggendo danno.",
    },
    "bestow_blessing": {
        "nome": "Elargisci Benedizione", "skill_richiesta": "bless", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Pone una benedizione su una fontana o sorgente: chiunque vi beva "
                       "riceve il beneficio di Benedizione, ma un non-morto che beve subisce "
                       "danno.",
    },

    # -- Frenesia --
    "blade_of_fury": {
        "nome": "Lama della Furia", "skill_richiesta": "frenzy", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Avvolge un'arma in fiamme magiche furiose, aumentandone di molto il "
                       "danno inflitto. Non permanente; c'e' una probabilita' che l'arma "
                       "venga distrutta.",
    },

    # -- Scudo Elementale: i tre scudi-riflesso, le quattro benedizioni di
    # immunita', le quattro parole di resistenza. Solo uno scudo, una
    # benedizione E una parola alla volta (ma una parola e una benedizione
    # insieme si', confermato dalla fonte). --
    "fire_shield": {
        "nome": "Scudo di Fuoco", "skill_richiesta": "elemental_shield", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Crea una barriera elementale che infligge danno a chiunque colpisca "
                       "il lanciatore in combattimento. Solo uno scudo elementale alla volta.",
    },
    "frost_shield": {
        "nome": "Scudo di Gelo", "skill_richiesta": "elemental_shield", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Come Scudo di Fuoco, ma di ghiaccio. Solo uno scudo elementale alla volta.",
    },
    "lightning_shield": {
        "nome": "Scudo di Fulmine", "skill_richiesta": "elemental_shield", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Come Scudo di Fuoco, ma di fulmini. Solo uno scudo elementale alla volta.",
    },
    "blessing_of_cthugha": {
        "nome": "Benedizione di Cthugha", "skill_richiesta": "elemental_shield", "costo_mana": 28,
        "bersaglio_richiesto": False,
        "descrizione": "Concede immunita' al danno di fuoco. Solo una benedizione elementale "
                       "alla volta (ma si puo' combinare con una Parola).",
    },
    "blessing_of_ithaqua": {
        "nome": "Benedizione di Ithaqua", "skill_richiesta": "elemental_shield", "costo_mana": 28,
        "bersaglio_richiesto": False,
        "descrizione": "Concede immunita' al danno da freddo. Solo una benedizione elementale "
                       "alla volta (ma si puo' combinare con una Parola).",
    },
    "blessing_of_yog": {
        "nome": "Benedizione di Yog", "skill_richiesta": "elemental_shield", "costo_mana": 28,
        "bersaglio_richiesto": False,
        "descrizione": "Concede immunita' al danno da fulmine. Solo una benedizione elementale "
                       "alla volta (ma si puo' combinare con una Parola).",
    },
    "blessing_of_tsathoggua": {
        "nome": "Benedizione di Tsathoggua", "skill_richiesta": "elemental_shield", "costo_mana": 28,
        "bersaglio_richiesto": False,
        "descrizione": "Concede immunita' al danno da armi. Solo una benedizione elementale "
                       "alla volta (ma si puo' combinare con una Parola).",
    },
    "word_of_cthugha": {
        "nome": "Parola di Cthugha", "skill_richiesta": "elemental_shield", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Concede resistenza (non immunita' completa) al danno di fuoco. Solo "
                       "una parola elementale alla volta (ma si puo' combinare con una Benedizione).",
    },
    "word_of_ithaqua": {
        "nome": "Parola di Ithaqua", "skill_richiesta": "elemental_shield", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Concede resistenza al danno da freddo. Solo una parola elementale "
                       "alla volta (ma si puo' combinare con una Benedizione).",
    },
    "word_of_yog": {
        "nome": "Parola di Yog", "skill_richiesta": "elemental_shield", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Concede resistenza al danno da fulmine. Solo una parola elementale "
                       "alla volta (ma si puo' combinare con una Benedizione).",
    },
    "word_of_tsathoggua": {
        "nome": "Parola di Tsathoggua", "skill_richiesta": "elemental_shield", "costo_mana": 18,
        "bersaglio_richiesto": False,
        "descrizione": "Concede resistenza al danno da armi. Solo una parola elementale "
                       "alla volta (ma si puo' combinare con una Benedizione).",
    },

    # -- Magia del Soffio: Acido/Fuoco/Gelo/Gas/Fulmine erano gia' stati
    # costruiti in Fase K, sesta tornata (world/magic.py li ha gia' tutti) -
    # qui si aggiunge solo il sesto mancante, Stordente. --
    "stun_breath": {
        "ostile": True,
        "nome": "Soffio Stordente", "skill_richiesta": "stun_breath", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Esala un soffio concussivo che stordisce il bersaglio invece di "
                       "infliggere danno diretto.",
    },

    # -- Via dell'Evocatore (nuova famiglia) --
    "call_pet": {
        "nome": "Richiama Animale", "skill_richiesta": "way_of_the_conjurer", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Richiama al proprio fianco un seguace perso o separato dal lanciatore.",
    },
    "create_figurine": {
        "nome": "Crea Statuetta", "skill_richiesta": "way_of_the_conjurer", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Trasforma un seguace del lanciatore in una piccola statuetta, "
                       "comoda da trasportare. USE sulla statuetta per farlo tornare in vita.",
    },
    "dimensional_pouch": {
        "nome": "Sacca Dimensionale", "skill_richiesta": "way_of_the_conjurer", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Apre uno squarcio nello spazio che da' accesso immediato al "
                       "contenuto del proprio armadietto.",
    },
    "elder_watcher": {
        "ostile": True,
        "nome": "Guardiano degli Antichi", "skill_richiesta": "way_of_the_conjurer", "costo_mana": 30,
        "bersaglio_richiesto": False,
        "descrizione": "Evoca un potente Guardiano a sorvegliare la stanza, che attacchera' "
                       "il primo personaggio che vi entra.",
    },
    "summon_spirit": {
        "nome": "Evoca Spirito", "skill_richiesta": "way_of_the_conjurer", "costo_mana": 25,
        "bersaglio_richiesto": False,
        "descrizione": "Evoca uno spirito magico e senziente al proprio servizio, capace di "
                       "lanciare incantesimi.",
    },
    "lesser_creation": {
        "nome": "Creazione Minore", "skill_richiesta": "way_of_the_conjurer", "costo_mana": 12,
        "bersaglio_richiesto": False, "richiede_testo": True,
        "descrizione": "Forma dal nulla un oggetto a scelta tra una barca, una sacca o un "
                       "attrezzo (una vanga). Nessuno degli oggetti creati e' permanente.",
    },
    "greater_creation": {
        "nome": "Creazione Maggiore", "skill_richiesta": "way_of_the_conjurer", "costo_mana": 25,
        "bersaglio_richiesto": False, "richiede_testo": True,
        "descrizione": "Come Creazione Minore, ma con una lista diversa di oggetti: "
                       "un'incudine, una scaglia d'ambra, delle catene o uno scudo.",
    },

    # -- Magia del Caos (nuova famiglia) --
    "cause_riot": {
        "ostile": True,
        "nome": "Causa Rivolta", "skill_richiesta": "chaos_magic", "costo_mana": 30,
        "bersaglio_richiesto": False,
        "descrizione": "Scatena le forze del caos nell'intera area, facendo impazzire gli "
                       "NPC e rendendoli aggressivamente pericolosi.",
    },
    "change_sex": {
        "nome": "Cambia Sesso", "skill_richiesta": "chaos_magic", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Cambia temporaneamente il genere della vittima.",
    },
    "chaos": {
        "ostile": True,
        "nome": "Caos", "skill_richiesta": "chaos_magic", "costo_mana": 28,
        "bersaglio_richiesto": False,
        "descrizione": "Apre un canale verso le pure forze arcane dell'universo, che "
                       "lacerano il lanciatore e l'intera stanza: facile da lanciare, "
                       "difficilissimo da cui proteggersi. Ferisce chiunque, lanciatore incluso.",
    },
    "entropy": {
        "ostile": True,
        "nome": "Entropia", "skill_richiesta": "chaos_magic", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Avvolge il bersaglio in un campo di energia che danneggia il suo "
                       "equipaggiamento, rendendolo meno utile o del tutto inservibile.",
    },

    # -- Causa Ferite/Paura: gia' costruiti in Fase K, sesta tornata --

    # -- singoli, senza famiglia condivisa --
    "acid_rain": {
        "ostile": True,
        "nome": "Pioggia Acida", "skill_richiesta": "acid_blast", "costo_mana": 30,
        "bersaglio_richiesto": False,
        "descrizione": "Crea un acquazzone acido sull'intera area, danneggiando sia i "
                       "personaggi sia il loro equipaggiamento. Funziona solo se l'area sta "
                       "gia' soffrendo di maltempo (vedi Controlla Meteo).",
    },
    "agony": {
        "ostile": True,
        "nome": "Agonia", "skill_richiesta": "manipulation", "costo_mana": 25,
        "bersaglio_richiesto": True,
        "descrizione": "Un potente incantesimo d'attacco capace di infliggere danno "
                       "significativo a qualunque personaggio si trovi nella stessa area del "
                       "lanciatore, senza bisogno di trovarsi nella stessa stanza.",
    },
    "fear": {
        "ostile": True,
        "nome": "Paura", "skill_richiesta": "manipulation", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Puo' essere lanciato solo su chi e' impegnato in combattimento: se "
                       "riesce, la vittima smette di combattere e fugge in preda al terrore "
                       "(o, se non puo' fuggire, resta comunque incapace di attaccare).",
    },
    "paralysis": {
        "ostile": True,
        "nome": "Paralisi", "skill_richiesta": "manipulation", "costo_mana": 28,
        "bersaglio_richiesto": True,
        "descrizione": "Riduce drasticamente la mobilita' del bersaglio, che potra' solo "
                       "difendersi, mai attaccare.",
    },
    "confuse_hunters": {
        "nome": "Confondi Cacciatori", "skill_richiesta": "invis", "costo_mana": 12,
        "bersaglio_richiesto": False,
        "descrizione": "Nasconde le proprie tracce, impedendo a chiunque di seguirle con "
                       "successo.",
    },
    "consecrate_doll": {
        "ostile": True,
        "nome": "Consacra Bambola", "skill_richiesta": "voodoo", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Combina una bambola voodoo vuota con dei capelli del bersaglio "
                       "(vedi CUT) per creare una bambola personalizzata, che potra' poi "
                       "essere usata con VOODOO STAB/TWIST/TEAR per infliggere dolore e danno "
                       "alla vittima ovunque essa si trovi.",
    },
    "counter_magic": {
        "nome": "Contromagia", "skill_richiesta": "cancellation", "costo_mana": 15,
        # Audit pre-beta: "richiede_testo" era dichiarato ma l'effetto non
        # usa alcun testo (sceglie a caso uno degli effetti attivi, vedi la
        # nota in world/magic.py). Il giocatore era costretto a digitare
        # parole qualsiasi, altrimenti il lancio veniva rifiutato.
        "bersaglio_richiesto": True,
        "descrizione": "Dissolve un singolo effetto magico attivo sul bersaglio (a differenza "
                       "di Cancellazione/Dissolvere la Magia, che li rimuovono tutti insieme).",
    },
    "dispel_room": {
        "nome": "Dissolvi Stanza", "skill_richiesta": "cancellation", "costo_mana": 25,
        "bersaglio_richiesto": False,
        "descrizione": "Tenta di rimuovere gli effetti magici attivi sull'intera stanza "
                       "(verificabili con RAFFECTS).",
    },
    "create_grimoire": {
        "nome": "Crea Grimorio", "skill_richiesta": "spell_casting", "costo_mana": 10,
        "bersaglio_richiesto": False,
        "descrizione": "Crea un libro magico su cui annotare le Discipline che si trovano "
                       "in giro per il mondo (nessun sistema di Discipline esiste ancora in "
                       "questo porting: il grimorio resta per ora un oggetto reale ma di "
                       "scena, pronto per quando verra' costruito). Si riceve automaticamente "
                       "raggiungendo un rating sufficiente in Lancio degli Incantesimi.",
    },
    "curse_of_the_mummy": {
        "ostile": True,
        "nome": "Maledizione della Mummia", "skill_richiesta": "curse", "costo_mana": 28,
        "bersaglio_richiesto": True,
        "descrizione": "Una versione molto piu' potente dell'incantesimo Maledizione.",
    },
    "destroy_portal": {
        "nome": "Distruggi Portale", "skill_richiesta": "portal", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Chiude un singolo portale.",
    },
    "dispel_portals": {
        "nome": "Dissolvi Portali", "skill_richiesta": "portal", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Chiude tutti i portali presenti nella stanza.",
    },
    "divine_portal": {
        "nome": "Portale Divino", "skill_richiesta": "portal", "costo_mana": 35,
        "bersaglio_richiesto": False,
        "descrizione": "Come Portale, ma capace di attraversare i confini di zona per "
                       "raggiungere il bersaglio. Costa 10 punti Fama.",
    },
    "personalize_portal": {
        "nome": "Personalizza Portale", "skill_richiesta": "portal", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Blocca un portale, impedendo a chiunque tranne il lanciatore di "
                       "attraversarlo.",
    },
    "detect_evil": {
        "nome": "Rilevare il Male", "skill_richiesta": "detect_evil", "costo_mana": 5,
        "bersaglio_richiesto": False,
        "descrizione": "Rivela l'allineamento di chi si trova nei dintorni: i personaggi "
                       "malvagi appaiono avvolti da un'aura rossa.",
    },
    "detect_good": {
        "nome": "Rilevare il Bene", "skill_richiesta": "detect_good", "costo_mana": 5,
        "bersaglio_richiesto": False,
        "descrizione": "Rivela l'allineamento di chi si trova nei dintorni: i personaggi "
                       "buoni appaiono avvolti da un'aura verde.",
    },
    "exorcism": {
        "ostile": True,
        "nome": "Esorcismo", "skill_richiesta": "clerical_magic", "costo_mana": 30,
        "bersaglio_richiesto": True,
        "descrizione": "Un potente incantesimo d'attacco pensato per danneggiare "
                       "gravemente i non-morti: evoca una raffica di energia sacra. Non ha "
                       "effetto su un bersaglio vivente.",
    },
    "farsight": {
        "nome": "Vista Lunga", "skill_richiesta": "vision", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Rivela per un istante le uscite delle stanze adiacenti a quella del "
                       "bersaglio, come se lo sguardo si estendesse oltre le mura.",
    },
    "fatigue": {
        "ostile": True,
        "nome": "Fatica", "skill_richiesta": "harm", "costo_mana": 18,
        "bersaglio_richiesto": True,
        "descrizione": "Un incantesimo d'attacco che prosciuga la vitalita' del bersaglio, "
                       "drenandone il movimento e indebolendone la Forza.",
    },
    "flamestrike": {
        "ostile": True,
        "nome": "Colonna di Fuoco", "skill_richiesta": "flamestrike", "costo_mana": 30,
        "bersaglio_richiesto": True,
        "descrizione": "Evoca un'enorme colonna di fiamme intense che si abbatte sulla "
                       "vittima, infliggendo gravi danni da fuoco.",
    },
    "giant_strength": {
        "nome": "Forza del Gigante", "skill_richiesta": "strength", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Una versione piu' potente dell'incantesimo Forza.",
    },
    "godlike_strength": {
        "nome": "Forza Divina", "skill_richiesta": "strength", "costo_mana": 32,
        "bersaglio_richiesto": True,
        "descrizione": "Una versione ancora piu' potente di Forza del Gigante.",
    },
    "heatstrike": {
        "ostile": True,
        "nome": "Colpo di Calore", "skill_richiesta": "fireball", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Dirige un potente getto di calore contro le armi impugnate "
                       "dall'avversario, danneggiandole e con una probabilita' di fargliele "
                       "cadere di mano.",
    },
    "incognito": {
        "nome": "Incognito", "skill_richiesta": "mask_self", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Come Maschera di Se', ma l'NPC scelto come aspetto non deve trovarsi "
                       "nella stessa stanza del lanciatore.",
    },
    "metamorphosis": {
        "nome": "Metamorfosi", "skill_richiesta": "mask_self", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Travestirebbe il lanciatore da oggetto inanimato. La fonte segnala "
                       "esplicitamente questo incantesimo come DISABILITATO (\"THIS SPELL HAS "
                       "BEEN TEMPORARILY DISABLED\") - onorato qui lasciandolo sempre fallire, "
                       "come gia' fatto per Lich.",
    },
    "infravision": {
        "nome": "Infravisione", "skill_richiesta": "vision", "costo_mana": 8,
        "bersaglio_richiesto": True,
        "descrizione": "Permette di vedere nell'oscurita' piu' totale, incluso quella "
                       "provocata dall'incantesimo Oscurita'.",
    },
    "lesser_oracle": {
        "nome": "Oracolo Minore", "skill_richiesta": "clairvoyance", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Evoca uno spirito oracolare che porta al lanciatore un messaggio "
                       "criptico dagli Dei.",
    },
    "mage_light": {
        "nome": "Luce del Mago", "skill_richiesta": "continual_light", "costo_mana": 5,
        "bersaglio_richiesto": False,
        "descrizione": "Raccoglie la luce attorno al lanciatore in una piccola sfera, una "
                       "fonte di luce che dura a lungo (ma non indefinitamente, a differenza "
                       "di Luce Continua).",
    },
    "zap": {
        "ostile": True,
        "nome": "Zap", "skill_richiesta": "magic_missile", "costo_mana": 6,
        "bersaglio_richiesto": True,
        "descrizione": "Il piu' debole della famiglia Zap/Missile Magico/Zappatore Magico: "
                       "scaglia un singolo proiettile di energia viola contro il bersaglio.",
    },
    "magic_zapper": {
        "ostile": True,
        "nome": "Zappatore Magico", "skill_richiesta": "magic_missile", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Il piu' potente della famiglia Zap/Missile Magico/Zappatore Magico: "
                       "scaglia tanti proiettili quanto Missile Magico, ma il doppio piu' "
                       "potenti ciascuno.",
    },
    "magical_campfire": {
        "nome": "Falo' Magico", "skill_richiesta": "spell_casting", "costo_mana": 15,
        "bersaglio_richiesto": False,
        "descrizione": "Crea un falo' arcano che accelera il recupero di chi vi si riposa "
                       "accanto, a differenza del comando CAMP funziona anche nelle stanze "
                       "interne.",
    },
    "mana_shield": {
        "nome": "Scudo di Mana", "skill_richiesta": "shield", "costo_mana": 12,
        "bersaglio_richiesto": False,
        "descrizione": "Avvolge il lanciatore in una sfera di energia arcana che migliora la "
                       "classe armatura e riduce il danno subito: una versione piu' debole ed "
                       "economica di Scudo Magico. Non si possono avere entrambi attivi insieme.",
    },
    "mana_storage": {
        "nome": "Riserva di Mana", "skill_richiesta": "brew", "costo_mana": 0,
        "bersaglio_richiesto": False,
        "descrizione": "Consuma tutto il mana del lanciatore per crearne una piccola pillola "
                       "(circa un quinto del totale), da mangiare in seguito per recuperarlo.",
    },
    "mana_transfer": {
        "nome": "Trasferisci Mana", "skill_richiesta": "spell_casting", "costo_mana": 10,
        "bersaglio_richiesto": True,
        "descrizione": "Trasferisce parte del mana del lanciatore a un altro personaggio. "
                       "Si riceve automaticamente insieme a Lancio degli Incantesimi.",
    },
    "material_anchor": {
        "nome": "Ancora Materiale", "skill_richiesta": "psychic_anchor", "costo_mana": 25,
        "bersaglio_richiesto": False,
        "descrizione": "Come Ancora Psichica, ma crea un fulcro magico che sopravvive a "
                       "morte, disconnessione e persino all'uso di Parola di Richiamo - "
                       "utilizzabile piu' volte. Se sono attive entrambe le ancore, Parola di "
                       "Richiamo cerca prima quella materiale.",
    },
    "power_word": {
        "nome": "Parola di Potere", "skill_richiesta": "spell_casting", "costo_mana": 8,
        "bersaglio_richiesto": False, "richiede_testo": True,
        "descrizione": "Un incantesimo generico il cui effetto dipende dalla parola "
                       "pronunciata e dal contesto esatto (di solito parte di una quest): da "
                       "solo non fa nulla. Nessuna quest di questo porting lo richiede ancora "
                       "- pronto per quando servira'. Si riceve automaticamente insieme a "
                       "Lancio degli Incantesimi.",
    },
    "primal_scream": {
        "ostile": True,
        "nome": "Urlo Primordiale", "skill_richiesta": "voice", "costo_mana": 22,
        "bersaglio_richiesto": True,
        "descrizione": "Usa energia arcana per amplificare la voce del lanciatore in un "
                       "urlo che infligge danno al bersaglio.",
    },
    "refresh": {
        "nome": "Ristoro (incantesimo)", "skill_richiesta": "refresh", "costo_mana": 8,
        "bersaglio_richiesto": True,
        "descrizione": "Ripristina una piccola quantita' di movimento.",
    },
    "restore_limb": {
        "nome": "Ripristina Arto", "skill_richiesta": "restore_limb", "costo_mana": 20,
        "bersaglio_richiesto": True,
        "descrizione": "Ripristina la funzionalita' di un arto ferito. Semplificazione "
                       "dichiarata: questo porting non ha un sistema di danno separato per "
                       "arto, quindi l'effetto qui e' una guarigione aggiuntiva.",
    },
    "silence": {
        "ostile": True,
        "nome": "Silenzio", "skill_richiesta": "mute", "costo_mana": 20,
        "bersaglio_richiesto": False,
        "descrizione": "Come Ammutolire, ma per l'intera stanza: chiunque vi si trovi ne "
                       "soffre gli effetti finche' non se ne va.",
    },
    "slow": {
        "ostile": True,
        "nome": "Lentezza", "skill_richiesta": "haste", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "L'opposto di Fretta: riduce temporaneamente la Destrezza del "
                       "bersaglio, rallentandolo in combattimento. Considerato un incantesimo "
                       "d'attacco.",
    },
    "step_lightly": {
        "nome": "Passo Leggero", "skill_richiesta": "refresh", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Come Ristoro, ma ripristina una quantita' di movimento molto maggiore.",
    },
    "true_invis": {
        "nome": "Vera Invisibilita'", "skill_richiesta": "true_invis", "costo_mana": 40,
        "bersaglio_richiesto": False,
        "descrizione": "Una versione molto piu' potente di Invisibilita': dura di piu', "
                       "resta attiva anche entrando in combattimento, e nasconde il "
                       "lanciatore anche da chi puo' Rilevare l'Invisibile. Puo' essere "
                       "lanciata solo su se stessi.",
    },
    "true_sight": {
        "nome": "Vera Vista", "skill_richiesta": "detect_magic", "costo_mana": 15,
        "bersaglio_richiesto": True,
        "descrizione": "Permette di vedere attraverso gli effetti di Maschera di Se'/"
                       "Incognito, rivelando la vera identita' di chi li ha usati.",
    },
}


def nome_incantesimo(spell_id):
    entry = SPELLS.get(spell_id)
    return entry["nome"] if entry else spell_id
