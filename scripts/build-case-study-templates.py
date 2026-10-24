#!/usr/bin/env python3
"""Make the case study templates (Claude drafts) from the user's own case studies.

  work/templates/case-study-template-claude.sla            from "case study one.sla"
  work/templates/case-study-overview-template-claude.sla   from "case study overview_1.sla"

Same layout, fonts and Ask Herby brand colours (the user's choice); every case-specific
sentence becomes a bracketed prompt to type over in Scribus. The user's files are not changed.
Each also gets a fillable twin (-fillable-claude.sla): the prompts left empty, with form
fields where they were (positions measured from the exported templates). The exercise
questions keep their inline [prompts] there, since a field can't sit inside a sentence.
Usage: python3 scripts/build-case-study-templates.py
Then:  scripts/export-pdf.sh work/templates/case-study*-template*-claude.sla
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sla_build import form_field  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "work/disability-effects"
OUT = ROOT / "work/templates"

# Text run (start of the user's wording) -> prompt. "" removes the run.
CASE = {
    "Case Study 1": "Case Study #",
    "Design Coordinator working": "[Job title, and the teams they work with]",
    "Demonstrates high initiative": "[What goes well, and the pattern of difficulty]",
    "Requests to transition": "[What they are asking for, and why]",
    "&quot;It's really hard": "&quot;[In their own words: what makes the work hard]&quot;",
    "Open-plan office": "[The physical workspace]",
    "Manager is unsure": "[What the manager or team thinks about the request]",
    "Office space has": "[Spaces, tools or support already available]",
    "   Teams meet in-person": "  [How the team meets and communicates]",
    " Microsoft Teams is": "",
    "What is the primary functional barrier":
        "What is the primary functional barrier driving [the pattern of difficulty]?",
    "Evaluate the request for":
        "Evaluate the request for &quot;[the request]&quot;. Is this a Solution, Accommodation, "
        "or Adjustment? What operational friction might it create?",
    "Propose a balanced resolution plan":
        "Propose a balanced resolution plan between [direct cost], [productivity recovery] "
        "and [team workflows].",
    "  How would your request": "  [Further question]",
    "  What does &quot;struggling": "  [Further question]",
    "  How would you handle": "  [Further question]",
}
# The user's sentences wrapped onto two lines; the short prompts need a paragraph break
# after them so the next prompt stays level with its label / bullet dot.
BREAK_AFTER = ["[What goes well, and the pattern of difficulty]",
               "[What they are asking for, and why]",
               "[Spaces, tools or support already available]"]
OVERVIEW = {
    "Managing Sensory Overload": "[Short title of the case]",
    "Joint Instability": "[Short title of the case]",
    "Return-to-Work Planning": "[Short title of the case]",
    "Design Coordinator working": "[The role, the workplace and how the team works]",
    "Front Desk Administrative": "[The role, the workplace and how the team works]",
    "Product Designer working": "[The role, the workplace and how the team works]",
    "Autism, social anxiety": "[The conditions, how they affect the work, and what was asked for]",
    "Recurrent right-shoulder": "[The conditions, how they affect the work, and what was asked for]",
    "ME/CFS, POTS, fibromyalgia": "[The conditions, how they affect the work, and what was asked for]",
    "Separate the work outcome": "[The idea that orients the group: what to separate, plan for or ask]",
    "Treat EDS and POTS": "[The idea that orients the group: what to separate, plan for or ask]",
    "Immediate ability is not": "[The idea that orients the group: what to separate, plan for or ask]",
}


# Fillable twins: (x0, y0, x1, y1, multi-line) in page points, measured with
# pdftotext -bbox-layout from the exported templates.
CASE_FIELDS = [
    (63, 74, 560, 92, False),     # Role
    (149, 95, 560, 134, True),    # Operational situation
    (80, 137, 560, 176, True),    # Request
    (93, 179, 560, 248, True),    # Statement
    (53, 282, 550, 299, False),   # context bullets
    (53, 300, 550, 317, False),
    (53, 318, 550, 335, False),
    (53, 336, 550, 353, False),
    (45, 586, 550, 603, False),   # further questions
    (45, 604, 550, 621, False),
    (45, 622, 550, 639, False),
]
OVERVIEW_FIELDS = [f for top in (0, 225, 450) for f in [
    (42, 180 + top, 553, 198 + top, False),   # short title
    (110, 204 + top, 553, 221 + top, False),  # work context
    (128, 223 + top, 553, 240 + top, False),  # disability context
    (86, 243 + top, 553, 355 + top, True),    # framing (to the bottom of the card)
]]
FILLABLE_KEEP = ("Case Study 1", "What is the primary", "Evaluate the request", "Propose a balanced")


def template(src, mapping, out, blank=False):
    """Copy src, swapping each mapped text run. blank=True leaves the prompts empty
    (the source for the fillable twin, whose fields sit where the prompts were)."""
    text = (SRC / src).read_text(encoding="utf-8")
    used = set()

    def swap(m):
        ch = m[1]
        for start, new in mapping.items():
            lead = ""
            if not ch.startswith(start):
                if not ch.lstrip(" ").startswith(start):
                    continue
                lead = ch[:len(ch) - len(ch.lstrip(" "))]  # keeps the label alignment
            used.add(start)
            if blank and not start.startswith(FILLABLE_KEEP):
                new = ""
            return f'CH="{lead}{new}"'
        return m[0]

    text = re.sub(r'CH="([^"]*)"', swap, text)
    for prompt in BREAK_AFTER:
        text = re.sub(rf'(<ITEXT\b[^>]*CH=" *{re.escape(prompt)}"[^>]*/>)', r"\1<para/>", text)
    missing = set(mapping) - used
    if missing:
        raise SystemExit(f"{src}: no text run starts with {sorted(missing)}")
    (OUT / out).write_text(text, encoding="utf-8")
    return OUT / out


def fillable(src, mapping, out, fields):
    path = template(src, mapping, out, blank=True)
    text = path.read_text(encoding="utf-8")
    page = re.search(r"<PAGE [^>]*>", text)[0]
    xy = tuple(float(re.search(rf'{k}="([^"]+)"', page)[1]) for k in ("PAGEXPOS", "PAGEYPOS"))
    xml = [form_field(x0, y0, x1 - x0, y1 - y0, f"p1_text{i}", "text", multi, page_xy=xy)
           for i, (x0, y0, x1, y1, multi) in enumerate(fields, 1)]
    cut = text.rindex("</DOCUMENT>")
    path.write_text(text[:cut] + "\n".join("        " + x for x in xml) + "\n    " + text[cut:],
                    encoding="utf-8")
    return path


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for src, mapping, out in [("case study one.sla", CASE, "case-study-template-claude.sla"),
                              ("case study overview_1.sla", OVERVIEW,
                               "case-study-overview-template-claude.sla")]:
        print(template(src, mapping, out).relative_to(ROOT))
    for src, mapping, out, fields in [
            ("case study one.sla", CASE, "case-study-template-fillable-claude.sla", CASE_FIELDS),
            ("case study overview_1.sla", OVERVIEW, "case-study-overview-template-fillable-claude.sla",
             OVERVIEW_FIELDS)]:
        print(fillable(src, mapping, out, fields).relative_to(ROOT))
