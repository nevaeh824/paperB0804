# Paper B：统计检验与数据检查

> 生成时间：2026-08-19 15:29（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。

## 1. Validation Report

### Overall Assessment: Share with caveats

单位换算检查通过 27/27 项；代数、映射与 hinge 检查通过 26/26 项；cutoff 最小 RSS 及继承关系检查通过 7/7 项。各回归已使用当前变量完整案例；第 2—3 节报告 LSDVC 的 50 次 bootstrap 标准误，第 4 节报告国家聚类标准误。theta 生成误差、cutoff 搜索和多判据选择不确定性尚未由联合推断覆盖。

### Methodology Review

主流程准确对应 workflow：第 2—3 节使用 Blundell–Bond 初始化的动态 LSDVC、`bias(2)` 和 50 次 bootstrap；第 4 节使用一期债务变化、去债务状态控制、A（1−Capacity）严格一阶差分且不加入滞后状态控制，并固定使用债务全控制 theta cutoff。每个回归按当前因变量、动态滞后项和右侧变量取完整案例；mA_hat 与 TA_hat 分别限制在其首选来源回归的实际样本内，theta 仅在两个来源样本共同覆盖且 b_pre 可用时构造。五种阈值判据使用各自的当前变量样本，因此其 RSS 与 Within R² 不作跨判据排名。

### Issues Found

1. **[Medium] 推断未覆盖 cutoff 搜索和上游生成误差。** 第 4 节 p 值使用国家聚类标准误，但条件于已估计的 theta 与已选择的 cutoff；上游 50 次方程内 bootstrap 也不是全流程联合 bootstrap。
2. **[Medium] 完整联合不确定性仍需管线 bootstrap。** 应按国家重抽样，并在每次重复中重估两条上游方程、theta 与 cutoff。
3. **[Low] 竞争判据使用不同完整案例样本。** 各行 RSS 只能解释为对应样本内拟合，不能直接据此给五个判据排序。

## 2. 数据来源、单位与时序

原始分析输入是 `data0804/invest_panel_weo.csv` 与 `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`。两者按唯一 `iso3 year` 键合并；`wsdi_days` 乘以 0.01 后定义 X。主面板源百分数、比率和 0—100 指数先除以 100；金额变量不缩放。`ln_constantgdp` 仅保留作正值与数据审计，不参与 T 构造，也不进入 Baseline 或其复核模型；`growth` 不进入 T 指标模型。Doomloop 从 empirical-theta panel 读取已换算变量，并单独将源 `interest_revenue` 除以 100。

- $T_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$，$T_{i,t+1}=F.T_{it}$；两者均严格要求相邻年份。
- 债务变化结果为 $\Delta debt_{i,t+1}=F.debt\_gdp_{it}-debt\_gdp_{it}$；理论债务状态统一使用 $b^{pre}_{it}=L.debt\_gdp_{it}$。
- $A_{it}=1-Capacity_{it}$；A 方程结果为 $A_{it}-A_{i,t-1}=adapt\_capacity_{it}-L.adapt\_capacity_{it}$，右侧不使用滞后状态项。

### 2.1 Doomloop 源字段换算

| 变量 | 源最小值 | 源最大值 | 比率最小值 | 比率最大值 | 最大误差 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| interest_revenue | -14.8211 | 79.8698 | -0.1482 | 0.7987 | 0 | 通过 |

## 3. 回归实际样本与描述统计

| 规格实际样本 | N | 国家数 | 年份数 | 年份范围 |
| --- | ---: | ---: | ---: | ---: |
| Baseline Layer2_A | 742 | 50 | 20 | 1999–2018 |
| T 指标全控制交互 | 1,024 | 52 | 23 | 1996–2018 |
| Doomloop 债务全控制 theta | 742 | 50 | 20 | 1999–2018 |
| Doomloop A（1−Capacity） | 742 | 50 | 20 | 1999–2018 |

### 3.1 Baseline 输入变量

