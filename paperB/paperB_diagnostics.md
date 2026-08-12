# Paper B：统计检验与数据检查

> 生成时间：2026-08-12 16:02（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。

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

唯一原始分析输入是 `data0804/invest_panel_weo.csv`。源百分数、比率和 0—100 指数先除以 100；金额变量不缩放。主流程构造 `ln_capitagdp=ln(capitaGDP)`、`ln_currentgdp=ln(CurrentGDP)` 与 `ln_debt=ln(debt)`；所有回归控制 growth 和 ln_capitagdp。Doomloop 从 empirical-theta panel 读取构造量，并单独将源 `interest_revenue` 除以 100。

- $Y_{it}=\ln(CurrentGDP_{it})$，$Y_{i,t+1}=F.\ln(CurrentGDP_{it})$。
- $\Delta\ln(debt)_{i,t+1}=F.\ln(debt_{it})-\ln(debt_{it})$，严格要求相邻年份。
- $A_{it}=readiness100_{it}$；readiness 方程不使用滞后状态项。

### 2.1 Doomloop 源字段换算

| 变量 | 源最小值 | 源最大值 | 比率最小值 | 比率最大值 | 最大误差 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| interest_revenue | -14.8211 | 79.8698 | -0.1482 | 0.7987 | 0 | 通过 |

## 3. 固定样本与描述统计

| 固定样本 | N | 国家数 | 年份数 | 年份范围 |
| --- | ---: | ---: | ---: | ---: |
| Baseline 全交互 | 1,174 | 60 | 26 | 1998–2023 |
| Y 全控制交互 | 1,485 | 60 | 28 | 1995–2022 |
| Doomloop 债务/五判据共同样本 | 1,433 | 60 | 28 | 1995–2022 |
| Doomloop Readiness | 1,458 | 59 | 29 | 1995–2023 |

### 3.1 Baseline 输入变量

| 变量 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bond_spreads | 1,330 | 0.0223 | 0.0428 | -0.0341 | 0.0061 | 0.3431 |
| vulnerability100 | 1,769 | 0.3825 | 0.079 | 0.251 | 0.368 | 0.5808 |
| readiness100 | 1,769 | 0.4987 | 0.1452 | 0.1793 | 0.4928 | 0.8072 |
| growth | 1,822 | 0.0337 | 0.0353 | -0.1455 | 0.0345 | 0.2462 |
| inflation_cpi | 1,820 | 0.0561 | 0.1074 | -0.0397 | 0.0317 | 1.973 |
| reserves | 1,757 | 0.0531 | 0.1262 | 1.31e-06 | 0.017 | 1.5271 |
| tt | 1,605 | 1.0069 | 0.1859 | 0.3188 | 0.9942 | 2.7308 |
| ln_capitagdp | 1,823 | 10.0449 | 0.9494 | 7.2866 | 10.3194 | 11.8118 |
| ln_debt | 1,724 | 7.2075 | 2.761 | 0.4055 | 7.0078 | 15.9286 |

### 3.2 Y 与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Y_outcome | output | 1,485 | 8.0535 | 2.7943 | 1.469 | 7.6614 | 16.8549 |
| Y_lag | output | 1,485 | 7.9737 | 2.7888 | 1.1909 | 7.5993 | 16.7905 |
| mA_hat_spread_ratio | theta_support | 1,114 | -0.0107 | 0.0743 | -0.2068 | -0.0159 | 0.2078 |
| mA_hat | theta_support | 1,114 | -0.0107 | 0.0743 | -0.2068 | -0.0159 | 0.2078 |
| ln_debt_mA_hat | theta_support | 1,114 | 0.1004 | 0.7027 | -0.7828 | -0.1219 | 3.2993 |
| spread_saving_component | theta_support | 1,114 | 0.1004 | 0.7027 | -0.7828 | -0.1219 | 3.2993 |
| YA_hat | theta_support | 1,114 | 0.0215 | 0.0061 | 0.0119 | 0.0199 | 0.0386 |
| theta_hat_A | theta_support | 1,114 | 0.1219 | 0.703 | -0.7476 | -0.1032 | 3.3261 |
| theta_hat_A | all_constructible | 1,677 | 0.0319 | 0.6783 | -0.8062 | -0.1651 | 3.3491 |

