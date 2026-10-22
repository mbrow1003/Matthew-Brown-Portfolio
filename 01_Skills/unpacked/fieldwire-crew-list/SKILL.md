---
name: "fieldwire-crew-list"
description: "Turn a Fieldwire task report PDF (Detailed or saved/closeout export with comments and photos) into a phone-readable crew list plus an ops-lead summary: checklist state per opening, issue comments after a cutoff, dated photos, flags for failed items, closed-with-open-work, done claims, stale receiving gates and no-photo tasks, plus an ops-notes layer. Use for any Fieldwire report, task report, export, punch list, walk list or door-number list, even without the words \"crew list.\""
---

# Fieldwire Crew List

A Fieldwire task report runs to hundreds of pages because it carries every comment and photo since the task was created. The crew needs today's state. This skill cuts the report down to what gets read on a phone and hands the ops lead the counts and flags separately. Fieldwire stays the record; nothing in it is edited.

The written standard is the SOP "Crew List from Fieldwire Task Report." This skill is that SOP as code.

## Inputs

- **The task report PDF**, exported from Fieldwire with comments and photos. Two layouts are read: the Detailed format (photos inline under their message) and the gallery format some saved reports use (a numbered "Photos" section after the messages, each photo listed as its own dated "Photo N" message). The summary says which the run saw.
- **A cutoff date** — usually the date of the latest walk. If none is given, the newest comment date in the report is used and the list says so.
- Optional: a plan filter, a list of door marks, `--walker` to count only one person's comments as issue comments, `--notes` (an ops-notes CSV) and `--banner` (one line under the title).

## Run

```bash
python3 scripts/crew_list.py --report report.pdf --title "<Project> — Crew List" \
    --cutoff 2026-09-22 [--gate-days 7] [--notes notes.csv] [--banner "<rules of the day>"] \
    --out crew_list.pdf --summary ops_summary.md
```

Deliver the crew list PDF to the crew and the summary to the ops lead. Read the summary before sending anything — its first lines say which export this was and therefore what the run could see.

## What each opening keeps

| Keep | Rule |
|---|---|
| Header | Door mark (large), task number, set, status. The set comes from a `#set_` tag when one exists, otherwise from `Set <name>` in the import comment or the description — a project built by the import skill carries it in the description and needs no tag |
| Flags | In red at the top of the block — see below |
| Ops note | From `--notes`, in blue, labelled "Ops note, not in Fieldwire" — see below |
| Import comment | The first comment on the task, when the report carries it. A report filtered to a date window may not; a comment inside the window or a "Photo N" carrier is never shown as the import comment |
| Checklist | Every item with its state: `[ ]` open (bold), `[!]` failed (red), `[x]` done, `[NA]` |
| Issue comments | On or after the cutoff; bare acknowledgements ("ok", "noted", "thanks") and "Photo N" carriers are dropped. A bare "done" / "installed" / "complete" is not an acknowledgement: on a task with open items it is shown, whoever wrote it, and the task is flagged |
| Photos | All photos on or after the cutoff; if none, the single most recent earlier photo, dated and labelled "latest available". Detailed format: a photo is any image left-aligned with the message text, whatever its size. Gallery format: a square image of 100 pt or more in the left column, numbered by the small label at its top-left corner; the number maps it to the task's "Photo N" message, which carries the date. Overlays drawn on a photo (a video's play icon) are skipped. Images elsewhere on the page (plan thumbnail, pin markers) are skipped and counted in the summary |

Openings that are closed (Completed or Verified) with nothing open, nothing failed, and no new comment collapse to one line per plan. Any of them with no photo on the task is starred.

## Ops notes and banner

The report says what the walker wrote; it does not say who owns each line. A comment reading "balcony door stop" on 25 units reads to a crew as 25 stops to install when the real answer is "those doors swing out — ask the super." The notes layer carries that without touching Fieldwire.

