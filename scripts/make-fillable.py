#!/usr/bin/env python3
"""Make a fillable twin of a binder .sla: the same pages plus PDF form fields.

Usage: python3 scripts/make-fillable.py FILE.sla ...   (no args: every eligible .sla)
Writes FILE-fillable-claude.sla (foo-claude.sla -> foo-fillable-claude.sla) next to FILE.
The original is never changed. Export both with scripts/export-pdf.sh.
A source that already holds the user's own form fields gets the opposite twin:
FILE-plain-claude.sla, the same page with its fields turned back into plain frames.

Fields are found from the page geometry, so they follow the drawing:
  check boxes      lens squares 8-14 pt              -> check box field on top
  write-on lines   horizontal lines (black 1 pt, or brown 2.83 pt label rules) -> text field
                   just above the line, trimmed clear of labels and boxes beside it
  small boxes      inner-outline boxes 14-40 pt tall (page squares, amounts, budgets)
                   -> text field inside (beside any label in the box)
  table cells      cells of a cream table panel with a brown grid -> text field per cell
                   (left of any check boxes in the cell; skipped if pre-filled)
  empty text boxes empty text frames (blank-template titles, goal box) -> text field
Currency (the user's choice: a fixed list of CURRENCIES, only where the page already
has a currency): cells under a "Currency" table heading become drop-downs, and on the
CURRENCY_BOXES pages each small box gets a drop-down in front of its amount.
Large unlined boxes (taping areas, photo squares) and donuts get no field.
"""
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sla_build import ROOT, form_field  # noqa: E402

LENS = "Autumn camera lens highlight"
CREAM = "Autumn cream base"
BROWN = "Autumn brown dark"
CURRENCIES = ("£", "$", "€")
CURRENCY_BOXES = {"finance/daily/daily-planner-claude.sla"}  # budget, cost and transfer boxes
COMBO_W = 30.0
# Writing areas with nothing drawn to detect: (page index, x0, y0, x1, y1), page-relative.
EXTRA = {"core/core-layouts.sla": [(1, 46, 98, 548, 168)]}  # "State the goal of this section"
SKIP = re.compile(r"(^|/)cover-claude\.sla$|travel-(divider|laminate)-claude\.sla$"
                  r"|-(fillable|plain)(-claude)?\.sla$"
                  # the user's own fillable twins exist for these
                  r"|^home/strategy/cleaning/cleaning-docs-templates\.sla$"
                  r"|^work/templates/ask-herby-business-templates-brand\.sla$"
                  # read-only guides, workshop cards and boards: nothing to type into
                  r"|^work/(disability-effects|cognitive-load)/")


def twin_name(rel):
    p = pathlib.PurePath(rel)
    stem = p.stem.removesuffix("-claude")
    return str(p.with_name(f"{stem}-fillable-claude.sla"))


class Obj:
    def __init__(self, attrs, body):
        g = lambda k, d="": (re.search(rf'(?:^|\s){k}="([^"]*)"', attrs) or [None, d])[1]
        self.ptype = int(g("PTYPE"))
        self.page = int(g("OwnPage", "0"))
        self.x, self.y = float(g("XPOS")), float(g("YPOS"))
        self.w, self.h = float(g("WIDTH")), float(g("HEIGHT"))
        self.rot = round(float(g("ROT", "0"))) % 360  # hand-drawn lines can be 270.0076
        self.pw = float(g("PWIDTH", "1") or 1)
        self.fill, self.stroke = g("PCOLOR"), g("PCOLOR2")
        self.frtype = g("FRTYPE", "0")
        self.annot = 'ANNOTATION="1"' in attrs
        self.text = "".join(re.findall(r'CH="([^"]*)"', body or "")).strip()

    # boxes as (x0, y0, x1, y1) on the canvas
    @property
    def box(self):
        return self.x, self.y, self.x + self.w, self.y + self.h


def overlap(a, b, pad=0.0):
    return a[0] < b[2] - pad and b[0] < a[2] - pad and a[1] < b[3] - pad and b[1] < a[3] - pad


def inside(inner, outer, tol=1.5):
    return (inner[0] >= outer[0] - tol and inner[1] >= outer[1] - tol
            and inner[2] <= outer[2] + tol and inner[3] <= outer[3] + tol)


def rect_like(o):
    return o.ptype == 6 and o.frtype == "0"


def is_check(o):
    return rect_like(o) and 8 <= o.w <= 14.5 and abs(o.w - o.h) < 0.6


