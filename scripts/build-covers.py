#!/usr/bin/env python3
"""Draw a cover (mini divider) for every sub-tab (Claude drafts, labelled -claude).

Same layout as the user's section dividers in core/core-layouts.sla: a cream box with
the name in Mono 16 and an icon, and the mushroom patch below-left. Printed on the
section's cardstock. Icons are cream outline (4.9:1 on the cream box).
Usage: python3 scripts/build-covers.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh <section>/<tab>/cover-claude.sla
Rerunning overwrites the drafts, so stop using this once the user starts editing them.
"""
from sla_build import BROWN, MONO, ROOT, Page

# Measured from the Finance divider (core-layouts.sla page 4).
BOX = (42.0, 105.2, 512.6, 115.3)
TITLE = (47.0, 112.0, 501.5, 34.5)
ICON_Y, ICON = 149.5, 28.3
MUSHROOM = (3.6, 176.0, 86.1, 83.0)

# section -> [(folder, name on the cover, Lucide icon in that section's assets)]
TABS = {
    "finance": [("tracked", "Tracked", "piggy-bank"), ("monthly", "Monthly", "calendar"),
                ("digitise", "Digitise", "scan-line"), ("weekly", "Weekly", "calendar-range"),
                ("daily", "Daily", "wallet")],
    "home": [("progress", "Progress", "trending-up"), ("strategy", "Strategy", "target"),
             ("monthly", "Monthly", "calendar"), ("weekly", "Weekly", "calendar-range"),
             ("inventory", "Inventory", "package")],
    "health": [("letters", "Letters", "mail"), ("diagnoses", "Diagnoses", "clipboard-list"),
               ("treatment", "Treatment", "pill-bottle"), ("look-ahead", "Look ahead", "telescope"),
               ("potential", "Potential", "search")],
    "work": [("clients", "Clients", "users"), ("projects", "Projects", "folder-kanban"),
             ("planning", "Planning", "calendar-days"), ("templates", "Templates", "layout-template"),
             ("archived", "Archived", "archive")],
    "learning": [("interest", "Interest", "lightbulb"), ("explore", "Explore", "compass")],
    "resources": [("templates", "Templates", "layout-template")],
    "archive": [("2025", "2025", "calendar"), ("2026", "2026", "calendar"),
                ("2027", "2027", "calendar"), ("digitised", "Digitised", "scan-line")],
    "travel": [("documents", "Documents", "id-card"), ("paperwork", "Paperwork", "file-text"),
               ("planning", "Planning", "map-pinned")],
}


def cover(section, name, icon):
    p = Page("", header=False)
    p.rect(*BOX)
    p.text(*TITLE, name.upper(), MONO, 16, color=BROWN, align=1)
    x = BOX[0] + BOX[2] / 2 - ICON / 2
    p.image(x, ICON_Y, ICON, ICON, f"{section}/{icon}-cream-outline.png")
    p.image(*MUSHROOM, "custom/mushroomvarious.png")
    return p


if __name__ == "__main__":
    n = 0
    for section, tabs in TABS.items():
        for folder, name, icon in tabs:
            cover(section, name, icon).write(f"{section}/{folder}/cover-claude.sla")
            n += 1
    print(n, "covers")
