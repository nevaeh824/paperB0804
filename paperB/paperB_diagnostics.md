# Paper B：统计检验与数据检查

> 生成时间：2026-08-17 17:21（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。

## 1. Validation Report

### Overall Assessment: Share with caveats

单位换算检查通过 27/27 项；代数、映射与 hinge 检查通过 25/25 项；cutoff 最小 RSS 及继承关系检查通过 7/7 项。计算实现和样本内比较已通过，但国家内相关、theta 生成误差、cutoff 搜索和多判据选择不确定性尚未由联合推断覆盖。

### Methodology Review

主流程准确对应 workflow：一期债务变化、去债务状态控制、readiness 水平去滞后状态控制，readiness 固定使用债务全控制 theta cutoff。五种阈值判据使用同一个债务全控制样本、因变量、控制变量、固定效应和误差口径，因此 RSS 与 Within R² 可比较。

### Issues Found

1. **[Medium] 推断未覆盖 cutoff 搜索和上游生成误差。** 当前 p 值是固定 cutoff 条件下的异方差稳健 p 值。
2. **[Medium] 标准误未处理国家内序列相关。** 面板推断应补充国家聚类及完整管线 bootstrap。
3. **[Low] 竞争判据为样本内拟合比较。** 最低 RSS 不等于统计上显著优于其他非嵌套判据。

## 2. 数据来源、单位与时序

原始分析输入是 `data0804/invest_panel_weo.csv` 与 `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`。两者按唯一 `iso3 year` 键合并；`wsdi_days` 乘以 0.01 后定义 X。主面板源百分数、比率和 0—100 指数先除以 100；金额变量不缩放。`ln_constantgdp` 仅用于构造 T，不进入 Baseline 或其复核模型；`growth` 不进入 T 指标模型。Doomloop 从 empirical-theta panel 读取已换算变量，并单独将源 `interest_revenue` 除以 100。

- $T_{it}=\ln(ConstantGDP_{it})/\ln(ConstantGDP_{i,t-1})$，$T_{i,t+1}=F.T_{it}$；两者均严格要求相邻年份。
- 债务变化结果为 $\Delta debt_{i,t+1}=F.debt\_gdp_{it}-debt\_gdp_{it}$；理论债务状态统一使用 $b^{pre}_{it}=L.debt\_gdp_{it}$。
- $A_{it}=readiness100_{it}$；readiness 方程不使用滞后状态项。

### 2.1 Doomloop 源字段换算

| 变量 | 源最小值 | 源最大值 | 比率最小值 | 比率最大值 | 最大误差 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| interest_revenue | -14.8211 | 79.8698 | -0.1482 | 0.7987 | 0 | 通过 |

## 3. 固定样本与描述统计

| 固定样本 | N | 国家数 | 年份数 | 年份范围 |
| --- | ---: | ---: | ---: | ---: |
| Baseline 全交互 | 742 | 50 | 20 | 1999–2018 |
| T 指标全控制交互 | 742 | 50 | 20 | 1999–2018 |
| Doomloop 债务/五判据共同样本 | 742 | 50 | 20 | 1999–2018 |
| Doomloop Readiness | 742 | 50 | 20 | 1999–2018 |

### 3.1 Baseline 输入变量

| 变量 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bond_spreads | 1,330 | 0.0223 | 0.0428 | -0.0341 | 0.0061 | 0.3431 |
| readiness100 | 1,769 | 0.4987 | 0.1452 | 0.1793 | 0.4928 | 0.8072 |
| growth | 1,822 | 0.0337 | 0.0353 | -0.1455 | 0.0345 | 0.2462 |
| inflation_cpi | 1,820 | 0.0561 | 0.1074 | -0.0397 | 0.0317 | 1.973 |
| reserves | 1,757 | 0.1664 | 0.188 | 0.0034 | 0.1134 | 1.4339 |
| tt | 1,605 | 1.0069 | 0.1859 | 0.3188 | 0.9942 | 2.7308 |
| wsdi_days | 1,233 | 0.1578 | 0.1026 | 0 | 0.1368 | 0.7334 |
| spread_lag | 1,267 | 0.022 | 0.0421 | -0.0302 | 0.0062 | 0.3431 |
| b_pre | 1,661 | 0.573 | 0.3469 | 0.0005 | 0.5077 | 2.6096 |

