#!/usr/bin/env python3
"""Draw the Home > Progress pages (Claude drafts, labelled -claude).

  rooms-progress  four rooms, each with a progress donut and 10 project lines
  project         one project per page: donut + started date, title, taped-notes area, tasks
                  with the Finance item # and month for each task's cost

Usage: python3 scripts/build-home-progress.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh home/progress/*-claude.sla
Rerunning overwrites the drafts, so stop using this once the user starts editing them.
"""
from sla_build import (BOTTOM, BROWN, CHECK, INNER, LEFT, LENS, MONO, RIGHT, ROOT,
                       SANS_BOLD, WRITE_GAP, Page)

ROOMS = ["Bedroom", "Office", "Living room", "Kitchen"]


def rooms_progress():
    p = Page("PROGRESS")
    top, gap, n = 190.0, 12.0, len(ROOMS)
    h = (BOTTOM - 12 - top - gap * (n - 1)) / n
    outer, inner = 46.0, 24.0
    for i, room in enumerate(ROOMS):
        y = top + i * (h + gap)
        p.rect(LEFT, y, RIGHT - LEFT, h)
        cx, cy = p.ring(LEFT + 12 + outer, y + h / 2, outer, inner)
        p.segments(cx, cy, outer, inner, 8)
        tx = LEFT + 24 + 2 * outer
        p.text(tx, y + 6, 250, 24, room, MONO, 16, color=BROWN)
        col_w = (RIGHT - 10 - tx) / 2
        for col in range(2):
            x0 = tx + col * col_w
            for r in range(5):
                ly = y + 36 + r * 21
                p.checkbox(x0, ly)
                p.line(x0 + CHECK + 5, ly + 13, col_w - CHECK - 15)
    return p


def project():
    p = Page("PROJECT", mushroom=False)
    outer, inner = 55.0, 30.0
    cx, cy = p.ring(LEFT + outer, 88 + outer, outer, inner)
    p.segments(cx, cy, outer, inner, 8)
    p.field(LEFT, 88 + 2 * outer + 18, "Started", 62, LEFT + 2 * outer + 6, 12)

    nx = LEFT + 2 * outer + 22
    p.field(nx, 88, "Project", 65, RIGHT)
    ny = 124.0
    notes_bottom = 420.0
    p.rect(nx, ny, RIGHT - nx, notes_bottom - ny)
    p.text(nx + 7, ny + 6, 200, 24, "Notes", MONO, 16, color=BROWN)
    p.rect(nx + 10, ny + 36, RIGHT - nx - 20, notes_bottom - ny - 46, fill=LENS, width=INNER)

    # Tasks, each with where its cost sits in Finance (item number + month).
    ty = notes_bottom + 16
    item_x, month_x, box_w = 410.0, 484.0, 66.0
    p.text(LEFT, ty, 200, 24, "Tasks", MONO, 16, color=BROWN)
    p.text(item_x, ty + 8, box_w, 16, "Item #", SANS_BOLD, 10)
    p.text(month_x, ty + 8, box_w, 16, "Month", SANS_BOLD, 10)
    y = ty + 32
    while y + 20 < BOTTOM:
        p.checkbox(LEFT, y + 2)
        p.line(LEFT + CHECK + 6, y + 16, item_x - 10 - (LEFT + CHECK + 6))
        p.rect(item_x, y, box_w, 18, fill=LENS, width=INNER)
        p.rect(month_x, y, RIGHT - month_x, 18, fill=LENS, width=INNER)
        y += WRITE_GAP + 1
    return p


if __name__ == "__main__":
    for name, build in [("rooms-progress", rooms_progress), ("project", project)]:
        print(build().write(f"home/progress/{name}-claude.sla").relative_to(ROOT))
