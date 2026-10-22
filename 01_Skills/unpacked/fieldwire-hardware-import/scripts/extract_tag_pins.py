#!/usr/bin/env python3
"""
Extract door-tag pin coordinates from architect plan sheets (text layer required).

Usage:
  python3 extract_tag_pins.py --sheet "A-1.01 FIRST FLOOR PLAN=path/to/A-1_01.pdf" \
                              --sheet "A-1.02 SECOND FLOOR=path/to/A-1_02.pdf" \
                              --pattern "[0-9]{4}[A-Z]" \
                              --out tags.json [--check-png check_A-1.01.png] [--page N]

  --pattern is a regex for ONE mark, matching the project's own mark convention.
  Read the door index first and write it to fit: e.g. "[0-9]{4}[A-Z]" for 2101A,
  "[A-Z][0-9]{3}[A-Z]?" for A101 / A101B, "(?:RD|WP|V)-[0-9]{2,3}" for casework.
  Default is the 4-digit-plus-letter convention it was first built on. Words shaped
  like a mark that fail the pattern are listed as near-misses: an empty tag count
  with a long near-miss list means the pattern is wrong, not the sheet.

  --page is required when a sheet PDF has more than one page. Percent coordinates
  are per page; a tag on another page keyed to page 1 would pin on the wrong image,
  so the script refuses to guess which page Fieldwire has.

  Each --sheet is "<Fieldwire plan name>=<pdf path>". Use the plan name exactly as
  Fieldwire's task export prints it in the Plan column.

Output tags.json:
  { "<plan name>": { "W": pts, "H": pts, "page": n, "tags": { "<mark>": [[x_pct, y_pct], ...] },
                     "near_misses": ["101A", "D-101", ...] } }

Coordinates are percent of page width/height from the top-left, i.e. Fieldwire's
"X pos (%)" / "Y pos (%)". A mark with more than one entry is tagged more than once
on that sheet - flag it, don't pick silently.

Why pdftotext -bbox and not pdfplumber: rotated tags (matrix 0,1,-1,0) come out of
pdfplumber as loose characters and are dropped or mangled; pdftotext's bbox output
returns them as whole words. Concatenated tags ("2101A2102A") are split along the
word box.

Optional --check-png renders the chosen page of the first sheet at 40 dpi with a red
circle on every tag found - look at it before trusting the numbers.
"""
import argparse, json, re, shutil, subprocess, sys
from collections import defaultdict

DEFAULT_PATTERN = r"[0-9]{4}[A-Z]|S[1-4]-[1-5][A-Z]"
# Shaped like a door mark (digits with a letter suffix, or a letter prefix with a dash) but not matched by --pattern.
NEAR = re.compile(r"^(?:[A-Z]{1,3}-?\d{1,5}[A-Z]{0,2}|\d{1,5}[A-Z]{1,2})$")


def preflight():
    if shutil.which("pdftotext") is None:
        sys.exit("missing: pdftotext (poppler-utils) - see requirements.txt")


def extract(pdf_path, TAG, FULL, page=None):
    xml = subprocess.run(["pdftotext", "-bbox", pdf_path, "-"], capture_output=True, text=True, check=True).stdout
    pages = re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', xml, re.S)
    if not pages:
        sys.exit(f"ABORT: {pdf_path}: no text layer found (flattened raster?) - this method does not apply")
    if len(pages) > 1 and page is None:
        sys.exit(f"ABORT: {pdf_path} has {len(pages)} pages. Pass --page N for the page Fieldwire has as this plan; "
                 "percent coordinates are per page and a tag on another page would pin on the wrong image.")
    pno = page or 1
    if not 1 <= pno <= len(pages):
        sys.exit(f"ABORT: --page {pno} but {pdf_path} has {len(pages)} page(s)")
    W, H, body = float(pages[pno - 1][0]), float(pages[pno - 1][1]), pages[pno - 1][2]
    found, near = defaultdict(list), set()
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]+)</word>', body):
        x0, y0, x1, y1, t = float(m[1]), float(m[2]), float(m[3]), float(m[4]), m[5]
        if not FULL.match(t):
            if NEAR.match(t):
                near.add(t)
            continue
        parts = TAG.findall(t)
        n = len(parts)
        w, h = x1 - x0, y1 - y0
        vert = h > w and h > 10
        for i, p in enumerate(parts):
            if n == 1:
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            elif vert:
                cx, cy = (x0 + x1) / 2, y1 - h * (i + 0.5) / n
            else:
                cx, cy = x0 + w * (i + 0.5) / n, (y0 + y1) / 2
            c = [round(cx / W * 100, 3), round(cy / H * 100, 3)]
            if c not in found[p]:
                found[p].append(c)
    return {"W": W, "H": H, "page": pno, "tags": dict(found), "near_misses": sorted(near)}


def check_png(pdf_path, tags, out_png, page):
    from PIL import Image, ImageDraw
    subprocess.run(["pdftoppm", "-r", "40", "-png", "-singlefile", "-f", str(page), "-l", str(page), pdf_path, "_chk"], check=True)
    im = Image.open("_chk.png").convert("RGB")
    W, H = im.size
    d = ImageDraw.Draw(im)
    for m, pts in tags.items():
        for x, y in pts:
            px, py = x / 100 * W, y / 100 * H
            d.ellipse([px - 6, py - 6, px + 6, py + 6], outline=(255, 0, 0), width=2)
    im.save(out_png)


def main():
    preflight()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet", action="append", required=True, help='"<plan name>=<pdf path>"')
    ap.add_argument("--out", default="tags.json")
    ap.add_argument("--check-png", default=None)
    ap.add_argument("--pattern", "--tag-regex", dest="pattern", default=DEFAULT_PATTERN, help="regex for one mark, in the project's convention")
    ap.add_argument("--page", type=int, default=None, help="1-based page of each sheet PDF to read (required when a PDF has several)")
    a = ap.parse_args()
    try:
        TAG = re.compile(a.pattern)
    except re.error as e:
        sys.exit(f"ABORT: --pattern does not compile: {e}")
    FULL = re.compile(r"^(?:" + a.pattern + r")+$")
    out = {}
    first = None
    for s in a.sheet:
        name, path = s.split("=", 1)
        out[name] = extract(path, TAG, FULL, a.page)
        dup = {k: len(v) for k, v in out[name]["tags"].items() if len(v) > 1}
        nm = out[name]["near_misses"]
        print(f"{name}: {len(out[name]['tags'])} tags on page {out[name]['page']}"
              + (f"  DUPLICATES {dup}" if dup else "")
              + (f"  NEAR-MISSES {len(nm)} (shaped like marks, failed --pattern): {nm[:20]}" if nm else ""), file=sys.stderr)
        first = first or (path, out[name]["tags"], out[name]["page"])
    json.dump(out, open(a.out, "w"), indent=1)
    if a.check_png and first:
        check_png(first[0], first[1], a.check_png, first[2])
        print(f"overlay written: {a.check_png}", file=sys.stderr)


if __name__ == "__main__":
    main()
