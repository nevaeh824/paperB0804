# Constant-GDP Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Paper B's baseline `ln(CurrentGDP)` control with `ln(ConstantGDP)`, make `ConstantGDP` reproducible from WEO `NGDP_R`, and regenerate every downstream output and document.

**Architecture:** Extend the upstream WEO field mapping first, then change the authoritative baseline and empirical-theta Stata sources to produce and consume the semantically named `ln_constantgdp`. Keep tax and Doomloop GDP-free, update rendering and integrated QA contracts, and run the complete pipeline so the changed baseline propagates through theta, cutoff selection, figures, and generated documents.

**Tech Stack:** Python 3.14, `unittest`, openpyxl/pandas/nbformat, Stata 18 MP, PowerShell, Markdown.

## Global Constraints

- `ConstantGDP` is WEO `NGDP_R`, in billions of domestic currency at constant prices.
- Construct `ln_constantgdp = ln(ConstantGDP)` only for strictly positive values.
- Baseline controls are exactly `growth ln_constantgdp inflation_cpi reserves tt` beyond the three core variables and interactions.
- Tax-base and retained Doomloop equations contain no current-price or constant-price GDP control.
- Preserve country/year fixed effects, observation-level `vce(robust)`, sample-locking rules, theta identity, cutoff method, and criterion comparison method.
- Do not overwrite or stage unrelated user files, including the untracked theory PDF and WEO workbook.
- Do not manually edit numerical values in generated Paper B documents; regenerate them through `paperB/run_workflow.ps1`.

---

### Task 1: Add executable constant-GDP contracts

**Files:**
- Create: `tests/test_constant_gdp_contract.py`
- Read: `data0804/WEOApr2026all.xlsx`
- Read: `data0804/invest_panel_weo.csv`

**Interfaces:**
- Consumes: repository source text, `builder.WEO_FIELDS`, the local WEO workbook, and the current analysis CSV.
- Produces: `python -m unittest tests.test_constant_gdp_contract` as the regression gate used by all later tasks.

- [ ] **Step 1: Write source and data contract tests**

Create `tests/test_constant_gdp_contract.py` with tests that:

```python
class ConstantGDPContractTests(unittest.TestCase):
    def test_builder_maps_real_gdp_after_current_gdp(self):
        self.assertEqual(
            list(builder.WEO_FIELDS.items())[:3],
            [("GGR_NGDP", "Revenue_gdp"), ("NGDP", "CurrentGDP"), ("NGDP_R", "ConstantGDP")],
        )

    def test_existing_constant_gdp_matches_weo_ngdp_r(self):
        # Read WEO NGDP_R at iso3-year grain and assert identical missingness
        # and max absolute difference 0 against ConstantGDP in the analysis CSV.

    def test_authoritative_sources_use_semantic_log_name(self):
        # Assert baseline, empirical theta, rendering, runner QA, and WORKFLOW
        # contain ln_constantgdp and contain no ln_currentgdp regression contract.

    def test_generated_outputs_use_constant_gdp_control(self):
        # Assert generated coefficient CSVs and Paper B Markdown use
        # ln_constantgdp / ln(ConstantGDP), not the former log control.
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
py -3.14 -m unittest tests.test_constant_gdp_contract -v
```

Expected: failures show `NGDP_R` is absent from `WEO_FIELDS`, authoritative sources still use `ln_currentgdp`, and generated outputs still report `ln(CurrentGDP)`.

- [ ] **Step 3: Preserve the red evidence**

Record the failing assertions in the task update before changing production files. Do not weaken assertions to accommodate the old behavior.

---

### Task 2: Make the upstream data build reproduce ConstantGDP

**Files:**
- Modify: `data0804/build_invest_panel_weo.py`
- Modify: `data0804/invest_panel_weo_documentation.md`
- Modify: `data0804/invest_panel_weo_profile.ipynb`
- Test: `tests/test_constant_gdp_contract.py`

**Interfaces:**
- Consumes: WEO `Countries` rows keyed by `COUNTRY.ID`, `INDICATOR.ID`, and year.
- Produces: `WEO_FIELDS["NGDP_R"] == "ConstantGDP"`, documentation/audit content covering six WEO fields, and exact source reconciliation.

- [ ] **Step 1: Extend the source mapping**

Change the ordered mapping to:

