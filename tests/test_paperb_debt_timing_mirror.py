from __future__ import annotations

import csv
import importlib.util
import math
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "paperB" / "paperBresult"
LAGGED = ROOT / "paperB_debt_lag" / "paperB_debt_lag"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def present(value: str | None) -> bool:
    return value not in (None, "", ".")


class TestPaperBDebtTimingMirror(unittest.TestCase):
    def test_cutoff_search_uses_every_estimable_observed_theta_value(self) -> None:
        sample_flags = {
            "theta": "sample_criterion_theta",
            "b_it": "sample_criterion_debt",
            "b_pre": "sample_criterion_debt",
            "mA": "sample_criterion_ma",
            "TA": "sample_criterion_ta",
            "b_it*mA": "sample_criterion_bma",
            "b_pre*mA": "sample_criterion_bma",
        }

        for result_root in (CURRENT, LAGGED):
            panel = rows(
                result_root / "doomloop/stata_outputs/doomloop_nostate_panel.csv"
            )
            profiles = rows(
                result_root / "doomloop/stata_outputs/criterion_rss_profiles.csv"
            )
            profile_by_criterion: dict[str, list[dict[str, str]]] = {}
            for row in profiles:
                profile_by_criterion.setdefault(row["criterion"], []).append(row)

            variables = {
                row["criterion"]: row["variable"]
                for row in profiles
            }
            self.assertEqual(set(sample_flags) & set(variables), set(variables))
            for criterion, variable in variables.items():
                sample_flag = sample_flags[criterion]
                observed = sorted(
                    {
                        float(row[variable])
                        for row in panel
                        if row[sample_flag] == "1" and present(row[variable])
                    }
                )
                self.assertGreaterEqual(len(observed), 3, (result_root, criterion))

                # The minimum and maximum cannot identify both hinge slopes:
                # at least one observation must be strictly below and above c.
                actual = sorted(
                    float(row["cutoff"])
                    for row in profile_by_criterion[criterion]
                )
                # CSV decimal formatting can collapse a handful of distinct
                # Stata doubles, so allow only that narrow serialization gap.
                self.assertLessEqual(
                    abs((len(observed) - 2) - len(actual)),
                    2,
                    (result_root, criterion),
                )
                self.assertGreater(min(actual), min(observed), (result_root, criterion))
                self.assertLess(max(actual), max(observed), (result_root, criterion))

                profile_rows = profile_by_criterion[criterion]
                sample_n = int(float(profile_rows[0]["N"]))
                one_percent = max(1, math.ceil(0.01 * sample_n))
                self.assertLessEqual(
                    min(int(float(row["N_low"])) for row in profile_rows),
                    one_percent,
                    (result_root, criterion),
                )
                self.assertLessEqual(
                    min(int(float(row["N_high"])) for row in profile_rows),
                    one_percent,
                    (result_root, criterion),
                )

    def test_both_powershell_entry_points_parse(self) -> None:
        for script in (
            ROOT / "paperB/run_workflow.ps1",
            ROOT / "paperB/run_robustness.ps1",
            ROOT / "paperB_debt_lag/run_workflow.ps1",
            ROOT / "paperB_debt_lag/run_robustness.ps1",
        ):
            command = (
                "$errors=$null; "
                f"[System.Management.Automation.Language.Parser]::ParseFile('{script}',"
                "[ref]$null,[ref]$errors) | Out-Null; "
                "if($errors.Count -gt 0){$errors | ForEach-Object {$_.Message}; exit 1}"
            )
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(0, completed.returncode, f"{script}: {completed.stdout}{completed.stderr}")

    def test_each_pipeline_owns_a_complete_result_root(self) -> None:
        required = (
            Path("baseline/stata_outputs/model_coefficients.csv"),
            Path("empirical_theta/stata_outputs/empirical_theta_panel.csv"),
            Path("doomloop/stata_outputs/doomloop_nostate_panel.csv"),
            Path("figures/figure1a_theta_distribution_cutoff.png"),
            Path("figures/figure3_standardized_rss_profiles.png"),
            Path("figures/figure3_standardized_rss_profiles.pdf"),
            Path("paperB_results.md"),
            Path("paperB_diagnostics.md"),
            Path("progress.md"),
        )
        for result_root in (CURRENT, LAGGED):
            for relative in required:
                artifact = result_root / relative
                self.assertTrue(artifact.is_file(), artifact)
                self.assertGreater(artifact.stat().st_size, 0, artifact)

    def test_current_and_lagged_debt_states_follow_exact_timing(self) -> None:
        current_panel = rows(
            CURRENT / "empirical_theta/stata_outputs/empirical_theta_panel.csv"
        )
        lagged_panel = rows(
            LAGGED / "empirical_theta/stata_outputs/empirical_theta_panel.csv"
        )
        current_by_key = {(row["iso3"], int(row["year"])): row for row in current_panel}
        lagged_by_key = {(row["iso3"], int(row["year"])): row for row in lagged_panel}
        self.assertEqual(set(current_by_key), set(lagged_by_key))

        for key, row in current_by_key.items():
            if present(row["debt_gdp"]):
                self.assertTrue(present(row["b_it"]), key)
                self.assertTrue(
                    math.isclose(
                        float(row["b_it"]),
                        float(row["debt_gdp"]),
                        rel_tol=0,
                        abs_tol=1e-12,
                    ),
                    key,
                )

        for (iso3, year), row in lagged_by_key.items():
            prior = lagged_by_key.get((iso3, year - 1))
            expected = None if prior is None else prior["debt_gdp"]
            if prior is None or not present(expected):
                self.assertFalse(present(row["b_pre"]), (iso3, year))
            else:
                self.assertTrue(present(row["b_pre"]), (iso3, year))
                self.assertTrue(
                    math.isclose(
                        float(row["b_pre"]),
                        float(expected),
                        rel_tol=0,
                        abs_tol=1e-12,
                    ),
                    (iso3, year),
                )

    def test_lagged_mirror_labels_centered_debt_at_t_minus_one(self) -> None:
        results = (LAGGED / "paperB_results.md").read_text(encoding="utf-8")
        workflow = (ROOT / "paperB_debt_lag/WORKFLOW.md").read_text(encoding="utf-8")
        theta_source = (ROOT / "paperB_debt_lag/code/empirical_theta.do").read_text(
            encoding="utf-8"
        )
        self.assertIn(r"$b^c_{i,t-1}$", results)
        self.assertNotIn(r"$b^c_{it}$", results)
        self.assertIn(r"b^c_{i,t-1}", workflow)
        self.assertIn("Lagged debt/GDP ratio times marginal spread-ratio relief", theta_source)
        self.assertNotIn("bad_b_pre_current_mapping_rows", theta_source)

    def test_lagged_stepwise_tables_use_common_controls_without_duplicates(self) -> None:
        baseline_rows = rows(
            LAGGED / "baseline/stata_outputs/model_coefficients.csv"
        )
        baseline_variables: dict[str, set[str]] = {}
        for row in baseline_rows:
            baseline_variables.setdefault(row["model"], set()).add(row["variable"])

        expected_baseline_models = {
            "A_b_only",
            "A_X_only",
            "A_A_only",
            "Layer2_A",
            "Interact_AB",
            "Interact_AX",
            "Interact_all",
        }
        self.assertEqual(expected_baseline_models, set(baseline_variables))
        common_baseline_controls = {"growth", "inflation_cpi", "reserves", "tt"}
        for model, variables in baseline_variables.items():
            self.assertTrue(common_baseline_controls <= variables, model)
            debt_term = "c_b" if model.startswith("Interact_") else "b_pre"
            self.assertIn(debt_term, variables, model)

        tax_rows = rows(
            LAGGED / "empirical_theta/stata_outputs/model_coefficients.csv"
        )
        tax_variables: dict[str, set[str]] = {}
        for row in tax_rows:
            if row["model"].startswith("T"):
                tax_variables.setdefault(row["model"], set()).add(row["variable"])

        expected_tax_models = {
            "T3_persistence",
            "T1_X_only",
            "T2_A_only",
            "T7_layer2_A",
            "T10_interact_full",
        }
        self.assertEqual(expected_tax_models, set(tax_variables))
        common_tax_controls = {"inflation_cpi", "reserves", "tt"}
        for model, variables in tax_variables.items():
            self.assertTrue(common_tax_controls <= variables, model)
        signatures = {
            frozenset(variables - {"T_it"}) for variables in tax_variables.values()
        }
        self.assertEqual(len(expected_tax_models), len(signatures))

        results = (LAGGED / "paperB_results.md").read_text(encoding="utf-8")
        section_2 = results.split("### 2.2 逐步回归表", 1)[1].split(
            "### 2.3", 1
        )[0]
        self.assertIn("Panel A", section_2)
        self.assertIn("Panel B", section_2)
        section_3 = results.split("### 3.2 T 指标逐步回归表", 1)[1].split(
            "### 3.3", 1
        )[0]
        self.assertNotIn("Panel A", section_3)
        self.assertNotIn("Panel B", section_3)

    def test_core_renderer_does_not_require_robustness_outputs(self) -> None:
        renderer_path = ROOT / "paperB/render_output.py"
        spec = importlib.util.spec_from_file_location("paperb_render_output_test", renderer_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            module.ROBUST = Path(temporary) / "missing-robustness"
            module.INCLUDE_ROBUSTNESS = False
            module.validate_inputs(include_robustness=False)
            rendered = module.render_results()
        self.assertNotIn("债务时点稳健性与全管线诊断", rendered)
        self.assertIn("结果解释边界", rendered)

    def test_bootstrap_workflow_accepts_and_reports_failed_replications(self) -> None:
        workflow = (ROOT / "paperB/run_robustness.ps1").read_text(encoding="utf-8")
        renderer = (ROOT / "paperB/render_output.py").read_text(encoding="utf-8")
        self.assertNotIn("Where-Object status -ne 'success'", workflow)
        self.assertNotIn("30 次均成功", renderer)
        self.assertIn("failed_reps", renderer)

    def test_common_742_interpretation_is_limited_to_final_stage_sample(self) -> None:
        renderer = (ROOT / "paperB/render_output.py").read_text(encoding="utf-8")
        self.assertNotIn("不是由额外两条当期债务观测造成", renderer)
        self.assertIn("未在共同 742 样本上重估上游", renderer)

    def test_standardized_rss_profile_has_correct_algebra(self) -> None:
        profile = rows(CURRENT / "robustness/standardized_rss_profile.csv")
        self.assertGreater(len(profile), 0)
        for specification in ("current_debt", "lagged_debt"):
            group = [row for row in profile if row["specification"] == specification]
            self.assertGreater(len(group), 0, specification)
            min_rss = min(float(row["rss"]) for row in group)
            self.assertGreater(min_rss, 0)
            for row in group:
                expected_index = float(row["rss"]) / min_rss
                self.assertTrue(
                    math.isclose(
                        float(row["rss_index"]),
                        expected_index,
                        rel_tol=1e-10,
                        abs_tol=1e-12,
                    ),
                    row,
                )
                self.assertTrue(
                    math.isclose(
                        float(row["rss_excess_pct"]),
                        100 * (expected_index - 1),
                        rel_tol=1e-10,
                        abs_tol=1e-12,
                    ),
                    row,
                )

    def test_cross_cutoff_table_contains_the_four_fixed_combinations(self) -> None:
        comparison = rows(CURRENT / "robustness/cross_cutoff_sensitivity.csv")
        keys = {(row["theta_specification"], row["cutoff_source"]) for row in comparison}
        expected = {
            ("current_debt", "current_debt"),
            ("current_debt", "lagged_debt"),
            ("lagged_debt", "current_debt"),
            ("lagged_debt", "lagged_debt"),
        }
        self.assertEqual(expected, keys)
        self.assertEqual(4, len(comparison))

    def test_common_sample_comparison_is_exactly_742_unique_rows(self) -> None:
        comparison = rows(CURRENT / "robustness/common_742_specification.csv")
        self.assertEqual({"current_debt", "lagged_debt"}, {row["specification"] for row in comparison})
        self.assertEqual(2, len(comparison))
        self.assertEqual({742}, {int(float(row["N"])) for row in comparison})
        audit = rows(CURRENT / "robustness/common_742_keys.csv")
        keys = {(row["iso3"], row["year"]) for row in audit}
        self.assertEqual(742, len(audit))
        self.assertEqual(742, len(keys))

    def test_country_bootstrap_is_paired_for_all_30_replications(self) -> None:
        draws = rows(CURRENT / "robustness/country_bootstrap_draw_assignments.csv")
        replications = rows(CURRENT / "robustness/country_bootstrap_replications.csv")
        expected_reps = set(range(1, 31))
        self.assertEqual(expected_reps, {int(row["replicate"]) for row in draws})
        by_specification: dict[str, set[int]] = {}
        for row in replications:
            by_specification.setdefault(row["specification"], set()).add(
                int(row["replicate"])
            )
        self.assertEqual(expected_reps, by_specification["current_debt"])
        self.assertEqual(expected_reps, by_specification["lagged_debt"])
        self.assertEqual(60, len(replications))

        lagged_draws = rows(
            LAGGED / "robustness/country_bootstrap_draw_assignments.csv"
        )
        lagged_replications = rows(
            LAGGED / "robustness/country_bootstrap_replications.csv"
        )
        current_keys = {
            (row["replicate"], row["draw_slot"], row["source_iso3"])
            for row in draws
        }
        lagged_keys = {
            (row["replicate"], row["draw_slot"], row["source_iso3"])
            for row in lagged_draws
        }
        self.assertEqual(current_keys, lagged_keys)
        self.assertEqual(replications, lagged_replications)

    def test_country_bootstrap_summary_uses_valid_replications_as_denominator(self) -> None:
        summary = rows(CURRENT / "robustness/country_bootstrap_summary.csv")
        replications = rows(CURRENT / "robustness/country_bootstrap_replications.csv")
        self.assertEqual({"current_debt", "lagged_debt"}, {row["specification"] for row in summary})
        self.assertEqual(2, len(summary))
        for row in summary:
            for field in (
                "min_branch_share_median",
                "share_min_branch_below_10pct",
                "share_min_branch_le_5_obs",
            ):
                self.assertIn(field, row)
            requested = int(row["requested_reps"])
            valid = int(row["valid_reps"])
            failed = int(row["failed_reps"])
            self.assertEqual(30, requested)
            self.assertEqual(requested, valid + failed)
            self.assertGreater(valid, 0)
            for field in ("share_beta_L_positive", "share_beta_H_negative", "share_both_theoretical"):
                value = float(row[field])
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 1)

            valid = [
                replication
                for replication in replications
                if replication["specification"] == row["specification"]
                and replication["status"] == "success"
            ]
            min_branch_shares = sorted(
                min(float(replication["N_low"]), float(replication["N_high"]))
                / float(replication["N"])
                for replication in valid
            )
            expected_below_ten = sum(value < 0.10 for value in min_branch_shares) / len(valid)
            expected_at_most_five = sum(
                min(float(replication["N_low"]), float(replication["N_high"])) <= 5
                for replication in valid
            ) / len(valid)
            self.assertTrue(
                math.isclose(
                    float(row["min_branch_share_median"]),
                    (min_branch_shares[14] + min_branch_shares[15]) / 2,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ),
                row,
            )
            self.assertTrue(
                math.isclose(
                    float(row["share_min_branch_below_10pct"]),
                    expected_below_ten,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ),
                row,
            )
            self.assertTrue(
                math.isclose(
                    float(row["share_min_branch_le_5_obs"]),
                    expected_at_most_five,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ),
                row,
            )


if __name__ == "__main__":
    unittest.main()
