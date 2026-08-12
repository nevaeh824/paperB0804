# Paper B ND-GAIN Delta Regressors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `vulnerability_delta100` and `readiness_delta100` the only ND-GAIN regressors in the active Paper B workflow and regenerate all results and documents.

**Architecture:** Preserve the existing three-stage pipeline and replace the two source fields consistently at each stage boundary. Strengthen output-level tests and integrated QA so generated coefficients and Readiness differences cannot silently revert to the level fields.

**Tech Stack:** Stata 18, PowerShell, Python 3.14 `unittest`, Markdown

## Global Constraints

- Normalize both source delta columns by dividing by 100 at Stata import.
- Keep all outcomes, controls, fixed effects, sample-locking rules, and cutoff procedures unchanged.
- Modify only the three active Stata scripts; leave historical specifications untouched.
- Preserve current uncommitted user changes and do not commit without a current explicit request.

---

### Task 1: Lock the generated-output contract

**Files:**
- Modify: `tests/test_paperb_growth_gdp_debt_contract.py`

**Interfaces:**
- Consumes: generated coefficient CSVs and Doomloop panel CSV
- Produces: assertions for delta regressor use and strict delta-Readiness differencing

- [ ] Add assertions that active model coefficient outputs contain the applicable delta fields and contain neither old level field.
- [ ] Recompute every nonmissing `A_outcome` as current normalized `readiness_delta100` minus its strict previous-year value.
- [ ] Run the focused test and confirm it fails against the existing level-field outputs.

### Task 2: Replace active regression inputs

**Files:**
- Modify: `paperB/code/baseline_twfe.do`
- Modify: `paperB/code/empirical_theta.do`
- Modify: `paperB/code/doomloop_no_state.do`

**Interfaces:**
- Consumes: `vulnerability_delta100` and `readiness_delta100` from `invest_panel_weo.csv`
- Produces: regenerated baseline, empirical-theta, and Doomloop machine-readable outputs

- [ ] Replace level fields in scaling, labels, sample locks, regressors, centering, interactions, algebra checks, and exports.
- [ ] Construct the Readiness outcome and strict lag from `readiness_delta100`.
- [ ] Keep output filenames and all non-ND-GAIN model choices unchanged.

### Task 3: Update orchestration and documentation

**Files:**
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/render_output.py`
- Modify: `paperB/WORKFLOW.md`
- Regenerate: `paperB/paperB_results.md`
- Regenerate: `paperB/paperB_diagnostics.md`
- Regenerate: `paperB/progress.md`

**Interfaces:**
- Consumes: regenerated stage CSVs
- Produces: validated documentation and figures using delta-variable labels

- [ ] Require the two delta fields in the workflow input contract and reject old level regressors in generated coefficient outputs.
- [ ] Update renderer term maps and diagnostic selections.
- [ ] Document the exact `A` and `X` mappings and the delta-based Readiness outcome.
- [ ] Run the complete workflow to regenerate results, figures, and documents.

### Task 4: Verify the complete handoff

**Files:**
- Test: `tests/test_paperb_growth_gdp_debt_contract.py`
- Test: `tests/test_constant_gdp_contract.py`

**Interfaces:**
- Consumes: all changed code and regenerated artifacts
- Produces: final evidence of correctness

- [ ] Run all Python tests and confirm they pass.
- [ ] Run `paperB/run_workflow.ps1 -SkipStata` and confirm integrated QA passes.
- [ ] Search active code and generated documents for unintended level-field regression references.
- [ ] Run `git diff --check` and review the final working-tree scope.
