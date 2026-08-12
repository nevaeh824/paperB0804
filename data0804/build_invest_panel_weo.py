from __future__ import annotations

import csv
import math
from collections import OrderedDict
from decimal import Decimal
from pathlib import Path
from typing import Iterable

import nbformat as nbf
import pandas as pd
from nbclient import NotebookClient
from openpyxl import load_workbook


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data0804"
BASE_CSV = PROJECT_ROOT / "cleaned_imf_like_panel_1995_2023.csv"
WEO_XLSX = next(PROJECT_ROOT.rglob("WEOApr2026all.xlsx"))
OUTPUT_CSV = OUTPUT_DIR / "invest_panel_weo.csv"
OUTPUT_DOC = OUTPUT_DIR / "invest_panel_weo_documentation.md"
OUTPUT_NOTEBOOK = OUTPUT_DIR / "invest_panel_weo_profile.ipynb"

WEO_FIELDS = OrderedDict(
    [
        ("GGR_NGDP", "Revenue_gdp"),
        ("NGDP", "CurrentGDP"),
        ("NGDP_R", "ConstantGDP"),
        ("GGXCNL_NGDP", "OverallBalance_gdp"),
        ("GGR", "revenue"),
        ("GGXWDG", "debt"),
    ]
)
DERIVED_FIELDS = ["interest_revenue"]
YEARS = range(1995, 2024)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("\ufffd", "").strip()


def format_number(value: object) -> str:
    """Return a clean decimal representation without changing the source unit."""
    if value is None or value == "":
        return ""
    numeric = float(value)
    if not math.isfinite(numeric):
        return ""
    rendered = format(Decimal(str(numeric)).normalize(), "f")
    return "0" if rendered in {"-0", ""} else rendered


def calculate_interest_revenue(output_row: dict[str, str]) -> str:
    required = ["PrimaryBalance_gdp", "OverallBalance_gdp", "Revenue_gdp"]
    if any(output_row.get(field, "") == "" for field in required):
        return ""
    primary_balance = Decimal(output_row["PrimaryBalance_gdp"])
    overall_balance = Decimal(output_row["OverallBalance_gdp"])
    revenue_gdp = Decimal(output_row["Revenue_gdp"])
    if revenue_gdp == 0:
        return ""
    return format_number(
        ((primary_balance - overall_balance) / revenue_gdp) * Decimal("100")
    )


def read_weo_values():
    workbook = load_workbook(
        WEO_XLSX,
        read_only=True,
        data_only=True,
        keep_links=False,
    )
    worksheet = workbook["Countries"]
    rows = worksheet.iter_rows(values_only=True)
    header = [clean_text(value) for value in next(rows)]
    index = {name: position for position, name in enumerate(header)}
    year_positions = {year: index[str(year)] for year in YEARS}

    values: dict[tuple[str, int, str], str] = {}
    numeric_values: dict[tuple[str, int, str], float] = {}
    metadata: list[dict[str, str]] = []
    source_country_codes: set[str] = set()
    duplicate_series: list[tuple[str, str]] = []
    seen_series: set[tuple[str, str]] = set()

    for row in rows:
        code = clean_text(row[index["INDICATOR.ID"]])
        if code not in WEO_FIELDS:
            continue
        iso3 = clean_text(row[index["COUNTRY.ID"]])
        series_key = (iso3, code)
        if series_key in seen_series:
            duplicate_series.append(series_key)
        seen_series.add(series_key)
        source_country_codes.add(iso3)
        metadata.append(
            {
                "iso3": iso3,
                "country": clean_text(row[index["COUNTRY"]]),
                "code": code,
                "series_code": clean_text(row[index["SERIES_CODE"]]),
                "indicator": clean_text(row[index["INDICATOR"]]),
                "scale": clean_text(row[index["SCALE"]]),
                "unit": clean_text(row[index["UNIT"]]),
                "latest_actual_annual_data": clean_text(
                    row[index["LATEST_ACTUAL_ANNUAL_DATA"]]
                ),
                "historical_data_source": clean_text(
                    row[index["HISTORICAL_DATA_SOURCE"]]
                ),
            }
        )
        for year, position in year_positions.items():
            raw_value = row[position]
            rendered = format_number(raw_value)
            if rendered:
                key = (iso3, year, code)
                values[key] = rendered
                numeric_values[key] = float(raw_value)

    workbook.close()
    if duplicate_series:
        raise ValueError(f"Duplicate WEO country-indicator rows: {duplicate_series[:5]}")
    return values, numeric_values, pd.DataFrame(metadata), source_country_codes