def find_fields(objs, currency_boxes=False):
    """Return [(page, x0, y0, x1, y1, kind, multiline)] in canvas coordinates."""
    out = []

    def free(r, ignore=()):
        return not any(overlap(r, f[1:5], 1.0) for f in out)

    def add(page, r, kind="text", multi=False):
        if r[2] - r[0] >= 10 and r[3] - r[1] >= 8 and free(r):
            out.append((page, *r, kind, multi))

    checks = [o for o in objs if is_check(o)]
    texts = [o for o in objs if o.ptype == 4 and not o.annot]
    labels = [o for o in texts if o.text]
    panels = [o for o in objs if rect_like(o) and o.fill == o.stroke == CREAM and o.w > 200]
    # short black lines count too (Length ___); short brown ones are donut ticks
    hlines = [o for o in objs if o.ptype == 5 and o.rot == 0 and o.w >= (12 if o.stroke != BROWN else 25)]
    vlines = [o for o in objs if o.ptype == 5 and o.rot in (90, 270)]

    # 1. check boxes
    for o in checks:
        add(o.page, o.box, "check")

    # 2. empty text frames (typed-in titles, goal box)
    for o in texts:
        if not o.text and o.w >= 20 and o.h >= 10:
            add(o.page, (o.x + 1, o.y + 1, o.x + o.w - 1, o.y + o.h - 1), multi=o.h > 30)

    # 3. table cells
    in_table = set()
    for p in panels:
        pb = p.box
        rows = sorted({round(l.y, 1) for l in hlines if l.page == p.page and l.pw > 2
                       and l.w > p.w * 0.9 and pb[1] - 2 <= l.y <= pb[3] + 2})
        if len(rows) < 2:
            continue
        cols = [pb[0]] + sorted({round(l.x, 1) for l in vlines if l.page == p.page
                                 and pb[0] + 5 < l.x < pb[2] - 5 and pb[1] - 2 <= l.y <= pb[3] + 2}) + [pb[2]]
        for l in hlines:
            if l.page == p.page and inside(l.box, pb, 3):
                in_table.add(id(l))
        heads = [t for t in labels if t.page == p.page and t.text == "Currency"
                 and pb[1] - 30 <= t.y < pb[1]]
        for y0, y1 in zip(rows, rows[1:]):
            for x0, x1 in zip(cols, cols[1:]):
                kind = "combo" if any(x0 <= t.x + 2 < x1 for t in heads) else "text"
                cell = (x0 + 3, y0 + 3, x1 - 3, y1 - 3)
                if any(overlap(cell, t.box, 2) for t in labels if t.page == p.page):
                    continue  # pre-filled
                # boxes in the cell (check boxes, page squares): the field takes the wider side
                cb = [c for c in objs if rect_like(c) and c.page == p.page and c.w < 60
                      and inside(c.box, (x0, y0, x1, y1))]
                if cb:
                    left = (cell[0], cell[1], min(c.x for c in cb) - 4, cell[3])
                    right = (max(c.x + c.w for c in cb) + 4, cell[1], cell[2], cell[3])
                    cell = max(left, right, key=lambda r: r[2] - r[0])
                    if cell[2] - cell[0] < 40:
                        continue
                if kind == "combo":
                    h = min(cell[3] - cell[1], 18)
                    cell = (cell[0], (y0 + y1 - h) / 2, cell[2], (y0 + y1 + h) / 2)
                add(p.page, cell, kind, multi=kind == "text" and (y1 - y0) > 40)

    # 4. small boxes (inner outline, short): page squares, amounts, budget boxes
    for o in objs:
        if not rect_like(o) or is_check(o) or o.fill == "None" or o.pw > 2:
            continue
        if not (14 <= o.h <= 40 and o.w >= 14 and o.w <= 320):
            continue
        r = [o.x + 2, o.y + 2, o.x + o.w - 2, o.y + o.h - 2]
        inner = [t for t in labels if t.page == o.page and overlap(t.box, o.box, 1)]
        if inner:  # labelled box: the field takes the space right of the label
            r[0] = max(r[0], max(t.x + t.w for t in inner) + 2)
        if currency_boxes and r[2] - r[0] > COMBO_W * 2:
            add(o.page, (r[0], r[1], r[0] + COMBO_W, r[3]), "combo")
            r[0] += COMBO_W + 2
        add(o.page, tuple(r), multi=o.h > 40)

    # 5. unlined writing boxes: a main box holding only labels gets a multi-line field
    #    under its lowest label (not taping areas, dividers or photo boxes, which hold boxes or icons)
    for o in objs:
        if not (rect_like(o) and o.pw > 2 and o.fill == CREAM and o.h >= 60 and o.w >= 100):
            continue
        held = [q for q in objs if q is not o and q.page == o.page and q.ptype in (2, 5, 6)
                and overlap(q.box if q.ptype != 5 else (q.x, q.y, q.x + 1, q.y + 1), o.box, 2)]
        if held:
            continue
        inner = [t for t in labels if t.page == o.page and overlap(t.box, o.box, 1)]
        top = max([t.y + t.h for t in inner], default=o.y) + 4
        if o.y + o.h - 6 - top >= 40:
            add(o.page, (o.x + 6, top, o.x + o.w - 6, o.y + o.h - 6), multi=True)

    # 6. write-on lines
    blockers = [o for o in objs if rect_like(o) and o.w < 300 and o.h < 60] + labels
    for l in hlines:
        if id(l) in in_table:
            continue
        thin_brown = l.stroke == BROWN and abs(l.pw - 1.4173) < 0.05  # 0.5 mm: scale lines, rules
        if thin_brown:
            continue
        x0, x1 = l.x, l.x + l.w
        top = l.y - 15
        # stop at the nearest line above (lines can be closer than 15 pt)
        for m in hlines:
            if m is not l and m.page == l.page and m.x < x1 and m.x + m.w > x0 and top < m.y < l.y:
                top = m.y + 1
        r = [x0, top, x1, l.y - 1]
        for b in blockers:
            if b.page != l.page or not overlap(r, b.box, 0.5):
                continue
            bc = b.x + b.w / 2
            if b.y + b.h <= l.y - 6 and b.y + b.h > r[1]:
                r[1] = max(r[1], b.y + b.h)  # label above: start under it
            elif bc < (r[0] + r[2]) / 2:
                r[0] = max(r[0], b.x + b.w + 1)
            else:
                r[2] = min(r[2], b.x - 1)
        add(l.page, tuple(r))
    return out


