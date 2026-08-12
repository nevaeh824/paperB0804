import csv
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(relative_path):
    path = ROOT / relative_path
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value):
    return None if value in (None, "", ".") else float(value)


class PaperBGrowthGdpDebtContractTests(unittest.TestCase):
    def assert_models_have_direct_controls(self, rows, models):
        for model in models:
            with self.subTest(model=model):
                variables = {row["variable"] for row in rows if row["model"] == model}
                self.assertTrue({"growth", "ln_constantgdp"}.issubset(variables))

    def test_every_reported_regression_has_growth_and_constant_gdp_once(self):
        baseline = read_csv("baseline/stata_outputs/model_coefficients.csv")
        baseline_models = list(dict.fromkeys(row["model"] for row in baseline))
        self.assertEqual(len(baseline_models), 10)
        self.assert_models_have_direct_controls(baseline, baseline_models)

        theta = read_csv("empirical_theta/stata_outputs/model_coefficients.csv")
        theta_models = list(dict.fromkeys(row["model"] for row in theta))
        self.assertEqual(theta_models[0], "Spread_Interact_all")
        self.assertEqual(theta_models[1:], [f"Y{i}_{name}" for i, name in [
            (1, "X_only"), (2, "A_only"), (3, "persistence"),
            (4, "all_core"), (5, "macro"), (6, "layer1_X"),
            (7, "layer2_A"), (8, "interact_core"),
            (9, "interact_macro"), (10, "interact_full"),
        ]])
        self.assert_models_have_direct_controls(
            theta, ["Spread_Interact_all", "Y1_X_only", "Y2_A_only"]
        )
        for model in theta_models[3:]:
            with self.subTest(model=model):
                variables = {row["variable"] for row in theta if row["model"] == model}
                self.assertIn("growth", variables)
                self.assertIn("Y_lag", variables)
                self.assertNotIn("ln_constantgdp", variables)

        doom = read_csv("doomloop/stata_outputs/nostate_model_coefficients.csv")
        doom_models = list(dict.fromkeys(row["model"] for row in doom))
        self.assertEqual(
            doom_models,
            ["DN1_core", "DN2_macro", "DN3_full", "RDN1_core", "RDN2_macro", "RDN3_full"],
        )
        self.assert_models_have_direct_controls(doom, doom_models)

    def test_baseline_uses_log_debt_for_b(self):
        rows = read_csv("baseline/stata_outputs/model_coefficients.csv")
        variables = {row["variable"] for row in rows}
        self.assertIn("ln_debt", variables)
        self.assertNotIn("debt_gdp", variables)

        centering = read_csv("baseline/stata_outputs/centering.csv")
        sources = {row["variable"] for row in centering}
        self.assertIn("ln_debt", sources)
        self.assertNotIn("debt_gdp", sources)

    def test_empirical_theta_uses_constant_gdp_and_log_debt(self):
        coefficients = read_csv("empirical_theta/stata_outputs/model_coefficients.csv")
        y_rows = [row for row in coefficients if row["model"].startswith("Y")]
        y_variables = {row["variable"] for row in y_rows}
        self.assertIn("Y_lag", y_variables)
        self.assertNotIn("taxbase_lag", y_variables)

        construction = read_csv("empirical_theta/stata_outputs/construction_coefficients.csv")
        construction_keys = {(row["source"], row["parameter"]) for row in construction}
        self.assertIn(("output", "gamma_A_raw"), construction_keys)
        self.assertIn(("output", "gamma_AX"), construction_keys)
        self.assertFalse(any(source == "tax" for source, _ in construction_keys))

        panel = read_csv("empirical_theta/stata_outputs/empirical_theta_panel.csv")
        self.assertTrue(panel)
        required = {
            "ConstantGDP", "debt", "ln_constantgdp", "ln_debt", "Y_outcome", "Y_lag",
            "YA_hat", "ln_debt_mA_hat", "theta_hat_A",
        }
        self.assertTrue(required.issubset(panel[0]))
        constant_gdp_by_country_year = {
            (row["iso3"], int(row["year"])): as_float(row["ln_constantgdp"])
            for row in panel
        }
        checked_leads = 0
        for row in panel:
            constant_gdp = as_float(row["ConstantGDP"])
            debt = as_float(row["debt"])
            ln_constantgdp = as_float(row["ln_constantgdp"])
            ln_debt = as_float(row["ln_debt"])
            if constant_gdp is not None:
                self.assertAlmostEqual(ln_constantgdp, math.log(constant_gdp), places=7)
                self.assertAlmostEqual(as_float(row["Y_lag"]), ln_constantgdp, places=9)
            y_outcome = as_float(row["Y_outcome"])
            if y_outcome is not None:
                following = constant_gdp_by_country_year.get(
                    (row["iso3"], int(row["year"]) + 1)
                )
                self.assertIsNotNone(following)
                self.assertAlmostEqual(y_outcome, following, places=9)
                checked_leads += 1
            if debt is not None:
                self.assertAlmostEqual(ln_debt, math.log(debt), places=7)
            m_a = as_float(row["mA_hat"])
            y_a = as_float(row["YA_hat"])
            theta = as_float(row["theta_hat_A"])
            component = as_float(row["ln_debt_mA_hat"])
            if None not in (ln_debt, m_a, y_a, theta, component):
                self.assertAlmostEqual(component, ln_debt * m_a, places=9)
                self.assertAlmostEqual(theta, component + y_a, places=9)
        self.assertGreater(checked_leads, 1000)

    def test_doomloop_uses_log_debt_change_and_new_criteria(self):
        panel = read_csv("doomloop/stata_outputs/doomloop_nostate_panel.csv")
        by_country_year = {
            (row["iso3"], int(row["year"])): as_float(row["ln_debt"])
            for row in panel
        }
        checked = 0
        for row in panel:
            outcome = as_float(row["b_outcome"])
            current = as_float(row["ln_debt"])
            following = by_country_year.get((row["iso3"], int(row["year"]) + 1))
            if outcome is not None:
                self.assertIsNotNone(following)
                self.assertAlmostEqual(outcome, following - current, places=9)
                checked += 1
        self.assertGreater(checked, 1000)

        criteria = read_csv("doomloop/stata_outputs/criterion_comparison.csv")
        self.assertEqual(
            {(row["criterion"], row["variable"]) for row in criteria},
            {
                ("theta", "theta_hat_A"),
                ("b", "ln_debt"),
                ("mA", "mA_hat"),
                ("YA", "YA_hat"),
                ("b*mA", "ln_debt_mA_hat"),
            },
        )

    def test_readiness_outcome_is_current_minus_strict_previous_year(self):
        panel = read_csv("doomloop/stata_outputs/doomloop_nostate_panel.csv")
        readiness_by_country_year = {
            (row["iso3"], int(row["year"])): as_float(row["readiness100"])
            for row in panel
        }
        checked = 0
        for row in panel:
            outcome = as_float(row["A_outcome"])
            if outcome is None:
                continue
            current_year = int(row["year"])
            current = as_float(row["readiness100"])
            previous = readiness_by_country_year.get((row["iso3"], current_year - 1))
            self.assertIsNotNone(previous)
            self.assertEqual(int(row["A_outcome_year"]), current_year)
            self.assertAlmostEqual(outcome, current - previous, places=9)
            checked += 1
        self.assertGreater(checked, 1000)

    def test_generated_documents_state_the_new_equations(self):
        results = (ROOT / "paperB/paperB_results.md").read_text(encoding="utf-8")
        diagnostics = (ROOT / "paperB/paperB_diagnostics.md").read_text(encoding="utf-8")
        self.assertIn(r"Y_{it}=\ln(ConstantGDP_{it})", results)
        self.assertIn(r"b_{it}=\ln(debt_{it})", results)
        self.assertIn(r"A_{it}-A_{i,t-1}", results)
        self.assertIn(r"\Delta\ln(debt)_{i,t+1}", results)
        self.assertIn("| Growth |", results)
        self.assertIn("ln_constantgdp", diagnostics)
        self.assertIn("ln_debt", diagnostics)


if __name__ == "__main__":
    unittest.main()
