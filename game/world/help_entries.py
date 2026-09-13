"""
File-based help entries. These complements command-based help and help entries
added in the database using the `sethelp` command in-game.

Control where Evennia reads these entries with `settings.FILE_HELP_ENTRY_MODULES`,
which is a list of python-paths to modules to read.

A module like this should hold a global `HELP_ENTRY_DICTS` list, containing
dicts that each represent a help entry. If no `HELP_ENTRY_DICTS` variable is
given, all top-level variables that are dicts in the module are read as help
entries.

Each dict is on the form
::

    {'key': <str>,
     'text': <str>}``     # the actual help text. Can contain # subtopic sections
     'category': <str>,   # optional, otherwise settings.DEFAULT_HELP_CATEGORY
     'aliases': <list>,   # optional
     'locks': <str>       # optional, 'view' controls seeing in help index, 'read'
                          #           if the entry can be read. If 'view' is unset,
                          #           'read' is used for the index. If unset, everyone
                          #           can read/view the entry.

"""

HELP_ENTRY_DICTS = [
    {
        "key": "evennia",
        "aliases": ["ev"],
        "category": "Generale",
        "locks": "read:perm(Developer)",
        "text": """
            Evennia e' il motore/framework MU* scritto in Python su cui e' costruito
            questo porting di CthulhuMud. Maggiori informazioni su https://www.evennia.com.

            # subtopics

            ## Installazione

            Le istruzioni di installazione si trovano su https://www.evennia.com.

            ## Comunita'

            Ci sono diversi modi per ottenere aiuto e comunicare con altri sviluppatori
            del motore Evennia (in inglese, essendo il progetto upstream internazionale)!

            ### Discussions

            Il forum Discussions si trova su https://github.com/evennia/evennia/discussions.

            ### Discord

            C'e' anche un canale Discord per chattare - connettiti tramite questo
            link: https://discord.gg/AJJpcRUhtF

        """,
    },
]
