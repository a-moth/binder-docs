#!/usr/bin/env python3
"""Draw the Health > Treatment page (Claude draft, labelled -claude).

Shared by medications and therapies, two per page. Each block: name, how well it
treats (fully / fully in combination with ___ ___ ___ / incompletely), a taped-notes
area beside that, and unlined space underneath with a square for a pill photo.
A Page box at the top lets diagnosis pages point here.
Usage: python3 scripts/build-health-treatment.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh health/treatment/*-claude.sla
Rerunning overwrites the draft, so stop using this once the user starts editing it.
"""
from sla_build import (BOTTOM, BROWN, CHECK, INNER, LEFT, LENS, MAIN, MONO, RIGHT, ROOT,
                       SANS, SANS_BOLD, Page)


def block(p, y, h):
    p.rect(LEFT, y, RIGHT - LEFT, h)
    p.field(LEFT + 8, y + 8, "Name", 50, RIGHT - 10)
    # How well it treats.
    cx, cy = LEFT + 10, y + 48
    p.checkbox(cx, cy)
    p.text(cx + CHECK + 5, cy - 3, 200, 20, "Fully treats", SANS, 12)
    cy += 28
    p.checkbox(cx, cy)
    p.text(cx + CHECK + 5, cy - 3, 220, 20, "Treats fully in combination with", SANS, 12)
    lx, lw = cx + CHECK + 5, 66.0
    for k in range(3):
        p.line(lx + k * (lw + 8), cy + 36, lw)
    cy += 56
    p.checkbox(cx, cy)
    p.text(cx + CHECK + 5, cy - 3, 200, 20, "Incompletely treats", SANS, 12)
    # Taped notes beside the checkboxes.
    nx, ny = 300.0, y + 42
    nb = cy + 26
    p.text(nx, ny - 4, 120, 24, "Notes", MONO, 16, color=BROWN)
    p.rect(nx, ny + 24, RIGHT - 10 - nx, nb - ny - 24, fill=LENS, width=INNER)
    # Unlined space underneath, with a square for a pill photo.
    dy = nb + 12
    photo = min(96.0, y + h - 10 - dy)
    p.rect(RIGHT - 10 - photo, dy, photo, photo, fill=LENS, width=INNER)


def treatments():
    p = Page("TREATMENTS", mushroom=False)
    p.text(LEFT, 80, 50, 23, "Page", SANS_BOLD, 14)
    p.rect(LEFT + 44, 80, 50, 22, fill=LENS, width=INNER)
    top, gap = 118.0, 14.0
    h = (BOTTOM - top - gap) / 2
    for i in range(2):
        block(p, top + i * (h + gap), h)
    return p


if __name__ == "__main__":
    print(treatments().write("health/treatment/treatments-claude.sla").relative_to(ROOT))