### 3.2 T 指标与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T_lead | tax | 742 | 1.0033 | 0.0047 | 0.9583 | 1.0033 | 1.0397 |
| T_it | tax | 742 | 1.0035 | 0.0049 | 0.9583 | 1.0035 | 1.0397 |
| mA_hat_spread_ratio | theta_support | 742 | 0.0372 | 0.0228 | -0.0004 | 0.0318 | 0.1325 |
| mA_hat | theta_support | 742 | 0.0372 | 0.0228 | -0.0004 | 0.0318 | 0.1325 |
| spread_saving_component | theta_support | 742 | 0.03 | 0.0396 | -0 | 0.0164 | 0.2697 |
| TA_hat | theta_support | 742 | 0.0077 | 0.0014 | 0.0054 | 0.0075 | 0.0153 |
| theta_hat_A | theta_support | 742 | 0.0377 | 0.0398 | 0.0057 | 0.0242 | 0.2764 |
| theta_hat_A | all_constructible | 742 | 0.0377 | 0.0398 | 0.0057 | 0.0242 | 0.2764 |

### 3.3 Doomloop 主规格与判据变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_no_b | debt | b_outcome | dependent_variable | 742 | 0.0093 | 0.0507 | -0.2736 | 0.0021 | 0.4186 |
| debt_no_b | debt | debt_kink_low | regressor | 742 | 0.0253 | 0.0141 | 0 | 0.0261 | 0.0538 |
| debt_no_b | debt | debt_kink_high | regressor | 742 | 0.0032 | 0.0161 | 0 | 0 | 0.1386 |
| debt_no_b | debt | wsdi_days | regressor | 742 | 0.1709 | 0.1051 | 0 | 0.1523 | 0.7334 |
| debt_no_b | debt | growth | regressor | 742 | 0.0281 | 0.0317 | -0.1451 | 0.0276 | 0.2462 |
| debt_no_b | debt | inflation_cpi | regressor | 742 | 0.0298 | 0.0294 | -0.0169 | 0.023 | 0.2353 |
| debt_no_b | debt | reserves | regressor | 742 | 0.1425 | 0.1344 | 0.0034 | 0.1086 | 1.1473 |
| debt_no_b | debt | tt | regressor | 742 | 0.9997 | 0.0976 | 0.6748 | 0.998 | 1.574 |
| debt_no_b | debt | readiness100 | construction_input | 742 | 0.5604 | 0.1314 | 0.2672 | 0.5557 | 0.7973 |
| debt_no_b | debt | theta_hat_A | construction_input | 742 | 0.0377 | 0.0398 | 0.0057 | 0.0242 | 0.2764 |
| debt_no_b | debt | b_pre | construction_input | 742 | 0.5967 | 0.3418 | 0.039 | 0.5128 | 2.0365 |
| debt_no_b | debt | mA_hat | construction_input | 742 | 0.0372 | 0.0228 | -0.0004 | 0.0318 | 0.1325 |
| debt_no_b | debt | TA_hat | construction_input | 742 | 0.0077 | 0.0014 | 0.0054 | 0.0075 | 0.0153 |
| debt_no_b | debt | b_pre_mA_hat | construction_input | 742 | 0.03 | 0.0396 | -0 | 0.0164 | 0.2697 |
| ready_no_lag_debt_cutoff | ready_debt | A_outcome | dependent_variable | 742 | 0.5604 | 0.1314 | 0.2672 | 0.5557 | 0.7973 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 742 | 0.0024 | 0.0031 | -0.0043 | 0.0016 | 0.0178 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 742 | 0.0003 | 0.0014 | 0 | 0 | 0.0153 |
| ready_no_lag_debt_cutoff | ready_debt | wsdi_days | regressor | 742 | 0.1709 | 0.1051 | 0 | 0.1523 | 0.7334 |
| ready_no_lag_debt_cutoff | ready_debt | growth | regressor | 742 | 0.0281 | 0.0317 | -0.1451 | 0.0276 | 0.2462 |
| ready_no_lag_debt_cutoff | ready_debt | inflation_cpi | regressor | 742 | 0.0298 | 0.0294 | -0.0169 | 0.023 | 0.2353 |
| ready_no_lag_debt_cutoff | ready_debt | reserves | regressor | 742 | 0.1425 | 0.1344 | 0.0034 | 0.1086 | 1.1473 |
| ready_no_lag_debt_cutoff | ready_debt | tt | regressor | 742 | 0.9997 | 0.0976 | 0.6748 | 0.998 | 1.574 |
| ready_no_lag_debt_cutoff | ready_debt | interest_revenue | construction_input | 742 | 0.0622 | 0.069 | -0.0624 | 0.0478 | 0.4362 |
| ready_no_lag_debt_cutoff | ready_debt | theta_hat_A | construction_input | 742 | 0.0377 | 0.0398 | 0.0057 | 0.0242 | 0.2764 |

