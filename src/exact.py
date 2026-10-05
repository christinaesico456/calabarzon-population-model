"""
exact.py
Exact (analytical) solutions and equilibrium for the population models.

These are used to verify the numerical solvers in solvers.py.
"""

import numpy as np


def exact_v1(t, N0, params):
    """
    Exact solution of V1: dN/dt = (b - d) * N

    Formula: N(t) = N0 * e^((b - d) * t)

    Parameters
    ----------
    t : numpy array
        Time points (years).
    N0 : float
        Population at t = 0 (persons).
    params : dict
        params["b"] : birth rate per person (1/year)
        params["d"] : death rate per person (1/year)

    Returns
    -------
    numpy array
        Exact population at each time point (persons).
    """
    b = params["b"]
    d = params["d"]

    return N0 * np.exp((b - d) * t)


def exact_logistic(t, N0, params):
    """
    Exact solution of V2 when there is no migration (M = 0):
    dN/dt = r * N * (1 - N/K)

    Formula: N(t) = K / (1 + ((K - N0) / N0) * e^(-r * t))

    Parameters
    ----------
    t : numpy array
        Time points (years).
    N0 : float
        Population at t = 0 (persons).
    params : dict
        params["r"] : intrinsic growth rate (1/year)
        params["K"] : carrying capacity (persons)
        params["M"] : net migration (persons/year), must be 0

    Returns
    -------
    numpy array
        Exact population at each time point (persons).
    """
    r = params["r"]
    K = params["K"]
    M = params["M"]

    # This formula is only correct when there is no migration
    if M != 0:
        raise ValueError("exact_logistic only applies when M = 0.")

    return K / (1 + ((K - N0) / N0) * np.exp(-r * t))


def equilibrium_v2(params):
    """
    Stable equilibrium of V2: the population where dN/dt = 0.

    Formula: N* = (K/2) * [1 + sqrt(1 + 4M / (rK))]

    M = 0      gives N* = K
    M > 0      gives N* > K
    M < 0      gives N* < K
    M < -rK/4  gives no positive equilibrium (population collapses)

    Parameters
    ----------
    params : dict
        params["r"] : intrinsic growth rate (1/year)
        params["K"] : carrying capacity (persons)
        params["M"] : net migration (persons/year)

    Returns
    -------
    float or None
        Equilibrium population (persons), or None if no equilibrium exists.
    """
    r = params["r"]
    K = params["K"]
    M = params["M"]

    # The value inside the square root
    inside_sqrt = 1 + 4 * M / (r * K)

    # Negative inside the square root: no real equilibrium (collapse)
    if inside_sqrt < 0:
        return None

    return (K / 2) * (1 + np.sqrt(inside_sqrt))