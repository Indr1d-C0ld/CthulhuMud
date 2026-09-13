"""
Generazione casuale del personaggio (Fase K, diciottesima tornata):
aggiunta dichiaratamente NUOVA rispetto alla fonte - vedi world/
nomi_generazione.py per le note sull'assenza di questa funzionalita'
nell'originale.

A differenza dei preset (world/personaggi_preimpostati.py, attributi
di base curati a mano), qui tutto e' davvero casuale: professione
scelta a caso tra le 16 newbie, attributi tirati con lo stesso
tira_attributi_base() usato dalla creazione guidata (quindi soggetto
anche li' all'anti-minmax, SOMMA_MASSIMA_ATTRIBUTI), genere scelto a
caso, nome pescato dal pool coerente con l'origine della professione
(world/nomi_generazione.py). Pensato per poter essere richiamato piu'
volte di fila ("rigenera") finche' il giocatore non e' soddisfatto,
prima di passare al passo di conferma del nome.
"""

import random

from world.professions_newbie import NEWBIE_PROFESSIONS
from world.nomi_generazione import genera_nome


def genera_personaggio_casuale(personaggio):
    """Sceglie una professione a caso, tira gli attributi, applica
    razza/professione/skill e propone un nome. Puo' essere richiamata
    piu' volte sullo stesso personaggio (ogni chiamata sovrascrive
    razza/attributi/professione/skill con un nuovo tiro) per un
    "rigenera". Ritorna (prof_id, nome_suggerito, genere)."""
    prof_id = random.choice(list(NEWBIE_PROFESSIONS.keys()))
    prof = NEWBIE_PROFESSIONS[prof_id]
    genere = random.choice(("m", "f"))

    # Reset esplicito prima di (ri)applicare: se questa e' una "rigenera"
    # dopo un tiro precedente su un'altra professione, senza questo reset
    # applica_professione_newbie() lascerebbe accumulati professione/skill
    # del tentativo scartato (non e' pensata per essere richiamata piu'
    # volte - vedi il suo docstring).
    personaggio.db.professions = {}
    personaggio.db.active_profession = None
    personaggio.db.skills = {}

    personaggio.imposta_razza(prof["razza"])
    personaggio.tira_attributi_base()
    personaggio.applica_professione_newbie(prof_id)
    personaggio.db.genere = genere

    nome = genera_nome(prof_id, genere=genere)
    return prof_id, nome, genere