```python
WEO_FIELDS = OrderedDict(
    [
        ("GGR_NGDP", "Revenue_gdp"),
        ("NGDP", "CurrentGDP"),
        ("NGDP_R", "ConstantGDP"),
        ("GGXCNL_NGDP", "OverallBalance_gdp"),
        ("GGR", "revenue"),
        ("GGXWDG", "debt"),
    ]
)
```

- [ ] **Step 2: Update generated documentation logic**

Add the variable dictionary row:

```python
("`ConstantGDP`", "固定价格 GDP（本币）", "十亿本币", "`WEOApr2026all.xlsx`，Countries 表，`NGDP_R`", "按 `iso3 + year` 左连接；WEO 原值")
```

Update field counts, appended-field prose, missingness summaries, comparability wording, notebook narrative, and reconciliation descriptions so they refer to six WEO source series and both GDP amount fields.

- [ ] **Step 3: Refresh upstream documentation artifacts without overwriting the analysis CSV**

Use the existing verified CSV with `profile_output`, `write_documentation`, and `build_notebook` to regenerate the Markdown and notebook template. Do not call `main()` because the absent base panel would rebuild/overwrite the analysis CSV.

- [ ] **Step 4: Run the focused upstream tests**

Run:

```powershell
py -3.14 -m unittest tests.test_constant_gdp_contract.ConstantGDPContractTests.test_builder_maps_real_gdp_after_current_gdp -v
py -3.14 -m unittest tests.test_constant_gdp_contract.ConstantGDPContractTests.test_existing_constant_gdp_matches_weo_ngdp_r -v
```

Expected: both tests pass; the source reconciliation reports two matching missing values and zero maximum absolute difference.

- [ ] **Step 5: Commit the upstream code and documentation**

Run:

```powershell
git add -- data0804/build_invest_panel_weo.py data0804/invest_panel_weo_documentation.md data0804/invest_panel_weo_profile.ipynb tests/test_constant_gdp_contract.py
git commit -m "data: reproduce constant-price GDP control"
```

Do not stage `data0804/invest_panel_weo.csv` or `data0804/WEOApr2026all.xlsx`.

---

### Task 3: Replace the baseline control and update workflow contracts

