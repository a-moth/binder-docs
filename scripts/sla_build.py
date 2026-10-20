"""Small helpers for drawing single-page Scribus documents in the binder style.

A page starts from the user's work/projects/projects-three-section.sla: its colours,
styles and "cleaning page" master (header bar + checklist) are kept, its page objects
are dropped. Coordinates are page-relative points (A4 595 x 842); see CLAUDE.md
"Page style" for the measurements these defaults come from.
"""
import itertools
import math
import pathlib
import re
from xml.sax.saxutils import quoteattr

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "work/projects/projects-three-section.sla"
PAGE_X, PAGE_Y = 100.001, 20.001  # where page 0 sits on the Scribus canvas

# Measured style
BROWN = "Autumn brown dark"
CREAM = "Autumn cream base"
LENS = "Autumn camera lens highlight"
HIGHLIGHT = "Autumn brown highlight"
ADMIN = "Admin blue"
# Colours added to every built page on top of the template's Autumn set.
EXTRA_COLOURS = {ADMIN: (98, 110, 122)}  # Admin cardstock (Ask Herby Design System)
MAIN = 2.83464566929134    # 1 mm outline
INNER = 1.41732283464567   # 0.5 mm outline
LEFT, RIGHT = 42.0, 554.6  # header bar span
BOTTOM = 798.0
ROW = 29.6                 # table row height (Weekly page)
WRITE_GAP = 25.0           # write-on line spacing
CHECK = 12.7559            # checkbox size
MONO, SANS, SANS_BOLD, MONO_ITALIC = (
    "Latin Modern Mono 10 Regular", "Latin Modern Sans 10 Regular",
    "Latin Modern Sans 10 Bold", "Latin Modern Mono 10 Italic")

_ids = itertools.count(1_920_000_000, 7919)


def _common(x, y, w, h):
    gx, gy = x + PAGE_X, y + PAGE_Y
    return (f'XPOS="{gx!r}" YPOS="{gy!r}" OwnPage="0" ItemID="{next(_ids)}" '
            f'WIDTH="{w!r}" HEIGHT="{h!r}"', f'gXpos="{gx!r}" gYpos="{gy!r}" gWidth="0" gHeight="0" LAYER="0"')


def _rect_path(w, h):
    return f"M0 0 L{w:g} 0 L{w:g} {h:g} L0 {h:g} L0 0 Z"


