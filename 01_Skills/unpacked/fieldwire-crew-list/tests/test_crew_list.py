#!/usr/bin/env python3
"""Regression suite for crew_list.py. Every case asserts an outcome; a parser that merely runs does not pass.

  python3 tests/test_crew_list.py        (from the skill folder; needs the same deps as crew_list.py)

Baseline: flags per task must equal tests/expected_flags.json exactly, and the independent-path line
must close. Each --case of make_demo_report.py then either aborts with the expected message or
produces the expected flag/content. Exit code is non-zero on any failure.
"""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.dirname(HERE)
GEN, CL = os.path.join(SK, "scripts", "make_demo_report.py"), os.path.join(SK, "scripts", "crew_list.py")
TASKS, CHECKS = os.path.join(HERE, "fixture_tasks.csv"), os.path.join(HERE, "fixture_checklists.csv")
EXPECTED = json.load(open(os.path.join(HERE, "expected_flags.json")))
EXPECTED.pop("_comment", None)


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).replace("warning: The `fitz` API is deprecated and will be removed in future. Use `import pymupdf` instead.\n", "")


def pdf_text(path):
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    return "\n".join(p.get_text() for p in fitz.open(path))


def flags_of(summary):
    out = {}
    sec = summary.split("## Flagged openings", 1)[1]
    for m in re.finditer(r"^- \*\*(.+?)\*\* \(#\d+, [^)]+\) — (.+)$", sec, re.M):
        out[m.group(1)] = [f.strip() for f in m.group(2).split(",")]
    # flags themselves contain commas ("DONE CLAIMED, 7 ITEMS OPEN"); re-join those
    fixed = {}
    for k, fl in out.items():
        merged, i = [], 0
        while i < len(fl):
            if fl[i] == "DONE CLAIMED" and i + 1 < len(fl):
                merged.append(fl[i] + ", " + fl[i + 1]); i += 2
            else:
                merged.append(fl[i]); i += 1
        fixed[k] = merged
    return fixed


def build(case, wd):
    pdf = os.path.join(wd, f"{case or 'baseline'}.pdf")
    rc, out = run([sys.executable, GEN, "--tasks", TASKS, "--checklists", CHECKS, "--out", pdf] + (["--case", case] if case else []))
    assert rc == 0, out
    return pdf


def crew(pdf, wd, cutoff="2026-09-08"):
    out_pdf, summ = pdf + ".crew.pdf", pdf + ".summary.md"
    rc, out = run([sys.executable, CL, "--report", pdf, "--cutoff", cutoff, "--title", "Test", "--out", out_pdf, "--summary", summ])
    return rc, out, (open(summ).read() if rc == 0 else ""), (out_pdf if rc == 0 else None)


CASES = [
    # (case, expect_abort_substring, checker on (summary, crew_pdf_text)) - checker returns a failure string or None
    ("box-offset", "checkbox(es) with no checklist text", None),
    ("box-missing", "cannot be a wrapped continuation", None),
    ("box-missing-first", "cannot be a wrapped continuation", None),
    ("color-shift", "checkbox fill not recognised", None),
    ("wrapped-item", None, lambda s, t: None if "checkbox drawings 125 = checklist items 125" in s and "protection goes back on" in t
     else "wrapped line was not merged into its item"),
    ("verified-open", None, lambda s, t: None if "CLOSED WITH OPEN ITEMS (Verified)" in flags_of(s).get("V-104", []) else "Verified task with open items not flagged"),
    ("done-claim", None, lambda s, t: None if "DONE CLAIMED, 7 ITEMS OPEN" in flags_of(s).get("V-104", []) and "Install Crew — Done" in t
     else "done claim not flagged or not shown"),
    ("narrow-photo", None, lambda s, t: None if "NO PHOTO" not in flags_of(s).get("V-102", []) else "narrow photo produced a false NO PHOTO"),
    ("no-set-tag", None, lambda s, t: None if re.search(r"RD-01 *#1 *· *Set L1-RECEPTION DESK", t) else "set not read from the import comment"),
]


def main():
    wd = tempfile.mkdtemp(prefix="crewtest_")
    fails = []
    # baseline
    pdf = build(None, wd)
    rc, out, summ, crew_pdf = crew(pdf, wd)
    if rc != 0:
        fails.append("baseline: aborted: " + out.strip())
    else:
        got = flags_of(summ)
        for mark in sorted(set(got) | set(EXPECTED)):
            if got.get(mark, []) != EXPECTED.get(mark, []):
                fails.append(f"baseline: {mark}: got {got.get(mark, [])}, expected {EXPECTED.get(mark, [])}")
        for must in ("| Export | Open Tasks |", "checkbox drawings 125 = checklist items 125", "message rows 37 = 37"):
            if must not in summ:
                fails.append(f"baseline: summary missing '{must}'")
    print(("FAIL" if any(f.startswith("baseline") for f in fails) else "pass") + "  baseline")
    # year boundary needs its own cutoff
    pdf = build("year-boundary", wd)
    rc, out, summ, crew_pdf = crew(pdf, wd, cutoff="2026-12-30")
    ok = rc == 0 and "| Issue comments shown | 2 |" in summ and "2 Jan · A. Reyes" in pdf_text(crew_pdf)
    print(("pass" if ok else "FAIL") + "  year-boundary")
    if not ok:
        fails.append("year-boundary: Jan comment dropped or run aborted: " + out.strip()[:200])
    for case, abort_sub, check in CASES:
        pdf = build(case, wd)
        rc, out, summ, crew_pdf = crew(pdf, wd)
        if abort_sub:
            ok = rc != 0 and abort_sub in out
            why = "" if ok else f"expected abort containing '{abort_sub}', got rc={rc}: {out.strip()[:200]}"
        else:
            why = ("run aborted: " + out.strip()[:200]) if rc != 0 else check(summ, pdf_text(crew_pdf))
            ok = why is None
        print(("pass" if ok else "FAIL") + f"  {case}")
        if not ok:
            fails.append(f"{case}: {why}")
    print()
    if fails:
        print("FAILURES:"); [print(" -", f) for f in fails]
        sys.exit(1)
    print(f"all {len(CASES) + 2} cases pass")


if __name__ == "__main__":
    main()
