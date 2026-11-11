#!/usr/bin/env python3
"""Draw the Health > Diagnoses pages (Claude drafts, labelled -claude).

  summary        (and summary-blank) one table: diagnosis, date, treated by, page, and two stacked status
                 pairs (Active / Resolved, Managed / Unmanaged)
  <diagnosis>    (and diagnosis-blank) one page each: diagnosed date + by, symptoms, triggers,
                 medications (past / now / future, each with its Treatments page number),
                 care team, treatments, and an unlined notes area for taping notes
Usage: python3 scripts/build-health-diagnoses.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh health/diagnoses/*-claude.sla
Rerunning overwrites the drafts, so stop using this once the user starts editing them.
"""
from sla_build import (BOTTOM, BROWN, INNER, LEFT, LENS, MONO, RIGHT, ROOT, SANS, SANS_BOLD,
                       TABLE_X, TABLE_Y, Page, lined_box, medications, table)

# (file slug, name as printed)
DIAGNOSES = [
    ("gastroparesis", "Gastroparesis"), ("migraines", "Migraines"), ("me", "ME"),
    ("cptsd", "CPTSD"), ("adhd", "ADHD"), ("autism", "Autism"), ("pots", "POTS"),
    ("heds", "hEDS"), ("allergies", "Allergies"),
]
# Pages for the user's wife's copy of the binder: not on the user's summary.
WIFE = [("neuropathic-pain", "Neuropathic pain"), ("bipolar-ii", "Bipolar II"),
        ("hypermobility", "Hypermobility")]


def summary(names):
    p = Page("DIAGNOSES")
    rows, row_h, box, gap = 17, 34.0, 11.0, 4.0
    s1, s2 = 408.0, 470.0  # Unmanaged needs the wider last column
    table(p, [(TABLE_X, "Diagnosis"), (200, "Date"), (260, "Treated by"), (366, "Page"),
              (s1, None), (s2, None)], rows, row_h)
    pad = (row_h - 2 * box - gap) / 2
    for i in range(rows):
        top = TABLE_Y + i * row_h
        # Every row gets a text box (empty when blank) to type the diagnosis into.
        p.text(TABLE_X + 5, top + 7, 150, 20, names[i] if i < len(names) else "", SANS, 12)
        # Two unnamed status columns, each with a stacked pair of labelled boxes.
        for x0, labels in [(s1, ("Active", "Resolved")), (s2, ("Managed", "Unmanaged"))]:
            for j, label in enumerate(labels):
                y = top + pad + j * (box + gap)
                p.rect(x0 + 5, y, box, box, fill=LENS, width=INNER)
                p.text(x0 + 5 + box + 3, y - 1, 60, box + 2, label, SANS_BOLD, 9)
    return p


def detail(name):
    # Header title: the diagnosis name (blank template: an empty text box to type into).
    p = Page(name if name in ("", "hEDS") else name.upper())
    p.field(LEFT, 80, "Diagnosed", 80, 300)
    p.field(LEFT, 112, "By", 30, 300)
    top, gap, h = 190.0, 14.0, 120.0
    w = (RIGHT - LEFT - gap) / 2
    lined_box(p, LEFT, top, w, h, "Symptoms")
    lined_box(p, LEFT + w + gap, top, w, h, "Triggers")
    my = top + h + gap
    medications(p, my, 150.0)
    y = my + 150.0 + gap
    lined_box(p, LEFT, y, w, h, "Care team")
    lined_box(p, LEFT + w + gap, y, w, h, "Treatments")
    ny = y + h + gap
    p.rect(LEFT, ny, RIGHT - LEFT, BOTTOM - ny)
    p.text(LEFT + 7, ny + 6, 200, 24, "Notes", MONO, 16, color=BROWN)
    p.rect(LEFT + 10, ny + 36, RIGHT - LEFT - 20, BOTTOM - ny - 46, fill=LENS, width=INNER)
    return p


if __name__ == "__main__":
    print(summary([n for _, n in DIAGNOSES]).write("health/diagnoses/summary-claude.sla").relative_to(ROOT))
    print(summary([]).write("health/diagnoses/summary-blank-claude.sla").relative_to(ROOT))
    print(detail("").write("health/diagnoses/diagnosis-blank-claude.sla").relative_to(ROOT))
    for slug, name in DIAGNOSES + WIFE:
        print(detail(name).write(f"health/diagnoses/{slug}-claude.sla").relative_to(ROOT))
