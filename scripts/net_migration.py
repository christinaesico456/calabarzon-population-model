"""
net_migration.py
Optional check of the fitted M, using the balancing equation:

    M = (Pop_end - Pop_start) - (Births - Deaths)

for each census period whose births and deaths were entered for every year.
Births and deaths for 1970 to 2003 are not available online, so this can only
be done from about 2010 onward. The model itself does NOT use these values:
M is fitted from the census (see src/calibration.py). This script only checks
whether the fitted M is reasonable.

Outputs (only if at least one period has births and deaths):
  results/net_migration_check.csv   balancing equation M for each period
  results/net_migration_check.png   balancing equation M vs fitted M

Run from the project folder:
  python -m scripts.net_migration          real CALABARZON data
  python -m scripts.net_migration --test   TEST VALUES files
"""

import os
import sys

import matplotlib.pyplot as plt

from src.baseline import choose_mode, build_baseline
from src.data_loader import load_vital_stats
from src.migration import net_migration_by_period
from src.plot_style import COLORS, GRAY, style_axes


mode = choose_mode()
baseline = build_baseline(mode)
census = baseline["census"]
vital = load_vital_stats(mode["vital"])

# All periods that have births and deaths for every year
periods = net_migration_by_period(census, vital)

if len(periods) == 0:
    print("No census period has births and deaths for every year yet, so the")
    print("check of the fitted M is skipped. (This check is optional.)")
    # exit code 0 = finished normally, so run_all continues
    sys.exit(0)


# ------------------------------------------------------------
# Table: balancing equation M vs fitted M
# ------------------------------------------------------------
M_fitted = baseline["M"]

print("CHECK OF THE FITTED M (balancing equation, periods with births and deaths)")
print(f"Fitted M (1970-2010 census): {M_fitted:,.0f} persons per year")
print()
print(f"{'Period':<12}{'Years':>7}{'Pop change':>14}{'Births':>13}{'Deaths':>13}"
      f"{'M per year':>13}{'minus fitted M':>16}")
print("-" * 88)
for i in periods.index:
    row = periods.loc[i]
    # int(): pandas stores a mixed row as decimals, so 2010 would print as 2010.0
    period = f"{int(row['start_year'])}-{int(row['end_year'])}"
    # Difference in persons per year (a percent would be confusing if M_fitted < 0)
    difference = row["M_per_year"] - M_fitted
    print(f"{period:<12}{row['length_years']:>7.2f}"
          f"{row['pop_change']:>14,.0f}{row['births']:>13,.0f}{row['deaths']:>13,.0f}"
          f"{row['M_per_year']:>13,.0f}{difference:>16,.0f}")
print()

os.makedirs("results", exist_ok=True)
table_path = "results/" + mode["prefix"] + "net_migration_check.csv"
periods.to_csv(table_path, index=False)
print("Table saved to", table_path)


# ------------------------------------------------------------
# Graph: balancing equation M per period (bars) vs fitted M (dashed line)
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))

for i in periods.index:
    row = periods.loc[i]
    ax.bar(row["start_year"], row["M_per_year"] / 1000,
           width=row["end_year"] - row["start_year"], align="edge",
           color=COLORS[0], edgecolor="white",
           label="Balancing equation (births and deaths)" if i == periods.index[0] else None)

ax.axhline(M_fitted / 1000, color=COLORS[1], linewidth=2, linestyle="--",
           label="Fitted M (1970-2010 census)")
ax.axhline(0, color=GRAY, linewidth=1)
ax.set_xlabel("Census period (calendar year)")
ax.set_ylabel("Net migration, M (thousands of persons per year)")
ax.set_title(mode["label"] + "Check of the fitted net migration M\n"
             "Purpose: is the M fitted from the census close to the M from births and deaths?",
             fontsize=11)
ax.legend(loc="lower right", frameon=False)
style_axes(ax)
fig.tight_layout()

graph_path = "results/" + mode["prefix"] + "net_migration_check.png"
fig.savefig(graph_path, dpi=150)
print("Graph saved to", graph_path)
