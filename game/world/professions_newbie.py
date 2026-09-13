"""
Registro delle 16 professioni newbie di CthulhuMUD ITA Redux (il sito
originale dichiara "15" in info_newbieprofs.txt, ma la sua stessa
tabella ne elenca 16 - refuso del sito, non nostro: verificato
contando le righe della tabella "PROFESSION/RACE/STARTING LOCATION/
PRIMARY ATTRIBUTE").

Ogni voce riproduce fedelmente i dati catalogati dal sito originale
(vedi il Dossier Miskatonic): razza compatibile, luogo di partenza,
modificatori ai 7 attributi (aggiunti a un tiro di base 3d6, scelta di
design non documentata dal sito originale) e le skill assegnate per
livello di professione (livello 0 = skill disponibili subito a rating 0,
pronte per essere allenate con PRACTICE).

"start_tag" punta alla stanza di RECALL creata da world/rooms_newbie.py.
"""

NEWBIE_PROFESSIONS = {
    "apprendista": {
        "nome_m": "Apprendista", "nome_f": "Apprendista",
        "razza": "human",
        "luogo": "Universita' Miskatonic, Arkham",
        "start_tag": "arkham_miskatonic",
        "descrizione": (
            "Un giovane che lavora e studia sotto un maestro di un mestiere "
            "particolare. Background misto tra skill pratiche ed educative."
        ),
        "attributi": {"str": 3, "int": 2, "wis": 3, "dex": 3, "con": 2, "luck": 2, "cha": 2,
                      "primario": "dex"},
        "skill_per_livello": {
            0: ["arkham", "dodge", "english", "hand_to_hand", "mace", "recall", "shield_block"],
            1: ["education", "streetwise"],
            3: ["haggle", "hide"],
            4: ["climb", "search"],
            5: ["accounting", "sneak"],
            6: ["german", "swim"],
            7: ["detection", "world_affairs"],
            8: ["pick_lock"],
            9: ["physics"],
            10: ["chemistry"],
            13: ["forging"],
        },
    },
    "cacciatore_di_cervelli": {
        "nome_m": "Cacciatore di Cervelli", "nome_f": "Cacciatrice di Cervelli",
        "razza": "mi_go",
        "luogo": "Nave Madre della Forza di Spedizione Mi-Go",
        "start_tag": "migo_mothership",
        "descrizione": (
            "Giovane esploratore Mi-Go incaricato di trovare cervelli umani "
            "freschi per scopi sperimentali. Addestrato nel travestimento e "
            "nella chirurgia cerebrale."
        ),
        "attributi": {"str": 2, "int": 3, "wis": 2, "dex": 2, "con": 2, "luck": 2, "cha": 2,
                      "primario": "int"},
        "skill_per_livello": {
            0: ["chinese", "dagger", "dodge", "english", "hand_to_hand", "recall", "yuggoth"],
            1: ["education", "spell_casting"],
            2: ["arabic"],
            3: ["japanese"],
            4: ["occult", "spear"],
            5: ["mask_self", "meditation"],
            6: ["astronomy", "scrolls"],
            7: ["ancient_history", "biology"],
            8: ["anthropology", "armor", "geology"],
            9: ["ancient_geography", "cure_light", "fast_healing"],
            10: ["staves", "wands"],
            12: ["bandage"],
            15: ["handgun"],
            25: ["sound_crystal"],
        },
    },
    "cadetto": {
        "nome_m": "Cadetto", "nome_f": "Cadetta",
        "razza": "human",
        "luogo": "Universita' Miskatonic, Arkham",
        "start_tag": "arkham_miskatonic",
        "descrizione": (
            "Un giovane in addestramento per le forze armate o le forze "
            "dell'ordine. Skill fisiche senza trascurare l'educazione."
        ),
        "attributi": {"str": 3, "int": 2, "wis": 2, "dex": 2, "con": 3, "luck": 2, "cha": 2,
                      "primario": "con"},
        "skill_per_livello": {
            0: ["arkham", "dodge", "english", "hand_to_hand", "mace", "recall", "shield_block"],
            1: ["education", "parry", "streetwise"],
            3: ["search", "swim"],
            4: ["brawling", "kick"],
            5: ["climb", "dagger", "hide"],
            6: ["german", "sneak"],
            7: ["handgun", "trip"],
            8: ["martial_arts"],
            9: ["second_attack"],
            10: ["gun"],
            11: ["detection"],
            12: ["disarm"],
            13: ["enhanced_damage"],
            14: ["riding"],
        },
    },
    "cacciatore_di_molluschi": {
        "nome_m": "Cacciatore di Molluschi", "nome_f": "Cacciatrice di Molluschi",
        "razza": "deep_one",
        "luogo": "Nido dei Profondi, Y'ha-nthlei",
        "start_tag": "yhanthlei",
        "descrizione": (
            "Giovane Profondo in addestramento per diventare un forte "
            "guerriero. Skill fisiche."
        ),
        "attributi": {"str": 3, "int": 1, "wis": 2, "dex": 2, "con": 3, "luck": 2, "cha": 1,
                      "primario": "str"},
        "skill_per_livello": {
            0: ["atlantean", "dagger", "dodge", "english", "hand_to_hand", "innsmouth", "recall", "swim"],
            1: ["education", "streetwise"],
            3: ["search", "spear"],
            4: ["brawling", "kick"],
            5: ["climb", "hide", "mace"],
            6: ["shield_block", "sneak"],
            7: ["parry", "sword"],
            8: ["martial_arts"],
            9: ["second_attack", "trip"],
            10: ["disarm"],
            12: ["enhanced_damage"],
            14: ["strong_grip"],
        },
    },
    "studentessa_conventuale": {
        "nome_m": "Studente Conventuale", "nome_f": "Studentessa Conventuale",
        "razza": "human",
        "luogo": "Universita' Miskatonic, Arkham",
        "start_tag": "arkham_miskatonic",
        "descrizione": (
            "Giovane che studia alla Miskatonic University con un'educazione "
            "precedente ricevuta in convento. Skill oscure ed esoteriche."
        ),
        "attributi": {"str": 2, "int": 2, "wis": 3, "dex": 2, "con": 3, "luck": 3, "cha": 1,
                      "primario": "wis"},
        "skill_per_livello": {
            0: ["arkham", "dodge", "english", "hand_to_hand", "mace", "recall"],
            1: ["education", "streetwise"],
            2: ["latin"],
            3: ["french", "german"],
            4: ["theology"],
            5: ["modern_history", "world_geography"],
            6: ["meditation", "old_english"],
            7: ["greek", "scrolls"],
            8: ["astronomy", "occult"],
            9: ["ancient_geography", "ancient_history"],
            10: ["staves", "wands"],
            15: ["debating"],
        },
    },
    "teppista": {
        "nome_m": "Teppista", "nome_f": "Teppista",
        "razza": "human",
        "luogo": "Universita' Miskatonic, Arkham",
        "start_tag": "arkham_miskatonic",
        "descrizione": (
            "Giovane cresciuto per strada, tra bande e ambienti criminali. "
            "Buon background di skill fisiche."
        ),
        "attributi": {"str": 3, "int": 1, "wis": 2, "dex": 3, "con": 3, "luck": 2, "cha": 1,
                      "primario": "str"},
        "skill_per_livello": {
            0: ["arkham", "dodge", "english", "hand_to_hand", "mace", "recall"],
            1: ["education", "streetwise"],
            2: ["climb", "haggle"],
            3: ["search", "swim"],
            4: ["dagger", "kick"],
            5: ["dirt_kicking", "hide", "steal"],
            6: ["german", "sneak"],
            7: ["backstab", "parry"],
            8: ["second_attack"],
            9: ["handgun"],
            10: ["circle"],
            15: ["strangle"],
        },
    },
    "iniziato": {
        "nome_m": "Iniziato", "nome_f": "Iniziata",
        "razza": "human",
        "luogo": "Tempio di Ulthar, Dreamlands",
        "start_tag": "ulthar_temple",
        "descrizione": (
            "Giovane che studia le arti arcane nella citta' di Ulthar. "
            "Skill oscure ed esoteriche."
        ),
        "attributi": {"str": 2, "int": 3, "wis": 3, "dex": 2, "con": 1, "luck": 1, "cha": 2,
                      "primario": "wis"},
        "skill_per_livello": {
            0: ["dodge", "english", "hand_to_hand", "mace", "recall", "ulthar"],
            1: ["education", "streetwise"],
            2: ["latin"],
            3: ["french", "spanish"],
            4: ["spear", "theology"],
            5: ["greek", "meditation"],
            6: ["scrolls"],
            7: ["occult"],
            8: ["astronomy"],
            9: ["ancient_geography", "ancient_history"],
            10: ["staves", "wands"],
            15: ["debating"],
        },
    },
    "maghetto": {
        "nome_m": "Maghetto", "nome_f": "Maghetta",
        "razza": "zoog",
        "luogo": "Villaggio degli Zoog, Bosco Incantato, Dreamlands",
        "start_tag": "zoog_village",
        "descrizione": (
            "Giovane Zoog che studia le arti arcane. Skill oscure ed "
            "esoteriche."
        ),
        "attributi": {"str": 1, "int": 3, "wis": 2, "dex": 3, "con": 2, "luck": 4, "cha": 1,
                      "primario": "int"},
        "skill_per_livello": {
            0: ["cthonic", "dagger", "dodge", "dreamlands", "english", "hand_to_hand", "recall"],
            1: ["education", "streetwise"],
            2: ["latin"],
            3: ["spanish"],
            4: ["mace", "occult"],
            5: ["greek", "meditation"],
            6: ["climb", "scrolls"],
            7: ["hide", "theology"],
            8: ["astronomy", "detect_evil", "spell_casting"],
            9: ["ancient_geography", "ancient_history", "detect_good"],
            10: ["refresh", "staves", "wands"],
        },
    },
    "scienziato_migo": {
        "nome_m": "Scienziato Mi-Go", "nome_f": "Scienziata Mi-Go",
        "razza": "mi_go",
        "luogo": "Struttura di Addestramento Primario, Yuggoth",
        "start_tag": "yuggoth_training",
        "descrizione": (
            "Giovane Mi-Go che preferisce restare sul pianeta natale invece "
            "di cacciare cervelli nelle aree coloniali. Fornisce le basi per "
            "diventare chirurgo cerebrale."
        ),
        "attributi": {"str": 1, "int": 4, "wis": 2, "dex": 2, "con": 1, "luck": 2, "cha": 3,
                      "primario": "int"},
        "skill_per_livello": {
            0: ["chinese", "dagger", "dodge", "english", "hand_to_hand", "recall", "yuggoth"],
            1: ["education", "spell_casting"],
            2: ["arabic"],
            3: ["japanese", "occult"],
            4: ["biology", "meditation"],
            5: ["cthonic", "dreaming"],
            6: ["astronomy", "scrolls"],
            7: ["ancient_history", "bandage", "bless"],
            8: ["anthropology", "geology"],
            9: ["ancient_geography", "cure_light", "music"],
            10: ["mask_self", "staves", "wands"],
            11: ["theology"],
            12: ["lore"],
            14: ["detect_magic"],
            15: ["mayan"],
            16: ["surgery"],
            18: ["sound_crystal"],
            20: ["shocking_grasp"],
        },
    },
    "scudiero": {
        "nome_m": "Scudiero", "nome_f": "Scudiera",
        "razza": "human",
        "luogo": "Tempio di Ulthar, Dreamlands",
        "start_tag": "ulthar_temple",
        "descrizione": (
            "Giovane in addestramento per diventare un guerriero nella citta' "
            "di Ulthar. Skill fisiche."
        ),
        "attributi": {"str": 2, "int": 2, "wis": 2, "dex": 2, "con": 3, "luck": 1, "cha": 3,
                      "primario": "con"},
        "skill_per_livello": {
            0: ["dodge", "english", "hand_to_hand", "mace", "recall", "ulthar"],
            1: ["education", "shield_block", "streetwise"],
            2: ["swim"],
            3: ["dagger", "search"],
            4: ["kick", "martial_arts"],
            5: ["climb", "hide", "spear"],
            6: ["sneak", "spanish"],
            7: ["parry", "sword"],
            8: ["second_attack", "trip"],
            9: ["disarm"],
            10: ["enhanced_damage"],
            12: ["riding"],
            15: ["forging"],
            18: ["strong_grip"],
        },
    },
    "melma": {
        "nome_m": "Melma", "nome_f": "Melma",
        "razza": "shuggoth",
        "luogo": "Nido dei Profondi, Y'ha-nthlei",
        "start_tag": "yhanthlei",
        "descrizione": (
            "Gli Shoggoth Melma sono ex servitori degli Old Ones divenuti "
            "indipendenti; inglobano vittime stordite per assorbirne skill "
            "e abilita'."
        ),
        "attributi": {"str": 3, "int": 2, "wis": 1, "dex": 2, "con": 4, "luck": 1, "cha": 1,
                      "primario": "con"},
        "skill_per_livello": {
            0: ["atlantean", "dodge", "english", "hand_to_hand", "recall"],
            3: ["trip"],
            4: ["bash"],
            5: ["fast_healing"],
            6: ["second_attack"],
            8: ["enhanced_damage"],
            10: ["crush"],
            12: ["disarm"],
            15: ["berserk"],
            17: ["martial_arts"],
            20: ["parry"],
            25: ["third_attack"],
            30: ["ultra_damage"],
            40: ["lethal_damage"],
            45: ["fourth_attack"],
            55: ["form_mastery"],
            70: ["black_belt"],
        },
    },
    "tentacolo_di_dagon": {
        "nome_m": "Tentacolo di Dagon", "nome_f": "Tentacolo di Dagon",
        "razza": "deep_one",
        "luogo": "Nido dei Profondi, Y'ha-nthlei",
        "start_tag": "yhanthlei",
        "descrizione": "Giovane Profondo che studia per diventare Sacerdote di Dagon.",
        "attributi": {"str": 2, "int": 2, "wis": 3, "dex": 2, "con": 3, "luck": 2, "cha": 2,
                      "primario": "wis"},
        "skill_per_livello": {
            0: ["atlantean", "dagger", "dodge", "english", "hand_to_hand", "innsmouth", "recall"],
            1: ["education", "streetwise"],
            2: ["latin"],
            3: ["german"],
            4: ["spear", "theology"],
            5: ["greek", "meditation"],
            6: ["scrolls"],
            7: ["occult"],
            8: ["astronomy"],
            9: ["ancient_geography", "ancient_history"],
            10: ["staves", "wands"],
            15: ["debating"],
        },
    },
    "universitario": {
        "nome_m": "Universitario", "nome_f": "Universitaria",
        "razza": "human",
        "luogo": "Universita' Miskatonic, Arkham",
        "start_tag": "arkham_miskatonic",
        "descrizione": (
            "Giovane che studia alla Miskatonic University. Buon background "
            "generalista in svariate skill."
        ),
        "attributi": {"str": 2, "int": 3, "wis": 2, "dex": 2, "con": 3, "luck": 2, "cha": 2,
                      "primario": "int"},
        "skill_per_livello": {
            0: ["arkham", "dagger", "dodge", "english", "german", "hand_to_hand", "recall"],
            1: ["education", "streetwise"],
            2: ["kick"],
            3: ["french"],
            4: ["modern_history", "world_geography"],
            5: ["italian", "spanish"],
            6: ["biology", "world_affairs"],
            7: ["chemistry", "physics", "rescue"],
            8: ["latin"],
            9: ["occult", "scrolls"],
            10: ["hide"],
            12: ["riding"],
            15: ["debating"],
        },
    },
    "monello": {
        "nome_m": "Monello", "nome_f": "Monella",
        "razza": "human",
        "luogo": "Riformatorio Minorile, Dylath-Leen, Dreamlands",
        "start_tag": "dylath_reformatory",
        "descrizione": (
            "Giovane cresciuto per strada nella citta' onirica di "
            "Dylath-Leen, tra bande e criminalita'. Skill fisiche."
        ),
        "attributi": {"str": 3, "int": 1, "wis": 1, "dex": 3, "con": 3, "luck": 2, "cha": 1,
                      "primario": "str"},
        "skill_per_livello": {
            0: ["english", "dagger", "dodge", "dylath", "hand_to_hand", "recall"],
            1: ["education", "streetwise"],
            2: ["climb", "haggle"],
            3: ["hide", "swim"],
            4: ["kick", "mace"],
            5: ["search", "steal"],
            6: ["sneak", "spanish"],
            7: ["parry", "spear"],
            8: ["backstab", "dirt_kicking"],
            9: ["second_attack"],
            10: ["circle"],
            12: ["detection"],
            14: ["gambling"],
            16: ["tame"],
            18: ["strangle"],
        },
    },
    "esploratore_yithiano": {
        "nome_m": "Esploratore Yithiano", "nome_f": "Esploratrice Yithiana",
        "razza": "yithian",
        "luogo": "Grande Biblioteca Yithiana",
        "start_tag": "yithian_library",
        "descrizione": (
            "Membro della Grande Razza di Yith che aspira a scoprire i "
            "segreti dell'universo. Forte background scientifico. "
            "Professione con progressione molto lunga (fino al 60esimo "
            "livello)."
        ),
        "attributi": {"str": 2, "int": 3, "wis": 3, "dex": 2, "con": 1, "luck": 1, "cha": 2,
                      "primario": "wis"},
        "skill_per_livello": {
            0: ["dodge", "english", "hand_to_hand", "recall", "stygian"],
            1: ["arabic"],
            2: ["education"],
            3: ["chinese", "dagger", "japanese"],
            4: ["ancient_history"],
            5: ["occult"],
            6: ["astronomy", "latin"],
            7: ["spell_casting"],
            8: ["biology", "greek", "hebrew"],
            9: ["anthropology", "scrolls"],
            10: ["old_english"],
            11: ["geology"],
            12: ["meditation"],
            13: ["chemistry"],
            14: ["ancient_geography"],
            16: ["hieroglyphics"],
            17: ["physics"],
            18: ["german"],
            19: ["gaelic"],
            20: ["clairvoyance", "cthonic"],
            21: ["spanish"],
            23: ["world_geography"],
            25: ["french", "spear"],
            27: ["fast_healing"],
            29: ["italian"],
            30: ["parry"],
            33: ["modern_history"],
            36: ["world_affairs"],
            40: ["polish"],
            45: ["self_discipline"],
            50: ["romany"],
            60: ["teach"],
        },
    },
    "zefiro": {
        "nome_m": "Zefiro", "nome_f": "Zefiro",
        "razza": "zoog",
        "luogo": "Villaggio degli Zoog, Bosco Incantato, Dreamlands",
        "start_tag": "zoog_village",
        "descrizione": (
            "Giovane Zoog che impara i modi delle selvagge foreste delle "
            "Dreamlands. Skill fisiche."
        ),
        "attributi": {"str": 2, "int": 2, "wis": 2, "dex": 4, "con": 2, "luck": 3, "cha": 1,
                      "primario": "dex"},
        "skill_per_livello": {
            0: ["cthonic", "dagger", "dodge", "dreamlands", "english", "hand_to_hand", "recall"],
            1: ["education", "streetwise"],
            2: ["climb", "hide"],
            3: ["kick", "tracking"],
            4: ["martial_arts", "search", "steal"],
            5: ["mace", "swim"],
            6: ["parry", "sneak"],
            7: ["second_attack", "spanish"],
            8: ["spear"],
            9: ["dirt_kicking", "haggle"],
            10: ["backstab", "detection"],
            13: ["tame"],
            15: ["traps"],
            18: ["tailor"],
        },
    },
}


def nome_professione(prof_id, genere="m"):
    entry = NEWBIE_PROFESSIONS.get(prof_id)
    if not entry:
        return prof_id
    return entry["nome_f"] if genere == "f" else entry["nome_m"]


def skill_fino_al_livello(prof_id, livello):
    """Ritorna l'insieme di skill sbloccate dal livello 0 al `livello` incluso."""
    entry = NEWBIE_PROFESSIONS.get(prof_id)
    if not entry:
        return set()
    skills = set()
    for lvl, lista in entry["skill_per_livello"].items():
        if lvl <= livello:
            skills.update(lista)
    return skills
