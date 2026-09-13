"""
Comandi PK/Criminale/Taglie&Missioni (Fase G, decima tornata): MURDER,
BOUNTY, MISSION, DELIVER. Vedi world/pk.py per la logica e le citazioni
della fonte originale.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.pk import (
    uccidi_o_murder, metti_taglia, paga_bribe, genera_missione,
    info_missione, tempo_missione, completa_missione, abort_missione,
    stato_missione, lista_mission_buy, mission_buy,
)


class CmdMurder(MuxCommand):
    """
    attacca un bersaglio anche se e' protetto (diventi un criminale)

    Uso:
      murder <bersaglio>

    Come KILL, ma funziona anche sugli NPC "protetti" (es. le forze
    dell'ordine): se il bersaglio era protetto, diventi un criminale -
    altri potranno mettere una taglia sulla tua testa.
    """

    key = "murder"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: murder <bersaglio>")
            return
        bersaglio = caller.search(self.args.strip())
        if not bersaglio:
            return
        if bersaglio == caller:
            caller.msg("Non puoi attaccare te stesso.")
            return
        if not hasattr(bersaglio, "avvia_combattimento"):
            caller.msg("Non puoi attaccare questo.")
            return

        ok, messaggio = uccidi_o_murder(caller, bersaglio, comando_murder=True)
        if not ok:
            caller.msg(messaggio)
            return

        caller.msg(f"Attacchi senza pieta' {bersaglio.key}!")
        caller.location.msg_contents(
            f"{caller.key} attacca senza pieta' {bersaglio.key}!", exclude=[caller]
        )
        caller.avvia_combattimento(bersaglio)


class CmdBounty(MuxCommand):
    """
    consulta o metti una taglia, o pagane il riscatto

    Uso:
      bounty
      bounty <giocatore> <importo>
      bounty bribe

    BOUNTY da solo mostra le taglie in corso. BOUNTY BRIBE toglie la
    taglia sulla TUA testa, ma costa il doppio del suo importo.
    """

    key = "bounty"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            self._lista(caller)
            return
        if self.args.strip().lower() == "bribe":
            ok, messaggio = paga_bribe(caller)
            caller.msg(messaggio)
            return

        parti = self.args.split()
        if len(parti) != 2 or not parti[1].isdigit():
            caller.msg("Uso: bounty <giocatore> <importo> | bounty bribe")
            return
        bersaglio = caller.search(parti[0])
        if not bersaglio:
            return
        ok, messaggio = metti_taglia(caller, bersaglio, int(parti[1]))
        caller.msg(messaggio)

    def _lista(self, caller):
        from evennia.objects.models import ObjectDB

        criminali = [
            p for p in ObjectDB.objects.filter(db_typeclass_path="typeclasses.characters.Character")
            if (p.db.taglia_oro or 0) > 0 and p.sessions.count() > 0
        ]
        if not criminali:
            caller.msg("Nessuna taglia in corso al momento (solo giocatori online, helps/bounty.txt).")
            return
        righe = ["Taglie in corso:"]
        for p in criminali:
            righe.append(f"  {p.key}: {p.db.taglia_oro} oro")
        caller.msg("\n".join(righe))


class CmdMission(MuxCommand):
    """
    gestisce le missioni della Gilda dei Cacciatori di Taglie

    Uso:
      mission request
      mission info
      mission time
      mission complete
      mission abort
      mission points
      mission list
      mission buy <oggetto>
    """

    key = "mission"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip() if self.args else ""
        sotto = args.split(None, 1)[0].lower() if args else ""

        if sotto == "request":
            ok, messaggio = genera_missione(caller)
            caller.msg(messaggio)
        elif sotto == "info":
            caller.msg(info_missione(caller))
        elif sotto == "time":
            caller.msg(f"{tempo_missione(caller)} secondi.")
        elif sotto == "complete":
            ok, messaggio = completa_missione(caller)
            caller.msg(messaggio)
        elif sotto == "abort":
            ok, messaggio = abort_missione(caller)
            caller.msg(messaggio)
        elif sotto == "points":
            caller.msg(f"Punti Fama: {caller.db.fame or 0}")
        elif sotto == "list":
            righe = ["In vendita all'Ufficio Taglie:"]
            for chiave, nome, costo in lista_mission_buy():
                righe.append(f"  {chiave:<10s} {nome:<15s} {costo} Fama")
            caller.msg("\n".join(righe))
        elif sotto == "buy":
            resto = args.split(None, 1)
            if len(resto) < 2:
                caller.msg("Uso: mission buy <oggetto> (vedi MISSION LIST)")
                return
            ok, messaggio = mission_buy(caller, resto[1].strip().lower())
            caller.msg(messaggio)
        else:
            caller.msg("Uso: mission request|info|time|complete|abort|points|list|buy")


class CmdDeliver(MuxCommand):
    """
    consegna un pacco a un destinatario (missione di corriere)

    Uso:
      deliver <npc>
    """

    key = "deliver"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: deliver <npc>")
            return
        missione = caller.db.missione
        if not missione or missione.get("tipo") != "corriere":
            caller.msg("Non hai un pacco da consegnare.")
            return

        pacco = next((o for o in caller.contents if o.db.pacco_missione_di == caller.key), None)
        if not pacco:
            caller.msg("Non hai piu' il pacco con te.")
            return

        destinatario = caller.search(self.args, quiet=True)
        destinatario = destinatario[0] if destinatario else None
        if not destinatario or not destinatario.is_typeclass("typeclasses.npcs.NPC", exact=False):
            caller.msg("Non vedi quel destinatario qui.")
            return

        pacco.delete()
        missione["pacco_consegnato"] = True
        caller.db.missione = missione
        caller.msg(f"Consegni il pacco a {destinatario.key}.")
        ok, messaggio = completa_missione(caller)
        if ok:
            caller.msg(messaggio)


def _toggle(caller, campo, nome_visualizzato):
    valore = not getattr(caller.db, campo)
    setattr(caller.db, campo, valore)
    stato = "attivo" if valore else "disattivo"
    caller.msg(f"{nome_visualizzato} ora {stato}.")


class CmdAutogold(MuxCommand):
    """
    alterna il prelievo automatico dell'oro dalle tue uccisioni

    Uso:
      autogold

    Semplificazione dichiarata (helps/autokill.txt): questo porting non
    ha mai fatto cadere oro dall'uccisione di un mostro (l'oro arriva
    solo da taglie/missioni - gia' dichiarato in world/gruppo.py). Il
    toggle e' tracciato e visibile in AUTOLIST, pronto per quando (e se)
    un sistema di bottino in oro verra' costruito - costruirlo ora
    sarebbe fuori scope per un audit di morte/cadaveri/PK.
    """
    key = "autogold"
    locks = "cmd:all()"

    def func(self):
        _toggle(self.caller, "autogold", "Autogold")


class CmdAutoloot(MuxCommand):
    """
    alterna il prelievo automatico dell'equipaggiamento dalle tue uccisioni

    Uso:
      autoloot

    Semplificazione dichiarata: gli NPC di questo porting non mettono
    ancora il proprio equipaggiamento nel cadavere alla morte (nessun
    sistema di bottino da mostri esiste ancora, vedi anche AUTOGOLD).
    Il toggle e' tracciato e visibile in AUTOLIST, pronto per quando
    (e se) tale sistema verra' costruito.
    """
    key = "autoloot"
    locks = "cmd:all()"

    def func(self):
        _toggle(self.caller, "autoloot", "Autoloot")


class CmdAutokill(MuxCommand):
    """
    alterna se tentare di uccidere (invece di stordire) i nemici in combattimento

    Uso:
      autokill

    Semplificazione dichiarata (helps/autokill.txt): questo porting non
    ha mai avuto una risoluzione di combattimento "stordisci senza
    uccidere" - lo stato del toggle e' tracciato e visibile in AUTOLIST,
    ma per ora non altera l'esito del combattimento (0 HP resta sempre
    morte reale, come in tutto il resto del gioco).
    """
    key = "autokill"
    locks = "cmd:all()"

    def func(self):
        _toggle(self.caller, "autokill", "Autokill")


class CmdNoloot(MuxCommand):
    """
    alterna se il tuo cadavere puo' essere saccheggiato

    Uso:
      noloot

    Il tuo cadavere e' gia' protetto di default (solo tu o il tuo
    gruppo potete frugarci dentro, helps/death.txt). NOLOOT attivo
    impedisce anche al TUO gruppo di farlo.
    """
    key = "noloot"
    locks = "cmd:all()"

    def func(self):
        _toggle(self.caller, "noloot", "Noloot")


class CmdAutosac(MuxCommand):
    """
    alterna il sacrificio automatico del cadavere delle tue uccisioni

    Uso:
      autosac

    Confermato dalla fonte (helps/autokill.txt/sacrifice.txt): richiede
    di adorare gia' una divinita' (WORSHIP <divinita>) - i sacrifici
    automatici non aumentano la tua pieta'.
    """
    key = "autosac"
    locks = "cmd:all()"

    def func(self):
        _toggle(self.caller, "autosac", "Autosac")


class CmdAutolist(MuxCommand):
    """
    mostra lo stato delle tue funzioni automatiche

    Uso:
      autolist
    """
    key = "autolist"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        campi = [
            ("autogold", "Autogold"), ("autoloot", "Autoloot"), ("autokill", "Autokill"),
            ("noloot", "Noloot"), ("autosac", "Autosac"), ("autosplit", "Autosplit"), ("autoassist", "Autoassist"),
        ]
        righe = ["Funzioni automatiche:"]
        for campo, nome in campi:
            stato = "attivo" if getattr(caller.db, campo) else "disattivo"
            righe.append(f"  {nome:<12s} {stato}")
        caller.msg("\n".join(righe))
