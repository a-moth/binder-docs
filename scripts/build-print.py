#!/usr/bin/env python3
"""Gather everything to print into print/<section>/ (the user's request).

For every section:
  <section>-covers-claude.pdf     all sub-tab covers, in tab order (printed on cardstock)
  <section>-laminate-claude.pdf   all pages that get laminated, in tab order
  copies of every other page      named <sub-tab>--<file>.pdf (main-area pages: <file>.pdf)
print/core/ also holds the binder cover and all section dividers in core-covers-claude.pdf
(the user's choice), the laminate tab strips, and the section goal + context pages.

Which PDF prints: the user's own export when there is one and it is newer than its .sla,
otherwise Claude's -claude export. Fillable versions never print. What gets laminated comes
from the user (LAMINATE below; pages given as 1-based page numbers when only some do).
Usage: python3 scripts/build-print.py   (rebuilds print/ from scratch)
"""
import pathlib
import shutil
import subprocess

from pypdf import PdfReader, PdfWriter

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "print"

# Sub-tabs in binder order (CLAUDE.md binder map).
TABS = {
    "finance": ["tracked", "monthly", "digitise", "weekly", "daily"],
    "home": ["progress", "strategy", "monthly", "weekly", "inventory"],
    "health": ["letters", "diagnoses", "treatment", "look-ahead", "potential"],
    "work": ["clients", "projects", "planning", "templates", "archived", "cognitive-load",
             "disability-effects"],
    "learning": ["interest", "explore"],
    "resources": ["templates"],
    "archive": ["2025", "2026", "2027", "digitised"],
    "travel": ["documents", "paperwork", "planning"],
}
# Laminated pages: source .sla (or one-off .pdf) -> pages (None = every page).
LAMINATE = {
    "finance/tracked/cash-pocket-claude.sla": None,
    "finance/tracked/groceries-weekly-claude.sla": None,
    "finance/tracked/pantry-stock-claude.sla": None,
    "finance/tracked/freezer-stock-claude.sla": None,
    "finance/daily/daily-planner-claude.sla": None,
    "finance/budgets/budget-templates.sla": None,             # Monthly + both Weekly
    "finance/yearly-budget.sla": None,
    "finance/tracked/goals-claude.sla": None,
    "finance/tracked/savings-pockets-claude.sla": None,
    "finance/tracked/subscriptions-claude.sla": None,
    "finance/digitise/digitised-log-claude.sla": None,
    "home/progress/rooms-progress-claude.sla": None,
    "home/progress/project-claude.sla": None,
    "home/monthly/*": None,                                   # overview + detail pages
    "home/weekly/weekly-claude.sla": None,
    "learning/interest/collection-pocket-claude.sla": None,
    "learning/interest/design-plan-claude.sla": None,
    "work/projects/projects-three-section.sla": None,
    "health/look-ahead/goals-claude.sla": None,
    "health/look-ahead/appointments-claude.sla": None,
    "health/diagnoses/*": None,                               # summaries, blanks, every diagnosis
    "health/potential/cci-events-claude.sla": None,
    "health/potential/mcas-events-claude.sla": None,
    "health/potential/events-blank-claude.sla": None,
    "health/potential/neuropathy-events-claude.sla": None,
    "health/treatment/treatments-claude.sla": None,
    "health/yearly-checkups-claude.sla": None,
    "work/cognitive-load/cognitive load cards.sla": None,
    "work/cognitive-load/cognitive load day board.sla": None,
    "core/core-layouts.sla": [11, 12],                        # laminate tab strips
}
# core-layouts pages: 1 binder cover, 2-3 section goal + context, 4-10 dividers.
CORE = "core/core-layouts.sla"
# Not printed: variants and files that only exist to be edited from.
SKIP = ("-fillable", "-plain-claude")
# The user's choices: not printed at all, and where Claude's export of the current .sla
# prints instead of the user's older PDF.
NOT_PRINTED = {"work/templates/ask-herby-business-templates-v2.sla",   # -brand prints instead
               "finance/budgets/budget-pages-1.pdf"}                   # old one-off
PRINT_CLAUDE_EXPORT = {"work/clients/client-overview-template-test.sla"}


def git_time(rel):
    out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", rel], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    return int(out or 0)


def page_count(sla):
    return (ROOT / sla).read_text(encoding="utf-8").count("<PAGE ")


def pdf_for(sla):
    """The PDF to print for a .sla: the user's own if it is up to date, else Claude's."""
    p = pathlib.PurePath(sla)
    stem = p.stem
    own = p.with_name(stem + ".pdf")
    mine = p.with_name((stem if stem.endswith("-claude") else stem + "-claude") + ".pdf")
    if (sla not in PRINT_CLAUDE_EXPORT and not stem.endswith("-claude") and (ROOT / own).exists()
            and git_time(str(own)) >= git_time(sla)
            and len(PdfReader(ROOT / own).pages) == page_count(sla)):  # not a one-page export
        return str(own)
    return str(mine) if (ROOT / mine).exists() else None


