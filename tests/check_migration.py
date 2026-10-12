"""
check_migration.py
Checks for load_vital_stats (data_loader.py) and the net migration
functions (migration.py), using small hand-checkable TEST VALUES.

Run from the project folder:  python -m tests.check_migration
"""

import pandas as pd

from src.data_loader import load_vital_stats
from src.migration import events_between, net_migration_by_period, average_over_periods


def pass_or_fail(condition):
    """Turn True/False into the text PASS/FAIL for the table."""
    if condition:
        return "PASS"
    else:
        return "FAIL"


rows = []

# TEST VALUES: 1,200 births and 300 deaths in every year from 2000 to 2003
vital = pd.DataFrame({"year": [2000, 2001, 2002, 2003],
                      "births": [1200, 1200, 1200, 1200],
                      "deaths": [300, 300, 300, 300]})

# Check 1: one full year that starts mid-year: half of 2000 + half of 2001
value = events_between(vital, "births", 2000.5, 2001.5)
rows.append(["Births over 1 year, mid-year start",
             "1,200",
             f"{value:,.0f}",
             pass_or_fail(abs(value - 1200) < 1e-9)])

# Check 2: a quarter of a year inside one calendar year (rule D1)
value = events_between(vital, "births", 2000.25, 2000.5)
rows.append(["Births over 0.25 year (rule D1)",
             "300",
             f"{value:,.0f}",
             pass_or_fail(abs(value - 300) < 1e-9)])

# Check 3: balancing equation by hand.
# Census 1,000 -> 4,000 over 2000.0 to 2002.0 (TEST VALUES)
# Births 2,400, deaths 600, natural increase 1,800,
# M total = 3,000 - 1,800 = 1,200, M per year = 600
census = pd.DataFrame({"year": [2000, 2002],
                       "decimal_year": [2000.0, 2002.0],
                       "total": [1000, 4000]})
periods = net_migration_by_period(census, vital)
M_per_year = periods.loc[0, "M_per_year"]
rows.append(["Balancing equation (by hand)",
             "M per year = 600",
             f"M per year = {M_per_year:,.0f}",
             pass_or_fail(abs(M_per_year - 600) < 1e-9)])

# Check 4: b = births / person-years. Person-years = (1,000 + 4,000) / 2 x 2 = 5,000
rates = average_over_periods(periods)
rows.append(["b = births / person-years",
             "2,400 / 5,000 = 0.48",
             f"{rates['b']:.4f}",
             pass_or_fail(abs(rates["b"] - 0.48) < 1e-12)])

# Check 5: a period with a year not entered is skipped (2003 to 2005 needs 2004)
census_gap = pd.DataFrame({"year": [2003, 2005],
                           "decimal_year": [2003.0, 2005.0],
                           "total": [1000, 1100]})
periods_gap = net_migration_by_period(census_gap, vital)
rows.append(["Period with missing year skipped",
             "0 periods",
             f"{len(periods_gap)} periods",
             pass_or_fail(len(periods_gap) == 0)])

# Check 6: a year with births but no deaths stops with an error
try:
    load_vital_stats("tests/data/vital_TEST_partial_row.csv")
    result = "no error"
except ValueError:
    result = "ValueError"
rows.append(["Missing deaths gives an error",
             "ValueError",
             result,
             pass_or_fail(result == "ValueError")])


print()
print("NET MIGRATION CHECKS (all inputs are TEST VALUES)")
print()
print(f"{'Check':<36}{'Expected Result':<26}{'Actual Result':<24}{'Status'}")
print("-" * 92)
for row in rows:
    print(f"{row[0]:<36}{row[1]:<26}{row[2]:<24}{row[3]}")
