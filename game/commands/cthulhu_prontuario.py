"""
Prontuario dei comandi in italiano (fase 1 della traduzione
dell'interfaccia; vedi world/comandi_italiano.py per i nomi).

Non duplica nulla: il nome italiano viene dalla tabella degli alias, la
descrizione dalla prima riga della docstring del comando (gia' in
italiano in tutto il gioco) e la categoria da help_category. Se domani
si aggiunge un comando, compare qui da solo; se se ne cambia la
descrizione, cambia anche qui. Una sola fonte di verita'.

Complementa HELP, non lo sostituisce: HELP risponde su un comando alla
volta e mostra l'aiuto completo, il prontuario da' la mappa d'insieme -
che e' esattamente cio' che manca a chi si affaccia per la prima volta a
un gioco con centosessanta comandi.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.colori import ORRORE_MAGIA, AMBIENTE, RESET
from world.comandi_italiano import ALIAS_ITALIANI


def titolo(testo):
    """Intestazione di sezione, nella famiglia cromatica del Mythos
    gia' usata altrove (world/colori.py)."""
    linea = '-' * max(0, 68 - len(testo) - 3)
    return f'{ORRORE_MAGIA}--- {testo} {linea}{RESET}'


def evidenzia(testo):
    """Nome di comando: bianco acceso, per staccarlo dalla descrizione."""
    return f'|w{testo}|n'


# Nomi leggibili delle categorie di aiuto, e ordine in cui presentarle:
# prima cio' che serve a chi gioca, poi cio' che serve a chi amministra.
CATEGORIE = [
    ("general", "Generale"),
    ("cthulhumud", "Avventura"),
    ("comunicazioni", "Comunicazione"),
    ("staff", "Staff"),
    ("amministrazione", "Amministrazione"),
    ("costruzione", "Costruzione"),
    ("building", "Costruzione (Evennia)"),
]


def _descrizione(cmd):
    """Prima riga non vuota della docstring del comando."""
    for riga in (cmd.__doc__ or "").splitlines():
        riga = riga.strip()
        if riga:
            return riga
    return ""


def _nome_italiano(cmd):
    """Il nome italiano del comando, se ce n'e' uno.

    Prima cerca nella tabella degli alias; se il comando non c'e',
    puo' essere uno di quelli gia' italiani di loro (il nome principale
    o un alias aggiunto a mano prima di questa tabella)."""
    dalla_tabella = ALIAS_ITALIANI.get(cmd.key)
    if dalla_tabella:
        return dalla_tabella[0]
    from world.comandi_italiano import GIA_ITALIANI
    if cmd.key in GIA_ITALIANI:
        # il nome principale e' gia' italiano (es. ALLOGGIA), oppure lo
        # e' il primo alias (es. BUY -> COMPRA)
        for alias in (cmd.aliases or []):
            if alias not in ("?", ".", "+", "-", "&", ":", '"', "'") and len(alias) > 2:
                return alias
        return cmd.key
    return ""


def _comandi_visibili(caller):
    """I comandi che questo personaggio puo' davvero usare, esclusi i
    social (sono 204 e hanno un elenco a parte) e i comandi @ di Evennia."""
    from world.socials import SOCIALS

    social = set(SOCIALS)
    visti = {}
    for cmdset in caller.cmdset.all():
        for cmd in cmdset.commands:
            if cmd.key in social or cmd.key.startswith("@"):
                continue
            if not cmd.access(caller, "cmd"):
                continue
            visti[cmd.key] = cmd
    return visti


