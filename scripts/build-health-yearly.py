#!/usr/bin/env python3
"""Draw Health's Yearly check-ups page (Claude draft, labelled -claude).

Finance Yearly layout: Annual / Biannual / Quarterly check-up columns. Under each
check-up: When + Booked box, then Clinic.
Usage: python3 scripts/build-health-yearly.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh health/yearly-checkups-claude.sla
Rerunning overwrites the draft, so stop using this once the user starts editing it.
"""
from sla_build import BROWN, CHECK, INNER, LEFT, LENS, MONO, ROOT, SANS, SANS_BOLD, Page

# Measured from finance/yearly-budget.sla
COL_W, COL_STEP, COL_Y, COL_H = 162.9, 174.85, 124.1, 675.9
FIRST_ROW, ROW_STEP = 191.0, 74.0  # check-up line + When/Booked + Clinic

COLUMNS = [
    ("Annual", ["Eye test", "General blood panel", "Testosterone levels", "Medication review"]),
    ("Biannual", ["Dentist"]),
    ("Quarterly", []),
]


def yearly_checkups():
    p = Page("YEARLY")
    p.field(LEFT, 80, "Year", 42, 248)
    for c, (name, prefill) in enumerate(COLUMNS):
        x = LEFT + c * COL_STEP
        p.rect(x, COL_Y, COL_W, COL_H)
        p.text(x + 5, COL_Y + 7, COL_W - 10, 44, f"{name}\ncheck-ups", MONO, 16, color=BROWN)
        lx, rx = x + 25, x + COL_W - 8
        y, i = FIRST_ROW, 0
        while y + 58 < COL_Y + COL_H:
            p.checkbox(x + 7, y)
            if i < len(prefill):
                p.text(lx, y - 3, rx - lx, 20, prefill[i], SANS, 12)
            p.line(lx, y + 15, rx - lx)
            sub = y + 22
            p.text(lx, sub, 30, 16, "When", SANS_BOLD, 9)
            p.line(lx + 27, sub + 13, 50)
            p.text(lx + 84, sub, 36, 16, "Booked", SANS_BOLD, 9)
            p.rect(rx - 11, sub + 3, 11, 11, fill=LENS, width=INNER)
            sub += 22
            p.text(lx, sub, 30, 16, "Clinic", SANS_BOLD, 9)
            p.line(lx + 30, sub + 13, rx - (lx + 30))
            y += ROW_STEP
            i += 1
    return p


if __name__ == "__main__":
    print(yearly_checkups().write("health/yearly-checkups-claude.sla").relative_to(ROOT))
