"""
Registro delle razze giocabili di CthulhuMUD ITA Redux.

Le 6 razze catalogate dal sito originale. Nessun bonus numerico diretto:
i modificatori di attributo dipendono dalla professione di partenza scelta
(vedi world/professions_newbie.py), non dalla razza in se'.
"""

RACES = {
    "human": {
        "nome": "Umano",
        "nome_plurale": "Umani",
        "descrizione": (
            "Discendenti delle scimmie, orgogliosi di progressi tecnologici "
            "minuscoli. Razza raccomandata a chi e' nuovo al gioco."
        ),
        "difficolta": "consigliata ai nuovi giocatori",
    },
    "deep_one": {
        "nome": "Profondo",
        "nome_plurale": "Profondi",
        "descrizione": (
            "Razza anfibia al servizio di Padre Dagon e Madre Hydra, con forti "
            "legami anche con Cthulhu. Ignota nelle acque dolci, vive in citta' "
            "sommerse come Y'ha-nthlei; spesso impiega gli Shoggoth come servitori."
        ),
        "difficolta": "normale",
    },
    "mi_go": {
        "nome": "Mi-Go",
        "nome_plurale": "Mi-Go",
        "descrizione": (
            "\"Funghi di Yuggoth\", specie interstellare in cerca di minerali rari. "
            "Grandi ingegneri e chirurghi: si narra di cervelli umani spediti vivi "
            "su Yuggoth per lavorare come schiavi nelle miniere."
        ),
        "difficolta": "normale",
    },
    "shuggoth": {
        "nome": "Shoggoth",
        "nome_plurale": "Shoggoth",
        "descrizione": (
            "Esseri amorfi mutaforma creati dagli Elder Things come servitori, "
            "poi ribellatisi. Il loro corpo non offre slot per l'equipaggiamento: "
            "fanno affidamento solo sul combattimento a mani nude."
        ),
        "difficolta": "difficile",
        "niente_equipaggiamento": True,
    },
    "yithian": {
        "nome": "Yithiano",
        "nome_plurale": "Yithiani",
        "descrizione": (
            "Membri della Grande Razza di Yith, viaggiatori nel tempo che occupano "
            "corpi ospiti altrui. Il cambio di corpo (MINDTRANSFER) e' complesso "
            "e il corpo originale e' fragile: sconsigliati ai principianti assoluti."
        ),
        "difficolta": "molto difficile",
    },
    "zoog": {
        "nome": "Zoog",
        "nome_plurale": "Zoog",
        "descrizione": (
            "Piccoli umanoidi blu delle Dreamlands, chiassosi e dispettosi. "
            "Si narra che i bambini cattivi morti nel sonno diventino Zoog."
        ),
        "difficolta": "normale",
    },
}


def nome_razza(race_id, plurale=False):
    entry = RACES.get(race_id)
    if not entry:
        return race_id
    return entry["nome_plurale"] if plurale else entry["nome"]
