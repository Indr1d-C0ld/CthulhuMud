"""
Sistema di quest (Fase K, prima tornata).

Confermato dalla fonte (helps/quest.txt): il comando QUEST mostra le
quest in corso con la tappa attuale, e "not every quest ends with a
deed, and not every deed must be obtained through a quest" - qui, per
questa prima tornata, costruiamo l'infrastruttura generica a tappe
(quest_progress sul personaggio, vedi typeclasses/characters.py) e UNA
quest completa e giocabile: "Il Risveglio", che assegna deed_59
("Qualcosa si e' risvegliato dentro di te!" - titolo REALE dalla
fonte, vedi world/imprese.py), l'impresa richiesta da ben 8 delle 39
professioni avanzate - tutte quelle magiche/occulte (Druido,
Camminatore Spettrale, Mago, Mentalista, Negromante, Maestro
dell'Occulto, Occultista, Evocatore di Spiriti - vedi
world/professions_avanzate.py) - quindi la singola impresa con il
maggior numero di professioni sbloccate a parita' di lavoro.

La fonte conferma CHE questa impresa esiste e il suo titolo esatto, ma
non descrive in nessuna pagina la quest che porta a ottenerla: le
tappe qui sotto sono percio' materiale originale, costruito nello
spirito occulto/cosmico dell'ambientazione - esattamente la stessa
situazione (e la stessa soluzione) gia' affrontata per il bestiario
quando la fonte non forniva un riferimento diretto (vedi
world/mostri.py). La quest riusa deliberatamente meccaniche gia'
esistenti (skill Occult, sanity, la posizione del vecchio cimitero di
Arkham con il suo ghoul residente) invece di introdurne di nuove.

Fase K, seconda tornata: le altre 17 imprese hanno ora tutte una
quest. A differenza del Risveglio (un vero percorso in due tappe),
queste sono "achievement" a tappa singola - coerente con la fonte
stessa: "not every mission or puzzle is coded as an official quest,
especially if it is a relatively easy or brief quest to complete".
QUEST COMPLETE <id> verifica i requisiti e assegna l'impresa in un
solo passo, senza bisogno di un QUEST START separato. Ogni requisito
riusa meccaniche gia' esistenti (skill, allineamento, luogo, clan,
oggetti forgiati, o uno dei tre nuovi contatori permanenti aggiunti
apposta: db.mostri_uccisi in typeclasses/npcs.py, db.omicidi_pk in
world/combat.py, db.ha_mindtransferito in
commands/cthulhu_yithian.py) invece di introdurre nuovi sistemi. Come
per il Risveglio, la fonte conferma titolo ed esistenza di ciascuna
impresa (vedi world/imprese.py) ma non descrive mai la prova che porta
a ottenerla: le condizioni sotto sono percio' materiale originale,
scelto per calzare il tema del titolo reale e per sfruttare luoghi/
meccaniche gia' presenti nel porting invece di inventarne di nuovi.
"""