class Page:
    def __init__(self, title, mushroom=True):
        self.objects = []
        # Title inside the header bar, right-aligned (as on every existing page).
        self.text(343.2, 41.8, 207.4, 30.4, title, MONO, 20, align=2, valign=1, inset_bottom=5.669)
        self.mushroom = mushroom  # drawn last in write(), so it sits on top (as on the user's pages)

    # --- primitives -------------------------------------------------------
    def rect(self, x, y, w, h, fill=CREAM, stroke=BROWN, width=MAIN):
        a, b = _common(x, y, w, h)
        p = _rect_path(w, h)
        self.objects.append(
            f'<PAGEOBJECT {a} PTYPE="6" FRTYPE="0" CLIPEDIT="0" PWIDTH="{width!r}" PCOLOR="{fill}" '
            f'PCOLOR2="{stroke}" PLINEART="1" PLINEJOIN="128" path="{p}" copath="{p}" {b}/>')

    def line(self, x, y, length, width=1.0, color="Black", rot=0.0):
        a, b = _common(x, y, length, 1)
        rot_attr = f' ROT="{rot!r}"' if rot else ""
        self.objects.append(
            f'<PAGEOBJECT {a} PTYPE="5" FRTYPE="0" CLIPEDIT="0"{rot_attr} PWIDTH="{width!r}" '
            f'PCOLOR="{color if color != "Black" else "None"}" SHADE="0" PCOLOR2="{color}" '
            f'PLINEART="1" path="" {b}/>')

    def text(self, x, y, w, h, s, font=SANS_BOLD, size=14, color=None, align=0, valign=0,
             inset_bottom=0.0):
        a, b = _common(x, y, w, h)
        p = _rect_path(w, h)
        fc = f' FCOLOR="{color}"' if color else ""
        trail = f' ALIGN="{align}"' if align else ""
        self.objects.append(
            f'<PAGEOBJECT {a} PTYPE="4" FRTYPE="0" CLIPEDIT="0" PWIDTH="1" PLINEART="1" LOCALSCX="1" '
            f'LOCALSCY="1" LOCALX="0" LOCALY="0" LOCALROT="0" PICART="1" SCALETYPE="1" RATIO="1" '
            f'COLUMNS="1" COLGAP="0" AUTOTEXT="0" EXTRA="0" TEXTRA="0" BEXTRA="{inset_bottom!r}" REXTRA="0" '
            f'VAlign="{valign}" FLOP="1" PLTSHOW="0" BASEOF="0" textPathType="0" textPathFlipped="0" '
            f'path="{p}" copath="{p}" {b} NEXTITEM="-1" BACKITEM="-1">'
            f'<StoryText><DefaultStyle FONT="{font}"{fc}/>'
            + "<para/>".join(f'<ITEXT FONT="{font}" FONTSIZE="{size}"{fc} CH={quoteattr(part)}/>'
                             for part in s.split("\n")) +
            f'<trail{trail}/></StoryText></PAGEOBJECT>')

    def image(self, x, y, w, h, asset):
        a, b = _common(x, y, w, h)
        p = _rect_path(w, h)
        # Scale is filled in by relink-images.py (it also picks the checklist colour).
        self.objects.append(
            f'<PAGEOBJECT {a} PTYPE="2" FRTYPE="0" CLIPEDIT="1" PWIDTH="1" PLINEART="1" LOCALSCX="1" '
            f'LOCALSCY="1" LOCALX="0" LOCALY="0" LOCALROT="0" PICART="1" SCALETYPE="1" RATIO="1" '
            f'Pagenumber="0" PFILE="ASSET:{asset}" PRFILE="Embedded sRGB built-in" IRENDER="0" '
            f'EPROF="Embedded sRGB built-in" path="{p}" copath="{p}" {b} NEXTITEM="-1" BACKITEM="-1"/>')

    def ring(self, cx, cy, outer, inner, fill=CREAM):
        """Donut (as on the Monthly page): one shape with a hole."""
        def circle(r):
            k = r * 0.5522847498
            o = outer
            return (f"M{o + r:g} {o:g} C{o + r:g} {o + k:g} {o + k:g} {o + r:g} {o:g} {o + r:g} "
                    f"C{o - k:g} {o + r:g} {o - r:g} {o + k:g} {o - r:g} {o:g} "
                    f"C{o - r:g} {o - k:g} {o - k:g} {o - r:g} {o:g} {o - r:g} "
                    f"C{o + k:g} {o - r:g} {o + r:g} {o - k:g} {o + r:g} {o:g} Z")
        a, b = _common(cx - outer, cy - outer, 2 * outer, 2 * outer)
        p = f"{circle(outer)} {circle(inner)}"
        self.objects.append(
            f'<PAGEOBJECT {a} PTYPE="6" FRTYPE="19" CLIPEDIT="1" PWIDTH="{MAIN!r}" PCOLOR="{fill}" '
            f'PCOLOR2="{BROWN}" PLINEART="1" PLINEJOIN="128" path="{p}" copath="{p}" {b}/>')
        return cx, cy

    # --- composites -------------------------------------------------------
    def checkbox(self, x, y, size=CHECK):
        self.rect(x, y, size, size, fill=LENS, width=INNER)

    def field(self, x, y, label, label_w, line_end, size=14):
        """Label + 2.83 pt brown write-on rule, as on Month / Week of."""
        self.text(x, y, label_w, 23, label, SANS_BOLD, size)
        self.line(x + label_w - 6, y + 18, line_end - (x + label_w - 6), MAIN, BROWN)

    def write_lines(self, x0, x1, y, count, gap=WRITE_GAP):
        for i in range(count):
            self.line(x0, y + i * gap, x1 - x0)

    def segments(self, cx, cy, outer, inner, n):
        """Radial dividers across a donut so it can be shaded in parts."""
        for i in range(n):
            ang = -90 + i * 360 / n
            r = math.radians(ang)
            self.line(cx + inner * math.cos(r), cy + inner * math.sin(r), outer - inner,
                      INNER, BROWN, rot=ang % 360)

    # --- output -----------------------------------------------------------
    def write(self, rel):
        if self.mushroom:
            self.image(491.7, 87.5, 89.6891408450705, 92.057336142841, "custom/mushroomvarious.png")
            self.mushroom = False
        src = TEMPLATE.read_text(encoding="utf-8")
        head = src[:src.index("<PAGEOBJECT")]
        last = head.rindex("<COLOR ")
        cut = head.index("\n", last) + 1
        extra = "".join(f'        <COLOR NAME="{n}" SPACE="RGB" R="{r}" G="{g}" B="{b}"/>\n'
                        for n, (r, g, b) in EXTRA_COLOURS.items() if f'NAME="{n}"' not in head)
        head = head[:cut] + extra + head[cut:]
        tail = src[src.rindex("</DOCUMENT>"):]
        out = ROOT / rel
        to_assets = pathlib.Path(*[".."] * (len(pathlib.PurePath(rel).parts) - 1), "assets")
        body = "\n".join("        " + o for o in self.objects)
        body = re.sub(r'PFILE="ASSET:([^"]+)"', lambda m: f'PFILE="{to_assets}/{m[1]}"', body)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(head + body + "\n    " + tail, encoding="utf-8")
        return out


