# SOP 01 - Fieldwire Task Standards & Import Workflow

Title: SOP 01: Fieldwire Task Standards & Import Workflow

Author: Matthew Brown

Status: Draft

Applies To: Door & Hardware Installation Projects

Version: v2.1 (supersedes v2.0)

Last Updated: 09/26/2026

## 1. Purpose

This SOP defines how door and hardware scope gets into **Fieldwire**. Each opening gets one task and each hardware heading gets one checklist. Tasks are pinned from the plan sheets and built by bulk import from the approved submittal.

The goal is to:

- turn a full day of manual setup into minutes

- put each opening's facts and flags where the field will see them

- keep hardware detail in one place and never retype it

- make it harder to close an opening that isn't done

- run the same way on any job, with any supplier, at any size

## 2. Scope

Applies to:

- **Fresh import:** setting up a new project from the submittal.

- **Reconciliation:** checking an existing Fieldwire project against the submittal. Existing pins are kept.

- **Revision:** submittal revisions, approved substitutions and reissued headings.

- **Multi-package jobs:** separate submittals or separate contracts on one project.

**Required inputs**

- Door index: every opening and its hardware heading.

- Grouped hardware schedule: every item under each heading.

These usually arrive as one combined supplier submittal. PDF is preferred; Excel or CSV is accepted.

**Inputs that change the output when present**

- Architect door schedule (A-2.xx sheets): ratings, remarks, and openings the submittal doesn't carry.

- Plan sheets: the exact files uploaded to Fieldwire, used for pins.

- Receiving log or closeout list: so closed work isn't called missing.

- Fieldwire task export: needed for reconciliation. Confirm which export it is (see 4.8).

## 3. Core Principles

1.  **The submittal defines hardware scope. The architect schedule checks it.**

2.  **Descriptions carry opening facts. Checklists carry hardware. Never both.**

3.  **Each hardware heading gets one checklist, named exactly as the submittal prints it.**

4.  **Every task gets a description, because a blank task can't be filtered.**

5.  **Bulk import replaces manual task creation and hand-placed pins.**

6.  **Nothing is missing, short or complete until it's been tested against the paperwork.**

7.  **Every run ends with a Build Brief, even when nothing is wrong.**

8.  **The field executes. It doesn't make structure or design decisions.**

## 4. Definitions / Standards

### 4.1 System Roles

| **Source / Tool**       | **Role**                                                             |
|-------------------------|----------------------------------------------------------------------|
| Hardware submittal      | Source for openings, headings and hardware items                     |
| Architect door schedule | Cross-check for ratings, remarks, and openings outside the submittal |
| Google Sheets trackers  | Quantities, billing and reporting                                    |
| Fieldwire               | Execution and verification: pins, checklists, photos, close-out      |
| WhatsApp                | Daily narrative and signal. Not a system of record.                  |

### 4.2 Terms

- **Opening:** one physical door location. A pair counts as one opening.

- **Heading:** a hardware set as the submittal prints it, including any suffix (2.0, 2.0:1, 2.0A). A suffixed heading carries different hardware, so it gets its own checklist. Count headings, not sets.

- **Package:** one submittal, which is usually one contract. Each package gets its own prefix.

- **Held opening:** an opening whose set is voided or pending reissue. It's listed but not imported.

- **Non-submittal opening:** a task that exists with no matching opening in the hardware submittal, such as detention, an all-glass entrance, an overhead coiling door or a storefront-supplied leaf.

- **Electrified opening:** a heading that includes any of these: an electric strike, electrified trim or lockset, power transfer hinge or EPT, maglock, magnetic hold-open, auto operator, or ELR exit device. A heading whose only electrified item is a power transfer hinge is the common miss.

### 4.3 Task Standard

- Each opening gets one Fieldwire task. The task represents the physical opening, not the activity.

- **Title on a fresh import:** the door mark exactly as the door index prints it, and nothing else.

- **Title on a reconciliation:** leave the existing title unchanged and read the mark out of it.

- **Location:** the room or area from the schedule. Keep it short and match the plan labels.

- **Pin:** on the door tag, derived from the plan sheet (see 4.6).

**Examples:**

> 104
>
> B12
>
> Door 110A - STOR (existing title, kept on reconciliation)

The v1 title format [OPENING ID] - [HARDWARE SET] is retired. The set now appears in the description and in the checklist name.

### 4.4 Description Recipe

