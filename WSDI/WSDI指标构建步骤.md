# WSDI 国家—年份指标构建步骤

## 1. 目标与最终口径

本项目的目标是把年度格点 WSDI 聚合为国家—年份指标，并与 [invest_panel_weo.csv](invest_panel_weo.csv) 的国家和年份主键一致。

论文基准口径为：

- 指标：Warm Spell Duration Index（WSDI，暖期持续指数）。
- 基准期：1961—1990 年。
- HadEX3 文件中的正式定义：一年内所有“日最高气温连续至少 6 天高于该日历日基准期第 90 百分位数”的事件所贡献的总天数。
- 单位：天；年度值可以是小数，因为 HadEX3 格点产品经过空间格点化处理，不应四舍五入成整数。
- 国家聚合：把落在一国边界内的有效格点值做算术平均；不做面积加权和人口加权。
- 论文复现气候面板：先保留 1951—2018 年，并剔除有效时间覆盖率低于 80% 的国家。
- 本项目目标实证期：1995—2018 年。
- 本项目目标国家：先从 `invest_panel_weo.csv` 读取 63 个 ISO3 国家或经济体，再按“联合国会员国”这一可复现标准去除非主权经济体 `HKG` 和 `TWN`，最终保留 61 个主权国家。

现有 HadEX3 3.0.4 文件覆盖至 2018 年，能够支持本项目完整的 1995—2018 实证期，不需要跨数据源扩展年份。

> 论文文字有时写成“超过 6 个连续日”，但 NetCDF 变量元数据明确写的是“6 个或更多连续日”。由于本文件已经由 HadEX3 按 ETCCDI 口径计算完成，复现时应以文件定义的“至少 6 天”为准，不再自行改变阈值。

## 2. 已有文件与核验结果

### 2.1 论文

文件：[WSDI指标.pdf](WSDI指标.pdf)

相关位置：第 3.1 节、表 1、表 3 和附录表 A1。论文说明使用 HadEX3，以 1961—1990 年为参考期，并按经纬度格点对各国做算术平均。

### 2.2 HadEX3 NetCDF

文件：[HadEX3-0-4_wsdi_ann_1961-1990.nc](HadEX3-0-4_wsdi_ann_1961-1990.nc)

实际元数据如下：

| 项目 | 值 |
|---|---|
| 数据集版本 | HadEX3 3.0.4 |
| 变量名 | `WSDI`，注意为大写 |
| 变量维度 | `longitude × latitude × time` |
| 网格 | 192 × 144 |
| 经度 | 0.9375°—359.0625°，步长 1.875° |
| 纬度 | −89.375°—89.375°，步长 1.25° |
| 时间 | 1901—2018 年，共 118 个年度值 |
| 单位 | `days` |
| 缺失值 | `-99.9`，按 CF 解码后应为 `NaN` |
| 基准期 | 1961—1990 年 |
| 空间坐标问题 | 经度为 0—360，需要转换为 −180—180 |

1995—2018 年共有 24 个年度值。该期间原始全球网格约 79.78% 为缺失值，主要因为海洋格点和观测覆盖范围，不应把全球缺失率直接当成数据故障。2018 年有效格点数为 4,908，低于 1995—2009 年约 5,700 个的水平，后续需要把这一覆盖下降作为稳健性检查。