### 3.3 Doomloop 主规格与判据变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_no_b | debt | b_outcome | dependent_variable | 1,433 | 0.0915 | 0.1129 | -0.8964 | 0.0765 | 1.2158 |
| debt_no_b | debt | debt_kink_low | regressor | 1,433 | 0.0237 | 0.0415 | 0 | 0 | 0.1951 |
| debt_no_b | debt | debt_kink_high | regressor | 1,433 | 0.2077 | 0.3607 | 0 | 0.0634 | 2.1101 |
| debt_no_b | debt | vulnerability100 | regressor | 1,433 | 0.3827 | 0.0786 | 0.251 | 0.3684 | 0.5808 |
| debt_no_b | debt | growth | regressor | 1,433 | 0.0338 | 0.0361 | -0.1455 | 0.0344 | 0.2462 |
| debt_no_b | debt | ln_capitagdp | regressor | 1,433 | 10.0469 | 0.9492 | 7.3312 | 10.293 | 11.8118 |
| debt_no_b | debt | inflation_cpi | regressor | 1,433 | 0.0462 | 0.0542 | -0.0177 | 0.0314 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,433 | 0.0546 | 0.1342 | 2.41e-06 | 0.0151 | 1.5271 |
| debt_no_b | debt | tt | regressor | 1,433 | 1.0089 | 0.1826 | 0.3188 | 0.9942 | 2.7308 |
| debt_no_b | debt | readiness100 | construction_input | 1,433 | 0.5057 | 0.1462 | 0.2021 | 0.4994 | 0.8072 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,433 | 0.0362 | 0.6879 | -0.8062 | -0.1625 | 3.3261 |
| debt_no_b | debt | ln_debt | construction_input | 1,433 | 7.3136 | 2.7322 | 0.9462 | 7.1055 | 15.8777 |
| debt_no_b | debt | mA_hat | construction_input | 1,433 | -0.0251 | 0.0815 | -0.2749 | -0.0272 | 0.2078 |
| debt_no_b | debt | YA_hat | construction_input | 1,433 | 0.0229 | 0.0066 | 0.0119 | 0.0217 | 0.0396 |
| debt_no_b | debt | ln_debt_mA_hat | construction_input | 1,433 | 0.0133 | 0.6889 | -0.8444 | -0.1814 | 3.2993 |
| ready_no_lag_debt_cutoff | ready_debt | A_outcome | dependent_variable | 1,458 | 0.5029 | 0.1442 | 0.2021 | 0.4965 | 0.7973 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 1,458 | 0.0079 | 0.0207 | -0.0004 | 0 | 0.1941 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 1,458 | 0.0252 | 0.0619 | -0.1083 | 0.0029 | 0.5622 |
| ready_no_lag_debt_cutoff | ready_debt | vulnerability100 | regressor | 1,458 | 0.3817 | 0.0792 | 0.251 | 0.3673 | 0.5808 |
| ready_no_lag_debt_cutoff | ready_debt | growth | regressor | 1,458 | 0.0331 | 0.0355 | -0.1455 | 0.0332 | 0.2462 |
| ready_no_lag_debt_cutoff | ready_debt | ln_capitagdp | regressor | 1,458 | 10.0344 | 0.9372 | 7.3312 | 10.2884 | 11.7097 |
| ready_no_lag_debt_cutoff | ready_debt | inflation_cpi | regressor | 1,458 | 0.0482 | 0.0564 | -0.0177 | 0.0331 | 0.723 |
| ready_no_lag_debt_cutoff | ready_debt | reserves | regressor | 1,458 | 0.0451 | 0.1146 | 2.41e-06 | 0.0146 | 1.5271 |
| ready_no_lag_debt_cutoff | ready_debt | tt | regressor | 1,458 | 1.0091 | 0.1831 | 0.3188 | 0.9945 | 2.7308 |
| ready_no_lag_debt_cutoff | ready_debt | interest_revenue | construction_input | 1,458 | 0.0857 | 0.0979 | -0.069 | 0.0567 | 0.7987 |
| ready_no_lag_debt_cutoff | ready_debt | theta_hat_A | construction_input | 1,458 | 0.0596 | 0.7019 | -0.8062 | -0.1453 | 3.3491 |

## 4. 缺失、重复键与 Within 变异

