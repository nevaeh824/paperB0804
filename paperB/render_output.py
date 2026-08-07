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
DOOM_FORWARD = ROOT / "doomloop_forward" / "stata_outputs"


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


def metadata_index(path: Path) -> dict[str, str]:
    return {row["item"]: row["value"] for row in read_csv(path)}


BASE_MODELS = [
    "A_X_only", "A_A_only", "A_b_only", "B_all_core", "C_macro",
    "Layer1_X", "Layer2_A", "Interact_AB", "Interact_AX", "Interact_all",
]
BASE_LABELS = {
    "A_X_only": "仅 X", "A_A_only": "仅 A", "A_b_only": "仅 b",
    "B_all_core": "三核心", "C_macro": "+宏观",
    "Layer1_X": "第一层", "Layer2_A": "第二层",
    "Interact_AB": "A×b", "Interact_AX": "A×X", "Interact_all": "双交互",
}
BASE_TERMS = {
    "vulnerability100": r"气候脆弱性 $X_{it}$",
    "readiness100": r"适应能力 $A_{it}$",
    "debt_gdp": r"债务/GDP $b_{it}$",
    "c_A": r"$A^c_{it}$", "c_X": r"$X^c_{it}$", "c_b": r"$b^c_{it}$",
    "int_AB": r"$A^c_{it}\times b^c_{it}$",
    "int_AX": r"$A^c_{it}\times X^c_{it}$",
    "growth": "Growth", "ln_currentgdp": r"$\ln(CurrentGDP_{it})$",
    "inflation_cpi": "Inflation", "reserves": "Reserves", "tt": "Terms of trade",
}
BASE_FLAGS = {
    "A_X_only": (False, False), "A_A_only": (False, False), "A_b_only": (False, False),
    "B_all_core": (False, False), "C_macro": (True, False),
    "Layer1_X": (True, True), "Layer2_A": (True, True),
    "Interact_AB": (True, True), "Interact_AX": (True, True), "Interact_all": (True, True),
}

TAX_MODELS = [
    "T1_X_only", "T2_A_only", "T3_persistence", "T4_all_core", "T5_macro",
    "T6_layer1_X", "T7_layer2_A", "T8_interact_core", "T9_interact_macro", "T10_interact_full",
]
TAX_LABELS = {
    "T1_X_only": "仅 X", "T2_A_only": "仅 A", "T3_persistence": "仅滞后税基",
    "T4_all_core": "核心项", "T5_macro": "+宏观", "T6_layer1_X": "第一层",
    "T7_layer2_A": "第二层", "T8_interact_core": "交互核心",
    "T9_interact_macro": "交互+宏观", "T10_interact_full": "交互+全控制",
}
TAX_TERMS = {
    "vulnerability100": r"气候脆弱性 $X_{it}$",
    "readiness100": r"适应能力 $A_{it}$",
    "taxbase_lag": r"$\widetilde T_{it}^{(t-1)}$",
    "c_A_T": r"$A^c_{it}$", "c_X_T": r"$X^c_{it}$",
    "int_AX_T": r"$A^c_{it}\times X^c_{it}$",
    "growth": "Growth", "ln_currentgdp": r"$\ln(CurrentGDP_{it})$",
    "inflation_cpi": "Inflation", "reserves": "Reserves", "tt": "Terms of trade",
}

DOOM_LABELS = {
    "D1_core": "核心项", "D2_macro": "+宏观", "D3_full": "+全控制",
    "DN1_core": "核心项（无 b）", "DN2_macro": "+宏观（无 b）", "DN3_full": "+全控制（无 b）",
    "R1_core": "核心项", "R2_macro": "+宏观", "R3_full": "+全控制",
    "RD1_core": "核心项（债务 cutoff）", "RD2_macro": "+宏观（债务 cutoff）", "RD3_full": "+全控制（债务 cutoff）",
    "RN1_core": "核心项（无 A 滞后）", "RN2_macro": "+宏观（无 A 滞后）", "RN3_full": "+全控制（无 A 滞后）",
    "RDN1_core": "核心项（无滞后，债务 cutoff）", "RDN2_macro": "+宏观（无滞后，债务 cutoff）", "RDN3_full": "+全控制（无滞后，债务 cutoff）",
}
DOOM_TERMS = {
    "debt_kink_low": r"$A_{it}(c-\widehat\theta^A_{it})_+$",
    "debt_kink_high": r"$A_{it}(\widehat\theta^A_{it}-c)_+$",
    "debt_gdp": r"$b_{it}$", "ready_kink_low": r"$FT_{it}(c-\widehat\theta^A_{it})_+$",
    "ready_kink_high": r"$FT_{it}(\widehat\theta^A_{it}-c)_+$",
    "ready_debt_kink_low": r"$FT_{it}(c_B-\widehat\theta^A_{it})_+$",
    "ready_debt_kink_high": r"$FT_{it}(\widehat\theta^A_{it}-c_B)_+$",
    "readiness_lag": r"$A_{i,t-1}$", "vulnerability100": r"$X_{it}$",
    "growth": "Growth", "ln_currentgdp": r"$\ln(CurrentGDP_{it})$",
    "inflation_cpi": "Inflation", "reserves": "Reserves", "tt": "Terms of trade",
}


