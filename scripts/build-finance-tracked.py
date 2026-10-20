#!/usr/bin/env python3
"""Draw the Finance > Tracked pages (Claude drafts, labelled -claude).

Usage: python3 scripts/build-finance-tracked.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh finance/tracked/*-claude.sla
Rerunning overwrites the drafts, so stop using this once the user starts editing them.
"""
from sla_build import (BOTTOM, BROWN, CHECK, CREAM, HEAD_Y, INNER, LEFT, LENS, MAIN, MONO,
                       MONO_ITALIC, RIGHT, ROOT, ROW, SANS_BOLD, TABLE_W, TABLE_X, TABLE_Y,
                       WRITE_GAP, Page, centre_checks, table)

DIR = "finance/tracked"
def subscriptions():
    p = Page("SUBSCRIPTIONS")
    p.field(LEFT, 80, "Updated", 75, 300)
    p.field(LEFT, 112, "Total per month", 125, 470)
    use, unused, end = 394, 474, TABLE_X + TABLE_W
    rows, row_h, box, gap = 17, 34.0, 11.0, 4.0
    table(p, [(TABLE_X, "Name"), (190, "Cost"), (250, "Currency"), (320, "Renews"),
              (use, None), (unused, None)], rows, row_h)
    # Two unnamed status columns, two stacked boxes in each cell.
    pad = (row_h - 2 * box - gap) / 2
    for x0, labels in [(use, ("Trial", "Active")), (unused, ("Paused", "Cancelled"))]:
        for i in range(rows):
            for j, label in enumerate(labels):
                y = TABLE_Y + i * row_h + pad + j * (box + gap)
                p.rect(x0 + 7, y, box, box, fill=LENS, width=INNER)
                p.text(x0 + 7 + box + 4, y - 1, 60, box + 2, label, SANS_BOLD, 9)
    return p


def savings():
    p = Page("SAVINGS")
    p.field(LEFT, 80, "Year", 45, 260)
    p.field(LEFT, 112, "Total saved", 95, 470)
    top, gap = 190.0, 14.0
    w = (RIGHT - LEFT - gap) / 2
    h = (BOTTOM - top - gap) / 2
    for row in range(2):
        for col in range(2):
            x, y = LEFT + col * (w + gap), top + row * (h + gap)
            p.rect(x, y, w, h)
            p.field(x + 7, y + 7, "Goal", 45, x + w - 10, 14)
            p.field(x + 7, y + 37, "Pocket #", 75, x + w - 110, 14)
            p.text(x + w - 98, y + 37, 70, 23, "Reached", SANS_BOLD, 12)
            p.checkbox(x + w - 25, y + 40)
            gy = y + 72
            p.rect(x + 10, gy, w - 20, y + h - 10 - gy, fill=LENS, width=INNER)
            p.text(x + 10, gy + (y + h - 10 - gy) / 2 - 12, w - 20, 24,
                   "glue or tape pocket here", MONO_ITALIC, 14, color=BROWN, align=1)
    return p


def goals():
    p = Page("GOALS")
    p.field(LEFT, 80, "Updated", 75, 300)
    p.field(LEFT, 112, "Savings available", 140, 470)
    rows, row_h = 10, 2 * ROW
    inc, wanted, cost = 170, 390, 470
    table(p, [(TABLE_X, "Want"), (inc, "Description"), (wanted, "Wanted on"),
              (cost, "Est. cost")], rows, row_h)
    return p


def cash():
    p = Page("CASH")
    p.field(LEFT, 80, "Last updated", 105, 360)
    top = 190.0
    box_h = 4 * 52 + 50
    p.rect(LEFT, top, RIGHT - LEFT, box_h)
    p.text(LEFT + 7, top + 7, 200, 24, "Current cash", MONO, 16, color=BROWN)
    for i, (icon, label) in enumerate([("circle-euro", "EUR"), ("circle-pound-sterling", "GBP"),
                                       ("circle-dollar-sign", "USD"), (None, "")]):
        y = top + 44 + i * 52
        if icon:
            p.image(LEFT + 14, y, 36, 36, f"finance/{icon}-brown-highlight.png")
            p.text(LEFT + 58, y + 6, 50, 24, label, SANS_BOLD, 14)
        else:
            p.line(LEFT + 14, y + 30, 90, MAIN, BROWN)
        p.line(LEFT + 120, y + 30, RIGHT - LEFT - 140, MAIN, BROWN)
    ny = top + box_h + 14
    p.rect(LEFT, ny, RIGHT - LEFT, BOTTOM - ny)
    p.text(LEFT + 7, ny + 7, 200, 24, "Cash pocket", MONO, 16, color=BROWN)
    gy = ny + 40
    p.rect(LEFT + 10, gy, RIGHT - LEFT - 20, BOTTOM - 10 - gy, fill=LENS, width=INNER)
    p.text(LEFT + 10, gy + (BOTTOM - 10 - gy) / 2 - 12, RIGHT - LEFT - 20, 24,
           "glue or tape cash pocket here", MONO_ITALIC, 14, color=BROWN, align=1)
    return p


def groceries():
    p = Page("GROCERIES")
    p.field(LEFT, 80, "Week of", 70, 300)
    p.field(LEFT, 112, "Total spent", 95, 470)
    rows = 20
    eaten, freezer, pantry, end = 300, 385, 470, TABLE_X + TABLE_W
    table(p, [(TABLE_X, "Item"), (230, "Cost"), (eaten, None), (freezer, None), (pantry, None)], rows)
    for x0, x1, icon, label in [(eaten, freezer, "utensils", "Eaten"),
                                (freezer, pantry, "snowflake", "Freezer"),
                                (pantry, end, "package", "Pantry")]:
        p.image(x0 + 4, HEAD_Y, 18, 18, f"finance/{icon}-brown-highlight.png")
        p.text(x0 + 25, HEAD_Y, x1 - x0 - 25, 20, label)
        centre_checks(p, x0, x1, TABLE_Y, rows)
    return p


def stock(title, icon):
    p = Page(title)
    p.field(LEFT, 80, "Updated", 75, 300)
    top, gap, n = 190.0, 9.5, 5
    h = (BOTTOM - top - gap * (n - 1)) / n
    outer, inner = 50.0, 26.0
    for i in range(n):
        y = top + i * (h + gap)
        p.rect(LEFT, y, RIGHT - LEFT, h)
        cx, cy = p.ring(LEFT + 14 + outer, y + h / 2, outer, inner)
        p.segments(cx, cy, outer, inner, 8)
        tx = LEFT + 14 + 2 * outer + 18
        p.image(tx, y + 9, 18, 18, f"finance/{icon}-brown-highlight.png")
        p.field(tx + 22, y + 7, "Item", 45, RIGHT - 10, 14)
        p.text(tx, y + 34, 120, 18, "Meal ideas", SANS_BOLD, 10)
        p.write_lines(tx, RIGHT - 10, y + 56, 3, (h - 66) / 2)
    return p


PAGES = {
    "subscriptions": subscriptions,
    "savings-pockets": savings,
    "goals": goals,
    "cash-pocket": cash,
    "groceries-weekly": groceries,
    "pantry-stock": lambda: stock("PANTRY", "package"),
    "freezer-stock": lambda: stock("FREEZER", "snowflake"),
}

if __name__ == "__main__":
    for name, build in PAGES.items():
        print(build().write(f"{DIR}/{name}-claude.sla").relative_to(ROOT))