| 变量 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bond_spreads | 1,330 | 0.0223 | 0.0428 | -0.0341 | 0.0061 | 0.3431 |
| growth | 1,822 | 0.0337 | 0.0353 | -0.1455 | 0.0345 | 0.2462 |
| inflation_cpi | 1,820 | 0.0561 | 0.1074 | -0.0397 | 0.0317 | 1.973 |
| reserves | 1,757 | 0.1664 | 0.188 | 0.0034 | 0.1134 | 1.4339 |
| tt | 1,605 | 1.0069 | 0.1859 | 0.3188 | 0.9942 | 2.7308 |
| wsdi_days | 1,233 | 0.1578 | 0.1026 | 0 | 0.1368 | 0.7334 |
| adapt_capacity | 1,769 | 0.5693 | 0.1587 | 0.2274 | 0.5955 | 0.8156 |
| spread_lag | 1,267 | 0.022 | 0.0421 | -0.0302 | 0.0062 | 0.3431 |
| b_pre | 1,661 | 0.573 | 0.3469 | 0.0005 | 0.5077 | 2.6096 |

### 3.2 Distribution of country or region samples — Layer2_A

| 国家/地区 | ISO3 | 观测数 | 样本占比 (%) | 起始年份 | 结束年份 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Australia | AUS | 19 | 2.56 | 2000 | 2018 |
| Austria | AUT | 19 | 2.56 | 2000 | 2018 |
| Bangladesh | BGD | 3 | 0.4 | 2016 | 2018 |
| Belgium | BEL | 19 | 2.56 | 2000 | 2018 |
| Brazil | BRA | 11 | 1.48 | 2008 | 2018 |
| Canada | CAN | 19 | 2.56 | 2000 | 2018 |
| Chile | CHL | 11 | 1.48 | 2008 | 2018 |
| China | CHN | 16 | 2.16 | 2003 | 2018 |
| Croatia | HRV | 10 | 1.35 | 2009 | 2018 |
| Czech Republic | CZE | 18 | 2.43 | 2001 | 2018 |
| Denmark | DNK | 19 | 2.56 | 2000 | 2018 |
| Egypt | EGY | 8 | 1.08 | 2011 | 2018 |
| Finland | FIN | 19 | 2.56 | 2000 | 2018 |
| France | FRA | 19 | 2.56 | 2000 | 2018 |
| Germany | DEU | 19 | 2.56 | 2000 | 2018 |
| Greece | GRC | 19 | 2.56 | 2000 | 2018 |
| Hungary | HUN | 15 | 2.02 | 2004 | 2018 |
| Iceland | ISL | 12 | 1.62 | 2007 | 2018 |
| India | IND | 20 | 2.7 | 1999 | 2018 |
| Indonesia | IDN | 8 | 1.08 | 2004 | 2011 |
| Ireland | IRL | 19 | 2.56 | 2000 | 2018 |
| Israel | ISR | 16 | 2.16 | 2003 | 2018 |
| Italy | ITA | 19 | 2.56 | 2000 | 2018 |
| Japan | JPN | 12 | 1.62 | 2007 | 2018 |
| Korea | KOR | 18 | 2.43 | 2001 | 2018 |
| Lithuania | LTU | 15 | 2.02 | 2004 | 2018 |
| Malaysia | MYS | 10 | 1.35 | 2002 | 2011 |
| Mexico | MEX | 12 | 1.62 | 2007 | 2018 |
| Morocco | MAR | 6 | 0.81 | 2013 | 2018 |
| Namibia | NAM | 4 | 0.54 | 2015 | 2018 |
| Netherlands | NLD | 19 | 2.56 | 2000 | 2018 |
| New Zealand | NZL | 18 | 2.43 | 2000 | 2017 |
| Norway | NOR | 19 | 2.56 | 2000 | 2018 |
| Pakistan | PAK | 9 | 1.21 | 2010 | 2018 |
| Philippines | PHL | 18 | 2.43 | 2001 | 2018 |
| Poland | POL | 18 | 2.43 | 2000 | 2018 |
| Portugal | PRT | 19 | 2.56 | 2000 | 2018 |
| Romania | ROU | 11 | 1.48 | 2008 | 2018 |
| Russia | RUS | 15 | 2.02 | 2004 | 2018 |
| Slovak Republic | SVK | 9 | 1.21 | 2008 | 2018 |
| Slovenia | SVN | 11 | 1.48 | 2008 | 2018 |
| South Africa | ZAF | 18 | 2.43 | 2001 | 2018 |
| Spain | ESP | 19 | 2.56 | 2000 | 2018 |
| Sweden | SWE | 19 | 2.56 | 2000 | 2018 |
| Switzerland | CHE | 14 | 1.89 | 2005 | 2018 |
| Thailand | THA | 17 | 2.29 | 2002 | 2018 |
| Turkey | TUR | 8 | 1.08 | 2011 | 2018 |
| United Kingdom | GBR | 19 | 2.56 | 2000 | 2018 |
| United States | USA | 17 | 2.29 | 2002 | 2018 |
| Vietnam | VNM | 11 | 1.48 | 2008 | 2018 |

