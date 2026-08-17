import json
import tempfile
import unittest
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box

from scripts import build_wsdi_country as build


class PanelAndNetcdfTests(unittest.TestCase):
    def test_compute_sha256_uses_file_bytes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.bin"
            path.write_bytes(b"abc")

            digest = build.compute_sha256(path)

        self.assertEqual(
            digest,
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_load_panel_keys_filters_years_and_exclusions(self):
        rows = []
        names = {
            "AAA": "Alpha",
            "BBB": "Beta",
            "HKG": "Hong Kong SAR",
            "TWN": "Taiwan Province of China",
        }
        for iso3, name in names.items():
            for year in (2000, 2001):
                rows.append({"country_name": name, "iso3": iso3, "year": year})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "panel.csv"
            pd.DataFrame(rows).to_csv(path, index=False)
            target, excluded = build.load_panel_keys(
                path,
                start_year=2000,
                end_year=2001,
                excluded_iso3={"HKG", "TWN"},
                expected_source_rows=8,
                expected_source_iso3=4,
                expected_source_years={2000, 2001},
            )

        self.assertEqual(target[["iso3", "year"]].values.tolist(), [
            ["AAA", 2000],
            ["AAA", 2001],
            ["BBB", 2000],
            ["BBB", 2001],
        ])
        self.assertEqual(set(excluded["iso3"]), {"HKG", "TWN"})
        self.assertEqual(len(excluded), 4)

    def test_load_panel_keys_rejects_duplicate_primary_key(self):
        panel = pd.DataFrame(
            [
                {"country_name": "Alpha", "iso3": "AAA", "year": 2000},
                {"country_name": "Alpha", "iso3": "AAA", "year": 2000},
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "panel.csv"
            panel.to_csv(path, index=False)

            with self.assertRaisesRegex(ValueError, "duplicate iso3-year"):
                build.load_panel_keys(
                    path,
                    start_year=2000,
                    end_year=2000,
                    excluded_iso3=set(),
                    expected_source_rows=2,
                    expected_source_iso3=1,
                    expected_source_years={2000},
                )

    def test_normalize_longitude_returns_unique_increasing_coordinate(self):
        data = xr.DataArray(
            np.array([[[10.0, 20.0, 30.0]]]),
            dims=("time", "latitude", "longitude"),
            coords={
                "time": pd.to_datetime(["2000-01-01"]),
                "latitude": [0.0],
                "longitude": [0.9375, 180.9375, 359.0625],
            },
        )

        result = build.normalize_longitude(data)

        np.testing.assert_allclose(
            result.longitude.values,
            np.array([-179.0625, -0.9375, 0.9375]),
        )
        np.testing.assert_allclose(
            result.values,
            np.array([[[20.0, 30.0, 10.0]]]),
        )

    def test_load_wsdi_validates_metadata_and_selects_climate_period(self):
        dataset = xr.Dataset(
            {
                "WSDI": (
                    ("time", "latitude", "longitude"),
                    np.array([[[1.0]], [[-99.9]], [[3.0]]]),
                    {"units": "days", "_FillValue": -99.9},
                )
            },
            coords={
                "time": pd.to_datetime(["1950-01-01", "1951-01-01", "1952-01-01"]),
                "latitude": [0.0],
                "longitude": [359.0],
            },
            attrs={"dataset_version": "3.0.4", "base_period": "1961-1990"},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "wsdi.nc"
            dataset.to_netcdf(path)

            result = build.load_wsdi(
                path,
                climate_start_year=1951,
                climate_end_year=1952,
                expected_source_start_year=1950,
                expected_source_end_year=1952,
                expected_source_time_count=3,
            )

        self.assertEqual(result.sizes["time"], 2)
        self.assertEqual(result.longitude.values.tolist(), [-1.0])
        self.assertTrue(np.isnan(result.sel(time="1951-01-01").item()))
        self.assertEqual(result.sel(time="1952-01-01").item(), 3.0)


class SpatialAndAggregationTests(unittest.TestCase):
    def test_load_boundaries_cleans_bom_and_dissolves_iso3(self):
        raw = gpd.GeoDataFrame(
            {
                "\ufeffISO_A3": ["\ufeffAAA", "\ufeffAAA", "\ufeffBBB"],
                "\ufeffNAM_0": ["\ufeffAlpha", "\ufeffAlpha", "\ufeffBeta"],
                "geometry": [
                    box(0, 0, 1, 1),
                    box(1, 0, 2, 1),
                    box(2, 0, 3, 1),
                ],
            },
            crs=4326,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "boundaries.gpkg"
            raw.to_file(path, layer="test_adm0", driver="GPKG", engine="pyogrio")

            countries, source_feature_count = build.load_boundaries(
                path, layer="test_adm0"
            )

        self.assertEqual(source_feature_count, 3)
        self.assertEqual(countries["ISO_A3"].tolist(), ["AAA", "BBB"])
        self.assertEqual(countries["NAM_0"].tolist(), ["Alpha", "Beta"])
        self.assertEqual(countries.crs.to_epsg(), 4326)
        self.assertTrue(countries.geometry.is_valid.all())
        self.assertAlmostEqual(countries.loc[0, "geometry"].area, 2.0)

    def test_build_grid_membership_returns_assignments_and_no_conflicts(self):
        countries = gpd.GeoDataFrame(
            {
                "ISO_A3": ["AAA", "BBB", "CCC"],
                "NAM_0": ["Alpha", "Beta", "Gamma"],
                "geometry": [
                    box(0, 0, 1, 1),
                    box(1, 0, 2, 1),
                    box(10, 10, 11, 11),
                ],
            },
            crs=4326,
        )
        wsdi = xr.DataArray(
            np.zeros((1, 1, 3)),
            dims=("time", "latitude", "longitude"),
            coords={
                "time": pd.to_datetime(["2000-01-01"]),
                "latitude": [0.5],
                "longitude": [0.5, 1.5, 2.5],
            },
        )

        membership, conflicts, countries_without_grid = build.build_grid_membership(
            wsdi, countries
        )

        self.assertEqual(
            membership[["latitude", "longitude", "ISO_A3"]].values.tolist(),
            [[0.5, 0.5, "AAA"], [0.5, 1.5, "BBB"]],
        )
        self.assertTrue(conflicts.empty)
        self.assertEqual(countries_without_grid["ISO_A3"].tolist(), ["CCC"])

    def test_build_grid_membership_reports_overlapping_assignments(self):
        countries = gpd.GeoDataFrame(
            {
                "ISO_A3": ["AAA", "BBB"],
                "NAM_0": ["Alpha", "Beta"],
                "geometry": [box(0, 0, 2, 2), box(1, 0, 3, 2)],
            },
            crs=4326,
        )
        wsdi = xr.DataArray(
            np.zeros((1, 1, 1)),
            dims=("time", "latitude", "longitude"),
            coords={
                "time": pd.to_datetime(["2000-01-01"]),
                "latitude": [1.0],
                "longitude": [1.5],
            },
        )

        membership, conflicts, _ = build.build_grid_membership(wsdi, countries)

        self.assertEqual(len(membership), 2)
        self.assertEqual(conflicts["ISO_A3"].tolist(), ["AAA", "BBB"])
        self.assertEqual(conflicts["n_iso3"].tolist(), [2, 2])

    def test_aggregate_country_year_uses_valid_grid_arithmetic_mean(self):
        wsdi = xr.DataArray(
            np.array([[[2.0, 4.0]], [[np.nan, 8.0]]]),
            dims=("time", "latitude", "longitude"),
            coords={
                "time": pd.to_datetime(["2000-01-01", "2001-01-01"]),
                "latitude": [0.5],
                "longitude": [0.5, 1.5],
            },
            name="WSDI",
        )
        membership = pd.DataFrame(
            {
                "latitude": [0.5, 0.5],
                "longitude": [0.5, 1.5],
                "ISO_A3": ["AAA", "AAA"],
                "NAM_0": ["Alpha", "Alpha"],
            }
        )

        result = build.aggregate_country_year(wsdi, membership)

        self.assertEqual(result["year"].tolist(), [2000, 2001])
        self.assertEqual(result["wsdi_days"].tolist(), [3.0, 8.0])
        self.assertEqual(result["n_valid_cells"].tolist(), [2, 1])
        self.assertEqual(result["n_total_cells"].tolist(), [2, 2])
        self.assertEqual(result["grid_coverage_rate"].tolist(), [1.0, 0.5])

    def test_aggregate_country_year_accumulates_float32_values_in_float64(self):
        wsdi = xr.DataArray(
            np.array([[[0.1, 10.2, 30.3]]], dtype="float32"),
            dims=("time", "latitude", "longitude"),
            coords={
                "time": pd.to_datetime(["2000-01-01"]),
                "latitude": [0.5],
                "longitude": [0.5, 1.5, 2.5],
            },
            name="WSDI",
        )
        membership = pd.DataFrame(
            {
                "latitude": [0.5, 0.5, 0.5],
                "longitude": [0.5, 1.5, 2.5],
                "ISO_A3": ["AAA", "AAA", "AAA"],
                "NAM_0": ["Alpha", "Alpha", "Alpha"],
            }
        )

        result = build.aggregate_country_year(wsdi, membership)

        self.assertAlmostEqual(result.loc[0, "wsdi_days"], 13.5333330159386, places=12)
        self.assertEqual(result["wsdi_days"].dtype, np.dtype("float64"))

    def test_apply_time_coverage_filter_includes_exact_threshold(self):
        country_year = pd.DataFrame(
            {
                "ISO_A3": ["AAA"] * 4 + ["BBB"] * 3,
                "NAM_0": ["Alpha"] * 4 + ["Beta"] * 3,
                "year": [2000, 2001, 2002, 2003, 2000, 2001, 2002],
                "wsdi_days": [1.0] * 7,
                "n_valid_cells": [1] * 7,
                "n_total_cells": [1] * 7,
                "grid_coverage_rate": [1.0] * 7,
            }
        )

        filtered, coverage = build.apply_time_coverage_filter(
            country_year, total_years=5, threshold=0.80
        )

        self.assertEqual(filtered["ISO_A3"].unique().tolist(), ["AAA"])
        self.assertEqual(
            coverage[["ISO_A3", "n_valid_years_1951_2018"]].values.tolist(),
            [["AAA", 4], ["BBB", 3]],
        )
        self.assertEqual(coverage["time_coverage_rate"].tolist(), [0.8, 0.6])
        self.assertEqual(coverage["passes_time_coverage"].tolist(), [True, False])

    def test_apply_time_coverage_filter_includes_zero_year_country(self):
        country_year = pd.DataFrame(
            {
                "ISO_A3": ["AAA"],
                "NAM_0": ["Alpha"],
                "year": [2000],
                "wsdi_days": [1.0],
                "n_valid_cells": [1],
                "n_total_cells": [1],
                "grid_coverage_rate": [1.0],
            }
        )

        _, coverage = build.apply_time_coverage_filter(
            country_year,
            total_years=1,
            threshold=0.80,
            all_iso3={"AAA", "BBB"},
        )

        self.assertEqual(
            coverage[["ISO_A3", "n_valid_years_1951_2018"]].values.tolist(),
            [["AAA", 1], ["BBB", 0]],
        )
        self.assertEqual(coverage["passes_time_coverage"].tolist(), [True, False])


class TargetAndOutputTests(unittest.TestCase):
    def make_target_fixture(self):
        panel_keys = pd.DataFrame(
            [
                {"country_name": name, "iso3": iso3, "year": year}
                for iso3, name in (
                    ("AAA", "Alpha"),
                    ("BBB", "Beta"),
                    ("CCC", "Gamma"),
                    ("DDD", "Delta"),
                )
                for year in (2000, 2001)
            ]
        )
        country_year = pd.DataFrame(
            {
                "iso3": ["AAA", "AAA", "DDD"],
                "boundary_name": ["Alpha boundary", "Alpha boundary", "Delta boundary"],
                "year": [2000, 2001, 2000],
                "wsdi_days": [2.0, 4.0, 8.0],
                "n_valid_cells": [2, 2, 1],
                "n_total_cells": [2, 2, 1],
                "grid_coverage_rate": [1.0, 1.0, 1.0],
                "n_valid_years_1951_2018": [2, 2, 2],
                "time_coverage_rate": [1.0, 1.0, 1.0],
                "passes_time_coverage": [True, True, True],
                "wsdi_source_dataset": ["HadEX3"] * 3,
                "wsdi_source_version": ["3.0.4"] * 3,
                "base_period": ["1961-1990"] * 3,
                "aggregation": ["grid_center_arithmetic_mean"] * 3,
            }
        )
        coverage = pd.DataFrame(
            {
                "ISO_A3": ["AAA", "BBB", "DDD"],
                "n_valid_years_1951_2018": [2, 1, 2],
                "time_coverage_rate": [1.0, 0.5, 1.0],
                "passes_time_coverage": [True, False, True],
            }
        )
        countries_without_grid = pd.DataFrame(
            {"ISO_A3": ["CCC"], "NAM_0": ["Gamma boundary"]}
        )
        return panel_keys, country_year, coverage, countries_without_grid

    def test_build_target_output_assigns_missing_reasons(self):
        panel_keys, country_year, coverage, countries_without_grid = (
            self.make_target_fixture()
        )

        target = build.build_target_output(
            panel_keys, country_year, coverage, countries_without_grid
        )

        reasons = target.set_index(["iso3", "year"])["wsdi_missing_reason"]
        statuses = target.set_index(["iso3", "year"])["wsdi_source_status"]
        self.assertTrue(pd.isna(reasons.loc[("AAA", 2000)]))
        self.assertEqual(reasons.loc[("BBB", 2000)], "failed_time_coverage")
        self.assertEqual(reasons.loc[("CCC", 2000)], "no_grid_center")
        self.assertEqual(reasons.loc[("DDD", 2001)], "missing_annual_value")
        self.assertEqual(statuses.loc[("AAA", 2000)], "available")
        self.assertEqual(
            statuses.loc[("DDD", 2001)],
            "missing_in_source_or_coverage_filter",
        )
        self.assertEqual(len(target), len(panel_keys))

    def test_validate_outputs_rejects_duplicate_target_key(self):
        panel_keys, country_year, coverage, countries_without_grid = (
            self.make_target_fixture()
        )
        target = build.build_target_output(
            panel_keys, country_year, coverage, countries_without_grid
        )
        duplicate_target = pd.concat([target, target.iloc[[0]]], ignore_index=True)

        with self.assertRaisesRegex(ValueError, "target row count"):
            build.validate_outputs(
                duplicate_target,
                country_year,
                expected_target_rows=8,
                expected_target_iso3=4,
                start_year=2000,
                end_year=2001,
                unmatched_target_iso3=[],
            )

    def test_validate_outputs_returns_quality_counts(self):
        panel_keys, country_year, coverage, countries_without_grid = (
            self.make_target_fixture()
        )
        target = build.build_target_output(
            panel_keys, country_year, coverage, countries_without_grid
        )

        summary = build.validate_outputs(
            target,
            country_year,
            expected_target_rows=8,
            expected_target_iso3=4,
            start_year=2000,
            end_year=2001,
            unmatched_target_iso3=[],
        )

        self.assertEqual(summary["target_rows"], 8)
        self.assertEqual(summary["available_rows"], 3)
        self.assertEqual(summary["missing_rows"], 5)
        self.assertEqual(summary["duplicate_target_keys"], 0)

    def test_write_outputs_creates_all_contract_files(self):
        panel_keys, country_year, coverage, countries_without_grid = (
            self.make_target_fixture()
        )
        target = build.build_target_output(
            panel_keys, country_year, coverage, countries_without_grid
        )
        membership = pd.DataFrame(
            {
                "latitude": [0.5],
                "longitude": [0.5],
                "ISO_A3": ["AAA"],
                "NAM_0": ["Alpha boundary"],
            }
        )
        conflicts = pd.DataFrame(
            columns=["latitude", "longitude", "ISO_A3", "NAM_0", "n_iso3"]
        )
        excluded = pd.DataFrame(
            {"country_name": ["Hong Kong SAR"], "iso3": ["HKG"], "year": [2000]}
        )
        hashes = pd.DataFrame(
            {"file": ["input.csv"], "sha256": ["a" * 64]}
        )
        qa = {"target_rows": 8, "available_rows": 3}

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paths = build.write_outputs(
                root=root,
                country_year=country_year,
                target=target,
                membership=membership,
                coverage=coverage,
                conflicts=conflicts,
                countries_without_grid=countries_without_grid,
                excluded_rows=excluded,
                input_hashes=hashes,
                qa_summary=qa,
            )

            self.assertEqual(set(paths), {
                "country_year",
                "target",
                "membership",
                "coverage",
                "conflicts",
                "countries_without_grid",
                "excluded",
                "input_hashes",
                "qa_summary",
            })
            self.assertTrue(all(path.exists() for path in paths.values()))
            self.assertEqual(len(pd.read_parquet(paths["country_year"])), 3)
            self.assertEqual(len(pd.read_csv(paths["target"])), 8)
            self.assertEqual(
                json.loads(paths["qa_summary"].read_text(encoding="utf-8")), qa
            )


class CommandLineTests(unittest.TestCase):
    def test_parse_args_uses_documented_defaults(self):
        args = build.parse_args([])

        self.assertEqual(args.root, Path(build.__file__).resolve().parents[1])
        self.assertEqual(args.climate_start_year, 1951)
        self.assertEqual(args.climate_end_year, 2018)
        self.assertEqual(args.empirical_start_year, 1995)
        self.assertEqual(args.empirical_end_year, 2018)
        self.assertEqual(args.coverage_threshold, 0.80)
        self.assertEqual(args.boundary_layer, "WB_GAD_ADM0")
        self.assertEqual(build.EXCLUDED_NON_SOVEREIGN, frozenset({"HKG", "TWN"}))


if __name__ == "__main__":
    unittest.main()