# {quest_id: {"deed": ..., "requisiti": {...}, "messaggio_ok": ...}}
QUESTS_SEMPLICI = {
    "laurea": {
        "deed": "deed_56",
        "requisiti": {
            "skill": {"education": 60},
            "stanza_tag": ("building_miskatonic_university", "arkham_building"),
        },
        "messaggio_ok": (
            "Davanti al cancello in ferro battuto dell'universita', qualcosa "
            "dentro di te si allinea: anni di studio trovano finalmente una "
            "forma compiuta. Sei ora un laureato/a della Miskatonic University."
        ),
    },
    "marduk": {
        "deed": "deed_57",
        "requisiti": {
            "skill": {"theology": 40},
            "allineamento_max": -400,
            "stanza_tag": ("cairo_sphinx", "cairo_room"),
        },
        "messaggio_ok": (
            "Davanti al volto consumato dalla Sfinge, pronunci un giuramento "
            "che nessun dio umano vorrebbe sentire. Marduk accetta la tua "
            "devozione."
        ),
    },
    "capolavoro": {
        "deed": "deed_60",
        "requisiti": {"oggetto_forgiato_min": 8},
        "messaggio_ok": (
            "L'oggetto che tieni tra le mani non e' solo forgiato: e' un "
            "capolavoro, e lo sai. Il tuo nome tra gli artigiani di Arkham non "
            "sara' piu' lo stesso."
        ),
    },
    "ammiraglio": {
        "deed": "deed_81",
        "requisiti": {
            "livello_min": 20,
            "stanza_tag": ("sub_9", "submarine_room"),
        },
        "messaggio_ok": (
            "Nella Torretta di Comando del relitto, tra le ossa di un "
            "equipaggio che non torno' mai a casa, comprendi cosa significhi "
            "davvero comandare. Un Ammiraglio, ovunque sia, prende nota del "
            "tuo valore."
        ),
    },
    "primo_caso": {
        "deed": "deed_82",
        "requisiti": {
            "skill": {"streetwise": 40},
            "stanza_tag": ("building_police_station", "arkham_building"),
        },
        "messaggio_ok": (
            "Deponi le tue conclusioni sulla scrivania del tenente di turno, "
            "che per una volta alza lo sguardo con vero interesse. Hai "
            "risolto il tuo primo caso."
        ),
    },
    "oltre_i_confini": {
        "deed": "deed_83",
        "requisiti": {"flag_true": "ha_mindtransferito"},
        "messaggio_ok": (
            "Hai gia' abitato una mente che non era la tua. Qualcosa in te "
            "sa ora, con certezza, che i confini dell'esperienza umana sono "
            "soltanto un'illusione di comodo."
        ),
    },
    "druido": {
        "deed": "deed_84",
        "requisiti": {
            "skill": {"biology": 40},
            "stanza_tag": ("zv_tree_of_souls", "zoogvillage_room"),
        },
        "messaggio_ok": (
            "Sotto i rami contorti dell'Albero delle Anime, lasci la tua "
            "offerta insieme a quelle degli Zoog. Qualcosa nel bosco, per la "
            "prima volta, ti riconosce come uno dei suoi."
        ),
    },
    "avatar_del_sole": {
        "deed": "deed_85",
        "requisiti": {
            "allineamento_min": 700,
            "stanza_tag": ("building_st_genisius", "arkham_building"),
        },
        "messaggio_ok": (
            "La luce che filtra dalle vetrate policrome della basilica ti "
            "avvolge per un istante piu' a lungo del dovuto. Sei diventato/a "
            "un Avatar del Sole."
        ),
    },
    "avatar_di_dagon": {
        "deed": "deed_86",
        "requisiti": {
            "allineamento_max": -700,
            "stanza_tag": ("cairo_docks", "cairo_room"),
        },
        "messaggio_ok": (
            "Sulle banchine fangose del Nilo, qualcosa di antico e sommerso "
            "riconosce la tua devozione. Sei diventato/a un Avatar di Dagon."
        ),
    },
    "sacerdote_yog_sothoth": {
        "deed": "deed_1309",
        "requisiti": {
            "skill": {"occult": 70},
            "stanza_tag": ("sub_8", "submarine_room"),
        },
        "messaggio_ok": (
            "Nello snodo dove ogni corridoio del relitto si dirama, comprendi "
            "che ogni porta, ogni soglia, ogni angolo e' in realta' la STESSA "
            "soglia. Yog-Sothoth e' il Cancello e la Chiave, e tu ne sei ora "
            "sacerdote/essa."
        ),
    },
    "sacerdote_dagon": {
        "deed": "deed_1319",
        "requisiti": {"clan": ("esoteric_order_of_dagon", 2)},
        "messaggio_ok": (
            "L'Ordine Esoterico di Dagon ti riconosce non piu' come semplice "
            "membro, ma come sacerdote/essa del suo culto sommerso."
        ),
    },
    "sacerdote_shub_niggurath": {
        "deed": "deed_1329",
        "requisiti": {
            "skill": {"biology": 60},
            "stanza_tag": ("dlo_verso_bosco", "dreamlands_overworld"),
        },
        "messaggio_ok": (
            "Al margine del Bosco Incantato, tra il chiacchiericcio distante "
            "degli Zoog, senti la presenza informe della Capra Nera dei "
            "Boschi con i Suoi Mille Cuccioli. Sei ora sacerdote/essa di "
            "Shub-Niggurath."
        ),
    },
    "sacrificio_thanatos": {
        "deed": "deed_3796",
        "requisiti": {"flag_min": ("omicidi_pk", 1)},
        "messaggio_ok": (
            "Il sangue versato con le tue mani non e' passato inosservato. "
            "Thanatos accetta il tuo sacrificio."
        ),
    },
    "sentiero_degli_eletti": {
        "deed": "deed_4316",
        "requisiti": {
            "livello_min": 25,
            "skill": {"occult": 50},
        },
        "messaggio_ok": (
            "Non c'e' un luogo, ne' un rito preciso, per il Sentiero degli "
            "Eletti - solo il peso accumulato di cio' che hai imparato e "
            "affrontato. Lo hai completato."
        ),
    },
    "seguace_di_bast": {
        "deed": "deed_9004",
        "requisiti": {
            "skill": {"occult": 20},
            "stanza_tag": ("street_calico_cross", "ulthar_room"),
        },
        "messaggio_ok": (
            "Al crepuscolo, circondato/a da decine di gatti maculati riuniti "
            "su Calico Cross, senti su di te lo sguardo antico e felino di "
            "Bast."
        ),
    },
    "valore_in_combattimento": {
        "deed": "deed_9061",
        "requisiti": {"flag_min": ("mostri_uccisi", 5)},
        "messaggio_ok": (
            "Le cicatrici e i ricordi di ogni scontro affrontato parlano da "
            "soli. Ti sei dimostrato/a valoroso/a in combattimento."
        ),
    },
    "cavaliere_di_ulthar": {
        "deed": "deed_9071",
        "requisiti": {
            "allineamento_min": 500,
            "stanza_tag": ("ulthar_temple_interior", "ulthar_room"),
        },
        "messaggio_ok": (
            "Tra le statue di gatti accovacciati del Grande Tempio, senti il "
            "peso di un giuramento cavalleresco posarsi sulle tue spalle. Sei "
            "un Cavaliere di Ulthar!"
        ),
    },
}


