"""
Societies/Clan (Fase G, settima tornata; completato nella
ventiseiesima tornata durante l'audit del sistema). Confermato dalla
scansione esaustiva (societies_list.txt, societies_newclans.txt,
societies_upgrades.txt, helps/societies.txt) che nell'originale i clan
NON erano un sistema self-service per i giocatori: fondarne uno
richiede di essere almeno livello HERO, due co-fondatori (uno almeno
INVESTIGATOR), 500.000 oro, e soprattutto l'approvazione manuale dello
staff Immortal via richiesta ("submitted to the Immortal staff through
the in-game board system or... email"). Le "imprese" di aggiornamento
(stanze/porte/mob, tutte prezzate) sono anch'esse acquisti mediati
dallo staff, non un comando di acquisto in-game.

Per questo qui NON implementiamo un comando "fonda il tuo clan" o un
negozio di potenziamenti self-service: sarebbe INFEDELE alla fonte,
non un gap. Quello che invece E' realmente giocabile - appartenenza,
ruolo/rango, consultare l'elenco dei clan - viene implementato qui.

I 6 clan pubblici elencati dalla fonte (esistono "dozzine" di clan
piu' piccoli e segreti, mai resi pubblici: non inventiamo nomi per
quelli). Rank a bitflag confermati dalla fonte: invited=1, member=2,
council=4, leader=8.

Gap chiusi nella ventiseiesima tornata (helps/societies.txt, sintassi
completa: "SOCIETY", "SOCIETY <sid>", "SOCIETY LIST <group>",
"SOCIETY INFO <sid>", "SOCIETY MEMBERS <sid>", "SOCIETY RESEARCH
<character>", "SOCIETY TELL <sid> <message>", "SOCIETY PROMOTE/DEMOTE/
EXPEL <character> <sid>"):
- **Appartenenza multipla**: la fonte presume che un personaggio possa
  appartenere a PIU' societa' contemporaneamente ("SOCIETY INFO will
  show you a list of the societies you are currently in", plurale) -
  prima un personaggio poteva avere un solo db.clan/db.rango_clan.
  Sostituito con db.societa_ranghi (dict {societa_id: rango}).
- MEMBERS/RESEARCH/TELL: comandi reali mancanti, vedi
  commands/cthulhu_clan.py.
- EXPEL come azione diretta, non solo effetto collaterale di demote
  ripetuto fino al rango minimo.
- Ricerca del bersaglio ora globale (global_search=True) per invite/
  promote/demote/expel, non piu' limitata alla sola stanza del chiamante.
- Bootstrap in-game per il primo membro/leader di un clan appena
  approvato dallo staff (prima possibile solo chiamando unisciti()
  manualmente via @py) - nuovo sottocomando CLAN INDUCT, riservato
  allo staff (stesso schema di CmdSubrace).
- Il "leader" mostrato da CLAN LIST/INFO ora e' dinamico quando un
  personaggio reale detiene il rango leader in quella societa' (prima
  era sempre e solo il nome statico "di lore", scollegato dal sistema
  di rango realmente giocabile) - ripiega sul nome di lore se nessuno
  lo detiene ancora davvero.

Deliberatamente NON implementato in questa tornata (dichiarato, non
dimenticato): l'intera suite di governance/economia di clan citata
dalla stessa pagina fonte - SOCIETY POLITICS, REVOLT, CHALLENGE, VOTE,
LAW, BANK, TAX, FOE/PARDON, AUTH, SIGN, SUBSCRIBE, RESET, TEST,
CLEANUP. Costruire anche solo un sottoinsieme minimamente credibile di
elezioni/tasse/diplomazia tra clan e' un sistema a se stante, delle
dimensioni dell'intero resto di questo modulo - andrebbe discusso e
scoperto a parte, non improvvisato dentro un audit di chiusura-gap.
SOCIETY LIST <group> non e' stato implementato per lo stesso motivo di
proporzione: nessuna delle due fonti fornisce una categorizzazione
tematica dei 6 clan pubblici, e inventarne una da zero senza alcun
indizio sarebbe arbitrario in un modo che gli altri "raggruppamenti
dichiarati" di questo progetto (es. tipo_orrore dei mostri) non sono
(li' la fonte descrive esplicitamente le creature del Mythos di
riferimento, qui non c'e' nulla di equivalente per i 6 clan).
"""

RANGO_INVITATO = 1
RANGO_MEMBRO = 2
RANGO_CONSIGLIO = 4
RANGO_LEADER = 8

NOMI_RANGO = {
    RANGO_INVITATO: "invitato/a",
    RANGO_MEMBRO: "membro",
    RANGO_CONSIGLIO: "membro del consiglio",
    RANGO_LEADER: "leader",
}

SCALA_RANGHI = (RANGO_INVITATO, RANGO_MEMBRO, RANGO_CONSIGLIO, RANGO_LEADER)

