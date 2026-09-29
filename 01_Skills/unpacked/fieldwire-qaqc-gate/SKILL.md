---
name: fieldwire-qaqc-gate
description: >-
  Build a Fieldwire project where every fabricated or installed unit carries a
  sequential QA/QC verification gate — an ordered checklist enforcing phase
  transitions (field-verified → released to shop → fabricated → delivered →
  installed → accepted) with separated sign-offs, not a hardware pick list.
  Outputs the same two Fieldwire CSVs as fieldwire-hardware-import (task import
  + checklist setup) plus the Fieldwire Build Brief. Use whenever the user mentions
  millwork, casework, cabinetry, countertops, wall panels, field dimensions,
  field verification, shop drawings, release to shop/fab, a receiving gate,
  QA/QC, verification sign-off, "staying on the same page," or any trade where
  a unit must pass a check before the next phase — even without the word
  Fieldwire. Also use in demo mode to build a sanitized fictional project for a
  prospect who asked to see examples. For door hardware install checklists from
  a supplier submittal use fieldwire-hardware-import; use this for the gates
  around any trade, doors included.
---

# Fieldwire QA/QC Gate

Turn a unit list — casework schedule, shop drawing index, cut list, door index — into a Fieldwire project where each unit's checklist is a **gate**, not a list. A gate is ordered. Each line is a state transition. The two lines that matter are sign-offs (`RELEASED` and `ACCEPTED`), and the person who signs them is never the person whose work they verify.

This encodes the discipline behind a subcontractor's receiving and closeout gates: nothing advances on silence, nothing is called done until it has been tested against the paperwork, and the doer and the verifier are different people. The hardware-import skill puts *what to install* on the pin. This skill puts *what has to be true before the next step* on the pin.

## The three outputs

Identical file formats to `fieldwire-hardware-import` so both skills import the same way. Read `references/format-spec.md` before generating anything — it carries the exact column formats, the description recipe for units, the gate-line recipe, and the naming rules.

**OUTPUT 1 — `Fieldwire_Task_Import.csv`** — one row per unit. `Title,Location,Description,Checklist,Category,Status` (plus `Plan,X pos (%),Y pos (%)` when plan sheets carry a text layer, and `ID` on a reconciliation). `Category` carries the unit's current gate phase so the board shows state at a glance.

**OUTPUT 2 — `Fieldwire_Checklist_Setup.csv`** — one gate checklist per **unit type** (not per unit), `Checklist,Item`. Lines are ordered by phase and prefixed `FIELD:` / `SHOP:` / `SITE:` / `GATE:`.

**OUTPUT 3 — `<Project>_Fieldwire_Build_Brief.md`** — always. The Build Brief (FBB) is the deliverable the client reads and pays for; the CSVs are how it gets executed. Structure is fixed in `references/format-spec.md` §3 and is identical to the one `fieldwire-hardware-import` produces. A clean job gets a brief that says so with counts.

## Required inputs

1. **A unit list** — anything with one line per fabricated or installed item and a mark: architect's casework schedule, the fabricator's shop drawing sheet index, a cut list, a room-by-room breakdown, a door index. If no list exists, derive one from the shop drawings (one elevation → one or more marked items) and **flag in the Build Brief that marks were derived, not issued**.
2. **The trade** — determines which gate applies. Read the matching file in `references/` (currently `millwork.md`). If the trade has no reference file yet, build the gate from the generic phases below and say so.
3. **Drawing references** — sheet number and revision for each unit, so the gate can name what the field dimension is compared *against*. A gate that says "compare to drawing" without naming the rev is not a gate.

Optional: an existing Fieldwire task export (reconciliation, same rules as the hardware skill), approved finish samples, a hardware schedule for casework hardware.

## The gate, generically

Every trade's gate is some subset of these phases. The reference file for the trade says which lines apply to which unit types.