### 3.3 T 指标与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T_lead | tax | 1,024 | 1.0318 | 0.0321 | 0.8549 | 1.0304 | 1.2462 |
| T_it | tax | 1,024 | 1.033 | 0.0325 | 0.8549 | 1.0319 | 1.2462 |
| mA_hat_spread_ratio | theta_support | 742 | -0.0234 | 0.0083 | -0.0562 | -0.0218 | -0.0087 |
| mA_hat | theta_support | 742 | -0.0234 | 0.0083 | -0.0562 | -0.0218 | -0.0087 |
| spread_saving_component | theta_support | 742 | -0.0167 | 0.0173 | -0.1142 | -0.0111 | -0.0004 |
| TA_hat | theta_support | 742 | 0.0115 | 0.0118 | -0.0077 | 0.0094 | 0.0749 |
| theta_hat_A | theta_support | 742 | -0.0052 | 0.0195 | -0.1137 | -0.0034 | 0.0553 |
| theta_hat_A | all_constructible | 742 | -0.0052 | 0.0195 | -0.1137 | -0.0034 | 0.0553 |

### 3.4 Doomloop 主规格与判据变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_no_b | debt | b_outcome | dependent_variable | 742 | 0.0093 | 0.0507 | -0.2736 | 0.0021 | 0.4186 |
| debt_no_b | debt | debt_kink_low | regressor | 742 | 0.0015 | 0.0074 | 0 | 0 | 0.0659 |
| debt_no_b | debt | debt_kink_high | regressor | 742 | 0.0135 | 0.0088 | 0 | 0.0133 | 0.0528 |
| debt_no_b | debt | wsdi_days | regressor | 742 | 0.1709 | 0.1051 | 0 | 0.1523 | 0.7334 |
| debt_no_b | debt | growth | regressor | 742 | 0.0281 | 0.0317 | -0.1451 | 0.0276 | 0.2462 |
| debt_no_b | debt | inflation_cpi | regressor | 742 | 0.0298 | 0.0294 | -0.0169 | 0.023 | 0.2353 |
| debt_no_b | debt | reserves | regressor | 742 | 0.1425 | 0.1344 | 0.0034 | 0.1086 | 1.1473 |
| debt_no_b | debt | tt | regressor | 742 | 0.9997 | 0.0976 | 0.6748 | 0.998 | 1.574 |
| debt_no_b | debt | adapt_capacity | construction_input | 742 | 0.6345 | 0.1262 | 0.2788 | 0.6742 | 0.8156 |
| debt_no_b | debt | theta_hat_A | construction_input | 742 | -0.0052 | 0.0195 | -0.1137 | -0.0034 | 0.0553 |
| debt_no_b | debt | b_pre | construction_input | 742 | 0.5967 | 0.3418 | 0.039 | 0.5128 | 2.0365 |
| debt_no_b | debt | mA_hat | construction_input | 742 | -0.0234 | 0.0083 | -0.0562 | -0.0218 | -0.0087 |
| debt_no_b | debt | TA_hat | construction_input | 742 | 0.0115 | 0.0118 | -0.0077 | 0.0094 | 0.0749 |
| debt_no_b | debt | b_pre_mA_hat | construction_input | 742 | -0.0167 | 0.0173 | -0.1142 | -0.0111 | -0.0004 |
| ready_no_lag_debt_cutoff | ready_debt | A_outcome | dependent_variable | 742 | 0.0022 | 0.0066 | -0.0507 | 0.0015 | 0.0602 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 742 | 0.0001 | 0.0005 | 0 | 0 | 0.0045 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 742 | 0.0012 | 0.0019 | -0.0021 | 0.0007 | 0.0183 |
| ready_no_lag_debt_cutoff | ready_debt | wsdi_days | regressor | 742 | 0.1709 | 0.1051 | 0 | 0.1523 | 0.7334 |
| ready_no_lag_debt_cutoff | ready_debt | growth | regressor | 742 | 0.0281 | 0.0317 | -0.1451 | 0.0276 | 0.2462 |
| ready_no_lag_debt_cutoff | ready_debt | inflation_cpi | regressor | 742 | 0.0298 | 0.0294 | -0.0169 | 0.023 | 0.2353 |
| ready_no_lag_debt_cutoff | ready_debt | reserves | regressor | 742 | 0.1425 | 0.1344 | 0.0034 | 0.1086 | 1.1473 |
| ready_no_lag_debt_cutoff | ready_debt | tt | regressor | 742 | 0.9997 | 0.0976 | 0.6748 | 0.998 | 1.574 |
| ready_no_lag_debt_cutoff | ready_debt | interest_revenue | construction_input | 742 | 0.0622 | 0.069 | -0.0624 | 0.0478 | 0.4362 |
| ready_no_lag_debt_cutoff | ready_debt | theta_hat_A | construction_input | 742 | -0.0052 | 0.0195 | -0.1137 | -0.0034 | 0.0553 |

