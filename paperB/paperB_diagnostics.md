# Paper B：统计检验与数据检查

> 生成时间：2026-08-07 23:57（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。

## 1. Validation Report

### Overall Assessment: Share with caveats

单位换算检查通过 28/28 项；代数、映射与 hinge 检查通过 25/25 项；cutoff 最小 RSS 及继承关系检查通过 7/7 项。计算实现和样本内比较已通过，但国家内相关、theta 生成误差、cutoff 搜索和多判据选择不确定性尚未由联合推断覆盖。

### Methodology Review

主流程准确对应 workflow：一期债务变化、去债务状态控制、readiness 水平去滞后状态控制，readiness 固定使用债务全控制 theta cutoff。五种阈值判据使用同一个债务全控制样本、因变量、控制变量、固定效应和误差口径，因此 RSS 与 Within R² 可比较。

### Issues Found

1. **[Medium] 推断未覆盖 cutoff 搜索和上游生成误差。** 当前 p 值是固定 cutoff 条件下的异方差稳健 p 值。
2. **[Medium] 标准误未处理国家内序列相关。** 面板推断应补充国家聚类及完整管线 bootstrap。
3. **[Low] 竞争判据为样本内拟合比较。** 最低 RSS 不等于统计上显著优于其他非嵌套判据。

## 2. 数据来源、单位与时序

唯一原始分析输入是 `data0804/invest_panel_weo.csv`。源百分数、比率和 0—100 指数先除以 100；金额变量不缩放。`ln_currentgdp` 只进入 baseline。Doomloop 从 empirical-theta panel 读取已换算变量，并单独将源 `interest_revenue` 除以 100。

- $T_{i,t+1}=taxgdp_{i,t+1}\times0.01$，$T_{it}=taxgdp_{it}\times0.01$。
- $\Delta b_{i,t+1}=F.debt\_gdp_{it}-debt\_gdp_{it}$，严格要求相邻年份。
- $A_{it}=readiness100_{it}$；readiness 方程不使用滞后状态项。

### 2.1 Doomloop 源字段换算

| 变量 | 源最小值 | 源最大值 | 比率最小值 | 比率最大值 | 最大误差 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| interest_revenue | -14.8211 | 79.8698 | -0.1482 | 0.7987 | 0 | 通过 |

## 3. 固定样本与描述统计

| 固定样本 | N | 国家数 | 年份数 | 年份范围 |
| --- | ---: | ---: | ---: | ---: |
| Baseline 全交互 | 1,174 | 60 | 26 | 1998–2023 |
| Tax 全控制交互 | 1,414 | 60 | 28 | 1995–2022 |
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
| debt_gdp | 1,724 | 0.5774 | 0.3489 | 0.0005 | 0.5117 | 2.6096 |
| reserves | 1,757 | 0.0531 | 0.1262 | 1.31e-06 | 0.017 | 1.5271 |
| tt | 1,605 | 1.0069 | 0.1859 | 0.3188 | 0.9942 | 2.7308 |
| ln_currentgdp | 1,825 | 7.9058 | 2.7744 | 1.1909 | 7.5496 | 16.8549 |

### 3.2 Tax 与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| taxbase_lead | tax | 1,414 | 0.2053 | 0.0804 | 0.0213 | 0.1974 | 0.4977 |
| taxbase_lag | tax | 1,414 | 0.2052 | 0.0806 | 0.0213 | 0.1971 | 0.4977 |
| mA_hat_spread_ratio | theta_support | 1,103 | 0.0714 | 0.0675 | -0.0387 | 0.0557 | 0.3886 |
| mA_hat | theta_support | 1,103 | 0.0714 | 0.0675 | -0.0387 | 0.0557 | 0.3886 |
| spread_saving_component | theta_support | 1,103 | 0.0681 | 0.1111 | -0.0029 | 0.0301 | 0.8891 |
| TA_hat | theta_support | 1,103 | -0.0331 | 0.0179 | -0.0616 | -0.0378 | 0.0173 |
| theta_hat_A | theta_support | 1,103 | 0.035 | 0.1112 | -0.0617 | 0.0041 | 0.8572 |
| theta_hat_A | all_constructible | 1,677 | 0.032 | 0.1068 | -0.0617 | 0.0044 | 1.1823 |