# --- tables (Weekly page layout) ---------------------------------------------
TABLE_X, TABLE_W = 39.6, 514.8  # Weekly page table panel
HEAD_Y, TABLE_Y = 183.0, 204.0  # column labels, table top


def table(p, cols, rows, row_h=ROW, top=TABLE_Y):
    """Weekly-page table: cream panel, 2.83 pt brown grid. cols = [(x0, label)]."""
    bottom = top + rows * row_h
    p.rect(TABLE_X, top, TABLE_W, bottom - top, fill=CREAM, stroke=CREAM, width=1)
    for i in range(rows + 1):
        p.line(TABLE_X - 0.9, top + i * row_h, TABLE_W + 1.1, MAIN, BROWN)
    xs = [x for x, _ in cols[1:]]
    for x in xs:
        p.line(x, top, bottom - top, MAIN, BROWN, rot=90)
    ends = [x for x, _ in cols[1:]] + [TABLE_X + TABLE_W]
    for (x, label), x1 in zip(cols, ends):
        if label:
            p.text(x + 1, HEAD_Y, x1 - x - 2, 20, label)
    return bottom


def centre_checks(p, x0, x1, top, rows, row_h=ROW):
    for i in range(rows):
        p.checkbox((x0 + x1 - CHECK) / 2, top + i * row_h + (row_h - CHECK) / 2)


# --- shared boxes ------------------------------------------------------------
def lined_box(p, x, y, w, h, title):
    """Main box with a Mono 16 title and write-on lines."""
    p.rect(x, y, w, h)
    p.text(x + 7, y + 6, w - 14, 24, title, MONO, 16, color=BROWN)
    ly = y + 50
    while ly < y + h - 8:
        p.line(x + 7, ly, w - 14)
        ly += WRITE_GAP


def medications(p, y, h):
    """Past / Now / Future medication lines, each with a square for its Treatments page."""
    p.rect(LEFT, y, RIGHT - LEFT, h)
    p.text(LEFT + 7, y + 6, 200, 24, "Medications", MONO, 16, color=BROWN)
    col_gap = 12.0
    col_w = (RIGHT - LEFT - 14 - 2 * col_gap) / 3
    sq_w, sq_h = 22.0, 16.0
    for c, label in enumerate(["Past", "Now", "Future"]):
        x = LEFT + 7 + c * (col_w + col_gap)
        p.text(x, y + 32, col_w, 18, label, SANS_BOLD, 12)
        ly = y + 70
        while ly < y + h - 6:
            p.line(x, ly, col_w - sq_w - 6)
            p.rect(x + col_w - sq_w, ly - sq_h + 1, sq_w, sq_h, fill=LENS, width=INNER)
            ly += 25
