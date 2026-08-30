import csv
import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PERCENTILES = {"P10", "P25", "P50", "P75", "P90"}


def rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class NewFigureOutputTests(unittest.TestCase):
    def test_theta_plot_data_use_the_debt_equation_sample_and_cutoff(self):
        distribution = rows("paperB/paperBresult/doomloop/stata_outputs/theta_distribution_cutoff_plot_data.csv")
        cutoff = float(rows("paperB/paperBresult/doomloop/stata_outputs/nostate_cutoffs.csv")[0]["rss_min_cutoff"])
        panel = rows("paperB/paperBresult/doomloop/stata_outputs/doomloop_nostate_panel.csv")
        debt_sample = [row for row in panel if row["sample_debt_ns"] == "1"]

        self.assertEqual(len(debt_sample), len(distribution))
        self.assertEqual(
            {(row["iso3"], row["year"]) for row in debt_sample},
            {(row["iso3"], row["year"]) for row in distribution},
        )
        for row in distribution:
            self.assertTrue(math.isclose(float(row["cutoff"]), cutoff, abs_tol=1e-12))

    def test_country_rank_plot_data_reconcile_to_theta_distribution(self):
        distribution = rows("paperB/paperBresult/doomloop/stata_outputs/theta_distribution_cutoff_plot_data.csv")
        ranking = rows("paperB/paperBresult/doomloop/stata_outputs/theta_country_rank_plot_data.csv")

        self.assertEqual(50, len(ranking))
        self.assertEqual(50, len({row["iso3"] for row in ranking}))
        self.assertEqual(set(range(1, 51)), {int(float(row["rank"])) for row in ranking})

        for row in ranking:
            country_rows = [item for item in distribution if item["iso3"] == row["iso3"]]
            self.assertEqual(len(country_rows), int(float(row["observations"])))
            expected_mean = sum(float(item["theta_hat_A"]) for item in country_rows) / len(country_rows)
            self.assertTrue(
                math.isclose(float(row["theta_mean"]), expected_mean, rel_tol=1e-7, abs_tol=1e-10),
                row,
            )

    def test_mA_plot_data_are_sign_reversed_interact_all_effects(self):
        source = {
            (row["moderator"], row["point"]): row
            for row in rows("paperB/paperBresult/baseline/stata_outputs/marginal_effects.csv")
            if row["model"] == "Interact_all"
            and row["moderator"] in {"b_it", "wsdi_days"}
            and row["point"] in PERCENTILES
        }
        plotted = rows("paperB/paperBresult/doomloop/stata_outputs/mA_by_debt_wsdi_plot_data.csv")

        self.assertEqual(10, len(source))
        self.assertEqual(10, len(plotted))
        self.assertEqual(set(source), {(row["moderator"], row["point"]) for row in plotted})
        for row in plotted:
            original = source[(row["moderator"], row["point"])]
            self.assertTrue(math.isclose(float(row["moderator_value"]), float(original["moderator_value"]), abs_tol=1e-12))
            self.assertTrue(math.isclose(float(row["mA"]), -float(original["marginal_effect"]), rel_tol=1e-7, abs_tol=1e-10))
            self.assertTrue(math.isclose(float(row["se"]), float(original["se"]), rel_tol=1e-7, abs_tol=1e-10))
            self.assertTrue(math.isclose(float(row["ci_low"]), -float(original["ci_high"]), rel_tol=1e-7, abs_tol=1e-10))
            self.assertTrue(math.isclose(float(row["ci_high"]), -float(original["ci_low"]), rel_tol=1e-7, abs_tol=1e-10))
            self.assertEqual("LSDVC bootstrap VCE (50 reps)", row["inference"])

    def test_new_figure_assets_are_exported_and_documented(self):
        names = [
            "figure1a_theta_distribution_cutoff.png",
            "figure1a_theta_distribution_cutoff.pdf",
            "figure1b_theta_country_rank_cutoff.png",
            "figure1b_theta_country_rank_cutoff.pdf",
            "figure2_mA_by_debt_wsdi.png",
            "figure2_mA_by_debt_wsdi.pdf",
        ]
        for directory in ["paperB/paperBresult/doomloop/figures", "paperB/paperBresult/figures"]:
            for name in names:
                path = ROOT / directory / name
                self.assertTrue(path.is_file() and path.stat().st_size > 0, path)

        results_text = (ROOT / "paperB/paperBresult/paperB_results.md").read_text(encoding="utf-8")
        diagnostics_text = (ROOT / "paperB/paperBresult/paperB_diagnostics.md").read_text(encoding="utf-8")
        workflow_text = (ROOT / "paperB/WORKFLOW.md").read_text(encoding="utf-8")
        for name in names:
            self.assertIn(name, results_text)
            self.assertIn(name, diagnostics_text)
            self.assertIn(name, workflow_text)


if __name__ == "__main__":
    unittest.main()
