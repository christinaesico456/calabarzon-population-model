"""
net_migration.py
Step 10: net migration for each period between two censuses, using the
balancing equation M = (Pop_end - Pop_start) - (Births - Deaths).

Outputs:
  results/net_migration_by_period.csv   table of every period
  results/net_migration_by_period.png   M per year for each period

Run from the project folder:
  python -m scripts.net_migration          real CALABARZON data
  python -m scripts.net_migration --test   TEST VALUES files
"""

import os

import matplotlib.pyplot as plt

from src.baseline import choose_mode, CALIBRATION_END_YEAR
from src.data_loader import load_census, load_vital_stats
from src.migration import net_migration_by_period, average_over_periods
from src.plot_style import COLORS, GRAY, style_axes


mode = choose_mode()
census = load_census(mode["census"])
vital = load_vital_stats(mode["vital"])

# All periods that have births and deaths for every year
periods = net_migration_by_period(census, vital)

if len(periods) == 0:
    raise SystemExit("No period has births and deaths for every year yet. "
                     "Enter them in " + mode["vital"] + " first.")


# ------------------------------------------------------------
# Table
# ------------------------------------------------------------
print("NET MIGRATION BY PERIOD (balancing equation)")
print(f"{'Period':<12}{'Years':>7}{'Pop change':>14}{'Births':>13}{'Deaths':>13}"
      f"{'Natural inc.':>14}{'M total':>13}{'M per year':>13}")
print("-" * 99)
for i in periods.index:
    row = periods.loc[i]
    # int(): pandas stores a mixed row as decimals, so 1970 would print as 1970.0
    period = f"{int(row['start_year'])}-{int(row['end_year'])}"
    print(f"{period:<12}{row['length_years']:>7.2f}"
          f"{row['pop_change']:>14,.0f}{row['births']:>13,.0f}{row['deaths']:>13,.0f}"
          f"{row['natural_increase']:>14,.0f}{row['M_total']:>13,.0f}{row['M_per_year']:>13,.0f}")
print()

# Averages over the calibration period only (these are used by the model)
in_calibration = periods[periods["end_year"] <= CALIBRATION_END_YEAR]
if len(in_calibration) > 0:
    rates = average_over_periods(in_calibration)
    print(f"Averages over periods ending by {CALIBRATION_END_YEAR} (used by the model):")
    print(f"  b = {rates['b']:.5f}, d = {rates['d']:.5f} per person per year")
    print(f"  M = {rates['M']:,.0f} persons per year")
    print()

os.makedirs("results", exist_ok=True)
table_path = "results/" + mode["prefix"] + "net_migration_by_period.csv"
periods.to_csv(table_path, index=False)
print("Table saved to", table_path)


# ------------------------------------------------------------
# Graph: M per year for each period (bar width = length of the period)
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))

for i in periods.index:
    row = periods.loc[i]
    ax.bar(row["start_year"], row["M_per_year"] / 1000,
           width=row["end_year"] - row["start_year"], align="edge",
           color=COLORS[0], edgecolor="white")

ax.axhline(0, color=GRAY, linewidth=1)
ax.set_xlabel("Census period (calendar year)")
ax.set_ylabel("Net migration, M (thousands of persons per year)")
ax.set_title(mode["label"] + "Net migration per year by census period (balancing equation)\n"
             "Purpose: show how much of the growth came from migration, and how M changed",
             fontsize=11)
style_axes(ax)
fig.tight_layout()

graph_path = "results/" + mode["prefix"] + "net_migration_by_period.png"
fig.savefig(graph_path, dpi=150)
print("Graph saved to", graph_path)
