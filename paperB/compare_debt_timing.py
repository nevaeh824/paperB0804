from __future__ import annotations

import argparse
import csv
import random
import shutil
import statistics
from pathlib import Path


SPECIFICATIONS = {
    "current_debt": ("paperB", "paperBresult"),
    "lagged_debt": ("paperB_debt_lag", "paperB_debt_lag"),
}
THRESHOLDS = (0.1, 0.5, 1.0)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fieldnames: list[str], data: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def result_roots(project_root: Path) -> dict[str, Path]:
    return {
        name: project_root / workflow / result
        for name, (workflow, result) in SPECIFICATIONS.items()
    }


def build_profiles(project_root: Path) -> None:
    roots = result_roots(project_root)
    profile_rows: list[dict[str, object]] = []
    interval_rows: list[dict[str, object]] = []
    for specification, root in roots.items():
        source_profile = [
            row
            for row in read_rows(
                root / "doomloop/stata_outputs/criterion_rss_profiles.csv"
            )
            if row["criterion"] == "theta"
        ]
        panel = read_rows(root / "doomloop/stata_outputs/doomloop_nostate_panel.csv")
        theta = [
            float(row["theta_hat_A"])
            for row in panel
            if row["sample_debt_ns"] == "1"
        ]
        center = statistics.median(theta)
        scale = statistics.stdev(theta)
        min_rss = min(float(row["rss"]) for row in source_profile)
        selected = min(source_profile, key=lambda row: float(row["rss"]))
        normalized: list[dict[str, object]] = []
        for row in source_profile:
            cutoff = float(row["cutoff"])
            rss = float(row["rss"])
            item = {
                "specification": specification,
                "cutoff": cutoff,
                "cutoff_z": (cutoff - center) / scale,
                "rss": rss,
                "rss_index": rss / min_rss,
                "rss_excess_pct": 100 * (rss / min_rss - 1),
                "selected": int(row is selected),
                "N": int(float(row["N"])),
                "N_low": int(float(row["N_low"])),
                "N_high": int(float(row["N_high"])),
            }
            normalized.append(item)
            profile_rows.append(item)
        for threshold in THRESHOLDS:
            accepted = [
                row for row in normalized if float(row["rss_excess_pct"]) <= threshold + 1e-12
            ]
            interval_rows.append(
                {
                    "specification": specification,
                    "rss_excess_threshold_pct": threshold,
                    "selected_cutoff": float(selected["cutoff"]),
                    "cutoff_low": min(float(row["cutoff"]) for row in accepted),
                    "cutoff_high": max(float(row["cutoff"]) for row in accepted),
                    "cutoff_z_low": min(float(row["cutoff_z"]) for row in accepted),
                    "cutoff_z_high": max(float(row["cutoff_z"]) for row in accepted),
                    "accepted_candidates": len(accepted),
                    "total_candidates": len(normalized),
                    "accepted_share": len(accepted) / len(normalized),
                }
            )

    robust = roots["current_debt"] / "robustness"
    write_rows(
        robust / "standardized_rss_profile.csv",
        [
            "specification",
            "cutoff",
            "cutoff_z",
            "rss",
            "rss_index",
            "rss_excess_pct",
            "selected",
            "N",
            "N_low",
            "N_high",
        ],
        profile_rows,
    )
    write_rows(
        robust / "near_optimal_cutoff_intervals.csv",
        [
            "specification",
            "rss_excess_threshold_pct",
            "selected_cutoff",
            "cutoff_low",
            "cutoff_high",
            "cutoff_z_low",
            "cutoff_z_high",
            "accepted_candidates",
            "total_candidates",
            "accepted_share",
        ],
        interval_rows,
    )


def build_draws(project_root: Path, reps: int = 30, seed: int = 20260830) -> None:
    source = read_rows(project_root / "data0804/invest_panel_weo.csv")
    countries = sorted({row["iso3"] for row in source if row["iso3"]})
    generator = random.Random(seed)
    assignments: list[dict[str, object]] = []
    for replicate in range(1, reps + 1):
        for draw_slot in range(1, len(countries) + 1):
            assignments.append(
                {
                    "replicate": replicate,
                    "draw_slot": draw_slot,
                    "source_iso3": generator.choice(countries),
                    "seed": seed,
                    "country_count": len(countries),
                }
            )
    roots = result_roots(project_root)
    fields = ["replicate", "draw_slot", "source_iso3", "seed", "country_count"]
    for root in roots.values():
        write_rows(
            root / "robustness/country_bootstrap_draw_assignments.csv",
            fields,
            assignments,
        )


