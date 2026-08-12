# invest_panel_weo ND-GAIN Delta 列设计

## 目标

在 `data0804/invest_panel_weo.csv` 增加：

- `vulnerability_delta100`，来源于
  `ndgain_countryindex_2026/resources/vulnerability/vulnerability_delta.csv`；
- `readiness_delta100`，来源于
  `ndgain_countryindex_2026/resources/readiness/readiness_delta.csv`。

每个非缺失源值精确乘以 100 后写入目标列。

## 合并与列序

两个来源均为宽表，以 `ISO3` 为行、1995--2023 为年度列。读取时转换为
`(ISO3, year) -> value` 映射，再按目标面板的 `iso3 + year` 唯一键执行严格左连接。
新列分别紧跟 `vulnerability100` 和 `readiness100`，便于识别水平量和 delta 量。

目标面板共 1,827 行、63 个国家/地区。来源不含 HKG 与 TWN，因此两列在这两个
ISO3 的 58 个国家年度行留空；不得补零、插值或删除目标行。其余 1,769 行应有值。

## 可复现性与安全约束

在 `build_invest_panel_weo.py` 中增加通用 ND-GAIN delta 读取和合并函数，并让完整数据
构建流程使用它。使用 `Decimal` 做 `×100` 与字符串格式化，避免二进制浮点尾差。
构建器必须拒绝重复 ISO3、缺少年份列和目标面板重复键。

除了新增两列之外，当前 `invest_panel_weo.csv` 的行数、行序、键和既有字段值保持
不变。由于更上游基础面板当前不在工作区，现有目标 CSV 通过原子式列刷新函数直接
更新；未来基础面板可用时，完整构建路径也会生成相同两列。

## 验证

合同测试逐行把目标值与独立读取的源值乘 100 比较，检查 1,769/58 的覆盖、列位置、
键唯一性和既有字段保持。测试还用临时小面板覆盖写入行为及重复源 ISO3 的失败路径。
