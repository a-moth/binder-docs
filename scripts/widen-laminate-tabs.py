#!/usr/bin/env python3
"""One-off edit (the user's request): double the width of every laminate tab in
core/core-layouts.sla. Each tab grows by half its width on both sides, with no lines in
the new parts, so the tab ends can be taped. The fold line and name stay in the middle.

Doubled tabs fit 3 columns per A4 sheet (it was 5), so page 11 keeps Finance, Home and
Health and a new page 12 takes Work, Learning + Resources and Archive + Travel. Adds the
tabs that weren't on the sheet: Work > Cognitive load and Disability effects, and Travel's
four (they replace the old separate Travel strip). Each column keeps the user's tab order.
Usage: python3 scripts/widen-laminate-tabs.py   (refuses to run twice)
"""
import itertools
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SLA = ROOT / "core/core-layouts.sla"
PAGE = 10                      # page 11, the laminate sheet
OLD_W = 77.30                  # measured tab width
NEW_W = 2 * OLD_W
PITCH = 80.5                   # tab to tab, as on the sheet
TOP, SECTION_GAP = 50.0, 16.0
COLUMNS_X = [42.0, 220.2, 398.4]
# New page layout: page index -> columns -> sections (each a list of tab names, top to bottom).
NEW_TABS = {"WORK": ["COGNITIVE\nLOAD", "DISABILITY\nEFFECTS"]}
TRAVEL = ["TRAVEL", "DOCUMENTS", "PAPERWORK", "PLANNING"]
_ids = itertools.count(2_120_000_000, 7919)


def attr(tag, k):
    m = re.search(rf'(?:^|\s){k}="([^"]*)"', tag)
    return float(m[1]) if m else 0.0


def set_attr(tag, k, v):
    return re.sub(rf'((?:^|\s){k}=")[^"]*(")', rf"\g<1>{v!r}\2", tag, count=1)


def main():
    text = SLA.read_text(encoding="utf-8")
    if 'ANZPAGES="12"' in text:
        raise SystemExit("already done (the document has 12 pages)")
    pages = re.findall(r"<PAGE [^>]*>", text)
    px, py = attr(pages[PAGE], "PAGEXPOS"), attr(pages[PAGE], "PAGEYPOS")
    page_step = py - attr(pages[PAGE - 1], "PAGEYPOS")

    objs = list(re.finditer(r'<PAGEOBJECT\b[^>]*?(?:/>|>.*?</PAGEOBJECT>)', text, re.S))
    on_page = [m for m in objs if f'OwnPage="{PAGE}"' in m[0][:400]]
    rects = [m for m in on_page if 'PTYPE="6"' in m[0][:400] and abs(attr(m[0], "WIDTH") - OLD_W) < 1]
    lines = [m for m in on_page if 'PTYPE="5"' in m[0][:400]]
    texts = [m for m in on_page if 'PTYPE="4"' in m[0][:400] and 'ROT="270"' in m[0][:600]]

    def inside(m, r, xoff):
        x, y = attr(m[0], "XPOS"), attr(m[0], "YPOS")
        rx, ry = attr(r[0], "XPOS"), attr(r[0], "YPOS")
        return rx < x + xoff < rx + OLD_W and ry < y <= ry + 84

    # Names repeat (MONTHLY, TEMPLATES, …), so a tab is (name, its objects).
    tabs = []
    for t in texts:
        r = next(r for r in rects if inside(t, r, 0))
        ln = next(ln for ln in lines if inside(ln, r, 0))
        tabs.append((re.search(r'CH="([^"]+)"', t[0])[1], (r, ln, t)))
    # Columns as on the sheet: tabs grouped by x, top to bottom, split where a gap opens.
    by_x = {}
    for tab in tabs:
        r = tab[1][0][0]
        by_x.setdefault(round(attr(r, "XPOS")), []).append((attr(r, "YPOS"), tab))
    sections = []
    for col in by_x.values():
        col.sort(key=lambda e: e[0])
        run = [col[0]]
        for prev, cur in zip(col, col[1:]):
            if cur[0] - prev[0] > PITCH + 5:
                sections.append([tab for _, tab in run])
                run = []
            run.append(cur)
        sections.append([tab for _, tab in run])
    find = lambda name: next(s for s in sections if name in [n for n, _ in s])  # noqa: E731
    work = find("WORK") + [(n, None) for n in NEW_TABS["WORK"]]
    travel = [(n, None) for n in TRAVEL]
    layout = {PAGE: [[find("FINANCE")], [find("HOME")], [find("HEALTH")]],
              PAGE + 1: [[work], [find("LEARNING"), find("RESOURCES")], [find("ARCHIVE"), travel]]}

    template = next(t for n, t in find("WORK") if n == "PLANNING")  # copied for new tabs
    removed = {(m.start(), m.end()) for _, t in tabs for m in t}
    new_objs = []
    for page, columns in layout.items():
        ppy = py + (page - PAGE) * page_step
        for cx, col in zip(COLUMNS_X, columns):
            y = TOP
            for s, section in enumerate(col):
                if s:
                    y += SECTION_GAP
                for name, triple in section:
                    new_objs += place(triple, template, name, px + cx, ppy + y, page)
                    y += PITCH

    out, last = [], 0
    for m in objs:
        if (m.start(), m.end()) in removed:
            out.append(text[last:m.start()])
            last = m.end()
    out.append(text[last:])
    text = "".join(out)
    cut = text.rindex("</DOCUMENT>")
    text = text[:cut] + "\n".join("        " + o for o in new_objs) + "\n    " + text[cut:]
    # The new page 12, and the page count / section range.
    new_page = set_attr(pages[PAGE].replace(f'NUM="{PAGE}"', f'NUM="{PAGE + 1}"'),
                        "PAGEYPOS", py + page_step)
    text = text.replace(pages[PAGE], pages[PAGE] + "\n    " + new_page, 1)
    text = text.replace('ANZPAGES="11"', 'ANZPAGES="12"', 1)
    text = re.sub(r'(<Section Number="0"[^>]*To=")10"', r'\g<1>11"', text, count=1)
    SLA.write_text(text, encoding="utf-8")
    print(f"{len(new_objs) // 3} tabs over pages {PAGE + 1}-{PAGE + 2}")