def documents(section):
    """(sub-tab or '', source, pdf) for every printable document in a section."""
    docs = []
    for sla in sorted((ROOT / section).rglob("*.sla")):
        rel = str(sla.relative_to(ROOT))
        if any(s in rel for s in SKIP) or "/print/" in rel or rel in NOT_PRINTED:
            continue
        pdf = pdf_for(rel)
        if pdf:
            parts = pathlib.PurePath(rel).relative_to(section).parts
            docs.append((parts[0] if len(parts) > 1 else "", rel, pdf))
    # One-off PDFs with no .sla (e.g. budget-pages-1.pdf, client-template-test.pdf).
    slas = {str(s.relative_to(ROOT))[:-4] for s in (ROOT / section).rglob("*.sla")}
    for pdf in sorted((ROOT / section).rglob("*.pdf")):
        rel = str(pdf.relative_to(ROOT))
        base = rel[:-4].removesuffix("-claude")
        if base in slas or rel[:-4] in slas or any(s in rel for s in SKIP) or rel in NOT_PRINTED:
            continue
        parts = pathlib.PurePath(rel).relative_to(section).parts
        docs.append((parts[0] if len(parts) > 1 else "", rel, rel))
    return docs


def is_cover(rel):
    return pathlib.PurePath(rel).name.startswith("cover")


def cover_tab(rel, section):
    name = pathlib.PurePath(rel).stem.removesuffix("-claude")
    if name == "cover":  # <section>/<tab>/cover-claude
        return pathlib.PurePath(rel).relative_to(section).parts[0]
    return name.removeprefix("cover-")


def laminate_pages(rel):
    if rel in LAMINATE:
        return LAMINATE[rel] or "all"
    folder = str(pathlib.PurePath(rel).parent) + "/*"
    return "all" if folder in LAMINATE else None


def add(writer, pdf, pages=None):
    reader = PdfReader(ROOT / pdf)
    for n in pages or range(1, len(reader.pages) + 1):
        writer.add_page(reader.pages[n - 1])


def tab_index(section, tab):
    order = TABS.get(section, [])
    return order.index(tab) if tab in order else len(order)


def build_section(section):
    out = OUT / section
    out.mkdir(parents=True)
    docs = documents(section)
    covers = sorted((d for d in docs if is_cover(d[1])), key=lambda d: tab_index(section, cover_tab(d[1], section)))
    pages = [d for d in docs if not is_cover(d[1])]
    pages.sort(key=lambda d: (d[0] != "", tab_index(section, d[0]), d[1]))
    lam, copies = PdfWriter(), []
    for tab, rel, pdf in pages:
        which = laminate_pages(rel)
        if which == "all":
            add(lam, pdf)
            continue
        if which:  # only some pages laminate: the rest print as their own copy
            add(lam, pdf, which)
            rest = [n for n in range(1, len(PdfReader(ROOT / pdf).pages) + 1) if n not in which]
            w = PdfWriter()
            add(w, pdf, rest)
            name = f"{pathlib.PurePath(pdf).stem}-pages-{'-'.join(map(str, rest))}-claude.pdf"
            copies.append((tab, name, w))
            continue
        copies.append((tab, pathlib.PurePath(pdf).name, pdf))
    report = {}
    if covers:
        w = PdfWriter()
        for _, _, pdf in covers:
            add(w, pdf)
        w.write(out / f"{section}-covers-claude.pdf")
        report["covers"] = [c[2] for c in covers]
    if lam.pages:
        lam.write(out / f"{section}-laminate-claude.pdf")
        report["laminate"] = len(lam.pages)
    for tab, name, src in copies:
        target = out / (f"{tab}--{name}" if tab else name)
        if isinstance(src, PdfWriter):
            src.write(target)
        else:
            shutil.copyfile(ROOT / src, target)
    report["copies"] = len(copies)
    return report


def build_core():
    out = OUT / "core"
    out.mkdir(parents=True)
    core = pdf_for(CORE)
    w = PdfWriter()
    add(w, core, [1] + list(range(4, 11)))  # binder cover + the seven section dividers
    travel = pdf_for("core/travel-divider.sla")
    if travel:
        add(w, travel)
    w.write(out / "core-covers-claude.pdf")
    lam = PdfWriter()
    add(lam, core, LAMINATE[CORE])
    lam.write(out / "core-laminate-claude.pdf")
    goal = PdfWriter()
    add(goal, core, [2, 3])  # used in every section: print one set per section
    goal.write(out / "section-goal-and-context-claude.pdf")
    return {"core": core, "travel divider": travel}


if __name__ == "__main__":
    if OUT.exists():
        shutil.rmtree(OUT)
    print("core:", build_core())
    for section in TABS:
        print(f"{section}:", build_section(section))
