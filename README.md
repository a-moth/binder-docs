# binder-docs

> **Note:** The files in the first commit initialise this repository. They are
> the starting set of binder templates (Scribus sources, uploaded as `.sla.xml` and
> since renamed to `.sla`, and exported PDFs), uploaded as-is.

Printable A4 templates for a ring binder, designed in Scribus 1.6.3.

| Folder             | Contents                                                |
|--------------------|---------------------------------------------------------|
| `core/`            | Cover, section dividers, laminate tabs, section sheets  |
| `finance/`         | Yearly budget; `budgets/` monthly, weekly, daily pages  |
| `finance/tracked/` | Subscriptions, savings, goals, cash, groceries, stock (drafts) |
| `home/strategy/cleaning/` | Focus and task worksheets (plain + fillable)     |
| `work/projects/`   | Projects page                                           |
| `travel/`          | Documents, paperwork, planning (to come)                |
| `assets/`          | Lucide icons in every theme colour, plus custom art     |
| `scripts/`         | Icon generator and Scribus helpers                      |

Edit the `.sla` source in Scribus, then export the PDF next to it.
Most documents also have a fillable twin (`*-fillable-claude.sla` / `.pdf`) with PDF
form fields; `scripts/make-fillable.py` makes it and `scripts/export-pdf.sh` exports both.
See [`CLAUDE.md`](CLAUDE.md) for the full binder map and the list of missing files.