SOCIETA = {
    "arkham_masonic_lodge": {
        "nome": "Loggia Massonica di Arkham",
        "descrizione": (
            "Un gruppo di viaggiatori instancabili, uniti dal racconto delle proprie "
            "avventure e dalle voci su segreti perduti nel tempo. Sempre pronti ad "
            "aiutarsi a vicenda e ad assistere i piu' giovani in cerca di un oggetto, o "
            "anche di qualcosa che non si puo' comprare: l'illuminazione."
        ),
        "leader": None,
    },
    "cabal_du_quixotic": {
        "nome": "Cabal Du Quixotic",
        "descrizione": (
            "Una societa' interessata all'esplorazione dei segreti in ogni loro forma, "
            "condivisi con chi e' disposto a pagarne il prezzo. Per entrare, si richiede "
            "di fornire alla dirigenza una mappa dettagliata di un'area non ancora "
            "mappata, o una raccolta equivalente di informazioni su qualche aspetto del mondo."
        ),
        "leader": "Wod",
    },
    "esoteric_order_of_dagon": {
        "nome": "Ordine Esoterico di Dagon",
        "descrizione": (
            "Un culto misterioso radicato nella decadente citta' portuale di Innsmouth, "
            "importato dalle navi mercantili di Obed Marsh. Voci di incroci tra i membri "
            "del culto e i Profondi, e rituali blasfemi celebrati di notte verso la "
            "Barriera del Diavolo, attendono il giorno del risveglio di Grande Cthulhu."
        ),
        "leader": None,
    },
    "renders_of_the_veil": {
        "nome": "Squarciatori del Velo",
        "descrizione": (
            "Ci sono troppe cose nascoste, troppi ciarlatani, troppi predatori segreti in "
            "attesa degli ignari. Ogni forma di inganno e trappola va combattuta, dagli dei "
            "oscuri agli uomini malvagi fino ai moralisti che vorrebbero imporre a tutti "
            "una vita di contemplazione divina."
        ),
        "leader": "Aemilia",
    },
    "ulthar_arcanuum": {
        "nome": "Arcanuum di Ulthar",
        "descrizione": (
            "L'obiettivo dell'Arcanuum e' l'acquisizione e la conservazione della "
            "conoscenza magica e la sperimentazione nelle Dreamlands: unire le diverse "
            "energie magiche che scorrono in flusso e riflusso dalla dimensione terrestre. "
            "Benvenuti coloro che si sono risvegliati alla vera magia e hanno scelto una "
            "professione affine alle nostre credenze."
        ),
        "leader": "Thistle",
    },
    "warriors_of_light": {
        "nome": "Guerrieri della Luce",
        "descrizione": (
            "Fin dalla creazione, questi guerrieri sacri tengono a bada le forze del male. "
            "Seguendo l'esempio di Marduk nell'uccidere Tiamat, attendono il giorno in cui "
            "Grande Cthulhu si risvegliera' dal sonno per poterlo distruggere e porre fine "
            "alla sua influenza malvagia. Si riconoscono dal sigillo di Marduk portato sul petto."
        ),
        "leader": None,
    },
}


def nome_societa(societa_id):
    entry = SOCIETA.get(societa_id)
    return entry["nome"] if entry else societa_id


def societa_di(personaggio):
    """{societa_id: rango} di appartenenza (puo' essere vuoto) - un
    personaggio puo' appartenere a piu' societa' contemporaneamente
    (confermato dalla fonte, vedi nota di modulo)."""
    return personaggio.db.societa_ranghi or {}


def rango_in(personaggio, societa_id):
    return societa_di(personaggio).get(societa_id, 0)


def ha_rango(personaggio, societa_id, rango_minimo):
    return rango_in(personaggio, societa_id) >= rango_minimo


def unisciti(personaggio, societa_id, rango=RANGO_MEMBRO):
    """Assegna un rango in una societa' a un personaggio - da usare solo
    dopo un invito/approvazione (nessun comando di auto-iscrizione: come
    da fonte, i clan pubblici non sono self-service)."""
    if societa_id not in SOCIETA:
        return False, "Societa' sconosciuta."
    ranghi = societa_di(personaggio)
    ranghi[societa_id] = rango
    personaggio.db.societa_ranghi = ranghi
    return True, f"Ora fai parte di {nome_societa(societa_id)} come {NOMI_RANGO[rango]}."


def lascia(personaggio, societa_id):
    ranghi = societa_di(personaggio)
    if societa_id not in ranghi:
        return False, f"Non fai parte di {nome_societa(societa_id)}."
    ranghi.pop(societa_id, None)
    personaggio.db.societa_ranghi = ranghi
    return True, f"Lasci {nome_societa(societa_id)}."


def leader_reale(societa_id):
    """Il personaggio che detiene DAVVERO il rango leader in questa
    societa' (vedi CLAN INFO/LIST), se esiste. None se nessuno lo ha
    ancora (allora si ripiega sul nome di lore statico in SOCIETA)."""
    from evennia.objects.models import ObjectDB
    for p in ObjectDB.objects.filter(db_typeclass_path="typeclasses.characters.Character"):
        if rango_in(p, societa_id) >= RANGO_LEADER:
            return p
    return None


def membri_di(societa_id):
    """Tutti i personaggi con un rango > 0 in questa societa'."""
    from evennia.objects.models import ObjectDB
    return [
        p for p in ObjectDB.objects.filter(db_typeclass_path="typeclasses.characters.Character")
        if rango_in(p, societa_id) > 0
    ]
