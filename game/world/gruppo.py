"""
FOLLOW/GROUP (Fase K, tredicesima tornata). Confermato dalla fonte
(helps/follow.txt, unica pagina condivisa da FOLLOW/GROUP/NOFOLLOW):

    "The FOLLOW command will force your character to tag along behind
    another character, following them from room to room. To stop
    following someone else, simply FOLLOW yourself. The GROUP command
    forms a single fighting group with a player who is following you.
    Characters who fight in a group fight combine their various
    strengths into a more powerful fighting force, share the experience
    from killing, and may communicate with each other with the GTELL
    command. The SPLIT command divides up any money that is taken from
    dead monsters amongst your group, but you can set this action to
    occur automatically with the AUTOSPLIT option. If one member of the
    group is attacked, all the members of the group will automatically
    join the fight (assuming that the characters have the AUTOASSIST
    option toggled). The GROUP command will also boot a character out of
    your group, or they can leave voluntarily by using the FOLLOW
    command. The GROUP command by itself will display the basic
    statistics of everyone currently in your group. In addition, the
    NOFOLLOW command will stop someone who currently follows you from
    following you and prevent you from getting new followers. Typing it
    again will toggle the setting back to allow you to have followers."

Modello dati (tutto su typeclasses.characters.Character):
- db.seguendo: chi sto seguendo (FOLLOW), None se nessuno.
- db.seguaci_giocatori: chi mi segue.
- db.leader_gruppo: il leader del MIO gruppo se sono un membro (non il
  leader stesso). None se non sono in un gruppo, o se sono io il leader.
- db.membri_gruppo: (solo se sono leader) la lista degli altri membri.
- db.non_accetta_seguaci: NOFOLLOW senza argomento (toggle).
- db.autoassist / db.autosplit: le due opzioni AUTO citate dalla fonte
  (helps/auto.txt) specificamente per il gruppo.

Semplificazione dichiarata: SPLIT/AUTOSPLIT nella fonte dividono "il
denaro preso dai mostri morti" - ma questo porting non ha mai
implementato un drop di oro automatico dall'uccisione di un mostro
(l'oro arriva solo da taglie/missioni, vedi world/pk.py): costruire
quel sistema sarebbe andato ben oltre lo scope di FOLLOW/GROUP. SPLIT
qui divide semplicemente l'oro attualmente posseduto dal chiamante tra
i membri del gruppo presenti - AUTOSPLIT resta un interruttore pronto
per quando (e se) un sistema di bottino in oro verra' costruito.
"Combinano le proprie forze in una forza da combattimento piu'
potente" non ha una formula nella fonte: qui e' un piccolo bonus a
colpire per ogni altro membro del gruppo vivo presente nella stanza
(world/gruppo.py:bonus_gruppo_colpire), scelta di design dichiarata.
"""


def _leader_di(personaggio):
    """Ritorna il leader del gruppo di personaggio (se stesso, se e'
    lui il leader), o None se non e' in nessun gruppo."""
    if personaggio.db.membri_gruppo:
        return personaggio
    if personaggio.db.leader_gruppo and personaggio.db.leader_gruppo.pk:
        return personaggio.db.leader_gruppo
    return None


def membri_gruppo(personaggio):
    """Lista completa del gruppo di personaggio (leader incluso),
    lista vuota se non e' in nessun gruppo."""
    leader = _leader_di(personaggio)
    if not leader:
        return []
    membri = [m for m in (leader.db.membri_gruppo or []) if m.pk]
    return [leader] + membri


def bonus_gruppo_colpire(personaggio):
    """+2 a colpire per ogni altro membro del gruppo vivo presente
    nella stessa stanza - vedi nota di modulo su "una forza da
    combattimento piu' potente" (nessuna formula nella fonte)."""
    gruppo = membri_gruppo(personaggio)
    if not gruppo:
        return 0
    alleati_presenti = [
        m for m in gruppo
        if m is not personaggio and m.location == personaggio.location and getattr(m, "vivo", False)
    ]
    return 2 * len(alleati_presenti)


