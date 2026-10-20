#!/usr/bin/env python3
"""Draw the binder's custom (non-Lucide) illustrations into assets/custom/.

  bigmushroom      Lucide-style mushroom (Lucide has none), outlined in the
                   disability pride colours in flag order, filled with
                   the same colours darker and duller
  mushroomvarious  a small patch of three of those mushrooms on a yellow oval

Usage: python3 scripts/make-custom.py   (needs `pip install cairosvg`)
"""
import colorsys
import pathlib

import cairosvg

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "custom"
PNG_SIZE = 1024

# Brand pride colours in disability-flag order (Ask Herby Design System).
PRIDE = ["#C07D78", "#D8C68A", "#DEDAD0", "#8FAEBD", "#7F9E7C"]
TAUPE = "#988C78"         # mark-outline taupe
PATCH = "#E3CD9E"         # yellow from the user's original pixel mark

# Lucide grid: 24 px, 2 px stroke, round caps and joins.
CAP = "M3 13a9 9 0 0 1 18 0z"
STEM = "M9 13v5a3 3 0 0 0 6 0v-5"
SPOTS = ["M8 9h.01", "M12 6.5h.01", "M16 9.5h.01"]


LINE = 2.6      # pride line weight (Lucide default is 2)
UNDERLAY = 3.6  # taupe line under it
FILL_LIGHTNESS = 0.62   # fills: pride colours darkened ...
FILL_SATURATION = 0.55  # ... and dulled


def muted(hexcode):
    r, g, b = (int(hexcode[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, l * FILL_LIGHTNESS, s * FILL_SATURATION)
    return "#%02X%02X%02X" % tuple(round(v * 255) for v in (r, g, b))


def gradient(gid, colours):
    # Diagonal hard-stop gradient: stripes run top-left to bottom-right,
    # first colour at the top right, as on the flag.
    n = len(colours)
    stops = "".join(
        f'<stop offset="{i / n:.2f}" stop-color="{c}"/><stop offset="{(i + 1) / n:.2f}" stop-color="{c}"/>'
        for i, c in enumerate(colours))
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="19" y1="4" x2="7" y2="20">{stops}</linearGradient>')


def gradients():
    return gradient("pride", PRIDE) + gradient("pride-fill", [muted(c) for c in PRIDE])


def mushroom(scale=1.0):
    """One mushroom on the 24 px grid. Stroke widths are divided by `scale`
    so every mushroom in a group prints with the same line weight."""
    paths = "".join(f'<path d="{d}"/>' for d in [CAP, STEM, *SPOTS])
    common = 'stroke-linecap="round" stroke-linejoin="round"'
    body = f'<path d="{CAP}"/><path d="{STEM} z"/>'
    return (
        f'<g fill="url(#pride-fill)" stroke="none">{body}</g>'
        # Taupe underlay keeps the pale stripes visible on white paper.
        + f'<g fill="none" {common} stroke="{TAUPE}" stroke-width="{UNDERLAY / scale:.3f}">{paths}</g>'
        + f'<g fill="none" {common} stroke="url(#pride)" stroke-width="{LINE / scale:.3f}">{paths}</g>')


def bigmushroom():
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
            f"{gradients()}{mushroom()}</svg>\n")


# (x offset, y offset, scale) on a 48 px canvas, back to front.
PATCH_MUSHROOMS = [(26.5, 14.5, 0.8), (3.5, 17.5, 0.65), (10.5, 6.5, 1.1)]


def mushroomvarious():
    group = "".join(
        f'<g transform="translate({x} {y}) scale({s})">{mushroom(s)}</g>'
        for x, y, s in PATCH_MUSHROOMS)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">'
            f'{gradients()}<ellipse cx="24" cy="31.5" rx="21" ry="6" fill="{PATCH}"/>'
            f"{group}</svg>\n")


def main():
    for name, svg in [("mushroomvarious", mushroomvarious()), ("bigmushroom", bigmushroom())]:
        (OUT / f"{name}.svg").write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(OUT / f"{name}.png"),
                         output_width=PNG_SIZE, output_height=PNG_SIZE)
        print(name)


if __name__ == "__main__":
    main()
