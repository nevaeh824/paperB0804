# WSDI Country Indicator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and execute a tested Python pipeline that converts HadEX3 WSDI grid data into a 61-country, 1995–2018 empirical panel plus complete intermediate data and QA logs.

**Architecture:** A single importable command-line module separates input validation, spatial membership, country-year aggregation, coverage filtering, target-panel assembly, output validation, and file writing into testable functions. Standard-library `unittest` exercises each transformation on small in-memory fixtures before the real pipeline reads the supplied CSV, NetCDF, and GeoPackage files.

**Tech Stack:** Python 3.11, pandas, NumPy, xarray, netCDF4, GeoPandas, Pyogrio, Shapely, PyArrow, unittest

## Global Constraints

- Treat `WSDI指标构建步骤.md` and the approved design spec as the controlling methodology.
- Preserve the four supplied source files unchanged.
- Use HadEX3 `WSDI`, base period 1961–1990, climate coverage period 1951–2018, and empirical period 1995–2018.
- Aggregate valid grid-center values with an unweighted arithmetic mean.
- Apply the 80% country time-coverage filter over 68 years.
- Exclude `HKG` and `TWN`; retain 61 sovereign countries and exactly 1,464 target keys.
- Retain `MUS` and `SGP` target keys as `no_grid_center`; do not use nearest-neighbor substitution.
- This workspace is not a Git repository, so task checkpoints cannot be committed.

---

### Task 1: Panel and NetCDF validation functions

**Files:**
- Create: `tests/test_build_wsdi_country.py`
- Create: `scripts/build_wsdi_country.py`

**Interfaces:**
- Consumes: panel CSV path, NetCDF path, year bounds, exclusion set
- Produces: `compute_sha256`, `load_panel_keys`, `normalize_longitude`, `load_wsdi`

- [ ] **Step 1: Write failing panel and longitude tests**

Add `unittest` cases that expect `load_panel_keys` to remove `HKG` and `TWN`, retain all requested years, reject duplicate `iso3 + year`, and return excluded rows separately. Add a case that expects `normalize_longitude` to map `[0.9375, 180.9375, 359.0625]` into a unique, increasing coordinate in `[−180, 180)`.

- [ ] **Step 2: Run the tests and verify RED**

Run: `python -m unittest tests.test_build_wsdi_country -v`

Expected: import failure because `scripts.build_wsdi_country` does not exist.

- [ ] **Step 3: Implement the minimum panel and NetCDF functions**

Implement exact source assertions for 1,827 rows, 63 ISO3 values, 1995–2023, required non-null fields, stable country names, and unique keys. Implement HadEX3 metadata assertions, CF decoding, 1951–2018 selection, missing-value masking, and normalized sorted longitude.

- [ ] **Step 4: Run the tests and verify GREEN**

Run: `python -m unittest tests.test_build_wsdi_country -v`

Expected: panel and longitude cases pass.

### Task 2: Boundary, spatial-membership, and aggregation functions

**Files:**
- Modify: `tests/test_build_wsdi_country.py`
- Modify: `scripts/build_wsdi_country.py`

**Interfaces:**
- Consumes: GeoPackage path/layer, normalized WSDI DataArray
- Produces: `load_boundaries`, `build_grid_membership`, `aggregate_country_year`, `apply_time_coverage_filter`

- [ ] **Step 1: Write failing spatial and aggregation tests**

Create two small square polygons and a four-point grid. Assert BOM removal, one ISO3 per dissolved geometry, `within` membership, empty conflict output, detection of a deliberately overlapping point, simple country-year mean, valid/total cell counts, grid coverage, and the inclusive `>= 0.80` time threshold.

- [ ] **Step 2: Run the new tests and verify RED**

Run: `python -m unittest tests.test_build_wsdi_country -v`

Expected: failures because the spatial and aggregation functions are missing.

- [ ] **Step 3: Implement the minimum spatial pipeline**

Clean BOM from columns and string values without pandas dtype warnings; convert to EPSG:4326; make geometries valid; filter three-letter uppercase ISO3 values; dissolve by ISO3. Build one static point GeoDataFrame, spatially join with `predicate="within"`, return both membership and all multi-country conflicts, calculate `n_total_cells`, and aggregate non-null WSDI values by ISO3 and year.

