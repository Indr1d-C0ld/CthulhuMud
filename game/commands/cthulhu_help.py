"""
Localizzazione del sistema di help (Fase C). Vedi Dossier/note di sessione:
evennia/commands/default/help.py non usa affatto gettext.

Non riscriviamo la logica di ricerca/indicizzazione (collect_topics,
do_search, parse, strip_cmd_prefix, can_read_topic, can_list_topic) che
non contiene stringhe in inglese destinate al giocatore: ereditiamo quella
da CmdHelp originale. Sovrascriviamo solo i metodi che generano testo.

NOTA IMPORTANTE E NON RISOLTA QUI: il contenuto vero e proprio dell'help
di ogni comando (compresi tutti i comandi di default di Evennia non
ancora tradotti, es. i comandi da builder in building.py) resta il
docstring del comando stesso, in inglese finche' non riscriviamo anche
quello. Questo file traduce solo l'INTERFACCIA del sistema di help
(titoli, "nessun aiuto trovato", indice per categoria, ecc.), non tutti
i contenuti che potra' restituire.
"""

from evennia.commands.default.help import CmdHelp as DefaultCmdHelp
from evennia.commands.default.help import CmdSetHelp as DefaultCmdSetHelp
from evennia.commands.default.help import HelpCategory
from evennia.help.utils import help_search_with_index
from evennia.locks.lockhandler import LockException
from evennia.utils import create, evmore
from evennia.utils.ansi import ANSIString
from evennia.utils.eveditor import EvEditor
from evennia.utils.utils import dedent, format_grid, inherits_from, pad


