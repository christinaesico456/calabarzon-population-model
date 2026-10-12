# Project Context: Population Dynamics Model (CALABARZON)

This file gives you (Claude Code) the full context of this project. Read it fully before doing anything.

## 1. Who you are working with and how

- I am Tina, a 4th-year BS Computer Science student at De La Salle University – Dasmariñas.
- This is our group's **Final Project in Computational Science**. I am doing **all the coding and data collection**. My groupmates are writing the paper.
- I work in **VS Code on Windows** and will push this project to **GitHub**.

**Your role:** Python programming mentor, mathematical modeling guide, and code reviewer.

**How to work with me (important):**
1. **Go step by step, one small step at a time.** After each step, stop and wait for me before starting the next step. Do not jump ahead or write several files at once.
2. **You make the file changes and run the commands.** You create, edit, and delete files yourself, and you run the commands and tests yourself.
3. **Explain before each change.** Briefly explain what you are adding and why, show how it connects to the equation, and show me the key code.
4. **Show and explain the output.** After running something, show me the output and explain what it means.
5. **I want to understand everything.** I must explain every line during our defense. Keep code beginner/intermediate friendly, clearly commented, and simple. No clever tricks.
6. **Never fabricate data, results, or references.** Any made-up numbers must be clearly labeled as TEST VALUES in both code and output. Do not claim the model is verified or validated unless the tests were actually run.
7. **Keep math and code consistent.** Function names and variables should match the equations below.
8. **Only use NumPy, Pandas, Matplotlib**, and **SciPy only for calibration** (curve_fit). No other libraries unless I agree.
9. **Ask "OK to commit?" before every commit.** Commit at sensible points with small, clear messages, but only after I say yes.
10. When writing any text meant for the paper: simple English, natural student academic tone, no em dashes.

## 2. Instructor requirements (summary)

**Goals:** understand the system; create basic starting code; verify the code; use it for sensitivity analysis, forecasting under prescribed conditions, tables and graphs, and a summary report.

**Must include:** a basic model, plus one or more added components that relax initial assumptions; model runs that answer research questions; verification; validation where possible.

**Rubric:** Programming Implementation 50%, Documentation 30%, Individual Performance/Presentation 20%. The code must work, be mathematically correct, testable, and explainable.

**Paper outline:** (1) Introduction: Statement of the Problem, Objectives; (2) Conceptual model with diagram; (3) Assumptions, variables, relationships, equations, functions; (4) Program codes (Python); (5) Results in tables and graphs; (6) Validation, analysis, reporting; (7) Conclusion; (8) References.

## 3. Decisions already made

- **Population:** human population of **CALABARZON (Region IV-A)**: Batangas, Cavite, Laguna, Quezon, Rizal (plus Lucena City, see pitfalls).
- **Why CALABARZON:** migration is significant (so V2 matters), and growth is slowing (needed to estimate K). National level was the backup option.
- **Model progression:**
  - **V1:** birth-death model (basic)
  - **V2:** logistic growth with net migration (relaxes "unlimited resources" and "closed population")
  - **V3:** V2 used for sensitivity analysis, scenarios, and forecasting
- **Numerical method:** Euler (main, explainable), RK4 as cross-check. Δt = 0.1 year.
- **Confirmed by the group (October 5, 2026):** in V2, r and K are **calibrated** from the 1970–2010 census data (not taken from vital statistics).

## 4. Mathematical model

### Notation

| Symbol | Meaning | Units |
|---|---|---|
| t | time since start year (t = 0 at 1970) | years |
| N(t) | CALABARZON population | persons |
| N0 | population at t = 0 (1970 census) | persons |
| b, d | birth and death rate per person | 1/year |
| r | net growth rate (V1: r = b − d; V2: calibrated intrinsic rate) | 1/year |
| K | carrying capacity | persons |
| M | net migration (in minus out) | persons/year |
| Δt | time step | years |

PSA crude birth/death rates are per 1,000 people: divide by 1,000 to get b and d.
Census reference dates differ (e.g., May 1 2010 and 2020, Aug 1 2015, Jul 1 2024): use fractional years (Aug 1 2015 ≈ 2015.58).

