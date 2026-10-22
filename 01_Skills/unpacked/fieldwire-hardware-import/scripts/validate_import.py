#!/usr/bin/env python3
"""Validate OUTPUT 1 (task import) and OUTPUT 2 (checklist setup) before Fieldwire ever sees them.

  python3 validate_import.py --tasks Fieldwire_Task_Import.csv --checklists Fieldwire_Checklist_Setup.csv \
      [--index marks.txt] [--strict]

Fails (exit 1) on what breaks an import or puts a wrong row in the field:
  - task header not the documented column set; blank Title; blank Description
  - a Checklist value with no exact match in OUTPUT 2 (the #1 cause of failed imports);
    near-matches that differ only by whitespace or case are named, since that is the usual cause
  - checklist header not `Checklist,Item`; blank names or items
  - an Install line with no per-opening quantity or no product number in parentheses
  - pin columns present but a coordinate blank on one axis, non-numeric, or outside 0-100
  - an ID column with blanks or repeats
  - a NOT IN HW SUBMITTAL row with a checklist attached or without #hw-tbd
  - the same heading name used both with and without a package prefix (a collision)
  - with --index: titles missing from or absent in the door index

Warns (exit 0 unless --strict) on what needs a decision rather than a fix:
  - duplicate titles inside one package - verified shells are intentional; confirm each one
  - several packages in the task file but unprefixed checklist names (project-global names collide)
  - an Install line whose quantity is flagged `total` (the division did not close)
  - a description that follows neither recipe
  - a checklist defined in OUTPUT 2 that no task references
"""
import argparse, csv, re, sys
from collections import Counter, defaultdict

BASE = ["Title", "Location", "Description", "Checklist"]
OPTIONAL = {"ID", "Plan", "X pos (%)", "Y pos (%)", "Category", "Assignee", "Status", "Plan folder"}
INSTALL = re.compile(r"^Install\s+(\d+)\s+(.+)$")
PRODUCT = re.compile(r"\([^()]*[A-Za-z0-9][^()]*\)")


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    return rows[0] if rows else [], rows[1:]