def read_csv_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return fieldnames, rows


def write_merged_csv(weo_values: dict[tuple[str, int, str], str]):
    source_fields, source_rows = read_csv_rows(BASE_CSV)
    if "OB_gdp" not in source_fields:
        raise ValueError("Expected OB_gdp in the base panel.")
    if "PrimaryBalance_gdp" in source_fields:
        raise ValueError("Base panel already contains PrimaryBalance_gdp.")

    renamed_fields = [
        "PrimaryBalance_gdp" if field == "OB_gdp" else field
        for field in source_fields
    ]
    output_fields = renamed_fields + list(WEO_FIELDS.values()) + DERIVED_FIELDS

    panel_keys: list[tuple[str, int]] = []
    output_rows: list[dict[str, str]] = []
    for source_row in source_rows:
        iso3 = source_row["iso3"].strip()
        year = int(source_row["year"])
        panel_keys.append((iso3, year))
        output_row = {
            ("PrimaryBalance_gdp" if field == "OB_gdp" else field): value
            for field, value in source_row.items()
        }
        for code, output_name in WEO_FIELDS.items():
            output_row[output_name] = weo_values.get((iso3, year, code), "")
        output_row["interest_revenue"] = calculate_interest_revenue(output_row)
        output_rows.append(output_row)

    if len(panel_keys) != len(set(panel_keys)):
        raise ValueError("The base panel contains duplicate iso3-year keys.")

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    return source_fields, source_rows, output_fields, output_rows


def verify_preservation(
    source_fields: list[str],
    source_rows: list[dict[str, str]],
    output_rows: list[dict[str, str]],
):
    if len(source_rows) != len(output_rows):
        raise AssertionError("Row count changed during the left join.")
    for row_number, (source_row, output_row) in enumerate(
        zip(source_rows, output_rows), start=2
    ):
        for source_field in source_fields:
            output_field = (
                "PrimaryBalance_gdp" if source_field == "OB_gdp" else source_field
            )
            if source_row[source_field] != output_row[output_field]:
                raise AssertionError(
                    f"Base value changed at CSV row {row_number}: {source_field}"
                )


def verify_weo_reconciliation(
    weo_values: dict[tuple[str, int, str], str],
) -> None:
    """Stop if any appended WEO value or missing position differs from source."""
    output_fields, output_rows = read_csv_rows(OUTPUT_CSV)
    missing_fields = set(WEO_FIELDS.values()) - set(output_fields)
    if missing_fields:
        raise AssertionError(
            f"Output is missing WEO fields: {sorted(missing_fields)}"
        )
    for row_number, output_row in enumerate(output_rows, start=2):
        iso3 = output_row["iso3"].strip()
        year = int(output_row["year"])
        for code, output_name in WEO_FIELDS.items():
            expected = weo_values.get((iso3, year, code), "")
            actual = output_row[output_name]
            if (actual == "") != (expected == ""):
                raise AssertionError(
                    f"WEO missingness mismatch at CSV row {row_number}: {output_name}"
                )
            if actual != "" and not math.isclose(
                float(actual), float(expected), rel_tol=0, abs_tol=1e-12
            ):
                raise AssertionError(
                    f"WEO value mismatch at CSV row {row_number}: {output_name}"
                )


def format_stat(value: object, count: bool = False) -> str:
    if pd.isna(value):
        return ""
    numeric = float(value)
    if count:
        return f"{int(round(numeric)):,}"
    absolute = abs(numeric)
    if absolute >= 1_000_000 or (0 < absolute < 0.0001):
        return f"{numeric:.6g}"
    return f"{numeric:.4f}".rstrip("0").rstrip(".")


