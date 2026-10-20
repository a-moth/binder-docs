#!/usr/bin/env bash
# Install what the repo's scripts need on a fresh Debian/Ubuntu container:
# headless Scribus for PDF export, the documents' fonts, and cairosvg for icons.
# Usage: bash scripts/setup-tools.sh   (as root)
set -euo pipefail

apt-get update -q
apt-get install -y -q scribus xvfb fonts-lmodern fonts-dejavu poppler-utils
pip install -q cairosvg pillow

# Comic Relief (used in core/core-layouts.sla) from Google Fonts.
fonts="$HOME/.local/share/fonts"
mkdir -p "$fonts"
css=$(curl -sS -A "Wget/1.0" "https://fonts.googleapis.com/css2?family=Comic+Relief:wght@400;700")
i=0
for url in $(grep -o 'https://fonts.gstatic.com[^)]*' <<<"$css"); do
  i=$((i + 1))
  curl -sSf -o "$fonts/ComicRelief-$i.ttf" "$url"
done
fc-cache -f
fc-list | grep -i 'comic relief'
