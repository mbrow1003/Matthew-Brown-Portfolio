# fieldwire-hardware-import — changes

## v2.3 (2026-09-30) — after the enforcement-layer audit
- `scripts/validate_import.py`: an import gate that runs before Fieldwire sees the files. Fails on a checklist name off by whitespace or case, a blank description, a pin outside 0–100 or on one axis only, blank or repeated IDs, a `NOT IN HW SUBMITTAL` row with a checklist or without `#hw-tbd`, an Install line with no quantity or no product number, and a heading used both prefixed and unprefixed. Warns on duplicate marks within a package (verified shells are intentional), unprefixed names on a multi-package job, quantities flagged `total`, descriptions off-recipe, and unreferenced checklists. On a file from `fieldwire-qaqc-gate` it skips the hardware recipe and applies the rest. `tests/test_validate_import.py` proves it on a clean pair and a broken pair; the demo project's CSVs pass it with no findings.
- `scripts/extract_tag_pins.py`: near-miss reporting (words shaped like a mark that fail `--pattern`), `--page N` with a refusal on multi-page sheet PDFs, an explicit abort on a sheet with no text layer, and a preflight that names a missing `pdftotext`. `--tag-regex` is accepted as an alias of `--pattern`.
- `requirements.txt`.

## v2.2 — exceptions log renamed and restructured as the Fieldwire Build Brief (summary line, seven sections, owner on every row); `--pattern` for the mark convention; live-job example marks and project references genericized.
## v2.1 — cut-sheet redlines, package-prefix namespacing, exceptions log on every run, pin extraction via `pdftotext -bbox`.