### 3.3 Doomloop 主规格与判据变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_no_b | debt | b_outcome | dependent_variable | 1,433 | 0.0077 | 0.0635 | -0.5417 | 0.0019 | 0.4186 |
| debt_no_b | debt | debt_kink_low | regressor | 1,433 | 0.0213 | 0.0203 | 0 | 0.017 | 0.0831 |
| debt_no_b | debt | debt_kink_high | regressor | 1,433 | 0.0152 | 0.0549 | 0 | 0 | 0.5541 |
| debt_no_b | debt | vulnerability100 | regressor | 1,433 | 0.3827 | 0.0786 | 0.251 | 0.3684 | 0.5808 |
| debt_no_b | debt | growth | regressor | 1,433 | 0.0338 | 0.0361 | -0.1455 | 0.0344 | 0.2462 |
| debt_no_b | debt | inflation_cpi | regressor | 1,433 | 0.0462 | 0.0542 | -0.0177 | 0.0314 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,433 | 0.0546 | 0.1342 | 2.41e-06 | 0.0151 | 1.5271 |
| debt_no_b | debt | tt | regressor | 1,433 | 1.0089 | 0.1826 | 0.3188 | 0.9942 | 2.7308 |
| debt_no_b | debt | readiness100 | construction_input | 1,433 | 0.5057 | 0.1462 | 0.2021 | 0.4994 | 0.8072 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,433 | 0.0325 | 0.1084 | -0.0617 | 0.0045 | 1.1823 |
| debt_no_b | debt | debt_gdp | construction_input | 1,433 | 0.5824 | 0.3516 | 0.039 | 0.5064 | 2.6096 |
| debt_no_b | debt | mA_hat | construction_input | 1,433 | 0.0652 | 0.0665 | -0.039 | 0.0518 | 0.4531 |
| debt_no_b | debt | TA_hat | construction_input | 1,433 | -0.0289 | 0.0195 | -0.0616 | -0.0324 | 0.0203 |
| debt_no_b | debt | bmA_hat | construction_input | 1,433 | 0.0613 | 0.1084 | -0.0029 | 0.0263 | 1.1824 |
| ready_no_lag_debt_cutoff | ready_debt | A_outcome | dependent_variable | 1,458 | 0.5029 | 0.1442 | 0.2021 | 0.4965 | 0.7973 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 1,458 | 0.0018 | 0.0025 | -0.0055 | 0.0014 | 0.0175 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 1,458 | 0.0026 | 0.0091 | -0.0023 | 0 | 0.138 |
| ready_no_lag_debt_cutoff | ready_debt | vulnerability100 | regressor | 1,458 | 0.3817 | 0.0792 | 0.251 | 0.3673 | 0.5808 |
| ready_no_lag_debt_cutoff | ready_debt | growth | regressor | 1,458 | 0.0331 | 0.0355 | -0.1455 | 0.0332 | 0.2462 |
| ready_no_lag_debt_cutoff | ready_debt | inflation_cpi | regressor | 1,458 | 0.0482 | 0.0564 | -0.0177 | 0.0331 | 0.723 |
| ready_no_lag_debt_cutoff | ready_debt | reserves | regressor | 1,458 | 0.0451 | 0.1146 | 2.41e-06 | 0.0146 | 1.5271 |
| ready_no_lag_debt_cutoff | ready_debt | tt | regressor | 1,458 | 1.0091 | 0.1831 | 0.3188 | 0.9945 | 2.7308 |
| ready_no_lag_debt_cutoff | ready_debt | interest_revenue | construction_input | 1,458 | 0.0857 | 0.0979 | -0.069 | 0.0567 | 0.7987 |
| ready_no_lag_debt_cutoff | ready_debt | theta_hat_A | construction_input | 1,458 | 0.0315 | 0.1092 | -0.0617 | 0.0041 | 1.1823 |

## 4. 缺失、重复键与 Within 变异

