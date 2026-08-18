import csv
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sample_keys(panel_rows: list[dict[str, str]], flag: str) -> set[tuple[str, int]]:
    return {
        (row["iso3"], int(row["year"]))
        for row in panel_rows
        if row[flag] == "1"
    }


class FullWorkflowCommonSampleTests(unittest.TestCase):
    def test_every_reported_regression_uses_one_cross_stage_sample_size(self):
        stats_paths = (
            "baseline/stata_outputs/model_stats.csv",
            "empirical_theta/stata_outputs/model_stats.csv",
            "doomloop/stata_outputs/nostate_model_stats.csv",
        )
        sample_sizes = {
            int(float(row["N"]))
            for path in stats_paths
            for row in rows(path)
        }
        self.assertEqual(1, len(sample_sizes), sample_sizes)

    def test_theta_components_exist_only_on_the_common_sample(self):
        panel = rows("empirical_theta/stata_outputs/empirical_theta_panel.csv")
        self.assertGreater(len(panel), 0)
        for field in (
            "sample_common_all",
            "sample_spread",
            "sample_tax",
            "sample_theta_support",
            "theta_constructible",
        ):
            self.assertIn(field, panel[0])

        for row in panel:
            flags = {
                row["sample_common_all"],
                row["sample_spread"],
                row["sample_tax"],
                row["sample_theta_support"],
                row["theta_constructible"],
            }
            self.assertEqual(1, len(flags), (row["iso3"], row["year"], flags))
            expected_present = row["sample_common_all"] == "1"
            for field in ("mA_hat", "TA_hat", "theta_hat_A"):
                self.assertEqual(
                    expected_present,
                    row[field] not in {"", "."},
                    (row["iso3"], row["year"], field),
                )

    def test_doomloop_equations_use_exact_theta_common_keys(self):
        theta_panel = rows(
            "empirical_theta/stata_outputs/empirical_theta_panel.csv"
        )
        doom_panel = rows("doomloop/stata_outputs/doomloop_nostate_panel.csv")
        self.assertGreater(len(doom_panel), 0)
        self.assertIn("sample_common_all", doom_panel[0])

        common = sample_keys(theta_panel, "sample_common_all")
        self.assertEqual(common, sample_keys(doom_panel, "sample_common_all"))
        self.assertEqual(common, sample_keys(doom_panel, "sample_debt_ns"))
        self.assertEqual(common, sample_keys(doom_panel, "sample_ready_ns"))

    def test_theta_criterion_matches_the_reported_full_debt_model(self):
        criterion = next(
            row
            for row in rows("doomloop/stata_outputs/criterion_comparison.csv")
            if row["criterion"] == "theta"
        )
        coefficients = rows(
            "doomloop/stata_outputs/nostate_model_coefficients.csv"
        )
        full = {
            row["variable"]: row
            for row in coefficients
            if row["model"] == "DN3_full"
        }
        self.assertAlmostEqual(
            float(criterion["beta_L"]),
            float(full["debt_kink_low"]["coefficient"]),
            delta=1e-10,
        )
        self.assertAlmostEqual(
            float(criterion["beta_H"]),
            float(full["debt_kink_high"]["coefficient"]),
            delta=1e-10,
        )


if __name__ == "__main__":
    unittest.main()
