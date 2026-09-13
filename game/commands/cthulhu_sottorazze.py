"""
Comandi delle sottorazze permanenti (Fase G, ottava tornata): LICH,
VAMPIRE, WERE, LINEAGE, e il comando di staff SUBRACE per concederle (
vedi world/sottorazze.py per la logica e le citazioni della fonte
originale - in particolare il perche' non esiste un modo per un
giocatore di diventare una sottorazza da solo).
"""

import random

from evennia.commands.default.muxcommand import MuxCommand
from world.colori import orrore, pericolo

PROBABILITA_FUGA_GROWL = 40  # non specificato dalla fonte

from world.sottorazze import (
    NOMI_SOTTORAZZA, diventa_sottorazza, induce, moltiplicatore_generazione,
    spendi_pool, applica_buff_temporaneo, fase_lunare, luna_piena, lineage_di,
    guadagna_pool, vittima_vulnerabile_a_drenaggio, probabilita_dominate,
    were_puo_trasformarsi_a_volonta, tenta_bite,
)


class CmdSubrace(MuxCommand):
    """
    (staff) concede una sottorazza permanente a un personaggio

    Uso:
      subrace <personaggio> <lich/vampire/were>

    Nessuna pagina della fonte originale descrive un rituale o una
    quest per diventare la PRIMA volta membro di una sottorazza: qui e'
    un'azione riservata allo staff (i giocatori poi si espandono da
    soli con LICH BESTOW / VAMPIRE EMBRACE / WERE BITE).
    """

    key = "subrace"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        parti = self.args.split(None, 1) if self.args else []
        if len(parti) != 2 or parti[1].lower() not in NOMI_SOTTORAZZA:
            caller.msg("Uso: subrace <personaggio> <lich|vampire|were>")
            return
        bersaglio = caller.search(parti[0])
        if not bersaglio:
            return
        ok, messaggio = diventa_sottorazza(bersaglio, parti[1].lower())
        caller.msg(messaggio)
        if ok:
            bersaglio.msg(
                orrore(
                    f"Sei diventato/a {NOMI_SOTTORAZZA[parti[1].lower()]}: un cambiamento "
                    "permanente, senza ritorno."
                )
            )


class CmdLineage(MuxCommand):
    """
    mostra razza, sottorazza, generazione e ascendenza di tutti i connessi

    Uso:
      lineage

    Confermato dalla fonte (helps/lineage.txt): mostra TUTTI i
    personaggi attualmente connessi, non solo chi e' nella tua stanza.
    Chi ha attivato PRIVACY non compare nell'elenco di nessun altro.
    """

    key = "lineage"
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        from evennia.objects.models import ObjectDB
        personaggi = [
            o for o in ObjectDB.objects.filter(db_typeclass_path="typeclasses.characters.Character")
            if o.sessions.count() > 0 and not o.db.privacy_lineage
        ]
        if not personaggi:
            caller.msg("Non c'e' nessuno da mostrare al momento.")
            return
        righe = ["|wLignaggio dei personaggi connessi:|n"]
        righe += [f"  {lineage_di(p)}" for p in personaggi]
        caller.msg("\n".join(righe))


class CmdPrivacy(MuxCommand):
    """
    alterna se compari nell'elenco di LINEAGE altrui

    Uso:
      privacy

    Confermato dalla fonte (helps/lineage.txt): se non vuoi che queste
    informazioni siano mostrate, usa il comando PRIVACY per nasconderle.
    """

    key = "privacy"
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        caller.db.privacy_lineage = not caller.db.privacy_lineage
        stato = "attiva" if caller.db.privacy_lineage else "disattivata"
        caller.msg(f"Privacy ora {stato}: {'non comparirai' if caller.db.privacy_lineage else 'comparirai'} in LINEAGE.")


