#!/usr/bin/env python3
"""Draw the Home > Inventory page (Claude draft, labelled -claude).

Columns: Item · Replacement (cost, with £ / $ / € boxes) · Room.
Usage: python3 scripts/build-home-inventory.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh home/inventory/*-claude.sla
Rerunning overwrites the draft, so stop using this once the user starts editing it.
"""
from sla_build import INNER, LENS, ROOT, ROW, SANS_BOLD, TABLE_X, TABLE_Y, Page, table

CURRENCIES = ["£", "$", "€"]


def inventory():
    p = Page("INVENTORY")
    rows, repl, room = 20, 250, 440
    table(p, [(TABLE_X, "Item"), (repl, "Replacement"), (room, "Room")], rows)
    # Currency is part of the replacement cell: amount on the left, £ / $ / € boxes on the right.
    box, step = 11.5, 29.0
    x0 = room - 6 - step * len(CURRENCIES)
    for i in range(rows):
        y = TABLE_Y + i * ROW + (ROW - box) / 2
        for j, sym in enumerate(CURRENCIES):
            x = x0 + j * step
            p.rect(x, y, box, box, fill=LENS, width=INNER)
            p.text(x + box + 3, y - 4, 14, box + 8, sym, SANS_BOLD, 14)
    return p


if __name__ == "__main__":
    print(inventory().write("home/inventory/inventory-claude.sla").relative_to(ROOT))
