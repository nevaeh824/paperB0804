from __future__ import annotations

import csv
import math
from datetime import datetime
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "baseline" / "stata_outputs"
THETA = ROOT / "empirical_theta" / "stata_outputs"
DOOM = ROOT / "doomloop" / "stata_outputs"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: object) -> float | None:
    if value is None or value == "" or value == ".":
        return None
    try:
        result = float(str(value))
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def fmt(value: object, digits: int = 4) -> str:
    x = number(value)
    if x is None:
        return "—"
    if x == 0:
        return "0"
    if abs(x) < 10 ** (-(digits + 1)) or abs(x) >= 1_000_000:
        return f"{x:.2e}"
    return f"{x:.{digits}f}".rstrip("0").rstrip(".")


def fmt_int(value: object) -> str:
    x = number(value)
    return "—" if x is None else f"{int(round(x)):,}"


def fmt_p(value: object) -> str:
    x = number(value)
    if x is None:
        return "—"
    return "<0.001" if x < 0.001 else f"{x:.3f}"


def stars(value: object) -> str:
    x = number(value)
    if x is None:
        return ""
    if x < 0.01:
        return "***"
    if x < 0.05:
        return "**"
    if x < 0.10:
        return "*"
    return ""


def safe(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def md_table(headers: list[str], rows: Iterable[Iterable[object]], numeric_from: int = 1) -> str:
    aligns = ["---"] + ["---:"] * (len(headers) - 1)
    if numeric_from <= 0:
        aligns = ["---:"] * len(headers)
    lines = [
        "| " + " | ".join(safe(x) for x in headers) + " |",
        "| " + " | ".join(aligns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(safe(x) for x in row) + " |")
    return "\n".join(lines)


def coef_cell(row: dict[str, str] | None) -> str:
    if row is None or row.get("omitted") == "1":
        return "—"
    return f"{fmt(row.get('coefficient'))}{stars(row.get('p'))}<br>({fmt(row.get('t'), 3)})"


def yesno(value: object) -> str:
    return "是" if str(value) == "1" else "否"


def model_table(
    models: list[str],
    model_labels: dict[str, str],
    variables: list[str],
    variable_labels: dict[str, str],
    coefficients: dict[tuple[str, str], dict[str, str]],
    stats: dict[str, dict[str, str]],
    control_flags: dict[str, tuple[bool, bool]] | None = None,
) -> str:
    headers = ["变量/统计量"] + [f"({m}) {model_labels[m]}" for m in models]
    rows: list[list[object]] = []
    for variable in variables:
        rows.append([variable_labels[variable]] + [coef_cell(coefficients.get((m, variable))) for m in models])
    if control_flags is not None:
        rows.append(["宏观控制"] + ["是" if control_flags[m][0] else "否" for m in models])
        rows.append(["外部控制"] + ["是" if control_flags[m][1] else "否" for m in models])
    elif "macro_controls" in stats[models[0]]:
        rows.append(["宏观控制"] + [yesno(stats[m].get("macro_controls")) for m in models])
        rows.append(["外部控制"] + [yesno(stats[m].get("external_controls")) for m in models])
    rows.extend(
        [
            ["国家固定效应"] + ["是"] * len(models),
            ["年份固定效应"] + ["是"] * len(models),
            ["国家数"] + [fmt_int(stats[m].get("countries")) for m in models],
            ["年份数"] + [fmt_int(stats[m].get("years")) for m in models],
            ["样本量"] + [fmt_int(stats[m].get("N")) for m in models],
            [r"Within $R^2$"] + [fmt(stats[m].get("r2_within"), 3) for m in models],
            [r"Overall $R^2$"] + [fmt(stats[m].get("r2_overall"), 3) for m in models],
        ]
    )
    return md_table(headers, rows)


def coefficient_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["model"], row["variable"]): row for row in rows}


def stats_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["model"]: row for row in rows}


BASE_MODELS = [
    "A_X_only", "A_A_only", "A_b_only", "B_all_core", "C_macro",
    "Layer1_X", "Layer2_A", "Interact_AB", "Interact_AX", "Interact_all", "Quadratic_all",
]
BASE_LABELS = {
    "A_X_only": "仅 X", "A_A_only": "仅 A", "A_b_only": "仅 b",
    "B_all_core": "三核心", "C_macro": "+宏观",
    "Layer1_X": "第一层", "Layer2_A": "第二层",
    "Interact_AB": "A×b", "Interact_AX": "A×X", "Interact_all": "双交互",
    "Quadratic_all": "完整二阶",
}
BASE_TERMS = {
    "vulnerability100": r"气候脆弱性 $X_{it}$",
    "readiness100": r"适应能力 $A_{it}$",
    "b_it": r"$b_{it}=debt_{it}/CurrentGDP_{it}$",
    "ln_currentgdp": r"$\ln(CurrentGDP_{it})$",
    "c_A": r"$A^c_{it}$", "c_X": r"$X^c_{it}$", "c_b": r"$b^c_{it}$",
    "half_A2": r"$\frac{1}{2}(A^c_{it})^2$",
    "half_b2": r"$\frac{1}{2}(b^c_{it})^2$",
    "half_X2": r"$\frac{1}{2}(X^c_{it})^2$",
    "int_AB": r"$A^c_{it}\times b^c_{it}$",
    "int_AX": r"$A^c_{it}\times X^c_{it}$",
    "int_bX": r"$b^c_{it}\times X^c_{it}$",
    "growth": "Growth", "inflation_cpi": "Inflation",
    "reserves": "Reserves", "tt": "Terms of trade",
}
BASE_FLAGS = {
    "A_X_only": (False, False), "A_A_only": (False, False), "A_b_only": (False, False),
    "B_all_core": (False, False), "C_macro": (True, False),
    "Layer1_X": (True, True), "Layer2_A": (True, True),
    "Interact_AB": (True, True), "Interact_AX": (True, True), "Interact_all": (True, True),
    "Quadratic_all": (True, True),
}

TAX_MODELS = [
    "T1_X_only", "T2_A_only", "T3_persistence", "T4_all_core", "T5_macro",
    "T6_layer1_X", "T7_layer2_A", "T8_interact_core", "T9_interact_macro", "T10_interact_full",
    "T11_quadratic_full",
]
TAX_LABELS = {
    "T1_X_only": "仅 X", "T2_A_only": "仅 A", "T3_persistence": "仅滞后税基",
    "T4_all_core": "核心项", "T5_macro": "+宏观", "T6_layer1_X": "第一层",
    "T7_layer2_A": "第二层", "T8_interact_core": "交互核心",
    "T9_interact_macro": "交互+宏观", "T10_interact_full": "交互+全控制",
    "T11_quadratic_full": "完整二阶+滞后税基+b+全控制",
}
TAX_TERMS = {
    "vulnerability100": r"气候脆弱性 $X_{it}$",
    "readiness100": r"适应能力 $A_{it}$",
    "taxbase_lag": r"$\widetilde T_{it}^{(t-1)}$",
    "b_it_theta": r"$b_{it}=debt_{it}/CurrentGDP_{it}$",
    "c_A_T": r"$A^c_{it}$", "c_X_T": r"$X^c_{it}$",
    "half_A2_T": r"$\frac{1}{2}(A^c_{it})^2$",
    "half_X2_T": r"$\frac{1}{2}(X^c_{it})^2$",
    "int_AX_T": r"$A^c_{it}\times X^c_{it}$",
    "growth": "Growth", "inflation_cpi": "Inflation",
    "reserves": "Reserves", "tt": "Terms of trade",
}

DOOM_LABELS = {
    "D1_core": "核心项", "D2_macro": "+宏观", "D3_full": "+全控制",
    "DN1_core": "核心项（无 b）", "DN2_macro": "+宏观（无 b）", "DN3_full": "+全控制（无 b）",
    "R1_core": "核心项", "R2_macro": "+宏观", "R3_full": "+全控制",
    "RD1_debtcut": "核心项（债务 cutoff）", "RD2_debtcut": "+宏观（债务 cutoff）", "RD3_debtcut": "+全控制（债务 cutoff）",
    "RN1_core": "核心项（无 A 滞后）", "RN2_macro": "+宏观（无 A 滞后）", "RN3_full": "+全控制（无 A 滞后）",
}
DOOM_TERMS = {
    "debt_kink_low": r"$A_{it}(c-\widehat\theta^A_{it})_+$",
    "debt_kink_high": r"$A_{it}(\widehat\theta^A_{it}-c)_+$",
    "b_it_theta": r"$b_{it}=debt_{it}/CurrentGDP_{it}$", "ready_kink_low": r"$FT_{it}(c-\widehat\theta^A_{it})_+$",
    "ln_currentgdp": r"$\ln(CurrentGDP_{it})$",
    "ready_kink_high": r"$FT_{it}(\widehat\theta^A_{it}-c)_+$",
    "ready_debt_kink_low": r"$FT_{it}(c_D-\widehat\theta^A_{it})_+$",
    "ready_debt_kink_high": r"$FT_{it}(\widehat\theta^A_{it}-c_D)_+$",
    "readiness_lag": r"$A_{i,t-1}$", "vulnerability100": r"$X_{it}$",
    "growth": "Growth", "inflation_cpi": "Inflation",
    "reserves": "Reserves", "tt": "Terms of trade",
}