## 4. 缺失、重复键与 Within 变异

三个估计阶段均对国家—年份键执行 fail-closed 唯一性检查；不会自动去重。Baseline 与 T 指标的每个动态回归均使用当前因变量、隐含滞后因变量与右侧变量的联合非缺失样本；Doomloop 债务和 A（1−Capacity）使用各自当前因变量与右侧变量的联合非缺失样本。mA_hat 仅在 Spread_Interact_all 的实际样本内生成，TA_hat 仅在 T10_interact_full 的实际样本内生成，theta 要求两个来源样本共同覆盖且 b_pre 可用；五种判据分别使用各自构造量与全控制变量的联合非缺失样本。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 (%) | 独占损失 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 497 | 27.2 | 1 |
| baseline | — | wsdi_days | 594 | 32.51 | 388 |
| baseline | — | adapt_capacity | 58 | 3.17 | 0 |
| baseline | — | b_pre | 166 | 9.09 | 11 |
| baseline | — | spread_lag | 560 | 30.65 | 30 |
| baseline | — | growth | 5 | 0.27 | 0 |
| baseline | — | inflation_cpi | 7 | 0.38 | 1 |
| baseline | — | reserves | 70 | 3.83 | 0 |
| baseline | — | tt | 222 | 12.15 | 69 |
| T | — | T_lead | 65 | 3.56 | 0 |
| T | — | adapt_capacity | 58 | 3.17 | 0 |
| T | — | wsdi_days | 594 | 32.51 | 437 |
| T | — | T_it | 65 | 3.56 | 17 |
| T | — | inflation_cpi | 7 | 0.38 | 1 |
| T | — | reserves | 70 | 3.83 | 0 |
| T | — | tt | 222 | 12.15 | 146 |
| doomloop | debt | b_outcome | 166 | 9.09 | 0 |
| doomloop | debt | adapt_capacity | 58 | 3.17 | 0 |
| doomloop | debt | theta_hat_A | 1,085 | 59.39 | 263 |
| doomloop | debt | wsdi_days | 594 | 32.51 | 0 |
| doomloop | debt | growth | 5 | 0.27 | 0 |
| doomloop | debt | inflation_cpi | 7 | 0.38 | 0 |
| doomloop | debt | reserves | 70 | 3.83 | 0 |
| doomloop | debt | tt | 222 | 12.15 | 0 |
| doomloop | ready | A_outcome | 119 | 6.51 | 0 |
| doomloop | ready | interest_revenue | 141 | 7.72 | 0 |
| doomloop | ready | theta_hat_A | 1,085 | 59.39 | 255 |
| doomloop | ready | wsdi_days | 594 | 32.51 | 0 |
| doomloop | ready | growth | 5 | 0.27 | 0 |
| doomloop | ready | inflation_cpi | 7 | 0.38 | 0 |
| doomloop | ready | reserves | 70 | 3.83 | 0 |
| doomloop | ready | tt | 222 | 12.15 | 0 |