> Set <heading> \| <door size> \| <fire rating> \| <door type> / <frame type> \| <handing> \| <flags>

**Example:**

> Set 1.0 \| 3' 0" x 7' 0" x 1 3/4" \| Non-rated per architect schedule \| WD Type A / HMF Type 1 \| LH \| Electrified - reader/power by others, Closer

- Opening facts only. No hardware items or product numbers.

- **Set:** the heading number, without the prefix. The prefix goes in the checklist name.

- **Rating:** take it from the submittal. If the submittal is silent, use the architect schedule, and write Non-rated per architect schedule only when that column is blank. If both are silent, write Rating: not specified. If they disagree, carry the submittal value and add OPEN REVIEW:.

- **Flags:** operational flags (Pair, Exterior, Exit device, Closer, Electrified - reader/power by others, Mag hold-open, Pocket, Bypass, Lead-lined) and review flags (OPEN REVIEW: <comment>). A review flag puts the open question on the pin where the field will see it.

- **Tags:** hashtags in the description become Fieldwire tags on import: #hw-tbd plus a scope tag.

- Leave out empty segments. Never invent a value to fill a gap. Flag it instead.

**Non-submittal openings:**

> NOT IN HW SUBMITTAL \| <scope> - <door mtl> door / <frame mtl> frame \| <size> \| HW <set> per <sheet> \| <rating> \| #hw-tbd #<scope-tag>

These descriptions come from the architect schedule, and the checklist stays blank. If a mark isn't in either document, its description is NOT IN HW SUBMITTAL \| no schedule entry found \| #hw-tbd.

### 4.5 Checklist Standard

- Each unique heading gets one checklist. Openings on the same heading share it.

- **Name:** <PACKAGE>-<heading> on multi-package jobs (1FL-2.0, TI-6.0.1). On a single-package job, use the heading alone.

- Keep the heading exactly as printed, so 001A never becomes 1A. Re-import matching is literal.

- Don't merge two headings just because their hardware matches. The set on the task has to match the checklist the field opens.

**Item recipe:**

> Install <qty per opening> <item> (<product number>) <finish>
>
> Install 3 Hinge (ECBB1100 4 1/2 x 4 1/2) US26D

The per-opening quantity is the heading total divided by the number of openings on that heading. If it doesn't divide evenly, write the total and flag it rather than rounding.

**After the items, in this order:**

1.  Confirm all hardware installed and operating per set <heading>. This line is always included.

2.  Electrified openings get three lines: the by-others line (reader, power and low-voltage by others; verify before energizing), the access control compatibility line, and a functional verification line worded for the actual device.

3.  Scope steps the set implies but doesn't itemize.

4.  Manufacturer constraints from the cut sheets, when they're a real condition (for example, fail-secure only on a rated opening).

5.  HOLD: <comment> - confirm resolution before closing, one for each unresolved review comment.

A scope step is work we do. A HOLD is an answer someone else owes us.

This replaces the generic functional checklist from v1. Hardware is now itemized on the checklist, once per heading.

### 4.6 Pin Standard

- Pins are set by X pos (%) and Y pos (%) on the plan image, measured from the top left.

- Coordinates come from the door-tag text on the **exact sheet files uploaded to Fieldwire**. Re-exports won't line up. Rotated tags have to be read with pdftotext -bbox.

- If a tag turns up on a different sheet than the task's plan, pin it there and correct the Plan.

- A task that can't be pinned is listed and still imported, with blank coordinates.

- Flattened or scanned sheets have no tag text to read, so those tasks are pinned by hand.

- The pin lands on the tag bubble rather than the door leaf. That's close enough to find the door.

### 4.7 Special Cases

- **Unit and prehung doors:** tracked in grouped tasks, not one per unit. Each door type and level set gets one task with one pin per plan. The checklist lists door types for progress only.

  - Title: PREHUNG DOORS TYPE [X] - LEVELS [Y] - [PLAN]

- **Mark in two packages:** it's still one task with one pin. The CSV attaches the base package's checklist, and the second one is attached by hand.

- **Alternates:** ALT 1 and ALT 2 openings in one submittal share the base headings. They get no prefix and are tracked with a task tag.

- **Loose hardware and keying:** a LOOSE heading gets its own task and checklist, never a door row.

- **Construction cores:** 1BC means construction keying. Permanent cores and the keying schedule are a separate deliverable. If every cylinder is 1BC and there's no keying schedule, the log says so.

