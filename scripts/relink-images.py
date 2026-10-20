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
Every frame linked into assets/ is scaled to its frame (checklists stretched to fill,
others proportional and centred) so a different pixel size can't change the printed size.
"""
import os
import pathlib
import re

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Which area's colour a document's checklist uses.
DOC_AREA = {
    "core/core-layouts.sla": "core",
    "finance/yearly-budget.sla": "finance",
    "finance/budgets/budget-templates.sla": "finance",
    "home/strategy/cleaning/cleaning-docs-templates.sla": "home",
    "home/strategy/cleaning/cleaning-docs-templates-fillable.sla": "home",
    "work/projects/projects-three-section.sla": "work",
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


def fit(tag, image, stretch):
    """Scale the image to its frame and store the scale explicitly
    (headless Scribus uses LOCALSCX/Y as saved rather than refitting).
    stretch=True is Scribus's "scale to frame" with proportional off."""
    if not image.exists():
        return tag
    attr = lambda k: float(re.search(rf' {k}="([^"]+)"', tag)[1])
    w, h = attr("WIDTH"), attr("HEIGHT")
    pw, ph = Image.open(image).size  # no DPI metadata: Scribus reads 1 px = 1 pt
    sx, sy = w / pw, h / ph
    if not stretch:
        sx = sy = min(sx, sy)
    # LOCALX/Y are in image units: centre the scaled image in the frame.
    values = {"SCALETYPE": "1", "RATIO": "0" if stretch else "1",
              "LOCALSCX": repr(sx), "LOCALSCY": repr(sy),
              "LOCALX": repr((w - pw * sx) / 2 / sx), "LOCALY": repr((h - ph * sy) / 2 / sy)}
    for k, v in values.items():
        tag = re.sub(rf' {k}="[^"]*"', f' {k}="{v}"', tag)
    return tag


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
        tag = tag.replace(m[0], f'PFILE="{to_assets}/{dest}"')
        return fit(tag, ROOT / "assets" / dest, stretch="/list-checks-" in dest)

    text = re.sub(r"<(?:PAGEOBJECT|MASTEROBJECT)\b[^>]*>", fix, text)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    for rel, area in DOC_AREA.items():
        relink(rel, area)
        print(rel)
