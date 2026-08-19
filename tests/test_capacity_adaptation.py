import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "data0804" / "build_invest_panel_weo.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_invest_panel_weo", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


class CapacityPanelJoinTests(unittest.TestCase):
    def test_capacity_is_left_joined_by_unique_iso3_year_without_scaling(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            capacity_source = temporary_root / "capacity.csv"
            capacity_source.write_text(
                "ISO3,Name,1995,1996\n"
                "AAA,Alpha,0.25,0.375\n"
                "BBB,Beta,,0.6\n",
                encoding="utf-8",
            )
            panel = temporary_root / "panel.csv"
            panel.write_text(
                "country_name,iso3,year,vulnerability_delta100,readiness100\n"
                "Alpha,AAA,1995,1.5,50\n"
                "Alpha,AAA,1996,1.6,51\n"
                "Beta,BBB,1995,2.5,60\n"
                "Beta,BBB,1996,2.6,61\n",
                encoding="utf-8",
            )

            builder.add_ndgain_capacity_column(
                panel, source=capacity_source, years=[1995, 1996]
            )

            fieldnames, rows = read_rows(panel)
            self.assertEqual(
                [
                    "country_name",
                    "iso3",
                    "year",
                    "vulnerability_delta100",
                    "capacity",
                    "readiness100",
                ],
                fieldnames,
            )
            self.assertEqual(
                [("AAA", "1995"), ("AAA", "1996"), ("BBB", "1995"), ("BBB", "1996")],
                [(row["iso3"], row["year"]) for row in rows],
            )
            self.assertEqual(["0.25", "0.375", "", "0.6"], [row["capacity"] for row in rows])
            self.assertEqual(["1.5", "1.6", "2.5", "2.6"], [row["vulnerability_delta100"] for row in rows])

    def test_full_panel_rebuild_includes_capacity(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            base_panel = temporary_root / "base.csv"
            base_panel.write_text(
                "country_name,iso3,year,vulnerability100,readiness100,OB_gdp,reserves\n"
                "Alpha,AAA,1995,40,50,-2,\n",
                encoding="utf-8",
            )
            output_panel = temporary_root / "output.csv"
            original_base = builder.BASE_CSV
            original_output = builder.OUTPUT_CSV
            builder.BASE_CSV = base_panel
            builder.OUTPUT_CSV = output_panel
            try:
                builder.write_merged_csv(
                    {},
                    ndgain_delta_values={
                        "vulnerability_delta100": {},
                        "readiness_delta100": {},
                    },
                    reserve_values={},
                    capacity_values={("AAA", 1995): "0.25"},
                )
            finally:
                builder.BASE_CSV = original_base
                builder.OUTPUT_CSV = original_output

            fieldnames, rows = read_rows(output_panel)
            self.assertIn("capacity", fieldnames)
            self.assertEqual("0.25", rows[0]["capacity"])


class CapacityPanelOutputTests(unittest.TestCase):
    def test_delivered_panel_capacity_matches_the_wide_source_by_key(self):
        source_fields, source_rows = read_rows(
            ROOT
            / "data0804"
            / "ndgain_countryindex_2026"
            / "resources"
            / "vulnerability"
            / "capacity.csv"
        )
        years = [field for field in source_fields if field.isdigit()]
        source = {
            (row["ISO3"], year): row[year]
            for row in source_rows
            for year in years
            if row[year] != ""
        }
        fieldnames, panel = read_rows(ROOT / "data0804" / "invest_panel_weo.csv")

        self.assertIn("capacity", fieldnames)
        self.assertEqual(len(panel), len({(row["iso3"], row["year"]) for row in panel}))
        compared = 0
        unmatched_iso3 = set()
        for row in panel:
            expected = source.get((row["iso3"], row["year"]), "")
            if expected == "":
                self.assertEqual("", row["capacity"], (row["iso3"], row["year"]))
                unmatched_iso3.add(row["iso3"])
                continue
            self.assertAlmostEqual(
                float(expected),
                float(row["capacity"]),
                delta=1e-15,
                msg=str((row["iso3"], row["year"])),
            )
            compared += 1

        self.assertEqual(1769, compared)
        self.assertEqual({"HKG", "TWN"}, unmatched_iso3)


class AdaptationCapacityWorkflowOutputTests(unittest.TestCase):
    def test_empirical_theta_panel_defines_a_as_one_minus_capacity(self):
        _, panel = read_rows(
            ROOT / "empirical_theta" / "stata_outputs" / "empirical_theta_panel.csv"
        )
        self.assertIn("capacity", panel[0])
        self.assertIn("adapt_capacity", panel[0])

        compared = 0
        for row in panel:
            if row["capacity"] == "":
                self.assertEqual("", row["adapt_capacity"])
                continue
            self.assertAlmostEqual(
                1.0 - float(row["capacity"]),
                float(row["adapt_capacity"]),
                delta=1e-12,
                msg=str((row["iso3"], row["year"])),
            )
            compared += 1
        self.assertEqual(1769, compared)

    def test_regression_outputs_use_adapt_capacity_instead_of_readiness(self):
        baseline_a_models = {"A_A_only", "B_all_core", "C_macro", "Layer2_A"}
        _, baseline_rows = read_rows(
            ROOT / "baseline" / "stata_outputs" / "model_coefficients.csv"
        )
        baseline_variables = {
            model: {
                row["variable"]
                for row in baseline_rows
                if row["model"] == model
            }
            for model in baseline_a_models
        }
        for model, variables in baseline_variables.items():
            self.assertIn("adapt_capacity", variables, model)
        self.assertNotIn("readiness100", {row["variable"] for row in baseline_rows})

        theta_a_models = {"T2_A_only", "T4_all_core", "T5_macro", "T7_layer2_A"}
        _, theta_rows = read_rows(
            ROOT / "empirical_theta" / "stata_outputs" / "model_coefficients.csv"
        )
        theta_variables = {
            model: {
                row["variable"]
                for row in theta_rows
                if row["model"] == model
            }
            for model in theta_a_models
        }
        for model, variables in theta_variables.items():
            self.assertIn("adapt_capacity", variables, model)
        self.assertNotIn("readiness100", {row["variable"] for row in theta_rows})

    def test_doomloop_a_outcome_is_the_strict_first_difference_of_one_minus_capacity(self):
        _, panel = read_rows(
            ROOT / "doomloop" / "stata_outputs" / "doomloop_nostate_panel.csv"
        )
        self.assertIn("adapt_capacity", panel[0])
        keyed = {(row["iso3"], int(row["year"])): row for row in panel}

        compared = 0
        for (iso3, year), row in keyed.items():
            previous = keyed.get((iso3, year - 1))
            if (
                previous is None
                or previous["adapt_capacity"] == ""
                or row["adapt_capacity"] == ""
            ):
                self.assertEqual("", row["A_outcome"], (iso3, year))
                continue
            expected = float(row["adapt_capacity"]) - float(
                previous["adapt_capacity"]
            )
            self.assertAlmostEqual(
                expected,
                float(row["A_outcome"]),
                delta=1e-12,
                msg=str((iso3, year)),
            )
            compared += 1
        self.assertGreater(compared, 1000)

    def test_progress_interpretation_matches_the_a_by_debt_p_value(self):
        _, coefficient_rows = read_rows(
            ROOT / "baseline" / "stata_outputs" / "model_coefficients.csv"
        )
        interaction = next(
            row
            for row in coefficient_rows
            if row["model"] == "Interact_all" and row["variable"] == "int_AB"
        )
        progress_line = next(
            line
            for line in (ROOT / "paperB" / "progress.md")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.startswith("| 利差：A×债务 |")
        )

        if float(interaction["p"]) >= 0.1:
            self.assertIn("未达到常用显著性水平", progress_line)
        else:
            self.assertIn("显著", progress_line)


if __name__ == "__main__":
    unittest.main()
