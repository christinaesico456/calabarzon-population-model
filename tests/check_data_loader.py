"""
check_data_loader.py
Checks for src/data_loader.py, using small CSV files of TEST VALUES
in tests/data/ (not real census data).

Run from the project folder:  python -m tests.check_data_loader
"""

import pandas as pd

from src.data_loader import load_census, date_to_decimal_year


def pass_or_fail(condition):
    """Turn True/False into the text PASS/FAIL for the table."""
    if condition:
        return "PASS"
    else:
        return "FAIL"


def error_raised(path):
    """Return "ValueError" if load_census stops with an error, otherwise "no error"."""
    try:
        load_census(path)
        result = "no error"          # only reached if load_census did NOT stop
    except ValueError:
        result = "ValueError"        # load_census stopped, as it should
    return result


rows = []

# Check 1: decimal year (example from CLAUDE.md: Aug 1 2015 is about 2015.58)
value = date_to_decimal_year(pd.Timestamp("2015-08-01"))
rows.append(["Aug 1 2015 as decimal year",
             "about 2015.58",
             f"{value:.4f}",
             pass_or_fail(abs(value - 2015.58) < 0.005)])

# Load the valid TEST VALUES file once and use it for checks 2 to 5
data = load_census("tests/data/census_TEST_VALUES.csv")

# Check 2: the 2024 row has no values, so it should be skipped
rows.append(["Year not entered is skipped",
             "3 rows (2024 skipped)",
             f"{len(data)} rows",
             pass_or_fail(len(data) == 3)])

# Check 3: 1970 has no total, so total should be the sum of areas
total_1970 = data.loc[0, "total"]
rows.append(["Empty total becomes sum of areas",
             "510,000",
             f"{total_1970:,.0f}",
             pass_or_fail(total_1970 == 510000)])

# Check 4: 2000 has a total that matches the sum, so it should be kept
total_2000 = data.loc[1, "total"]
rows.append(["Matching total is kept",
             "1,020,000",
             f"{total_2000:,.0f}",
             pass_or_fail(total_2000 == 1020000)])

# Check 5: t should be 0 at the first census and 45.58 at Aug 1 2015
t_first = data.loc[0, "t"]
t_last = data.loc[2, "t"]
rows.append(["t = 0 at first census",
             "t = 0 and t = 45.58 (2015)",
             f"t = {t_first} and t = {t_last:.2f}",
             pass_or_fail(t_first == 0 and abs(t_last - 45.58) < 0.005)])

# Check 6: total that does not match the areas should stop with an error
result = error_raised("tests/data/census_TEST_bad_total.csv")
rows.append(["Wrong total gives an error",
             "ValueError",
             result,
             pass_or_fail(result == "ValueError")])

# Check 7: a year with some areas missing should stop with an error
result = error_raised("tests/data/census_TEST_partial_row.csv")
rows.append(["Missing area gives an error",
             "ValueError",
             result,
             pass_or_fail(result == "ValueError")])


# Print the table
print("DATA LOADER CHECKS (all inputs are TEST VALUES)")
print()
print(f"{'Check':<36}{'Expected Result':<30}{'Actual Result':<26}{'Status'}")
print("-" * 98)
for row in rows:
    print(f"{row[0]:<36}{row[1]:<30}{row[2]:<26}{row[3]}")
