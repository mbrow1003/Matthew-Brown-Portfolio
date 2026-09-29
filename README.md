# Matthew Brown — Implementation Portfolio

Artifacts from implementing Fieldwire at a commercial door and hardware subcontractor (Nov 2024 – present) and then productizing the method for outside contractors. Everything here is mine or built for demonstration. No client project data is included; real engagements are described at pattern level in `03_Case_Notes`.

## What's here

**01_Skills** — three packaged AI pipelines (`.skill` files for Claude; unpacked copies alongside for reading without installing).

- `fieldwire-hardware-import` — supplier hardware submittal (door index + grouped schedule, marked up or clean) → Fieldwire task import CSV, checklist setup CSV, and a Build Brief. Handles reviewer markups, multi-package jobs, and reconciliation against an existing Fieldwire export with pin coordinates preserved. Includes a plan-pinning script that reads each mark's position from an architect sheet's text layer — `pdftotext -bbox`, because pdfplumber drops rotated tags — with the mark pattern set per project, duplicate tags flagged rather than guessed, and a mandatory overlay check before anything imports. On a 461-opening project it pinned 440 tasks from four composite sheets.
- `fieldwire-qaqc-gate` — unit list for any trade (millwork, casework, doors) → sequential verification-gate checklists with separated sign-offs, phase categories on the board, deviation tracking, and a demo mode for building sanitized prospect projects.

- `fieldwire-crew-list` — a Fieldwire task report PDF → a phone-readable crew list and an ops-lead summary. Keeps the checklist state, the import comment, issue comments from the cutoff on, and the newest photos with a dated fallback. Reads checklist state from Fieldwire's checkbox colors and stops on any state it doesn't recognize; checks its own parse against an independent pdftotext count.

The first two produce the same client-facing deliverable, the Fieldwire Build Brief: summary line, source and scope, reconciliation counts, discrepancies, holds, unpinned units, items owed by others, deployment steps — an owner on every row.

**02_Demo_Project** — fully shareable. A fictional hotel lobby millwork package: 14 units, 5 gate checklists (85 lines), one seeded field deviation caught before release to the shop, one unit fully accepted, an original floor plan drawn to match, the Build Brief, and a one-page walkthrough. Built with `fieldwire-qaqc-gate` in demo mode; all 14 tasks import pinned, using the hardware skill's pinning script against the plan. `Pin_Check_Overlay.png` is the verification render. `Demo_Crew_List.pdf` and `Demo_Ops_Summary.md` are the crew-list skill run against `Demo_Fieldwire_Report_Fixture.pdf`, a synthetic report of the same project after a walk — fictional authors, placeholder photos, and one of each case the skill flags. Upload the plan, then import the two CSVs into any Fieldwire project to see it live.

**03_Case_Notes** — the real engagements at pattern level: the subcontractor implementation, a 209-opening school renovation reconciliation, the millwork inquiry that produced the demo, four implementation runs with their numbers, and seven reconciliation and triage patterns. Numbers and findings, no files or names.

**04_Resume** — one page. Phone number omitted from this public copy; email and LinkedIn are in the header.

**05_Operating_Kit** — the field layer around the Fieldwire build.
- `Field_Gates.md` — site recon before mobilization, a receiving gate at every delivery, a closeout gate on every opening, and the missing-material filter that decides whether anything gets reordered. Only one path spends money.
- `Gate_Checklists.csv` — the two gates, ready to import into Fieldwire.
- `QC_Discrepancy_Ledger_Demo.xlsx` — every field claim logged verbatim, walked, and classified by driver, including the ones that held, so the discrepancy rate has a denominator. Fictional data, live formulas.
- `Kickoff_Brief_Demo.md` — a one-page GC kickoff brief on a fictional project: what to hold the line on, what to ask for, and the numbers to carry in.
- `SOW_Template_Demo.md` — the statement of work behind an engagement: deliverables, what's excluded, what the client provides, acceptance criteria, and the line between enablement (mine) and adoption (the client's leadership). Shown filled in for the demo project, fees left blank.


## How I use AI

Not as a chat assistant. The pattern is: capture what's actually true on a jobsite — the submittal as approved, the tasks as pinned, the shipments as received — structure it, and hand it to an agent with rules I wrote from the user's chair. The rules carry things the model wouldn't know to look for: that a power-transfer hinge means an electrified opening, that a reviewer's "see heading" note moved a door to a different set, that a count that doesn't reconcile means the file doesn't ship.

The output is validated before anyone acts on it. Every skill has a self-check; every Build Brief has counts that must reconcile. The human step is designed in, not assumed.

The clearest example: I checked an AI extraction of a 70-page GC schedule. Every date it pulled was correct — and it covered about 38% of the areas. Correct-but-incomplete is the failure that gets through, because everything you spot-check passes. The same pass surfaced two real sequencing conflicts in the GC's own schedule — door and hardware dated about nine days ahead of MEP trim-out in two amenity rooms — and threw out the false flags my own rebuild had generated.

That's the part I think transfers: knowing where the tool fails, from use, and building the gate accordingly.

**06_SOPs** — the written standards behind the tools, all on one nine-section template: purpose, scope, principles, standards, process, validation, boundaries, outputs, summary.
- `SOP_01_Fieldwire_Task_Standards_Import_Workflow_v2.md` — the standard `fieldwire-hardware-import` implements: task, description, checklist, and pin standards; fresh import, reconciliation, and revision workflows; Fieldwire behaviors learned in use; and what the field may and may not change.
- `SOP_Crew_List_from_Fieldwire_Task_Report.md` — turning a Fieldwire task report into a list a crew reads on a phone: what each opening keeps, the flags, and attribution rules for shared accounts. Packaged as the `fieldwire-crew-list` skill.
- `SOP_Ops_Cadence.md` — the governance layer: one card per project with five fields, a Monday update, and a first-Monday board meeting where every decision is asked as yes/no with a named decider.
