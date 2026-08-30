from __future__ import annotations

import argparse
import csv
import math
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path


PAGE_SINGLE = (4.8, 4.8)
PAGE_HORIZONTAL = (9.6, 4.8)
PAGE_VERTICAL = (4.8, 9.6)
AXIS_SIZE = 3.35
THETA_TICKS = r"xtick={-0.05,0,0.05,0.10,0.15,0.20},xticklabels={-0.05,0,0.05,0.10,0.15,0.20}"
MARGINAL_Y_TICKS = r"ytick={-0.20,-0.10,0,0.10,0.20,0.30},yticklabels={-0.20,-0.10,0,0.10,0.20,0.30}"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: float) -> str:
    if abs(value) < 5e-13:
        return "0"
    return f"{value:.12g}"


def coordinates(points: list[tuple[float, float]]) -> str:
    return " ".join(f"({number(x)},{number(y)})" for x, y in points)


def polygon_coordinates(
    x: list[float], upper: list[float], lower: list[float]
) -> str:
    points = list(zip(x, upper)) + list(zip(reversed(x), reversed(lower)))
    return coordinates(points)


def axis_at(x: float, y: float, options: str, plots: str) -> str:
    common = rf"""
        width={AXIS_SIZE}in,
        height={AXIS_SIZE}in,
        scale only axis,
        axis lines=left,
        tick align=outside,
        tick style={{papergray,line width=0.45pt}},
        axis line style={{papergray,line width=0.55pt}},
        label style={{font=\small}},
        tick label style={{font=\footnotesize}},
        every axis plot/.append style={{line join=round,line cap=round}},
        clip=true,
        at={{({x}in,{y}in)}},
        anchor=south west,
        {options}
    """
    common = " ".join(line.strip() for line in common.splitlines() if line.strip())
    return rf"\begin{{axis}}[{common}]{plots}\end{{axis}}"


def document(page: tuple[float, float], axes: str) -> str:
    width, height = page
    return rf"""
\documentclass{{article}}
\usepackage[paperwidth={width}in,paperheight={height}in,margin=0in]{{geometry}}
\usepackage{{newtxtext,newtxmath}}
\usepackage{{pgfplots}}
\usetikzlibrary{{calc}}
\pgfplotsset{{compat=1.18}}
\definecolor{{paperbluedark}}{{HTML}}{{1F4E79}}
\definecolor{{paperblue}}{{HTML}}{{5B9BD5}}
\definecolor{{paperbluelight}}{{HTML}}{{DCE6F1}}
\definecolor{{papergray}}{{HTML}}{{4B5563}}
\pagestyle{{empty}}
\setlength{{\parindent}}{{0pt}}
\begin{{document}}
\begin{{tikzpicture}}[remember picture,overlay]
\begin{{scope}}[shift={{(current page.south west)}}]
{axes}
\end{{scope}}
\end{{tikzpicture}}
\end{{document}}
"""


def kde(values: list[float], points: int = 241) -> list[tuple[float, float]]:
    n = len(values)
    stdev = statistics.stdev(values)
    bandwidth = 1.06 * stdev * n ** (-0.2)
    data_min = min(values)
    data_max = max(values)
    bandwidth = max(bandwidth, (data_max - data_min) / 100)
    start = data_min
    stop = data_max
    normalizer = n * bandwidth * math.sqrt(2 * math.pi)
    result: list[tuple[float, float]] = []
    for index in range(points):
        x = start + index * (stop - start) / (points - 1)
        density = sum(
            math.exp(-0.5 * ((x - value) / bandwidth) ** 2) for value in values
        ) / normalizer
        result.append((x, density))
    return result


def histogram_density(
    values: list[float], bins: int = 24
) -> list[tuple[float, float]]:
    start = min(values)
    stop = max(values)
    width = (stop - start) / bins
    counts = [0] * bins
    for value in values:
        index = min(int((value - start) / width), bins - 1)
        counts[index] += 1
    density = [count / (len(values) * width) for count in counts]
    return [(start + index * width, value) for index, value in enumerate(density)] + [
        (stop, density[-1])
    ]