def copy_comparison_outputs(project_root: Path) -> None:
    roots = result_roots(project_root)
    source = roots["current_debt"] / "robustness"
    target = roots["lagged_debt"] / "robustness"
    target.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        if path.is_file():
            shutil.copy2(path, target / path.name)


def summarize_bootstrap(project_root: Path) -> None:
    roots = result_roots(project_root)
    robust = roots["current_debt"] / "robustness"
    replications = read_rows(robust / "country_bootstrap_replications.csv")
    summary: list[dict[str, object]] = []
    for specification in ("current_debt", "lagged_debt"):
        group = [row for row in replications if row["specification"] == specification]
        if len(group) != 30 or {int(row["replicate"]) for row in group} != set(range(1, 31)):
            raise ValueError(f"Bootstrap replication coverage is incomplete for {specification}")
        valid = [row for row in group if row["status"] == "success"]
        if not valid:
            raise ValueError(f"No valid bootstrap replications for {specification}")
        cutoffs = [float(row["cutoff"]) for row in valid]
        quartiles = statistics.quantiles(cutoffs, n=4, method="inclusive")
        beta_l = [float(row["beta_L"]) for row in valid]
        beta_h = [float(row["beta_H"]) for row in valid]
        min_branch_counts = [
            min(float(row["N_low"]), float(row["N_high"])) for row in valid
        ]
        min_branch_shares = [
            count / float(row["N"])
            for count, row in zip(min_branch_counts, valid)
        ]
        summary.append(
            {
                "specification": specification,
                "requested_reps": 30,
                "valid_reps": len(valid),
                "failed_reps": 30 - len(valid),
                "cutoff_min": min(cutoffs),
                "cutoff_p25": quartiles[0],
                "cutoff_median": statistics.median(cutoffs),
                "cutoff_p75": quartiles[2],
                "cutoff_max": max(cutoffs),
                "share_beta_L_positive": sum(value > 0 for value in beta_l) / len(valid),
                "share_beta_H_negative": sum(value < 0 for value in beta_h) / len(valid),
                "share_both_theoretical": sum(
                    left > 0 and right < 0 for left, right in zip(beta_l, beta_h)
                )
                / len(valid),
                "min_branch_share_median": statistics.median(min_branch_shares),
                "share_min_branch_below_10pct": sum(
                    value < 0.10 for value in min_branch_shares
                )
                / len(valid),
                "share_min_branch_le_5_obs": sum(
                    value <= 5 for value in min_branch_counts
                )
                / len(valid),
                "seed": 20260830,
                "bootstrap_unit": "country block",
                "nested_lsdvc_vce_reps": 0,
                "interpretation": "compact stability diagnostic; not a formal confidence interval",
            }
        )
    write_rows(
        robust / "country_bootstrap_summary.csv",
        [
            "specification",
            "requested_reps",
            "valid_reps",
            "failed_reps",
            "cutoff_min",
            "cutoff_p25",
            "cutoff_median",
            "cutoff_p75",
            "cutoff_max",
            "share_beta_L_positive",
            "share_beta_H_negative",
            "share_both_theoretical",
            "min_branch_share_median",
            "share_min_branch_below_10pct",
            "share_min_branch_le_5_obs",
            "seed",
            "bootstrap_unit",
            "nested_lsdvc_vce_reps",
            "interpretation",
        ],
        summary,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and reconcile Paper B debt-timing robustness outputs.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--stage", choices=("prepare", "summarize", "copy"), required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    if args.stage == "prepare":
        build_profiles(project_root)
        build_draws(project_root)
    elif args.stage == "summarize":
        summarize_bootstrap(project_root)
    else:
        copy_comparison_outputs(project_root)


if __name__ == "__main__":
    main()
