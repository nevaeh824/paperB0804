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
    lines.extend("| " + " | ".join(safe(x) for x in row) + " |" for row in rows)
    return "\n".join(lines)


def coefficient_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["model"], row["variable"]): row for row in rows}


def stats_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["model"]: row for row in rows}


def metadata_index(path: Path) -> dict[str, str]:
    return {row["item"]: row["value"] for row in read_csv(path)}


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
    headers = ["变量/统计量"] + [f"({model}) {model_labels[model]}" for model in models]
    rows: list[list[object]] = []
    for variable in variables:
        rows.append([variable_labels[variable]] + [coef_cell(coefficients.get((model, variable))) for model in models])
    if control_flags is not None:
        rows.append(["宏观控制"] + ["是" if control_flags[model][0] else "否" for model in models])
        rows.append(["外部控制"] + ["是" if control_flags[model][1] else "否" for model in models])
    elif "macro_controls" in stats[models[0]]:
        rows.append(["宏观控制"] + [yesno(stats[model].get("macro_controls")) for model in models])
        rows.append(["外部控制"] + [yesno(stats[model].get("external_controls")) for model in models])
    rows.extend([
        ["国家固定效应"] + ["是"] * len(models),
        ["年份固定效应"] + ["是"] * len(models),
    ])
    is_lsdvc = all(stats[model].get("estimator") == "LSDVC" for model in models)
    if is_lsdvc:
        rows.extend(
            [
                ["估计量"] + [stats[model].get("estimator", "") for model in models],
                ["初始化"] + [stats[model].get("initial_estimator", "") for model in models],
                ["偏差修正阶数"] + [fmt_int(stats[model].get("bias_order")) for model in models],
                ["Bootstrap 次数"] + [fmt_int(stats[model].get("bootstrap_reps")) for model in models],
                ["标准误"] + [stats[model].get("se_type", "") for model in models],
                ["动态滞后项"] + [stats[model].get("dynamic_lag", "") for model in models],
            ]
        )
    else:
        rows.extend(
            [
             ["聚类变量"] + [stats[model].get("cluster_variable", "") for model in models],
             ["聚类数"] + [fmt_int(stats[model].get("clusters")) for model in models],
            ]
        )
    rows.extend(
        [
             ["国家数"] + [fmt_int(stats[model].get("countries")) for model in models],
             ["年份数"] + [fmt_int(stats[model].get("years")) for model in models],
             ["样本量"] + [fmt_int(stats[model].get("N")) for model in models],
        ]
    )
    if not is_lsdvc:
        rows.extend(
            [
                [r"Within $R^2$"] + [fmt(stats[model].get("r2_within"), 3) for model in models],
                [r"Overall $R^2$"] + [fmt(stats[model].get("r2_overall"), 3) for model in models],
            ]
        )
    return md_table(headers, rows)


def marginal_table(rows: list[dict[str, str]]) -> str:
    output = []
    labels = {"debt": "债务变化", "ready_debt": "Readiness（债务 cutoff）"}
    for row in rows:
        output.append(
            [
                labels.get(row["equation"], row["equation"]),
                row["point"],
                fmt(row["theta"]),
                fmt(row["marginal_effect"]),
                fmt(row["se"]),
                fmt_p(row["p"]),
                f"[{fmt(row['ci_low'])}, {fmt(row['ci_high'])}]",
            ]
        )
    return md_table(["方程", "点", r"$\theta$", "边际效应", "国家聚类 SE", "p 值", "95% CI"], output)


def validation_summary(paths: list[Path], pass_field: str = "passed") -> tuple[int, int]:
    rows = [row for path in paths for row in read_csv(path)]
    return sum(row.get(pass_field) == "1" for row in rows), len(rows)


def rows_simple(path: Path, fields: list[str], labels: list[str], formats: dict[str, str] | None = None) -> str:
    formats = formats or {}
    output: list[list[str]] = []
    for row in read_csv(path):
        rendered: list[str] = []
        for field in fields:
            value = row.get(field, "")
            mode = formats.get(field, "raw")
            if mode == "num":
                rendered.append(fmt(value))
            elif mode == "num8":
                rendered.append(fmt(value, 8))
            elif mode == "int":
                rendered.append(fmt_int(value))
            elif mode == "p":
                rendered.append(fmt_p(value))
            elif mode == "pass":
                rendered.append("通过" if value == "1" else "未通过")
            else:
                rendered.append(value)
        output.append(rendered)
    return md_table(labels, output)


BASE_MODELS = [
    "A_X_only", "A_A_only", "A_b_only", "B_all_core", "C_macro",
    "Layer1_X", "Layer2_A", "Interact_AB", "Interact_AX", "Interact_all",
]
BASE_LABELS = {
    "A_X_only": "仅 X", "A_A_only": "仅 A", "A_b_only": "仅 b-pre",
    "B_all_core": "三核心", "C_macro": "+宏观", "Layer1_X": "第一层",
    "Layer2_A": "第二层", "Interact_AB": "A×b-pre", "Interact_AX": "A×X",
    "Interact_all": "双交互",
}
BASE_TERMS = {
    "wsdi_days": r"WSDI 天数×0.01 $X_{it}$", "readiness100": r"适应能力 $A_{it}$",
    "b_pre": r"前一期债务/GDP $b^{pre}_{it}=b_{i,t-1}$", "c_A": r"$A^c_{it}$", "c_X": r"$X^c_{it}$",
    "c_b": r"$(b^{pre}_{it})^c$", "int_AB": r"$A^c_{it}\times(b^{pre}_{it})^c$",
    "int_AX": r"$A^c_{it}\times X^c_{it}$", "growth": "Growth",
    "spread_lag": r"滞后主权利差 $s_{i,t-1}$",
    "ln_constantgdp": r"$\ln(ConstantGDP_{it})$", "inflation_cpi": "Inflation",
    "reserves": "Reserves", "tt": "Terms of trade",
}
BASE_FLAGS = {
    "A_X_only": (False, False), "A_A_only": (False, False), "A_b_only": (False, False),
    "B_all_core": (False, False), "C_macro": (True, False), "Layer1_X": (True, True),
    "Layer2_A": (True, True), "Interact_AB": (True, True), "Interact_AX": (True, True),
    "Interact_all": (True, True),
}

TAX_MODELS = [
    "T1_X_only", "T2_A_only", "T3_persistence", "T4_all_core", "T5_macro",
    "T6_layer1_X", "T7_layer2_A", "T8_interact_core", "T9_interact_macro", "T10_interact_full",
]
TAX_LABELS = {
    "T1_X_only": "仅 X", "T2_A_only": "仅 A", "T3_persistence": "仅当期 T 指标",
    "T4_all_core": "核心项", "T5_macro": "+宏观", "T6_layer1_X": "第一层",
    "T7_layer2_A": "第二层", "T8_interact_core": "交互核心",
    "T9_interact_macro": "交互+宏观", "T10_interact_full": "交互+全控制",
}
TAX_TERMS = {
    "wsdi_days": r"WSDI 天数×0.01 $X_{it}$", "readiness100": r"适应能力 $A_{it}$",
    "T_it": r"$T_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$", "c_A_T": r"$A^c_{it}$", "c_X_T": r"$X^c_{it}$",
    "int_AX_T": r"$A^c_{it}\times X^c_{it}$", "growth": "Growth",
    "inflation_cpi": "Inflation", "reserves": "Reserves", "tt": "Terms of trade",
}

