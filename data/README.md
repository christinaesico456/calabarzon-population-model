# Data: CALABARZON census population

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
