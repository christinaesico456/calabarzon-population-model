"""
check_calibration.py
Checks for the error measures and calibration (calibration.py),
using TEST VALUES only.

Run from the project folder:  python -m tests.check_calibration
(tests/data/ must contain the files made by python -m tests.make_test_data)
"""

import numpy as np

from src.models import rate_v1, rate_v2
from src.solvers import solve_at_times
from src.data_loader import load_census
from src.calibration import rmse, mape, calibrate_v1, calibrate_v2
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

# Census-like times (years since the first census), TEST VALUES
t_data = np.array([0, 5, 10, 20, 25.3, 30, 37.2, 40])
N0 = 3000000

# Check 3: V1 calibration gets back r from data made by the same model
# (TEST VALUE: r = b - d = 0.025)
N_data = solve_at_times(rate_v1, N0, {"b": 0.025, "d": 0}, t_data, 0.1)
fit = calibrate_v1(t_data, N_data, N0, 0.1, r_guess=0.05)
error = percent_off(fit["r"], 0.025)
rows.append(["V1 calibration recovers r",
             "within 0.01%",
             f"{error:.2e}%",
             pass_or_fail(error < 0.01)])

# Check 4: V2 calibration gets back r, K, and M from data made by the same model
# (TEST VALUES: r = 0.03, K = 15,000,000, M = 80,000)
true_params = {"r": 0.03, "K": 15000000, "M": 80000}
N_data = solve_at_times(rate_v2, N0, true_params, t_data, 0.1)
fit = calibrate_v2(t_data, N_data, N0, 0.1, r_guess=0.05, K_guess=30000000, M_guess=0)
worst = max(percent_off(fit["r"], 0.03),
            percent_off(fit["K"], 15000000),
            percent_off(fit["M"], 80000))
rows.append(["V2 calibration recovers r, K, M",
             "all within 0.01%",
             f"worst {worst:.2e}%",
             pass_or_fail(worst < 0.01)])

# Check 5: harder case, the TEST census file (made with RK4, rounded to whole
# persons like a real census; true r = 0.04, K = 25,000,000, M = 150,000).
# Only the census years up to 2010 are used, the same as the real calibration.
census = load_census("tests/data/census_TEST_full.csv")
calibration_years = census[census["year"] <= 2010]
t_census = calibration_years["t"].to_numpy()
N_census = calibration_years["total"].to_numpy()

fit = calibrate_v2(t_census, N_census, N_census[0], 0.1,
                   r_guess=0.05, K_guess=2 * N_census.max(), M_guess=0)
r_off = percent_off(fit["r"], 0.04)
K_off = percent_off(fit["K"], 25000000)
M_off = percent_off(fit["M"], 150000)
rows.append(["V2 recovers r, K, M (TEST file)",
             "all within 5%",
             f"r {r_off:.1f}%, K {K_off:.1f}%, M {M_off:.1f}%",
             pass_or_fail(max(r_off, K_off, M_off) < 5)])


# Check 6: the whole shared setup (baseline.py) on the TEST files gives the
# same answer as check 5, even though it starts curve_fit from a different
# r_guess. (Tiny differences in the last decimals are normal: the search
# stops when it is close enough, so 1e-6% is the limit here.)
baseline = build_baseline({"census": "tests/data/census_TEST_full.csv",
                           "vital": "tests/data/vital_stats_TEST_VALUES.csv"})
worst = max(percent_off(baseline["r"], fit["r"]),
            percent_off(baseline["K"], fit["K"]),
            percent_off(baseline["M"], fit["M"]))
rows.append(["Shared setup gives the same fit",
             "within 1e-6%",
             f"worst {worst:.1e}%",
             pass_or_fail(worst < 1e-6)])


print("CALIBRATION CHECKS (all inputs are TEST VALUES)")
print()
print(f"{'Check':<34}{'Expected Result':<20}{'Actual Result':<28}{'Status'}")
print("-" * 88)
for row in rows:
    print(f"{row[0]:<34}{row[1]:<20}{row[2]:<28}{row[3]}")
print()
print("Check 5 fitted values with standard errors:")
print(f"  r = {fit['r']:.5f} (se {fit['r_se']:.5f})   true 0.04")
print(f"  K = {fit['K']:,.0f} (se {fit['K_se']:,.0f})   true 25,000,000")
print(f"  M = {fit['M']:,.0f} (se {fit['M_se']:,.0f})   true 150,000")