三个估计阶段均对国家—年份键执行 fail-closed 唯一性检查；不会自动去重。每个方程在估计前锁定全控制样本，五种判据进一步共用同一债务样本。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 (%) | 独占损失 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 497 | 27.2 | 319 |
| baseline | — | vulnerability100 | 58 | 3.17 | 0 |
| baseline | — | readiness100 | 58 | 3.17 | 0 |
| baseline | — | ln_debt | 103 | 5.64 | 11 |
| baseline | — | growth | 5 | 0.27 | 0 |
| baseline | — | ln_capitagdp | 4 | 0.22 | 0 |
| baseline | — | inflation_cpi | 7 | 0.38 | 1 |
| baseline | — | reserves | 70 | 3.83 | 3 |
| baseline | — | tt | 222 | 12.15 | 90 |
| output | — | Y_outcome | 64 | 3.5 | 60 |
| output | — | readiness100 | 58 | 3.17 | 0 |
| output | — | vulnerability100 | 58 | 3.17 | 0 |
| output | — | Y_lag | 2 | 0.11 | 0 |
| output | — | growth | 5 | 0.27 | 0 |
| output | — | ln_capitagdp | 4 | 0.22 | 0 |
| output | — | inflation_cpi | 7 | 0.38 | 2 |
| output | — | reserves | 70 | 3.83 | 28 |
| output | — | tt | 222 | 12.15 | 180 |
| doomloop | debt | b_outcome | 166 | 9.09 | 60 |
| doomloop | debt | readiness100 | 58 | 3.17 | 0 |
| doomloop | debt | theta_hat_A | 150 | 8.21 | 0 |
| doomloop | debt | ln_debt | 103 | 5.64 | 0 |
| doomloop | debt | mA_hat | 150 | 8.21 | 0 |
| doomloop | debt | YA_hat | 58 | 3.17 | 0 |
| doomloop | debt | ln_debt_mA_hat | 150 | 8.21 | 0 |
| doomloop | debt | vulnerability100 | 58 | 3.17 | 0 |
| doomloop | debt | growth | 5 | 0.27 | 0 |
| doomloop | debt | ln_capitagdp | 4 | 0.22 | 0 |
| doomloop | debt | inflation_cpi | 7 | 0.38 | 2 |
| doomloop | debt | reserves | 70 | 3.83 | 26 |
| doomloop | debt | tt | 222 | 12.15 | 148 |
| doomloop | ready | A_outcome | 58 | 3.17 | 0 |
| doomloop | ready | interest_revenue | 141 | 7.72 | 35 |
| doomloop | ready | theta_hat_A | 150 | 8.21 | 13 |
| doomloop | ready | vulnerability100 | 58 | 3.17 | 0 |
| doomloop | ready | growth | 5 | 0.27 | 0 |
| doomloop | ready | ln_capitagdp | 4 | 0.22 | 0 |
| doomloop | ready | inflation_cpi | 7 | 0.38 | 2 |
| doomloop | ready | reserves | 70 | 3.83 | 27 |
| doomloop | ready | tt | 222 | 12.15 | 145 |

### 4.2 Within 变异

