#!/usr/bin/env bash
# Instala o FigCraft (CLI headless) e as fontes do estilo premium. Uso: bash figcraft/instalar.sh
# No fim imprime o caminho do figcraft-cli (use em --cli do figcraft/premium.py).
set -euo pipefail
VER="${FIGCRAFT_VER:-0.11.2}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/figcraft"
CLI="$DEST/figcraft-$VER-linux-x86_64/bin/figcraft-cli"
if [ ! -x "$CLI" ]; then
  mkdir -p "$DEST"
  curl -sSL -m 300 -o "$DEST/fc.tgz" \
    "https://github.com/storytold/figcraft/releases/download/v$VER/figcraft-$VER-linux-x86_64.tar.gz"
  tar -xzf "$DEST/fc.tgz" -C "$DEST" && rm -f "$DEST/fc.tgz"
fi
mkdir -p "$HOME/.fonts"
cp "$RAIZ"/assets/fonts/*.ttf "$HOME/.fonts/"
fc-cache -f >/dev/null
fc-list : family | grep "Inter Display" >/dev/null || echo "AVISO: fonte Inter/Inter Display não encontrada no sistema" >&2
"$CLI" --version >&2 || true
echo "$CLI"
