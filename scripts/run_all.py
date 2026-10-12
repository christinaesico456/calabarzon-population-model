"""
run_all.py
Step 16: runs every results script in order, so all tables (CSV) and
graphs (PNG) are saved to results/ with one command.

Run from the project folder:
  python -m scripts.run_all          real CALABARZON data
  python -m scripts.run_all --test   TEST VALUES files (outputs named results/TEST_*)

Each script runs as its own program (the same as typing python -m <name>),
and run_all stops at the first script that fails.
"""

import subprocess
import sys


SCRIPTS = [
    "scripts.net_migration",    # Step 10
    "scripts.rq1_validation",   # Step 12 (RQ1), includes calibration (Step 11)
    "scripts.rq2_sensitivity",  # Step 13 (RQ2)
    "scripts.rq3_migration",    # Step 14 (RQ3)
    "scripts.rq4_forecast",     # Step 15 (RQ4)
]

# Pass --test on to every script if run_all was given --test
extra = []
if "--test" in sys.argv:
    extra = ["--test"]

for name in SCRIPTS:
    # flush=True prints the header now, before the script's own output
    print("=" * 90)
    print("Running", name, " ".join(extra))
    print("=" * 90, flush=True)

    # sys.executable is the Python running this file (the .venv Python)
    result = subprocess.run([sys.executable, "-m", name] + extra)

    if result.returncode != 0:
        print()
        print("Stopped:", name, "did not finish (see the message above).")
        sys.exit(1)

    print()

print("All scripts finished. Tables and graphs are in results/.")