| 板块 | 方程 | 变量 | 总体 SD | Within SD | Within/总体 | FE 识别 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | — | year | 8.3689 | 8.3689 | 1 | adequate |
| baseline | — | bond_spreads | 0.0428 | 0.0174 | 0.406 | adequate |
| baseline | — | bond_10y | 0.0426 | 0.0224 | 0.5248 | adequate |
| baseline | — | vulnerability100 | 0.079 | 0.0105 | 0.1327 | adequate |
| baseline | — | readiness100 | 0.1452 | 0.0434 | 0.2986 | adequate |
| baseline | — | lnrgdp | 2.735 | 0.308 | 0.1126 | adequate |
| baseline | — | growth | 0.0353 | 0.0317 | 0.8996 | adequate |
| baseline | — | inflation_cpi | 0.1074 | 0.0925 | 0.8612 | adequate |
| baseline | — | debt_gdp | 0.3489 | 0.1833 | 0.5253 | adequate |
| baseline | — | PrimaryBalance_gdp | 0.0342 | 0.0292 | 0.8537 | adequate |
| baseline | — | reserves | 0.1262 | 0.0709 | 0.562 | adequate |
| baseline | — | gee | 0.9129 | 0.1927 | 0.2111 | adequate |
| baseline | — | rqe | 0.8587 | 0.1822 | 0.2122 | adequate |
| baseline | — | tt | 0.1859 | 0.165 | 0.8875 | adequate |
| baseline | — | is_advanced | 0.5001 | 0 | 0 | not_identified_by_FE |
| baseline | — | Revenue_gdp | 0.1298 | 0.0241 | 0.1855 | adequate |
| baseline | — | CurrentGDP | 1.37e+06 | 880947.5 | 0.6414 | adequate |
| baseline | — | ConstantGDP | 1.04e+06 | 395694.13 | 0.3792 | adequate |
| baseline | — | capitaGDP | 23153.4351 | 6876.271 | 0.297 | adequate |
| baseline | — | OverallBalance_gdp | 0.0396 | 0.0292 | 0.7377 | adequate |
| baseline | — | revenue | 220774.6148 | 135491.17 | 0.6137 | adequate |
| baseline | — | debt | 519926.9195 | 304445.22 | 0.5856 | adequate |
| baseline | — | interest_revenue | 0.0959 | 0.0468 | 0.488 | adequate |
| baseline | — | taxgdp | 8.1057 | 1.6723 | 0.2063 | adequate |
| baseline | — | ln_capitagdp | 0.9494 | 0.2338 | 0.2463 | adequate |
| baseline | — | ln_debt | 2.761 | 0.7881 | 0.2854 | adequate |
| output | — | Y_outcome | 2.7943 | 0.6701 | 0.2398 | adequate |
| output | — | Y_lag | 2.7888 | 0.6834 | 0.2451 | adequate |
| output | — | readiness100 | 0.1465 | 0.0403 | 0.2749 | adequate |
| output | — | vulnerability100 | 0.0797 | 0.0101 | 0.1267 | adequate |
| output | — | growth | 0.036 | 0.0317 | 0.8822 | adequate |
| output | — | ln_capitagdp | 0.9683 | 0.2103 | 0.2171 | adequate |
| output | — | inflation_cpi | 0.0732 | 0.0561 | 0.7659 | adequate |
| output | — | reserves | 0.1321 | 0.0611 | 0.4628 | adequate |
| output | — | tt | 0.1878 | 0.167 | 0.8892 | adequate |
| doomloop | debt | b_outcome | 0.1129 | 0.1045 | 0.9255 | adequate |
| doomloop | debt | theta_hat_A | 0.6879 | 0.2267 | 0.3296 | adequate |
| doomloop | debt | ln_debt | 2.7322 | 0.7447 | 0.2726 | adequate |
| doomloop | debt | mA_hat | 0.0815 | 0.026 | 0.3197 | adequate |
| doomloop | debt | YA_hat | 0.0066 | 0.0008 | 0.1253 | adequate |
| doomloop | debt | ln_debt_mA_hat | 0.6889 | 0.2273 | 0.33 | adequate |
| doomloop | debt | readiness100 | 0.1462 | 0.0403 | 0.2756 | adequate |
| doomloop | debt | vulnerability100 | 0.0786 | 0.0099 | 0.1253 | adequate |
| doomloop | debt | growth | 0.0361 | 0.0319 | 0.8821 | adequate |
| doomloop | debt | ln_capitagdp | 0.9492 | 0.2034 | 0.2143 | adequate |
| doomloop | debt | inflation_cpi | 0.0542 | 0.0416 | 0.7676 | adequate |
| doomloop | debt | reserves | 0.1342 | 0.0617 | 0.46 | adequate |
| doomloop | debt | tt | 0.1826 | 0.1609 | 0.8807 | adequate |
| doomloop | ready | A_outcome | 0.1442 | 0.0389 | 0.2696 | adequate |
| doomloop | ready | theta_hat_A | 0.7019 | 0.239 | 0.3405 | adequate |
| doomloop | ready | interest_revenue | 0.0979 | 0.0455 | 0.4646 | adequate |
| doomloop | ready | vulnerability100 | 0.0792 | 0.0102 | 0.1284 | adequate |
| doomloop | ready | growth | 0.0355 | 0.0312 | 0.8803 | adequate |
| doomloop | ready | ln_capitagdp | 0.9372 | 0.2067 | 0.2205 | adequate |
| doomloop | ready | inflation_cpi | 0.0564 | 0.0434 | 0.7693 | adequate |
| doomloop | ready | reserves | 0.1146 | 0.0599 | 0.5229 | adequate |
| doomloop | ready | tt | 0.1831 | 0.1615 | 0.8821 | adequate |

