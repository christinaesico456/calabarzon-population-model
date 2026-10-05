"""
data_loader.py
Loads the CALABARZON census CSV and prepares it for the model.

Checks done while loading:
- Years with no area values yet are skipped (not entered yet).
- Years with only some area values stop with an error.
- The six areas must add up to the official total (if one was entered).
- Census dates are turned into decimal years and t (years since first census).
"""

import pandas as pd


# The six areas that make up CALABARZON.
# Lucena City is counted separately from Quezon province.
AREA_COLUMNS = ["batangas", "cavite", "laguna", "quezon", "lucena", "rizal"]


def date_to_decimal_year(date):
    """
    Convert a date to a decimal year.

    Example: 2015-08-01 is day 213 of 2015, so 2015 + 212/365 = about 2015.58

    Parameters
    ----------
    date : pandas Timestamp
        A census reference date.

    Returns
    -------
    float
        The date as a decimal year.
    """
    if date.is_leap_year:
        days_in_year = 366
    else:
        days_in_year = 365

    # dayofyear is 1 on January 1, so subtract 1 to make January 1 = .0
    return date.year + (date.dayofyear - 1) / days_in_year


def load_census(path="data/calabarzon_census.csv"):
    """
    Load the census CSV, check it, and add the columns the model needs.

    Parameters
    ----------
    path : str
        Location of the census CSV file.

    Returns
    -------
    pandas DataFrame
        One row per entered census year, sorted by date, with added columns:
        total        : regional population (persons)
        decimal_year : census date as a decimal year, e.g. 2015.58
        t            : years since the first census (t = 0 at the first census)
    """
    data = pd.read_csv(path)

    # 1. Keep only years where at least one area value was entered
    entered = data[AREA_COLUMNS].notna().any(axis=1)
    data = data[entered].copy()

    if len(data) == 0:
        print("Note: no census years have been entered yet in", path)
        return data

    # 2. Every entered year must have all six areas and a census date
    for i in data.index:
        year = data.loc[i, "year"]

        if data.loc[i, AREA_COLUMNS].isna().any():
            raise ValueError(f"Year {year}: some area values are missing.")

        if pd.isna(data.loc[i, "census_date"]):
            raise ValueError(f"Year {year}: census_date is missing.")

    # 3. Add up the six areas and compare with the official total
    data["area_sum"] = data[AREA_COLUMNS].sum(axis=1)

    for i in data.index:
        year = data.loc[i, "year"]
        official_total = data.loc[i, "total"]
        area_sum = data.loc[i, "area_sum"]

        if pd.isna(official_total):
            # No published regional total for this year: use the sum
            data.loc[i, "total"] = area_sum
        elif official_total != area_sum:
            raise ValueError(
                f"Year {year}: the areas add up to {area_sum:,.0f} "
                f"but total is {official_total:,.0f} "
                f"(difference {area_sum - official_total:,.0f}). "
                f"Check for typos or Lucena counted twice."
            )

    # 4. Turn census dates into decimal years (format must be YYYY-MM-DD)
    data["census_date"] = pd.to_datetime(data["census_date"], format="%Y-%m-%d")
    data = data.sort_values("census_date")
    data["decimal_year"] = data["census_date"].apply(date_to_decimal_year)

    # 5. t = years since the first census, so N0 is exactly the first census value
    data["t"] = data["decimal_year"] - data["decimal_year"].iloc[0]

    # Number the rows 0, 1, 2, ... again after skipping and sorting
    data = data.reset_index(drop=True)

    return data
