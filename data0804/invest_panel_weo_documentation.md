# invest_panel_weo 数据说明与 Overview

## 1. 交付内容

- 数据文件：`data0804/invest_panel_weo.csv`
- 基础数据：`cleaned_imf_like_panel_1995_2023.csv`
- WEO 数据：`宏观indicators/WEOApr2026all.xlsx`（April 2026 WEO，`Countries` 工作表）
- 可复核代码：`data0804/build_invest_panel_weo.py`
- 质量核验 notebook：`data0804/invest_panel_weo_profile.ipynb`

输出包含 1,827 行、25 列、63 个国家/地区，年份为 1995–2023。以 `iso3 + year` 为唯一键，原面板行序和原字段数值均被保留；`OB_gdp` 仅重命名为 `PrimaryBalance_gdp`，随后在列末追加 `Revenue_gdp`、`CurrentGDP`、`ConstantGDP`、`OverallBalance_gdp`、`revenue`、`debt`、`interest_revenue`。

## 2. 单位和缩放规则

- WEO 百分比变量保留 Excel 中的原始百分数/百分比点表示。例如 WEO 的 `38.031` 仍写为 `38.031`，不转换为 `0.38031`，也不再乘以 100。
- 本次没有对任何从基础面板复制的数值做二次缩放。
- `vulnerability100` 与 `readiness100` 是基础面板中已有的 0–100 指数点，名字中的 `100` 不代表本次进行了缩放。
- `reserves` 也按基础面板既有数值原样复制；其历史构造本身包含 `*100`，本次没有再次缩放。
- `interest_revenue` 是百分数，按 `((PrimaryBalance_gdp - OverallBalance_gdp) / Revenue_gdp) * 100` 计算；数值 5 表示约 5%。

## 3. 变量定义、单位与来源