三个估计阶段均对国家—年份键执行 fail-closed 唯一性检查；不会自动去重。每个方程在估计前锁定全控制样本，五种判据进一步共用同一债务样本。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 (%) | 独占损失 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 497 | 27.2 | 319 |
| baseline | — | vulnerability100 | 58 | 3.17 | 0 |
| baseline | — | readiness100 | 58 | 3.17 | 0 |
| baseline | — | debt_gdp | 103 | 5.64 | 11 |
| baseline | — | growth | 5 | 0.27 | 0 |
| baseline | — | ln_currentgdp | 2 | 0.11 | 0 |
| baseline | — | inflation_cpi | 7 | 0.38 | 1 |
| baseline | — | reserves | 70 | 3.83 | 3 |
| baseline | — | tt | 222 | 12.15 | 90 |
| tax | — | taxbase_lead | 192 | 10.51 | 60 |
| tax | — | readiness100 | 58 | 3.17 | 0 |
| tax | — | vulnerability100 | 58 | 3.17 | 0 |
| tax | — | taxbase_lag | 147 | 8.05 | 11 |
| tax | — | growth | 5 | 0.27 | 0 |
| tax | — | inflation_cpi | 7 | 0.38 | 1 |
| tax | — | reserves | 70 | 3.83 | 20 |
| tax | — | tt | 222 | 12.15 | 152 |
| doomloop | debt | b_outcome | 166 | 9.09 | 60 |
| doomloop | debt | readiness100 | 58 | 3.17 | 0 |
| doomloop | debt | theta_hat_A | 150 | 8.21 | 0 |
| doomloop | debt | debt_gdp | 103 | 5.64 | 0 |
| doomloop | debt | mA_hat | 150 | 8.21 | 0 |
| doomloop | debt | TA_hat | 58 | 3.17 | 0 |
| doomloop | debt | bmA_hat | 150 | 8.21 | 0 |
| doomloop | debt | vulnerability100 | 58 | 3.17 | 0 |
| doomloop | debt | growth | 5 | 0.27 | 0 |
| doomloop | debt | inflation_cpi | 7 | 0.38 | 2 |
| doomloop | debt | reserves | 70 | 3.83 | 26 |
| doomloop | debt | tt | 222 | 12.15 | 148 |
| doomloop | ready | A_outcome | 58 | 3.17 | 0 |
| doomloop | ready | interest_revenue | 141 | 7.72 | 35 |
| doomloop | ready | theta_hat_A | 150 | 8.21 | 13 |
| doomloop | ready | vulnerability100 | 58 | 3.17 | 0 |
| doomloop | ready | growth | 5 | 0.27 | 0 |
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
| baseline | — | OverallBalance_gdp | 0.0396 | 0.0292 | 0.7377 | adequate |
| baseline | — | revenue | 220774.6148 | 135491.17 | 0.6137 | adequate |
| baseline | — | debt | 519926.9195 | 304445.22 | 0.5856 | adequate |
| baseline | — | interest_revenue | 0.0959 | 0.0468 | 0.488 | adequate |
| baseline | — | taxgdp | 8.1057 | 1.6723 | 0.2063 | adequate |
| baseline | — | ln_currentgdp | 2.7744 | 0.7588 | 0.2735 | adequate |
| tax | — | taxbase_lead | 0.0804 | 0.0162 | 0.2011 | adequate |
| tax | — | taxbase_lag | 0.0806 | 0.0163 | 0.202 | adequate |
| tax | — | readiness100 | 0.1456 | 0.0402 | 0.2761 | adequate |
| tax | — | vulnerability100 | 0.0798 | 0.0096 | 0.1204 | adequate |
| tax | — | growth | 0.0362 | 0.0318 | 0.8794 | adequate |
| tax | — | inflation_cpi | 0.0525 | 0.0399 | 0.7606 | adequate |
| tax | — | reserves | 0.1348 | 0.0606 | 0.4495 | adequate |
| tax | — | tt | 0.1853 | 0.1593 | 0.8598 | adequate |
| doomloop | debt | b_outcome | 0.0635 | 0.062 | 0.9756 | adequate |
| doomloop | debt | theta_hat_A | 0.1084 | 0.0595 | 0.549 | adequate |
| doomloop | debt | debt_gdp | 0.3516 | 0.1708 | 0.4857 | adequate |
| doomloop | debt | mA_hat | 0.0665 | 0.0324 | 0.4867 | adequate |
| doomloop | debt | TA_hat | 0.0195 | 0.0024 | 0.1253 | adequate |
| doomloop | debt | bmA_hat | 0.1084 | 0.0597 | 0.551 | adequate |
| doomloop | debt | readiness100 | 0.1462 | 0.0403 | 0.2756 | adequate |
| doomloop | debt | vulnerability100 | 0.0786 | 0.0099 | 0.1253 | adequate |
| doomloop | debt | growth | 0.0361 | 0.0319 | 0.8821 | adequate |
| doomloop | debt | inflation_cpi | 0.0542 | 0.0416 | 0.7676 | adequate |
| doomloop | debt | reserves | 0.1342 | 0.0617 | 0.46 | adequate |
| doomloop | debt | tt | 0.1826 | 0.1609 | 0.8807 | adequate |
| doomloop | ready | A_outcome | 0.1442 | 0.0389 | 0.2696 | adequate |
| doomloop | ready | theta_hat_A | 0.1092 | 0.0589 | 0.5395 | adequate |
| doomloop | ready | interest_revenue | 0.0979 | 0.0455 | 0.4646 | adequate |
| doomloop | ready | vulnerability100 | 0.0792 | 0.0102 | 0.1284 | adequate |
| doomloop | ready | growth | 0.0355 | 0.0312 | 0.8803 | adequate |
| doomloop | ready | inflation_cpi | 0.0564 | 0.0434 | 0.7693 | adequate |
| doomloop | ready | reserves | 0.1146 | 0.0599 | 0.5229 | adequate |
| doomloop | ready | tt | 0.1831 | 0.1615 | 0.8821 | adequate |

