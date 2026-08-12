# Paper B：统计检验与数据检查

> 生成时间：2026-08-12 17:30（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。

## 1. Validation Report

### Overall Assessment: Share with caveats

单位换算检查通过 27/27 项；代数、映射与 hinge 检查通过 26/26 项；cutoff 最小 RSS 及继承关系检查通过 7/7 项。计算实现和样本内比较已通过，但国家内相关、theta 生成误差、cutoff 搜索和多判据选择不确定性尚未由联合推断覆盖。

### Methodology Review

主流程准确对应 workflow：一期债务变化、去债务状态控制、readiness 当期一阶差分且右侧不含滞后状态控制，readiness 固定使用债务全控制 theta cutoff。五种阈值判据使用同一个债务全控制样本、因变量、控制变量、固定效应和误差口径，因此 RSS 与 Within R² 可比较。

### Issues Found

1. **[Medium] 推断未覆盖 cutoff 搜索和上游生成误差。** 当前 p 值是固定 cutoff 条件下的异方差稳健 p 值。
2. **[Medium] 标准误未处理国家内序列相关。** 面板推断应补充国家聚类及完整管线 bootstrap。
3. **[Low] 竞争判据为样本内拟合比较。** 最低 RSS 不等于统计上显著优于其他非嵌套判据。

## 2. 数据来源、单位与时序

唯一原始分析输入是 `data0804/invest_panel_weo.csv`。源百分数、比率和 0—100 指数先除以 100；金额变量不缩放。主流程构造 `ln_constantgdp=ln(ConstantGDP)` 与 `ln_debt=ln(debt)`；所有回归控制 growth 和 ln_constantgdp。产出模型含 Y_lag 时，Y_lag 本身就是 ln_constantgdp，因此只保留一次。Doomloop 从 empirical-theta panel 读取构造量，并单独将源 `interest_revenue` 除以 100。

- $Y_{it}=\ln(ConstantGDP_{it})$，$Y_{i,t+1}=F.\ln(ConstantGDP_{it})$。
- $\Delta\ln(debt)_{i,t+1}=F.\ln(debt_{it})-\ln(debt_{it})$，严格要求相邻年份。
- Readiness 因变量为 $A_{it}-A_{i,t-1}$；$A_{i,t-1}$ 只用于构造差分，不作为右侧状态控制。

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
| Doomloop Readiness | 1,448 | 59 | 28 | 1996–2023 |

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
| ln_constantgdp | 1,825 | 8.1897 | 2.735 | 2.9628 | 7.8151 | 16.3252 |
| ln_debt | 1,724 | 7.2075 | 2.761 | 0.4055 | 7.0078 | 15.9286 |

### 3.2 Y 与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Y_outcome | output | 1,485 | 8.2572 | 2.7671 | 3.2544 | 7.827 | 16.3252 |
| Y_lag | output | 1,485 | 8.2253 | 2.7623 | 3.1901 | 7.8116 | 16.276 |
| mA_hat_spread_ratio | theta_support | 1,114 | -0.0001 | 0.0762 | -0.2013 | -0.0058 | 0.2235 |
| mA_hat | theta_support | 1,114 | -0.0001 | 0.0762 | -0.2013 | -0.0058 | 0.2235 |
| ln_debt_mA_hat | theta_support | 1,114 | 0.1838 | 0.7451 | -0.7392 | -0.0488 | 3.548 |
| spread_saving_component | theta_support | 1,114 | 0.1838 | 0.7451 | -0.7392 | -0.0488 | 3.548 |
| YA_hat | theta_support | 1,114 | -0.0224 | 0.025 | -0.0624 | -0.0291 | 0.048 |
| theta_hat_A | theta_support | 1,114 | 0.1614 | 0.7466 | -0.7054 | -0.063 | 3.5475 |
| theta_hat_A | all_constructible | 1,677 | 0.0691 | 0.7178 | -0.7564 | -0.1494 | 3.5717 |

