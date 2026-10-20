#!/usr/bin/env python3
"""Move one page out of a Scribus .sla file into a new single-page .sla file.

Usage: split-sla-page.py SOURCE PAGE_INDEX OUTPUT
PAGE_INDEX is 0-based. SOURCE is rewritten without that page.
"""
import copy
import sys
import xml.etree.ElementTree as ET

src, idx, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
tree = ET.parse(src)
doc = tree.getroot().find("DOCUMENT")
pages = doc.findall("PAGE")
step = float(pages[1].get("PAGEYPOS")) - float(pages[0].get("PAGEYPOS"))
top = pages[0].get("PAGEYPOS")


def shift(el, dy):
    """Move an object vertically; gYpos follows only when it mirrors YPOS."""
    y = float(el.get("YPOS"))
    if el.get("gYpos") is not None and abs(float(el.get("gYpos")) - y) < 1e-6:
        el.set("gYpos", repr(y + dy))
    el.set("YPOS", repr(y + dy))


def set_page_count(d, n):
    d.set("ANZPAGES", str(n))
    d.find("Sections").find("Section").set("To", str(n - 1))


# New single-page document: everything except the other pages and their objects.
new = copy.deepcopy(tree)
ndoc = new.getroot().find("DOCUMENT")
for p in ndoc.findall("PAGE"):
    if int(p.get("NUM")) != idx:
        ndoc.remove(p)
    else:
        p.set("NUM", "0")
        p.set("PAGEYPOS", top)
for o in ndoc.findall("PAGEOBJECT"):
    if int(o.get("OwnPage")) != idx:
        ndoc.remove(o)
    else:
        o.set("OwnPage", "0")
        shift(o, -step * idx)
set_page_count(ndoc, 1)
new.write(out, encoding="UTF-8", xml_declaration=True)

# Source document: drop the page and close the gap.
for p in doc.findall("PAGE"):
    n = int(p.get("NUM"))
    if n == idx:
        doc.remove(p)
    elif n > idx:
        p.set("NUM", str(n - 1))
        p.set("PAGEYPOS", repr(float(p.get("PAGEYPOS")) - step))
for o in doc.findall("PAGEOBJECT"):
    n = int(o.get("OwnPage"))
    if n == idx:
        doc.remove(o)
    elif n > idx:
        o.set("OwnPage", str(n - 1))
        shift(o, -step)
set_page_count(doc, len(pages) - 1)
tree.write(src, encoding="UTF-8", xml_declaration=True)
