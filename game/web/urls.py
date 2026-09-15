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

# NOTA (da non rifare): qui erano stati montati gli stessi percorsi anche
# sotto "cthulhumud/", per far funzionare l'accesso diretto alla porta
# 4001 con gli URL prefissati che Django genera per il proxy
# (FORCE_SCRIPT_NAME, vedi server/conf/settings.py).
#
# Sembrava innocuo ed era invece dannoso: `reverse()` risolve un nome di
# rotta sull'ULTIMO pattern registrato con quel nome, quindi i duplicati
# vincevano su quelli veri e Django generava indirizzi con il prefisso
# RADDOPPIATO - e per giunta sbagliati, perche' i nomi di web.website e
# web.webclient collidono fra loro. Il link del logo, per dire, puntava a
# /cthulhumud/cthulhumud/webclient/ invece che alla homepage.
#
# Si accetta quindi il compromesso: l'accesso buono e' quello via Apache
# in HTTPS; aprire direttamente la porta 4001 mostra le pagine ma con i
# collegamenti e i fogli di stile non risolti, ed e' utile solo per
# diagnosi rapide.
