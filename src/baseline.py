"""
baseline.py
Builds the baseline model that the Step 10 to 15 scripts share:

    census + vital statistics
      -> net migration by period                        (Step 10, migration.py)
      -> b, d, M over the calibration period             (rules D2, D3)
      -> r, K calibrated on census years up to 2010      (Step 11, calibration.py)

It also chooses which data files to use:
    python -m scripts.rq1_validation          real CALABARZON data (data/)
    python -m scripts.rq1_validation --test   TEST VALUES files (tests/data/)
"""

import sys

import numpy as np

from src.models import rate_v2
from src.solvers import solve_at_times
from src.data_loader import load_census, load_vital_stats
from src.migration import net_migration_by_period, average_over_periods
from src.calibration import calibrate_v2


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
    Load the data, estimate b, d, M, and calibrate r, K.

    Parameters
    ----------
    mode : dict
        From choose_mode().

    Returns
    -------
    dict
        census, periods      : the loaded census and the Step 10 table
        N0                   : first census population (persons)
        start_decimal_year   : first census date as a decimal year (t = 0)
        b, d                 : births and deaths per person per year (V1)
        r, K, M              : V2 parameters (r and K calibrated, M fixed)
        r_se, K_se           : standard errors of r and K from curve_fit
        latest_year, latest_decimal_year, latest_N : the latest census,
                               where all projections start (jump-off point)
    """
    census = load_census(mode["census"])
    vital = load_vital_stats(mode["vital"])

    # Calibration uses census years up to 2010 only; 2015 onward is kept for validation
    calibration_census = census[census["year"] <= CALIBRATION_END_YEAR]

    periods = net_migration_by_period(calibration_census, vital)

    # Every calibration period needs M, otherwise the average M leaves out years
    if len(periods) < len(calibration_census) - 1:
        raise ValueError(
            f"Births and deaths are needed for every year from the first census "
            f"to the {CALIBRATION_END_YEAR} census. Enter them in {mode['vital']} first."
        )

    rates = average_over_periods(periods)

    N0 = census.loc[0, "total"]
    t_data = calibration_census["t"].to_numpy()
    N_data = calibration_census["total"].to_numpy()

    # Starting guesses for curve_fit (only where the search starts, not the answer):
    # r_guess = average growth per year over the calibration period
    # K_guess = twice the largest calibration census
    r_guess = np.log(N_data[-1] / N_data[0]) / t_data[-1]
    K_guess = 2 * N_data.max()

    fit = calibrate_v2(t_data, N_data, N0, rates["M"], DT, r_guess, K_guess)

    # The latest census in the file: all projections start here
    last = len(census) - 1

    return {
        "census": census,
        "periods": periods,
        "N0": N0,
        "start_decimal_year": census.loc[0, "decimal_year"],
        "b": rates["b"],
        "d": rates["d"],
        "r": fit["r"],
        "K": fit["K"],
        "M": fit["M"],
        "r_se": fit["r_se"],
        "K_se": fit["K_se"],
        "latest_year": census.loc[last, "year"],
        "latest_decimal_year": census.loc[last, "decimal_year"],
        "latest_N": census.loc[last, "total"],
    }


def print_baseline(baseline):
    """Print the baseline parameters with their units."""
    print("Baseline parameters")
    print(f"  N0 = {baseline['N0']:,.0f} persons (first census)")
    print(f"  b  = {baseline['b']:.5f} per person per year")
    print(f"  d  = {baseline['d']:.5f} per person per year")
    print(f"  M  = {baseline['M']:,.0f} persons per year (average, held fixed)")
    print(f"  r  = {baseline['r']:.5f} per year (calibrated, standard error {baseline['r_se']:.5f})")
    print(f"  K  = {baseline['K']:,.0f} persons (calibrated, standard error {baseline['K_se']:,.0f})")
    print(f"  Projections start from the {baseline['latest_year']} census: "
          f"{baseline['latest_N']:,.0f} persons")
    print()


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
