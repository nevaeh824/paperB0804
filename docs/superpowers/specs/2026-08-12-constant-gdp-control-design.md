# Paper B Constant-GDP Control Design

> Superseded on 2026-08-12 by the user's follow-up request to use WEO
> `NGDPRPPPPC` per-capita GDP. The implemented specification is documented in
> `paperB/WORKFLOW.md`; this file remains as the historical design record for
> the intermediate `NGDP_R` request. The final workflow also excludes `growth`
> from every regression specification.

## Objective

Replace the baseline control `ln(CurrentGDP)` with `ln(ConstantGDP)` throughout the reproducible Paper B workflow. Preserve the existing rule that the tax-base and Doomloop equations contain no GDP-level control. Update the upstream WEO merge so future data rebuilds reproduce `ConstantGDP` rather than relying on a manually appended CSV column.

## Source Definition

- `ConstantGDP` maps to WEO indicator `NGDP_R`.
- The source is the `Countries` worksheet of `WEOApr2026all.xlsx`.
- The source unit is billions of domestic currency at constant prices.
- The merge grain is one row per `iso3 + year`, restricted to 1995–2023.
- The regression variable is `ln_constantgdp = ln(ConstantGDP)` for strictly positive values; missing or nonpositive source values yield missing log values.
- The existing local CSV has already been reconciled to WEO: all 1,825 nonmissing `ConstantGDP` values agree exactly with `NGDP_R`, its two missing values agree with source missingness, and no nonpositive values occur.

## Data-Build Changes

Update `data0804/build_invest_panel_weo.py` so `WEO_FIELDS` includes `NGDP_R -> ConstantGDP` immediately after `NGDP -> CurrentGDP`. The generated CSV, documentation, and audit notebook must include the new field in their source reconciliation, coverage, descriptive statistics, and data-quality checks.

The generated documentation must distinguish current-price and constant-price GDP explicitly. References to the number of WEO target series, appended fields, missingness summaries, and local-currency comparability must be computed or worded consistently with the expanded field list.

The build remains a left join that preserves the base panel row order and values. It must stop on duplicate source series, duplicate panel keys, row-count changes, unmatched panel ISO3 codes, or WEO/output reconciliation failures.

## Estimation Changes

### Baseline

In `paperB/code/baseline_twfe.do`:

- confirm and audit `ConstantGDP`;
- construct `ln_constantgdp` from positive `ConstantGDP` values;
- replace `ln_currentgdp` with `ln_constantgdp` in the macro-control list, common-sample definition, all applicable model right-hand sides, profiles, variation diagnostics, correlations, collinearity checks, estimator validation, and run metadata;
- retain `CurrentGDP` as an unused source field if it remains in the input CSV;
- name metadata and output rows according to `ConstantGDP`, not the former current-price variable.

The baseline full specification becomes:

```text
macro controls: growth ln_constantgdp inflation_cpi
external controls: reserves tt
```

Country and year fixed effects, observation-level heteroskedasticity-robust standard errors, model sequence, centering rules, and all other variable definitions remain unchanged.

### Empirical theta

In `paperB/code/empirical_theta.do`:

- construct the same `ln_constantgdp` variable;
- use it only to reproduce the baseline spread common sample and full-interaction coefficients;
- update panel exports, audits, metadata, and estimator-validation variable lists accordingly;
- retain the tax equation controls as `growth inflation_cpi reserves tt`, with neither current-price nor constant-price GDP included.

The theta identity remains unchanged:

```math
\widehat\theta^A_{it}=debt\_gdp_{it}\widehat m^A_{it}+\widehat T^A_{it}.
```

### Doomloop

The Doomloop model definitions do not otherwise change. Both debt and readiness equations continue to exclude `CurrentGDP`, `ConstantGDP`, `ln_currentgdp`, and `ln_constantgdp`. They consume the newly rebuilt empirical-theta panel, so the upstream coefficient change is allowed to propagate through theta, cutoff searches, criterion comparisons, marginal effects, and figures.

## Rendering and Documentation

Update `paperB/render_output.py` so generated tables label the baseline control as `ln(ConstantGDP)` and select `ln_constantgdp` rows from machine-readable outputs. Generated narrative must state:

- baseline controls for real output level using `ln(ConstantGDP)`;
- the tax-base and Doomloop equations contain no GDP-level control;
- `ln_constantgdp` is used in empirical theta only for exact baseline reproduction.

Update `paperB/WORKFLOW.md` to match the executable workflow. Do not hand-edit numerical values in `paperB_results.md`, `paperB_diagnostics.md`, or `progress.md`; regenerate them through `paperB/run_workflow.ps1`.

## Pipeline QA and Stop Conditions

Update `paperB/run_workflow.ps1` to enforce all of the following:

1. Required source and generated GDP variables are present where expected.
2. Baseline and spread-reproduction outputs contain `ln_constantgdp` and do not contain `ln_currentgdp` as a regression variable.
3. Tax-model coefficient rows contain neither old nor new GDP controls.
4. Retained Doomloop coefficient rows contain none of `CurrentGDP`, `ConstantGDP`, `ln_currentgdp`, or `ln_constantgdp`.
5. Generated Paper B documents do not describe the baseline as controlling for `ln(CurrentGDP)`.
6. Existing unit, formula, sample, cutoff, criterion, estimator-reconciliation, and figure checks still pass.

Any failed condition stops the workflow before results are presented as valid.

## Test and Execution Strategy

Use test-first checks for the source and rendering contracts before changing production code. The red checks must demonstrate that the current build mapping and Paper B sources still use the old current-GDP control. After implementation:

1. run targeted static and Python tests for mapping, naming, and documentation contracts;
2. reconcile `ConstantGDP` in the existing analysis CSV against WEO `NGDP_R`;
3. run the full Paper B workflow, including all three Stata stages;
4. inspect logs for completion markers and absence of `r(#);` failures;
5. run the integrated PowerShell QA;
6. search executable sources and generated Paper B documents for stale semantic references;
7. inspect the final git diff without modifying unrelated user files.

The upstream build script will be validated with focused tests and source reconciliation because `cleaned_imf_like_panel_1995_2023.csv` is not currently present. The existing `data0804/invest_panel_weo.csv`, `data0804/WEOApr2026all.xlsx`, and unrelated untracked PDF remain user-owned and must not be overwritten or included in task commits.

## Deliverables

- Updated upstream builder and generated data documentation/notebook template.
- Updated authoritative Stata sources under `paperB/code/`.
- Updated Paper B runner QA and rendering logic.
- Updated `paperB/WORKFLOW.md`.
- Fully regenerated baseline, empirical-theta, Doomloop, figure, and Paper B document outputs.
- Verification evidence identifying commands run, exit status, and any limitations.

## Non-Goals

- Do not add a dual current-price/constant-price robustness specification.
- Do not change fixed effects, standard errors, controls other than the baseline GDP-level variable, samples except where the new variable's missingness requires it, or cutoff methodology.
- Do not introduce GDP controls into tax-base or Doomloop equations.
- Do not claim causal identification.
