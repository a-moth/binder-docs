#!/usr/bin/env bash
# Export Scribus sources to PDF next to them: foo.sla -> foo-claude.pdf
# (foo-claude.sla -> foo-claude.pdf)
# Usage: scripts/export-pdf.sh path/to/file.sla [...]
# Needs scribus + xvfb-run (headless). Opens read-only: the .sla is never saved.
set -euo pipefail

py=$(mktemp --suffix=.py)
trap 'rm -f "$py"' EXIT
cat >"$py" <<'PY'
import os, scribus
if not scribus.openDoc(os.environ["IN_SLA"]):
    raise SystemExit("could not open " + os.environ["IN_SLA"])
pdf = scribus.PDFfile()
pdf.file = os.environ["OUT_PDF"]
pdf.compressmtd = 2  # lossless (zip) images: JPEG blurs icon edges
pdf.save()
scribus.closeDoc()
PY

for src in "$@"; do
  src=$(realpath "$src")
  stem="${src%.sla}"
  # Every file Claude makes is labelled in its name: foo.sla -> foo-claude.pdf
  [[ "$stem" == *-claude ]] || stem="$stem-claude"
  out="$stem.pdf"
  IN_SLA="$src" OUT_PDF="$out" xvfb-run -a scribus -g -ns -py "$py" >/dev/null 2>&1 \
    || { echo "failed: $src" >&2; exit 1; }
  echo "$out"
done