| 变量 | 含义 | 单位 | 来源 | 处理 |
|---|---|---|---|---|
| `country_name` | 国家/地区英文名 | 文本 | 基础面板；名称体系沿用原面板 | 原样复制 |
| `iso3` | ISO3 国家/地区代码 | 文本 | 基础面板；用于和 WEO `COUNTRY.ID` 合并 | 原样复制，合并键之一 |
| `year` | 年度 | 公历年 | 基础面板 1995–2023 年骨架 | 原样复制，合并键之一 |
| `bond_spreads` | 10 年期国债收益率相对美国的利差 | 百分点 | 基础面板；Investing.com 年均收益率及 `dataADD` 补充 | 原样复制；国别收益率减美国收益率 |
| `bond_10y` | 10 年期国债收益率年均值 | % | 基础面板；Investing.com 及 `dataADD` 补充 | 原样复制，不再缩放 |
| `vulnerability100` | ND-GAIN 气候脆弱性指数 | 0–100 指数点（非百分比） | 基础面板；`宏观indicators/vulnerability.csv` | 原样复制；原基础面板已将 0–1 指数乘以 100，本次不再缩放 |
| `readiness100` | ND-GAIN 气候准备度/韧性指数 | 0–100 指数点（非百分比） | 基础面板；`宏观indicators/readiness.csv` | 原样复制；原基础面板已将 0–1 指数乘以 100，本次不再缩放 |
| `lnrgdp` | 实际 GDP 水平的自然对数 | 自然对数；底层 `NGDP_R` 为十亿本币 | 基础面板；IMF WEO `NGDP_R` | 原样复制；`ln(NGDP_R)` |
| `growth` | 实际 GDP 年增长率 | % | 基础面板；IMF WEO `NGDP_RPCH` | 原样复制，不乘以 100 |
| `inflation_cpi` | 平均 CPI 年通胀率 | % | 基础面板；IMF WEO `PCPIPCH` | 原样复制，不乘以 100 |
| `debt_gdp` | 一般政府总债务占 GDP | % of GDP | 基础面板；IMF WEO `GGXWDG_NGDP` | 原样复制，不乘以 100 |
| `PrimaryBalance_gdp` | 一般政府基础净借贷/净借款占 GDP | % of GDP | 基础面板原 `OB_gdp`；IMF WEO `GGXONLB_NGDP` | 仅改名，数值原样复制；不乘以 100 |
| `reserves` | 含黄金国际储备的既有派生比率 | 基础面板既有比率 ×100 | 基础面板；WDI `FI.RES.TOTL.CD` 与 WEO `NGDP_R` | 原样复制；沿用既有公式 `FI.RES.TOTL.CD / 1e9 / NGDP_R * 100`，本次不再缩放 |
| `gee` | 政府有效性估计值 | WGI 估计值（约 -2.5 至 2.5） | 基础面板；WGI `GE.EST` | 原样复制 |
| `rqe` | 监管质量估计值 | WGI 估计值（约 -2.5 至 2.5） | 基础面板；WGI `RQ.EST` | 原样复制 |
| `tt` | 净易货贸易条件指数 | 指数，2015=100 | 基础面板；WDI `TT.PRI.MRCH.XD.WD` | 原样复制 |
| `is_advanced` | 发达经济体标识 | 0/1 | 基础面板；沿用 `原数据集/dataIMF.xlsx` 分类 | 原样复制 |
| `Revenue_gdp` | 一般政府收入占 GDP | % of GDP | `宏观indicators/WEOApr2026all.xlsx`，Countries 表，`GGR_NGDP` | 按 `iso3 + year` 左连接；WEO 原值，不乘以 100 |
| `CurrentGDP` | 现价 GDP（本币） | 十亿本币 | `宏观indicators/WEOApr2026all.xlsx`，Countries 表，`NGDP` | 按 `iso3 + year` 左连接；WEO 原值 |
| `ConstantGDP` | 固定价格 GDP（本币） | 十亿本币 | `宏观indicators/WEOApr2026all.xlsx`，Countries 表，`NGDP_R` | 按 `iso3 + year` 左连接；WEO 原值 |
| `OverallBalance_gdp` | 一般政府净借贷（+）/净借款（-）占 GDP | % of GDP | `宏观indicators/WEOApr2026all.xlsx`，Countries 表，`GGXCNL_NGDP` | 按 `iso3 + year` 左连接；WEO 原值，不乘以 100 |
| `revenue` | 一般政府收入（本币金额） | 十亿本币 | `宏观indicators/WEOApr2026all.xlsx`，Countries 表，`GGR` | 按 `iso3 + year` 左连接；WEO 原值 |
| `debt` | 一般政府总债务（本币金额） | 十亿本币 | `宏观indicators/WEOApr2026all.xlsx`，Countries 表，`GGXWDG` | 按 `iso3 + year` 左连接；WEO 原值 |
| `interest_revenue` | 利息支出占政府收入的百分比 | % | 由面板字段派生 | `((PrimaryBalance_gdp - OverallBalance_gdp) / Revenue_gdp) * 100`；任一输入缺失或分母为 0 时留空 |

## 4. WEO 合并覆盖

WEO 中六个目标指标各有 197 条唯一 country–indicator 行；其中 `NGDP_R` 在 1995–2023 至少有一个非缺失值的国家/地区为 196 个，其余目标系列为 197 个；基础面板的 63 个 ISO3 全部存在于 WEO。合并为严格的左连接，行数从 1,827 保持为 1,827，没有一对多扩张。

| 新增列 | WEO 代码 | 非缺失 | 覆盖率 | WEO 单位 | 缺失最多的年份（缺失行数） |
|---|---|---|---|---|---|
| `Revenue_gdp` | `GGR_NGDP` | 1,771 | 96.93% | Units / Percent | 1995: 13, 1996: 13, 1997: 11, 1998: 9, 1999: 8 |
| `CurrentGDP` | `NGDP` | 1,825 | 99.89% | Billions / Domestic currency | 1995: 1, 1996: 1 |
| `ConstantGDP` | `NGDP_R` | 1,825 | 99.89% | Billions / Domestic currency | 1995: 1, 1996: 1 |
| `OverallBalance_gdp` | `GGXCNL_NGDP` | 1,764 | 96.55% | Units / Percent | 1995: 14, 1996: 14, 1997: 12, 1998: 10, 1999: 9 |
| `revenue` | `GGR` | 1,771 | 96.93% | Billions / Domestic currency | 1995: 13, 1996: 13, 1997: 11, 1998: 9, 1999: 8 |
| `debt` | `GGXWDG` | 1,724 | 94.36% | Billions / Domestic currency | 1995: 25, 1996: 22, 1997: 18, 1998: 14, 1999: 14 |
| `interest_revenue` | 派生公式 | 1,686 | 92.28% | 百分数（%） | 1995: 19, 1996: 19, 1997: 17, 1998: 15, 1999: 14 |