### 3.3 Doomloop 主规格与判据变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_no_b | debt | b_outcome | dependent_variable | 1,433 | 0.0915 | 0.1129 | -0.8964 | 0.0765 | 1.2158 |
| debt_no_b | debt | debt_kink_low | regressor | 1,433 | 0.1732 | 0.139 | 0 | 0.1726 | 0.5104 |
| debt_no_b | debt | debt_kink_high | regressor | 1,433 | 0.1035 | 0.3049 | 0 | 0 | 1.8475 |
| debt_no_b | debt | vulnerability100 | regressor | 1,433 | 0.3827 | 0.0786 | 0.251 | 0.3684 | 0.5808 |
| debt_no_b | debt | growth | regressor | 1,433 | 0.0338 | 0.0361 | -0.1455 | 0.0344 | 0.2462 |
| debt_no_b | debt | ln_constantgdp | regressor | 1,433 | 8.248 | 2.785 | 3.1901 | 7.8017 | 16.276 |
| debt_no_b | debt | inflation_cpi | regressor | 1,433 | 0.0462 | 0.0542 | -0.0177 | 0.0314 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,433 | 0.0546 | 0.1342 | 2.41e-06 | 0.0151 | 1.5271 |
| debt_no_b | debt | tt | regressor | 1,433 | 1.0089 | 0.1826 | 0.3188 | 0.9942 | 2.7308 |
| debt_no_b | debt | readiness100 | construction_input | 1,433 | 0.5057 | 0.1462 | 0.2021 | 0.4994 | 0.8072 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,433 | 0.0749 | 0.7273 | -0.7564 | -0.1418 | 3.5475 |
| debt_no_b | debt | ln_debt | construction_input | 1,433 | 7.3136 | 2.7322 | 0.9462 | 7.1055 | 15.8777 |
| debt_no_b | debt | mA_hat | construction_input | 1,433 | -0.015 | 0.0837 | -0.2722 | -0.017 | 0.2235 |
| debt_no_b | debt | YA_hat | construction_input | 1,433 | -0.0166 | 0.0273 | -0.0624 | -0.0216 | 0.0522 |
| debt_no_b | debt | ln_debt_mA_hat | construction_input | 1,433 | 0.0916 | 0.7305 | -0.7981 | -0.1147 | 3.548 |
| ready_no_lag_debt_cutoff | ready_debt | A_outcome | dependent_variable | 1,448 | 0.0025 | 0.0179 | -0.22 | 0.002 | 0.0803 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 1,448 | 0.0353 | 0.0556 | -0.013 | 0.013 | 0.4159 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 1,448 | 0.0117 | 0.0454 | -0.0792 | 0 | 0.5092 |
| ready_no_lag_debt_cutoff | ready_debt | vulnerability100 | regressor | 1,448 | 0.3812 | 0.0791 | 0.251 | 0.3671 | 0.5808 |
| ready_no_lag_debt_cutoff | ready_debt | growth | regressor | 1,448 | 0.033 | 0.0353 | -0.1455 | 0.0331 | 0.2462 |
| ready_no_lag_debt_cutoff | ready_debt | ln_constantgdp | regressor | 1,448 | 8.3086 | 2.7973 | 3.1901 | 7.838 | 16.3252 |
| ready_no_lag_debt_cutoff | ready_debt | inflation_cpi | regressor | 1,448 | 0.048 | 0.0564 | -0.0177 | 0.0329 | 0.723 |
| ready_no_lag_debt_cutoff | ready_debt | reserves | regressor | 1,448 | 0.0454 | 0.115 | 2.41e-06 | 0.015 | 1.5271 |
| ready_no_lag_debt_cutoff | ready_debt | tt | regressor | 1,448 | 1.008 | 0.1759 | 0.3188 | 0.9945 | 2.7308 |
| ready_no_lag_debt_cutoff | ready_debt | interest_revenue | construction_input | 1,448 | 0.0852 | 0.0977 | -0.069 | 0.0567 | 0.7987 |
| ready_no_lag_debt_cutoff | ready_debt | theta_hat_A | construction_input | 1,448 | 0.1021 | 0.7431 | -0.7564 | -0.1215 | 3.5717 |

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
| baseline | — | ln_constantgdp | 2 | 0.11 | 0 |
| baseline | — | inflation_cpi | 7 | 0.38 | 1 |
| baseline | — | reserves | 70 | 3.83 | 3 |
| baseline | — | tt | 222 | 12.15 | 90 |
| output | — | Y_outcome | 64 | 3.5 | 60 |
| output | — | readiness100 | 58 | 3.17 | 0 |
| output | — | vulnerability100 | 58 | 3.17 | 0 |
| output | — | Y_lag | 2 | 0.11 | 0 |
| output | — | growth | 5 | 0.27 | 0 |
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
| doomloop | debt | ln_constantgdp | 2 | 0.11 | 0 |
| doomloop | debt | inflation_cpi | 7 | 0.38 | 2 |
| doomloop | debt | reserves | 70 | 3.83 | 26 |
| doomloop | debt | tt | 222 | 12.15 | 148 |
| doomloop | ready | A_outcome | 119 | 6.51 | 10 |
| doomloop | ready | interest_revenue | 141 | 7.72 | 34 |
| doomloop | ready | theta_hat_A | 150 | 8.21 | 9 |
| doomloop | ready | vulnerability100 | 58 | 3.17 | 0 |
| doomloop | ready | growth | 5 | 0.27 | 0 |
| doomloop | ready | ln_constantgdp | 2 | 0.11 | 0 |
| doomloop | ready | inflation_cpi | 7 | 0.38 | 1 |
| doomloop | ready | reserves | 70 | 3.83 | 27 |
| doomloop | ready | tt | 222 | 12.15 | 120 |

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
| baseline | — | ln_constantgdp | 2.735 | 0.308 | 0.1126 | adequate |
| baseline | — | ln_debt | 2.761 | 0.7881 | 0.2854 | adequate |
| output | — | Y_outcome | 2.7671 | 0.2825 | 0.1021 | adequate |
| output | — | Y_lag | 2.7623 | 0.2868 | 0.1038 | adequate |
| output | — | ln_constantgdp | 2.7623 | 0.2868 | 0.1038 | adequate |
| output | — | readiness100 | 0.1465 | 0.0403 | 0.2749 | adequate |
| output | — | vulnerability100 | 0.0797 | 0.0101 | 0.1267 | adequate |
| output | — | growth | 0.036 | 0.0317 | 0.8822 | adequate |
| output | — | inflation_cpi | 0.0732 | 0.0561 | 0.7659 | adequate |
| output | — | reserves | 0.1321 | 0.0611 | 0.4628 | adequate |
| output | — | tt | 0.1878 | 0.167 | 0.8892 | adequate |
| doomloop | debt | b_outcome | 0.1129 | 0.1045 | 0.9255 | adequate |
| doomloop | debt | theta_hat_A | 0.7273 | 0.2375 | 0.3266 | adequate |
| doomloop | debt | ln_debt | 2.7322 | 0.7447 | 0.2726 | adequate |
| doomloop | debt | mA_hat | 0.0837 | 0.0268 | 0.3199 | adequate |
| doomloop | debt | YA_hat | 0.0273 | 0.0034 | 0.1253 | adequate |
| doomloop | debt | ln_debt_mA_hat | 0.7305 | 0.2398 | 0.3283 | adequate |
| doomloop | debt | readiness100 | 0.1462 | 0.0403 | 0.2756 | adequate |
| doomloop | debt | vulnerability100 | 0.0786 | 0.0099 | 0.1253 | adequate |
| doomloop | debt | growth | 0.0361 | 0.0319 | 0.8821 | adequate |
| doomloop | debt | ln_constantgdp | 2.785 | 0.2727 | 0.0979 | adequate |
| doomloop | debt | inflation_cpi | 0.0542 | 0.0416 | 0.7676 | adequate |
| doomloop | debt | reserves | 0.1342 | 0.0617 | 0.46 | adequate |
| doomloop | debt | tt | 0.1826 | 0.1609 | 0.8807 | adequate |
| doomloop | ready | A_outcome | 0.0179 | 0.0178 | 0.9934 | adequate |
| doomloop | ready | theta_hat_A | 0.7431 | 0.2471 | 0.3326 | adequate |
| doomloop | ready | interest_revenue | 0.0977 | 0.0452 | 0.4629 | adequate |
| doomloop | ready | vulnerability100 | 0.0791 | 0.0101 | 0.1275 | adequate |
| doomloop | ready | growth | 0.0353 | 0.0311 | 0.8813 | adequate |
| doomloop | ready | ln_constantgdp | 2.7973 | 0.2694 | 0.0963 | adequate |
| doomloop | ready | inflation_cpi | 0.0564 | 0.0433 | 0.7675 | adequate |
| doomloop | ready | reserves | 0.115 | 0.0601 | 0.523 | adequate |
| doomloop | ready | tt | 0.1759 | 0.1567 | 0.891 | adequate |

