# WSDI 国家—年份指标构建设计

## 1. 目标

依据 `WSDI指标构建步骤.md`，把 HadEX3 3.0.4 年度格点 WSDI 聚合为国家—年份指标，并生成与 `invest_panel_weo.csv` 对齐的 1995—2018 年实证面板。

最终样本以联合国会员国为操作口径，从源面板的 63 个国家或经济体中排除 `HKG` 和 `TWN`，保留 61 个国家、24 个年份和 1,464 个唯一 `iso3 + year` 主键。

## 2. 已确认的数据事实

- HadEX3 文件版本为 3.0.4，基准期为 1961—1990，时间覆盖 1901—2018，变量为 `WSDI`，单位为天。
- 世界银行边界图层为 `WB_GAD_ADM0`，共有 251 条记录；字段名和部分文本值含 BOM，需要清洗。
- 边界按有效 `ISO_A3` dissolve 后有 245 个代码。
- HadEX3 网格共有 27,648 个格点中心；使用 `within` 与清洗后的国家边界连接时不存在多国归属冲突。
- 61 个目标国家均有边界，但 `MUS` 和 `SGP` 没有落在国境内的 HadEX3 格点中心。
- `MUS` 和 `SGP` 的目标主键必须保留并标记缺失，不使用最近邻格点替代。

## 3. 方案与组件

采用模块化 Python 脚本和标准库 `unittest`，而不是把正式流水线放在 Notebook 中。

### 3.1 正式脚本

创建 `scripts/build_wsdi_country.py`，包含以下职责边界：

- `compute_sha256(path)`：计算输入文件指纹。
- `load_panel_keys(path, start_year, end_year, excluded_iso3)`：验证源面板结构、记录排除项并返回 61 国目标主键。
- `load_wsdi(path, climate_start_year, climate_end_year)`：验证 HadEX3 元数据、解码缺失值、选择 1951—2018 并转换经度。
- `load_boundaries(path, layer)`：清理 BOM、统一 CRS、修复几何、过滤 ISO3 并 dissolve。
- `build_grid_membership(wsdi, countries)`：建立静态格点中心—国家映射并检测多国冲突。
- `aggregate_country_year(wsdi, membership)`：对有效格点做国家年度简单平均，同时计算有效格点数和空间覆盖率。
- `apply_time_coverage_filter(country_year, total_years, threshold)`：计算 1951—2018 时间覆盖率并保留不低于 80% 的国家。
- `build_target_output(panel_keys, country_year, coverage, countries_without_grid)`：左连接 1,464 个目标主键并生成状态和缺失原因。
- `validate_outputs(...)`：执行最终主键、范围、连接覆盖和数值断言。
- `write_outputs(...)`：仅在全部校验通过后写入数据和日志。
- `main()`：解析路径和年份参数并编排整个流程。

脚本默认从项目根目录读取现有四个输入文件，不移动或改写原始文件。年份和覆盖率作为命令行参数提供，但默认值固定为文档口径：气候覆盖期 1951—2018、实证期 1995—2018、时间覆盖率阈值 0.80。

### 3.2 自动化测试

创建 `tests/test_build_wsdi_country.py`，使用小型内存数据验证：

- 面板排除规则、年份筛选和主键唯一性；
- 经度从 0—360 转为 −180—180 后唯一且递增；
- BOM 清洗与重复 ISO3 dissolve；
- 格点中心空间归属和冲突识别；
- 国家年度简单平均、有效格点数与空间覆盖率；
- 80% 时间覆盖率的边界条件；
- 左连接不丢失目标主键，且缺失原因分类正确；
- 最终输出排序和数据类型稳定。

测试必须先在正式模块不存在或函数未实现时产生预期失败，再编写最小实现使其通过。

## 4. 数据流