## 5. 共线性、相关性与系数变化

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline | vulnerability100 | 1.2912 | 0.7744 | 1.8791 |
| baseline | readiness100 | 1.0701 | 0.9345 | 1.8791 |
| baseline | ln_debt | 1.4073 | 0.7106 | 1.8791 |
| baseline | growth | 1.0859 | 0.9209 | 1.8791 |
| baseline | ln_capitagdp | 1.3121 | 0.7622 | 1.8791 |
| baseline | inflation_cpi | 1.0749 | 0.9303 | 1.8791 |
| baseline | reserves | 1.1178 | 0.8947 | 1.8791 |
| baseline | tt | 1.0505 | 0.9519 | 1.8791 |
| output | readiness100 | 1.1545 | 0.8662 | 2.4157 |
| output | vulnerability100 | 1.1745 | 0.8514 | 2.4157 |
| output | Y_lag | 1.8781 | 0.5324 | 2.4157 |
| output | growth | 1.0274 | 0.9733 | 2.4157 |
| output | ln_capitagdp | 1.5741 | 0.6353 | 2.4157 |
| output | inflation_cpi | 1.1715 | 0.8536 | 2.4157 |
| output | reserves | 1.033 | 0.968 | 2.4157 |
| output | tt | 1.0698 | 0.9348 | 2.4157 |
| output | c_A_Y | 1.2494 | 0.8004 | 2.6034 |
| output | c_X_Y | 1.278 | 0.7825 | 2.6034 |
| output | int_AX_Y | 1.2427 | 0.8047 | 2.6034 |
| output | Y_lag | 1.9596 | 0.5103 | 2.6034 |
| output | growth | 1.0319 | 0.9691 | 2.6034 |
| output | ln_capitagdp | 1.5801 | 0.6329 | 2.6034 |
| output | inflation_cpi | 1.1787 | 0.8484 | 2.6034 |
| output | reserves | 1.0404 | 0.9612 | 2.6034 |
| output | tt | 1.0711 | 0.9336 | 2.6034 |


绝对相关系数不低于 0.60 的非重复变量对：

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |
| baseline | vulnerability100 | readiness100 | -0.7606 |
| baseline | vulnerability100 | ln_capitagdp | -0.8685 |
| baseline | readiness100 | ln_capitagdp | 0.8597 |
| output | readiness100 | vulnerability100 | -0.7766 |
| output | readiness100 | ln_capitagdp | 0.8596 |
| output | vulnerability100 | ln_capitagdp | -0.8925 |

## 6. 统计与程序验证

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | F | 分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 26.5739 | 2 | 1,080 | <0.001 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 50.6915 | 1 | 1,080 | <0.001 |
| baseline | Interact_AX | c_A = int_AX = 0 | 1.6158 | 2 | 1,080 | 0.199 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 1.5435 | 1 | 1,080 | 0.214 |
| baseline | Interact_all | c_A = int_AB = 0 | 31.0958 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AX = 0 | 5.3272 | 2 | 1,079 | 0.005 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 20.8455 | 3 | 1,079 | <0.001 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 30.2475 | 2 | 1,079 | <0.001 |
| output | Y5_macro | inflation control zero | 81.7532 | 1 | 1,392 | <0.001 |
| output | Y7_layer2_A | external controls jointly zero | 5.0865 | 2 | 1,390 | 0.006 |
| output | Y7_layer2_A | all controls jointly zero | 31.0378 | 3 | 1,390 | <0.001 |
| output | Y8_interact_core | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 1.6932 | 2 | 1,392 | 0.184 |
| output | Y8_interact_core | interaction zero: int_AX_Y = 0 | 2.8516 | 1 | 1,392 | 0.092 |
| output | Y9_interact_macro | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 0.4237 | 2 | 1,391 | 0.655 |
| output | Y9_interact_macro | interaction zero: int_AX_Y = 0 | 0.1508 | 1 | 1,391 | 0.698 |
| output | Y10_interact_full | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 0.3169 | 2 | 1,389 | 0.728 |
| output | Y10_interact_full | interaction zero: int_AX_Y = 0 | 0.0627 | 1 | 1,389 | 0.802 |
| output | Y9_interact_macro | inflation control zero | 80.0572 | 1 | 1,391 | <0.001 |
| output | Y10_interact_full | external controls jointly zero | 4.9817 | 2 | 1,389 | 0.007 |
| output | Y10_interact_full | all controls jointly zero | 30.4732 | 3 | 1,389 | <0.001 |
| doomloop | DN3_full | low- and high-branch coefficients jointly zero | 11.3252 | 2 | 1,338 | <0.001 |
| doomloop | DN3_full | macro controls jointly zero | 4.6438 | 1 | 1,338 | 0.031 |
| doomloop | DN3_full | external controls jointly zero | 1.6266 | 2 | 1,338 | 0.197 |
| doomloop | DN3_full | all controls jointly zero | 1.8935 | 3 | 1,338 | 0.129 |
| doomloop | RDN3_full | branches jointly zero; debt-equation cutoff | 51.9117 | 2 | 1,363 | <0.001 |
| doomloop | RDN3_full | macro controls jointly zero | 0.5231 | 1 | 1,363 | 0.470 |
| doomloop | RDN3_full | external controls jointly zero | 10.2363 | 2 | 1,363 | <0.001 |
| doomloop | RDN3_full | all controls jointly zero | 6.9629 | 3 | 1,363 | <0.001 |