## 5. 共线性、相关性与系数变化

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline | vulnerability100 | 1.3369 | 0.748 | 2.0172 |
| baseline | readiness100 | 1.0124 | 0.9877 | 2.0172 |
| baseline | debt_gdp | 1.1541 | 0.8665 | 2.0172 |
| baseline | growth | 1.0695 | 0.935 | 2.0172 |
| baseline | ln_currentgdp | 1.5266 | 0.6551 | 2.0172 |
| baseline | inflation_cpi | 1.1238 | 0.8899 | 2.0172 |
| baseline | reserves | 1.1182 | 0.8943 | 2.0172 |
| baseline | tt | 1.0467 | 0.9554 | 2.0172 |
| tax | readiness100 | 1.0424 | 0.9593 | 1.3021 |
| tax | vulnerability100 | 1.0402 | 0.9613 | 1.3021 |
| tax | taxbase_lag | 1.0244 | 0.9762 | 1.3021 |
| tax | growth | 1.0256 | 0.975 | 1.3021 |
| tax | inflation_cpi | 1.0299 | 0.971 | 1.3021 |
| tax | reserves | 1.0132 | 0.987 | 1.3021 |
| tax | tt | 1.0231 | 0.9774 | 1.3021 |
| tax | c_A_T | 1.1419 | 0.8757 | 1.6539 |
| tax | c_X_T | 1.1746 | 0.8514 | 1.6539 |
| tax | int_AX_T | 1.2409 | 0.8059 | 1.6539 |
| tax | taxbase_lag | 1.0612 | 0.9423 | 1.6539 |
| tax | growth | 1.0261 | 0.9746 | 1.6539 |
| tax | inflation_cpi | 1.0299 | 0.971 | 1.6539 |
| tax | reserves | 1.0298 | 0.9711 | 1.6539 |
| tax | tt | 1.0248 | 0.9758 | 1.6539 |


绝对相关系数不低于 0.60 的非重复变量对：

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |
| baseline | vulnerability100 | readiness100 | -0.7606 |
| tax | readiness100 | vulnerability100 | -0.777 |
| tax | readiness100 | taxbase_lag | 0.63 |
| tax | vulnerability100 | taxbase_lag | -0.655 |