### V1: Birth-death
- Equation: dN/dt = (b − d) N
- Exact solution: N(t) = N0 · e^((b − d) t)
- Checks: b = d stays constant; b < d declines; doubling time = ln(2)/(b − d)

### V2: Logistic + migration
- Equation: dN/dt = r N (1 − N/K) + M
- With M = 0, exact solution: N(t) = K / (1 + ((K − N0)/N0) e^(−r t))
- Equilibrium: N* = (K/2) [1 + sqrt(1 + 4M/(rK))]
  - M = 0 → N* = K; M > 0 → N* > K; M < 0 → N* < K; M < −rK/4 → no positive equilibrium (collapse)
- Why r is calibrated in V2: observed birth/death rates already include crowding, i.e., they equal r(1 − N/K), not r. Vital statistics become a reasonableness check.
- Known limitation: when N > K, natural increase becomes negative; for humans, K is a summary of social/economic limits, not a literal food/space limit.

### Numerical methods
- Euler: N[k+1] = N[k] + Δt · f(N[k])
- RK4: k1 = f(N), k2 = f(N + Δt/2·k1), k3 = f(N + Δt/2·k2), k4 = f(N + Δt·k3); N[k+1] = N[k] + Δt/6 (k1 + 2k2 + 2k3 + k4)
- Boundary condition: population cannot go below 0.
- Use np.linspace for the time grid (np.arange with decimal steps can add/drop the last point).

### Calibration and error measures
- Calibrate V2 (r, K) on 1970–2010 census by minimizing SSE = Σ (N_model − N_census)², using scipy.optimize.curve_fit.
- Validate on 2015, 2020, 2024 only: RMSE (persons) and MAPE (%).
- Net migration estimate (demographic balancing equation): M = (Pop_end − Pop_start) − (Births − Deaths) over each intercensal period.

### Parameter sources

| Parameter | V1 | V2 | Varied in experiments? |
|---|---|---|---|
| N0 | 1970 census | 1970 census | No |
| b, d | PSA vital statistics | check only | V1 only |
| r | b − d | calibrated | Yes (RQ2, RQ4) |
| K | not used | calibrated | Yes (RQ2) |
| M | not used | balancing equation | Yes (RQ2, RQ3, RQ4) |

## 5. Research questions (each must map to code that produces a table and a graph)

| RQ | Question | Simulation | Output |
|---|---|---|---|
| RQ1 (validation) | How accurately do V1 and V2 reproduce CALABARZON's census population from 2015 to 2024? | Calibrate on 1970–2010, test on 2015/2020/2024 | Observed vs simulated table; observed points vs model lines graph; RMSE, MAPE |
| RQ2 (sensitivity) | Which parameter (r, K, M) most affects the projected 2050 population? | Low/baseline/high, one parameter at a time | Low/Baseline/High/% change table; trajectories or tornado chart |
| RQ3 | How does net migration affect long-term population and equilibrium? | Range of M from 0 to high in-migration | M vs equilibrium table; multiple trajectories |
| RQ4 (forecasting) | What population does the model project for 2030, 2040, 2050 under scenarios? | Baseline, lower fertility, higher mortality (lower r), high migration | Scenario × year table; all scenarios on one plot |

Forecasts are **projections under stated assumptions**, not predictions. Always label them that way.

## 6. Data plan (I collect this myself)

**Census years:** 1970, 1975, 1980, 1990, 1995, 2000, 2007, 2010, 2015, 2020, 2024.

**Known official totals for cross-checking (PSA):**

| Year | CALABARZON population |
|---|---|
| 2000 | 9,320,629 |
| 2010 | 12,609,803 |
| 2015 | 14,414,774 |
| 2020 | 16,195,042 |
| 2024 | 16,933,234 |

Older years still need to be collected from PSA census reports. Do not fill them in from memory.

**Pitfalls:**
- CALABARZON was created in 2002 (split from Southern Tagalog, Region IV). For older years, sum the 5 provinces.
- **Lucena City** is a highly urbanized city counted separately from Quezon province. Include it exactly once in regional totals.
- **Aurora** was part of Quezon until 1979. Check whether older Quezon figures include it.
- Birth/death registration is incomplete in older years (limitation).
- Record the exact source (table, publication, link) for every number.