- **Pairs:** a pair is one opening. If Fieldwire has each leaf as a separate task, flag it rather than picking one.

- **Partial exports:** check the Page N of M footer on page 1. If the file doesn't start at page 1, the front matter is missing, and that's usually where the ratings are.

### 4.8 Fieldwire Behaviors

- **Imports add, they don't remove.** An import attaches the checklist named in the row but doesn't detach one already on the task. A wrong checklist has to be removed by hand, task by task.

- **Template edits don't carry over.** Editing a checklist template doesn't change tasks that already have it. Those tasks get the checklist replaced by hand.

- **No filtering by ID.** Search only matches titles, so manual-fix lists are grouped by door mark or room keyword.

- **Exports:** files are UTF-16 and tab-delimited, with three rows above the header. "All Tasks (Summary)" has no Description or Checklist columns. "Open Tasks (Detailed)" leaves out completed tasks but includes checklist items and tags.

- **No API on standard tiers.** Checklists are created in Project Settings by pasting into the builder, by hand, or by a browser agent working from the paste file.

## 5. Process / Workflow

### 5.1 Fresh Import

1.  **Read every page of every PDF.** Markups on the cut sheets change scope as often as markups on the schedule.

2.  **Parse openings and headings.** For each opening: mark, heading, location, size, rating, door and frame type, handing and flags. For each heading: every item and its product number. State the count of unique headings early.

3.  **Read the markups visually** on any marked-up page. Text extraction shows the comment but not what the arrow points at.

4.  **Cross-check the architect door schedule** for ratings, remarks, and openings the submittal doesn't carry.

5.  **Derive pins** if the plan sheets are in hand.

6.  **Build the task import, the checklist setup and the paste file.**

7.  **Write the Build Brief.**

8.  **Run validation** (Section 6).

9.  **Deploy in order:** create the checklists with their exact names, then strip wrong checklists by hand, then import one test row and check its pin and checklist, then import the rest.

### 5.2 Import Files

| **File**             | **Columns / Format**                                                                                                       | **Goes to**                       |
|----------------------|----------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| Task import CSV      | Title, Location, Description, Checklist, plus ID, Plan, X pos (%), Y pos (%) on a reconciliation or when pins are included | Tasks > Import Tasks             |
| Checklist setup CSV  | Checklist, Item                                                                                                            | Project Settings > Checklists    |
| Checklist paste file | ### <name> blocks. Part A lists checklists to create; Part B lists existing ones to verify.                             | Pasted into the checklist builder |
| Fieldwire Build Brief | Summary line and seven sections, one to two pages | Read and forwarded by a person |

Pins go in the task import. Never send a separate pin-only import.

### 5.3 Reconciliation

1.  Export the tasks and confirm which export it is.

2.  Match on **package + door mark**, never the mark alone, because marks repeat across packages.

3.  Sort every task into a bucket:

    - **Matched:** carry ID, Plan and the pins through, so the import updates the task in place.

    - **Not on the submittal:** use the non-submittal recipe and leave the checklist blank.

    - **Held:** leave it out and list it with the reason.

    - **No task:** check receiving and closeout first. On an Open Tasks export, most of these are closed. Real gaps go in a create-file with no ID column.

4.  On a Detailed export, audit the attached checklists. Group tasks by their checklist items, compare each group to its heading, and list wrong attachments by ID.

5.  Report the arithmetic: tasks, submittal openings, matched, not on the submittal, closed, and real gaps. The numbers have to reconcile.

6.  Watch for adjacent marks on opposite sides, such as one pinned with no schedule entry next to one scheduled with no pin. That's a typo signal. Flag the pair and don't merge them.

### 5.4 Revisions

1.  Export the current tasks. The pins come with the export.

2.  Update the affected checklist template **before** those tasks go active.

3.  Re-import the task CSV with the ID and coordinates intact. Don't re-pin by hand.

4.  Tasks that already carry the old checklist have it replaced by hand.

## 6. Validation / Quality Control

### 6.1 Before Import

- Every opening in the index has exactly one row, and the counts reconcile.

- Every Checklist value matches a checklist name character for character. A mismatch here is the #1 cause of failed imports.

- Every multi-package job uses prefixes, and no two packages share a checklist name.

- Every PDF was read to its last page.

- Every markup is either resolved in the files or listed in the Build Brief.

