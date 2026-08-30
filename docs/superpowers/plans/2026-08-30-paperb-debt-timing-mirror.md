# Paper B Debt-Timing Mirror Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Relocate the contemporaneous Paper B outputs, add a self-contained lagged-debt mirror, and produce four reconciled cross-specification robustness exercises including a 30-replication paired country bootstrap.

**Architecture:** Each workflow owns a result root containing stage outputs, figures, generated documents, and robustness artifacts. Mirrored Stata code differs only in the debt-state mapping. A comparison layer reads both result roots, while a Stata outer-bootstrap program rebuilds the two theta source estimates, cutoff, and final kink equation on paired country draws.

**Tech Stack:** Stata 18 MP, PowerShell, Python 3.14 standard library, Python `unittest`, Markdown, CSV/DTA, LaTeX figure renderer.

**Spec:** `docs/superpowers/specs/2026-08-30-paperb-debt-timing-mirror-design.md`

## Global Constraints

- Current results root: `paperB/paperBresult/`.
- Lagged results root: `paperB_debt_lag/paperB_debt_lag/`.
- Lagged debt is `b_pre=L.debt_gdp`; current debt is `b_it=debt_gdp`.
- Debt outcome remains `F.debt_gdp-debt_gdp` in both pipelines.
- Main models retain `xtlsdvc, initial(bb) bias(2) vcov(50)`.
- Outer bootstrap uses 30 paired country draws, seed 20260830, and no nested LSDVC VCE bootstrap.
- Common-sample comparison must contain exactly 742 unique country-year observations.
- Existing unrelated dirty-worktree changes must be preserved.

---

### Task 1: Lock result-root and robustness contracts

**Files:**
- Create: `tests/test_paperb_debt_timing_mirror.py`
- Modify: existing Paper B tests that currently read root-level module outputs.

**Interfaces:**
- Consumes: `paperB/paperBresult/` and `paperB_debt_lag/paperB_debt_lag/`.
- Produces: behavioral assertions over real generated CSV files and documents.

- [ ] **Step 1: Write failing tests** asserting both result roots exist, stage outputs do not alias, current `b_it` equals current debt, lagged `b_pre` equals the strict prior-year debt, the common sample has 742 unique keys, standardized RSS rows satisfy hand-computed ratios, cross sensitivity has four unique combinations, and bootstrap outputs contain paired replications 1--30.
- [ ] **Step 2: Run `python -m unittest tests.test_paperb_debt_timing_mirror -v`** and confirm failure because the new result roots and artifacts do not exist.
- [ ] **Step 3: Update existing path fixtures** to read the authoritative current result root without weakening coefficient, formula, figure, or estimator assertions.
- [ ] **Step 4: Run `python -m unittest discover -s tests -v`** and record the expected failures caused only by missing implementation outputs.

### Task 2: Make the current workflow self-contained

