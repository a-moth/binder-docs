#!/usr/bin/env python3
"""Draw the Home > Monthly pages (Claude drafts, labelled -claude).

  overview          month + season, every seasonal item with how often and where it lives
  <item> pages      one detail page per item: checklist (When + Length per line) + notes

Usage: python3 scripts/build-home-monthly.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh home/monthly/*-claude.sla
Rerunning overwrites the drafts, so stop using this once the user starts editing them.
"""
from sla_build import (BOTTOM, BROWN, CHECK, INNER, LEFT, LENS, MONO, RIGHT, ROOT, SANS,
                       SANS_BOLD, Page)

ROOMS = ["Bedroom", "Office", "Living room", "Kitchen", "Bathroom"]
SECTIONS = ["Finance", "Home", "Health", "Work", "Learning", "Resources", "Archive", "Travel"]
MONTHLY, START = "every month", "start of season"

# (slug, header title, item name, how often, pre-filled checklist lines)
DETAIL = {
    "vacuum": ("VACUUM", "Vacuum / sweep all floors", MONTHLY, ROOMS),
    "refresh-bathroom": ("BATHROOM", "Refresh bathroom", MONTHLY,
                         ["Clean bathtub", "Refresh toilet cleaner"]),
    "review-binder": ("BINDER REVIEW", "Review binder in total", START, SECTIONS),
    "kitchen-cabinets": ("CABINETS", "Sort through all kitchen cabinets", START, []),
    "under-bed-sort": ("UNDER BED", "Sort through under-bed storage", START, []),
    "swap-clothes": ("SWAP CLOTHES", "Swap clothes in under-bed storage", START, []),
    "radiators": ("RADIATORS", "Clean radiators", MONTHLY, ROOMS),
}

# Overview groups: (heading, [(item, how often, detail slug or "see …" page)])
GROUPS = [
    ("Every season", [
        ("Vacuum / sweep all floors", MONTHLY, "vacuum"),
        ("Refresh bathroom", MONTHLY, "refresh-bathroom"),
        ("Change bedding", MONTHLY, ""),
        ("Update pantry", MONTHLY, "see Pantry stock"),
        ("Update freezer", MONTHLY, "see Freezer stock"),
        ("Update inventory", START, "see Inventory"),
        ("Review binder in total", START, "review-binder"),
    ]),
    ("Spring & Autumn", [
        ("Sort through all kitchen cabinets", START, "kitchen-cabinets"),
        ("Sort through under-bed storage", START, "under-bed-sort"),
    ]),
    ("Summer & Winter", [
        ("Clean radiators", MONTHLY, "radiators"),
        ("Swap clothes in under-bed storage", START, "swap-clothes"),
    ]),
]

ROW_H = 26.0
FREQ_X, PAGE_X = 330.0, 452.0


def overview():
    p = Page("MONTHLY")
    p.field(LEFT, 80, "Month", 55, 300)
    # Season: one box each, plus start of season.
    p.text(LEFT, 112, 60, 23, "Season", SANS_BOLD, 14)
    x = LEFT + 62
    for label, w in [("Spring", 52), ("Summer", 60), ("Autumn", 58), ("Winter", 54)]:
        p.checkbox(x, 114)
        p.text(x + CHECK + 4, 112, w, 20, label, SANS_BOLD, 12)
        x += CHECK + 10 + w
    p.checkbox(LEFT + 62, 144)  # own line: the mushroom patch sits at the end of the season row
    p.text(LEFT + 62 + CHECK + 4, 142, 120, 20, "Start of season", SANS_BOLD, 12)
    y = 190.0
    for heading, items in GROUPS:
        h = 34 + len(items) * ROW_H + 8
        p.rect(LEFT, y, RIGHT - LEFT, h)
        p.text(LEFT + 7, y + 6, 250, 24, heading, MONO, 16, color=BROWN)
        p.text(FREQ_X, y + 12, 110, 16, "How often", SANS_BOLD, 10)
        p.text(PAGE_X, y + 12, 100, 16, "Page", SANS_BOLD, 10)
        for i, (item, freq, ref) in enumerate(items):
            ry = y + 34 + i * ROW_H
            p.checkbox(LEFT + 9, ry + 4)
            p.text(LEFT + 9 + CHECK + 6, ry + 1, FREQ_X - LEFT - 30, 20, item, SANS, 12)
            p.text(FREQ_X, ry + 3, 120, 18, freq, SANS_BOLD, 10)
            if not ref:
                pass  # single job: no detail page
            elif ref.startswith("see "):
                p.text(PAGE_X, ry + 3, RIGHT - PAGE_X - 8, 18, ref, SANS_BOLD, 10)
            else:
                p.rect(PAGE_X, ry + 2, 50, 18, fill=LENS, width=INNER)
        y += h + 14
    return p


def detail(title, item, freq, prefill):
    p = Page(title)
    p.text(LEFT, 80, 420, 24, item, MONO, 16, color=BROWN)
    p.text(LEFT, 106, 300, 18, freq.capitalize(), SANS_BOLD, 12)
    p.field(LEFT, 132, "Month", 55, 300)

    top, notes_h = 190.0, 150.0
    rows = 15
    list_h = 34 + rows * ROW_H + 8
    p.rect(LEFT, top, RIGHT - LEFT, list_h)
    p.text(LEFT + 7, top + 6, 250, 24, "Checklist", MONO, 16, color=BROWN)
    when_x, length_x = 368.0, 458.0
    p.text(when_x, top + 12, 80, 16, "When", SANS_BOLD, 10)
    p.text(length_x, top + 12, 80, 16, "Length", SANS_BOLD, 10)
    for i in range(rows):
        ry = top + 34 + i * ROW_H
        p.checkbox(LEFT + 9, ry + 4)
        lx = LEFT + 9 + CHECK + 6
        if i < len(prefill):
            p.text(lx, ry + 1, when_x - lx - 12, 20, prefill[i], SANS, 12)
        p.line(lx, ry + 19, when_x - 12 - lx)
        p.line(when_x, ry + 19, length_x - 12 - when_x)
        p.line(length_x, ry + 19, RIGHT - 9 - length_x)

    ny = top + list_h + 14
    p.rect(LEFT, ny, RIGHT - LEFT, BOTTOM - ny)
    p.text(LEFT + 7, ny + 6, 200, 24, "Notes", MONO, 16, color=BROWN)
    y = ny + 50
    while y < BOTTOM - 8:
        p.line(LEFT + 7, y, RIGHT - LEFT - 14)
        y += 25
    return p


if __name__ == "__main__":
    print(overview().write("home/monthly/overview-claude.sla").relative_to(ROOT))
    for slug, args in DETAIL.items():
        print(detail(*args).write(f"home/monthly/{slug}-claude.sla").relative_to(ROOT))