def markdown_table(headers: Iterable[str], rows: Iterable[Iterable[object]]) -> str:
    headers = [str(header) for header in headers]
    body = [[str(cell).replace("|", "\\|") for cell in row] for row in rows]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def profile_output(
    source_rows: list[dict[str, str]],
    metadata: pd.DataFrame,
    source_country_codes: set[str],
):
    data = pd.read_csv(OUTPUT_CSV)
    country_count = int(data["iso3"].nunique())
    year_min = int(data["year"].min())
    year_max = int(data["year"].max())
    expected_years = year_max - year_min + 1
    balanced = bool(
        len(data) == country_count * expected_years
        and data.groupby("iso3")["year"].nunique().eq(expected_years).all()
    )

    coverage_rows = []
    for column in data.columns:
        non_missing = int(data[column].notna().sum())
        missing = int(data[column].isna().sum())
        coverage_rows.append(
            (
                f"`{column}`",
                f"{non_missing:,}",
                f"{missing:,}",
                f"{non_missing / len(data) * 100:.2f}%",
            )
        )

    numeric_columns = data.select_dtypes(include="number").columns.tolist()
    stats = (
        data[numeric_columns]
        .describe(percentiles=[0.25, 0.5, 0.75])
        .T.rename(columns={"25%": "P25", "50%": "Median", "75%": "P75"})
    )
    stat_rows = []
    for variable, row in stats.iterrows():
        stat_rows.append(
            [
                f"`{variable}`",
                format_stat(row["count"], count=True),
                format_stat(row["mean"]),
                format_stat(row["std"]),
                format_stat(row["min"]),
                format_stat(row["P25"]),
                format_stat(row["Median"]),
                format_stat(row["P75"]),
                format_stat(row["max"]),
            ]
        )

    new_coverage_rows = []
    for code, output_name in WEO_FIELDS.items():
        series = data[output_name]
        meta = metadata.loc[metadata["code"].eq(code)].iloc[0]
        missing_by_year = (
            data.loc[series.isna()].groupby("year").size().sort_values(ascending=False)
        )
        top_missing = ", ".join(
            f"{int(year)}: {int(count)}"
            for year, count in missing_by_year.head(5).items()
        )
        new_coverage_rows.append(
            (
                f"`{output_name}`",
                f"`{code}`",
                f"{int(series.notna().sum()):,}",
                f"{series.notna().mean() * 100:.2f}%",
                f"{meta['scale']} / {meta['unit']}",
                top_missing or "无",
            )
        )

    interest_series = data["interest_revenue"]
    interest_missing_by_year = (
        data.loc[interest_series.isna()].groupby("year").size().sort_values(ascending=False)
    )
    interest_top_missing = ", ".join(
        f"{int(year)}: {int(count)}"
        for year, count in interest_missing_by_year.head(5).items()
    )
    new_coverage_rows.append(
        (
            "`interest_revenue`",
            "派生公式",
            f"{int(interest_series.notna().sum()):,}",
            f"{interest_series.notna().mean() * 100:.2f}%",
            "百分数（%）",
            interest_top_missing or "无",
        )
    )

    formula_inputs_complete = data[
        ["PrimaryBalance_gdp", "OverallBalance_gdp", "Revenue_gdp"]
    ].notna().all(axis=1)
    nonzero_denominator = data["Revenue_gdp"].ne(0)
    expected_interest_mask = formula_inputs_complete & nonzero_denominator
    expected_interest = (
        data["PrimaryBalance_gdp"] - data["OverallBalance_gdp"]
    ) / data["Revenue_gdp"] * 100
    formula_max_difference = float(
        (data.loc[expected_interest_mask, "interest_revenue"] - expected_interest[expected_interest_mask])
        .abs()
        .max()
    )

    missing_panel_isos = sorted(set(data["iso3"]) - source_country_codes)
    quality = {
        "rows": int(len(data)),
        "columns": int(data.shape[1]),
        "countries": country_count,
        "year_min": year_min,
        "year_max": year_max,
        "balanced": balanced,
        "duplicate_keys": int(data.duplicated(["iso3", "year"]).sum()),
        "exact_duplicates": int(data.duplicated().sum()),
        "missing_identifiers": int(data[["country_name", "iso3", "year"]].isna().sum().sum()),
        "source_rows": int(len(source_rows)),
        "unmatched_panel_isos": missing_panel_isos,
        "weo_series_rows": int(len(metadata)),
        "weo_duplicate_series": int(metadata.duplicated(["iso3", "code"]).sum()),
        "new_missing": {
            column: int(data[column].isna().sum())
            for column in list(WEO_FIELDS.values()) + DERIVED_FIELDS
        },
        "new_coverage": {
            column: float(data[column].notna().mean() * 100)
            for column in list(WEO_FIELDS.values()) + DERIVED_FIELDS
        },
        "zero_revenue_gdp": int(data["Revenue_gdp"].eq(0).sum()),
        "interest_formula_missingness_matches": bool(
            data["interest_revenue"].notna().equals(expected_interest_mask)
        ),
        "interest_formula_max_difference": formula_max_difference,
    }
    return data, coverage_rows, stat_rows, new_coverage_rows, quality