def squash(s):
    return re.sub(r"\s+", " ", s.strip()).casefold()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", required=True); ap.add_argument("--checklists", required=True)
    ap.add_argument("--index", help="door index: one mark per line, or a CSV with a Title column")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    a = ap.parse_args()
    fails, warns, notes = [], [], []

    th, trows = read(a.tasks)
    ch, crows = read(a.checklists)
    if th[:len(BASE)] != BASE and not (th and th[0] == "ID" and th[1:5] == BASE):
        fails.append(f"task header is {th!r}; expected {','.join(BASE)} or ID,{','.join(BASE)},Plan,X pos (%),Y pos (%)")
    unknown = [c for c in th if c not in BASE and c not in OPTIONAL]
    if unknown:
        warns.append(f"task columns Fieldwire's import does not document: {unknown}")
    if ch != ["Checklist", "Item"]:
        fails.append(f"checklist header is {ch!r}; expected Checklist,Item")
    col = {c: i for i, c in enumerate(th)}

    def cell(r, name, raw=False):
        i = col.get(name)
        if i is None or i >= len(r):
            return ""
        return r[i] if raw else r[i].strip()

    # OUTPUT 2
    names, items_by = [], defaultdict(list)
    for n, r in enumerate(crows, 2):
        nm, it = (r[0] if r else ""), (r[1] if len(r) > 1 else "").strip()
        if not nm.strip() or not it:
            fails.append(f"checklists row {n}: blank {'name' if not nm.strip() else 'item'}"); continue
        if nm != nm.strip():
            fails.append(f"checklists row {n}: name {nm!r} has leading/trailing whitespace - Fieldwire matches names literally")
        if nm not in items_by:
            names.append(nm)
        items_by[nm].append((n, it))
    for nm, its in items_by.items():
        for n, it in its:
            m = INSTALL.match(it)
            if it.startswith("Install"):
                if not m:
                    fails.append(f"checklists row {n} ({nm}): Install line has no per-opening quantity: {it[:70]!r}")
                elif not PRODUCT.search(m.group(2)):
                    fails.append(f"checklists row {n} ({nm}): Install line has no product number in parentheses: {it[:70]!r}")
                if re.search(r"\btotal\b", it, re.I):
                    warns.append(f"checklists row {n} ({nm}): quantity flagged 'total' - per-opening division did not close")
    name_set = set(names)
    squashed = defaultdict(list)
    for nm in names:
        squashed[squash(nm)].append(nm)
    for k, v in squashed.items():
        if len(v) > 1:
            fails.append(f"checklist names that differ only by whitespace/case: {v}")
    # prefix / collision analysis: a name is prefixed when it has a '-' with a short all-caps token before it
    def split_prefix(nm):
        m = re.match(r"^([A-Z0-9]{1,4})-(.+)$", nm)
        return (m.group(1), m.group(2)) if m else ("", nm)
    heads = defaultdict(set)
    for nm in names:
        p, h = split_prefix(nm)
        heads[h].add(p)
    for h, ps in heads.items():
        if "" in ps and len(ps) > 1:
            fails.append(f"heading {h!r} exists both unprefixed and prefixed {sorted(p for p in ps if p)} - these collide on import")

    # OUTPUT 1
    used, pkgs_seen, off_recipe = Counter(), set(), []
    titles_by_pkg = defaultdict(list)
    ids = []
    has_pins = "X pos (%)" in col or "Y pos (%)" in col
    for n, r in enumerate(trows, 2):
        t, d, c = cell(r, "Title"), cell(r, "Description"), cell(r, "Checklist", raw=True)
        if c != c.strip():
            fails.append(f"tasks row {n} ({t}): Checklist {c!r} has leading/trailing whitespace - will not match on import")
        if not t:
            fails.append(f"tasks row {n}: blank Title")
        if not d:
            fails.append(f"tasks row {n} ({t}): blank Description")
        pkg = cell(r, "Plan folder") or cell(r, "Plan").split(" ")[0] if (cell(r, "Plan folder") or cell(r, "Plan")) else ""
        pkgs_seen.add(pkg)
        titles_by_pkg[pkg].append((n, t))
        if "ID" in col:
            ids.append((n, cell(r, "ID")))
        if c:
            used[c] += 1
            if c not in name_set:
                near = squashed.get(squash(c))
                fails.append(f"tasks row {n} ({t}): Checklist {c!r} not in OUTPUT 2"
                             + (f" - off by whitespace/case from {near[0]!r}" if near else ""))
        if d.startswith("NOT IN HW SUBMITTAL"):
            if c:
                fails.append(f"tasks row {n} ({t}): NOT IN HW SUBMITTAL row carries a checklist {c!r}")
            if "#hw-tbd" not in d:
                fails.append(f"tasks row {n} ({t}): NOT IN HW SUBMITTAL row lacks #hw-tbd")
        elif d and not d.startswith("Set "):
            off_recipe.append((n, t, d))
        elif d and not c:
            warns.append(f"tasks row {n} ({t}): a Set description with no Checklist")
        if has_pins:
            x, y = cell(r, "X pos (%)"), cell(r, "Y pos (%)")
            if bool(x) != bool(y):
                fails.append(f"tasks row {n} ({t}): one pin axis blank ({x!r}, {y!r})")
            for ax, v in (("X", x), ("Y", y)):
                if v:
                    try:
                        fv = float(v)
                        if not 0 <= fv <= 100:
                            fails.append(f"tasks row {n} ({t}): {ax} pos {v} outside 0-100")
                    except ValueError:
                        fails.append(f"tasks row {n} ({t}): {ax} pos {v!r} is not a number")
    hw_rows = sum(1 for r in trows if cell(r, "Description").startswith(("Set ", "NOT IN HW SUBMITTAL")))
    if off_recipe and hw_rows == 0:
        notes.append(f"no description follows the hardware recipe ({len(off_recipe)} rows) - another trade's recipe (QA/QC gate?); recipe checks skipped, everything else applied")
    else:
        warns += [f"tasks row {n} ({t}): description follows neither recipe: {d[:60]!r}" for n, t, d in off_recipe]
    if ids:
        blank = [n for n, i in ids if not i]
        if blank:
            fails.append(f"ID column present but blank on rows {blank[:10]}")
        dup = [i for i, k in Counter(i for _, i in ids if i).items() if k > 1]
        if dup:
            fails.append(f"ID values repeated: {dup[:10]}")
    for pkg, lst in titles_by_pkg.items():
        dup = [t for t, k in Counter(t for _, t in lst).items() if k > 1]
        if dup:
            warns.append(f"duplicate titles in package {pkg or '(none)'}: {dup[:15]} - verified shells are intentional; confirm each")
    real_pkgs = {p for p in pkgs_seen if p}
    if len(real_pkgs) > 1 and any(split_prefix(nm)[0] == "" for nm in names):
        warns.append(f"{len(real_pkgs)} packages in the task file but unprefixed checklist names exist - names are project-global and collide")
    unused = [nm for nm in names if used[nm] == 0]
    if unused:
        warns.append(f"checklists defined but referenced by no task: {unused[:15]}")
    if a.index:
        with open(a.index, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        if rows and "Title" in rows[0]:
            k = rows[0].index("Title"); idx = [r[k].strip() for r in rows[1:] if len(r) > k and r[k].strip()]
        else:
            idx = [r[0].strip() for r in rows if r and r[0].strip()]
        titles = [t for _, lst in titles_by_pkg.items() for _, t in lst]
        missing, extra = sorted(set(idx) - set(titles)), sorted(set(titles) - set(idx))
        if len(idx) != len(titles):
            fails.append(f"row count {len(titles)} != index count {len(idx)}")
        if missing:
            fails.append(f"index marks with no task row: {missing[:20]}")
        if extra:
            warns.append(f"task rows not in the index (non-submittal openings?): {extra[:20]}")

    print(f"tasks: {len(trows)} rows, {len(used)} distinct checklists referenced; checklists: {len(names)} names, {len(crows)} items")
    for n_ in notes:
        print("NOTE ", n_)
    for w in warns:
        print("WARN ", w)
    for f_ in fails:
        print("FAIL ", f_)
    if fails or (a.strict and warns):
        print(f"\nNOT READY: {len(fails)} failure(s), {len(warns)} warning(s)")
        sys.exit(1)
    print(f"\nready for import: 0 failures, {len(warns)} warning(s)")


if __name__ == "__main__":
    main()