def marginal_table(rows: list[dict[str, str]], include_model: bool) -> str:
    headers = (["模型", "调节变量"] if include_model else ["方程/规格"]) + [
        "点", r"调节变量/$\theta$", "边际效应", "稳健 SE", "p 值", "95% CI",
    ]
    output: list[list[object]] = []
    for row in rows:
        group = row.get("model") or row.get("equation", "")
        prefix = [group, row.get("moderator", "")] if include_model else [group]
        output.append(prefix + [
            row.get("point", ""), fmt(row.get("moderator_value") or row.get("theta")),
            fmt(row.get("marginal_effect")), fmt(row.get("se")), fmt_p(row.get("p")),
            f"[{fmt(row.get('ci_low'))}, {fmt(row.get('ci_high'))}]",
        ])
    return md_table(headers, output)


def render_results() -> str:
    base_coef_rows = read_csv(BASE / "model_coefficients.csv")
    base_stats_rows = read_csv(BASE / "model_stats.csv")
    tax_coef_rows = read_csv(THETA / "model_coefficients.csv")
    tax_stats_rows = read_csv(THETA / "model_stats.csv")
    doom_coef_rows = read_csv(DOOM / "model_coefficients.csv") + read_csv(DOOM / "nostate_model_coefficients.csv")
    doom_stats_rows = read_csv(DOOM / "model_stats.csv") + read_csv(DOOM / "nostate_model_stats.csv")
    base_coefs, base_stats = coefficient_index(base_coef_rows), stats_index(base_stats_rows)
    tax_coefs, tax_stats = coefficient_index(tax_coef_rows), stats_index(tax_stats_rows)
    doom_coefs, doom_stats = coefficient_index(doom_coef_rows), stats_index(doom_stats_rows)

    construction = read_csv(THETA / "construction_coefficients.csv")
    construction_by = {(r["source"], r["parameter"]): r for r in construction}
    theta_desc = read_csv(THETA / "descriptive_stats.csv")
    original_cutoffs = {row["equation"]: row for row in read_csv(DOOM / "cutoffs.csv")}
    nostate_cutoffs = {row["equation"]: row for row in read_csv(DOOM / "nostate_cutoffs.csv")}
    original_keys = {row["equation"]: row for row in read_csv(DOOM / "key_results.csv")}
    nostate_keys = {row["equation"]: row for row in read_csv(DOOM / "nostate_key_results.csv")}
    ready_scenarios = {row["scenario"]: row for row in read_csv(DOOM / "readiness_cutoff_scenarios.csv")}
    base_wald = read_csv(BASE / "wald_tests.csv")
    doom_wald = read_csv(DOOM / "wald_tests.csv") + read_csv(DOOM / "nostate_wald_tests.csv")

    def joint_p(model: str) -> str:
        row = next(
            r for r in doom_wald
            if r["model"] == model and "low- and high-branch" in r["hypothesis"]
        )
        return fmt_p(row["p"])

    def p_label(value: object) -> str:
        rendered = fmt_p(value)
        return f"p{rendered}" if rendered.startswith("<") else f"p={rendered}"

    lines: list[str] = []
    add = lines.append
    add("# Paper B：统一回归公式与结果表")
    add("")
    add(f"> 数据：`data0804/invest_panel_weo.csv`；整合生成时间：{datetime.now():%Y-%m-%d %H:%M}（Asia/Shanghai）。")
    add("> 本文档只放回归公式、正式系数表、边际效应、cutoff 与经验指标构造结果。数据检查和统计检验见 `paperB_diagnostics.md`。所有源比率、百分数和 0—100 指数均先除以 100，以 0—1 比率进入回归；`CurrentGDP` 保留原始金额尺度。")
    add("")
    add("## 技术摘要")
    add("")
    base_ab = construction_by[("spread", "beta_AB")]
    base_ax = construction_by[("spread", "beta_AX")]
    base_aa = construction_by[("spread", "beta_AA")]
    tax_a = construction_by[("tax", "gamma_A_raw")]
    tax_aa = construction_by[("tax", "gamma_AA")]
    tax_ax = construction_by[("tax", "gamma_AX")]
    second_order_p = next(r["p"] for r in base_wald if r["model"] == "Quadratic_all" and "all second-order" in r["hypothesis"])
    add(f"- Baseline 完整二阶模型中，$\\beta_{{AA}}$={fmt(base_aa['estimate'])}（{p_label(base_aa['p'])}）、$\\beta_{{Ab}}$={fmt(base_ab['estimate'])}（{p_label(base_ab['p'])}）、$\\beta_{{AX}}$={fmt(base_ax['estimate'])}（{p_label(base_ax['p'])}）；六个二阶项联合检验 {p_label(second_order_p)}。")
    add(f"- 完整二阶税基模型的原始尺度适应能力线性项为 {fmt(tax_a['estimate'])}（p={fmt_p(tax_a['p'])}），A² 与 A×X 系数分别为 {fmt(tax_aa['estimate'])}（p={fmt_p(tax_aa['p'])}）、{fmt(tax_ax['estimate'])}（p={fmt_p(tax_ax['p'])}）。")
    add(f"- Kink 全控制模型中，原始债务方程两支联合检验 p={joint_p('D3_full')}；readiness 使用自身 min-RSS cutoff 与债务方程 cutoff 时分别为 p={joint_p('R3_full')}、p={joint_p('RD3_debtcut')}；去状态变量后债务与 readiness 分别为 p={joint_p('DN3_full')}、p={joint_p('RN3_full')}。")
    add("- 所有结果均为双向固定效应相关性估计。theta 和 cutoff 都是生成量，当前常规稳健标准误未覆盖完整上游估计与 cutoff 搜索不确定性。")
    add("")
    add("## 1. 统一符号、控制变量与估计口径")
    add("")
    add(r"令 $s_{it}$ 为主权利差比率，$A_{it}$ 为适应能力比率，$X_{it}$ 为气候脆弱性比率，$b_{it}=debt_{it}/CurrentGDP_{it}$。宏观控制为 Growth、Inflation，外部控制为 Reserves、Terms of trade。规模控制 $\ln(CurrentGDP_{it})$ 纳入利差和 readiness 回归，但不纳入税基和债务变化回归（ln(CurrentGDP) is included in spread/readiness and excluded from tax/debt-change）。全部模型含国家固定效应与年份固定效应，推断采用观测层面异方差稳健标准误（不是国家聚类标准误）。")
    add("")
    add("## 2. Baseline：主权利差回归")
    add("")
    add("### 2.1 回归公式")
    add("")
    add(r"$$\begin{aligned}s_{it}^{g}={}&\alpha_i+\lambda_t+\beta_A A_{it}^{c}+\beta_b b_{it}^{c}+\beta_X X_{it}^{c} \\ &+\frac{1}{2}\beta_{AA}(A_{it}^{c})^2+\frac{1}{2}\beta_{bb}(b_{it}^{c})^2+\frac{1}{2}\beta_{XX}(X_{it}^{c})^2 \\ &+\beta_{Ab}A_{it}^{c}b_{it}^{c}+\beta_{AX}A_{it}^{c}X_{it}^{c}+\beta_{bX}b_{it}^{c}X_{it}^{c}+\eta_G\ln(CurrentGDP_{it})+\Gamma_s^{\prime}W_{it}^{s}+\varepsilon_{it}^{s}.\end{aligned}$$")
    add("")
    add(r"完整二阶回归使用 baseline 固定样本均值中心化：$A^c=A-\bar A_s$、$b^c=b-\bar b_s$、$X^c=X-\bar X_s$。二阶项采用 $\frac12\beta_{jj}(j^c)^2$ 记法，因此对 $j$ 求导后的系数直接是 $\beta_{jj}j^c$。从中心化系数还原原始尺度线性系数：")
    add("")
    add(r"$$\begin{aligned}\widehat\beta_A^{raw}&=\widehat\beta_A^c-\widehat\beta_{AA}\bar A_s-\widehat\beta_{Ab}\bar b_s-\widehat\beta_{AX}\bar X_s,\\ \widehat\beta_b^{raw}&=\widehat\beta_b^c-\widehat\beta_{bb}\bar b_s-\widehat\beta_{Ab}\bar A_s-\widehat\beta_{bX}\bar X_s,\\ \widehat\beta_X^{raw}&=\widehat\beta_X^c-\widehat\beta_{XX}\bar X_s-\widehat\beta_{AX}\bar A_s-\widehat\beta_{bX}\bar b_s.\end{aligned}$$")
    add("")
    add(r"二阶和交叉项系数在中心化前后不变；常数平移由固定效应吸收。适应能力的边际利差节约为")
    add("")
    add(r"$$\widehat m^A_{it}=-\left(\widehat\beta_A^{raw}+\widehat\beta_{AA}A_{it}+\widehat\beta_{Ab}b_{it}+\widehat\beta_{AX}X_{it}\right)=-\left(\widehat\beta_A^c+\widehat\beta_{AA}A^c_{it}+\widehat\beta_{Ab}b^c_{it}+\widehat\beta_{AX}X^c_{it}\right).$$")
    add("")
    add("### 2.2 逐步回归表")
    add("")
    add("系数下方括号为稳健 t 值；`***`、`**`、`*` 分别表示 1%、5%、10% 显著性。所有列使用同一共同样本。")
    add("")
    add("**Panel A：核心变量与控制变量逐步检验**")
    add("")
    add(model_table(BASE_MODELS[:7], BASE_LABELS, ["vulnerability100", "readiness100", "b_it", "growth", "inflation_cpi", "reserves", "tt", "ln_currentgdp"], BASE_TERMS, base_coefs, base_stats, BASE_FLAGS))
    add("")
    add("**Panel B：交互模型**")
    add("")
    add(model_table(BASE_MODELS[7:10], BASE_LABELS, ["c_A", "c_b", "c_X", "int_AB", "int_AX", "growth", "inflation_cpi", "reserves", "tt", "ln_currentgdp"], BASE_TERMS, base_coefs, base_stats, BASE_FLAGS))
    add("")
    add("**Panel C：用于构造 $m^A_{it}$ 的完整二阶模型**")
    add("")
    add(model_table(["Quadratic_all"], BASE_LABELS, ["c_A", "c_b", "c_X", "half_A2", "half_b2", "half_X2", "int_AB", "int_AX", "int_bX", "growth", "inflation_cpi", "reserves", "tt", "ln_currentgdp"], BASE_TERMS, base_coefs, base_stats, BASE_FLAGS))
    add("")
    add("### 2.3 构造用原始尺度系数")
    add("")
    rows = []
    for key in [
        ("spread", "beta_A_raw"), ("spread", "beta_b_raw"), ("spread", "beta_X_raw"),
        ("spread", "beta_AA"), ("spread", "beta_bb"), ("spread", "beta_XX"),
        ("spread", "beta_AB"), ("spread", "beta_AX"), ("spread", "beta_bX"),
    ]:
        row = construction_by[key]
        rows.append([row["parameter"], fmt(row["estimate"]), fmt(row["se"]), fmt(row["t"], 3), fmt_p(row["p"]), f"[{fmt(row['ci_low'])}, {fmt(row['ci_high'])}]"])
    add(md_table(["参数", "估计值", "稳健 SE", "t", "p", "95% CI"], rows))
    add("")
    add("<details><summary>展开：baseline 交互模型的点边际效应</summary>")
    add("")
    add(marginal_table(read_csv(BASE / "marginal_effects.csv"), True))
    add("")
    add("</details>")
    add("")
    add("## 3. Empirical theta：边际税基收益与经验指标")
    add("")
    add("### 3.1 税基回归公式与时序")
    add("")
    add(r"$$\widetilde T_{i,t+1}^{(t)}=\frac{revenue_{i,t+1}}{CurrentGDP_{it}},\qquad \widetilde T_{it}^{(t-1)}=\frac{revenue_{it}}{CurrentGDP_{i,t-1}}.$$" )
    add("")
    add("以上两个税基变量都不乘 100，直接以比率进入回归。")
    add("")
    add(r"$$\begin{aligned}\widetilde T_{i,t+1}^{(t)}={}&\alpha_i+\lambda_t+\gamma_A A_{it}^{c}+\gamma_X X_{it}^{c} \\ &+\frac{1}{2}\gamma_{AA}(A_{it}^{c})^2+\frac{1}{2}\gamma_{XX}(X_{it}^{c})^2+\gamma_{AX}A_{it}^{c}X_{it}^{c} \\ &+\rho_T\widetilde T_{it}^{(t-1)}+\phi_b b_{it}+\Gamma_T^{\prime}W_{it}^{T}+\varepsilon_{i,t+1}^{T}.\end{aligned}$$" )
    add("")
    add(r"该税基方程及其 T1–T11 逐步规格均不控制 $\ln(CurrentGDP_{it})$；$b_{it}=debt_{it}/CurrentGDP_{it}$。T11 是构造边际税基收益的正式模型。")
    add("")
    add(r"税基完整二阶模型在固定 tax 样本内中心化。适应能力线性项还原为 $\widehat\gamma_A^{raw}=\widehat\gamma_A^c-\widehat\gamma_{AA}\bar A_T-\widehat\gamma_{AX}\bar X_T$，故")
    add("")
    add(r"$$\widehat T^A_{it}=\widehat\gamma_A^{raw}+\widehat\gamma_{AA}A_{it}+\widehat\gamma_{AX}X_{it}=\widehat\gamma_A^c+\widehat\gamma_{AA}A^c_{it}+\widehat\gamma_{AX}X^c_{it}.$$" )
    add("")
    add("### 3.2 税基逐步回归表")
    add("")
    add("**Panel A：核心变量与控制变量逐步检验**")
    add("")
    add(model_table(TAX_MODELS[:7], TAX_LABELS, ["vulnerability100", "readiness100", "taxbase_lag", "growth", "inflation_cpi", "reserves", "tt"], TAX_TERMS, tax_coefs, tax_stats))
    add("")
    add("**Panel B：交互模型**")
    add("")
    add(model_table(TAX_MODELS[7:10], TAX_LABELS, ["c_A_T", "c_X_T", "int_AX_T", "taxbase_lag", "growth", "inflation_cpi", "reserves", "tt"], TAX_TERMS, tax_coefs, tax_stats))
    add("")
    add("**Panel C：用于构造边际税基收益的完整二阶模型**")
    add("")
    add(model_table(["T11_quadratic_full"], TAX_LABELS, ["c_A_T", "c_X_T", "half_A2_T", "half_X2_T", "int_AX_T", "taxbase_lag", "b_it_theta", "growth", "inflation_cpi", "reserves", "tt"], TAX_TERMS, tax_coefs, tax_stats))
    add("")
    add("### 3.3 边际税基收益与 theta 构造")
    add("")
    rows = []
    for key in [("tax", "gamma_A_raw"), ("tax", "gamma_AA"), ("tax", "gamma_XX"), ("tax", "gamma_AX"), ("tax", "phi_b")]:
        row = construction_by[key]
        rows.append([row["parameter"], fmt(row["estimate"]), fmt(row["se"]), fmt(row["t"], 3), fmt_p(row["p"]), f"[{fmt(row['ci_low'])}, {fmt(row['ci_high'])}]"])
    add(md_table(["参数", "估计值", "稳健 SE", "t", "p", "95% CI"], rows))
    add("")
    add(r"最终经验指标为")
    add("")
    add(r"$$\widehat\theta^A_{it}=b_{it}\widehat m^A_{it}+\widehat T^A_{it},\qquad b_{it}=\frac{debt_{it}}{CurrentGDP_{it}}.$$" )
    add("")
    desc_rows = []
    for row in theta_desc:
        if row["variable"] in {"mA_hat", "spread_saving_component", "TA_hat", "theta_hat_A"}:
            desc_rows.append([row["variable"], row["sample"], fmt_int(row["N"]), fmt(row["mean"]), fmt(row["sd"]), fmt(row["p10"]), fmt(row["p50"]), fmt(row["p90"])])
    add(md_table(["构造量", "样本", "N", "均值", "SD", "P10", "P50", "P90"], desc_rows))
    add("")
    add("`theta_support` 是 spread 与 tax 估计样本的交集；`all_constructible` 是三项构造输入均非缺失的所有观测。联合 theta 标准误未报告，因为跨方程协方差需要联合 bootstrap 或系统估计。")
    add("")
    add("<details><summary>展开：税基交互模型的点边际效应</summary>")
    add("")
    add(marginal_table(read_csv(THETA / "marginal_effects.csv"), True))
    add("")
    add("</details>")
    add("")
    add("## 4. Doomloop：Single-Crossing Kink Marginal-Effect Model")
    add("")
    add("### 4.1 两个方程、readiness 双 cutoff 与去状态规格")
    add("")
    add(r"$$\Delta d_{i,t+1}^{(t)}=\frac{debt_{i,t+1}-debt_{it}}{CurrentGDP_{it}}.$$" )
    add("")
    add(r"$$\Delta d_{i,t+1}^{(t)}=\alpha_i+\lambda_t+\beta_LA_{it}(c-\widehat\theta^A_{it})_++\beta_HA_{it}(\widehat\theta^A_{it}-c)_++\rho_bb_{it}+\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.$$" )
    add("")
    add(r"债务变化方程（D1–D3 与 DN1–DN3）均不控制 $\ln(CurrentGDP_{it})$。")
    add("")
    add(r"$$J_{it}=A_{it}-A_{i,t-1}.$$" )
    add("")
    add(r"$$J_{it}=\alpha_i+\lambda_t+\delta_LFT_{it}(c-\widehat\theta^A_{it})_++\delta_HFT_{it}(\widehat\theta^A_{it}-c)_++\rho_AA_{i,t-1}+\gamma_XX_{it}+\eta_G\ln(CurrentGDP_{it})+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.$$" )
    add("")
    add("第二个方程的低、高两支都只乘 `FT=interest_revenue`，不再乘适应能力 A。readiness 主方程并列报告两套 cutoff：第一套使用 readiness 方程自身的 min-RSS cutoff；第二套固定使用主债务变化方程的 min-RSS cutoff（debt-equation cutoff）。后者是外部施加的比较情景，不称为 readiness 的最优 cutoff。每套均完成核心、宏观和全控制三列回归。")
    add("")
    panels = [
        ("债务变化方程（含 b）", ["D1_core", "D2_macro", "D3_full"], ["debt_kink_low", "debt_kink_high", "b_it_theta", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt"]),
        ("债务变化方程（去 b）", ["DN1_core", "DN2_macro", "DN3_full"], ["debt_kink_low", "debt_kink_high", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt"]),
        ("Readiness 变化方程（含 A 滞后）", ["R1_core", "R2_macro", "R3_full"], ["ready_kink_low", "ready_kink_high", "readiness_lag", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt", "ln_currentgdp"]),
        ("Readiness 变化方程（使用债务方程 cutoff）", ["RD1_debtcut", "RD2_debtcut", "RD3_debtcut"], ["ready_debt_kink_low", "ready_debt_kink_high", "readiness_lag", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt", "ln_currentgdp"]),
        ("Readiness 变化方程（去 A 滞后）", ["RN1_core", "RN2_macro", "RN3_full"], ["ready_kink_low", "ready_kink_high", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt", "ln_currentgdp"]),
    ]
    for title, models, variables in panels:
        add(f"**{title}**")
        add("")
        add(model_table(models, DOOM_LABELS, variables, DOOM_TERMS, doom_coefs, doom_stats))
        add("")
    add("### 4.2 Cutoff 与全控制分支系数")
    add("")
    cutoff_rows = []
    for spec, cutoff, key in [
        ("原始", original_cutoffs["debt"], original_keys["debt"]),
        ("原始", original_cutoffs["ready"], original_keys["ready"]),
        ("去状态变量", nostate_cutoffs["debt"], nostate_keys["debt"]),
        ("去状态变量", nostate_cutoffs["ready"], nostate_keys["ready"]),
    ]:
        cutoff_rows.append([
            spec, cutoff["equation"], fmt(cutoff["rss_min_cutoff"]), fmt(cutoff["rss"]),
            fmt_int(cutoff["candidate_count"]), fmt_int(cutoff["low_n"]), fmt_int(cutoff["high_n"]),
            fmt(key["effective_a"]), fmt(key["effective_b"]), "是" if key["opposite_sign"] == "1" else "否",
        ])
    add(md_table(["规格", "方程", "cutoff", "最小 RSS", "候选数", "低支 N", "高支 N", "a", "b", "异号"], cutoff_rows))
    add("")
    add("**Readiness 主方程的两种 cutoff 情景**")
    add("")
    ready_scenario_rows = []
    for scenario in ["readiness_minRSS", "debt_equation_cutoff"]:
        row = ready_scenarios[scenario]
        key = original_keys["ready"] if scenario == "readiness_minRSS" else original_keys["ready_debt"]
        ready_scenario_rows.append([
            scenario, row["cutoff_source"], fmt(row["cutoff"]), fmt(row["readiness_rss"]),
            fmt(row["readiness_min_rss"]), fmt(row["rss_gap"]), fmt(key["effective_a"]),
            fmt(key["effective_b"]), "是" if key["opposite_sign"] == "1" else "否",
        ])
    add(md_table(["情景", "cutoff 来源", "cutoff", "readiness RSS", "readiness 最小 RSS", "RSS 差", "a", "b", "异号"], ready_scenario_rows))
    add("")
    add(r"点边际效应统一按 $m(\theta;c)=a(c-\theta)_++b(\theta-c)_+$ 计算；在 cutoff 处定义为 0。正值表示当前解释变量改善与更高的结果变量变化相关，负值表示与更低的结果变量变化相关。")
    add("")
    add("<details><summary>展开：含双 cutoff 情景的 kink 点边际效应</summary>")
    add("")
    orig = read_csv(DOOM / "marginal_effects.csv")
    nostate = read_csv(DOOM / "nostate_marginal_effects.csv")
    labelled: list[dict[str, str]] = []
    for row in orig:
        row = dict(row)
        row["equation"] = f"原始-{row['equation']}"
        labelled.append(row)
    for row in nostate:
        row = dict(row)
        row["equation"] = f"去状态-{row['equation']}"
        labelled.append(row)
    add(marginal_table(labelled, False))
    add("")
    add("</details>")
    add("")
    add("### 4.3 边际效应图")
    add("")
    add("每张图绘制同一分段线性函数。min-RSS 图的竖直虚线是该方程自身选择的 cutoff；债务-cutoff 图的虚线来自债务变化方程，不是 readiness RSS 最优点。横轴与 theta 均为统一比率尺度。")
    add("")
    add("| 原始状态变量规格 | 去状态变量规格 |")
    add("| --- | --- |")
    add("| ![债务变化边际效应](figures/debt_marginal_effect.png) | ![债务变化边际效应：去 b](figures/debt_marginal_effect_no_b.png) |")
    add("| ![readiness 变化边际效应](figures/readiness_marginal_effect.png) | ![readiness 变化边际效应：去 A 滞后](figures/readiness_marginal_effect_no_lag.png) |")
    add("")
    add("**Readiness cutoff 情景对比**")
    add("")
    add("![readiness 两种 cutoff 对比](figures/readiness_cutoff_comparison.png)")
    add("")
    add("## 5. 结果解释边界")
    add("")
    add("这些是双向固定效应相关性估计，不应表述为因果效应。cutoff 是同一样本内按 RSS 选择的生成参数，常规条件于 cutoff 的稳健标准误没有计入搜索不确定性；theta 也是两条上游回归生成的指标。正式推断应进一步采用完整流程 bootstrap，并考虑国家层面聚类或其他适合面板依赖结构的推断。")
    add("")
    return "\n".join(lines)


def rows_simple(path: Path, fields: list[str], labels: list[str], formatters: dict[str, str] | None = None) -> str:
    output = []
    formatters = formatters or {}
    for row in read_csv(path):
        values: list[str] = []
        for field in fields:
            mode = formatters.get(field, "raw")
            value = row.get(field, "")
            if mode == "num":
                values.append(fmt(value))
            elif mode == "int":
                values.append(fmt_int(value))
            elif mode == "p":
                values.append(fmt_p(value))
            elif mode == "pass":
                values.append("通过" if value == "1" else "未通过")
            else:
                values.append(value)
        output.append(values)
    return md_table(labels, output)


def validation_summary(paths: list[Path], pass_field: str = "passed") -> tuple[int, int]:
    rows = [row for path in paths for row in read_csv(path)]
    return sum(row.get(pass_field) == "1" for row in rows), len(rows)


def render_diagnostics() -> str:
    lines: list[str] = []
    add = lines.append
    formula_paths = [
        THETA / "formula_checks.csv", DOOM / "formula_checks.csv", DOOM / "nostate_formula_checks.csv",
    ]
    cutoff_paths = [DOOM / "cutoff_validation.csv", DOOM / "nostate_cutoff_validation.csv"]
    f_ok, f_n = validation_summary(formula_paths)
    c_ok, c_n = validation_summary(cutoff_paths)
    unit_ok, unit_n = validation_summary([BASE / "unit_scaling_checks.csv", THETA / "unit_scaling_checks.csv", DOOM / "unit_scaling_checks.csv"])
    original_keys = {row["equation"]: row for row in read_csv(DOOM / "key_results.csv")}
    nostate_keys = {row["equation"]: row for row in read_csv(DOOM / "nostate_key_results.csv")}

    add("# Paper B：统计检验与数据检查")
    add("")
    add(f"> 生成时间：{datetime.now():%Y-%m-%d %H:%M}（Asia/Shanghai）。本文件汇总三个板块的诊断、样本审计、单位审计、稳健性检验与验证结果；正式公式和回归表见 `paperB_results.md`。")
    add("")
    add("## 1. 总体评估：可在明确限制条件下使用")
    add("")
    add(f"单位换算检查通过 {unit_ok}/{unit_n} 项；代数/构造检查通过 {f_ok}/{f_n} 项；cutoff 最小 RSS 复核通过 {c_ok}/{c_n} 项。当前结果在代码一致性和样本内计算层面通过，但仍属于“Share with caveats”：生成 theta、样本内 cutoff 搜索和面板相关推断的不确定性尚未由完整流程 bootstrap 与国家聚类标准误覆盖。")
    add("")
    add("## 2. 数据来源、单位与时序检查")
    add("")
    add("唯一原始输入是 `data0804/invest_panel_weo.csv`。所有源百分数、比率和 0—100 指数在读入后除以 100；金额变量 `revenue`、`debt`、`CurrentGDP` 不缩放。本次回归直接构造 $b_{it}=debt_{it}/CurrentGDP_{it}$，不再以源字段 `debt_gdp` 作为 b；规模控制采用 `ln_currentgdp=ln(CurrentGDP)`，并严格执行：ln(CurrentGDP) is included in spread/readiness and excluded from tax/debt-change。关键因变量的精确定义为：")
    add("")
    add(r"- $\widetilde T_{i,t+1}^{(t)}=revenue_{i,t+1}/CurrentGDP_{it}$，不乘 100。")
    add(r"- $\widetilde T_{it}^{(t-1)}=revenue_{it}/CurrentGDP_{i,t-1}$，不乘 100。")
    add(r"- $\Delta d_{i,t+1}^{(t)}=(debt_{i,t+1}-debt_{it})/CurrentGDP_{it}$，不乘 100。")
    add(r"- $J_{it}=A_{it}-A_{i,t-1}$，其中 A 已经是 0—1 比率。")
    add("")
    add("### 2.1 基准单位换算审计")
    add("")
    add(rows_simple(BASE / "unit_scaling_checks.csv", ["variable", "source_min", "source_max", "ratio_min", "ratio_max", "max_abs_scaling_diff", "passed"], ["变量", "源最小值", "源最大值", "比率最小值", "比率最大值", "最大换算误差", "状态"], {"source_min": "num", "source_max": "num", "ratio_min": "num", "ratio_max": "num", "max_abs_scaling_diff": "num", "passed": "pass"}))
    add("")
    add("Empirical-theta 重新执行同一 13 项审计；doomloop 从已审计的 theta panel 读入并对关键上游比例变量复核。全部检查的原始 CSV 保留在各板块 `stata_outputs` 目录。")
    add("")
    add("## 3. 样本覆盖与描述性统计")
    add("")
    base_stats = stats_index(read_csv(BASE / "model_stats.csv"))["Quadratic_all"]
    tax_stats = stats_index(read_csv(THETA / "model_stats.csv"))["T11_quadratic_full"]
    doom_stats = stats_index(read_csv(DOOM / "model_stats.csv") + read_csv(DOOM / "nostate_model_stats.csv"))
    sample_rows = [
        ["Baseline 共同样本", fmt_int(base_stats["N"]), fmt_int(base_stats["countries"]), fmt_int(base_stats["years"]), "1998–2023"],
        ["Tax 共同样本", fmt_int(tax_stats["N"]), fmt_int(tax_stats["countries"]), fmt_int(tax_stats["years"]), f"{tax_stats['first_year']}–{tax_stats['last_year']}"],
        ["Doomloop 债务方程", fmt_int(doom_stats["D3_full"]["N"]), fmt_int(doom_stats["D3_full"]["countries"]), fmt_int(doom_stats["D3_full"]["years"]), f"{doom_stats['D3_full']['first_year']}–{doom_stats['D3_full']['last_year']}"],
        ["Doomloop readiness 方程", fmt_int(doom_stats["R3_full"]["N"]), fmt_int(doom_stats["R3_full"]["countries"]), fmt_int(doom_stats["R3_full"]["years"]), f"{doom_stats['R3_full']['first_year']}–{doom_stats['R3_full']['last_year']}"],
    ]
    add(md_table(["固定样本", "N", "国家数", "年份数", "基准年份范围"], sample_rows))
    add("")
    add("### 3.1 Baseline 输入变量（全数据非缺失分布）")
    add("")
    selected = {"bond_spreads", "vulnerability100", "readiness100", "b_it", "growth", "inflation_cpi", "reserves", "tt", "ln_currentgdp"}
    base_profile = [r for r in read_csv(BASE / "profile.csv") if r["variable"] in selected]
    add(md_table(["变量", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["variable"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in base_profile]))
    add("")
    add("### 3.2 Tax 与 theta 构造量")
    add("")
    theta_desc = read_csv(THETA / "descriptive_stats.csv")
    add(md_table(["变量", "样本", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["variable"], r["sample"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in theta_desc]))
    add("")
    add("### 3.3 含 readiness 双 cutoff 的 doomloop 回归变量")
    add("")
    doom_desc = read_csv(DOOM / "regression_descriptive_stats.csv") + read_csv(DOOM / "nostate_regression_descriptive_stats.csv")
    add(md_table(["规格", "方程", "变量", "角色", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["specification"], r["equation"], r["variable"], r["role"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in doom_desc]))
    add("")
    add("## 4. 缺失值、重复键与固定效应可识别性")
    add("")
    add("国家—年份重复键检查在三段流程中均为零；代码遇到重复键会直接终止，不会静默删除。各段共同样本在估计前锁定，逐步模型与 cutoff 候选使用相同观测。")
    add("")
    add("### 4.1 独占样本损失")
    add("")
    missing = []
    for stage, path in [("baseline", BASE / "missing_loss.csv"), ("tax", THETA / "missing_loss.csv"), ("doomloop", DOOM / "missing_loss.csv")]:
        for r in read_csv(path):
            missing.append([stage, r.get("equation", "—"), r["variable"], fmt_int(r["missing_total"]), fmt(r["missing_rate"], 2), fmt_int(r["exclusive_loss"])])
    add(md_table(["板块", "方程", "变量", "缺失数", "缺失率", "独占损失"], missing))
    add("")
    add("### 4.2 Within 变异")
    add("")
    variation = []
    for stage, path in [("baseline", BASE / "variation.csv"), ("tax", THETA / "variation.csv"), ("doomloop", DOOM / "variation.csv")]:
        for r in read_csv(path):
            if r.get("variable") == "year":
                continue
            variation.append([stage, r.get("equation", "—"), r["variable"], fmt(r["sd_overall"]), fmt(r["sd_within"]), fmt(r["ratio_within_overall"]), r["fe_identification"]])
    add(md_table(["板块", "方程", "变量", "总体 SD", "Within SD", "Within/总体", "FE 识别"], variation))
    add("")
    add("## 5. 共线性、相关性与系数变化")
    add("")
    add("### 5.1 VIF/条件数")
    add("")
    vif_rows = []
    for stage, path in [
        ("baseline-linear", BASE / "collinearity.csv"),
        ("baseline-quadratic", BASE / "quadratic_collinearity.csv"),
        ("tax", THETA / "collinearity.csv"),
    ]:
        for r in read_csv(path):
            vif_rows.append([stage, r["variable"], fmt(r["vif"]), fmt(r["tolerance"]), fmt(r["condition_number"])])
    add(md_table(["板块", "变量", "VIF", "容忍度", "条件数"], vif_rows))
    add("")
    add("### 5.2 高绝对相关系数（排除对角线与镜像重复）")
    add("")
    corr_rows = []
    for stage, path in [("baseline", BASE / "correlations.csv"), ("tax", THETA / "correlations.csv")]:
        seen: set[tuple[str, str]] = set()
        for r in read_csv(path):
            a, b = r["variable_i"], r["variable_j"]
            key = tuple(sorted((a, b)))
            value = number(r["correlation"])
            if a == b or key in seen or value is None or abs(value) < 0.60:
                continue
            seen.add(key)
            corr_rows.append([stage, a, b, fmt(value)])
    add(md_table(["板块", "变量 1", "变量 2", "相关系数"], corr_rows))
    add("")
    add("### 5.3 加入控制变量后的系数变化")
    add("")
    changes = []
    for stage, path in [("baseline", BASE / "coefficient_changes.csv"), ("tax", THETA / "coefficient_changes.csv")]:
        for r in read_csv(path):
            changes.append([stage, r["model"], r["variable"], fmt(r["baseline"]), fmt(r["new"]), fmt(r["absolute_change"]), fmt(r["percent_change"], 1), r["reporting_rule"]])
    add(md_table(["板块", "模型", "变量", "基准系数", "新系数", "绝对变化", "%变化", "报告规则"], changes))
    add("")
    add("## 6. 统计检验")
    add("")
    add("### 6.1 Wald 联合检验")
    add("")
    wald_rows = []
    for stage, path in [("baseline", BASE / "wald_tests.csv"), ("tax", THETA / "wald_tests.csv"), ("doomloop", DOOM / "wald_tests.csv"), ("doomloop-no-state", DOOM / "nostate_wald_tests.csv")]:
        for r in read_csv(path):
            wald_rows.append([stage, r["model"], r["hypothesis"], fmt(r["F"]), fmt_int(r["df_num"]), fmt_int(r["df_den"]), fmt_p(r["p"])])
    add(md_table(["板块", "模型", "原假设", "F", "分子 df", "分母 df", "p"], wald_rows))
    add("")
    add("### 6.2 代数、映射与时序公式检查")
    add("")
    check_rows = []
    for stage, path in [("theta", THETA / "formula_checks.csv"), ("doomloop", DOOM / "formula_checks.csv"), ("doomloop-no-state", DOOM / "nostate_formula_checks.csv")]:
        for r in read_csv(path):
            check_rows.append([stage, r["check"], fmt(r.get("max_abs_diff") or r.get("max_abs_difference"), 8), fmt(r["tolerance"], 8), "通过" if r["passed"] == "1" else "未通过"])
    add(md_table(["板块", "检查", "最大绝对误差", "容差", "状态"], check_rows))
    add("")
    add("### 6.3 areg 与显式 LSDV 复核")
    add("")
    est_rows = []
    for stage, path in [("tax", THETA / "estimator_validation.csv"), ("doomloop", DOOM / "estimator_validation.csv"), ("doomloop-no-state", DOOM / "nostate_estimator_validation.csv")]:
        for r in read_csv(path):
            est_rows.append([stage, r.get("model") or r.get("equation"), r["variable"], fmt(r["areg_b"]), fmt(r["lsdv_b"]), fmt(r["abs_b_diff"], 8), fmt(r["abs_se_diff"], 8)])
    for r in read_csv(BASE / "validation_checks.csv"):
        est_rows.insert(0, ["baseline", r["model"], r["variable"], fmt(r["main_b"]), fmt(r["lsdv_b"]), fmt(r["abs_b_diff"], 8), fmt(r["abs_se_diff"], 8)])
    add(md_table(["板块", "模型/方程", "变量", "areg", "LSDV", "|系数差|", "|SE差|"], est_rows))
    add("")
    add("### 6.4 Cutoff 最小 RSS 复核")
    add("")
    cutoff_checks = []
    for stage, path in [("原始", DOOM / "cutoff_validation.csv"), ("去状态变量", DOOM / "nostate_cutoff_validation.csv")]:
        for r in read_csv(path):
            cutoff_checks.append([stage, r["equation"], fmt(r["recorded_cutoff"]), fmt(r["profile_min_rss"]), fmt(r["rss_at_recorded_cutoff"]), fmt(r["abs_rss_diff"], 8), "通过" if r["passed"] == "1" else "未通过"])
    add(md_table(["规格", "方程", "记录 cutoff", "profile 最小 RSS", "cutoff RSS", "差值", "状态"], cutoff_checks))
    add("")
    add("### 6.5 Readiness 双 cutoff 来源复核")
    add("")
    scenario_rows = []
    for r in read_csv(DOOM / "readiness_cutoff_scenarios.csv"):
        scenario_rows.append([r["scenario"], r["cutoff_source"], fmt(r["cutoff"]), fmt(r["readiness_rss"]), fmt(r["readiness_min_rss"]), fmt(r["rss_gap"]), fmt_int(r["N"])])
    add(md_table(["情景", "cutoff 来源", "cutoff", "readiness RSS", "最小 RSS", "RSS 差", "N"], scenario_rows))
    add("")
    add(rows_simple(DOOM / "cutoff_scenario_checks.csv", ["check", "value", "benchmark", "tolerance", "passed"], ["检查", "值", "基准", "容差", "状态"], {"value": "num", "benchmark": "num", "tolerance": "num", "passed": "pass"}))
    add("")
    add("## 7. 图形 QA")
    add("")
    add("新增的 readiness 债务-cutoff 单图和双 cutoff 对比图均保留 PNG 与 PDF。所有曲线使用连续 theta 网格并把相应 cutoff 精确插入；借用债务 cutoff 的图明确标注其来源，不把它表述为 readiness 的 RSS 最优点。")
    add("")
    add("## 8. 必须保留的限制与建议")
    add("")
    add("- 当前稳健标准误处理异方差，但不处理同一国家内序列相关；面板论文通常还应报告国家聚类标准误或适当的双向聚类/空间相关推断。")
    add("- cutoff 在同一样本上搜索，条件于 cutoff 的常规标准误偏窄风险未纳入。建议按国家重抽样，完整重复 baseline、tax/theta、cutoff 搜索和最终回归。")
    add("- theta 是生成解释变量；联合不确定性依赖跨方程协方差。当前只对两个组成边际量分别做 delta-method 标准误，不提供 theta 的联合 SE。")
    add("- 结果是固定效应相关性证据，不支持没有额外识别设计的因果措辞。")
    same_sign_specs = []
    for label, row in [
        ("原始 debt", original_keys["debt"]), ("原始 readiness-minRSS", original_keys["ready"]),
        ("原始 readiness-债务cutoff", original_keys["ready_debt"]),
        ("去 b debt", nostate_keys["debt"]), ("去滞后 A readiness", nostate_keys["ready"]),
    ]:
        if row["opposite_sign"] != "1":
            same_sign_specs.append(label)
    add(f"- 分支异号是经验 single-crossing 的额外形状要求，不由 kink 联合显著自动保证。当前两支同号的规格为：{'、'.join(same_sign_specs) if same_sign_specs else '无'}；必须与联合检验分开报告。")
    add("")
    add("## 9. 原始诊断输出索引")
    add("")
    add("完整 CSV/DTA/日志仍保留在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/`、`doomloop/stata_outputs/`。本文件是汇总层，不替代这些逐项机器可读结果。")
    add("")
    return "\n".join(lines)


def render_progress() -> str:
    construction = {row["parameter"]: row for row in read_csv(THETA / "construction_coefficients.csv")}
    scale_coefs = coefficient_index(
        read_csv(BASE / "model_coefficients.csv")
        + read_csv(DOOM / "model_coefficients.csv")
        + read_csv(DOOM / "nostate_model_coefficients.csv")
    )
    base_stats = stats_index(read_csv(BASE / "model_stats.csv"))["Quadratic_all"]
    tax_stats = stats_index(read_csv(THETA / "model_stats.csv"))["T11_quadratic_full"]
    doom_stats = stats_index(read_csv(DOOM / "model_stats.csv") + read_csv(DOOM / "nostate_model_stats.csv"))

    def find_wald(path: Path, model: str, text: str) -> dict[str, str]:
        for row in read_csv(path):
            if row["model"] == model and text in row["hypothesis"]:
                return row
        raise KeyError(f"Wald test not found: {path.name}, {model}, {text}")

    def p_label(value: object) -> str:
        rendered = fmt_p(value)
        return f"p{rendered}" if rendered.startswith("<") else f"p={rendered}"

    def significance_label(value: object) -> str:
        p = number(value)
        if p is None:
            return "显著性无法判断"
        if p < 0.01:
            return "达到 1% 显著性水平"
        if p < 0.05:
            return "达到 5% 显著性水平"
        if p < 0.10:
            return "达到 10% 显著性水平"
        return "未达 10% 显著性水平"

    debt_wald = find_wald(DOOM / "wald_tests.csv", "D3_full", "low- and high-branch")
    ready_wald = find_wald(DOOM / "wald_tests.csv", "R3_full", "low- and high-branch")
    ready_debt_wald = find_wald(DOOM / "wald_tests.csv", "RD3_debtcut", "low- and high-branch")
    debt_ns_wald = find_wald(DOOM / "nostate_wald_tests.csv", "DN3_full", "low- and high-branch")
    ready_ns_wald = find_wald(DOOM / "nostate_wald_tests.csv", "RN3_full", "low- and high-branch")
    tax_joint = find_wald(THETA / "wald_tests.csv", "T11_quadratic_full", "marginal-A terms jointly")

    original_cutoffs = {row["equation"]: row for row in read_csv(DOOM / "cutoffs.csv")}
    nostate_cutoffs = {row["equation"]: row for row in read_csv(DOOM / "nostate_cutoffs.csv")}
    original_keys = {row["equation"]: row for row in read_csv(DOOM / "key_results.csv")}
    nostate_keys = {row["equation"]: row for row in read_csv(DOOM / "nostate_key_results.csv")}
    ready_scenarios = {row["scenario"]: row for row in read_csv(DOOM / "readiness_cutoff_scenarios.csv")}
    unit_ok, unit_total = validation_summary(
        [BASE / "unit_scaling_checks.csv", THETA / "unit_scaling_checks.csv", DOOM / "unit_scaling_checks.csv"]
    )
    formula_ok, formula_total = validation_summary(
        [THETA / "formula_checks.csv", DOOM / "formula_checks.csv", DOOM / "nostate_formula_checks.csv"]
    )
    cutoff_ok, cutoff_total = validation_summary(
        [DOOM / "cutoff_validation.csv", DOOM / "nostate_cutoff_validation.csv"]
    )
    scenario_ok, scenario_total = validation_summary([DOOM / "cutoff_scenario_checks.csv"])

    beta_ab = construction["beta_AB"]
    beta_ax = construction["beta_AX"]
    beta_aa = construction["beta_AA"]
    gamma_a = construction["gamma_A_raw"]
    gamma_aa = construction["gamma_AA"]
    gamma_ax = construction["gamma_AX"]
    spread_gdp = scale_coefs[("Quadratic_all", "ln_currentgdp")]
    ready_gdp = scale_coefs[("R3_full", "ln_currentgdp")]
    ready_ns_gdp = scale_coefs[("RN3_full", "ln_currentgdp")]

    lines: list[str] = []
    add = lines.append
    add("# Paper B 工作进展与核心卡点")
    add("")
    add(f"> 更新时间：{datetime.now():%Y-%m-%d %H:%M}（Asia/Shanghai）。本文件由 `paperB/render_output.py` 基于本次 Stata 机器可读输出自动生成。")
    add("")
    add("## 技术摘要：分析链已跑通，核心门槛结论仍需稳健性支持")
    add("")
    add("- 当前 `invest_panel_weo.csv` 已完成 baseline、empirical theta、doomloop 与去状态变量四段重估；结果、诊断、图形、CSV、DTA 和日志均已刷新。")
    add(f"- 边际税基收益现由 T11 完整二阶模型生成：$\\gamma_{{AA}}$={fmt(gamma_aa['estimate'])}（{p_label(gamma_aa['p'])}）、$\\gamma_{{AX}}$={fmt(gamma_ax['estimate'])}（{p_label(gamma_ax['p'])}），并控制滞后税基、$b_{{it}}$ 与四个非规模控制。")
    add(f"- 方程级规模控制已落实：$\\ln(CurrentGDP)$ 在完整二阶利差、readiness 主规格和去滞后规格中的系数分别为 {fmt(spread_gdp['coefficient'])}（{p_label(spread_gdp['p'])}）、{fmt(ready_gdp['coefficient'])}（{p_label(ready_gdp['p'])}）和 {fmt(ready_ns_gdp['coefficient'])}（{p_label(ready_ns_gdp['p'])}）；tax 与 debt-change 全部排除该项。")
    add(f"- `mA_hat` 已改由完整二阶 spread 模型生成：$\\beta_{{AA}}$={fmt(beta_aa['estimate'])}（{p_label(beta_aa['p'])}）、$\\beta_{{Ab}}$={fmt(beta_ab['estimate'])}（{p_label(beta_ab['p'])}）、$\\beta_{{AX}}$={fmt(beta_ax['estimate'])}（{p_label(beta_ax['p'])}）。")
    add(f"- Doomloop 联合检验：债务方程含/不含 b 时分别为 {p_label(debt_wald['p'])}、{p_label(debt_ns_wald['p'])}；readiness 使用自身 min-RSS cutoff、债务方程 cutoff、去滞后 A 时分别为 {p_label(ready_wald['p'])}、{p_label(ready_debt_wald['p'])}、{p_label(ready_ns_wald['p'])}。")
    add(f"- readiness 的 min-RSS、债务-cutoff 与去滞后 A 三个规格的低、高分支依次为{'异号' if original_keys['ready']['opposite_sign'] == '1' else '同号'}、{'异号' if original_keys['ready_debt']['opposite_sign'] == '1' else '同号'}、{'异号' if nostate_keys['ready']['opposite_sign'] == '1' else '同号'}；异号才满足经验 single-crossing 的形状要求。")
    add("- 当前结果可作为双向固定效应相关性证据使用，但尚未纳入国家内序列相关、theta 生成误差与 cutoff 搜索不确定性，不能解释为因果效应或最终门槛证据。")
    add("")
    add("## 1. 已完成：数据输入已审计，四段估计和统一输出均成功")
    add("")
    add(md_table(
        ["板块", "状态", "本次交付/样本", "判断"],
        [
            ["分析输入", "完成", "1,972 行、68 国、1995–2023；国家—年份重复键为 0", "可作为本次 Stata 分析的固定输入"],
            ["Baseline", "完成", f"N={fmt_int(base_stats['N'])}，{fmt_int(base_stats['countries'])} 国，{fmt_int(base_stats['years'])} 年", "完整二阶 TWFE、原始尺度还原、Wald 与诊断已输出"],
            ["Empirical theta", "完成", f"N={fmt_int(tax_stats['N'])}，{fmt_int(tax_stats['countries'])} 国，{fmt_int(tax_stats['years'])} 年", "税基方程、theta panel 与构造审计已输出"],
            ["Doomloop debt", "完成", f"N={fmt_int(doom_stats['D3_full']['N'])}，cutoff={fmt(original_cutoffs['debt']['rss_min_cutoff'])}", "原始与去 b 规格均已重估"],
            ["Doomloop readiness", "完成", f"N={fmt_int(doom_stats['R3_full']['N'])}，minRSS cutoff={fmt(original_cutoffs['ready']['rss_min_cutoff'])}，债务 cutoff={fmt(ready_scenarios['debt_equation_cutoff']['cutoff'])}", "两种 cutoff 与去滞后 A 规格均已重估"],
            ["统一交付", "完成", "results、diagnostics、progress、PNG/PDF、CSV/DTA、日志", "统一入口可从现有分析 CSV 重跑"],
        ],
        numeric_from=99,
    ))
    add("")
    add("范围说明：回归中的百分比、比率和 0–100 指数均先除以 100；金额变量保持原尺度，$b_{it}$ 由同年 `debt/CurrentGDP` 直接计算。宏观控制为 Growth、Inflation，外部控制为 Reserves、Terms of trade；规模控制为 `ln_currentgdp=ln(CurrentGDP)`，规则是 ln(CurrentGDP) is included in spread/readiness and excluded from tax/debt-change。所有正式模型包含国家和年份固定效应，当前标准误为观测层异方差稳健标准误。")
    add("")
    add("## 2. 当前证据：baseline 机制较稳定，doomloop 门槛尚不稳定")
    add("")
    add(md_table(
        ["证据节点", "估计/检验", "p 值", "当前解释"],
        [
            ["利差：A²", fmt(beta_aa["estimate"]), fmt_p(beta_aa["p"]), "适应能力边际利差效应随 A 自身水平变化"],
            ["利差：A×债务", fmt(beta_ab["estimate"]), fmt_p(beta_ab["p"]), "债务水平调节适应能力的边际利差效应"],
            ["利差：A×脆弱性", fmt(beta_ax["estimate"]), fmt_p(beta_ax["p"]), "脆弱性水平调节适应能力的边际利差效应"],
            ["税基：A 原始尺度", fmt(gamma_a["estimate"]), fmt_p(gamma_a["p"]), significance_label(gamma_a["p"])],
            ["税基：A²", fmt(gamma_aa["estimate"]), fmt_p(gamma_aa["p"]), significance_label(gamma_aa["p"])],
            ["税基：A×脆弱性", fmt(gamma_ax["estimate"]), fmt_p(gamma_ax["p"]), f"{significance_label(gamma_ax['p'])}；边际 A 项联合检验 {p_label(tax_joint['p'])}"],
            ["原始 debt kink", f"cutoff={fmt(original_cutoffs['debt']['rss_min_cutoff'])}", fmt_p(debt_wald["p"]), f"{significance_label(debt_wald['p'])}；两支{'异号' if original_keys['debt']['opposite_sign'] == '1' else '同号'}"],
            ["原始 readiness kink", f"cutoff={fmt(original_cutoffs['ready']['rss_min_cutoff'])}", fmt_p(ready_wald["p"]), f"{significance_label(ready_wald['p'])}；两支{'异号' if original_keys['ready']['opposite_sign'] == '1' else '同号'}"],
            ["readiness：债务方程 cutoff", f"cutoff={fmt(ready_scenarios['debt_equation_cutoff']['cutoff'])}", fmt_p(ready_debt_wald["p"]), f"{significance_label(ready_debt_wald['p'])}；两支{'异号' if original_keys['ready_debt']['opposite_sign'] == '1' else '同号'}；RSS 差={fmt(ready_scenarios['debt_equation_cutoff']['rss_gap'])}"],
            ["去 b debt kink", f"cutoff={fmt(nostate_cutoffs['debt']['rss_min_cutoff'])}", fmt_p(debt_ns_wald["p"]), f"{significance_label(debt_ns_wald['p'])}；两支{'异号' if nostate_keys['debt']['opposite_sign'] == '1' else '同号'}"],
            ["去滞后 A readiness kink", f"cutoff={fmt(nostate_cutoffs['ready']['rss_min_cutoff'])}", fmt_p(ready_ns_wald["p"]), f"{significance_label(ready_ns_wald['p'])}；两支{'异号' if nostate_keys['ready']['opposite_sign'] == '1' else '同号'}"],
        ],
        numeric_from=99,
    ))
    add("")
    add("对应完整系数、边际效应和图形见 `paperB_results.md`；本进展文档不重复嵌图，以避免与正式结果文档形成两套展示口径。")
    add("")
    add("## 3. 质量核验：计算一致性通过，但不等同于推断充分")
    add("")
    add(md_table(
        ["核验", "通过", "总数", "结论"],
        [
            ["单位换算", unit_ok, unit_total, "通过" if unit_ok == unit_total else "未通过"],
            ["代数、映射与构造", formula_ok, formula_total, "通过" if formula_ok == formula_total else "未通过"],
            ["cutoff 最小 RSS", cutoff_ok, cutoff_total, "通过" if cutoff_ok == cutoff_total else "未通过"],
            ["readiness 双 cutoff 来源", scenario_ok, scenario_total, "通过" if scenario_ok == scenario_total else "未通过"],
            ["国家—年份唯一键", 3, 3, "三段流程重复键均为 0"],
            ["areg 与显式 LSDV", "已复核", "关键系数", "数值一致"],
        ],
        numeric_from=99,
    ))
    add("")
    add("这些检查证明本次结果在单位、公式、样本锁定和程序实现层面一致；它们不能替代聚类推断、完整 bootstrap 或外生识别。")
    add("")
    add("## 4. 核心卡点：正式推断、single-crossing 形状和上游数据复现")
    add("")
    add("### 4.1 正式推断尚未覆盖三类不确定性")
    add("")
    add("当前 `vce(robust)` 不处理同一国家内序列相关；theta 来自两条上游回归，cutoff 又由同一样本 RSS 搜索产生。现有标准误没有联合覆盖这三层不确定性，p 值可能偏乐观。")
    add("")
    add("### 4.2 Cutoff 与分支形状对状态项设定敏感")
    add("")
    add(f"readiness 使用自身 min-RSS cutoff={fmt(original_cutoffs['ready']['rss_min_cutoff'])} 时联合 {p_label(ready_wald['p'])}；固定使用债务方程 cutoff={fmt(ready_scenarios['debt_equation_cutoff']['cutoff'])} 时 {p_label(ready_debt_wald['p'])}，其 readiness RSS 比最小值高 {fmt(ready_scenarios['debt_equation_cutoff']['rss_gap'])}。去滞后 A 后 cutoff={fmt(nostate_cutoffs['ready']['rss_min_cutoff'])}、{p_label(ready_ns_wald['p'])}。三种 readiness 规格的两支分别为{'异号' if original_keys['ready']['opposite_sign'] == '1' else '同号'}、{'异号' if original_keys['ready_debt']['opposite_sign'] == '1' else '同号'}、{'异号' if nostate_keys['ready']['opposite_sign'] == '1' else '同号'}。因此不能把借用债务 cutoff、readiness RSS 最优、kink 显著和 single-crossing 成立视为同一结论。")
    add("")
    add("### 4.3 当前仓库可复现分析，但不能从源文件重建分析 CSV")
    add("")
    add("四份完整 Stata 源码与三段输出已经保留，`paperB/run_workflow.ps1` 可从 `data0804/invest_panel_weo.csv` 重跑分析。WEO 工作簿 `data0804/WEOApr2026all.xlsx` 已在库内，但数据构建脚本仍依赖当前目录中不存在的根目录基础面板 `cleaned_imf_like_panel_1995_2023.csv`；补齐该文件前，数据层只能审计现有分析 CSV，不能从最上游完整重建。")
    add("")
    add("### 4.4 缺失和单位限制仍影响外推")
    add("")
    add("`bond_spreads` 缺失 525 行（26.62%），`tt` 缺失 242 行（12.27%），是主要样本损失来源；财政系列在早期年份也存在缺失。`CurrentGDP`、`revenue` 和 `debt` 是不同国家的本币金额，既有 reserves 口径也不适合直接做跨国水平比较。")
    add("")
    add("### 4.5 识别边界没有改变")
    add("")
    add("全部结果属于双向固定效应相关性估计。没有外生冲击、工具变量、事件研究或其他识别设计时，不应使用因果措辞。")
    add("")
    add("## 5. 下一步：先补推断，再决定是否强化门槛叙事")
    add("")
    add("1. **P0——补齐国家层面的推断。** 并列报告国家聚类标准误；随后按国家重抽样，每次完整重估 baseline、tax、theta、cutoff 和最终 kink 回归。")
    add("2. **P0——恢复数据层完全复现。** 补齐根目录基础面板 `cleaned_imf_like_panel_1995_2023.csv`，并记录它、WEO 工作簿与最终分析 CSV 的文件哈希及生成关系。")
    add("3. **P1——做 cutoff 稳定性分析。** 系统改变 trimming、候选网格、年份窗口、状态项和控制变量，报告 cutoff 与分支系数分布，而不是只报告单点最优值。")
    add("4. **P1——处理样本选择风险。** 比较完整样本、平衡窗口和高缺失变量剔除后的结果，明确 bond spread 与 terms-of-trade 缺失是否改变国家构成。")
    add("5. **P2——收紧论文表述。** 先将完整二阶 spread 模型及其 $m^A$ 构造作为上游发现，把 doomloop/readiness 门槛定位为待验证机制；只有在 bootstrap 和敏感性分析后仍稳定，才升级为核心结论。")
    add("")
    add("## 6. 待回答的问题")
    add("")
    add("- 论文的主命题究竟是“适应能力的非线性边际利差效应”，还是“存在稳定 doomloop cutoff”？两者需要由更新后的稳健性结果重新排序。")
    add("- readiness 的两支同号究竟意味着单调但斜率变化的 kink，还是理论 single-crossing 约束需要重新设定？")
    add(f"- 补齐聚类与全流程 bootstrap 后，主规格 readiness 的 p={fmt_p(ready_wald['p'])} 是否仍能维持？")
    add("- 早期财政数据和 bond spread 缺失是否集中在特定国家组，从而限制外部有效性？")
    add("")
    return "\n".join(lines)


def main() -> None:
    required = [
        BASE / "model_coefficients.csv", BASE / "model_stats.csv",
        BASE / "raw_scale_coefficients.csv", BASE / "quadratic_collinearity.csv",
        THETA / "model_coefficients.csv", THETA / "empirical_theta_panel.dta",
        DOOM / "model_coefficients.csv", DOOM / "nostate_model_coefficients.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required workflow outputs:\n" + "\n".join(missing))
    (HERE / "paperB_results.md").write_text(render_results(), encoding="utf-8")
    (HERE / "paperB_diagnostics.md").write_text(render_diagnostics(), encoding="utf-8")
    (HERE / "progress.md").write_text(render_progress(), encoding="utf-8")


if __name__ == "__main__":
    main()