## 4. 缺失、重复键与 Within 变异

三个估计阶段均对国家—年份键执行 fail-closed 唯一性检查；不会自动去重。Baseline、T 指标、theta 构造、Doomloop 债务和 readiness 方程逐行使用同一个全流程共同非缺失样本；五种判据也继承该样本。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 (%) | 独占损失 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 497 | 27.2 | 1 |
| baseline | — | wsdi_days | 594 | 32.51 | 388 |
| baseline | — | readiness100 | 58 | 3.17 | 0 |
| baseline | — | b_pre | 166 | 9.09 | 11 |
| baseline | — | spread_lag | 560 | 30.65 | 30 |
| baseline | — | growth | 5 | 0.27 | 0 |
| baseline | — | inflation_cpi | 7 | 0.38 | 1 |
| baseline | — | reserves | 70 | 3.83 | 0 |
| baseline | — | tt | 222 | 12.15 | 69 |
| T | — | T_lead | 65 | 3.56 | 0 |
| T | — | readiness100 | 58 | 3.17 | 0 |
| T | — | wsdi_days | 594 | 32.51 | 437 |
| T | — | T_it | 65 | 3.56 | 17 |
| T | — | inflation_cpi | 7 | 0.38 | 1 |
| T | — | reserves | 70 | 3.83 | 0 |
| T | — | tt | 222 | 12.15 | 146 |
| doomloop | debt | b_outcome | 166 | 9.09 | 0 |
| doomloop | debt | readiness100 | 58 | 3.17 | 0 |
| doomloop | debt | theta_hat_A | 1,085 | 59.39 | 0 |
| doomloop | debt | b_pre | 166 | 9.09 | 0 |
| doomloop | debt | mA_hat | 1,085 | 59.39 | 0 |
| doomloop | debt | TA_hat | 1,085 | 59.39 | 0 |
| doomloop | debt | b_pre_mA_hat | 1,085 | 59.39 | 0 |
| doomloop | debt | wsdi_days | 594 | 32.51 | 0 |
| doomloop | debt | growth | 5 | 0.27 | 0 |
| doomloop | debt | inflation_cpi | 7 | 0.38 | 0 |
| doomloop | debt | reserves | 70 | 3.83 | 0 |
| doomloop | debt | tt | 222 | 12.15 | 0 |
| doomloop | ready | A_outcome | 58 | 3.17 | 0 |
| doomloop | ready | interest_revenue | 141 | 7.72 | 0 |
| doomloop | ready | theta_hat_A | 1,085 | 59.39 | 266 |
| doomloop | ready | wsdi_days | 594 | 32.51 | 0 |
| doomloop | ready | growth | 5 | 0.27 | 0 |
| doomloop | ready | inflation_cpi | 7 | 0.38 | 0 |
| doomloop | ready | reserves | 70 | 3.83 | 0 |
| doomloop | ready | tt | 222 | 12.15 | 0 |

### 4.2 Within 变异