**Planned data file:** `data/calabarzon_census.csv` with columns like: year, census_date, batangas, cavite, laguna, quezon, lucena, rizal, total, source.

## 7. Suggested repository structure (build gradually, not all at once)

```
population-dynamics-calabarzon/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── .gitignore            (.venv/, __pycache__/)
├── data/                 (census CSV, vital statistics)
├── src/
│   ├── models.py         (rate_v1, rate_v2)
│   ├── solvers.py        (make_time_grid, euler_solve, rk4_solve)
│   ├── exact.py          (exact_v1, exact_logistic, equilibrium_v2)
│   ├── calibration.py    (curve_fit wrapper, RMSE, MAPE)
│   └── data_loader.py
├── tests/                (verification tests)
├── notebooks/ or scripts/ (experiments for RQ1 to RQ4)
└── results/              (tables as CSV, graphs as PNG)
```

If you think a simpler structure is better for explainability, suggest it and explain why.

**Design decisions already agreed:**
- Rate functions take `(N, params)` where params is a dict, e.g., `rate_v2(N, params)` uses params["r"], params["K"], params["M"].
- One solver works for both models: `euler_solve(rate_func, N0, params, t_end, dt)` returns `(t, N)`.

## 8. Build order (one step at a time)

1. Environment setup: folder, `.venv`, `pip install numpy matplotlib`, `requirements.txt`, `git init`, `.gitignore`
2. V1 rate function
3. V2 rate function
4. Time grid + Euler solver
5. RK4 solver
6. Exact solutions + equilibrium function
7. Test run with clearly labeled TEST VALUES + first graph
8. Verification tests (Phase 5), presented as a table: Test | Expected Result | Actual Result | Status. Include: Euler vs exact (V1 and logistic), error shrinks when Δt is halved, b = d constant, M = 0 reduces to logistic, removing K and M reduces to V1, N0 = K stays at K, N0 > K declines, equilibrium matches simulation, large negative M never gives negative N.
9. Data loader for the census CSV
10. Net migration estimate
11. Calibration (SciPy) + RMSE/MAPE
12. RQ1 validation run
13. RQ2 sensitivity analysis (ranges must be justified, not arbitrary)
14. RQ3 migration experiments
15. RQ4 scenario forecasts
16. Export all tables (CSV) and graphs (PNG) to results/
17. README for GitHub

Every graph must state x-axis, y-axis, units, and purpose. No decorative graphs.

## 9. Current status

- Phases 1 to 3 (research, model selection, mathematical model) are done and documented in Google Docs.
- Deadline not yet confirmed. Tentative 4-week plan started October 5, 2026: Week 1 code + verification, Week 2 data + calibration + validation, Week 3 sensitivity + scenarios + results, Week 4 paper review + code walkthrough for groupmates.

**Build order steps 1 to 9 are done** (all tested with TEST VALUES only, no real data used yet):

| Step | Done | Where |
|---|---|---|
| 1 | Environment, `.venv`, `requirements.txt` (pip freeze style), `.gitignore`, Git repo | project root |
| 2–3 | `rate_v1`, `rate_v2` | `src/models.py` |
| 4–5 | `make_time_grid`, `euler_solve`, `rk4_solve` (N ≥ 0 boundary in both) | `src/solvers.py` |
| 6 | `exact_v1`, `exact_logistic`, `equilibrium_v2` | `src/exact.py` |
| 7 | First test run + V2 migration graph | `scripts/test_run.py` |
| 8 | 12 verification tests, all PASS; Euler error graph | `tests/verify.py`, `scripts/plot_verification.py` |
| 9 | `load_census` + 7 loader checks, all PASS | `src/data_loader.py`, `tests/check_data_loader.py`, `tests/data/` |

