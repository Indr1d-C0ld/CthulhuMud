"""
Comando CLAN (Fase G, settima tornata; completato nella ventiseiesima
tornata). Appartenenza e ruoli nelle Societies/Clan. Vedi
world/societies.py per la logica, le citazioni della fonte, e la nota
su cosa e' stato deliberatamente lasciato fuori scope (l'intera suite
di governance/economia di clan, e la fondazione/potenziamento
self-service, infedele alla fonte).
"""

from evennia.commands.default.muxcommand import MuxCommand

from world.societies import (
    SOCIETA, nome_societa, NOMI_RANGO, SCALA_RANGHI,
    RANGO_INVITATO, RANGO_MEMBRO, RANGO_CONSIGLIO, RANGO_LEADER,
    ha_rango, rango_in, societa_di, unisciti, lascia, leader_reale, membri_di,
)


class CmdClan(MuxCommand):
    """
    gestisce l'appartenenza e il ruolo nelle societa'/clan

    Uso:
      clan
      clan list
      clan info <societa>
      clan members <societa>
      clan research <personaggio>
      clan tell <societa> <messaggio>
      clan invite <personaggio> <societa>    (richiede rango consiglio+)
      clan promote <personaggio> <societa>   (richiede rango leader)
      clan demote <personaggio> <societa>    (richiede rango leader)
      clan expel <personaggio> <societa>     (richiede rango leader)
      clan leave <societa>

    Un personaggio puo' appartenere a piu' societa' contemporaneamente
    (confermato dalla fonte). Fondare un nuovo clan o acquistarne i
    potenziamenti non e' un comando in gioco: nell'originale richiede
    l'approvazione dello staff Immortal (vedi world/societies.py).
    """

    key = "clan"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        parti = self.args.strip().split(None, 1) if self.args else []
        sotto = parti[0].lower() if parti else ""
        resto = parti[1] if len(parti) > 1 else ""

        if not sotto:
            self._mio_stato(caller)
        elif sotto == "list":
            self._lista(caller)
        elif sotto == "info":
            self._info(caller, resto)
        elif sotto == "members":
            self._members(caller, resto)
        elif sotto == "research":
            self._research(caller, resto)
        elif sotto == "tell":
            self._tell(caller, resto)
        elif sotto == "invite":
            self._invita(caller, resto)
        elif sotto == "promote":
            self._promuovi(caller, resto)
        elif sotto == "demote":
            self._degrada(caller, resto)
        elif sotto == "expel":
            self._espelli(caller, resto)
        elif sotto == "leave":
            self._lascia(caller, resto)
        elif sotto == "induct" and caller.check_permstring("Builder"):
            self._induct(caller, resto)
        else:
            caller.msg(
                "Uso: clan | clan list | clan info/members <societa> | clan research <personaggio> | "
                "clan tell <societa> <messaggio> | clan invite/promote/demote/expel <personaggio> <societa> | "
                "clan leave <societa>"
            )

    def _mio_stato(self, caller):
        ranghi = societa_di(caller)
        if not ranghi:
            caller.msg("Non fai parte di nessuna societa'/clan.")
            return
        righe = ["Fai parte di:"]
        for sid, rango in ranghi.items():
            righe.append(f"  {nome_societa(sid)} - {NOMI_RANGO.get(rango, 'sconosciuto')}")
        caller.msg("\n".join(righe))

    def _lista(self, caller):
        righe = ["Societa'/clan pubblici conosciuti:"]
        for sid, dati in SOCIETA.items():
            reale = leader_reale(sid)
            leader = reale.key if reale else (dati["leader"] or "attualmente inattivo")
            righe.append(f"  {dati['nome']} - guidato da {leader}")
        righe.append("")
        righe.append("(Esistono anche clan segreti, non elencati pubblicamente.)")
        caller.msg("\n".join(righe))

    def _info(self, caller, nome):
        sid = self._trova(nome)
        if not sid:
            caller.msg("Societa' sconosciuta.")
            return
        dati = SOCIETA[sid]
        reale = leader_reale(sid)
        leader = reale.key if reale else (dati["leader"] or "attualmente inattivo")
        caller.msg(f"|w{dati['nome']}|n\n\n{dati['descrizione']}\n\nGuidato da: {leader}")

    def _members(self, caller, nome):
        sid = self._trova(nome)
        if not sid:
            caller.msg("Uso: clan members <societa>")
            return
        membri = membri_di(sid)
        if not membri:
            caller.msg(f"{nome_societa(sid)} non ha ancora membri registrati in gioco.")
            return
        righe = [f"Membri di {nome_societa(sid)}:"]
        for m in sorted(membri, key=lambda p: -rango_in(p, sid)):
            righe.append(f"  {m.key} - {NOMI_RANGO.get(rango_in(m, sid), '?')}")
        caller.msg("\n".join(righe))

    def _research(self, caller, nome):
        if not nome.strip():
            caller.msg("Uso: clan research <personaggio>")
            return
        bersaglio = caller.search(nome.strip(), quiet=True, global_search=True)
        bersaglio = bersaglio[0] if bersaglio else None
        if not bersaglio:
            caller.msg(f"Non trovi '{nome.strip()}'.")
            return
        ranghi = societa_di(bersaglio)
        if not ranghi:
            caller.msg(f"{bersaglio.key} non risulta far parte di nessuna societa' pubblica conosciuta.")
            return
        righe = [f"{bersaglio.key} fa parte di:"]
        for sid, rango in ranghi.items():
            righe.append(f"  {nome_societa(sid)} - {NOMI_RANGO.get(rango, 'sconosciuto')}")
        caller.msg("\n".join(righe))

    def _tell(self, caller, resto):
        parti = resto.split(None, 1) if resto else []
        if len(parti) != 2:
            caller.msg("Uso: clan tell <societa> <messaggio>")
            return
        sid = self._trova(parti[0])
        if not sid or not ha_rango(caller, sid, RANGO_MEMBRO):
            caller.msg("Non fai parte di quella societa'.")
            return
        messaggio = parti[1]
        destinatari = [m for m in membri_di(sid) if m.sessions.count() > 0]
        for m in destinatari:
            m.msg(f"|c[{nome_societa(sid)}] {caller.key}: {messaggio}|n")
        if caller not in destinatari:
            caller.msg(f"|c[{nome_societa(sid)}] {caller.key}: {messaggio}|n")

    def _trova(self, nome):
        nome = nome.strip().lower()
        if nome in SOCIETA:
            return nome
        for sid, dati in SOCIETA.items():
            if nome == dati["nome"].lower() or nome in dati["nome"].lower():
                return sid
        # ricerca piu' permissiva: tutte le parole della query compaiono
        # nell'id interno o nel nome italiano, in qualunque ordine
        parole = nome.replace("_", " ").split()
        for sid, dati in SOCIETA.items():
            bersaglio = f"{sid.replace('_', ' ')} {dati['nome'].lower()}"
            if all(parola in bersaglio for parola in parole):
                return sid
        return None

    def _invita(self, caller, resto):
        parti = resto.rsplit(None, 1) if resto else []
        if len(parti) != 2:
            caller.msg("Uso: clan invite <personaggio> <societa>")
            return
        sid = self._trova(parti[1])
        if not sid:
            caller.msg("Societa' sconosciuta.")
            return
        if not ha_rango(caller, sid, RANGO_CONSIGLIO):
            caller.msg("Solo un membro del consiglio o il leader possono invitare.")
            return
        bersaglio = caller.search(parti[0], quiet=True, global_search=True)
        bersaglio = bersaglio[0] if bersaglio else None
        if not bersaglio:
            caller.msg(f"Non trovi '{parti[0]}'.")
            return
        unisciti(bersaglio, sid, rango=RANGO_INVITATO)
        caller.msg(f"Inviti {bersaglio.key} a {nome_societa(sid)}.")
        bersaglio.msg(f"{caller.key} ti invita a unirti a {nome_societa(sid)}.")

    def _promuovi(self, caller, resto):
        parti = resto.rsplit(None, 1) if resto else []
        if len(parti) != 2:
            caller.msg("Uso: clan promote <personaggio> <societa>")
            return
        sid = self._trova(parti[1])
        if not sid:
            caller.msg("Societa' sconosciuta.")
            return
        if not ha_rango(caller, sid, RANGO_LEADER):
            caller.msg("Solo il leader puo' promuovere.")
            return
        bersaglio = caller.search(parti[0], quiet=True, global_search=True)
        bersaglio = bersaglio[0] if bersaglio else None
        if not bersaglio or rango_in(bersaglio, sid) <= 0:
            caller.msg("Quel personaggio non fa parte di quella societa'.")
            return
        rango_attuale = rango_in(bersaglio, sid)
        indice = SCALA_RANGHI.index(rango_attuale) if rango_attuale in SCALA_RANGHI else -1
        if indice >= len(SCALA_RANGHI) - 1:
            caller.msg(f"{bersaglio.key} e' gia' al rango massimo.")
            return
        nuovo_rango = SCALA_RANGHI[indice + 1]
        unisciti(bersaglio, sid, rango=nuovo_rango)
        caller.msg(f"Promuovi {bersaglio.key} a {NOMI_RANGO[nuovo_rango]}.")
        bersaglio.msg(f"{caller.key} ti promuove a {NOMI_RANGO[nuovo_rango]} in {nome_societa(sid)}.")

    def _degrada(self, caller, resto):
        parti = resto.rsplit(None, 1) if resto else []
        if len(parti) != 2:
            caller.msg("Uso: clan demote <personaggio> <societa>")
            return
        sid = self._trova(parti[1])
        if not sid:
            caller.msg("Societa' sconosciuta.")
            return
        if not ha_rango(caller, sid, RANGO_LEADER):
            caller.msg("Solo il leader puo' degradare.")
            return
        bersaglio = caller.search(parti[0], quiet=True, global_search=True)
        bersaglio = bersaglio[0] if bersaglio else None
        if not bersaglio or rango_in(bersaglio, sid) <= 0:
            caller.msg("Quel personaggio non fa parte di quella societa'.")
            return
        rango_attuale = rango_in(bersaglio, sid)
        indice = SCALA_RANGHI.index(rango_attuale) if rango_attuale in SCALA_RANGHI else 0
        if indice <= 0:
            lascia(bersaglio, sid)
            caller.msg(f"Espelli {bersaglio.key} da {nome_societa(sid)}.")
            bersaglio.msg(f"{caller.key} ti espelle da {nome_societa(sid)}.")
            return
        nuovo_rango = SCALA_RANGHI[indice - 1]
        unisciti(bersaglio, sid, rango=nuovo_rango)
        caller.msg(f"Degradi {bersaglio.key} a {NOMI_RANGO[nuovo_rango]} in {nome_societa(sid)}.")
        bersaglio.msg(f"{caller.key} ti degrada a {NOMI_RANGO[nuovo_rango]} in {nome_societa(sid)}.")

    def _espelli(self, caller, resto):
        # helps/societies.txt: SOCIETY EXPEL <character> <sid> - prima
        # esisteva solo come effetto collaterale di demote ripetuto.
        parti = resto.rsplit(None, 1) if resto else []
        if len(parti) != 2:
            caller.msg("Uso: clan expel <personaggio> <societa>")
            return
        sid = self._trova(parti[1])
        if not sid:
            caller.msg("Societa' sconosciuta.")
            return
        if not ha_rango(caller, sid, RANGO_LEADER):
            caller.msg("Solo il leader puo' espellere.")
            return
        bersaglio = caller.search(parti[0], quiet=True, global_search=True)
        bersaglio = bersaglio[0] if bersaglio else None
        if not bersaglio or rango_in(bersaglio, sid) <= 0:
            caller.msg("Quel personaggio non fa parte di quella societa'.")
            return
        lascia(bersaglio, sid)
        caller.msg(f"Espelli {bersaglio.key} da {nome_societa(sid)}.")
        bersaglio.msg(f"{caller.key} ti espelle da {nome_societa(sid)}.")

    def _lascia(self, caller, nome):
        sid = self._trova(nome)
        if not sid:
            caller.msg("Uso: clan leave <societa>")
            return
        ok, messaggio = lascia(caller, sid)
        caller.msg(messaggio)

    def _induct(self, caller, resto):
        """(staff) CLAN INDUCT <personaggio> <societa> [rango] - onboarding
        in gioco del primo membro/leader di un clan gia' approvato fuori
        gioco dallo staff (helps/societies_newclans.txt): prima l'unico
        modo era chiamare unisciti() manualmente via @py."""
        parti = resto.split() if resto else []
        if len(parti) not in (2, 3):
            caller.msg("Uso: clan induct <personaggio> <societa> [invited|member|council|leader]")
            return
        bersaglio = caller.search(parti[0], quiet=True, global_search=True)
        bersaglio = bersaglio[0] if bersaglio else None
        if not bersaglio:
            caller.msg(f"Non trovi '{parti[0]}'.")
            return
        sid = self._trova(parti[1])
        if not sid:
            caller.msg("Societa' sconosciuta.")
            return
        mappa_rango = {
            "invited": RANGO_INVITATO, "invitato": RANGO_INVITATO,
            "member": RANGO_MEMBRO, "membro": RANGO_MEMBRO,
            "council": RANGO_CONSIGLIO, "consiglio": RANGO_CONSIGLIO,
            "leader": RANGO_LEADER,
        }
        rango = RANGO_MEMBRO
        if len(parti) == 3:
            rango = mappa_rango.get(parti[2].lower())
            if not rango:
                caller.msg("Rango sconosciuto: usa invited/member/council/leader.")
                return
        unisciti(bersaglio, sid, rango=rango)
        caller.msg(f"{bersaglio.key} e' ora {NOMI_RANGO[rango]} di {nome_societa(sid)}.")
        bersaglio.msg(f"|gSei stato/a accolto/a in {nome_societa(sid)} come {NOMI_RANGO[rango]}.|n")