### 4.2 Within 变异

| 板块 | 方程 | 变量 | 总体 SD | Within SD | Within/总体 | FE 识别 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 0.0428 | 0.0174 | 0.406 | adequate |
| baseline | — | growth | 0.0353 | 0.0317 | 0.8996 | adequate |
| baseline | — | inflation_cpi | 0.1074 | 0.0925 | 0.8612 | adequate |
| baseline | — | reserves | 0.188 | 0.091 | 0.4842 | adequate |
| baseline | — | tt | 0.1859 | 0.165 | 0.8875 | adequate |
| baseline | — | wsdi_days | 0.1026 | 0.0858 | 0.8364 | adequate |
| baseline | — | adapt_capacity | 0.1587 | 0.0265 | 0.167 | adequate |
| baseline | — | spread_lag | 0.0421 | 0.0174 | 0.4129 | adequate |
| baseline | — | b_pre | 0.3469 | 0.182 | 0.5246 | adequate |
| T | — | T_lead | 0.0321 | 0.0265 | 0.8256 | adequate |
| T | — | T_it | 0.0325 | 0.0271 | 0.8311 | adequate |
| T | — | adapt_capacity | 0.1447 | 0.0196 | 0.1351 | adequate |
| T | — | wsdi_days | 0.1059 | 0.0852 | 0.8047 | adequate |
| T | — | inflation_cpi | 0.0674 | 0.0515 | 0.7646 | adequate |
| T | — | reserves | 0.1223 | 0.0697 | 0.5702 | adequate |
| T | — | tt | 0.1816 | 0.1531 | 0.8431 | adequate |
| doomloop | debt | b_outcome | 0.0507 | 0.0484 | 0.9544 | adequate |
| doomloop | debt | theta_hat_A | 0.0195 | 0.0105 | 0.5382 | adequate |
| doomloop | debt | b_pre | 0.3418 | 0.1404 | 0.4107 | adequate |
| doomloop | debt | mA_hat | 0.0083 | 0.0036 | 0.4359 | adequate |
| doomloop | debt | TA_hat | 0.0118 | 0.0092 | 0.7788 | adequate |
| doomloop | debt | b_pre_mA_hat | 0.0173 | 0.0075 | 0.4342 | adequate |
| doomloop | debt | adapt_capacity | 0.1262 | 0.0143 | 0.1132 | adequate |
| doomloop | debt | wsdi_days | 0.1051 | 0.0819 | 0.7788 | adequate |
| doomloop | debt | growth | 0.0317 | 0.0257 | 0.8125 | adequate |
| doomloop | debt | inflation_cpi | 0.0294 | 0.0196 | 0.6668 | adequate |
| doomloop | debt | reserves | 0.1344 | 0.0642 | 0.4776 | adequate |
| doomloop | debt | tt | 0.0976 | 0.0823 | 0.8429 | adequate |
| doomloop | ready | A_outcome | 0.0066 | 0.0063 | 0.9523 | adequate |
| doomloop | ready | theta_hat_A | 0.0195 | 0.0105 | 0.5382 | adequate |
| doomloop | ready | interest_revenue | 0.069 | 0.0209 | 0.3034 | adequate |
| doomloop | ready | wsdi_days | 0.1051 | 0.0819 | 0.7788 | adequate |
| doomloop | ready | growth | 0.0317 | 0.0257 | 0.8125 | adequate |
| doomloop | ready | inflation_cpi | 0.0294 | 0.0196 | 0.6668 | adequate |
| doomloop | ready | reserves | 0.1344 | 0.0642 | 0.4776 | adequate |
| doomloop | ready | tt | 0.0976 | 0.0823 | 0.8429 | adequate |