### 6.2 代数、映射与 hinge 公式

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | Y(t+1) equals exact F.ln_currentgdp | 0 | 1.00e-12 | 通过 |
| theta | Y(t) equals current ln_currentgdp | 0 | 1.00e-12 | 通过 |
| theta | b_it equals ln_debt exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 8.33e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw output formula | 6.94e-18 | 1.00e-12 | 通过 |
| theta | stored versus predictnl output margin | 0 | 1.00e-12 | 通过 |
| theta | theta component identity | 0 | 1.00e-12 | 通过 |
| doomloop | theta uses ln_debt*mA_hat + YA_hat | 0 | 1.00e-10 | 通过 |
| doomloop | b_it maps exactly to ln_debt | 0 | 1.00e-10 | 通过 |
| doomloop | criterion theta low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion theta high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion mA low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion mA high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion YA low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion YA high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b*mA low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b*mA high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | main debt low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | main debt high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | readiness debt-cutoff low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | readiness debt-cutoff high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | readiness cutoff equals debt cutoff | 0 | 1.00e-12 | 通过 |

### 6.3 areg 与显式 LSDV

| 板块 | 模型/判据 | 变量 | areg | LSDV | \|系数差\| | \|SE差\| |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Layer2_A | vulnerability100 | 0.0928 | 0.0928 | 2.29e-15 | 2.35e-13 |
| baseline | Layer2_A | readiness100 | -0.0221 | -0.0221 | 9.86e-15 | 1.36e-15 |
| baseline | Layer2_A | ln_debt | 0.0207 | 0.0207 | 2.12e-15 | 1.68e-15 |
| baseline | Layer2_A | growth | -0.179 | -0.179 | 9.94e-15 | 2.43e-16 |
| baseline | Layer2_A | ln_capitagdp | -0.0321 | -0.0321 | 1.02e-14 | 1.70e-14 |
| baseline | Layer2_A | inflation_cpi | 0.1501 | 0.1501 | 4.86e-15 | 8.67e-16 |
| baseline | Layer2_A | reserves | 0.019 | 0.019 | 1.03e-15 | 1.41e-15 |
| baseline | Layer2_A | tt | -0.0051 | -0.0051 | 2.87e-15 | 3.56e-16 |
| baseline | Interact_all | c_A | 0.0093 | 0.0093 | 6.79e-15 | 2.88e-15 |
| baseline | Interact_all | c_X | 0.2756 | 0.2756 | 8.87e-14 | 9.27e-15 |
| baseline | Interact_all | c_b | 0.0182 | 0.0182 | 3.04e-15 | 4.38e-16 |
| baseline | Interact_all | int_AB | -0.0299 | -0.0299 | 1.49e-15 | 6.42e-17 |
| baseline | Interact_all | int_AX | 0.5014 | 0.5014 | 1.33e-13 | 2.60e-14 |
| baseline | Interact_all | growth | -0.1793 | -0.1793 | 1.11e-14 | 2.01e-16 |
| baseline | Interact_all | ln_capitagdp | -0.0319 | -0.0319 | 1.05e-14 | 9.47e-15 |
| baseline | Interact_all | inflation_cpi | 0.1413 | 0.1413 | 7.74e-15 | 3.96e-16 |
| baseline | Interact_all | reserves | 0.0222 | 0.0222 | 4.06e-15 | 3.30e-17 |
| baseline | Interact_all | tt | -0.0068 | -0.0068 | 3.08e-15 | 8.23e-16 |
| tax | Spread_Interact_all | c_A | 0.0093 | 0.0093 | 4.65e-15 | 2.84e-15 |
| tax | Spread_Interact_all | c_X | 0.2756 | 0.2756 | 9.25e-14 | 1.65e-14 |
| tax | Spread_Interact_all | c_b | 0.0182 | 0.0182 | 3.17e-15 | 1.38e-15 |
| tax | Spread_Interact_all | int_AB | -0.0299 | -0.0299 | 9.99e-16 | 6.11e-17 |
| tax | Spread_Interact_all | int_AX | 0.5014 | 0.5014 | 1.14e-13 | 2.28e-14 |
| tax | Spread_Interact_all | growth | -0.1793 | -0.1793 | 1.07e-14 | 1.23e-15 |
| tax | Spread_Interact_all | ln_capitagdp | -0.0319 | -0.0319 | 9.16e-15 | 2.16e-14 |
| tax | Spread_Interact_all | inflation_cpi | 0.1413 | 0.1413 | 7.74e-15 | 3.47e-16 |
| tax | Spread_Interact_all | reserves | 0.0222 | 0.0222 | 4.48e-15 | 2.16e-16 |
| tax | Spread_Interact_all | tt | -0.0068 | -0.0068 | 2.90e-15 | 5.17e-16 |
| tax | Y7_layer2_A | vulnerability100 | -0.0252 | -0.0252 | 3.68e-13 | 5.39e-13 |
| tax | Y7_layer2_A | readiness100 | 0.0256 | 0.0256 | 5.01e-15 | 3.05e-14 |
| tax | Y7_layer2_A | Y_lag | 0.986 | 0.986 | 5.11e-15 | 7.38e-15 |
| tax | Y7_layer2_A | growth | 0.4142 | 0.4142 | 8.77e-15 | 1.76e-15 |
| tax | Y7_layer2_A | ln_capitagdp | -0.0153 | -0.0153 | 2.83e-14 | 2.80e-14 |
| tax | Y7_layer2_A | inflation_cpi | 0.4427 | 0.4427 | 3.77e-14 | 7.45e-15 |
| tax | Y7_layer2_A | reserves | 0.0033 | 0.0033 | 1.04e-14 | 1.95e-15 |
| tax | Y7_layer2_A | tt | -0.0258 | -0.0258 | 1.33e-14 | 5.03e-16 |
| tax | Y10_interact_full | c_A_Y | 0.0231 | 0.0231 | 1.29e-14 | 1.26e-14 |
| tax | Y10_interact_full | c_X_Y | -0.0135 | -0.0135 | 1.11e-13 | 6.11e-15 |
| tax | Y10_interact_full | int_AX_Y | 0.0841 | 0.0841 | 2.04e-13 | 3.14e-14 |
| tax | Y10_interact_full | Y_lag | 0.9858 | 0.9858 | 4.44e-15 | 6.49e-15 |
| tax | Y10_interact_full | growth | 0.4135 | 0.4135 | 1.57e-14 | 1.11e-15 |
| tax | Y10_interact_full | ln_capitagdp | -0.0151 | -0.0151 | 3.69e-14 | 5.26e-14 |
| tax | Y10_interact_full | inflation_cpi | 0.4422 | 0.4422 | 3.48e-14 | 5.17e-15 |
| tax | Y10_interact_full | reserves | 0.0037 | 0.0037 | 7.17e-15 | 7.98e-17 |
| tax | Y10_interact_full | tt | -0.0258 | -0.0258 | 1.16e-14 | 5.69e-16 |
| doomloop | theta | beta_L | 0.0435 | 0.0435 | 6.41e-14 | 1.49e-14 |
| doomloop | theta | beta_H | -0.1348 | -0.1348 | 2.88e-14 | 1.13e-14 |
| doomloop | b | beta_L | 0.1278 | 0.1278 | 5.97e-15 | 6.94e-18 |
| doomloop | b | beta_H | -0.0875 | -0.0875 | 1.13e-14 | 2.75e-15 |
| doomloop | mA | beta_L | 3.5038 | 3.5038 | 7.21e-13 | 9.93e-14 |
| doomloop | mA | beta_H | -3.1833 | -3.1833 | 4.70e-13 | 1.39e-14 |
| doomloop | YA | beta_L | -5.1039 | -5.1039 | 4.72e-12 | 7.26e-12 |
| doomloop | YA | beta_H | -54.7681 | -54.7681 | 5.39e-12 | 2.97e-11 |
| doomloop | b*mA | beta_L | 0.0407 | 0.0407 | 6.20e-14 | 1.69e-14 |
| doomloop | b*mA | beta_H | -0.1346 | -0.1346 | 2.60e-14 | 2.55e-14 |
| doomloop | readiness | delta_L | 0.5041 | 0.5041 | 2.66e-15 | 3.68e-15 |
| doomloop | readiness | delta_H | -0.1984 | -0.1984 | 4.44e-16 | 3.05e-16 |

