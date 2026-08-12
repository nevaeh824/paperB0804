# Paper B Debt/GDP and Output Ratio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace theoretical debt with `debt_gdp` and estimate output models using adjacent-year ConstantGDP growth ratios with their lagged ratio as the common state control.

**Architecture:** Preserve the three-stage Stata pipeline and its machine-readable audit outputs. Change variable construction at the earliest stage in each script, propagate unambiguous names through theta and Doomloop, and make PowerShell/Python QA independently verify the new mappings.

**Tech Stack:** Stata 18, PowerShell, Python 3.14 `unittest`, Markdown.

## Global Constraints

- `b_it = debt_gdp_it / 100` after the existing source-unit conversion.
- `Y_outcome = ConstantGDP_(t+1) / ConstantGDP_t` and `Y_lag = ConstantGDP_t / ConstantGDP_(t-1)` on strict adjacent years with positive denominators.
- Every output regression includes `Y_lag` and excludes `growth` and `ln_constantgdp`.
- Baseline, spread, and Doomloop retain their current `growth ln_constantgdp` controls.
- Do not alter the ND-GAIN delta regressors, fixed effects, robust-SE convention, or cutoff procedure.

---

### Task 1: Encode failing data and model contracts

**Files:**
- Modify: `tests/test_paperb_growth_gdp_debt_contract.py`

**Interfaces:**
- Consumes: current generated CSV outputs.
- Produces: independent assertions for b mapping, adjacent-year GDP ratios, output controls, theta construction, and Doomloop debt/GDP change.

- [ ] Replace log-debt expectations with literal `debt_gdp` expectations.
- [ ] Add row-level checks for both ConstantGDP ratios and theta construction.
- [ ] Require one `Y_lag` and zero `growth`/`ln_constantgdp` in every Y model.
- [ ] Run the focused test and confirm it fails against commit `18f93c4` for the expected old definitions.

### Task 2: Update Stata estimation and audit outputs

**Files:**
- Modify: `paperB/code/baseline_twfe.do`
- Modify: `paperB/code/empirical_theta.do`
- Modify: `paperB/code/doomloop_no_state.do`

**Interfaces:**
- Consumes: `data0804/invest_panel_weo.csv`.
- Produces: CSV/DTA/log outputs with `debt_gdp`, `debt_gdp_mA_hat`, `Y_outcome`, and `Y_lag` under the new definitions.

- [ ] Map baseline b, centered b, interactions and effects to `debt_gdp`.
- [ ] Construct both Y ratios and remove output-only growth/log-GDP controls.
- [ ] Map empirical theta and Doomloop b components/outcome to debt/GDP.
- [ ] Update formula checks, labels, profiles, exports and metadata.

### Task 3: Update workflow QA and presentation

**Files:**
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/render_output.py`
- Modify: `paperB/WORKFLOW.md`

**Interfaces:**
- Consumes: regenerated machine-readable outputs.
- Produces: validated results, diagnostics, progress and workflow documentation.

- [ ] Enforce the new model-control and b-mapping contracts in PowerShell.
- [ ] Replace log-level output/debt formulas and labels in the renderer.
- [ ] Document exact adjacent-year ratio construction and sample restrictions.

### Task 4: Regenerate and verify

**Files:**
- Regenerate: `baseline/stata_outputs/*`, `empirical_theta/stata_outputs/*`, `doomloop/stata_outputs/*`, `paperB/figures/*`, and three generated Markdown reports.

**Interfaces:**
- Consumes: updated scripts and source panel.
- Produces: current regression results and verification evidence.

- [ ] Run `paperB/run_workflow.ps1` without `-SkipStata` and require exit 0.
- [ ] Run all Python unit tests and require zero failures.
- [ ] Independently verify coefficient membership and row-level ratio/difference identities.
- [ ] Scan active Stata logs for `r(#);`, run `git diff --check`, and report actual status.