## 5. 共线性、相关性与系数变化

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline | wsdi_days | 1.0128 | 0.9874 | 1.7728 |
| baseline | adapt_capacity | 1.023 | 0.9775 | 1.7728 |
| baseline | b_pre | 1.2161 | 0.8223 | 1.7728 |
| baseline | spread_lag | 1.3202 | 0.7575 | 1.7728 |
| baseline | growth | 1.1705 | 0.8543 | 1.7728 |
| baseline | inflation_cpi | 1.0386 | 0.9629 | 1.7728 |
| baseline | reserves | 1.0411 | 0.9605 | 1.7728 |
| baseline | tt | 1.04 | 0.9615 | 1.7728 |
| T | adapt_capacity | 1.0491 | 0.9532 | 1.262 |
| T | wsdi_days | 1.0085 | 0.9915 | 1.262 |
| T | T_it | 1.0094 | 0.9907 | 1.262 |
| T | inflation_cpi | 1.0488 | 0.9534 | 1.262 |
| T | reserves | 1.0089 | 0.9912 | 1.262 |
| T | tt | 1.0085 | 0.9915 | 1.262 |
| T | c_A_T | 1.0825 | 0.9238 | 1.3405 |
| T | c_X_T | 1.0086 | 0.9915 | 1.3405 |
| T | int_AX_T | 1.0399 | 0.9616 | 1.3405 |
| T | T_it | 1.0096 | 0.9905 | 1.3405 |
| T | inflation_cpi | 1.0503 | 0.9521 | 1.3405 |
| T | reserves | 1.0109 | 0.9893 | 1.3405 |
| T | tt | 1.0148 | 0.9854 | 1.3405 |


绝对相关系数不低于 0.60 的非重复变量对：

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |

## 6. 统计与程序验证

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | Wald χ² / F | 约束数/分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 0.6636 | 2 | — | 0.718 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 0.4255 | 1 | — | 0.514 |
| baseline | Interact_AX | c_A = int_AX = 0 | 0.2994 | 2 | — | 0.861 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 0.1765 | 1 | — | 0.674 |
| baseline | Interact_all | c_A = int_AB = 0 | 0.6681 | 2 | — | 0.716 |
| baseline | Interact_all | c_A = int_AX = 0 | 0.3879 | 2 | — | 0.824 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 0.8489 | 3 | — | 0.838 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 0.679 | 2 | — | 0.712 |
| T | T5_macro | macro controls jointly zero | 2.103 | 1 | — | 0.147 |
| T | T7_layer2_A | external controls jointly zero | 9.8188 | 2 | — | 0.007 |
| T | T7_layer2_A | all controls jointly zero | 10.1277 | 3 | — | 0.018 |
| T | T8_interact_core | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 1.6914 | 2 | — | 0.429 |
| T | T8_interact_core | interaction zero: int_AX_T = 0 | 0.2473 | 1 | — | 0.619 |
| T | T9_interact_macro | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 1.3225 | 2 | — | 0.516 |
| T | T9_interact_macro | interaction zero: int_AX_T = 0 | 0.2747 | 1 | — | 0.600 |
| T | T10_interact_full | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 3.4598 | 2 | — | 0.177 |
| T | T10_interact_full | interaction zero: int_AX_T = 0 | 3.3893 | 1 | — | 0.066 |
| T | T9_interact_macro | macro controls jointly zero | 2.1297 | 1 | — | 0.144 |
| T | T10_interact_full | external controls jointly zero | 9.8461 | 2 | — | 0.007 |
| T | T10_interact_full | all controls jointly zero | 10.0881 | 3 | — | 0.018 |
| doomloop | DN3_full | low- and high-branch coefficients jointly zero | 13.3133 | 2 | 49 | <0.001 |
| doomloop | DN3_full | macro controls jointly zero | 21.7806 | 2 | 49 | <0.001 |
| doomloop | DN3_full | external controls jointly zero | 0.8964 | 2 | 49 | 0.415 |
| doomloop | DN3_full | all controls jointly zero | 11.8624 | 4 | 49 | <0.001 |
| doomloop | RDN3_full | branches jointly zero; debt-equation cutoff | 1.5946 | 2 | 49 | 0.213 |
| doomloop | RDN3_full | macro controls jointly zero | 0.524 | 2 | 49 | 0.595 |
| doomloop | RDN3_full | external controls jointly zero | 6.0509 | 2 | 49 | 0.004 |
| doomloop | RDN3_full | all controls jointly zero | 3.1217 | 4 | 49 | 0.023 |