`--notes notes.csv` has columns `mark,note[,collapse]`. A note keyed by door mark lands on that mark's PreHung/unit task; a note keyed `#<task number>` lands on that one task (use it when a unit number is shared with a storage-door or common task). `collapse=1` renders the opening as one line under "Nothing for the crew (N), see the ops note" instead of a full block — for units whose only comments belong to someone else, and for units photographed with no issue. `--banner` prints one line under the title for every reader: the rules of the day (what a missing unit means, whose the balcony items are, which counts come from another list, what is waiting on the supplier).

The notes file stays next to the PDF and reruns on the next export. It is project data; it never goes in the portfolio copy of this skill.

## Flags

| Flag | Set when |
|---|---|
| `FAILED ITEM` | Any checklist item carries Fieldwire's red failed mark |
| `CLOSED WITH OPEN ITEMS (Completed)` / `(Verified)` | The task is closed but an item is still open or failed. Verified counts as closed; a task walked past Completed into Verified with work open does not pass |
| `DONE CLAIMED, N ITEMS OPEN` | A comment on or after the cutoff says done / installed / complete while N items are open or failed. The comment is shown under the checklist so the contradiction is visible |
| `RECEIVING GATE OPEN N DAYS` | A task titled `Receiving ...` (the per-delivery receiving gate) is still open more than `--gate-days` (default 7) after its Created date. The one gate that failed in practice sat open for weeks while material was absorbed; this is the in-line check for it |
| `NO PHOTO` | The task has no photo from any date |
| `CONFIRM SET` | The import comment asks to confirm the set |

The SOP's third flag, a checklist that doesn't match the set, can't be seen in this report — it doesn't print checklist names. Catch it with the checklist audit in `fieldwire-hardware-import` against the Detailed CSV export.

**What the export decides.** An Open Tasks report omits completed tasks, so `CLOSED WITH OPEN ITEMS` can only fire on tasks still in it. A saved report with a custom name ("Closeout") reads as an unknown export type; the summary says so and counts the closed tasks it did see. A report filtered to a date window carries only the tasks and comments with activity in that window: a task absent from it had nothing happen, which is a statement about the window, not about the door, and the import comment is usually outside the window. Run the crew list on an All Tasks report when the closed-with-open-work check is the point.

## Validation built into the script

The rule is refuse rather than guess: every abort names the page and position.

- **Unknown checkbox state → abort.** State is read from the fill color Fieldwire draws. A color not in `STATES` stops the run. This exists because Fieldwire's fourth state, failed, was once silently merged into the line above it.
- **Checkbox with no text beside it → abort.** Every box must pair with a checklist line within 5 pt. A box drawn off its line used to merge that item into the one above it and print `[x]` over an open item with every check green; now it stops the run.
- **Wrapped items pair as a block.** Fieldwire centres the checkbox on a wrapped item's whole block, not its first line, and a long item wraps the moment a checked-by date is appended to it. When a line pairs with no box, the parser gathers its continuation lines (each line that reached the column's right edge, followed by one within a line height — line boxes carry ascender padding and may overlap by a few points) and pairs the box against the block's centre. The first real export aborted on exactly this: 29 unpaired lines, every one a two-line item.
- **Checklist line with no checkbox → abort, unless it is a wrapped continuation.** A short line followed by a box-less line is a missing checkbox, not a wrap.
- **Plan sheets are skipped.** Pages of a different size from the report's body pages (the full-size drawings with the pins, appended at the end) are left out and named in the summary; their rotated title-block text would otherwise land in the checklist column.
- **Independent paths.** `pdftotext` counts task headers and message rows; the page's drawings are counted as checkboxes; all three must equal the parser's counts or the run stops.
- **Every opening accounted for.** Full blocks plus one-line completes plus collapsed notes must equal the openings after filtering.
- **Every photo shown is dated.** A gallery photo whose "Photo N" message is missing or undated is not shown and is counted in the summary.
- **Years.** Report dates carry no year. Each task's Created line sets the year — `Created DD Mon YYYY` or `Created MM-DD-YYYY`, both forms occur — and it rolls forward whenever a comment's month drops below the one before it, so a walk on 30 Dec and an issue on 2 Jan both land on the right side of a cutoff. A task with no Created year is noted in the summary.

Then, by hand: spot-check three openings against the source PDF — checklist, comments, photos — before sending. Read the ops notes once more as the crew will: every note should say what is ours and what is not, in that order.