class CmdComandi(MuxCommand):
    """
    elenco di tutti i comandi, in italiano

    Uso:
      comandi                  le categorie disponibili
      comandi <categoria>      i comandi di una categoria
      comandi tutto            l'elenco completo
      comandi cerca <parola>   cerca fra nomi e descrizioni

    Per ogni comando mostra il nome italiano, quello originale inglese e
    una riga di descrizione. Entrambi i nomi funzionano in gioco: sono
    lo stesso comando.

    Per l'aiuto completo di un singolo comando usa invece HELP <nome>.
    I social (abbracciare, sorridere, ...) non compaiono qui: sono oltre
    duecento e si consultano con HELP.
    """

    key = "comandi"
    aliases = ["prontuario"]
    locks = "cmd:all()"
    help_category = "Generale"

    def _riga(self, cmd):
        it = _nome_italiano(cmd)
        desc = _descrizione(cmd)
        if it and it != cmd.key:
            nome = f"{evidenzia(it)} |x({cmd.key})|n"
            larghezza = len(it) + len(cmd.key) + 3
        else:
            nome = evidenzia(cmd.key)
            larghezza = len(cmd.key)
        riempi = " " * max(1, 30 - larghezza)
        return f"  {nome}{riempi}{desc}"

    def func(self):
        caller = self.caller
        arg = self.args.strip().lower()
        comandi = _comandi_visibili(caller)

        per_categoria = {}
        for cmd in comandi.values():
            per_categoria.setdefault((cmd.help_category or "general").lower(), []).append(cmd)

        # --- ricerca -----------------------------------------------------
        if arg.startswith("cerca"):
            chiave = arg[5:].strip()
            if not chiave:
                caller.msg("Cosa cerco? Uso: comandi cerca <parola>")
                return
            trovati = []
            for cmd in comandi.values():
                nomi = " ".join([cmd.key, _nome_italiano(cmd)] + list(cmd.aliases or []))
                if chiave in nomi.lower() or chiave in _descrizione(cmd).lower():
                    trovati.append(cmd)
            if not trovati:
                caller.msg(f"Nessun comando corrisponde a '{chiave}'.")
                return
            righe = [titolo(f"Comandi che corrispondono a '{chiave}' ({len(trovati)})")]
            righe += [self._riga(c) for c in sorted(trovati, key=lambda x: x.key)]
            caller.msg("\n".join(righe))
            return

        # --- elenco completo ---------------------------------------------
        if arg in ("tutto", "tutti"):
            righe = [titolo(f"Tutti i comandi ({len(comandi)})")]
            for chiave, etichetta in CATEGORIE:
                gruppo = per_categoria.get(chiave)
                if not gruppo:
                    continue
                righe.append("")
                righe.append(titolo(etichetta))
                righe += [self._riga(c) for c in sorted(gruppo, key=lambda x: x.key)]
            caller.msg("\n".join(righe))
            return

        # --- una categoria -----------------------------------------------
        if arg:
            scelta = None
            for chiave, etichetta in CATEGORIE:
                if arg in (chiave, etichetta.lower()) or etichetta.lower().startswith(arg):
                    scelta = (chiave, etichetta)
                    break
            if not scelta:
                caller.msg(f"Categoria sconosciuta: '{arg}'. Scrivi COMANDI per vedere quali ci sono.")
                return
            chiave, etichetta = scelta
            gruppo = per_categoria.get(chiave, [])
            righe = [titolo(f"{etichetta} ({len(gruppo)} comandi)")]
            righe += [self._riga(c) for c in sorted(gruppo, key=lambda x: x.key)]
            righe.append("")
            righe.append("Per l'aiuto completo di un comando: |wHELP <nome>|n")
            caller.msg("\n".join(righe))
            return

        # --- indice delle categorie ---------------------------------------
        righe = [titolo("Prontuario dei comandi")]
        righe.append("")
        righe.append("Ogni comando si puo' scrivere in italiano o in inglese: sono")
        righe.append("lo stesso comando. Qui sotto le categorie disponibili.")
        righe.append("")
        for chiave, etichetta in CATEGORIE:
            gruppo = per_categoria.get(chiave)
            if not gruppo:
                continue
            esempi = []
            for cmd in sorted(gruppo, key=lambda x: x.key):
                # ripiego sul nome inglese per i pochi comandi senza nome
                # italiano (interni di Evennia, nomi propri): meglio un
                # esempio in inglese che una parentesi vuota.
                esempi.append(_nome_italiano(cmd) or cmd.key)
                if len(esempi) >= 4:
                    break
            righe.append(f"  {evidenzia(etichetta.lower()):<32} {len(gruppo):>3} comandi   "
                         f"|x(es. {', '.join(esempi)})|n")
        righe.append("")
        righe.append("  |wcomandi <categoria>|n   i comandi di quella categoria")
        righe.append("  |wcomandi tutto|n         l'elenco completo")
        righe.append("  |wcomandi cerca <parola>|n  cerca fra nomi e descrizioni")
        righe.append("")
        righe.append("I social (sorridere, abbracciare, ...) sono oltre duecento e non")
        righe.append("compaiono qui: si consultano con |wHELP|n.")
        caller.msg("\n".join(righe))
