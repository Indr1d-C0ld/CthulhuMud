"""
Personaggi pre-impostati (Fase K, diciottesima tornata): aggiunta
dichiaratamente NUOVA rispetto alla fonte - nessuna pagina del sito
originale descrive personaggi pronti all'uso in creazione. Tributo ai
giochi di ruolo cartacei/videoludici, richiesto esplicitamente
dall'utente.

Un preset per ciascuna delle 16 professioni newbie (world/
professions_newbie.py). Gli attributi di base (quelli tirati a caso in
creazione normale, vedi typeclasses/characters.py:tira_attributi_base)
qui sono sostituiti da una curva fissa e curata invece che casuale:
[13, 12, 11, 10, 9, 8, 7] assegnata in ordine decrescente agli
attributi che la professione stessa valorizza di piu' (ordinando i
suoi modificatori "attributi" - stesso campo gia' usato per il tiro
normale). Cosi' il preset enfatizza coerentemente cio' che la
professione gia' privilegia (l'attributo primario finisce quasi sempre
con base 13 o 12), senza dover scegliere a mano 16*7 numeri uno per
uno. Somma fissa 70 - identica alla media attesa di 7 tiri 3d6, ben
sotto SOMMA_MASSIMA_ATTRIBUTI (85, l'anti-minmax di
typeclasses/characters.py): un preset non e' mai "piu' forte" di un
personaggio fortunato tirato a caso, solo piu' prevedibile.

Il nome suggerito qui e' solo un default: il giocatore lo conferma o
lo cambia comunque nel passo di scelta del nome del chargen (world/
chargen_menu.py), come per qualunque altro personaggio.
"""

from world.professions_newbie import NEWBIE_PROFESSIONS

CURVA_BASE = (13, 12, 11, 10, 9, 8, 7)

# profession_id -> nome maschile suggerito (i generi "_f" sono le
# controparti femminili di NEWBIE_PROFESSIONS, il preset propone
# sempre la forma "_m" scelta a caso tra i due generi disponibili per
# varieta' - vedi lista_preset()).
PRESET_NOME_M = {
    "apprendista": "Nathaniel",
    "cadetto": "Walter",
    "studentessa_conventuale": "Herbert",
    "teppista": "Silas",
    "universitario": "Ambrose",
    "iniziato": "Atal",
    "scudiero": "Kranon",
    "monello": "Sabbat",
    "cacciatore_di_molluschi": "Obed",
    "tentacolo_di_dagon": "Nereus",
    "cacciatore_di_cervelli": "Fthaggua",
    "scienziato_migo": "Nyarlek",
    "melma": "Marsh",
    "esploratore_yithiano": "Nlarro",
    "maghetto": "Ziq",
    "zefiro": "Brol",
}
PRESET_NOME_F = {
    "apprendista": "Abigail",
    "cadetto": "Charity",
    "studentessa_conventuale": "Prudence",
    "teppista": "Keziah",
    "universitario": "Cordelia",
    "iniziato": "Yala",
    "scudiero": "Nithra",
    "monello": "Sable",
    "cacciatore_di_molluschi": "Coral",
    "tentacolo_di_dagon": "Thalassa",
    "cacciatore_di_cervelli": "Fthaggua",
    "scienziato_migo": "Nyarlek",
    "melma": "Marsh",
    "esploratore_yithiano": "Nlarro",
    "maghetto": "Ziq",
    "zefiro": "Brol",
}


def _base_curata(prof_id):
    """{attributo: valore_base} secondo la curva fissa, in ordine
    decrescente di quanto la professione lo valorizza gia'."""
    modificatori = NEWBIE_PROFESSIONS[prof_id]["attributi"]
    attributi_ordinati = sorted(
        (a for a in modificatori if a != "primario"),
        key=lambda a: modificatori[a],
        reverse=True,
    )
    return dict(zip(attributi_ordinati, CURVA_BASE))


def lista_preset():
    """Ritorna [(prof_id, nome_m, nome_f, nome_professione, razza_id, descrizione), ...]
    nello stesso ordine di NEWBIE_PROFESSIONS, pronta per un menu."""
    righe = []
    for prof_id, prof in NEWBIE_PROFESSIONS.items():
        righe.append((
            prof_id,
            PRESET_NOME_M.get(prof_id, prof["nome_m"]),
            PRESET_NOME_F.get(prof_id, prof["nome_f"]),
            prof["nome_m"],
            prof["razza"],
            prof["descrizione"],
        ))
    return righe


def applica_preset(personaggio, prof_id, genere="m"):
    """Applica un preset: razza, attributi di base curati (non tirati a
    caso), professione e le sue skill/luogo di partenza. Ritorna il
    nome suggerito (stringa) - il chiamante lo passa al passo di scelta
    del nome del chargen, dove il giocatore lo conferma o lo cambia."""
    prof = NEWBIE_PROFESSIONS[prof_id]
    # Reset esplicito: se il giocatore ha gia' guardato/scelto un altro
    # preset prima di questo (stesso "new_char" ancora in creazione),
    # applica_professione_newbie() da sola lascerebbe accumulati
    # professione/skill del preset scartato in precedenza.
    personaggio.db.professions = {}
    personaggio.db.active_profession = None
    personaggio.db.skills = {}

    personaggio.imposta_razza(prof["razza"])
    for attr, valore in _base_curata(prof_id).items():
        personaggio.attributes.add(f"stat_{attr}", valore, category="cthulhu")
    personaggio.applica_professione_newbie(prof_id)
    mappa_nomi = PRESET_NOME_F if genere == "f" else PRESET_NOME_M
    return mappa_nomi.get(prof_id, prof["nome_m"])
