#!/usr/bin/env python3
"""Build the binder's Lucide icon set into assets/<area>/.

Every icon is written as SVG and PNG in each colour its area uses:
  brown-highlight  Autumn theme default for new icons
  section          the area's cardstock colour (Ask Herby Design System)
  physical, neurodivergent, invisible, psychiatric, sensory
                   disability pride colours (Ask Herby Design System)

Usage: python3 scripts/make-icons.py   (needs network + `pip install cairosvg`)
Edit AREAS / COLOURS below, then rerun; output is overwritten.
"""
import pathlib
import re
import urllib.request

import cairosvg

LUCIDE_VERSION = "1.60.0"
PNG_SIZE = 512  # px; ~260 dpi at the binder's largest 50 mm icon frames
ROOT = pathlib.Path(__file__).resolve().parent.parent / "assets"

COLOURS = {
    "brown-highlight": "#AD7A4F",
    "cream-outline": "#6C5641",  # Autumn; icons on the cream divider/cover boxes (4.9:1)
    "physical": "#C07D78",
    "neurodivergent": "#D8C68A",
    "invisible": "#DEDAD0",
    "psychiatric": "#8FAEBD",
    "sensory": "#7F9E7C",
}

# Cardstock colour per area; None = no cardstock colour defined yet.
SECTION_COLOURS = {
    "core": "#B6BCC0",  # Front, cloudy
    "finance": "#5F6C42",
    "home": "#715C4D",
    "health": "#AE857F",
    "work": "#8B7D78",
    "learning": "#A3AF9F",
    "resources": "#E0C1B6",  # Media pink (Resources is the old Media section)
    "archive": "#A08A75",
    "travel": "#DAD0C4",  # reserve beige, the unused cardstock
}

AREAS = {
    "core": ["list-checks", "users", "file", "file-text", "mail", "receipt",
             "signpost", "timer", "compass", "leaf"],
    "finance": ["list-checks", "circle-dollar-sign", "circle-euro",
                "circle-pound-sterling", "coins", "wallet", "receipt",
                "piggy-bank", "calendar-range", "scan-line", "snowflake",
                "package", "utensils", "calendar"],
    "home": ["list-checks", "house", "house-heart", "broom-sparkles",
             "brush-cleaning", "sparkles", "package", "trending-up", "target",
             "calendar-range", "calendar"],
    "health": ["list-checks", "heart", "heart-pulse", "pill-bottle", "salad",
               "scan-heart", "stethoscope", "mail", "clipboard-list",
               "telescope", "calendar-range", "search"],
    "work": ["list-checks", "briefcase", "folder-kanban", "workflow", "users",
             "calendar-days", "layout-template", "archive", "calendar-range",
             "brain", "accessibility"],
    "learning": ["list-checks", "book", "book-text", "book-open",
                 "graduation-cap", "lightbulb", "compass"],
    "resources": ["list-checks", "book-alert", "book-text", "library",
                  "layout-template"],
    "archive": ["list-checks", "archive", "package-open", "box",
                "folder-archive", "calendar", "scan-line"],
    "travel": ["list-checks", "plane", "luggage", "map", "map-pinned",
               "ticket", "id-card", "file-text", "car", "train-front", "hotel"],
}

# Icons drawn on a pride-stripe tile: area -> icons. Writes <icon>-pride.{svg,png}.
PRIDE_TILES = {"work": ["list-checks"]}
PRIDE_ORDER = ["physical", "neurodivergent", "invisible", "psychiatric", "sensory"]
INK = "#3A1A08"      # hb-ink: brand text colour, used on all pride colours
OUTLINE = "#988C78"  # mark-outline taupe
ADMIN = "#626E7A"    # Admin cardstock blue (Ask Herby Design System)
CREAM_INK = "#EAD7AD"  # Autumn cream base, the icon colour on Admin blue

# Pride tile corners: top-left/bottom-right big, top-right/bottom-left small.
TILE_RADII = (7, 2.5, 7, 2.5)  # tl, tr, br, bl on the 24 px grid

_cache = {}


def rounded_rect(x, y, w, h, radii):
    tl, tr, br, bl = radii
    return (f"M{x + tl} {y}H{x + w - tr}A{tr} {tr} 0 0 1 {x + w} {y + tr}"
            f"V{y + h - br}A{br} {br} 0 0 1 {x + w - br} {y + h}"
            f"H{x + bl}A{bl} {bl} 0 0 1 {x} {y + h - bl}"
            f"V{y + tl}A{tl} {tl} 0 0 1 {x + tl} {y}Z")


def tile(svg, background, ink):
    """Lucide icon drawn in `ink` on a rounded tile filled with `background` (SVG markup)."""
    body = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S)[1]
    return (
        '<!-- @license lucide-static v' + LUCIDE_VERSION + ' - ISC -->\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
        '<clipPath id="tile"><path d="' + rounded_rect(0, 0, 24, 24, TILE_RADII) + '"/></clipPath>'
        f'<g clip-path="url(#tile)">{background}</g>'
        f'<path d="{rounded_rect(0.5, 0.5, 23, 23, [r - 0.5 for r in TILE_RADII])}" fill="none" stroke="{OUTLINE}"/>'
        f'<g transform="translate(12 12) scale(0.7) translate(-12 -12)" fill="none" '
        f'stroke="{ink}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
        f"{body}</g></svg>\n")


def pride_tile(svg):
    """Lucide icon in brand ink on diagonal stripes in disability-flag order."""
    band = 24 * 2 ** 0.5 / len(PRIDE_ORDER)
    stripes = "".join(
        f'<rect x="-12" y="{12 - 2.5 * band + i * band:.3f}" width="48" '
        f'height="{band + 0.05:.3f}" fill="{COLOURS[c]}"/>'
        for i, c in enumerate(PRIDE_ORDER))
    return tile(svg, f'<g transform="rotate(45 12 12)">{stripes}</g>', INK)


def admin_tile(svg):
    """Lucide icon in cream on a plain Admin-blue tile."""
    return tile(svg, f'<rect width="24" height="24" fill="{ADMIN}"/>', CREAM_INK)


def write(stem, svg):
    stem.with_suffix(".svg").write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(stem.with_suffix(".png")),
                     output_width=PNG_SIZE, output_height=PNG_SIZE)


def lucide(name):
    if name not in _cache:
        url = f"https://unpkg.com/lucide-static@{LUCIDE_VERSION}/icons/{name}.svg"
        with urllib.request.urlopen(url) as r:
            _cache[name] = r.read().decode()
    return _cache[name]


def main():
    for area, icons in AREAS.items():
        colours = dict(COLOURS)
        if SECTION_COLOURS[area]:
            colours["section"] = SECTION_COLOURS[area]
        out = ROOT / area
        out.mkdir(parents=True, exist_ok=True)
        for icon in icons:
            svg = lucide(icon)  # keeps Lucide's ISC licence comment
            for cname, hexcode in colours.items():
                write(out / f"{icon}-{cname}", svg.replace("currentColor", hexcode))
        for icon in PRIDE_TILES.get(area, []):
            write(out / f"{icon}-pride", pride_tile(lucide(icon)))
        write(out / "list-checks-admin", admin_tile(lucide("list-checks")))
        print(f"{area}: {len(icons)} icons x {len(colours)} colours")


if __name__ == "__main__":
    main()
