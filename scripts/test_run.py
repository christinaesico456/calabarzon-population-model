"""
test_run.py
First test run of the models using TEST VALUES (not CALABARZON data).

Purpose:
1. Check that Euler and RK4 run correctly against the exact logistic solution.
2. Show how net migration M changes where V2 levels off (equilibrium N*).

Run from the project folder:  python -m scripts.test_run
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from src.models import rate_v2
from src.solvers import euler_solve, rk4_solve
from src.exact import exact_logistic, equilibrium_v2


# ------------------------------------------------------------
# TEST VALUES ONLY (not CALABARZON data)
# ------------------------------------------------------------
N0 = 5000000      # starting population (persons)
r = 0.05          # intrinsic growth rate (1/year)
K = 20000000      # carrying capacity (persons)
t_end = 200       # length of the run (years)
dt = 0.1          # time step (years)

# Three migration cases (persons/year): none, in-migration, out-migration
M_values = [0, 100000, -100000]


# ------------------------------------------------------------
# Part 1: Solver check with M = 0 (the only case with an exact solution)
# ------------------------------------------------------------
params = {"r": r, "K": K, "M": 0}

t, N_euler = euler_solve(rate_v2, N0, params, t_end, dt)
t, N_rk4 = rk4_solve(rate_v2, N0, params, t_end, dt)
N_exact = exact_logistic(t, N0, params)

# Largest gap from the exact solution over the whole run (persons)
max_error_euler = np.max(np.abs(N_euler - N_exact))
max_error_rk4 = np.max(np.abs(N_rk4 - N_exact))

print("=== TEST VALUES: solver check (V2 with M = 0) ===")
print("Largest Euler error:", round(max_error_euler, 1), "persons")
print("Largest RK4 error:  ", max_error_rk4, "persons")
print()


# ------------------------------------------------------------
# Part 2: Effect of migration on the equilibrium (Euler)
# ------------------------------------------------------------
print("=== TEST VALUES: equilibrium check (after", t_end, "years) ===")
print("M (persons/yr) | N* formula | N simulated | difference")

# One color per migration case
colors = ["#2a78d6", "#eb6834", "#1baf7a"]
labels = ["M = 0 (no migration)",
          "M = +100,000 per year (in-migration)",
          "M = -100,000 per year (out-migration)"]

fig, ax = plt.subplots(figsize=(9, 5.5))

for i in range(len(M_values)):
    params = {"r": r, "K": K, "M": M_values[i]}

    t, N = euler_solve(rate_v2, N0, params, t_end, dt)
    N_star = equilibrium_v2(params)

    print(M_values[i], "|", round(N_star), "|", round(N[-1]), "|", round(N[-1] - N_star))

    # Population curve, in millions of persons for readability
    ax.plot(t, N / 1e6, color=colors[i], linewidth=2, label=labels[i])

    # Dashed line at the equilibrium from the formula (from t = 0 to t_end)
    ax.hlines(N_star / 1e6, 0, t_end, color=colors[i], linewidth=1, linestyle="--")

    # Label the dashed line just after its right end (2 decimal places)
    ax.text(t_end + 3, N_star / 1e6, f"N* = {N_star / 1e6:.2f} M",
            va="center", fontsize=9, color="#52514e")

# Axes, units, and purpose
ax.set_xlabel("Time since start, t (years)")
ax.set_ylabel("Population, N (millions of persons)")
ax.set_title("TEST VALUES ONLY: V2 logistic growth with net migration (Euler, dt = 0.1)\n"
             "Purpose: each run should level off at its equilibrium N* (dashed lines)",
             fontsize=11)
ax.set_xlim(0, t_end + 30)
ax.set_ylim(0, 25)

# Light, solid gridlines behind the data
ax.grid(color="#e1e0d9", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(loc="lower right", frameon=False)
fig.tight_layout()

# Save the graph (create the results folder if it does not exist yet)
os.makedirs("results", exist_ok=True)
fig.savefig("results/TEST_v2_migration.png", dpi=150)
print()
print("Graph saved to results/TEST_v2_migration.png")