import csv
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GDP_TERMS = {"CurrentGDP", "ConstantGDP", "ln_currentgdp", "ln_constantgdp"}
BASELINE_CONTROL_MODELS = {
    "C_macro",
    "Layer1_X",
    "Layer2_A",
    "Interact_AB",
    "Interact_AX",
    "Interact_all",
}


def rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ControlExclusionOutputTests(unittest.TestCase):
    def test_baseline_output_excludes_gdp_controls_but_keeps_other_macro_controls(self):
        coefficient_rows = rows("baseline/stata_outputs/model_coefficients.csv")
        actual = {
            (row["model"], row["variable"])
            for row in coefficient_rows
            if row["variable"] in GDP_TERMS
        }
        self.assertEqual(set(), actual)
        for model in BASELINE_CONTROL_MODELS:
            model_variables = {
                row["variable"] for row in coefficient_rows if row["model"] == model
            }
            self.assertIn("growth", model_variables, model)
            self.assertIn("inflation_cpi", model_variables, model)

    def test_spread_validation_excludes_gdp_controls(self):
        actual = [
            (row["model"], row["variable"])
            for row in rows("empirical_theta/stata_outputs/model_coefficients.csv")
            if row["model"] == "Spread_Interact_all"
            and row["variable"] in GDP_TERMS
        ]
        self.assertEqual([], actual)

    def test_t_models_exclude_growth_but_keep_remaining_control_blocks(self):
        coefficient_rows = rows("empirical_theta/stata_outputs/model_coefficients.csv")
        t_rows = [row for row in coefficient_rows if row["model"].startswith("T")]
        self.assertEqual([], [row for row in t_rows if row["variable"] == "growth"])

        for model in {"T5_macro", "T6_layer1_X", "T7_layer2_A", "T9_interact_macro", "T10_interact_full"}:
            model_variables = {
                row["variable"] for row in t_rows if row["model"] == model
            }
            self.assertIn("inflation_cpi", model_variables, model)
        for model in {"T6_layer1_X", "T7_layer2_A", "T10_interact_full"}:
            model_variables = {
                row["variable"] for row in t_rows if row["model"] == model
            }
            self.assertIn("reserves", model_variables, model)
            self.assertIn("tt", model_variables, model)

    def test_tax_and_doomloop_outputs_remain_gdp_free(self):
        tax_variables = {
            row["variable"]
            for row in rows("empirical_theta/stata_outputs/model_coefficients.csv")
            if row["model"].startswith("T")
        }
        doom_variables = {
            row["variable"]
            for row in rows(
                "doomloop/stata_outputs/nostate_model_coefficients.csv"
            )
        }
        self.assertTrue(GDP_TERMS.isdisjoint(tax_variables))
        self.assertTrue(GDP_TERMS.isdisjoint(doom_variables))

    def test_run_metadata_audits_constant_gdp_positivity(self):
        baseline_items = {
            row["item"]: float(row["value"])
            for row in rows("baseline/stata_outputs/run_metadata.csv")
        }
        theta_items = {
            row["item"]: float(row["value"])
            for row in rows("empirical_theta/stata_outputs/run_metadata.csv")
        }
        self.assertEqual(0.0, baseline_items["nonpositive_ConstantGDP"])
        self.assertEqual(0.0, theta_items["nonpositive_ConstantGDP_rows"])


if __name__ == "__main__":
    unittest.main()
