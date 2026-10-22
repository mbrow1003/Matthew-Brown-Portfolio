#!/usr/bin/env python3
"""validate_import.py must pass the clean pair and name every planted fault in the broken pair."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(os.path.dirname(HERE), "scripts", "validate_import.py")
def run(t, c):
    p = subprocess.run([sys.executable, V, "--tasks", os.path.join(HERE, t), "--checklists", os.path.join(HERE, c)], capture_output=True, text=True)
    return p.returncode, p.stdout
rc, out = run("good_tasks.csv", "good_checklists.csv")
fails = [] if rc == 0 and "0 failures, 0 warning" in out else ["clean pair did not pass: " + out]
rc, out = run("bad_tasks.csv", "bad_checklists.csv")
if rc == 0:
    fails.append("broken pair passed")
for must in ("trailing whitespace", "no per-opening quantity", "no product number", "both unprefixed and prefixed",
             "blank Description", "outside 0-100", "carries a checklist", "lacks #hw-tbd", "one pin axis blank",
             "is not a number", "ID values repeated", "flagged 'total'", "duplicate titles", "unprefixed checklist names exist"):
    if must not in out:
        fails.append(f"broken pair: finding missing: {must!r}")
print("\n".join(fails) if fails else "all validator checks pass"); sys.exit(1 if fails else 0)