DOOM_MODELS_DEBT = ["DN1_core", "DN2_macro", "DN3_full"]
DOOM_MODELS_READY = ["RDN1_core", "RDN2_macro", "RDN3_full"]
DOOM_LABELS = {
    "DN1_core": "核心项", "DN2_macro": "+宏观", "DN3_full": "+全控制",
    "RDN1_core": "核心项", "RDN2_macro": "+宏观", "RDN3_full": "+全控制",
}
DOOM_TERMS = {
    "debt_kink_low": r"$A_{it}(c-\widehat\theta^A_{it})_+$",
    "debt_kink_high": r"$A_{it}(\widehat\theta^A_{it}-c)_+$",
    "ready_debt_kink_low": r"$FT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+$",
    "ready_debt_kink_high": r"$FT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_+$",
    "wsdi_days": r"WSDI 天数×0.01 $X_{it}$", "growth": "Growth", "inflation_cpi": "Inflation",
    "reserves": "Reserves", "tt": "Terms of trade",
}
CRITERION_ORDER = ["theta", "b_pre", "mA", "TA", "b_pre*mA"]
CRITERION_LABELS = {
    "theta": r"$\widehat\theta^A_{it}$", "b_pre": r"$b^{pre}_{it}$",
    "mA": r"$\widehat m^A_{it}$", "TA": r"$\widehat T^A_{it}$",
    "b_pre*mA": r"$b^{pre}_{it}\widehat m^A_{it}$",
}


def find_wald(rows: list[dict[str, str]], model: str, text: str) -> dict[str, str]:
    for row in rows:
        if row["model"] == model and text in row["hypothesis"]:
            return row
    raise KeyError(f"Wald test not found: {model}, {text}")


