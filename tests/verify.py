"""
verify.py
Verification tests: does the code solve the equations correctly?
All parameter values in this file are TEST VALUES (not CALABARZON data).

Each test returns one row: [test name, expected result, actual result, status]

Run from the project folder:  python -m tests.verify
"""

import numpy as np

from src.models import rate_v1, rate_v2
from src.solvers import euler_solve, rk4_solve
from src.exact import exact_v1, exact_logistic, equilibrium_v2


# ------------------------------------------------------------
# Settings shared by all tests
# ------------------------------------------------------------
T_END = 80          # years (same length as 1970 to 2050)
DT = 0.1            # time step (years)
TOLERANCE = 0.005   # largest allowed relative error (0.5%)

# Only for the equilibrium test: long enough for the run to settle at N*.
# This is NOT a projection period. With M < 0 the approach is slow
# (still 0.0036% away after 300 years), so we use 500 years.
T_LONG = 500


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def max_relative_error(N_numeric, N_exact):
    """Largest error over the whole run, as a fraction of the exact value."""
    return np.max(np.abs(N_numeric - N_exact) / N_exact)


def pass_or_fail(condition):
    """Turn True/False into the text PASS/FAIL for the table."""
    if condition:
        return "PASS"
    else:
        return "FAIL"


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------
def test_euler_vs_exact_v1():
    """Euler solution of V1 should match the exact exponential formula."""
    params = {"b": 0.025, "d": 0.006}   # TEST VALUES
    N0 = 1000000                        # TEST VALUE

    t, N_euler = euler_solve(rate_v1, N0, params, T_END, DT)
    N_exact = exact_v1(t, N0, params)
    error = max_relative_error(N_euler, N_exact)

    return ["Euler vs exact (V1)",
            "max relative error < 0.5%",
            f"{error * 100:.4f}%",
            pass_or_fail(error < TOLERANCE)]


def test_euler_vs_exact_logistic():
    """
    Euler solution of V2 with M = 0 should match the exact logistic formula.
    This also covers the property "M = 0 reduces to logistic".
    """
    params = {"r": 0.05, "K": 20000000, "M": 0}   # TEST VALUES
    N0 = 5000000                                 # TEST VALUE

    t, N_euler = euler_solve(rate_v2, N0, params, T_END, DT)
    N_exact = exact_logistic(t, N0, params)
    error = max_relative_error(N_euler, N_exact)

    return ["Euler vs exact (logistic, M = 0)",
            "max relative error < 0.5%",
            f"{error * 100:.4f}%",
            pass_or_fail(error < TOLERANCE)]


def test_error_halves_with_dt():
    """Euler is first-order: halving dt should halve the error (ratio about 2)."""
    params = {"b": 0.025, "d": 0.006}   # TEST VALUES
    N0 = 1000000                        # TEST VALUE

    # Run with dt and with dt / 2
    t1, N1 = euler_solve(rate_v1, N0, params, T_END, DT)
    t2, N2 = euler_solve(rate_v1, N0, params, T_END, DT / 2)

    error_full = max_relative_error(N1, exact_v1(t1, N0, params))
    error_half = max_relative_error(N2, exact_v1(t2, N0, params))
    ratio = error_full / error_half

    return ["Error halves when dt is halved",
            "error ratio between 1.8 and 2.2",
            f"{ratio:.4f}",
            pass_or_fail(1.8 <= ratio <= 2.2)]


def test_rk4_vs_exact_v1():
    """RK4 solution of V1 should match the exact exponential formula."""
    params = {"b": 0.025, "d": 0.006}   # TEST VALUES
    N0 = 1000000                        # TEST VALUE

    t, N_rk4 = rk4_solve(rate_v1, N0, params, T_END, DT)
    N_exact = exact_v1(t, N0, params)
    error = max_relative_error(N_rk4, N_exact)

    return ["RK4 vs exact (V1)",
            "max relative error < 0.5%",
            f"{error * 100:.2e}%",
            pass_or_fail(error < TOLERANCE)]


def test_euler_vs_rk4_with_migration():
    """With M not 0 there is no exact formula, so RK4 is the reference."""
    params = {"r": 0.05, "K": 20000000, "M": 100000}   # TEST VALUES
    N0 = 5000000                                      # TEST VALUE

    t, N_euler = euler_solve(rate_v2, N0, params, T_END, DT)
    t, N_rk4 = rk4_solve(rate_v2, N0, params, T_END, DT)
    difference = max_relative_error(N_euler, N_rk4)

    return ["Euler vs RK4 (V2, M = +100,000)",
            "max relative difference < 0.5%",
            f"{difference * 100:.4f}%",
            pass_or_fail(difference < TOLERANCE)]


def test_birth_equals_death_constant():
    """If b = d, then dN/dt = 0, so the population should never change."""
    params = {"b": 0.02, "d": 0.02}   # TEST VALUES
    N0 = 1000000                      # TEST VALUE

    t, N = euler_solve(rate_v1, N0, params, T_END, DT)
    largest_change = np.max(np.abs(N - N0))

    return ["b = d stays constant (V1)",
            "N stays at N0 (change < 1e-6)",
            f"{largest_change:.2e} persons",
            pass_or_fail(largest_change < 1e-6)]


