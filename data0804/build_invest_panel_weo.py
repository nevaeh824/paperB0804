from __future__ import annotations

import csv
import math
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable

import pandas as pd
from openpyxl import load_workbook


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data0804"
BASE_CSV = PROJECT_ROOT / "cleaned_imf_like_panel_1995_2023.csv"
WEO_XLSX = next(PROJECT_ROOT.rglob("WEOApr2026all.xlsx"))
OUTPUT_CSV = OUTPUT_DIR / "invest_panel_weo.csv"
OUTPUT_DOC = OUTPUT_DIR / "invest_panel_weo_documentation.md"
OUTPUT_NOTEBOOK = OUTPUT_DIR / "invest_panel_weo_profile.ipynb"
WDI_RESERVES_CSV = OUTPUT_DIR / "API_FI.RES.TOTL.CD_DS2_en_csv_v2_14.csv"
NDGAIN_ROOT = OUTPUT_DIR / "ndgain_countryindex_2026" / "resources"
NDGAIN_CAPACITY_SOURCE = NDGAIN_ROOT / "vulnerability" / "capacity.csv"

WEO_FIELDS = OrderedDict(
    [
        ("GGR_NGDP", "Revenue_gdp"),
        ("NGDPD", "CurrentGDP"),
        ("NGDP_R", "ConstantGDP"),
        ("NGDPRPPPPC", "capitaGDP"),
        ("GGXCNL_NGDP", "OverallBalance_gdp"),
        ("GGR", "revenue"),
        ("GGXWDG", "debt"),
    ]
)
DERIVED_FIELDS = ["interest_revenue"]
YEARS = range(1995, 2024)
NDGAIN_DELTA_SOURCES = OrderedDict(
    [
        (
            "vulnerability_delta100",
            NDGAIN_ROOT / "vulnerability" / "vulnerability_delta.csv",
        ),
        (
            "readiness_delta100",
            NDGAIN_ROOT / "readiness" / "readiness_delta.csv",
        ),
    ]
)
NDGAIN_DELTA_ANCHORS = {
    "vulnerability_delta100": "vulnerability100",
    "readiness_delta100": "readiness100",
}


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


def format_decimal(value: Decimal) -> str:
    """Render a finite Decimal without exponent notation or binary-float drift."""
    if not value.is_finite():
        return ""
    rendered = format(value.normalize(), "f")
    return "0" if rendered in {"-0", ""} else rendered


def read_wdi_reserve_values(
    path: Path = WDI_RESERVES_CSV,
    years: Iterable[int] = YEARS,
) -> dict[tuple[str, int], str]:
    """Read FI.RES.TOTL.CD from a World Bank wide CSV with metadata preamble."""
    selected_years = list(years)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = csv.reader(handle)
        header = next(
            (row for row in raw_rows if row and row[0] == "Country Name"), None
        )
        if header is None:
            raise ValueError(f"WDI header row not found in {path}")
        required = {
            "Country Code",
            "Indicator Code",
            *(str(year) for year in selected_years),
        }
        missing_fields = required - set(header)
        if missing_fields:
            raise ValueError(
                f"WDI reserve source {path} is missing fields: {sorted(missing_fields)}"
            )
        rows = [dict(zip(header, row)) for row in raw_rows]

    values: dict[tuple[str, int], str] = {}
    seen_iso3: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        if clean_text(row.get("Indicator Code")) != "FI.RES.TOTL.CD":
            continue
        iso3 = clean_text(row.get("Country Code"))
        if not iso3:
            raise ValueError(f"Blank WDI Country Code at data row {row_number}: {path}")
        if iso3 in seen_iso3:
            raise ValueError(f"Duplicate WDI reserve ISO3: {iso3} in {path}")
        seen_iso3.add(iso3)
        for year in selected_years:
            raw_value = clean_text(row.get(str(year)))
            if not raw_value:
                continue
            try:
                reserve_usd = Decimal(raw_value)
            except InvalidOperation as error:
                raise ValueError(
                    f"Invalid WDI reserve at {iso3}-{year}: {raw_value}"
                ) from error
            if not reserve_usd.is_finite():
                raise ValueError(
                    f"Non-finite WDI reserve at {iso3}-{year}: {raw_value}"
                )
            values[(iso3, year)] = format_decimal(reserve_usd)
    if not seen_iso3:
        raise ValueError(f"No FI.RES.TOTL.CD rows found in {path}")
    return values


