#!/usr/bin/env python3
"""Build the business + personal workbook (Claude draft): finance/yearly-workbook-claude.xlsx

One workbook (the user's choice) so the tabs can link to each other in Excel and Google Sheets.
  Read me      what to fill in
  Client data  one row per client                       (Work > Clients)
  Projects     one row per project, picked client       (Work > Clients)
  Money        one row per payment in or out            (Work > Clients, later Work Yearly)
  Client view  pick a client: details, projects, revenue / spending per currency
Work Yearly and Admin (personal) Yearly tabs come in later stages.
Usage: python3 scripts/build-workbook.py   (overwrites the draft: stop once the user fills it in)
Then:  python3 <xlsx skill>/scripts/recalc.py finance/yearly-workbook-claude.xlsx
"""
import pathlib

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "finance/yearly-workbook-claude.xlsx"

# Autumn palette (CLAUDE.md)
BROWN, CREAM, LENS, CREAM_DARK = "4A2A1A", "EAD7AD", "A9C6CC", "C2A679"
FONT = "Arial"
CURRENCIES = ["£", "$", "€"]  # the user's fixed list
CLIENT_STATUS = ["Active", "Paused", "Retainer", "Iterate"]  # from the client overview page
PROJECT_STATUS = ["Ongoing", "Completed"]
MONEY_TYPES = ["Revenue", "Spending"]
ROWS = {"Client data": 100, "Projects": 300, "Money": 1000}  # rows ready to fill in
VIEW_PROJECTS = 20  # projects listed on Client view

head_font = Font(name=FONT, bold=True, color=BROWN)
head_fill = PatternFill("solid", fgColor=CREAM)
input_fill = PatternFill("solid", fgColor="FFFFFF")
pick_fill = PatternFill("solid", fgColor=LENS)  # cells with a drop-down
thin = Side(style="thin", color=CREAM_DARK)
box = Border(left=thin, right=thin, top=thin, bottom=thin)
body = Font(name=FONT, color="000000")
calc = Font(name=FONT, color=BROWN, italic=True)  # formulas: don't type here


def header(ws, row, labels, widths):
    for col, (label, width) in enumerate(zip(labels, widths), 1):
        c = ws.cell(row, col, label)
        c.font, c.fill, c.border = head_font, head_fill, box
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = width
    ws.freeze_panes = ws.cell(row + 1, 1)


def grid(ws, first, last, cols, fill=input_fill):
    for r in range(first, last + 1):
        for c in range(1, cols + 1):
            cell = ws.cell(r, c)
            cell.border, cell.font = box, body
            if cell.fill.fgColor.rgb in (None, "00000000"):
                cell.fill = fill