class CmdHelp(DefaultCmdHelp):
    """
    Ottieni aiuto.

    Uso:
      help
      help <argomento, comando o categoria>
      help <argomento>/<sottoargomento>
      help <argomento>/<sottoargomento>/<sottosottoargomento> ...

    Usa 'help' da solo per vedere un indice di tutti gli argomenti di
    aiuto, organizzati per categoria. Alcuni argomenti importanti possono
    offrire ulteriori sotto-argomenti.
    """

    def format_help_entry(
        self,
        topic="",
        help_text="",
        aliases=None,
        suggested=None,
        subtopics=None,
        click_topics=True,
    ):
        separator = "|C" + "-" * self.client_width() + "|n"
        start = f"{separator}\n"

        title = f"|CAiuto per |w{topic}|n" if topic else "|rNessun aiuto trovato|n"

        if aliases:
            aliases = " |C(alias: {}|C)|n".format("|C,|n ".join(f"|w{ali}|n" for ali in aliases))
        else:
            aliases = ""

        help_text = "\n" + dedent(help_text.strip("\n")) if help_text else ""

        if subtopics:
            if click_topics:
                subtopics = [
                    f"|lchelp {topic}/{subtop}|lt|w{topic}/{subtop}|n|le" for subtop in subtopics
                ]
            else:
                subtopics = [f"|w{topic}/{subtop}|n" for subtop in subtopics]
            subtopics = "\n|CSotto-argomenti:|n\n  {}".format(
                "\n  ".join(
                    format_grid(
                        subtopics, width=self.client_width(), line_prefix=self.index_topic_clr
                    )
                )
            )
        else:
            subtopics = ""

        if suggested:
            suggested = sorted(suggested)
            if click_topics:
                suggested = [f"|lchelp {sug}|lt|w{sug}|n|le" for sug in suggested]
            else:
                suggested = [f"|w{sug}|n" for sug in suggested]
            suggested = "\n|CAltri argomenti suggeriti:|n\n{}".format(
                "\n  ".join(
                    format_grid(
                        suggested, width=self.client_width(), line_prefix=self.index_topic_clr
                    )
                )
            )
        else:
            suggested = ""

        end = start
        partorder = (start, title + aliases, help_text, subtopics, suggested, end)
        return "\n".join(part.rstrip() for part in partorder if part)

    def format_help_index(
        self, cmd_help_dict=None, db_help_dict=None, title_lone_category=False, click_topics=True
    ):
        def _group_by_category(help_dict):
            grid = []
            verbatim_elements = []

            if len(help_dict) == 1 and not title_lone_category:
                for category in help_dict:
                    entries = sorted(set(help_dict.get(category, [])))
                    if click_topics:
                        entries = [f"|lchelp {entry}|lt{entry}|le" for entry in entries]
                    grid.extend(entries)
            else:
                for category in sorted(set(list(help_dict.keys()))):
                    category_str = f"-- {category.title()} "
                    grid.append(
                        ANSIString(
                            self.index_category_clr
                            + category_str
                            + "-" * (width - len(category_str))
                            + self.index_topic_clr
                        )
                    )
                    verbatim_elements.append(len(grid) - 1)
                    entries = sorted(set(help_dict.get(category, [])))
                    if click_topics:
                        entries = [f"|lchelp {entry}|lt{entry}|le" for entry in entries]
                    grid.extend(entries)

            return grid, verbatim_elements

        help_index = ""
        width = self.client_width()
        grid = []
        verbatim_elements = []
        cmd_grid, db_grid = "", ""

        if any(cmd_help_dict.values()):
            sep1 = (
                self.index_type_separator_clr
                + pad("Comandi", width=width, fillchar="-")
                + self.index_topic_clr
            )
            grid, verbatim_elements = _group_by_category(cmd_help_dict)
            gridrows = format_grid(
                grid,
                width,
                sep="  ",
                verbatim_elements=verbatim_elements,
                line_prefix=self.index_topic_clr,
            )
            cmd_grid = ANSIString("\n").join(gridrows) if gridrows else ""

        if any(db_help_dict.values()):
            sep2 = (
                self.index_type_separator_clr
                + pad("Gioco e Mondo", width=width, fillchar="-")
                + self.index_topic_clr
            )
            grid, verbatim_elements = _group_by_category(db_help_dict)
            gridrows = format_grid(
                grid,
                width,
                sep="  ",
                verbatim_elements=verbatim_elements,
                line_prefix=self.index_topic_clr,
            )
            db_grid = ANSIString("\n").join(gridrows) if gridrows else ""

        if cmd_grid and db_grid:
            help_index = f"{sep1}\n{cmd_grid}\n{sep2}\n{db_grid}"
        else:
            help_index = f"{cmd_grid}{db_grid}"

        return help_index

    def func(self):
        from collections import defaultdict
        from itertools import chain

        caller = self.caller
        query, subtopics = self.topic, self.subtopics
        clickable_topics = self.clickable_topics

        if not query:
            cmd_help_topics, db_help_topics, file_help_topics = self.collect_topics(
                caller, mode="list"
            )
            file_db_help_topics = {**file_help_topics, **db_help_topics}
            cmd_help_by_category = defaultdict(list)
            file_db_help_by_category = defaultdict(list)
            key_and_aliases = set(chain(*(cmd._keyaliases for cmd in cmd_help_topics.values())))

            for key, cmd in cmd_help_topics.items():
                key = self.strip_cmd_prefix(key, key_and_aliases)
                cmd_help_by_category[cmd.help_category].append(key)
            for key, entry in file_db_help_topics.items():
                file_db_help_by_category[entry.help_category].append(key)

            output = self.format_help_index(
                cmd_help_by_category, file_db_help_by_category, click_topics=clickable_topics
            )
            self.msg_help(output)
            return

        cmd_help_topics, db_help_topics, file_help_topics = self.collect_topics(
            caller, mode="query"
        )
        key_and_aliases = set(chain(*(cmd._keyaliases for cmd in cmd_help_topics.values())))
        file_db_help_topics = {**file_help_topics, **db_help_topics}
        all_topics = {**file_db_help_topics, **cmd_help_topics}
        all_categories = list(
            set(HelpCategory(topic.help_category) for topic in all_topics.values())
        )
        entries = list(all_topics.values()) + all_categories
        match, suggestions = self.do_search(query, entries)

        if not match:
            help_text = f"Non c'e' nessun argomento di aiuto che corrisponda a '{query}'."

            if not suggestions:
                search_fields = [{"field_name": "text", "boost": 1}]
                for match_query in [query, f"{query}*", f"*{query}"]:
                    _, suggestions = help_search_with_index(
                        match_query,
                        entries,
                        suggestion_maxnum=self.suggestion_maxnum,
                        fields=search_fields,
                    )
                    if suggestions:
                        help_text += (
                            "\n... Ma sono state trovate corrispondenze nei testi di aiuto "
                            "dei suggerimenti sottostanti."
                        )
                        suggestions = [
                            self.strip_cmd_prefix(sugg, key_and_aliases) for sugg in suggestions
                        ]
                        break

            output = self.format_help_entry(
                topic=None,
                help_text=help_text,
                suggested=suggestions,
                click_topics=clickable_topics,
            )
            self.msg_help(output)
            return

        if isinstance(match, HelpCategory):
            category = match.key
            category_lower = category.lower()
            cmds_in_category = [
                key for key, cmd in cmd_help_topics.items() if category_lower == cmd.help_category
            ]
            topics_in_category = [
                key
                for key, topic in file_db_help_topics.items()
                if category_lower == topic.help_category
            ]
            output = self.format_help_index(
                {category: cmds_in_category},
                {category: topics_in_category},
                title_lone_category=True,
                click_topics=clickable_topics,
            )
            self.msg_help(output)
            return

        if inherits_from(match, "evennia.commands.command.Command"):
            topic = match.key
            help_text = match.get_help(caller, self.cmdset)
            aliases = match.aliases
            suggested = suggestions[1:]
        else:
            topic = match.key
            help_text = match.entrytext
            aliases = match.aliases if isinstance(match.aliases, list) else match.aliases.all()
            suggested = suggestions[1:]

        from evennia.help.utils import parse_entry_for_subcategories

        subtopic_map = parse_entry_for_subcategories(help_text)
        help_text = subtopic_map[None]
        subtopic_index = [subtopic for subtopic in subtopic_map if subtopic is not None]

        if subtopics:
            for subtopic_query in subtopics:
                if subtopic_query not in subtopic_map:
                    fuzzy_match = False
                    for key in subtopic_map:
                        if key and key.startswith(subtopic_query):
                            subtopic_query = key
                            fuzzy_match = True
                            break
                    if not fuzzy_match:
                        for key in subtopic_map:
                            if key and subtopic_query in key:
                                subtopic_query = key
                                fuzzy_match = True
                                break
                    if not fuzzy_match:
                        checked_topic = topic + f"{self.subtopic_separator_char}{subtopic_query}"
                        output = self.format_help_entry(
                            topic=topic,
                            help_text=f"Nessun argomento di aiuto trovato per '{checked_topic}'",
                            subtopics=subtopic_index,
                            click_topics=clickable_topics,
                        )
                        self.msg_help(output)
                        return

                subtopic_map = subtopic_map.pop(subtopic_query)
                subtopic_index = [subtopic for subtopic in subtopic_map if subtopic is not None]
                topic = topic + f"{self.subtopic_separator_char}{subtopic_query}"

            help_text = subtopic_map[None]

        topic = self.strip_cmd_prefix(topic, key_and_aliases)
        if subtopics:
            aliases = None
        else:
            aliases = [self.strip_cmd_prefix(alias, key_and_aliases) for alias in aliases]
        suggested = [self.strip_cmd_prefix(sugg, key_and_aliases) for sugg in suggested]

        output = self.format_help_entry(
            topic=topic,
            help_text=help_text,
            aliases=aliases,
            subtopics=subtopic_index,
            suggested=suggested,
            click_topics=clickable_topics,
        )
        self.msg_help(output)


