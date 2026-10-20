#!/usr/bin/env python3
"""Draw Home's Yearly tasks page (Claude draft) from the user's Finance Yearly page.

Same layout as finance/yearly-budget.sla: Annual / Biannual / Quarterly columns of
checkbox lines, with "expenses" renamed to "tasks".
Usage: python3 scripts/build-home-yearly.py
Then:  python3 scripts/relink-images.py && scripts/export-pdf.sh home/yearly-tasks-claude.sla
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "finance/yearly-budget.sla").read_text(encoding="utf-8")
assert src.count('CH="expenses"') == 3
out = ROOT / "home/yearly-tasks-claude.sla"
out.write_text(src.replace('CH="expenses"', 'CH="tasks"'), encoding="utf-8")
print(out.relative_to(ROOT))
