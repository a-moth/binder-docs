#!/usr/bin/env python3
"""Draw the binder's custom (non-Lucide) illustrations into assets/custom/.

  bigmushroom      Lucide-style mushroom (Lucide has none), outlined in the
                   disability pride colours in flag order
  mushroomvarious  a small patch of three of those mushrooms on a yellow oval

Usage: python3 scripts/make-custom.py   (needs `pip install cairosvg`)
"""
import pathlib

import cairosvg

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "custom"
PNG_SIZE = 1024

# Brand pride colours in disability-flag order (Ask Herby Design System).
PRIDE = ["#C07D78", "#D8C68A", "#DEDAD0", "#8FAEBD", "#7F9E7C"]
TAUPE = "#988C78"         # mark-outline taupe
PAPER = "#FFFFFF"         # hb-paper
PATCH = "#E3CD9E"         # yellow from the user's original pixel mark

# Lucide grid: 24 px, 2 px stroke, round caps and joins.
CAP = "M3 13a9 9 0 0 1 18 0z"
STEM = "M9 13v5a3 3 0 0 0 6 0v-5"
SPOTS = ["M8 9h.01", "M12 6.5h.01", "M16 9.5h.01"]


def gradient():
    # Diagonal hard-stop gradient: stripes run top-left to bottom-right,
    # first colour at the top right, as on the flag.
    n = len(PRIDE)
    stops = "".join(
        f'<stop offset="{i / n:.2f}" stop-color="{c}"/><stop offset="{(i + 1) / n:.2f}" stop-color="{c}"/>'
        for i, c in enumerate(PRIDE))
    return ('<linearGradient id="pride" gradientUnits="userSpaceOnUse" '
            f'x1="19" y1="4" x2="7" y2="20">{stops}</linearGradient>')


def mushroom(fill="none", scale=1.0):
    """One mushroom on the 24 px grid. Stroke widths are divided by `scale`
    so every mushroom in a group prints with the same line weight."""
    paths = "".join(f'<path d="{d}"/>' for d in [CAP, STEM, *SPOTS])
    common = 'stroke-linecap="round" stroke-linejoin="round"'
    body = f'<path d="{CAP}"/><path d="{STEM} z"/>'
    return (
        (f'<g fill="{fill}" stroke="none">{body}</g>' if fill != "none" else "")
        # Taupe underlay keeps the pale stripes visible on white paper.
        + f'<g fill="none" {common} stroke="{TAUPE}" stroke-width="{3.4 / scale:.3f}">{paths}</g>'
        + f'<g fill="none" {common} stroke="url(#pride)" stroke-width="{2 / scale:.3f}">{paths}</g>')


def bigmushroom():
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
            f"{gradient()}{mushroom()}</svg>\n")


# (x offset, y offset, scale) on a 48 px canvas, back to front.
PATCH_MUSHROOMS = [(26.5, 14.5, 0.8), (3.5, 17.5, 0.65), (10.5, 6.5, 1.1)]


def mushroomvarious():
    group = "".join(
        f'<g transform="translate({x} {y}) scale({s})">{mushroom(PAPER, s)}</g>'
        for x, y, s in PATCH_MUSHROOMS)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">'
            f'{gradient()}<ellipse cx="24" cy="31.5" rx="21" ry="6" fill="{PATCH}"/>'
            f"{group}</svg>\n")


def main():
    for name, svg in [("mushroomvarious", mushroomvarious()), ("bigmushroom", bigmushroom())]:
        (OUT / f"{name}.svg").write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(OUT / f"{name}.png"),
                         output_width=PNG_SIZE, output_height=PNG_SIZE)
        print(name)


if __name__ == "__main__":
    main()