## 5. 全字段覆盖率

| 变量 | 非缺失 | 缺失 | 覆盖率 |
|---|---|---|---|
| `country_name` | 1,827 | 0 | 100.00% |
| `iso3` | 1,827 | 0 | 100.00% |
| `year` | 1,827 | 0 | 100.00% |
| `bond_spreads` | 1,330 | 497 | 72.80% |
| `bond_10y` | 1,330 | 497 | 72.80% |
| `vulnerability100` | 1,769 | 58 | 96.83% |
| `readiness100` | 1,769 | 58 | 96.83% |
| `lnrgdp` | 1,825 | 2 | 99.89% |
| `growth` | 1,822 | 5 | 99.73% |
| `inflation_cpi` | 1,820 | 7 | 99.62% |
| `debt_gdp` | 1,724 | 103 | 94.36% |
| `PrimaryBalance_gdp` | 1,686 | 141 | 92.28% |
| `reserves` | 1,757 | 70 | 96.17% |
| `gee` | 1,575 | 252 | 86.21% |
| `rqe` | 1,575 | 252 | 86.21% |
| `tt` | 1,605 | 222 | 87.85% |
| `is_advanced` | 1,827 | 0 | 100.00% |
| `Revenue_gdp` | 1,771 | 56 | 96.93% |
| `CurrentGDP` | 1,825 | 2 | 99.89% |
| `ConstantGDP` | 1,825 | 2 | 99.89% |
| `OverallBalance_gdp` | 1,764 | 63 | 96.55% |
| `revenue` | 1,771 | 56 | 96.93% |
| `debt` | 1,724 | 103 | 94.36% |
| `interest_revenue` | 1,686 | 141 | 92.28% |
| `taxgdp` | 1,680 | 147 | 91.95% |

## 6. 数值变量描述统计

统计量按非缺失观察计算。`CurrentGDP`、`ConstantGDP`、`revenue` 和 `debt` 为不同本币单位的十亿本币，下面的跨国汇总仅用于数据概览，不应解释为可直接比较的经济规模。

| 变量 | N | 均值 | 标准差 | 最小值 | P25 | 中位数 | P75 | 最大值 |
|---|---|---|---|---|---|---|---|---|
| `year` | 1,827 | 2009 | 8.3689 | 1995 | 2002 | 2009 | 2016 | 2023 |
| `bond_spreads` | 1,330 | 2.2331 | 4.2845 | -3.4057 | -0.4655 | 0.6131 | 3.9521 | 34.3087 |
| `bond_10y` | 1,330 | 5.473 | 4.2634 | -0.5059 | 2.7273 | 4.5034 | 7.1284 | 35.2028 |
| `vulnerability100` | 1,769 | 38.254 | 7.9015 | 25.103 | 31.7121 | 36.7987 | 43.4822 | 58.08 |
| `readiness100` | 1,769 | 49.8685 | 14.5222 | 17.9342 | 36.8021 | 49.2806 | 61.9318 | 80.7202 |
| `lnrgdp` | 1,825 | 8.1897 | 2.735 | 2.9628 | 6.2834 | 7.8151 | 9.7386 | 16.3252 |
| `growth` | 1,822 | 3.3695 | 3.5291 | -14.547 | 1.7 | 3.446 | 5.3972 | 24.624 |
| `inflation_cpi` | 1,820 | 5.6068 | 10.7407 | -3.967 | 1.6105 | 3.1715 | 6.4725 | 197.3 |
| `debt_gdp` | 1,724 | 57.7393 | 34.8948 | 0.052 | 34.988 | 51.1745 | 72.246 | 260.964 |
| `PrimaryBalance_gdp` | 1,686 | -0.4817 | 3.424 | -29.952 | -2.334 | -0.52 | 1.4215 | 23.449 |
| `reserves` | 1,757 | 5.3066 | 12.6181 | 0.0001 | 0.1964 | 1.7024 | 5.5238 | 152.7072 |
| `gee` | 1,575 | 0.6614 | 0.9129 | -1.3496 | -0.1287 | 0.693 | 1.5183 | 2.4697 |
| `rqe` | 1,575 | 0.6587 | 0.8587 | -1.2928 | -0.1162 | 0.7561 | 1.4242 | 2.3086 |
| `tt` | 1,605 | 100.6902 | 18.5928 | 31.8761 | 93.8 | 99.421 | 104.6 | 273.0755 |
| `is_advanced` | 1,827 | 0.4921 | 0.5001 | 0 | 0 | 0 | 1 | 1 |
| `Revenue_gdp` | 1,771 | 31.323 | 12.9761 | 3.634 | 19.906 | 31.656 | 41.9295 | 60.918 |
| `CurrentGDP` | 1,825 | 227900.5442 | 1.37338e+06 | 3.29 | 425.691 | 1899.93 | 12849.794 | 2.08923e+07 |
| `ConstantGDP` | 1,825 | 215573.1384 | 1.04336e+06 | 19.352 | 535.592 | 2477.8 | 16958.941 | 1.23015e+07 |
| `OverallBalance_gdp` | 1,764 | -2.4991 | 3.9615 | -32.145 | -4.7047 | -2.5705 | -0.355 | 24.668 |
| `revenue` | 1,771 | 42271.8422 | 220774.6159 | 2.264 | 145.5275 | 667.323 | 2620.714 | 3.13287e+06 |
| `debt` | 1,724 | 98319.8456 | 519926.9212 | 1.5 | 266.133 | 1105.2175 | 5537.9767 | 8.27364e+06 |
| `interest_revenue` | 1,686 | 8.4628 | 9.5854 | -14.8211 | 2.7086 | 5.8686 | 11.2411 | 79.8698 |
| `taxgdp` | 1,680 | 20.7233 | 8.1057 | 2.1258 | 14.7139 | 20.0189 | 26.1268 | 49.7654 |

