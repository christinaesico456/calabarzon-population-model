# Population Dynamics Model: CALABARZON (Region IV-A)

Final Project in Computational Science, De La Salle University – Dasmariñas.

This project models the human population of CALABARZON (Batangas, Cavite,
Laguna, Quezon, Lucena City, and Rizal) with two differential equation models,
checks that the code solves them correctly (verification), compares them with
census data (validation), and uses them for sensitivity analysis and scenario
projections.

> **Status:** code complete and run on real data (census 1970 to 2024, PSA
> births and deaths 2015 to 2024). The method for net migration is Option A
> (below), chosen October 13, 2026; adviser confirmation is recommended.

## The models

| Model | Equation | Relaxes |
|---|---|---|
| V1: birth-death | dN/dt = (b − d) N | (basic model) |
| V2: logistic + net migration | dN/dt = r N (1 − N/K) + M | unlimited resources (K), closed population (M) |

- N: population (persons), t: years since the 1970 census (May 6, 1970)
- V1: r = b − d (per year), fitted to the 1970 to 2010 census
- V2: r (per year), K (persons), and M (persons per year), all fitted to the 1970 to 2010 census
- V2 equilibrium: N* = (K/2) [1 + sqrt(1 + 4M/(rK))]

Both models are solved with Euler's method (dt = 0.1 year). RK4 is used as a cross-check.

### How net migration is handled (Option A)

Registered births and deaths before 2015 are not available online, so M cannot
be taken from the balancing equation for the 1970 to 2010 calibration period.
Instead, M is fitted from the census together with r and K. The fitted M is
negative (about −159,000 per year), which is not realistic: with PSA births and
deaths, the balancing equation M = (population change) − (births − deaths) gives

| Period | Observed net migration (PSA data) |
|---|---|
| 2015–2020 | +212,394 persons per year |
| 2020–2024 | +71,383 persons per year |

So the fitted M is a fitting number, not real migration. The likely reason is
that real migration changes over time, while the model assumes one constant M
for 1970 to 2050. The observed values are used as real-data migration levels in
RQ3 and RQ4, and as a check of the fitted M.

## Research questions and main results

All projections are **projections under stated assumptions, not predictions**.

| RQ | Question | Result (real data) | Script |
|---|---|---|---|
| RQ1 | How accurately do V1 and V2 reproduce the 2015 to 2024 census? | Validation MAPE: V1 11.97%, V2 0.93% | `scripts/rq1_validation.py` |
| RQ2 | Which parameter (r, K, M) most affects the projected 2050 population? | K (swing 42.7%), then r (13.7%), then M (11.5%), with ranges ± 2 standard errors | `scripts/rq2_sensitivity.py` |
| RQ3 | How does net migration affect long-term population and equilibrium? | N* from 22.0 million (fitted M) to 24.1 million (M = 0) to 26.4 million (M = 2015–2020 level) | `scripts/rq3_migration.py` |
| RQ4 | What population does the model project for 2030, 2040, 2050? | 2050: baseline 20.9 million, lower growth rate 20.5 million, high migration 22.7 million | `scripts/rq4_forecast.py` |

Tables (CSV) and graphs (PNG) are in `results/`.

## How it works

```
data/calabarzon_census.csv ──► load_census ──► fit V1 (r) and V2 (r, K, M)
                                               on census 1970–2010 (curve_fit, Euler)
                                                        │
data/calabarzon_vital_stats.csv ──► balancing equation  │
   (births, deaths 2015–2024)       observed M per period
                                         │              │
                     ┌───────────────┬───┴───────────┬──┴────────────┐
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
  migration.py     events_between, net_migration_by_period
  calibration.py   sse, rmse, mape, calibrate_v1, calibrate_v2
  baseline.py      shared setup: fit V1 and V2, observed migration, projections
  plot_style.py    shared graph colors and styling
scripts/
  rq1_validation.py, rq2_sensitivity.py, rq3_migration.py, rq4_forecast.py,
  net_migration.py (check of the fitted M), run_all.py
  test_run.py, plot_verification.py (early TEST VALUES demos)
tests/
  verify.py               14 verification tests of the solvers
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

## Assumptions and limitations

- r, K, and M are constant over time; one population for the whole region (no age groups).
- Calibration uses census years 1970 to 2010; 2015, 2020, and 2024 are kept for validation.
- Projections start from the 2024 census count.
- The fitted M is negative while observed migration is positive (see above).
- Births and deaths are registered counts, not adjusted for under-registration.
- RQ2 ranges are fitted value ± 2 standard errors; these can be narrower than the real uncertainty.
- The RQ4 "lower growth rate" size (r 10% lower) is a placeholder that still needs a cited source.

## Data sources

Philippine Statistics Authority (PSA). The exact table and link for every row
are in the `source` column of `data/calabarzon_census.csv` and
`data/calabarzon_vital_stats.csv`. Census files are in `data/sources/`. Entry
rules and pitfalls (Lucena City, Aurora, Rizal boundaries) are in `data/README.md`.
