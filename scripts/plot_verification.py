"""
plot_verification.py
Graph of Euler's relative error over time, compared with the exact solutions.
All parameter values are TEST VALUES (the same ones used in tests/verify.py).

Purpose:
1. Show how Euler's error changes over an 80-year run.
2. Show that halving dt halves the error (Euler is a first-order method).

Run from the project folder:  python -m scripts.plot_verification
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from src.models import rate_v1, rate_v2
from src.solvers import euler_solve
from src.exact import exact_v1, exact_logistic


# ------------------------------------------------------------
# TEST VALUES ONLY (same as tests/verify.py, not CALABARZON data)
# ------------------------------------------------------------
T_END = 80                                      # years (same length as 1970 to 2050)
dt_values = [0.1, 0.05]                         # time steps to compare (years)

params_v1 = {"b": 0.025, "d": 0.006}            # V1 birth and death rates (1/year)
N0_v1 = 1000000                                 # V1 starting population (persons)

params_logistic = {"r": 0.05, "K": 20000000, "M": 0}   # V2 with no migration
N0_logistic = 5000000                                  # starting population (persons)

# One color per time step, the same in both panels
colors = ["#2a78d6", "#eb6834"]


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def relative_error_percent(N_numeric, N_exact):
    """Euler minus exact, as a percent of exact (negative = Euler too low)."""
    return (N_numeric - N_exact) / N_exact * 100


def plot_error_line(ax, t, error, color, label):
    """Draw one error line and mark its largest gap from the exact solution."""
    ax.plot(t, error, color=color, linewidth=2, label=label)

    # Mark the largest gap (either sign) on the line
    k = np.argmax(np.abs(error))   # position of the largest gap
    ax.plot(t[k], error[k], "o", color=color, markersize=5, clip_on=False)

    # Put the label below a negative point and above a positive point
    if error[k] < 0:
        vertical = "top"
    else:
        vertical = "bottom"

    # Put the label on the side of the point that has more room
    if t[k] < T_END / 2:
        horizontal = "left"
    else:
        horizontal = "right"

    ax.text(t[k], error[k], f"  largest gap {error[k]:.3f}%  ",
            va=vertical, ha=horizontal, fontsize=9, color="#52514e")


def style_axes(ax, title):
    """Same labels and light styling for both panels."""
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("Time since start, t (years)")
    ax.set_ylabel("Euler minus exact (% of exact)")
    ax.set_xlim(0, T_END)

    # Zero line: Euler equals the exact solution
    ax.axhline(0, color="#898781", linewidth=1)

    ax.grid(color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="best", frameon=False)


# ------------------------------------------------------------
# Run Euler with each dt and compare with the exact solutions
# ------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))

for i in range(len(dt_values)):
    dt = dt_values[i]

    # Panel (a): V1 vs exact exponential
    t, N = euler_solve(rate_v1, N0_v1, params_v1, T_END, dt)
    error = relative_error_percent(N, exact_v1(t, N0_v1, params_v1))
    plot_error_line(ax1, t, error, colors[i], f"Euler, dt = {dt}")

    # Panel (b): logistic (V2 with M = 0) vs exact logistic
    t, N = euler_solve(rate_v2, N0_logistic, params_logistic, T_END, dt)
    error = relative_error_percent(N, exact_logistic(t, N0_logistic, params_logistic))
    plot_error_line(ax2, t, error, colors[i], f"Euler, dt = {dt}")

style_axes(ax1, "(a) V1 birth-death (b = 0.025, d = 0.006)")
style_axes(ax2, "(b) V2 logistic, M = 0 (r = 0.05, K = 20 million)")

fig.suptitle("TEST VALUES ONLY: Euler error relative to the exact solution over 80 years\n"
             "Purpose: halving dt should halve the error (Euler is first-order)",
             fontsize=11)
fig.tight_layout()

# Save the graph (create the results folder if it does not exist yet)
os.makedirs("results", exist_ok=True)
fig.savefig("results/TEST_verification_error.png", dpi=150)
print("Graph saved to results/TEST_verification_error.png")
