"""
calibration.py
Calibration of V2 (r and K) and the error measures (Step 11).

Calibration: find the r and K that make the model closest to the census,
by minimizing SSE = sum of (N_model - N_census)^2 with scipy.optimize.curve_fit.

M is held fixed during calibration (PROVISIONAL rule D3: average yearly M
from the balancing equation). Because M is not 0, there is no exact formula,
so the model values come from the Euler solution (solve_at_times).
"""

import numpy as np
from scipy.optimize import curve_fit

from src.models import rate_v2
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


def calibrate_v2(t_data, N_data, N0, M, dt, r_guess, K_guess):
    """
    Find r and K for V2 that best fit the census (smallest SSE).

    Parameters
    ----------
    t_data : numpy array
        Census times (years since the first census).
    N_data : numpy array
        Census populations (persons).
    N0 : float
        Population at t = 0 (persons), the first census.
    M : float
        Net migration (persons/year), held fixed.
    dt : float
        Euler time step (years).
    r_guess, K_guess : float
        Where curve_fit starts searching. They do not decide the answer,
        they only need to be in a sensible range.

    Returns
    -------
    dict
        r, K, M, and r_se, K_se (standard errors from curve_fit: how
        uncertain each fitted value is, in the same units as r and K).
    """

    # curve_fit needs a function of the form f(t, r, K).
    # N0, M, and dt are fixed, so this small function passes them along.
    def model(t, r, K):
        params = {"r": r, "K": K, "M": M}
        return solve_at_times(rate_v2, N0, params, t, dt)

    # bounds: r and K must stay positive while curve_fit searches.
    # x_scale="jac": r (about 0.03) and K (about 10 million) have very
    # different sizes, so curve_fit scales its steps to each parameter.
    best, covariance = curve_fit(model, t_data, N_data,
                                 p0=[r_guess, K_guess],
                                 bounds=([0, 0], [np.inf, np.inf]),
                                 x_scale="jac")

    # Standard error = square root of the diagonal of the covariance matrix
    standard_errors = np.sqrt(np.diag(covariance))

    return {"r": best[0], "K": best[1], "M": M,
            "r_se": standard_errors[0], "K_se": standard_errors[1]}
