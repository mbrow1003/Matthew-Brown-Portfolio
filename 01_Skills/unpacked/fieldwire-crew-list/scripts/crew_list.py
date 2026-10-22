#!/usr/bin/env python3
"""Fieldwire task report PDF -> crew list PDF + ops-lead summary.

Implements the SOP "Crew List from Fieldwire Task Report". Input is a Fieldwire task report
exported with comments and photos (the Detailed format). Output is a phone-readable list:
per opening, the checklist as it stands, the import comment (set context), the issue comments
on or after the cutoff, and the newest photos, with one dated fallback photo when nothing is
current. Everything older stays in Fieldwire.

  python3 crew_list.py --report report.pdf --title "Project - Crew List" \
      [--cutoff 2026-09-22] [--walker "Name"] [--plans "A1.1,A1.2"] [--marks "101,102"] \
      [--gate-days 7] --out crew_list.pdf --summary ops_summary.md

Checklist state is read from the checkbox fill Fieldwire draws: done, N/A, failed, or open.
The run refuses rather than guesses. It aborts on: a checkbox fill it does not know, a
checkbox with no checklist text beside it, a checklist line with no checkbox that cannot be a
wrapped continuation, or any count the independent paths disagree on.
"""
import argparse, io, os, re, shutil, subprocess, sys, tempfile, warnings
from collections import Counter
from datetime import date

warnings.filterwarnings("ignore")


def _importable(m):
    try:
        __import__(m); return True
    except ImportError:
        return False


def preflight():
    """Name what is missing instead of failing on the first import."""
    missing = []
    for mods, pkg in ((("pymupdf", "fitz"), "pymupdf"), (("PIL",), "Pillow"), (("reportlab",), "reportlab")):
        if not any(_importable(m) for m in mods):
            missing.append(f"{pkg} (pip install {pkg})")
    if shutil.which("pdftotext") is None:
        missing.append("pdftotext (poppler-utils)")
    if missing:
        sys.exit("missing: " + "; ".join(missing) + " - see requirements.txt")


preflight()
try:
    import pymupdf as fitz
except ImportError:  # older PyMuPDF
    import fitz
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, KeepTogether)
from xml.sax.saxutils import escape

MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS = {m: i + 1 for i, m in enumerate(MON)}
DATE_RE = re.compile(r"^(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{2}:\d{2}\s+[AP]M)$")
DATE_ANY = re.compile(r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2}:\d{2}\s+[AP]M\b")
CREATED_RE = re.compile(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})")
TASK_RE = re.compile(r"^#(\d+)\s*-\s*(.+)$")
STATES = {"done": (0.3647, 0.4784, 0.7412), "na": (0.6038, 0.6039, 0.6038), "failed": (0.9255, 0.3843, 0.3255)}
CLOSED = ("Completed", "Verified")          # both are closed; a Verified task with open items is still wrong
ACK = re.compile(r"^(ok|okay|k|thanks|thank you|got it|noted|\U0001F44D)[.!]*$", re.I)
DONE_CLAIM = re.compile(r"^(done|complete|completed|installed|finished|all set|all done|good to go)[\s.,!]*$", re.I)
CONFIRM_SET = re.compile(r"confirm\s+set", re.I)
SET_IN_TEXT = re.compile(r"\bSet\s+#?([A-Za-z0-9][A-Za-z0-9 ._:/\-]*?)\s*(?:[.;,]|$)")
GATE_RE = re.compile(r"^\s*receiving\b", re.I)   # per-delivery receiving-gate tasks are titled "Receiving - <BOL> ..."
PAIR_TOL = 5.0    # pt between a checkbox centre and the centre of its text line
WRAP_TOL = 70.0   # a line can only have wrapped if it reached within this of the column's right edge
WRAP_GAP = 14.0   # a continuation line sits within one line height of the line it continues


def norm(t):
    return t.replace("\u2000", " ").replace("\u00a0", " ").strip()


def close(a, b, tol=0.02):
    return all(abs(x - y) < tol for x, y in zip(a, b))


