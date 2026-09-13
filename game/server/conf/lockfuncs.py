"""

Lockfuncs

Lock functions are functions available when defining lock strings,
which in turn limits access to various game systems.

All functions defined globally in this module are assumed to be
available for use in lockstrings to determine access. See the
Evennia documentation for more info on locks.

A lock function is always called with two arguments, accessing_obj and
accessed_obj, followed by any number of arguments. All possible
arguments should be handled with *args, **kwargs. The lock function
should handle all eventual tracebacks by logging the error and
returning False.

Lock functions in this module extend (and will overload same-named)
lock functions from evennia.locks.lockfuncs.

"""

# def myfalse(accessing_obj, accessed_obj, *args, **kwargs):
#    """
#    called in lockstring with myfalse().
#    A simple logger that always returns false. Prints to stdout
#    for simplicity, should use utils.logger for real operation.
#    """
#    print "%s tried to access %s. Access denied." % (accessing_obj, accessed_obj)
#    return False


def invisibilita_permessa(accessing_obj, accessed_obj, *args, **kwargs):
    """Fase K, sesta tornata: vero se accessing_obj puo' vedere/trovare
    accessed_obj nonostante un'eventuale invisibilita' magica (incantesimi
    invis/mass_invis - vedi world/effetti.py, world/magic.py). Usata sui
    lock "view"/"search" di Character e NPC, impostata UNA VOLA in
    at_living_creation() e mai piu' toccata: essendo dinamica (legge
    accessed_obj.db.invisibile ad ogni valutazione) non serve
    aggiungere/rimuovere il lock a ogni lancio/scadenza dell'incantesimo.

    Confermato dalla fonte (helps/invis.txt): "characters of higher level
    can still see it" - nessuna soglia numerica specificata: 10 livelli
    e' una scelta di design esplicita. Lo staff (Builder+) vede sempre
    tutto, per comodita' di building. Un personaggio con lo stato
    temporaneo "vede_invisibile" (dato da Rilevare l'Invisibile/Nebbia
    Fatata) vede sempre attraverso l'invisibilita' semplice.

    Fase K, ventesima tornata: gestisce anche WIZINVIS/CLOAK
    (commands/cthulhu_staff.py, helps/wizinvis.txt) - un Immortale
    WIZINVIS non e' visto da nessuno sotto Builder, ovunque si trovi;
    uno CLOAK solo da chi non e' nella sua stessa stanza. HOLYLIGHT
    (helps/holylight.txt, immhelp_commands.txt) vede sempre attraverso
    entrambi, come attraverso l'invisibilita' magica.
    """
    is_builder_o_superiore = hasattr(accessing_obj, "permissions") and accessing_obj.permissions.check("Builder")
    ha_holylight = getattr(accessing_obj, "db", None) and accessing_obj.db.holylight
    dati_bersaglio = getattr(accessed_obj, "db", None)
    if dati_bersaglio and dati_bersaglio.wizinvis and not is_builder_o_superiore and not ha_holylight:
        return False
    if dati_bersaglio and dati_bersaglio.cloak and not is_builder_o_superiore and not ha_holylight:
        stessa_stanza = getattr(accessing_obj, "location", None) and accessing_obj.location == accessed_obj.location
        if not stessa_stanza:
            return False

    invisibile = dati_bersaglio and accessed_obj.db.invisibile
    if not invisibile:
        return True
    if is_builder_o_superiore or ha_holylight:
        return True
    stati_bersaglio = getattr(accessed_obj, "db", None) and (accessed_obj.db.stati or {})
    if stati_bersaglio and stati_bersaglio.get("vera_invisibilita"):
        # Fase K, decima tornata: Vera Invisibilita' resiste anche a
        # Rilevare l'Invisibile (confermato dalla fonte) - nessuna
        # eccezione oltre al bypass Builder gia' gestito sopra.
        return False
    stati = getattr(accessing_obj, "db", None) and (accessing_obj.db.stati or {})
    if stati and stati.get("vede_invisibile"):
        return True
    livello_bersaglio = accessed_obj.livello_per_equip() if hasattr(accessed_obj, "livello_per_equip") else 1
    livello_osservatore = accessing_obj.livello_per_equip() if hasattr(accessing_obj, "livello_per_equip") else 1
    return livello_osservatore >= livello_bersaglio + 10


def _personaggio_di(oggetto):
    """Se oggetto e' gia' un personaggio (ha livello_per_equip) lo
    ritorna; se e' un Account, prova a risalire al personaggio
    attualmente impersonato."""
    if hasattr(oggetto, "livello_per_equip"):
        return oggetto
    char = getattr(oggetto, "puppet", None) or getattr(oggetto, "character", None)
    if char and hasattr(char, "livello_per_equip"):
        return char
    return None


def livello_minimo(accessing_obj, accessed_obj, *args, **kwargs):
    """Fase K, settima tornata: vero se accessing_obj ha raggiunto il
    livello minimo richiesto (primo argomento del lockfunc, es.
    "send:livello_minimo(51)") - usata per i canali INVESTIGATORTALK
    (51+) e HERO (101+), confermati dalla fonte (helps/ooc.txt)."""
    if not args:
        return True
    try:
        soglia = int(args[0])
    except (ValueError, TypeError):
        return True
    personaggio = _personaggio_di(accessing_obj)
    return bool(personaggio and personaggio.livello_per_equip() >= soglia)


def e_remortato(accessing_obj, accessed_obj, *args, **kwargs):
    """Fase K, settima tornata: vero se accessing_obj ha completato un
    remort (db.remortato) - usata per il canale REMTALK."""
    personaggio = _personaggio_di(accessing_obj)
    return bool(personaggio and getattr(personaggio.db, "remortato", False))


def porta_aperta(accessing_obj, accessed_obj, *args, **kwargs):
    """Fase K, nona tornata: usata sul lock "traverse" delle uscite (vedi
    world/porte.py, commands/cthulhu_porte.py) - vero se l'uscita NON e'
    chiusa (db.chiusa falso/assente, il caso comune per la stragrande
    maggioranza delle uscite del mondo, mai toccate da OPEN/CLOSE), oppure
    se chi attraversa ha lo stato "attraversa_porte" attivo (incantesimo
    Pass Door, confermato dalla fonte: "enables the caster to pass through
    most closed doors")."""
    if not getattr(accessed_obj, "db", None) or not accessed_obj.db.chiusa:
        return True
    personaggio = _personaggio_di(accessing_obj)
    if personaggio and (personaggio.db.stati or {}).get("attraversa_porte"):
        return True
    if hasattr(accessing_obj, "permissions") and accessing_obj.permissions.check("Builder"):
        return True
    return False
