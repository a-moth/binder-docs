#!/usr/bin/env python3
"""Draw the Finance > Digitise log (Claude draft, labelled -claude).

Usage: python3 scripts/build-finance-digitise.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh finance/digitise/*-claude.sla
Rerunning overwrites the draft, so stop using this once the user starts editing it.
"""
from sla_build import HEAD_Y, LEFT, ROOT, ROW, TABLE_W, TABLE_X, TABLE_Y, Page, centre_checks, table


def digitised_log():
    p = Page("DIGITISE")
    p.field(LEFT, 80, "Month", 55, 300)
    scanned, archived, end = 394, 474, TABLE_X + TABLE_W
    rows = 20
    table(p, [(TABLE_X, "Date"), (100, "What it is"), (230, "Amount"), (310, "Saved to"),
              (scanned, "Scanned"), (archived, "Archived")], rows)
    centre_checks(p, scanned, archived, TABLE_Y, rows)
    centre_checks(p, archived, end, TABLE_Y, rows)
    return p


if __name__ == "__main__":
    print(digitised_log().write("finance/digitise/digitised-log-claude.sla").relative_to(ROOT))