def page_lines(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b["lines"]:
            t = norm("".join(s["text"] for s in ln["spans"]))
            if t:
                x0, y0, x1, y1 = ln["bbox"]
                out.append({"t": t, "x0": x0, "y0": y0, "x1": x1, "y1": y1, "size": max(s["size"] for s in ln["spans"])})
    return out


def noise_lines(doc):
    """Report title / header text repeated at the page edge on most pages."""
    seen = Counter()
    for page in doc:
        h = page.rect.height
        for ln in page_lines(page):
            if ln["y0"] < 25 or ln["y1"] > h - 25:
                seen[ln["t"]] += 1
    n = len(doc)
    return {t for t, c in seen.items() if n > 1 and c >= max(2, 0.6 * n)}


def detect_export(doc, noise):
    """Which export this is, from the report header. Decides what the run can see at all."""
    heads = [ln["t"] for ln in page_lines(doc[0]) if ln["y0"] < 40] + sorted(noise) if len(doc) else []
    for t in heads:
        m = re.search(r"\b(Open|All)\s+Tasks\b", t, re.I)
        if m:
            return m.group(1).title() + " Tasks"
    return "unknown"


def parse(path, imgdir):
    doc = fitz.open(path)
    noise = noise_lines(doc)
    info = {"unknown": [], "unpaired_boxes": [], "unpaired_text": [], "orphans": 0, "others": [],
            "images_skipped": 0, "boxes_total": 0, "pages": len(doc), "export_type": detect_export(doc, noise)}
    events, saved = [], {}
    # The widest checklist line in the report is the column's right edge. Only a line that reached
    # it can have wrapped, so only a line below such a line may stand without a checkbox.
    col_right = max((ln["x1"] for page in doc for ln in page_lines(page) if 40 < ln["x0"] < 46), default=0.0)
    # Photos are left-aligned with the message text; anything else (plan thumbnail top-right, pin
    # markers) is outside the column and is skipped and counted, whatever its size.
    body_left = min((ln["x0"] for page in doc for ln in page_lines(page) if 120 < ln["x0"] < 480), default=125.0)
    for pno, page in enumerate(doc):
        boxes = []  # [y_centre, state, paired]
        for dr in page.get_drawings():
            r = dr["rect"]
            if not (21 < r.x0 < 25 and 9 < r.width < 11.5 and 9 < r.height < 11.5):
                continue
            yc, fill = (r.y0 + r.y1) / 2, dr.get("fill")
            if fill is None:
                if dr.get("color") and (dr.get("width") or 0) > 1.0:
                    boxes.append([yc, "open", False])
                continue
            st = next((k for k, v in STATES.items() if close(fill, v)), None)
            if st is None:
                info["unknown"].append((pno + 1, round(yc, 1), tuple(round(c, 4) for c in fill)))
            else:
                boxes.append([yc, st, False])
        info["boxes_total"] += len(boxes)
        for img in page.get_images(full=True):
            xref = img[0]
            for r in page.get_image_rects(xref):
                if abs(r.x0 - body_left) > 30:
                    info["images_skipped"] += 1
                    continue
                if xref not in saved:
                    try:
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n - pix.alpha > 3:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                        im = PILImage.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                        im.thumbnail((640, 640))
                        p = os.path.join(imgdir, f"img_{xref}.jpg")
                        im.save(p, "JPEG", quality=82)
                        saved[xref] = p
                    except Exception:
                        saved[xref] = None
                if saved.get(xref):
                    events.append((pno, r.y0, 5, "photo", saved[xref]))
        last_check = None  # (y1, x1) of the previous checklist line on this page
        for ln in sorted(page_lines(page), key=lambda l: (round(l["y0"], 1), l["x0"])):
            t, x0, y0, x1, y1 = ln["t"], ln["x0"], ln["y0"], ln["x1"], ln["y1"]
            if t in noise or t.startswith("pg. ") or t.startswith("Created with Fieldwire"):
                continue
            mt = TASK_RE.match(t)
            if mt and x0 < 30 and ln["size"] >= 10.5:
                events.append((pno, y0, 0, "task", {"num": int(mt.group(1)), "mark": mt.group(2).strip()}))
                continue
            if x0 < 30 and ln["size"] > 13:
                continue  # category heading
            if x0 < 30:
                if t.startswith("Plan:"):
                    events.append((pno, y0, 1, "plan", t[5:].strip())); continue
                if t.startswith("Tags:"):
                    events.append((pno, y0, 1, "tags", t[5:].strip())); continue
                if t.startswith("Created "):
                    events.append((pno, y0, 1, "created", t[8:].strip())); continue
                if t.startswith("Description:"):
                    events.append((pno, y0, 1, "description", t[12:].strip())); continue
                if " | " in t:
                    events.append((pno, y0, 1, "status", t)); continue
                if t == "Checklist" or t.startswith("Task messages"):
                    events.append((pno, y0, 1, "section", t)); continue
                events.append((pno, y0, 2, "author", t)); continue
            if 40 < x0 < 46:
                yc, best = (y0 + y1) / 2, None
                for b in boxes:
                    d = abs(b[0] - yc)
                    if d < PAIR_TOL and not b[2] and (best is None or d < best[0]):
                        best = (d, b)
                if best:
                    best[1][2] = True
                    events.append((pno, y0, 3, "check", {"text": t, "state": best[1][1]}))
                elif last_check and last_check[1] >= col_right - WRAP_TOL and 0 <= y0 - last_check[0] < WRAP_GAP:
                    events.append((pno, y0, 3, "check", {"text": t, "state": None}))  # wrapped continuation
                else:
                    info["unpaired_text"].append((pno + 1, round(y0, 1), t[:60]))
                last_check = (y1, x1)
                continue
            if t.startswith("GPS:"):
                continue
            m = DATE_RE.match(t)
            if m and x0 > 480:
                events.append((pno, y0, 4, "date", {"day": int(m.group(1)), "month": MONTHS[m.group(2)], "time": m.group(3)}))
                continue
            if 120 < x0 < 480:
                events.append((pno, y0, 3, "body", t)); continue
            info["others"].append(f"p{pno + 1} x0={x0:.0f} {t}")
        for b in boxes:
            if not b[2]:
                info["unpaired_boxes"].append((pno + 1, round(b[0], 1), b[1]))
    events.sort(key=lambda e: (e[0], round(e[1], 1), e[2]))
    tasks, cur, msg = [], None, None
    for pno, y, order, kind, p in events:
        if kind == "task":
            cur = {"num": p["num"], "mark": p["mark"], "plan": "", "tags": "", "status": "", "created": "",
                   "description": "", "checklist": [], "msgs": []}
            tasks.append(cur); msg = None; continue
        if cur is None:
            continue
        if kind in ("plan", "tags", "created", "status", "description"):
            cur[kind] = p; continue
        if kind == "section":
            msg = None; continue
        if kind == "check":
            if p["state"] is None:
                if cur["checklist"]:
                    cur["checklist"][-1]["text"] += " " + p["text"]  # wrapped line
                else:
                    info["orphans"] += 1
            else:
                cur["checklist"].append(p)
            continue
        if kind == "author":
            msg = {"author": p, "body": "", "day": None, "month": None, "year": None, "time": "", "photos": []}
            cur["msgs"].append(msg); continue
        if kind == "body" and msg is not None:
            msg["body"] = (msg["body"] + " " + p).strip(); continue
        if kind == "date" and msg is not None and msg["day"] is None:
            msg.update(day=p["day"], month=p["month"], time=p["time"]); continue
        if kind == "photo" and msg is not None:
            msg["photos"].append(p)
    return tasks, info


def second_path(path):
    """Independent count from pdftotext, to check the parser against."""
    txt = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout
    return len(re.findall(r"(?m)^\s*#\d+\s*-\s*\S", txt)), len(DATE_ANY.findall(txt))


def assign_years(tasks, fallback_year):
    """Report dates carry no year. Start from the task's Created line and roll the year forward
    whenever a comment's month drops below the previous one. Returns how many tasks had no Created year."""
    inferred = 0
    for t in tasks:
        m = CREATED_RE.search(t["created"])
        if m:
            y, last = int(m.group(3)), (MONTHS[m.group(2)], int(m.group(1)))
            t["created_date"] = date(y, last[0], last[1])
        else:
            y, last = fallback_year, None
            t["created_date"] = None
            inferred += 1
        for msg in t["msgs"]:
            if msg["day"] is None:
                continue
            cur = (msg["month"], msg["day"])
            if last is not None and cur[0] < last[0]:
                y += 1
            msg["year"] = y
            last = cur
    return inferred


def mdate(m):
    return (m["year"], m["month"], m["day"])


def tkey(m):
    hh, mm = int(m["time"][:2]), int(m["time"][3:5])
    return (m["year"], m["month"], m["day"], (hh % 12 + (12 if m["time"].endswith("PM") else 0)) * 60 + mm)


def status_of(t):
    return t["status"].split(" | ")[0].strip()


def set_of(t):
    """Set context: a #set_ tag first; then 'Set <name>' in the import comment or the description."""
    tags = [x.strip() for x in t["tags"].split(",") if x.strip()]
    s = [x for x in tags if x.lower().startswith("#set_")]
    if s:
        return "Set " + s[0][5:]
    for text in ((t["msgs"][0]["body"] if t["msgs"] else ""), t.get("description", "")):
        m = SET_IN_TEXT.search(text or "")
        if m:
            return "Set " + m.group(1).strip()
    return ""


def mark_key(m):
    mm = re.match(r"^([A-Za-z-]*)(\d+)(.*)$", m)
    return (0, mm.group(1), int(mm.group(2)), mm.group(3).upper()) if mm else (1, m, 0, "")


def build(tasks, cutoff, cutoff_date, walker, gate_days):
    """Apply the SOP keep rules and flags. Returns per-task view dicts."""
    views = []
    for t in tasks:
        dated = [m for m in t["msgs"] if m["day"] is not None]
        first = t["msgs"][0] if t["msgs"] else None
        on_after = [m for m in dated[1:] if mdate(m) >= cutoff and m["body"]]
        claims = [m for m in on_after if DONE_CLAIM.match(m["body"])]
        issues = [m for m in on_after if not ACK.match(m["body"]) and not DONE_CLAIM.match(m["body"])
                  and (walker is None or m["author"] == walker)]
        current = [(p, m) for m in dated if mdate(m) >= cutoff for p in m["photos"]]
        prior = sorted([m for m in dated if m["photos"] and mdate(m) < cutoff], key=tkey)
        if current:
            photos = [(p, m, False) for p, m in current]
        elif prior:
            photos = [(prior[-1]["photos"][-1], prior[-1], True)]
        else:
            photos = []
        st = status_of(t)
        open_items = [c for c in t["checklist"] if c["state"] == "open"]
        failed = [c for c in t["checklist"] if c["state"] == "failed"]
        flags = []
        if first and CONFIRM_SET.search(first["body"] or ""):
            flags.append("CONFIRM SET")
        if failed:
            flags.append("FAILED ITEM")
        if st in CLOSED and (open_items or failed):
            flags.append(f"CLOSED WITH OPEN ITEMS ({st})")
        if claims and (open_items or failed):
            n = len(open_items) + len(failed)
            flags.append(f"DONE CLAIMED, {n} ITEM{'S' if n != 1 else ''} OPEN")
            issues = sorted(issues + claims, key=tkey)  # the claim that contradicts the record is shown, whoever wrote it
        if GATE_RE.search(t["mark"]) and st not in CLOSED and t.get("created_date"):
            days = (cutoff_date - t["created_date"]).days
            if days > gate_days:
                flags.append(f"RECEIVING GATE OPEN {days} DAYS")
        if not any(m["photos"] for m in t["msgs"]):
            flags.append("NO PHOTO")
        block = st not in CLOSED or bool(open_items) or bool(failed) or bool(issues)
        views.append({"t": t, "first": first, "issues": issues, "photos": photos, "flags": flags,
                      "open": open_items, "failed": failed, "block": block})
    return views


def render(views, out, title, cutoff_label, n_report):
    ss = getSampleStyleSheet()
    INK, MUTE, LINE, RED = (colors.HexColor(c) for c in ("#1A1A1A", "#8A8A8A", "#D9D9D9", "#B3261E"))
    STATUS_COLOR = {"Issue": "#B3261E", "In Progress": "#8A6D1B", "Completed": "#2E7D32", "Verified": "#2E7D32"}
    P = lambda name, **kw: ParagraphStyle(name, parent=ss["Normal"], **kw)
    title_s = P("t", fontName="Helvetica-Bold", fontSize=15, leading=18, spaceAfter=2)
    sub_s = P("s", fontSize=8, leading=10, textColor=MUTE, spaceAfter=6)
    plan_s = P("p", fontName="Helvetica-Bold", fontSize=12, leading=14, textColor=colors.HexColor("#2B4A6F"), spaceBefore=10, spaceAfter=4)
    head_s = P("h", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=INK, spaceBefore=6, spaceAfter=1)
    flag_s = P("f", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=RED, leftIndent=8)
    ctx_s = P("c", fontName="Helvetica-Oblique", fontSize=7.5, leading=9.5, textColor=MUTE, leftIndent=8, spaceAfter=2)
    open_s = P("o", fontName="Helvetica-Bold", fontSize=8.5, leading=10.5, textColor=INK, leftIndent=8)
    fail_s = P("x", fontName="Helvetica-Bold", fontSize=8.5, leading=10.5, textColor=RED, leftIndent=8)
    done_s = P("d", fontSize=7.5, leading=9.5, textColor=MUTE, leftIndent=8)
    note_s = P("n", fontName="Helvetica-Bold", fontSize=9, leading=11.5, textColor=INK, leftIndent=8, spaceBefore=2)
    cap_s = P("cap", fontSize=6.5, leading=8, textColor=MUTE, alignment=1)
    lab_s = P("lab", fontSize=6.5, leading=8, textColor=MUTE, leftIndent=8)
    line_s = P("l", fontSize=8, leading=10, textColor=MUTE, leftIndent=2)
    TW, TH, COLS, CW = 100.0, 118.0, 5, letter[0] - 64

    def rule(w=0.4, c=LINE):
        return Table([[""]], colWidths=[CW], rowHeights=[2], style=TableStyle([("LINEBELOW", (0, 0), (-1, -1), w, c)]))

    def img(path):
        with PILImage.open(path) as im:
            w, h = im.size
        s = min(TW / w, TH / h)
        return Image(path, width=w * s, height=h * s)

    story = [Paragraph(escape(title), title_s),
             Paragraph(f"Cutoff {cutoff_label} &nbsp;·&nbsp; {n_report} openings &nbsp;·&nbsp; "
                       "[ ] open &nbsp; [!] failed &nbsp; [x] done &nbsp; [NA] not applicable &nbsp;·&nbsp; "
                       "photos from the cutoff on; where none, the latest earlier photo, dated", sub_s),
             rule(0.8, colors.HexColor("#2B4A6F"))]
    plans = []
    for v in views:
        if v["t"]["plan"] not in plans:
            plans.append(v["t"]["plan"])
    stats = Counter()
    for plan in plans:
        pv = sorted([v for v in views if v["t"]["plan"] == plan], key=lambda v: mark_key(v["t"]["mark"]))
        heading = Paragraph(f"{escape(plan or 'No plan')} &nbsp;<font size=8 color='#8A8A8A'>— {len(pv)} opening{'s' if len(pv) != 1 else ''}, "
                            f"{sum(v['block'] for v in pv)} with work or notes</font>", plan_s)
        done_only = []
        for v in pv:
            t = v["t"]
            if not v["block"]:
                done_only.append(v); continue
            stats["blocks"] += 1
            block = [heading] if heading else []
            heading = None
            st = status_of(t)
            hdr = f"{escape(t['mark'])} <font size=8 color='#8A8A8A'>&nbsp;#{t['num']}"
            if set_of(t):
                hdr += f" &nbsp;·&nbsp; {escape(set_of(t))}"
            hdr += f" &nbsp;·&nbsp; </font><font size=9 color='{STATUS_COLOR.get(st, '#1A1A1A')}'>{escape(st)}</font>"
            block.append(Paragraph(hdr, head_s))
            if v["flags"]:
                block.append(Paragraph(" &nbsp;·&nbsp; ".join(v["flags"]), flag_s))
            if v["first"] and v["first"]["body"]:
                block.append(Paragraph(escape(v["first"]["body"]), ctx_s))
            for c in t["checklist"]:
                if c["state"] == "open":
                    block.append(Paragraph("[&nbsp;&nbsp;] " + escape(c["text"]), open_s))
                elif c["state"] == "failed":
                    block.append(Paragraph("[!] " + escape(c["text"]), fail_s))
                else:
                    block.append(Paragraph(("[NA] " if c["state"] == "na" else "[x] ") + escape(c["text"]), done_s))
            for m in v["issues"]:
                block.append(Paragraph(f"<font color='#8A8A8A'>{m['day']} {MON[m['month'] - 1]} · {escape(m['author'])}</font> — {escape(m['body'])}", note_s))
                stats["issue_comments"] += 1
            story.append(KeepTogether(block))
            if v["photos"]:
                cells, caps = [], []
                for p, m, fb in v["photos"]:
                    assert m["day"] is not None, "undated photo"
                    cells.append(img(p))
                    caps.append(Paragraph(f"{m['day']} {MON[m['month'] - 1]}" + (" · latest available" if fb else ""), cap_s))
                    stats["photos_fallback" if fb else "photos_current"] += 1
                rows = [[Paragraph(f"photos · {escape(t['mark'])}", lab_s)] + [""] * (COLS - 1)]
                for i in range(0, len(cells), COLS):
                    r1, r2 = cells[i:i + COLS], caps[i:i + COLS]
                    rows += [r1 + [""] * (COLS - len(r1)), r2 + [""] * (COLS - len(r2))]
                story.append(Table(rows, colWidths=[TW + 8] * COLS, hAlign="LEFT", style=TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("SPAN", (0, 0), (-1, 0)),
                    ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 4)])))
                if any(fb for _, _, fb in v["photos"]):
                    stats["tasks_fallback"] += 1
            story += [Spacer(1, 3), rule()]
        if heading is not None:
            story.append(heading)
        if done_only:
            marks = [escape(v["t"]["mark"]) + ("*" if "NO PHOTO" in v["flags"] else "") for v in done_only]
            story.append(Paragraph(f"[x] Closed, nothing outstanding ({len(done_only)}): " + ", ".join(marks), line_s))
            if any("NO PHOTO" in v["flags"] for v in done_only):
                story.append(Paragraph("* no photo on the task", line_s))
            stats["oneliners"] += len(done_only)
    SimpleDocTemplate(out, pagesize=letter, leftMargin=32, rightMargin=32, topMargin=28, bottomMargin=28,
                      title=title).build(story)
    return stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", required=True)
    ap.add_argument("--title", default="Crew List")
    ap.add_argument("--cutoff", help="YYYY-MM-DD; default is the newest comment date in the report")
    ap.add_argument("--walker", help="only this author's comments count as issue comments")
    ap.add_argument("--plans", help="comma list of plan names to keep")
    ap.add_argument("--marks", help="comma list of door marks to keep")
    ap.add_argument("--gate-days", type=int, default=7, help="flag a receiving-gate task still open this many days after creation")
    ap.add_argument("--out", default="crew_list.pdf")
    ap.add_argument("--summary", default="ops_summary.md")
    a = ap.parse_args()

    imgdir = tempfile.mkdtemp(prefix="crewlist_")
    tasks, info = parse(a.report, imgdir)
    if info["unknown"]:
        sys.exit("ABORT: checkbox fill not recognised (page, y, rgb): " + repr(info["unknown"][:5]) +
                 " - Fieldwire may have added a state. Inspect one page and add it to STATES before trusting any output.")
    if info["unpaired_boxes"]:
        sys.exit(f"ABORT: {len(info['unpaired_boxes'])} checkbox(es) with no checklist text within {PAIR_TOL:g} pt "
                 f"(page, y, state): {info['unpaired_boxes'][:5]!r} - the layout shifted; an item would have been "
                 "merged into the one above it.")
    if info["unpaired_text"]:
        sys.exit(f"ABORT: {len(info['unpaired_text'])} checklist line(s) with no checkbox that cannot be a wrapped "
                 f"continuation (page, y, text): {info['unpaired_text'][:5]!r} - inspect the page; do not send.")
    heads, date_rows = second_path(a.report)
    n_msgs = sum(1 for t in tasks for m in t["msgs"] if m["day"] is not None)
    n_items = sum(len(t["checklist"]) for t in tasks)
    problems = []
    if heads != len(tasks):
        problems.append(f"task headers: pdftotext {heads} vs parser {len(tasks)}")
    if date_rows != n_msgs:
        problems.append(f"message rows: pdftotext {date_rows} vs parser {n_msgs}")
    if info["boxes_total"] != n_items:
        problems.append(f"checkbox drawings {info['boxes_total']} vs checklist items parsed {n_items}")
    if info["orphans"]:
        problems.append(f"{info['orphans']} checklist line(s) before any checkbox")
    if problems:
        sys.exit("ABORT: independent-path check failed - " + "; ".join(problems))

    cutoff_year = date.fromisoformat(a.cutoff).year if a.cutoff else date.today().year
    inferred = assign_years(tasks, cutoff_year)
    all_dates = [mdate(m) for t in tasks for m in t["msgs"] if m["day"] is not None]
    if a.cutoff:
        d = date.fromisoformat(a.cutoff)
    else:
        y, mo, dd = max(all_dates); d = date(y, mo, dd)
    cutoff = (d.year, d.month, d.day)
    cutoff_label = f"{d.day} {MON[d.month - 1]} {d.year}" + ("" if a.cutoff else " (newest comment date in the report)")
    keep = tasks
    if a.plans:
        want = {p.strip() for p in a.plans.split(",")}; keep = [t for t in keep if t["plan"] in want]
    if a.marks:
        want = {p.strip() for p in a.marks.split(",")}; keep = [t for t in keep if t["mark"] in want]

    views = build(keep, cutoff, d, a.walker, a.gate_days)
    stats = render(views, a.out, a.title, cutoff_label, len(keep))
    assert stats["blocks"] + stats["oneliners"] == len(keep), "openings on the list != openings after filtering"

    states = Counter(c["state"] for t in keep for c in t["checklist"])
    flagged = [v for v in views if v["flags"]]
    closed_seen = sum(1 for t in tasks if status_of(t) in CLOSED)
    export = info["export_type"]
    if export == "Open Tasks":
        export_note = "Open Tasks export: completed tasks are not in this report, so CLOSED WITH OPEN ITEMS can only fire on tasks that are still in it."
    elif export == "unknown" and closed_seen == 0:
        export_note = "Export type not stated in the header and no closed task appears. If this is an Open Tasks export, closed tasks are not visible to this run."
    else:
        export_note = f"{export} export; {closed_seen} closed task(s) in the report."
    year_note = ("Years taken from each task's Created line; the year rolls forward when a comment's month drops."
                 if not inferred else
                 f"{inferred} task(s) had no Created year; {cutoff_year} assumed for them and rolled forward from there.")
    lines = [f"# Ops lead summary — {a.title}", "",
             f"Cutoff: {cutoff_label}", "",
             "| | |", "|---|---|",
             f"| Export | {export} |",
             f"| Openings in report | {len(tasks)} |",
             f"| Openings after filter | {len(keep)} |",
             f"| Full blocks / one-line completes | {stats['blocks']} / {stats['oneliners']} |",
             f"| Checklist items | {sum(states.values())} — {states['done']} done, {states['open']} open, {states['na']} N/A, {states['failed']} failed |",
             f"| Issue comments shown | {stats['issue_comments']} |",
             f"| Photos shown | {stats['photos_current'] + stats['photos_fallback']} — {stats['photos_current']} current, {stats['photos_fallback']} fallback |",
             f"| Openings using a fallback photo | {stats['tasks_fallback']} |",
             f"| Images outside the message column skipped | {info['images_skipped']} (plan thumbnails, markers) |",
             f"| Flagged openings | {len(flagged)} |", "",
             export_note, "", year_note, "",
             f"Independent-path check: task headers pdftotext {heads} = parser {len(tasks)}; message rows {date_rows} = {n_msgs}; "
             f"checkbox drawings {info['boxes_total']} = checklist items {n_items}.", "",
             "## Flagged openings", ""]
    lines += [f"- **{v['t']['mark']}** (#{v['t']['num']}, {status_of(v['t'])}) — {', '.join(v['flags'])}" for v in flagged] or ["None — verified."]
    lines += ["", "Authors are shown exactly as Fieldwire records them. Accounts are sometimes shared; confirm who was on site before attributing a comment to a person."]
    open(a.summary, "w").write("\n".join(lines) + "\n")
    print(f"ok: {export}; {len(keep)} openings -> {stats['blocks']} blocks + {stats['oneliners']} one-liners; "
          f"checklist {dict(states)}; flagged {len(flagged)}; paths {heads}={len(tasks)}, {date_rows}={n_msgs}, "
          f"boxes {info['boxes_total']}={n_items}; images skipped {info['images_skipped']}")


if __name__ == "__main__":
    main()
