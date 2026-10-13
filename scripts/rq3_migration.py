"""
rq3_migration.py
RQ3: How does net migration affect long-term population and equilibrium?

Method: keep the calibrated r and K, and run V2 with several values of M.
Each run starts from the latest census count. The M values are:
  - the fitted M (the model baseline; a fitting number, see Option A)
  - 0 (no migration)
  - the observed M of the latest census period and of the period with the
    highest M (balancing equation, PSA data): 2020-2024 and 2015-2020
Option A (PROVISIONAL): r and K come from the census fit; the observed M
values are real-data migration levels put on top of them ("what if").

For each M, the equilibrium is N* = (K/2) [1 + sqrt(1 + 4M/(rK))]
(the population where growth stops, dN/dt = 0).

The long runs (to 2200) show where the population levels off. They are
NOT forecasts: they show what the equation does if r, K, and M stay fixed.

Outputs:
  results/rq3_migration_equilibrium.csv   M vs equilibrium table
  results/rq3_migration.png               trajectories for each M

Run from the project folder:
  python -m scripts.rq3_migration          real CALABARZON data
  python -m scripts.rq3_migration --test   TEST VALUES files
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.exact import equilibrium_v2
from src.baseline import choose_mode, build_baseline, print_baseline, project, observed_migration
from src.plot_style import COLORS, DARK, GRAY, style_axes


END_YEAR = 2200       # long enough to see the population level off

mode = choose_mode()
baseline = build_baseline(mode)
print_baseline(baseline)


# ------------------------------------------------------------
# M values: fitted M, no migration, and each observed period
# ------------------------------------------------------------
observed = observed_migration(mode, baseline)


def period_name(i):
    """Census period of row i of the observed table, e.g. '2015-2020'."""
    return f"{int(observed.loc[i, 'start_year'])}-{int(observed.loc[i, 'end_year'])}"


# The latest observed period, and the period with the highest M
latest = observed.index[-1]
highest = observed["M_per_year"].idxmax()

M_values = [baseline["M"], 0, observed.loc[latest, "M_per_year"]]
M_labels = ["fitted M (model baseline)", "no migration",
            f"observed {period_name(latest)} (PSA)"]

if highest != latest:
    M_values.append(observed.loc[highest, "M_per_year"])
    M_labels.append(f"observed {period_name(highest)} (PSA)")


# ------------------------------------------------------------
# Equilibrium and long-term population for each M
# ------------------------------------------------------------
rows = []
for i in range(len(M_values)):
    M = M_values[i]
    params = {"r": baseline["r"], "K": baseline["K"], "M": M}
    N_star = equilibrium_v2(params)
    N_2050, N_2100 = project(params, baseline, [2050, 2100])

    rows.append({
        "case": M_labels[i],
        "M_per_year": round(M),
        "equilibrium_N_star": round(N_star),
        "N_star_minus_K": round(N_star - baseline["K"]),
        "N_2050": round(N_2050),
        "N_2100": round(N_2100),
    })

table = pd.DataFrame(rows)

print("RQ3: NET MIGRATION VS EQUILIBRIUM (r and K fixed at calibrated values)")
print(f"K = {baseline['K']:,.0f} persons. With M = 0 the equilibrium is K; "
      f"with M > 0 it is above K, with M < 0 below K.")
print()
print(f"{'Case':<30}{'M per year':>12}{'N*':>15}{'N* - K':>14}{'N in 2050':>15}{'N in 2100':>15}")
print("-" * 101)
for i in table.index:
    row = table.loc[i]
    print(f"{row['case']:<30}{row['M_per_year']:>12,}{row['equilibrium_N_star']:>15,}"
          f"{row['N_star_minus_K']:>14,}{row['N_2050']:>15,}{row['N_2100']:>15,}")
print()

os.makedirs("results", exist_ok=True)
table_path = "results/" + mode["prefix"] + "rq3_migration_equilibrium.csv"
table.to_csv(table_path, index=False)
print("Table saved to", table_path)


# ------------------------------------------------------------
# Graph: one trajectory per M, with its equilibrium as a dashed line
# ------------------------------------------------------------
census = baseline["census"]
years = np.linspace(baseline["latest_decimal_year"], END_YEAR, 400)

fig, ax = plt.subplots(figsize=(9.5, 5.5))

for i in range(len(M_values)):
    params = {"r": baseline["r"], "K": baseline["K"], "M": M_values[i]}
    N = project(params, baseline, years)
    N_star = equilibrium_v2(params)

    ax.plot(years, N / 1e6, color=COLORS[i], linewidth=2,
            label=f"M = {M_values[i]:,.0f} per year, {M_labels[i]}")
    ax.hlines(N_star / 1e6, years[0], END_YEAR, color=COLORS[i], linewidth=1, linestyle="--")
    ax.text(END_YEAR + 2, N_star / 1e6, f"N* = {N_star / 1e6:.2f} M",
            va="center", fontsize=8, color=GRAY)

ax.plot(census["decimal_year"], census["total"] / 1e6, "o", color=DARK, label="Census")

ax.set_xlim(census["decimal_year"].iloc[0] - 2, END_YEAR + 25)
ax.set_xlabel("Year")
ax.set_ylabel("Population, N (millions of persons)")
ax.set_title(mode["label"] + "RQ3: Effect of net migration M on V2 (r and K fixed)\n"
             "Purpose: each run levels off at its equilibrium N* (dashed); "
             "long-term behavior, not a forecast", fontsize=11)
ax.legend(loc="lower right", frameon=False, fontsize=9)
style_axes(ax)
fig.tight_layout()

graph_path = "results/" + mode["prefix"] + "rq3_migration.png"
fig.savefig(graph_path, dpi=150)
print("Graph saved to", graph_path)
