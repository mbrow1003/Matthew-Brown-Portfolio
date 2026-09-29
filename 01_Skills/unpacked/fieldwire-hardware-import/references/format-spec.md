# Fieldwire Import Format Spec

The exact formats for the output files. These are load-bearing — Fieldwire matches on them at import and re-import. Do not improvise.

## Contents

1. OUTPUT 1 — Task Import CSV
2. OUTPUT 2 — Checklist Setup CSV
3. OUTPUT 3 — Fieldwire Build Brief (FBB)
4. Naming rules
5. Parsing notes (PDF and Fieldwire export)
6. Checklist paste file (for Chrome / manual creation)
7. What NOT to do

---

## 1. OUTPUT 1 — Task Import CSV

Header row exactly: `Title,Location,Description,Checklist`

On a **reconciliation** (tasks already exist and are pinned), extend the header to carry the pins through, using the export's own column spellings:

`ID,Title,Location,Description,Checklist,Plan,X pos (%),Y pos (%)`

`Category`, `Assignee`, `Status`, `Plan folder` may be added when they are being changed; leave them out otherwise so the import touches only what it should.

One row per opening. On a reconciliation, **one row per existing task** - including tasks that are not on the hardware submittal (see the non-submittal recipe below). Every task gets a description; none are left blank.

| Column | Content | Rules |
|---|---|---|
| `ID` | Fieldwire task ID | Reconciliation only. Copied from the export so the import updates in place instead of creating duplicates. |
| `Title` | The door mark / opening number | Fresh import: verbatim from the door index (e.g., `104`, `210`, `B12`), nothing else. Reconciliation: **preserve the existing title unchanged** - the person's convention (e.g. `Door 110A - MAINT`) is theirs; parse the mark out of it, don't overwrite it. |
| `Location` | Room / area / plan location | From the schedule's location field. Keep it short and consistent with how the plan labels areas. |
| `Description` | Opening-level facts ONLY (recipe below) | No hardware line items. No product numbers. |
| `Checklist` | The package-prefixed hardware heading name | **Exact match** to the `Checklist` name in OUTPUT 2. Preserve leading zeros, letters, and case. |
| `X pos (%)`, `Y pos (%)` | Pin coordinates | Copied unchanged from the export when tasks are already pinned. When they are not (all `0.0`), derive them from the plan sheets per `references/plan-pinning.md`. Leave blank on rows with no tag - the rest of the row still lands. |

### Description recipe

The description carries only these elements, in this order, separated by ` | `:

```
Set <heading> | <door size> | <fire rating> | <door type> / <frame type> | <handing> | <flags>
```

- **Set**: the hardware heading/set number, unprefixed (the prefix lives in the `Checklist` column).
- **Door size**: e.g., `3' 0" x 7' 0" x 1 3/4"`. Prefix `Pair ` for a pair opening.
- **Fire rating**: e.g., `90 min`, `45 min`. If the submittal is silent, check the **architect door schedule** (A-2.xx sheets): a blank rating column there is a positive statement - write `Non-rated per architect schedule`. Only when both sources are silent, or the architect row won't parse, write `Rating: not specified`. Never infer non-rated from the hardware submittal alone. Where the two sources disagree (architect `120M`, submittal `90Min`), carry the submittal value and add an `OPEN REVIEW:` flag.
- **Door type / frame type**: e.g., `WD Type A / HMF Type 1`, `HMD Type E / HMF`. Use the submittal's abbreviations.
- **Handing**: `LH`, `RH`, `LHR`, `RHR`, `RHRA`, `LHR\RHR`. Strip the `90°` prefix.
- **Flags**: only those present, comma-separated. Two kinds:
  - *Operational*: `Pair`, `Lead-lined`, `Exterior`, `Exit device`, `Closer`, `Electrified - reader/power by others`, `Pocket`, `Bypass`, `Mag hold-open`.
  - *Review*: prefixed `OPEN REVIEW:` — e.g. `OPEN REVIEW: closer requested`, `OPEN REVIEW: occupancy indicator required (not in set)`. These put the unresolved comment on the pin where the field will see it.

Omit any segment with no content. Keep it lean. If a fact isn't in the submittal, don't invent it — flag it.

**Example:**
`Set 1.0 | 3' 0" x 7' 0" x 1 3/4" | Non-rated per architect schedule | WD Type A / HMF Type 1 | LH | Electrified - reader/power by others, Closer`

### Non-submittal opening recipe

A reconciliation export routinely contains tasks for doors that are not in the hardware submittal: detention / security hollow metal (S-series sets), all-glass entrances (glazier), overhead coilings, storefront-supplied leaves. On one 461-opening institutional project that was 84. They still get a description - the field needs to see at a glance why there is no hardware checklist. Source the facts from the architect door schedule:

