# ND-GAIN Delta Columns Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reproducible `vulnerability_delta100` and `readiness_delta100` columns to the analysis panel using ND-GAIN source values multiplied by 100.

**Architecture:** Read each wide ND-GAIN CSV into a unique `(ISO3, year)` mapping, scale values with `Decimal`, and left-join them into the long panel without changing existing rows or values. Expose the same operation in both the complete builder and an atomic refresh function for the existing output CSV.

**Tech Stack:** Python 3.14 standard-library CSV/Decimal, unittest, existing pandas/notebook profiling pipeline.

## Global Constraints

- Join only on exact `iso3 + year` keys for 1995--2023.
- Multiply every nonmissing source value by exactly 100.
- Keep HKG and TWN missing because neither source contains those ISO3 codes.
- Preserve target row count, row order, keys, and all existing field values.
- Place each delta column directly after its corresponding level column.

---

### Task 1: Contract tests

**Files:**
- Modify: `tests/test_constant_gdp_contract.py`

**Interfaces:**
- Consumes: the two ND-GAIN wide CSV files and `invest_panel_weo.csv`.
- Produces: observable contracts for `read_ndgain_delta_values()` and `add_ndgain_delta_columns()`.

- [ ] Add a real-data test that independently reads both sources and compares every target value to `Decimal(source) * 100`.
- [ ] Assert exactly 1,769 populated and 58 missing rows per new column, with missing ISO3 values exactly HKG and TWN.
- [ ] Add a temporary-panel test proving field placement, row/value preservation and blank unmatched keys.
- [ ] Add a duplicate-ISO3 source test that expects `ValueError`.
- [ ] Run `py -3.14 -m unittest tests.test_constant_gdp_contract` and confirm failure because the new columns/API do not exist.

### Task 2: Builder implementation and output refresh

**Files:**
- Modify: `data0804/build_invest_panel_weo.py`
- Modify: `data0804/invest_panel_weo.csv`

**Interfaces:**
- Produces: `read_ndgain_delta_values(path: Path) -> dict[tuple[str, int], str]` and `add_ndgain_delta_columns(path: Path, sources: dict[str, Path] = NDGAIN_DELTA_SOURCES) -> None`.

- [ ] Define source paths and output-field mappings.
- [ ] Implement wide-source validation, exact `Decimal * 100` formatting and duplicate-key rejection.
- [ ] Implement atomic left-join refresh with delta columns after their matching level columns.
- [ ] Extend `write_merged_csv()` so future full builds populate both columns.
- [ ] Run the atomic refresh on `invest_panel_weo.csv`.
- [ ] Run the focused test and confirm it passes.

### Task 3: Documentation and verification

**Files:**
- Modify: `data0804/build_invest_panel_weo.py`
- Test: `tests/test_constant_gdp_contract.py`

**Interfaces:**
- Consumes: refreshed CSV and source mappings.
- Produces: updated variable dictionary and quality metadata when the full builder is runnable.

- [ ] Add both variables, source locations, `×100` rule and expected HKG/TWN gaps to builder-generated documentation.
- [ ] Independently verify target row count, key uniqueness, source mapping, missingness and column order.
- [ ] Run `py -3.14 -m unittest discover -s tests -p 'test_*.py'`.
- [ ] Run `git diff --check` and review the scoped diff.
