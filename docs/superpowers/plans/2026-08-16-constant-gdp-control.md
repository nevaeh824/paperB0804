# Constant GDP Baseline Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Paper B Baseline control $\ln(CurrentGDP_{it})$ with $\ln(ConstantGDP_{it})$, preserve GDP-free tax and Doomloop equations, and regenerate every downstream result and document.

**Architecture:** Construct `ln_constantgdp` in both Baseline and the empirical-theta Baseline-validation path. Enforce the boundary with output-contract tests over real Stata artifacts and integrated workflow checks, then use the existing Stata-to-CSV-to-Markdown pipeline to regenerate results, figures, and documents.

**Tech Stack:** Stata 18 MP, PowerShell, Python 3.14 standard-library `unittest`, Markdown.

## Global Constraints

- Baseline macro controls must be exactly `growth ln_constantgdp inflation_cpi`.
- `ln_constantgdp` must equal `ln(ConstantGDP)` only when `ConstantGDP>0`; a nonmissing nonpositive value must stop Stata.
- The empirical-theta spread validation uses the same Baseline control; the tax equation remains GDP-free.
- Doomloop equations remain GDP-free.
- Do not change the input dataset, its builder, fixed effects, standard errors, sample locking, theta construction, or cutoff search.
- Preserve `CurrentGDP` as an upstream field used by the reserves construction.
- Preserve unrelated user changes and do not stage or commit them.

---

### Task 1: Add a failing output-contract regression test

**Files:**
- Create: `tests/test_constant_gdp_control.py`
- Read: `baseline/stata_outputs/model_coefficients.csv`
- Read: `baseline/stata_outputs/run_metadata.csv`
- Read: `empirical_theta/stata_outputs/model_coefficients.csv`
- Read: `empirical_theta/stata_outputs/run_metadata.csv`
- Read: `doomloop/stata_outputs/nostate_model_coefficients.csv`

**Interfaces:**
- Consumes: the real machine-readable CSV artifacts delivered by the Stata stages.
- Produces: `ConstantGdpControlOutputTests`, runnable with Python 3.14 `unittest`.

- [ ] **Step 1: Write the failing contract tests**

```python
import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GDP_TERMS = {"CurrentGDP", "ConstantGDP", "ln_currentgdp", "ln_constantgdp"}

def rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

class ConstantGdpControlOutputTests(unittest.TestCase):
    def test_baseline_output_uses_constant_gdp_log(self):
        variables = {row["variable"] for row in rows(
            "baseline/stata_outputs/model_coefficients.csv"
        )}
        self.assertIn("ln_constantgdp", variables)
        self.assertNotIn("ln_currentgdp", variables)

    def test_spread_validation_uses_constant_gdp_log(self):
        variables = {row["variable"] for row in rows(
            "empirical_theta/stata_outputs/model_coefficients.csv"
        ) if row["model"] == "Spread_Interact_all"}
        self.assertIn("ln_constantgdp", variables)
        self.assertNotIn("ln_currentgdp", variables)

    def test_tax_and_doomloop_outputs_remain_gdp_free(self):
        tax_variables = {row["variable"] for row in rows(
            "empirical_theta/stata_outputs/model_coefficients.csv"
        ) if row["model"].startswith("T")}
        doom_variables = {row["variable"] for row in rows(
            "doomloop/stata_outputs/nostate_model_coefficients.csv"
        )}
        self.assertTrue(GDP_TERMS.isdisjoint(tax_variables))
        self.assertTrue(GDP_TERMS.isdisjoint(doom_variables))

    def test_run_metadata_audits_constant_gdp_positivity(self):
        baseline_items = {row["item"] for row in rows(
            "baseline/stata_outputs/run_metadata.csv"
        )}
        theta_items = {row["item"] for row in rows(
            "empirical_theta/stata_outputs/run_metadata.csv"
        )}
        self.assertIn("nonpositive_ConstantGDP", baseline_items)
        self.assertIn("nonpositive_ConstantGDP_rows", theta_items)
```

- [ ] **Step 2: Run `py -3.14 -m unittest tests.test_constant_gdp_control -v`**

Expected: two or more failures because current delivered Baseline and spread-validation artifacts still contain `ln_currentgdp`, and metadata still audits CurrentGDP.

---

### Task 2: Replace the Baseline control in both Stata paths

**Files:**
- Modify: `paperB/code/baseline_twfe.do:79-83,108,138,327-342,510-540`
- Modify: `paperB/code/empirical_theta.do:109-131,352,613-622,767-790`
- Test: `tests/test_constant_gdp_control.py`

**Interfaces:**
- Consumes: raw `ConstantGDP` from `data0804/invest_panel_weo.csv`.
- Produces: `ln_constantgdp`, Baseline coefficient rows keyed by that name, and an empirical-theta spread validation using the same control.

- [ ] **Step 1: Change the Baseline transformation**