def pick(ws, ref, source):
    """Drop-down on ref; source is a list or a range formula."""
    formula = f'"{",".join(source)}"' if isinstance(source, list) else source
    dv = DataValidation(type="list", formula1=formula, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(ref)
    cells = ws[ref]
    for row in (cells if isinstance(cells, tuple) else ((cells,),)):
        for cell in row:
            cell.fill = pick_fill


def build():
    wb = Workbook()

    # --- Read me ------------------------------------------------------------
    rd = wb.active
    rd.title = "Read me"
    rd.column_dimensions["A"].width = 100
    lines = [
        ("Business + personal workbook", Font(name=FONT, bold=True, size=14, color=BROWN)),
        ("", body),
        ("Type only in white or blue cells. Blue cells have a drop-down.", body),
        ("Brown italic cells are formulas: they fill in by themselves.", body),
        ("Row 2 of each list is an example: overwrite it or delete it.", body),
        ("", body),
        ("Client data: one row per client.", body),
        ("Projects: one row per project; pick its client from the drop-down.", body),
        ("Money: one row per payment in (Revenue) or out (Spending), with its currency.", body),
        ("Client view: pick a client in B3 to see everything about them on one tab.", body),
        ("", body),
        ("Totals are kept per currency (£, $, €): they are never added together.", body),
    ]
    for i, (text, font) in enumerate(lines, 1):
        rd.cell(i, 1, text).font = font

    # --- Client data ----------------------------------------------------------
    cd = wb.create_sheet("Client data")
    header(cd, 1, ["Client", "Contact name", "Email", "Phone", "Address", "Billing address",
                   "Status", "Notes"], [26, 20, 28, 16, 30, 30, 12, 30])
    n = ROWS["Client data"] + 1
    grid(cd, 2, n, 8)
    pick(cd, f"G2:G{n}", CLIENT_STATUS)
    for col, v in enumerate(["Example Ltd", "Sam Taylor", "sam@example.com", "01234 567890",
                             "1 High Street, Leeds", "1 High Street, Leeds", "Active",
                             "Example row: overwrite or delete"], 1):
        cd.cell(2, col, v)
    clients = f"'Client data'!$A$2:$A${n}"

    # --- Projects -------------------------------------------------------------
    pj = wb.create_sheet("Projects")
    header(pj, 1, ["Project", "Client", "Status", "Start", "End", "Notes", "List no. (auto)"],
           [30, 26, 12, 12, 12, 30, 14])
    n = ROWS["Projects"] + 1
    grid(pj, 2, n, 7)
    pick(pj, f"B2:B{n}", clients)
    pick(pj, f"C2:C{n}", PROJECT_STATUS)
    for r in range(2, n + 1):
        for col in (4, 5):
            pj.cell(r, col).number_format = "dd/mm/yyyy"
        # Numbers the chosen client's projects 1, 2, 3 … so Client view can list them.
        c = pj.cell(r, 7, f"=IF(AND($B{r}<>\"\",$B{r}='Client view'!$B$3),"
                          f"COUNTIF($B$2:$B{r},'Client view'!$B$3),\"\")")
        c.font = calc
    for col, v in enumerate(["Website accessibility review", "Example Ltd", "Ongoing"], 1):
        pj.cell(2, col, v)
    pj.cell(2, 4, "=DATE(2026,9,1)")
    pj.cell(2, 6, "Example row: overwrite or delete")
    projects = f"Projects!$A$2:$A${n}"
    pj_n = n

    # --- Money ----------------------------------------------------------------
    mo = wb.create_sheet("Money")
    header(mo, 1, ["Date", "Client", "Project", "Type", "Currency", "Amount", "Area", "Note"],
           [12, 26, 30, 12, 10, 12, 16, 30])
    n = ROWS["Money"] + 1
    grid(mo, 2, n, 8)
    pick(mo, f"B2:B{n}", clients)
    pick(mo, f"C2:C{n}", projects)
    pick(mo, f"D2:D{n}", MONEY_TYPES)
    pick(mo, f"E2:E{n}", CURRENCIES)
    for r in range(2, n + 1):
        mo.cell(r, 1).number_format = "dd/mm/yyyy"
        mo.cell(r, 6).number_format = "#,##0.00"
    mo.cell(2, 1, "=DATE(2026,9,15)")
    for col, v in enumerate(["Example Ltd", "Website accessibility review", "Revenue", "£", 450,
                             "", "Example row: overwrite or delete"], 2):
        mo.cell(2, col, v)
    mo["G1"].comment = Comment("Area (travel, office, food …) links business spending to the "
                               "Admin yearly tabs, which come in a later stage.", "Claude")
    m = lambda col: f"Money!${col}$2:${col}${n}"  # noqa: E731

    # --- Client view ----------------------------------------------------------
    cv = wb.create_sheet("Client view")
    for col, w in zip("ABCDEF", [30, 30, 13, 13, 13, 13]):
        cv.column_dimensions[col].width = w
    cv["A1"] = "Client view"
    cv["A1"].font = Font(name=FONT, bold=True, size=14, color=BROWN)
    cv["A3"], cv["A3"].font = "Client", head_font
    cv["B3"] = "Example Ltd"
    pick(cv, "B3", clients)
    cv["B3"].border, cv["B3"].font = box, Font(name=FONT, bold=True)
    cv["C3"] = "← pick a client"
    cv["C3"].font = calc
    # Details from Client data
    details = [("Contact", "B"), ("Email", "C"), ("Phone", "D"), ("Address", "E"),
               ("Billing address", "F"), ("Status", "G"), ("Notes", "H")]
    for i, (label, col) in enumerate(details, 5):
        cv.cell(i, 1, label).font = head_font
        c = cv.cell(i, 2, f"=IFERROR(INDEX('Client data'!${col}:${col},"
                          f"MATCH($B$3,'Client data'!$A:$A,0))&\"\",\"\")")
        c.font = calc
    # Money per currency
    top = 5 + len(details) + 1
    for j, label in enumerate(["Currency", "Revenue", "Spending", "Balance"]):
        c = cv.cell(top, 1 + j, label)
        c.font, c.fill, c.border = head_font, head_fill, box
    for i, cur in enumerate(CURRENCIES, top + 1):
        cv.cell(i, 1, cur).border = box
        for j, kind in enumerate(MONEY_TYPES, 2):
            c = cv.cell(i, j, f"=SUMIFS({m('F')},{m('B')},$B$3,{m('E')},$A{i},{m('D')},\"{kind}\")")
            c.font, c.border, c.number_format = calc, box, "#,##0.00;-#,##0.00;-"
        c = cv.cell(i, 4, f"=B{i}-C{i}")
        c.font, c.border, c.number_format = calc, box, "#,##0.00;-#,##0.00;-"
    # Projects of the chosen client (numbered by Projects!G)
    top = top + len(CURRENCIES) + 2
    labels = (["Project", "Status", "Start", "End"] + [f"Revenue {c}" for c in CURRENCIES]
              + [f"Spending {c}" for c in CURRENCIES])
    for col in "GHIJ":
        cv.column_dimensions[col].width = 13
    for j, label in enumerate(labels, 1):
        c = cv.cell(top, j, label)
        c.font, c.fill, c.border = head_font, head_fill, box
    for k in range(1, VIEW_PROJECTS + 1):
        r = top + k
        row = f"MATCH({k},Projects!$G$2:$G${pj_n},0)"
        for j, col in enumerate("ACDE", 1):
            c = cv.cell(r, j, f"=IFERROR(INDEX(Projects!${col}$2:${col}${pj_n},{row})"
                              + ("&\"\"" if col in "AC" else "") + ",\"\")")
            c.font, c.border = calc, box
            if col in "DE":
                c.number_format = "dd/mm/yyyy;;"
        cols = [(cur, kind) for kind in MONEY_TYPES for cur in CURRENCIES]
        for j, (cur, kind) in enumerate(cols, 5):
            c = cv.cell(r, j, f"=IF($A{r}=\"\",\"\",SUMIFS({m('F')},{m('B')},$B$3,{m('C')},$A{r},"
                              f"{m('E')},\"{cur}\",{m('D')},\"{kind}\"))")
            c.font, c.border, c.number_format = calc, box, "#,##0.00;-#,##0.00;-"
    cv.cell(top + VIEW_PROJECTS + 1, 1, f"Shows the first {VIEW_PROJECTS} projects.").font = calc

    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = ws.title not in ("Read me", "Client view")
    wb.active = wb.sheetnames.index("Client view")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build().relative_to(ROOT))