### 6.2 代数、映射与 hinge 公式

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | T(t+1) equals exact F.T(t) | 0 | 1.00e-12 | 通过 |
| theta | T(t) equals ConstantGDP(t) / ConstantGDP(t-1) | 0 | 1.00e-12 | 通过 |
| theta | b_pre equals exact L.debt_gdp | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 6.94e-18 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw T-margin formula | 1.39e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl T margin | 0 | 1.00e-12 | 通过 |
| theta | theta component identity | 0 | 1.00e-12 | 通过 |
| doomloop | theta uses b_pre*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop | b_pre maps exactly to L.debt_gdp | 0 | 1.00e-10 | 通过 |
| doomloop | criterion theta low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion theta high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b_pre low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b_pre high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion mA low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion mA high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion TA low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion TA high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b_pre*mA low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b_pre*mA high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | A=(1-capacity) outcome equals A(t)-A(t-1) | 0 | 1.00e-10 | 通过 |
| doomloop | main debt low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | main debt high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | A=(1-capacity) debt-cutoff low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | A=(1-capacity) debt-cutoff high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | A=(1-capacity) cutoff equals debt cutoff | 0 | 1.00e-12 | 通过 |

### 6.3 估计器配置与数值复核

| 板块 | 模型 | 检查 | 期望 | 实际 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | Layer2_A | e(cmd) is xtlsdvc | 1 | 1 | 通过 |
| baseline | Layer2_A | bootstrap variances positive | 1 | 1 | 通过 |
| baseline | Interact_all | e(cmd) is xtlsdvc | 1 | 1 | 通过 |
| baseline | Interact_all | bootstrap variances positive | 1 | 1 | 通过 |
| T | Spread_Interact_all | e(cmd) is xtlsdvc | 1 | 1 | 通过 |
| T | Spread_Interact_all | bootstrap variances positive | 1 | 1 | 通过 |
| T | T7_layer2_A | e(cmd) is xtlsdvc | 1 | 1 | 通过 |
| T | T7_layer2_A | bootstrap variances positive | 1 | 1 | 通过 |
| T | T10_interact_full | e(cmd) is xtlsdvc | 1 | 1 | 通过 |
| T | T10_interact_full | bootstrap variances positive | 1 | 1 | 通过 |

第 2—3 节正式配置均为 `xtlsdvc, initial(bb) bias(2) vcov(50)`。`bias(2)` 修正精度为 $O((NT)^{-1})$，在代表性规格中与 `bias(1)` 数值接近且稳定；`bias(3)` 在当前短而不平衡面板的预检中产生爆炸性动态系数，故未作为主规格。第 4 节继续用 areg 与显式 LSDV 复核：

| 板块 | 模型/判据 | 变量 | areg | LSDV | \|系数差\| | \|SE差\| |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| doomloop | theta | beta_L | -2.2634 | -2.2634 | 1.36e-13 | 1.14e-13 |
| doomloop | theta | beta_H | 3.4159 | 3.4159 | 2.66e-14 | 4.22e-15 |
| doomloop | b_pre | beta_L | 0.1923 | 0.1923 | 1.22e-15 | 2.71e-16 |
| doomloop | b_pre | beta_H | -0.1441 | -0.1441 | 6.47e-15 | 4.00e-15 |
| doomloop | mA | beta_L | -6.3812 | -6.3812 | 4.45e-13 | 2.72e-13 |
| doomloop | mA | beta_H | 8.5655 | 8.5655 | 3.73e-14 | 8.66e-15 |
| doomloop | TA | beta_L | 0.2503 | 0.2503 | 3.07e-14 | 7.66e-15 |
| doomloop | TA | beta_H | -2.0869 | -2.0869 | 5.20e-14 | 7.77e-16 |
| doomloop | b_pre*mA | beta_L | -1.708 | -1.708 | 9.06e-14 | 6.16e-14 |
| doomloop | b_pre*mA | beta_H | 4.9064 | 4.9064 | 3.55e-14 | 1.55e-15 |
| doomloop | adapt_capaci | delta_L | 0.6958 | 0.6958 | 1.83e-14 | 1.02e-14 |
| doomloop | adapt_capaci | delta_H | -0.1539 | -0.1539 | 6.94e-15 | 2.05e-15 |

