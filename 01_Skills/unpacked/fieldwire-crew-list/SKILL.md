---
name: fieldwire-crew-list
description: >-
  Turn a Fieldwire task report PDF (exported with comments and photos) into a
  phone-readable crew list plus an ops-lead summary: per opening, the checklist
  as it stands (done, open, N/A, failed), the import comment carrying the set
  context, issue comments on or after a cutoff date, and the newest photos with
  one dated fallback when nothing is current. Use whenever the user uploads or
  mentions a Fieldwire report, task report, detailed export, open-tasks PDF,
  punch list for the crew, walk list, or door-number list, or asks to strip old
  comments or photos out of a Fieldwire export — even without the words "crew
  list." Flags failed checklist items, tasks closed with work still open,
  openings with no photo, and import comments that ask to confirm a set. Pairs
  with fieldwire-hardware-import (builds the project) and fieldwire-qaqc-gate
  (builds the gates).
---

# Fieldwire Crew List

A Fieldwire task report runs to hundreds of pages because it carries every comment and photo since the task was created. The crew needs today's state. This skill cuts the report down to what gets read on a phone and hands the ops lead the counts and flags separately. Fieldwire stays the record; nothing in it is edited.

The written standard is the SOP "Crew List from Fieldwire Task Report." This skill is that SOP as code.

## Inputs

- **The task report PDF**, exported from Fieldwire with comments and photos (the Detailed format).
- **A cutoff date** — usually the date of the latest walk. If none is given, the newest comment date in the report is used and the list says so.
- Optional: a plan filter, a list of door marks, and `--walker` to count only one person's comments as issue comments.

## Run

```bash
python3 scripts/crew_list.py --report report.pdf --title "<Project> — Crew List" \
    --cutoff 2026-09-22 --out crew_list.pdf --summary ops_summary.md
```

Deliver the crew list PDF to the crew and the summary to the ops lead. Read the summary before sending anything.

## What each opening keeps

| Keep | Rule |
|---|---|
| Header | Door mark (large), task number, set from a `#set_` tag, status |
| Flags | In red at the top of the block — see below |
| Import comment | The first comment, always — it carries the set context |
| Checklist | Every item with its state: `[ ]` open (bold), `[!]` failed (red), `[x]` done, `[NA]` |
| Issue comments | On or after the cutoff; acknowledgements like "ok" or "done" are dropped |
| Photos | All photos on or after the cutoff; if none, the single most recent earlier photo, dated and labelled "latest available" |

Openings that are Completed with nothing open, nothing failed, and no new comment collapse to one line per plan. Any of them with no photo on the task is starred.

## Flags

| Flag | Set when |
|---|---|
| `FAILED ITEM` | Any checklist item carries Fieldwire's red failed mark |
| `CLOSED WITH OPEN ITEMS` | The task is Completed but an item is still open or failed |
| `NO PHOTO` | The task has no photo from any date |
| `CONFIRM SET` | The import comment asks to confirm the set |

The SOP's third flag, a checklist that doesn't match the set, can't be seen in this report — it doesn't print checklist names. Catch it with the checklist audit in `fieldwire-hardware-import` against the Detailed CSV export.

## Validation built into the script

- **Unknown checkbox state → abort.** State is read from the fill color Fieldwire draws. A color not in `STATES` stops the run with the page and position. This exists because Fieldwire's fourth state, failed, was once silently merged into the line above it.
- **Second path.** `pdftotext` independently counts task headers and message rows; both must equal the parser's counts or the run stops.
- **Every opening accounted for.** Full blocks plus one-line completes must equal the openings after filtering.
- **Every photo shown is dated.**

Then, by hand: spot-check three openings against the source PDF — checklist, comments, photos — before sending.

## Attribution

Authors are shown exactly as Fieldwire records them. Accounts are sometimes shared. Before naming who wrote a comment in any summary, confirm who was on site that day; if that isn't known, don't infer it.

## Limitations

- Report dates carry no year. The cutoff compares month and day, so a report spanning a year boundary needs a manual check.
- The parser reads layout — positions and fill colors. If Fieldwire changes its report layout, the second-path check or the state check will fail loudly rather than produce a wrong list.
- This generalized version was tested against `scripts/make_demo_report.py`, a synthetic report built to the same layout. Its earlier, project-specific form ran on real exports. On the first real export, spot-check more than three openings.

## Testing

```bash
python3 scripts/make_demo_report.py --tasks Fieldwire_Task_Import.csv \
    --checklists Fieldwire_Checklist_Setup.csv --out demo_report.pdf
python3 scripts/crew_list.py --report demo_report.pdf --cutoff 2026-09-08 \
    --title "Demo — Crew List" --out demo_crew_list.pdf --summary demo_summary.md
```

The fixture uses the portfolio's fictional demo project and plants one of each case: a repeated page title, plan thumbnails, an "ok" acknowledgement, a failed item, a task closed with work open, a set to confirm, and tasks with no photo.
