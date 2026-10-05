"""
models.py
Rate functions for the CALABARZON population models.

Each rate function returns dN/dt (persons per year) for a given
population N. The solvers in solvers.py call these functions.
"""


def rate_v1(N, params):
    """
    V1: Birth-death model.

    Equation: dN/dt = (b - d) * N

    Parameters
    ----------
    N : float
        Current population (persons).
    params : dict
        params["b"] : birth rate per person (1/year), e.g. 0.025
        params["d"] : death rate per person (1/year), e.g. 0.006

    Returns
    -------
    float
        Rate of change of population (persons/year).
    """
    b = params["b"]
    d = params["d"]

    return (b - d) * N



def rate_v2(N, params):
    """
    V2: Logistic growth with net migration.

    Equation: dN/dt = r * N * (1 - N/K) + M

    Parameters
    ----------
    N : float
        Current population (persons).
    params : dict
        params["r"] : intrinsic growth rate (1/year), calibrated from census
        params["K"] : carrying capacity (persons)
        params["M"] : net migration, in minus out (persons/year)

    Returns
    -------
    float
        Rate of change of population (persons/year).
    """
    r = params["r"]
    K = params["K"]
    M = params["M"]

    natural_increase = r * N * (1 - N / K)

    return natural_increase + M