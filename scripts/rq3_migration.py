"""
rq3_migration.py
RQ3: How does net migration affect long-term population and equilibrium?

Method: keep the calibrated r and K, and run V2 with several values of M,
from 0 (no migration) up to the largest M per year observed in 1970-2010
(balancing equation). Each run starts from the latest census count.

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
from src.baseline import choose_mode, build_baseline, print_baseline, project
from src.plot_style import COLORS, DARK, GRAY, style_axes


END_YEAR = 2200       # long enough to see the population level off
NUMBER_OF_M = 5       # M values from 0 to the largest observed, evenly spaced

mode = choose_mode()
baseline = build_baseline(mode)
print_baseline(baseline)


# ------------------------------------------------------------
# M values: from 0 to the largest M per year observed in 1970-2010
# ------------------------------------------------------------
M_max = baseline["periods"]["M_per_year"].max()

if M_max <= 0:
    raise ValueError("No period with in-migration (M > 0) was observed, so the "
                     "range 0 to high in-migration cannot be set from the data.")

M_values = np.linspace(0, M_max, NUMBER_OF_M)


# ------------------------------------------------------------
# Equilibrium and long-term population for each M
# ------------------------------------------------------------
rows = []
for M in M_values:
    params = {"r": baseline["r"], "K": baseline["K"], "M": M}
    N_star = equilibrium_v2(params)
    N_2050, N_2100 = project(params, baseline, [2050, 2100])

    rows.append({
        "M_per_year": round(M),
        "equilibrium_N_star": round(N_star),
        "N_star_minus_K": round(N_star - baseline["K"]),
        "N_2050": round(N_2050),
        "N_2100": round(N_2100),
    })

table = pd.DataFrame(rows)

print("RQ3: NET MIGRATION VS EQUILIBRIUM (r and K fixed at calibrated values)")
print(f"K = {baseline['K']:,.0f} persons. With M = 0 the equilibrium is K; "
      f"with M > 0 it is above K.")
print()
print(f"{'M per year':>12}{'N*':>15}{'N* - K':>14}{'N in 2050':>15}{'N in 2100':>15}")
print("-" * 71)
for i in table.index:
    row = table.loc[i]
    print(f"{row['M_per_year']:>12,}{row['equilibrium_N_star']:>15,}{row['N_star_minus_K']:>14,}"
          f"{row['N_2050']:>15,}{row['N_2100']:>15,}")
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
            label=f"M = {M_values[i]:,.0f} per year")
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