## 7. 数据质量结论

| 检查 | 结果 | 严重度 | 置信度 | 分析影响/建议 |
|---|---|---|---|---|
| 面板键唯一性 | `iso3 + year` 重复 0 行；整行重复 0 行 | 通过 | 高 | 不会因重复键造成面板或合并膨胀 |
| 面板完整性 | 63 个国家/地区 × 29 年 = 1,827 行；平衡面板=True | 通过 | 高 | 国家—年份骨架完整 |
| WEO 国家匹配 | 基础面板未匹配 WEO 的 ISO3：无 | 通过 | 高 | 全部 63 个国家/地区可在 WEO 六个目标系列中找到 |
| 新增变量缺失 | Revenue_gdp 缺失 56；CurrentGDP 缺失 2；ConstantGDP 缺失 2；OverallBalance_gdp 缺失 63；revenue 缺失 56；debt 缺失 103；interest_revenue 缺失 141 | 中 | 高 | 建模或均值比较需报告最终可用样本，并检查早期年份选择性缺失 |
| interest_revenue 公式 | 缺失位置一致=True；公式最大绝对误差=1.42e-14；Revenue_gdp 为 0 的行数=0 | 通过 | 高 | 该列单位为百分数；例如 5 表示利息支出约占收入 5% |
| 本币金额可比性 | CurrentGDP、ConstantGDP、revenue 和 debt 的单位均为十亿本币，各国币种不同 | 中 | 高 | 可做国别内时间变化；不可直接把跨国水平当作同一货币规模比较 |
| 既有 lnrgdp/reserves 口径 | lnrgdp 基于本币实际 GDP；reserves 继承美元储备除以本币实际 GDP 的既有公式 | 高（若作跨国水平解释） | 高 | 本次按要求原样复制；跨国解释前建议统一货币/价格口径并重新构造 |

总体判断：新文件的键、行数、列映射、WEO 合并和 `interest_revenue` 公式可靠；主要限制是财政系列在样本早期的缺失，以及本币金额/既有储备口径不适合直接做跨国水平比较。

## 8. 复现与假设

- 运行：`py -3.14 data0804/build_invest_panel_weo.py`
- WEO 合并键假设：基础面板 `iso3` 与 WEO `COUNTRY.ID` 使用相同 ISO3 体系。
- 新增变量只提取 1995–2023，与基础面板时间范围一致；不引入 WEO 2024–2031 的估计/预测年份。
- CSV 使用 UTF-8 编码，缺失值写为空字段。