```stata
count if ConstantGDP<=0 & !missing(ConstantGDP)
assert r(N)==0
scalar N_nonpositive_constant_gdp = r(N)
generate double ln_constantgdp = ln(ConstantGDP) if ConstantGDP>0
label variable ln_constantgdp "Natural log of ConstantGDP; generated only when ConstantGDP>0"
```

Use `ln_constantgdp` in `local macro`, `profilevars`, every staged RHS, validation RHS, and metadata key `nonpositive_ConstantGDP`.

- [ ] **Step 2: Change empirical-theta Baseline validation**

Apply the same validation and construction. Replace the old log only in `spread_controls`, `spread_rhs`, spread validation loops, audit fields, and metadata. Keep `local macro growth inflation_cpi` for tax unchanged.

- [ ] **Step 3: Preserve transparent panel fields**

Retain `CurrentGDP`, add `ConstantGDP`, and replace `ln_currentgdp` with `ln_constantgdp` in empirical-theta panel `keep` lists.

- [ ] **Step 4: Run the focused test**

Run `py -3.14 -m unittest tests.test_constant_gdp_control -v`.

Expected: output tests remain red because the machine-readable artifacts have not yet been regenerated; proceed directly to Tasks 3 and 4 to complete the green phase.

---

### Task 3: Update renderer, integrated QA, and workflow documentation

**Files:**
- Modify: `paperB/render_output.py:195-205,299-323,484-506`
- Modify: `paperB/run_workflow.ps1:220-250`
- Modify: `paperB/WORKFLOW.md:55-80,130-185,315-335`
- Modify: `paperB/code/doomloop.do:146`
- Test: `tests/test_constant_gdp_control.py`

**Interfaces:**
- Consumes: CSV rows keyed by `ln_constantgdp`.
- Produces: tables labeled `$\ln(ConstantGDP_{it})$`, GDP-free tax/Doomloop guards, and matching workflow prose.

- [ ] **Step 1: Update the renderer contract**

Use `"ln_constantgdp": r"$\ln(ConstantGDP_{it})$"` in the label map. Replace Baseline table terms, selected diagnostics, and Baseline-control narrative while leaving data-source prose about CurrentGDP reserves unchanged.

- [ ] **Step 2: Strengthen integrated QA**

Require Baseline coefficient output to contain `ln_constantgdp` and reject `ln_currentgdp`. Forbid `CurrentGDP`, `ConstantGDP`, `ln_currentgdp`, and `ln_constantgdp` in tax and Doomloop coefficient rows while retaining existing Doomloop exclusions.

- [ ] **Step 3: Update authoritative prose and comments**

Update the Baseline transformation, macro list, empirical-theta reproduction explanation, Doomloop exclusion text, and Doomloop source comment.

- [ ] **Step 4: Compile the updated renderer**

Run `py -3.14 -m py_compile paperB/render_output.py`.

Expected: PASS. Output-contract tests remain red until the Stata artifacts are regenerated in Task 4.

- [ ] **Step 5: Scan obsolete contexts**

Run `rg -n "ln_currentgdp|ln\(CurrentGDP" paperB/code paperB/render_output.py paperB/run_workflow.ps1 paperB/WORKFLOW.md`.

Expected: only negative-test strings and fail-closed messages remain.

---

### Task 4: Re-estimate and verify the full pipeline

**Files:**
- Regenerate: `baseline/stata_outputs/*`
- Regenerate: `empirical_theta/stata_outputs/*`
- Regenerate: `doomloop/stata_outputs/*`
- Regenerate: `doomloop/figures/*`
- Regenerate: `paperB/figures/*`
- Regenerate: `paperB/paperB_results.md`
- Regenerate: `paperB/paperB_diagnostics.md`
- Regenerate: `paperB/progress.md`

**Interfaces:**
- Consumes: updated Stata sources and `data0804/invest_panel_weo.csv`.
- Produces: refreshed estimates, diagnostics, cutoffs, figures, and documents.

- [ ] **Step 1: Run the full workflow**

Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1`.

Expected: all three Stata stages, figure copy, renderer, and integrated QA exit 0.

- [ ] **Step 2: Re-run contract tests**

Run `py -3.14 -m unittest tests.test_constant_gdp_control -v`.

Expected: 4 tests PASS.

- [ ] **Step 3: Verify model boundaries in CSV outputs**

Assert Baseline and spread-validation rows use `ln_constantgdp`; tax and Doomloop rows contain none of `CurrentGDP`, `ConstantGDP`, `ln_currentgdp`, or `ln_constantgdp`.

- [ ] **Step 4: Verify logs and documents**

Confirm all completion markers, zero `r(#);` errors, nonempty documents, and no obsolete Baseline-control phrase in the three generated Markdown files.

- [ ] **Step 5: Visually inspect figures**

Open the three regenerated PNGs and confirm titles, axes, curves, confidence intervals, legends, and cutoff lines render correctly.

- [ ] **Step 6: Review the final diff**

Run `git status --short`, `git diff --check`, and `git diff --stat`. Confirm intended changes are present and unrelated pre-existing changes remain untouched and unstaged.
