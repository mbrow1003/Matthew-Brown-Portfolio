---
name: fieldwire-hardware-import
description: >-
  Convert a door hardware submittal (door index + grouped hardware schedule) into
  Fieldwire-ready CSVs: a task import (one row per opening, with pins) and a
  checklist setup (one checklist per hardware heading), plus the Fieldwire Build
  Brief, the client-facing reconciliation document. Use whenever the user
  uploads or references a hardware submittal, door schedule, hardware schedule,
  keying schedule, or supplier package and wants Fieldwire tasks, checklists, or a
  hardware import, even if they don't say "Fieldwire." Also use for reconciling a
  Fieldwire task export against a schedule, mid-job set revisions with pins
  preserved, pinning tasks from architect floor-plan PDFs, cross-checking an
  architect door schedule (A-2.xx) against a submittal, auditing which checklists
  are attached, or producing a batch of checklists to create. Prefer it over ad-hoc
  CSV building whenever hardware sets, door schedules, or Fieldwire pins are involved.
---

# Fieldwire Hardware Set Import

Turn a supplier door-hardware submittal into two Fieldwire-ready CSVs. What used to be a full day of manual formatting becomes a few minutes. This skill encodes a specific, field-proven convention — follow it exactly so imports are reliable and re-imports match on heading names.

## The two outputs

**OUTPUT 1 — `Fieldwire_Task_Import.csv`** — one row per door/opening. Columns: `Title`, `Location`, `Description`, `Checklist`. Imported via Tasks > Import Tasks.

**OUTPUT 2 — `Fieldwire_Checklist_Setup.csv`** — every hardware heading as a set of action-oriented line items. Columns: `Checklist`, `Item`. One checklist per hardware heading. Built once per job in Project Settings > Manage Checklists.

The division of labor between the two files is the core principle: **the task description carries opening-level facts; the checklist carries the hardware detail.** Never duplicate hardware line items into the description, and never bury opening facts inside checklist items. This keeps each door task readable at a glance while the checklist drives the actual install/verify steps.

**OUTPUT 3 — `<Project>_Fieldwire_Build_Brief.md`** — **required on every run.** Not only when the submittal is marked up. The Fieldwire Build Brief (FBB) is the key artifact and the deliverable the client pays for: the record of what the reconciliation found — counts that close, wrong attachments, openings outside the submittal, architect-vs-submittal conflicts, what's still missing from the package, who owes each answer, and the deployment steps. The CSVs get consumed by Fieldwire; the brief is what gets read by a person, forwarded to a supplier, or shown to someone who wasn't in the room. A run with no exceptions still produces the brief with the counts and "None — verified" under each section — that is a finding. The skeleton is shared with `fieldwire-qaqc-gate`, so a client who gets both sees one document.

Two more outputs when the inputs support them:

**Pins** — if tasks are unpinned (`X pos (%)` / `Y pos (%)` all `0.0`) and the person can supply the plan sheets Fieldwire has, derive pin coordinates from the door tags in the sheet's text layer and carry them in OUTPUT 1. Read `references/plan-pinning.md`. This replaces hand-placing every pin.

**Checklist paste file** — a plain-text version of OUTPUT 2 (`### name` blocks) for creating checklists by paste or with Claude in Chrome, since the Fieldwire API is not available on standard tiers. Format in `references/format-spec.md` §6.

## Required inputs

1. **Door Index** — supplier submittal listing every door mark/opening and its hardware heading number.
2. **Grouped Hardware Schedule** — supplier submittal showing every hardware item under each heading.

Most suppliers issue these as one combined submittal PDF — parse both halves from the single document. Accept PDF (preferred), Excel, or CSV. If a keying schedule or loose-hardware sheet is included, treat it per "Special cases" below.

Ask for these too — each one changes the output when present:

3. **Architect door schedule** (A-2.00 series sheets). A second source for ratings, remarks, and scope. It settles "non-rated" (a blank rating column is a statement; a silent submittal isn't), it identifies openings the hardware submittal doesn't carry (detention SHM, all-glass, OHC), and its remarks column flags conflicts the submittal misses (`NO ELEC. STRIKE` on an opening whose set ships a strike; `ADD DOOR MONITOR/ALARM` on a set with none). Cross-check every rating and every remark.
4. **Plan sheets** — the exact PDFs uploaded to Fieldwire — for pinning.
5. **Receiving log / closeout list** from earlier phases, so "on the schedule, no task" can be reconciled against closed work instead of being called missing.
6. **Fieldwire task export** — "Open Tasks (Detailed)" carries attached checklist items and tags; "All Tasks (Summary)" doesn't. Ask which one it is.

Before generating anything, read `references/format-spec.md` — it defines the exact column formats, the description field recipe, the checklist item recipe, and the naming rules. Do not improvise these; they are what make Fieldwire matching work on import and re-import.

## Workflow

1. **Read the whole submittal.** Not just the schedule pages — see "Read past the schedule" below. This step is where scope changes hide.

2. **Parse the submittal.** Extract, per opening: door mark, hardware heading, location/room, door size, fire rating, door type, frame type, handing, and any operational flags (electrified, fail-safe/secure, magnetic hold-open, closer, pocket/bypass, etc.). Extract, per heading: every hardware line item with its product number. Extract, separately, every review markup and what it points at. **Count unique headings, not sets**, and say the number early — headings with `:1`, `:2`, `A`, `B` suffixes carry different hardware and each is a checklist. Read the submittal's own opening-list notes too (`Add opening 1251A to the commercial set` is an instruction someone never executed).

2a. **Cross-check the architect door schedule** when it's in hand: ratings (`120M` vs `90Min` on stair doors goes on the checklist as a HOLD), remarks column, and every task in Fieldwire that has no submittal opening — classify it by door/frame material and hardware set prefix (S-series = detention, G/AL = glazier, OHC, STL) so it gets a sourced `NOT IN HW SUBMITTAL` description instead of a blank.

2b. **Audit what's already attached** on a reconciliation with a Detailed export: group tasks by their checklist-item signature and compare to the heading the schedule assigns. Wrong-checklist attachments show up as a hardware signature that contradicts the heading (stair items on a break-room door). List the IDs. See "Imports add, they don't remove."

2c. **Derive pins** if tasks are unpinned and plan sheets are available — `references/plan-pinning.md`, then `scripts/extract_tag_pins.py`. Verify visually before anything else.

3. **Build OUTPUT 1 (task import).** One row per opening — on a reconciliation, one row per existing task including non-submittal ones. Follow the description recipe in `references/format-spec.md` exactly; every row gets a description, none blank. The `Checklist` column value must match the `Checklist` name in OUTPUT 2 character-for-character. Pins ride in the same file — never a separate pin-only import.

4. **Build OUTPUT 2 (checklist setup).** One checklist per unique heading. Each hardware item becomes an action-oriented install line with its product number present. Add the verification steps required by the recipe, plus a HOLD line on any heading with an unresolved review comment.

5. **Build OUTPUT 3 (the Build Brief).** Always. Summary line, then the seven sections in order, every row with an owner. Every count, every exception, every open question.

6. **Validate before presenting.** Run the checks in "Self-check" below. Fix any failure before handing files over.

7. **Present the files** for download with the deployment order: create checklists (exact names) → strip any wrong checklists by hand → import one test row (pin + checklist attach) → import the rest. Nothing to re-export afterwards unless plans or tasks change; coordinates are already in hand.

## Read past the schedule

**Submittals are marked up, and the markups on the product cut sheets change scope as often as the ones on the schedule pages.** Do not stop parsing at the first "PRODUCT SPECIFICATIONS" / "FULL MORTISE" / catalog page. Read to the end of every PDF.

Real examples of scope-changing redlines found only on cut sheets:

- A note on a privacy-lockset sheet requiring occupancy indicators — a different part number, on every privacy opening in the job.
- A full-page X through a lockset cut sheet, voiding that product across a whole heading.
- A fire-rating line resolving an open question about whether a strike could be used on a rated opening, with a fail-secure-only condition.
- "VERIFY W/ ACCESS CONTROLS SUB" notes on strike sheets, which belong in the electrified checklists as a pre-install step.

Cut sheets also carry install constraints worth turning into checklist lines: fail-safe/fail-secure conditions, minimum stile widths, "not to be installed in an inactive leaf," sizing conventions ("36" at single doors, 72" at pairs"). Pull these in when they're a real constraint, not when they're generic catalog copy.

## Reading markups

Markup convention on these submittals:

| Mark | Meaning |
|---|---|
| Red text + arrow | Review comment. What the arrow touches is what it applies to. |
| Blue cloud | Identifies which product on a catalog page is the submitted one. Not a change. |
| Yellow/green highlight | The specific option/size/finish selected. Not a change. |
| Full-page X or strikethrough | The product is voided. Treat as a scope change. |
| Strikethrough on a heading number with a new number written in | The heading is re-designated. |

**Text extraction alone is not enough.** `pdftotext -layout` interleaves red markup text into the schedule rows and corrupts them — a comment lands mid-line inside a door's location field or a hardware item's finish column. Two consequences:

- Strip known markup strings before parsing a line, and re-check any field that came out malformed.
- **Rasterize any page with markups and read it visually** (`pdftoppm -jpeg -r 105`) to see which door or item each arrow actually points at. An arrow pointing at a hardware line applies to the whole heading; an arrow pointing at a door row applies to that opening only. Text extraction cannot tell you which.

Every markup is either: resolved into the output, or listed in the Build Brief. Never dropped, and never silently treated as if the set already includes it. The checklists reflect **what the sets actually list**, with a HOLD line where a set is short.

## Multi-package jobs

A job frequently arrives as several submittals — shell vs. tenant improvement, or floor by floor — often with **different job numbers, meaning different contracts.** Two rules:

1. **Namespace every checklist with a package prefix** (`1FL-`, `2FL-`, `SH-`) — for separate submittals only. A single submittal with ALT 1 / ALT 2 openings is one package; the alternates share headings with base and get no prefix (see `references/format-spec.md` §4). Set numbers repeat across packages with different contents, and Fieldwire checklist names are project-global — unprefixed names collide and the wrong checklist lands on the opening. The prefix also keeps separate contracts visibly separate, which matters for billing and scope.
2. **A door mark can appear in two packages.** The same physical opening may take base hardware from one package and an addition from another (a shell stair door getting an electric strike under the TI finish-out package). One task, one pin. Assign the base package's checklist in the CSV and flag the second checklist for manual attach — don't create a duplicate task.

## Detecting electrified openings

Do not key on "Electric Strike" alone. An opening is electrified if the heading contains any of:

- an electric strike (2925, 2945, etc.)
- an electrified trim or lockset (45ET, motor-driven trim, electrified mortise)
- a power transfer device — ETW / EPT hinge, electric through-wire, power transfer loop
- a maglock, electromagnetic hold-open, or automatic operator
- an ELR (electric latch retraction) exit device with an EPT power transfer — no strike anywhere in the set, easy to miss

Missing a power-transfer hinge is the common failure. Every electrified opening gets the by-others confirmation line, the access-control compatibility line, and a functional-verification line. Word the verification for the actual device — strike release for a strike, trim release plus power-transfer wiring for an electrified trim.

## Imports add, they don't remove

Two Fieldwire behaviors shape every reconciliation:

- **An import attaches the checklist named in the row; it does not detach one already on the task.** A task carrying the wrong checklist keeps it after import and gains the right one. Removal is manual, per task. List the IDs and say so plainly.
- **Editing a checklist template does not update tasks that already have it populated.** Fix the template, then replace the checklist on affected tasks by hand.

The consequence: when the audit in step 2b finds wrong attachments, the deliverable includes a manual-fix list, and the person needs it before the import, not after. Give it as IDs plus marks plus the tag(s) to strip, grouped so a search-bar pass in Fieldwire (which cannot filter by ID) covers them: room-type keywords for a scope batch, door marks one at a time for stragglers.

## Reconciling against an existing Fieldwire export

When tasks already exist and are pinned, the job is a reconciliation, not a fresh import. The person will hand over an "All Tasks" export (UTF-16, tab-delimited, three header rows to skip) alongside the submittals.

Match on **(package, door mark)** — not door mark alone, since marks repeat across packages. Sort into three buckets:

- **Matched** — write to the task import with `ID`, `Plan`, `X pos (%)`, `Y pos (%)` carried through from the export so the pins survive.
- **Not on the submittal** — a task exists but the hardware submittal has no opening for it. Classify from the architect door schedule (detention SHM / S-series set, all-glass entrance, OHC, connector, storefront-supplied) and write the `NOT IN HW SUBMITTAL` description with scope hashtags — sourced, not guessed — with `Checklist` blank. Pin it if it's tagged. Only a mark absent from **both** documents gets the bare `no schedule entry found` line. Never leave a description blank; the person's standard is that every task carries its flag.
- **Held** — a submittal opening whose set is voided or pending reissue. Leave out; list with the reason.
- **No task** — on the schedule but no task. On an "Open Tasks" export, check the receiving / closeout record first: most of these are closed, not missing. For the real gaps, give a separate create-file (no `ID` column, so Fieldwire creates rather than updates) with the pin coordinates if the tag exists.

Report the arithmetic: task count, submittal opening count, matched, not-on-submittal, closed, real gaps. It should reconcile.

Adjacent mark numbers appearing on opposite sides (a `271` pinned with no schedule entry while `272` is on the schedule with no pin) are a typo signal — flag the pair, don't merge them.

## OUTPUT 3 — Fieldwire Build Brief (FBB)

Plain markdown, a page or two. Required every run. The skeleton — summary line plus seven sections — is specified in `references/format-spec.md` §3 and shared with `fieldwire-qaqc-gate`. Every row in sections 3–6 names an owner. Hardware runs fill it like this:

1. **Source & scope** — package, rev, approval status and date; **what changed from the previous revision** if this is a rebuild.
2. **Counts** — the reconciliation arithmetic above. Must close.
3. **Discrepancies**, in this order:
   - **Wrong checklists attached** (from the audit) — IDs, marks, what's on them, what should be, tags to strip. This is the manual-fix list; it goes first.
   - **Open review comments and markups** — grouped by what they affect, with the opening marks listed.
   - **Not on the submittal** — grouped by scope (detention / glazing / OHC / other), with IDs so a tag pass can be batched.
   - **Architect-vs-submittal conflicts** — rating, size, or function mismatches.
4. **Held** — openings not imported, with the reason and who unblocks them.
5. **Not pinned** — (a) on the schedule with no task, split into closed (against the receiving log) and real gaps, with a create-file for the gaps; (b) the four pin buckets from `references/plan-pinning.md`, with IDs.
6. **Owed by others** — still missing from the package (see below), plus RFIs and by-others confirmations.
7. **Deployment steps** — numbered, ending with what to walk.

## Special cases

- **Loose hardware / keying deliverables** (e.g., a `LOOSE1` heading, cores/keying): create a dedicated task+checklist for it rather than forcing it onto a door row. Flag it as a keying/loose deliverable in the description.
- **`1BC` in a lockset or cylinder part number** means one bitted core — construction keying. Permanent cores and the keying schedule are a separate deliverable. If every cylinder on the job is 1BC and no keying schedule is present, say so in the Build Brief rather than assuming keying is covered.
- **Partial exports.** Check the `Page N of M` footer on the first page of each PDF. If it doesn't start at page 1, the front matter — cover, door index, general notes, keying schedule — isn't in hand, and that's usually where fire ratings live. Say which page each file starts on so the person can ask for the rest specifically.
- **Pairs.** A pair is one opening. If a schedule lists `Pair Doors #105A` but Fieldwire has both `105A` and `105B` pinned, flag the inconsistency rather than picking a convention. Per-opening quantities for a pair cover both leaves.
- **Voided or reissued heading pages / held openings**: do NOT import openings whose hardware set is voided or pending reissue. List them separately as held, with the reason. Never silently drop or guess them.

## Revision workflow

When a set is revised (submittal revision or approved substitution):

1. Mass-export current tasks from Fieldwire — XY pin coordinates are preserved in the export.
2. Update the affected checklist in Project Settings > Manage Checklists.
3. Re-batch import the task CSV — coordinates are retained and the updated checklist reference applies.

Critical: update the checklist template **before** the task goes active. Once a task is in progress, checklist edits apply to the template only and do not retroactively update items already completed on active tasks. If coordinates exist from a prior export, re-import with them intact rather than re-pinning by hand.

## Self-check (run before presenting)

- Every opening in the index has exactly one task row; counts match and the reconciliation arithmetic closes.
- Every `Checklist` value in OUTPUT 1 exactly matches a `Checklist` name in OUTPUT 2 (character-for-character — this is the #1 cause of failed imports).
- Checklist names are package-prefixed on multi-package jobs; no two packages share a name.
- Every PDF was read to its last page, not truncated at the first catalog page.
- Every markup found is either resolved into the output or listed in the Build Brief.
- No hardware line items appear in any description; no opening facts are buried in checklist items.
- Every checklist line item includes its product number.
- Every electrified opening — including ones electrified only by trim or power-transfer hinge — has the by-others line, the compatibility line, and a functional-verification line.
- Held openings are listed, not imported. Non-submittal tasks are imported with a sourced `NOT IN HW SUBMITTAL` description and blank checklist — no description is blank.
- Pin coordinates were verified visually on a rendered sheet (one horizontal tag, one rotated) before presenting; the person was told to test one row first.
- Ratings were cross-checked against the architect schedule; `Non-rated per architect schedule` only where that column is blank; disagreements carry an `OPEN REVIEW:` flag.
- On a Detailed export, attached checklist items were audited against headings; wrong attachments are listed by ID with the tag to strip.
- The supplier is named only if the document names it.
- The Build Brief exists, its counts reconcile, every section is present ("None — verified" where empty), and every row in sections 3–6 names an owner.
- Descriptions contain only: set number, size, fire rating, door/frame type, handing, operational flags, review flags.
- Per-opening quantities divide evenly by opening count; if they don't, say so rather than rounding.
- Surface any ambiguity (missing size, illegible heading, unclear location) in the chat as a flagged question — never invent a value to fill a gap.

## House style

Output is plain, forward-ready, no inflation. Ambiguities are surfaced in chat, not embedded silently in the files. Heading naming conventions are preserved exactly as the submittal has them (plus the package prefix), for reliable re-import matching. The description field stays lean so tasks are readable without duplicating checklist content.

Every task carries a description with its status flag — the person's convention is a hashtag (`#hw-tbd` plus a scope tag) that Fieldwire turns into a filterable tag on import. A blank description is a task nobody can filter.

The governing discipline is falsification before escalation: nothing is called missing, short, or complete until it's been tested against the paperwork. The files should make it harder, not easier, to close an opening that isn't actually done.
