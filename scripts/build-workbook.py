#!/usr/bin/env python3
"""Build the business + personal workbook (Claude draft): finance/yearly-workbook-claude.xlsx

One workbook (the user's choice) so the tabs can link to each other in Excel and Google Sheets.
  Read me      what to fill in
  Client data  one row per client                       (Work > Clients)
  Projects     one row per project, picked client       (Work > Clients)
  Money        one row per payment in or out            (Work > Clients, later Work Yearly)
  Client view  pick a client: details, projects, revenue / spending per currency
  Overview, Business spending, Business revenue, Client list   (Work > Yearly, for one year)
  Lists        the areas (travel, office, food …) shared by business and personal spending
  Private overview, Personal spending   (Admin yearly: personal money, same year and areas)
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
AREAS = ["Travel", "Office", "Food", "Software", "Equipment", "Training", "Marketing", "Other"]
AREA_SLOTS = 15  # the area list can grow to this many
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONEY_FMT = "#,##0.00;-#,##0.00;-"
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
        ("Work yearly: type the year on Overview (B3). Business spending, Business revenue and", body),
        ("Client list summarise Money for that year, in the currency picked at the top of each.", body),
        ("Money: leave Client empty for business costs that aren't for a client.", body),
        ("Lists: edit the areas (travel, office, food …). They feed the Area drop-down.", body),
        ("", body),
        ("Personal spending: type personal (not business) spending per area and month,", body),
        ("in the £, $ or € block. Private overview: income is the business revenue;", body),
        ("business spending stays on the Work tabs and is not counted here.", body),
        ("", body),
        ("Totals are kept per currency (£, $, €): they are never added together.", body),
    ]
    for i, (text, font) in enumerate(lines, 1):
        rd.cell(i, 1, text).font = font

    # --- Lists ----------------------------------------------------------------
    ls = wb.create_sheet("Lists")
    header(ls, 1, ["Area"], [24])
    grid(ls, 2, AREA_SLOTS + 1, 1)
    for i, a in enumerate(AREAS, 2):
        ls.cell(i, 1, a)
    ls.cell(1, 3, f"Edit or add areas (up to {AREA_SLOTS}). Business and personal spending "
                  "use the same list.").font = calc
    areas = f"Lists!$A$2:$A${AREA_SLOTS + 1}"

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
    pick(mo, f"G2:G{n}", areas)
    for r in range(2, n + 1):
        mo.cell(r, 1).number_format = "dd/mm/yyyy"
        mo.cell(r, 6).number_format = "#,##0.00"
    mo.cell(2, 1, "=DATE(2026,9,15)")
    for col, v in enumerate(["Example Ltd", "Website accessibility review", "Revenue", "£", 450,
                             "", "Example row: overwrite or delete"], 2):
        mo.cell(2, col, v)
    mo["G1"].comment = Comment("Area (travel, office, food …): edit the list on the Lists tab. "
                               "It will also link business spending to the Admin yearly tabs.",
                               "Claude")
    mo["B1"].comment = Comment("Leave empty for business costs that aren't for a client.", "Claude")
    cd_n = ROWS["Client data"] + 1
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

    work_yearly(wb, m, cd_n, pj_n)
    admin_yearly(wb, m)

    order = ["Read me", "Overview", "Business spending", "Business revenue", "Client list",
             "Private overview", "Personal spending",
             "Client view", "Client data", "Projects", "Money", "Lists"]
    wb._sheets = [wb[t] for t in order]
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = ws.title in ("Client data", "Projects", "Money", "Lists",
                                                    "Personal spending")
    wb.active = wb.sheetnames.index("Overview")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    return OUT


def title(ws, text, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    ws["A1"] = text
    ws["A1"].font = Font(name=FONT, bold=True, size=14, color=BROWN)


def currency_pick(ws):
    ws["A3"], ws["A3"].font = "Currency", head_font
    ws["B3"] = CURRENCIES[0]
    ws["B3"].font, ws["B3"].border = Font(name=FONT, bold=True), box
    pick(ws, "B3", CURRENCIES)
    ws["C3"], ws["C3"].font = "← pick a currency", calc
    ws["E3"], ws["E3"].font = "=\"Year \"&Overview!$B$3", head_font


def cells(ws, r, values, font=calc, fmt=None, fill=None):
    for j, v in enumerate(values, 1):
        c = ws.cell(r, j, v)
        c.font, c.border = font, box
        if fmt and j > 1:
            c.number_format = fmt
        if fill:
            c.fill = fill


def work_yearly(wb, m, cd_n, pj_n):
    """Overview, Business spending, Business revenue and Client list for the year on Overview."""
    year = "Overview!$B$3"
    in_year = (f"{m('A')},\">=\"&DATE({year},1,1),{m('A')},\"<\"&DATE({year}+1,1,1)")

    def in_month(k):  # k = 1..12
        return (f"{m('A')},\">=\"&DATE({year},{k},1),{m('A')},\"<\"&DATE({year},{k + 1},1)")

    # --- Overview -------------------------------------------------------------
    ov = wb.create_sheet("Overview")
    title(ov, "Work yearly overview", [30, 14, 14, 14])
    ov["A3"], ov["A3"].font = "Year", head_font
    ov["B3"] = 2026
    ov["B3"].font, ov["B3"].border = Font(name=FONT, bold=True), box
    ov["C3"], ov["C3"].font = "← type the year", calc
    cells(ov, 5, ["", *CURRENCIES], head_font, fill=head_fill)
    for i, kind in enumerate(MONEY_TYPES, 6):
        cells(ov, i, [kind] + [f"=SUMIFS({m('F')},{m('D')},\"{kind}\",{m('E')},\"{c}\",{in_year})"
                               for c in CURRENCIES], fmt=MONEY_FMT)
        ov.cell(i, 1).font = head_font
    cells(ov, 8, ["Profit"] + [f"={col}6-{col}7" for col in "BCD"], fmt=MONEY_FMT)
    ov["A8"].font = head_font
    counts = [
        ("Clients", f"=COUNTIF('Client data'!$A$2:$A${cd_n},\"?*\")"),
        ("Active clients", f"=COUNTIF('Client data'!$G$2:$G${cd_n},\"Active\")"),
        ("Projects ongoing", f"=COUNTIF(Projects!$C$2:$C${pj_n},\"Ongoing\")"),
        ("Projects completed this year",
         f"=COUNTIFS(Projects!$C$2:$C${pj_n},\"Completed\",Projects!$E$2:$E${pj_n},"
         f"\">=\"&DATE({year},1,1),Projects!$E$2:$E${pj_n},\"<\"&DATE({year}+1,1,1))"),
    ]
    for i, (label, f) in enumerate(counts, 10):
        cells(ov, i, [label, f])
        ov.cell(i, 1).font = head_font
    ov.cell(15, 1, "Spending and revenue by month: see Business spending and Business revenue. "
                   "Completed projects count by their End date.").font = calc

    # --- Business spending: months x areas ----------------------------------------
    bs = wb.create_sheet("Business spending")
    ncol = 1 + AREA_SLOTS + 2
    title(bs, "Business spending", [10] + [12] * (AREA_SLOTS + 2))
    currency_pick(bs)
    head = ["Month"] + [f"=IF(Lists!$A${k + 2}=\"\",\"\",Lists!$A${k + 2})" for k in range(AREA_SLOTS)]
    cells(bs, 5, head + ["No area", "Total"], head_font, fill=head_fill)
    last_area = bs.cell(5, 1 + AREA_SLOTS).column_letter
    for k in range(1, 13):
        r = 5 + k
        row = [MONTHS[k - 1]]
        for a in range(AREA_SLOTS):
            col = bs.cell(5, 2 + a).column_letter
            row.append(f"=IF({col}$5=\"\",\"\",SUMIFS({m('F')},{m('D')},\"Spending\","
                       f"{m('E')},$B$3,{m('G')},{col}$5,{in_month(k)}))")
        row.append(f"=SUMIFS({m('F')},{m('D')},\"Spending\",{m('E')},$B$3,{m('G')},\"\",{in_month(k)})")
        row.append(f"=SUM(B{r}:{bs.cell(r, ncol - 1).column_letter}{r})")
        cells(bs, r, row, fmt=MONEY_FMT)
    tot = ["Total"] + [f"=IF({bs.cell(5, j).column_letter}$5=\"\",\"\",SUM({bs.cell(6, j).column_letter}6:"
                       f"{bs.cell(17, j).column_letter}17))" if j <= 1 + AREA_SLOTS else
                       f"=SUM({bs.cell(6, j).column_letter}6:{bs.cell(17, j).column_letter}17)"
                       for j in range(2, ncol + 1)]
    cells(bs, 18, tot, head_font, fmt=MONEY_FMT, fill=head_fill)
    bs.freeze_panes = "B6"

    # --- Business revenue: clients x months ---------------------------------------
    br = wb.create_sheet("Business revenue")
    title(br, "Business revenue", [28] + [11] * 13)
    currency_pick(br)
    cells(br, 5, ["Client", *MONTHS, "Total"], head_font, fill=head_fill)
    for i in range(cd_n - 1):  # one row per Client data row
        r = 6 + i
        row = [f"=IF('Client data'!$A${i + 2}=\"\",\"\",'Client data'!$A${i + 2})"]
        for k in range(1, 13):
            row.append(f"=IF($A{r}=\"\",\"\",SUMIFS({m('F')},{m('D')},\"Revenue\",{m('E')},$B$3,"
                       f"{m('B')},$A{r},{in_month(k)}))")
        row.append(f"=IF($A{r}=\"\",\"\",SUM(B{r}:M{r}))")
        cells(br, r, row, fmt=MONEY_FMT)
    r = 6 + cd_n - 1
    cells(br, r, ["No client"] + [f"=SUMIFS({m('F')},{m('D')},\"Revenue\",{m('E')},$B$3,{m('B')},\"\","
                                  f"{in_month(k)})" for k in range(1, 13)] + [f"=SUM(B{r}:M{r})"],
          fmt=MONEY_FMT)
    cells(br, r + 1, ["Total"] + [f"=SUM({c}6:{c}{r})" for c in "BCDEFGHIJKLMN"], head_font,
          fmt=MONEY_FMT, fill=head_fill)
    br.freeze_panes = "B6"

    # --- Client list ----------------------------------------------------------
    cl = wb.create_sheet("Client list")
    title(cl, "Client list", [28, 12, 14, 16, 16, 16])
    currency_pick(cl)
    cells(cl, 5, ["Client", "Status", "Projects ongoing", "Projects completed", "Income this year",
                  "Spending this year"], head_font, fill=head_fill)
    for i in range(cd_n - 1):
        r, src = 6 + i, i + 2
        cells(cl, r, [
            f"=IF('Client data'!$A${src}=\"\",\"\",'Client data'!$A${src})",
            f"=IF($A{r}=\"\",\"\",'Client data'!$G${src}&\"\")",
            f"=IF($A{r}=\"\",\"\",COUNTIFS(Projects!$B$2:$B${pj_n},$A{r},Projects!$C$2:$C${pj_n},\"Ongoing\"))",
            f"=IF($A{r}=\"\",\"\",COUNTIFS(Projects!$B$2:$B${pj_n},$A{r},Projects!$C$2:$C${pj_n},\"Completed\"))",
            f"=IF($A{r}=\"\",\"\",SUMIFS({m('F')},{m('D')},\"Revenue\",{m('E')},$B$3,{m('B')},$A{r},{in_year}))",
            f"=IF($A{r}=\"\",\"\",SUMIFS({m('F')},{m('D')},\"Spending\",{m('E')},$B$3,{m('B')},$A{r},{in_year}))",
        ])
        for col in (5, 6):
            cl.cell(r, col).number_format = MONEY_FMT
    cl.freeze_panes = "B6"


def admin_yearly(wb, m):
    """Personal spending (typed, one block per currency) and the Private overview:
    income = business revenue from Money; business spending is kept out (the user's choice)."""
    year = "Overview!$B$3"

    def in_month(k):
        return (f"{m('A')},\">=\"&DATE({year},{k},1),{m('A')},\"<\"&DATE({year},{k + 1},1)")

    # --- Personal spending: a months x areas block per currency ---------------------
    ps = wb.create_sheet("Personal spending")
    ncol = 1 + AREA_SLOTS + 1
    title(ps, "Personal spending", [10] + [12] * (AREA_SLOTS + 1))
    ps["A2"] = "=\"Year \"&Overview!$B$3&\": type personal spending only (business costs go in Money).\""
    ps["A2"].font = calc
    block = 17  # rows per currency block
    tot_col = ps.cell(1, ncol).column_letter
    starts = {}
    for b, cur in enumerate(CURRENCIES):
        top = 4 + b * block
        starts[cur] = top
        ps.cell(top, 1, f"Spending in {cur}").font = Font(name=FONT, bold=True, size=12, color=BROWN)
        head = ["Month"] + [f"=IF(Lists!$A${k + 2}=\"\",\"\",Lists!$A${k + 2})" for k in range(AREA_SLOTS)]
        cells(ps, top + 1, head + ["Total"], head_font, fill=head_fill)
        for k in range(1, 13):
            r = top + 1 + k
            ps.cell(r, 1, MONTHS[k - 1]).border = box
            ps.cell(r, 1).font = head_font
            for j in range(2, 2 + AREA_SLOTS):
                c = ps.cell(r, j)
                c.border, c.font, c.number_format = box, body, MONEY_FMT
            c = ps.cell(r, ncol, f"=SUM(B{r}:{ps.cell(r, ncol - 1).column_letter}{r})")
            c.font, c.border, c.number_format = calc, box, MONEY_FMT
        r = top + 14
        cells(ps, r, ["Total"] + [f"=SUM({ps.cell(1, j).column_letter}{top + 2}:"
                                  f"{ps.cell(1, j).column_letter}{top + 13})" for j in range(2, ncol + 1)],
              head_font, fmt=MONEY_FMT, fill=head_fill)
    ps.freeze_panes = "B4"

    def pick_block(rel_row, col):
        """The cell at (row offset, column) in the block of the currency on Private overview."""
        refs = [f"'Personal spending'!{col}{starts[c] + rel_row}" for c in CURRENCIES]
        return f"CHOOSE(MATCH($B$3,{{\"{'\",\"'.join(CURRENCIES)}\"}},0),{','.join(refs)})"

    # --- Private overview ---------------------------------------------------------
    po = wb.create_sheet("Private overview")
    title(po, "Private finance overview", [18, 16, 18, 14, 4, 18, 16])
    currency_pick(po)
    cells(po, 5, ["Month", "Income (business revenue)", "Personal spending", "Left over"],
          head_font, fill=head_fill)
    for k in range(1, 13):
        r = 5 + k
        cells(po, r, [MONTHS[k - 1],
                      f"=SUMIFS({m('F')},{m('D')},\"Revenue\",{m('E')},$B$3,{in_month(k)})",
                      f"={pick_block(1 + k, tot_col)}",
                      f"=B{r}-C{r}"], fmt=MONEY_FMT)
        po.cell(r, 1).font = head_font
    cells(po, 18, ["Year"] + [f"=SUM({c}6:{c}17)" for c in "BCD"], head_font, fmt=MONEY_FMT,
          fill=head_fill)
    # Personal spending by area for the year
    po.cell(5, 6, "Area").font = head_font
    po.cell(5, 7, "Personal spending").font = head_font
    for j in (6, 7):
        po.cell(5, j).fill, po.cell(5, j).border = head_fill, box
    for a in range(AREA_SLOTS):
        r, col = 6 + a, ps.cell(1, 2 + a).column_letter
        po.cell(r, 6, f"=IF(Lists!$A${a + 2}=\"\",\"\",Lists!$A${a + 2})")
        po.cell(r, 7, f"=IF(F{r}=\"\",\"\",{pick_block(14, col)})")
        for j in (6, 7):
            c = po.cell(r, j)
            c.font, c.border, c.number_format = calc, box, MONEY_FMT
    po.cell(20, 1, "Income is business revenue from Money. Business spending is kept on the "
                   "Work tabs and not counted here.").font = calc


if __name__ == "__main__":
    print(build().relative_to(ROOT))