def sposta_seguaci_giocatori(personaggio):
    """Da chiamare quando personaggio cambia stanza: chi lo segue con
    FOLLOW lo segue automaticamente."""
    seguaci = [s for s in (personaggio.db.seguaci_giocatori or []) if s.pk]
    for seguace in seguaci:
        if seguace.location != personaggio.location:
            seguace.move_to(personaggio.location, quiet=True, move_type="follow")
    if seguaci != (personaggio.db.seguaci_giocatori or []):
        personaggio.db.seguaci_giocatori = seguaci


def tenta_follow(personaggio, testo):
    """FOLLOW <bersaglio> / FOLLOW se stesso (per smettere). Ritorna
    (ok, messaggio)."""
    if not testo:
        return False, "Uso: follow <personaggio>"
    testo = testo.strip().lower()
    if testo in ("me", "self", personaggio.key.lower()):
        vecchio = personaggio.db.seguendo
        if not vecchio or not vecchio.pk:
            return False, "Non stai seguendo nessuno."
        seguaci = [s for s in (vecchio.db.seguaci_giocatori or []) if s is not personaggio]
        vecchio.db.seguaci_giocatori = seguaci
        personaggio.db.seguendo = None
        return True, f"Smetti di seguire {vecchio.key}."

    bersaglio = personaggio.search(testo)
    if not bersaglio:
        return False, None
    if bersaglio is personaggio:
        return False, "Non puoi seguire te stesso/a."
    if not hasattr(bersaglio, "db") or not hasattr(bersaglio, "livello_per_equip"):
        return False, f"Non puoi seguire {bersaglio.key}."
    if bersaglio.db.non_accetta_seguaci:
        return False, f"{bersaglio.key} non accetta nuovi seguaci al momento."

    vecchio = personaggio.db.seguendo
    if vecchio and vecchio.pk:
        vecchio.db.seguaci_giocatori = [s for s in (vecchio.db.seguaci_giocatori or []) if s is not personaggio]

    seguaci = bersaglio.db.seguaci_giocatori or []
    if personaggio not in seguaci:
        seguaci.append(personaggio)
    bersaglio.db.seguaci_giocatori = seguaci
    personaggio.db.seguendo = bersaglio
    return True, f"Ora segui {bersaglio.key}."


def tenta_nofollow(personaggio, testo):
    """NOFOLLOW (da solo, toggle) / NOFOLLOW <seguace> (lo scaccia
    senza attivare il toggle). Ritorna (ok, messaggio)."""
    testo = (testo or "").strip()
    if not testo:
        personaggio.db.non_accetta_seguaci = not personaggio.db.non_accetta_seguaci
        if personaggio.db.non_accetta_seguaci:
            for seguace in list(personaggio.db.seguaci_giocatori or []):
                seguace.db.seguendo = None
                seguace.msg(f"{personaggio.key} non accetta piu' seguaci: smetti di seguirlo/a.")
            personaggio.db.seguaci_giocatori = []
            return True, "Non accetti piu' nuovi seguaci (i seguaci attuali sono stati congedati)."
        return True, "Torni ad accettare seguaci."

    bersaglio = personaggio.search(testo)
    if not bersaglio:
        return False, None
    seguaci = personaggio.db.seguaci_giocatori or []
    if bersaglio not in seguaci:
        return False, f"{bersaglio.key} non ti sta seguendo."
    personaggio.db.seguaci_giocatori = [s for s in seguaci if s is not bersaglio]
    bersaglio.db.seguendo = None
    bersaglio.msg(f"{personaggio.key} ti allontana: smetti di seguirlo/a.")
    return True, f"Allontani {bersaglio.key}."


def _rimuovi_dal_gruppo(membro):
    leader = membro.db.leader_gruppo
    if leader and leader.pk:
        leader.db.membri_gruppo = [m for m in (leader.db.membri_gruppo or []) if m is not membro]
    membro.db.leader_gruppo = None


