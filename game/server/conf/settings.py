r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

import os

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "CthulhuMud ITA Redux"
GAME_SLOGAN = "Il gioco di ruolo online basato sui Miti di Cthulhu"

######################################################################
# Rete: la porta telnet di default di Evennia (4000) e' occupata da un
# altro servizio su questo host (Balthasar). Riprendiamo la porta 8889,
# la stessa usata dal CthulhuMUD originale, libera su questa macchina.
######################################################################
TELNET_PORTS = [8889]

######################################################################
# Ascolto in dual-stack (IPv4 + IPv6): SOLO per il telnet.
#
# I default di Evennia sono "0.0.0.0", cioe' solo IPv4, mentre il nome
# pubblico di questo server pubblica anche un record AAAA: un client con
# connettivita' IPv6 prova quella per prima e trova la porta chiusa.
# Tutti gli altri servizi della macchina (SSH, Samba, la BBS sulla 2222)
# sono gia' in dual-stack. Con net.ipv6.bindv6only = 0, impostazione di
# questo sistema, un singolo socket su "::" serve entrambi i protocolli.
#
# ATTENZIONE - il WEBSERVER deve restare su IPv4. Provato in dual-stack e
# subito rientrato: e' un limite di Evennia stesso, non della nostra
# configurazione. In evennia/server/webserver.py:76 c'e'
#     client_ip, port = self.transport.client
# che assume una tupla di DUE elementi, come su IPv4; su IPv6 quella
# tupla ne ha quattro (host, porta, flowinfo, scope-id) e ogni singola
# richiesta HTTP muore con
#     ValueError: too many values to unpack (expected 2)
# lasciando il sito irraggiungibile su ENTRAMBI i protocolli. Stessa
# prudenza per il websocket del client web, che passa per la medesima
# infrastruttura. Se un domani Evennia correggera' quella riga, si
# potranno portare a "::" anche queste due.
######################################################################
TELNET_INTERFACES = ["::"]

######################################################################
# Accesso al sito tramite Apache in HTTPS, su /cthulhumud/
#
# Motivo: la porta 4001 e' una porta anomala e molte reti (aziendali,
# mobili, hotspot pubblici) scartano in silenzio il traffico verso porte
# non standard - il sintomo e' una lunga attesa seguita da timeout,
# esattamente quello osservato. La 443 invece funziona gia' dall'esterno,
# perche' serve le altre piattaforme di questo server, ed e' in
# dual-stack, quindi risolve insieme anche il problema IPv6 descritto
# sopra. Vedi deploy/apache/ per la configurazione del proxy.
#
# FORCE_SCRIPT_NAME dice a Django di generare tutti gli URL con il
# prefisso /cthulhumud: e' Apache a rimuoverlo prima di inoltrare la
# richiesta a Evennia. CONSEGUENZA DA CONOSCERE: da questo momento
# l'accesso DIRETTO a http://<indirizzo>:4001/ mostra ancora la
# homepage, ma i collegamenti interni puntano a /cthulhumud/... e non
# funzionano su quella porta. L'accesso buono diventa quello via HTTPS.
######################################################################
FORCE_SCRIPT_NAME = "/cthulhumud"
STATIC_URL = "/cthulhumud/static/"
MEDIA_URL = "/cthulhumud/media/"

# Django 4+ richiede che le origini HTTPS siano dichiarate, altrimenti
# ogni invio di modulo (login, registrazione) fallisce con errore CSRF.
CSRF_TRUSTED_ORIGINS = ["https://timrouter.dns.army"]

# Dietro un proxy, Django deve sapere che la connessione con il browser
# e' cifrata anche se quella verso Evennia non lo e', altrimenti genera
# URL "http://" dentro una pagina servita in HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Il client web di gioco apre un websocket: va indirizzato al percorso
# proxato, non alla porta 4002 diretta (bloccata dagli stessi firewall).
WEBSOCKET_CLIENT_URL = "wss://timrouter.dns.army/cthulhumud/ws"

