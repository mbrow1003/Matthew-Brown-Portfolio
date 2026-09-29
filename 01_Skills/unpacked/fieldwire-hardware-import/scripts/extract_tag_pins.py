#!/usr/bin/env python3
"""
Extract door-tag pin coordinates from architect plan sheets (text layer required).

Usage:
  python3 extract_tag_pins.py --sheet "A-1.01 FIRST FLOOR PLAN=path/to/A-1_01.pdf" \
                              --sheet "A-1.02 SECOND FLOOR=path/to/A-1_02.pdf" \
                              --pattern "[0-9]{4}[A-Z]" \
                              --out tags.json [--check-png check_A-1.01.png]

  --pattern is a regex for ONE mark, matching the project's own mark convention.
  Read the door index first and write it to fit: e.g. "[0-9]{4}[A-Z]" for 2101A,
  "[A-Z][0-9]{3}[A-Z]?" for A101 / A101B, "(?:RD|WP|V)-[0-9]{2,3}" for casework.
  Default is the 4-digit-plus-letter convention it was first built on.

  Each --sheet is "<Fieldwire plan name>=<pdf path>". Use the plan name exactly as
  Fieldwire's task export prints it in the Plan column.

Output tags.json:
  { "<plan name>": { "W": pts, "H": pts, "tags": { "<mark>": [[x_pct, y_pct], ...] } } }

Coordinates are percent of page width/height from the top-left, i.e. Fieldwire's
"X pos (%)" / "Y pos (%)". A mark with more than one entry is tagged more than once
on that sheet - flag it, don't pick silently.

Why pdftotext -bbox and not pdfplumber: rotated tags (matrix 0,1,-1,0) come out of
pdfplumber as loose characters and are dropped or mangled; pdftotext's bbox output
returns them as whole words. Concatenated tags ("2101A2102A") are split along the
word box.

Optional --check-png renders the first sheet at 40 dpi with a red circle on every
tag found - look at it before trusting the numbers.
"""
import argparse, json, re, subprocess, sys
from collections import defaultdict

DEFAULT_PATTERN = r"[0-9]{4}[A-Z]|S[1-4]-[1-5][A-Z]"


def extract(pdf_path, TAG, FULL):
    x = subprocess.run(["pdftotext", "-bbox", pdf_path, "-"], capture_output=True, text=True, check=True).stdout
    pm = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', x)
    W, H = float(pm.group(1)), float(pm.group(2))
    found = defaultdict(list)
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]+)</word>', x):
        x0, y0, x1, y1, t = float(m[1]), float(m[2]), float(m[3]), float(m[4]), m[5]
        if not FULL.match(t):
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
    return {"W": W, "H": H, "tags": dict(found)}


def check_png(pdf_path, tags, out_png):
    from PIL import Image, ImageDraw
    subprocess.run(["pdftoppm", "-r", "40", "-png", "-singlefile", pdf_path, "_chk"], check=True)
    im = Image.open("_chk.png").convert("RGB")
    W, H = im.size
    d = ImageDraw.Draw(im)
    for m, pts in tags.items():
        for x, y in pts:
            px, py = x / 100 * W, y / 100 * H
            d.ellipse([px - 6, py - 6, px + 6, py + 6], outline=(255, 0, 0), width=2)
    im.save(out_png)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", action="append", required=True, help='"<plan name>=<pdf path>"')
    ap.add_argument("--out", default="tags.json")
    ap.add_argument("--check-png", default=None)
    ap.add_argument("--pattern", default=DEFAULT_PATTERN, help="regex for one mark, in the project's convention")
    a = ap.parse_args()
    TAG = re.compile(a.pattern)
    FULL = re.compile(r"^(?:" + a.pattern + r")+$")
    out = {}
    first = None
    for s in a.sheet:
        name, path = s.split("=", 1)
        out[name] = extract(path, TAG, FULL)
        dup = {k: len(v) for k, v in out[name]["tags"].items() if len(v) > 1}
        print(f"{name}: {len(out[name]['tags'])} tags" + (f"  DUPLICATES {dup}" if dup else ""), file=sys.stderr)
        first = first or (path, out[name]["tags"])
    json.dump(out, open(a.out, "w"), indent=1)
    if a.check_png and first:
        check_png(first[0], first[1], a.check_png)
        print(f"overlay written: {a.check_png}", file=sys.stderr)


if __name__ == "__main__":
    main()
