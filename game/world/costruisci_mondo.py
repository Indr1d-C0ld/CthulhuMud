"""
Punto d'ingresso unico per la costruzione del mondo di CthulhuMUD.

PERCHE' QUESTO MODULO ESISTE
----------------------------
Il mondo e' stato costruito nel tempo chiamando a mano, una per una, le
funzioni di costruzione sparse nei moduli di world/. Finche' il database
esiste la cosa non si nota; ma se il database andasse perso, l'ordine
delle chiamate esisterebbe solo nella memoria di chi le ha fatte. Questo
modulo mette quell'ordine per iscritto, in modo eseguibile.

Non e' quindi una comodita': e' la differenza fra "il mondo e' un file
.db3 da custodire" e "il mondo e' codice, e il .db3 e' solo la partita in
corso".

TRE TRAPPOLE CHE QUESTO MODULO DISINNESCA
-----------------------------------------
1. Esistono TRE funzioni diverse chiamate popola_tutto(), in
   world/popola_mostri.py, world/popola_scenografia.py e
   world/popola_scenografia_arkham.py, e coprono cose diverse. Chiamarne
   una sola sembra aver fatto tutto. Qui sono elencate tutte e tre, con
   il modulo esplicito.
2. La scenografia di Arkham, Cairo e Zoog NON sta dentro
   popola_scenografia.popola_tutto(): sta in tre moduli separati.
3. espandi_inventari_negozi() deve girare DOPO i popolatori dei negozi.
   Se gira prima non trova mercanti da espandere e riesce in silenzio,
   senza errori e senza effetto.

IDEMPOTENZA E CONVERGENZA
-------------------------
Tutti i costruttori elencati qui si dichiarano idempotenti nei loro
docstring: rilanciarli non duplica nulla. Alcuni (rooms_ulthar,
rooms_dreamlands_overworld, rooms_bounty_office) dichiarano inoltre di
RIMANDARE i collegamenti verso zone non ancora costruite. Per questo la
fase della topologia viene eseguita due volte: la prima passata crea le
stanze, la seconda chiude i collegamenti incrociati che la prima ha
dovuto rimandare. Con l'ordine qui sotto la seconda passata non dovrebbe
trovare nulla da fare - ma resta, perche' costa poco ed e' cio' che rende
il risultato indipendente da eventuali riordini futuri.

USO
---
    from world.costruisci_mondo import costruisci_mondo
    esito = costruisci_mondo()

oppure, da dentro il gioco e con permessi da Developer:

    costruiscimondo
    costruiscimondo/verifica     (elenca le fasi senza eseguirle)
"""

from evennia.objects.models import ObjectDB


# ---------------------------------------------------------------------
# LE FASI
#
# Ogni voce e': (modulo, funzione, descrizione).
# I moduli si importano al momento dell'uso e non in testa al file:
# molti moduli di world/ si importano fra loro, e caricarli tutti qui
# creerebbe cicli di import che al momento non esistono.
# ---------------------------------------------------------------------

# Fase 0 - infrastruttura che non dipende da nessuna stanza.
INFRASTRUTTURA = [
    ("world.canali", "crea_canali", "canali di comunicazione"),
]

# Fase 1 - topologia: stanze e collegamenti.
#
# L'ordine NON e' alfabetico ne' casuale: gli hub newbie vengono per
# primi perche' quasi tutto il resto vi si aggancia; le Dreamlands
# vengono dopo Ulthar e Zoog perche' li collegano entrambi; l'ufficio
# taglie dopo gli hub perche' si attacca al recall di Dylath-Leen;
# collega_hub_al_mondo() viene per ultimo perche' presuppone che
# esistano sia gli hub sia le zone a cui agganciarli.
TOPOLOGIA = [
    ("world.rooms_newbie", "crea_stanze_newbie",
     "8 hub newbie (recall/respawn/morgue)"),
    ("world.rooms_arkham", "crea_vie_arkham",
     "32 vie di Arkham"),
    ("world.rooms_arkham_edifici", "crea_tutti_edifici",
     "73 edifici di Arkham"),
    ("world.rooms_cairo", "crea_cairo",
     "Cairo e i 7 negozi del Bazaar"),
    ("world.rooms_submarine", "crea_sottomarino",
     "relitto dello U-29 (23 stanze)"),
    ("world.rooms_ulthar", "crea_ulthar",
     "Ulthar (richiede gli hub newbie)"),
    ("world.rooms_zoogvillage", "crea_zoogvillage",
     "Zoog Village (richiede gli hub newbie)"),
    ("world.rooms_dreamlands_overworld", "crea_dreamlands_overworld",
     "sentieri delle Dreamlands (richiede Ulthar, Zoog, Dylath)"),
    ("world.rooms_bounty_office", "crea_ufficio_taglie",
     "ufficio taglie (richiede il recall di Dylath-Leen)"),
    ("world.rooms_hub_alieni", "costruisci_hub_alieni",
     "4 aree non umane (Y'ha-nthlei, Mi-Go, Yuggoth, Biblioteca)"),
    ("world.rooms_newbie", "collega_hub_al_mondo",
     "aggancio degli hub al mondo costruito"),
    # Rete di sicurezza: va per ultima, quando ogni modulo d'area ha gia'
    # collegato cio' che gli compete, cosi' interviene solo su cio' che e'
    # rimasto davvero isolato.
    ("world.rooms_newbie", "collega_ruoli_isolati_agli_hub",
     "uscite per le stanze di respawn/obitorio rimaste isolate"),
]

