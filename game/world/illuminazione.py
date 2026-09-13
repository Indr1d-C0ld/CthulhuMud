"""
Buio/luce (Fase K, sedicesima tornata): confermato dalla fonte come
meccanica reale, non semplice colore - helps/darkness.txt (l'incantesimo
Oscurita' "fills an entire room with a magical wave of darkness"),
helps/light.txt (i comandi LIGHT/EXTINGUISH controllano lo stato di un
oggetto-luce; "holding a light object automatically ignites it, and
removing it automatically extinguishes it"), helps/infravision.txt
("enables a character to see in the dark... provides the infrared
affect, which allows you to see in pitch-black conditions"), e la FAQ
ufficiale (guides_advice.txt): "The room is dark and there's all these
glowing red eyes!? ... The room is affected by magical darkness. Get
the spell infravision."

NESSUN ciclo giorno/notte ambientale e' stato trovato nella fonte
raccolta finora (nessuna pagina su sunrise/sunset/illuminazione
diurna): il buio qui e' SOLO magico (incantesimo Oscurita', temporaneo)
o intrinseco a specifiche stanze gia' descritte come tali nel testo
(es. "E' buio pesto qui dentro", vedi world/rooms_submarine.py) - non
un meccanismo universale legato all'orario di world/tempo.py. Vedere
la conversazione di progetto per la scelta esplicita di NON inventare
un ciclo solare non confermato.

Semplificazione dichiarata (stesso principio gia' visto in
world/effetti.py per cieco/muto): il buio blocca solo la descrizione
della stanza (LOOK/EXAMINE senza argomenti) - guardare un oggetto o un
personaggio specifico per nome, se lo si conosce gia', resta possibile
anche al buio. Nessuna fonte specifica un elenco esaustivo di comandi
bloccati dal buio, e replicarlo per ogni possibile bersaglio di LOOK
(oggetti, personaggi, uscite) uscirebbe dallo scope di questa tornata.
Il buio non influenza il combattimento (nessuna fonte conferma un
malus a colpire per l'oscurita').
"""

from world.effetti import ha_stato


def stanza_buia(stanza):
    """True se la stanza e' al buio in questo momento: permanentemente
    (tag manuale su stanze intrinsecamente buie) o temporaneamente
    (incantesimo Oscurita' attivo, vedi world/magic.py:_effetto_darkness)."""
    if not stanza:
        return False
    return bool(stanza.db.buio_permanente) or ha_stato(stanza, "buio_magico")


def _oggetto_illumina(oggetto):
    return bool(oggetto.db.luce) and bool(oggetto.db.luce_accesa)


def stanza_illuminata(stanza):
    """True se in questo momento c'e' abbastanza luce per vedere
    normalmente nella stanza: perche' non e' buia, perche' CONTINUAL
    LIGHT/MAGE LIGHT sono attivi (rispettivamente permanente e
    temporaneo, vedi world/magic.py:_effetto_continual_light/
    _effetto_mage_light), o perche' un oggetto-luce acceso e' presente
    (a terra, o addosso/in mano a qualcuno presente - vedi
    typeclasses/objects.py:OggettoLuce)."""
    if not stanza_buia(stanza):
        return True
    if stanza.db.luce_permanente or ha_stato(stanza, "luce_magica"):
        return True
    for presente in stanza.contents:
        if _oggetto_illumina(presente):
            return True
        for portato in getattr(presente, "contents", ()):
            if _oggetto_illumina(portato):
                return True
    return False


def personaggio_vede_al_buio(personaggio):
    """Infravisione (incantesimo, vedi world/magic.py:_effetto_infravision)."""
    return ha_stato(personaggio, "vede_al_buio")


def si_vede(personaggio):
    """True se il personaggio riesce a vedere la sua stanza attuale in
    questo momento (usato da typeclasses/rooms.py:Room.return_appearance).
    HOLYLIGHT (Fase K, ventesima tornata, commands/cthulhu_staff.py)
    bypassa sempre il buio - comodita' da staff confermata dalla fonte
    (immhelp_commands.txt, comando HOLYLIGHT)."""
    if getattr(personaggio, "db", None) and personaggio.db.holylight:
        return True
    if not personaggio.location:
        return True
    return stanza_illuminata(personaggio.location) or personaggio_vede_al_buio(personaggio)