## 5. 共线性、相关性与系数变化

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline | vulnerability100 | 1.3337 | 0.7498 | 2.0361 |
| baseline | readiness100 | 1.0402 | 0.9613 | 2.0361 |
| baseline | ln_debt | 1.5182 | 0.6587 | 2.0361 |
| baseline | growth | 1.0872 | 0.9198 | 2.0361 |
| baseline | ln_constantgdp | 1.4555 | 0.687 | 2.0361 |
| baseline | inflation_cpi | 1.0754 | 0.9299 | 2.0361 |
| baseline | reserves | 1.112 | 0.8993 | 2.0361 |
| baseline | tt | 1.0371 | 0.9642 | 2.0361 |
| output | readiness100 | 1.035 | 0.9661 | 1.5903 |
| output | vulnerability100 | 1.2076 | 0.8281 | 1.5903 |
| output | Y_lag | 1.1704 | 0.8544 | 1.5903 |
| output | growth | 1.0168 | 0.9834 | 1.5903 |
| output | inflation_cpi | 1.0304 | 0.9705 | 1.5903 |
| output | reserves | 1.0253 | 0.9754 | 1.5903 |
| output | tt | 1.0235 | 0.9771 | 1.5903 |
| output | c_A_Y | 1.0967 | 0.9118 | 1.7973 |
| output | c_X_Y | 1.3146 | 0.7607 | 1.7973 |
| output | int_AX_Y | 1.2084 | 0.8276 | 1.7973 |
| output | Y_lag | 1.1917 | 0.8391 | 1.7973 |
| output | growth | 1.0184 | 0.9819 | 1.7973 |
| output | inflation_cpi | 1.0304 | 0.9705 | 1.7973 |
| output | reserves | 1.0342 | 0.9669 | 1.7973 |
| output | tt | 1.0235 | 0.977 | 1.7973 |


