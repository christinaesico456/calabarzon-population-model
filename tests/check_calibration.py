"""
check_calibration.py
Checks for the error measures and calibration (calibration.py) and for the
whole pipeline (baseline.py), using TEST VALUES only.

Run from the project folder:  python -m tests.check_calibration
(tests/data/ must contain the files made by python -m tests.make_test_data)
"""

import numpy as np

from src.models import rate_v2
from src.solvers import solve_at_times
from src.calibration import rmse, mape, calibrate_v2
from src.baseline import build_baseline


def pass_or_fail(condition):
    """Turn True/False into the text PASS/FAIL for the table."""
    if condition:
        return "PASS"
    else:
        return "FAIL"


def percent_off(value, true_value):
    """How far value is from true_value, as a percent of true_value."""
    return abs(value - true_value) / true_value * 100


rows = []

# Check 1 and 2: error measures by hand (TEST VALUES)
# Errors are +10 and -10, so RMSE = 10; MAPE = (10/100 + 10/200) / 2 = 7.5%
observed = np.array([100, 200])
simulated = np.array([110, 190])

value = rmse(observed, simulated)
rows.append(["RMSE by hand", "10", f"{value:g}", pass_or_fail(abs(value - 10) < 1e-12)])

value = mape(observed, simulated)
rows.append(["MAPE by hand", "7.5%", f"{value:g}%", pass_or_fail(abs(value - 7.5) < 1e-12)])

# Check 3: calibration gets back r and K from data made by the same model
# (TEST VALUES: r = 0.03, K = 15,000,000, M = 80,000)
true_params = {"r": 0.03, "K": 15000000, "M": 80000}
N0 = 3000000
t_data = np.array([0, 5, 10, 20, 25.3, 30, 37.2, 40])
N_data = solve_at_times(rate_v2, N0, true_params, t_data, 0.1)

fit = calibrate_v2(t_data, N_data, N0, true_params["M"], 0.1, r_guess=0.05, K_guess=30000000)
worst = max(percent_off(fit["r"], 0.03), percent_off(fit["K"], 15000000))
rows.append(["Calibration recovers r and K",
             "both within 0.01%",
             f"worst {worst:.2e}%",
             pass_or_fail(worst < 0.01)])

# Check 4: whole pipeline on the TEST files made by tests/make_test_data.py
# (true values r = 0.04, K = 25,000,000, M = 150,000; the files were made with
# RK4 and rounded, so small differences are expected)
baseline = build_baseline({"census": "tests/data/census_TEST_full.csv",
                           "vital": "tests/data/vital_stats_TEST_VALUES.csv"})
worst = max(percent_off(baseline["M"], 150000),
            percent_off(baseline["r"], 0.04),
            percent_off(baseline["K"], 25000000))
rows.append(["Pipeline recovers M, r, K (files)",
             "all within 1%",
             f"worst {worst:.2f}%",
             pass_or_fail(worst < 1)])


print("CALIBRATION CHECKS (all inputs are TEST VALUES)")
print()
print(f"{'Check':<36}{'Expected Result':<22}{'Actual Result':<22}{'Status'}")
print("-" * 86)
for row in rows:
    print(f"{row[0]:<36}{row[1]:<22}{row[2]:<22}{row[3]}")