**Files:**
- Modify: `paperB/code/baseline_twfe.do`
- Modify: `paperB/code/empirical_theta.do`
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/render_output.py`
- Modify: `paperB/WORKFLOW.md`
- Test: `tests/test_constant_gdp_contract.py`

**Interfaces:**
- Consumes: input columns `ConstantGDP` and the unchanged model variables.
- Produces: machine-readable coefficient rows named `ln_constantgdp`, regenerated narrative labeled `ln(ConstantGDP)`, and QA failures for any old GDP-log regression contract.

- [ ] **Step 1: Replace the baseline transformation and every model-side reference**

Implement:

```stata
confirm variable ConstantGDP
count if ConstantGDP<=0 & !missing(ConstantGDP)
scalar N_nonpositive_constant_gdp = r(N)
generate double ln_constantgdp = ln(ConstantGDP) if ConstantGDP>0
label variable ln_constantgdp "Natural log of ConstantGDP; generated only when ConstantGDP>0"
```

Use `ln_constantgdp` in the macro controls, profile/variation lists, all six applicable model RHS lists, correlations, VIF, LSDV validation, and metadata row `nonpositive_ConstantGDP`.

- [ ] **Step 2: Replace the empirical-theta baseline-reproduction transformation**

Implement the same positive-value transformation, use `ln_constantgdp` in `spread_controls` and `spread_rhs`, export `ConstantGDP` and `ln_constantgdp`, and rename run metadata to `nonpositive_ConstantGDP_rows`. Leave `tax_controls` exactly `growth inflation_cpi reserves tt`.

- [ ] **Step 3: Update renderer variable mapping and narrative**

Implement:

```python
"ln_constantgdp": r"$\ln(ConstantGDP_{it})$"
```

Replace selected/model term lists with `ln_constantgdp`. State that only baseline controls for `ln(ConstantGDP)` and that tax/Doomloop do not control GDP level.

- [ ] **Step 4: Strengthen integrated PowerShell QA**

Require baseline and spread-reproduction coefficient rows for `ln_constantgdp`; reject `ln_currentgdp` there. Reject both log names from tax models and reject all four raw/log GDP names from retained Doomloop models. Scan generated Paper B documents for the obsolete `ln(CurrentGDP)` claim.

- [ ] **Step 5: Update the executable workflow documentation**

Replace the baseline construction, control lists, baseline-reproduction explanation, GDP exclusions, update rules, and validation checklist in `paperB/WORKFLOW.md` with the approved constant-price semantics.

- [ ] **Step 6: Run the source-contract test and verify GREEN for source code**

Run:

```powershell
py -3.14 -m unittest tests.test_constant_gdp_contract.ConstantGDPContractTests.test_authoritative_sources_use_semantic_log_name -v
```

Expected: pass. The full suite may still fail only because generated outputs have not yet been rebuilt.

- [ ] **Step 7: Commit authoritative source changes**

Run:

```powershell
git add -- paperB/code/baseline_twfe.do paperB/code/empirical_theta.do paperB/run_workflow.ps1 paperB/render_output.py paperB/WORKFLOW.md tests/test_constant_gdp_contract.py
git commit -m "refactor: use constant GDP in Paper B baseline"
```

---

### Task 4: Re-estimate and regenerate all outputs

**Files:**
- Modify: `baseline/stata_outputs/*`
- Modify: `empirical_theta/stata_outputs/*`
- Modify: `doomloop/stata_outputs/*`
- Modify: `doomloop/figures/*`
- Modify: `paperB/figures/*`
- Modify: `paperB/paperB_results.md`
- Modify: `paperB/paperB_diagnostics.md`
- Modify: `paperB/progress.md`
- Test: `tests/test_constant_gdp_contract.py`

**Interfaces:**
- Consumes: authoritative sources from Task 3 and `data0804/invest_panel_weo.csv`.
- Produces: complete Stata output sets, empirical-theta panel, selected cutoffs, criterion comparisons, figures, and generated Paper B documents.

- [ ] **Step 1: Run the full workflow**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1
```

Expected: exit code 0 after baseline, empirical theta, Doomloop, rendering, and integrated QA.

- [ ] **Step 2: Inspect the three authoritative logs**

Run:

```powershell
rg -n "WORKFLOW COMPLETE|ANALYSIS COMPLETE|r\([0-9]+\);" baseline/stata_outputs/baseline_twfe.log empirical_theta/stata_outputs/empirical_theta.log doomloop/stata_outputs/doomloop_no_state.log
```

Expected: each log has its completion marker and none has an `r(#);` error line.

- [ ] **Step 3: Run the full contract suite**

Run:

```powershell
py -3.14 -m unittest tests.test_constant_gdp_contract -v
```

Expected: all tests pass, including generated coefficient and document contracts.

- [ ] **Step 4: Run stale-reference and output-integrity checks**

Search executable sources and generated Paper B documents for `ln_currentgdp` and `ln(CurrentGDP)`; allow raw `CurrentGDP` only where documenting an unused source field or an explicit exclusion. Confirm required PNG/PDF figures are nonempty.

- [ ] **Step 5: Commit regenerated outputs**

Stage only tracked generated output and document paths, then run:

```powershell
git commit -m "results: regenerate Paper B with constant GDP"
```

Do not stage the user-owned input CSV, WEO workbook, or theory PDF.

---

### Task 5: Final verification and handoff

**Files:**
- Read: `docs/superpowers/specs/2026-08-12-constant-gdp-control-design.md`
- Read: all task diffs and verification outputs

**Interfaces:**
- Consumes: completed implementation and generated artifacts.
- Produces: evidence-backed completion report with changed files, key result changes, test counts, and limitations.

- [ ] **Step 1: Run fresh full verification**

Run the complete workflow once more only if any executable source changed after Task 4; otherwise run `-SkipStata` to revalidate all machine-readable outputs and documents, followed by the full unittest suite.

- [ ] **Step 2: Review scope and repository state**

Run:

```powershell
git diff --check
git status --short
git log -4 --oneline
```

Confirm unrelated user-owned inputs remain unstaged and unmodified by task commits.

- [ ] **Step 3: Compare central output changes**

Report the new baseline GDP coefficient, common sample size, theta summary, debt cutoff, and criterion winner from regenerated CSVs, clearly identifying these as descriptive workflow changes rather than causal results.

- [ ] **Step 4: Deliver final handoff**

Link the authoritative source, workflow documentation, results document, diagnostics document, and tests. State exact verification commands and outcomes, plus the upstream rebuild limitation caused by the absent base panel.
