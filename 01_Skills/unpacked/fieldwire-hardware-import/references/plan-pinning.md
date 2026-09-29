# Pinning Tasks From Plan Sheets

Fieldwire pins are `X pos (%)` / `Y pos (%)` of the plan image, origin top-left. If the plan sheets came out of Revit (or any CAD export with a text layer), every door tag is a text object with a page position. Extract it, convert to percent, and 400+ tasks pin in one import. No visual guesswork, no hand placement.

Proven on a 461-opening institutional project: 440 of 461 open tasks pinned from four composite sheets, verified dead-center on the tag bubble.

## Contents

1. What to ask for
2. Extraction
3. Matching tasks to tags
4. Verification (mandatory)
5. The four exception buckets
6. Import mechanics

---

## 1. What to ask for

The **exact sheet files uploaded to Fieldwire** - not a re-export of the same sheet. Percent is relative to the page as Fieldwire rendered it; a crop, rotation, or different page size breaks the mapping.

Confirm the plan names from the task export's `Plan` column and use them verbatim in the import.

If the sheets are flattened rasters (scanned, or plotted to image), this does not work. Say so; do not attempt OCR positioning.

## 2. Extraction

Use `scripts/extract_tag_pins.py`. It wraps `pdftotext -bbox`, which is the extractor that matters:

- **pdfplumber misses rotated tags.** Tags on vertical walls are rotated 90° (char matrix `0,1,-1,0`). pdfplumber returns them as loose characters that `extract_words` drops or mangles. On one project it found 66 of 171 tags on a first-floor sheet. `pdftotext -bbox` returns rotated words whole.
- **Concatenated tags.** Adjacent tags on the sheet come out as one word (`2101A2102A`). The script splits them along the word box - horizontally for upright, vertically for rotated.
- **Page size.** Read from the bbox XML `<page width height>`. Percent = coordinate / page dimension × 100.

The script writes `tags.json` keyed by plan name, and reports duplicates (a mark tagged twice on one sheet).

## 3. Matching tasks to tags

Parse the door mark out of each task's title (the person's title convention may be `Door <mark> - <room>` - preserve it, don't rewrite to a bare mark). Then, per task:

1. Look for the mark on the sheet the task is currently assigned to (`Plan` column). Found → pin.
2. Not found there → look on every other sheet Fieldwire has. Found → pin **and change `Plan`** in the import row. The task was on the wrong floor.
3. Found only on a sheet Fieldwire does not have → list it; the person uploads that sheet or pins by hand.
4. Not on any sheet → list it. Roof doors, overhead coilings, vestibule doors tagged only on enlarged plans, and doors the architect never tagged all land here.

## 4. Verification (mandatory)

Before presenting, rasterize one sheet at low resolution (`pdftoppm -r 40`), draw a marker at every computed position, and look at it. Then crop at full resolution around one horizontal tag and one rotated tag and confirm the marker is centered on the tag bubble. Do not skip this - it is the only thing that catches an origin or axis error before 400 pins land in the wrong place.

Then tell the person to **import one row first** and check the pin in Fieldwire. Three outcomes:

- On the tag → import the rest.
- Constant offset → scale mismatch (Fieldwire cropped the sheet). Get the rendered image dimensions and rescale in one pass.
- Scattered → Fieldwire has a different file than the one in hand. Stop.

## 5. The four exception buckets

Report counts for all four in the pin log, with IDs and marks:

| Bucket | What it means | What to do |
|---|---|---|
| Pinned, moved | mark found on a different sheet than the task's plan | import row carries the corrected `Plan` |
| Sheet not in Fieldwire | tagged only on a sheet the project lacks (ALT sheets, enlarged plans) | list; upload the sheet or hand-pin |
| Not on any sheet | roof, OHC, untagged, vestibule-only-on-enlarged-plan | list; hand-pin |
| Duplicate tag | same mark, two bubbles on one sheet | pin to the first, flag for a site check |

Rows that cannot be pinned still go in the import with `X pos (%)` / `Y pos (%)` blank - the description and checklist still land.

## 6. Import mechanics

The pin lands on the tag bubble, which sits a few inches off the leaf on a plan. Fine for finding the door; a nudge per task if the person wants it on the leaf.

Do not ship a separate pin-only import when a full task import is coming - one file keyed on `ID` carries pins, descriptions, and checklist references together. Two imports on the same tasks is two chances for a mismatch.
