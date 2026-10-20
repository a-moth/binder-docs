#!/usr/bin/env python3
"""Point every image frame in the binder's .sla files at assets/.

Usage: python3 scripts/relink-images.py
Rules:
  checklist.png         -> assets/<area>/list-checks-section.png  (page's area colour;
                           Work uses the pride-stripe tile list-checks-pride.png)
  section divider icons -> assets/<area>/<icon>-brown-highlight.png
                           (dividers print on cardstock in the section colour)
  other Lucide icons    -> assets/core/<icon>-brown-highlight.png
  custom illustrations  -> assets/custom/<file>   (supplied by hand)
Every frame linked into assets/ is set to fit-to-frame (SCALETYPE=0 -> 1) so a
different pixel size can't change the printed size.
"""
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Which area's colour a document's checklist uses.
DOC_AREA = {
    "core/core-layouts.sla.xml": "core",
    "finance/yearly-budget.sla.xml": "finance",
    "finance/budgets/budget-templates.sla.xml": "finance",
    "home/strategy/cleaning/cleaning-docs-templates.sla.xml": "home",
    "home/strategy/cleaning/cleaning-docs-templates-fillable.sla.xml": "home",
    "work/projects/projects-three-section.sla.xml": "work",
}

CORE_ICONS = {
    "user-group.png": "core/users-brown-highlight.png",
    "envelope.png": "core/mail-brown-highlight.png",
    "file.png": "core/file-brown-highlight.png",
    "receipt.png": "core/receipt-brown-highlight.png",
    "signpointingright.png": "core/signpost-brown-highlight.png",
    "brownleaves.png": "core/leaf-brown-highlight.png",
}
# Areas whose checklist uses a special variant instead of the section colour.
CHECKLIST_VARIANT = {"work": "pride"}
CUSTOM = {"mushroomvarious.png", "bigmushroom.png"}


def target(pfile, area):
    name = pfile.split("/")[-1]
    if name == "checklist.png":
        return f"{area}/list-checks-{CHECKLIST_VARIANT.get(area, 'section')}.png"
    if name in CORE_ICONS:
        return CORE_ICONS[name]
    if name.startswith("list-checks-"):
        return target("checklist.png", area)
    if name in CUSTOM:
        return f"custom/{name}"
    m = re.fullmatch(r"(\w+)/([\w-]+?)(?:-brown-highlight)?\.png", pfile)
    if m and (ROOT / "assets" / m[1] / f"{m[2]}-brown-highlight.png").exists():
        return f"{m[1]}/{m[2]}-brown-highlight.png"
    return None  # leave anything else (e.g. photos) untouched


def relink(rel, area):
    path = ROOT / rel
    to_assets = os.path.relpath(ROOT / "assets", path.parent)
    text = path.read_text(encoding="utf-8")

    def fix(tag):
        tag = tag.group(0)
        m = re.search(r'PFILE="([^"]+)"', tag)
        if not m:
            return tag
        dest = target(m[1].removeprefix(to_assets + "/"), area)  # rerun-safe
        if not dest:
            return tag
        tag = tag.replace('SCALETYPE="0"', 'SCALETYPE="1"')
        return tag.replace(m[0], f'PFILE="{to_assets}/{dest}"')

    text = re.sub(r"<(?:PAGEOBJECT|MASTEROBJECT)\b[^>]*>", fix, text)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    for rel, area in DOC_AREA.items():
        relink(rel, area)
        print(rel)