## 6. 统计与程序验证

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | F | 分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 21.8427 | 2 | 1,080 | <0.001 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 39.4341 | 1 | 1,080 | <0.001 |
| baseline | Interact_AX | c_A = int_AX = 0 | 5.6693 | 2 | 1,080 | 0.004 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 0.0121 | 1 | 1,080 | 0.913 |
| baseline | Interact_all | c_A = int_AB = 0 | 21.086 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AX = 0 | 8.9191 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 14.7463 | 3 | 1,079 | <0.001 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 20.1624 | 2 | 1,079 | <0.001 |
| tax | T5_macro | macro controls jointly zero | 0.8499 | 2 | 1,322 | 0.428 |
| tax | T7_layer2_A | external controls jointly zero | 1.6829 | 2 | 1,320 | 0.186 |
| tax | T7_layer2_A | all controls jointly zero | 1.1519 | 4 | 1,320 | 0.331 |
| tax | T8_interact_core | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 7.7369 | 2 | 1,323 | <0.001 |
| tax | T8_interact_core | interaction zero: int_AX_T = 0 | 12.5998 | 1 | 1,323 | <0.001 |
| tax | T9_interact_macro | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 7.6724 | 2 | 1,321 | <0.001 |
| tax | T9_interact_macro | interaction zero: int_AX_T = 0 | 12.381 | 1 | 1,321 | <0.001 |
| tax | T10_interact_full | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 7.6885 | 2 | 1,319 | <0.001 |
| tax | T10_interact_full | interaction zero: int_AX_T = 0 | 11.73 | 1 | 1,319 | <0.001 |
| tax | T9_interact_macro | macro controls jointly zero | 0.8084 | 2 | 1,321 | 0.446 |
| tax | T10_interact_full | external controls jointly zero | 1.4747 | 2 | 1,319 | 0.229 |
| tax | T10_interact_full | all controls jointly zero | 1.0431 | 4 | 1,319 | 0.384 |
| doomloop | DN3_full | low- and high-branch coefficients jointly zero | 18.5938 | 2 | 1,339 | <0.001 |
| doomloop | DN3_full | macro controls jointly zero | 19.0266 | 2 | 1,339 | <0.001 |
| doomloop | DN3_full | external controls jointly zero | 1.7787 | 2 | 1,339 | 0.169 |
| doomloop | DN3_full | all controls jointly zero | 10.7751 | 4 | 1,339 | <0.001 |
| doomloop | RDN3_full | branches jointly zero; debt-equation cutoff | 32.8502 | 2 | 1,364 | <0.001 |
| doomloop | RDN3_full | macro controls jointly zero | 0.3692 | 2 | 1,364 | 0.691 |
| doomloop | RDN3_full | external controls jointly zero | 5.6052 | 2 | 1,364 | 0.004 |
| doomloop | RDN3_full | all controls jointly zero | 2.9773 | 4 | 1,364 | 0.018 |