| Phase | What it verifies | Signed by |
|---|---|---|
| `FIELD:` | The real condition matches the drawing, or the deviation is resolved | Whoever measured |
| `GATE: RELEASED` | Fabrication risk is accepted on a named rev | PM / owner — **not** the person who measured |
| `SHOP:` | The piece matches the ticket, finish sample, and hardware schedule | Shop lead |
| `SITE:` | Delivered undamaged, installed per drawing, punch complete | Installer |
| `GATE: ACCEPTED` | The unit is done | PM or GC — **not** the installer |

Two rules that make it a gate:

- **Doer ≠ verifier on every `GATE:` line.** A field guy checking his own release, or an installer checking his own acceptance, is the failure mode this exists to prevent. Write the sign-off into the line: `GATE: RELEASED TO SHOP — PM name + date in task comment`.
- **HOLD is explicit.** A deviation, a missing rev, a by-others condition not confirmed — each gets a `HOLD:` line in the checklist and moves the task to Category `HOLD` and Status `Priority 1`. Nothing sits quietly unreleased.

## Workflow

1. **Identify the unit and the trade.** Ask if it isn't obvious. "What's a unit for you — a run, an elevation, a room, a ticket?" is the first question on any new trade. Read the trade reference.
2. **Get or derive the unit list.** One row per unit with mark, location, type, drawing ref, rev, nominal dims. Flag derived marks.
3. **Decide the gate per unit type** from the reference file. Countertops need a template line; wall panels don't. Don't ship a gate with lines that don't apply.
4. **Build OUTPUT 1.** Description recipe in `format-spec.md`. `Category` = the unit's current phase if known, else `FIELD VERIFICATION`. `Checklist` matches OUTPUT 2 character-for-character.
5. **Build OUTPUT 2.** One checklist per unit type, lines in phase order, every `GATE:` line naming who signs. Add `HOLD:` lines for known open items on that type.
6. **Build OUTPUT 3 (the Build Brief).** Summary line, then the seven sections in order, every finding with an owner. Deviations, holds, and rev mismatches all land in their sections — nothing lives only in chat.
7. **Demo mode?** If this is for a prospect, read `references/demo-mode.md` before step 2 and follow it — it changes the unit list (fictional), seeds a deviation, sets a mid-project state, and adds a walkthrough note.
8. **Self-check**, below. Then present the files and the setup reminder: checklists first with exact-match names, then task import.

## Reconciling against an existing export

Same rules as `fieldwire-hardware-import`: match on (package, mark), carry `ID`/`Plan`/`X pos (%)`/`Y pos (%)` through, three buckets (matched / held / unpinned), report the arithmetic, never write a guessed description over an existing task. The `ID` column is what lets the import update in place; test on two or three units before running the full set.

## OUTPUT 3 — Fieldwire Build Brief (FBB)

The brief is the product. Its structure — summary line, source & scope, counts, discrepancies, held, not pinned, owed by others, deployment steps — is specified once in `references/format-spec.md` §3 and shared with `fieldwire-hardware-import`. Deviations go in Discrepancies with field value, drawing value, delta, disposition, owner. Units not released go in Held with the reason and who unblocks them. Every row names an owner.

## Self-check

- Every unit on the list has exactly one task row; counts reconcile.
- Every `Checklist` value in OUTPUT 1 matches a name in OUTPUT 2 exactly.
- Every checklist is per unit *type*; no checklist is duplicated per unit.
- Every `GATE:` line names who signs, and that role is not the role that did the gated work.
- Every `FIELD:` compare line names the drawing sheet and rev it compares against.
- Every known deviation appears in the Build Brief **and** as a `HOLD:` on the affected unit's task (Category `HOLD`, Priority 1).
- Descriptions carry unit facts only — no gate steps, no hardware line items.
- Lines that don't apply to a unit type were removed, not left as noise.
- Derived marks, missing revs, and unknown dims are flagged in the Build Brief — never filled in.
- In demo mode: no real client, project, person, or address anywhere in the files.

## House style

Plain, forward-ready, no inflation. Ambiguity surfaces in chat, not silently in the files. Marks and sheet numbers are preserved exactly as the source has them. The gate should make it harder, not easier, to release a unit that hasn't been verified or accept one that hasn't been walked.
