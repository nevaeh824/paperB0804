# WSDI Workflow 文档设计规格

## 1. 文档目标

编写一份可独立阅读、可复现、可用于实证研究交接与审计的中文 Workflow 文档，解释 WSDI 国家—年份指标从原始数据到最终面板的完整构建过程，并逐项解释所有正式输出、中间结果、日志及 QA 指标。

正式文档文件名：`WSDI指标构建Workflow与字段解读.md`。

## 2. 目标读者

- 需要复现 WSDI 指标构建的研究人员；
- 需要将 WSDI 合并进 `invest_panel_weo.csv` 的实证分析人员；
- 需要核查空间匹配、时间覆盖和缺失原因的审稿或数据质量检查人员。

## 3. 内容组织方案

采用用户确认的方案 1：按照指标构建顺序组织正文，在每个步骤后解释该步骤产生的指标，文末提供按文件整理的完整字段速查表。

正文包含以下模块：

1. 研究目标、样本范围与指标口径；
2. WSDI 的气候学定义、计算公式、单位和正确解读；
3. 输入文件、版本、时间范围和边界图层；
4. 环境配置与一键复现命令；
5. 从 NetCDF 到国家—年份面板的端到端数据流；
6. 各构建步骤的输入、处理规则、输出字段和质量检查；
7. 80% 时间覆盖筛选和目标主键左连接逻辑；
8. 最终结果规模、可用值和缺失原因统计；
9. 完整字段字典；
10. 实证合并、缺失处理和解释限制；
11. 验收清单与故障排查入口。

## 4. 指标解释范围

### 4.1 最终面板

覆盖 `data/processed/wsdi_sovereign61_1995_2018.csv` 的全部 17 个字段：

- `country_name`
- `iso3`
- `year`
- `boundary_name`
- `wsdi_days`
- `n_valid_cells`
- `n_total_cells`
- `grid_coverage_rate`
- `wsdi_source_dataset`
- `wsdi_source_version`
- `base_period`
- `aggregation`
- `n_valid_years_1951_2018`
- `time_coverage_rate`
- `passes_time_coverage`
- `wsdi_source_status`
- `wsdi_missing_reason`

每个字段至少说明：数据类型、单位或取值、生成方法、研究含义、缺失条件和使用注意事项。

### 4.2 中间国家年度数据

覆盖 `data/processed/wsdi_country_year_1951_2018.parquet` 的全部 14 个字段，并说明其与最终面板字段的关系、覆盖国家范围以及为何保留 1951—2018 年完整气候时段。

### 4.3 日志与 QA

覆盖以下文件的所有字段或 JSON 节点：

- `logs/country_grid_membership.csv`
- `logs/country_coverage.csv`
- `logs/spatial_join_conflicts.csv`
- `logs/countries_without_grid.csv`
- `logs/excluded_non_sovereign.csv`
- `logs/input_hashes.csv`
- `logs/qa_summary.json`

对 `qa_summary.json` 按 `parameters`、`source`、`spatial`、`coverage`、`target`、`outputs` 六组解释，另行解释构建时间字段。

## 5. 关键公式与状态规则

文档必须明确给出：

- 国家年度 WSDI：当年属于暖持续事件的日数在该国有效格点上的算术平均；
- `grid_coverage_rate = n_valid_cells / n_total_cells`；
- `time_coverage_rate = n_valid_years_1951_2018 / 68`；
- `passes_time_coverage = time_coverage_rate >= 0.80`；
- 目标面板规模：61 个主权国家乘 24 年，共 1,464 行；
- `wsdi_source_status` 和 `wsdi_missing_reason` 的生成逻辑；
- `failed_time_coverage`、`no_grid_center`、`missing_annual_value` 的含义及优先判断顺序。

同时明确：`wsdi_days` 可以是小数，因为它是格点值的国家算术平均；缺失值不能解释为零天。

## 6. 当前构建结果

正式文档采用实际产物中的统计，而不是示意数字：

- 最终面板：1,464 行、61 个 ISO3、24 年；
- `available`：1,233 行；
- 缺失：231 行；
- `failed_time_coverage`：168 行；
- `no_grid_center`：48 行；
- `missing_annual_value`：15 行；
- 目标国家边界匹配：61/61；
- 空间冲突格点：0。

## 7. 数据流表达

使用一个紧凑的 Mermaid 流程图表示：输入文件 → 数据校验 → 经度统一 → 国界清洗 → 格点—国家映射 → 国家年度聚合 → 时间覆盖筛选 → 主权国家与年份筛选 → 最终输出与 QA。

除该流程图外，以表格承担字段字典、状态规则和产物清单，避免不必要的视觉元素。

## 8. 实证使用边界

文档应说明：

- 使用 `iso3 + year` 作为合并主键；
- 回归主指标为 `wsdi_days`；
- `grid_coverage_rate` 和 `time_coverage_rate` 是数据质量指标，不是替代性的气候冲击变量；
- 不对缺失 WSDI 做零值填充；
- WSDI 表示暖持续事件日数，不是事件次数、温度异常幅度、人口暴露或经济损失；
- 当前国家聚合为格点中心落入国界后的非面积加权算术平均。

## 9. 可复现性要求

文档引用现有文件与脚本，不重新实现算法。至少提供：

- Conda 环境激活命令；
- 正式构建命令；
- 自动化测试命令；
- 关键输出文件位置；
- 输入文件哈希日志的用途。

## 10. 验收标准

- 文档中的字段名与实际 CSV、Parquet、日志和 JSON 完全一致；
- 所有 17 个最终字段、14 个中间字段和全部日志字段/QA 节点均有解释；
- 公式、样本期、国家数、年份数和行数与实际产物一致；
- 状态和缺失原因的判断逻辑与构建脚本一致；
- 所有本地路径存在，复现命令可从项目根目录执行；
- 文档明确区分核心气候指标、覆盖率指标、来源元数据和审计指标；
- 文档不把国家格点均值误述为人口加权或面积加权结果。
