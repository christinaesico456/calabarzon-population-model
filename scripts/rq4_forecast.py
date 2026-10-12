"""
rq4_forecast.py
RQ4: What population does the model project for 2030, 2040, and 2050
under different scenarios?

These are PROJECTIONS UNDER STATED ASSUMPTIONS, not predictions.
Every scenario starts from the latest census count and uses V2.

Scenarios (each changes one thing from the baseline):
  Baseline          calibrated r and K, average M (1970-2010)
  Lower fertility   births per person fall by SCENARIO_CHANGE:  r - SCENARIO_CHANGE * b
  Higher mortality  deaths per person rise by SCENARIO_CHANGE:  r - SCENARIO_CHANGE * d
  High migration    M = largest M per year observed in 1970-2010
Assumption: a change in b or d changes r by the same amount.

Outputs:
  results/rq4_scenarios.csv   scenario x year table
  results/rq4_scenarios.png   all scenarios on one plot

Run from the project folder:
  python -m scripts.rq4_forecast          real CALABARZON data
  python -m scripts.rq4_forecast --test   TEST VALUES files
"""

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.baseline import choose_mode, build_baseline, print_baseline, project
from src.plot_style import COLORS, DARK, GRAY, style_axes


PROJECTION_YEARS = [2030, 2040, 2050]

# PROVISIONAL (rule D5): size of the fertility and mortality changes.
# 0.10 means "10% fewer births per person" or "10% more deaths per person".
# The group must replace this with a value from a cited source.
SCENARIO_CHANGE = 0.10

mode = choose_mode()
baseline = build_baseline(mode)
print_baseline(baseline)

r = baseline["r"]
K = baseline["K"]
M = baseline["M"]
b = baseline["b"]
d = baseline["d"]
M_max = baseline["periods"]["M_per_year"].max()


# ------------------------------------------------------------
# Scenario parameters
# ------------------------------------------------------------
scenarios = [
    {"name": "Baseline",
     "description": "calibrated r and K, average M 1970-2010",
     "params": {"r": r, "K": K, "M": M}},
    {"name": "Lower fertility",
     "description": f"b lower by {SCENARIO_CHANGE:.0%}: r - {SCENARIO_CHANGE} x b",
     "params": {"r": r - SCENARIO_CHANGE * b, "K": K, "M": M}},
    {"name": "Higher mortality",
     "description": f"d higher by {SCENARIO_CHANGE:.0%}: r - {SCENARIO_CHANGE} x d",
     "params": {"r": r - SCENARIO_CHANGE * d, "K": K, "M": M}},
    {"name": "High migration",
     "description": "M = largest observed M per year, 1970-2010",
     "params": {"r": r, "K": K, "M": M_max}},
]


# ------------------------------------------------------------
# Projections
# ------------------------------------------------------------
rows = []
for scenario in scenarios:
    N = project(scenario["params"], baseline, PROJECTION_YEARS)

    row = {"scenario": scenario["name"],
           "description": scenario["description"],
           "r": scenario["params"]["r"],
           "K": scenario["params"]["K"],
           "M": scenario["params"]["M"]}
    for i in range(len(PROJECTION_YEARS)):
        row[f"N_{PROJECTION_YEARS[i]}"] = round(N[i])
    rows.append(row)

table = pd.DataFrame(rows)

# Difference from the baseline in the last projection year
last = f"N_{PROJECTION_YEARS[-1]}"
baseline_last = table.loc[0, last]
table[f"change_{PROJECTION_YEARS[-1]}_pct"] = np.round(
    (table[last] - baseline_last) / baseline_last * 100, 2)

print("RQ4: SCENARIO PROJECTIONS (projections under stated assumptions, not predictions)")
print(f"All scenarios start from the {baseline['latest_year']} census: "
      f"{baseline['latest_N']:,.0f} persons")
print()
header = f"{'Scenario':<18}{'r':>9}{'M':>11}"
for year in PROJECTION_YEARS:
    header = header + f"{year:>14}"
print(header + f"{'vs base':>10}")
print("-" * len(header + "          "))
for i in table.index:
    row = table.loc[i]
    line = f"{row['scenario']:<18}{row['r']:>9.5f}{row['M']:>11,.0f}"
    for year in PROJECTION_YEARS:
        line = line + f"{row[f'N_{year}']:>14,}"
    print(line + f"{row[f'change_{PROJECTION_YEARS[-1]}_pct']:>9.2f}%")
print()

os.makedirs("results", exist_ok=True)
table_path = "results/" + mode["prefix"] + "rq4_scenarios.csv"
table.to_csv(table_path, index=False)
print("Table saved to", table_path)


# ------------------------------------------------------------
# Graph: census points, then all scenarios from the latest census to 2050
# ------------------------------------------------------------
census = baseline["census"]
years = np.linspace(baseline["latest_decimal_year"], PROJECTION_YEARS[-1], 200)

fig, ax = plt.subplots(figsize=(9, 5.5))

ax.plot(census["decimal_year"], census["total"] / 1e6, "o", color=DARK, label="Census")

for i in range(len(scenarios)):
    N = project(scenarios[i]["params"], baseline, years)
    ax.plot(years, N / 1e6, color=COLORS[i], linewidth=2, label=scenarios[i]["name"])

# Dashed line where the projections start (the latest census)
ax.axvline(baseline["latest_decimal_year"], color=GRAY, linewidth=1, linestyle="--")
ax.set_xlim(census["decimal_year"].iloc[0] - 2, PROJECTION_YEARS[-1] + 2)
ax.set_xlabel("Year")
ax.set_ylabel("Population, N (millions of persons)")
ax.set_title(mode["label"] + f"RQ4: V2 projections to {PROJECTION_YEARS[-1]} under four scenarios\n"
             f"Purpose: compare scenarios (projections under stated assumptions, "
             f"not predictions)", fontsize=11)
ax.legend(loc="upper left", frameon=False, fontsize=9)
style_axes(ax)
fig.tight_layout()

graph_path = "results/" + mode["prefix"] + "rq4_scenarios.png"
fig.savefig(graph_path, dpi=150)
print("Graph saved to", graph_path)
