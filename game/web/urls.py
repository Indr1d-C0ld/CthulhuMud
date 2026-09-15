"""
This is the starting point when a user enters a url in their web browser.

The urls is matched (by regex) and mapped to a 'view' - a Python function or
callable class that in turn (usually) makes use of a 'template' (a html file
with slots that can be replaced by dynamic content) in order to render a HTML
page to show the user.

This file includes the urls in website, webclient and admin. To override you
should modify urls.py in those sub directories.

Search the Django documentation for "URL dispatcher" for more help.

"""

from django.urls import include, path

# default evennia patterns
from evennia.web.urls import urlpatterns as evennia_default_urlpatterns

# add patterns
urlpatterns = [
    # website
    path("", include("web.website.urls")),
    # webclient
    path("webclient/", include("web.webclient.urls")),
    # web admin
    path("admin/", include("web.admin.urls")),
    # add any extra urls here:
    # path("mypath/", include("path.to.my.urls.file")),
]

# 'urlpatterns' must be named such for Django to find it.
urlpatterns = urlpatterns + evennia_default_urlpatterns

# Compatibilita' con l'accesso DIRETTO alla porta 4001.
#
# Il sito e' pensato per stare dietro Apache su https://.../cthulhumud/
# (vedi FORCE_SCRIPT_NAME in server/conf/settings.py e deploy/apache/):
# Django genera quindi tutti gli URL con quel prefisso, ed e' Apache a
# rimuoverlo prima di inoltrare la richiesta. Chi pero' apre il sito
# direttamente sulla porta 4001 - dalla rete locale, o per diagnosi -
# riceve pagine i cui collegamenti puntano a /cthulhumud/..., che senza
# Apache davanti non corrisponderebbero a nulla. Montando gli stessi
# percorsi anche sotto quel prefisso, entrambe le vie funzionano.
urlpatterns = urlpatterns + [
    path("cthulhumud/", include("web.website.urls")),
    path("cthulhumud/webclient/", include("web.webclient.urls")),
    path("cthulhumud/admin/", include("web.admin.urls")),
]
