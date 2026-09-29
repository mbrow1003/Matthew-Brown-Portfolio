# QA/QC Gate — Import Format Spec

Same files, same import path as `fieldwire-hardware-import`. Where this spec is silent, that one governs. Do not improvise column names — Fieldwire matches literally.

## Contents

1. OUTPUT 1 — Task Import CSV
2. OUTPUT 2 — Checklist Setup CSV
3. OUTPUT 3 — Fieldwire Build Brief (FBB)
4. Category and Status rules
5. Naming rules
6. What NOT to do

---

## 1. OUTPUT 1 — Task Import CSV

Header row exactly: `Title,Location,Description,Checklist,Category,Status`

When **plan sheets with a text layer** are available, add `Plan,X pos (%),Y pos (%)` so tasks import pinned. On a **reconciliation** (tasks already pinned), extend to the export's own spellings:

`ID,Title,Location,Description,Checklist,Category,Assignee,Status,Plan,Plan folder,X pos (%),Y pos (%)`

One row per unit.

| Column | Content | Rules |
|---|---|---|
| `ID` | Fieldwire task ID | Reconciliation only. Copied from the export so the import updates in place. |
| `Title` | The unit mark | Verbatim from the source (`RD-01`, `WP-03`, `V-104`, `C-2.1`). Nothing else. |
| `Location` | Room / area as the plan labels it | Short, consistent with the plan sheet. |
| `Description` | Unit-level facts only (recipe below) | No gate steps. No hardware line items. |
| `Checklist` | The unit-type gate checklist name | **Exact match** to OUTPUT 2. |
| `Category` | Current gate phase | One of the fixed values in §4. |
| `Status` | Fieldwire status | Per §4. |
| `Plan`, `X pos (%)`, `Y pos (%)` | Pin coordinates | On a reconciliation, unchanged from the export. On a fresh import, extract from the plan's text layer with `fieldwire-hardware-import/scripts/extract_tag_pins.py` (set `--pattern` to the unit mark convention), check the overlay, and exclude title-block schedule duplicates. `Plan` must match the uploaded sheet's name exactly. |

### Description recipe

```
<Unit type> | <Sheet> rev <n> | <nominal W x H x D> | <material / finish> | <flags>
```

- **Unit type**: the trade reference's vocabulary (`Base cabinet run`, `Wall panel`, `Reception desk`, `Countertop – solid surface`).
- **Sheet rev**: the shop drawing sheet and revision the unit is built from. If the rev is unknown, write `rev: not stated` and flag it in the Build Brief — do not guess.
- **Nominal dims**: from the drawing, in the drawing's units and order. These are what the field dim gets compared to.
- **Material / finish**: as scheduled (`PLAM WilsonArt 7939K`, `Rift white oak, clear`, `Corian Glacier White`).
- **Flags**: only those present, comma-separated:
  - *Gate*: `Field dim required`, `Template required`, `HOLD: <reason>`
  - *Coordination*: `Blocking by others`, `MEP rough-in at unit`, `Coordinate w/ stone`, `Coordinate w/ glazing`
  - *Condition*: `Rated`, `ADA`, `Exterior`

Omit empty segments. Keep it lean.

**Example:**
`Wall panel | SD-04 rev 2 | 96" x 48" | Rift white oak, clear | Field dim required, Blocking by others`

**Example (held):**
`Reception desk | SD-01 rev 1 | 144" x 42" x 30" | PLAM + solid surface top | Field dim required, Template required, HOLD: field width 142-1/4" vs 144" drawn`

---

## 2. OUTPUT 2 — Checklist Setup CSV

Header row exactly: `Checklist,Item`

One block per **unit type**. Lines in phase order. Every line prefixed with its phase.

### Gate line recipe

```
<PHASE>: <action> — <what it is checked against> [— <who signs> + date in task comment]
```

Phases, in order: `FIELD:` → `GATE: RELEASED` → `SHOP:` → `SITE:` → `GATE: ACCEPTED`. `HOLD:` lines sit inside whichever phase they block.

The "who signs" suffix is **required on both `GATE:` lines** and optional elsewhere.

**Generic gate (trim to the unit type per the trade reference):**

```
FIELD: Capture field dims (W / H / D as applicable) — record on task, attach photo
FIELD: Verify adjacent conditions — wall type, blocking, MEP rough-in, floor level
FIELD: Compare field dims to <sheet> rev <n> — mark MATCH or DEVIATION on task
FIELD: If DEVIATION — hold; drawing revised or condition corrected before release
GATE: RELEASED TO SHOP on <sheet> rev __ — PM name + date in task comment
SHOP: Cut list generated from the released rev
SHOP: Fabricated per ticket
SHOP: Finish verified against approved sample
SHOP: Hardware installed per schedule
SHOP: QC — dims vs ticket, finish, function — shop lead name + date
SITE: Delivered — condition verified, damage noted with photo
SITE: Installed per drawing — level, plumb, scribed
SITE: Hardware adjusted, doors and drawers aligned
SITE: Punch complete
GATE: ACCEPTED — PM or GC name + date in task comment
```

