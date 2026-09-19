"""
Il comando DREAM (Fase E, quinta tornata; formula/gap completati nella
ventiseiesima tornata - vedi world/dreamlands.py per la logica e le
citazioni della fonte): l'accesso alle Dreamlands tramite il sogno,
citato nel Dossier Miskatonic ("Dreamlands: Dimensione onirica
parallela, raggiungibile via DREAM WALK, con rischi propri - morte in
sogno puo' disallineare respawn/cadavere").

Il rischio scelto col committente e' quello "lieve", che si scopre
essere gia' il comportamento di default del sistema di morte (M3,
world/combat.py:_morte_personaggio): il cadavere resta sempre dove si
muore, il respawn va sempre alla propria stanza RESPAWN nel mondo
reale. Morire nelle Dreamlands lascia quindi gia' naturalmente il
cadavere li' dentro, irraggiungibile finche' non si torna a sognare.
Non serve nessuna modifica al sistema di morte: serve solo il modo di
entrare e uscire dal sogno.

Sintassi: il comando qui si chiama DREAM/WAKE (non DREAM WALK/DREAM
AWAKEN come nella sintassi letterale della fonte) - deviazione minore
mai discussa esplicitamente col committente, lasciata com'era per non
rompere l'uso gia' consolidato in questo porting.
"""

import random

from evennia import Command

from world.dreamlands import (
    in_dreamlands, get_crocevia, get_destinazione_ingresso, sveglia_da_sogno,
    fluttua_skill_casuali, PROBABILITA_INCUBO_SENZA_SKILL, BONUS_TRANCE,
)
from world.colori import onirico, orrore


class CmdDream(Command):
    """
    prova ad addormentarti e a scivolare nelle Dreamlands

    Uso:
      dream

    Tenta di farti addormentare e proiettarti nelle Dreamlands, la
    dimensione onirica parallela. La probabilita' di riuscita dipende
    dalla skill Sognare (Dreaming, aiutata dalla Saggezza) e dalla tua
    Sanity: piu' la tua mente e' provata, piu' facilmente scivola nel
    sogno - ma senza la skill rischi di finire intrappolato/a in un
    incubo pericoloso invece che in un sogno normale.

    Non puoi usare questo comando se sei gia' nelle Dreamlands (usa
    invece wake per svegliarti).

    Attenzione: se muori nelle Dreamlands, ti risveglierai comunque
    sano e salvo nel mondo reale - ma il tuo cadavere e i tuoi
    oggetti resteranno nel sogno, raggiungibili solo tornandoci.
    """

    key = "dream"
    aliases = ["sogna"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        if in_dreamlands(caller.location):
            caller.msg("Sei gia' immerso in un sogno. Usa |wwake|n per svegliarti.")
            return

        destinazione = get_destinazione_ingresso(caller.location)
        if not destinazione:
            caller.msg(
                "Chiudi gli occhi, ma il sogno non prende forma. "
                "(le Dreamlands non sono ancora state costruite)"
            )
            return

        sanity = caller.db.sanity if caller.db.sanity is not None else 100
        sanity_max = caller.db.sanity_max or 100
        percentuale_sanity = max(0, min(100, (sanity / sanity_max) * 100))

        rating_dreaming = caller.skill_rating("dreaming")
        # Stesso difetto corretto in world/magic.py:tiro_salvezza: db.wis
        # non viene mai scritto, la Saggezza si legge con valore_attributo()
        # - prima valeva sempre 10 e non incideva su nulla.
        saggezza = (caller.valore_attributo("wis")
                    if hasattr(caller, "valore_attributo") else 10)

        # helps/dreaming.txt: la skill (aiutata dalla Saggezza) rende il
        # viaggio piu' facile; la Sanity bassa lo facilita comunque un
        # po' (coerente con lo spirito cosmic horror gia' scelto in
        # questo porting: e' la follia ad aprire la porta).
        probabilita = 15 + rating_dreaming * 0.4 + saggezza * 0.5 + (100 - percentuale_sanity) * 0.3
        from world.effetti import ha_stato
        if ha_stato(caller, "trance"):
            probabilita += BONUS_TRANCE
        probabilita = max(5, min(95, probabilita))

        caller.msg("Chiudi gli occhi e ti lasci scivolare nel sonno...")

        if random.uniform(0, 100) <= probabilita:
            caller.msg(
                onirico(
                    "Il mondo si dissolve in vortici di colore. Quando riapri gli occhi, "
                    "sei altrove - in un luogo che esiste solo quando qualcuno lo sogna."
                )
            )
            caller.db.ultimo_sogno = destinazione
            caller.move_to(destinazione, quiet=True, move_type="teleport")
            fluttua_skill_casuali(caller)
            caller.msg(caller.at_look(caller.location))
            return

        if rating_dreaming <= 0 and random.randint(1, 100) <= PROBABILITA_INCUBO_SENZA_SKILL:
            # helps/dreaming.txt: "characters who attempt to travel in
            # their dreams without developing this skill will often
            # find themselves trapped in terrible nightmares that can
            # be both dangerous and deadly."
            from world.sanita import perdi_sanita
            from world.effetti import applica_stato

            caller.msg(orrore("Ti ritrovi intrappolato/a in un incubo terrificante!"))
            perdi_sanita(caller, random.randint(5, 15))
            applica_stato(caller, "impaurito", 60, "L'incubo svanisce, lasciandoti scosso/a ma sveglio/a.")
            caller.db.ultimo_sogno = destinazione
            caller.move_to(destinazione, quiet=True, move_type="teleport")
            caller.msg(caller.at_look(caller.location))
            return

        caller.msg(
            "Il sonno ti sfugge, agitato e superficiale. Resti sveglio, "
            "con la vaga sensazione di aver sfiorato qualcos'altro."
        )


class CmdWake(Command):
    """
    svegliati dal sogno, o alzati/sveglia qualcuno (REST/SLEEP/STAND/WAKE)

    Uso:
      wake
      wake <personaggio>

    Se sei nelle Dreamlands, questo comando ti sveglia di soprassalto,
    riportandoti alla tua stanza di RECALL nel mondo reale. Funziona
    anche su un altro personaggio addormentato nelle Dreamlands: lo
    riporta a SUA volta al mondo reale, non solo in piedi sul posto.

    Altrimenti, WAKE fa parte del sistema di posizione REST/SLEEP/STAND
    (vedi world/posizione.py, Fase K, quattordicesima tornata): senza
    argomenti equivale a STAND (ti alzi); con un bersaglio, provi a
    svegliare un altro personaggio addormentato - se il suo sonno e'
    di origine magica, la fonte dice che e' "molto piu' difficile"
    riuscirci.
    """

    key = "wake"
    aliases = ["svegliati", "sveglia"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        if not self.args.strip():
            if sveglia_da_sogno(caller, "|mTi svegli di soprassalto, il cuore che batte forte.|n"):
                caller.msg(caller.at_look(caller.location))
                return
            from world.posizione import tenta_wake
            messaggio = tenta_wake(caller, "")
            if messaggio:
                caller.msg(messaggio)
            return

        from world.posizione import tenta_wake
        messaggio = tenta_wake(caller, self.args.strip())
        if messaggio:
            caller.msg(messaggio)
