# SOP - Crew List from Fieldwire Task Report

Title: SOP: Crew List from Fieldwire Task Report

Author: Matthew Brown

Status: Draft

Applies To: Door & Hardware Installation Projects

Version: v1.1

Last Updated: 09/26/2026

## 1. Purpose

This SOP defines how a raw **Fieldwire task report** becomes a list a crew can work from on a phone. Each opening keeps only what the crew needs today. Older history stays in Fieldwire.

The goal is to:

- give the crew door numbers and direct instructions, and nothing else

- show every open issue next to its newest photo

- keep the set context that came in with the import

- cut a long report down to what actually gets read

- surface problems instead of burying them

## 2. Scope

Applies to any job with tasks in Fieldwire, whenever there is open work: punch walks, closeout, return trips and prep for a walk.

**Required inputs**

- A Fieldwire task report PDF, exported with comments and photos.

- A cutoff date, usually the date of the latest walk.

**Optional inputs**

- A scope filter: floor, area, status, or a list of door numbers.

- Who was on site on which days. This is needed for attribution (see 6.2).

## 3. Core Principles

1.  **The crew gets door numbers and direct instructions, not the reasoning.**

2.  **The list shows current state only. History stays in Fieldwire.**

3.  **The import comment always stays because it carries the set context.**

4.  **Every opening shows a photo or says it has none.**

5.  **Problems are flagged, never hidden.**

6.  **The list states facts, not blame.**

## 4. Definitions / Standards

### 4.1 Terms

- **Cutoff date:** the date that separates current from history. It's named at the top of the list. If none is given, use the newest comment date in the report and say so.

- **Import comment:** the first comment on each task. It carries the set context and any "confirm set" flag, and it's kept regardless of its date.

- **Issue comment:** a comment on or after the cutoff that calls out a problem. Acknowledgements that add nothing, like "ok" or "done," are left out.

- **Fallback photo:** the single most recent photo from before the cutoff. It's used only when an opening has no photo on or after the cutoff, and it's always labeled with its date.

### 4.2 What Each Opening Keeps

| **Keep**       | **Rule**                                                                   |
|----------------|----------------------------------------------------------------------------|
| Header         | Door number, location, set or checklist name, and status                   |
| Checklist      | Items as they currently stand, with open items marked                      |
| Import comment | Always, regardless of date                                                 |
| Issue comments | Only those on or after the cutoff                                          |
| Photos         | Those on or after the cutoff. If there are none, one fallback photo, dated |

Everything else comes out: older comments, older photos, and system log lines such as status changes and assignments.

### 4.3 Flags

| **Flag**           | **When it's set**                                                                    |
|--------------------|--------------------------------------------------------------------------------------|
| NO PHOTO           | The opening has no photo from any date                                               |
| CONFIRM SET        | The import comment asks to confirm the set. The flag goes at the top of that opening |
| CHECKLIST MISMATCH | The attached checklist doesn't match the set. Not visible in the task report, which doesn't print checklist names — caught by the checklist audit in SOP 01 |
| FAILED ITEM | Any checklist item carries Fieldwire's red failed mark |
| CLOSED WITH OPEN ITEMS | The task is Completed but an item is still open or failed |

## 5. Process / Workflow

1.  **Export the task report** from Fieldwire with comments and photos included, then apply the scope filter.

2.  **Set the cutoff date.**

3.  **Split the report into one block per task,** using the task header (door number, title and status line).

4.  **Tie each photo to its task and date** by page and position. The date comes from the caption or timestamp next to the photo.

5.  **Parse the comments** for author, date and text. The first comment in each block is the import comment.

6.  **Apply the keep rules** in 4.2.

7.  **Set the flags** in 4.3.

8.  **Build the list,** sorted by door number, or by walk order if one is given.

9.  **Validate** against Section 6, then send.

Tooling: the list is built by script (`fieldwire-crew-list`). PyMuPDF reads the text, the checkbox states from their fill colors, and the photos with their positions; pdftotext makes an independent count to check the parse against; ReportLab builds the PDF. A checkbox color the script doesn't recognize stops the run.

## 6. Validation / Quality Control

### 6.1 Before Sending

- The number of openings on the list equals the number in the report after filtering.

- Three openings are spot-checked against the source PDF: checklist, comments and photos.

- Every photo on the list is dated.

- Every opening either has a photo or is flagged NO PHOTO.

- The counts are reported to the ops lead: openings, open checklist items, openings using a fallback photo, and flagged openings.

### 6.2 Attribution

Fieldwire accounts are sometimes shared. Before naming who wrote a comment in any summary, confirm who was on site that day. If that isn't known, keep the author exactly as Fieldwire shows it and don't infer anything.

## 7. Boundaries / Exclusions

- The list is a working copy, not a system of record. Fieldwire remains the record, and nothing in Fieldwire is edited or deleted.

- The list doesn't create, close or re-scope tasks. Scope questions go through reconciliation (SOP 01).

- The list shows flags but doesn't resolve them.

- The list contains no commentary, reasoning or fault.

- Crews get the list. The counts and flag summary go to the ops lead.

## 8. Reporting / Outputs

**PDF (default)**

- Letter size with 0.75" margins, laid out to read on a phone.

- A title line with the job, the cutoff date and the opening count.

- One section per opening: the door number in large type, then the checklist, comments, and photos scaled to page width.

- Plain text, with no commentary.

**WhatsApp text (on request)**

- Door numbers, each with a one-line instruction. No photos.

**Ops lead summary**

- The counts from 6.1 and the list of flagged openings.

## 9. Summary Statement

The crew list is the Fieldwire task report cut down to what the crew needs today. Each opening keeps its checklist, its import comment, its newest issue comments and its newest photos.

Everything older stays in Fieldwire. The crew gets door numbers and direct instructions.

### Revision Notes (v1.1)

- Added the FAILED ITEM and CLOSED WITH OPEN ITEMS flags. Fieldwire has a fourth checklist state, failed, that an earlier parser merged into the line above it; the script now fails loudly on any state it doesn't recognize.
- CHECKLIST MISMATCH is noted as caught upstream, since the task report doesn't print checklist names.
- Tooling updated to match the packaged script.