def tenta_group(personaggio, testo):
    """GROUP (mostra) / GROUP <bersaglio> (aggiunge se ti sta seguendo,
    espelle se e' gia' nel gruppo). Ritorna (ok, messaggio)."""
    testo = (testo or "").strip()
    if not testo:
        gruppo = membri_gruppo(personaggio)
        if not gruppo:
            return True, "Non fai parte di nessun gruppo."
        righe = ["Il tuo gruppo:"]
        for membro in gruppo:
            righe.append(f"  {membro.key} - HP {membro.db.hp}/{membro.db.hp_max}, Mana {membro.db.mana}/{membro.db.mana_max}")
        return True, "\n".join(righe)

    bersaglio = personaggio.search(testo)
    if not bersaglio:
        return False, None

    # sono io il leader? (o lo divento ora, se ho gia' qualcuno che mi segue)
    leader = personaggio if not personaggio.db.leader_gruppo else None
    if not leader:
        return False, "Solo il leader di un gruppo puo' aggiungere o espellere membri."

    if bersaglio.db.leader_gruppo is personaggio:
        _rimuovi_dal_gruppo(bersaglio)
        bersaglio.msg(f"{personaggio.key} ti espelle dal gruppo.")
        return True, f"Espelli {bersaglio.key} dal gruppo."

    if bersaglio not in (personaggio.db.seguaci_giocatori or []):
        return False, f"{bersaglio.key} deve prima seguirti (FOLLOW) per unirsi al tuo gruppo."
    if bersaglio.db.leader_gruppo:
        return False, f"{bersaglio.key} fa gia' parte di un altro gruppo."

    membri = personaggio.db.membri_gruppo or []
    membri.append(bersaglio)
    personaggio.db.membri_gruppo = membri
    bersaglio.db.leader_gruppo = personaggio
    bersaglio.msg(f"{personaggio.key} ti aggiunge al gruppo.")
    return True, f"{bersaglio.key} si unisce al tuo gruppo."


def gtell(personaggio, testo):
    """GTELL <messaggio>: comunica con tutto il gruppo. Ritorna
    (ok, messaggio)."""
    if not testo:
        return False, "Uso: gtell <messaggio>"
    gruppo = membri_gruppo(personaggio)
    if not gruppo:
        return False, "Non fai parte di nessun gruppo."
    for membro in gruppo:
        if membro is not personaggio:
            membro.msg(f"|c[gruppo] {personaggio.key}:|n {testo}")
    return True, f"|c[gruppo] tu:|n {testo}"


def dividi_oro(personaggio):
    """SPLIT: divide l'oro attualmente posseduto dal chiamante tra i
    membri del gruppo presenti nella stessa stanza (chiamante incluso).
    Ritorna (ok, messaggio)."""
    gruppo = [m for m in membri_gruppo(personaggio) if m.location == personaggio.location]
    if len(gruppo) <= 1:
        return False, "Non hai nessun compagno di gruppo qui con cui dividere l'oro."
    oro = personaggio.db.gold or 0
    if oro <= 0:
        return False, "Non hai oro da dividere."
    quota = oro // len(gruppo)
    if quota <= 0:
        return False, "Hai troppo poco oro per dividerlo tra tutti."
    personaggio.db.gold = oro - quota * (len(gruppo) - 1)
    for membro in gruppo:
        if membro is not personaggio:
            membro.db.gold = (membro.db.gold or 0) + quota
            membro.msg(f"{personaggio.key} divide il bottino: ricevi {quota} oro.")
    return True, f"Dividi {quota} oro a testa tra i {len(gruppo)} membri del gruppo presenti."


def condividi_xp_gruppo(uccisore, xp):
    """Se uccisore e' in un gruppo, l'XP viene divisa tra i membri
    presenti nella stessa stanza (uccisore incluso) invece di andare
    tutta a lui - confermato qualitativamente dalla fonte ("share the
    experience from killing"), formula di divisione non specificata:
    scelta di design esplicita (divisione equa)."""
    gruppo = [m for m in membri_gruppo(uccisore) if m.location == uccisore.location]
    if len(gruppo) <= 1:
        return {uccisore: xp}
    quota = max(1, xp // len(gruppo))
    return {membro: quota for membro in gruppo}


def assist_automatico(vittima, attaccante):
    """Se vittima e' in un gruppo, i membri presenti con AUTOASSIST
    attivo si uniscono automaticamente al combattimento contro
    attaccante - confermato dalla fonte."""
    gruppo = membri_gruppo(vittima)
    for membro in gruppo:
        if (
            membro is not vittima
            and membro.location == vittima.location
            and membro.db.autoassist
            and getattr(membro, "vivo", False)
            and not membro.db.combat_target
        ):
            membro.location.msg_contents(f"{membro.key} si lancia in aiuto di {vittima.key}!")
            membro.avvia_combattimento(attaccante)
