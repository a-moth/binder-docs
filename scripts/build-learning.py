#!/usr/bin/env python3
"""Draw the Learning pages (Claude drafts, labelled -claude).

Interest (one set per special interest):
  interest-profile    name, since, strength 1-10, what I love, key words, people, resources, focus
  design-plan         project, goal, sketch / taping area, steps to tick, materials with cost
  collection-log      item, where from, date, currency, cost, Have / Want, kept where
  collection-pocket   a space to glue a pocket for small collected things
Explore:
  explore-log         interest, ADHD / Autism, how to access it
  certificates        certificate, from, date, kept in a pocket / digital
The user designs the AAC boards themselves.
Usage: python3 scripts/build-learning.py
Then:  python3 scripts/relink-images.py && python3 scripts/make-fillable.py <each page>
       && scripts/export-pdf.sh <each page and its fillable twin>
Rerunning overwrites the drafts, so stop using this once the user starts editing them.
"""
from sla_build import (BOTTOM, BROWN, CHECK, CREAM, INNER, LEFT, LENS, MAIN, MONO, MONO_ITALIC,
                       RIGHT, ROOT, ROW, SANS_BOLD, TABLE_W, TABLE_X, TABLE_Y, WRITE_GAP, Page,
                       centre_checks, lined_box, table)

TOP, GAP = 190.0, 14.0


def stacked(p, x0, top, rows, row_h, labels, box=11.0, gap=4.0):
    """Two labelled boxes stacked in each row (as on Subscriptions)."""
    pad = (row_h - 2 * box - gap) / 2
    for i in range(rows):
        for j, label in enumerate(labels):
            y = top + i * row_h + pad + j * (box + gap)
            p.rect(x0 + 7, y, box, box, fill=LENS, width=INNER)
            p.text(x0 + 7 + box + 4, y - 1, 34, box + 2, label, SANS_BOLD, 9)  # stays in its column


def taping_area(p, x, y, w, h, title, note):
    p.rect(x, y, w, h)
    p.text(x + 7, y + 6, w - 14, 24, title, MONO, 16, color=BROWN)
    gy = y + 36
    p.rect(x + 10, gy, w - 20, y + h - 10 - gy, fill=LENS, width=INNER)
    if note:
        p.text(x + 10, gy + (y + h - 10 - gy) / 2 - 12, w - 20, 24, note, MONO_ITALIC, 14,
               color=BROWN, align=1)


def profile():
    p = Page("INTEREST")
    p.field(LEFT, 80, "Interest", 70, 470)
    p.field(LEFT, 112, "Since", 50, 250)
    # Strength right now: tick one of 1-10.
    p.text(LEFT, 146, 110, 20, "Strength now", SANS_BOLD, 14)
    for n in range(10):
        x = LEFT + 115 + n * 33
        p.text(x - 6, 140, 26, 12, str(n + 1), MONO, 9, align=1)
        p.checkbox(x, 152)
    w = (RIGHT - LEFT - GAP) / 2
    lined_box(p, LEFT, TOP, RIGHT - LEFT, 120, "What I love about it")
    y = TOP + 120 + GAP
    lined_box(p, LEFT, y, w, 170, "Key words & facts")
    lined_box(p, LEFT + w + GAP, y, w, 170, "People & communities")
    y += 170 + GAP
    lined_box(p, LEFT, y, w, BOTTOM - y, "Resources")
    lined_box(p, LEFT + w + GAP, y, w, BOTTOM - y, "Current focus")
    return p