### 6.2 代数、映射与 hinge 公式

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | T(t+1) equals exact F.taxgdp ratio | 0 | 1.00e-12 | 通过 |
| theta | T(t) equals current taxgdp ratio | 0 | 1.00e-12 | 通过 |
| theta | b_it equals debt_gdp exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 5.55e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw tax formula | 1.73e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl tax margin | 0 | 1.00e-12 | 通过 |
| theta | theta component identity | 0 | 1.00e-12 | 通过 |
| doomloop | theta uses debt_gdp*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop | b_it maps exactly to debt_gdp | 0 | 1.00e-10 | 通过 |
| doomloop | criterion theta low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion theta high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion b high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion mA low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion mA high hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion TA low hinge | 0 | 1.00e-10 | 通过 |
| doomloop | criterion TA high hinge | 0 | 1.00e-10 | 通过 |
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
| baseline | Layer2_A | vulnerability100 | 0.2263 | 0.2263 | 1.21e-13 | 3.90e-13 |
| baseline | Layer2_A | readiness100 | -0.0539 | -0.0539 | 1.38e-15 | 5.07e-15 |
| baseline | Layer2_A | debt_gdp | 0.0515 | 0.0515 | 3.09e-15 | 1.03e-15 |
| baseline | Layer2_A | growth | -0.1814 | -0.1814 | 5.33e-15 | 4.86e-17 |
| baseline | Layer2_A | ln_currentgdp | 0.0217 | 0.0217 | 5.47e-15 | 1.04e-14 |
| baseline | Layer2_A | inflation_cpi | 0.149 | 0.149 | 1.14e-14 | 4.34e-15 |
| baseline | Layer2_A | reserves | 0.0241 | 0.0241 | 6.28e-15 | 1.27e-14 |
| baseline | Layer2_A | tt | 0.0005 | 0.0005 | 2.33e-15 | 3.90e-17 |
| baseline | Interact_all | c_A | -0.072 | -0.072 | 2.35e-15 | 3.85e-16 |
| baseline | Interact_all | c_X | 0.2486 | 0.2486 | 1.29e-13 | 1.56e-14 |
| baseline | Interact_all | c_b | 0.0556 | 0.0556 | 2.49e-15 | 1.65e-17 |
| baseline | Interact_all | int_AB | -0.1898 | -0.1898 | 1.04e-14 | 3.47e-18 |
| baseline | Interact_all | int_AX | -0.0261 | -0.0261 | 2.31e-14 | 4.11e-15 |
| baseline | Interact_all | growth | -0.1649 | -0.1649 | 3.58e-15 | 2.78e-17 |
| baseline | Interact_all | ln_currentgdp | 0.0175 | 0.0175 | 5.19e-15 | 3.40e-16 |
| baseline | Interact_all | inflation_cpi | 0.1567 | 0.1567 | 1.14e-14 | 7.15e-16 |
| baseline | Interact_all | reserves | 0.027 | 0.027 | 5.87e-15 | 3.37e-16 |
| baseline | Interact_all | tt | -0.0031 | -0.0031 | 1.86e-15 | 5.72e-17 |
| tax | Spread_Interact_all | c_A | -0.072 | -0.072 | 1.03e-15 | 1.70e-16 |
| tax | Spread_Interact_all | c_X | 0.2486 | 0.2486 | 1.65e-13 | 3.55e-15 |
| tax | Spread_Interact_all | c_b | 0.0556 | 0.0556 | 3.03e-15 | 9.02e-17 |
| tax | Spread_Interact_all | int_AB | -0.1898 | -0.1898 | 9.85e-15 | 2.29e-16 |
| tax | Spread_Interact_all | int_AX | -0.0261 | -0.0261 | 2.73e-14 | 6.52e-15 |
| tax | Spread_Interact_all | growth | -0.1649 | -0.1649 | 4.52e-15 | 2.08e-16 |
| tax | Spread_Interact_all | ln_currentgdp | 0.0175 | 0.0175 | 5.70e-15 | 2.44e-15 |
| tax | Spread_Interact_all | inflation_cpi | 0.1567 | 0.1567 | 1.28e-14 | 1.17e-15 |
| tax | Spread_Interact_all | reserves | 0.027 | 0.027 | 6.54e-15 | 9.94e-16 |
| tax | Spread_Interact_all | tt | -0.0031 | -0.0031 | 1.85e-15 | 1.13e-16 |
| tax | T7_layer2_A | vulnerability100 | 0.0484 | 0.0484 | 8.08e-15 | 1.79e-14 |
| tax | T7_layer2_A | readiness100 | -0.0215 | -0.0215 | 1.11e-14 | 8.53e-16 |
| tax | T7_layer2_A | taxbase_lag | 0.7371 | 0.7371 | 1.23e-14 | 4.86e-16 |
| tax | T7_layer2_A | growth | 0.0156 | 0.0156 | 1.40e-15 | 7.98e-17 |
| tax | T7_layer2_A | inflation_cpi | -0.0036 | -0.0036 | 9.60e-16 | 2.69e-17 |
| tax | T7_layer2_A | reserves | -0.0005 | -0.0005 | 4.02e-16 | 6.03e-17 |
| tax | T7_layer2_A | tt | -0.0031 | -0.0031 | 2.21e-16 | 1.04e-16 |
| tax | T10_interact_full | c_A_T | -0.0289 | -0.0289 | 1.15e-14 | 1.60e-16 |
| tax | T10_interact_full | c_X_T | 0.0887 | 0.0887 | 1.72e-14 | 2.84e-15 |
| tax | T10_interact_full | int_AX_T | 0.2483 | 0.2483 | 5.32e-14 | 5.69e-15 |
| tax | T10_interact_full | taxbase_lag | 0.7278 | 0.7278 | 1.40e-14 | 2.35e-15 |
| tax | T10_interact_full | growth | 0.0149 | 0.0149 | 1.54e-15 | 4.34e-17 |
| tax | T10_interact_full | inflation_cpi | -0.0036 | -0.0036 | 1.23e-15 | 9.71e-17 |
| tax | T10_interact_full | reserves | 0.0012 | 0.0012 | 6.14e-16 | 2.65e-17 |
| tax | T10_interact_full | tt | -0.0029 | -0.0029 | 2.31e-16 | 3.23e-17 |
| doomloop | theta | beta_L | 0.8282 | 0.8282 | 2.44e-14 | 1.35e-14 |
| doomloop | theta | beta_H | -0.4726 | -0.4726 | 1.11e-15 | 1.19e-15 |
| doomloop | b | beta_L | 0.1328 | 0.1328 | 1.44e-15 | 5.90e-16 |
| doomloop | b | beta_H | -0.2206 | -0.2206 | 5.66e-15 | 8.19e-16 |
| doomloop | mA | beta_L | 0.6867 | 0.6867 | 2.45e-14 | 6.77e-15 |
| doomloop | mA | beta_H | -1.1716 | -1.1716 | 1.44e-14 | 3.77e-15 |
| doomloop | TA | beta_L | -13.1903 | -13.1903 | 5.66e-12 | 9.41e-13 |
| doomloop | TA | beta_H | -1.7281 | -1.7281 | 1.24e-12 | 1.28e-12 |
| doomloop | b*mA | beta_L | 5.948 | 5.948 | 4.71e-14 | 1.40e-14 |
| doomloop | b*mA | beta_H | -0.5096 | -0.5096 | 5.55e-16 | 8.05e-16 |
| doomloop | readiness | delta_L | -5.6355 | -5.6355 | 2.09e-13 | 1.83e-14 |
| doomloop | readiness | delta_H | 0.0806 | 0.0806 | 3.57e-15 | 1.60e-15 |

