# Case Notes — Pattern Level

Real engagements, described without client files, names, or project identifiers. Numbers are as reported at the time; each can be discussed in detail in conversation.

## 1. Commercial door & hardware subcontractor — Nashville (Nov 2024 – present)

**Situation.** Fieldwire had been purchased and was sitting unused. Field crews ran off printed schedules; material shortages were reported from the field with no way to verify them against what had actually shipped.

**What was built.**
- Fieldwire taken from an unused license to the operational system of record across multiple concurrent commercial projects — 1,000+ tracked openings, each a pinned task carrying hardware set, size, rating, door/frame type, and handing, with a checklist per hardware set.
- Automated submittal-to-task tooling: a supplier's hardware submittal (door index plus grouped schedule) parsed into import-ready CSVs. Per-package setup went from a full day of manual formatting to minutes. Later packaged as a reusable skill (see `01_Skills`).
- Receiving and closeout QA/QC gates: supplier bills of lading, packing slips, and production tickets reconciled against field shortage claims before any reorder. Verification caught roughly $7,500 in false shortage claims.
- A weekly GC communication cadence and a monthly ops review reporting phase, milestones, blockers, and decisions needed at owner level.
- Structured change-order and T&M tracking that captured $15K+ in additional revenue on a single project.

**Proof points.**
- First 30 days of the receiving gate: the first seven field shortage claims all failed verification — material was on site each time. The first genuine supplier miss surfaced through reconciliation, not a field report.
- Day-one mobilization walk on one project: every bathroom opening came in roughly half an inch under clear height. All photographed and blocked before delivery; the GC requested the list to support a change order.
- How shortage claims actually resolve: six closers reported missing had all shipped — the field's visual sort had misread two — and twelve reported surplus were tagged to openings. On another job, a three-floor walk found zero true short-ships; the one real gap was a hardware heading the supplier had never released. Each claim resolves to a driver on the ledger — false shortage, short, scope, waste — and each driver has a different payer. Root-cause before escalating.
- Closeout diagnosis: an exit device that looked intact had never latched; a dead electrified lock traced from a 0 VDC reading to a missing door position switch. Evidence first, then the call.

**What it taught.** Coordination, not labor, was the bottleneck. And a QA/QC gate has no value unless someone runs it — the systems were the easy part; the discipline was the product.

## 2. High school renovation, Southeast US — referred outside engagement (Sep 2026)

**Situation.** A door and hardware installer, referred by a peer, had set up a Fieldwire project eight months earlier and left it at zero: 199 tasks pinned, none titled, no checklists, crews running off printouts taped to doors. He suspected openings were missing but couldn't say which.

**What was found, from the approved-as-noted hardware submittal and the client's own project, before any build.**
- 209 door openings on the submittal's opening list; 199 pinned in Fieldwire — a 10-opening gap, quantified for the first time.
- 3 openings referencing hardware sets absent from the package entirely (specialty door sets carried on a separate spec section).
- 206 openings under 86 hardware headings; 19 rated openings.
- Reviewer changes buried in RFI responses and heading markups that had never reached the field: one exterior pair moved to a different hardware set; power supplies denied on five sets (monitored-only); every adhesive-mount protection plate changed to screw-mount; lever design changed on all exit devices; silencers added to roughly half the building.
- Two plan sheets carrying a post-bid architect's supplemental instruction — the likeliest source of openings the architect added that the supplier never scheduled.

**What was proposed.** A scoped, fixed-fee build: titles and descriptions on all 199 pins, 86 heading checklists built and attached, the 10 missing openings pinned, and a Fieldwire Build Brief listing every reviewer change, every held opening, and who owed the next answer. Before work started, the client's scope turned out to be 80% installed rather than 20%. The proposal was re-scoped for closeout, and the engagement hasn't gone forward.

**What it taught.** The exceptions are the product. The CSVs are how they get executed.

## 3. Architectural millwork fabricator — referred inquiry (Sep 2026)

A fabricator using Fieldwire only to log field dimensions asked to see what a deeper build looked like. Rather than show another client's project, a sanitized demo was built in his trade's vocabulary (see `02_Demo_Project`): a fictional hotel lobby, 14 units, five gate checklists with release and acceptance sign-offs separated from the people who do the work, and one seeded field deviation caught before release to the shop.


## 4. Implementation runs — Fieldwire builds from hardware submittals (2025–2026)