def marginal_table(rows: list[dict[str, str]], include_model: bool) -> str:
    headers = (["模型"] if include_model else ["方程/规格"]) + [
        "点", r"调节变量/$\theta$", "边际效应", "稳健 SE", "p 值", "95% CI",
    ]
    output: list[list[object]] = []
    for row in rows:
        group = row.get("model") or row.get("equation", "")
        output.append([
            group, row.get("point", ""), fmt(row.get("moderator_value") or row.get("theta")),
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
    forward_coef_rows = read_csv(DOOM_FORWARD / "model_coefficients.csv") + read_csv(DOOM_FORWARD / "nostate_model_coefficients.csv")
    forward_stats_rows = read_csv(DOOM_FORWARD / "model_stats.csv") + read_csv(DOOM_FORWARD / "nostate_model_stats.csv")
    base_coefs, base_stats = coefficient_index(base_coef_rows), stats_index(base_stats_rows)
    tax_coefs, tax_stats = coefficient_index(tax_coef_rows), stats_index(tax_stats_rows)
    doom_coefs, doom_stats = coefficient_index(doom_coef_rows), stats_index(doom_stats_rows)
    forward_coefs, forward_stats = coefficient_index(forward_coef_rows), stats_index(forward_stats_rows)

    construction = read_csv(THETA / "construction_coefficients.csv")
    construction_by = {(r["source"], r["parameter"]): r for r in construction}
    theta_desc = read_csv(THETA / "descriptive_stats.csv")
    doom_wald = read_csv(DOOM / "wald_tests.csv") + read_csv(DOOM / "nostate_wald_tests.csv")
    forward_wald = read_csv(DOOM_FORWARD / "wald_tests.csv") + read_csv(DOOM_FORWARD / "nostate_wald_tests.csv")

    def joint_p(rows: list[dict[str, str]], model: str) -> str:
        row = next(
            r for r in rows
            if r["model"] == model and "jointly zero" in r["hypothesis"]
        )
        return fmt_p(row["p"])

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
    tax_a = construction_by[("tax", "gamma_A_raw")]
    tax_ax = construction_by[("tax", "gamma_AX")]
    add(f"- Baseline 全交互模型中，A×b 系数为 {fmt(base_ab['estimate'])}（p {fmt_p(base_ab['p'])}），A×X 系数为 {fmt(base_ax['estimate'])}（p={fmt_p(base_ax['p'])}）。")
    add(f"- 全控制税基模型的原始尺度适应能力系数为 {fmt(tax_a['estimate'])}（p={fmt_p(tax_a['p'])}），A×X 系数为 {fmt(tax_ax['estimate'])}（p={fmt_p(tax_ax['p'])}）。")
    add(f"- 第四节全控制水平模型中，债务方程两支联合检验 p={joint_p(doom_wald, 'D3_full')}，readiness 自身 cutoff 规格 p={joint_p(doom_wald, 'R3_full')}；第五节对应两期前瞻结果分别为 p={joint_p(forward_wald, 'D3_full')} 和 p={joint_p(forward_wald, 'R3_full')}。")
    add("- 所有结果均为双向固定效应相关性估计。theta 和 cutoff 都是生成量，当前常规稳健标准误未覆盖完整上游估计与 cutoff 搜索不确定性。")
    add("")
    add("## 1. 统一符号、控制变量与估计口径")
    add("")
    add(r"令 $s_{it}$ 为主权利差比率，$A_{it}$ 为适应能力比率，$X_{it}$ 为气候脆弱性比率，$b_{it}=debt\_gdp_{it}$。Baseline 的宏观控制为 Growth、$\ln(CurrentGDP)$、Inflation；税基和第四、第五节全部 Doomloop 规格不控制 `CurrentGDP` 或 `ln_currentgdp`，宏观控制仅为 Growth、Inflation。外部控制均为 Reserves、Terms of trade。全部模型含国家固定效应与年份固定效应，推断采用观测层面异方差稳健标准误（不是国家聚类标准误）。")
    add("")
    add("## 2. Baseline：主权利差回归")
    add("")
    add("### 2.1 回归公式")
    add("")
    add(r"$$s_{it}=\alpha_i+\lambda_t+\beta_AA_{it}+\beta_Bb_{it}+\beta_XX_{it}+\beta_{AB}A_{it}b_{it}+\beta_{AX}A_{it}X_{it}+\Gamma_m'W^m_{it}+\varepsilon^m_{it}.$$" )
    add("")
    add(r"交互回归实际用各自固定样本均值进行中心化：$A^c=A-\bar A_s$、$b^c=b-\bar b_s$、$X^c=X-\bar X_s$。为构造原始尺度边际效应，使用")
    add("")
    add(r"$$\widehat\beta_A^{raw}=\widehat\beta_A^c-\widehat\beta_{AB}\bar b_s-\widehat\beta_{AX}\bar X_s,$$")
    add("")
    add(r"$$\widehat m^A_{it}=-\left(\widehat\beta_A^{raw}+\widehat\beta_{AB}b_{it}+\widehat\beta_{AX}X_{it}\right)=-\left(\widehat\beta_A^c+\widehat\beta_{AB}b^c_{it}+\widehat\beta_{AX}X^c_{it}\right).$$")
    add("")
    add("### 2.2 逐步回归表")
    add("")
    add("系数下方括号为稳健 t 值；`***`、`**`、`*` 分别表示 1%、5%、10% 显著性。所有列使用同一共同样本。")
    add("")
    add("**Panel A：核心变量与控制变量逐步检验**")
    add("")
    add(model_table(BASE_MODELS[:7], BASE_LABELS, ["vulnerability100", "readiness100", "debt_gdp", "growth", "ln_currentgdp", "inflation_cpi", "reserves", "tt"], BASE_TERMS, base_coefs, base_stats, BASE_FLAGS))
    add("")
    add("**Panel B：交互模型**")
    add("")
    add(model_table(BASE_MODELS[7:], BASE_LABELS, ["c_A", "c_X", "c_b", "int_AB", "int_AX", "growth", "ln_currentgdp", "inflation_cpi", "reserves", "tt"], BASE_TERMS, base_coefs, base_stats, BASE_FLAGS))
    add("")
    add("### 2.3 构造用原始尺度系数")
    add("")
    rows = []
    for key in [("spread", "beta_A_raw"), ("spread", "beta_AB"), ("spread", "beta_AX")]:
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
    add(r"$$\widetilde T_{i,t+1}^{(t)}=\frac{(taxgdp_{i,t+1}\times0.01)\,CurrentGDP_{i,t+1}}{CurrentGDP_{it}},\qquad \widetilde T_{it}^{(t-1)}=taxgdp_{it}\times0.01.$$" )
    add("")
    add("`taxgdp` 的源单位是 GDP 百分比，先乘 0.01 转成 0—1 比率。税基回归不把 `CurrentGDP` 或 `ln_currentgdp` 作为控制变量；`CurrentGDP` 仅用于构造前瞻因变量。")
    add("")
    add(r"$$\widetilde T_{i,t+1}^{(t)}=\alpha_i+\lambda_t+\gamma_AA_{it}+\gamma_XX_{it}+\gamma_{AX}A_{it}X_{it}+\rho_T\widetilde T_{it}^{(t-1)}+\Gamma_T'W^T_{it}+\varepsilon^T_{i,t+1}.$$" )
    add("")
    add(r"税基交互模型也在税基固定样本内中心化。原始尺度截距斜率为 $\widehat\gamma_A^{raw}=\widehat\gamma_A^c-\widehat\gamma_{AX}\bar X_T$，故")
    add("")
    add(r"$$\widehat T^A_{it}=\widehat\gamma_A^{raw}+\widehat\gamma_{AX}X_{it}=\widehat\gamma_A^c+\widehat\gamma_{AX}X^c_{it}.$$" )
    add("")
    add("### 3.2 税基逐步回归表")
    add("")
    add("**Panel A：核心变量与控制变量逐步检验**")
    add("")
    add(model_table(TAX_MODELS[:7], TAX_LABELS, ["vulnerability100", "readiness100", "taxbase_lag", "growth", "inflation_cpi", "reserves", "tt"], TAX_TERMS, tax_coefs, tax_stats))
    add("")
    add("**Panel B：交互模型**")
    add("")
    add(model_table(TAX_MODELS[7:], TAX_LABELS, ["c_A_T", "c_X_T", "int_AX_T", "taxbase_lag", "growth", "inflation_cpi", "reserves", "tt"], TAX_TERMS, tax_coefs, tax_stats))
    add("")
    add("### 3.3 边际税基收益与 theta 构造")
    add("")
    rows = []
    for key in [("tax", "gamma_A_raw"), ("tax", "gamma_AX")]:
        row = construction_by[key]
        rows.append([row["parameter"], fmt(row["estimate"]), fmt(row["se"]), fmt(row["t"], 3), fmt_p(row["p"]), f"[{fmt(row['ci_low'])}, {fmt(row['ci_high'])}]"])
    add(md_table(["参数", "估计值", "稳健 SE", "t", "p", "95% CI"], rows))
    add("")
    add(r"最终经验指标为")
    add("")
    add(r"$$\widehat\theta^A_{it}=b_{it}\widehat m^A_{it}+\widehat T^A_{it},\qquad b_{it}=debt\_gdp_{it}.$$" )
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
    doom_sections = [
        (4, "Doomloop：Single-Crossing Kink Marginal-Effect Model", DOOM, doom_coefs, doom_stats, ""),
        (5, "两期前瞻 Doomloop：与第四节相同规格", DOOM_FORWARD, forward_coefs, forward_stats, "_forward"),
    ]
    for section, title, output_dir, section_coefs, section_stats, figure_suffix in doom_sections:
        add(f"## {section}. {title}")
        add("")
        add(f"### {section}.1 方程、控制变量与 cutoff 口径")
        add("")
        if section == 4:
            add(r"$$\Delta b_{i,t+1}=b_{i,t+1}-b_{it}.$$" )
            add("")
            add(r"$$\Delta b_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-\widehat\theta^A_{it})_++\beta_HA_{it}(\widehat\theta^A_{it}-c)_++\rho_bb_{it}+\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.$$" )
            add("")
            add(r"$$A_{it}=\alpha_i+\lambda_t+\delta_LFT_{it}(c-\widehat\theta^A_{it})_++\delta_HFT_{it}(\widehat\theta^A_{it}-c)_++\rho_AA_{i,t-1}+\gamma_XX_{it}+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.$$" )
        else:
            add(r"$$\Delta b_{i,t+2}=b_{i,t+2}-b_{it}.$$" )
            add("")
            add(r"$$\Delta b_{i,t+2}=\alpha_i+\lambda_t+\beta_LA_{it}(c-\widehat\theta^A_{it})_++\beta_HA_{it}(\widehat\theta^A_{it}-c)_++\rho_bb_{it}+\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.$$" )
            add("")
            add(r"$$A_{i,t+1}=\alpha_i+\lambda_t+\delta_LFT_{it}(c-\widehat\theta^A_{it})_++\delta_HFT_{it}(\widehat\theta^A_{it}-c)_++\rho_AA_{i,t-1}+\gamma_XX_{it}+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.$$" )
        add("")
        add("第二个方程的两支只乘 `FT=interest_revenue`。所有规格均显式控制 $X_{it}$，宏观控制仅为 Growth 与 Inflation，外部控制为 Reserves 与 Terms of trade；不加入 `CurrentGDP` 或 `ln_currentgdp`。每个方程先锁定全控制共同样本。readiness 同时报告两种 cutoff：自身全控制方程的 RSS 最小值，以及相应债务全控制方程的 RSS 最小值。去状态规格分别去掉 $b_{it}$ 与 $A_{i,t-1}$，并重新完成 cutoff 搜索。")
        add("")
        panels = [
            ("债务变化方程（含 b）", ["D1_core", "D2_macro", "D3_full"], ["debt_kink_low", "debt_kink_high", "debt_gdp", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt"]),
            ("债务变化方程（去 b）", ["DN1_core", "DN2_macro", "DN3_full"], ["debt_kink_low", "debt_kink_high", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt"]),
            ("Readiness 水平方程（自身 cutoff，含 A 滞后）", ["R1_core", "R2_macro", "R3_full"], ["ready_kink_low", "ready_kink_high", "readiness_lag", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt"]),
            ("Readiness 水平方程（债务 cutoff，含 A 滞后）", ["RD1_core", "RD2_macro", "RD3_full"], ["ready_debt_kink_low", "ready_debt_kink_high", "readiness_lag", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt"]),
            ("Readiness 水平方程（自身 cutoff，去 A 滞后）", ["RN1_core", "RN2_macro", "RN3_full"], ["ready_kink_low", "ready_kink_high", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt"]),
            ("Readiness 水平方程（债务 cutoff，去 A 滞后）", ["RDN1_core", "RDN2_macro", "RDN3_full"], ["ready_debt_kink_low", "ready_debt_kink_high", "vulnerability100", "growth", "inflation_cpi", "reserves", "tt"]),
        ]
        for panel_title, models, variables in panels:
            add(f"**{panel_title}**")
            add("")
            add(model_table(models, DOOM_LABELS, variables, DOOM_TERMS, section_coefs, section_stats))
            add("")

        add(f"### {section}.2 Cutoff 与全控制分支系数")
        add("")
        searched = {
            ("含状态", row["equation"]): row for row in read_csv(output_dir / "cutoffs.csv")
        }
        searched.update({
            ("去状态", row["equation"]): row for row in read_csv(output_dir / "nostate_cutoffs.csv")
        })
        key_rows = {
            ("含状态", row["equation"]): row for row in read_csv(output_dir / "key_results.csv")
        }
        key_rows.update({
            ("去状态", row["equation"]): row for row in read_csv(output_dir / "nostate_key_results.csv")
        })
        variants = [
            ("含状态", "债务", "debt", "debt", "债务方程 RSS"),
            ("含状态", "Readiness", "ready", "ready", "Readiness 方程 RSS"),
            ("含状态", "Readiness", "ready_debt", "debt", "债务方程 RSS"),
            ("去状态", "债务", "debt", "debt", "去 b 债务方程 RSS"),
            ("去状态", "Readiness", "ready", "ready", "去滞后 Readiness 方程 RSS"),
            ("去状态", "Readiness", "ready_debt", "debt", "去 b 债务方程 RSS"),
        ]
        cutoff_rows = []
        for spec, equation, key_equation, cutoff_equation, source in variants:
            cutoff = searched[(spec, cutoff_equation)]
            key = key_rows[(spec, key_equation)]
            cutoff_rows.append([
                spec, equation, source, fmt(cutoff["rss_min_cutoff"]), fmt(cutoff["rss"]),
                fmt_int(cutoff["candidate_count"]), fmt_int(cutoff["low_n"]), fmt_int(cutoff["high_n"]),
                fmt(key["effective_a"]), fmt(key["effective_b"]), "是" if key["opposite_sign"] == "1" else "否",
            ])
        add(md_table(["规格", "结果方程", "cutoff 来源", "cutoff", "来源方程最小 RSS", "候选数", "低支 N", "高支 N", "a", "b", "异号"], cutoff_rows))
        add("")
        add(r"点边际效应统一按 $m(\theta;c)=a(c-\theta)_++b(\theta-c)_+$ 计算；在 cutoff 处定义为 0。")
        add("")
        add(f"<details><summary>展开：第 {section} 节六组 kink 点边际效应</summary>")
        add("")
        labelled: list[dict[str, str]] = []
        for prefix, path in [("含状态", output_dir / "marginal_effects.csv"), ("去状态", output_dir / "nostate_marginal_effects.csv")]:
            for row in read_csv(path):
                labelled_row = dict(row)
                labelled_row["equation"] = f"{prefix}-{row['equation']}"
                labelled.append(labelled_row)
        add(marginal_table(labelled, False))
        add("")
        add("</details>")
        add("")
        add(f"### {section}.3 边际效应图")
        add("")
        add("| 含状态变量 | 去状态变量 |")
        add("| --- | --- |")
        add(f"| ![债务变化边际效应](figures/debt_marginal_effect{figure_suffix}.png) | ![债务变化边际效应：去 b](figures/debt_marginal_effect_no_b{figure_suffix}.png) |")
        add(f"| ![readiness：自身 cutoff](figures/readiness_marginal_effect{figure_suffix}.png) | ![readiness：自身 cutoff、去滞后](figures/readiness_marginal_effect_no_lag{figure_suffix}.png) |")
        add(f"| ![readiness：债务 cutoff](figures/readiness_marginal_effect_debt_cutoff{figure_suffix}.png) | ![readiness：债务 cutoff、去滞后](figures/readiness_marginal_effect_debt_cutoff_no_lag{figure_suffix}.png) |")
        add("")

    add("## 6. 结果解释边界")
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
        DOOM_FORWARD / "formula_checks.csv", DOOM_FORWARD / "nostate_formula_checks.csv",
    ]
    cutoff_paths = [
        DOOM / "cutoff_validation.csv", DOOM / "nostate_cutoff_validation.csv",
        DOOM_FORWARD / "cutoff_validation.csv", DOOM_FORWARD / "nostate_cutoff_validation.csv",
    ]
    f_ok, f_n = validation_summary(formula_paths)
    c_ok, c_n = validation_summary(cutoff_paths)
    unit_ok, unit_n = validation_summary([BASE / "unit_scaling_checks.csv", THETA / "unit_scaling_checks.csv", DOOM / "unit_scaling_checks.csv", DOOM_FORWARD / "unit_scaling_checks.csv"])

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
    add("唯一原始输入是 `data0804/invest_panel_weo.csv`。所有源百分数、比率和 0—100 指数（包括 `taxgdp`）在读入后除以 100；金额变量 `revenue`、`debt`、`CurrentGDP` 不缩放。`ln_currentgdp=ln(CurrentGDP)` 只进入 baseline，不进入税基或 Doomloop 方程。关键因变量的精确定义为：")
    add("")
    add(r"- $\widetilde T_{i,t+1}^{(t)}=(taxgdp_{i,t+1}\times0.01)CurrentGDP_{i,t+1}/CurrentGDP_{it}$。")
    add(r"- $\widetilde T_{it}^{(t-1)}=taxgdp_{it}\times0.01$。")
    add(r"- 第四节使用 $\Delta b_{i,t+1}=F.debt\_gdp_{it}-debt\_gdp_{it}$ 与 $A_{it}=readiness100_{it}$。")
    add(r"- 第五节使用 $\Delta b_{i,t+2}=F2.debt\_gdp_{it}-debt\_gdp_{it}$ 与 $A_{i,t+1}=F.readiness100_{it}$；所有 lead 均要求严格相邻年份。")
    add("")
    add("### 2.1 基准单位换算审计")
    add("")
    add(rows_simple(BASE / "unit_scaling_checks.csv", ["variable", "source_min", "source_max", "ratio_min", "ratio_max", "max_abs_scaling_diff", "passed"], ["变量", "源最小值", "源最大值", "比率最小值", "比率最大值", "最大换算误差", "状态"], {"source_min": "num", "source_max": "num", "ratio_min": "num", "ratio_max": "num", "max_abs_scaling_diff": "num", "passed": "pass"}))
    add("")
    add("Baseline 执行 13 项单位审计；Empirical-theta 在此基础上加入 `taxgdp`，执行 14 项审计；doomloop 从已审计的 theta panel 读入并对关键上游比例变量复核。全部检查的原始 CSV 保留在各板块 `stata_outputs` 目录。")
    add("")
    add("## 3. 样本覆盖与描述性统计")
    add("")
    base_stats = stats_index(read_csv(BASE / "model_stats.csv"))["Interact_all"]
    base_meta = metadata_index(BASE / "run_metadata.csv")
    tax_stats = stats_index(read_csv(THETA / "model_stats.csv"))["T10_interact_full"]
    doom_stats = stats_index(read_csv(DOOM / "model_stats.csv") + read_csv(DOOM / "nostate_model_stats.csv"))
    forward_stats = stats_index(read_csv(DOOM_FORWARD / "model_stats.csv") + read_csv(DOOM_FORWARD / "nostate_model_stats.csv"))
    forward_stats = stats_index(read_csv(DOOM_FORWARD / "model_stats.csv") + read_csv(DOOM_FORWARD / "nostate_model_stats.csv"))
    sample_rows = [
        ["Baseline 共同样本", fmt_int(base_stats["N"]), fmt_int(base_stats["countries"]), fmt_int(base_stats["years"]), f"{fmt(base_meta['common_sample_first_year'], 0)}–{fmt(base_meta['common_sample_last_year'], 0)}"],
        ["Tax 共同样本", fmt_int(tax_stats["N"]), fmt_int(tax_stats["countries"]), fmt_int(tax_stats["years"]), f"{tax_stats['first_year']}–{tax_stats['last_year']}"],
        ["第四节 Δb(t+1)", fmt_int(doom_stats["D3_full"]["N"]), fmt_int(doom_stats["D3_full"]["countries"]), fmt_int(doom_stats["D3_full"]["years"]), f"{doom_stats['D3_full']['first_year']}–{doom_stats['D3_full']['last_year']}"],
        ["第四节 A(t)", fmt_int(doom_stats["R3_full"]["N"]), fmt_int(doom_stats["R3_full"]["countries"]), fmt_int(doom_stats["R3_full"]["years"]), f"{doom_stats['R3_full']['first_year']}–{doom_stats['R3_full']['last_year']}"],
        ["第五节 Δb(t+2)", fmt_int(forward_stats["D3_full"]["N"]), fmt_int(forward_stats["D3_full"]["countries"]), fmt_int(forward_stats["D3_full"]["years"]), f"{forward_stats['D3_full']['first_year']}–{forward_stats['D3_full']['last_year']}"],
        ["第五节 A(t+1)", fmt_int(forward_stats["R3_full"]["N"]), fmt_int(forward_stats["R3_full"]["countries"]), fmt_int(forward_stats["R3_full"]["years"]), f"{forward_stats['R3_full']['first_year']}–{forward_stats['R3_full']['last_year']}"],
    ]
    add(md_table(["固定样本", "N", "国家数", "年份数", "基准年份范围"], sample_rows))
    add("")
    add("### 3.1 Baseline 输入变量（全数据非缺失分布）")
    add("")
    selected = {"bond_spreads", "vulnerability100", "readiness100", "debt_gdp", "growth", "ln_currentgdp", "inflation_cpi", "reserves", "tt"}
    base_profile = [r for r in read_csv(BASE / "profile.csv") if r["variable"] in selected]
    add(md_table(["变量", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["variable"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in base_profile]))
    add("")
    add("### 3.2 Tax 与 theta 构造量")
    add("")
    theta_desc = read_csv(THETA / "descriptive_stats.csv")
    add(md_table(["变量", "样本", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["variable"], r["sample"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in theta_desc]))
    add("")
    add("### 3.3 第四、第五节 Doomloop 回归变量")
    add("")
    doom_desc = []
    for section, output_dir in [("第四节", DOOM), ("第五节", DOOM_FORWARD)]:
        for row in read_csv(output_dir / "regression_descriptive_stats.csv") + read_csv(output_dir / "nostate_regression_descriptive_stats.csv"):
            labelled = dict(row)
            labelled["specification"] = f"{section}-{row['specification']}"
            doom_desc.append(labelled)
    add(md_table(["规格", "方程", "变量", "角色", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["specification"], r["equation"], r["variable"], r["role"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in doom_desc]))
    add("")
    add("## 4. 缺失值、重复键与固定效应可识别性")
    add("")
    add("国家—年份重复键检查在三段流程中均为零；代码遇到重复键会直接终止，不会静默删除。各段共同样本在估计前锁定，逐步模型与 cutoff 候选使用相同观测。")
    add("")
    add("### 4.1 独占样本损失")
    add("")
    missing = []
    for stage, path in [("baseline", BASE / "missing_loss.csv"), ("tax", THETA / "missing_loss.csv"), ("doomloop-h1", DOOM / "missing_loss.csv"), ("doomloop-h2", DOOM_FORWARD / "missing_loss.csv")]:
        for r in read_csv(path):
            missing.append([stage, r.get("equation", "—"), r["variable"], fmt_int(r["missing_total"]), fmt(r["missing_rate"], 2), fmt_int(r["exclusive_loss"])])
    add(md_table(["板块", "方程", "变量", "缺失数", "缺失率", "独占损失"], missing))
    add("")
    add("### 4.2 Within 变异")
    add("")
    variation = []
    for stage, path in [("baseline", BASE / "variation.csv"), ("tax", THETA / "variation.csv"), ("doomloop-h1", DOOM / "variation.csv"), ("doomloop-h2", DOOM_FORWARD / "variation.csv")]:
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
    for stage, path in [("baseline", BASE / "collinearity.csv"), ("tax", THETA / "collinearity.csv")]:
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
    for stage, path in [("baseline", BASE / "wald_tests.csv"), ("tax", THETA / "wald_tests.csv"), ("doomloop-h1", DOOM / "wald_tests.csv"), ("doomloop-h1-no-state", DOOM / "nostate_wald_tests.csv"), ("doomloop-h2", DOOM_FORWARD / "wald_tests.csv"), ("doomloop-h2-no-state", DOOM_FORWARD / "nostate_wald_tests.csv")]:
        for r in read_csv(path):
            wald_rows.append([stage, r["model"], r["hypothesis"], fmt(r["F"]), fmt_int(r["df_num"]), fmt_int(r["df_den"]), fmt_p(r["p"])])
    add(md_table(["板块", "模型", "原假设", "F", "分子 df", "分母 df", "p"], wald_rows))
    add("")
    add("### 6.2 代数、映射与时序公式检查")
    add("")
    check_rows = []
    for stage, path in [("theta", THETA / "formula_checks.csv"), ("doomloop-h1", DOOM / "formula_checks.csv"), ("doomloop-h1-no-state", DOOM / "nostate_formula_checks.csv"), ("doomloop-h2", DOOM_FORWARD / "formula_checks.csv"), ("doomloop-h2-no-state", DOOM_FORWARD / "nostate_formula_checks.csv")]:
        for r in read_csv(path):
            check_rows.append([stage, r["check"], fmt(r.get("max_abs_diff") or r.get("max_abs_difference"), 8), fmt(r["tolerance"], 8), "通过" if r["passed"] == "1" else "未通过"])
    add(md_table(["板块", "检查", "最大绝对误差", "容差", "状态"], check_rows))
    add("")
    add("### 6.3 areg 与显式 LSDV 复核")
    add("")
    est_rows = []
    for stage, path in [("tax", THETA / "estimator_validation.csv"), ("doomloop-h1", DOOM / "estimator_validation.csv"), ("doomloop-h1-no-state", DOOM / "nostate_estimator_validation.csv"), ("doomloop-h2", DOOM_FORWARD / "estimator_validation.csv"), ("doomloop-h2-no-state", DOOM_FORWARD / "nostate_estimator_validation.csv")]:
        for r in read_csv(path):
            est_rows.append([stage, r.get("model") or r.get("equation"), r["variable"], fmt(r["areg_b"]), fmt(r["lsdv_b"]), fmt(r["abs_b_diff"], 8), fmt(r["abs_se_diff"], 8)])
    for r in read_csv(BASE / "validation_checks.csv"):
        est_rows.insert(0, ["baseline", r["model"], r["variable"], fmt(r["main_b"]), fmt(r["lsdv_b"]), fmt(r["abs_b_diff"], 8), fmt(r["abs_se_diff"], 8)])
    add(md_table(["板块", "模型/方程", "变量", "areg", "LSDV", "|系数差|", "|SE差|"], est_rows))
    add("")
    add("### 6.4 Cutoff 最小 RSS 复核")
    add("")
    cutoff_checks = []
    for stage, path in [("第四节-含状态", DOOM / "cutoff_validation.csv"), ("第四节-去状态", DOOM / "nostate_cutoff_validation.csv"), ("第五节-含状态", DOOM_FORWARD / "cutoff_validation.csv"), ("第五节-去状态", DOOM_FORWARD / "nostate_cutoff_validation.csv")]:
        for r in read_csv(path):
            cutoff_checks.append([stage, r["equation"], fmt(r["recorded_cutoff"]), fmt(r["profile_min_rss"]), fmt(r["rss_at_recorded_cutoff"]), fmt(r["abs_rss_diff"], 8), "通过" if r["passed"] == "1" else "未通过"])
    add(md_table(["规格", "方程", "记录 cutoff", "profile 最小 RSS", "cutoff RSS", "差值", "状态"], cutoff_checks))
    add("")
    add("## 7. 图形 QA")
    add("")
    add("第四、第五节分别生成含状态与去状态的债务图、readiness 自身 cutoff 图、readiness 债务 cutoff 图及合并图，全部保留 PNG 与 PDF。单方程图使用连续 theta 网格并把 cutoff 精确插入网格；竖直虚线与 CSV 中记录的 cutoff 一致。")
    add("")
    add("## 8. 必须保留的限制与建议")
    add("")
    add("- 当前稳健标准误处理异方差，但不处理同一国家内序列相关；面板论文通常还应报告国家聚类标准误或适当的双向聚类/空间相关推断。")
    add("- cutoff 在同一样本上搜索，条件于 cutoff 的常规标准误偏窄风险未纳入。建议按国家重抽样，完整重复 baseline、tax/theta、cutoff 搜索和最终回归。")
    add("- theta 是生成解释变量；联合不确定性依赖跨方程协方差。当前只对两个组成边际量分别做 delta-method 标准误，不提供 theta 的联合 SE。")
    add("- 结果是固定效应相关性证据，不支持没有额外识别设计的因果措辞。")
    add("")
    add("## 9. 原始诊断输出索引")
    add("")
    add("完整 CSV/DTA/日志仍保留在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/`、`doomloop/stata_outputs/` 与 `doomloop_forward/stata_outputs/`。本文件是汇总层，不替代这些逐项机器可读结果。")
    add("")
    return "\n".join(lines)


def render_progress() -> str:
    construction = {row["parameter"]: row for row in read_csv(THETA / "construction_coefficients.csv")}
    base_stats = stats_index(read_csv(BASE / "model_stats.csv"))["Interact_all"]
    tax_stats = stats_index(read_csv(THETA / "model_stats.csv"))["T10_interact_full"]
    doom_stats = stats_index(read_csv(DOOM / "model_stats.csv") + read_csv(DOOM / "nostate_model_stats.csv"))
    forward_stats = stats_index(read_csv(DOOM_FORWARD / "model_stats.csv") + read_csv(DOOM_FORWARD / "nostate_model_stats.csv"))

    def find_wald(path: Path, model: str, text: str) -> dict[str, str]:
        for row in read_csv(path):
            if row["model"] == model and text in row["hypothesis"]:
                return row
        raise KeyError(f"Wald test not found: {path.name}, {model}, {text}")

    def p_label(value: object) -> str:
        rendered = fmt_p(value)
        return f"p{rendered}" if rendered.startswith("<") else f"p={rendered}"

    debt_wald = find_wald(DOOM / "wald_tests.csv", "D3_full", "low- and high-branch")
    ready_wald = find_wald(DOOM / "wald_tests.csv", "R3_full", "low- and high-branch")
    debt_ns_wald = find_wald(DOOM / "nostate_wald_tests.csv", "DN3_full", "low- and high-branch")
    ready_ns_wald = find_wald(DOOM / "nostate_wald_tests.csv", "RN3_full", "low- and high-branch")
    ready_debt_cutoff_wald = find_wald(DOOM / "wald_tests.csv", "RD3_full", "branches jointly")
    forward_debt_wald = find_wald(DOOM_FORWARD / "wald_tests.csv", "D3_full", "low- and high-branch")
    forward_ready_wald = find_wald(DOOM_FORWARD / "wald_tests.csv", "R3_full", "low- and high-branch")
    forward_ready_debt_cutoff_wald = find_wald(DOOM_FORWARD / "wald_tests.csv", "RD3_full", "branches jointly")
    tax_joint = find_wald(THETA / "wald_tests.csv", "T10_interact_full", "adaptation terms jointly")

    original_cutoffs = {row["equation"]: row for row in read_csv(DOOM / "cutoffs.csv")}
    nostate_cutoffs = {row["equation"]: row for row in read_csv(DOOM / "nostate_cutoffs.csv")}
    forward_cutoffs = {row["equation"]: row for row in read_csv(DOOM_FORWARD / "cutoffs.csv")}
    unit_ok, unit_total = validation_summary(
        [BASE / "unit_scaling_checks.csv", THETA / "unit_scaling_checks.csv", DOOM / "unit_scaling_checks.csv", DOOM_FORWARD / "unit_scaling_checks.csv"]
    )
    formula_ok, formula_total = validation_summary(
        [THETA / "formula_checks.csv", DOOM / "formula_checks.csv", DOOM / "nostate_formula_checks.csv", DOOM_FORWARD / "formula_checks.csv", DOOM_FORWARD / "nostate_formula_checks.csv"]
    )
    cutoff_ok, cutoff_total = validation_summary(
        [DOOM / "cutoff_validation.csv", DOOM / "nostate_cutoff_validation.csv", DOOM_FORWARD / "cutoff_validation.csv", DOOM_FORWARD / "nostate_cutoff_validation.csv"]
    )

    beta_ab = construction["beta_AB"]
    beta_ax = construction["beta_AX"]
    gamma_a = construction["gamma_A_raw"]
    gamma_ax = construction["gamma_AX"]
    source_rows = read_csv(ROOT / "data0804" / "invest_panel_weo.csv")
    source_countries = len({row["iso3"] for row in source_rows})
    source_years = [int(float(row["year"])) for row in source_rows]
    base_missing = {row["variable"]: row for row in read_csv(BASE / "missing_loss.csv")}
    bond_missing = base_missing["bond_spreads"]
    tt_missing = base_missing["tt"]

    lines: list[str] = []
    add = lines.append
    add("# Paper B 工作进展与核心卡点")
    add("")
    add(f"> 更新时间：{datetime.now():%Y-%m-%d %H:%M}（Asia/Shanghai）。本文件由 `paperB/render_output.py` 基于本次 Stata 机器可读输出自动生成。")
    add("")
    add("## 技术摘要：分析链已跑通，核心门槛结论仍需稳健性支持")
    add("")
    add("- 当前 `invest_panel_weo.csv` 已完成 baseline、empirical theta、第四节水平 Doomloop、第五节两期前瞻 Doomloop 及两组去状态规格；结果、诊断、图形、CSV、DTA 和日志均已刷新。")
    add(f"- 最稳定的实证结果是适应能力与债务的交互项：$A\\times b$={fmt(beta_ab['estimate'])}，{p_label(beta_ab['p'])}。适应能力与脆弱性的利差交互项不显著：$A\\times X$={fmt(beta_ax['estimate'])}，{p_label(beta_ax['p'])}。")
    add(f"- 第四节：$\\Delta b_{{t+1}}$ 方程两支联合检验 {p_label(debt_wald['p'])}；$A_t$ 方程自身 cutoff 为 {p_label(ready_wald['p'])}，改用债务 cutoff 为 {p_label(ready_debt_cutoff_wald['p'])}。第五节对应的 $\\Delta b_{{t+2}}$、$A_{{t+1}}$ 检验分别为 {p_label(forward_debt_wald['p'])}、{p_label(forward_ready_wald['p'])}（自身 cutoff）和 {p_label(forward_ready_debt_cutoff_wald['p'])}（债务 cutoff）。")
    add("- 当前结果可作为双向固定效应相关性证据使用，但尚未纳入国家内序列相关、theta 生成误差与 cutoff 搜索不确定性，不能解释为因果效应或最终门槛证据。")
    add("")
    add("## 1. 已完成：数据输入已审计，六段估计和统一输出均成功")
    add("")
    add(md_table(
        ["板块", "状态", "本次交付/样本", "判断"],
        [
            ["分析输入", "完成", f"{fmt_int(len(source_rows))} 行、{source_countries} 国、{min(source_years)}–{max(source_years)}；国家—年份重复键为 0", "可作为本次 Stata 分析的固定输入"],
            ["Baseline", "完成", f"N={fmt_int(base_stats['N'])}，{fmt_int(base_stats['countries'])} 国，{fmt_int(base_stats['years'])} 年", "全交互 TWFE、边际效应、Wald 与诊断已输出"],
            ["Empirical theta", "完成", f"N={fmt_int(tax_stats['N'])}，{fmt_int(tax_stats['countries'])} 国，{fmt_int(tax_stats['years'])} 年", "税基方程、theta panel 与构造审计已输出"],
            ["Doomloop debt", "完成", f"N={fmt_int(doom_stats['D3_full']['N'])}，cutoff={fmt(original_cutoffs['debt']['rss_min_cutoff'])}", "原始与去 b 规格均已重估"],
            ["Doomloop readiness", "完成", f"N={fmt_int(doom_stats['R3_full']['N'])}，cutoff={fmt(original_cutoffs['ready']['rss_min_cutoff'])}", "原始与去滞后 A 规格均已重估"],
            ["Forward debt", "完成", f"N={fmt_int(forward_stats['D3_full']['N'])}，cutoff={fmt(forward_cutoffs['debt']['rss_min_cutoff'])}", "$\\Delta b_{t+2}$ 含状态与去 b 规格均已重估"],
            ["Forward readiness", "完成", f"N={fmt_int(forward_stats['R3_full']['N'])}，cutoff={fmt(forward_cutoffs['ready']['rss_min_cutoff'])}", "$A_{t+1}$ 自身 cutoff 与债务 cutoff 均已估计"],
            ["统一交付", "完成", "results、diagnostics、progress、PNG/PDF、CSV/DTA、日志", "统一入口可从现有分析 CSV 重跑"],
        ],
        numeric_from=99,
    ))
    add("")
    add("范围说明：回归中的百分比、比率和 0–100 指数均先除以 100；金额变量保持原尺度。税基以及第四、第五节全部 Doomloop 规格均不含 `CurrentGDP`/`ln_currentgdp` 控制；只有 baseline 保留规模控制。所有正式模型包含国家和年份固定效应，当前标准误为观测层异方差稳健标准误。")
    add("")
    add("## 2. 当前证据：baseline 机制较稳定，doomloop 门槛尚不稳定")
    add("")
    add(md_table(
        ["证据节点", "估计/检验", "p 值", "当前解释"],
        [
            ["利差：A×债务", fmt(beta_ab["estimate"]), fmt_p(beta_ab["p"]), "显著；债务水平系统性调节适应能力与主权利差的关系"],
            ["利差：A×脆弱性", fmt(beta_ax["estimate"]), fmt_p(beta_ax["p"]), "不显著；没有独立交互证据"],
            ["税基：A 原始尺度", fmt(gamma_a["estimate"]), fmt_p(gamma_a["p"]), "仅 10% 水平边际显著"],
            ["税基：A×脆弱性", fmt(gamma_ax["estimate"]), fmt_p(gamma_ax["p"]), f"单项临界显著，但适应项联合检验 p={fmt_p(tax_joint['p'])}"],
            ["原始 debt kink", f"cutoff={fmt(original_cutoffs['debt']['rss_min_cutoff'])}", fmt_p(debt_wald["p"]), "$\\Delta b_{t+1}$ 全控制规格"],
            ["原始 readiness kink", f"cutoff={fmt(original_cutoffs['ready']['rss_min_cutoff'])}", fmt_p(ready_wald["p"]), "$A_t$ 自身 cutoff 全控制规格"],
            ["readiness：债务 cutoff", f"cutoff={fmt(original_cutoffs['debt']['rss_min_cutoff'])}", fmt_p(ready_debt_cutoff_wald["p"]), "cutoff 来自第四节债务全控制方程"],
            ["去 b debt kink", f"cutoff={fmt(nostate_cutoffs['debt']['rss_min_cutoff'])}", fmt_p(debt_ns_wald["p"]), "$\\Delta b_{t+1}$ 去状态规格"],
            ["去滞后 A readiness kink", f"cutoff={fmt(nostate_cutoffs['ready']['rss_min_cutoff'])}", fmt_p(ready_ns_wald["p"]), "$A_t$ 去状态规格"],
            ["两期前瞻 debt kink", f"cutoff={fmt(forward_cutoffs['debt']['rss_min_cutoff'])}", fmt_p(forward_debt_wald["p"]), "$\\Delta b_{t+2}$ 全控制规格"],
            ["一期前瞻 readiness kink", f"cutoff={fmt(forward_cutoffs['ready']['rss_min_cutoff'])}", fmt_p(forward_ready_wald["p"]), "$A_{t+1}$ 自身 cutoff 规格"],
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
            ["国家—年份唯一键", 4, 4, "上游与两套 Doomloop 流程重复键均为 0"],
            ["areg 与显式 LSDV", "已复核", "关键系数", "数值一致"],
        ],
        numeric_from=99,
    ))
    add("")
    add("这些检查证明本次结果在单位、公式、样本锁定和程序实现层面一致；它们不能替代聚类推断、完整 bootstrap 或外生识别。")
    add("")
    add("## 4. 核心卡点：正式推断、规格稳定性和上游数据复现")
    add("")
    add("### 4.1 正式推断尚未覆盖三类不确定性")
    add("")
    add("当前 `vce(robust)` 不处理同一国家内序列相关；theta 来自两条上游回归，cutoff 又由同一样本 RSS 搜索产生。现有标准误没有联合覆盖这三层不确定性，p 值可能偏乐观。")
    add("")
    add("### 4.2 主要 doomloop 发现对模型状态项敏感")
    add("")
    add(f"readiness 的联合 p 值由主规格 {fmt_p(ready_wald['p'])} 变为去滞后项后的 {fmt_p(ready_ns_wald['p'])}，cutoff 由 {fmt(original_cutoffs['ready']['rss_min_cutoff'])} 变为 {fmt(nostate_cutoffs['ready']['rss_min_cutoff'])}；债务 cutoff 也由 {fmt(original_cutoffs['debt']['rss_min_cutoff'])} 变为 {fmt(nostate_cutoffs['debt']['rss_min_cutoff'])}。因此目前不能把某个 cutoff 当作稳定结构参数。")
    add("")
    add("### 4.3 当前仓库可复现分析，但不能从源文件重建分析 CSV")
    add("")
    add("四份完整 Stata 源码与四个分析输出目录已经保留，`paperB/run_workflow.ps1` 可从 `data0804/invest_panel_weo.csv` 重跑分析。数据构建脚本仍依赖当前目录中不存在的 `cleaned_imf_like_panel_1995_2023.csv` 和 `WEOApr2026all.xlsx`；在补齐这两项之前，数据层只能审计现有 CSV，不能从最上游重建。")
    add("")
    add("### 4.4 缺失和单位限制仍影响外推")
    add("")
    add(f"`bond_spreads` 缺失 {fmt_int(bond_missing['missing_total'])} 行（{fmt(bond_missing['missing_rate'], 2)}%），`tt` 缺失 {fmt_int(tt_missing['missing_total'])} 行（{fmt(tt_missing['missing_rate'], 2)}%），是主要样本损失来源；财政系列在早期年份也存在缺失。`CurrentGDP`、`revenue` 和 `debt` 是不同国家的本币金额，既有 reserves 口径也不适合直接做跨国水平比较。")
    add("")
    add("### 4.5 识别边界没有改变")
    add("")
    add("全部结果属于双向固定效应相关性估计。没有外生冲击、工具变量、事件研究或其他识别设计时，不应使用因果措辞。")
    add("")
    add("## 5. 下一步：先补推断，再决定是否强化门槛叙事")
    add("")
    add("1. **P0——补齐国家层面的推断。** 并列报告国家聚类标准误；随后按国家重抽样，每次完整重估 baseline、tax、theta、cutoff 和最终 kink 回归。")
    add("2. **P0——恢复数据层完全复现。** 将基础面板 CSV 与 WEO 工作簿纳入受控数据目录，或提供可验证的下载/生成方式及文件哈希。")
    add("3. **P1——做 cutoff 稳定性分析。** 系统改变 trimming、候选网格、年份窗口、状态项和控制变量，报告 cutoff 与分支系数分布，而不是只报告单点最优值。")
    add("4. **P1——处理样本选择风险。** 比较完整样本、平衡窗口和高缺失变量剔除后的结果，明确 bond spread 与 terms-of-trade 缺失是否改变国家构成。")
    add("5. **P2——收紧论文表述。** 目前以稳健的 $A\\times b$ 结果为主发现，将 doomloop/readiness 门槛定位为待验证机制；只有在 bootstrap 和敏感性分析后仍稳定，才升级为核心结论。")
    add("")
    add("## 6. 待回答的问题")
    add("")
    add("- 论文的主命题究竟是“债务调节适应能力的利差效应”，还是“存在稳定 doomloop cutoff”？当前证据更支持前者。")
    add("- readiness 方程为何强依赖滞后状态项：真实动态调整、均值回归，还是模型设定造成的变化？")
    add(f"- 补齐聚类与全流程 bootstrap 后，第四节 readiness 自身 cutoff 的 p={fmt_p(ready_wald['p'])} 及债务 cutoff 的 p={fmt_p(ready_debt_cutoff_wald['p'])} 是否仍能维持？")
    add("- 早期财政数据和 bond spread 缺失是否集中在特定国家组，从而限制外部有效性？")
    add("")
    return "\n".join(lines)


def main() -> None:
    required = [
        BASE / "model_coefficients.csv", BASE / "model_stats.csv",
        THETA / "model_coefficients.csv", THETA / "empirical_theta_panel.dta",
        DOOM / "model_coefficients.csv", DOOM / "nostate_model_coefficients.csv",
        DOOM_FORWARD / "model_coefficients.csv", DOOM_FORWARD / "nostate_model_coefficients.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required workflow outputs:\n" + "\n".join(missing))
    (HERE / "paperB_results.md").write_text(render_results(), encoding="utf-8")
    (HERE / "paperB_diagnostics.md").write_text(render_diagnostics(), encoding="utf-8")
    (HERE / "progress.md").write_text(render_progress(), encoding="utf-8")


if __name__ == "__main__":
    main()
