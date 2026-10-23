#!/usr/bin/env python3
"""Point every image frame in the binder's .sla files at assets/.

Usage: python3 scripts/relink-images.py
Rules:
  checklist.png         -> assets/<area>/list-checks-admin.png  (cream on an Admin-blue
                           tile; Work uses the pride-stripe tile list-checks-pride.png)
  section divider icons -> assets/<area>/<icon>-cream-outline.png
                           (they sit on the dividers' cream box; 4.9:1)
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

# A document's area (its checklist colour) is its top-level folder.
def doc_area(rel):
    return pathlib.PurePath(rel).parts[0]


CORE_ICONS = {
    "user-group.png": "core/users-brown-highlight.png",
    "envelope.png": "core/mail-brown-highlight.png",
    "file.png": "core/file-brown-highlight.png",
    "receipt.png": "core/receipt-brown-highlight.png",
    "signpointingright.png": "core/signpost-brown-highlight.png",
    "brownleaves.png": "core/leaf-brown-highlight.png",
}
# Checklist variant per area: Admin-blue tile by default, Work keeps the pride tile.
CHECKLIST_VARIANT = {"work": "pride"}
CHECKLIST_DEFAULT = "admin"
CUSTOM = {"mushroomvarious.png", "bigmushroom.png"}


def target(pfile, area):
    name = pfile.split("/")[-1]
    if name == "checklist.png":
        return f"{area}/list-checks-{CHECKLIST_VARIANT.get(area, CHECKLIST_DEFAULT)}.png"
    if name in CORE_ICONS:
        return CORE_ICONS[name]
    if name.startswith("list-checks-"):
        return target("checklist.png", area)
    if name in CUSTOM:
        return f"custom/{name}"
    m = re.fullmatch(r"(\w+)/([\w-]+?)(?:-brown-highlight|-cream-outline)?\.png", pfile)
    # Section icons on the dividers (core-layouts) sit on the cream box: cream outline,
    # because brown highlight is only 2.6:1 on cream.
    variant = "cream-outline" if area == "core" and m and m[1] != "core" else "brown-highlight"
    if pfile.endswith("-cream-outline.png"):
        variant = "cream-outline"  # already chosen on purpose (covers): keep it
    if m and (ROOT / "assets" / m[1] / f"{m[2]}-{variant}.png").exists():
        return f"{m[1]}/{m[2]}-{variant}.png"
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
    import subprocess
    files = subprocess.run(["git", "ls-files", "--others", "--cached", "--exclude-standard", "*.sla"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    for rel in files:
        relink(rel, doc_area(rel))
        print(rel)
