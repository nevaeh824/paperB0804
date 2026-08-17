# Drop Baseline GDP Control and T Growth Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove `ln_constantgdp` from every Baseline spread regression and remove `growth` from every retained T-indicator regression.

**Architecture:** Delete each control from its stage-specific common-sample contract, regression RHS, diagnostics, replication checks, renderer, and PowerShell QA. Keep `ln_constantgdp` solely as an input to the consecutive-log T construction, keep Baseline `growth`/`inflation_cpi`, keep T `inflation_cpi`/`reserves`/`tt`, and leave Doomloop unchanged.

**Tech Stack:** Stata 18, Python 3.14 `unittest`, PowerShell, Markdown.

## Global Constraints

- Baseline outputs and the empirical-theta Baseline reproduction contain no GDP-level/log control.
- T-model coefficient outputs contain no `growth` control.
- T remains defined from consecutive `ln_constantgdp` values.
- Doomloop controls remain unchanged.

---

### Task 1: Add failing output-contract tests

**Files:**
- Modify: `tests/test_constant_gdp_control.py`

**Interfaces:**
- Consumes: generated model coefficient CSV files.
- Produces: assertions that detect either removed control re-entering its stage.

- [ ] Replace the prior GDP-inclusion expectations with Baseline GDP-exclusion expectations.
- [ ] Assert all retained T models exclude `growth` while their remaining control blocks stay intact.
- [ ] Run the test module and confirm it fails against the old outputs.

### Task 2: Implement regression and sample changes

**Files:**
- Modify: `paperB/code/baseline_twfe.do`
- Modify: `paperB/code/empirical_theta.do`

**Interfaces:**
- Consumes: existing WSDI, lagged debt, spread-lag, T, and remaining controls.
- Produces: revised fixed-sample Baseline and T estimates plus full-precision reproduction checks.

- [ ] Remove `ln_constantgdp` from all Baseline RHS/sample/validation lists.
- [ ] Remove `growth` from all T RHS/sample/profile/correlation/VIF/Wald lists.

### Task 3: Synchronize renderer, QA, and workflow documentation

**Files:**
- Modify: `paperB/render_output.py`
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/WORKFLOW.md`

**Interfaces:**
- Consumes: revised machine-readable output schemas.
- Produces: revised results tables and fail-closed checks.

- [ ] Remove the deleted control rows and update formulas/control descriptions.
- [ ] Require zero Baseline GDP controls and zero T growth rows.

### Task 4: Regenerate and verify

**Files:**
- Regenerate: all retained Stata outputs, figures, and Paper B Markdown documents.

**Interfaces:**
- Consumes: revised code and current source data.
- Produces: final `paperB/paperB_results.md` and passing QA evidence.

- [ ] Run the complete Paper B workflow.
- [ ] Run the complete Python test suite.
