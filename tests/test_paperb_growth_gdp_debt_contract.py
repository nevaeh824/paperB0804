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

    def test_output_models_use_lagged_output_ratio_without_growth_or_log_gdp(self):
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
        self.assert_models_have_direct_controls(theta, ["Spread_Interact_all"])
        for model in theta_models[1:]:
            with self.subTest(model=model):
                variables = {row["variable"] for row in theta if row["model"] == model}
                self.assertIn("Y_lag", variables)
                self.assertNotIn("growth", variables)
                self.assertNotIn("ln_constantgdp", variables)

        doom = read_csv("doomloop/stata_outputs/nostate_model_coefficients.csv")
        doom_models = list(dict.fromkeys(row["model"] for row in doom))
        self.assertEqual(
            doom_models,
            ["DN1_core", "DN2_macro", "DN3_full", "RDN1_core", "RDN2_macro", "RDN3_full"],
        )
        self.assert_models_have_direct_controls(doom, doom_models)

    def test_baseline_uses_debt_gdp_for_b(self):
        rows = read_csv("baseline/stata_outputs/model_coefficients.csv")
        variables = {row["variable"] for row in rows}
        self.assertIn("debt_gdp", variables)
        self.assertNotIn("ln_debt", variables)

        centering = read_csv("baseline/stata_outputs/centering.csv")
        sources = {row["variable"] for row in centering}
        self.assertIn("debt_gdp", sources)
        self.assertNotIn("ln_debt", sources)

    def test_reported_models_use_ndgain_delta_regressors(self):
        output_specs = {
            "baseline/stata_outputs/model_coefficients.csv": {
                "vulnerability_delta100", "readiness_delta100"
            },
            "empirical_theta/stata_outputs/model_coefficients.csv": {
                "vulnerability_delta100", "readiness_delta100"
            },
            "doomloop/stata_outputs/nostate_model_coefficients.csv": {
                "vulnerability_delta100"
            },
        }
        for relative_path, required in output_specs.items():
            with self.subTest(relative_path=relative_path):
                variables = {row["variable"] for row in read_csv(relative_path)}
                self.assertTrue(required.issubset(variables))
                self.assertTrue(
                    {"vulnerability100", "readiness100"}.isdisjoint(variables)
                )

        theta_panel = read_csv(
            "empirical_theta/stata_outputs/empirical_theta_panel.csv"
        )
        self.assertTrue(theta_panel)
        self.assertTrue(
            {"vulnerability_delta100", "readiness_delta100"}.issubset(
                theta_panel[0]
            )
        )

    def test_empirical_theta_uses_output_ratios_and_debt_gdp(self):
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
            "ConstantGDP", "debt_gdp", "b_it_theta", "Y_outcome", "Y_lag",
            "YA_hat", "debt_gdp_mA_hat", "theta_hat_A",
        }
        self.assertTrue(required.issubset(panel[0]))
        constant_gdp_by_country_year = {
            (row["iso3"], int(row["year"])): as_float(row["ConstantGDP"])
            for row in panel
        }
        checked_leads = checked_lags = 0
        for row in panel:
            key = (row["iso3"], int(row["year"]))
            constant_gdp = as_float(row["ConstantGDP"])
            y_outcome = as_float(row["Y_outcome"])
            if y_outcome is not None:
                following = constant_gdp_by_country_year.get(
                    (row["iso3"], key[1] + 1)
                )
                self.assertIsNotNone(following)
                self.assertAlmostEqual(y_outcome, following / constant_gdp, places=9)
                checked_leads += 1
            y_lag = as_float(row["Y_lag"])
            if y_lag is not None:
                previous = constant_gdp_by_country_year.get(
                    (row["iso3"], key[1] - 1)
                )
                self.assertIsNotNone(previous)
                self.assertAlmostEqual(y_lag, constant_gdp / previous, places=9)
                checked_lags += 1
            debt_gdp = as_float(row["debt_gdp"])
            b_it = as_float(row["b_it_theta"])
            if debt_gdp is not None:
                self.assertAlmostEqual(b_it, debt_gdp, places=12)
            m_a = as_float(row["mA_hat"])
            y_a = as_float(row["YA_hat"])
            theta = as_float(row["theta_hat_A"])
            component = as_float(row["debt_gdp_mA_hat"])
            if None not in (debt_gdp, m_a, y_a, theta, component):
                self.assertAlmostEqual(component, debt_gdp * m_a, places=9)
                self.assertAlmostEqual(theta, component + y_a, places=9)
        self.assertGreater(checked_leads, 1000)
        self.assertGreater(checked_lags, 1000)

    def test_doomloop_uses_debt_gdp_change_and_new_criteria(self):
        panel = read_csv("doomloop/stata_outputs/doomloop_nostate_panel.csv")
        by_country_year = {
            (row["iso3"], int(row["year"])): as_float(row["debt_gdp"])
            for row in panel
        }
        checked = 0
        for row in panel:
            outcome = as_float(row["b_outcome"])
            current = as_float(row["debt_gdp"])
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
                ("b", "debt_gdp"),
                ("mA", "mA_hat"),
                ("YA", "YA_hat"),
                ("b*mA", "debt_gdp_mA_hat"),
            },
        )

    def test_readiness_outcome_is_current_minus_strict_previous_year(self):
        panel = read_csv("doomloop/stata_outputs/doomloop_nostate_panel.csv")
        readiness_by_country_year = {
            (row["iso3"], int(row["year"])): as_float(
                row["readiness_delta100"]
            )
            for row in panel
        }
        checked = 0
        for row in panel:
            outcome = as_float(row["A_outcome"])
            if outcome is None:
                continue
            current_year = int(row["year"])
            current = as_float(row["readiness_delta100"])
            previous = readiness_by_country_year.get((row["iso3"], current_year - 1))
            self.assertIsNotNone(previous)
            self.assertEqual(int(row["A_outcome_year"]), current_year)
            self.assertAlmostEqual(outcome, current - previous, places=9)
            checked += 1
        self.assertGreater(checked, 1000)

    def test_generated_documents_state_the_new_equations(self):
        results = (ROOT / "paperB/paperB_results.md").read_text(encoding="utf-8")
        diagnostics = (ROOT / "paperB/paperB_diagnostics.md").read_text(encoding="utf-8")
        self.assertIn(r"Y_{it}=\frac{ConstantGDP_{it}}{ConstantGDP_{i,t-1}}", results)
        self.assertIn(r"Y_{i,t+1}=\frac{ConstantGDP_{i,t+1}}{ConstantGDP_{it}}", results)
        self.assertIn(r"b_{it}=debt\_gdp_{it}", results)
        self.assertIn(r"A_{it}-A_{i,t-1}", results)
        self.assertIn(r"\Delta debt\_gdp_{i,t+1}", results)
        self.assertIn("| Growth |", results)
        self.assertIn("Y_lag", diagnostics)
        self.assertIn("debt_gdp", diagnostics)


if __name__ == "__main__":
    unittest.main()