# Fase 2 - popolamento: NPC, mostri, scenografia, negozi, oggetti.
#
# I negozi vanno popolati PRIMA di espandere i loro inventari (vedi la
# trappola 3 in testa al file): espandi_inventari_negozi e' volutamente
# l'ultima voce dei negozi.
POPOLAMENTO = [
    ("world.npcs_newbie", "crea_npc_newbie",
     "NPC degli hub newbie"),

    # --- NPC di ambientazione ---
    #
    # DEVONO precedere i mostri. I tre popolatori qui sotto saltano una
    # stanza se contiene GIA' UN NPC QUALSIASI (non solo un NPC di
    # ambientazione), e i mostri sono NPC: popolando prima i mostri, gli
    # NPC di ambientazione delle stanze occupate non nascono affatto.
    # L'ordine inverso e' invece sicuro, perche' il reset dei mostri
    # controlla la presenza per bestiario_chiave e un NPC di
    # ambientazione, che non ne ha una, non lo blocca.
    ("world.popola_npc_ambientazione", "popola_npc_ambientazione",
     "NPC di ambientazione (Arkham e Dreamlands)"),
    ("world.popola_npc_ambientazione_cairo", "popola_npc_ambientazione_cairo",
     "NPC di ambientazione del Cairo"),
    ("world.popola_npc_ambientazione_zoog", "popola_npc_ambientazione_zoog",
     "NPC di ambientazione di Zoog Village"),

    # --- Mostri ---
    # NON usare popola_mostri.popola_tutto() qui: genera l'intera
    # tabella di reset a ogni chiamata senza guardare cosa c'e' gia', e
    # su un mondo popolato accumula ~70 mostri per esecuzione. La
    # versione di repop crea solo le voci mancanti.
    ("world.repop", "popola_tutte_le_zone_mancanti",
     "mostri di Arkham, Cairo, sommergibile, Dreamlands"),
    ("world.popola_hub_alieni", "popola_hub_alieni",
     "NPC, mercanti e ostili delle 4 aree non umane"),

    # --- Scenografia (extra descriptions) ---
    # Attenzione: le tre chiamate seguenti sono TUTTE necessarie, non
    # sono l'una il superinsieme dell'altra.
    ("world.popola_scenografia", "popola_tutto",
     "scenografia di sommergibile, Dreamlands, Ulthar"),
    ("world.popola_scenografia_arkham", "popola_tutto",
     "scenografia di Arkham (vie ed edifici)"),
    ("world.popola_scenografia_cairo", "popola_eds_cairo",
     "scenografia del Cairo"),
    ("world.popola_scenografia_zoog", "popola_eds_zoog",
     "scenografia di Zoog Village"),

    # --- Negozi e mercanti ---
    ("world.popola_negozi", "popola_negozi_demo",
     "prima tornata di mercanti"),
    ("world.popola_negozi_generici", "popola_negozi_generici",
     "negozi generici"),
    ("world.popola_negozi_abbigliamento", "popola_negozi_abbigliamento",
     "negozi di abbigliamento"),
    ("world.popola_negozi_cibo", "popola_negozi_cibo",
     "negozi di cibo"),
    ("world.popola_negozi_cairo", "popola_negozi_cairo",
     "negozi del Cairo"),
    ("world.popola_negozi_zoog", "popola_negozi_zoog",
     "negozi di Zoog Village"),
    ("world.espandi_inventari_negozi", "espandi_inventari_negozi",
     "espansione degli inventari (DEVE seguire i negozi)"),

    # --- Servizi e oggetti sparsi ---
    ("world.popola_alberghi", "popola_alberghi",
     "alberghi e locandieri"),
    ("world.popola_terapeuti", "popola_terapeuti",
     "terapeuti della sanita' mentale"),
    ("world.popola_forgiatura", "popola_forgiatura",
     "fucine e fabbri"),
    ("world.popola_cristalli_focus", "popola_cristalli_focus",
     "cristalli focus"),

    # --- Manutenzione ---
    # Per ultima: completa gli attributi di base mancanti di chi e' stato
    # creato prima che quei default esistessero (il caso del Dr. Armitage,
    # senza punti vita). Non crea oggetti, quindi il contatore di questa
    # fase resta a zero anche quando lavora.
    ("world.costruisci_mondo", "completa_attributi_viventi",
     "attributi di base mancanti di personaggi e NPC"),
]


