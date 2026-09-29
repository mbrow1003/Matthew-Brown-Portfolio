#!/usr/bin/env python3
"""Build a synthetic Fieldwire task report (Detailed format) for testing crew_list.py.

Fictional data only: the demo hotel lobby millwork project from the portfolio. Geometry follows
what crew_list.py reads (header at x<30, checkbox squares at x~22, checklist text at x~43,
message body at x 120-480, dates at x>480, photos in the message column, plan thumbnail right).
It exists so the parser can be exercised without client data. It is not Fieldwire output.

  python3 make_demo_report.py --tasks Fieldwire_Task_Import.csv \
      --checklists Fieldwire_Checklist_Setup.csv --out demo_report.pdf
"""
import argparse, csv, os, tempfile
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

W, H = 612, 792
TITLE = "Demo Hotel Lobby Millwork - Open Tasks (Detailed)"
FILL = {"done": (0.3647, 0.4784, 0.7412), "na": (0.6038, 0.6039, 0.6038), "failed": (0.9255, 0.3843, 0.3255)}
RANK = {"FIELD VERIFICATION": 0, "HOLD": 0, "RELEASED TO SHOP": 1, "IN SHOP": 2, "DELIVERED": 3, "INSTALLED": 4, "ACCEPTED": 5}
IMPORT = "1 Sep 08:00 AM"
# (author, date, body, photo caption or None) after the import comment. Cutoff for the demo is 8 Sep.
MSGS = {
 "RD-01": [("T. Nguyen", "4 Sep 10:12 AM", "Field dims taken.", "field dims"),
           ("A. Reyes", "8 Sep 09:05 AM", "Field width 142-1/4 vs 144 drawn. Not released - PM to pick a revised drawing or filler.", "width at desk wall")],
 "BD-01": [("T. Nguyen", "3 Sep 11:20 AM", "Field dims taken.", "bar wall"),
           ("PM Account", "5 Sep 02:30 PM", "Released on SD-02 rev 2.", None),
           ("T. Nguyen", "8 Sep 09:40 AM", "ok", None)],
 "WP-01": [("T. Nguyen", "3 Sep 11:45 AM", "Dims taken.", "north wall"),
           ("A. Reyes", "8 Sep 09:15 AM", "Blocking still not confirmed at cleats - framing owes it.", "open wall at cleats")],
 "WP-02": [("T. Nguyen", "3 Sep 11:50 AM", "Dims taken.", "north wall east"),
           ("A. Reyes", "8 Sep 09:17 AM", "Same as WP-01 - blocking not confirmed.", None)],
 "WP-03": [("T. Nguyen", "3 Sep 12:05 PM", "Dims taken.", "east wall"), ("PM Account", "5 Sep 02:35 PM", "Released on SD-04 rev 2.", None)],
 "WP-04": [("Shop Account", "6 Sep 03:10 PM", "Cut list issued, panel in fabrication.", "panel on bench")],
 "WP-05": [("Install Crew", "7 Sep 01:30 PM", "Installed.", "installed panel"),
           ("A. Reyes", "8 Sep 09:30 AM", "Reveal tight at top right - adjust before punch.", "reveal detail")],
 "CT-01": [("T. Nguyen", "2 Sep 09:00 AM", "Bar area as of today.", "bar area"),
           ("A. Reyes", "8 Sep 09:45 AM", "Bar die not in yet - template waits on it.", None)],
 "CT-02": [],
 "V-101": [("GC Account", "2 Sep 04:00 PM", "Accepted on GC walk.", "vanity 101")],
 "V-102": [("Install Crew", "7 Sep 10:00 AM", "Delivered, staged in room 102.", "staged 102")],
 "V-103": [("Install Crew", "7 Sep 10:05 AM", "Delivered, staged in room 103.", "staged 103"),
           ("A. Reyes", "8 Sep 10:10 AM", "Task marked complete but the vanity is still in the carton - reopen.", "carton in 103")],
 "V-104": [],
 "V-105": [("T. Nguyen", "2 Sep 01:15 PM", "Dims taken.", "room 105"),
           ("A. Reyes", "8 Sep 10:20 AM", "Rough-in centerline not verified - plumber on site Thursday.", None)],
}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def photo(path, mark, cap, date, color):
    im = Image.new("RGB", (480, 360), color)
    d = ImageDraw.Draw(im)
    try:
        f1, f2 = ImageFont.truetype(FONT, 44), ImageFont.truetype(FONT, 22)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.rectangle([12, 12, 468, 348], outline=(255, 255, 255), width=3)
    d.text((32, 40), mark, fill="white", font=f1)
    d.text((32, 120), cap, fill="white", font=f2)
    d.text((32, 160), date, fill="white", font=f2)
    d.text((32, 300), "PLACEHOLDER PHOTO", fill=(235, 235, 235), font=f2)
    im.save(path, "JPEG", quality=85)