绝对相关系数不低于 0.60 的非重复变量对：

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |
| baseline | vulnerability100 | readiness100 | -0.7606 |
| baseline | ln_debt | ln_constantgdp | 0.9611 |
| output | readiness100 | vulnerability100 | -0.7766 |

## 6. 统计与程序验证

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | F | 分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 27.4176 | 2 | 1,080 | <0.001 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 48.8692 | 1 | 1,080 | <0.001 |
| baseline | Interact_AX | c_A = int_AX = 0 | 2.87 | 2 | 1,080 | 0.057 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 1.7339 | 1 | 1,080 | 0.188 |
| baseline | Interact_all | c_A = int_AB = 0 | 31.3862 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AX = 0 | 5.1236 | 2 | 1,079 | 0.006 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 20.9345 | 3 | 1,079 | <0.001 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 28.7765 | 2 | 1,079 | <0.001 |
| output | Y5_macro | inflation control zero | 0.6859 | 1 | 1,393 | 0.408 |
| output | Y7_layer2_A | external controls jointly zero | 0.5643 | 2 | 1,391 | 0.569 |
| output | Y7_layer2_A | all controls jointly zero | 0.5556 | 3 | 1,391 | 0.644 |
| output | Y8_interact_core | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 1.9293 | 2 | 1,393 | 0.146 |
| output | Y8_interact_core | interaction zero: int_AX_Y = 0 | 3.8023 | 1 | 1,393 | 0.051 |
| output | Y9_interact_macro | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 1.9423 | 2 | 1,392 | 0.144 |
| output | Y9_interact_macro | interaction zero: int_AX_Y = 0 | 3.794 | 1 | 1,392 | 0.052 |
| output | Y10_interact_full | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 2.1029 | 2 | 1,390 | 0.122 |
| output | Y10_interact_full | interaction zero: int_AX_Y = 0 | 4.0181 | 1 | 1,390 | 0.045 |
| output | Y9_interact_macro | inflation control zero | 0.6777 | 1 | 1,392 | 0.411 |
| output | Y10_interact_full | external controls jointly zero | 0.7921 | 2 | 1,390 | 0.453 |
| output | Y10_interact_full | all controls jointly zero | 0.6953 | 3 | 1,390 | 0.555 |
| doomloop | DN3_full | low- and high-branch coefficients jointly zero | 12.6149 | 2 | 1,338 | <0.001 |
| doomloop | DN3_full | macro controls jointly zero | 4.5234 | 1 | 1,338 | 0.034 |
| doomloop | DN3_full | external controls jointly zero | 1.2964 | 2 | 1,338 | 0.274 |
| doomloop | DN3_full | all controls jointly zero | 1.7125 | 3 | 1,338 | 0.163 |
| doomloop | RDN3_full | branches jointly zero; debt-equation cutoff | 0.3797 | 2 | 1,354 | 0.684 |
| doomloop | RDN3_full | macro controls jointly zero | 0.0468 | 1 | 1,354 | 0.829 |
| doomloop | RDN3_full | external controls jointly zero | 0.8632 | 2 | 1,354 | 0.422 |
| doomloop | RDN3_full | all controls jointly zero | 0.6047 | 3 | 1,354 | 0.612 |