英国气象局的 [HadEX3 官方页面](https://www.metoffice.gov.uk/hadobs/hadex3/index.html)和[产品指南](https://www.metoffice.gov.uk/hadobs/hadex3/hadex3_product_user_guide.pdf)均说明当前 ETCCDI 版本为 3.0.4、覆盖 1901—2018 年，与本项目的实证期终点一致。

### 2.3 世界银行国界 GeoPackage

文件：[World Bank Official Boundaries - Admin 0.gpkg](World Bank Official Boundaries - Admin 0.gpkg)

实际结构如下：

| 项目 | 值 |
|---|---|
| 图层名 | `WB_GAD_ADM0` |
| 行数 | 251 |
| 几何类型 | `MULTIPOLYGON` |
| 坐标系 | EPSG:4326 |
| 推荐国家键 | `ISO_A3` |
| 名称字段 | `NAM_0` |
| 唯一行政记录键 | `ADM0CD_c` |

必须处理两个数据问题：

1. 属性列名和字符串值前都带有不可见的 BOM 字符 `\ufeff`，必须同时清理列名与文本值。
2. `ISO_A3` 只有 245 个不同值，并非逐行唯一。例如西班牙、澳大利亚、英国和 BES 均有分离领土记录。空间连接前应按 `ISO_A3` 合并边界；不要使用存在异常值的 `SOV_ISO_A3` 作为主键。

应用主权国家筛选后，61 个目标 ISO3 均能在该边界文件中匹配。

### 2.4 目标实证面板

文件：[invest_panel_weo.csv](invest_panel_weo.csv)

实际结构：

| 项目 | 值 |
|---|---|
| 行数 | 1,827 |
| 列数 | 28 |
| 源文件国家或经济体数 | 63 |
| 排除的非主权经济体 | `HKG`、`TWN` |
| 本项目主权国家数 | 61 |
| 源文件年份 | 1995—2023，共 29 年 |
| 本项目使用年份 | 1995—2018，共 24 年 |
| 本项目目标面板 | 61 × 24 = 1,464 个主键 |
| 合并主键 | `iso3 + year` |
| 主键缺失 | 0 |
| 主键重复 | 0 |
| ISO3 格式异常 | 0 |

国家清单和目标年份先从该文件读取，再使用固定、可审计的排除清单删除 `HKG` 和 `TWN`。本项目将[联合国会员国名单](https://www.un.org/about-us/member-states)作为主权国家操作口径；其中香港特别行政区依据[香港基本法第一章](https://www.basiclaw.gov.hk/en/basiclaw/chapter1.html?module=inline&pgtype=article)属于中华人民共和国的一部分。该筛选是为了定义实证样本，不用于对争议地位作额外政治判断。`country_name` 只用于显示，合并键固定为 `iso3 + year`。

### 2.5 输入文件指纹

为保证以后能够确定是否使用了同一版本，记录 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `WSDI指标.pdf` | `19B31F5BD9F766DF8B3EB2E8B5212FBB0C88A240914408DFC6C8777E01EB34F1` |
| `HadEX3-0-4_wsdi_ann_1961-1990.nc` | `667FE4E01F55FD2DE2FCF8CAEDCD2AB46F58D7B12B6582984A6BAB78F658C558` |
| `World Bank Official Boundaries - Admin 0.gpkg` | `A8F9860ADBACDC21887F1E7375DE9D7744A858E9771FB1A3C8179F2927B304F5` |
| `invest_panel_weo.csv` | `928D33F014A922E9A74264FEEC1D83708249C5F547D3877A2209689D866C3447` |

## 3. 推荐项目结构

原始文件应只读保存，派生文件单独输出：

```text
WSDI/
├─ data/
│  ├─ raw/
│  │  ├─ HadEX3-0-4_wsdi_ann_1961-1990.nc
│  │  ├─ World Bank Official Boundaries - Admin 0.gpkg
│  │  └─ invest_panel_weo.csv
│  └─ processed/
│     ├─ wsdi_country_year_1951_2018.parquet
│     └─ wsdi_sovereign61_1995_2018.csv
├─ scripts/
│  └─ build_wsdi_country.py
├─ logs/
│  ├─ country_grid_membership.csv
│  ├─ country_coverage.csv
│  ├─ spatial_join_conflicts.csv
│  ├─ excluded_non_sovereign.csv
│  └─ qa_summary.json
└─ WSDI指标构建步骤.md
```

建议把 Parquet 作为保留数据类型和精度的主文件，把 CSV 或 Stata `.dta` 作为模型合并用的交换文件。

## 4. 软件环境

推荐使用 Conda，以避免 GeoPandas、GDAL 与 NetCDF 二进制依赖不一致：

```bash
conda create -n wsdi python=3.11 -y
conda activate wsdi
conda install -c conda-forge xarray netcdf4 pandas numpy geopandas pyogrio shapely pyarrow matplotlib jupyterlab -y
```

运行后保存环境：

```bash
conda env export --from-history > environment.yml
```

## 5. 构建流程

### 步骤 1：读取并验证 NetCDF

读取时启用 CF 解码和缺失值掩膜。只使用变量 `WSDI`，不要从此文件尝试重算第 90 百分位数，因为文件中没有逐日最高气温。

强制校验：

- `dataset_version == "3.0.4"`；
- `base_period == "1961-1990"`；
- `WSDI.units == "days"`；
- `time` 覆盖 1901—2018；
- 变量包含 `time`、`latitude`、`longitude` 三个维度；
- 有效值不小于 0；
- 不要把小数值取整。

### 步骤 2：统一经度坐标

将 NetCDF 的 0—360 经度转换为边界数据使用的 −180—180：

```python
lon_new = ((longitude + 180) % 360) - 180
```

转换后按经度重新排序，并校验经度唯一、严格递增、范围落在 `[−180, 180)`。这一操作必须发生在生成格点几何之前。

### 步骤 3：读取并清洗国界

读取 `WB_GAD_ADM0` 后：

1. 删除所有列名中的 `\ufeff` 并去除首尾空格。
2. 对所有文本列删除值中的 `\ufeff` 并去除首尾空格。
3. 把坐标系统一为 EPSG:4326。
4. 修复无效几何，并记录修复数量。
5. 仅保留符合三位大写代码格式的 `ISO_A3`。
6. 按 `ISO_A3` dissolve，把本土、岛屿和分离领土合并到一个国家几何中。

国家名只用于展示；后续合并必须使用 ISO3 代码，不使用国家名称字符串。

### 步骤 4：建立固定的“格点—国家”映射

HadEX3 网格在所有年份固定，因此空间连接只做一次：

1. 对 144 × 192 个格点中心创建点几何。
2. 使用点在多边形内部的空间关系，把格点分配到 `ISO_A3`。
3. 保存 `longitude`、`latitude`、`ISO_A3` 的静态映射表。
4. 检查一个格点是否被分配给多个 ISO3；如有，写入冲突日志并人工核查，不得直接保留第一条。
5. 记录没有任何格点中心的小国或地区。论文基准法不应自动用最近格点替代它们。

这里使用的是格点中心归属法，而不是格网与国界相交面积法。这是与论文“按经纬度格点做算术平均”最一致的解释。

### 步骤 5：转成长表并计算国家年度均值

先选择 1951—2018 年，然后把 `WSDI(time, latitude, longitude)` 转为长表，与固定格点映射按经纬度合并。删除当年为缺失值的格点后，对每个 `ISO_A3 × year` 计算：

\[
WSDI_{i,t}=\frac{1}{N_{i,t}}\sum_{g\in i,\;valid}WSDI_{g,t}
\]

其中，`N(i,t)` 为国家 `i` 在年份 `t` 的有效格点数。基准结果不乘 `cos(latitude)`，也不使用人口权重。

每条记录同时保留：

- `n_valid_cells`：该国该年的有效格点数；
- `n_total_cells`：静态分配给该国的格点总数；
- `grid_coverage_rate = n_valid_cells / n_total_cells`；
- `wsdi_days`：有效格点的简单算术平均。

### 步骤 6：执行论文的 80% 时间覆盖筛选

论文未完全说明“80% 有效覆盖率”的分母。最可复现的基准解释是：

\[
time\_coverage_i=\frac{\#\{t\in[1951,2018]:WSDI_{i,t}\text{ 可计算}\}}{68}
\]

保留 `time_coverage >= 0.80` 的国家。随后将结果与论文报告的中间目标比较：约 160 个国家、1951—2018 年共 10,737 个国家—年份观测。

若数量不一致，按以下顺序排查：

1. 边界版本和争议地区代码是否与论文不同；
2. 作者是否把“80%”定义成国境内格点覆盖率而不是时间覆盖率；
3. 空间谓词是 `within`、`covers` 还是格网相交；
4. 小国是否使用了最近格点；
5. 作者使用的数据是否是论文所称的早期 HadEX3 发布版本。

不要为了凑到 160 和 10,737 而静默修改规则；每次替代口径都应作为独立方案输出并标记。

### 步骤 7：筛选 61 个主权国家和 1995—2018 主键

读取 `invest_panel_weo.csv` 的 `country_name`、`iso3` 和 `year`，并强制验证：

- 源文件恰好 1,827 行、63 个 ISO3；
- 删除 `HKG` 和 `TWN` 后保留 61 个 ISO3；
- 筛选主权国家及 1995—2018 年后恰好 1,464 行；
- 筛选后的年份连续覆盖 1995—2018，共 24 年；
- `iso3 + year` 无缺失、无重复；
- 每个 ISO3 只对应一个国家名称。

最终保留的 61 个 ISO3 为：

```python
SOVEREIGN_ISO3 = [
    "AUS", "AUT", "BEL", "BGD", "BRA", "CAN", "CHE", "CHL", "CHN", "CIV",
    "COL", "CZE", "DEU", "DNK", "EGY", "ESP", "FIN", "FRA", "GBR", "GRC",
    "HRV", "HUN", "IDN", "IND", "IRL", "ISL", "ISR", "ITA", "JPN",
    "KAZ", "KEN", "KOR", "LKA", "LTU", "MAR", "MEX", "MUS", "MYS", "NAM",
    "NGA", "NLD", "NOR", "NZL", "PAK", "PHL", "POL", "PRT", "ROU", "RUS",
    "SGP", "SRB", "SVK", "SVN", "SWE", "THA", "TUR", "UGA", "USA",
    "VNM", "ZAF", "ZMB"
]
```

这段清单仅用于人工审计；代码应从 CSV 动态读取、删除 `HKG` 和 `TWN`，再筛选 1995—2018 年。目标面板共有 `61 × 24 = 1,464` 个主键。

将国家年度 WSDI 左连接到这 1,464 个主键。现有文件下：

- 1995—2018 年共有 `61 × 24 = 1,464` 个目标主键；
- 61 个目标国家均能匹配世界银行边界，但 WSDI 可用性仍会受小国无格点和 HadEX3 覆盖筛选影响。

### 步骤 8：输出标准化结果

推荐字段：

| 字段 | 含义 |
|---|---|
| `iso3` | ISO 3166-1 alpha-3 国家代码 |
| `country_name` | 世界银行边界中的国家名 |
| `year` | 年份 |
| `wsdi_days` | 国家年度 WSDI 算术平均，单位为天 |
| `n_valid_cells` | 有效格点数 |
| `n_total_cells` | 国境内格点中心总数 |
| `grid_coverage_rate` | 年度空间覆盖率 |
| `n_valid_years_1951_2018` | 1951—2018 有效年份数 |
| `time_coverage_rate` | 68 年中的有效时间覆盖率 |
| `wsdi_source_dataset` | 固定为 `HadEX3` |
| `wsdi_source_version` | 固定为 `3.0.4` |
| `base_period` | 固定为 `1961-1990` |
| `aggregation` | 固定为 `grid_center_arithmetic_mean` |
| `wsdi_source_status` | `available` 或 `missing_in_source_or_coverage_filter` |

目标输出固定为 1,464 行，主键满足 `iso3 + year` 唯一。`country_name` 以 `invest_panel_weo.csv` 为准，边界文件名称仅保留作空间审计字段。

## 6. 1995—2018 目标输出的 Python 骨架

以下代码展示如何从 `invest_panel_weo.csv` 读取国家清单、删除 `HKG` 和 `TWN`、筛选 1995—2018 年，并生成 1,464 行目标文件。正式脚本还应增加日志、参数解析、文件哈希和 QA 输出。

```python
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
NC = ROOT / "data/raw/HadEX3-0-4_wsdi_ann_1961-1990.nc"
GPKG = ROOT / "data/raw/World Bank Official Boundaries - Admin 0.gpkg"
PANEL = ROOT / "data/raw/invest_panel_weo.csv"
OUT = ROOT / "data/processed"
LOG = ROOT / "logs"
OUT.mkdir(parents=True, exist_ok=True)
LOG.mkdir(parents=True, exist_ok=True)

# 1. 目标面板主键
panel_keys = pd.read_csv(
    PANEL, usecols=["country_name", "iso3", "year"]
)
assert len(panel_keys) == 1827
assert panel_keys["iso3"].nunique() == 63
assert set(panel_keys["year"]) == set(range(1995, 2024))
assert not panel_keys[["country_name", "iso3", "year"]].isna().any().any()
assert not panel_keys.duplicated(["iso3", "year"]).any()
assert panel_keys.groupby("iso3")["country_name"].nunique().eq(1).all()
excluded_non_sovereign = {"HKG", "TWN"}
excluded_rows = panel_keys[panel_keys["iso3"].isin(excluded_non_sovereign)].copy()
assert set(excluded_rows["iso3"]) == excluded_non_sovereign
excluded_rows.to_csv(LOG / "excluded_non_sovereign.csv", index=False)
panel_keys = panel_keys[
    panel_keys["year"].between(1995, 2018)
    & ~panel_keys["iso3"].isin(excluded_non_sovereign)
].copy()
assert len(panel_keys) == 1464
assert panel_keys["iso3"].nunique() == 61
assert set(panel_keys["year"]) == set(range(1995, 2019))

# 2. NetCDF
ds = xr.open_dataset(NC, decode_times=True, mask_and_scale=True)
assert ds.attrs["dataset_version"] == "3.0.4"
assert ds.attrs["base_period"] == "1961-1990"
assert ds["WSDI"].attrs["units"] == "days"
source_end_year = int(pd.DatetimeIndex(ds["time"].values).year.max())
assert source_end_year == 2018

wsdi = ds["WSDI"].sel(time=slice("1951-01-01", "2018-12-31"))
wsdi = wsdi.where(wsdi != -99.9)
wsdi = wsdi.assign_coords(
    longitude=((wsdi.longitude + 180) % 360) - 180
).sortby("longitude")
assert wsdi.sizes["time"] == 68

# 3. 边界：同时清理列名和值中的 BOM
adm0 = gpd.read_file(GPKG, layer="WB_GAD_ADM0")
adm0.columns = [c.replace("\ufeff", "").strip() for c in adm0.columns]
for col in adm0.select_dtypes(include="object").columns:
    adm0[col] = (
        adm0[col].str.replace("\ufeff", "", regex=False).str.strip()
    )
adm0 = adm0.to_crs(4326)
adm0["geometry"] = adm0.geometry.make_valid()
adm0 = adm0[adm0["ISO_A3"].str.fullmatch(r"[A-Z]{3}", na=False)].copy()
countries = (
    adm0[["ISO_A3", "NAM_0", "geometry"]]
    .dissolve(by="ISO_A3", aggfunc="first")
    .reset_index()
)
unmatched_target = sorted(set(panel_keys["iso3"]) - set(countries["ISO_A3"]))
assert unmatched_target == []

# 4. 静态格点—国家映射
grid = pd.MultiIndex.from_product(
    [wsdi.latitude.values, wsdi.longitude.values],
    names=["latitude", "longitude"],
).to_frame(index=False)
points = gpd.GeoDataFrame(
    grid,
    geometry=gpd.points_from_xy(grid.longitude, grid.latitude),
    crs=4326,
)
membership = gpd.sjoin(
    points,
    countries[["ISO_A3", "NAM_0", "geometry"]],
    how="inner",
    predicate="within",
).drop(columns="index_right")

conflict = (
    membership.groupby(["latitude", "longitude"])["ISO_A3"]
    .nunique()
    .gt(1)
)
if conflict.any():
    raise ValueError("存在同时归属于多个国家的格点，请先输出并核查冲突。")

n_total = membership.groupby("ISO_A3").size().rename("n_total_cells")

# 5. 年度格点长表与国家均值
long = (
    wsdi.transpose("time", "latitude", "longitude")
    .to_dataframe(name="wsdi_days")
    .reset_index()
)
long["year"] = pd.DatetimeIndex(long["time"]).year
long = long.merge(
    membership[["latitude", "longitude", "ISO_A3", "NAM_0"]],
    on=["latitude", "longitude"],
    how="inner",
    validate="many_to_one",
)

country_year = (
    long.dropna(subset=["wsdi_days"])
    .groupby(["ISO_A3", "NAM_0", "year"], as_index=False)
    .agg(
        wsdi_days=("wsdi_days", "mean"),
        n_valid_cells=("wsdi_days", "size"),
    )
    .merge(n_total, on="ISO_A3", validate="many_to_one")
)
country_year["grid_coverage_rate"] = (
    country_year["n_valid_cells"] / country_year["n_total_cells"]
)

# 6. 80% 时间覆盖筛选
coverage = (
    country_year.groupby("ISO_A3")["year"]
    .nunique()
    .rename("n_valid_years_1951_2018")
    .to_frame()
)
coverage["time_coverage_rate"] = coverage["n_valid_years_1951_2018"] / 68
country_year = country_year.merge(coverage, on="ISO_A3", validate="many_to_one")
country_year = country_year[country_year["time_coverage_rate"] >= 0.80].copy()

country_year = country_year.rename(
    columns={"ISO_A3": "iso3", "NAM_0": "boundary_name"}
)
country_year["wsdi_source_dataset"] = "HadEX3"
country_year["wsdi_source_version"] = "3.0.4"
country_year["base_period"] = "1961-1990"
country_year["aggregation"] = "grid_center_arithmetic_mean"

assert not country_year.duplicated(["iso3", "year"]).any()
assert country_year["wsdi_days"].ge(0).all()

country_year.to_parquet(
    OUT / "wsdi_country_year_1951_2018.parquet", index=False
)

# 7. 左连接到 61 个主权国家 × 1995—2018 年目标主键
target = panel_keys.merge(
    country_year,
    on=["iso3", "year"],
    how="left",
    validate="one_to_one",
)
target["wsdi_source_status"] = np.where(
    target["wsdi_days"].notna(),
    "available",
    "missing_in_source_or_coverage_filter",
)

assert len(target) == 1464
assert not target.duplicated(["iso3", "year"]).any()
target.to_csv(
    OUT / "wsdi_sovereign61_1995_2018.csv",
    index=False,
    encoding="utf-8-sig",
)
```

## 7. 质量检查与验收标准

### 7.1 数据结构检查

- NetCDF 时间数为 118，1951—2018 子样本为 68，1995—2018 子样本为 24。
- `invest_panel_weo.csv` 源文件为 1,827 行、63 个 ISO3、29 个年份；删除 `HKG`、`TWN` 并筛选 1995—2018 后为 1,464 行、61 国、24 个年份。
- `invest_panel_weo.csv` 的 `iso3 + year` 无缺失和重复，每个 ISO3 只对应一个 `country_name`。
- 转换后经度范围为 `[−180, 180)`，且无重复。
- 边界 CRS 为 EPSG:4326。
- 清洗后的列名和值中不再包含 `\ufeff`。
- dissolve 后每个 `ISO_A3` 只有一条国家几何。
- 目标国家与边界匹配结果为 61/61，无未匹配代码。
- 最终目标键输出为 1,464 行且 `iso3 + year` 唯一。

### 7.2 数值检查

- `wsdi_days >= 0`。
- 不用整数规则校验 WSDI；该格点产品的有效值可为小数。
- 原始文件有效值最大约为 188.7829 天，可作为读取是否正确的快速检查。
- `0 < n_valid_cells <= n_total_cells`。
- `0 < grid_coverage_rate <= 1`。
- 所有保留国家满足 `time_coverage_rate >= 0.8`。

### 7.3 空间检查

- 随机抽查中国、澳大利亚、西班牙、英国、俄罗斯等大国的格点分布。
- 单独检查跨越 180° 经线的国家和岛屿，确认经度转换后未错配。
- 输出无格点国家清单、空间冲突清单和每国格点数排名。
- 对 `n_total_cells` 极小的国家作标记，因为其国家均值对单一格点更敏感。

### 7.4 与论文结果对照

论文结果只作为 1995—2018 重叠期的方法核对，不再决定本项目国家清单。核对目标分两层：

1. 气候面板：1951—2018 年约 160 国、10,737 个国家—年份观测。
2. 合并后的最终实证面板：49 国、1995—2018 年、757 个观测；其中 WSDI 均值 16.78、标准差 10.33、最小值 0、最大值 47.55。

第二组统计量只能在重建论文原 49 国样本时验证。当前 61 个主权国家目标面板不应被强行调整到均值 16.78 或 757 条观测。

### 7.5 目标面板覆盖检查

按 `wsdi_source_status` 输出行数和占比，并至少满足：

- 总行数为 1,464；
- `iso3` 中不包含 `HKG` 和 `TWN`；
- 61 个 ISO3 全部匹配边界；
- 其余缺失单独标记为 `missing_in_source_or_coverage_filter`，并按国家和年份列出原因。

### 7.6 HadEX3 时间覆盖检查

按年份输出全球有效格点数和各国 `grid_coverage_rate`。特别标记 2018 年覆盖下降，并至少执行以下稳健性比较：

- 基准结果：保留 2018 年，与论文一致。
- 稳健性 A：仅保留年度格点覆盖率达到预设阈值的国家—年份。
- 稳健性 B：将实证期截止到 2017 年，比较回归方向和显著性是否稳定。

阈值应预先设定并报告，不能看到结果后调整。

## 8. 基准法与稳健性方案的边界

| 方案 | 聚合方法 | 是否匹配论文主口径 | 用途 |
|---|---|---:|---|
| A | 国境内有效格点中心简单平均 | 是 | 主结果 |
| B | 按 `cos(latitude)` 近似面积加权 | 否 | 检查高纬地区被等权格点放大的影响 |
| C | 按格网与国界相交面积加权 | 否 | 更严格的面积暴露稳健性 |
| D | 按人口栅格加权 | 否 | 衡量人口实际暴露，不用于复现论文主变量 |

论文主结果必须使用方案 A。B—D 应另起变量名，例如 `wsdi_area_weighted`、`wsdi_population_weighted`，不能覆盖 `wsdi_days`。

## 9. 关键风险与解释限制

- **边界版本风险：** 当前世界银行边界文件的更新时间晚于论文数据期，争议地区和领土归属可能与作者版本不同，因此完全相同的 160 国和 10,737 条观测不一定能够仅凭论文描述复原。
- **主权口径风险：** 本项目以联合国会员国作为操作标准，因此排除 `HKG` 和 `TWN`。如果后续研究采用不同的国家承认或经济体口径，必须另建样本版本，不能覆盖当前主权国家结果。
- **80% 规则歧义：** 论文没有说明是时间覆盖、空间格点覆盖还是原始站点覆盖。基准文档采用时间覆盖解释，并要求用论文中间数量做反推验证。
- **等权格点偏差：** 经纬网格在高纬度的实际面积更小，简单平均会使每个高纬格点获得与低纬格点相同的权重。这符合论文文字口径，但不等同于国土面积平均。
- **小国缺格点：** 1.875° × 1.25° 网格较粗，一些小国可能没有格点中心。最近邻替代会改变指标含义，不应在基准结果中使用。
- **非因果指标：** 国家年度 WSDI 是极端高温暴露指标，不是灾害损失、人口暴露或因果效应本身。

## 10. 完成定义

只有同时满足以下条件，才算完成 WSDI 构建：

- 原始文件及哈希已记录；
- NetCDF 元数据断言全部通过；
- BOM、经度、CRS、重复 ISO3 和几何问题均已显式处理；
- 格点—国家映射、覆盖率和冲突日志已保存；
- 国家年度 WSDI、有效格点数和覆盖率已输出；
- 80% 规则及其歧义已记录；
- `invest_panel_weo.csv` 已删除 `HKG` 和 `TWN`，筛选为 61 个主权国家 × 1995—2018 年，共 1,464 个目标主键；
- 1995—2018 年 HadEX3 数据已合并，并对每条缺失记录给出状态；
- 排除清单及其联合国会员国操作标准已记录，61 个目标国家均已匹配边界；
- 与论文的 1995—2018 气候面板规模和描述统计完成分层核对，但未用论文 49 国清单覆盖当前 61 国清单；
- 任何与论文数量不一致之处均有可追溯解释，而非通过删改样本静默修正。