```
NOT IN HW SUBMITTAL | <scope> - <door mtl> door / <frame mtl> frame | <size> | HW <set> per <sheet> | <rating> | #hw-tbd #<scope-tag>
```

- **Scope**: `Detention`, `All-glass entrance`, `Overhead coiling`, `Connector`, or the bare door/frame material when scope is unclear. Add a short reason clause when there is one (`Submittal opening-list note says add to commercial set, never assigned`).
- **Scope tag**: `#detention`, `#glazing`, `#ohc`. Always also `#hw-tbd`.
- **Hashtags become Fieldwire tags on import.** That is the mechanism: the description carries the flag and the tag filter works without a separate tagging pass. Match the person's existing tag convention where one exists.
- `Checklist` blank.

Example: `NOT IN HW SUBMITTAL | Detention - SHM door / SHM frame | 3'0" x 7'0" x 2" | HW S1 per A-601 | #hw-tbd #detention`

This is not a guessed description - it is sourced from the architect schedule. A task with no source in either document still gets `NOT IN HW SUBMITTAL | no schedule entry found | #hw-tbd` rather than a blank.

---

## 2. OUTPUT 2 — Checklist Setup CSV

Header row exactly: `Checklist,Item`

One block of rows per unique hardware heading. The `Checklist` value repeats for every item in that heading.

### Checklist item recipe

For each hardware item, write an install-oriented line that **includes the product number**, with the per-opening quantity:

```
Install <qty-per-opening> <Item Name> (<product number>) <finish>
```

Per-opening quantity = heading total ÷ number of openings in that heading. Verify it divides evenly; if it doesn't, write the total with the word `total` and flag it rather than rounding.

**Examples:**
- `Install 3 Hinge (ECBB1100 4 1/2 x 4 1/2) US26D`
- `Install 1 Lockset (2580 WTN 1BC 2 3/4 Backset) US26D`
- `Install 1 Electric Strike (2925) US32D`
- `Install 1 Threshold (171 A 36")`

Then append, in this order:

1. `Confirm all hardware installed and operating per set <heading>` — always.
2. For **electrified** openings (strike, electrified trim, power transfer hinge, maglock, operator):
   - `Confirm access control reader, power and low-voltage furnished + installed by others (verify before energizing)`
   - `Confirm compatibility with the access control sub's card reader and operator system before install`
   - then the device-appropriate verification:
     - strike → `Functional verification: cycle opening under power, confirm strike release and positive latching`
     - electrified trim → `Confirm ETW power transfer hinge wired to electrified trim before hanging leaf` + `Functional verification: cycle opening under power, confirm trim release and positive latching both leaves`
3. **Scope steps** the set implies but doesn't itemize — e.g. `Confirm door and frame prepped for future card reader (equipment by TI finish-out package)`.
4. **Manufacturer install constraints** pulled from the cut sheets where they're a real condition — e.g. `Leave strike set fail-secure - switching to fail-safe voids the UL fire rating on this 45-min opening`.
5. **HOLD lines** for unresolved review comments: `HOLD: <comment> - confirm resolution before closing`.

The by-others line matters because on electrified openings the door installer is not responsible for the power supply, access control head-end, or low-voltage. The line forces that boundary to be confirmed rather than assumed.

A scope step is work the installer does. A HOLD is a question someone else owes an answer to. Don't file one as the other.

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

**Hardware-specific formatting**, in addition to the above:

- **Held / unpinned entries carry the ID, mark, plan, and the likely cause.** "Reads as a duplicate pin" is more useful than "not found."
- **Unpinned rows are paste-ready** — full pipe-delimited row in the OUTPUT 1 description format plus the checklist name, so the person can create the task without re-deriving anything.


---

## 4. Naming rules

- Checklist name = `<PACKAGE>-<heading>`, e.g. `1FL-2.0-1`, `SH-6.0.1`. Package prefixes are short and consistent within a job.
- Preserve the heading portion **exactly** as the submittal prints it. Do not normalize `001A` to `1A` or `009 B` to `009B` — Fieldwire re-import matching is literal.
- If two openings share a heading, they share the checklist (one checklist, many tasks referencing it). Do not duplicate the checklist per opening.
- Do not collapse two headings into one checklist just because their hardware happens to be identical. The set number on the task must match the checklist name the field opens, or the mismatch reads as an error.
- The number of unique headings determines checklist-setup effort, not the number of openings **or sets**. Headings split by suffix (`3.01`, `3.01:1`, `3.01:2`, `8.11A`) carry different hardware. On one institutional project: 30 sets, 68 headings, 68 checklists. Count headings, and say so early - the person is usually carrying the set count.
- **Single-package jobs with alternates** (ALT 1 / ALT 2 sheets): alternate openings share headings and hardware with base (the submittal lists them under the same heading). One checklist per heading, no prefix. Track the alternate at the task level with a tag, never by duplicating checklists.
- Package prefixes are for **separate submittals / separate contracts** only.

