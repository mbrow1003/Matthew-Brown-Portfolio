# Demo — Hotel Lobby Millwork L1 — Fieldwire Build Brief (FBB) & Deployment Steps

**14 units · 1 held · 5 not released · 0 rev mismatches · 4 items owed by others.** Built from shop drawing set SD-01 through SD-06 (fictional). Brief rev 1, 9/8.

## 1. Source & scope

Package `L1` — Level 1 lobby, bar, and guest room vanities. Shop drawings SD-01 r1 (reception), SD-02 r2 (bar), SD-04 r2 (wall panels), SD-06 r1 (vanities). All sheets current per the sheet index.

This brief reconciles the shop drawing set against the Fieldwire project. No architectural cross-check was performed.

Faithful to the package as issued at these revs; not warranted against later revisions or field conditions. First issue — no prior brief.

Every mark, dimension, and name in this brief is invented for demonstration.

## 2. Counts

| | Count |
|---|---|
| Units on list | 14 |
| Task rows in import | 14 |
| Pinned at import | 14 (from the plan's text layer) |
| Held | 1 |
| Unpinned | 0 |

14 = 14. Reconciles.

## 3. Discrepancies

| Mark(s) | Finding | Source says | Found / changed to | Disposition | Owner | Status |
|---|---|---|---|---|---|---|
| RD-01 | Field width short of drawing | 144" (SD-01 r1) | 142-1/4" measured 9/8 by JT; delta −1-3/4" | Pending — revise drawing to 142-1/4" or accept with 7/8" filler each end | PM | HOLD — not released |

Multi-section unit with a templated solid surface top (CT-02). Building to 144" is a field cut on a finished unit or a remake. The gate stopped it at the compare line.

## 4. Held

| Mark | Reason | Owner | Unblocks when |
|---|---|---|---|
| RD-01 | Deviation above, disposition pending | PM | Disposition chosen and rev issued or filler accepted in writing |
| WP-01 | Field dims captured; blocking at cleat locations not confirmed | Framing sub | Blocking confirmed on site, photo on task |
| WP-02 | Field dims captured; blocking at cleat locations not confirmed | Framing sub | Blocking confirmed on site, photo on task |
| CT-01 | Template pending — BD-01 not yet installed | Own crew | BD-01 installed and level |
| CT-02 | Template pending — RD-01 held | PM | RD-01 released and installed |
| V-105 | ADA vanity; rough-in centerline not verified against SD-06 | Plumbing | Centerline verified, photo on task |

## 5. Not pinned

None — verified. All 14 units carry a pin extracted from the plan's text layer. Every mark also appears in the title-block millwork schedule (RD-01 and BD-01 twice more in its location column); those duplicates were flagged by the extractor and excluded by region, leaving one on-plan pin per mark. Overlay checked before import.

## 6. Owed by others

| Item | Affects | Owner | Unblocks |
|---|---|---|---|
| Blocking in wall at panel cleats | WP-01, WP-02 | Framing sub | Release of both panels |
| Floor box and conduit stub location at desk | RD-01 | Electrical | Release of RD-01 (with disposition) |
| Supply / waste rough-in centerline, Room 105 | V-105 | Plumbing | Release of V-105 |
| Bar die install before top template | CT-01 | Own crew — sequencing | Template for CT-01 |

## 7. Deployment steps

1. Project Settings → Manage Checklists: create the five `L1-` checklists from `Fieldwire_Checklist_Setup.csv`, names character-for-character.
2. Plans: upload `A1-1_LEVEL_1_FLOOR_PLAN_DEMO.pdf` and confirm the plan name reads `A1.1` exactly — rename if not. The import's `Plan` column matches on it.
3. Tasks → Import Tasks: import **one row first** (RD-01) and confirm the pin lands on its tag. On the tag → import the remaining 13. Constant offset → Fieldwire cropped the sheet; stop and rescale. Scattered → wrong file; stop.
4. Check off checklist lines per unit to match its Category (see walkthrough note).
5. Add the RD-01 task comment: `Field W 142-1/4" measured 9/8 by JT. SD-01 rev 1 shows 144". Delta -1-3/4". Disposition pending — revise drawing or accept with filler? Not released.`
6. Walk: RD-01 (held), V-101 (accepted), WP-04 (in shop).
