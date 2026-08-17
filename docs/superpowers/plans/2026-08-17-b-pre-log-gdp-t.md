# Lagged Debt State and Log-GDP T Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace every theoretical current debt state with the strict prior-year debt state and redefine the empirical T indicator as the ratio of consecutive log constant-GDP levels.

**Architecture:** Generate `b_pre=L.debt_gdp` after `xtset` and propagate it through Baseline regressors, centering, interactions, theta construction, and competing criteria. Generate `T_it=ln_constantgdp/L.ln_constantgdp`, set `T_lead=F.T_it`, and use those variables throughout the T regressions while keeping the debt-change outcome `F.debt_gdp-debt_gdp` unchanged.

**Tech Stack:** Stata 18, Python 3.14 `unittest`, PowerShell workflow QA, Markdown renderer.

## Global Constraints

- `b_pre` must be missing across non-consecutive panel years.
- `T_it` is the ratio of logs, not log growth and not a ratio of GDP levels.
- `T_lead` must be the exact panel lead of `T_it`.
- Existing WSDI scaling and spread-lag behavior remain unchanged.

---

### Task 1: Lock the output contracts with failing integration tests

**Files:**
- Modify: `tests/test_wsdi_x_spread_lag.py`

**Interfaces:**
- Consumes: generated CSV outputs from Baseline, empirical theta, and Doomloop.
- Produces: behavioral assertions for exact lag timing and algebraic construction.

- [ ] Add tests that compare `b_pre` to the keyed prior-year `debt_gdp`, compare `T_it` to hand-computed log ratios, compare `T_lead` to the keyed next-year `T_it`, and verify theta/criterion propagation.
- [ ] Run `python -m unittest discover -s tests -v` and confirm the new tests fail because the old outputs still use current debt and `taxgdp`.

### Task 2: Implement the new state and T definitions

**Files:**
- Modify: `paperB/code/baseline_twfe.do`
- Modify: `paperB/code/empirical_theta.do`
- Modify: `paperB/code/doomloop_no_state.do`

**Interfaces:**
- Consumes: panel-sorted `debt_gdp` and positive `ConstantGDP`.
- Produces: `b_pre`, `T_it`, `T_lead`, revised theta, and revised competing criteria.

- [ ] Generate strict panel lags/leads and replace current-debt state uses in regressors, centering, marginal effects, theta, audits, and criterion variables.
- [ ] Preserve `b_outcome=F.debt_gdp-debt_gdp` as the debt-change dependent variable.

### Task 3: Update rendering, QA, and documentation

**Files:**
- Modify: `paperB/render_output.py`
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/WORKFLOW.md`

**Interfaces:**
- Consumes: revised machine-readable outputs.
- Produces: `paperB/paperB_results.md`, diagnostics, progress, and fail-closed contract checks.

- [ ] Replace current-debt and tax-base wording/formulas with `b_pre` and the consecutive log-GDP ratio.
- [ ] Require the new formulas and variables in integrated QA.

### Task 4: Regenerate and verify once

**Files:**
- Regenerate: `baseline/stata_outputs/`, `empirical_theta/stata_outputs/`, `doomloop/stata_outputs/`, `paperB/paperB_results.md`, `paperB/paperB_diagnostics.md`, `paperB/progress.md`, and final figures.

**Interfaces:**
- Consumes: revised code and source data.
- Produces: final results document and passing integration evidence.

- [ ] Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1`.
- [ ] Run `python -m unittest discover -s tests -v` once and report the result.