def theta_documents(project_root: Path) -> dict[str, str]:
    output = project_root / "doomloop" / "stata_outputs"
    distribution = read_rows(output / "theta_distribution_cutoff_plot_data.csv")
    ranking = read_rows(output / "theta_country_rank_plot_data.csv")
    values = [float(row["theta_hat_A"]) for row in distribution]
    cutoff = float(distribution[0]["cutoff"])
    hist = histogram_density(values)
    density = kde(values)
    ymax = 1.06 * max(max(y for _, y in hist), max(y for _, y in density))

    distribution_plots = rf"""
        \addplot[ybar interval,fill=paperbluelight,draw=paperblue,line width=0.35pt]
            coordinates {{{coordinates(hist)}}};
        \addplot[paperbluedark,line width=0.9pt] coordinates {{{coordinates(density)}}};
        \addplot[papergray,densely dashed,line width=0.65pt]
            coordinates {{({number(cutoff)},0) ({number(cutoff)},{number(ymax)})}};
    """
    distribution_axis = axis_at(
        0.72,
        0.72,
        rf"""
            xmin=-0.06,xmax=0.22,ymin=0,ymax={number(ymax)},
            {THETA_TICKS}
        """,
        distribution_plots,
    )

    low = [
        (float(row["theta_mean"]), float(row["rank"]))
        for row in ranking
        if row["above_cutoff"] == "0"
    ]
    high = [
        (float(row["theta_mean"]), float(row["rank"]))
        for row in ranking
        if row["above_cutoff"] == "1"
    ]
    label_styles = {
        "Chile": "anchor=west,xshift=4pt",
        "Italy": "anchor=west,xshift=4pt",
        "Greece": "anchor=west,xshift=4pt",
        "Japan": "anchor=east,xshift=-4pt",
    }
    representative_nodes = []
    for row in ranking:
        label = row["country_label"].strip()
        if not label:
            continue
        representative_nodes.append(
            rf"\node[font=\footnotesize,text=paperbluedark,{label_styles[label]}] "
            rf"at (axis cs:{number(float(row['theta_mean']))},{number(float(row['rank']))}) "
            rf"{{{label}}};"
        )
    rank_plots = rf"""
        \addplot[only marks,mark=o,mark size=1.8pt,
            mark options={{draw=paperblue,fill=white,line width=0.65pt}}]
            coordinates {{{coordinates(low)}}};
        \addplot[only marks,mark=square*,mark size=1.7pt,
            mark options={{draw=paperbluedark,fill=paperbluedark,line width=0.45pt}}]
            coordinates {{{coordinates(high)}}};
        \addplot[papergray,densely dashed,line width=0.65pt]
            coordinates {{({number(cutoff)},0) ({number(cutoff)},51)}};
        {" ".join(representative_nodes)}
    """
    rank_axis = axis_at(
        0.72,
        0.72,
        rf"""
            xmin=-0.06,xmax=0.22,ymin=0,ymax=51,
            {THETA_TICKS},
            ytick={{0,10,20,30,40,50}}
        """,
        rank_plots,
    )
    return {
        "figure1a_theta_distribution_cutoff": document(
            PAGE_SINGLE, distribution_axis
        ),
        "figure1b_theta_country_rank_cutoff": document(PAGE_SINGLE, rank_axis),
    }


def asymmetric_error_coordinates(rows: list[dict[str, str]]) -> str:
    items: list[str] = []
    for row in sorted(rows, key=lambda item: int(float(item["percentile_order"]))):
        x = float(row["percentile_order"])
        y = float(row["mA"])
        upper = float(row["ci_high"]) - y
        lower = y - float(row["ci_low"])
        items.append(
            f"({number(x)},{number(y)}) += (0,{number(upper)}) -= (0,{number(lower)})"
        )
    return " ".join(items)


