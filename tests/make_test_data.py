"""
make_test_data.py
Creates the TEST VALUES files used by the --test mode of the Step 10 to 15
scripts and by tests/check_calibration.py. NOT CALABARZON data.

The files describe a made-up region whose TRUE parameters are known:
    r = 0.04 per year, K = 25,000,000 persons, M = 150,000 persons per year
If the whole pipeline (net migration -> calibration) works, it should get
values close to these back from the files.

How the files are made:
1. Run V2 with the true parameters (RK4, small dt so it is very accurate).
2. Census file: the population on each census date (real census dates).
3. Vital statistics file, for each calendar year Y, using the population N
   in the middle of the year (Y + 0.5):
       deaths = 0.007 * N                    (TEST VALUE death rate)
       births = r * N * (1 - N/K) + deaths   (so births - deaths = natural increase)

Run from the project folder:  python -m tests.make_test_data
"""

import numpy as np
import pandas as pd

from src.models import rate_v2
from src.solvers import rk4_solve
from src.data_loader import date_to_decimal_year


# ------------------------------------------------------------
# TEST VALUES ONLY (not CALABARZON data)
# ------------------------------------------------------------
TRUE_PARAMS = {"r": 0.04, "K": 25000000, "M": 150000}
N0 = 3000000          # population on the first census date (persons)
DEATH_RATE = 0.007    # deaths per person per year

CENSUS_DATES = ["1970-05-06", "1975-05-01", "1980-05-01", "1990-05-01",
                "1995-09-01", "2000-05-01", "2007-08-01", "2010-05-01",
                "2015-08-01", "2020-05-01", "2024-07-01"]

NOTE = "TEST VALUES: made by tests/make_test_data.py, not CALABARZON data"


# 1. Accurate V2 run from the first census date to beyond 2025
start = date_to_decimal_year(pd.Timestamp(CENSUS_DATES[0]))
t, N = rk4_solve(rate_v2, N0, TRUE_PARAMS, 60, 0.01)


def population_at(decimal_year):
    """Population of the TEST region on a date (decimal year)."""
    return np.interp(decimal_year - start, t, N)


# 2. Census file (whole total in the batangas column, other areas 0)
census_rows = []
for date in CENSUS_DATES:
    total = round(population_at(date_to_decimal_year(pd.Timestamp(date))))
    census_rows.append({"year": int(date[:4]), "census_date": date,
                        "batangas": total, "cavite": 0, "laguna": 0, "quezon": 0,
                        "lucena": 0, "rizal": 0, "total": total,
                        "source": NOTE, "notes": "whole total put in the batangas column"})

pd.DataFrame(census_rows).to_csv("tests/data/census_TEST_full.csv", index=False)


# 3. Vital statistics file, 1970 to 2024
r = TRUE_PARAMS["r"]
K = TRUE_PARAMS["K"]
vital_rows = []
for year in range(1970, 2025):
    N_mid = population_at(year + 0.5)
    deaths = DEATH_RATE * N_mid
    births = r * N_mid * (1 - N_mid / K) + deaths
    vital_rows.append({"year": year, "births": round(births), "deaths": round(deaths),
                       "crude_birth_rate": "", "crude_death_rate": "",
                       "source": NOTE, "notes": ""})

pd.DataFrame(vital_rows).to_csv("tests/data/vital_stats_TEST_VALUES.csv", index=False)

print("Saved tests/data/census_TEST_full.csv and tests/data/vital_stats_TEST_VALUES.csv")
print("(TEST VALUES: r = 0.04, K = 25,000,000, M = 150,000)")