def variable_dictionary_rows():
    return [
        ("`country_name`", "国家/地区英文名", "文本", "基础面板；名称体系沿用原面板", "原样复制"),
        ("`iso3`", "ISO3 国家/地区代码", "文本", "基础面板；用于和 WEO `COUNTRY.ID` 合并", "原样复制，合并键之一"),
        ("`year`", "年度", "公历年", "基础面板 1995–2023 年骨架", "原样复制，合并键之一"),
        ("`bond_spreads`", "10 年期国债收益率相对美国的利差", "百分点", "基础面板；Investing.com 年均收益率及 `dataADD` 补充", "原样复制；国别收益率减美国收益率"),
        ("`bond_10y`", "10 年期国债收益率年均值", "%", "基础面板；Investing.com 及 `dataADD` 补充", "原样复制，不再缩放"),
        ("`vulnerability100`", "ND-GAIN 气候脆弱性指数", "0–100 指数点（非百分比）", "基础面板；`宏观indicators/vulnerability.csv`", "原样复制；原基础面板已将 0–1 指数乘以 100，本次不再缩放"),
        ("`readiness100`", "ND-GAIN 气候准备度/韧性指数", "0–100 指数点（非百分比）", "基础面板；`宏观indicators/readiness.csv`", "原样复制；原基础面板已将 0–1 指数乘以 100，本次不再缩放"),
        ("`lnrgdp`", "实际 GDP 水平的自然对数", "自然对数；底层 `NGDP_R` 为十亿本币", "基础面板；IMF WEO `NGDP_R`", "原样复制；`ln(NGDP_R)`"),
        ("`growth`", "实际 GDP 年增长率", "%", "基础面板；IMF WEO `NGDP_RPCH`", "原样复制，不乘以 100"),
        ("`inflation_cpi`", "平均 CPI 年通胀率", "%", "基础面板；IMF WEO `PCPIPCH`", "原样复制，不乘以 100"),
        ("`debt_gdp`", "一般政府总债务占 GDP", "% of GDP", "基础面板；IMF WEO `GGXWDG_NGDP`", "原样复制，不乘以 100"),
        ("`PrimaryBalance_gdp`", "一般政府基础净借贷/净借款占 GDP", "% of GDP", "基础面板原 `OB_gdp`；IMF WEO `GGXONLB_NGDP`", "仅改名，数值原样复制；不乘以 100"),
        ("`reserves`", "含黄金国际储备的既有派生比率", "基础面板既有比率 ×100", "基础面板；WDI `FI.RES.TOTL.CD` 与 WEO `NGDP_R`", "原样复制；沿用既有公式 `FI.RES.TOTL.CD / 1e9 / NGDP_R * 100`，本次不再缩放"),
        ("`gee`", "政府有效性估计值", "WGI 估计值（约 -2.5 至 2.5）", "基础面板；WGI `GE.EST`", "原样复制"),
        ("`rqe`", "监管质量估计值", "WGI 估计值（约 -2.5 至 2.5）", "基础面板；WGI `RQ.EST`", "原样复制"),
        ("`tt`", "净易货贸易条件指数", "指数，2015=100", "基础面板；WDI `TT.PRI.MRCH.XD.WD`", "原样复制"),
        ("`is_advanced`", "发达经济体标识", "0/1", "基础面板；沿用 `原数据集/dataIMF.xlsx` 分类", "原样复制"),
        ("`Revenue_gdp`", "一般政府收入占 GDP", "% of GDP", "`宏观indicators/WEOApr2026all.xlsx`，Countries 表，`GGR_NGDP`", "按 `iso3 + year` 左连接；WEO 原值，不乘以 100"),
        ("`CurrentGDP`", "现价 GDP（本币）", "十亿本币", "`宏观indicators/WEOApr2026all.xlsx`，Countries 表，`NGDP`", "按 `iso3 + year` 左连接；WEO 原值"),
        ("`ConstantGDP`", "固定价格 GDP（本币）", "十亿本币", "`宏观indicators/WEOApr2026all.xlsx`，Countries 表，`NGDP_R`", "按 `iso3 + year` 左连接；WEO 原值"),
        ("`OverallBalance_gdp`", "一般政府净借贷（+）/净借款（-）占 GDP", "% of GDP", "`宏观indicators/WEOApr2026all.xlsx`，Countries 表，`GGXCNL_NGDP`", "按 `iso3 + year` 左连接；WEO 原值，不乘以 100"),
        ("`revenue`", "一般政府收入（本币金额）", "十亿本币", "`宏观indicators/WEOApr2026all.xlsx`，Countries 表，`GGR`", "按 `iso3 + year` 左连接；WEO 原值"),
        ("`debt`", "一般政府总债务（本币金额）", "十亿本币", "`宏观indicators/WEOApr2026all.xlsx`，Countries 表，`GGXWDG`", "按 `iso3 + year` 左连接；WEO 原值"),
        ("`interest_revenue`", "利息支出占政府收入的百分比", "%", "由面板字段派生", "`((PrimaryBalance_gdp - OverallBalance_gdp) / Revenue_gdp) * 100`；任一输入缺失或分母为 0 时留空"),
    ]


