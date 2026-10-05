"""
solvers.py
Numerical solvers for the CALABARZON population models.

The solvers work with any rate function from models.py
that takes (N, params) and returns dN/dt.
"""

import numpy as np


def make_time_grid(t_end, dt):
    """
    Create evenly spaced time points from 0 to t_end.

    Uses np.linspace instead of np.arange, because np.arange with
    decimal steps can add or drop the last point.

    Parameters
    ----------
    t_end : float
        End time (years since start year).
    dt : float
        Time step (years), e.g. 0.1

    Returns
    -------
    numpy array
        Time points [0, dt, 2*dt, ..., t_end].
    """
    # round() instead of int(): 0.3 / 0.1 gives 2.9999999999999996,
    # int() would make that 2, round() correctly makes it 3
    n_steps = round(t_end / dt)

    # Stop if dt does not divide t_end evenly
    if abs(n_steps * dt - t_end) > 1e-9:
        raise ValueError("dt must divide t_end evenly (t_end / dt must be a whole number).")

    # n_steps steps means n_steps + 1 time points (we include t = 0)
    t = np.linspace(0, t_end, n_steps + 1)

    return t


def euler_solve(rate_func, N0, params, t_end, dt):
    """
    Solve dN/dt = rate_func(N, params) using Euler's method.

    Euler update: N[k+1] = N[k] + dt * rate_func(N[k], params)

    Parameters
    ----------
    rate_func : function
        Rate function from models.py, e.g. rate_v1 or rate_v2.
    N0 : float
        Population at t = 0 (persons).
    params : dict
        Model parameters passed to rate_func.
    t_end : float
        End time (years since start year).
    dt : float
        Time step (years).

    Returns
    -------
    t : numpy array
        Time points (years).
    N : numpy array
        Population at each time point (persons).
    """
    t = make_time_grid(t_end, dt)

    # Empty array to hold the population at each time point
    N = np.zeros(len(t))
    N[0] = N0

    # Each loop step moves from time point k to time point k + 1
    for k in range(len(t) - 1):
        N[k + 1] = N[k] + dt * rate_func(N[k], params)

        # Boundary condition: population cannot go below 0
        if N[k + 1] < 0:
            N[k + 1] = 0

    return t, N



def rk4_solve(rate_func, N0, params, t_end, dt):
    """
    Solve dN/dt = rate_func(N, params) using the 4th-order Runge-Kutta method.

    RK4 update:
        k1 = f(N)
        k2 = f(N + dt/2 * k1)
        k3 = f(N + dt/2 * k2)
        k4 = f(N + dt * k3)
        N[k+1] = N[k] + dt/6 * (k1 + 2*k2 + 2*k3 + k4)

    Used as a cross-check for euler_solve. Same inputs and outputs.

    Parameters
    ----------
    rate_func : function
        Rate function from models.py, e.g. rate_v1 or rate_v2.
    N0 : float
        Population at t = 0 (persons).
    params : dict
        Model parameters passed to rate_func.
    t_end : float
        End time (years since start year).
    dt : float
        Time step (years).

    Returns
    -------
    t : numpy array
        Time points (years).
    N : numpy array
        Population at each time point (persons).
    """
    t = make_time_grid(t_end, dt)

    N = np.zeros(len(t))
    N[0] = N0

    for k in range(len(t) - 1):
        # Four slope estimates within one time step
        k1 = rate_func(N[k], params)                  # slope at the start
        k2 = rate_func(N[k] + dt / 2 * k1, params)    # slope at the midpoint (using k1)
        k3 = rate_func(N[k] + dt / 2 * k2, params)    # slope at the midpoint (using k2)
        k4 = rate_func(N[k] + dt * k3, params)        # slope at the end (using k3)

        # Weighted average of the four slopes
        N[k + 1] = N[k] + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

        # Boundary condition: population cannot go below 0
        if N[k + 1] < 0:
            N[k + 1] = 0

    return t, N