---

## 5. Parsing notes

### Hardware schedule PDFs

- `pdftotext -layout` is the right extractor — column alignment carries the quantity, finish, and manufacturer fields.
- **Do not truncate at the first catalog page.** Cut sheets carry scope-changing markups. Read every page.
- Red markup text is interleaved into the layout output and will corrupt schedule rows. Strip known markup strings before field-splitting, then re-check any field that came out malformed (a finish column absorbed into a product description is the usual symptom).
- **Rasterize marked-up pages and read them visually** — `pdftoppm -jpeg -r 105 -f N -l N` — to see what each arrow points at. Text extraction gives you the comment but not its target.
- Check the `Page N of M` footer on page 1 of each file to detect a partial export. The supplier name usually lives on page 1 too - if it isn't in hand, say "the submittal" or "the supplier," don't name one.
- **pdfplumber page headers/footers** land as their own lines (`<Project name> ... / <job no.> / <date> ... Page N of NN`), sometimes glued to the last item on the page. Strip each line pattern independently with `re.M` before parsing, or the last hardware line on every page is corrupted.
- **Multi-line by-others items** (`4 Card Reader By Others(By` / `Others)` / `CARD READER BY OTHERS MISC`) need the item-name regex to match the first-line prefix, then absorb continuation lines. Otherwise they glue onto the preceding hardware line.
- **Handing sits mid-line after joining wrapped door rows** (`... 2100 to RH FAM TLT 2107`). Search for the handing token anywhere in the door line, don't anchor it at the end.
- Aggregate handed variants of the same item (`Lockset ... RH` + `... LH` + `... RHR`) before dividing by opening count.

### Fieldwire task export

- UTF-16, tab-delimited, three header rows before the real header: `pd.read_csv(path, sep="\t", encoding="utf-16", skiprows=3, dtype=str)`.
- **Know which export you have.** "All Tasks (Summary)" has no `Description` / `Checklist` columns. "Open Tasks (Detailed)" **excludes completed tasks** and carries `Checklist 1..N` and `Tag 1..N` columns. On an Open export, "on the schedule, no task" usually means *closed*, not *missing* - reconcile against a receiving log or closeout list before calling anything missing. On one institutional project: 48 "missing" = 39 closed Phase 1 doors + 8 CS openings + 1 real gap.
- `Checklist N` cells hold **items**, not checklist names, formatted `<status>: <item text> (<initials>) - <date>`. Use them to audit what is attached: group tasks by their item signature and compare to the heading the schedule assigns. A stair-door item set (fire exit device, 90-min label) on a break-room heading means the wrong checklist was attached - list the IDs; the import cannot fix it (see SKILL.md, "Imports add, they don't remove").
- The `Tag N` columns may not reflect the live project (tags can be cleared after export). Confirm on one task before building a filter on them.
- No `Location` column in the Detailed export - parse room from the title if the person's convention carries it.
- Derive the package from `Plan folder` / `Plan`, not from the door mark.
- Fieldwire's task list **cannot filter by ID.** The search bar matches titles, so search by door mark. Room-type words that appear only in one scope (`CELL`, `SALLY`, `INMATE VST`, `S. VEST`, `SEC HALL`, `LOCK`) isolate detention batches for select-all tagging.

---

## 6. Checklist paste file

Fieldwire's API is not available on standard tiers (add-on via sales, spend threshold, unpublished price). Checklists get created in Project Settings > Checklists either by hand - the builder accepts a block paste of items - or by Claude in Chrome driving the page. Either way, alongside OUTPUT 2 produce a plain-text file the person can open in a browser tab:

```
### <checklist name>
<item>
<item>

### <next name>
```

Split into **PART A - new (create these)** and **PART B - should already exist (verify names, do not duplicate)** when some headings were built in an earlier phase. A side-panel instruction that works: do the first block, stop, show the result, then continue; for PART B only confirm the name exists.

---

## 7. What NOT to do

- Do not put hardware line items or product numbers in the task description.
- Do not put opening facts (size, rating, location) into checklist items.
- Do not invent a size, rating, location, or heading to fill a gap — surface it.
- Do not infer "non-rated" from a silent hardware submittal. Confirm from the architect schedule or write `Rating: not specified`.
- Do not leave any task's description blank on a reconciliation. Non-submittal openings get the `NOT IN HW SUBMITTAL` recipe.
- Do not name the supplier unless the document names it.
- Do not ship a pin-only import and a task import against the same tasks - one file.
- Do not import openings on voided/reissue-pending heading pages — list them as held.
- Do not write a *guessed hardware* description over a task with no schedule match. Give it the non-submittal recipe (sourced from the architect schedule) and pin it; leave `Checklist` blank.
- Do not renumber or reformat heading names.
- Do not stop reading a submittal at the schedule pages.