def figure_moderators(project_root: Path) -> str:
    rows = read_rows(
        project_root
        / "doomloop"
        / "stata_outputs"
        / "mA_by_debt_wsdi_plot_data.csv"
    )
    debt = [row for row in rows if row["moderator"] == "b_pre"]
    wsdi = [row for row in rows if row["moderator"] == "wsdi_days"]
    y_low = min(float(row["ci_low"]) for row in rows)
    y_high = max(float(row["ci_high"]) for row in rows)
    padding = 0.06 * (y_high - y_low)
    ymin = min(-0.05, y_low - padding)
    ymax = max(0.11, y_high + padding)

    def panel(panel_rows: list[dict[str, str]], x: float) -> str:
        plots = rf"""
            \addplot[papergray,dashdotted,line width=0.45pt]
                coordinates {{(0.75,0) (5.25,0)}};
            \addplot[paperbluedark,line width=0.8pt,mark=o,mark size=2.2pt,
                mark options={{draw=paperbluedark,fill=white,line width=0.65pt}},
                error bars/error bar style={{paperblue,line width=0.65pt}},
                error bars/.cd,y dir=both,y explicit]
                coordinates {{{asymmetric_error_coordinates(panel_rows)}}};
        """
        return axis_at(
            x,
            0.72,
            rf"""
                xmin=0.75,xmax=5.25,ymin={number(ymin)},ymax={number(ymax)},
                xtick={{1,2,3,4,5}},xticklabels={{P10,P25,P50,P75,P90}},
                ytick={{-0.05,0,0.05,0.10}},
                yticklabels={{-0.05,0,0.05,0.10}}
            """,
            plots,
        )

    left = panel(debt, 0.72)
    right = panel(wsdi, 5.52)
    return document(PAGE_HORIZONTAL, left + right)


def marginal_axis(
    rows: list[dict[str, str]],
    x: float,
    y: float,
) -> str:
    ordered = sorted(rows, key=lambda row: float(row["theta"]))
    theta = [float(row["theta"]) for row in ordered]
    effect = [float(row["marginal_effect"]) for row in ordered]
    lower = [float(row["ci_low"]) for row in ordered]
    upper = [float(row["ci_high"]) for row in ordered]
    cutoff = float(ordered[0]["cutoff"])
    plots = rf"""
        \addplot[fill=paperbluelight,draw=none]
            coordinates {{{polygon_coordinates(theta, upper, lower)}}} \closedcycle;
        \addplot[papergray,dashdotted,line width=0.45pt]
            coordinates {{(-0.05,0) (0.205,0)}};
        \addplot[papergray,densely dashed,line width=0.65pt]
            coordinates {{({number(cutoff)},-0.22) ({number(cutoff)},0.32)}};
        \addplot[paperbluedark,line width=0.9pt]
            coordinates {{{coordinates(list(zip(theta, effect)))}}};
    """
    return axis_at(
        x,
        y,
        rf"""
            xmin=-0.05,xmax=0.205,ymin=-0.22,ymax=0.32,
            {THETA_TICKS},
            {MARGINAL_Y_TICKS}
        """,
        plots,
    )


def marginal_documents(project_root: Path) -> dict[str, str]:
    output = project_root / "doomloop" / "stata_outputs"
    debt = read_rows(output / "nostate_marginal_curve_debt.csv")
    readiness = read_rows(
        output / "nostate_marginal_curve_ready_debt_cutoff.csv"
    )
    debt_axis = marginal_axis(debt, 0.72, 0.72)
    readiness_axis = marginal_axis(readiness, 0.72, 0.72)
    combined_debt = marginal_axis(debt, 0.72, 5.52)
    combined_readiness = marginal_axis(readiness, 0.72, 0.72)
    return {
        "debt_marginal_effect_no_b": document(PAGE_SINGLE, debt_axis),
        "readiness_marginal_effect_debt_cutoff_no_lag": document(
            PAGE_SINGLE, readiness_axis
        ),
        "kink_marginal_effects_no_state": document(
            PAGE_VERTICAL, combined_debt + combined_readiness
        ),
    }


