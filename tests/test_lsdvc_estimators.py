import csv
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class LsdvcEstimatorOutputTests(unittest.TestCase):
    def test_sections_two_and_three_report_the_requested_lsdvc_configuration(self):
        expected_models = {
            "baseline/stata_outputs/model_stats.csv": {
                "A_X_only",
                "A_A_only",
                "A_b_only",
                "B_all_core",
                "C_macro",
                "Layer1_X",
                "Layer2_A",
                "Interact_AB",
                "Interact_AX",
                "Interact_all",
            },
            "empirical_theta/stata_outputs/model_stats.csv": {
                "Spread_Interact_all",
                "T1_X_only",
                "T2_A_only",
                "T3_persistence",
                "T4_all_core",
                "T5_macro",
                "T6_layer1_X",
                "T7_layer2_A",
                "T8_interact_core",
                "T9_interact_macro",
                "T10_interact_full",
            },
        }

        for path, expected in expected_models.items():
            model_rows = rows(path)
            self.assertEqual(expected, {row["model"] for row in model_rows}, path)
            for row in model_rows:
                self.assertEqual("LSDVC", row.get("estimator"), (path, row))
                self.assertEqual("Blundell-Bond", row.get("initial_estimator"), (path, row))
                self.assertEqual("1", row.get("bias_order"), (path, row))
                self.assertEqual("50", row.get("bootstrap_reps"), (path, row))
                self.assertEqual("bootstrap", row.get("se_type"), (path, row))
                self.assertEqual(1, int(float(row["country_fe"])), (path, row))
                self.assertEqual(1, int(float(row["year_fe"])), (path, row))

    def test_lsdvc_models_report_the_implicit_lagged_dependent_variable(self):
        expected_lags = {
            "baseline/stata_outputs/model_stats.csv": "L.bond_spreads",
            "empirical_theta/stata_outputs/model_stats.csv": None,
        }

        for path, default_lag in expected_lags.items():
            for row in rows(path):
                expected = default_lag
                if path.startswith("empirical_theta"):
                    expected = (
                        "L.bond_spreads"
                        if row["model"] == "Spread_Interact_all"
                        else "L.T_lead"
                    )
                self.assertEqual(expected, row.get("dynamic_lag"), (path, row))


if __name__ == "__main__":
    unittest.main()
