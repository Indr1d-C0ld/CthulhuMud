#!/bin/bash
# Installa i servizi systemd di CthulhuMud (avvio al boot + watchdog anti-crash).
# Da eseguire con sudo, una tantum, dalla directory del repo:
#   sudo bash deploy/systemd/install.sh
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "Questo script va eseguito con sudo." >&2
    exit 1
fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "$SRC_DIR/cthulhumud.service" /etc/systemd/system/cthulhumud.service
cp "$SRC_DIR/cthulhumud-watchdog.service" /etc/systemd/system/cthulhumud-watchdog.service
cp "$SRC_DIR/cthulhumud-watchdog.timer" /etc/systemd/system/cthulhumud-watchdog.timer

systemctl daemon-reload
systemctl enable --now cthulhumud.service
systemctl enable --now cthulhumud-watchdog.timer

echo "Fatto. Stato:"
systemctl status cthulhumud.service --no-pager || true
systemctl status cthulhumud-watchdog.timer --no-pager || true
