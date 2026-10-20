#!/usr/bin/env python3
"""Draw the Home > Inventory page (Claude draft, labelled -claude).

Columns: Item · Replacement (cost to replace) · Currency · Room.
Usage: python3 scripts/build-home-inventory.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh home/inventory/*-claude.sla
Rerunning overwrites the draft, so stop using this once the user starts editing it.
"""
from sla_build import ROOT, TABLE_X, Page, table


def inventory():
    p = Page("INVENTORY")
    table(p, [(TABLE_X, "Item"), (270, "Replacement"), (370, "Currency"), (440, "Room")], 20)
    return p


if __name__ == "__main__":
    print(inventory().write("home/inventory/inventory-claude.sla").relative_to(ROOT))
