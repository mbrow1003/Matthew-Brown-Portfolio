# Demo Mode

For building a sanitized project to show a prospect who asked for examples. Read this **before** building the unit list. It changes what goes in the files and adds a fourth output.

## Why a demo instead of a screenshot

Client projects are never shown to other clients. That rule is the sales pitch — a prospect who handles designers' and GCs' drawings all day understands it instantly. The demo replaces the screenshot: a small, fictional project the prospect can click through in their own Fieldwire login, built in their trade's vocabulary.

## Rules

1. **Nothing real.** No client name, project name, address, person, drawing, or mark from any real job. Invent all of it. Project name should be obviously generic (`Demo — Hotel Lobby Millwork`, `Demo — Clinic Casework L2`).
2. **Their trade, their unit.** If you don't yet know what their unit is, pick the most common one from the trade reference and say in the walkthrough note that it's a guess.
3. **Small.** 12–15 units across 4–6 unit types — enough checklists to show the gate varies by type, not so many that building them eats the demo. It's a demo, not a delivery.
4. **Mid-project.** A demo where everything is at zero shows nothing. Set a realistic spread of gate states so the board reads like a live job.
5. **One seeded deviation.** This is the whole demo. One unit where the field dim came back off the drawing, flagged, held, not released, with the disposition pending. It's the remake that didn't happen. Everything else is structure; this is the reason to pay.
6. **One unit fully through.** So "done" is visible — every line checked, `ACCEPTED` with a name and date, Category `ACCEPTED`, Status `Completed`.
7. **Invite, don't send.** Add the prospect as a guest to the demo project. Screenshots and PDFs are the fallback, not the plan.

## Building it

**Unit list** — invent it. The reference build (hotel lobby, 14 units, 5 types):

| Mark | Type | Location | Sheet rev | Phase |
|---|---|---|---|---|
| RD-01 | Reception desk | Lobby | SD-01 rev 1 | HOLD (seeded deviation) |
| BD-01 | Bar die | Lobby bar | SD-02 rev 2 | RELEASED TO SHOP |
| WP-01…WP-05 | Wall panel | Lobby | SD-04 rev 2 | 2 FIELD VERIFICATION, 1 RELEASED, 1 IN SHOP, 1 INSTALLED |
| CT-01, CT-02 | Countertop | Lobby bar, Lobby | SD-02 r2, SD-01 r1 | FIELD VERIFICATION (templates pending) |
| V-101…V-105 | Vanity | Rooms 101–105 | SD-06 rev 1 | 1 ACCEPTED, 2 DELIVERED, 1 IN SHOP, 1 FIELD VERIFICATION |

Adjust to the prospect's work. A restaurant gets a host stand and banquette; a clinic gets nurse stations and exam casework.

**Task import** — per `format-spec.md`. Category and Status set per unit to produce the spread above. Descriptions carry invented but plausible dims and finishes.

**Checklist setup** — one gate per unit type present, from `millwork.md`. Four or five checklists.

**Checklist item states** — the CSV import does not set item completion. After import, check off lines manually to match each unit's phase. Fifteen units, a few minutes. The seeded-deviation unit gets its `FIELD:` lines checked through the compare line, then stops, with the `HOLD:` line visible and unchecked.

**The seeded deviation, written out:**

- Description flag: `HOLD: field width 142-1/4" vs 144" drawn`
- Task comment (add after import): `Field W 142-1/4" measured 9/8 by JT. Drawing SD-01 rev 1 shows 144". Delta -1-3/4". Disposition pending — revise drawing or accept with filler? Not released.`
- Category `HOLD`, Status `Priority 1`
- Discrepancies row in the Build Brief with all seven columns.

**Build Brief** — real format, real sections, populated from the demo. The prospect should see what the brief looks like on a live job; it is the thing they are buying.

## OUTPUT 4 — Walkthrough note

A short markdown note the prospect reads before clicking around. Under 200 words. Contents, in order:

1. What this is: a fictional project in their trade, built the way a real one would be.
2. What to look at first: the held unit (name it), then the accepted unit, then one in the middle.
3. The one sentence on the gate: release and acceptance are signed by someone other than the person whose work they verify.
4. The invitation to correct: "This is my read of how your work flows. Tell me where the unit or the order is wrong for your shop."
5. Nothing about price.

## Self-check additions for demo mode

- Grep the four outputs for any real client, project, person, or address. Zero hits.
- Exactly one unit in `HOLD` with a fully written deviation.
- Exactly one unit `ACCEPTED` / `Completed`.
- Category spread covers at least four distinct phases.
- Walkthrough note names the held unit and ends with the invitation to correct.