**Steps 10 to 17: code written October 12, 2026, all at once (Tina's choice), tested with TEST VALUES only. No real results yet** (real runs stop until the vital statistics are entered):

| Step | Done | Where |
|---|---|---|
| 10 | `load_vital_stats`; `events_between`, `net_migration_by_period`, `average_over_periods`; 6 checks PASS | `src/data_loader.py`, `src/migration.py`, `tests/check_migration.py`, `scripts/net_migration.py` |
| 11 | `sse`, `rmse`, `mape`, `calibrate_v2` (curve_fit on the Euler solution); `solve_at_times`; shared setup `build_baseline`; 4 checks PASS (incl. recovering known r, K, M from TEST files) | `src/calibration.py`, `src/solvers.py`, `src/baseline.py`, `tests/check_calibration.py`, `tests/make_test_data.py` |
| 12–15 | RQ1 validation, RQ2 sensitivity (tornado), RQ3 migration vs equilibrium, RQ4 scenarios | `scripts/rq1_validation.py` … `scripts/rq4_forecast.py` |
| 16 | `run_all` runs every results script, saves CSV + PNG to `results/` | `scripts/run_all.py` |
| 17 | README for GitHub | `README.md` |

**Data status** (Tina enters all numbers from PSA sources):
- `data/calabarzon_census.csv`: **1970 to 2020 entered** (10 census years, 2007 boundaries, sources recorded, all pass the loader's sum check; 2000 to 2020 match the official PSA totals). **2024 row still empty.**
- `data/calabarzon_vital_stats.csv`: registered births and deaths, 1970 to 2024. **Still empty.**
- Entry rules and pitfalls: `data/README.md`

**Open decisions (need group confirmation). D1 to D5 are already used PROVISIONALLY in the code (Tina's choice, October 12, 2026); if the group decides differently, change the one marked place in the code:**

| # | Decision | Needed by | Options | Claude's recommendation |
|---|---|---|---|---|
| D1 | Partial years at census dates when summing births and deaths over an intercensal period | Step 10 | (a) split each end year in proportion to the census date, e.g. May 1 census: 4/12 of that year's events before, 8/12 after; (b) count whole calendar years only | (a), assumes events are spread evenly through the year; state this as an assumption |
| D2 | Which b and d V1 uses | Step 12 (RQ1) | (a) crude rates over 1970 to 2010 (the calibration period), computed as total births (deaths) / total person-years; (b) the 1970 rates only | (a), so V1 and V2 use information from the same period. Code: `average_over_periods` in `src/migration.py` |
| D3 | Which M is used while calibrating r and K | Step 11 | (a) average yearly M over 1970 to 2010 from the balancing equation, held fixed; (b) fit M as a third parameter; (c) M = 0 | (a). (b) would no longer take M from data, (c) contradicts V2. Because M is not 0, curve_fit must fit the Euler solution, not `exact_logistic` |
| D4 | Sensitivity ranges for RQ2 | Step 13 | (a) r and K: calibrated value ± 2 standard errors; M: smallest to largest observed period M (1970 to 2010); (b) the same ± % for all three | (a), every range comes from the data. Note: the answer to RQ2 depends on these ranges, so state them in the paper. Code: top of `scripts/rq2_sensitivity.py` |
| D5 | Size of the RQ4 fertility and mortality changes | Step 15 | `SCENARIO_CHANGE = 0.10` (10% lower b or 10% higher d, r changes by the same amount) | Placeholder only: replace with a value from a cited source. Code: top of `scripts/rq4_forecast.py` |

**Conventions already set:**
- Run scripts and tests from the project folder with `python -m`, e.g. `python -m tests.verify`.
- Outputs made from TEST VALUES are named `results/TEST_*` and are ignored by Git.
- In the data loader, t = 0 at the **1970 census date** (not January 1, 1970), so a calendar year Y is t = Y − (1970 census decimal year).
- Verification tolerance is 0.5% max relative error. Revisit it after RQ1 gives the real MAPE.
- Results scripts take `--test` to use the TEST VALUES files in `tests/data/` (outputs `results/TEST_*`). Without it they use `data/`.
- All projections (RQ2 to RQ4) start from the **latest census count** (jump-off point), not from the model's value at that date. RQ1 runs from 1970.
- A calendar year Y as a projection target means January 1 of Y (decimal year Y.0).

**Next:** enter the vital statistics and the 2024 census row, then run `python -m scripts.run_all` for the first real results, and check them carefully. Get group confirmation of D1 to D5. Continue the lessons (Lesson 2 questions still open).