def _verifica_requisiti(personaggio, requisiti):
    """Ritorna (ok: bool, motivi_mancanti: list[str])."""
    mancanti = []

    for skill_id, soglia in requisiti.get("skill", {}).items():
        rating = personaggio.skill_rating(skill_id)
        if rating < soglia:
            from world.skills import nome_skill
            mancanti.append(f"{nome_skill(skill_id)} {soglia}% (hai {rating}%)")

    if "livello_min" in requisiti:
        livello = personaggio.livello_personaggio() if hasattr(personaggio, "livello_personaggio") else 0
        if livello < requisiti["livello_min"]:
            mancanti.append(f"livello {requisiti['livello_min']} (hai {livello})")

    if "allineamento_min" in requisiti:
        if (personaggio.db.alignment or 0) < requisiti["allineamento_min"]:
            mancanti.append(f"un allineamento di almeno {requisiti['allineamento_min']}")

    if "allineamento_max" in requisiti:
        if (personaggio.db.alignment or 0) > requisiti["allineamento_max"]:
            mancanti.append(f"un allineamento non superiore a {requisiti['allineamento_max']}")

    if "stanza_tag" in requisiti:
        tag, categoria = requisiti["stanza_tag"]
        stanza = personaggio.location
        if not stanza or not stanza.tags.get(tag, category=categoria):
            mancanti.append("trovarti nel luogo giusto")

    if "clan" in requisiti:
        clan_id, rango_minimo = requisiti["clan"]
        from world.societies import ha_rango
        if not ha_rango(personaggio, clan_id, rango_minimo):
            mancanti.append("appartenere al clan giusto, con il rango adeguato")

    if "flag_min" in requisiti:
        campo, soglia = requisiti["flag_min"]
        valore = getattr(personaggio.db, campo, 0) or 0
        if valore < soglia:
            mancanti.append("non hai ancora fatto abbastanza per dimostrartelo")

    if "flag_true" in requisiti:
        campo = requisiti["flag_true"]
        if not getattr(personaggio.db, campo, False):
            mancanti.append("non hai ancora vissuto l'esperienza necessaria")

    if "oggetto_forgiato_min" in requisiti:
        soglia = requisiti["oggetto_forgiato_min"]
        trovato = any(
            (oggetto.db.bonus_danno or 0) >= soglia or (oggetto.db.classe_armatura or 0) >= soglia
            for oggetto in personaggio.contents
        )
        if not trovato:
            mancanti.append("non possiedi ancora un capolavoro di fattura sufficiente")

    return not mancanti, mancanti