### 6.4 Cutoff 最小 RSS 与样本加总

| Criterion | 记录 cutoff | 最小 RSS | cutoff RSS | \|差值\| | N | N_low | N_high | 加总 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | -0.025 | 1.096934 | 1.096934 | 0 | 742 | 75 | 667 | 通过 | 通过 |
| $b^{pre}_{it}$ | 1.0003 | 1.358765 | 1.358765 | 0 | 984 | 885 | 99 | 通过 | 通过 |
| $\widehat m^A_{it}$ | -0.0337 | 1.063838 | 1.063838 | 0 | 742 | 75 | 667 | 通过 | 通过 |
| $\widehat T^A_{it}$ | 0.0135 | 1.694753 | 1.694753 | 0 | 996 | 648 | 348 | 通过 | 通过 |
| $b^{pre}_{it}\widehat m^A_{it}$ | -0.0354 | 1.061425 | 1.061425 | 0 | 742 | 75 | 667 | 通过 | 通过 |

A（1−Capacity）cutoff 继承检查：

| 方程 | cutoff 来源 | cutoff | 债务 profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| debt | debt_full | -0.025 | 1.0969 | 1.0969 | 0 | 通过 |
| ready_debt | debt_full | -0.025 | 1.0969 | 1.0969 | 0 | 通过 |

### 6.5 五判据特定样本与拟合结果

| Criterion | N | 聚类数 | RSS | Within R2 | 理论方向 |
| --- | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | 742 | 50 | 1.096934 | 0.3683 | No (-,+) |
| $b^{pre}_{it}$ | 984 | 52 | 1.358765 | 0.3633 | Match (+,-) |
| $\widehat m^A_{it}$ | 742 | 50 | 1.063838 | 0.3874 | No (-,+) |
| $\widehat T^A_{it}$ | 996 | 52 | 1.694753 | 0.2535 | Match (+,-) |
| $b^{pre}_{it}\widehat m^A_{it}$ | 742 | 50 | 1.061425 | 0.3888 | No (-,+) |

各行使用判据特定的完整案例样本；当 N 不同时，RSS 与 Within R² 不作跨行排名。

## 7. 图形 QA

| 图形 | 字节 | 状态 |
| --- | ---: | ---: |
| figure1_theta_distribution_cutoff.png | 293,596 | 通过 |
| figure1_theta_distribution_cutoff.pdf | 81,181 | 通过 |
| figure2_mA_by_debt_wsdi.png | 269,503 | 通过 |
| figure2_mA_by_debt_wsdi.pdf | 75,399 | 通过 |
| debt_marginal_effect_no_b.png | 177,746 | 通过 |
| debt_marginal_effect_no_b.pdf | 73,945 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.png | 177,917 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.pdf | 72,541 | 通过 |
| kink_marginal_effects_no_state.png | 227,021 | 通过 |
| kink_marginal_effects_no_state.pdf | 79,795 | 通过 |

图 1 的 theta 直方图与国家排序都只使用债务全控制方程实际样本，竖直线来自同一方程的 RSS 最优 cutoff。图 2 逐项取负转换 `Interact_all` 的边际利差效应及其 bootstrap 置信区间。债务图和 A（1−Capacity）图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0；A 图的竖直线同样来自债务全控制方程。

## 8. Required Caveats for Stakeholders

- 第 2—3 节使用 `xtlsdvc, initial(bb) bias(2) vcov(50)` 的方程内 bootstrap 标准误；第 4 节使用 `vce(cluster country_id)`。两者都不等于传播全部上游生成误差的全流程 bootstrap。
- theta 是两条上游回归的生成变量；cutoff 又在对应样本中搜索，常规 p 值没有覆盖联合不确定性。
- 五种判据使用各自当前变量完整案例；样本不同时不能按 RSS 直接排序，并仍有模型选择和多重比较问题。
- 固定效应相关性结果不支持因果措辞。

## 9. 原始输出索引

完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。
