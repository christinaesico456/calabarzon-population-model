# Population Dynamics Model: CALABARZON (Region IV-A)

Final Project in Computational Science, De La Salle University – Dasmariñas.

This project models the human population of CALABARZON (Batangas, Cavite,
Laguna, Quezon, Lucena City, and Rizal) with two differential equation models,
checks that the code solves them correctly (verification), compares them with
census data (validation), and uses them for sensitivity analysis and scenario
projections.

> **Status:** the code is complete and tested with TEST VALUES. The real
> results need the vital statistics (births and deaths, 1970 to 2024) and the
> 2024 census row, which are still being entered. Until then, real-data runs
> stop with a message saying what is missing.

## The models

| Model | Equation | Relaxes |
|---|---|---|
| V1: birth-death | dN/dt = (b − d) N | (basic model) |
| V2: logistic + net migration | dN/dt = r N (1 − N/K) + M | unlimited resources (K), closed population (M) |

- N: population (persons), t: years since the 1970 census
- b, d: births and deaths per person per year (from vital statistics)
- r: intrinsic growth rate (per year), K: carrying capacity (persons), both calibrated
- M: net migration (persons per year), from the demographic balancing equation
- V2 equilibrium: N* = (K/2) [1 + sqrt(1 + 4M/(rK))]

Both models are solved with Euler's method (dt = 0.1 year). RK4 is used as a cross-check.

## Research questions

| RQ | Question | Script |
|---|---|---|
| RQ1 | How accurately do V1 and V2 reproduce the 2015 to 2024 census? | `scripts/rq1_validation.py` |
| RQ2 | Which parameter (r, K, M) most affects the projected 2050 population? | `scripts/rq2_sensitivity.py` |
| RQ3 | How does net migration affect long-term population and equilibrium? | `scripts/rq3_migration.py` |
| RQ4 | What population does the model project for 2030, 2040, 2050 under scenarios? | `scripts/rq4_forecast.py` |

All projections are **projections under stated assumptions, not predictions**.

## How it works

```
data/calabarzon_census.csv ──► load_census ──┐
                                             ├─► net migration by period (balancing equation)
data/calabarzon_vital_stats.csv ─► load_vital_stats ┘        │
                                                             ▼
                                         b, d, M averaged over 1970–2010
                                                             │
                                                             ▼
                              r, K calibrated on 1970–2010 census (curve_fit, Euler)
                                                             │
                     ┌───────────────┬───────────────┬───────┴───────┐
                     ▼               ▼               ▼               ▼
                    RQ1             RQ2             RQ3             RQ4
              (validation)    (sensitivity)    (migration)     (scenarios)
                     └──────── tables (CSV) and graphs (PNG) in results/ ┘
```

## Project structure

```
src/
  models.py        rate_v1, rate_v2 (the equations)
  solvers.py       make_time_grid, euler_solve, rk4_solve, solve_at_times
  exact.py         exact_v1, exact_logistic, equilibrium_v2 (for verification)
  data_loader.py   load_census, load_vital_stats (with data checks)
  migration.py     events_between, net_migration_by_period, average_over_periods
  calibration.py   sse, rmse, mape, calibrate_v2
  baseline.py      shared setup for the results scripts (data -> b, d, M -> r, K)
  plot_style.py    shared graph colors and styling
scripts/
  net_migration.py, rq1_validation.py, rq2_sensitivity.py,
  rq3_migration.py, rq4_forecast.py, run_all.py
  test_run.py, plot_verification.py (early TEST VALUES demos)
tests/
  verify.py               12 verification tests of the solvers
  check_data_loader.py    census loader checks
  check_migration.py      vital statistics and net migration checks
  check_calibration.py    error measure and calibration checks
  make_test_data.py       makes the TEST VALUES files in tests/data/
data/
  calabarzon_census.csv, calabarzon_vital_stats.csv, README.md (entry rules), sources/
results/                  tables (CSV) and graphs (PNG)
```

## Setup (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Libraries: NumPy, Pandas, Matplotlib, and SciPy (calibration only).

## Running

Run everything from the project folder.

```
python -m tests.verify               # verification tests
python -m tests.check_data_loader    # census loader checks
python -m tests.check_migration      # net migration checks
python -m tests.check_calibration    # calibration checks

python -m scripts.run_all            # all results, real data
python -m scripts.run_all --test     # all results, TEST VALUES files
```

Each results script can also run alone, e.g. `python -m scripts.rq1_validation`.
With `--test`, scripts use the TEST VALUES files in `tests/data/`, and their
outputs are named `results/TEST_*` (ignored by Git). TEST VALUES outputs are not
CALABARZON results.

## Assumptions and provisional choices

- r, K, and M are constant over time; one population for the whole region (no age groups).
- Calibration uses census years 1970 to 2010; 2015, 2020, and 2024 are kept for validation.
- Projections start from the latest census count.
- The following are **provisional** and still need confirmation by the group:
  - D1: a calendar year partly inside a census period counts in proportion to the part inside.
  - D2: b and d = total births and deaths / person-years, 1970 to 2010.
  - D3: M = average yearly net migration, 1970 to 2010, held fixed during calibration.
  - D4: sensitivity ranges: r and K ± 2 standard errors; M from the smallest to the largest observed period value.
  - D5: scenario size (10% lower births or 10% higher deaths per person), still needs a cited source.

## Data sources

Census population: Philippine Statistics Authority (PSA). The exact table and
link for every row are in the `source` column of `data/calabarzon_census.csv`,
and the original files are in `data/sources/`. Entry rules and pitfalls
(Lucena City, Aurora, Rizal boundaries) are in `data/README.md`.