def write_documentation(
    coverage_rows,
    stat_rows,
    new_coverage_rows,
    quality,
):
    variable_table = markdown_table(
        ["变量", "含义", "单位", "来源", "处理"], variable_dictionary_rows()
    )
    coverage_table = markdown_table(
        ["变量", "非缺失", "缺失", "覆盖率"], coverage_rows
    )
    stats_table = markdown_table(
        ["变量", "N", "均值", "标准差", "最小值", "P25", "中位数", "P75", "最大值"],
        stat_rows,
    )
    new_coverage_table = markdown_table(
        ["新增列", "WEO 代码", "非缺失", "覆盖率", "WEO 单位", "缺失最多的年份（缺失行数）"],
        new_coverage_rows,
    )
    quality_table = markdown_table(
        ["检查", "结果", "严重度", "置信度", "分析影响/建议"],
        [
            ("面板键唯一性", f"`iso3 + year` 重复 {quality['duplicate_keys']} 行；整行重复 {quality['exact_duplicates']} 行", "通过", "高", "不会因重复键造成面板或合并膨胀"),
            ("面板完整性", f"{quality['countries']} 个国家/地区 × 29 年 = {quality['rows']:,} 行；平衡面板={quality['balanced']}", "通过", "高", "国家—年份骨架完整"),
            ("WEO 国家匹配", f"基础面板未匹配 WEO 的 ISO3：{quality['unmatched_panel_isos'] or '无'}", "通过", "高", f"全部 {quality['countries']} 个国家/地区可在 WEO 六个目标系列中找到"),
            ("新增变量缺失", f"Revenue_gdp 缺失 {quality['new_missing']['Revenue_gdp']}；CurrentGDP 缺失 {quality['new_missing']['CurrentGDP']}；ConstantGDP 缺失 {quality['new_missing']['ConstantGDP']}；OverallBalance_gdp 缺失 {quality['new_missing']['OverallBalance_gdp']}；revenue 缺失 {quality['new_missing']['revenue']}；debt 缺失 {quality['new_missing']['debt']}；interest_revenue 缺失 {quality['new_missing']['interest_revenue']}", "中", "高", "建模或均值比较需报告最终可用样本，并检查早期年份选择性缺失"),
            ("interest_revenue 公式", f"缺失位置一致={quality['interest_formula_missingness_matches']}；公式最大绝对误差={quality['interest_formula_max_difference']:.3g}；Revenue_gdp 为 0 的行数={quality['zero_revenue_gdp']}", "通过", "高", "该列单位为百分数；例如 5 表示利息支出约占收入 5%"),
            ("本币金额可比性", "CurrentGDP、ConstantGDP、revenue 和 debt 的单位均为十亿本币，各国币种不同", "中", "高", "可做国别内时间变化；不可直接把跨国水平当作同一货币规模比较"),
            ("既有 lnrgdp/reserves 口径", "lnrgdp 基于本币实际 GDP；reserves 继承美元储备除以本币实际 GDP 的既有公式", "高（若作跨国水平解释）", "高", "本次按要求原样复制；跨国解释前建议统一货币/价格口径并重新构造"),
        ],
    )

    text = f"""# invest_panel_weo 数据说明与 Overview

## 1. 交付内容

- 数据文件：`data0804/invest_panel_weo.csv`
- 基础数据：`cleaned_imf_like_panel_1995_2023.csv`
- WEO 数据：`宏观indicators/WEOApr2026all.xlsx`（April 2026 WEO，`Countries` 工作表）
- 可复核代码：`data0804/build_invest_panel_weo.py`
- 质量核验 notebook：`data0804/invest_panel_weo_profile.ipynb`

输出包含 {quality['rows']:,} 行、{quality['columns']} 列、{quality['countries']} 个国家/地区，年份为 {quality['year_min']}–{quality['year_max']}。以 `iso3 + year` 为唯一键，原面板行序和原字段数值均被保留；`OB_gdp` 仅重命名为 `PrimaryBalance_gdp`，随后在列末追加 `Revenue_gdp`、`CurrentGDP`、`ConstantGDP`、`OverallBalance_gdp`、`revenue`、`debt`、`interest_revenue`。

## 2. 单位和缩放规则

- WEO 百分比变量保留 Excel 中的原始百分数/百分比点表示。例如 WEO 的 `38.031` 仍写为 `38.031`，不转换为 `0.38031`，也不再乘以 100。
- 本次没有对任何从基础面板复制的数值做二次缩放。
- `vulnerability100` 与 `readiness100` 是基础面板中已有的 0–100 指数点，名字中的 `100` 不代表本次进行了缩放。
- `reserves` 也按基础面板既有数值原样复制；其历史构造本身包含 `*100`，本次没有再次缩放。
- `interest_revenue` 是百分数，按 `((PrimaryBalance_gdp - OverallBalance_gdp) / Revenue_gdp) * 100` 计算；数值 5 表示约 5%。

## 3. 变量定义、单位与来源

{variable_table}

## 4. WEO 合并覆盖

WEO 中六个目标指标各有 197 条唯一 country–indicator 行；其中 `NGDP_R` 在 1995–2023 至少有一个非缺失值的国家/地区为 196 个，其余目标系列为 197 个；基础面板的 {quality['countries']} 个 ISO3 全部存在于 WEO。合并为严格的左连接，行数从 {quality['source_rows']:,} 保持为 {quality['rows']:,}，没有一对多扩张。

{new_coverage_table}

## 5. 全字段覆盖率

{coverage_table}

## 6. 数值变量描述统计

统计量按非缺失观察计算。`CurrentGDP`、`ConstantGDP`、`revenue` 和 `debt` 为不同本币单位的十亿本币，下面的跨国汇总仅用于数据概览，不应解释为可直接比较的经济规模。

{stats_table}

## 7. 数据质量结论

{quality_table}

总体判断：新文件的键、行数、列映射、WEO 合并和 `interest_revenue` 公式可靠；主要限制是财政系列在样本早期的缺失，以及本币金额/既有储备口径不适合直接做跨国水平比较。

## 8. 复现与假设

- 运行：`py -3.14 data0804/build_invest_panel_weo.py`
- WEO 合并键假设：基础面板 `iso3` 与 WEO `COUNTRY.ID` 使用相同 ISO3 体系。
- 新增变量只提取 1995–2023，与基础面板时间范围一致；不引入 WEO 2024–2031 的估计/预测年份。
- CSV 使用 UTF-8 编码，缺失值写为空字段。
"""
    OUTPUT_DOC.write_text(text, encoding="utf-8")


