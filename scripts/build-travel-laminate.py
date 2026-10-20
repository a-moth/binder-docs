#!/usr/bin/env python3
"""Draw the Travel laminate tab strip (Claude draft, labelled -claude).

Copies one strip of the user's laminate sheet (core/core-layouts.sla, page 11, the
Health strip) object by object: cream squares, fold lines and rotated Comic Relief
labels. Only the first four squares are kept and the labels are swapped for Travel's.
The laminate sheet is full (five strips), so Travel gets its own sheet.
Usage: python3 scripts/build-travel-laminate.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh core/travel-laminate-claude.sla
"""
import copy
import itertools
import xml.etree.ElementTree as ET

from sla_build import PAGE_X, PAGE_Y, ROOT, Page

SRC_PAGE = "10"            # laminate sheet in core-layouts.sla
STRIP_X = (190.0, 280.0)   # page-relative x range of the Health strip
LABELS = {"LETTERS": ("TRAVEL", None), "DIAGNOSES": ("DOCUMENTS", "11"),
          "HEALTH": ("PAPERWORK", "11"), "TREATMENT": ("PLANNING", "11")}
KEEP_SQUARES = 4
_ids = itertools.count(1_930_000_000, 7919)


def strip_objects():
    doc = ET.parse(ROOT / "core/core-layouts.sla").getroot().find("DOCUMENT")
    page = next(p for p in doc.findall("PAGE") if p.get("NUM") == SRC_PAGE)
    px, py = float(page.get("PAGEXPOS")), float(page.get("PAGEYPOS"))
    objs = [o for o in doc.findall("PAGEOBJECT") if o.get("OwnPage") == SRC_PAGE
            and STRIP_X[0] <= float(o.get("XPOS")) - px <= STRIP_X[1]]
    squares = sorted(float(o.get("YPOS")) for o in objs if o.get("PTYPE") == "6")
    bottom = squares[KEEP_SQUARES - 1] + 80.0  # end of the last square kept
    out = []
    for o in objs:
        if float(o.get("YPOS")) > bottom:
            continue
        o = copy.deepcopy(o)
        text = "".join(i.get("CH", "") for i in o.iter("ITEXT"))
        if o.get("PTYPE") == "4":
            if text not in LABELS:
                continue
            new, size = LABELS[text]
            for i in o.iter("ITEXT"):
                i.set("CH", new)
                if size:
                    i.set("FONTSIZE", size)
        # Move from the source page onto page 0 of the new document.
        for k, base, new_base in [("XPOS", px, PAGE_X), ("YPOS", py, PAGE_Y),
                                  ("gXpos", px, PAGE_X), ("gYpos", py, PAGE_Y)]:
            if o.get(k) is not None:
                o.set(k, repr(float(o.get(k)) - base + new_base))
        o.set("OwnPage", "0")
        o.set("ItemID", str(next(_ids)))
        out.append(ET.tostring(o, encoding="unicode").strip())
    return out


if __name__ == "__main__":
    p = Page("", header=False, mushroom=False)
    p.objects.extend(strip_objects())
    print(p.write("core/travel-laminate-claude.sla").relative_to(ROOT))
