# CurrentGDP NGDPD and Reserves Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Source `CurrentGDP` from WEO NGDPD and calculate reserves as WDI current-US-dollar reserves divided by NGDPD in billions, times 100.

**Architecture:** Extend the existing WEO mapping, add a validated WDI wide-CSV reader, and centralize the reserves formula in one Decimal-based function. Use the same functions in full panel builds and in an atomic two-column refresh of the existing output.

**Tech Stack:** Python 3.14, csv, Decimal, openpyxl, unittest, existing pandas profiling.

## Global Constraints

- CurrentGDP maps to WEO `NGDPD`, unit billions of US dollars.
- Reserves formula is exactly `FI.RES.TOTL.CD / 1e9 / NGDPD * 100`.
- Join keys are exact ISO3 and calendar year for 1995--2023.
- Do not impute source gaps or alter columns other than CurrentGDP and reserves.
- Reject duplicate WDI country rows and nonpositive NGDPD denominators.

---

### Task 1: Source and formula contracts

**Files:**
- Modify: `tests/test_constant_gdp_contract.py`

**Interfaces:**
- Consumes: WEO workbook, WDI reserve CSV and current analysis panel.
- Produces: tests for NGDPD mapping, WDI parsing, reserves formula, missingness and atomic refresh.

- [ ] Change the WEO mapping expectation from `NGDP` to `NGDPD`.
- [ ] Independently read NGDPD and WDI values and assert every target CurrentGDP/reserves value.
- [ ] Assert 1,825 CurrentGDP values and 1,757 reserves values with exact missing-key sets.
- [ ] Add temporary-source tests for atomic refresh and nonpositive NGDPD rejection.
- [ ] Run the focused tests and confirm they fail against the old production mapping/output.

### Task 2: Builder and data refresh

**Files:**
- Modify: `data0804/build_invest_panel_weo.py`
- Modify: `data0804/invest_panel_weo.csv`

**Interfaces:**
- Produces: `read_wdi_reserve_values(path, years)`, `calculate_reserves(ngdpd, reserve_usd)`, and `refresh_currentgdp_and_reserves(path, weo_values, reserve_values)`.

- [ ] Map WEO `NGDPD` to `CurrentGDP`.
- [ ] Implement WDI metadata-header discovery, indicator validation and duplicate-ISO3 rejection.
- [ ] Implement Decimal reserves calculation with blank propagation and positive-denominator validation.
- [ ] Use the formula in `write_merged_csv()` and the atomic refresh function.
- [ ] Refresh the existing CSV and run focused tests to green.

### Task 3: Documentation and final verification

**Files:**
- Modify: `data0804/build_invest_panel_weo.py`
- Modify: `data0804/invest_panel_weo_documentation.md`

**Interfaces:**
- Produces: updated unit/source dictionary and quality narrative.

- [ ] Change CurrentGDP documentation to NGDPD, billions of US dollars.
- [ ] Change reserves documentation to the new WDI/NGDPD formula and recorded coverage.
- [ ] Verify all untouched columns against the pre-change Git version.
- [ ] Run all Python tests, Paper B `-SkipStata` QA and `git diff --check`.
