# fieldwire-crew-list — changes

## v1.2 (2026-09-30) — after the enforcement-layer audit
Each line names the audit finding it closes and the case in `tests/test_crew_list.py` that proves it.
- Checkbox with no text within 5 pt aborts; a checklist line with no checkbox aborts unless it is a wrapped continuation (the line above reached the column edge). Closes finding 1 (an open item rendered done with every check green). Cases `box-offset`, `box-missing`, `box-missing-first`, `wrapped-item`.
- Checkbox drawings counted independently must equal checklist items parsed (third path). Finding 1's counts now have something to compare against. Baseline asserts `125 = 125`.
- Export type read from the header and stated in the summary, with the consequence spelled out when closed tasks cannot be present. Finding 2. Baseline asserts `Export | Open Tasks`.
- Completed and Verified are both closed; the flag carries the status word. Finding 3. Case `verified-open`.
- "done" / "installed" / "complete" are no longer dropped as acknowledgements: on a task with open items they raise `DONE CLAIMED, N ITEMS OPEN` and are shown. Finding 6. Case `done-claim`.
- The year comes from each task's Created line and rolls forward when a comment's month drops. Finding 7. Case `year-boundary`.
- Photos are selected by column (left-aligned with the message text), not width; skipped images are counted in the summary. Finding 8. Case `narrow-photo`.
- Set context falls back to `Set <name>` in the import comment or description when no `#set_` tag exists. Finding 12. Case `no-set-tag`.
- `RECEIVING GATE OPEN N DAYS` on a receiving-gate task left open past `--gate-days`. Not in the audit: the one gate that failed in practice, now checked in line. Baseline fixture.
- Golden expectations (`tests/expected_flags.json`) and a regression suite that fails on any difference. Finding 10. Run against v1.1, seven of the eleven cases produce wrong output with no error (`box-offset`, `box-missing`, `verified-open`, `done-claim`, `narrow-photo`, `year-boundary`, `no-set-tag`); v1.1 aborts correctly on `color-shift` and `box-missing-first` and handles `wrapped-item`.
- `requirements.txt` and a preflight that names the missing package or binary. Finding 11.

## v1.1 — generalized from the project-specific parser; synthetic fixture; unknown-fill abort; pdftotext second path.
