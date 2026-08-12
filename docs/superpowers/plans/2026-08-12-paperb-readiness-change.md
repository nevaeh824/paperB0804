# Paper B Readiness Change Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the retained Readiness equation explain `A_it - A_i,t-1` while retaining the debt-derived cutoff and current right-hand-side specification.

**Architecture:** Construct a panel-aware lag and difference inside the single retained Doom-loop entry point, relock its Readiness sample, and propagate the changed outcome through existing RDN models and generated artifacts. Preserve model names and file interfaces while updating equations, labels, audits, and narrative output.

**Tech Stack:** Stata 18, Python `unittest`, PowerShell workflow QA, Markdown renderer.

## Global Constraints

- `A_outcome = readiness100 - L.readiness100` for the horizon-one retained workflow.
- The lag must be from the immediately preceding calendar year in the same country.
- All regressors remain measured at `t`.
- Readiness inherits the full debt equation's theta cutoff and performs no independent cutoff search.
- `growth` and `ln_capitagdp` remain in every retained regression.

---

### Task 1: Add the behavioral regression contract

**Files:**
- Modify: `tests/test_paperb_growth_gdp_debt_contract.py`

**Interfaces:**
- Consumes: `doomloop/stata_outputs/doomloop_nostate_panel.csv`.
- Produces: a direct observation-level assertion for the Readiness difference and outcome year.

- [ ] **Step 1: Add a test that reconstructs the preceding-year value by country and compares it with every nonmissing `A_outcome`.**
- [ ] **Step 2: Run the focused test and verify that current level outcomes fail the difference identity.**

### Task 2: Implement the Readiness change equation

**Files:**
- Modify: `paperB/code/doomloop_no_state.do`

**Interfaces:**
- Consumes: `readiness100`, the panel key, inherited debt cutoff, theta, FT, X, and controls.
- Produces: changed `A_outcome`, relocked RDN samples, refreshed estimates, formula checks, audit fields, and figures.

- [ ] **Step 1: Generate `readiness_lag=L.readiness100`, `A_outcome=readiness100-readiness_lag`, and `A_outcome_year=year`.**
- [ ] **Step 2: Update labels, stored equations, display text, and figure titles.**
- [ ] **Step 3: Add the exact outcome identity to formula checks and export `readiness_lag`.**

### Task 3: Update documentation and integrated QA

**Files:**
- Modify: `paperB/render_output.py`
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/WORKFLOW.md`

**Interfaces:**
- Consumes: refreshed Readiness outputs.
- Produces: consistent change-equation prose and QA gates.

- [ ] **Step 1: Replace Readiness level formula, headings, summaries, and interpretations with Readiness change.**
- [ ] **Step 2: Require the new formula in workflow QA and forbid the old retained level formula.**
- [ ] **Step 3: Update the durable workflow procedure and validation checklist.**

### Task 4: Regenerate and verify

**Files:**
- Regenerate: `doomloop/stata_outputs/*`
- Regenerate: `doomloop/figures/*`
- Regenerate: `paperB/figures/*`
- Regenerate: `paperB/paperB_results.md`
- Regenerate: `paperB/paperB_diagnostics.md`
- Regenerate: `paperB/progress.md`

**Interfaces:**
- Consumes: unchanged baseline and empirical-theta outputs plus the modified Doom-loop code.
- Produces: a complete Readiness-change result set and documentation.

- [ ] **Step 1: Run `paperB/run_workflow.ps1` without `-SkipStata`.**
- [ ] **Step 2: Run `py -3.14 -m unittest discover -s tests -v`.**
- [ ] **Step 3: Scan Stata logs, old formulas, and `git diff --check` before reporting completion.**
