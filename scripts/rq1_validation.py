"""
rq1_validation.py
RQ1: How accurately do V1 and V2 reproduce CALABARZON's census population
from 2015 to 2024?

Both models start from the first census (1970) and run forward:
  V1: dN/dt = (b - d) N            b, d from vital statistics (rule D2)
  V2: dN/dt = r N (1 - N/K) + M    r, K calibrated on 1970-2010, M fixed (rule D3)
Census years up to 2010 were used to fit the models ("calibration").
Census years after 2010 were NOT used, so they test the models ("validation").

Outputs:
  results/rq1_observed_vs_simulated.csv   observed vs simulated, every census year
  results/rq1_error_measures.csv          RMSE and MAPE
  results/rq1_validation.png              census points vs model lines

Run from the project folder:
  python -m scripts.rq1_validation          real CALABARZON data
  python -m scripts.rq1_validation --test   TEST VALUES files
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.models import rate_v1, rate_v2
from src.solvers import solve_at_times
from src.calibration import rmse, mape
from src.baseline import choose_mode, build_baseline, print_baseline, CALIBRATION_END_YEAR, DT
from src.plot_style import COLORS, DARK, GRAY, style_axes


mode = choose_mode()
baseline = build_baseline(mode)
print_baseline(baseline)

census = baseline["census"]
params_v1 = {"b": baseline["b"], "d": baseline["d"]}
params_v2 = {"r": baseline["r"], "K": baseline["K"], "M": baseline["M"]}


# ------------------------------------------------------------
# Observed vs simulated at every census date
# ------------------------------------------------------------
t_census = census["t"].to_numpy()
observed = census["total"].to_numpy()

N_v1 = solve_at_times(rate_v1, baseline["N0"], params_v1, t_census, DT)
N_v2 = solve_at_times(rate_v2, baseline["N0"], params_v2, t_census, DT)

table = pd.DataFrame({
    "year": census["year"],
    "used_for": np.where(census["year"] <= CALIBRATION_END_YEAR, "calibration", "validation"),
    "observed": observed,
    "V1_simulated": np.round(N_v1),
    "V1_error_pct": np.round((N_v1 - observed) / observed * 100, 2),
    "V2_simulated": np.round(N_v2),
    "V2_error_pct": np.round((N_v2 - observed) / observed * 100, 2),
})

print("RQ1: OBSERVED VS SIMULATED (error % = simulated minus observed, as % of observed)")
print(table.to_string(index=False))
print()


# ------------------------------------------------------------
# Error measures, separately for calibration and validation years
# ------------------------------------------------------------
error_rows = []
for used_for in ["calibration", "validation"]:
    rows = table["used_for"] == used_for

    if rows.sum() == 0:
        print(f"Note: no {used_for} census years entered yet, so no {used_for} error measures.")
        continue

    for model, column in [("V1", "V1_simulated"), ("V2", "V2_simulated")]:
        error_rows.append({
            "years": used_for,
            "model": model,
            "RMSE_persons": round(rmse(table.loc[rows, "observed"], table.loc[rows, column])),
            "MAPE_pct": round(mape(table.loc[rows, "observed"], table.loc[rows, column]), 2),
        })

errors = pd.DataFrame(error_rows)
print("RQ1: ERROR MEASURES (validation rows answer RQ1)")
print(errors.to_string(index=False))
print()

os.makedirs("results", exist_ok=True)
table.to_csv("results/" + mode["prefix"] + "rq1_observed_vs_simulated.csv", index=False)
errors.to_csv("results/" + mode["prefix"] + "rq1_error_measures.csv", index=False)
print("Tables saved to results/" + mode["prefix"] + "rq1_*.csv")


# ------------------------------------------------------------
# Graph: census points vs model lines
# ------------------------------------------------------------
t_line = np.linspace(0, t_census[-1] + 1, 300)
years_line = t_line + baseline["start_decimal_year"]
census_years = census["decimal_year"].to_numpy()
is_calibration = census["year"].to_numpy() <= CALIBRATION_END_YEAR

fig, ax = plt.subplots(figsize=(9, 5.5))

ax.plot(years_line, solve_at_times(rate_v1, baseline["N0"], params_v1, t_line, DT) / 1e6,
        color=COLORS[1], linewidth=2, label="V1 birth-death (b, d from vital statistics)")
ax.plot(years_line, solve_at_times(rate_v2, baseline["N0"], params_v2, t_line, DT) / 1e6,
        color=COLORS[0], linewidth=2, label="V2 logistic + migration (r, K calibrated)")

ax.plot(census_years[is_calibration], observed[is_calibration] / 1e6, "o",
        color=DARK, label="Census, used for calibration")
ax.plot(census_years[~is_calibration], observed[~is_calibration] / 1e6, "o",
        markerfacecolor="white", color=DARK, markeredgewidth=1.5,
        label="Census, used for validation only")

# Line between the calibration and validation years
last_calibration_date = census_years[is_calibration][-1]
ax.axvline(last_calibration_date, color=GRAY, linewidth=1, linestyle="--")
ax.text(last_calibration_date + 0.5, ax.get_ylim()[1] * 0.97,
        "validation", va="top", fontsize=9, color=GRAY)
ax.text(last_calibration_date - 0.5, ax.get_ylim()[1] * 0.97,
        "calibration", va="top", ha="right", fontsize=9, color=GRAY)

ax.set_xlabel("Year")
ax.set_ylabel("Population, N (millions of persons)")
ax.set_title(mode["label"] + "RQ1: Census population vs V1 and V2 (Euler, dt = 0.1)\n"
             "Purpose: how closely each model reproduces the census, "
             "especially the years not used for fitting", fontsize=11)
ax.legend(loc="upper left", frameon=False, fontsize=9, bbox_to_anchor=(0, 0.92))
style_axes(ax)
fig.tight_layout()

graph_path = "results/" + mode["prefix"] + "rq1_validation.png"
fig.savefig(graph_path, dpi=150)
print("Graph saved to", graph_path)
