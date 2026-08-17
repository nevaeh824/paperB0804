from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Collection, Sequence

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_NON_SOVEREIGN = frozenset({"HKG", "TWN"})
NC_FILENAME = "HadEX3-0-4_wsdi_ann_1961-1990.nc"
BOUNDARY_FILENAME = "World Bank Official Boundaries - Admin 0.gpkg"
PANEL_FILENAME = "invest_panel_weo.csv"
PAPER_FILENAME = "WSDI指标.pdf"


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_panel_keys(
    path: Path,
    start_year: int,
    end_year: int,
    excluded_iso3: Collection[str],
    expected_source_rows: int,
    expected_source_iso3: int,
    expected_source_years: Collection[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(
        path,
        usecols=["country_name", "iso3", "year"],
        dtype={"country_name": "string", "iso3": "string", "year": "int64"},
    )

    if len(panel) != expected_source_rows:
        raise ValueError(
            f"unexpected panel row count: {len(panel)} != {expected_source_rows}"
        )
    if panel["iso3"].nunique() != expected_source_iso3:
        raise ValueError(
            "unexpected panel ISO3 count: "
            f"{panel['iso3'].nunique()} != {expected_source_iso3}"
        )
    if set(panel["year"]) != set(expected_source_years):
        raise ValueError("unexpected panel year coverage")
    if panel[["country_name", "iso3", "year"]].isna().any().any():
        raise ValueError("panel keys contain missing values")
    if not panel["iso3"].str.fullmatch(r"[A-Z]{3}").all():
        raise ValueError("panel contains invalid ISO3 codes")
    if panel.duplicated(["iso3", "year"]).any():
        raise ValueError("duplicate iso3-year keys in panel")
    if not panel.groupby("iso3")["country_name"].nunique().eq(1).all():
        raise ValueError("an ISO3 code maps to multiple country names")

    excluded_iso3 = set(excluded_iso3)
    excluded_rows = panel[panel["iso3"].isin(excluded_iso3)].copy()
    if set(excluded_rows["iso3"]) != excluded_iso3:
        missing = sorted(excluded_iso3 - set(excluded_rows["iso3"]))
        raise ValueError(f"excluded ISO3 codes not found in panel: {missing}")

    target = panel[
        panel["year"].between(start_year, end_year)
        & ~panel["iso3"].isin(excluded_iso3)
    ].copy()
    expected_years = set(range(start_year, end_year + 1))
    if set(target["year"]) != expected_years:
        raise ValueError("target panel does not cover every requested year")
    retained_iso3 = set(panel["iso3"]) - excluded_iso3
    expected_target_rows = len(retained_iso3) * len(expected_years)
    if len(target) != expected_target_rows:
        raise ValueError(
            f"target panel is not balanced: {len(target)} != {expected_target_rows}"
        )
    if target.duplicated(["iso3", "year"]).any():
        raise ValueError("duplicate iso3-year keys in target panel")

    target = target.sort_values(["iso3", "year"], ignore_index=True)
    excluded_rows = excluded_rows.sort_values(["iso3", "year"], ignore_index=True)
    return target, excluded_rows


def normalize_longitude(wsdi: xr.DataArray) -> xr.DataArray:
    if "longitude" not in wsdi.coords:
        raise ValueError("WSDI has no longitude coordinate")
    normalized = wsdi.assign_coords(
        longitude=((wsdi.longitude + 180) % 360) - 180
    ).sortby("longitude")
    longitude = np.asarray(normalized.longitude.values, dtype=float)
    if len(np.unique(longitude)) != len(longitude):
        raise ValueError("normalized longitude contains duplicates")
    if len(longitude) > 1 and not np.all(np.diff(longitude) > 0):
        raise ValueError("normalized longitude is not strictly increasing")
    if not np.all((longitude >= -180) & (longitude < 180)):
        raise ValueError("normalized longitude falls outside [-180, 180)")
    return normalized


def load_wsdi(
    path: Path,
    climate_start_year: int,
    climate_end_year: int,
    expected_source_start_year: int,
    expected_source_end_year: int,
    expected_source_time_count: int,
) -> xr.DataArray:
    with xr.open_dataset(path, decode_times=True, mask_and_scale=True) as dataset:
        if dataset.attrs.get("dataset_version") != "3.0.4":
            raise ValueError("unexpected HadEX3 dataset_version")
        if dataset.attrs.get("base_period") != "1961-1990":
            raise ValueError("unexpected HadEX3 base_period")
        if "WSDI" not in dataset:
            raise ValueError("NetCDF does not contain WSDI")
        source = dataset["WSDI"]
        if source.attrs.get("units") != "days":
            raise ValueError("unexpected WSDI units")
        if set(source.dims) != {"time", "latitude", "longitude"}:
            raise ValueError("unexpected WSDI dimensions")

        years = pd.DatetimeIndex(dataset["time"].values).year
        observed = (int(years.min()), int(years.max()), len(years))
        expected = (
            expected_source_start_year,
            expected_source_end_year,
            expected_source_time_count,
        )
        if observed != expected:
            raise ValueError(f"unexpected source time coverage: {observed} != {expected}")

        wsdi = source.sel(
            time=slice(
                f"{climate_start_year}-01-01",
                f"{climate_end_year}-12-31",
            )
        )
        wsdi = wsdi.where(wsdi != -99.9).load()

    if wsdi.sizes["time"] != climate_end_year - climate_start_year + 1:
        raise ValueError("selected WSDI period is incomplete")
    wsdi = normalize_longitude(wsdi)
    valid = np.asarray(wsdi.values)[np.isfinite(wsdi.values)]
    if valid.size and np.any(valid < 0):
        raise ValueError("WSDI contains negative valid values")
    return wsdi


def load_boundaries(
    path: Path,
    layer: str,
) -> tuple[gpd.GeoDataFrame, int]:
    adm0 = gpd.read_file(path, layer=layer, engine="pyogrio")
    source_feature_count = len(adm0)
    adm0.columns = [column.replace("\ufeff", "").strip() for column in adm0.columns]
    required = {"ISO_A3", "NAM_0", "geometry"}
    if not required.issubset(adm0.columns):
        raise ValueError(f"boundary layer is missing columns: {sorted(required - set(adm0.columns))}")

    for column in adm0.columns:
        if column == adm0.geometry.name:
            continue
        dtype = adm0[column].dtype
        if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
            adm0[column] = adm0[column].map(
                lambda value: value.replace("\ufeff", "").strip()
                if isinstance(value, str)
                else value
            )

    if adm0.crs is None:
        raise ValueError("boundary layer has no CRS")
    adm0 = adm0.to_crs(4326)
    invalid_geometry_count = int((~adm0.geometry.is_valid).sum())
    adm0["geometry"] = adm0.geometry.make_valid()
    if adm0.geometry.isna().any() or adm0.geometry.is_empty.any():
        raise ValueError("boundary layer contains missing or empty geometry")

    adm0 = adm0[adm0["ISO_A3"].str.fullmatch(r"[A-Z]{3}", na=False)].copy()
    countries = (
        adm0[["ISO_A3", "NAM_0", "geometry"]]
        .dissolve(by="ISO_A3", aggfunc={"NAM_0": "first"})
        .reset_index()
        .sort_values("ISO_A3", ignore_index=True)
    )
    if countries["ISO_A3"].duplicated().any():
        raise ValueError("boundary dissolve left duplicate ISO3 codes")
    if not countries.geometry.is_valid.all():
        raise ValueError("boundary dissolve produced invalid geometry")
    countries.attrs["source_feature_count"] = source_feature_count
    countries.attrs["invalid_geometry_count"] = invalid_geometry_count
    return countries, source_feature_count


def build_grid_membership(
    wsdi: xr.DataArray,
    countries: gpd.GeoDataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    grid = pd.MultiIndex.from_product(
        [wsdi.latitude.values, wsdi.longitude.values],
        names=["latitude", "longitude"],
    ).to_frame(index=False)
    points = gpd.GeoDataFrame(
        grid,
        geometry=gpd.points_from_xy(grid["longitude"], grid["latitude"]),
        crs=4326,
    )
    joined = gpd.sjoin(
        points,
        countries[["ISO_A3", "NAM_0", "geometry"]],
        how="inner",
        predicate="within",
    )
    membership = joined.drop(columns=["index_right", "geometry"])
    membership = membership.sort_values(
        ["latitude", "longitude", "ISO_A3"], ignore_index=True
    )

    assignment_counts = (
        membership.groupby(["latitude", "longitude"])["ISO_A3"]
        .nunique()
        .rename("n_iso3")
    )
    conflict_counts = assignment_counts[assignment_counts > 1]
    if conflict_counts.empty:
        conflicts = membership.iloc[0:0].copy()
        conflicts["n_iso3"] = pd.Series(dtype="int64")
    else:
        conflicts = membership.merge(
            conflict_counts,
            on=["latitude", "longitude"],
            how="inner",
            validate="many_to_one",
        ).sort_values(["latitude", "longitude", "ISO_A3"], ignore_index=True)

    iso3_with_grid = set(membership["ISO_A3"])
    countries_without_grid = countries.loc[
        ~countries["ISO_A3"].isin(iso3_with_grid), ["ISO_A3", "NAM_0"]
    ].sort_values("ISO_A3", ignore_index=True)
    return membership, conflicts, countries_without_grid


def aggregate_country_year(
    wsdi: xr.DataArray,
    membership: pd.DataFrame,
) -> pd.DataFrame:
    if membership.duplicated(["latitude", "longitude"]).any():
        raise ValueError("grid membership contains multi-country assignments")
    n_total = membership.groupby("ISO_A3").size().rename("n_total_cells")
    long = (
        wsdi.transpose("time", "latitude", "longitude")
        .to_dataframe(name="wsdi_days")
        .reset_index()
    )
    long["wsdi_days"] = long["wsdi_days"].astype("float64")
    long["year"] = pd.DatetimeIndex(long["time"]).year
    long = long.merge(
        membership[["latitude", "longitude", "ISO_A3", "NAM_0"]],
        on=["latitude", "longitude"],
        how="inner",
        validate="many_to_one",
    )
    country_year = (
        long.dropna(subset=["wsdi_days"])
        .groupby(["ISO_A3", "NAM_0", "year"], as_index=False, sort=True)
        .agg(
            wsdi_days=("wsdi_days", "mean"),
            n_valid_cells=("wsdi_days", "size"),
        )
        .merge(n_total, on="ISO_A3", validate="many_to_one")
    )
    country_year["n_valid_cells"] = country_year["n_valid_cells"].astype("int64")
    country_year["n_total_cells"] = country_year["n_total_cells"].astype("int64")
    country_year["grid_coverage_rate"] = (
        country_year["n_valid_cells"] / country_year["n_total_cells"]
    )
    return country_year.sort_values(["ISO_A3", "year"], ignore_index=True)


def apply_time_coverage_filter(
    country_year: pd.DataFrame,
    total_years: int,
    threshold: float,
    all_iso3: Collection[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if total_years <= 0:
        raise ValueError("total_years must be positive")
    if not 0 <= threshold <= 1:
        raise ValueError("coverage threshold must be between zero and one")
    observed_coverage = (
        country_year.groupby("ISO_A3")["year"]
        .nunique()
        .rename("n_valid_years_1951_2018")
        .reset_index()
    )
    if all_iso3 is None:
        coverage = observed_coverage
    else:
        coverage = pd.DataFrame({"ISO_A3": sorted(set(all_iso3))}).merge(
            observed_coverage,
            on="ISO_A3",
            how="left",
            validate="one_to_one",
        )
        coverage["n_valid_years_1951_2018"] = (
            coverage["n_valid_years_1951_2018"].fillna(0).astype("int64")
        )
    coverage = coverage.sort_values("ISO_A3", ignore_index=True)
    coverage["time_coverage_rate"] = (
        coverage["n_valid_years_1951_2018"] / total_years
    )
    coverage["passes_time_coverage"] = coverage["time_coverage_rate"] >= threshold
    with_coverage = country_year.merge(
        coverage,
        on="ISO_A3",
        how="left",
        validate="many_to_one",
    )
    filtered = with_coverage[with_coverage["passes_time_coverage"]].copy()
    filtered = filtered.sort_values(["ISO_A3", "year"], ignore_index=True)
    return filtered, coverage


def build_target_output(
    panel_keys: pd.DataFrame,
    country_year: pd.DataFrame,
    coverage: pd.DataFrame,
    countries_without_grid: pd.DataFrame,
) -> pd.DataFrame:
    coverage_columns = [
        "n_valid_years_1951_2018",
        "time_coverage_rate",
        "passes_time_coverage",
    ]
    metrics = country_year.drop(
        columns=[column for column in coverage_columns if column in country_year],
        errors="ignore",
    )
    target = panel_keys.merge(
        metrics,
        on=["iso3", "year"],
        how="left",
        validate="one_to_one",
    )
    coverage_for_merge = coverage.rename(columns={"ISO_A3": "iso3"})
    target = target.merge(
        coverage_for_merge[["iso3", *coverage_columns]],
        on="iso3",
        how="left",
        validate="many_to_one",
    )

    available = target["wsdi_days"].notna()
    no_grid_iso3 = set(countries_without_grid["ISO_A3"])
    failed_coverage_iso3 = set(
        coverage.loc[~coverage["passes_time_coverage"], "ISO_A3"]
    )
    missing_reason = pd.Series(pd.NA, index=target.index, dtype="string")
    missing_reason.loc[~available & target["iso3"].isin(no_grid_iso3)] = (
        "no_grid_center"
    )
    missing_reason.loc[
        ~available
        & missing_reason.isna()
        & target["iso3"].isin(failed_coverage_iso3)
    ] = "failed_time_coverage"
    missing_reason.loc[~available & missing_reason.isna()] = "missing_annual_value"
    target["wsdi_source_status"] = np.where(
        available,
        "available",
        "missing_in_source_or_coverage_filter",
    )
    target["wsdi_missing_reason"] = missing_reason
    return target.sort_values(["iso3", "year"], ignore_index=True)


def validate_outputs(
    target: pd.DataFrame,
    country_year: pd.DataFrame,
    expected_target_rows: int,
    expected_target_iso3: int,
    start_year: int,
    end_year: int,
    unmatched_target_iso3: Collection[str],
    coverage_threshold: float = 0.80,
) -> dict[str, int]:
    if len(target) != expected_target_rows:
        raise ValueError(
            f"unexpected target row count: {len(target)} != {expected_target_rows}"
        )
    if target["iso3"].nunique() != expected_target_iso3:
        raise ValueError("unexpected target ISO3 count")
    if set(target["year"]) != set(range(start_year, end_year + 1)):
        raise ValueError("unexpected target year coverage")
    if target[["country_name", "iso3", "year"]].isna().any().any():
        raise ValueError("target keys contain missing values")
    if target.duplicated(["iso3", "year"]).any():
        raise ValueError("duplicate iso3-year keys in target output")
    if set(target["iso3"]) & {"HKG", "TWN"}:
        raise ValueError("excluded non-sovereign codes remain in target output")
    if list(unmatched_target_iso3):
        raise ValueError(
            f"target ISO3 codes do not match boundaries: {sorted(unmatched_target_iso3)}"
        )

    if country_year.duplicated(["iso3", "year"]).any():
        raise ValueError("duplicate iso3-year keys in country-year output")
    if not country_year["wsdi_days"].ge(0).all():
        raise ValueError("country-year WSDI contains negative or missing values")
    if not (
        country_year["n_valid_cells"].gt(0)
        & country_year["n_valid_cells"].le(country_year["n_total_cells"])
    ).all():
        raise ValueError("invalid country-year grid cell counts")
    if not country_year["grid_coverage_rate"].between(0, 1, inclusive="right").all():
        raise ValueError("invalid country-year grid coverage rate")
    if not country_year["time_coverage_rate"].ge(coverage_threshold).all():
        raise ValueError("country-year output includes failed time coverage")

    available = target["wsdi_days"].notna()
    if not target.loc[available, "wsdi_source_status"].eq("available").all():
        raise ValueError("available WSDI rows have an invalid source status")
    if not target.loc[available, "wsdi_missing_reason"].isna().all():
        raise ValueError("available WSDI rows have a missing reason")
    if not target.loc[~available, "wsdi_source_status"].eq(
        "missing_in_source_or_coverage_filter"
    ).all():
        raise ValueError("missing WSDI rows have an invalid source status")
    allowed_reasons = {
        "no_grid_center",
        "failed_time_coverage",
        "missing_annual_value",
    }
    if not set(target.loc[~available, "wsdi_missing_reason"]).issubset(
        allowed_reasons
    ):
        raise ValueError("target output contains an invalid missing reason")

    return {
        "target_rows": int(len(target)),
        "target_iso3": int(target["iso3"].nunique()),
        "target_years": int(target["year"].nunique()),
        "available_rows": int(available.sum()),
        "missing_rows": int((~available).sum()),
        "duplicate_target_keys": int(target.duplicated(["iso3", "year"]).sum()),
        "country_year_rows": int(len(country_year)),
        "country_year_iso3": int(country_year["iso3"].nunique()),
    }


def _sorted_copy(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    present_keys = [key for key in keys if key in frame.columns]
    if not present_keys or frame.empty:
        return frame.copy()
    return frame.sort_values(present_keys, ignore_index=True)


def write_outputs(
    root: Path,
    country_year: pd.DataFrame,
    target: pd.DataFrame,
    membership: pd.DataFrame,
    coverage: pd.DataFrame,
    conflicts: pd.DataFrame,
    countries_without_grid: pd.DataFrame,
    excluded_rows: pd.DataFrame,
    input_hashes: pd.DataFrame,
    qa_summary: dict,
) -> dict[str, Path]:
    processed_dir = root / "data" / "processed"
    logs_dir = root / "logs"
    processed_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "country_year": processed_dir / "wsdi_country_year_1951_2018.parquet",
        "target": processed_dir / "wsdi_sovereign61_1995_2018.csv",
        "membership": logs_dir / "country_grid_membership.csv",
        "coverage": logs_dir / "country_coverage.csv",
        "conflicts": logs_dir / "spatial_join_conflicts.csv",
        "countries_without_grid": logs_dir / "countries_without_grid.csv",
        "excluded": logs_dir / "excluded_non_sovereign.csv",
        "input_hashes": logs_dir / "input_hashes.csv",
        "qa_summary": logs_dir / "qa_summary.json",
    }

    _sorted_copy(country_year, ["iso3", "year"]).to_parquet(
        paths["country_year"], index=False
    )
    _sorted_copy(target, ["iso3", "year"]).to_csv(
        paths["target"], index=False, encoding="utf-8-sig"
    )
    csv_outputs = {
        "membership": (membership, ["latitude", "longitude", "ISO_A3"]),
        "coverage": (coverage, ["ISO_A3"]),
        "conflicts": (conflicts, ["latitude", "longitude", "ISO_A3"]),
        "countries_without_grid": (countries_without_grid, ["ISO_A3"]),
        "excluded": (excluded_rows, ["iso3", "year"]),
        "input_hashes": (input_hashes, ["file"]),
    }
    for name, (frame, keys) in csv_outputs.items():
        _sorted_copy(frame, keys).to_csv(
            paths[name], index=False, encoding="utf-8-sig"
        )
    paths["qa_summary"].write_text(
        json.dumps(qa_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return paths


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build country-year WSDI indicators from HadEX3 grid data."
    )
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--climate-start-year", type=int, default=1951)
    parser.add_argument("--climate-end-year", type=int, default=2018)
    parser.add_argument("--empirical-start-year", type=int, default=1995)
    parser.add_argument("--empirical-end-year", type=int, default=2018)
    parser.add_argument("--coverage-threshold", type=float, default=0.80)
    parser.add_argument("--boundary-layer", default="WB_GAD_ADM0")
    return parser.parse_args(argv)


def _counts_as_int_dict(series: pd.Series) -> dict[str, int]:
    return {str(key): int(value) for key, value in series.items()}


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    if args.climate_start_year > args.climate_end_year:
        raise ValueError("climate start year is after climate end year")
    if args.empirical_start_year > args.empirical_end_year:
        raise ValueError("empirical start year is after empirical end year")
    if not (
        args.climate_start_year
        <= args.empirical_start_year
        <= args.empirical_end_year
        <= args.climate_end_year
    ):
        raise ValueError("empirical period must fall inside the climate period")

    source_paths = {
        "paper": root / PAPER_FILENAME,
        "netcdf": root / NC_FILENAME,
        "boundaries": root / BOUNDARY_FILENAME,
        "panel": root / PANEL_FILENAME,
    }
    missing_files = [str(path) for path in source_paths.values() if not path.is_file()]
    if missing_files:
        raise FileNotFoundError(f"missing source files: {missing_files}")

    input_hashes = pd.DataFrame(
        [
            {
                "file": path.name,
                "bytes": int(path.stat().st_size),
                "sha256": compute_sha256(path),
            }
            for path in source_paths.values()
        ]
    )

    panel_keys, excluded_rows = load_panel_keys(
        source_paths["panel"],
        start_year=args.empirical_start_year,
        end_year=args.empirical_end_year,
        excluded_iso3=EXCLUDED_NON_SOVEREIGN,
        expected_source_rows=1827,
        expected_source_iso3=63,
        expected_source_years=set(range(1995, 2024)),
    )
    if len(panel_keys) != 1464 or panel_keys["iso3"].nunique() != 61:
        raise ValueError("sovereign target panel is not 61 countries by 24 years")

    wsdi = load_wsdi(
        source_paths["netcdf"],
        climate_start_year=args.climate_start_year,
        climate_end_year=args.climate_end_year,
        expected_source_start_year=1901,
        expected_source_end_year=2018,
        expected_source_time_count=118,
    )
    countries, boundary_source_features = load_boundaries(
        source_paths["boundaries"], layer=args.boundary_layer
    )
    if boundary_source_features != 251:
        raise ValueError(
            f"unexpected boundary feature count: {boundary_source_features} != 251"
        )
    if countries["ISO_A3"].nunique() != 245:
        raise ValueError("unexpected dissolved boundary ISO3 count")

    target_iso3 = set(panel_keys["iso3"])
    unmatched_target_iso3 = sorted(target_iso3 - set(countries["ISO_A3"]))
    membership, conflicts, countries_without_grid = build_grid_membership(
        wsdi, countries
    )
    if not conflicts.empty:
        logs_dir = root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        conflicts.to_csv(
            logs_dir / "spatial_join_conflicts.csv",
            index=False,
            encoding="utf-8-sig",
        )
        raise ValueError(
            f"{conflicts[['latitude', 'longitude']].drop_duplicates().shape[0]} "
            "grid points belong to multiple countries"
        )

    raw_country_year = aggregate_country_year(wsdi, membership)
    total_climate_years = args.climate_end_year - args.climate_start_year + 1
    iso3_with_grid = set(membership["ISO_A3"])
    filtered_country_year, coverage = apply_time_coverage_filter(
        raw_country_year,
        total_years=total_climate_years,
        threshold=args.coverage_threshold,
        all_iso3=iso3_with_grid,
    )
    filtered_country_year = filtered_country_year.rename(
        columns={"ISO_A3": "iso3", "NAM_0": "boundary_name"}
    )
    filtered_country_year["wsdi_source_dataset"] = "HadEX3"
    filtered_country_year["wsdi_source_version"] = "3.0.4"
    filtered_country_year["base_period"] = "1961-1990"
    filtered_country_year["aggregation"] = "grid_center_arithmetic_mean"

    target = build_target_output(
        panel_keys,
        filtered_country_year,
        coverage,
        countries_without_grid,
    )
    boundary_names = countries.set_index("ISO_A3")["NAM_0"]
    total_cells = membership.groupby("ISO_A3").size()
    if "boundary_name" not in target:
        target["boundary_name"] = target["iso3"].map(boundary_names)
    else:
        target["boundary_name"] = target["boundary_name"].fillna(
            target["iso3"].map(boundary_names)
        )
    target["n_total_cells"] = target["n_total_cells"].fillna(
        target["iso3"].map(total_cells)
    ).astype("Int64")
    target["n_valid_cells"] = target["n_valid_cells"].astype("Int64")
    target["n_valid_years_1951_2018"] = target[
        "n_valid_years_1951_2018"
    ].astype("Int64")
    target["wsdi_source_dataset"] = "HadEX3"
    target["wsdi_source_version"] = "3.0.4"
    target["base_period"] = "1961-1990"
    target["aggregation"] = "grid_center_arithmetic_mean"

    validation_summary = validate_outputs(
        target,
        filtered_country_year,
        expected_target_rows=1464,
        expected_target_iso3=61,
        start_year=args.empirical_start_year,
        end_year=args.empirical_end_year,
        unmatched_target_iso3=unmatched_target_iso3,
        coverage_threshold=args.coverage_threshold,
    )

    target_no_grid = sorted(
        target_iso3 & set(countries_without_grid["ISO_A3"])
    )
    expected_output_paths = {
        "country_year": "data/processed/wsdi_country_year_1951_2018.parquet",
        "target": "data/processed/wsdi_sovereign61_1995_2018.csv",
        "membership": "logs/country_grid_membership.csv",
        "coverage": "logs/country_coverage.csv",
        "conflicts": "logs/spatial_join_conflicts.csv",
        "countries_without_grid": "logs/countries_without_grid.csv",
        "excluded": "logs/excluded_non_sovereign.csv",
        "input_hashes": "logs/input_hashes.csv",
        "qa_summary": "logs/qa_summary.json",
    }
    qa_summary = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "climate_start_year": args.climate_start_year,
            "climate_end_year": args.climate_end_year,
            "empirical_start_year": args.empirical_start_year,
            "empirical_end_year": args.empirical_end_year,
            "coverage_threshold": args.coverage_threshold,
            "boundary_layer": args.boundary_layer,
            "excluded_iso3": sorted(EXCLUDED_NON_SOVEREIGN),
        },
        "source": {
            "panel_rows": 1827,
            "panel_iso3": 63,
            "netcdf_time_values": int(wsdi.sizes["time"]),
            "netcdf_latitude_values": int(wsdi.sizes["latitude"]),
            "netcdf_longitude_values": int(wsdi.sizes["longitude"]),
            "boundary_features": int(boundary_source_features),
            "boundary_iso3_after_dissolve": int(countries["ISO_A3"].nunique()),
            "boundary_invalid_geometry_repairs": int(
                countries.attrs.get("invalid_geometry_count", 0)
            ),
        },
        "spatial": {
            "grid_points": int(wsdi.sizes["latitude"] * wsdi.sizes["longitude"]),
            "membership_rows": int(len(membership)),
            "conflict_rows": int(len(conflicts)),
            "conflict_grid_points": int(
                conflicts[["latitude", "longitude"]].drop_duplicates().shape[0]
            ),
            "countries_without_grid": int(len(countries_without_grid)),
            "target_countries_without_grid": target_no_grid,
            "target_boundary_matches": int(len(target_iso3) - len(unmatched_target_iso3)),
            "target_boundary_unmatched": unmatched_target_iso3,
        },
        "coverage": {
            "raw_country_year_rows": int(len(raw_country_year)),
            "countries_with_grid": int(len(iso3_with_grid)),
            "countries_passing_time_coverage": int(
                coverage["passes_time_coverage"].sum()
            ),
            "countries_failing_time_coverage": int(
                (~coverage["passes_time_coverage"]).sum()
            ),
            "filtered_country_year_rows": int(len(filtered_country_year)),
        },
        "target": {
            **validation_summary,
            "status_counts": _counts_as_int_dict(
                target["wsdi_source_status"].value_counts(dropna=False)
            ),
            "missing_reason_counts": _counts_as_int_dict(
                target["wsdi_missing_reason"].value_counts(dropna=False)
            ),
        },
        "outputs": expected_output_paths,
    }

    output_paths = write_outputs(
        root=root,
        country_year=filtered_country_year,
        target=target,
        membership=membership,
        coverage=coverage,
        conflicts=conflicts,
        countries_without_grid=countries_without_grid,
        excluded_rows=excluded_rows,
        input_hashes=input_hashes,
        qa_summary=qa_summary,
    )

    print("WSDI_BUILD_PASS")
    print(
        f"country_year_rows={len(filtered_country_year)}, "
        f"country_year_iso3={filtered_country_year['iso3'].nunique()}"
    )
    print(
        f"target_rows={len(target)}, target_iso3={target['iso3'].nunique()}, "
        f"available_rows={validation_summary['available_rows']}, "
        f"missing_rows={validation_summary['missing_rows']}"
    )
    print(f"target_countries_without_grid={target_no_grid}")
    for name, path in output_paths.items():
        print(f"{name}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