### 6.2 代数、映射与 hinge 公式

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | Y(t+1) equals exact F.ln_constantgdp | 0 | 1.00e-12 | 通过 |
| theta | Y(t) equals current ln_constantgdp | 0 | 1.00e-12 | 通过 |
| theta | b_it equals ln_debt exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 6.94e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw output formula | 3.47e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl output margin | 0 | 1.00e-12 | 通过 |
| theta | theta component identity | 0 | 1.00e-12 | 通过 |
| doomloop | theta uses ln_debt*mA_hat + YA_hat | 0 | 1.00e-10 | 通过 |
| doomloop | b_it maps exactly to ln_debt | 0 | 1.00e-10 | 通过 |
| doomloop | readiness outcome is exact one-year change | 0 | 1.00e-12 | 通过 |
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
| baseline | Layer2_A | vulnerability100 | 0.1057 | 0.1057 | 1.59e-14 | 6.09e-13 |
| baseline | Layer2_A | readiness100 | -0.034 | -0.034 | 3.09e-15 | 3.29e-15 |
| baseline | Layer2_A | ln_debt | 0.0208 | 0.0208 | 9.75e-16 | 1.67e-16 |
| baseline | Layer2_A | growth | -0.1829 | -0.1829 | 1.42e-15 | 5.34e-16 |
| baseline | Layer2_A | ln_constantgdp | -0.022 | -0.022 | 6.19e-15 | 2.43e-15 |
| baseline | Layer2_A | inflation_cpi | 0.1496 | 0.1496 | 1.19e-15 | 4.48e-16 |
| baseline | Layer2_A | reserves | 0.0218 | 0.0218 | 1.15e-15 | 4.05e-15 |
| baseline | Layer2_A | tt | -0.0028 | -0.0028 | 6.42e-16 | 6.55e-16 |
| baseline | Interact_all | c_A | -0.0013 | -0.0013 | 4.77e-15 | 1.84e-16 |
| baseline | Interact_all | c_X | 0.2873 | 0.2873 | 6.07e-14 | 3.33e-15 |
| baseline | Interact_all | c_b | 0.0184 | 0.0184 | 7.36e-16 | 1.33e-15 |
| baseline | Interact_all | int_AB | -0.0307 | -0.0307 | 3.40e-16 | 6.94e-17 |
| baseline | Interact_all | int_AX | 0.5224 | 0.5224 | 2.82e-14 | 4.43e-14 |
| baseline | Interact_all | growth | -0.1824 | -0.1824 | 1.22e-15 | 8.81e-16 |
| baseline | Interact_all | ln_constantgdp | -0.0232 | -0.0232 | 7.12e-15 | 2.48e-14 |
| baseline | Interact_all | inflation_cpi | 0.1405 | 0.1405 | 2.50e-15 | 4.30e-16 |
| baseline | Interact_all | reserves | 0.0251 | 0.0251 | 2.28e-15 | 4.60e-17 |
| baseline | Interact_all | tt | -0.0047 | -0.0047 | 6.90e-16 | 6.57e-16 |
| tax | Spread_Interact_all | c_A | -0.0013 | -0.0013 | 2.00e-15 | 2.36e-16 |
| tax | Spread_Interact_all | c_X | 0.2873 | 0.2873 | 5.30e-14 | 5.16e-15 |
| tax | Spread_Interact_all | c_b | 0.0184 | 0.0184 | 3.92e-16 | 7.55e-16 |
| tax | Spread_Interact_all | int_AB | -0.0307 | -0.0307 | 6.49e-16 | 3.82e-17 |
| tax | Spread_Interact_all | int_AX | 0.5224 | 0.5224 | 3.80e-14 | 9.30e-15 |
| tax | Spread_Interact_all | growth | -0.1824 | -0.1824 | 1.67e-16 | 8.05e-16 |
| tax | Spread_Interact_all | ln_constantgdp | -0.0232 | -0.0232 | 5.18e-15 | 2.16e-14 |
| tax | Spread_Interact_all | inflation_cpi | 0.1405 | 0.1405 | 2.64e-15 | 2.29e-16 |
| tax | Spread_Interact_all | reserves | 0.0251 | 0.0251 | 2.49e-15 | 8.33e-17 |
| tax | Spread_Interact_all | tt | -0.0047 | -0.0047 | 8.83e-16 | 8.55e-16 |
| tax | Y7_layer2_A | vulnerability100 | -0.0617 | -0.0617 | 6.04e-12 | 1.90e-13 |
| tax | Y7_layer2_A | readiness100 | -0.0076 | -0.0076 | 1.18e-13 | 1.60e-15 |
| tax | Y7_layer2_A | Y_lag | 0.9703 | 0.9703 | 7.67e-13 | 2.89e-14 |
| tax | Y7_layer2_A | growth | 0.2547 | 0.2547 | 2.72e-13 | 5.90e-15 |
| tax | Y7_layer2_A | inflation_cpi | -0.0148 | -0.0148 | 1.09e-13 | 2.48e-15 |
| tax | Y7_layer2_A | reserves | 0.0057 | 0.0057 | 1.98e-13 | 1.81e-15 |
| tax | Y7_layer2_A | tt | -0.003 | -0.003 | 8.60e-15 | 2.32e-16 |
| tax | Y10_interact_full | c_A_Y | -0.0158 | -0.0158 | 1.63e-14 | 3.68e-15 |
| tax | Y10_interact_full | c_X_Y | -0.0121 | -0.0121 | 5.29e-12 | 1.08e-13 |
| tax | Y10_interact_full | int_AX_Y | 0.3475 | 0.3475 | 4.40e-12 | 6.36e-14 |
| tax | Y10_interact_full | Y_lag | 0.9691 | 0.9691 | 7.64e-13 | 1.22e-14 |
| tax | Y10_interact_full | growth | 0.2529 | 0.2529 | 2.41e-13 | 4.54e-15 |
| tax | Y10_interact_full | inflation_cpi | -0.0147 | -0.0147 | 1.06e-13 | 3.21e-15 |
| tax | Y10_interact_full | reserves | 0.0074 | 0.0074 | 1.72e-13 | 4.25e-17 |
| tax | Y10_interact_full | tt | -0.003 | -0.003 | 8.26e-15 | 5.82e-16 |
| doomloop | theta | beta_L | 0.259 | 0.259 | 2.65e-14 | 1.13e-14 |
| doomloop | theta | beta_H | -0.1376 | -0.1376 | 9.83e-15 | 2.40e-15 |
| doomloop | b | beta_L | 0.136 | 0.136 | 4.72e-14 | 7.79e-15 |
| doomloop | b | beta_H | -0.1027 | -0.1027 | 3.10e-14 | 1.79e-15 |
| doomloop | mA | beta_L | 3.8777 | 3.8777 | 1.15e-12 | 1.94e-13 |
| doomloop | mA | beta_H | -3.375 | -3.375 | 7.78e-13 | 1.59e-13 |
| doomloop | YA | beta_L | -9.2442 | -9.2442 | 5.75e-12 | 6.89e-12 |
| doomloop | YA | beta_H | -2.0236 | -2.0236 | 3.47e-13 | 4.15e-12 |
| doomloop | b*mA | beta_L | 0.2497 | 0.2497 | 2.36e-15 | 1.15e-14 |
| doomloop | b*mA | beta_H | -0.1371 | -0.1371 | 4.14e-15 | 7.28e-15 |
| doomloop | readiness | delta_L | -0.0004 | -0.0004 | 2.59e-16 | 5.38e-17 |
| doomloop | readiness | delta_H | 0.0209 | 0.0209 | 6.77e-16 | 1.19e-15 |

