# WSDI X and Lagged Sovereign Spread Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Use scaled WSDI days as theoretical variable X throughout the retained Paper B pipeline and control every Baseline sovereign-spread regression for the exact one-year lag of the spread.

**Architecture:** Baseline and empirical theta independently merge the read-only WSDI CSV by `iso3 year`, validate its key and scale, and expose one consistently named analytical variable, `wsdi_days`. Baseline and the empirical-theta spread reproduction construct `spread_lag` with Stata's panel lag operator; the generated theta panel carries both variables into the retained Doomloop stage.

**Tech Stack:** Stata 18, PowerShell, Python 3 `unittest`, Markdown.

## Global Constraints

- Use `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv` as the only WSDI input.
- Define analytical X as `wsdi_days * 0.01` and retain the name `wsdi_days`.
- Merge on unique `iso3 year` without deleting a main-panel row or appending a WSDI-only row.
- Define `spread_lag` as exact `L.bond_spreads` after `xtset`; do not fill gaps.
- Include `spread_lag` in all ten Baseline models and the empirical-theta Baseline reproduction, but not in tax or Doomloop equations.
- Preserve country and year fixed effects, observation-level robust VCE, and the existing macro/external control sets.
- Regenerate report documents from Stata CSV outputs; do not hand-edit generated numbers.

---

### Task 1: Lock the output contract with a failing integration test

**Files:**
- Create: `tests/test_wsdi_x_spread_lag.py`

**Interfaces:**
- Consumes: WSDI source CSV and generated Baseline, empirical-theta, and Doomloop CSV outputs.
- Produces: assertions for keyed WSDI scaling, X propagation, and lag-control presence.

- [ ] **Step 1: Write the failing tests**

Create `unittest` cases that require: (a) every Baseline model to contain `spread_lag`; (b) the empirical-theta `Spread_Interact_all` model to contain `spread_lag`; (c) Baseline linear models and retained Doomloop models to use `wsdi_days` and not `vulnerability100`; and (d) each nonmissing keyed value in `empirical_theta_panel.csv` to equal source `wsdi_days * 0.01` within `1e-12`.

- [ ] **Step 2: Run the tests to verify RED**

Run: `python -m unittest tests.test_wsdi_x_spread_lag -v`

Expected: FAIL because current outputs lack `spread_lag` and `wsdi_days` and still report `vulnerability100`.

### Task 2: Implement the Baseline merge, scale, lag, and models

**Files:**
- Modify: `paperB/code/baseline_twfe.do`

**Interfaces:**
- Consumes: `invest_panel_weo.csv` and unique WSDI `iso3 year wsdi_days` rows.
- Produces: scaled `wsdi_days`, exact `spread_lag`, fixed common sample, and updated Baseline CSV outputs.

- [ ] **Step 1: Merge and validate WSDI**

Import the WSDI CSV into a temporary dataset, stop on duplicate `iso3 year`, merge it into the untouched main-panel master, and record matched/nonmatched counts. Scale with `replace wsdi_days = wsdi_days*0.01` while posting the source-to-analysis difference to `unit_scaling_checks`.

- [ ] **Step 2: Construct the lag and update the common sample**

After `xtset country_id year`, generate `spread_lag = L.bond_spreads`. Replace `vulnerability100` with `wsdi_days` in the core, diagnostics, centering, interactions, marginal effects, and validation blocks; add `spread_lag` to `modelvars`.

- [ ] **Step 3: Add the lag to every regression**

Append `spread_lag` to `r1` through `r10`, include it in every displayed equation, coefficient collector, and LSDV validation RHS.

### Task 3: Mirror the contract in empirical theta and propagate X

**Files:**
- Modify: `paperB/code/empirical_theta.do`
- Modify: `paperB/code/doomloop_no_state.do`

**Interfaces:**
- Consumes: the same WSDI CSV and Baseline output contract.
- Produces: an exactly reproduced spread model, WSDI-based tax and theta models, and a theta panel with `wsdi_days` and `spread_lag`.

- [ ] **Step 1: Merge, scale, and construct the spread lag**

Repeat the validated WSDI merge and `*0.01` scaling before sample construction. Generate `spread_lag=L.bond_spreads` after `xtset` and include it in `spread_modelvars` and `spread_rhs`.

- [ ] **Step 2: Replace the X indicator throughout theta construction**

Use `wsdi_days` for spread/tax samples, centering scalars, linear tax regressors, marginal effects, raw formula checks, and theta-panel exports. Include `spread_lag` in spread coefficient and LSDV comparisons.

- [ ] **Step 3: Update retained Doomloop X controls**

Require and export `wsdi_days`, set `local xcontrol wsdi_days`, and remove retained `vulnerability100` references.

### Task 4: Update workflow QA and rendering

**Files:**
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/render_output.py`

**Interfaces:**
- Consumes: regenerated machine-readable outputs.
- Produces: fail-fast QA and human-readable reports with WSDI/lag labels and formulas.

- [ ] **Step 1: Strengthen workflow inputs and QA**

Require the WSDI CSV before Stata starts. Assert `wsdi_days` appears where X is required, `vulnerability100` does not appear in retained model coefficients, every Baseline model and `Spread_Interact_all` contains exactly one `spread_lag`, and the unit-scaling audit for `wsdi_days` passes.

- [ ] **Step 2: Update renderer variable maps and equations**

Replace display keys and selected diagnostic variables from `vulnerability100` to `wsdi_days`, add `spread_lag` to Baseline tables, and describe X as scaled WSDI days.

### Task 5: Run the full workflow and finish documentation

**Files:**
- Modify: `paperB/WORKFLOW.md`
- Regenerate: `paperB/paperB_results.md`
- Regenerate: `paperB/paperB_diagnostics.md`
- Regenerate: `paperB/progress.md`
- Regenerate: `paperB/figures/*`

**Interfaces:**
- Consumes: all updated Stata and rendering code.
- Produces: fresh validated results and synchronized documentation.

- [ ] **Step 1: Run the complete workflow**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1`

Expected: all three Stata stages finish, integrated QA passes, and the renderer rebuilds all three documents.

- [ ] **Step 2: Verify GREEN**

Run: `python -m unittest discover -s tests -v`

Expected: all WSDI/lag integration tests and existing constant-GDP tests pass.

- [ ] **Step 3: Update the workflow narrative**

Document the two-input data contract, keyed WSDI merge, `wsdi_days * 0.01` definition, strict spread lag, revised Baseline equation/sample, and downstream X propagation in `paperB/WORKFLOW.md`.

- [ ] **Step 4: Review the final diff and generated outputs**

Run: `git diff --check` and inspect `git status --short`, the updated formulas, coefficient variable sets, WSDI unit audit, and generated document references.
