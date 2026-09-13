"""
Comandi di compravendita (Fase F, prima tornata): list/lista, buy/compra,
sell/vendi. Funzionano cercando un mercante (NPC con db.negozio
impostato, vedi world/economia.py) nella stanza attuale.

Fase K, quindicesima tornata: LIST/BUY/SELL rispettano ora gli orari
di apertura (world/tempo.py) - confermato dalla fonte, che elenca
HOURS/LIST/APPRAISE/BUY/SELL come un unico gruppo di comandi negozio
(helps/buy.txt/list.txt/sell.txt). HOURS stesso (commands/
cthulhu_tempo.py) resta sempre disponibile, per poter controllare
quando il negozio riapre.
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.economia import trova_mercante
from world.tempo import negozio_aperto


class CmdList(MuxCommand):
    """
    mostra la merce in vendita da un mercante

    Uso:
      list
      lista

    Se nella stanza e' presente un mercante, mostra cosa vende e a
    quale prezzo in Oro.
    """

    key = "list"
    aliases = ["lista"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        mercante = trova_mercante(caller.location) if caller.location else None
        if not mercante:
            caller.msg("Non c'e' nessun mercante qui.")
            return
        if not negozio_aperto(caller.location):
            caller.msg(f"{mercante.key} ha chiuso bottega. Usa HOURS per sapere quando riapre.")
            return

        righe = [f"|w{mercante.key} vende:|n"]
        for voce in mercante.db.negozio:
            righe.append(f"  {voce['chiave']:<20s} {voce['nome']:<40s} {voce['prezzo']} oro")
        caller.msg("\n".join(righe))


class CmdBuy(MuxCommand):
    """
    compra un oggetto da un mercante

    Uso:
      buy <chiave>
      compra <chiave>

    Compra l'oggetto <chiave> dal mercante presente nella stanza, se
    hai abbastanza Oro. Usa list/lista per vedere cosa e' in vendita.
    """

    key = "buy"
    aliases = ["compra"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: buy <chiave> (vedi 'list' per la merce disponibile)")
            return

        mercante = trova_mercante(caller.location) if caller.location else None
        if not mercante:
            caller.msg("Non c'e' nessun mercante qui.")
            return
        if not negozio_aperto(caller.location):
            caller.msg(f"{mercante.key} ha chiuso bottega. Usa HOURS per sapere quando riapre.")
            return

        chiave = self.args.strip().lower()
        voce = next((v for v in mercante.db.negozio if v["chiave"] == chiave), None)
        if not voce:
            caller.msg(f"{mercante.key} non vende nulla chiamato '{chiave}'.")
            return

        oro = caller.db.gold or 0
        if oro < voce["prezzo"]:
            caller.msg(
                f"Non hai abbastanza oro per {voce['nome']} "
                f"({voce['prezzo']} oro, ne hai {oro})."
            )
            return

        caller.db.gold = oro - voce["prezzo"]

        oggetto = create_object_from_voce(voce, caller)
        caller.msg(f"Compri {oggetto.name} per {voce['prezzo']} oro.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} compra {oggetto.name} da {mercante.key}.",
                exclude=caller,
            )


class CmdSell(MuxCommand):
    """
    vendi un oggetto a un mercante

    Uso:
      sell <oggetto>
      vendi <oggetto>

    Vende l'oggetto al mercante presente nella stanza, per meta' del
    suo valore originale. Funziona solo con oggetti che hanno un
    valore in oro assegnato (di norma, quelli comprati da un
    mercante).
    """

    key = "sell"
    aliases = ["vendi"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uso: sell <oggetto>")
            return

        mercante = trova_mercante(caller.location) if caller.location else None
        if not mercante:
            caller.msg("Non c'e' nessun mercante qui.")
            return
        if not negozio_aperto(caller.location):
            caller.msg(f"{mercante.key} ha chiuso bottega. Usa HOURS per sapere quando riapre.")
            return

        oggetto = caller.search(self.args, location=caller, quiet=True)
        oggetto = oggetto[0] if oggetto else None
        if not oggetto:
            caller.msg(f"Non hai '{self.args}'.")
            return

        valore = oggetto.db.valore
        if not valore:
            caller.msg(f"{mercante.key} non e' interessato a {oggetto.name}.")
            return

        prezzo_vendita = max(1, valore // 2)
        caller.db.gold = (caller.db.gold or 0) + prezzo_vendita
        caller.msg(f"Vendi {oggetto.name} per {prezzo_vendita} oro.")
        oggetto.delete()


# Chiavi opzionali (equipaggiamento o cibo/bevanda) che una "voce" di
# negozio puo' portare (vedi world/equipment.py e world/sopravvivenza.py):
# copiate sull'oggetto solo se presenti, cosi' i negozi che vendono pura
# ambientazione non cambiano.
_CHIAVI_EQUIPAGGIAMENTO = (
    "slot", "tipo_arma", "dado_min", "dado_max", "bonus_danno",
    "classe_armatura", "livello", "bonus_livello_equip",
    "cibo", "bevanda", "materiale_forgiatura",
)


def create_object_from_voce(voce, caller):
    """Crea l'oggetto acquistato nell'inventario del compratore. Se la
    voce ha "luce": True (Fase K, sedicesima tornata - torce/lanterne/
    candele gia' in vendita in alcuni negozi, mai state oggetti-luce
    veri finora), usa typeclasses.objects.OggettoLuce invece del
    generico Object, cosi' si accende/spegne da sola tenendola/
    lasciandola (vedi world/illuminazione.py)."""
    from evennia.utils import create
    from world.equipment import CONDIZIONE_INIZIALE

    typeclass = "typeclasses.objects.OggettoLuce" if voce.get("luce") else "typeclasses.objects.Object"
    oggetto = create.create_object(
        typeclass,
        key=voce["nome"],
        location=caller,
    )
    oggetto.db.desc = voce.get("descrizione", "")
    oggetto.db.valore = voce["prezzo"]
    for chiave in _CHIAVI_EQUIPAGGIAMENTO:
        if chiave in voce:
            oggetto.attributes.add(chiave, voce[chiave])
    if "slot" in voce:
        oggetto.db.condizione = CONDIZIONE_INIZIALE
    return oggetto
