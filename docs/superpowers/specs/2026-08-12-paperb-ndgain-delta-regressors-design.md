# Paper B ND-GAIN Delta Regressors Design

## Objective

Replace the Paper B main workflow's climate regressors `vulnerability100` and `readiness100` with `vulnerability_delta100` and `readiness_delta100` throughout baseline estimation, empirical-theta construction, the no-state Doomloop specifications, integrated QA, rendering, and workflow documentation.

## Scope and invariants

- The authoritative entry point remains `paperB/run_workflow.ps1` and the three authoritative Stata scripts remain under `paperB/code/`.
- The two delta columns continue to be divided by 100 at Stata import, matching the workflow's existing convention for source values stored as index points.
- `A` denotes `readiness_delta100 / 100`; `X` denotes `vulnerability_delta100 / 100` everywhere in the empirical equations.
- The Readiness outcome remains `A_it - A_i,t-1`, now computed from the normalized `readiness_delta100` series with strict panel lags.
- Existing outcome definitions, controls (`growth`, `ln_constantgdp`, `inflation_cpi`, `reserves`, `tt`), fixed effects, robust standard errors, locked-sample rules, cutoff search, and output filenames remain unchanged.
- Historical scripts outside the current three-stage workflow are not modified.

## Implementation

Update all model variable lists, centering scalars, interactions, algebra checks, audit exports, and labels in the three active Stata scripts. Update the PowerShell input contract and readiness-difference QA to require and validate the delta fields. Update the Python renderer's term maps and selected diagnostic variables. Revise `WORKFLOW.md` and generated documents to state the new source variables and normalized interpretation.

## Verification

Add an output-level regression test that rejects the old level variables in reported coefficients, confirms the delta variables and panel fields, and independently recomputes the Readiness outcome from strict prior-year `readiness_delta100`. Run that test before implementation to observe the expected failure, then rerun the entire Stata workflow and all tests. Finish with integrated `-SkipStata` QA and `git diff --check`.