def states(cat, ctype, lines, mark):
    r, out, hold = RANK[cat], [], cat == "HOLD"
    first_field, seen_compare = True, False
    for ln in lines:
        k = ln.split(":")[0]
        if cat == "ACCEPTED":
            out.append("done"); continue
        if k == "FIELD":
            if r >= 1:
                s = "done"
            elif hold:
                if ln.startswith("FIELD: Compare"):
                    s, seen_compare = "failed", True
                else:
                    s = "open" if seen_compare else "done"
            else:
                s = "done" if (first_field and ctype != "COUNTERTOP") else "open"
            first_field = False
        elif k == "HOLD":
            s = ("na" if mark == "WP-05" else "done") if r >= 1 else "open"
        elif ln.startswith("GATE: RELEASED"):
            s = "done" if r >= 1 else "open"
        elif k == "SHOP":
            s = "done" if r >= 3 else ("done" if r == 2 and sum(1 for x in out if x) < 0 else "open")
            if r == 2:
                s = "done" if ln.startswith(("SHOP: Cut list", "SHOP: Fabricated")) else "open"
        elif k == "SITE":
            if r >= 4:
                s = "open" if ln.startswith("SITE: Punch") else "done"
            elif r == 3:
                s = "done" if ln.startswith("SITE: Delivered") else "open"
            else:
                s = "open"
        else:  # GATE: ACCEPTED
            s = "open"
        out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True); ap.add_argument("--checklists", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cl = defaultdict(list)
    for row in csv.DictReader(open(a.checklists)):
        cl[row["Checklist"]].append(row["Item"])
    rows = list(csv.DictReader(open(a.tasks)))
    tmp = tempfile.mkdtemp(prefix="fixture_")
    plan_img = os.path.join(tmp, "plan.jpg")
    Image.new("RGB", (420, 270), (225, 225, 225)).save(plan_img)
    colors_by = {0: (120, 120, 120), 1: (70, 110, 150), 2: (140, 110, 60), 3: (80, 130, 90), 4: (100, 90, 140), 5: (60, 120, 60)}
    c = canvas.Canvas(a.out, pagesize=(W, H))
    page = [1]

    def chrome():
        c.setFont("Helvetica", 7); c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(22, H - 14, TITLE)
        c.drawString(22, 12, f"pg. {page[0]}"); c.drawString(250, 12, "Created with Fieldwire")
        c.setFillColorRGB(0, 0, 0)

    def text(x, ytop, s, size=8.5, font="Helvetica"):
        c.setFont(font, size); c.drawString(x, H - ytop - size * 0.8, s)

    y = [0]

    def need(h):
        if y[0] + h > 755:
            c.showPage(); page[0] += 1; chrome(); y[0] = 34

    chrome()
    for i, row in enumerate(rows, 1):
        if i > 1:
            c.showPage(); page[0] += 1; chrome()
        mark, cat, cname = row["Title"], row["Category"], row["Checklist"]
        ctype = cname.split("-", 1)[1]
        status = {"HOLD": "Issue | Priority 1", "ACCEPTED": "Completed | Priority 2"}.get(cat, "In Progress | Priority 2")
        if mark == "V-103":
            status = "Completed | Priority 2"  # closed early in the field: the flag should catch it
        y[0] = 30
        text(22, y[0], f"#{i} - {mark}", 12, "Helvetica-Bold")
        c.drawImage(plan_img, 440, H - 30 - 90, 140, 90)
        for s in (f"Plan: {row['Plan']}", f"Tags: #set_{cname}, #demo", "Created 01 Sep 2026 by A. Reyes", status):
            y[0] += 14; text(22, y[0], s)
        y[0] = 132; text(22, y[0], "Checklist", 9, "Helvetica-Bold"); y[0] += 16
        for ln, st in zip(cl[cname], states(cat, ctype, cl[cname], mark)):
            parts = simpleSplit(ln, "Helvetica", 8.5, 540)
            need(12 * len(parts))
            if st == "open":
                c.setStrokeColorRGB(0.55, 0.55, 0.55); c.setLineWidth(1.2); c.rect(22.5, H - y[0] - 9.5, 10, 10, stroke=1, fill=0)
            else:
                c.setFillColorRGB(*FILL[st]); c.rect(22.5, H - y[0] - 9.5, 10, 10, stroke=0, fill=1); c.setFillColorRGB(0, 0, 0)
            for j, p in enumerate(parts):
                text(43, y[0], p); y[0] += 12
        y[0] += 8; need(20); text(22, y[0], "Task messages", 9, "Helvetica-Bold"); y[0] += 16
        imp = "Imported 09/01 from the L1 package. " + ("CONFIRM SET - transaction top type depends on the RD-01 disposition." if mark == "CT-02" else f"Set {cname}.")
        for author, when, body, cap in [("A. Reyes", IMPORT, imp, None)] + MSGS.get(mark, []):
            parts = simpleSplit(body, "Helvetica", 8.5, 340)
            need(14 + 11 * len(parts) + (82 if cap else 0))
            text(22, y[0], author, 8.5, "Helvetica-Bold"); text(490, y[0], when, 8)
            for p in parts:
                y[0] += 11; text(125, y[0], p)
            y[0] += 14
            if cap:
                pth = os.path.join(tmp, f"{mark}_{when.replace(' ', '_').replace(':', '')}.jpg")
                photo(pth, mark, cap, when.rsplit(" ", 2)[0], colors_by[RANK[cat]])
                c.drawImage(pth, 130, H - y[0] - 75, 100, 75); y[0] += 82
    c.save()
    print("fixture:", a.out, "| tasks:", len(rows), "| pages:", page[0])


if __name__ == "__main__":
    main()