| 板块 | 方程 | 变量 | 总体 SD | Within SD | Within/总体 | FE 识别 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 0.0428 | 0.0174 | 0.406 | adequate |
| baseline | — | readiness100 | 0.1452 | 0.0434 | 0.2986 | adequate |
| baseline | — | growth | 0.0353 | 0.0317 | 0.8996 | adequate |
| baseline | — | inflation_cpi | 0.1074 | 0.0925 | 0.8612 | adequate |
| baseline | — | reserves | 0.188 | 0.091 | 0.4842 | adequate |
| baseline | — | tt | 0.1859 | 0.165 | 0.8875 | adequate |
| baseline | — | wsdi_days | 0.1026 | 0.0858 | 0.8364 | adequate |
| baseline | — | spread_lag | 0.0421 | 0.0174 | 0.4129 | adequate |
| baseline | — | b_pre | 0.3469 | 0.182 | 0.5246 | adequate |
| T | — | T_lead | 0.0047 | 0.0042 | 0.8988 | adequate |
| T | — | T_it | 0.0049 | 0.0044 | 0.8997 | adequate |
| T | — | readiness100 | 0.1314 | 0.0352 | 0.2678 | adequate |
| T | — | wsdi_days | 0.1051 | 0.0819 | 0.7788 | adequate |
| T | — | inflation_cpi | 0.0294 | 0.0196 | 0.6668 | adequate |
| T | — | reserves | 0.1344 | 0.0642 | 0.4776 | adequate |
| T | — | tt | 0.0976 | 0.0823 | 0.8429 | adequate |
| doomloop | debt | b_outcome | 0.0507 | 0.0484 | 0.9544 | adequate |
| doomloop | debt | theta_hat_A | 0.0398 | 0.0173 | 0.4348 | adequate |
| doomloop | debt | b_pre | 0.3418 | 0.1404 | 0.4107 | adequate |
| doomloop | debt | mA_hat | 0.0228 | 0.0094 | 0.4122 | adequate |
| doomloop | debt | TA_hat | 0.0014 | 0.0011 | 0.7788 | adequate |
| doomloop | debt | b_pre_mA_hat | 0.0396 | 0.0171 | 0.4316 | adequate |
| doomloop | debt | readiness100 | 0.1314 | 0.0352 | 0.2678 | adequate |
| doomloop | debt | wsdi_days | 0.1051 | 0.0819 | 0.7788 | adequate |
| doomloop | debt | growth | 0.0317 | 0.0257 | 0.8125 | adequate |
| doomloop | debt | inflation_cpi | 0.0294 | 0.0196 | 0.6668 | adequate |
| doomloop | debt | reserves | 0.1344 | 0.0642 | 0.4776 | adequate |
| doomloop | debt | tt | 0.0976 | 0.0823 | 0.8429 | adequate |
| doomloop | ready | A_outcome | 0.1314 | 0.0352 | 0.2678 | adequate |
| doomloop | ready | theta_hat_A | 0.0398 | 0.0173 | 0.4348 | adequate |
| doomloop | ready | interest_revenue | 0.069 | 0.0209 | 0.3034 | adequate |
| doomloop | ready | wsdi_days | 0.1051 | 0.0819 | 0.7788 | adequate |
| doomloop | ready | growth | 0.0317 | 0.0257 | 0.8125 | adequate |
| doomloop | ready | inflation_cpi | 0.0294 | 0.0196 | 0.6668 | adequate |
| doomloop | ready | reserves | 0.1344 | 0.0642 | 0.4776 | adequate |
| doomloop | ready | tt | 0.0976 | 0.0823 | 0.8429 | adequate |

## 5. 共线性、相关性与系数变化

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline | wsdi_days | 1.014 | 0.9862 | 1.7914 |
| baseline | readiness100 | 1.0286 | 0.9722 | 1.7914 |
| baseline | b_pre | 1.2178 | 0.8212 | 1.7914 |
| baseline | spread_lag | 1.3254 | 0.7545 | 1.7914 |
| baseline | growth | 1.1781 | 0.8489 | 1.7914 |
| baseline | inflation_cpi | 1.0301 | 0.9708 | 1.7914 |
| baseline | reserves | 1.0397 | 0.9618 | 1.7914 |
| baseline | tt | 1.0374 | 0.9639 | 1.7914 |
| T | readiness100 | 1.0181 | 0.9822 | 1.1773 |
| T | wsdi_days | 1.009 | 0.991 | 1.1773 |
| T | T_it | 1.0197 | 0.9806 | 1.1773 |
| T | inflation_cpi | 1.0214 | 0.9791 | 1.1773 |
| T | reserves | 1.0157 | 0.9846 | 1.1773 |
| T | tt | 1.0076 | 0.9924 | 1.1773 |
| T | c_A_T | 1.0458 | 0.9562 | 1.2639 |
| T | c_X_T | 1.0201 | 0.9803 | 1.2639 |
| T | int_AX_T | 1.0432 | 0.9586 | 1.2639 |
| T | T_it | 1.0202 | 0.9802 | 1.2639 |
| T | inflation_cpi | 1.0214 | 0.9791 | 1.2639 |
| T | reserves | 1.0172 | 0.9831 | 1.2639 |
| T | tt | 1.0076 | 0.9924 | 1.2639 |


绝对相关系数不低于 0.60 的非重复变量对：

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |

## 6. 统计与程序验证

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | F | 分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 4.3046 | 2 | 664 | 0.014 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 4.0092 | 1 | 664 | 0.046 |
| baseline | Interact_AX | c_A = int_AX = 0 | 3.3355 | 2 | 664 | 0.036 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 0.3573 | 1 | 664 | 0.550 |
| baseline | Interact_all | c_A = int_AB = 0 | 4.2324 | 2 | 663 | 0.015 |
| baseline | Interact_all | c_A = int_AX = 0 | 4.0049 | 2 | 663 | 0.019 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 2.871 | 3 | 663 | 0.036 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 2.016 | 2 | 663 | 0.134 |
| T | T5_macro | macro controls jointly zero | 3.6194 | 1 | 669 | 0.058 |
| T | T7_layer2_A | external controls jointly zero | 0.4116 | 2 | 667 | 0.663 |
| T | T7_layer2_A | all controls jointly zero | 1.5383 | 3 | 667 | 0.203 |
| T | T8_interact_core | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 3.7805 | 2 | 669 | 0.023 |
| T | T8_interact_core | interaction zero: int_AX_T = 0 | 2.4078 | 1 | 669 | 0.121 |
| T | T9_interact_macro | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 4.1443 | 2 | 668 | 0.016 |
| T | T9_interact_macro | interaction zero: int_AX_T = 0 | 2.3004 | 1 | 668 | 0.130 |
| T | T10_interact_full | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 4.0395 | 2 | 666 | 0.018 |
| T | T10_interact_full | interaction zero: int_AX_T = 0 | 2.2444 | 1 | 666 | 0.135 |
| T | T9_interact_macro | macro controls jointly zero | 3.6558 | 1 | 668 | 0.056 |
| T | T10_interact_full | external controls jointly zero | 0.3808 | 2 | 666 | 0.683 |
| T | T10_interact_full | all controls jointly zero | 1.5217 | 3 | 666 | 0.208 |
| doomloop | DN3_full | low- and high-branch coefficients jointly zero | 14.6848 | 2 | 666 | <0.001 |
| doomloop | DN3_full | macro controls jointly zero | 5.2319 | 2 | 666 | 0.006 |
| doomloop | DN3_full | external controls jointly zero | 2.2202 | 2 | 666 | 0.109 |
| doomloop | DN3_full | all controls jointly zero | 4.6599 | 4 | 666 | 0.001 |
| doomloop | RDN3_full | branches jointly zero; debt-equation cutoff | 0.653 | 2 | 666 | 0.521 |
| doomloop | RDN3_full | macro controls jointly zero | 5.3234 | 2 | 666 | 0.005 |
| doomloop | RDN3_full | external controls jointly zero | 1.7835 | 2 | 666 | 0.169 |
| doomloop | RDN3_full | all controls jointly zero | 3.5743 | 4 | 666 | 0.007 |

### 6.2 代数、映射与 hinge 公式

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | T(t+1) equals exact F.T(t) | 0 | 1.00e-12 | 通过 |
| theta | T(t) equals ln GDP(t) / ln GDP(t-1) | 0 | 1.00e-12 | 通过 |
| theta | b_pre equals exact L.debt_gdp | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 2.78e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw T-margin formula | 1.73e-18 | 1.00e-12 | 通过 |
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
| doomloop | main debt low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | main debt high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | readiness debt-cutoff low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | readiness debt-cutoff high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | readiness cutoff equals debt cutoff | 0 | 1.00e-12 | 通过 |

### 6.3 areg 与显式 LSDV