**Files:**
- Modify: `paperB/code/baseline_twfe.do`
- Modify: `paperB/code/empirical_theta.do`
- Modify: `paperB/code/doomloop_no_state.do`
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/render_output.py`
- Modify: `paperB/render_figures.py`
- Move/regenerate: `paperB/paperBresult/**`

**Interfaces:**
- Consumes: project root plus result-root argument passed from PowerShell to Stata/Python.
- Produces: all current-specification stage artifacts and documents under `paperB/paperBresult/`.

- [ ] **Step 1: Parameterize Stata result paths** so each script receives project root and result root, with baseline, empirical-theta, doomloop, and figure subpaths derived from that result root.
- [ ] **Step 2: Parameterize Python renderers** with `--result-root`; remove reads and writes to root-level `baseline/`, `empirical_theta/`, and `doomloop/`.
- [ ] **Step 3: Update PowerShell orchestration** to create and validate only `paperB/paperBresult/` artifacts and pass that path to every stage.
- [ ] **Step 4: Seed the new result root from existing generated artifacts without deleting unrelated legacy files**, then run the path-contract tests until current-pipeline isolation passes.

### Task 3: Build the lagged-debt mirror

**Files:**
- Create: `paperB_debt_lag/code/baseline_twfe.do`
- Create: `paperB_debt_lag/code/empirical_theta.do`
- Create: `paperB_debt_lag/code/doomloop_no_state.do`
- Create: `paperB_debt_lag/run_workflow.ps1`
- Create: `paperB_debt_lag/render_output.py`
- Create: `paperB_debt_lag/render_figures.py`
- Create: `paperB_debt_lag/WORKFLOW.md`

**Interfaces:**
- Consumes: the same source panel and WSDI file as `paperB`.
- Produces: a structurally identical lagged-debt pipeline under `paperB_debt_lag/paperB_debt_lag/`.

- [ ] **Step 1: Copy the current workflow source layout** while excluding generated results.
- [ ] **Step 2: Replace only the theoretical debt state** with `b_pre=L.debt_gdp` across regressors, centering, interactions, theta, audits, labels, competing criteria, rendering, and QA; retain all non-debt choices.
- [ ] **Step 3: Run the focused debt-timing tests** and verify strict lag behavior across missing calendar years.
- [ ] **Step 4: Run the lagged full workflow** to generate baseline, theta, doomloop, figures, and documents.

### Task 4: Add deterministic profile and specification comparisons

**Files:**
- Create: `paperB/compare_debt_timing.py`
- Mirror: `paperB_debt_lag/compare_debt_timing.py`
- Generate: both result roots' `robustness/standardized_rss_profile.csv`
- Generate: both result roots' `robustness/near_optimal_cutoff_intervals.csv`
- Generate: both result roots' `robustness/cross_cutoff_sensitivity.csv`
- Generate: both result roots' `robustness/common_742_specification.csv`

**Interfaces:**
- Consumes: the two `doomloop_nostate_panel.csv`, theta RSS profiles, cutoffs, and model artifacts.
- Produces: reconciled comparison CSV files with explicit specification, sample, cutoff-source, and estimator fields.

- [ ] **Step 1: Extend failing tests** with literal RSS normalization examples and exact expected row keys for the profile and comparison tables.
- [ ] **Step 2: Run the focused test** and confirm it fails on missing comparison artifacts.
- [ ] **Step 3: Implement profile normalization and near-optimal intervals** at 0.1%, 0.5%, and 1.0% excess-RSS thresholds.
- [ ] **Step 4: Implement Stata-backed fixed-cutoff and common-sample estimates** with country/year effects and country-clustered inference; fail unless the common key set has N=742.
- [ ] **Step 5: Copy identical comparison outputs into both robustness directories** and run focused tests to green.

### Task 5: Add the paired 30-replication full-pipeline bootstrap

**Files:**
- Create: `paperB/code/bootstrap_full_pipeline.do`
- Mirror/adapt: `paperB_debt_lag/code/bootstrap_full_pipeline.do`
- Extend: `paperB/compare_debt_timing.py`
- Generate: both result roots' `robustness/country_bootstrap_draw_assignments.csv`
- Generate: both result roots' `robustness/country_bootstrap_replications.csv`
- Generate: both result roots' `robustness/country_bootstrap_summary.csv`

**Interfaces:**
- Consumes: shared draw assignments with columns `replicate`, `draw_slot`, and source country key.
- Produces: one retained status row per specification and requested replication plus distribution/sign-stability summaries.

- [ ] **Step 1: Add failing tests** for exactly 30 paired replication IDs, identical draw assignments across specifications, retained failure statuses, and summary denominators equal to valid replications.
- [ ] **Step 2: Generate draw assignments deterministically** with seed 20260830 and copy the exact file to both result roots.
- [ ] **Step 3: Implement each Stata bootstrap replication** by assigning new panel IDs to duplicated country blocks, recreating exact lags/leads, estimating the two required LSDVC models with `vcov(0)`, reconstructing theta, searching P10--P90, and estimating the final debt equation.
- [ ] **Step 4: Run both 30-replication bootstrap jobs**, retain success/failure status rows, and aggregate cutoff distribution and branch-sign stability.
- [ ] **Step 5: Run focused bootstrap tests** and inspect all failed replication reasons before accepting the summaries.

### Task 6: Render the supplemented documents and figures

**Files:**
- Modify: both `render_output.py` files.
- Modify: both `render_figures.py` files if robustness figures are added.
- Modify: both `WORKFLOW.md` files.
- Generate: both result roots' three Markdown documents and final figures.

**Interfaces:**
- Consumes: validated main and robustness artifacts.
- Produces: documents that state timing, sample, cutoff, bootstrap denominator, and interpretation consistently.

- [ ] **Step 1: Add the four robustness sections** to both result documents, including the standardized RSS/near-optimal intervals, four cross-cutoff estimates, common-742 comparison, and bootstrap cutoff/sign-stability summary.
- [ ] **Step 2: Explain that 30 outer draws are a compact stability diagnostic** and that main-model 50-repetition LSDVC VCE remains unchanged.
- [ ] **Step 3: Update each workflow guide** with independent run commands, directory ownership, expected runtime, and artifact map.
- [ ] **Step 4: Regenerate documents and run document/result reconciliation tests.**

### Task 7: Full verification

**Files:**
- Verify: all modified source, generated outputs, figures, and documents.

**Interfaces:**
- Consumes: completed current and lagged workflows.
- Produces: fresh evidence for final delivery.

- [ ] **Step 1: Run both full workflow entry points** without `-SkipStata` and confirm every Stata completion marker and no `r(#);` errors.
- [ ] **Step 2: Run `python -m unittest discover -s tests -v`** and require zero failures/errors.
- [ ] **Step 3: Re-run both workflows with `-SkipStata`** to prove existing-output reproducibility and fail-closed validation.
- [ ] **Step 4: Inspect generated RSS and bootstrap figures plus both Markdown reports** for clipping, missing labels, contradictory Ns, or stale current/lag terminology.
- [ ] **Step 5: Compare `git status --short` against the pre-change dirty-worktree inventory** and report only task-related additions/moves without reverting unrelated changes.