def build_notebook(quality):
    notebook = nbf.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3.14 (Data Investing)",
        "language": "python",
        "name": "data-investing-py314",
    }
    notebook["metadata"]["language_info"] = {"name": "python", "version": "3.14"}
    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            f"""# invest_panel_weo：合并与数据质量核验

## tl;dr

- 输出为 {quality['rows']:,} 行、{quality['columns']} 列、{quality['countries']} 个国家/地区的 1995–2023 平衡面板。
- `iso3 + year` 无重复，合并没有改变基础面板行数。
- 新增 WEO GDP 列覆盖率：CurrentGDP {quality['new_coverage']['CurrentGDP']:.2f}%，ConstantGDP {quality['new_coverage']['ConstantGDP']:.2f}%；财政金额列覆盖率：revenue {quality['new_coverage']['revenue']:.2f}%，debt {quality['new_coverage']['debt']:.2f}%。
- 派生列 interest_revenue 覆盖率为 {quality['new_coverage']['interest_revenue']:.2f}%，公式最大绝对误差为 {quality['interest_formula_max_difference']:.3g}。
- WEO 百分数保持原始百分比点单位，没有乘以 100。
"""
        ),
        nbf.v4.new_markdown_cell(
            """## Context & Methods

本 notebook 是 CSV 与说明文档的审计附件。它重新读取基础面板、输出面板和 WEO 六个目标系列，检查字段保留、唯一键、左连接行数、WEO 数值一致性、派生公式、缺失率和描述统计。

### Key Assumptions

- `iso3 + year` 是目标面板唯一键。
- WEO `COUNTRY.ID` 与基础面板 `iso3` 可直接匹配。
- 分析期限定为 1995–2023。
"""
        ),
        nbf.v4.new_markdown_cell("## Data\n\n### 1. Load inputs and output"),
        nbf.v4.new_code_cell(
            """from pathlib import Path
import importlib.util
import sys
import pandas as pd

sys.dont_write_bytecode = True
OUTPUT_DIR = Path.cwd()
PROJECT_ROOT = OUTPUT_DIR.parent
BASE_CSV = PROJECT_ROOT / "cleaned_imf_like_panel_1995_2023.csv"
OUTPUT_CSV = OUTPUT_DIR / "invest_panel_weo.csv"

base = pd.read_csv(BASE_CSV)
panel = pd.read_csv(OUTPUT_CSV)

spec = importlib.util.spec_from_file_location("builder", OUTPUT_DIR / "build_invest_panel_weo.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
_, weo_numeric, weo_metadata, _ = builder.read_weo_values()

base.shape, panel.shape, weo_metadata.groupby("code")["iso3"].nunique().to_dict()
"""
        ),
        nbf.v4.new_markdown_cell("## Results\n\n### 2. Validate grain and source-field preservation"),
        nbf.v4.new_code_cell(
            """expected_columns = ["PrimaryBalance_gdp" if c == "OB_gdp" else c for c in base.columns] + list(builder.WEO_FIELDS.values()) + builder.DERIVED_FIELDS

renamed_base = base.rename(columns={"OB_gdp": "PrimaryBalance_gdp"})
preserved = renamed_base.equals(panel[renamed_base.columns])
checks = pd.Series({
    "output_rows": len(panel),
    "output_columns": panel.shape[1],
    "column_order_matches": panel.columns.tolist() == expected_columns,
    "base_values_preserved": preserved,
    "duplicate_iso3_year_keys": int(panel.duplicated(["iso3", "year"]).sum()),
    "exact_duplicate_rows": int(panel.duplicated().sum()),
    "countries": int(panel["iso3"].nunique()),
    "year_min": int(panel["year"].min()),
    "year_max": int(panel["year"].max()),
})
checks
"""
        ),
        nbf.v4.new_markdown_cell("### 3. Reconcile appended values to WEO"),
        nbf.v4.new_code_cell(
            """weo_rows = [
    {"iso3": iso3, "year": year, "code": code, "source_value": value}
    for (iso3, year, code), value in weo_numeric.items()
]
weo_long = pd.DataFrame(weo_rows)
weo_wide = weo_long.pivot(index=["iso3", "year"], columns="code", values="source_value").reset_index()
weo_wide = weo_wide.rename(columns=builder.WEO_FIELDS)
reconciled = panel.merge(weo_wide, on=["iso3", "year"], how="left", suffixes=("_out", "_src"), validate="one_to_one")

reconciliation = {}
for column in builder.WEO_FIELDS.values():
    out = reconciled[f"{column}_out"]
    src = reconciled[f"{column}_src"]
    both = out.notna() & src.notna()
    reconciliation[column] = {
        "output_non_missing": int(out.notna().sum()),
        "source_non_missing": int(src.notna().sum()),
        "max_absolute_difference": float((out[both] - src[both]).abs().max()) if both.any() else None,
        "missingness_matches": bool(out.isna().equals(src.isna())),
    }
display(pd.DataFrame(reconciliation).T)

expected_interest = (panel["PrimaryBalance_gdp"] - panel["OverallBalance_gdp"]) / panel["Revenue_gdp"] * 100
expected_interest_mask = panel[["PrimaryBalance_gdp", "OverallBalance_gdp", "Revenue_gdp"]].notna().all(axis=1) & panel["Revenue_gdp"].ne(0)
interest_check = pd.Series({
    "output_non_missing": int(panel["interest_revenue"].notna().sum()),
    "expected_non_missing": int(expected_interest_mask.sum()),
    "missingness_matches": bool(panel["interest_revenue"].notna().equals(expected_interest_mask)),
    "max_absolute_difference": float((panel.loc[expected_interest_mask, "interest_revenue"] - expected_interest[expected_interest_mask]).abs().max()),
    "zero_revenue_gdp_rows": int(panel["Revenue_gdp"].eq(0).sum()),
})
interest_check
"""
        ),
        nbf.v4.new_markdown_cell("### 4. Review completeness"),
        nbf.v4.new_code_cell(
            """coverage = pd.DataFrame({
    "non_missing": panel.notna().sum(),
    "missing": panel.isna().sum(),
    "coverage_pct": panel.notna().mean().mul(100),
})
coverage
"""
        ),
        nbf.v4.new_markdown_cell("### 5. Review numeric distributions"),
        nbf.v4.new_code_cell(
            """panel.describe(percentiles=[0.25, 0.5, 0.75]).T
"""
        ),
        nbf.v4.new_markdown_cell(
            """## Takeaways

- 面板键和行数检查通过，基础字段在改名后逐值保持一致。
- 六个 WEO 字段与源值及缺失位置一致，未发生单位缩放。
- `interest_revenue` 严格按 `((PrimaryBalance_gdp - OverallBalance_gdp) / Revenue_gdp) * 100` 计算，单位为百分数。
- 财政收入和总体余额缺失主要发生在样本早期；建模时应记录最终可用样本。
- CurrentGDP、ConstantGDP、revenue 和 debt 为十亿本币，适合国别内时间变化分析，不适合未经汇率或 PPP 转换的跨国水平比较。
"""
        ),
    ]
    nbf.write(notebook, OUTPUT_NOTEBOOK)


