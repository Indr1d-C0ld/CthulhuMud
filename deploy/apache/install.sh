#!/bin/bash
# Espone il sito di CthulhuMud su https://timrouter.dns.army/cthulhumud/
# tramite il vhost HTTPS gia' esistente di Apache.
#
# Da eseguire con sudo, una tantum:
#   sudo bash deploy/apache/install.sh
#
# Lo script e' prudente: salva una copia del vhost prima di toccarlo,
# verifica la configurazione di Apache PRIMA di ricaricarla, e se la
# verifica fallisce ripristina da solo la copia e non ricarica nulla.
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "Questo script va eseguito con sudo." >&2
    exit 1
fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VHOST="/etc/apache2/sites-enabled/000-default-le-ssl.conf"
INCLUDE_DST="/etc/apache2/conf-available/cthulhumud-proxy.conf"
BACKUP="${VHOST}.prima-di-cthulhumud.$(date +%Y%m%d-%H%M%S)"

if [[ ! -f "$VHOST" ]]; then
    echo "ERRORE: non trovo il vhost HTTPS in $VHOST" >&2
    exit 1
fi

echo "1) Abilito i moduli proxy necessari"
a2enmod proxy proxy_http proxy_wstunnel headers rewrite >/dev/null
echo "   ok"

echo "2) Copio la configurazione del proxy"
cp "$SRC_DIR/cthulhumud-proxy.conf" "$INCLUDE_DST"
echo "   -> $INCLUDE_DST"

echo "3) Salvo una copia del vhost e vi aggiungo l'inclusione"
cp "$VHOST" "$BACKUP"
echo "   copia di sicurezza: $BACKUP"

if grep -q "cthulhumud-proxy.conf" "$VHOST"; then
    echo "   (inclusione gia' presente, non la aggiungo di nuovo)"
else
    # inserisce la riga subito prima della chiusura del VirtualHost
    awk -v inc="    Include $INCLUDE_DST" '
        /<\/VirtualHost>/ && !done { print inc; done=1 }
        { print }
    ' "$BACKUP" > "$VHOST"
    echo "   inclusione aggiunta"
fi

echo "4) Verifico la configurazione di Apache PRIMA di ricaricarla"
if ! apache2ctl configtest 2>&1 | tee /tmp/cthulhumud-configtest.log | grep -q "Syntax OK"; then
    echo
    echo "!!! La configurazione NON e' valida: ripristino il vhost originale e non ricarico nulla."
    cat /tmp/cthulhumud-configtest.log
    cp "$BACKUP" "$VHOST"
    exit 1
fi
echo "   Syntax OK"

echo "5) Ricarico Apache"
systemctl reload apache2
echo "   ok"

echo
echo "Fatto. Il sito dovrebbe ora rispondere su:"
echo "   https://timrouter.dns.army/cthulhumud/"
echo
echo "Per annullare tutto: ripristina $BACKUP su $VHOST,"
echo "rimuovi $INCLUDE_DST e ricarica Apache."
