# Field QA/QC Kit — Three Gates and a Filter

Every opening passes through the same checks: a recon before mobilization, a receiving gate at every delivery, and a closeout gate before anything is called done. Each produces a timestamped, photo-backed record, so a "missing" call or a reopened punch item can't be relitigated later. The receiving and closeout checklists import directly into Fieldwire from `Gate_Checklists.csv`.

The rule under all of it: **the person who did the work doesn't verify it.** A gate that gets rescued stops being a gate.

---

## Gate 0 — Site recon (before mobilization)

A walk to read starting conditions — see, photograph, note, route. Not a walk to fix anything. A condition caught at door one that would compound across five hundred is the highest-leverage thing this kit does.

**Frames**
- Frame type per area — hollow metal, welded, knockdown, wood, storefront
- Welded vs. field-assembled
- **Set before or after drywall and openings were built out?** The most common source of downstream fit problems.
- Condition — plumb, square, damaged, racked
- Painted vs. unpainted (unpainted blocks weatherstripping later)
- Anchoring and grouting correct
- Rated frames: labels present where required

**Floors**
- Finish type per area — concrete, VCT, tile, carpet, sealed. Drives undercut and threshold needs.
- Flatness and level — high spots cause drag and latching failures later
- Flooring in before or after door install? (sequencing risk)
- Threshold needs, and the floor's condition to receive them

**Openings and site**
- Which trades are ahead of and behind the door scope right now
- Openings built to plan vs. modified in the field
- Wall conditions — backing, bracing, anything that fouls install
- Access and staging — where material can sit safely for the full flow
- Power and lift access for upper floors

**Hardware and electrified**
- Electrified openings: is the power and access-control rough-in there, or coordinated?
- Card readers and access control: confirm the scope boundary in writing
- **Auto-operators — in scope or not? Pin it in writing now**, before it becomes a free add
- Electric strikes, position switches, security hardware — trade coordination
- Rated sets — labeling and compliance per opening

**GC and coordination**
- GC PM, and their walk and verification cadence
- Their door schedule vs. the Fieldwire build — any divergence to reconcile now
- Change-order and RFI process on this job

---

## Gate 1 — Receiving (every delivery)

Attach the RECEIVING GATE checklist to a `Receiving — <date / BOL #>` task at every drop.

- Confirm PO # and job # match the BOL / packing slip
- Count pieces against the slip — not from memory
- Photograph the staged load, location-tagged
- Log any discrepancy at receipt, by type:
  - On the slip, not in the load → **short-ship** → vendor claim within 48 hours
  - Wrong or substituted item → **quarantine**, do not install
  - Damaged → photograph before signing
- Stage by heading or opening where possible
- Sign: name + date

## Gate 2 — Closeout (every opening)

A second checklist on every opening task. The opening is not done until this reads 100%.

- All heading-checklist hardware installed and operating
- Electrified: reader and power by others confirmed, operation verified
- Rated opening: fire label intact and visible
- Photograph of the finished opening (both leaves on pairs)
- Any punch item logged with photo + owner
- Sign: name + date

**Verification has a shelf life.** The check that counts is the one nearest closeout, not the first one that passed. Other trades keep working around a door after it's signed off.

---

## The missing-material filter

Run before anything is reported missing. No "missing" report leaves the field until all three are answered.

1. **Is it on the receiving log?**
   Yes → it's on site. Locate it. A staging gap, not a shortage. **Stop.**
   No → go to 2.
2. **Is it on the BOL or the submittal?**
   On the submittal, not received → real short-ship → vendor claim.
   Not on the submittal → a take-off gap. Never in scope to order. Not a shortage and not a claim — route it for a reorder decision.
3. **Is it a field-process gap?** Cut-to-fit, wrong size pulled, install sequence.
   Yes → a field fix, not a material order.

**Only one path spends money:** on the submittal, not received, and not a field gap. Everything else closes without a reorder or an expedite.

---

## Operating notes

- The gate holds only if leads enforce it: no closeout checklist, not complete. No exceptions.
- Missing reports route through the filter, not raw to a group chat. The filter *is* the report.
- Receiving discrepancies feed the BOL and production-ticket reconciliation — the field front end to the same numbers the office already pulls.
- Every claim that gets walked goes in the ledger (`QC_Discrepancy_Ledger_Demo.xlsx`), including the ones that held.