- No description contains hardware, and no checklist contains opening facts.

- Every checklist item includes its product number.

- Every electrified opening has the by-others, compatibility and verification lines.

- Held openings are listed, not imported, and no description is blank.

- Ratings are cross-checked, and every disagreement carries OPEN REVIEW:.

- Per-opening quantities divide evenly or are flagged.

- The supplier is named only if the document names it.

- Gaps are raised as questions, never filled with a guess.

### 6.2 Pin Check

Before importing, render one sheet with a marker at every computed pin. Confirm that one horizontal tag and one rotated tag are centered under their markers. Then import one row and check it in Fieldwire.

| **Test row result** | **Meaning**                           | **Action**                   |
|---------------------|---------------------------------------|------------------------------|
| On the tag          | The mapping is right                  | Import the rest              |
| Constant offset     | Fieldwire cropped or scaled the sheet | Rescale all pins in one pass |
| Scattered           | Fieldwire has a different file        | Stop                         |

### 6.3 Task Close-Out

A task can be closed only when all of these are true:

- every checklist item is complete

- no HOLD line is open

- the door is fully operational and latching

- any electrified opening has passed functional verification under power

- fire, life-safety and ADA are verified where they apply

- the required photos are uploaded

## 7. Boundaries / Exclusions

**Field crews and vendors may:**

- run the import from the prepared files

- work tasks and complete checklist items

- upload photos and add comments

- hand-pin the tasks listed on the pin exceptions list

**Field crews and vendors may not:**

- create tasks outside the import

- rename tasks

- edit, attach or remove checklists

- interpret schedules

- change the workflow

**Other boundaries:**

- On electrified openings, power, access control head-end, readers and low-voltage are by others. The by-others checklist line makes the field confirm that boundary rather than assume it.

- Held openings aren't imported. Non-submittal openings get a task but no checklist.

- For outside engagements, the deliverable is the import files and the workflow. No work is done inside a client's Fieldwire project unless the client is live on the call.

- Out of scope for this SOP: crew list builds (SOP: Crew List), the ops cadence (SOP: Ops Cadence), receiving and QA/QC gates, and keying schedules.

## 8. Reporting / Outputs

**Every run produces:**

- the task import CSV

- the checklist setup CSV and paste file

- the Fieldwire Build Brief (FBB)

**Build Brief structure.** A summary line, then seven sections — the same skeleton the QA/QC gate skill produces, so a client who gets both sees one document. Every row in sections 3–6 names an owner.

1. **Source & scope** — package, revision, approval status; changes from the previous revision
2. **Counts** — the reconciliation arithmetic, which must close
3. **Discrepancies** — wrong checklists attached (the manual-fix list, first); open review comments; openings not on the submittal, grouped by scope; architect-vs-submittal conflicts
4. **Held** — openings not imported, with the reason and who unblocks them
5. **Not pinned** — openings with no task, split into closed and real gaps; pins moved, on a sheet not in Fieldwire, on no sheet, or duplicated
6. **Owed by others** — what's still missing from the package, RFIs, by-others confirmations
7. **Deployment steps** — numbered, ending with what to walk

An empty section says "None — verified." A clean run is still a finding.

**Weekly progress (reported through the Ops Cadence):**

- Commercial openings: complete vs. total

- Unit doors: level sets complete vs. total

No per-task noise.

## 9. Summary Statement

Each opening gets one task, and each hardware heading gets one checklist. Tasks are pinned from the plan sheets and built by bulk import from the approved submittal.

Descriptions carry opening facts, and checklists carry hardware. Every run ends with a Build Brief. Nothing is called missing, short or complete until it has been tested against the paperwork.

### Revision Notes (v2.0)

- Structure now comes from the approved submittal, cross-checked against the architect schedule. It no longer comes from the tracker importer tab.

- Titles are now the door mark alone. [OPENING ID] - [HARDWARE SET] is retired.

- One itemized checklist per hardware heading replaces the generic functional checklist.

- Pins are derived from the plan sheets instead of placed by hand. Vendors hand-pin only the listed exceptions.

- New in this version: the description recipe, exceptions log (now the Build Brief), reconciliation, revisions, package prefixes, special cases and Fieldwire behaviors.

### Revision Notes (v2.1)

- The exceptions log is renamed and restructured as the Fieldwire Build Brief: a summary line and seven sections shared with the QA/QC gate skill, with an owner on every row.
