#!/usr/bin/env python3
"""Draw Home's Yearly tasks page (Claude draft).

Same layout as the user's finance/yearly-budget.sla (three cream columns with
checkbox lines), with Annual / Biannual / Quarterly *tasks*, and under each task a
When (month/date) and Length (estimated time) line.
Usage: python3 scripts/build-home-yearly.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh home/yearly-tasks-claude.sla
Rerunning overwrites the draft, so stop using this once the user starts editing it.
"""
from sla_build import BROWN, CHECK, LEFT, MAIN, MONO, ROOT, SANS_BOLD, Page

# Measured from finance/yearly-budget.sla
COL_W, COL_STEP, COL_Y, COL_H = 162.9, 174.85, 124.1, 675.9
FIRST_ROW, ROW_STEP = 191.0, 58.0  # taller rows: task line + When/Time line


def yearly_tasks():
    p = Page("YEARLY")
    p.field(LEFT, 80, "Year", 42, 248)
    for c, name in enumerate(["Annual", "Biannual", "Quarterly"]):
        x = LEFT + c * COL_STEP
        p.rect(x, COL_Y, COL_W, COL_H)
        p.text(x + 5, COL_Y + 7, COL_W - 10, 44, f"{name}\ntasks", MONO, 16, color=BROWN)
        lx, rx = x + 25, x + COL_W - 8
        y = FIRST_ROW
        while y + 40 < COL_Y + COL_H:
            p.checkbox(x + 7, y)
            p.line(lx, y + 15, rx - lx)
            # When / Length on the line below the task.
            sub = y + 22
            p.text(lx, sub, 30, 16, "When", SANS_BOLD, 9)
            p.line(lx + 27, sub + 13, 42)
            p.text(lx + 74, sub, 34, 16, "Length", SANS_BOLD, 9)
            p.line(lx + 106, sub + 13, rx - (lx + 106))
            y += ROW_STEP
    return p


if __name__ == "__main__":
    print(yearly_tasks().write("home/yearly-tasks-claude.sla").relative_to(ROOT))
