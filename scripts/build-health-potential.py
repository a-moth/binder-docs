#!/usr/bin/env python3
"""Draw the Health > Potential pages (Claude drafts, labelled -claude).

  <name>          potential diagnosis: name, typical occurrences, medications
                  (past / now / future + Treatments page + Effect line), events reference
                  (date + event log page)
  <name>-events   three events per page: date, a taped-notes box (what happened), a
                  trigger box, a 1-10 severity scale to circle and a 15 min - 10 day
                  duration scale to mark
Usage: python3 scripts/build-health-potential.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh health/potential/*-claude.sla
Rerunning overwrites the drafts, so stop using this once the user starts editing them.
"""
from sla_build import (BOTTOM, BROWN, INNER, LEFT, LENS, MAIN, MONO, RIGHT, ROOT, SANS_BOLD,
                       WRITE_GAP, Page, lined_box, medications)

POTENTIAL = [("mcas", "MCAS"), ("cci", "CCI"), ("neuropathy", "NEUROPATHY")]
DURATIONS = ["15m", "30m", "1h", "2h", "4h", "8h", "12h", "1d", "2d", "3d", "5d", "7d", "10d"]
EVENTS, TOP, GAP = 3, 88.0, 14.0


def scale(p, y, label, marks, size):
    """A brown scale line with a tick and a centred label at each mark."""
    x0, x1 = LEFT + 92, RIGHT - 18
    p.text(LEFT + 8, y - 8, 84, 20, label, SANS_BOLD, 12)
    p.line(x0, y, x1 - x0, INNER, BROWN)
    step = (x1 - x0) / (len(marks) - 1)
    for i, m in enumerate(marks):
        x = x0 + i * step
        p.line(x, y - 4, 8, INNER, BROWN, rot=90)
        w = 30.0
        # Mono centres correctly in this Scribus (Sans Bold doesn't).
        p.text(x - w / 2, y - 6 - size - 6, w, size + 6, m, MONO, size, align=1)


def event(p, y, h):
    p.rect(LEFT, y, RIGHT - LEFT, h)
    p.field(LEFT + 8, y + 8, "Date", 42, 300)
    gap = 12.0
    nw = (RIGHT - LEFT - 20 - gap) * 0.58
    tx = LEFT + 10 + nw + gap
    by, bh = y + 62, h - 62 - 74
    p.text(LEFT + 10, by - 26, 200, 24, "Notes", MONO, 16, color=BROWN)
    p.rect(LEFT + 10, by, nw, bh, fill=LENS, width=INNER)
    p.text(tx, by - 26, 200, 24, "Trigger", MONO, 16, color=BROWN)
    p.rect(tx, by, RIGHT - 10 - tx, bh, fill=LENS, width=INNER)
    ly = by + 22
    while ly < by + bh - 4:
        p.line(tx + 6, ly, RIGHT - 16 - tx - 6)
        ly += WRITE_GAP - 3
    scale(p, y + h - 44, "Severity", [str(n) for n in range(1, 11)], 12)
    scale(p, y + h - 12, "How long", DURATIONS, 9)


def events_page(title):
    p = Page(title, mushroom=False)
    h = (BOTTOM - TOP - GAP * (EVENTS - 1)) / EVENTS
    for i in range(EVENTS):
        event(p, TOP + i * (h + GAP), h)
    return p


def potential(name):
    p = Page(name)
    top, gap = 190.0, 14.0
    occ_h, med_h = 120.0, 222.0
    lined_box(p, LEFT, top, RIGHT - LEFT, occ_h, "Typical occurrences")
    my = top + occ_h + gap
    medications(p, my, med_h, effect=True)  # Effect line under each medication
    ey = my + med_h + gap
    # Events reference: date + the event log page it's on.
    p.rect(LEFT, ey, RIGHT - LEFT, BOTTOM - ey)
    p.text(LEFT + 7, ey + 6, 250, 24, "Events reference", MONO, 16, color=BROWN)
    col_gap = 12.0
    col_w = (RIGHT - LEFT - 14 - 2 * col_gap) / 3
    sq_w, sq_h = 22.0, 16.0
    for c in range(3):
        x = LEFT + 7 + c * (col_w + col_gap)
        p.text(x, ey + 32, 60, 18, "Date", SANS_BOLD, 10)
        p.text(x + col_w - sq_w - 4, ey + 32, 40, 18, "Page", SANS_BOLD, 10)
        ly = ey + 70
        while ly < BOTTOM - 6:
            p.line(x, ly, col_w - sq_w - 6)
            p.rect(x + col_w - sq_w, ly - sq_h + 1, sq_w, sq_h, fill=LENS, width=INNER)
            ly += WRITE_GAP
    return p


if __name__ == "__main__":
    for slug, name in POTENTIAL:
        print(potential(name).write(f"health/potential/{slug}-claude.sla").relative_to(ROOT))
    print(potential("").write("health/potential/potential-blank-claude.sla").relative_to(ROOT))
    for slug, name in POTENTIAL:
        print(events_page(f"{name} EVENTS").write(f"health/potential/{slug}-events-claude.sla").relative_to(ROOT))
    print(events_page("").write("health/potential/events-blank-claude.sla").relative_to(ROOT))
