import csv
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MISSING = {"", "."}


def rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def present(row: dict[str, str], field: str) -> bool:
    return row.get(field, "") not in MISSING


class CurrentRegressionSampleTests(unittest.TestCase):
    def test_progressive_models_use_their_own_complete_case_samples(self):
        baseline = {
            row["model"]: int(float(row["N"]))
            for row in rows("paperB/paperBresult/baseline/stata_outputs/model_stats.csv")
        }
        self.assertGreater(baseline["A_X_only"], baseline["Layer2_A"])
        self.assertGreater(baseline["A_A_only"], baseline["Layer2_A"])
        self.assertGreaterEqual(baseline["C_macro"], baseline["Layer2_A"])

        theta = {
            row["model"]: int(float(row["N"]))
            for row in rows("paperB/paperBresult/empirical_theta/stata_outputs/model_stats.csv")
        }
        self.assertGreater(theta["T1_X_only"], theta["T10_interact_full"])
        self.assertGreater(theta["T2_A_only"], theta["T10_interact_full"])

        doomloop = {
            row["model"]: int(float(row["N"]))
            for row in rows("paperB/paperBresult/doomloop/stata_outputs/nostate_model_stats.csv")
        }
        self.assertGreaterEqual(doomloop["DN1_core"], doomloop["DN3_full"])
        self.assertGreaterEqual(doomloop["RDN1_core"], doomloop["RDN3_full"])

    def test_sections_two_and_three_use_bootstrap_and_section_four_clusters(self):
        lsdvc_paths = (
            "paperB/paperBresult/baseline/stata_outputs/model_stats.csv",
            "paperB/paperBresult/empirical_theta/stata_outputs/model_stats.csv",
        )
        for path in lsdvc_paths:
            model_rows = rows(path)
            self.assertGreater(len(model_rows), 0, path)
            for row in model_rows:
                self.assertEqual("LSDVC", row["estimator"], (path, row))
                self.assertEqual("bootstrap", row["se_type"], (path, row))
                self.assertEqual("50", row["bootstrap_reps"], (path, row))

        path = "paperB/paperBresult/doomloop/stata_outputs/nostate_model_stats.csv"
        for row in rows(path):
            self.assertEqual("country_id", row["cluster_variable"], (path, row))
            self.assertGreaterEqual(int(float(row["clusters"])), 2, (path, row))

    def test_generated_components_are_limited_to_their_source_regression_samples(self):
        panel = rows("paperB/paperBresult/empirical_theta/stata_outputs/empirical_theta_panel.csv")
        self.assertGreater(len(panel), 0)

        for row in panel:
            spread_source_sample = row["sample_spread"] == "1"
            tax_source_sample = row["sample_tax"] == "1"
            self.assertEqual(
                spread_source_sample,
                present(row, "mA_hat"),
                (row["iso3"], row["year"]),
            )
            self.assertEqual(
                tax_source_sample,
                present(row, "TA_hat"),
                (row["iso3"], row["year"]),
            )

            expected_theta = (
                present(row, "b_it")
                and spread_source_sample
                and tax_source_sample
            )
            self.assertEqual(
                expected_theta,
                present(row, "theta_hat_A"),
                (row["iso3"], row["year"]),
            )

    def test_dn3_full_is_a_subset_of_both_upstream_source_samples(self):
        upstream = {
            (row["iso3"], row["year"]): row
            for row in rows("paperB/paperBresult/empirical_theta/stata_outputs/empirical_theta_panel.csv")
        }
        dn3_rows = [
            row
            for row in rows("paperB/paperBresult/doomloop/stata_outputs/nostate_sample_audit.csv")
            if row["sample_debt_ns"] == "1"
        ]
        self.assertGreater(len(dn3_rows), 0)

        for row in dn3_rows:
            source = upstream[(row["iso3"], row["year"])]
            self.assertEqual("1", source["sample_spread"], (row["iso3"], row["year"]))
            self.assertEqual("1", source["sample_tax"], (row["iso3"], row["year"]))

    def test_layer2_a_country_distribution_reconciles_to_model_sample(self):
        distribution = rows(
            "paperB/paperBresult/baseline/stata_outputs/layer2_a_country_distribution.csv"
        )
        self.assertGreater(len(distribution), 1)
        self.assertEqual(
            len(distribution),
            len({row["iso3"] for row in distribution}),
        )
        self.assertTrue(all(row["model"] == "Layer2_A" for row in distribution))

        layer2_stats = next(
            row
            for row in rows("paperB/paperBresult/baseline/stata_outputs/model_stats.csv")
            if row["model"] == "Layer2_A"
        )
        self.assertEqual(
            int(float(layer2_stats["N"])),
            sum(int(float(row["observations"])) for row in distribution),
        )
        self.assertAlmostEqual(
            1.0,
            sum(float(row["sample_share"]) for row in distribution),
            delta=1e-8,
        )
        self.assertTrue(
            all(int(row["first_year"]) <= int(row["last_year"]) for row in distribution)
        )

    def test_diagnostics_reports_layer2_a_country_distribution(self):
        diagnostics = (ROOT / "paperB/paperBresult/paperB_diagnostics.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Distribution of country or region samples — Layer2_A", diagnostics)
        for row in rows("paperB/paperBresult/baseline/stata_outputs/layer2_a_country_distribution.csv"):
            self.assertIn(
                f"| {row['country_name']} | {row['iso3']} |",
                diagnostics,
            )
            self.assertIn(
                f"| {int(float(row['first_year']))} | {int(float(row['last_year']))} |",
                diagnostics,
            )


if __name__ == "__main__":
    unittest.main()
