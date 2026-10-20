#!/usr/bin/env python3
"""Draw the Home > Weekly page (Claude draft, labelled -claude). Laminated, reused weekly.

Areas: Cleaning, Admin, Exercise, Community. Each task has one tick box per time
it's due in the week.
Usage: python3 scripts/build-home-weekly.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh home/weekly/*-claude.sla
Rerunning overwrites the draft, so stop using this once the user starts editing it.
"""
from sla_build import (BROWN, CHECK, INNER, LEFT, LENS, MAIN, MONO, RIGHT, ROOT, SANS,
                       SANS_BOLD, Page)

ROW_H = 26.0
BOX_X, BOX_STEP = 330.0, 22.0
CONTACTS = ["Vanu", "Alyx", "Louise", "Zoe"]

# (area, [(task, times per week)]); special rows are drawn by name below.
AREAS = [
    ("Cleaning", [("Wash dishes", 3), ("Laundry", 1), ("Bins / recycling", 1),
                  ("Wipe kitchen surfaces", 1)]),
    ("Admin", [("Weekly finance summary", 1), ("Paperwork / post", 1), ("Work admin", 1),
               ("Appointments", 1)]),
    ("Exercise", [("STEPS_GOAL", 0), ("STEPS_AVERAGE", 0)]),
    ("Community", [("Leave the house", 2), ("CONTACTS", 0), ("Contact Gwen", 3),
                   ("Monday: Meetup, free events", 1)]),
]


def weekly():
    p = Page("WEEKLY")
    p.field(LEFT, 80, "Week of", 70, 300)
    y = 190.0  # below the mushroom patch, as on the other pages
    for area, rows in AREAS:
        h = 34 + len(rows) * ROW_H + 8
        p.rect(LEFT, y, RIGHT - LEFT, h)
        p.text(LEFT + 7, y + 6, 250, 24, area, MONO, 16, color=BROWN)
        for i, (task, times) in enumerate(rows):
            ry = y + 34 + i * ROW_H
            tx = LEFT + 12
            if task == "STEPS_GOAL":
                p.text(tx, ry + 1, 60, 20, "Average", SANS, 12)
                p.line(tx + 50, ry + 18, 44, MAIN, BROWN)
                p.text(tx + 98, ry + 1, 150, 20, "k steps a day", SANS, 12)
            elif task == "STEPS_AVERAGE":
                p.text(tx, ry + 1, 260, 20, "Sunday: this week's average", SANS, 12)
                p.rect(BOX_X, ry + 2, 90, 18, fill=LENS, width=INNER)
                p.text(BOX_X + 94, ry + 1, 20, 20, "k", SANS, 12)
            elif task == "CONTACTS":
                p.text(tx, ry + 1, 70, 20, "Contact", SANS, 12)
                x = tx + 58
                for name in CONTACTS:
                    p.checkbox(x, ry + 4)
                    p.text(x + CHECK + 4, ry + 1, 60, 20, name, SANS, 12)
                    x += CHECK + 14 + 7 * len(name) + 8
            else:
                p.text(tx, ry + 1, BOX_X - tx - 10, 20, task, SANS, 12)
                for j in range(times):
                    p.checkbox(BOX_X + j * BOX_STEP, ry + 4)
        y += h + 14
    return p


if __name__ == "__main__":
    print(weekly().write("home/weekly/weekly-claude.sla").relative_to(ROOT))