def place(triple, template, name, x, y, page):
    """The tab's rect (doubled) and its fold line and name, moved with the tab's middle."""
    new = triple is None
    r, ln, t = [m[0] for m in (triple or template)]
    dx = x - attr(r, "XPOS") + OLD_W / 2
    dy = y - attr(r, "YPOS")
    h = attr(r, "HEIGHT")
    path = f"M0 0 L{NEW_W:g} 0 L{NEW_W:g} {h:g} L0 {h:g} L0 0 Z"
    r = set_attr(set_attr(set_attr(r, "XPOS", x), "YPOS", y), "WIDTH", NEW_W)
    r = set_attr(set_attr(r, "gXpos", x), "gYpos", y)
    r = re.sub(r'(?<=\s)path="[^"]*"', f'path="{path}"', r, count=1)
    r = re.sub(r'(?<=\s)copath="[^"]*"', f'copath="{path}"', r, count=1)
    moved = [r]
    for o in (ln, t):
        for k, d in (("XPOS", dx), ("YPOS", dy), ("gXpos", dx), ("gYpos", dy)):
            o = set_attr(o, k, attr(o, k) + d)
        moved.append(o)
    if new:
        t = moved[2]
        style = re.search(r'<ITEXT ([^>]*?)CH="[^"]*"', t)[1]
        if max(map(len, name.split("\n"))) > 8 and "FONTSIZE" not in style:
            style += 'FONTSIZE="11" '  # as the user's longer names (DIAGNOSES, TREATMENT)
        runs = '<para ALIGN="1"/>'.join(f'<ITEXT {style}CH="{part}"/>' for part in name.split("\n"))
        t = re.sub(r'<ITEXT [^>]*/>', runs, t, count=1)
        if "\n" in name:  # two lines: taller frame, still starting at the fold line
            w, fh = attr(t, "WIDTH"), 2 * attr(t, "HEIGHT") - 2
            t = set_attr(t, "HEIGHT", fh)
            box = f"M0 0 L{w:g} 0 L{w:g} {fh:g} L0 {fh:g} L0 0 Z"  # Scribus lays text out in this
            t = re.sub(r'(?<=\s)path="[^"]*"', f'path="{box}"', t, count=1)
            t = re.sub(r'(?<=\s)copath="[^"]*"', f'copath="{box}"', t, count=1)
        moved[2] = t
        moved = [re.sub(r'ItemID="\d+"', f'ItemID="{next(_ids)}"', o, count=1) for o in moved]
    return [re.sub(r'OwnPage="\d+"', f'OwnPage="{page}"', o, count=1) for o in moved]


if __name__ == "__main__":
    main()