def calculate_reserves(ngdpd: str, reserve_usd: str) -> str:
    """Return reserves as a percent of current-price GDP in US dollars."""
    if not ngdpd or not reserve_usd:
        return ""
    try:
        denominator = Decimal(ngdpd)
        numerator = Decimal(reserve_usd)
    except InvalidOperation as error:
        raise ValueError(
            f"Invalid reserves inputs: NGDPD={ngdpd}, FI.RES.TOTL.CD={reserve_usd}"
        ) from error
    if not denominator.is_finite() or denominator <= 0:
        raise ValueError(f"NGDPD must be positive and finite; got {ngdpd}")
    if not numerator.is_finite():
        raise ValueError(f"FI.RES.TOTL.CD must be finite; got {reserve_usd}")
    return format_decimal(
        numerator / Decimal("1e9") / denominator * Decimal("100")
    )


def refresh_currentgdp_and_reserves(
    path: Path,
    weo_values: dict[tuple[str, int, str], str],
    reserve_values: dict[tuple[str, int], str],
) -> None:
    """Atomically refresh CurrentGDP=NGDPD and its same-currency reserve ratio."""
    fieldnames, rows = read_csv_rows(path)
    required = {"iso3", "year", "CurrentGDP", "reserves"}
    missing_fields = required - set(fieldnames)
    if missing_fields:
        raise ValueError(f"Target panel is missing fields: {sorted(missing_fields)}")
    keys = [(row["iso3"].strip(), int(row["year"])) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("The target panel contains duplicate iso3-year keys.")

    for row, (iso3, year) in zip(rows, keys):
        ngdpd = weo_values.get((iso3, year, "NGDPD"), "")
        row["CurrentGDP"] = ngdpd
        row["reserves"] = calculate_reserves(
            ngdpd, reserve_values.get((iso3, year), "")
        )

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def read_ndgain_delta_values(
    path: Path,
    years: Iterable[int] = YEARS,
) -> dict[tuple[str, int], str]:
    """Read one wide ND-GAIN delta file and return exact source values times 100."""
    fieldnames, rows = read_csv_rows(path)
    selected_years = list(years)
    required = {"ISO3", *(str(year) for year in selected_years)}
    missing_fields = required - set(fieldnames)
    if missing_fields:
        raise ValueError(
            f"ND-GAIN delta source {path} is missing fields: {sorted(missing_fields)}"
        )

    values: dict[tuple[str, int], str] = {}
    seen_iso3: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        iso3 = clean_text(row["ISO3"])
        if not iso3:
            raise ValueError(f"Blank ND-GAIN ISO3 at CSV row {row_number}: {path}")
        if iso3 in seen_iso3:
            raise ValueError(f"Duplicate ND-GAIN ISO3: {iso3} in {path}")
        seen_iso3.add(iso3)
        for year in selected_years:
            raw_value = clean_text(row[str(year)])
            if not raw_value:
                continue
            try:
                scaled = Decimal(raw_value) * Decimal("100")
            except InvalidOperation as error:
                raise ValueError(
                    f"Invalid ND-GAIN delta at {iso3}-{year}: {raw_value}"
                ) from error
            if not scaled.is_finite():
                raise ValueError(
                    f"Non-finite ND-GAIN delta at {iso3}-{year}: {raw_value}"
                )
            values[(iso3, year)] = format_decimal(scaled)
    return values


def read_ndgain_capacity_values(
    path: Path = NDGAIN_CAPACITY_SOURCE,
    years: Iterable[int] = YEARS,
) -> dict[tuple[str, int], str]:
    """Read the ND-GAIN capacity wide file without changing its 0--1 unit."""
    fieldnames, rows = read_csv_rows(path)
    selected_years = list(years)
    required = {"ISO3", *(str(year) for year in selected_years)}
    missing_fields = required - set(fieldnames)
    if missing_fields:
        raise ValueError(
            f"ND-GAIN capacity source {path} is missing fields: {sorted(missing_fields)}"
        )

    values: dict[tuple[str, int], str] = {}
    seen_iso3: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        iso3 = clean_text(row["ISO3"])
        if not iso3:
            raise ValueError(f"Blank ND-GAIN ISO3 at CSV row {row_number}: {path}")
        if iso3 in seen_iso3:
            raise ValueError(f"Duplicate ND-GAIN capacity ISO3: {iso3} in {path}")
        seen_iso3.add(iso3)
        for year in selected_years:
            raw_value = clean_text(row[str(year)])
            if not raw_value:
                continue
            try:
                capacity = Decimal(raw_value)
            except InvalidOperation as error:
                raise ValueError(
                    f"Invalid ND-GAIN capacity at {iso3}-{year}: {raw_value}"
                ) from error
            if not capacity.is_finite() or not Decimal("0") <= capacity <= Decimal("1"):
                raise ValueError(
                    f"ND-GAIN capacity must be finite and within [0, 1] at "
                    f"{iso3}-{year}; got {raw_value}"
                )
            values[(iso3, year)] = format_decimal(capacity)
    return values


def insert_ndgain_capacity_fieldname(fieldnames: Iterable[str]) -> list[str]:
    """Place capacity beside the vulnerability fields in the target panel."""
    output_fields = list(fieldnames)
    anchor = "vulnerability_delta100"
    if anchor not in output_fields:
        raise ValueError(f"Expected {anchor} in the target panel.")
    if "capacity" not in output_fields:
        output_fields.insert(output_fields.index(anchor) + 1, "capacity")
    return output_fields


def add_ndgain_capacity_column(
    path: Path,
    source: Path = NDGAIN_CAPACITY_SOURCE,
    years: Iterable[int] = YEARS,
) -> None:
    """Add or refresh capacity by exact iso3-year key without changing panel rows."""
    selected_years = list(years)
    capacity_values = read_ndgain_capacity_values(source, selected_years)
    fieldnames, rows = read_csv_rows(path)
    if not {"iso3", "year"}.issubset(fieldnames):
        raise ValueError("Expected iso3 and year in the target panel.")
    keys = [(row["iso3"].strip(), int(row["year"])) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("The target panel contains duplicate iso3-year keys.")

    output_fields = insert_ndgain_capacity_fieldname(fieldnames)
    for row, key in zip(rows, keys):
        row["capacity"] = capacity_values.get(key, "")

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def insert_ndgain_delta_fieldnames(fieldnames: Iterable[str]) -> list[str]:
    """Place each delta field immediately after its corresponding level field."""
    output_fields = list(fieldnames)
    for output_name, anchor in NDGAIN_DELTA_ANCHORS.items():
        if anchor not in output_fields:
            raise ValueError(f"Expected {anchor} in the target panel.")
        if output_name not in output_fields:
            output_fields.insert(output_fields.index(anchor) + 1, output_name)
    return output_fields


def add_ndgain_delta_columns(
    path: Path,
    sources: dict[str, Path] = NDGAIN_DELTA_SOURCES,
    years: Iterable[int] = YEARS,
) -> None:
    """Add or refresh both scaled ND-GAIN delta columns by exact iso3-year key."""
    if set(sources) != set(NDGAIN_DELTA_SOURCES):
        raise ValueError(
            f"Expected ND-GAIN delta outputs: {list(NDGAIN_DELTA_SOURCES)}"
        )
    selected_years = list(years)
    delta_values = {
        output_name: read_ndgain_delta_values(source, selected_years)
        for output_name, source in sources.items()
    }
    fieldnames, rows = read_csv_rows(path)
    if not {"iso3", "year"}.issubset(fieldnames):
        raise ValueError("Expected iso3 and year in the target panel.")
    keys = [(row["iso3"].strip(), int(row["year"])) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("The target panel contains duplicate iso3-year keys.")

    output_fields = insert_ndgain_delta_fieldnames(fieldnames)
    for row, key in zip(rows, keys):
        for output_name, values in delta_values.items():
            row[output_name] = values.get(key, "")

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def add_weo_column(
    path: Path,
    code: str,
    weo_values: dict[tuple[str, int, str], str],
) -> None:
    """Add or refresh one WEO field without changing row order or other values."""
    if code not in WEO_FIELDS:
        raise ValueError(f"Unsupported WEO field: {code}")
    output_name = WEO_FIELDS[code]
    fieldnames, rows = read_csv_rows(path)
    if not {"iso3", "year"}.issubset(fieldnames):
        raise ValueError("Expected iso3 and year in the target panel.")

    keys = [(row["iso3"].strip(), int(row["year"])) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("The target panel contains duplicate iso3-year keys.")

    output_fields = list(fieldnames)
    if output_name not in output_fields:
        mapping_names = list(WEO_FIELDS.values())
        output_position = mapping_names.index(output_name)
        preceding = [
            name for name in mapping_names[:output_position] if name in output_fields
        ]
        insert_at = output_fields.index(preceding[-1]) + 1 if preceding else len(output_fields)
        output_fields.insert(insert_at, output_name)

    for row, (iso3, year) in zip(rows, keys):
        row[output_name] = weo_values.get((iso3, year, code), "")

    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def write_merged_csv(
    weo_values: dict[tuple[str, int, str], str],
    ndgain_delta_values: dict[str, dict[tuple[str, int], str]] | None = None,
    reserve_values: dict[tuple[str, int], str] | None = None,
    capacity_values: dict[tuple[str, int], str] | None = None,
):
    source_fields, source_rows = read_csv_rows(BASE_CSV)
    if "OB_gdp" not in source_fields:
        raise ValueError("Expected OB_gdp in the base panel.")
    if "PrimaryBalance_gdp" in source_fields:
        raise ValueError("Base panel already contains PrimaryBalance_gdp.")

    renamed_fields = [
        "PrimaryBalance_gdp" if field == "OB_gdp" else field
        for field in source_fields
    ]
    output_fields = (
        insert_ndgain_capacity_fieldname(
            insert_ndgain_delta_fieldnames(renamed_fields)
        )
        + list(WEO_FIELDS.values())
        + DERIVED_FIELDS
    )
    if ndgain_delta_values is None:
        ndgain_delta_values = {
            output_name: read_ndgain_delta_values(source)
            for output_name, source in NDGAIN_DELTA_SOURCES.items()
        }
    if reserve_values is None:
        reserve_values = read_wdi_reserve_values()
    if capacity_values is None:
        capacity_values = read_ndgain_capacity_values()

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
        for output_name, values in ndgain_delta_values.items():
            output_row[output_name] = values.get((iso3, year), "")
        output_row["capacity"] = capacity_values.get((iso3, year), "")
        for code, output_name in WEO_FIELDS.items():
            output_row[output_name] = weo_values.get((iso3, year, code), "")
        output_row["reserves"] = calculate_reserves(
            output_row["CurrentGDP"], reserve_values.get((iso3, year), "")
        )
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
            if source_field == "reserves":
                continue
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
    reserve_values: dict[tuple[str, int], str] | None = None,
):
    data = pd.read_csv(OUTPUT_CSV)
    if reserve_values is None:
        reserve_values = read_wdi_reserve_values()
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
    capacity_series = data["capacity"]
    capacity_missing_by_year = (
        data.loc[capacity_series.isna()].groupby("year").size().sort_values(ascending=False)
    )
    capacity_top_missing = ", ".join(
        f"{int(year)}: {int(count)}"
        for year, count in capacity_missing_by_year.head(5).items()
    )
    new_coverage_rows.append(
        (
            "`capacity`",
            "ND-GAIN capacity",
            f"{int(capacity_series.notna().sum()):,}",
            f"{capacity_series.notna().mean() * 100:.2f}%",
            "0–1 指数",
            capacity_top_missing or "无",
        )
    )
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
                " / ".join(
                    part for part in (meta["scale"], meta["unit"]) if part
                ),
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

    expected_reserves = []
    for row in data.itertuples(index=False):
        key = (str(row.iso3), int(row.year))
        if pd.isna(row.CurrentGDP) or key not in reserve_values:
            expected_reserves.append(float("nan"))
        else:
            expected_reserves.append(
                float(calculate_reserves(str(row.CurrentGDP), reserve_values[key]))
            )
    expected_reserves_series = pd.Series(expected_reserves, index=data.index)
    expected_reserves_mask = expected_reserves_series.notna()
    reserves_formula_max_difference = float(
        (
            data.loc[expected_reserves_mask, "reserves"]
            - expected_reserves_series[expected_reserves_mask]
        )
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
            for column in ["capacity"]
            + list(NDGAIN_DELTA_SOURCES)
            + list(WEO_FIELDS.values())
            + DERIVED_FIELDS
        },
        "new_coverage": {
            column: float(data[column].notna().mean() * 100)
            for column in ["capacity"]
            + list(NDGAIN_DELTA_SOURCES)
            + list(WEO_FIELDS.values())
            + DERIVED_FIELDS
        },
        "zero_revenue_gdp": int(data["Revenue_gdp"].eq(0).sum()),
        "interest_formula_missingness_matches": bool(
            data["interest_revenue"].notna().equals(expected_interest_mask)
        ),
        "interest_formula_max_difference": formula_max_difference,
        "reserves_formula_missingness_matches": bool(
            data["reserves"].notna().equals(expected_reserves_mask)
        ),
        "reserves_formula_max_difference": reserves_formula_max_difference,
        "nonpositive_CurrentGDP": int(data["CurrentGDP"].le(0).sum()),
        "reserves_coverage": float(data["reserves"].notna().mean() * 100),
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
        ("`vulnerability_delta100`", "ND-GAIN 气候脆弱性 delta", "源 delta ×100", "`data0804/ndgain_countryindex_2026/resources/vulnerability/vulnerability_delta.csv`", "按 `iso3 + year` 左连接；每个非缺失源值乘以 100；HKG、TWN 因源文件无对应 ISO3 而留空"),
        ("`capacity`", "ND-GAIN capacity；Paper B 的 A 定义为 `1-capacity`", "0–1 指数", "`data0804/ndgain_countryindex_2026/resources/vulnerability/capacity.csv`", "按 `iso3 + year` 左连接；不缩放；HKG、TWN 因源文件无对应 ISO3 而留空"),
        ("`readiness100`", "ND-GAIN 气候准备度/韧性指数", "0–100 指数点（非百分比）", "基础面板；`宏观indicators/readiness.csv`", "原样复制；原基础面板已将 0–1 指数乘以 100，本次不再缩放"),
        ("`readiness_delta100`", "ND-GAIN 气候准备度/韧性 delta", "源 delta ×100", "`data0804/ndgain_countryindex_2026/resources/readiness/readiness_delta.csv`", "按 `iso3 + year` 左连接；每个非缺失源值乘以 100；HKG、TWN 因源文件无对应 ISO3 而留空"),
        ("`lnrgdp`", "实际 GDP 水平的自然对数", "自然对数；底层 `NGDP_R` 为十亿本币", "基础面板；IMF WEO `NGDP_R`", "原样复制；`ln(NGDP_R)`"),
        ("`growth`", "实际 GDP 年增长率", "%", "基础面板；IMF WEO `NGDP_RPCH`", "原样复制，不乘以 100"),
        ("`inflation_cpi`", "平均 CPI 年通胀率", "%", "基础面板；IMF WEO `PCPIPCH`", "原样复制，不乘以 100"),
        ("`debt_gdp`", "一般政府总债务占 GDP", "% of GDP", "基础面板；IMF WEO `GGXWDG_NGDP`", "原样复制，不乘以 100"),
        ("`PrimaryBalance_gdp`", "一般政府基础净借贷/净借款占 GDP", "% of GDP", "基础面板原 `OB_gdp`；IMF WEO `GGXONLB_NGDP`", "仅改名，数值原样复制；不乘以 100"),
        ("`reserves`", "含黄金国际储备占现价美元 GDP", "%", "`data0804/API_FI.RES.TOTL.CD_DS2_en_csv_v2_14.csv` 与 WEO `NGDPD`", "按 `iso3 + year` 计算 `FI.RES.TOTL.CD / 1e9 / NGDPD * 100`；任一输入缺失时留空"),
        ("`gee`", "政府有效性估计值", "WGI 估计值（约 -2.5 至 2.5）", "基础面板；WGI `GE.EST`", "原样复制"),
        ("`rqe`", "监管质量估计值", "WGI 估计值（约 -2.5 至 2.5）", "基础面板；WGI `RQ.EST`", "原样复制"),
        ("`tt`", "净易货贸易条件指数", "指数，2015=100", "基础面板；WDI `TT.PRI.MRCH.XD.WD`", "原样复制"),
        ("`is_advanced`", "发达经济体标识", "0/1", "基础面板；沿用 `原数据集/dataIMF.xlsx` 分类", "原样复制"),
        ("`Revenue_gdp`", "一般政府收入占 GDP", "% of GDP", "`data0804/WEOApr2026all.xlsx`，Countries 表，`GGR_NGDP`", "按 `iso3 + year` 左连接；WEO 原值，不乘以 100"),
        ("`CurrentGDP`", "现价 GDP（美元）", "十亿美元", "`data0804/WEOApr2026all.xlsx`，Countries 表，`NGDPD`", "按 `iso3 + year` 左连接；WEO 原值"),
        ("`ConstantGDP`", "固定价格 GDP（本币）", "十亿本币", "`data0804/WEOApr2026all.xlsx`，Countries 表，`NGDP_R`", "按 `iso3 + year` 左连接；WEO 原值"),
        ("`capitaGDP`", "固定价格人均 GDP（PPP）", "2021 ICP 基准国际元/人", "`data0804/WEOApr2026all.xlsx`，Countries 表，`NGDPRPPPPC`", "按 `iso3 + year` 左连接；WEO 原值"),
        ("`OverallBalance_gdp`", "一般政府净借贷（+）/净借款（-）占 GDP", "% of GDP", "`data0804/WEOApr2026all.xlsx`，Countries 表，`GGXCNL_NGDP`", "按 `iso3 + year` 左连接；WEO 原值，不乘以 100"),
        ("`revenue`", "一般政府收入（本币金额）", "十亿本币", "`data0804/WEOApr2026all.xlsx`，Countries 表，`GGR`", "按 `iso3 + year` 左连接；WEO 原值"),
        ("`debt`", "一般政府总债务（本币金额）", "十亿本币", "`data0804/WEOApr2026all.xlsx`，Countries 表，`GGXWDG`", "按 `iso3 + year` 左连接；WEO 原值"),
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
            ("WEO 国家匹配", f"基础面板未匹配 WEO 的 ISO3：{quality['unmatched_panel_isos'] or '无'}", "通过", "高", f"全部 {quality['countries']} 个国家/地区可在 WEO 七个目标系列中找到"),
            ("ND-GAIN 合并", f"capacity 缺失 {quality['new_missing']['capacity']}；vulnerability_delta100 缺失 {quality['new_missing']['vulnerability_delta100']}；readiness_delta100 缺失 {quality['new_missing']['readiness_delta100']}", "通过（来源覆盖边界）", "高", "三列均有 1,769 行；HKG、TWN 不在来源中，对应 58 行按左连接留空"),
            ("新增变量缺失", f"Revenue_gdp 缺失 {quality['new_missing']['Revenue_gdp']}；CurrentGDP 缺失 {quality['new_missing']['CurrentGDP']}；ConstantGDP 缺失 {quality['new_missing']['ConstantGDP']}；capitaGDP 缺失 {quality['new_missing']['capitaGDP']}；OverallBalance_gdp 缺失 {quality['new_missing']['OverallBalance_gdp']}；revenue 缺失 {quality['new_missing']['revenue']}；debt 缺失 {quality['new_missing']['debt']}；interest_revenue 缺失 {quality['new_missing']['interest_revenue']}", "中", "高", "建模或均值比较需报告最终可用样本，并检查早期年份选择性缺失"),
            ("interest_revenue 公式", f"缺失位置一致={quality['interest_formula_missingness_matches']}；公式最大绝对误差={quality['interest_formula_max_difference']:.3g}；Revenue_gdp 为 0 的行数={quality['zero_revenue_gdp']}", "通过", "高", "该列单位为百分数；例如 5 表示利息支出约占收入 5%"),
            ("reserves 公式", f"缺失位置一致={quality['reserves_formula_missingness_matches']}；公式最大绝对误差={quality['reserves_formula_max_difference']:.3g}；CurrentGDP 非正值={quality['nonpositive_CurrentGDP']}", "通过", "高", "分子与分母均为美元；数值 5 表示储备约为现价 GDP 的 5%"),
            ("金额单位可比性", "CurrentGDP 为十亿美元；ConstantGDP、revenue 和 debt 仍为十亿本币", "中", "高", "CurrentGDP 可按统一美元口径比较；其他本币金额不可直接跨国比较"),
        ],
    )

    text = f"""# invest_panel_weo 数据说明与 Overview

## 1. 交付内容

- 数据文件：`data0804/invest_panel_weo.csv`
- 基础数据：`cleaned_imf_like_panel_1995_2023.csv`
- WEO 数据：`data0804/WEOApr2026all.xlsx`（April 2026 WEO，`Countries` 工作表）
- 可复核代码：`data0804/build_invest_panel_weo.py`
- 质量核验 notebook：`data0804/invest_panel_weo_profile.ipynb`

输出包含 {quality['rows']:,} 行、{quality['columns']} 列、{quality['countries']} 个国家/地区，年份为 {quality['year_min']}–{quality['year_max']}。以 `iso3 + year` 为唯一键，原面板行序和原字段数值均被保留；`OB_gdp` 仅重命名为 `PrimaryBalance_gdp`。`capacity` 位于 vulnerability 字段之后，保持 0–1 源单位；其余 WEO 与派生列位于面板末尾。

## 2. 单位和缩放规则

- WEO 百分比变量保留 Excel 中的原始百分数/百分比点表示。例如 WEO 的 `38.031` 仍写为 `38.031`，不转换为 `0.38031`，也不再乘以 100。
- 本次没有对任何从基础面板复制的数值做二次缩放。
- `vulnerability100` 与 `readiness100` 是基础面板中已有的 0–100 指数点，名字中的 `100` 不代表本次进行了缩放。
- `capacity` 逐键等于 ND-GAIN 源文件中的 0–1 值；Paper B 在估计阶段定义 `A = 1 - capacity`。
- `vulnerability_delta100` 与 `readiness_delta100` 将相应 ND-GAIN delta 源值乘以 100；HKG、TWN 不在两个 delta 来源中，故对应 58 个国家年度行留空。
- `CurrentGDP` 取 WEO `NGDPD`，单位为十亿美元；`reserves` 按 `FI.RES.TOTL.CD / 1e9 / NGDPD * 100` 重新计算，单位为百分比。
- `interest_revenue` 是百分数，按 `((PrimaryBalance_gdp - OverallBalance_gdp) / Revenue_gdp) * 100` 计算；数值 5 表示约 5%。

## 3. 变量定义、单位与来源

{variable_table}

## 4. WEO 合并覆盖

WEO 中七个目标指标各有 197 条唯一 country–indicator 行；在 1995–2023 至少有一个非缺失值的国家/地区中，`NGDPRPPPPC` 覆盖 195 个，`NGDP_R` 覆盖 196 个，其余目标系列覆盖 197 个；基础面板的 {quality['countries']} 个 ISO3 全部存在于 WEO。合并为严格的左连接，行数从 {quality['source_rows']:,} 保持为 {quality['rows']:,}，没有一对多扩张。

{new_coverage_table}

## 5. 全字段覆盖率

{coverage_table}

## 6. 数值变量描述统计

统计量按非缺失观察计算。`CurrentGDP` 为十亿美元；`ConstantGDP`、`revenue` 和 `debt` 为不同本币单位的十亿本币，不可直接做跨国水平比较；`capitaGDP` 为固定价格 PPP 国际元/人，尺度可跨国比较，但仍应结合各国价格与统计口径解释。

{stats_table}

## 7. 数据质量结论

{quality_table}

总体判断：新文件的键、行数、列映射、WEO 合并、`interest_revenue` 与 `reserves` 公式可靠；主要限制是财政和储备源在部分国家年度存在缺失，以及 ConstantGDP、revenue、debt 等本币金额不适合直接做跨国水平比较。

## 8. 复现与假设

- 运行：`py -3.14 data0804/build_invest_panel_weo.py`
- WEO 合并键假设：基础面板 `iso3` 与 WEO `COUNTRY.ID` 使用相同 ISO3 体系。
- WDI 储备合并键假设：目标 `iso3` 与 World Bank `Country Code` 使用相同 ISO3 体系；不补零、不插值。
- 新增变量只提取 1995–2023，与基础面板时间范围一致；不引入 WEO 2024–2031 的估计/预测年份。
- ND-GAIN capacity 与 delta 均通过精确 ISO3 与年份匹配；capacity 保持 0–1，delta 使用十进制定点运算乘以 100；不补零、不插值。
- CSV 使用 UTF-8 编码，缺失值写为空字段。
"""
    OUTPUT_DOC.write_text(text, encoding="utf-8")


def build_notebook(quality):
    import nbformat as nbf

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
- 新增 WEO GDP 列覆盖率：CurrentGDP {quality['new_coverage']['CurrentGDP']:.2f}%，ConstantGDP {quality['new_coverage']['ConstantGDP']:.2f}%，capitaGDP {quality['new_coverage']['capitaGDP']:.2f}%；财政金额列覆盖率：revenue {quality['new_coverage']['revenue']:.2f}%，debt {quality['new_coverage']['debt']:.2f}%。
- CurrentGDP 来自 WEO `NGDPD`（十亿美元）；reserves 覆盖率为 {quality['reserves_coverage']:.2f}%，并按 WDI 美元储备除以 NGDPD 后乘 100。
- ND-GAIN capacity 与 delta 三列覆盖率均为 {quality['new_coverage']['capacity']:.2f}%（1,769/1,827）；HKG、TWN 的 58 行因来源无对应 ISO3 而留空。
- 派生列 interest_revenue 覆盖率为 {quality['new_coverage']['interest_revenue']:.2f}%，公式最大绝对误差为 {quality['interest_formula_max_difference']:.3g}。
- WEO 百分数保持原始百分比点单位，没有乘以 100。
"""
        ),
        nbf.v4.new_markdown_cell(
            """## Context & Methods

本 notebook 是 CSV 与说明文档的审计附件。它重新读取基础面板、输出面板、WEO 七个目标系列与 WDI 储备，检查字段保留、唯一键、左连接行数、WEO 数值一致性、派生公式、缺失率和描述统计。

### Key Assumptions

- `iso3 + year` 是目标面板唯一键。
- WEO `COUNTRY.ID` 与基础面板 `iso3` 可直接匹配。
- World Bank `Country Code` 与基础面板 `iso3` 可直接匹配。
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
            """expected_columns = builder.insert_ndgain_capacity_fieldname(builder.insert_ndgain_delta_fieldnames(["PrimaryBalance_gdp" if c == "OB_gdp" else c for c in base.columns])) + list(builder.WEO_FIELDS.values()) + builder.DERIVED_FIELDS

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
- 七个 WEO 字段与源值及缺失位置一致，未发生单位缩放。
- `CurrentGDP` 为 WEO `NGDPD` 的十亿美元原值；`reserves` 按 `FI.RES.TOTL.CD / 1e9 / NGDPD * 100` 计算。
- ND-GAIN capacity 保持 0–1 源值，两个 delta 字段精确乘以 100；三者均按 ISO3--年份左连接，HKG、TWN 保持缺失。
- `interest_revenue` 严格按 `((PrimaryBalance_gdp - OverallBalance_gdp) / Revenue_gdp) * 100` 计算，单位为百分数。
- 财政收入和总体余额缺失主要发生在样本早期；建模时应记录最终可用样本。
- CurrentGDP 为十亿美元；ConstantGDP、revenue 和 debt 为十亿本币，不适合未经汇率或 PPP 转换的跨国水平比较；capitaGDP 为固定价格 PPP 国际元/人。
"""
        ),
    ]
    nbf.write(notebook, OUTPUT_NOTEBOOK)


