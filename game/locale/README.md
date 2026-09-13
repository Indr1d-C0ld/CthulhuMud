# Localizzazione italiana

Questa cartella contiene la nostra copia completata della traduzione
italiana di Evennia (`it/LC_MESSAGES/django.po` + `.mo`), che integra e
completa la bozza parziale distribuita con Evennia stesso
(`evennia/locale/it/`, ~24% tradotta all'origine).

`server/conf/settings.py` la rende attiva tramite `LOCALE_PATHS`, quindi
funziona subito con un `pip install evennia` pulito - **non serve copiarla
a mano nel virtualenv**.

Se in futuro si vuole comunque allineare anche la copia dentro il
virtualenv (per coerenza, non necessario per il funzionamento), copiare
questi due file su:

    <venv>/lib/python3.13/site-packages/evennia/locale/it/LC_MESSAGES/

Per ricompilare `django.po` in `django.mo` dopo una modifica:

    msgfmt --check django.po -o django.mo