def test_v2_reduces_to_v1():
    """With K = infinity and M = 0, V2 becomes dN/dt = rN, which is V1 with r = b - d."""
    params_v1 = {"b": 0.025, "d": 0.006}   # TEST VALUES
    params_v2 = {"r": params_v1["b"] - params_v1["d"], "K": float("inf"), "M": 0}
    N0 = 1000000                           # TEST VALUE

    t, N_v1 = euler_solve(rate_v1, N0, params_v1, T_END, DT)
    t, N_v2 = euler_solve(rate_v2, N0, params_v2, T_END, DT)
    difference = max_relative_error(N_v2, N_v1)

    return ["V2 with K = inf, M = 0 equals V1",
            "max relative difference < 1e-10%",
            f"{difference * 100:.2e}%",
            pass_or_fail(difference * 100 < 1e-10)]


def test_start_at_K_stays_at_K():
    """If N0 = K and M = 0, then 1 - N/K = 0, so the population should stay at K."""
    params = {"r": 0.05, "K": 20000000, "M": 0}   # TEST VALUES
    N0 = params["K"]

    t, N = euler_solve(rate_v2, N0, params, T_END, DT)
    largest_change = np.max(np.abs(N - params["K"]) / params["K"])

    return ["N0 = K stays at K",
            "change from K < 1e-10%",
            f"{largest_change * 100:.2e}%",
            pass_or_fail(largest_change * 100 < 1e-10)]


def test_above_K_declines():
    """If N0 > K and M = 0, then 1 - N/K < 0, so N should fall toward K but not below it."""
    params = {"r": 0.05, "K": 20000000, "M": 0}   # TEST VALUES
    N0 = 25000000                                # TEST VALUE (above K)
    K = params["K"]

    t, N = euler_solve(rate_v2, N0, params, T_END, DT)

    always_decreasing = np.all(np.diff(N) < 0)   # every step goes down
    stays_above_K = np.all(N > K)                 # never drops below K

    return ["N0 > K declines toward K",
            "falls every step, stays above K",
            f"{N[0] / 1e6:.2f}M down to {N[-1] / 1e6:.2f}M",
            pass_or_fail(always_decreasing and stays_above_K)]


def test_equilibrium_matches_simulation(M):
    """A long V2 run should settle at N* = (K/2) * [1 + sqrt(1 + 4M / (rK))]."""
    params = {"r": 0.05, "K": 20000000, "M": M}   # TEST VALUES
    N0 = 5000000                                 # TEST VALUE

    t, N = euler_solve(rate_v2, N0, params, T_LONG, DT)
    N_star = equilibrium_v2(params)
    difference = abs(N[-1] - N_star) / N_star

    # {M:+,} shows the sign and a comma separator, e.g. +100,000
    return [f"Equilibrium matches (M = {M:+,})",
            "final N within 0.01% of N*",
            f"{difference * 100:.2e}%",
            pass_or_fail(difference * 100 < 0.01)]


def test_large_negative_M_never_negative():
    """If M < -rK/4 there is no equilibrium: N should fall to 0 and never go below it."""
    params = {"r": 0.05, "K": 20000000, "M": -500000}   # TEST VALUES (-rK/4 = -250,000)
    N0 = 5000000                                       # TEST VALUE

    t, N_euler = euler_solve(rate_v2, N0, params, T_END, DT)
    t, N_rk4 = rk4_solve(rate_v2, N0, params, T_END, DT)

    never_negative = np.all(N_euler >= 0) and np.all(N_rk4 >= 0)
    ends_at_zero = N_euler[-1] == 0 and N_rk4[-1] == 0
    no_equilibrium = equilibrium_v2(params) is None

    return ["Large negative M (collapse)",
            "N never < 0, ends at 0, no N*",
            f"min N: Euler {N_euler.min():.0f}, RK4 {N_rk4.min():.0f}",
            pass_or_fail(never_negative and ends_at_zero and no_equilibrium)]


# ------------------------------------------------------------
# Run all tests and print the table
# ------------------------------------------------------------
def print_table(rows):
    """Print the results as a table: Test | Expected Result | Actual Result | Status."""
    print(f"{'Test':<36}{'Expected Result':<36}{'Actual Result':<26}{'Status'}")
    print("-" * 104)
    for row in rows:
        print(f"{row[0]:<36}{row[1]:<36}{row[2]:<26}{row[3]}")


rows = [
    test_euler_vs_exact_v1(),
    test_euler_vs_exact_logistic(),
    test_error_halves_with_dt(),
    test_rk4_vs_exact_v1(),
    test_euler_vs_rk4_with_migration(),
    test_birth_equals_death_constant(),
    test_v2_reduces_to_v1(),
    test_start_at_K_stays_at_K(),
    test_above_K_declines(),
    test_equilibrium_matches_simulation(100000),
    test_equilibrium_matches_simulation(-100000),
    test_large_negative_M_never_negative(),
]

print("VERIFICATION TESTS (all inputs are TEST VALUES)")
print()
print_table(rows)