### 6.4 Cutoff 最小 RSS 与样本加总

| Criterion | 记录 cutoff | 最小 RSS | cutoff RSS | \|差值\| | N | N_low | N_high | 加总 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | 0.0455 | 3.59077 | 3.59077 | 0 | 1,433 | 1,080 | 353 | 通过 | 通过 |
| $b_{it}$ | 0.6661 | 3.57392 | 3.57392 | 0 | 1,433 | 966 | 467 | 通过 | 通过 |
| $\widehat m^A_{it}$ | 0.0813 | 3.572821 | 3.572821 | 0 | 1,433 | 974 | 459 | 通过 | 通过 |
| $\widehat T^A_{it}$ | -0.039 | 3.829212 | 3.829212 | 0 | 1,433 | 549 | 884 | 通过 | 通过 |
| $b_{it}\widehat m^A_{it}$ | 0.0064 | 3.565086 | 3.565086 | 0 | 1,433 | 327 | 1,106 | 通过 | 通过 |

Readiness cutoff 继承检查：

| 方程 | cutoff 来源 | cutoff | 债务 profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| debt | debt_full | 0.0455 | 3.5908 | 3.5908 | 0 | 通过 |
| ready_debt | debt_full | 0.0455 | 3.5908 | 3.5908 | 0 | 通过 |

### 6.5 五判据共同样本与拟合排序

| RSS 排名 | Criterion | N | RSS | Within R2 | 理论方向 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | $b_{it}\widehat m^A_{it}$ | 1,433 | 3.565086 | 0.3519 | Match (+,-) |
| 2 | $\widehat m^A_{it}$ | 1,433 | 3.572821 | 0.3505 | Match (+,-) |
| 3 | $b_{it}$ | 1,433 | 3.573919 | 0.3503 | Match (+,-) |
| 4 | $\widehat\theta^A_{it}$ | 1,433 | 3.59077 | 0.3472 | Match (+,-) |
| 5 | $\widehat T^A_{it}$ | 1,433 | 3.829212 | 0.3039 | Partial (-,-) |

## 7. 图形 QA

| 图形 | 字节 | 状态 |
| --- | ---: | ---: |
| debt_marginal_effect_no_b.png | 181,057 | 通过 |
| debt_marginal_effect_no_b.pdf | 74,010 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.png | 181,375 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.pdf | 72,518 | 通过 |
| kink_marginal_effects_no_state.png | 230,358 | 通过 |
| kink_marginal_effects_no_state.pdf | 80,841 | 通过 |

债务图和 readiness 图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0。Readiness 图的竖直线来自债务全控制方程。

## 8. Required Caveats for Stakeholders

- 当前 `vce(robust)` 处理异方差，但不处理同一国家内序列相关。
- theta 是两条上游回归的生成变量；cutoff 又在同一样本中搜索，常规 p 值没有覆盖联合不确定性。
- 比较五种判据会引入模型选择和多重比较问题；最低 RSS 仅代表本样本内拟合。
- 固定效应相关性结果不支持因果措辞。

## 9. 原始输出索引

完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。
