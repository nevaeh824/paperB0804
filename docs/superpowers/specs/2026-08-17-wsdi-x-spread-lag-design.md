# WSDI X and Lagged Sovereign Spread Design

## Goal

Replace the empirical indicator used for theoretical variable \(X_{it}\) from ND-GAIN `vulnerability100` to `wsdi_days` from `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`, scaled as `wsdi_days * 0.01`, and add the exact one-year lag of the sovereign spread, \(s_{i,t-1}\), to every Baseline sovereign-spread regression.

## Scope and assumptions

- The change applies to every retained stage in `paperB/WORKFLOW.md`: Baseline, empirical theta, and the no-state Doomloop specifications.
- `wsdi_days` is merged by the unique `iso3 year` key. The main panel remains the master dataset; WSDI-only rows are not appended and unmatched main-panel rows retain missing `wsdi_days`.
- The analytical variable keeps the name `wsdi_days`. It is recast to double and multiplied by `0.01` after the merge. The old name `vulnerability100` is not reused for WSDI values.
- `spread_lag = L.bond_spreads` is generated only after `xtset country_id year`, so a year gap never counts as a one-year lag.
- The fixed Baseline common sample includes `spread_lag` and scaled `wsdi_days`. Consequently, all ten nested Baseline specifications use the same sample and all include the lag control.
- The empirical-theta spread reproduction uses the identical WSDI merge, sample definition, centering, interactions, and `spread_lag` control. Its tax equation uses WSDI as \(X\) but does not use `spread_lag`, because that lag is specific to the sovereign-spread equation.
- The retained Doomloop stage reads `wsdi_days` from `empirical_theta_panel.dta` and uses it as its explicit \(X\) control.
- Generated result documents are rebuilt from fresh Stata outputs; numerical report files are not edited by hand.

## Data contract and validation

The WSDI source has 1,464 unique `iso3 year` rows covering 61 sovereigns from 1995 through 2018. All 1,464 keys occur in the main panel; 1,233 rows have nonmissing `wsdi_days`. Both Baseline and empirical theta will stop on duplicate WSDI keys, audit merge coverage, and write a unit-scaling check proving that the analytical value equals the source value times `0.01` to a tolerance of `1e-12`.

## Regression design

Every Baseline model becomes

\[
s_{it}=\alpha_i+\lambda_t+\rho_s s_{i,t-1}+f(A_{it},b_{it},X_{it})+\Gamma'W_{it}+\varepsilon_{it},
\]

where `spread_lag` is included in every progressive specification and

\[
X_{it}=0.01\times wsdi\_days_{it}.
\]

The full interaction model retains centered \(A\), \(b\), and \(X\), plus \(A\times b\) and \(A\times X\). The raw-scale marginal-effect identities are unchanged apart from the empirical definition of \(X\). Because `spread_lag` is a control and not an interaction moderator, it does not enter the marginal-effect formula.

## Outputs and documentation

- Baseline coefficient, equation, audit, profile, variation, collinearity, and metadata outputs identify `wsdi_days` and `spread_lag` explicitly.
- `empirical_theta_panel.dta/.csv` carries `wsdi_days` and `spread_lag` for downstream auditability.
- No retained coefficient output uses `vulnerability100` as \(X\).
- `render_output.py`, `run_workflow.ps1`, and `paperB/WORKFLOW.md` document and enforce the new indicator, source, scaling, merge, sample, and lag-control contract.

## Test strategy

An integration-output test first fails against the current outputs because they contain `vulnerability100` and lack `spread_lag`. After implementation, the full Stata workflow regenerates all outputs. Tests then verify WSDI scaling by keyed comparison with the source CSV, lag presence in all Baseline spread models and the empirical-theta spread reproduction, and propagation of `wsdi_days` into retained Doomloop models. The existing constant-GDP tests remain green.
