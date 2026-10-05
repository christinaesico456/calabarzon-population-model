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