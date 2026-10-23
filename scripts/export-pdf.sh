#!/usr/bin/env bash
# Export Scribus sources to PDF next to them: foo.sla -> foo-claude.pdf
# (foo-claude.sla -> foo-claude.pdf, foo-fillable-claude.sla -> foo-fillable-claude.pdf)
# Usage: scripts/export-pdf.sh path/to/file.sla [...]
#
# Runs Scribus windowed (the user's request), on a virtual screen (Xvfb) when there is no
# display, and closes its startup dialog with xdotool. Opens read-only: the .sla is never saved.
# Uses Scribus 1.6.3 from /opt/scribus-1.6.3 (setup-tools.sh); set SCRIBUS=... to override.
#
# Fillable files (any with form fields) keep them. Scribus crashes when it
# exports form fields with embedded fonts, so these export with fonts as outlines
# (text not selectable) and scripts/fix-form-pdf.py then tidies the fields.
set -euo pipefail

here=$(dirname "$(realpath "$0")")
scribus=${SCRIBUS:-/opt/scribus-1.6.3/AppRun}
[ -x "$scribus" ] || scribus=$(command -v scribus)

work=$(mktemp -d)
trap 'kill "${xvfb:-}" 2>/dev/null || true; rm -rf "$work"' EXIT
cat >"$work/export.py" <<'PY'
import os, scribus
try:
    if not scribus.openDoc(os.environ["IN_SLA"]):
        raise SystemExit("could not open " + os.environ["IN_SLA"])
    pdf = scribus.PDFfile()
    pdf.file = os.environ["OUT_PDF"]
    pdf.compressmtd = 2  # lossless (zip) images: JPEG blurs icon edges
    if os.environ["FILLABLE"]:
        pdf.fontEmbedding = 1  # outlines: embedding crashes Scribus on form fields
    pdf.save()
    scribus.closeDoc()
    open(os.environ["DONE"], "w").close()
finally:
    os._exit(0)  # windowed Scribus would otherwise stay open
PY

if [ -z "${DISPLAY:-}" ]; then
  disp=":$((100 + $$ % 800))"
  Xvfb "$disp" -screen 0 1600x1200x24 >/dev/null 2>&1 &
  xvfb=$!
  export DISPLAY=$disp
  sleep 1
fi

for src in "$@"; do
  src=$(realpath "$src")
  stem="${src%.sla}"
  # Every file Claude makes is labelled in its name: foo.sla -> foo-claude.pdf
  [[ "$stem" == *-claude ]] || stem="$stem-claude"
  out="$stem.pdf"
  fillable=""
  grep -q 'ANNOTATION="1"' "$src" && fillable=1  # has form fields
  done="$work/done"
  rm -f "$done"
  IN_SLA="$src" OUT_PDF="$out" FILLABLE="$fillable" DONE="$done" \
    "$scribus" -ns -py "$work/export.py" >/dev/null 2>&1 &
  pid=$!
  for _ in $(seq 1 360); do  # up to 3 minutes
    [ -f "$done" ] && break
    kill -0 "$pid" 2>/dev/null || break
    xdotool search --name "New Document" key --window %@ Escape >/dev/null 2>&1 || true
    sleep 0.5
  done
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  [ -f "$done" ] || { echo "failed: $src" >&2; exit 1; }
  [ -n "$fillable" ] && python3 "$here/fix-form-pdf.py" "$out" >/dev/null
  echo "$out"
done