def execute_notebook():
    notebook = nbf.read(OUTPUT_NOTEBOOK, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="data-investing-py314",
        resources={"metadata": {"path": str(OUTPUT_DIR)}},
    )
    client.execute()
    nbf.write(notebook, OUTPUT_NOTEBOOK)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    weo_values, _, metadata, source_country_codes = read_weo_values()
    source_fields, source_rows, _, output_rows = write_merged_csv(weo_values)
    verify_preservation(source_fields, source_rows, output_rows)
    verify_weo_reconciliation(weo_values)
    data, coverage_rows, stat_rows, new_coverage_rows, quality = profile_output(
        source_rows, metadata, source_country_codes
    )

    expected_appended_columns = list(WEO_FIELDS.values()) + DERIVED_FIELDS
    if data.columns.tolist()[-len(expected_appended_columns):] != expected_appended_columns:
        raise AssertionError("The appended WEO columns are not in the requested order.")
    if "OB_gdp" in data.columns or "PrimaryBalance_gdp" not in data.columns:
        raise AssertionError("OB_gdp was not renamed correctly.")
    if quality["duplicate_keys"] or quality["weo_duplicate_series"]:
        raise AssertionError("Uniqueness check failed.")
    if quality["rows"] != quality["source_rows"]:
        raise AssertionError("Join changed the source row count.")
    if quality["unmatched_panel_isos"]:
        raise AssertionError("One or more panel ISO3 values are absent from WEO.")
    if not quality["interest_formula_missingness_matches"]:
        raise AssertionError("interest_revenue missingness does not match its inputs.")
    if quality["interest_formula_max_difference"] > 1e-12:
        raise AssertionError("interest_revenue does not match the requested formula.")

    write_documentation(coverage_rows, stat_rows, new_coverage_rows, quality)
    build_notebook(quality)
    execute_notebook()

    print(f"CSV: {OUTPUT_CSV}")
    print(f"Documentation: {OUTPUT_DOC}")
    print(f"Notebook: {OUTPUT_NOTEBOOK}")
    print(
        "Quality: "
        f"rows={quality['rows']}, columns={quality['columns']}, "
        f"countries={quality['countries']}, duplicate_keys={quality['duplicate_keys']}"
    )


if __name__ == "__main__":
    main()