Each run: a supplier's hardware submittal parsed into task and checklist imports, validated, and deployed. Projects described by type and size only.

- **Institutional facility, Phase 2** — 461 tasks, 68 checklists (50 new, 18 verification), 440 pinned from four composite plan sheets. Caught 27 tasks carrying the wrong checklist, 84 openings outside the submittal classified by scope, two architect-versus-submittal rating conflicts, one missing door, and four floor corrections. Of 48 tasks reported missing mid-phase, 39 were Phase 1 doors already closed. Replaced roughly a week of manual setup.
- **Same facility, Phase 1** — 39 openings, an 18-heading checklist set, nine electrified openings flagged. Output reordered to match the live export row for row; one gap and one location mismatch flagged.
- **Healthcare tenant improvement** — 140 tasks, 35 checklists, 256 checklist lines. Four scope-changing redlines found only in cut sheets, not in the schedule. Package-prefix namespacing introduced to stop checklist collisions across floors.
- **Vocational campus** — 123 tasks and 947 checklist items live from day one, with a receiving-gate task issued at import. Later, a 447-item GC punch list reconciled against the record: 164 done, 272 open, 7 failed, 4 N/A. The record was stale; the building wasn't.

**Delivery model on outside engagements.** Import package and pin coordinates delivered as files; a live onboarding session; no work inside a client's instance unless the client is live on the call.

## 5. Working rules that came out of it

- **Adoption.** A platform that captures everything and enforces nothing is a personal database. When one person is the only write path, the system of record is that person. The gates exist to make the write path a team habit.
- **Authority.** Scope and money run through the customer channel; rules and approvals run through the site-authority channel. Never negotiate scope with the party that controls the site, or site rules with the party that controls the money.
- **Verification before belief.** A field claim is a hypothesis. Walk it, photograph it, reconcile it against the paperwork, then act. Logging the claims that checked out — not only the ones that didn't — is what makes the discrepancy rate a real number.

## 6. Reconciliation and triage — how findings get written

Pattern level, drawn from real job documents that stay private. Each shows a way of turning a messy field situation into something a GC, supplier, or owner can act on.

- **Verification has a shelf life.** A GC punch walk a month after a signed-off walk showed 8 openings previously marked Good now failing. Five more had been marked Skipped the first time, so the second walk was their first assessment, not a regression. Two items belonged to other trades — storefront and access control — and were routed out. The reconciliation recommended confirming the current cause before any of it was assigned as rework.
- **As-built beats the take-off.** On a residential floor-set reconciliation, net need came from physical openings and physical doors on site: 13 openings missing a door, 7 covered by reallocating staged doors, 6 sets to reorder. The take-off could never have surfaced the need — it never specified that door type at the affected openings, and the doors it did specify arrived as surplus.
- **Hypothesis, then the test that confirms it.** Seventeen bypass tracks reported missing were framed as a field size-matching gap rather than a vendor short-ship: size-specific 60-inch kits cut down for 48-inch openings. The write-up named the count that would prove it — unopened 48-inch kits still on site — and split the outcome in two: a reorder for the short 60-inch tracks, and remediation for 48-inch openings running on cut track.
- **Status that separates material from labor.** An executive page compared two walks: 30 open, then 19 — 12 cleared in 13 days, every one walk-verified, and one apparent clearance caught the same day as a misfiled comment. The remaining 19 were gated on two material threads, not labor, and the page said so.
- **Pilot findings, triaged by root cause.** A mockup walk logged nine conditions, each with what was observed, the governing reference, and the direction requested. Four traced to one root — frames prepped for residential hardware and field-modified for commercial strikes. One was flagged as life-safety rather than punch. No corrective work was done without written direction, and the log noted that if the mockup product differed from production, it shouldn't set the acceptance standard.
- **Schedule change management.** Two GC schedule updates diffed across 68 door and hardware control points — 66 had moved — and sorted into four tiers: escalate procurement now (one area pulled about four months earlier), a residential acceleration of three to four weeks, hotel relief of one to two weeks, and two amenity-room sequencing conflicts carried forward unresolved — the same two described in the README's AI audit.
- **Commercial revisions that show their work.** A quote revision exhibit stated its verification status at the top — which counts were checked line by line, which carried forward as approximate — separated priced deltas from items needing a rate that didn't exist yet, and listed open questions for the contracting party instead of pricing around them.