### 6.4 Cutoff 最小 RSS 与样本加总

| Criterion | 记录 cutoff | 最小 RSS | cutoff RSS | \|差值\| | N | N_low | N_high | 加总 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | 0.2431 | 12.410913 | 12.410913 | 0 | 1,433 | 1,095 | 338 | 通过 | 通过 |
| $b_{it}$ | 8.2025 | 12.098584 | 12.098584 | 0 | 1,433 | 995 | 438 | 通过 | 通过 |
| $\widehat m^A_{it}$ | 0.0036 | 12.156384 | 12.156384 | 0 | 1,433 | 870 | 563 | 通过 | 通过 |
| $\widehat Y^A_{it}$ | -0.0361 | 12.618523 | 12.618523 | 0 | 1,433 | 415 | 1,018 | 通过 | 通过 |
| $b_{it}\widehat m^A_{it}$ | 0.2825 | 12.415705 | 12.415705 | 0 | 1,433 | 1,097 | 336 | 通过 | 通过 |

Readiness cutoff 继承检查：

| 方程 | cutoff 来源 | cutoff | 债务 profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| debt | debt_full | 0.2431 | 12.4109 | 12.4109 | 0 | 通过 |
| ready_debt | debt_full | 0.2431 | 12.4109 | 12.4109 | 0 | 通过 |