def completa_attributi_viventi():
    """Completa gli attributi di base mancanti di ogni personaggio e NPC
    (typeclasses/living.py:completa_default_mancanti). Non crea oggetti e
    non tocca valori esistenti. Ritorna {id: [campi completati]} per le
    sole entita' toccate."""
    from evennia.objects.models import ObjectDB
    toccati = {}
    for o in ObjectDB.objects.filter(
            db_typeclass_path__in=("typeclasses.characters.Character", "typeclasses.npcs.NPC")):
        if hasattr(o, "completa_default_mancanti"):
            campi = o.completa_default_mancanti()
            if campi:
                toccati[o.id] = campi
    return toccati


def _esegui(modulo, funzione, descrizione, esito, verboso):
    """Esegue una singola fase, misurando quanti oggetti ha creato.

    Il conteggio e' fatto sul numero di righe in ObjectDB prima e dopo,
    invece che leggendo il valore di ritorno della funzione: i
    costruttori ritornano cose eterogenee (dizionari, liste, tuple,
    None) e interpretarle una per una sarebbe fragile. Il delta sul
    database e' invece uniforme e non mente.

    Un'eccezione in una fase non ferma le altre: viene registrata e si
    prosegue, perche' un mondo costruito all'85% con un errore visibile
    a video e' piu' utile di un mondo costruito al 30% con un traceback.
    """
    prima = ObjectDB.objects.count()
    etichetta = f"{modulo.split('.')[-1]}.{funzione}()"
    try:
        mod = __import__(modulo, fromlist=[funzione])
        getattr(mod, funzione)()
    except Exception as err:
        esito["errori"].append((etichetta, repr(err)))
        if verboso:
            print(f"  !! {etichetta}: {err!r}")
        return
    creati = ObjectDB.objects.count() - prima
    esito["fasi"].append((etichetta, creati, descrizione))
    if verboso:
        segno = f"+{creati}" if creati else "  ="
        print(f"  {segno:>5}  {etichetta:<52} {descrizione}")


def costruisci_mondo(verboso=True):
    """Costruisce (o completa) l'intero mondo di gioco.

    Idempotente: su un mondo gia' costruito non crea nulla e si limita a
    confermare che ogni fase non ha trovato niente da fare. Su un
    database vuoto ricostruisce il mondo da zero.

    Ritorna un dizionario con le fasi eseguite, gli oggetti creati da
    ciascuna e gli eventuali errori.
    """
    esito = {"fasi": [], "errori": [], "oggetti_prima": ObjectDB.objects.count()}

    if verboso:
        print(f"\nOggetti in partenza: {esito['oggetti_prima']}")
        print("\n--- infrastruttura ---")
    for voce in INFRASTRUTTURA:
        _esegui(*voce, esito, verboso)

    if verboso:
        print("\n--- topologia (prima passata) ---")
    for voce in TOPOLOGIA:
        _esegui(*voce, esito, verboso)

    # Seconda passata: chiude i collegamenti che i costruttori delle
    # zone dipendenti hanno dovuto rimandare. Con l'ordine attuale non
    # dovrebbe creare nulla; se crea qualcosa, vuol dire che l'ordine
    # della lista TOPOLOGIA non e' piu' corretto e va rivisto.
    if verboso:
        print("\n--- topologia (seconda passata: collegamenti rimandati) ---")
    recuperi = 0
    for modulo, funzione, descrizione in TOPOLOGIA:
        prima = ObjectDB.objects.count()
        _esegui(modulo, funzione, descrizione, esito, verboso=False)
        recuperi += ObjectDB.objects.count() - prima
    esito["recuperi_seconda_passata"] = recuperi
    if verboso:
        if recuperi:
            print(f"  ATTENZIONE: {recuperi} oggetti creati solo alla seconda "
                  f"passata: l'ordine di TOPOLOGIA andrebbe rivisto.")
        else:
            print("  nulla da recuperare: l'ordine della prima passata e' corretto.")

    if verboso:
        print("\n--- popolamento ---")
    for voce in POPOLAMENTO:
        _esegui(*voce, esito, verboso)

    esito["oggetti_dopo"] = ObjectDB.objects.count()
    esito["creati"] = esito["oggetti_dopo"] - esito["oggetti_prima"]

    if verboso:
        print(f"\nOggetti finali: {esito['oggetti_dopo']} "
              f"(creati in questa esecuzione: {esito['creati']})")
        if esito["errori"]:
            print(f"\n{len(esito['errori'])} FASI IN ERRORE:")
            for etichetta, err in esito["errori"]:
                print(f"  {etichetta}: {err}")
        else:
            print("Nessun errore.")

    return esito


def elenca_fasi():
    """Elenca le fasi nell'ordine in cui verrebbero eseguite, senza
    eseguirle. Utile per rivedere l'ordine senza toccare il mondo."""
    righe = []
    for titolo, gruppo in (("infrastruttura", INFRASTRUTTURA),
                           ("topologia", TOPOLOGIA),
                           ("popolamento", POPOLAMENTO)):
        righe.append(f"--- {titolo} ---")
        for modulo, funzione, descrizione in gruppo:
            righe.append(f"  {modulo.split('.')[-1]}.{funzione}()  -  {descrizione}")
    return righe