def completa_quest_semplice(personaggio, quest_id):
    """QUEST COMPLETE <id> per una delle QUESTS_SEMPLICI. Ritorna
    (ok, messaggio)."""
    voce = QUESTS_SEMPLICI.get(quest_id)
    if not voce:
        return False, "Quest sconosciuta."
    if voce["deed"] in (personaggio.db.imprese or set()):
        return False, "Hai gia' completato questa impresa."
    ok, mancanti = _verifica_requisiti(personaggio, voce["requisiti"])
    if not ok:
        return False, "Non sei ancora pronto/a: " + "; ".join(mancanti) + "."
    from world.imprese import assegna_impresa
    assegna_impresa(personaggio, voce["deed"])
    return True, voce["messaggio_ok"]

SOGLIA_OCCULT_INIZIO = 20
SOGLIA_SANITY_COMPLETAMENTO = 70

QUEST_RISVEGLIO_ID = "risveglio"
QUEST_RISVEGLIO_DEED = "deed_59"
QUEST_RISVEGLIO_TAG = "building_olde_towne_cemetery"
QUEST_RISVEGLIO_TAG_CATEGORY = "arkham_building"


def inizia_risveglio(personaggio):
    """QUEST START RISVEGLIO. Ritorna (ok, messaggio)."""
    if QUEST_RISVEGLIO_DEED in (personaggio.db.imprese or set()):
        return False, "Hai gia' completato questa impresa."
    progresso = personaggio.db.quest_progress or {}
    if QUEST_RISVEGLIO_ID in progresso:
        return False, "Hai gia' iniziato questa quest."
    if personaggio.skill_rating("occult") < SOGLIA_OCCULT_INIZIO:
        return False, (
            "Non senti ancora nulla di insolito dentro di te. Forse "
            "approfondire i tuoi studi occulti ti aiuterebbe a percepirlo."
        )
    progresso[QUEST_RISVEGLIO_ID] = 1
    personaggio.db.quest_progress = progresso
    return True, (
        "Una vertigine improvvisa ti coglie, come se qualcosa di sopito "
        "avesse socchiuso un occhio dentro di te. Senti che il velo tra i "
        "mondi si assottiglia - ma solo dove i confini della citta' vecchia "
        "sfumano nell'ombra, tra le tombe piu' antiche, potresti scoprire "
        "davvero cosa si e' destato."
    )


def completa_risveglio(personaggio):
    """QUEST COMPLETE RISVEGLIO. Ritorna (ok, messaggio)."""
    progresso = personaggio.db.quest_progress or {}
    if progresso.get(QUEST_RISVEGLIO_ID) != 1:
        return False, "Non hai ancora iniziato questa quest (o l'hai gia' completata)."
    stanza = personaggio.location
    if not stanza or not stanza.tags.get(QUEST_RISVEGLIO_TAG, category=QUEST_RISVEGLIO_TAG_CATEGORY):
        return False, "Non e' qui che troverai le risposte che cerchi."
    if (personaggio.db.sanity if personaggio.db.sanity is not None else 105) > SOGLIA_SANITY_COMPLETAMENTO:
        return False, (
            "Ti fermi tra le lapidi, in attesa. Ma la tua mente e' ancora "
            "troppo salda, troppo integra: qualunque cosa si sia risvegliata "
            "in te non e' ancora pronta a mostrarsi. Forse dovrai prima "
            "guardare negli occhi qualcosa che nessuno dovrebbe vedere."
        )
    from world.imprese import assegna_impresa
    assegna_impresa(personaggio, QUEST_RISVEGLIO_DEED)
    del progresso[QUEST_RISVEGLIO_ID]
    personaggio.db.quest_progress = progresso
    return True, (
        "Tra le lapidi consumate dal tempo, per un solo istante, senti gli "
        "occhi di qualcosa di antico posarsi su di te - e ritrarsi, quasi "
        "soddisfatto. Qualcosa si e' risvegliato dentro di te, e non "
        "tornera' piu' a dormire."
    )
