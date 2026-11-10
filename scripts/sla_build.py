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
    def __init__(self, title, mushroom=True, header=True):
        """header=False: a divider-style page on the "Normal" master (no header bar,
        no checklist, no title); place the mushroom yourself with image()."""
        self.objects = []
        self.header = header
        if header:
            # Title inside the header bar, right-aligned (as on every existing page).
            self.text(343.2, 41.8, 207.4, 30.4, title, MONO, 20, align=2, valign=1,
                      inset_bottom=5.669)
        self.mushroom = mushroom and header  # drawn last in write(), on top as on the user's pages

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
        src = size_checklist(TEMPLATE.read_text(encoding="utf-8"))
        head = src[:src.index("<PAGEOBJECT")]
        last = head.rindex("<COLOR ")
        cut = head.index("\n", last) + 1
        extra = "".join(f'        <COLOR NAME="{n}" SPACE="RGB" R="{r}" G="{g}" B="{b}"/>\n'
                        for n, (r, g, b) in EXTRA_COLOURS.items() if f'NAME="{n}"' not in head)
        head = head[:cut] + extra + head[cut:]
        if not self.header:
            i = head.index("<PAGE ")
            j = head.index(">", i)
            head = head[:i] + head[i:j].replace('MNAM="cleaning page"', 'MNAM="Normal"') + head[j:]
        tail = src[src.rindex("</DOCUMENT>"):]
        out = ROOT / rel
        to_assets = pathlib.Path(*[".."] * (len(pathlib.PurePath(rel).parts) - 1), "assets")
        body = "\n".join("        " + o for o in self.objects)
        body = re.sub(r'PFILE="ASSET:([^"]+)"', lambda m: f'PFILE="{to_assets}/{m[1]}"', body)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(head + body + "\n    " + tail, encoding="utf-8")
        return out


# --- master-page checklist ---------------------------------------------------
# The user's size for the top-left checklist (measured from their core-layouts-fillable.sla):
# x, y, width, height on the master page, the 512 px icon scaled proportionally.
CHECKLIST_FRAME = (131.182102362205, 50.1971830985915, 32.5925455251192, 32.9577464788733)
CHECKLIST_PX = 512


def size_checklist(text):
    """Give every master-page checklist in an .sla text the user's size."""
    x, y, w, h = CHECKLIST_FRAME
    scale = min(w, h) / CHECKLIST_PX
    path = f"M0 0 L{w:g} 0 L{w:g} {h:g} L0 {h:g} L0 0 Z"
    values = {"XPOS": x, "YPOS": y, "gXpos": x, "gYpos": y, "WIDTH": w, "HEIGHT": h,
              "LOCALSCX": scale, "LOCALSCY": scale, "LOCALX": 0, "LOCALY": 0,
              "SCALETYPE": 0, "RATIO": 1}

    def fix(m):
        tag = m[0]
        for k, v in values.items():
            tag = re.sub(rf'(?<=\s){k}="[^"]*"', f'{k}="{v!r}"' if isinstance(v, float) else f'{k}="{v}"',
                         tag, count=1)
        tag = re.sub(r'(?<=\s)path="[^"]*"', f'path="{path}"', tag, count=1)
        return re.sub(r'(?<=\s)copath="[^"]*"', f'copath="{path}"', tag, count=1)

    return re.sub(r'<MASTEROBJECT\b[^>]*PFILE="[^"]*list-checks[^"]*"[^>]*>', fix, text)


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


