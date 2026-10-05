# Data: CALABARZON census population and vital statistics

This folder has two data files, both entered by hand:

| File | What it holds | Used for |
|---|---|---|
| `calabarzon_census.csv` | Census population by area | N0, calibration (Step 11), validation (RQ1) |
| `calabarzon_vital_stats.csv` | Registered births and deaths by year | b and d for V1, net migration M (Step 10) |

# Census population (`calabarzon_census.csv`)

All numbers in `calabarzon_census.csv` are entered by hand from official PSA
census reports. Nothing in this file may be estimated, rounded, or filled in
from memory. If a number cannot be found, leave the cell empty and write why
in `notes`.

## Columns

| Column | What to enter | Example format |
|---|---|---|
| `year` | Census year (already filled in) | `2015` |
| `census_date` | Census reference date, copied from the PSA report | `2015-08-01` (YYYY-MM-DD) |
| `batangas` | Population of Batangas province | `1234567` |
| `cavite` | Population of Cavite province | |
| `laguna` | Population of Laguna province | |
| `quezon` | Population of Quezon province, **without** Lucena City | |
| `lucena` | Population of Lucena City | |
| `rizal` | Population of Rizal province | |
| `total` | Official regional total, **only if PSA published one** for that year. Otherwise leave empty (the code will add up the areas). | |
| `source` | Exact source of the numbers in this row: publication title, table number, and link | `"PSA 2015 POPCEN, Table 1, https://..."` |
| `notes` | Anything a reader must know about this row | `"Quezon includes Aurora"` |

(The `1234567` example above is a placeholder that only shows the format. It is not real data.)

## Rules for entering numbers

1. **No commas or spaces inside numbers.** Write `12609803`, not `12,609,803`.
   A comma would split the number into two columns.
2. **Put text that contains commas inside double quotes**, for example
   `"PSA, Table 1"`. If you edit the file in Excel and save as CSV, Excel
   does this for you.
3. **Leave a cell empty** if the number is not available. Do not write 0,
   `NA`, or `-`.
4. **One source per row.** If one row uses two publications, list both in
   `source`, separated by a semicolon.

## CALABARZON pitfalls (check these for every year)

- **CALABARZON was created in 2002** (split from Southern Tagalog, Region IV).
  For census years before 2002, there is no published CALABARZON total, so
  enter the five provinces and Lucena separately and leave `total` empty.
- **Lucena City** is a highly urbanized city counted separately from Quezon
  province. Check whether each report's Quezon figure already includes
  Lucena. It must be counted **exactly once**: if the Quezon figure includes
  it, subtract it and write that in `notes`.
- **Aurora** was part of Quezon until 1979. For 1970 and 1975, check whether
  the Quezon figure includes Aurora, and write what you found in `notes`.
- Note in `notes` if a figure was revised in a later PSA publication, and
  which version you used.

## Official totals for cross-checking

From the project plan (CLAUDE.md). When you enter these years, the areas
should add up to these totals, and the `source` column still needs the
exact PSA table and link.

| Year | CALABARZON population |
|---|---|
| 2000 | 9,320,629 |
| 2010 | 12,609,803 |
| 2015 | 14,414,774 |
| 2020 | 16,195,042 |
| 2024 | 16,933,234 |

# Vital statistics (`calabarzon_vital_stats.csv`)

Registered births and deaths for CALABARZON, one row per calendar year from
1970 to 2024, entered by hand from PSA vital statistics publications. The
same rule applies: nothing may be estimated, rounded, or filled in from
memory. If a number cannot be found, leave the cell empty and write why in
`notes`.

## Why every year is needed (not only census years)

- **Net migration (Step 10)** uses the demographic balancing equation for each
  period between two censuses:
  M = (Pop_end - Pop_start) - (Births - Deaths).
  Births and Deaths are the totals over **all years in that period**, so a
  missing year makes M wrong for the whole period.
- **V1** uses b and d, the birth and death rates per person:
  b = crude birth rate / 1000, d = crude death rate / 1000.

## Columns

| Column | What to enter | Example format |
|---|---|---|
| `year` | Calendar year (already filled in) | `2010` |
| `births` | Number of registered live births in CALABARZON that year | `1234567` |
| `deaths` | Number of registered deaths in CALABARZON that year | `123456` |
| `crude_birth_rate` | Crude birth rate **per 1,000 population**, only if PSA published it for that year. Otherwise leave empty. | `22.5` |
| `crude_death_rate` | Crude death rate **per 1,000 population**, only if PSA published it for that year. Otherwise leave empty. | `5.1` |
| `source` | Exact source: publication title, table number, and link | `"PSA Vital Statistics Report 2010, Table 2, https://..."` |
| `notes` | Anything a reader must know about this row | `"sum of 5 provinces and Lucena"` |

(All examples above are placeholders that only show the format. They are not real data.)

The same entry rules as the census file apply: no commas inside numbers,
text with commas inside double quotes, and empty cells (not 0, `NA`, or `-`)
for missing values. Rates may have decimals; counts are whole numbers.

## Vital statistics pitfalls (check these for every year)

- **Before 2002 there is no CALABARZON region.** Add up Batangas, Cavite,
  Laguna, Quezon, Lucena City, and Rizal yourself, and write
  `"sum of 5 provinces and Lucena"` in `notes`. Do not use the Southern
  Tagalog (Region IV) total, which includes MIMAROPA provinces.
- **Lucena City** must be counted exactly once, the same as in the census
  file. Check whether each table's Quezon figure already includes it.
- **Aurora** was part of Quezon until 1979. For 1970 to 1978, check whether
  the Quezon figures include Aurora, and treat it the same way as in the
  census file, so births and deaths cover the same area as the population.
- **Basis of the counts.** Tables can count events by the place of usual
  residence (of the mother or the person who died) or by the place where the
  event happened or was registered. This matters a lot for CALABARZON,
  because many births and deaths of residents happen in Metro Manila
  hospitals. Use the same basis for all years if possible, and write the
  basis in `notes`.
- **Late registration.** Check whether a table counts events by the year they
  happened or the year they were registered, and write it in `notes`.
- **Under-registration.** Registration was less complete in older years, so
  older counts may be too low. This is a known limitation of the model; do
  not adjust the numbers, only note it.
- **Rates vs counts.** If a table gives only rates, enter the rates and leave
  the counts empty (and the reverse). Do not compute one from the other by
  hand; the code will do any conversion, so it can be checked.
