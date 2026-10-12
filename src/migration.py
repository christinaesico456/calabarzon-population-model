"""
migration.py
Net migration estimate (Step 10) using the demographic balancing equation:

    M_period = (Pop_end - Pop_start) - (Births - Deaths)

for each period between two censuses.

Births and deaths are given per calendar year, but census dates fall partway
through a year (e.g. May 1). PROVISIONAL rule D1 (not yet confirmed by the
group): a calendar year that is only partly inside a period counts in
proportion to the part inside, assuming births and deaths are spread evenly
through the year. Example: a period starting May 1 2010 (2010.33) gets
0.67 of the 2010 births and deaths.
"""

import numpy as np
import pandas as pd


def calendar_years_in(start, end):
    """
    Calendar years that overlap the period from start to end (decimal years).

    Example: 2010.33 to 2015.58 gives 2010, 2011, 2012, 2013, 2014, 2015.
    """
    return range(int(np.floor(start)), int(np.ceil(end)))


def has_vital_stats_for(vital, start, end):
    """True if births and deaths were entered for every year the period touches."""
    for year in calendar_years_in(start, end):
        if year not in vital["year"].values:
            return False
    return True


def events_between(vital, column, start, end):
    """
    Total births (or deaths) between two dates, using rule D1.

    Parameters
    ----------
    vital : pandas DataFrame
        From load_vital_stats: columns year, births, deaths.
    column : str
        "births" or "deaths".
    start, end : float
        Period start and end as decimal years, e.g. 2010.33 and 2015.58.

    Returns
    -------
    float
        Number of events in the period (persons).
    """
    total = 0.0

    for year in calendar_years_in(start, end):
        # Fraction of calendar year [year, year + 1) inside the period [start, end)
        overlap = min(end, year + 1) - max(start, year)

        row = vital[vital["year"] == year]
        if len(row) == 0:
            raise ValueError(f"Year {year}: {column} not entered.")

        total = total + overlap * row[column].iloc[0]

    return total


def net_migration_by_period(census, vital):
    """
    Net migration for each period between two consecutive censuses.

    Periods whose births and deaths are not entered for every year are
    skipped, with a printed note.

    Parameters
    ----------
    census : pandas DataFrame
        From load_census: columns year, decimal_year, total (sorted by date).
    vital : pandas DataFrame
        From load_vital_stats: columns year, births, deaths.

    Returns
    -------
    pandas DataFrame
        One row per period with: start_year, end_year, length_years,
        pop_change, births, deaths, natural_increase, M_total, M_per_year,
        person_years.
    """
    rows = []

    for i in range(len(census) - 1):
        start_year = census.loc[i, "year"]
        end_year = census.loc[i + 1, "year"]
        start = census.loc[i, "decimal_year"]
        end = census.loc[i + 1, "decimal_year"]

        if not has_vital_stats_for(vital, start, end):
            print(f"Note: period {start_year}-{end_year} skipped "
                  f"(births and deaths not entered for every year).")
            continue

        pop_start = census.loc[i, "total"]
        pop_end = census.loc[i + 1, "total"]
        length = end - start

        births = events_between(vital, "births", start, end)
        deaths = events_between(vital, "deaths", start, end)
        natural_increase = births - deaths

        # Balancing equation: whatever growth births and deaths do not explain is migration
        M_total = (pop_end - pop_start) - natural_increase

        # Person-years lived in the period: average population times length
        # (straight line between the two census counts). Used for b and d.
        person_years = (pop_start + pop_end) / 2 * length

        rows.append({
            "start_year": start_year,
            "end_year": end_year,
            "length_years": length,
            "pop_change": pop_end - pop_start,
            "births": births,
            "deaths": deaths,
            "natural_increase": natural_increase,
            "M_total": M_total,
            "M_per_year": M_total / length,
            "person_years": person_years,
        })

    return pd.DataFrame(rows)


def average_over_periods(periods):
    """
    b, d, and M averaged over a set of periods (PROVISIONAL rules D2 and D3).

    b = total births / total person-years   (births per person per year)
    d = total deaths / total person-years   (deaths per person per year)
    M = total net migrants / total years    (persons per year)

    Totals are used instead of averaging each period's value, so a long
    period (e.g. 1980-1990) counts more than a short one (e.g. 2007-2010).

    Parameters
    ----------
    periods : pandas DataFrame
        From net_migration_by_period.

    Returns
    -------
    dict
        {"b": ..., "d": ..., "M": ...}
    """
    person_years = periods["person_years"].sum()

    b = periods["births"].sum() / person_years
    d = periods["deaths"].sum() / person_years
    M = periods["M_total"].sum() / periods["length_years"].sum()

    return {"b": b, "d": d, "M": M}