def materials(p, x, y, w, h):
    """Materials box: a small Item / Currency / Cost grid (Weekly-page table style)."""
    p.rect(x, y, w, h)
    p.text(x + 7, y + 6, w - 14, 24, "Materials", MONO, 16, color=BROWN)
    cols = [(x + 7, "Item"), (x + w - 125, "Currency"), (x + w - 58, "Cost")]
    top, row_h = y + 56, 25.0
    rows = int((y + h - 8 - top) // row_h)
    x0, x1 = x + 7, x + w - 7
    p.rect(x0, top, x1 - x0, rows * row_h, fill=CREAM, stroke=CREAM, width=1)
    for i in range(rows + 1):
        p.line(x0, top + i * row_h, x1 - x0, MAIN, BROWN)  # same weight as the Weekly table
    for cx, _ in cols[1:]:
        p.line(cx, top, rows * row_h, MAIN, BROWN, rot=90)
    ends = [c for c, _ in cols[1:]] + [x1]
    for (cx, label), cx1 in zip(cols, ends):
        p.text(cx + 1, top - 20, cx1 - cx - 2, 18, label, SANS_BOLD, 10)


def design_plan():
    p = Page("DESIGN PLAN")
    p.field(LEFT, 80, "Interest", 70, 470)
    p.field(LEFT, 112, "Project", 65, 470)
    lined_box(p, LEFT, TOP, RIGHT - LEFT, 70, "Goal")
    y = TOP + 70 + GAP
    taping_area(p, LEFT, y, RIGHT - LEFT, 250, "Sketch", "")
    y += 250 + GAP
    w = (RIGHT - LEFT - GAP) / 2
    # Steps to tick off
    p.rect(LEFT, y, w, BOTTOM - y)
    p.text(LEFT + 7, y + 6, w - 14, 24, "Steps", MONO, 16, color=BROWN)
    ly = y + 50
    while ly < BOTTOM - 8:
        p.checkbox(LEFT + 8, ly - CHECK + 1)
        p.line(LEFT + 8 + CHECK + 6, ly, w - CHECK - 21)
        ly += WRITE_GAP
    materials(p, LEFT + w + GAP, y, w, BOTTOM - y)
    return p


def collection_log():
    p = Page("COLLECTION")
    p.field(LEFT, 80, "Interest", 70, 470)
    rows, row_h = 17, 34.0
    status, kept = 392, 452
    table(p, [(TABLE_X, "Item"), (140, "Where from"), (226, "Date"), (274, "Currency"),
              (345, "Cost"), (status, None), (kept, "Kept where")], rows, row_h)
    stacked(p, status, TABLE_Y, rows, row_h, ("Have", "Want"))
    return p


def collection_pocket():
    p = Page("POCKET")
    p.field(LEFT, 80, "Interest", 70, 470)
    taping_area(p, LEFT, TOP, RIGHT - LEFT, BOTTOM - TOP, "Collection pocket",
                "glue or tape pocket here")
    return p


def explore_log():
    p = Page("EXPLORE")
    p.field(LEFT, 80, "Updated", 75, 300)
    rows = 20
    adhd, autism, access = 220, 280, 345
    table(p, [(TABLE_X, "Interest"), (adhd, "ADHD"), (autism, "Autism"),
              (access, "How to access it")], rows)
    centre_checks(p, adhd, autism, TABLE_Y, rows)
    centre_checks(p, autism, access, TABLE_Y, rows)
    return p


def certificates():
    p = Page("CERTIFICATES")
    p.field(LEFT, 80, "Updated", 75, 300)
    rows, row_h = 17, 34.0
    kept = 470
    table(p, [(TABLE_X, "Certificate"), (260, "From"), (400, "Date"), (kept, "Kept")],
          rows, row_h)
    stacked(p, kept, TABLE_Y, rows, row_h, ("Pocket", "Digital"))
    return p


PAGES = {
    "learning/interest/interest-profile": profile,
    "learning/interest/design-plan": design_plan,
    "learning/interest/collection-log": collection_log,
    "learning/interest/collection-pocket": collection_pocket,
    "learning/explore/explore-log": explore_log,
    "learning/explore/certificates": certificates,
}

if __name__ == "__main__":
    for name, build in PAGES.items():
        print(build().write(f"{name}-claude.sla").relative_to(ROOT))
