"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    def return_appearance(self, looker, **kwargs):
        """Fase K, sedicesima tornata: se chi guarda non riesce a vedere
        al buio (world/illuminazione.py), la stanza mostra solo un
        messaggio di buio invece della normale descrizione/contenuto/
        uscite - stesso comportamento della fonte (guides_advice.txt:
        "The room is dark..."). Semplificazione dichiarata: questo
        blocca solo LOOK/EXAMINE senza argomenti (il bersaglio qui e'
        sempre la stanza); guardare un oggetto o un personaggio
        specifico per nome resta possibile anche al buio, coerente con
        la stessa scelta di non-esaustivita' gia' fatta per cieco/muto
        (vedi world/effetti.py)."""
        from world.illuminazione import si_vede

        if hasattr(looker, "location") and looker.location is self and not si_vede(looker):
            return "E' troppo buio per vedere qualcosa."
        return super().return_appearance(looker, **kwargs)

    def at_object_receive(self, obj, source_location, **kwargs):
        """NPC ostili con db.attacca_a_vista (vedi world/mostri.py,
        Fase G/H) attaccano un personaggio giocante non appena entra
        nella stanza - una scelta di design esplicita (nessuna fonte
        originale descrive la logica esatta di aggro), coerente con la
        convenzione classica dei MUD derivati da Diku. Il livello del
        personaggio e' comunque rispettato: confermato dalla fonte
        (immhelp_flags.txt, flag AGGRESSIVE) che un mob del genere "will
        attack everyone who's not very superior in level" - vedi
        world.mostri.MARGINE_AGGRESSIONE."""
        super().at_object_receive(obj, source_location, **kwargs)
        if not obj.is_typeclass("typeclasses.characters.Character", exact=False):
            return
        from world.mostri import tenta_aggro

        # Fase K, nona tornata: RECRUIT e' passivo, "works automatically"
        # (helps/recruit.txt) - controllato qui, la stessa sede gia' usata
        # per l'aggro, ogni volta che un personaggio entra in una stanza.
        from world.seguaci import tenta_recruit
        tenta_recruit(obj)

        # world.mostri.tenta_aggro centralizza sia il caso AGGRESSIVE
        # (immhelp_flags.txt) sia il caso guardia/criminale
        # (helps/criminal.txt), gia' descritti nel modulo condiviso.
        for npc in self.contents:
            if npc is obj:
                continue
            tenta_aggro(npc, obj)

    def at_object_leave(self, moved_obj, target_location, move_type="move", **kwargs):
        """HUNTER/TRACKER (world.mostri.tenta_inseguimento) esteso a
        QUALUNQUE uscita di un personaggio dalla stanza, non solo alla
        fuga esplicita col comando FLEE - vedi la funzione condivisa per
        il dettaglio del gap trovato in audit (Fase K, pre-release) e
        della scelta di scope (inseguimento a un salto per volta, non
        teletrasporto)."""
        super().at_object_leave(moved_obj, target_location, move_type=move_type, **kwargs)
        if not target_location or not moved_obj.is_typeclass("typeclasses.characters.Character", exact=False):
            return
        from world.mostri import tenta_inseguimento

        for cacciatore in list(self.contents):
            tenta_inseguimento(cacciatore, moved_obj, target_location)
