#!/usr/bin/env bash
# Install what the repo's scripts need on a fresh Debian/Ubuntu container:
# Scribus 1.6.3 (the user's version, run windowed on a virtual screen) for PDF export,
# the documents' fonts, cairosvg for icons and pypdf for the form fields.
# Usage: bash scripts/setup-tools.sh   (as root)
set -euo pipefail

apt-get update -q
apt-get install -y -q scribus xvfb xdotool fonts-lmodern fonts-dejavu poppler-utils
pip install -q cairosvg pillow pypdf

# Scribus 1.6.3 AppImage, unpacked (no FUSE in containers) to /opt/scribus-1.6.3.
# The distro's scribus package (1.6.1) is only a fallback.
if [ ! -x /opt/scribus-1.6.3/AppRun ]; then
  tmp=$(mktemp -d)
  curl -sSfL -o "$tmp/scribus.AppImage" \
    "https://sourceforge.net/projects/scribus/files/scribus/1.6.3/scribus-1.6.3-linux-x86_64.AppImage/download"
  chmod +x "$tmp/scribus.AppImage"
  (cd "$tmp" && ./scribus.AppImage --appimage-extract >/dev/null)
  rm -rf /opt/scribus-1.6.3
  mv "$tmp/squashfs-root" /opt/scribus-1.6.3
  rm -rf "$tmp"
fi

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