def medications(p, y, h, effect=False):
    """Past / Now / Future medication lines, each with a square for its Treatments page.
    effect=True adds an "Effect" line under each one (how it affected symptoms)."""
    p.rect(LEFT, y, RIGHT - LEFT, h)
    p.text(LEFT + 7, y + 6, 200, 24, "Medications", MONO, 16, color=BROWN)
    col_gap = 12.0
    col_w = (RIGHT - LEFT - 14 - 2 * col_gap) / 3
    sq_w, sq_h = 22.0, 16.0
    step = 50 if effect else 25
    for c, label in enumerate(["Past", "Now", "Future"]):
        x = LEFT + 7 + c * (col_w + col_gap)
        p.text(x, y + 32, col_w, 18, label, SANS_BOLD, 12)
        ly = y + 70
        while ly + (24 if effect else 0) < y + h - 6:
            p.line(x, ly, col_w - sq_w - 6)
            p.rect(x + col_w - sq_w, ly - sq_h + 1, sq_w, sq_h, fill=LENS, width=INNER)
            if effect:
                p.text(x, ly + 7, 40, 16, "Effect", SANS_BOLD, 9)
                p.line(x + 32, ly + 21, col_w - 32)
            ly += step


# --- PDF form fields -----------------------------------------------------------
# Attribute set copied from the user's cleaning-docs-templates-fillable.sla
# (ANTYPE 3 = text field, 4 = check box, 5 = combo box; ANFLAG 4096 = multi-line,
# 131072 = combo). A combo box's choices are its text, one paragraph each.
_ANNOT = ('ANNOTATION="1" ANTYPE="{t}" ANACTION="" ANEACT="" ANXACT="" ANDACT="" ANFOACT="" '
          'ANBLACT="" ANKACT="" ANFACT="" ANVACT="" ANCACT="" ANEXTERN="" ANZIEL="0" ANACTYP="0" '
          'ANTOOLTIP="" ANBWID="0" ANBSTY="0" ANFEED="1" ANFLAG="{flag}" ANFONT="0" ANFORMAT="0" '
          'ANROLL="" ANDOWN="" ANVIS="0" ANMC="-1" ANCHK="0" ANAA="0" ANCHKS="0" ANBCOL="{bcol}" '
          'ANHTML="0" ANICON="0" ANPLACE="1" ANSCALE="0" ANITYP="0" ANOPEN="0" ANNAME={name}')


def form_field(x, y, w, h, name, kind="text", multiline=False, size=10, page_xy=(PAGE_X, PAGE_Y),
               own_page=0, item_id=None, options=()):
    """XML for one PDF form field (a Scribus text frame with annotation attributes).
    x, y are page-relative; page_xy is that page's canvas position."""
    gx, gy = x + page_xy[0], y + page_xy[1]
    t = {"text": 3, "check": 4, "combo": 5}[kind]
    flag = 131072 if kind == "combo" else 4096 if multiline else 0
    p = _rect_path(w, h)
    annot = _ANNOT.format(t=t, flag=flag, bcol="None" if kind == "check" else "Black",
                          name=quoteattr(name))
    return (f'<PAGEOBJECT XPOS="{gx!r}" YPOS="{gy!r}" OwnPage="{own_page}" '
            f'ItemID="{item_id or next(_ids)}" PTYPE="4" WIDTH="{w!r}" HEIGHT="{h!r}" FRTYPE="0" '
            f'CLIPEDIT="0" PWIDTH="1" PLINEART="1" {annot} LOCALSCX="1" LOCALSCY="1" LOCALX="0" '
            f'LOCALY="0" LOCALROT="0" PICART="1" SCALETYPE="1" RATIO="1" COLUMNS="1" COLGAP="0" '
            f'AUTOTEXT="0" EXTRA="0" TEXTRA="0" BEXTRA="0" REXTRA="0" VAlign="0" FLOP="1" '
            f'PLTSHOW="0" BASEOF="0" textPathType="0" textPathFlipped="0" path="{p}" copath="{p}" '
            f'gXpos="{gx!r}" gYpos="{gy!r}" gWidth="0" gHeight="0" LAYER="0" NEXTITEM="-1" '
            f'BACKITEM="-1"><StoryText><DefaultStyle FONTSIZE="{size}"/>'
            + "<para/>".join(f"<ITEXT CH={quoteattr(o)}/>" for o in options)
            + '<trail/></StoryText></PAGEOBJECT>')