def execute_notebook():
    import nbformat as nbf
    from nbclient import NotebookClient

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
    reserve_values = read_wdi_reserve_values()
    ndgain_delta_values = {
        output_name: read_ndgain_delta_values(source)
        for output_name, source in NDGAIN_DELTA_SOURCES.items()
    }
    capacity_values = read_ndgain_capacity_values()
    source_fields, source_rows, _, output_rows = write_merged_csv(
        weo_values, ndgain_delta_values, reserve_values, capacity_values
    )
    verify_preservation(source_fields, source_rows, output_rows)
    verify_weo_reconciliation(weo_values)
    data, coverage_rows, stat_rows, new_coverage_rows, quality = profile_output(
        source_rows, metadata, source_country_codes, reserve_values
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
    if not quality["reserves_formula_missingness_matches"]:
        raise AssertionError("reserves missingness does not match NGDPD and WDI inputs.")
    if quality["reserves_formula_max_difference"] > 1e-12:
        raise AssertionError("reserves does not match the requested formula.")
    if quality["nonpositive_CurrentGDP"]:
        raise AssertionError("CurrentGDP contains nonpositive NGDPD values.")
    for output_name, values in ndgain_delta_values.items():
        nonmissing = sum(
            (row["iso3"].strip(), int(row["year"])) in values
            for row in output_rows
        )
        if nonmissing != 1769:
            raise AssertionError(
                f"Unexpected {output_name} coverage: {nonmissing}; expected 1769."
            )
    capacity_nonmissing = sum(
        (row["iso3"].strip(), int(row["year"])) in capacity_values
        for row in output_rows
    )
    if capacity_nonmissing != 1769:
        raise AssertionError(
            f"Unexpected capacity coverage: {capacity_nonmissing}; expected 1769."
        )

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
