"""
rq2_sensitivity.py
RQ2: Which parameter (r, K, M) most affects the projected 2050 population?

Method: one parameter at a time. Each parameter is set to a low and a high
value while the other two stay at their baseline values. All projections
start from the latest census count.

Ranges (PROVISIONAL rule D4, based on the data, not picked by hand):
  r, K : calibrated value +/- 2 standard errors from curve_fit
         (about a 95% range of values the 1970-2010 census allows)
  M    : smallest and largest M per year observed in the 1970-2010 periods
         (balancing equation)

Outputs:
  results/rq2_sensitivity.csv   Low / Baseline / High / % change table
  results/rq2_tornado.png       tornado chart of % change in the 2050 population

Run from the project folder:
  python -m scripts.rq2_sensitivity          real CALABARZON data
  python -m scripts.rq2_sensitivity --test   TEST VALUES files
"""

import os

import pandas as pd
import matplotlib.pyplot as plt

from src.baseline import choose_mode, build_baseline, print_baseline, project
from src.plot_style import COLORS, GRAY, style_axes


TARGET_YEAR = 2050

mode = choose_mode()
baseline = build_baseline(mode)
print_baseline(baseline)

baseline_params = {"r": baseline["r"], "K": baseline["K"], "M": baseline["M"]}


# ------------------------------------------------------------
# Low and high value for each parameter (rule D4)
# ------------------------------------------------------------
periods = baseline["periods"]

ranges = [
    {"parameter": "r",
     "low": baseline["r"] - 2 * baseline["r_se"],
     "high": baseline["r"] + 2 * baseline["r_se"],
     "basis": "calibrated r +/- 2 standard errors"},
    {"parameter": "K",
     "low": baseline["K"] - 2 * baseline["K_se"],
     "high": baseline["K"] + 2 * baseline["K_se"],
     "basis": "calibrated K +/- 2 standard errors"},
    {"parameter": "M",
     "low": periods["M_per_year"].min(),
     "high": periods["M_per_year"].max(),
     "basis": "smallest and largest observed M per year, 1970-2010"},
]

# r and K must stay positive, otherwise the model has no meaning
for item in ranges:
    if item["parameter"] in ["r", "K"] and item["low"] <= 0:
        raise ValueError(f"Low {item['parameter']} is not positive ({item['low']}): the "
                         f"standard error is too large for the +/- 2 standard error rule. "
                         f"Choose and justify another range.")


# ------------------------------------------------------------
# Projected population in the target year for each case
# ------------------------------------------------------------
N_baseline = project(baseline_params, baseline, [TARGET_YEAR])[0]

rows = []
for item in ranges:
    name = item["parameter"]

    # Copy the baseline, then change only this one parameter
    params_low = dict(baseline_params)
    params_low[name] = item["low"]
    params_high = dict(baseline_params)
    params_high[name] = item["high"]

    N_low = project(params_low, baseline, [TARGET_YEAR])[0]
    N_high = project(params_high, baseline, [TARGET_YEAR])[0]

    change_low = (N_low - N_baseline) / N_baseline * 100
    change_high = (N_high - N_baseline) / N_baseline * 100

    rows.append({
        "parameter": name,
        "low_value": item["low"],
        "baseline_value": baseline_params[name],
        "high_value": item["high"],
        "range_basis": item["basis"],
        f"N{TARGET_YEAR}_low": round(N_low),
        f"N{TARGET_YEAR}_baseline": round(N_baseline),
        f"N{TARGET_YEAR}_high": round(N_high),
        "change_low_pct": round(change_low, 3),
        "change_high_pct": round(change_high, 3),
        "swing_pct": round(abs(change_high - change_low), 3),
    })

# Largest swing first: this parameter affects the target year the most
table = pd.DataFrame(rows).sort_values("swing_pct", ascending=False)

print(f"RQ2: SENSITIVITY OF THE {TARGET_YEAR} POPULATION (projection under stated assumptions)")
print(f"Baseline {TARGET_YEAR} projection: {N_baseline:,.0f} persons")
print()
def format_value(name, value):
    """r is a small rate (5 decimals); K and M are persons (whole numbers with commas)."""
    if name == "r":
        return f"{value:.5f}"
    return f"{value:,.0f}"


print(f"{'Param':<7}{'Low value':>14}{'High value':>14}{'N low':>14}{'N high':>14}"
      f"{'% low':>9}{'% high':>9}{'Swing %':>9}")
print("-" * 90)
for i in table.index:
    row = table.loc[i]
    low_text = format_value(row["parameter"], row["low_value"])
    high_text = format_value(row["parameter"], row["high_value"])
    print(f"{row['parameter']:<7}{low_text:>14}{high_text:>14}"
          f"{row[f'N{TARGET_YEAR}_low']:>14,.0f}{row[f'N{TARGET_YEAR}_high']:>14,.0f}"
          f"{row['change_low_pct']:>9.3f}{row['change_high_pct']:>9.3f}{row['swing_pct']:>9.3f}")
print()
print("Most influential parameter (largest swing):", table.iloc[0]["parameter"])
print()

os.makedirs("results", exist_ok=True)
table_path = "results/" + mode["prefix"] + "rq2_sensitivity.csv"
table.to_csv(table_path, index=False)
print("Table saved to", table_path)


# ------------------------------------------------------------
# Tornado chart: largest swing at the top
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.5))

# barh draws from the bottom up, so reverse the order to put the largest on top
tornado = table.iloc[::-1].reset_index(drop=True)
for i in tornado.index:
    row = tornado.loc[i]
    ax.barh(i, row["change_low_pct"], color=COLORS[0], height=0.5,
            label="Low value" if i == 0 else None)
    ax.barh(i, row["change_high_pct"], color=COLORS[1], height=0.5,
            label="High value" if i == 0 else None)

ax.set_yticks(range(len(tornado)))
ax.set_yticklabels([f"{p}\n({b})" for p, b in zip(tornado["parameter"], tornado["range_basis"])],
                   fontsize=8)
ax.axvline(0, color=GRAY, linewidth=1)
ax.set_xlabel(f"Change in projected {TARGET_YEAR} population from baseline (%)")
# suptitle centers the title on the whole figure, so the long
# parameter labels on the left do not push it off the right edge
fig.suptitle(mode["label"] + f"RQ2: Sensitivity of the projected {TARGET_YEAR} population "
             f"(one parameter at a time)\nPurpose: the longest bar is the parameter "
             f"that matters most (projection, not prediction)", fontsize=11)
ax.legend(loc="lower right", frameon=False)
style_axes(ax)
fig.tight_layout()

graph_path = "results/" + mode["prefix"] + "rq2_tornado.png"
fig.savefig(graph_path, dpi=150)
print("Graph saved to", graph_path)