######################################################################
# Localizzazione italiana. Evennia disabilita l'i18n di default e la
# traduzione italiana che distribuisce e' solo una bozza parziale (~24%);
# l'abbiamo completata noi (vedi game/locale/README.md) e la rendiamo
# attiva qui, mettendo la NOSTRA copia per prima in LOCALE_PATHS cosi'
# da non dover modificare il pacchetto Evennia nel virtualenv.
######################################################################
USE_I18N = True
LANGUAGE_CODE = "it"
_GAME_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCALE_PATHS = [os.path.join(_GAME_DIR, "locale")] + list(LOCALE_PATHS)

######################################################################
# Creazione personaggio: usiamo il contrib character_creator con un
# menu custom (world/chargen_menu.py) per la scelta di razza/professione.
######################################################################
AUTO_CREATE_CHARACTER_WITH_ACCOUNT = False
AUTO_PUPPET_ON_LOGIN = False
CHARGEN_MENU = "world.chargen_menu"

######################################################################
# Descrizioni italiane delle opzioni di stile (comando "style"). Solo
# la descrizione cambia: classe e valore di default restano quelli di
# Evennia (vedi evennia.settings_default.OPTIONS_ACCOUNT_DEFAULT).
######################################################################
######################################################################
# Orologio di gioco (Fase K, quindicesima tornata): confermato dalla
# fonte come meccanica reale, non solo colore - helps/time.txt ("The
# TIME command displays the current game time...") e helps/buy.txt/
# list.txt/sell.txt ("The HOURS command will show you when the shop
# is open"). Vedi world/tempo.py.
#
# TIME_FACTOR scala il tempo di gioco (nativo di Evennia, vedi
# evennia.utils.gametime) rispetto al tempo reale. helps/merc.txt
# conferma che questo gioco e' basato su Merc 2.2 ("This mud is based
# on Merc 2.2"); nessuna fonte specifica se CthulhuMUD abbia cambiato
# il ritmo di default del motore, quindi si riproduce qui il default
# classico di Merc (SECS_PER_MUD_HOUR = 75, un giorno di gioco intero
# ogni 30 minuti reali) invece del 2.0 generico di Evennia - la scelta
# piu' fedele disponibile in assenza di dati piu' specifici.
######################################################################
TIME_FACTOR = 48.0  # 3600 secondi di gioco / 75 secondi reali

OPTIONS_ACCOUNT_DEFAULT = {
    "border_color": ("Intestazioni, piè di pagina, bordi di tabella, ecc.", "Color", "n"),
    "header_star_color": ("* dentro le righe di intestazione.", "Color", "n"),
    "header_text_color": ("Testo dentro le righe di intestazione.", "Color", "w"),
    "header_fill": ("Riempimento delle righe di intestazione.", "Text", "="),
    "separator_star_color": ("* dentro le righe separatrici.", "Color", "n"),
    "separator_text_color": ("Testo dentro le righe separatrici.", "Color", "w"),
    "separator_fill": ("Riempimento delle righe separatrici.", "Text", "-"),
    "footer_star_color": ("* dentro le righe di piè di pagina.", "Color", "n"),
    "footer_text_color": ("Testo dentro le righe di piè di pagina.", "Color", "n"),
    "footer_fill": ("Riempimento delle righe di piè di pagina.", "Text", "="),
    "column_names_color": ("Testo delle intestazioni di colonna nelle tabelle.", "Color", "w"),
    "timezone": ("Fuso orario per le date.", "Timezone", "UTC"),
}


######################################################################
# Notifica via email allo staff alla registrazione di un nuovo account
# (punto 2 della checklist pre-release). Riusa il relay SMTP Brevo gia'
# attivo per il forum phpBB "Loggia Nera" del progetto SubSpazio, sullo
# stesso server: nessun account Brevo nuovo da creare. Le credenziali
# vere (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL) NON
# vanno mai messe qui (questo file finira' nel repo pubblico, punto 5)
# ma solo in server/conf/secret_settings.py, gia' in .gitignore - vedi
# i placeholder e le istruzioni li' dentro.
######################################################################
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp-relay.brevo.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = ""

# Destinatario delle notifiche staff (nuove registrazioni, ecc.).
STAFF_NOTIFICATION_EMAIL = "cthulhumud@proton.me"
# Interruttore generale: se EMAIL_HOST_PASSWORD resta vuoto (credenziali
# non ancora inserite in secret_settings.py) world/notifiche.py salta
# l'invio senza sollevare errori, per non bloccare la registrazione.
NOTIFY_STAFF_ON_NEW_ACCOUNT = True


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