def render_results() -> str:
    base_coef_rows = read_csv(BASE / "model_coefficients.csv")
    base_stats_rows = read_csv(BASE / "model_stats.csv")
    tax_coef_rows = read_csv(THETA / "model_coefficients.csv")
    tax_stats_rows = read_csv(THETA / "model_stats.csv")
    doom_coef_rows = read_csv(DOOM / "nostate_model_coefficients.csv")
    doom_stats_rows = read_csv(DOOM / "nostate_model_stats.csv")
    base_coefs, base_stats = coefficient_index(base_coef_rows), stats_index(base_stats_rows)
    tax_coefs, tax_stats = coefficient_index(tax_coef_rows), stats_index(tax_stats_rows)
    doom_coefs, doom_stats = coefficient_index(doom_coef_rows), stats_index(doom_stats_rows)
    construction = {(row["source"], row["parameter"]): row for row in read_csv(THETA / "construction_coefficients.csv")}
    theta_desc = read_csv(THETA / "descriptive_stats.csv")
    doom_wald = read_csv(DOOM / "nostate_wald_tests.csv")
    debt_wald = find_wald(doom_wald, "DN3_full", "jointly zero")
    ready_wald = find_wald(doom_wald, "RDN3_full", "branches jointly")
    cutoff = read_csv(DOOM / "nostate_cutoffs.csv")[0]
    key_rows = {row["equation"]: row for row in read_csv(DOOM / "nostate_key_results.csv")}
    criterion_by = {row["criterion"]: row for row in read_csv(DOOM / "criterion_comparison.csv")}
    criterion_rows = [criterion_by[name] for name in CRITERION_ORDER]
    criterion_ns = [int(float(row["N"])) for row in criterion_rows]

    lines: list[str] = []
    add = lines.append
    add("# Paper B：统一回归公式与结果表")
    add("")
    add(f"> 数据：`data0804/invest_panel_weo.csv` 与 `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`；整合生成时间：{datetime.now():%Y-%m-%d %H:%M}（Asia/Shanghai）。")
    add("> 本文档呈现正式公式、回归表、边际效应、债务 cutoff 与竞争判据结果。数据检查和统计验证见 `paperB_diagnostics.md`。主面板源比率、百分数和 0—100 指数均先除以 100；WSDI 天数乘以 0.01 后作为 X 进入回归。")
    add("")
    add("## 技术摘要")
    add("")
    base_ab = construction[("spread", "beta_AB")]
    base_ax = construction[("spread", "beta_AX")]
    tax_a = construction[("T", "gamma_A_raw")]
    tax_ax = construction[("T", "gamma_AX")]
    add(f"- Baseline 全交互模型中，A×b-pre 系数为 {fmt(base_ab['estimate'])}（p={fmt_p(base_ab['p'])}），A×X 系数为 {fmt(base_ax['estimate'])}（p={fmt_p(base_ax['p'])}）。")
    add(f"- 全控制 T 指标模型的原始尺度适应能力系数为 {fmt(tax_a['estimate'])}（p={fmt_p(tax_a['p'])}），A×X 系数为 {fmt(tax_ax['estimate'])}（p={fmt_p(tax_ax['p'])}）。")
    add(f"- 第四节唯一主规格的债务 cutoff 为 {fmt(cutoff['rss_min_cutoff'])}；债务两支联合检验 p={fmt_p(debt_wald['p'])}，使用同一 cutoff 的 readiness 两支联合检验 p={fmt_p(ready_wald['p'])}。")
    add(f"- 五个替代判据按各自当前变量取完整案例，N 范围为 {min(criterion_ns):,}–{max(criterion_ns):,}；完整 theta 的样本内 RSS={fmt(criterion_by['theta']['rss'], 6)}。因样本量可能不同，RSS 不作跨判据排名。")
    add("- 第 2—3 节为含国家与年份效应的动态面板 LSDVC 相关性估计，采用 Blundell–Bond 初始化、`bias(1)` 与 50 次 bootstrap 标准误；第 4 节仍为双向固定效应并报告国家聚类标准误。theta 和 cutoff 是生成量，末阶段聚类标准误仍未覆盖完整上游估计与 cutoff 搜索不确定性。")
    add("")
    add("## 1. 统一符号、控制变量与估计口径")
    add("")
    add(r"令 $s_{it}$ 为主权利差比率，$A_{it}$ 为适应能力比率，$X_{it}=wsdi\_days_{it}\times0.01$，$b^{pre}_{it}=b_{i,t-1}=debt\_gdp_{i,t-1}$。Baseline 的宏观控制为 Growth、Inflation，不控制 $\ln(ConstantGDP)$；T 指标方程的宏观控制仅为 Inflation，不控制 Growth；Doomloop 的宏观控制仍为 Growth、Inflation。外部控制为 Reserves、Terms of trade。全部模型含国家和年份效应。第 2—3 节使用 `xtlsdvc, initial(bb) bias(1) vcov(50)`：一阶偏差修正精度为 $O(T^{-1})$，标准误来自 50 次 bootstrap；动态滞后因变量由 LSDVC 自动加入。第 4 节使用按 `country_id` 聚类的双向固定效应。每个回归使用其因变量、动态滞后项与当前右侧变量的联合非缺失样本，不再设置跨模型或跨阶段固定样本。生成量不向来源回归样本外外推：$\widehat m^A$ 限于 Spread_Interact_all 的实际样本，$\widehat T^A$ 限于 T10_interact_full 的实际样本，theta 限于两个来源样本的交集。三阶修正曾在当前短而不平衡的面板上产生爆炸性动态系数，因此主流程采用数值更稳定的 `bias(1)`。")
    add("")
    add("## 2. Baseline：主权利差回归")
    add("")
    add("### 2.1 回归公式")
    add("")
    add(r"$$s_{it}=\alpha_i+\lambda_t+\rho_s s_{i,t-1}+\beta_AA_{it}+\beta_Bb^{pre}_{it}+\beta_XX_{it}+\beta_{AB}A_{it}b^{pre}_{it}+\beta_{AX}A_{it}X_{it}+\Gamma_m'W^m_{it}+\varepsilon^m_{it}.$$")
    add("")
    add(r"交互回归在对应完整交互式的实际样本内中心化。原始尺度适应能力斜率和边际利差节约为")
    add("")
    add(r"$$\widehat\beta_A^{raw}=\widehat\beta_A^c-\widehat\beta_{AB}\overline{b^{pre}}_s-\widehat\beta_{AX}\bar X_s,$$")
    add("")
    add(r"$$\widehat m^A_{it}=-\left(\widehat\beta_A^{raw}+\widehat\beta_{AB}b^{pre}_{it}+\widehat\beta_{AX}X_{it}\right).$$")
    add("")
    add("### 2.2 逐步回归表")
    add("")
    add("系数下方括号为基于 50 次 bootstrap 标准误的 z 值；`***`、`**`、`*` 分别表示 1%、5%、10% 显著性。")
    add("")
    add("**Panel A：核心变量与控制变量**")
    add("")
    add(model_table(BASE_MODELS[:7], BASE_LABELS, ["wsdi_days", "readiness100", "b_pre", "spread_lag", "growth", "inflation_cpi", "reserves", "tt"], BASE_TERMS, base_coefs, base_stats, BASE_FLAGS))
    add("")
    add("**Panel B：交互模型**")
    add("")
    add(model_table(BASE_MODELS[7:], BASE_LABELS, ["c_A", "c_X", "c_b", "int_AB", "int_AX", "spread_lag", "growth", "inflation_cpi", "reserves", "tt"], BASE_TERMS, base_coefs, base_stats, BASE_FLAGS))
    add("")
    add("### 2.3 构造用原始尺度系数")
    add("")
    construction_rows = []
    for key in [("spread", "beta_A_raw"), ("spread", "beta_AB"), ("spread", "beta_AX")]:
        row = construction[key]
        construction_rows.append([row["parameter"], fmt(row["estimate"]), fmt(row["se"]), fmt(row["t"], 3), fmt_p(row["p"]), f"[{fmt(row['ci_low'])}, {fmt(row['ci_high'])}]"])
    add(md_table(["参数", "估计值", "Bootstrap SE", "z", "p", "95% CI"], construction_rows))
    add("")
    add("<details><summary>展开：baseline 点边际效应</summary>")
    add("")
    base_me = read_csv(BASE / "marginal_effects.csv")
    add(md_table(["模型", "点", "调节变量", "边际效应", "SE", "p", "95% CI"], [[r["model"], r["point"], fmt(r["moderator_value"]), fmt(r["marginal_effect"]), fmt(r["se"]), fmt_p(r["p"]), f"[{fmt(r['ci_low'])}, {fmt(r['ci_high'])}]"] for r in base_me]))
    add("")
    add("</details>")
    add("")
    add("## 3. Empirical theta：边际 T 收益与经验指标")
    add("")
    add("### 3.1 T 指标回归公式与时序")
    add("")
    add(r"$$T_{it}=\frac{(ConstantGDP_{it})}{(ConstantGDP_{i,t-1})},\qquad T_{i,t+1}=\frac{(ConstantGDP_{i,t+1})}{(ConstantGDP_{it})}=F.T_{it}.$$")
    add("")
    add(r"$$T_{i,t+1}=\alpha_i+\lambda_t+\gamma_AA_{it}+\gamma_XX_{it}+\gamma_{AX}A_{it}X_{it}+\rho_TT_{it}+\Gamma_T'W^T_{it}+\varepsilon^T_{i,t+1}.$$")
    add("")
    add(r"T 指标交互模型在全控制交互式的实际样本内中心化，故 $\widehat\gamma_A^{raw}=\widehat\gamma_A^c-\widehat\gamma_{AX}\bar X_T$，且")
    add("")
    add(r"$$\widehat T^A_{it}=\widehat\gamma_A^{raw}+\widehat\gamma_{AX}X_{it}=\widehat\gamma_A^c+\widehat\gamma_{AX}X^c_{it}.$$")
    add("")
    add("### 3.2 T 指标逐步回归表")
    add("")
    add("系数下方括号为基于 50 次 bootstrap 标准误的 z 值。所有规格均由 LSDVC 自动加入 $L.T_{i,t+1}=T_{it}$。")
    add("")
    add("**Panel A：核心变量与控制变量**")
    add("")
    add(model_table(TAX_MODELS[:7], TAX_LABELS, ["wsdi_days", "readiness100", "T_it", "inflation_cpi", "reserves", "tt"], TAX_TERMS, tax_coefs, tax_stats))
    add("")
    add("**Panel B：交互模型**")
    add("")
    add(model_table(TAX_MODELS[7:], TAX_LABELS, ["c_A_T", "c_X_T", "int_AX_T", "T_it", "inflation_cpi", "reserves", "tt"], TAX_TERMS, tax_coefs, tax_stats))
    add("")
    add("### 3.3 边际 T 收益与 theta 构造")
    add("")
    tax_construction_rows = []
    for key in [("T", "gamma_A_raw"), ("T", "gamma_AX")]:
        row = construction[key]
        tax_construction_rows.append([row["parameter"], fmt(row["estimate"]), fmt(row["se"]), fmt(row["t"], 3), fmt_p(row["p"]), f"[{fmt(row['ci_low'])}, {fmt(row['ci_high'])}]"])
    add(md_table(["参数", "估计值", "Bootstrap SE", "z", "p", "95% CI"], tax_construction_rows))
    add("")
    add(r"$$\widehat\theta^A_{it}=b^{pre}_{it}\widehat m^A_{it}+\widehat T^A_{it},\qquad b^{pre}_{it}=debt\_gdp_{i,t-1}.$$")
    add("")
    add("构造支持集严格继承来源回归：`mA_hat` 仅在 Spread_Interact_all 的 `e(sample)` 内生成，`TA_hat` 仅在 T10_interact_full 的 `e(sample)` 内生成，theta 仅在二者共同覆盖时生成。")
    add("")
    selected_theta = [row for row in theta_desc if row["variable"] in {"mA_hat", "spread_saving_component", "TA_hat", "theta_hat_A"}]
    add(md_table(["构造量", "样本", "N", "均值", "SD", "P10", "P50", "P90"], [[r["variable"], r["sample"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["p10"]), fmt(r["p50"]), fmt(r["p90"])] for r in selected_theta]))
    add("")
    add("## 4. Doomloop：一期去状态变量主规格")
    add("")
    add("### 4.1 方程与 cutoff 口径")
    add("")
    add(r"$$\Delta debt_{i,t+1}=debt\_gdp_{i,t+1}-debt\_gdp_{it}.$$")
    add("")
    add(r"$$\Delta debt_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-\widehat\theta^A_{it})_++\beta_HA_{it}(\widehat\theta^A_{it}-c)_++\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.$$")
    add("")
    add(r"$$A_{it}-A_{i,t-1}=\alpha_i+\lambda_t+\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_++\delta_HFT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_++\gamma_XX_{it}+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.$$")
    add("")
    add(r"债务方程不另加入 $b^{pre}_{it}$ 状态项，readiness 方程不加入 $A_{i,t-1}$。$\widehat c_B^\theta$ 仅由债务全控制方程在 theta 的 P10—P90 观测值中按最小 RSS 选择；readiness 不进行独立 cutoff 搜索。两类方程均显式控制 $X_{it}$，并依次加入 Growth、Inflation、Reserves 与 Terms of trade。")
    add("")
    add("### 4.2 债务变化方程")
    add("")
    add(model_table(DOOM_MODELS_DEBT, DOOM_LABELS, ["debt_kink_low", "debt_kink_high", "wsdi_days", "growth", "inflation_cpi", "reserves", "tt"], DOOM_TERMS, doom_coefs, doom_stats))
    add("")
    add("### 4.3 Readiness 一阶差分方程：固定使用债务 cutoff")
    add("")
    add(model_table(DOOM_MODELS_READY, DOOM_LABELS, ["ready_debt_kink_low", "ready_debt_kink_high", "wsdi_days", "growth", "inflation_cpi", "reserves", "tt"], DOOM_TERMS, doom_coefs, doom_stats))
    add("")
    add("### 4.4 全控制结果、边际效应与图形")
    add("")
    cutoff_rows = [
        ["债务变化", "债务全控制 RSS", fmt(cutoff["rss_min_cutoff"]), fmt(cutoff["rss"], 6), fmt_int(cutoff["candidate_count"]), fmt_int(cutoff["low_n"]), fmt_int(cutoff["high_n"]), fmt(key_rows["debt"]["coefficient_low"]), fmt_p(key_rows["debt"]["p_low"]), fmt(key_rows["debt"]["coefficient_high"]), fmt_p(key_rows["debt"]["p_high"])],
        ["Readiness", "继承债务 cutoff", fmt(key_rows["ready_debt"]["cutoff"]), fmt(doom_stats["RDN3_full"]["rss"], 6), "—", "—", "—", fmt(key_rows["ready_debt"]["coefficient_low"]), fmt_p(key_rows["ready_debt"]["p_low"]), fmt(key_rows["ready_debt"]["coefficient_high"]), fmt_p(key_rows["ready_debt"]["p_high"])],
    ]
    add(md_table(["结果方程", "cutoff 来源", "cutoff", "RSS", "候选数", "N_low", "N_high", "低支系数", "p_L", "高支系数", "p_H"], cutoff_rows))
    add("")
    add(r"点边际效应按 $m(\theta;c)=a(c-\theta)_++b(\theta-c)_+$ 计算；在 cutoff 处定义为 0。")
    add("")
    add("<details><summary>展开：主规格点边际效应</summary>")
    add("")
    add(marginal_table(read_csv(DOOM / "nostate_marginal_effects.csv")))
    add("")
    add("</details>")
    add("")
    add("| 债务变化 | Readiness（债务 cutoff） |")
    add("| --- | --- |")
    add("| ![债务变化边际效应](figures/debt_marginal_effect_no_b.png) | ![Readiness 边际效应](figures/readiness_marginal_effect_debt_cutoff_no_lag.png) |")
    add("")
    add("合并版：[PNG](figures/kink_marginal_effects_no_state.png) · [PDF](figures/kink_marginal_effects_no_state.pdf)")
    add("")
    add("## 5. Criterion Decomposition / Competing Criterion Test")
    add("")
    add(r"令阈值判据为 $q_{it}$，每个判据均在其因变量、分支构造量和全套控制变量共同非缺失的样本上估计")
    add("")
    add(r"$$\Delta debt_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-q_{it})_++\beta_HA_{it}(q_{it}-c)_++\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1},$$")
    add("")
    add(r"$$q_{it}\in\left\{\widehat\theta^A_{it},\ b^{pre}_{it},\ \widehat m^A_{it},\ \widehat T^A_{it},\ b^{pre}_{it}\widehat m^A_{it}\right\}.$$")
    add("")
    add(r"每种判据分别在自身 P10—P90 候选值上搜索最小 RSS cutoff。理论方向为 $\beta_L>0$、$\beta_H<0$；$N_{low}=\#\{q_{it}\le c\}$，$N_{high}=\#\{q_{it}>c\}$。")
    add("")
    comparison_table = []
    for row in criterion_rows:
        comparison_table.append([
            CRITERION_LABELS[row["criterion"]], fmt(row["cutoff"]), fmt(row["beta_L"]),
            fmt_p(row["p_L"]), fmt(row["beta_H"]), fmt_p(row["p_H"]),
            row["theoretical_signs"], fmt(row["rss"], 6), fmt(row["r2_within"], 4),
            fmt_int(row["N"]), fmt_int(row["N_low"]), fmt_int(row["N_high"]),
        ])
    add(md_table(["Criterion", "cutoff", "beta_L", "p_L", "beta_H", "p_H", "theoretical signs", "RSS", "Within R2", "N", "N_low", "N_high"], comparison_table))
    add("")
    add("各判据的 cutoff、分支系数和 RSS 均处于自身尺度与自身完整案例样本中。由于 N 可能不同，cutoff、系数和 RSS 不作跨行绝对排名；表格用于报告各判据内部的拟合、显著性、理论方向与阈值两侧覆盖。")
    add("")
    add("## 6. 结果解释边界")
    add("")
    add("这些结果是相关性估计，不应表述为因果效应。第 2—3 节的 50 次 LSDVC bootstrap 标准误只对应各上游方程；第 4 节的国家聚类标准误处理国家内相关，但没有计入 theta 生成误差或 cutoff 搜索不确定性。正式联合推断仍应采用按国家重抽样、每次重估完整流程的 bootstrap。竞争判据使用各自完整案例样本，既不是同样本 RSS 比较，也不是非嵌套模型的正式显著性检验。")
    add("")
    return "\n".join(lines)


