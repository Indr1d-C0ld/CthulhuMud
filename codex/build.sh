#!/bin/bash
# Compila il Codex di CthulhuMud in PDF a partire dai capitoli markdown.
# Toolchain: pandoc (md -> HTML standalone, con indice) + weasyprint
# (HTML -> PDF), scelta al posto di LaTeX per gestire senza problemi i
# caratteri Unicode generati nei capitoli (frecce, simboli, emoji) e per
# un controllo piu' preciso via CSS sulle interruzioni di pagina (tabelle
# mai spezzate a meta').
# Uso: bash build.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

CAPITOLI=$(ls capitoli/*.md | sort)

pandoc $CAPITOLI \
    --from=markdown+smart \
    --standalone \
    --toc --toc-depth=3 \
    --css=stile_stampa.css \
    --include-before-body=frontespizio.html \
    --metadata title="Il Codex di CthulhuMud" \
    --metadata lang=it \
    -o documento.html

weasyprint documento.html codex_cthulhumud.pdf

echo "Fatto: codex_cthulhumud.pdf"
