"""
baseline.py
Builds the baseline model that the results scripts share:

    census (1970 to 2010)
      -> V1: r = b - d fitted to the census          (calibration.py)
      -> V2: r, K, and M fitted to the census        (calibration.py)

Fallback decision (group, October 13, 2026): births and deaths for 1970 to
2003 are not available online, so M is fitted from the census instead of
the balancing equation. The balancing equation is kept only as a check for
2010 onward (scripts/net_migration.py).

It also chooses which data files to use:
    python -m scripts.rq1_validation          real CALABARZON data (data/)
    python -m scripts.rq1_validation --test   TEST VALUES files (tests/data/)
"""

import sys

import numpy as np

from src.models import rate_v2
from src.solvers import solve_at_times
from src.data_loader import load_census, load_vital_stats
from src.migration import net_migration_by_period
from src.calibration import calibrate_v1, calibrate_v2


CALIBRATION_END_YEAR = 2010   # calibrate on census years up to 2010 (CLAUDE.md)
DT = 0.1                      # Euler time step (years)


def choose_mode():
    """
    Real data, or TEST VALUES if the script was run with --test.

    Returns
    -------
    dict
        census, vital : data file paths
        prefix        : added to output file names ("TEST_" in test mode,
                        so .gitignore keeps test outputs out of Git)
        label         : added to graph titles ("TEST VALUES ONLY: " in test mode)
    """
    if "--test" in sys.argv:
        print("*** TEST MODE: TEST VALUES files from tests/data/, NOT CALABARZON data ***")
        print()
        return {"census": "tests/data/census_TEST_full.csv",
                "vital": "tests/data/vital_stats_TEST_VALUES.csv",
                "prefix": "TEST_",
                "label": "TEST VALUES ONLY: "}

    return {"census": "data/calabarzon_census.csv",
            "vital": "data/calabarzon_vital_stats.csv",
            "prefix": "",
            "label": ""}


def build_baseline(mode):
    """
    Load the census and calibrate V1 and V2 on the census years up to 2010.

    Parameters
    ----------
    mode : dict
        From choose_mode().

    Returns
    -------
    dict
        census               : the loaded census
        N0                   : first census population (persons)
        start_decimal_year   : first census date as a decimal year (t = 0)
        r_v1, r_v1_se        : V1 growth rate r = b - d (per year) and its standard error
        r, K, M              : V2 parameters, all fitted
        r_se, K_se, M_se     : standard errors of r, K, M from curve_fit
        latest_year, latest_decimal_year, latest_N : the latest census,
                               where all projections start (jump-off point)
    """
    census = load_census(mode["census"])

    # Calibration uses census years up to 2010 only; 2015 onward is kept for validation
    calibration_census = census[census["year"] <= CALIBRATION_END_YEAR]

    N0 = census.loc[0, "total"]
    t_data = calibration_census["t"].to_numpy()
    N_data = calibration_census["total"].to_numpy()

    # Starting guesses for curve_fit (only where the search starts, not the answer):
    # r_guess = average growth per year over the calibration period
    # K_guess = twice the largest calibration census
    # M_guess = 0 (no migration), so the data alone decides the sign of M
    r_guess = np.log(N_data[-1] / N_data[0]) / t_data[-1]
    K_guess = 2 * N_data.max()
    M_guess = 0

    fit_v1 = calibrate_v1(t_data, N_data, N0, DT, r_guess)
    fit_v2 = calibrate_v2(t_data, N_data, N0, DT, r_guess, K_guess, M_guess)

    # The latest census in the file: all projections start here
    last = len(census) - 1

    return {
        "census": census,
        "N0": N0,
        "start_decimal_year": census.loc[0, "decimal_year"],
        "r_v1": fit_v1["r"],
        "r_v1_se": fit_v1["r_se"],
        "r": fit_v2["r"],
        "K": fit_v2["K"],
        "M": fit_v2["M"],
        "r_se": fit_v2["r_se"],
        "K_se": fit_v2["K_se"],
        "M_se": fit_v2["M_se"],
        "latest_year": census.loc[last, "year"],
        "latest_decimal_year": census.loc[last, "decimal_year"],
        "latest_N": census.loc[last, "total"],
    }


def print_baseline(baseline):
    """Print the fitted parameters with their units and standard errors."""
    print(f"Calibrated on census years up to {CALIBRATION_END_YEAR}")
    print(f"  N0 = {baseline['N0']:,.0f} persons (first census)")
    print(f"  V1: r = b - d = {baseline['r_v1']:.5f} per year "
          f"(standard error {baseline['r_v1_se']:.5f})")
    print(f"  V2: r = {baseline['r']:.5f} per year (standard error {baseline['r_se']:.5f})")
    print(f"      K = {baseline['K']:,.0f} persons (standard error {baseline['K_se']:,.0f})")
    print(f"      M = {baseline['M']:,.0f} persons per year (standard error {baseline['M_se']:,.0f})")
    print(f"  Projections start from the {baseline['latest_year']} census: "
          f"{baseline['latest_N']:,.0f} persons")
    print()


def observed_migration(mode, baseline):
    """
    Net migration per year observed with the balancing equation, for every
    census period whose births and deaths were entered (2015 onward).

    M = (Pop_end - Pop_start) - (Births - Deaths), divided by the period length.

    Option A (PROVISIONAL, October 13, 2026): these observed values are NOT
    used to fit the model. They are used as real-data migration levels in
    RQ3 and RQ4, and to check the fitted M (scripts/net_migration.py).

    Parameters
    ----------
    mode : dict
        From choose_mode().
    baseline : dict
        From build_baseline().

    Returns
    -------
    pandas DataFrame
        One row per period (see net_migration_by_period in migration.py).
    """
    vital = load_vital_stats(mode["vital"])
    periods = net_migration_by_period(baseline["census"], vital)

    if len(periods) == 0:
        raise ValueError("No census period has births and deaths for every year. "
                         "Enter them in " + mode["vital"] + " first.")

    return periods


def project(params, baseline, decimal_years):
    """
    V2 projection from the latest census to chosen dates.

    Starts from the latest census COUNT (not the model's value at that date),
    so a projection does not carry the model's past error forward.

    Parameters
    ----------
    params : dict
        V2 parameters r, K, M.
    baseline : dict
        From build_baseline().
    decimal_years : numpy array
        Dates to project to, e.g. [2030.0, 2040.0, 2050.0]. All must be on or
        after the latest census date.

    Returns
    -------
    numpy array
        Projected population at each date (persons).
    """
    t_from_latest = np.array(decimal_years) - baseline["latest_decimal_year"]

    return solve_at_times(rate_v2, baseline["latest_N"], params, t_from_latest, DT)