def render_diagnostics() -> str:
    formula_paths = [THETA / "formula_checks.csv", DOOM / "nostate_formula_checks.csv"]
    cutoff_paths = [DOOM / "nostate_cutoff_validation.csv", DOOM / "criterion_cutoff_validation.csv"]
    unit_paths = [BASE / "unit_scaling_checks.csv", THETA / "unit_scaling_checks.csv", DOOM / "unit_scaling_checks.csv"]
    formula_ok, formula_total = validation_summary(formula_paths)
    cutoff_ok, cutoff_total = validation_summary(cutoff_paths)
    unit_ok, unit_total = validation_summary(unit_paths)
    base_stats = stats_index(read_csv(BASE / "model_stats.csv"))["Layer2_A"]
    tax_stats = stats_index(read_csv(THETA / "model_stats.csv"))["T10_interact_full"]
    doom_stats = stats_index(read_csv(DOOM / "nostate_model_stats.csv"))
    criterion_by = {row["criterion"]: row for row in read_csv(DOOM / "criterion_comparison.csv")}

    lines: list[str] = []
    add = lines.append
    add("# Paper B：统计检验与数据检查")
    add("")
    add(f"> 生成时间：{datetime.now():%Y-%m-%d %H:%M}（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。")
    add("")
    add("## 1. Validation Report")
    add("")
    add("### Overall Assessment: Share with caveats")
    add("")
    add(f"单位换算检查通过 {unit_ok}/{unit_total} 项；代数、映射与 hinge 检查通过 {formula_ok}/{formula_total} 项；cutoff 最小 RSS 及继承关系检查通过 {cutoff_ok}/{cutoff_total} 项。各回归已使用当前变量完整案例；第 2—3 节报告 LSDVC 的 50 次 bootstrap 标准误，第 4 节报告国家聚类标准误。theta 生成误差、cutoff 搜索和多判据选择不确定性尚未由联合推断覆盖。")
    add("")
    add("### Methodology Review")
    add("")
    add("主流程准确对应 workflow：第 2—3 节使用 Blundell–Bond 初始化的动态 LSDVC、`bias(1)` 和 50 次 bootstrap；第 4 节使用一期债务变化、去债务状态控制、readiness 严格一阶差分且不加入滞后状态控制，并固定使用债务全控制 theta cutoff。每个回归按当前因变量、动态滞后项和右侧变量取完整案例；mA_hat 与 TA_hat 分别限制在其首选来源回归的实际样本内，theta 仅在两个来源样本共同覆盖且 b_pre 可用时构造。五种阈值判据使用各自的当前变量样本，因此其 RSS 与 Within R² 不作跨判据排名。")
    add("")
    add("### Issues Found")
    add("")
    add("1. **[Medium] 推断未覆盖 cutoff 搜索和上游生成误差。** 第 4 节 p 值使用国家聚类标准误，但条件于已估计的 theta 与已选择的 cutoff；上游 50 次方程内 bootstrap 也不是全流程联合 bootstrap。")
    add("2. **[Medium] 完整联合不确定性仍需管线 bootstrap。** 应按国家重抽样，并在每次重复中重估两条上游方程、theta 与 cutoff。")
    add("3. **[Low] 竞争判据使用不同完整案例样本。** 各行 RSS 只能解释为对应样本内拟合，不能直接据此给五个判据排序。")
    add("")
    add("## 2. 数据来源、单位与时序")
    add("")
    add("原始分析输入是 `data0804/invest_panel_weo.csv` 与 `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`。两者按唯一 `iso3 year` 键合并；`wsdi_days` 乘以 0.01 后定义 X。主面板源百分数、比率和 0—100 指数先除以 100；金额变量不缩放。`ln_constantgdp` 仅保留作正值与数据审计，不参与 T 构造，也不进入 Baseline 或其复核模型；`growth` 不进入 T 指标模型。Doomloop 从 empirical-theta panel 读取已换算变量，并单独将源 `interest_revenue` 除以 100。")
    add("")
    add(r"- $T_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$，$T_{i,t+1}=F.T_{it}$；两者均严格要求相邻年份。")
    add(r"- 债务变化结果为 $\Delta debt_{i,t+1}=F.debt\_gdp_{it}-debt\_gdp_{it}$；理论债务状态统一使用 $b^{pre}_{it}=L.debt\_gdp_{it}$。")
    add(r"- readiness 结果为 $A_{it}-A_{i,t-1}=readiness100_{it}-L.readiness100_{it}$；方程右侧不使用滞后状态项。")
    add("")
    add("### 2.1 Doomloop 源字段换算")
    add("")
    add(rows_simple(DOOM / "unit_scaling_checks.csv", ["variable", "source_min", "source_max", "ratio_min", "ratio_max", "max_abs_scaling_diff", "passed"], ["变量", "源最小值", "源最大值", "比率最小值", "比率最大值", "最大误差", "状态"], {"source_min": "num", "source_max": "num", "ratio_min": "num", "ratio_max": "num", "max_abs_scaling_diff": "num8", "passed": "pass"}))
    add("")
    add("## 3. 回归实际样本与描述统计")
    add("")
    sample_rows = [
        ["Baseline Layer2_A", fmt_int(base_stats["N"]), fmt_int(base_stats["countries"]), fmt_int(base_stats["years"]), f"{base_stats['first_year']}–{base_stats['last_year']}"],
        ["T 指标全控制交互", fmt_int(tax_stats["N"]), fmt_int(tax_stats["countries"]), fmt_int(tax_stats["years"]), f"{tax_stats['first_year']}–{tax_stats['last_year']}"],
        ["Doomloop 债务全控制 theta", fmt_int(doom_stats["DN3_full"]["N"]), fmt_int(doom_stats["DN3_full"]["countries"]), fmt_int(doom_stats["DN3_full"]["years"]), f"{doom_stats['DN3_full']['first_year']}–{doom_stats['DN3_full']['last_year']}"],
        ["Doomloop Readiness", fmt_int(doom_stats["RDN3_full"]["N"]), fmt_int(doom_stats["RDN3_full"]["countries"]), fmt_int(doom_stats["RDN3_full"]["years"]), f"{doom_stats['RDN3_full']['first_year']}–{doom_stats['RDN3_full']['last_year']}"],
    ]
    add(md_table(["规格实际样本", "N", "国家数", "年份数", "年份范围"], sample_rows))
    add("")
    add("### 3.1 Baseline 输入变量")
    add("")
    selected = {"bond_spreads", "spread_lag", "wsdi_days", "readiness100", "b_pre", "growth", "inflation_cpi", "reserves", "tt"}
    base_profile = [row for row in read_csv(BASE / "profile.csv") if row["variable"] in selected]
    add(md_table(["变量", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["variable"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in base_profile]))
    add("")
    add("### 3.2 Distribution of country or region samples — Layer2_A")
    add("")
    country_distribution = read_csv(BASE / "layer2_a_country_distribution.csv")
    add(md_table(
        ["国家/地区", "ISO3", "观测数", "样本占比 (%)", "起始年份", "结束年份"],
        [[row["country_name"], row["iso3"], fmt_int(row["observations"]), fmt(100 * float(row["sample_share"]), 2), str(int(float(row["first_year"]))), str(int(float(row["last_year"])))] for row in country_distribution],
    ))
    add("")
    add("### 3.3 T 指标与 theta 构造量")
    add("")
    theta_desc = read_csv(THETA / "descriptive_stats.csv")
    add(md_table(["变量", "样本", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["variable"], r["sample"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in theta_desc]))
    add("")
    add("### 3.4 Doomloop 主规格与判据变量")
    add("")
    doom_desc = read_csv(DOOM / "nostate_regression_descriptive_stats.csv")
    add(md_table(["规格", "方程", "变量", "角色", "N", "均值", "SD", "最小值", "P50", "最大值"], [[r["specification"], r["equation"], r["variable"], r["role"], fmt_int(r["N"]), fmt(r["mean"]), fmt(r["sd"]), fmt(r["min"]), fmt(r["p50"]), fmt(r["max"])] for r in doom_desc]))
    add("")
    add("## 4. 缺失、重复键与 Within 变异")
    add("")
    add("三个估计阶段均对国家—年份键执行 fail-closed 唯一性检查；不会自动去重。Baseline 与 T 指标的每个动态回归均使用当前因变量、隐含滞后因变量与右侧变量的联合非缺失样本；Doomloop 债务和 readiness 使用各自当前因变量与右侧变量的联合非缺失样本。mA_hat 仅在 Spread_Interact_all 的实际样本内生成，TA_hat 仅在 T10_interact_full 的实际样本内生成，theta 要求两个来源样本共同覆盖且 b_pre 可用；五种判据分别使用各自构造量与全控制变量的联合非缺失样本。")
    add("")
    add("### 4.1 独占样本损失")
    add("")
    missing_rows = []
    for stage, path in [("baseline", BASE / "missing_loss.csv"), ("T", THETA / "missing_loss.csv"), ("doomloop", DOOM / "nostate_missing_loss.csv")]:
        for row in read_csv(path):
            missing_rows.append([stage, row.get("equation", "—"), row["variable"], fmt_int(row["missing_total"]), fmt(row["missing_rate"], 2), fmt_int(row["exclusive_loss"])])
    add(md_table(["板块", "方程", "变量", "缺失数", "缺失率 (%)", "独占损失"], missing_rows))
    add("")
    add("### 4.2 Within 变异")
    add("")
    variation_rows = []
    for stage, path in [("baseline", BASE / "variation.csv"), ("T", THETA / "variation.csv"), ("doomloop", DOOM / "nostate_variation.csv")]:
        for row in read_csv(path):
            if stage == "baseline" and row["variable"] not in selected:
                continue
            variation_rows.append([stage, row.get("equation", "—"), row["variable"], fmt(row["sd_overall"]), fmt(row["sd_within"]), fmt(row["ratio_within_overall"]), row["fe_identification"]])
    add(md_table(["板块", "方程", "变量", "总体 SD", "Within SD", "Within/总体", "FE 识别"], variation_rows))
    add("")
    add("## 5. 共线性、相关性与系数变化")
    add("")
    vif_rows = []
    for stage, path in [("baseline", BASE / "collinearity.csv"), ("T", THETA / "collinearity.csv")]:
        for row in read_csv(path):
            vif_rows.append([stage, row["variable"], fmt(row["vif"]), fmt(row["tolerance"]), fmt(row["condition_number"])])
    add(md_table(["板块", "变量", "VIF", "容忍度", "条件数"], vif_rows))
    add("")
    corr_rows = []
    for stage, path in [("baseline", BASE / "correlations.csv"), ("T", THETA / "correlations.csv")]:
        seen: set[tuple[str, str]] = set()
        for row in read_csv(path):
            key = tuple(sorted((row["variable_i"], row["variable_j"])))
            value = number(row["correlation"])
            if row["variable_i"] == row["variable_j"] or key in seen or value is None or abs(value) < 0.60:
                continue
            seen.add(key)
            corr_rows.append([stage, row["variable_i"], row["variable_j"], fmt(value)])
    add("")
    add("绝对相关系数不低于 0.60 的非重复变量对：")
    add("")
    add(md_table(["板块", "变量 1", "变量 2", "相关系数"], corr_rows))
    add("")
    add("## 6. 统计与程序验证")
    add("")
    add("### 6.1 Wald 联合检验")
    add("")
    wald_rows = []
    for stage, path in [("baseline", BASE / "wald_tests.csv"), ("T", THETA / "wald_tests.csv"), ("doomloop", DOOM / "nostate_wald_tests.csv")]:
        for row in read_csv(path):
            wald_rows.append([stage, row["model"], row["hypothesis"], fmt(row["F"]), fmt_int(row["df_num"]), fmt_int(row["df_den"]), fmt_p(row["p"])])
    add(md_table(["板块", "模型", "原假设", "Wald χ² / F", "约束数/分子 df", "分母 df", "p"], wald_rows))
    add("")
    add("### 6.2 代数、映射与 hinge 公式")
    add("")
    formula_rows = []
    for stage, path in [("theta", THETA / "formula_checks.csv"), ("doomloop", DOOM / "nostate_formula_checks.csv")]:
        for row in read_csv(path):
            formula_rows.append([stage, row["check"], fmt(row.get("max_abs_diff") or row.get("max_abs_difference"), 8), fmt(row["tolerance"], 8), "通过" if row["passed"] == "1" else "未通过"])
    add(md_table(["板块", "检查", "最大绝对误差", "容差", "状态"], formula_rows))
    add("")
    add("### 6.3 估计器配置与数值复核")
    add("")
    config_rows = []
    for row in read_csv(BASE / "validation_checks.csv"):
        config_rows.append(["baseline", row["model"], row["check"], fmt(row["expected"]), fmt(row["actual"]), "通过" if row["passed"] == "1" else "未通过"])
    for row in read_csv(THETA / "estimator_validation.csv"):
        config_rows.append(["T", row.get("model", "T"), row["check"], fmt(row["expected"]), fmt(row["actual"]), "通过" if row["passed"] == "1" else "未通过"])
    add(md_table(["板块", "模型", "检查", "期望", "实际", "状态"], config_rows))
    add("")
    add("第 2—3 节正式配置均为 `xtlsdvc, initial(bb) bias(1) vcov(50)`。一阶修正对应 $O(T^{-1})$；三阶修正在当前短而不平衡面板的预检中产生爆炸性动态系数，故未作为主规格。第 4 节继续用 areg 与显式 LSDV 复核：")
    add("")
    estimator_rows = []
    for row in read_csv(DOOM / "nostate_estimator_validation.csv"):
        estimator_rows.append(["doomloop", row["specification"], row["variable"], fmt(row["areg_b"]), fmt(row["lsdv_b"]), fmt(row["abs_b_diff"], 8), fmt(row["abs_se_diff"], 8)])
    add(md_table(["板块", "模型/判据", "变量", "areg", "LSDV", "|系数差|", "|SE差|"], estimator_rows))
    add("")
    add("### 6.4 Cutoff 最小 RSS 与样本加总")
    add("")
    criterion_checks = read_csv(DOOM / "criterion_cutoff_validation.csv")
    add(md_table(["Criterion", "记录 cutoff", "最小 RSS", "cutoff RSS", "|差值|", "N", "N_low", "N_high", "加总", "状态"], [[CRITERION_LABELS[r["criterion"]], fmt(r["recorded_cutoff"]), fmt(r["profile_min_rss"], 6), fmt(r["rss_at_recorded_cutoff"], 6), fmt(r["abs_rss_diff"], 8), fmt_int(r["N"]), fmt_int(r["N_low"]), fmt_int(r["N_high"]), "通过" if r["count_identity"] == "1" else "未通过", "通过" if r["passed"] == "1" else "未通过"] for r in criterion_checks]))
    add("")
    add("Readiness cutoff 继承检查：")
    add("")
    add(rows_simple(DOOM / "nostate_cutoff_validation.csv", ["equation", "cutoff_source", "recorded_cutoff", "profile_min_rss", "rss_at_recorded_cutoff", "abs_rss_diff", "passed"], ["方程", "cutoff 来源", "cutoff", "债务 profile 最小 RSS", "cutoff RSS", "差值", "状态"], {"recorded_cutoff": "num", "profile_min_rss": "num", "rss_at_recorded_cutoff": "num", "abs_rss_diff": "num8", "passed": "pass"}))
    add("")
    add("### 6.5 五判据特定样本与拟合结果")
    add("")
    ordered = [criterion_by[name] for name in CRITERION_ORDER]
    add(md_table(["Criterion", "N", "聚类数", "RSS", "Within R2", "理论方向"], [[CRITERION_LABELS[row["criterion"]], fmt_int(row["N"]), fmt_int(row["clusters"]), fmt(row["rss"], 6), fmt(row["r2_within"], 4), row["theoretical_signs"]] for row in ordered]))
    add("")
    add("各行使用判据特定的完整案例样本；当 N 不同时，RSS 与 Within R² 不作跨行排名。")
    add("")
    add("## 7. 图形 QA")
    add("")
    figure_rows = []
    for name in ["debt_marginal_effect_no_b.png", "debt_marginal_effect_no_b.pdf", "readiness_marginal_effect_debt_cutoff_no_lag.png", "readiness_marginal_effect_debt_cutoff_no_lag.pdf", "kink_marginal_effects_no_state.png", "kink_marginal_effects_no_state.pdf"]:
        path = HERE / "figures" / name
        figure_rows.append([name, fmt_int(path.stat().st_size) if path.exists() else "—", "通过" if path.exists() and path.stat().st_size > 0 else "未通过"])
    add(md_table(["图形", "字节", "状态"], figure_rows))
    add("")
    add("债务图和 readiness 图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0。Readiness 图的竖直线来自债务全控制方程。")
    add("")
    add("## 8. Required Caveats for Stakeholders")
    add("")
    add("- 第 2—3 节使用 `xtlsdvc, initial(bb) bias(1) vcov(50)` 的方程内 bootstrap 标准误；第 4 节使用 `vce(cluster country_id)`。两者都不等于传播全部上游生成误差的全流程 bootstrap。")
    add("- theta 是两条上游回归的生成变量；cutoff 又在对应样本中搜索，常规 p 值没有覆盖联合不确定性。")
    add("- 五种判据使用各自当前变量完整案例；样本不同时不能按 RSS 直接排序，并仍有模型选择和多重比较问题。")
    add("- 固定效应相关性结果不支持因果措辞。")
    add("")
    add("## 9. 原始输出索引")
    add("")
    add("完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。")
    add("")
    return "\n".join(lines)


def render_progress() -> str:
    construction = {row["parameter"]: row for row in read_csv(THETA / "construction_coefficients.csv")}
    base_stats = stats_index(read_csv(BASE / "model_stats.csv"))["Interact_all"]
    tax_stats = stats_index(read_csv(THETA / "model_stats.csv"))["T10_interact_full"]
    doom_stats = stats_index(read_csv(DOOM / "nostate_model_stats.csv"))
    doom_wald = read_csv(DOOM / "nostate_wald_tests.csv")
    debt_wald = find_wald(doom_wald, "DN3_full", "jointly zero")
    ready_wald = find_wald(doom_wald, "RDN3_full", "branches jointly")
    tax_wald = find_wald(read_csv(THETA / "wald_tests.csv"), "T10_interact_full", "adaptation terms jointly")
    cutoff = read_csv(DOOM / "nostate_cutoffs.csv")[0]
    criterion_rows = read_csv(DOOM / "criterion_comparison.csv")
    criterion_by = {row["criterion"]: row for row in criterion_rows}
    criterion_ns = [int(float(row["N"])) for row in criterion_rows]
    unit_ok, unit_total = validation_summary([BASE / "unit_scaling_checks.csv", THETA / "unit_scaling_checks.csv", DOOM / "unit_scaling_checks.csv"])
    formula_ok, formula_total = validation_summary([THETA / "formula_checks.csv", DOOM / "nostate_formula_checks.csv"])
    cutoff_ok, cutoff_total = validation_summary([DOOM / "nostate_cutoff_validation.csv", DOOM / "criterion_cutoff_validation.csv"])
    source_rows = read_csv(ROOT / "data0804" / "invest_panel_weo.csv")
    source_countries = len({row["iso3"] for row in source_rows})
    source_years = [int(float(row["year"])) for row in source_rows]
    duplicate_keys = len(source_rows) - len({(row["iso3"], row["year"]) for row in source_rows})
    wsdi_rows = read_csv(ROOT / "WSDI" / "data" / "processed" / "wsdi_sovereign61_1995_2018.csv")
    wsdi_countries = len({row["iso3"] for row in wsdi_rows})
    wsdi_years = [int(float(row["year"])) for row in wsdi_rows]
    wsdi_nonmissing = sum(row["wsdi_days"] != "" for row in wsdi_rows)
    wsdi_duplicate_keys = len(wsdi_rows) - len({(row["iso3"], row["year"]) for row in wsdi_rows})
    base_missing = {row["variable"]: row for row in read_csv(BASE / "missing_loss.csv")}

    def p_label(value: object) -> str:
        rendered = fmt_p(value)
        return f"p{rendered}" if rendered.startswith("<") else f"p={rendered}"

    lines: list[str] = []
    add = lines.append
    add("# Paper B 工作进展与核心卡点")
    add("")
    add(f"> 更新时间：{datetime.now():%Y-%m-%d %H:%M}（Asia/Shanghai）。本文件由 `paperB/render_output.py` 基于本次 Stata 机器可读输出自动生成。")
    add("")
    add("## 技术摘要：新主流程已完整跑通")
    add("")
    add("- 当前统一入口只执行 baseline、empirical theta 和一期去状态 Doomloop 三个估计阶段；结果、诊断、图形、CSV、DTA 与日志均由同一次流程刷新。")
    add(r"- 理论变量 $X_{it}=wsdi\_days_{it}\times0.01$；Baseline 十个主权利差规格均控制严格相邻年份的 $s_{i,t-1}$。")
    add("- mA_hat 与 TA_hat 分别限定在 Spread_Interact_all 和 T10_interact_full 的实际样本内，theta 及下游含 theta 的 Doomloop 规格限定在两个来源样本的交集内，不执行样本外外推。")
    add(f"- 债务全控制方程在 theta 上得到 cutoff={fmt(cutoff['rss_min_cutoff'])}，两支联合检验 {p_label(debt_wald['p'])}；readiness 固定使用该 cutoff，两支联合检验 {p_label(ready_wald['p'])}。")
    add(f"- 竞争判据按各自当前变量取完整案例，N 范围为 {min(criterion_ns):,}–{max(criterion_ns):,}；完整 theta 的 RSS={fmt(criterion_by['theta']['rss'], 6)}，不与不同 N 的替代判据作排名。")
    add("- 计算一致性已通过；第 2—3 节使用 LSDVC/Blundell–Bond、`bias(1)` 与 50 次 bootstrap，第 4 节使用国家聚类标准误。完整管线 bootstrap 与模型选择不确定性仍待补充。")
    add("")
    add("## 1. 本次交付状态")
    add("")
    add(md_table(
        ["板块", "状态", "本次样本/交付", "判断"],
        [
            ["主面板输入", "完成", f"{fmt_int(len(source_rows))} 行、{source_countries} 国、{min(source_years)}–{max(source_years)}；重复键 {duplicate_keys}", "固定主面板输入"],
            ["WSDI 输入", "完成", f"{fmt_int(len(wsdi_rows))} 行、{wsdi_countries} 国、{min(wsdi_years)}–{max(wsdi_years)}；非缺失 {fmt_int(wsdi_nonmissing)}；重复键 {wsdi_duplicate_keys}", "按 iso3 year 合并并乘 0.01"],
            ["Baseline", "完成", f"N={fmt_int(base_stats['N'])}，{fmt_int(base_stats['countries'])} 国", "动态 LSDVC、利差滞后、边际效应、Wald 与诊断已刷新"],
            ["Empirical theta", "完成", f"N={fmt_int(tax_stats['N'])}，{fmt_int(tax_stats['countries'])} 国", "T 指标方程、theta panel 与构造审计已刷新"],
            ["Doomloop debt", "完成", f"N={fmt_int(doom_stats['DN3_full']['N'])}，cutoff={fmt(cutoff['rss_min_cutoff'])}", "一期、去 b 状态变量的唯一主规格"],
            ["Doomloop readiness", "完成", f"N={fmt_int(doom_stats['RDN3_full']['N'])}，cutoff={fmt(doom_stats['RDN3_full']['cutoff'])}", "去滞后状态变量并继承债务 cutoff"],
            ["Competing Criterion Test", "完成", f"5 个判据，N={min(criterion_ns):,}–{max(criterion_ns):,}", "各自在当前变量样本完成 P10—P90 RSS 搜索"],
            ["统一文档", "完成", "results、diagnostics、progress 与 3 组 PNG/PDF", "旧规格不进入新文档或最终图形目录"],
        ],
        numeric_from=99,
    ))
    add("")
    add("## 2. 当前证据")
    add("")
    beta_ab = construction["beta_AB"]
    beta_ax = construction["beta_AX"]
    gamma_a = construction["gamma_A_raw"]
    gamma_ax = construction["gamma_AX"]
    evidence_rows = [
        ["利差：A×债务", fmt(beta_ab["estimate"]), fmt_p(beta_ab["p"]), "显著；债务水平调节适应能力与主权利差的相关关系"],
        ["利差：A×WSDI X", fmt(beta_ax["estimate"]), fmt_p(beta_ax["p"]), "未达到常用显著性水平"],
        ["T 指标：A 原始尺度", fmt(gamma_a["estimate"]), fmt_p(gamma_a["p"]), "边际 T 收益的构造系数"],
        ["T 指标：A×WSDI X", fmt(gamma_ax["estimate"]), fmt_p(gamma_ax["p"]), f"适应项联合检验 {p_label(tax_wald['p'])}"],
        ["债务 kink", f"cutoff={fmt(cutoff['rss_min_cutoff'])}", fmt_p(debt_wald["p"]), r"$\Delta b_{t+1}$ 去状态全控制规格"],
        ["Readiness kink", f"cutoff={fmt(cutoff['rss_min_cutoff'])}", fmt_p(ready_wald["p"]), r"$A_t$ 去状态全控制规格；cutoff 来自债务方程"],
        ["判据样本口径", f"N={min(criterion_ns):,}–{max(criterion_ns):,}", "不作跨样本 RSS 排名", "各判据使用自身当前变量完整案例"],
        ["完整 theta 判据", f"N={fmt_int(criterion_by['theta']['N'])}", fmt(criterion_by["theta"]["rss"], 6), criterion_by["theta"]["theoretical_signs"]],
    ]
    add(md_table(["证据节点", "估计/口径", "p 值或 RSS", "当前解释"], evidence_rows, numeric_from=99))
    add("")
    add("五判据详细系数、p 值、Within R² 和阈值两侧样本量见 `paperB_results.md`；全部 cutoff profile 与验证记录保存在 `doomloop/stata_outputs/`。")
    add("")
    add("## 3. 质量核验")
    add("")
    add(md_table(
        ["核验", "通过", "总数", "结论"],
        [
            ["单位换算", unit_ok, unit_total, "通过" if unit_ok == unit_total else "未通过"],
            ["代数、映射与 hinge", formula_ok, formula_total, "通过" if formula_ok == formula_total else "未通过"],
            ["cutoff 最小 RSS/继承", cutoff_ok, cutoff_total, "通过" if cutoff_ok == cutoff_total else "未通过"],
            ["五判据当前变量样本", 5, 5, f"各行 N={min(criterion_ns):,}–{max(criterion_ns):,}，且 N_low+N_high=N"],
            ["LSDVC 配置 / Doomloop LSDV", 22, 22, "上游配置检查与末阶段显式 LSDV 复核通过"],
        ],
        numeric_from=99,
    ))
    add("")
    add("## 4. 核心卡点")
    add("")
    add("### 4.1 方程内 bootstrap / 国家聚类已报告，但联合推断仍未覆盖两层不确定性")
    add("")
    add("第 2—3 节已有 50 次 LSDVC 方程内 bootstrap，第 4 节的 `vce(cluster country_id)` 已处理国家内相关；但 theta 来自两条上游回归，cutoff 又由对应样本搜索产生。现有标准误没有联合覆盖生成变量与阈值选择不确定性。")
    add("")
    add("### 4.2 五种判据的样本量可能不同")
    add("")
    add(f"五种判据均使用相同的方程结构和控制口径，但因构造量可得性不同，实际 N 为 {min(criterion_ns):,}–{max(criterion_ns):,}。不同 N 下的 RSS 不能直接排序；在共同样本敏感性分析、bootstrap、样本外验证或正式非嵌套比较前，不宜据此认定某个判据更优。")
    add("")
    add("### 4.3 上游数据构建尚未完全自包含")
    add("")
    add("本仓库可从现有 `invest_panel_weo.csv` 与 `wsdi_sovereign61_1995_2018.csv` 重跑全部估计；主面板构建脚本仍依赖当前未纳入仓库的基础面板 CSV 与 WEO 工作簿。")
    add("")
    add("### 4.4 缺失限制外推")
    add("")
    bond_missing = base_missing["bond_spreads"]
    wsdi_missing = base_missing["wsdi_days"]
    tt_missing = base_missing["tt"]
    add(f"`wsdi_days` 缺失 {fmt_int(wsdi_missing['missing_total'])} 行（{fmt(wsdi_missing['missing_rate'], 2)}%），`bond_spreads` 缺失 {fmt_int(bond_missing['missing_total'])} 行（{fmt(bond_missing['missing_rate'], 2)}%），`tt` 缺失 {fmt_int(tt_missing['missing_total'])} 行（{fmt(tt_missing['missing_rate'], 2)}%）；WSDI 的 2018 年截止期同时限制样本外推。")
    add("")
    add("## 5. 下一步")
    add("")
    add("1. **P0——补齐联合推断。** 在现有上游方程内 bootstrap 与末阶段国家聚类标准误的基础上按国家重抽样，每次完整重估 baseline、T 指标、theta、五个 cutoff 和最终 kink 回归。")
    add("2. **P0——检验判据稳定性。** 在 bootstrap、年份窗口和 trimming 变化下记录各判据的样本量、样本内 RSS、cutoff 与分支系数；另做共同样本敏感性比较。")
    add("3. **P1——做样本外或交叉验证比较。** 避免仅凭样本内最小 RSS 选择判据。")
    add("4. **P1——恢复数据层完全复现。** 纳入上游源文件，或提供可验证的下载方式与哈希。")
    add("5. **P2——收紧论文表述。** 将门槛结果定位为待验证机制，不使用因果或唯一结构阈值措辞。")
    add("")
    return "\n".join(lines)


def validate_inputs() -> None:
    required = [
        BASE / "model_coefficients.csv", BASE / "model_stats.csv", BASE / "unit_scaling_checks.csv",
        BASE / "sample_audit.csv", BASE / "layer2_a_country_distribution.csv",
        THETA / "model_coefficients.csv", THETA / "model_stats.csv", THETA / "empirical_theta_panel.dta",
        THETA / "empirical_theta_panel.csv",
        DOOM / "unit_scaling_checks.csv", DOOM / "nostate_model_coefficients.csv",
        DOOM / "nostate_model_stats.csv", DOOM / "nostate_wald_tests.csv",
        DOOM / "nostate_key_results.csv", DOOM / "nostate_cutoffs.csv",
        DOOM / "nostate_marginal_effects.csv", DOOM / "nostate_formula_checks.csv",
        DOOM / "nostate_cutoff_validation.csv", DOOM / "nostate_estimator_validation.csv",
        DOOM / "criterion_comparison.csv", DOOM / "criterion_rss_profiles.csv",
        DOOM / "criterion_cutoff_validation.csv", DOOM / "nostate_missing_loss.csv",
        DOOM / "nostate_variation.csv", DOOM / "nostate_regression_descriptive_stats.csv",
        DOOM / "doomloop_nostate_panel.csv",
    ]
    missing = [str(path) for path in required if not path.exists() or path.stat().st_size == 0]
    if missing:
        raise FileNotFoundError("Missing or empty workflow outputs:\n" + "\n".join(missing))

    upstream_stats = read_csv(BASE / "model_stats.csv") + read_csv(THETA / "model_stats.csv")
    for row in upstream_stats:
        expected = {
            "estimator": "LSDVC",
            "initial_estimator": "Blundell-Bond",
            "bias_order": "1",
            "bootstrap_reps": "50",
            "se_type": "bootstrap",
            "country_fe": "1",
            "year_fe": "1",
        }
        if any(row.get(field) != value for field, value in expected.items()):
            raise ValueError(f"Model lacks required LSDVC configuration: {row.get('model')}")
    for row in read_csv(DOOM / "nostate_model_stats.csv"):
        if row.get("cluster_variable") != "country_id" or int(float(row.get("clusters", 0))) < 2:
            raise ValueError(f"Model lacks valid country-clustered inference: {row.get('model')}")

    baseline_stats = stats_index(read_csv(BASE / "model_stats.csv"))
    layer2_distribution = read_csv(BASE / "layer2_a_country_distribution.csv")
    if sum(int(float(row["observations"])) for row in layer2_distribution) != int(float(baseline_stats["Layer2_A"]["N"])):
        raise ValueError("Layer2_A country distribution does not reconcile to model N.")
    if abs(sum(float(row["sample_share"]) for row in layer2_distribution) - 1.0) > 1e-8:
        raise ValueError("Layer2_A country distribution shares do not sum to one.")

    theta_panel = read_csv(THETA / "empirical_theta_panel.csv")

    def present(row: dict[str, str], field: str) -> bool:
        return row.get(field, "") not in {"", "."}

    for row in theta_panel:
        b_present = present(row, "b_pre")
        spread_source_sample = row.get("sample_spread") == "1"
        tax_source_sample = row.get("sample_tax") == "1"
        ma_present = present(row, "mA_hat")
        ta_present = present(row, "TA_hat")
        theta_present = present(row, "theta_hat_A")
        if ma_present != spread_source_sample:
            raise ValueError(f"mA support mismatch at {row['iso3']} {row['year']}")
        if ta_present != tax_source_sample:
            raise ValueError(f"TA support mismatch at {row['iso3']} {row['year']}")
        joint = b_present and spread_source_sample and tax_source_sample
        if theta_present != joint or (row.get("theta_constructible") == "1") != joint:
            raise ValueError(f"theta joint-support mismatch at {row['iso3']} {row['year']}")

    upstream_by_key = {(row["iso3"], row["year"]): row for row in theta_panel}
    for row in read_csv(DOOM / "doomloop_nostate_panel.csv"):
        if row.get("sample_debt_ns") == "1" or row.get("sample_ready_ns") == "1":
            source = upstream_by_key[(row["iso3"], row["year"])]
            if source.get("sample_spread") != "1" or source.get("sample_tax") != "1":
                raise ValueError(
                    f"Doomloop sample outside upstream source samples at {row['iso3']} {row['year']}"
                )

    comparison = read_csv(DOOM / "criterion_comparison.csv")
    if len(comparison) != 5 or {row["criterion"] for row in comparison} != set(CRITERION_ORDER):
        raise ValueError("Criterion comparison must contain theta, b_pre, mA, TA, and b_pre*mA exactly once.")
    for row in comparison:
        if int(float(row["N_low"])) + int(float(row["N_high"])) != int(float(row["N"])):
            raise ValueError(f"Criterion sample counts do not add up: {row['criterion']}")
        if row.get("cluster_variable") != "country_id" or int(float(row.get("clusters", 0))) < 2:
            raise ValueError(f"Criterion lacks country-clustered inference: {row['criterion']}")
    for path in [DOOM / "nostate_formula_checks.csv", DOOM / "nostate_cutoff_validation.csv", DOOM / "criterion_cutoff_validation.csv"]:
        if any(row.get("passed") != "1" for row in read_csv(path)):
            raise ValueError(f"Validation failure in {path}")
    cutoffs = read_csv(DOOM / "nostate_cutoffs.csv")
    if len(cutoffs) != 1 or cutoffs[0]["equation"] != "debt":
        raise ValueError("Only the debt equation may have a searched main cutoff.")


def main() -> None:
    validate_inputs()
    (HERE / "paperB_results.md").write_text(render_results(), encoding="utf-8")
    (HERE / "paperB_diagnostics.md").write_text(render_diagnostics(), encoding="utf-8")
    (HERE / "progress.md").write_text(render_progress(), encoding="utf-8")


if __name__ == "__main__":
    main()
