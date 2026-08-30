# Paper B Debt-Timing Mirror and Robustness Design

## Objective

Keep the contemporaneous-debt specification as the authoritative `paperB` pipeline, add an independently runnable lagged-debt mirror at `paperB_debt_lag`, relocate each pipeline's generated artifacts beneath its own result root, and compare the two specifications with four reproducible robustness exercises.

## Directory boundaries

The contemporaneous pipeline keeps source code and workflow documentation at `paperB/` and writes every generated artifact beneath `paperB/paperBresult/`:

```text
paperB/
├── code/
├── run_workflow.ps1
├── render_output.py
├── render_figures.py
├── WORKFLOW.md
└── paperBresult/
    ├── baseline/stata_outputs/
    ├── empirical_theta/stata_outputs/
    ├── doomloop/stata_outputs/
    ├── figures/
    ├── robustness/
    ├── paperB_results.md
    ├── paperB_diagnostics.md
    └── progress.md
```

The lagged-debt pipeline mirrors that layout, with its generated result root named exactly as requested:

```text
paperB_debt_lag/
├── code/
├── run_workflow.ps1
├── render_output.py
├── render_figures.py
├── WORKFLOW.md
└── paperB_debt_lag/
    ├── baseline/stata_outputs/
    ├── empirical_theta/stata_outputs/
    ├── doomloop/stata_outputs/
    ├── figures/
    ├── robustness/
    ├── paperB_results.md
    ├── paperB_diagnostics.md
    └── progress.md
```

The two workflows may read the shared source data under `data0804/` and `WSDI/`, but may not read or overwrite one another's stage outputs. Existing root-level module outputs are treated as legacy snapshots; the new workflows no longer depend on them.

## Debt-timing specifications

The contemporaneous pipeline uses `b_it=debt_gdp` in the baseline spread equation, its centering and interaction terms, the marginal spread-relief term, theta, formula audits, and competing debt criteria.

The mirror pipeline differs only in this theoretical debt state: it uses the strict panel lag `b_pre=L.debt_gdp`. Gaps in calendar years therefore yield missing `b_pre`. The debt-change outcome remains `F.debt_gdp-debt_gdp`, the T equation remains unchanged, and all other estimators, controls, units, samples, cutoff search rules, figures, and document structure remain aligned with `paperB`.

## Robustness experiments

The same comparison artifacts are copied into both result roots under `robustness/`, and both generated results documents explain them.

### Standardized RSS profiles

For each specification's theta criterion, retain every searched cutoff and report:

- raw cutoff;
- standardized cutoff `(c-median(theta))/sd(theta)` on that specification's full debt-equation sample;
- `rss_index=RSS/RSS_min`;
- `rss_excess_pct=100*(RSS/RSS_min-1)`.

Near-optimal cutoff intervals are the minimum and maximum candidate cutoff satisfying excess RSS thresholds of 0.1%, 0.5%, and 1.0%. The output also reports the standardized endpoints, number and share of accepted candidates, and the selected minimum-RSS cutoff.

### Fixed-cutoff cross sensitivity

Estimate four debt equations: lagged theta at the lagged and contemporaneous cutoffs, and contemporaneous theta at the lagged and contemporaneous cutoffs. Each theta specification uses its own natural full debt-equation sample. Report the fixed cutoff source, coefficients and clustered p-values for both branches, RSS, within R-squared, N, countries, and observations on each side.

### Common 742-observation comparison

Intersect the country-year keys used by the two full debt equations and fail closed unless the intersection contains exactly 742 unique observations. On that fixed sample, re-search each theta specification's P10--P90 candidate grid, re-estimate the full debt equation at its own minimum-RSS cutoff, and report the same statistics for both specifications. This separates debt-timing effects from sample-composition effects.

### Paired country bootstrap

Use 30 paired country-block bootstrap replications with seed 20260830. In each replication, draw the original number of countries with replacement and keep all observed years for every selected country; duplicate selections receive new bootstrap panel IDs. Both debt specifications consume exactly the same draw assignments.

Each replication re-estimates the two LSDVC point-estimate models needed to construct theta (`Spread_Interact_all` and `T10_interact_full`) with Blundell--Bond initialization and second-order bias correction, but does not nest the original 50-repetition LSDVC VCE bootstrap. It then reconstructs theta, re-searches the debt-equation cutoff, and re-estimates the final country/year fixed-effects debt equation. Failed replications are retained with a status and reason.

For each specification report requested repetitions, valid repetitions, failures, cutoff minimum, P25, median, P75 and maximum, plus the valid-replication shares satisfying `beta_L>0`, `beta_H<0`, and both theoretical signs. These 30 draws are explicitly described as a compact stability diagnostic, not a formal confidence interval.

## Reproducibility and validation

- All result paths are resolved from the workflow folder and result-root argument, never from the old root-level module directories.
- Machine-readable CSV and DTA artifacts remain paired wherever the existing workflow already produces both.
- Tests validate directory isolation, exact contemporaneous/lagged debt mapping, the 742-key identity, standardized-RSS algebra, four cross-cutoff rows, paired 30-draw bootstrap coverage, and document/result reconciliation.
- The original 50-repetition LSDVC VCE remains unchanged for the two main full workflows; only the outer bootstrap suppresses nested VCE computation.