def make_plain(rel, src):
    """The user's fields switched off (ANNOTATION="0"): same look, nothing to fill."""
    out = str(pathlib.PurePath(rel).with_name(f"{pathlib.PurePath(rel).stem.removesuffix('-claude')}-plain-claude.sla"))
    (ROOT / out).write_text(src.replace('ANNOTATION="1"', 'ANNOTATION="0"'), encoding="utf-8")
    return out


def make(rel):
    src = (ROOT / rel).read_text(encoding="utf-8")
    if 'ANNOTATION="1"' in src:
        return make_plain(rel, src), -src.count('ANNOTATION="1"')
    pages = [(float(re.search(r'PAGEXPOS="([^"]+)"', p)[1]), float(re.search(r'PAGEYPOS="([^"]+)"', p)[1]))
             for p in re.findall(r"<PAGE [^>]*>", src)]
    objs = [Obj(m[1], m[3]) for m in
            re.finditer(r"<PAGEOBJECT\b([^>]*?)(/>|>(.*?)</PAGEOBJECT>)", src, re.S)]
    fields = find_fields(objs, rel in CURRENCY_BOXES)
    for page, *r in EXTRA.get(rel, []):  # canvas = page-relative + page position
        px, py = pages[page]
        fields.append((page, r[0] + px, r[1] + py, r[2] + px, r[3] + py, "text", True))
    if not fields:
        return None, 0
    xml = []
    for n, (page, x0, y0, x1, y1, kind, multi) in enumerate(sorted(fields, key=lambda f: (f[0], f[2], f[1])), 1):
        name = f"p{page + 1}_{kind}{n}"
        xml.append("        " + form_field(x0, y0, x1 - x0, y1 - y0, name, kind, multi,
                                           page_xy=(0, 0), own_page=page,
                                           options=CURRENCIES if kind == "combo" else ()))
    cut = src.rindex("</DOCUMENT>")
    out = twin_name(rel)
    (ROOT / out).write_text(src[:cut] + "\n".join(xml) + "\n    " + src[cut:], encoding="utf-8")
    return out, len(fields)


def eligible():
    files = subprocess.run(["git", "ls-files", "--others", "--cached", "--exclude-standard", "*.sla"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    return [f for f in files if not SKIP.search(f)]


if __name__ == "__main__":
    for rel in sys.argv[1:] or eligible():
        out, n = make(rel)
        if n < 0:
            print(f"{rel}: already has {-n} fields -> plain copy {out}")
        else:
            print(f"{rel}: {n} fields -> {out}" if out else f"{rel}: no fields, skipped")