| 板块 | 模型/判据 | 变量 | areg | LSDV | \|系数差\| | \|SE差\| |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Layer2_A | wsdi_days | 0.0094 | 0.0094 | 3.30e-17 | 8.67e-19 |
| baseline | Layer2_A | readiness100 | -0.0306 | -0.0306 | 6.63e-16 | 6.09e-15 |
| baseline | Layer2_A | b_pre | 0.0062 | 0.0062 | 6.16e-17 | 8.07e-17 |
| baseline | Layer2_A | spread_lag | 0.5784 | 0.5784 | 1.89e-15 | 6.38e-16 |
| baseline | Layer2_A | growth | -0.17 | -0.17 | 4.16e-16 | 0 |
| baseline | Layer2_A | inflation_cpi | 0.154 | 0.154 | 8.33e-16 | 1.49e-16 |
| baseline | Layer2_A | reserves | -0.0082 | -0.0082 | 4.51e-17 | 1.13e-17 |
| baseline | Layer2_A | tt | 0.0044 | 0.0044 | 3.82e-17 | 8.66e-16 |
| baseline | Interact_all | c_A | -0.0372 | -0.0372 | 1.11e-15 | 1.14e-16 |
| baseline | Interact_all | c_X | 0.0094 | 0.0094 | 3.30e-17 | 3.47e-18 |
| baseline | Interact_all | c_b | 0.0086 | 0.0086 | 9.54e-17 | 5.20e-18 |
| baseline | Interact_all | int_AB | -0.0665 | -0.0665 | 3.75e-16 | 1.39e-16 |
| baseline | Interact_all | int_AX | -0.0051 | -0.0051 | 3.89e-16 | 8.33e-17 |
| baseline | Interact_all | spread_lag | 0.5527 | 0.5527 | 1.11e-15 | 2.08e-16 |
| baseline | Interact_all | growth | -0.1664 | -0.1664 | 3.05e-16 | 3.47e-17 |
| baseline | Interact_all | inflation_cpi | 0.1617 | 0.1617 | 8.60e-16 | 1.39e-17 |
| baseline | Interact_all | reserves | -0.0088 | -0.0088 | 3.64e-17 | 5.46e-17 |
| baseline | Interact_all | tt | 0.0029 | 0.0029 | 4.03e-17 | 3.25e-17 |
| T | Spread_Interact_all | c_A | -0.0372 | -0.0372 | 1.36e-15 | 3.99e-17 |
| T | Spread_Interact_all | c_X | 0.0094 | 0.0094 | 1.73e-18 | 1.73e-18 |
| T | Spread_Interact_all | c_b | 0.0086 | 0.0086 | 2.26e-16 | 1.39e-17 |
| T | Spread_Interact_all | int_AB | -0.0665 | -0.0665 | 1.76e-15 | 9.71e-17 |
| T | Spread_Interact_all | int_AX | -0.0051 | -0.0051 | 5.85e-16 | 8.33e-17 |
| T | Spread_Interact_all | spread_lag | 0.5527 | 0.5527 | 3.00e-15 | 5.00e-16 |
| T | Spread_Interact_all | growth | -0.1664 | -0.1664 | 2.50e-16 | 6.25e-17 |
| T | Spread_Interact_all | inflation_cpi | 0.1617 | 0.1617 | 1.03e-15 | 6.25e-17 |
| T | Spread_Interact_all | reserves | -0.0088 | -0.0088 | 1.39e-17 | 4.34e-18 |
| T | Spread_Interact_all | tt | 0.0029 | 0.0029 | 6.29e-17 | 1.28e-16 |
| T | T7_layer2_A | wsdi_days | -0.0009 | -0.0009 | 1.51e-15 | 4.94e-17 |
| T | T7_layer2_A | readiness100 | 0.0086 | 0.0086 | 1.00e-14 | 2.27e-15 |
| T | T7_layer2_A | T_it | 0.2938 | 0.2938 | 7.33e-15 | 7.88e-13 |
| T | T7_layer2_A | inflation_cpi | -0.0267 | -0.0267 | 8.38e-15 | 1.15e-15 |
| T | T7_layer2_A | reserves | 0.0007 | 0.0007 | 4.29e-15 | 2.65e-16 |
| T | T7_layer2_A | tt | -0.0008 | -0.0008 | 1.36e-15 | 1.84e-16 |
| T | T10_interact_full | c_A_T | 0.0077 | 0.0077 | 1.02e-14 | 6.07e-15 |
| T | T10_interact_full | c_X_T | -0.0007 | -0.0007 | 1.49e-15 | 7.96e-17 |
| T | T10_interact_full | int_AX_T | 0.0136 | 0.0136 | 6.59e-16 | 2.26e-17 |
| T | T10_interact_full | T_it | 0.293 | 0.293 | 7.83e-15 | 1.10e-13 |
| T | T10_interact_full | inflation_cpi | -0.0266 | -0.0266 | 8.39e-15 | 2.43e-17 |
| T | T10_interact_full | reserves | 0.0006 | 0.0006 | 4.31e-15 | 2.90e-16 |
| T | T10_interact_full | tt | -0.0008 | -0.0008 | 1.36e-15 | 8.24e-18 |
| doomloop | theta | beta_L | 2.3649 | 2.3649 | 8.88e-15 | 1.78e-15 |
| doomloop | theta | beta_H | -0.9025 | -0.9025 | 7.72e-14 | 2.99e-14 |
| doomloop | b_pre | beta_L | 0.0657 | 0.0657 | 2.94e-15 | 9.02e-16 |
| doomloop | b_pre | beta_H | -0.2275 | -0.2275 | 6.38e-16 | 5.55e-17 |
| doomloop | mA | beta_L | 0.9549 | 0.9549 | 5.68e-14 | 1.49e-14 |
| doomloop | mA | beta_H | -3.4161 | -3.4161 | 3.33e-14 | 6.44e-15 |
| doomloop | TA | beta_L | 2.2579 | 2.2579 | 1.48e-12 | 3.45e-13 |
| doomloop | TA | beta_H | -26.71 | -26.71 | 2.32e-12 | 1.25e-12 |
| doomloop | b_pre*mA | beta_L | 2.9045 | 2.9045 | 2.98e-14 | 1.22e-15 |
| doomloop | b_pre*mA | beta_H | -1.2233 | -1.2233 | 8.79e-14 | 2.65e-14 |
| doomloop | readiness | delta_L | -0.1376 | -0.1376 | 3.61e-13 | 1.62e-14 |
| doomloop | readiness | delta_H | -0.8396 | -0.8396 | 4.79e-14 | 3.44e-15 |