The `<sheet>` and `<n>` in the compare line are filled per unit type with the sheet that type is drawn on. If a type spans several sheets, the compare line says `to the sheet named in this task's description`.

### HOLD lines

`HOLD: <condition> — confirm before <phase it blocks>`

Examples:
- `HOLD: blocking not confirmed at wall panels — confirm before RELEASED`
- `HOLD: stone template pending — confirm before SHOP cut`
- `HOLD: rev 3 issued after release — confirm cut list matches before SITE install`

A HOLD is a question someone owes an answer to. A `FIELD:` or `SHOP:` line is work the crew does. Don't file one as the other.

---

## 3. OUTPUT 3 — Fieldwire Build Brief (FBB) & Deployment Steps

**This is the deliverable.** The CSVs are the mechanism; the brief is what the client reads, acts on, and pays for. It is always produced — a clean job gets a brief that says, with counts, that it is clean.

File name: `<Project>_Fieldwire_Build_Brief.md`. Title line: `# <Project> — Fieldwire Build Brief (FBB) & Deployment Steps`. Same skeleton for every trade and for both Fieldwire skills, so a client who gets two briefs sees one document.

**Summary line, first thing under the title, one line:**

`<N> units · <n> held · <n> not released / unpinned · <n> rev mismatches · <n> items owed by others. Built from <package / sheets> at <rev, date>. Brief rev <n>, <date>.`

**Sections, in this order, all present.** Write "None — verified" rather than omitting a section; an absent section reads as unchecked.

1. **Source & scope** — package(s) and sheet numbers, revision, approval status and date. What this brief reconciles: package ↔ Fieldwire always; package ↔ drawings when a cross-check was done. One fidelity line: *faithful to the package as issued at this rev; not warranted against later revisions or field conditions.* On a rebuild, what changed since the previous brief.
2. **Counts** — units on list, pinned, matched, held, unpinned. Must reconcile; show the arithmetic.
3. **Discrepancies** — every reviewer change, markup, or field deviation. Columns: `Mark(s) | Finding | Source says | Found / changed to | Disposition | Owner | Status`. Hardware: resolved into a checklist line, or open with a HOLD. Gate: revise drawing / correct by others / accept as-is.
4. **Held** — not imported or not released. Columns: `Mark | Reason | Owner | Unblocks when`.
5. **Not pinned** — on the list, no task. Paste-ready full row in OUTPUT 1 format, plus `Owner`.
6. **Owed by others** — RFIs, by-others confirmations, coordination, package pieces still missing. Columns: `Item | Affects | Owner | Unblocks`.
7. **Deployment steps** — numbered: checklists first with exact-match names, import, pin, set states, paste comments, and end with the units to walk.

**Every row in sections 3–6 names an owner.** A finding without an owner is a note, not a deliverable.

---

## 4. Category and Status rules

`Category` values are fixed so the board filters cleanly. Use these exact strings:

| Category | Meaning |
|---|---|
| `FIELD VERIFICATION` | Not yet released. Default for a new unit. |
| `HOLD` | A deviation or open condition blocks release or install. |
| `RELEASED TO SHOP` | Release signed; in fabrication queue or in shop. |
| `IN SHOP` | Fabrication underway. |
| `DELIVERED` | On site, not installed. |
| `INSTALLED` | In place, punch open. |
| `ACCEPTED` | Signed off. |

`Status`:

| Condition | Status |
|---|---|
| Any unit in `HOLD` | `Priority 1` |
| Everything else not accepted | `Priority 2` |
| `ACCEPTED` | `Completed` (or `Verified` if the client uses that column for GC sign-off) |

Category changes are made by the person who signs the gate line, at the time they sign it. The checklist and the category should never disagree — if they do, the Build Brief calls it out.

---

## 5. Naming rules

- Checklist name = `<PACKAGE>-<UNIT TYPE>` e.g. `L1-BASE CABINET`, `L1-WALL PANEL`, `L1-COUNTERTOP`. Package prefix required on any multi-package or multi-floor job, same reason as the hardware skill.
- One checklist per unit type. Two reception desks share `L1-RECEPTION DESK`. Do not fork a checklist because two units of the same type differ in size — size lives in the description.
- Fork a checklist only when the **gate** differs (a countertop needs a template line; a wall panel doesn't).
- Unit marks are preserved exactly as the source prints them.

---

## 6. What NOT to do

- Don't put gate steps in the description or unit facts in the checklist.
- Don't let a `GATE:` line be signable by the person whose work it verifies.
- Don't write "compare to drawing" without a sheet and rev.
- Don't leave a unit unreleased without a `HOLD:` line saying why.
- Don't infer a rev, a dim, or a finish. Flag it.
- Don't reuse a real client's project, marks, or drawings in a demo.