1. 读取源面板并验证 1,827 行、63 个 ISO3、1995—2023 年及唯一主键。
2. 保存 `HKG`、`TWN` 的排除记录，筛选出 61 国 × 1995—2018 的 1,464 个目标主键。
3. 读取 HadEX3，验证版本、基准期、变量、单位、时间和维度；选择 1951—2018 并转换经度。
4. 读取边界，清洗 BOM、修复几何、过滤合法 ISO3 并 dissolve。
5. 将 27,648 个格点中心与国家多边形做 `within` 空间连接，输出映射、冲突和无格点国家。
6. 将 WSDI 转为国家年度长表，对有效格点做算术平均，计算 `n_valid_cells`、`n_total_cells` 和 `grid_coverage_rate`。
7. 按 68 年中存在可计算国家年度值的年份比例计算 `time_coverage_rate`，保留比例不低于 0.80 的国家。
8. 输出保留后的 1951—2018 国家年度中间数据。
9. 将国家年度数据左连接到 1,464 个目标主键，保留所有目标行并生成状态字段。
10. 完成 QA 断言后输出最终 CSV 和 JSON/CSV 日志。

## 5. 输出契约

### 5.1 中间国家年度数据

`data/processed/wsdi_country_year_1951_2018.parquet` 至少包含：

- `iso3`
- `boundary_name`
- `year`
- `wsdi_days`
- `n_valid_cells`
- `n_total_cells`
- `grid_coverage_rate`
- `n_valid_years_1951_2018`
- `time_coverage_rate`
- `wsdi_source_dataset`
- `wsdi_source_version`
- `base_period`
- `aggregation`

### 5.2 最终目标面板

`data/processed/wsdi_sovereign61_1995_2018.csv` 固定为 1,464 行，按 `iso3, year` 排序，至少包含：

- `country_name`：来自 `invest_panel_weo.csv`
- `iso3`
- `year`
- 中间国家年度数据的全部指标与审计字段
- `wsdi_source_status`：`available` 或 `missing_in_source_or_coverage_filter`
- `wsdi_missing_reason`：可用时为空；缺失时为 `no_grid_center`、`failed_time_coverage` 或 `missing_annual_value`

### 5.3 日志

- `logs/country_grid_membership.csv`
- `logs/country_coverage.csv`
- `logs/spatial_join_conflicts.csv`
- `logs/countries_without_grid.csv`
- `logs/excluded_non_sovereign.csv`
- `logs/input_hashes.csv`
- `logs/qa_summary.json`

日志按稳定键排序并使用 UTF-8 with BOM 写出 CSV，便于 Excel 检查。

## 6. 错误处理

以下情况直接失败并给出明确错误，不静默修改口径：

- 输入文件缺失或 NetCDF 元数据不符合预期；
- 面板行数、国家数、年份范围、ISO3 格式或主键唯一性异常；
- 经度转换后重复或未严格递增；
- 边界 CRS、ISO3、几何或 dissolve 结果异常；
- 一个格点中心归属于多个国家；
- 国家年度结果出现重复主键、负 WSDI、无效覆盖率或错误年份；
- 最终面板不是 1,464 行、61 国、24 年或出现重复主键；
- 最终目标国家未匹配边界。

无格点国家和未通过 80% 时间覆盖率的国家属于可解释缺失，不作为运行失败，但必须写入日志并保留目标主键。

## 7. 验证与验收

构建完成后必须同时满足：

- 全部单元测试通过且无警告；
- 正式脚本退出码为 0；
- 目标面板为 1,464 行、61 个 ISO3、1995—2018 共 24 年；
- `iso3 + year` 无缺失、无重复；
- `HKG`、`TWN` 不在目标面板；
- 61/61 目标 ISO3 均匹配边界；
- `MUS`、`SGP` 被记录为 `no_grid_center`；
- 有效 `wsdi_days` 不小于 0；
- `0 < n_valid_cells <= n_total_cells`；
- `0 < grid_coverage_rate <= 1`；
- 保留的国家年度数据满足 `time_coverage_rate >= 0.80`；
- QA JSON 记录输入哈希、参数、源数据规模、空间连接数量、覆盖筛选数量、最终可用/缺失行数和输出路径；
- 独立读取最终 CSV 与 Parquet 后重新验证行数、主键、年份、范围和缺失原因。

## 8. 明确不包含的处理

- 不从逐日温度重新计算 WSDI。
- 不对格点做面积或人口加权。
- 不为无格点小国分配最近邻格点。
- 不为了匹配论文的 160 国、10,737 条或 49 国、757 条而调整当前样本。
- 不生成图表、仪表板或回归结果。
