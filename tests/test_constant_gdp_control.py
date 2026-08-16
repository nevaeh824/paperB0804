import csv
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GDP_TERMS = {"CurrentGDP", "ConstantGDP", "ln_currentgdp", "ln_constantgdp"}
BASELINE_GDP_MODELS = {
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


class ConstantGdpControlOutputTests(unittest.TestCase):
    def test_baseline_output_uses_constant_gdp_log(self):
        actual = {
            (row["model"], row["variable"])
            for row in rows("baseline/stata_outputs/model_coefficients.csv")
            if row["variable"] in GDP_TERMS
        }
        expected = {
            (model, "ln_constantgdp") for model in BASELINE_GDP_MODELS
        }
        self.assertEqual(expected, actual)

    def test_spread_validation_uses_constant_gdp_log(self):
        actual = [
            (row["model"], row["variable"])
            for row in rows("empirical_theta/stata_outputs/model_coefficients.csv")
            if row["model"] == "Spread_Interact_all"
            and row["variable"] in GDP_TERMS
        ]
        self.assertEqual([("Spread_Interact_all", "ln_constantgdp")], actual)

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