### 6.5 五判据共同样本与拟合排序

| RSS 排名 | Criterion | N | RSS | Within R2 | 理论方向 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | $b_{it}$ | 1,433 | 12.098584 | 0.2256 | Match (+,-) |
| 2 | $\widehat m^A_{it}$ | 1,433 | 12.156384 | 0.2219 | Match (+,-) |
| 3 | $\widehat\theta^A_{it}$ | 1,433 | 12.410912 | 0.2056 | Match (+,-) |
| 4 | $b_{it}\widehat m^A_{it}$ | 1,433 | 12.415705 | 0.2053 | Match (+,-) |
| 5 | $\widehat Y^A_{it}$ | 1,433 | 12.618523 | 0.1923 | Partial (-,-) |

## 7. 图形 QA

| 图形 | 字节 | 状态 |
| --- | ---: | ---: |
| debt_marginal_effect_no_b.png | 178,795 | 通过 |
| debt_marginal_effect_no_b.pdf | 73,500 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.png | 175,665 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.pdf | 71,610 | 通过 |
| kink_marginal_effects_no_state.png | 226,363 | 通过 |
| kink_marginal_effects_no_state.pdf | 79,303 | 通过 |

债务图和 readiness 图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0。Readiness 图的竖直线来自债务全控制方程。

## 8. Required Caveats for Stakeholders

- 当前 `vce(robust)` 处理异方差，但不处理同一国家内序列相关。
- theta 是两条上游回归的生成变量；cutoff 又在同一样本中搜索，常规 p 值没有覆盖联合不确定性。
- 比较五种判据会引入模型选择和多重比较问题；最低 RSS 仅代表本样本内拟合。
- 固定效应相关性结果不支持因果措辞。

## 9. 原始输出索引

完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。