def _loadhelp(caller):
    entry = caller.db._editing_help
    return entry.entrytext if entry else ""


def _savehelp(caller, buffer):
    entry = caller.db._editing_help
    caller.msg("Voce di aiuto salvata.")
    if entry:
        entry.entrytext = buffer


def _quithelp(caller):
    caller.msg("Editor chiuso.")
    del caller.db._editing_help


class CmdSetHelp(CmdHelp):
    """
    Modifica il database di aiuto.

    Uso:
      sethelp[/switch] <argomento>[[;alias;alias][,categoria[,lock]]
                [= <testo o nuovo valore>]
    Switch:
      edit - apre un editor di riga per modificare il testo dell'argomento
      replace - sovrascrive un argomento esistente
      append - aggiunge testo in fondo all'argomento esistente (con newline)
      extend - come append, ma senza aggiungere una newline
      category - cambia la categoria di un argomento esistente
      locks - cambia i lock di un argomento esistente
      delete - rimuove l'argomento

    Esempi:
      sethelp lore = All'inizio c'era...
      sethelp/append taccheggio,Furfanteria = Questo ruba...
      sethelp/edit furfanteria
      sethelp/locks furfanteria = read:all()
      sethelp/category furfanteria = classi

    Se non si assegna una categoria, verra' usata quella predefinita. Se
    non si specifica un lockstring, tutti potranno leggere l'argomento.
    """

    key = "sethelp"
    aliases = []
    switch_options = ("edit", "replace", "append", "extend", "category", "locks", "delete")
    locks = "cmd:perm(Helper)"
    help_category = "Costruzione"
    arg_regex = None

    def parse(self):
        return DefaultCmdSetHelp.parse(self)

    def func(self):
        switches = self.switches
        lhslist = self.lhslist
        rhslist = self.rhslist

        if not self.args:
            self.msg(
                "Uso: sethelp[/switch] <argomento>[[;alias;alias][,categoria[,lock]] "
                "[= <testo o nuova categoria>]"
            )
            return

        nlist = len(lhslist)
        topicstr = lhslist[0] if nlist > 0 else ""
        if not topicstr:
            self.msg("Devi definire un argomento!")
            return
        topicstrlist = topicstr.split(";")
        topicstr, aliases = (
            topicstrlist[0],
            topicstrlist[1:] if len(topicstr) > 1 else [],
        )
        aliastxt = ("(alias: %s)" % ", ".join(aliases)) if aliases else ""

        cmd_help_topics, db_help_topics, file_help_topics = self.collect_topics(
            self.caller, mode="query"
        )
        file_db_help_topics = {**file_help_topics, **db_help_topics}
        all_topics = {**file_db_help_topics, **cmd_help_topics}
        all_categories = list(
            set(HelpCategory(topic.help_category) for topic in all_topics.values())
        )
        entries = list(all_topics.values()) + all_categories

        from django.conf import settings as _settings

        category = lhslist[1] if nlist > 1 else _settings.DEFAULT_HELP_CATEGORY
        lockstring = ",".join(lhslist[2:]) if nlist > 2 else "read:all()"

        old_entry = None
        for querystr in topicstrlist:
            match, _ = self.do_search(querystr, entries)
            if match:
                warning = None
                if isinstance(match, HelpCategory):
                    warning = (
                        f"'{querystr}' corrisponde (o corrisponde parzialmente) al nome della "
                        f"categoria di aiuto '{match.key}'. Continuando, la tua voce avra' la "
                        "precedenza e la categoria (o parte del suo nome) potrebbe non essere "
                        "piu' utilizzabile per raggruppare le voci di aiuto."
                    )
                elif inherits_from(match, "evennia.commands.command.Command"):
                    warning = (
                        f"'{querystr}' corrisponde (o corrisponde parzialmente) alla chiave/"
                        f"alias del comando '{match.key}'. L'aiuto dei comandi ha la precedenza "
                        "sulle altre voci di aiuto, quindi la tua voce potrebbe risultare "
                        "irraggiungibile per chi ha accesso a quel comando."
                    )
                elif inherits_from(match, "evennia.help.filehelp.FileHelpEntry"):
                    warning = (
                        f"'{querystr}' corrisponde (o corrisponde parzialmente) al nome/alias "
                        f"dell'argomento di aiuto su file '{match.key}'. Le voci di aiuto su "
                        "file non possono essere modificate dal gioco. Continuando, la tua voce "
                        "potrebbe oscurare parzialmente o completamente quella su file."
                    )
                if warning:
                    self.msg(f"|rAttenzione:\n|r{warning}|n")
                    repl = yield ("|wVuoi continuare comunque? S/[N]?|n")
                    if repl.lower() in ("s", "si", "y", "yes"):
                        db_topics = {**db_help_topics}
                        db_categories = list(
                            set(HelpCategory(topic.help_category) for topic in db_topics.values())
                        )
                        entries = list(db_topics.values()) + db_categories
                        match, _ = self.do_search(querystr, entries)
                        if match:
                            old_entry = match
                    else:
                        self.msg("Annullato.")
                        return
                else:
                    old_entry = match
                    category = lhslist[1] if nlist > 1 else old_entry.help_category
                    lockstring = ",".join(lhslist[2:]) if nlist > 2 else old_entry.locks.get()
                    break

        category = category.lower()

        if "edit" in switches:
            if old_entry:
                topicstr = old_entry.key
                if self.rhs:
                    old_entry.entrytext += "\n%s" % self.rhs
                helpentry = old_entry
            else:
                helpentry = create.create_help_entry(
                    topicstr,
                    self.rhs if self.rhs is not None else "",
                    category=category,
                    locks=lockstring,
                    aliases=aliases,
                )
            self.caller.db._editing_help = helpentry
            EvEditor(
                self.caller,
                loadfunc=_loadhelp,
                savefunc=_savehelp,
                quitfunc=_quithelp,
                key="argomento {}".format(topicstr),
                persistent=True,
            )
            return

        if "append" in switches or "merge" in switches or "extend" in switches:
            if not old_entry:
                self.msg(f"Impossibile trovare l'argomento '{topicstr}'. Devi dare un nome esatto.")
                return
            if not self.rhs:
                self.msg("Devi fornire il testo da aggiungere/unire.")
                return
            if "merge" in switches:
                old_entry.entrytext += " " + self.rhs
            else:
                old_entry.entrytext += "\n%s" % self.rhs
            old_entry.aliases.add(aliases)
            self.msg(f"Voce aggiornata:\n{old_entry.entrytext}{aliastxt}")
            return

        if "category" in switches:
            if not old_entry:
                self.msg(f"Impossibile trovare l'argomento '{topicstr}'{aliastxt}.")
                return
            if not self.rhs:
                self.msg("Devi fornire una categoria.")
                return
            category = self.rhs.lower()
            old_entry.help_category = category
            self.msg(f"Categoria della voce '{topicstr}'{aliastxt} cambiata in '{category}'.")
            return

        if "locks" in switches:
            if not old_entry:
                self.msg(f"Impossibile trovare l'argomento '{topicstr}'{aliastxt}.")
                return
            show_locks = not rhslist
            clear_locks = rhslist and not rhslist[0]
            if show_locks:
                self.msg(f"I lock attuali per la voce '{topicstr}'{aliastxt} sono: {old_entry.locks}")
                return
            if clear_locks:
                old_entry.locks.clear()
                old_entry.locks.add("read:all()")
                self.msg(f"Lock per la voce '{topicstr}'{aliastxt} ripristinati a: read:all()")
                return
            lockstring = ",".join(rhslist)
            existing_locks = old_entry.locks.all()
            old_entry.locks.clear()
            try:
                old_entry.locks.add(lockstring)
            except LockException as e:
                old_entry.locks.add(existing_locks)
                self.msg(str(e) + " Lock non modificati.")
            else:
                self.msg(f"Lock per la voce '{topicstr}'{aliastxt} cambiati in: {lockstring}")
            return

        if "delete" in switches or "del" in switches:
            if not old_entry:
                self.msg(f"Impossibile trovare l'argomento '{topicstr}'{aliastxt}.")
                return
            old_entry.delete()
            self.msg(f"Voce di aiuto '{topicstr}'{aliastxt} eliminata.")
            return

        if not self.rhs:
            self.msg("Devi fornire un testo di aiuto da aggiungere.")
            return
        if old_entry:
            if "replace" in switches:
                old_entry.key = topicstr
                old_entry.entrytext = self.rhs
                old_entry.help_category = category
                old_entry.locks.clear()
                old_entry.locks.add(lockstring)
                old_entry.aliases.add(aliases)
                old_entry.save()
                self.msg(f"Sovrascritto il vecchio argomento '{topicstr}'{aliastxt}.")
            else:
                self.msg(
                    f"L'argomento '{topicstr}'{aliastxt} esiste gia'. Usa /edit per aprirlo "
                    "nell'editor, oppure /replace, /append e /merge per modificarlo direttamente."
                )
        else:
            new_entry = create.create_help_entry(
                topicstr, self.rhs, category=category, locks=lockstring, aliases=aliases
            )
            if new_entry:
                self.msg(f"L'argomento '{topicstr}'{aliastxt} e' stato creato con successo.")
                if "edit" in switches:
                    self.caller.db._editing_help = new_entry
                    EvEditor(
                        self.caller,
                        loadfunc=_loadhelp,
                        savefunc=_savehelp,
                        quitfunc=_quithelp,
                        key="argomento {}".format(new_entry.key),
                        persistent=True,
                    )
                    return
            else:
                self.msg(f"Errore nella creazione dell'argomento '{topicstr}'{aliastxt}! Contatta un amministratore.")