class CmdLich(MuxCommand):
    """
    comandi del Lich

    Uso:
      lich
      lich touch <vittima>
      lich dominate <npc>
      lich empower <quantita>
      lich strike <vittima> <quantita>
      lich enhance <quantita>
      lich bestow <vittima>
    """

    key = "lich"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if caller.db.sottorazza != "lich":
            caller.msg("Non sei un Lich.")
            return
        parti = self.args.split(None, 1) if self.args else []
        if not parti:
            caller.msg(
                f"Sei un Lich di generazione {caller.db.generazione}. "
                f"Potere: {caller.db.pool_sottorazza or 0}.\n"
                "Uso: lich touch/dominate/empower/strike/enhance/bestow ..."
            )
            return
        sotto, resto = parti[0].lower(), (parti[1] if len(parti) > 1 else "")

        if sotto == "touch":
            self._touch(caller, resto)
        elif sotto == "dominate":
            self._dominate(caller, resto)
        elif sotto == "empower":
            self._empower(caller, resto)
        elif sotto == "strike":
            self._strike(caller, resto)
        elif sotto == "enhance":
            self._enhance(caller, resto)
        elif sotto == "bestow":
            self._bestow(caller, resto)
        else:
            caller.msg("Sottocomando sconosciuto.")

    def _touch(self, caller, nome):
        vittima = caller.search(nome, quiet=True)
        vittima = vittima[0] if vittima else None
        if not vittima:
            caller.msg(f"Non vedi '{nome}' qui.")
            return
        if vittima.db.sottorazza in ("lich", "vampire"):
            caller.msg(f"{vittima.key} e' gia' non-morto/a: non ha mana da offrirti in questo modo.")
            return
        if not vittima_vulnerabile_a_drenaggio(vittima):
            caller.msg(f"{vittima.key} e' sveglio/a: puoi drenare mana solo da una vittima addormentata.")
            return
        mana = vittima.db.mana or 0
        if mana <= 0:
            caller.msg(f"{vittima.key} non ha mana da offrire.")
            return
        drenato = min(mana, int(10 * moltiplicatore_generazione(caller)))
        vittima.db.mana = mana - drenato
        guadagno = guadagna_pool(caller, drenato)
        caller.msg(f"Drenati {drenato} mana da {vittima.key} (potere ora {caller.db.pool_sottorazza}, +{guadagno}).")

    def _dominate(self, caller, nome):
        npc = caller.search(nome, quiet=True)
        npc = npc[0] if npc else None
        if not npc or not npc.is_typeclass("typeclasses.npcs.NPC", exact=False):
            caller.msg("Bersaglio non valido.")
            return
        if not npc.db.non_morto:
            caller.msg(f"{npc.key} non e' un non-morto.")
            return
        if npc.db.ostile:
            caller.msg(f"{npc.key} e' troppo ostile per essere dominato.")
            return
        percentuale = probabilita_dominate(caller, npc)
        if random.randint(1, 100) > percentuale:
            caller.msg(f"{npc.key} resiste alla tua volonta' di dominarlo.")
            return
        npc.db.dominato_da = caller.key
        caller.msg(f"{npc.key} si inchina alla tua volonta'.")

    def _empower(self, caller, testo):
        if not testo.strip().isdigit():
            caller.msg("Uso: lich empower <quantita>")
            return
        quantita = int(testo.strip())
        if not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza potere.")
            return
        durata = 20 + quantita
        bonus = max(1, int(quantita * moltiplicatore_generazione(caller) // 2))
        # helps/lich.txt: "empowers all of your spells" - agganciato
        # davvero alla percentuale di successo del lancio (vedi
        # world/magic.py:_completa_lancio) e al divieto di usare armi
        # (vedi typeclasses/living.py:calcola_hit_chance).
        applica_buff_temporaneo(
            caller, "bonus_incantesimi", bonus, durata,
            messaggio_scadenza="Il potere che avvolgeva i tuoi incantesimi svanisce.",
        )
        applica_buff_temporaneo(caller, "lich_empower_no_armi", 1, durata)
        caller.msg(
            f"I tuoi incantesimi si potenziano per {durata} secondi "
            "(non puoi impugnare armi finche' l'effetto e' attivo)."
        )

    def _strike(self, caller, resto):
        parti = resto.rsplit(None, 1)
        if len(parti) != 2 or not parti[1].isdigit():
            caller.msg("Uso: lich strike <vittima> <quantita>")
            return
        vittima = caller.search(parti[0], quiet=True)
        vittima = vittima[0] if vittima else None
        if not vittima:
            caller.msg(f"Non vedi '{parti[0]}' qui.")
            return
        quantita = int(parti[1])
        if not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza potere.")
            return
        danno = int(quantita * moltiplicatore_generazione(caller))
        caller.location.msg_contents(
            pericolo(f"{caller.key} scaglia potere grezzo contro {vittima.key} per {danno} danni!")
        )
        morto = vittima.subisci_danno(danno)
        if morto:
            from world.combat import gestisci_morte
            gestisci_morte(vittima, caller)

    def _enhance(self, caller, testo):
        if not testo.strip().isdigit():
            caller.msg("Uso: lich enhance <quantita>")
            return
        quantita = int(testo.strip())
        if not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza potere.")
            return
        durata = 20 + quantita
        bonus = max(1, int(quantita * moltiplicatore_generazione(caller) // 3))
        # helps/lich.txt: "enhances your intelligence and wisdom" -
        # distinto da EMPOWER, che invece potenzia gli incantesimi
        # stessi: qui si usano mod_temp_int/mod_temp_wis, gia' letti
        # da Character.valore_attributo() per altri incantesimi.
        applica_buff_temporaneo(caller, "mod_temp_int", bonus, durata,
                                 messaggio_scadenza="La tua mente torna alla sua acutezza normale.")
        applica_buff_temporaneo(caller, "mod_temp_wis", bonus, durata)
        caller.msg(f"La tua mente si acuisce per {durata} secondi (+{bonus} INT, +{bonus} WIS).")

    def _bestow(self, caller, nome):
        vittima = caller.search(nome, quiet=True)
        vittima = vittima[0] if vittima else None
        if not vittima:
            caller.msg(f"Non vedi '{nome}' qui.")
            return
        ok, messaggio = induce(caller, vittima, "lich")
        caller.msg(messaggio)


class CmdVampire(MuxCommand):
    """
    comandi del Vampiro

    Uso:
      vampire
      vampire suck <vittima>
      vampire fangs
      vampire mesmerize <npc> <comando>
      vampire enhance <sangue>
      vampire majesty <sangue>
      vampire mistform <sangue>
      vampire embrace <vittima>
    """

    key = "vampire"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if caller.db.sottorazza != "vampire":
            caller.msg("Non sei un Vampiro.")
            return
        parti = self.args.split(None, 1) if self.args else []
        if not parti:
            caller.msg(
                f"Sei un Vampiro di generazione {caller.db.generazione}. "
                f"Sangue: {caller.db.pool_sottorazza or 0}.\n"
                "Uso: vampire suck/fangs/mesmerize/enhance/majesty/mistform/embrace ..."
            )
            return
        sotto, resto = parti[0].lower(), (parti[1] if len(parti) > 1 else "")

        if sotto == "suck":
            self._suck(caller, resto)
        elif sotto == "fangs":
            self._fangs(caller)
        elif sotto == "mesmerize":
            self._mesmerize(caller, resto)
        elif sotto == "enhance":
            self._enhance(caller, resto)
        elif sotto == "majesty":
            self._majesty(caller, resto)
        elif sotto == "mistform":
            self._mistform(caller, resto)
        elif sotto == "embrace":
            self._embrace(caller, resto)
        else:
            caller.msg("Sottocomando sconosciuto.")

    def _suck(self, caller, nome):
        vittima = caller.search(nome, quiet=True)
        vittima = vittima[0] if vittima else None
        if not vittima:
            caller.msg(f"Non vedi '{nome}' qui.")
            return
        if not vittima_vulnerabile_a_drenaggio(vittima):
            caller.msg(f"{vittima.key} e' sveglio/a: puoi succhiare sangue solo da una vittima addormentata.")
            return
        divario = max(0, (vittima.livello_per_equip() if hasattr(vittima, "livello_per_equip") else 1)
                      - caller.livello_per_equip())
        prelievo = 10 + divario
        danno = max(1, prelievo // 5)
        vittima.subisci_danno(danno)
        guadagno = guadagna_pool(caller, prelievo)
        caller.location.msg_contents(pericolo(f"{caller.key} affonda i denti in {vittima.key}."))
        caller.msg(f"Sangue ora: {caller.db.pool_sottorazza} (+{guadagno}).")

    def _fangs(self, caller):
        caller.db.zanne_visibili = not caller.db.zanne_visibili
        if caller.db.zanne_visibili:
            caller.location.msg_contents(orrore(f"{caller.key} scopre due zanne affilate."))
        else:
            caller.location.msg_contents(orrore(f"{caller.key} nasconde le zanne."))

    def _mesmerize(self, caller, resto):
        parti = resto.split(None, 1)
        if len(parti) != 2:
            caller.msg("Uso: vampire mesmerize <npc> <comando>")
            return
        bersaglio = caller.search(parti[0], quiet=True)
        bersaglio = bersaglio[0] if bersaglio else None
        # per sicurezza, solo su NPC (mai su altri giocatori) e solo
        # comandi non distruttivi - scelta di design piu' prudente
        # della fonte, che teoricamente lo permetteva anche tra vampiri
        if not bersaglio or not bersaglio.is_typeclass("typeclasses.npcs.NPC", exact=False):
            caller.msg("Puoi ammaliare solo un NPC (per sicurezza, mai un altro giocatore).")
            return
        comando_sicuro = parti[1].split()[0].lower()
        if comando_sicuro not in ("say", "pose", "look", "dire", "posa", "guarda"):
            caller.msg("Puoi far fare all'NPC solo azioni innocue (say/pose/look).")
            return
        bersaglio.execute_cmd(parti[1])
        caller.msg(f"Ammalii {bersaglio.key}.")

    def _enhance(self, caller, testo):
        if not testo.strip().isdigit():
            caller.msg("Uso: vampire enhance <sangue>")
            return
        quantita = int(testo.strip())
        if not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza sangue.")
            return
        durata = 20 + quantita
        bonus = int(quantita * moltiplicatore_generazione(caller) // 5)
        applica_buff_temporaneo(caller, "bonus_colpire", bonus, durata,
                                messaggio_scadenza="Il vigore del sangue ti abbandona.")
        caller.msg(f"Forza e saggezza crescono in te per {durata} secondi.")

    def _majesty(self, caller, testo):
        if not testo.strip().isdigit():
            caller.msg("Uso: vampire majesty <sangue>")
            return
        quantita = int(testo.strip())
        if not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza sangue.")
            return
        durata = 15 + quantita
        # helps/vampires.txt: "granting protection and frightening some
        # creatures away" - "protezione" e' letta davvero da
        # world/equipment.py:classe_armatura_totale (prima un campo
        # mai controllato da nessuno).
        applica_buff_temporaneo(caller, "classe_armatura_maesta", quantita // 3, durata,
                                messaggio_scadenza="L'aura maestosa attorno a te svanisce.")
        caller.location.msg_contents(
            orrore(f"{caller.key} si avvolge in un'aura maestosa e terribile.")
        )
        from world.esperienza import livello_effettivo
        spaventati = []
        for presente in list(caller.location.contents):
            if (
                presente is not caller
                and presente.is_typeclass("typeclasses.npcs.NPC", exact=False)
                and getattr(presente, "vivo", False)
                and livello_effettivo(presente) < livello_effettivo(caller)
            ):
                if presente.db.combat_target is caller:
                    presente.ferma_combattimento()
                spaventati.append(presente)
        if spaventati:
            caller.location.msg_contents(
                orrore(f"{', '.join(p.key for p in spaventati)} indietreggia/no, terrorizzato/i.")
            )

    def _mistform(self, caller, testo):
        if not testo.strip().isdigit():
            caller.msg("Uso: vampire mistform <sangue>")
            return
        quantita = int(testo.strip())
        if not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza sangue.")
            return
        durata = 10 + quantita * 2
        caller.db.forma_nebbia = True
        caller.location.msg_contents(orrore(f"{caller.key} si dissolve in una nube di nebbia rossastra."))
        script = caller.scripts.add(
            "typeclasses.scripts.SottorazzaBuffExpireScript", key="buff_forma_nebbia"
        )
        script.db.campo = "forma_nebbia"
        script.db.valore_precedente = False
        script.db.messaggio_scadenza = "Riprendi forma corporea."
        # Fase K, ventiseiesima tornata: assegnare .interval come
        # attributo non riarma il timer di uno script gia' avviato da
        # .add() - va richiamato .start() esplicitamente (bug reale
        # scoperto testando dal vivo, vedi world/sottorazze.py:
        # applica_buff_temporaneo per lo stesso fix e la spiegazione).
        script.start(interval=durata, force_restart=True)

    def _embrace(self, caller, nome):
        vittima = caller.search(nome, quiet=True)
        vittima = vittima[0] if vittima else None
        if not vittima:
            caller.msg(f"Non vedi '{nome}' qui.")
            return
        ok, messaggio = induce(caller, vittima, "vampire")
        caller.msg(messaggio)


class CmdWere(MuxCommand):
    """
    comandi del Licantropo

    Uso:
      were
      were change
      were rage <lumen>
      were growl
      were desc <breve|lunga|descrizione> <testo>
      were bite <vittima>
      were fury <lumen>
      were heal [lumen]
      were regen <lumen>
      were sense
    """

    key = "were"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if caller.db.sottorazza != "were":
            caller.msg("Non sei un Licantropo.")
            return
        parti = self.args.split(None, 1) if self.args else []
        if not parti:
            forma = "animale" if caller.db.in_forma_animale else "umana"
            caller.msg(
                f"Sei un Licantropo di generazione {caller.db.generazione}, forma {forma}. "
                f"Lumen: {caller.db.pool_sottorazza or 0}.\n"
                "Uso: were change/rage/growl/desc/bite/fury/heal/regen/sense ..."
            )
            return
        sotto, resto = parti[0].lower(), (parti[1] if len(parti) > 1 else "")

        if sotto == "change":
            self._change(caller)
        elif sotto == "rage":
            self._rage(caller, resto)
        elif sotto == "growl":
            self._growl(caller)
        elif sotto == "desc":
            self._desc(caller, resto)
        elif sotto == "bite":
            self._bite(caller, resto)
        elif sotto == "fury":
            self._fury(caller, resto)
        elif sotto == "heal":
            self._heal(caller, resto)
        elif sotto == "regen":
            self._regen(caller, resto)
        elif sotto == "sense":
            self._sense(caller)
        else:
            caller.msg("Sottocomando sconosciuto.")

    def _change(self, caller):
        if caller.db.in_forma_animale:
            if luna_piena() or caller.db.in_rabbia:
                caller.msg("Qualcosa in te rifiuta di tornare umano finche' questo dura.")
                return
            caller.db.in_forma_animale = False
            if caller.db.maschera:
                caller.db.maschera = None
            caller.location.msg_contents(orrore(f"{caller.key} torna alla propria forma umana."))
        else:
            if not were_puo_trasformarsi_a_volonta(caller) and not luna_piena():
                # helps/weres.txt: "more experienced and powerful weres
                # can perform this change at will" - implica che gli
                # altri debbano aspettare la luna piena.
                caller.msg(
                    "Non sei ancora abbastanza esperto/a per trasformarti a volonta': "
                    "solo la luna piena potra' costringerti a cambiare."
                )
                return
            caller.db.in_forma_animale = True
            descrizioni = caller.db.were_desc or {}
            caller.db.maschera = descrizioni.get("breve", "una bestia selvaggia")
            caller.location.msg_contents(orrore(f"{caller.key} si trasforma in una bestia selvaggia!"))

    def _rage(self, caller, testo):
        if not caller.db.in_forma_animale:
            caller.msg("Devi essere in forma animale.")
            return
        quantita = int(testo) if testo.strip().isdigit() else 0
        if quantita and not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza lumen.")
            return
        durata = 15 + quantita
        caller.db.in_rabbia = True
        # helps/were.txt: "This increase is applied to your DR and HR"
        # (Damage Roll e Hit Roll) - prima solo l'HR (bonus_colpire) era
        # davvero applicato.
        applica_buff_temporaneo(caller, "bonus_colpire", 10 + quantita // 2, durata,
                                messaggio_scadenza="La furia dentro di te si placa.")
        applica_buff_temporaneo(caller, "bonus_danno_temp", 5 + quantita // 3, durata)
        script = caller.scripts.add(
            "typeclasses.scripts.SottorazzaBuffExpireScript", key="buff_in_rabbia"
        )
        script.db.campo = "in_rabbia"
        script.db.valore_precedente = False
        script.start(interval=durata, force_restart=True)
        caller.location.msg_contents(orrore(f"{caller.key} entra in una furia frenetica!"))

    def _growl(self, caller):
        if not caller.db.in_forma_animale:
            caller.msg("Devi essere in forma animale per ringhiare in modo credibile.")
            return
        caller.location.msg_contents(orrore(f"{caller.key} ringhia minacciosamente!"))
        # helps/were.txt: "Anyone nearby who hears your growling may
        # panic and run away in fear." Nessuna probabilita' esatta dalla
        # fonte: qui solo gli NPC piu' deboli del licantropo rischiano
        # di fuggire, coerente con lo stesso criterio di "creature piu'
        # deboli" gia' usato per VAMPIRE MAJESTY.
        from world.esperienza import livello_effettivo
        for presente in list(caller.location.contents):
            if (
                presente is not caller
                and presente.is_typeclass("typeclasses.npcs.NPC", exact=False)
                and getattr(presente, "vivo", False)
                and livello_effettivo(presente) < livello_effettivo(caller)
                and random.randint(1, 100) <= PROBABILITA_FUGA_GROWL
            ):
                if presente.db.combat_target is caller:
                    presente.ferma_combattimento()
                uscite = [e for e in (presente.location.exits or []) if not (e.db.chiusa)]
                if uscite:
                    presente.location.msg_contents(orrore(f"{presente.key} fugge terrorizzato/a!"))
                    presente.move_to(random.choice(uscite).destination, quiet=True)

    def _desc(self, caller, resto):
        parti = resto.split(None, 1)
        mappa = {"breve": "breve", "lunga": "lunga", "descrizione": "descrizione",
                 "short": "breve", "long": "lunga", "desc": "descrizione"}
        if len(parti) != 2 or parti[0].lower() not in mappa:
            caller.msg("Uso: were desc <breve/lunga/descrizione> <testo>")
            return
        descrizioni = caller.db.were_desc or {}
        descrizioni[mappa[parti[0].lower()]] = parti[1]
        caller.db.were_desc = descrizioni
        caller.msg(f"Descrizione '{parti[0]}' della forma animale aggiornata.")

    def _bite(self, caller, nome):
        vittima = caller.search(nome, quiet=True)
        vittima = vittima[0] if vittima else None
        if not vittima:
            caller.msg(f"Non vedi '{nome}' qui.")
            return
        ok, messaggio = induce(caller, vittima, "were")
        caller.msg(messaggio)

    def _fury(self, caller, testo):
        if not testo.strip().isdigit():
            caller.msg("Uso: were fury <lumen>")
            return
        quantita = int(testo.strip())
        if not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza lumen.")
            return
        durata = 15 + quantita
        # helps/were.txt: "boosted an amount appropriate to your
        # generation and lumen pool expenditure" - prima solo il lumen
        # speso contava, la generazione mai.
        bonus = int((5 + quantita // 3) * moltiplicatore_generazione(caller))
        applica_buff_temporaneo(caller, "bonus_colpire", bonus, durata,
                                messaggio_scadenza="Il vigore della furia si esaurisce.")
        caller.msg(f"Le tue capacita' di combattimento si acuiscono per {durata} secondi.")

    def _heal(self, caller, testo):
        base = max(1, caller.livello_per_equip() // 3)
        if not testo.strip():
            caller.msg(f"Il costo base per una guarigione completa e' {base} lumen.")
            return
        if not testo.strip().isdigit():
            caller.msg("Uso: were heal [lumen]")
            return
        quantita_richiesta = int(testo.strip())
        # helps/were.txt: "Any amount over the base is not spent" - bug
        # reale corretto: prima si spendeva SEMPRE quantita_richiesta
        # per intero, anche oltre base, pur limitando solo la percentuale
        # di guarigione risultante.
        quantita_da_spendere = min(quantita_richiesta, base)
        if not spendi_pool(caller, quantita_da_spendere):
            caller.msg("Non hai abbastanza lumen.")
            return
        percentuale = min(1.0, quantita_da_spendere / base) if base else 1.0
        recupero = int((caller.db.hp_max or 0) * 0.2 * percentuale)
        caller.db.hp = min(caller.db.hp_max, (caller.db.hp or 0) + recupero)
        caller.msg(f"Recuperi {recupero} HP (spesi {quantita_da_spendere} lumen).")

    def _regen(self, caller, testo):
        if not testo.strip().isdigit():
            caller.msg("Uso: were regen <lumen>")
            return
        quantita = int(testo.strip())
        if not spendi_pool(caller, quantita):
            caller.msg("Non hai abbastanza lumen.")
            return
        # helps/were.txt: "grants you a regeneration affect similar to
        # the regeneration spell" - prima impostava solo un flag
        # (rigenerazione_attiva) mai controllato da nessuna parte:
        # riusa lo stesso meccanismo REALE gia' funzionante
        # dell'incantesimo Rigenerazione (world/magic.py:_effetto_regeneration)
        # invece di duplicarne uno inerte.
        from world.effetti import applica_cura_periodica
        numero_tick = max(1, (10 + quantita * 2) // 10)
        applica_cura_periodica(caller, 5, 10, 10, numero_tick,
                                messaggio_tick="Ti senti rigenerare ({danno} HP).")
        caller.msg(f"Una rigenerazione attiva ti scorre addosso per {numero_tick * 10} secondi.")

    def _sense(self, caller):
        caller.msg(f"La luna e' attualmente: {fase_lunare()}.")


class CmdBite(MuxCommand):
    """
    attacca un bersaglio con le zanne (Vampiro)

    Uso:
      bite <bersaglio>

    Confermato dalla fonte (helps/bite.txt): comando di combattimento
    disponibile solo a chi ha le zanne fuori (VAMPIRE FANGS), basato
    sulla skill Corpo a Corpo indipendentemente da qualunque arma
    impugnata.
    """

    key = "bite"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: bite <bersaglio>")
            return
        vittima = caller.search(self.args.strip(), quiet=True)
        vittima = vittima[0] if vittima else None
        if not vittima:
            caller.msg(f"Non vedi '{self.args.strip()}' qui.")
            return
        ok, messaggio = tenta_bite(caller, vittima)
        if messaggio:
            caller.msg(messaggio)