def robustness_documents(project_root: Path) -> dict[str, str]:
    path = project_root / "robustness" / "standardized_rss_profile.csv"
    if not path.exists():
        return {}
    rows = read_rows(path)
    current = sorted(
        (
            (float(row["cutoff_z"]), float(row["rss_excess_pct"]))
            for row in rows
            if row["specification"] == "current_debt"
        ),
        key=lambda point: point[0],
    )
    lagged = sorted(
        (
            (float(row["cutoff_z"]), float(row["rss_excess_pct"]))
            for row in rows
            if row["specification"] == "lagged_debt"
        ),
        key=lambda point: point[0],
    )
    if not current or not lagged:
        raise ValueError("Standardized RSS profile must contain both debt specifications")
    xmin = min(x for x, _ in current + lagged)
    xmax = max(x for x, _ in current + lagged)
    ymax = max(y for _, y in current + lagged)
    ymax = max(0.5, math.ceil(ymax * 4) / 4)
    plots = rf"""
        \addplot[paperbluedark,line width=0.95pt]
            coordinates {{{coordinates(current)}}};
        \addplot[paperblue,densely dashed,line width=0.95pt]
            coordinates {{{coordinates(lagged)}}};
        \addplot[papergray,dashdotted,line width=0.45pt]
            coordinates {{({number(xmin)},0.1) ({number(xmax)},0.1)}};
        \addplot[papergray,dotted,line width=0.45pt]
            coordinates {{({number(xmin)},0.5) ({number(xmax)},0.5)}};
        \addplot[papergray,densely dashed,line width=0.45pt]
            coordinates {{({number(xmin)},1) ({number(xmax)},1)}};
    """
    axis = axis_at(
        0.72,
        0.72,
        rf"""
            xmin={number(xmin)},xmax={number(xmax)},ymin=0,ymax={number(ymax)},
            xtick={{-0.5,0,0.5,1}},
            ytick={{0,0.5,1,1.5,2}}
        """,
        plots,
    )
    return {"figure3_standardized_rss_profiles": document(PAGE_SINGLE, axis)}


def compile_figure(name: str, tex: str, output_dir: Path) -> None:
    lualatex = shutil.which("lualatex")
    pdftocairo = shutil.which("pdftocairo")
    if lualatex is None or pdftocairo is None:
        raise RuntimeError("lualatex and pdftocairo are required to render figures")

    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"paperb-{name}-") as temp_name:
        temp_dir = Path(temp_name)
        tex_path = temp_dir / f"{name}.tex"
        tex_path.write_text(tex, encoding="utf-8")
        command = [
            lualatex,
            "-halt-on-error",
            "-interaction=nonstopmode",
            "-output-directory",
            str(temp_dir),
            str(tex_path),
        ]
        for _ in range(2):
            completed = subprocess.run(
                command,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"TeX rendering failed for {name}:\n"
                    f"{completed.stdout}\n{completed.stderr}"
                )

        pdf_path = temp_dir / f"{name}.pdf"
        shutil.copy2(pdf_path, output_dir / f"{name}.pdf")
        raster = subprocess.run(
            [
                pdftocairo,
                "-png",
                "-singlefile",
                "-r",
                "300",
                str(pdf_path),
                str(output_dir / name),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if raster.returncode != 0:
            raise RuntimeError(
                f"PNG rendering failed for {name}:\n{raster.stdout}\n{raster.stderr}"
            )


def render_all(project_root: Path, output_dir: Path) -> None:
    figures = theta_documents(project_root)
    figures["figure2_mA_by_debt_wsdi"] = figure_moderators(project_root)
    figures.update(marginal_documents(project_root))
    figures.update(robustness_documents(project_root))
    for name, tex in figures.items():
        compile_figure(name, tex, output_dir)
    for suffix in (".pdf", ".png"):
        legacy = output_dir / f"figure1_theta_distribution_cutoff{suffix}"
        if legacy.exists():
            legacy.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render Paper B journal-style figures from validated CSV outputs."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else project_root / "doomloop" / "figures"
    )
    render_all(project_root, output_dir)


if __name__ == "__main__":
    main()
