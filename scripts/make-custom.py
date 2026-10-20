#!/usr/bin/env python3
"""Draw the binder's custom (non-Lucide) illustrations into assets/custom/.

  mushroomvarious  the Ask Herby mark on a cream circle with a tiny leaf
  bigmushroom      Lucide-style mushroom (Lucide has none), outlined in the
                   disability pride colours in flag order

Usage: python3 scripts/make-custom.py   (needs `pip install cairosvg`)
"""
import pathlib

import cairosvg

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "custom"
PNG_SIZE = 1024

# Brand pride colours in disability-flag order (Ask Herby Design System).
PRIDE = ["#C07D78", "#D8C68A", "#DEDAD0", "#8FAEBD", "#7F9E7C"]
MARK_OUTLINE = "#58575C"  # outline used in the user's mark artwork
TAUPE = "#988C78"         # mark-outline taupe
CREAM = "#EAD7AD"         # Autumn cream base
CREAM_OUTLINE = "#6C5641" # Autumn outline of cream base
COPPER = "#9A5126"        # Autumn copper base
BROWN_DARK = "#4A2A1A"    # Autumn brown dark

# The mark, measured from the user's 375 px artwork: (cx, cy, fill radius, colour).
MARK = [
    (244.5, 60.5, 5.0, PRIDE[0]),
    (287.5, 80.5, 12.0, PRIDE[1]),
    (334.0, 148.5, 25.5, PRIDE[2]),
    (297.0, 273.0, 46.5, PRIDE[3]),
    (95.0, 210.0, 80.5, PRIDE[4]),
]
MARK_STROKE = 7.0
MARK_CENTRE = (187.0, 187.0)  # centre of the mark's bounding box


def mushroomvarious():
    circles = "".join(
        f'<circle cx="{x}" cy="{y}" r="{r + MARK_STROKE / 2}" fill="{c}" '
        f'stroke="{MARK_OUTLINE}" stroke-width="{MARK_STROKE}"/>'
        for x, y, r, c in MARK)
    mx, my = MARK_CENTRE
    leaf = (f'<path d="M0 -24 C15 -11 15 11 0 24 C-15 11 -15 -11 0 -24 Z" fill="{COPPER}" '
            f'stroke="{BROWN_DARK}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M0 -14 V30" stroke="{BROWN_DARK}" stroke-width="4" stroke-linecap="round"/>')
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">'
        f'<circle cx="200" cy="200" r="190" fill="{CREAM}" stroke="{CREAM_OUTLINE}" stroke-width="12"/>'
        f'<g transform="translate(200 180) scale(0.86) translate({-mx} {-my})">{circles}</g>'
        f'<g transform="translate(200 340) rotate(-20) scale(1.15)">{leaf}</g>'
        '</svg>\n')


# Lucide grid: 24 px, 2 px stroke, round caps and joins.
MUSHROOM_PATHS = [
    "M3 13a9 9 0 0 1 18 0z",      # cap
    "M9 13v5a3 3 0 0 0 6 0v-5",   # stem
    "M8 9h.01", "M12 6.5h.01", "M16 9.5h.01",  # spots
]


def bigmushroom():
    n = len(PRIDE)
    stops = "".join(
        f'<stop offset="{i / n:.2f}" stop-color="{c}"/><stop offset="{(i + 1) / n:.2f}" stop-color="{c}"/>'
        for i, c in enumerate(PRIDE))
    paths = "".join(f'<path d="{d}"/>' for d in MUSHROOM_PATHS)
    common = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
        # Diagonal hard-stop gradient: stripes run top-left to bottom-right,
        # first colour at the top right, as on the flag.
        '<linearGradient id="pride" gradientUnits="userSpaceOnUse" x1="19" y1="4" x2="7" y2="20">'
        f"{stops}</linearGradient>"
        # Taupe underlay keeps the pale stripes visible on white paper.
        f'<g {common} stroke="{TAUPE}" stroke-width="3.4">{paths}</g>'
        f'<g {common} stroke="url(#pride)" stroke-width="2">{paths}</g>'
        '</svg>\n')


def main():
    for name, svg in [("mushroomvarious", mushroomvarious()), ("bigmushroom", bigmushroom())]:
        (OUT / f"{name}.svg").write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(OUT / f"{name}.png"),
                         output_width=PNG_SIZE, output_height=PNG_SIZE)
        print(name)


if __name__ == "__main__":
    main()
