# CurrentGDP NGDPD 与 Reserves 美元口径设计

## 目标

将 `data0804/invest_panel_weo.csv` 的 `CurrentGDP` 来源从 WEO `NGDP` 改为
`NGDPD`。`NGDPD` 的单位是十亿美元。同步重算：

```text
reserves = FI.RES.TOTL.CD / 1e9 / NGDPD * 100
```

其中 `FI.RES.TOTL.CD` 来自
`data0804/API_FI.RES.TOTL.CD_DS2_en_csv_v2_14.csv`。

## 数据流与更新边界

WEO 由现有 `read_weo_values()` 读取，以 `COUNTRY.ID + year + INDICATOR.ID`
为键；`WEO_FIELDS` 将 `NGDPD` 映射到 `CurrentGDP`。WDI 宽表跳过元数据行，验证
唯一 `Country Code + Indicator Code`，再读取 1995--2023 年值，以
`Country Code + year` 为键。

新增一个原子刷新函数，同时读取 NGDPD 和 WDI 储备后更新当前 CSV 的
`CurrentGDP` 与 `reserves`。完整 `write_merged_csv()` 路径复用相同的 reserves
公式，防止手工刷新和未来全量重建产生两套口径。

## 缺失和单位规则

- `CurrentGDP` 按目标面板覆盖 1,825/1,827 行，缺失为 SRB 1995--1996；
- `reserves` 只有在 NGDPD 与 WDI 储备均存在且 NGDPD 严格为正时计算，覆盖
  1,757/1,827 行；
- reserves 缺失 70 行，涉及 CIV、HKG、SRB、TWN，保持空值，不补零、不插值；
- `CurrentGDP` 单位更新为十亿美元，`reserves` 是储备占现价美元 GDP 的百分比；
- 除 `CurrentGDP` 和 `reserves` 外，目标行数、行序、键和其他 26 列逐值不变。

## 精度、失败条件与验证

使用 `Decimal` 读取 WDI 与计算 reserves，输出为无科学计数法的规范小数字符串。
遇到重复 WDI ISO3、错误指标、非数值储备或非正 NGDPD 时停止，不静默覆盖。

合同测试独立读取 WEO/WDI，并逐行验证 CurrentGDP 与 reserves 的源映射、公式和
缺失位置；临时文件测试原子刷新行为和非正分母失败。最终运行全部测试、Paper B
整合 QA 与 `git diff --check`。
