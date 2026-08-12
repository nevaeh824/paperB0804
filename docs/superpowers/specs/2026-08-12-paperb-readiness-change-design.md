# Paper B Readiness Change Equation Design

## Objective

Replace the retained Readiness level outcome with the contemporaneous one-year change:

```math
A_{it}-A_{i,t-1}
=\alpha_i+\lambda_t
+\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+
+\delta_HFT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_+
+\gamma_XX_{it}
+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.
```

The debt equation, empirical theta construction, and debt-equation cutoff are unchanged.

## Timing and sample

- For the retained horizon-one workflow, define `A_outcome = readiness100 - L.readiness100` after `xtset country_id year`.
- `A_outcome_year = year` whenever the change is observed.
- Stata's panel lag enforces strict adjacency: a missing preceding calendar year makes `A_outcome` missing.
- All right-hand-side variables remain at year `t`.
- The Readiness sample is relocked using the change outcome and the existing full set of construction inputs and controls.

## Model and outputs

- Keep `RDN1_core`, `RDN2_macro`, and `RDN3_full` as the only retained Readiness columns; their dependent variable becomes the Readiness change.
- Keep the inherited debt cutoff and the existing kink terms `FT*(c-theta)_+` and `FT*(theta-c)_+`.
- Preserve existing CSV/DTA schemas where possible, while retaining `readiness100` and adding `readiness_lag` to audit exports so the difference is reproducible.
- Keep existing figure filenames to avoid breaking document links, but update titles and prose from “Readiness level” to “Readiness change.”

## Validation

- A behavioral test must verify every nonmissing `A_outcome` equals current `readiness100` minus the same country's value in the immediately preceding calendar year.
- The formula-check output must include and pass the same identity.
- Integrated QA must require the new equation and reject the retained Readiness level equation.
- The full Stata workflow, Python tests, log scan, and whitespace checks must pass.