### 6.4 Cutoff 最小 RSS 与样本加总

| Criterion | 记录 cutoff | 最小 RSS | cutoff RSS | \|差值\| | N | N_low | N_high | 加总 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | 0.078 | 1.074117 | 1.074117 | 0 | 742 | 667 | 75 | 通过 | 通过 |
| $b^{pre}_{it}$ | 0.26 | 1.044275 | 1.044275 | 0 | 742 | 75 | 667 | 通过 | 通过 |
| $\widehat m^A_{it}$ | 0.0146 | 1.044151 | 1.044151 | 0 | 742 | 75 | 667 | 通过 | 通过 |
| $\widehat T^A_{it}$ | 0.0082 | 1.202965 | 1.202965 | 0 | 742 | 525 | 217 | 通过 | 通过 |
| $b^{pre}_{it}\widehat m^A_{it}$ | 0.0402 | 1.075191 | 1.075191 | 0 | 742 | 574 | 168 | 通过 | 通过 |

Readiness cutoff 继承检查：

| 方程 | cutoff 来源 | cutoff | 债务 profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| debt | debt_full | 0.078 | 1.0741 | 1.0741 | 0 | 通过 |
| ready_debt | debt_full | 0.078 | 1.0741 | 1.0741 | 0 | 通过 |

### 6.5 五判据共同样本与拟合排序

| RSS 排名 | Criterion | N | RSS | Within R2 | 理论方向 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | $\widehat m^A_{it}$ | 742 | 1.044151 | 0.3987 | Match (+,-) |
| 2 | $b^{pre}_{it}$ | 742 | 1.044275 | 0.3986 | Match (+,-) |
| 3 | $\widehat\theta^A_{it}$ | 742 | 1.074117 | 0.3815 | Match (+,-) |
| 4 | $b^{pre}_{it}\widehat m^A_{it}$ | 742 | 1.075191 | 0.3808 | Match (+,-) |
| 5 | $\widehat T^A_{it}$ | 742 | 1.202965 | 0.3073 | Match (+,-) |

## 7. 图形 QA

| 图形 | 字节 | 状态 |
| --- | ---: | ---: |
| debt_marginal_effect_no_b.png | 180,069 | 通过 |
| debt_marginal_effect_no_b.pdf | 73,074 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.png | 176,535 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.pdf | 71,869 | 通过 |
| kink_marginal_effects_no_state.png | 229,868 | 通过 |
| kink_marginal_effects_no_state.pdf | 78,983 | 通过 |

债务图和 readiness 图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0。Readiness 图的竖直线来自债务全控制方程。

## 8. Required Caveats for Stakeholders

- 当前 `vce(robust)` 处理异方差，但不处理同一国家内序列相关。
- theta 是两条上游回归的生成变量；cutoff 又在同一样本中搜索，常规 p 值没有覆盖联合不确定性。
- 比较五种判据会引入模型选择和多重比较问题；最低 RSS 仅代表本样本内拟合。
- 固定效应相关性结果不支持因果措辞。

## 9. 原始输出索引

完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。