## Attribution

Authors are shown exactly as Fieldwire records them. Accounts are sometimes shared. Before naming who wrote a comment in any summary, confirm who was on site that day; if that isn't known, don't infer it.

## Limitations

- A task with no `Created` year falls back to the cutoff's year and rolls from there; the summary says how many tasks that was.
- The parser reads layout — positions and fill colors. If Fieldwire changes its report layout, the independent-path checks or the state check fail loudly rather than produce a wrong list.
- The synthetic fixture draws a wrapped item's checkbox on its first line; real Fieldwire centres it on the block. The parser handles both, but the fixture does not yet plant the centred case, the gallery photo layout, an appended plan sheet, or a numeric Created line — those four came from the first real export (a closeout report, 10/19/26) and are on the suite's to-add list below.
- The receiving-gate flag keys on the title convention `Receiving ...`; a gate task titled otherwise is not seen.
- The ops-notes layer is only as right as the person who wrote it. It is labelled "not in Fieldwire" on every line so nobody mistakes it for the record.

## Testing

```bash
python3 tests/test_crew_list.py
```

The suite builds the fixture from `tests/fixture_tasks.csv` and `tests/fixture_checklists.csv` (the fictional demo project plus one receiving-gate task), runs the baseline, and compares every task's flags to `tests/expected_flags.json` — a golden file reviewed by hand, not recorded from a run. It then plants one case at a time with `make_demo_report.py --case <name>` and asserts the outcome:

| Case | Must |
|---|---|
| `box-offset`, `box-missing`, `box-missing-first` | abort — a box off its line, a box missing on a later item, a box missing on a first item |
| `color-shift` | abort — a done fill shifted 0.03 |
| `wrapped-item` | pass with the item count unchanged — a real two-line item is one item |
| `verified-open` | flag `CLOSED WITH OPEN ITEMS (Verified)` |
| `done-claim` | flag `DONE CLAIMED, 7 ITEMS OPEN` and show the comment |
| `year-boundary` | show both the 30 Dec and the 2 Jan comment against a 30 Dec cutoff |
| `narrow-photo` | a 55 pt photo is still a photo; no false `NO PHOTO` |
| `no-set-tag` | the set still appears in the header, read from the import comment |

The baseline fixture also fires `RECEIVING GATE OPEN 14 DAYS` on the gate task. All eleven cases pass on v1.3.

To add, from the real-export layouts: `wrapped-item-centred` (box centred on a two-line block, must pass with the item count unchanged), `gallery-photos` (photos in a numbered section, each mapped to its dated "Photo N" message, carriers not shown as issues), `plan-sheet` (a landscape sheet appended, must be skipped and named), `created-numeric` (`Created MM-DD-YYYY`, no "no Created year" note).

To build the demo report by hand:

```bash
python3 scripts/make_demo_report.py --tasks Fieldwire_Task_Import.csv \
    --checklists Fieldwire_Checklist_Setup.csv --out demo_report.pdf [--case <name>]
python3 scripts/crew_list.py --report demo_report.pdf --cutoff 2026-09-08 \
    --title "Demo — Crew List" --out demo_crew_list.pdf --summary demo_summary.md
```

Dependencies are in `requirements.txt`; both scripts name what is missing instead of failing on an import.

## Version

v1.3 — after the first real export (a saved closeout report, 81 pages): wrapped items paired as a block against a centred checkbox; the gallery photo layout (numbered "Photos" section, "Photo N" carrier messages, overlay icons skipped, two-digit labels ignored); appended plan sheets skipped by page size; `Created MM-DD-YYYY`; the import comment shown only when it predates the cutoff; `--notes` ops layer with collapse and `#<task>` keys; `--banner`. The script is `scripts/crew_list.py` v1.3; replace the v1.2 file with it when saving this.

v1.2 — after the enforcement-layer audit: unpaired-checkbox and unpaired-line aborts, checkbox-drawing count as a third path, export type in the summary, Verified treated as closed, done-claim flag, year roll from the Created line, photo filter by column, set read from the import comment, receiving-gate age flag, golden-file regression suite, declared dependencies.