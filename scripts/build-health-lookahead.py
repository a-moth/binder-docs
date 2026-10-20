#!/usr/bin/env python3
"""Draw the Health > Look ahead pages (Claude drafts, labelled -claude).

  appointments  two per page: date, time, who, where, a taped-notes area, outcome box
  goals         two per page (typed in, printed, laminated): goal text box, progress
                donut (one slot per step) and step lines to fill in and redo
Usage: python3 scripts/build-health-lookahead.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh health/look-ahead/*-claude.sla
Rerunning overwrites the drafts, so stop using this once the user starts editing them.
"""
from sla_build import (BOTTOM, BROWN, CHECK, INNER, LEFT, LENS, MONO, RIGHT, ROOT, SANS,
                       WRITE_GAP, Page)

TOP, GAP = 190.0, 14.0
BLOCK_H = (BOTTOM - TOP - GAP) / 2


def appointment(p, y, h):
    p.rect(LEFT, y, RIGHT - LEFT, h)
    mid = (LEFT + RIGHT) / 2
    p.field(LEFT + 8, y + 8, "Date", 42, mid - 12)
    p.field(mid + 4, y + 8, "Time", 42, RIGHT - 10)
    p.field(LEFT + 8, y + 36, "Who", 38, mid - 12)
    p.field(mid + 4, y + 36, "Where", 52, RIGHT - 10)
    ny = y + 70
    p.text(LEFT + 8, ny, 200, 24, "Notes", MONO, 16, color=BROWN)
    oy = y + h - 82  # Outcome: title + two lines at the bottom of the block
    notes_h = oy - 10 - (ny + 26)  # taped-notes area takes the rest
    p.rect(LEFT + 10, ny + 26, RIGHT - LEFT - 20, notes_h, fill=LENS, width=INNER)
    p.text(LEFT + 8, oy, 200, 24, "Outcome", MONO, 16, color=BROWN)
    ly = oy + 46
    while ly < y + h - 6:
        p.line(LEFT + 10, ly, RIGHT - LEFT - 20)
        ly += WRITE_GAP


STEPS = 10  # step lines per goal = donut slots


def goal(p, y, h):
    p.rect(LEFT, y, RIGHT - LEFT, h)
    outer, inner = 50.0, 27.0
    cx, cy = p.ring(LEFT + 12 + outer, y + 12 + outer, outer, inner)
    p.segments(cx, cy, outer, inner, STEPS)  # one slot per step line
    gx = LEFT + 30 + 2 * outer
    p.text(gx, y + 8, 200, 24, "Goal", MONO, 16, color=BROWN)
    box_y, box_h = y + 36, 2 * outer - 24
    p.rect(gx, box_y, RIGHT - 10 - gx, box_h, fill=LENS, width=INNER)
    # Empty text box to type the goal into before printing.
    p.text(gx + 6, box_y + 6, RIGHT - 22 - gx, box_h - 12, "", SANS, 12)
    sy = y + 24 + 2 * outer
    p.text(LEFT + 8, sy, 200, 24, "Steps", MONO, 16, color=BROWN)
    col_w = (RIGHT - LEFT - 30) / 2
    for i in range(STEPS):
        col, row = divmod(i, STEPS // 2)
        x = LEFT + 10 + col * (col_w + 10)
        ly = sy + 32 + row * (WRITE_GAP + 2)
        p.checkbox(x, ly)
        p.line(x + CHECK + 5, ly + 13, col_w - CHECK - 5)


def pages():
    # Appointments start right under the header (no mushroom) to give the notes room.
    a = Page("APPOINTMENTS", mushroom=False)
    g = Page("GOALS")
    a_top = 88.0
    a_h = (BOTTOM - a_top - GAP) / 2
    for i in range(2):
        appointment(a, a_top + i * (a_h + GAP), a_h)
        goal(g, TOP + i * (BLOCK_H + GAP), BLOCK_H)
    return a, g


if __name__ == "__main__":
    a, g = pages()
    print(a.write("health/look-ahead/appointments-claude.sla").relative_to(ROOT))
    print(g.write("health/look-ahead/goals-claude.sla").relative_to(ROOT))
