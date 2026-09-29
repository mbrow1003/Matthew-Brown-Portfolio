# Millwork / Casework Gate

For architectural millwork fabricators and installers: casework, countertops, wall panels, reception and bar dies, vanities, shelving, trim. Read this when the trade is millwork; it says what the unit is, what the gate lines are per unit type, and where millwork jobs actually fail.

## Where millwork fails

The expensive failure is not a wrong part. It's a piece **built to an unverified or stale dimension.** A casework run cut to the drawing when the field is an inch and three quarters shorter is a remake — material, shop time, schedule, and a second trip. The gate exists to make release-to-shop a decision someone signs on a named rev, not a thing that happens because the drawing was done.

Second failure: **revision drift.** Shop cuts to rev 2, architect issued rev 3 last week, nobody told the shop. The compare line naming the rev is what catches this.

Third: **adjacent conditions.** Blocking not in the wall, MEP rough-in landing in the cabinet, floor out of level at a long run. These are by-others and they belong on the gate as `FIELD:` verification lines, with a `HOLD:` if unconfirmed.

## What the unit is

Ask. Fabricators differ. Common answers:

| Unit | Mark convention | Notes |
|---|---|---|
| Casework run | `C-2.1`, `BC-04`, room + elevation | Most common. A run is one unit even if it's several boxes. |
| Countertop | `CT-04` | Separate unit from the cabinets below it — different gate (template), often a different material or vendor. |
| Wall panel / paneling elevation | `WP-03` | One elevation = one unit. |
| Reception / nurse station / bar die | `RD-01`, `NS-02`, `BD-01` | Single high-value unit; full gate. |
| Vanity | `V-104` (room number) | Usually one per room; cabinet and top may be one unit or two. |
| Shelving / closet | `SH-12` | Often no field dim beyond a width check. |
| Trim / base / crown | by room or by run | Thin gate; often tracked at the room level, not per piece. |

If the fabricator tracks by **shop ticket**, the ticket number is the mark and the ticket is the unit. If by **room**, the room is the unit and the checklist lists the items in it.

## Gate per unit type

Start from the generic gate in `format-spec.md` and trim.

### Casework run (`<PKG>-BASE CABINET`, `<PKG>-UPPER CABINET`, `<PKG>-TALL CABINET`)
Full gate. Field dims: overall W, H to underside of any obstruction, D to any clearance constraint. Add:
- `FIELD: Verify floor level along the run — note high point`
- `FIELD: Verify MEP rough-in locations against cabinet layout (sink, outlets, supply/waste)`
- `SHOP: Hardware installed per schedule — slides, hinges, pulls (name the spec in the checklist name if it varies)`

### Countertop (`<PKG>-COUNTERTOP`)
Template replaces field dim:
- `FIELD: Base cabinets installed and level before template`
- `FIELD: Template taken — attach photo of template on cabinets`
- `FIELD: Sink / cooktop / cutouts marked on template`
- `GATE: RELEASED TO FAB on template dated __ — PM name + date`
- Drop the generic dim-compare line; the template *is* the compare.
- `SITE: Seams located per approved drawing`

### Wall panel / paneling (`<PKG>-WALL PANEL`)
- Field dims: W, H, plus any penetrations (outlets, switches, thermostats).
- `FIELD: Verify blocking in wall at panel cleat locations — HOLD if not confirmed`
- `FIELD: Verify wall plumb / flat — note out-of-plane`
- `SITE: Reveals consistent per drawing`

### Reception desk / station / bar die (`<PKG>-RECEPTION DESK`, `<PKG>-BAR DIE`)
Full gate plus:
- `FIELD: Verify floor box / conduit stub locations against desk layout`
- `FIELD: Verify ADA transaction height and knee clearance per drawing`
- `SHOP: Mock-up or dry fit of multi-section units before finish`
- `SITE: Sections joined, seams aligned, top installed`

### Vanity (`<PKG>-VANITY`)
- Field dims: W between walls, H, plumbing rough-in location.
- `FIELD: Verify supply / waste rough-in centerline against vanity layout`
- If the top is a separate vendor, split into `-VANITY` and `-VANITY TOP` with the template gate on the top.

### Shelving / closet (`<PKG>-SHELVING`)
Thin gate: one field width check, release, fabricate, install, accept. Don't pad it.

### Trim (`<PKG>-TRIM`)
Room-level. Lines: profile verified against sample, quantity per room verified, installed, caulked/filled, accepted. No field dim gate.

## Standing HOLD lines

Two conditions recur on every millwork job and belong on the type checklist as standing `HOLD:` lines, not just in the description:

- **Wall panels:** `HOLD: blocking not confirmed - confirm before RELEASED`. Blocking is by others and is the single most common reason a panel can't hang.
- **Countertops:** `HOLD: template pending - confirm before SHOP cut`. The template is the release condition; the line makes it visible on every top.

Other unit types carry `HOLD:` only in the description flag and Category when a specific condition is open. Don't add standing holds to casework runs, desks, or vanities — those conditions vary by job and a standing line becomes noise.

## Casework hardware

If a hardware schedule exists (slides, hinges, pulls, locks by mark), the `SHOP: Hardware installed per schedule` line should name the schedule. If hardware varies enough by unit that one line can't cover it, fork the checklist by hardware group — same logic as forking by gate, not by size.

## Reading a millwork package

- **Shop drawings are the fabricator's own.** Sheet index is the unit list if no schedule exists. One elevation may yield several marked units; read the callouts.
- **Architect's casework schedule** (often an `A-6xx` sheet or a schedule on the interior elevations) is the issued unit list when it exists. Reconcile shop marks against it.
- **Revisions are on the title block.** Record sheet + rev per unit. If the package has mixed revs, the Build Brief's Discrepancies section must carry the rev mismatches.
- **Finish schedules** live on a separate sheet or in the spec. Pull the finish onto the description; put the sample-verification line in `SHOP:`.
- **Field dims arrive as photos and notes.** In a live project these land on the task as comments and photos; the checklist line is what makes them a gate instead of a note.

## Deviation dispositions

Every deviation resolves to one of three, named in the Build Brief and on the task:

1. **Revise drawing** — new rev issued; task description updated to the new rev; compare line re-run.
2. **Correct condition by others** — framing, blocking, MEP moved; `HOLD:` until confirmed, then re-measure.
3. **Accept as-is** — the deviation is absorbed (scribe, filler, reveal); who accepted it is named.

"We'll make it work" is not a disposition.