### 6.4 Cutoff 最小 RSS 与样本加总

| Criterion | 记录 cutoff | 最小 RSS | cutoff RSS | \|差值\| | N | N_low | N_high | 加总 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | -0.2934 | 12.703639 | 12.703639 | 0 | 1,433 | 494 | 939 | 通过 | 通过 |
| $b_{it}$ | 7.8993 | 12.420159 | 12.420159 | 0 | 1,433 | 938 | 495 | 通过 | 通过 |
| $\widehat m^A_{it}$ | -0.0214 | 12.46224 | 12.46224 | 0 | 1,433 | 775 | 658 | 通过 | 通过 |
| $\widehat Y^A_{it}$ | 0.0323 | 12.805001 | 12.805001 | 0 | 1,433 | 1,252 | 181 | 通过 | 通过 |
| $b_{it}\widehat m^A_{it}$ | -0.3167 | 12.70325 | 12.70325 | 0 | 1,433 | 490 | 943 | 通过 | 通过 |

Readiness cutoff 继承检查：

| 方程 | cutoff 来源 | cutoff | 债务 profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| debt | debt_full | -0.2934 | 12.7036 | 12.7036 | 0 | 通过 |
| ready_debt | debt_full | -0.2934 | 12.7036 | 12.7036 | 0 | 通过 |

