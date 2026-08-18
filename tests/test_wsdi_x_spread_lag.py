import csv
from collections import defaultdict
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE_MODELS = {
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
}
BASELINE_RAW_X_MODELS = {
    "A_X_only",
    "B_all_core",
    "C_macro",
    "Layer1_X",
    "Layer2_A",
}
TAX_RAW_X_MODELS = {
    "T1_X_only",
    "T4_all_core",
    "T5_macro",
    "T6_layer1_X",
    "T7_layer2_A",
}
BASELINE_RAW_B_MODELS = {
    "A_b_only",
    "B_all_core",
    "C_macro",
    "Layer1_X",
    "Layer2_A",
}
T_MODELS_WITH_CURRENT_T = {
    "T3_persistence",
    "T4_all_core",
    "T5_macro",
    "T6_layer1_X",
    "T7_layer2_A",
    "T8_interact_core",
    "T9_interact_macro",
    "T10_interact_full",
}


def rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def variables_by_model(relative_path: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for row in rows(relative_path):
        result[row["model"]].add(row["variable"])
    return dict(result)


class WsdiXAndSpreadLagOutputTests(unittest.TestCase):
    def test_every_baseline_model_controls_for_spread_lag(self):
        coefficient_rows = rows("baseline/stata_outputs/model_coefficients.csv")
        variables = variables_by_model("baseline/stata_outputs/model_coefficients.csv")
        self.assertEqual(BASELINE_MODELS, set(variables))
        missing_lag = {
            model for model in BASELINE_MODELS if "spread_lag" not in variables[model]
        }
        self.assertEqual(set(), missing_lag)
        lag_rows = [row for row in coefficient_rows if row["variable"] == "spread_lag"]
        self.assertEqual(len(BASELINE_MODELS), len(lag_rows))
        for row in lag_rows:
            self.assertEqual("0", row["omitted"], row["model"])
            self.assertTrue(row["coefficient"] not in {"", "."}, row["model"])
            self.assertTrue(row["se"] not in {"", "."}, row["model"])
            self.assertTrue(float(row["se"]) > 0, row["model"])

    def test_empirical_theta_reproduces_the_lagged_spread_model(self):
        variables = variables_by_model(
            "empirical_theta/stata_outputs/model_coefficients.csv"
        )
        self.assertIn("spread_lag", variables["Spread_Interact_all"])

        validation_rows = rows(
            "empirical_theta/stata_outputs/baseline_validation.csv"
        )
        validated = {row["variable"] for row in validation_rows}
        self.assertIn("spread_lag", validated)
        self.assertLessEqual(
            max(float(row["abs_b_diff"]) for row in validation_rows), 1e-10
        )
        self.assertLessEqual(
            max(float(row["abs_se_diff"]) for row in validation_rows), 1e-8
        )

    def test_retained_models_use_wsdi_days_instead_of_vulnerability(self):
        baseline = variables_by_model(
            "baseline/stata_outputs/model_coefficients.csv"
        )
        for model in BASELINE_RAW_X_MODELS:
            self.assertIn("wsdi_days", baseline[model])

        theta = variables_by_model(
            "empirical_theta/stata_outputs/model_coefficients.csv"
        )
        for model in TAX_RAW_X_MODELS:
            self.assertIn("wsdi_days", theta[model])

        doom = variables_by_model(
            "doomloop/stata_outputs/nostate_model_coefficients.csv"
        )
        self.assertGreater(len(doom), 0)
        for model, model_variables in doom.items():
            self.assertIn("wsdi_days", model_variables, model)

        for variables in (baseline, theta, doom):
            for model_variables in variables.values():
                self.assertNotIn("vulnerability100", model_variables)

    def test_theta_panel_wsdi_values_equal_keyed_source_times_point_zero_one(self):
        source = {
            (row["iso3"], int(row["year"])): row["wsdi_days"]
            for row in rows(
                "WSDI/data/processed/wsdi_sovereign61_1995_2018.csv"
            )
        }
        panel = rows("empirical_theta/stata_outputs/empirical_theta_panel.csv")
        self.assertIn("wsdi_days", panel[0])

        compared = 0
        for row in panel:
            key = (row["iso3"], int(row["year"]))
            source_value = source.get(key, "")
            if source_value == "":
                self.assertEqual("", row["wsdi_days"], key)
                continue
            self.assertNotEqual("", row["wsdi_days"], key)
            self.assertAlmostEqual(
                float(source_value) * 0.01,
                float(row["wsdi_days"]),
                delta=1e-12,
                msg=str(key),
            )
            compared += 1

        self.assertEqual(1233, compared)

    def test_theta_panel_spread_lag_uses_only_exact_previous_year(self):
        panel = rows("empirical_theta/stata_outputs/empirical_theta_panel.csv")
        self.assertIn("spread_lag", panel[0])
        keyed = {(row["iso3"], int(row["year"])): row for row in panel}

        compared = 0
        for (iso3, year), row in keyed.items():
            previous = keyed.get((iso3, year - 1))
            expected = "" if previous is None else previous["bond_spreads"]
            if expected == "":
                self.assertEqual("", row["spread_lag"], (iso3, year))
                continue
            self.assertNotEqual("", row["spread_lag"], (iso3, year))
            self.assertAlmostEqual(
                float(expected),
                float(row["spread_lag"]),
                delta=1e-12,
                msg=str((iso3, year)),
            )
            compared += 1

        self.assertGreater(compared, 1000)

    def test_baseline_raw_debt_state_uses_strict_prior_year_debt(self):
        variables = variables_by_model("baseline/stata_outputs/model_coefficients.csv")
        for model in BASELINE_RAW_B_MODELS:
            self.assertIn("b_pre", variables[model], model)
            self.assertNotIn("debt_gdp", variables[model], model)

        centered = {row["variable"] for row in rows("baseline/stata_outputs/centering.csv")}
        self.assertIn("b_pre", centered)
        self.assertNotIn("debt_gdp", centered)

    def test_theta_panel_b_pre_is_exact_previous_year_debt(self):
        panel = rows("empirical_theta/stata_outputs/empirical_theta_panel.csv")
        self.assertIn("b_pre", panel[0])
        keyed = {(row["iso3"], int(row["year"])): row for row in panel}

        compared = 0
        for (iso3, year), row in keyed.items():
            previous = keyed.get((iso3, year - 1))
            expected = "" if previous is None else previous["debt_gdp"]
            if expected == "":
                self.assertEqual("", row["b_pre"], (iso3, year))
                continue
            self.assertAlmostEqual(
                float(expected), float(row["b_pre"]), delta=1e-12, msg=str((iso3, year))
            )
            compared += 1

        self.assertGreater(compared, 1000)

    def test_t_indicator_is_consecutive_constant_gdp_level_ratio(self):
        panel = rows("empirical_theta/stata_outputs/empirical_theta_panel.csv")
        self.assertIn("T_it", panel[0])
        self.assertIn("T_lead", panel[0])
        keyed = {(row["iso3"], int(row["year"])): row for row in panel}

        compared_current = 0
        compared_lead = 0
        for (iso3, year), row in keyed.items():
            previous = keyed.get((iso3, year - 1))
            if previous is None or previous["ConstantGDP"] == "" or row["ConstantGDP"] == "":
                self.assertEqual("", row["T_it"], (iso3, year))
            else:
                denominator = float(previous["ConstantGDP"])
                expected = float(row["ConstantGDP"]) / denominator
                self.assertAlmostEqual(expected, float(row["T_it"]), delta=1e-7, msg=str((iso3, year)))
                compared_current += 1

            following = keyed.get((iso3, year + 1))
            expected_lead = "" if following is None else following["T_it"]
            if expected_lead == "":
                self.assertEqual("", row["T_lead"], (iso3, year))
            else:
                self.assertAlmostEqual(float(expected_lead), float(row["T_lead"]), delta=1e-12, msg=str((iso3, year)))
                compared_lead += 1

        self.assertGreater(compared_current, 1000)
        self.assertGreater(compared_lead, 1000)

    def test_readiness_outcome_is_exact_first_difference(self):
        panel = rows("doomloop/stata_outputs/doomloop_nostate_panel.csv")
        self.assertIn("A_outcome", panel[0])
        keyed = {(row["iso3"], int(row["year"])): row for row in panel}

        compared = 0
        for (iso3, year), row in keyed.items():
            previous = keyed.get((iso3, year - 1))
            if previous is None or previous["readiness100"] == "" or row["readiness100"] == "":
                self.assertEqual("", row["A_outcome"], (iso3, year))
                continue
            expected = float(row["readiness100"]) - float(previous["readiness100"])
            self.assertAlmostEqual(
                expected,
                float(row["A_outcome"]),
                delta=1e-12,
                msg=str((iso3, year)),
            )
            compared += 1

        self.assertGreater(compared, 1000)

    def test_t_models_use_new_current_t_indicator_not_taxgdp(self):
        variables = variables_by_model("empirical_theta/stata_outputs/model_coefficients.csv")
        for model in T_MODELS_WITH_CURRENT_T:
            self.assertIn("T_it", variables[model], model)
            self.assertNotIn("taxbase_lag", variables[model], model)
            self.assertNotIn("taxgdp", variables[model], model)

    def test_theta_and_competing_debt_criteria_use_b_pre(self):
        panel = rows("empirical_theta/stata_outputs/empirical_theta_panel.csv")
        compared = 0
        for row in panel:
            if any(row.get(name, "") == "" for name in ("b_pre", "mA_hat", "TA_hat", "theta_hat_A")):
                continue
            expected_component = float(row["b_pre"]) * float(row["mA_hat"])
            self.assertAlmostEqual(expected_component, float(row["spread_saving_component"]), delta=1e-12)
            self.assertAlmostEqual(expected_component + float(row["TA_hat"]), float(row["theta_hat_A"]), delta=1e-12)
            compared += 1
        self.assertGreater(compared, 500)

        criteria = {row["criterion"]: row["variable"] for row in rows("doomloop/stata_outputs/criterion_comparison.csv")}
        self.assertEqual("b_pre", criteria["b_pre"])
        self.assertEqual("b_pre_mA_hat", criteria["b_pre*mA"])


if __name__ == "__main__":
    unittest.main()
