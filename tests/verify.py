"""
verify.py
Verification tests: does the code solve the equations correctly?
All parameter values in this file are TEST VALUES (not CALABARZON data).

Each test returns one row: [test name, expected result, actual result, status]

Run from the project folder:  python -m tests.verify
"""

import numpy as np

from src.models import rate_v1, rate_v2
from src.solvers import euler_solve
from src.exact import exact_v1, exact_logistic


# ------------------------------------------------------------
# Settings shared by all tests
# ------------------------------------------------------------
T_END = 80          # years (same length as 1970 to 2050)
DT = 0.1            # time step (years)
TOLERANCE = 0.005   # largest allowed relative error (0.5%)


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
    """Euler solution of V2 with M = 0 should match the exact logistic formula."""
    params = {"r": 0.05, "K": 20000000, "M": 0}   # TEST VALUES
    N0 = 5000000                                 # TEST VALUE

    t, N_euler = euler_solve(rate_v2, N0, params, T_END, DT)
    N_exact = exact_logistic(t, N0, params)
    error = max_relative_error(N_euler, N_exact)

    return ["Euler vs exact (logistic, M = 0)",
            "max relative error < 0.5%",
            f"{error * 100:.4f}%",
            pass_or_fail(error < TOLERANCE)]


# ------------------------------------------------------------
# Run all tests and print the table
# ------------------------------------------------------------
def print_table(rows):
    """Print the results as a table: Test | Expected Result | Actual Result | Status."""
    print(f"{'Test':<36}{'Expected Result':<30}{'Actual Result':<16}{'Status'}")
    print("-" * 88)
    for row in rows:
        print(f"{row[0]:<36}{row[1]:<30}{row[2]:<16}{row[3]}")


rows = [
    test_euler_vs_exact_v1(),
    test_euler_vs_exact_logistic(),
]

print("VERIFICATION TESTS (all inputs are TEST VALUES)")
print()
print_table(rows)