### 6.5 五判据共同样本与拟合排序

| RSS 排名 | Criterion | N | RSS | Within R2 | 理论方向 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | $b_{it}$ | 1,433 | 12.420159 | 0.205 | Match (+,-) |
| 2 | $\widehat m^A_{it}$ | 1,433 | 12.462241 | 0.2023 | Match (+,-) |
| 3 | $b_{it}\widehat m^A_{it}$ | 1,433 | 12.70325 | 0.1869 | Match (+,-) |
| 4 | $\widehat\theta^A_{it}$ | 1,433 | 12.703639 | 0.1869 | Match (+,-) |
| 5 | $\widehat Y^A_{it}$ | 1,433 | 12.805001 | 0.1804 | Partial (-,-) |

## 7. 图形 QA

| 图形 | 字节 | 状态 |
| --- | ---: | ---: |
| debt_marginal_effect_no_b.png | 178,879 | 通过 |
| debt_marginal_effect_no_b.pdf | 73,709 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.png | 173,355 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.pdf | 71,683 | 通过 |
| kink_marginal_effects_no_state.png | 224,878 | 通过 |
| kink_marginal_effects_no_state.pdf | 79,453 | 通过 |

债务图和 readiness 图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0。Readiness 图的竖直线来自债务全控制方程。

## 8. Required Caveats for Stakeholders

- 当前 `vce(robust)` 处理异方差，但不处理同一国家内序列相关。
- theta 是两条上游回归的生成变量；cutoff 又在同一样本中搜索，常规 p 值没有覆盖联合不确定性。
- 比较五种判据会引入模型选择和多重比较问题；最低 RSS 仅代表本样本内拟合。
- 固定效应相关性结果不支持因果措辞。

## 9. 原始输出索引

完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。
