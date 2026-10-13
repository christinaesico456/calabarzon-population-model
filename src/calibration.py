"""
calibration.py
Calibration of V1 and V2 and the error measures (Step 11).

Calibration: find the parameter values that make the model closest to the
census, by minimizing SSE = sum of (N_model - N_census)^2 with
scipy.optimize.curve_fit.

Fallback decision (group, October 13, 2026): births and deaths for 1970 to
2003 are not available online, so M cannot come from the balancing equation.
Instead M is fitted together with r and K from the census.
  V1: fits r = b - d (one number)
  V2: fits r, K, and M (three numbers)

The model values come from the Euler solution (solve_at_times), the same
method used everywhere else in the project.
"""

import numpy as np
from scipy.optimize import curve_fit

from src.models import rate_v1, rate_v2
from src.solvers import solve_at_times


def sse(observed, simulated):
    """Sum of squared errors (persons^2). This is what calibration makes as small as possible."""
    return np.sum((simulated - observed) ** 2)


def rmse(observed, simulated):
    """Root mean square error (persons): the typical size of the error."""
    return np.sqrt(np.mean((simulated - observed) ** 2))


def mape(observed, simulated):
    """Mean absolute percentage error (%): the typical error as a percent of the census."""
    return np.mean(np.abs((simulated - observed) / observed)) * 100


def calibrate_v1(t_data, N_data, N0, dt, r_guess):
    """
    Find the V1 growth rate r = b - d that best fits the census (smallest SSE).

    In V1, dN/dt = (b - d) N, only the difference b - d matters. So the fitted
    rate is passed to rate_v1 as b, with d = 0.

    Parameters
    ----------
    t_data : numpy array
        Census times (years since the first census).
    N_data : numpy array
        Census populations (persons).
    N0 : float
        Population at t = 0 (persons), the first census.
    dt : float
        Euler time step (years).
    r_guess : float
        Where curve_fit starts searching (per year).

    Returns
    -------
    dict
        r (per year) and r_se (its standard error, per year).
    """

    # curve_fit needs a function of the form f(t, r)
    def model(t, r):
        params = {"b": r, "d": 0}
        return solve_at_times(rate_v1, N0, params, t, dt)

    best, covariance = curve_fit(model, t_data, N_data, p0=[r_guess])

    return {"r": best[0], "r_se": np.sqrt(covariance[0, 0])}


def calibrate_v2(t_data, N_data, N0, dt, r_guess, K_guess, M_guess):
    """
    Find r, K, and M for V2 that best fit the census (smallest SSE).

    Parameters
    ----------
    t_data : numpy array
        Census times (years since the first census).
    N_data : numpy array
        Census populations (persons).
    N0 : float
        Population at t = 0 (persons), the first census.
    dt : float
        Euler time step (years).
    r_guess, K_guess, M_guess : float
        Where curve_fit starts searching. They do not decide the answer,
        they only need to be in a sensible range.

    Returns
    -------
    dict
        r, K, M, and r_se, K_se, M_se (standard errors from curve_fit: how
        uncertain each fitted value is, in the same units as the value).
    """

    # curve_fit needs a function of the form f(t, r, K, M).
    # N0 and dt are fixed, so this small function passes them along.
    def model(t, r, K, M):
        params = {"r": r, "K": K, "M": M}
        return solve_at_times(rate_v2, N0, params, t, dt)

    # bounds: r and K must stay positive while curve_fit searches;
    # M can be negative (more people leaving than arriving).
    # x_scale="jac": r (about 0.03), K (about 20 million), and M (about
    # 100,000) have very different sizes, so curve_fit scales its steps.
    best, covariance = curve_fit(model, t_data, N_data,
                                 p0=[r_guess, K_guess, M_guess],
                                 bounds=([0, 0, -np.inf], [np.inf, np.inf, np.inf]),
                                 x_scale="jac")

    # Standard error = square root of the diagonal of the covariance matrix
    standard_errors = np.sqrt(np.diag(covariance))

    return {"r": best[0], "K": best[1], "M": best[2],
            "r_se": standard_errors[0], "K_se": standard_errors[1], "M_se": standard_errors[2]}