- [ ] **Step 4: Run the tests and verify GREEN**

Run: `python -m unittest tests.test_build_wsdi_country -v`

Expected: all spatial and aggregation tests pass without warnings.

### Task 3: Target assembly, missing reasons, QA, and writers

**Files:**
- Modify: `tests/test_build_wsdi_country.py`
- Modify: `scripts/build_wsdi_country.py`

**Interfaces:**
- Consumes: 1,464 target keys, filtered country-year values, complete coverage table, no-grid ISO3 set
- Produces: `build_target_output`, `validate_outputs`, `write_outputs`

- [ ] **Step 1: Write failing target-output tests**

Use three synthetic countries to assert that available rows have blank `wsdi_missing_reason`, a country without a grid receives `no_grid_center`, a country below the time threshold receives `failed_time_coverage`, and an otherwise retained country-year without a value receives `missing_annual_value`. Assert that the left join preserves every target key.

- [ ] **Step 2: Run the new tests and verify RED**

Run: `python -m unittest tests.test_build_wsdi_country -v`

Expected: failures because target assembly and output validation are missing.

- [ ] **Step 3: Implement target assembly and deterministic writers**

Set the two-level `wsdi_source_status`, assign the three missing reasons in precedence order, validate exact target shape and domain rules, sort every artifact on stable keys, write Parquet and UTF-8-BOM CSV files, and serialize `qa_summary.json` with UTF-8 and sorted keys.

- [ ] **Step 4: Run the tests and verify GREEN**

Run: `python -m unittest tests.test_build_wsdi_country -v`

Expected: all target and writer tests pass without warnings.

### Task 4: CLI orchestration and real-data construction

**Files:**
- Modify: `tests/test_build_wsdi_country.py`
- Modify: `scripts/build_wsdi_country.py`
- Create: `data/processed/wsdi_country_year_1951_2018.parquet`
- Create: `data/processed/wsdi_sovereign61_1995_2018.csv`
- Create: `logs/country_grid_membership.csv`
- Create: `logs/country_coverage.csv`
- Create: `logs/spatial_join_conflicts.csv`
- Create: `logs/countries_without_grid.csv`
- Create: `logs/excluded_non_sovereign.csv`
- Create: `logs/input_hashes.csv`
- Create: `logs/qa_summary.json`

**Interfaces:**
- Consumes: project root and optional command-line year/threshold arguments
- Produces: all approved data and QA artifacts

- [ ] **Step 1: Write a failing CLI parser/defaults test**

Assert defaults for project root, 1951, 2018, 1995, 2018, 0.80, `WB_GAD_ADM0`, and the two exclusions.

- [ ] **Step 2: Run the CLI test and verify RED**

Run: `python -m unittest tests.test_build_wsdi_country -v`

Expected: failure because CLI orchestration is incomplete.

- [ ] **Step 3: Implement `main()` and QA summary assembly**

Resolve the four root-level source paths, run each transformation, abort after writing the conflict log if any grid belongs to multiple countries, verify 61/61 boundary coverage, construct output directories, write all artifacts, and print a compact run summary.

- [ ] **Step 4: Run the complete unit suite**

Run: `python -W error -m unittest tests.test_build_wsdi_country -v`

Expected: every test passes and warnings are treated as errors.

- [ ] **Step 5: Execute the real build**

Run: `python scripts/build_wsdi_country.py --root C:\Users\chenyu\Desktop\WSDI`

Expected: exit code 0 and all ten approved output artifacts exist.

- [ ] **Step 6: Independently validate the saved outputs**

Run a fresh Python process that reads both processed files and every log, verifies exact target keys against a newly filtered `invest_panel_weo.csv`, checks row counts and domains, recomputes selected country-year means directly from membership plus NetCDF values, validates input hashes, and confirms `MUS`/`SGP` missing reasons.

Expected: all independent checks pass and a concise confidence assessment can be reported with remaining coverage caveats.
