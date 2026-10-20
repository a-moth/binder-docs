#!/usr/bin/env python3
"""Draw the Finance > Daily planning page (Claude draft, labelled -claude).

Usage: python3 scripts/build-finance-daily.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh finance/daily/*-claude.sla
Rerunning overwrites the draft, so stop using this once the user starts editing it.
"""
from sla_build import (ADMIN, BOTTOM, CREAM, INNER, LEFT, LENS, MAIN, MONO, RIGHT, ROOT,
                       SANS_BOLD, Page)

X0, X1 = 56.0, 540.0  # inset from the margins: white space at the page edges


def daily():
    p = Page("DAILY", mushroom=False)
    p.field(LEFT, 80, "Day", 40, 290)
    p.field(LEFT, 112, "Date", 45, 290)

    # Budget left: large Admin-blue box under the title, three currency budgets.
    bx, by, bw, bh = 330.0, 80.0, RIGHT - 330.0, 132.0
    p.rect(bx, by, bw, bh, fill=ADMIN)
    p.text(bx + 10, by + 6, bw - 20, 24, "Budget left", MONO, 16, color=CREAM)
    for i in range(3):
        p.rect(bx + 10, by + 36 + i * 31, bw - 20, 25, fill=CREAM, width=INNER)

    # Costs: description line + one box holding currency and cost.
    box_x, box_w, gap = 430.0, X1 - 430.0, 30.0
    y = 234.0
    p.text(X0, y, 200, 24, "Costs", MONO, 16)
    p.text(X0, y + 26, 200, 18, "Description of cost", SANS_BOLD, 10)
    p.text(box_x, y + 26, box_w, 18, "Currency + cost", SANS_BOLD, 10)
    rows = 12
    top = y + 52
    for i in range(rows):
        ry = top + i * gap
        p.line(X0, ry + 20, box_x - 12 - X0)
        p.rect(box_x, ry, box_w, 22, fill=LENS, width=INNER)

    # Transfers between currencies.
    ty = top + rows * gap + 14
    p.text(X0, ty, 200, 24, "Transfers", MONO, 16)
    p.text(X0, ty + 26, 100, 18, "From", SANS_BOLD, 10)
    p.text(X0 + 136, ty + 26, 100, 18, "To", SANS_BOLD, 10)
    p.text(X0 + 272, ty + 26, 100, 18, "Note", SANS_BOLD, 10)
    for i in range(4):
        ry = ty + 52 + i * gap
        if ry + 22 > BOTTOM:
            break
        p.rect(X0, ry, 110, 22, fill=LENS, width=INNER)
        p.text(X0 + 112, ry, 22, 22, "→", SANS_BOLD, 14, align=1)
        p.rect(X0 + 136, ry, 110, 22, fill=LENS, width=INNER)
        p.line(X0 + 272, ry + 20, X1 - X0 - 272)
    return p


if __name__ == "__main__":
    print(daily().write("finance/daily/daily-planner-claude.sla").relative_to(ROOT))
