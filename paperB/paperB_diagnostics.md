# Paper B：统计检验与数据检查

> 生成时间：2026-08-12 20:38（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。

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

唯一原始分析输入是 `data0804/invest_panel_weo.csv`。A=`readiness_delta100/100`，X=`vulnerability_delta100/100`；金额变量不缩放。主流程构造 `ln_constantgdp=ln(ConstantGDP)` 与 `ln_debt=ln(debt)`；所有回归控制 growth 和 ln_constantgdp。产出模型含 Y_lag 时，Y_lag 本身就是 ln_constantgdp，因此只保留一次。Doomloop 从 empirical-theta panel 读取构造量，并单独将源 `interest_revenue` 除以 100。

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
| vulnerability_delta100 | 1,769 | -0.0393 | 0.0587 | -0.1847 | -0.047 | 0.2955 |
| readiness_delta100 | 1,769 | 0.06 | 0.0896 | -0.3264 | 0.0498 | 0.3034 |
| growth | 1,822 | 0.0337 | 0.0353 | -0.1455 | 0.0345 | 0.2462 |
| inflation_cpi | 1,820 | 0.0561 | 0.1074 | -0.0397 | 0.0317 | 1.973 |
| reserves | 1,757 | 0.1664 | 0.188 | 0.0034 | 0.1134 | 1.4339 |
| tt | 1,605 | 1.0069 | 0.1859 | 0.3188 | 0.9942 | 2.7308 |
| ln_constantgdp | 1,825 | 8.1897 | 2.735 | 2.9628 | 7.8151 | 16.3252 |
| ln_debt | 1,724 | 7.2075 | 2.761 | 0.4055 | 7.0078 | 15.9286 |

### 3.2 Y 与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Y_outcome | output | 1,485 | 8.2572 | 2.7671 | 3.2544 | 7.827 | 16.3252 |
| Y_lag | output | 1,485 | 8.2253 | 2.7623 | 3.1901 | 7.8116 | 16.276 |
| mA_hat_spread_ratio | theta_support | 1,114 | -0.0114 | 0.0833 | -0.2045 | -0.0234 | 0.2451 |
| mA_hat | theta_support | 1,114 | -0.0114 | 0.0833 | -0.2045 | -0.0234 | 0.2451 |
| ln_debt_mA_hat | theta_support | 1,114 | 0.14 | 0.8287 | -0.4782 | -0.1669 | 3.8911 |
| spread_saving_component | theta_support | 1,114 | 0.14 | 0.8287 | -0.4782 | -0.1669 | 3.8911 |
| YA_hat | theta_support | 1,114 | 0.0056 | 0.0034 | -0.0152 | 0.0061 | 0.0145 |
| theta_hat_A | theta_support | 1,114 | 0.1456 | 0.8279 | -0.4729 | -0.1613 | 3.8956 |
| theta_hat_A | all_constructible | 1,677 | 0.0936 | 0.7714 | -0.4731 | -0.1853 | 3.9331 |

### 3.3 Doomloop 主规格与判据变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_no_b | debt | b_outcome | dependent_variable | 1,433 | 0.0915 | 0.1129 | -0.8964 | 0.0765 | 1.2158 |
| debt_no_b | debt | debt_kink_low | regressor | 1,433 | 0.0118 | 0.0229 | -0.1151 | 0 | 0.1226 |
| debt_no_b | debt | debt_kink_high | regressor | 1,433 | 0.0182 | 0.0884 | -0.141 | 0 | 0.6569 |
| debt_no_b | debt | vulnerability_delta100 | regressor | 1,433 | -0.036 | 0.0561 | -0.183 | -0.0444 | 0.2955 |
| debt_no_b | debt | growth | regressor | 1,433 | 0.0338 | 0.0361 | -0.1455 | 0.0344 | 0.2462 |
| debt_no_b | debt | ln_constantgdp | regressor | 1,433 | 8.248 | 2.785 | 3.1901 | 7.8017 | 16.276 |
| debt_no_b | debt | inflation_cpi | regressor | 1,433 | 0.0462 | 0.0542 | -0.0177 | 0.0314 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,433 | 0.1627 | 0.1669 | 0.0034 | 0.1178 | 1.4339 |
| debt_no_b | debt | tt | regressor | 1,433 | 1.0089 | 0.1826 | 0.3188 | 0.9942 | 2.7308 |
| debt_no_b | debt | readiness_delta100 | construction_input | 1,433 | 0.0623 | 0.0882 | -0.3264 | 0.0526 | 0.3034 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,433 | 0.106 | 0.7769 | -0.4729 | -0.1643 | 3.8956 |
| debt_no_b | debt | ln_debt | construction_input | 1,433 | 7.3136 | 2.7322 | 0.9462 | 7.1055 | 15.8777 |
| debt_no_b | debt | mA_hat | construction_input | 1,433 | -0.0175 | 0.0838 | -0.2124 | -0.0242 | 0.2451 |
| debt_no_b | debt | YA_hat | construction_input | 1,433 | 0.0054 | 0.0035 | -0.0152 | 0.0059 | 0.0145 |
| debt_no_b | debt | ln_debt_mA_hat | construction_input | 1,433 | 0.1007 | 0.7776 | -0.4782 | -0.1723 | 3.8911 |
| ready_no_lag_debt_cutoff | ready_debt | A_outcome | dependent_variable | 1,448 | -0.0025 | 0.0199 | -0.2212 | -0.0014 | 0.0974 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 1,448 | 0.0095 | 0.017 | -0.0089 | 0.0011 | 0.1804 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 1,448 | 0.0317 | 0.0846 | -0.0955 | 0 | 0.6856 |
| ready_no_lag_debt_cutoff | ready_debt | vulnerability_delta100 | regressor | 1,448 | -0.0375 | 0.0521 | -0.183 | -0.0437 | 0.2096 |
| ready_no_lag_debt_cutoff | ready_debt | growth | regressor | 1,448 | 0.033 | 0.0353 | -0.1455 | 0.0331 | 0.2462 |
| ready_no_lag_debt_cutoff | ready_debt | ln_constantgdp | regressor | 1,448 | 8.3086 | 2.7973 | 3.1901 | 7.838 | 16.3252 |
| ready_no_lag_debt_cutoff | ready_debt | inflation_cpi | regressor | 1,448 | 0.048 | 0.0564 | -0.0177 | 0.0329 | 0.723 |
| ready_no_lag_debt_cutoff | ready_debt | reserves | regressor | 1,448 | 0.1494 | 0.1356 | 0.0034 | 0.1152 | 1.4339 |
| ready_no_lag_debt_cutoff | ready_debt | tt | regressor | 1,448 | 1.008 | 0.1759 | 0.3188 | 0.9945 | 2.7308 |
| ready_no_lag_debt_cutoff | ready_debt | interest_revenue | construction_input | 1,448 | 0.0852 | 0.0977 | -0.069 | 0.0567 | 0.7987 |
| ready_no_lag_debt_cutoff | ready_debt | theta_hat_A | construction_input | 1,448 | 0.1294 | 0.7957 | -0.4731 | -0.1462 | 3.9331 |

## 4. 缺失、重复键与 Within 变异

三个估计阶段均对国家—年份键执行 fail-closed 唯一性检查；不会自动去重。每个方程在估计前锁定全控制样本，五种判据进一步共用同一债务样本。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 (%) | 独占损失 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 497 | 27.2 | 319 |
| baseline | — | vulnerability_delta100 | 58 | 3.17 | 0 |
| baseline | — | readiness_delta100 | 58 | 3.17 | 0 |
| baseline | — | ln_debt | 103 | 5.64 | 11 |
| baseline | — | growth | 5 | 0.27 | 0 |
| baseline | — | ln_constantgdp | 2 | 0.11 | 0 |
| baseline | — | inflation_cpi | 7 | 0.38 | 1 |
| baseline | — | reserves | 70 | 3.83 | 3 |
| baseline | — | tt | 222 | 12.15 | 90 |
| output | — | Y_outcome | 64 | 3.5 | 60 |
| output | — | readiness_delta100 | 58 | 3.17 | 0 |
| output | — | vulnerability_delta100 | 58 | 3.17 | 0 |
| output | — | Y_lag | 2 | 0.11 | 0 |
| output | — | growth | 5 | 0.27 | 0 |
| output | — | inflation_cpi | 7 | 0.38 | 2 |
| output | — | reserves | 70 | 3.83 | 28 |
| output | — | tt | 222 | 12.15 | 180 |
| doomloop | debt | b_outcome | 166 | 9.09 | 60 |
| doomloop | debt | readiness_delta100 | 58 | 3.17 | 0 |
| doomloop | debt | theta_hat_A | 150 | 8.21 | 0 |
| doomloop | debt | ln_debt | 103 | 5.64 | 0 |
| doomloop | debt | mA_hat | 150 | 8.21 | 0 |
| doomloop | debt | YA_hat | 58 | 3.17 | 0 |
| doomloop | debt | ln_debt_mA_hat | 150 | 8.21 | 0 |
| doomloop | debt | vulnerability_delta100 | 58 | 3.17 | 0 |
| doomloop | debt | growth | 5 | 0.27 | 0 |
| doomloop | debt | ln_constantgdp | 2 | 0.11 | 0 |
| doomloop | debt | inflation_cpi | 7 | 0.38 | 2 |
| doomloop | debt | reserves | 70 | 3.83 | 26 |
| doomloop | debt | tt | 222 | 12.15 | 148 |
| doomloop | ready | A_outcome | 119 | 6.51 | 10 |
| doomloop | ready | interest_revenue | 141 | 7.72 | 34 |
| doomloop | ready | theta_hat_A | 150 | 8.21 | 9 |
| doomloop | ready | vulnerability_delta100 | 58 | 3.17 | 0 |
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
| baseline | — | vulnerability100 | 7.9015 | 1.0485 | 0.1327 | adequate |
| baseline | — | vulnerability_delta100 | 0.0587 | 0.028 | 0.4775 | adequate |
| baseline | — | readiness100 | 14.5222 | 4.3358 | 0.2986 | adequate |
| baseline | — | readiness_delta100 | 0.0896 | 0.0412 | 0.4595 | adequate |
| baseline | — | lnrgdp | 2.735 | 0.308 | 0.1126 | adequate |
| baseline | — | growth | 0.0353 | 0.0317 | 0.8996 | adequate |
| baseline | — | inflation_cpi | 0.1074 | 0.0925 | 0.8612 | adequate |
| baseline | — | debt_gdp | 0.3489 | 0.1833 | 0.5253 | adequate |
| baseline | — | PrimaryBalance_gdp | 0.0342 | 0.0292 | 0.8537 | adequate |
| baseline | — | reserves | 0.188 | 0.091 | 0.4842 | adequate |
| baseline | — | gee | 0.9129 | 0.1927 | 0.2111 | adequate |
| baseline | — | rqe | 0.8587 | 0.1822 | 0.2122 | adequate |
| baseline | — | tt | 0.1859 | 0.165 | 0.8875 | adequate |
| baseline | — | is_advanced | 0.5001 | 0 | 0 | not_identified_by_FE |
| baseline | — | Revenue_gdp | 0.1298 | 0.0241 | 0.1855 | adequate |
| baseline | — | CurrentGDP | 2435.2277 | 1052.4202 | 0.4322 | adequate |
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
| output | — | readiness_delta100 | 0.0879 | 0.0394 | 0.4485 | adequate |
| output | — | vulnerability_delta100 | 0.0564 | 0.0241 | 0.4269 | adequate |
| output | — | growth | 0.036 | 0.0317 | 0.8822 | adequate |
| output | — | inflation_cpi | 0.0732 | 0.0561 | 0.7659 | adequate |
| output | — | reserves | 0.1653 | 0.0765 | 0.4631 | adequate |
| output | — | tt | 0.1878 | 0.167 | 0.8892 | adequate |
| doomloop | debt | b_outcome | 0.1129 | 0.1045 | 0.9255 | adequate |
| doomloop | debt | theta_hat_A | 0.7769 | 0.2168 | 0.279 | adequate |
| doomloop | debt | ln_debt | 2.7322 | 0.7447 | 0.2726 | adequate |
| doomloop | debt | mA_hat | 0.0838 | 0.0229 | 0.2729 | adequate |
| doomloop | debt | YA_hat | 0.0035 | 0.0015 | 0.4319 | adequate |
| doomloop | debt | ln_debt_mA_hat | 0.7776 | 0.217 | 0.279 | adequate |
| doomloop | debt | readiness_delta100 | 0.0882 | 0.0399 | 0.4526 | adequate |
| doomloop | debt | vulnerability_delta100 | 0.0561 | 0.0242 | 0.4319 | adequate |
| doomloop | debt | growth | 0.0361 | 0.0319 | 0.8821 | adequate |
| doomloop | debt | ln_constantgdp | 2.785 | 0.2727 | 0.0979 | adequate |
| doomloop | debt | inflation_cpi | 0.0542 | 0.0416 | 0.7676 | adequate |
| doomloop | debt | reserves | 0.1669 | 0.0767 | 0.4596 | adequate |
| doomloop | debt | tt | 0.1826 | 0.1609 | 0.8807 | adequate |
| doomloop | ready | A_outcome | 0.0199 | 0.0196 | 0.988 | adequate |
| doomloop | ready | theta_hat_A | 0.7957 | 0.2259 | 0.2839 | adequate |
| doomloop | ready | interest_revenue | 0.0977 | 0.0452 | 0.4629 | adequate |
| doomloop | ready | vulnerability_delta100 | 0.0521 | 0.0241 | 0.4629 | adequate |
| doomloop | ready | growth | 0.0353 | 0.0311 | 0.8813 | adequate |
| doomloop | ready | ln_constantgdp | 2.7973 | 0.2694 | 0.0963 | adequate |
| doomloop | ready | inflation_cpi | 0.0564 | 0.0433 | 0.7675 | adequate |
| doomloop | ready | reserves | 0.1356 | 0.0752 | 0.5548 | adequate |
| doomloop | ready | tt | 0.1759 | 0.1567 | 0.891 | adequate |

## 5. 共线性、相关性与系数变化

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline | vulnerability_delta100 | 1.7074 | 0.5857 | 2.3823 |
| baseline | readiness_delta100 | 1.4554 | 0.6871 | 2.3823 |
| baseline | ln_debt | 1.656 | 0.6039 | 2.3823 |
| baseline | growth | 1.0931 | 0.9148 | 2.3823 |
| baseline | ln_constantgdp | 1.2978 | 0.7706 | 2.3823 |
| baseline | inflation_cpi | 1.0802 | 0.9258 | 2.3823 |
| baseline | reserves | 1.0938 | 0.9142 | 2.3823 |
| baseline | tt | 1.0332 | 0.9679 | 2.3823 |
| output | readiness_delta100 | 1.196 | 0.8361 | 1.6382 |
| output | vulnerability_delta100 | 1.2545 | 0.7971 | 1.6382 |
| output | Y_lag | 1.0661 | 0.938 | 1.6382 |
| output | growth | 1.0325 | 0.9685 | 1.6382 |
| output | inflation_cpi | 1.0235 | 0.977 | 1.6382 |
| output | reserves | 1.0166 | 0.9836 | 1.6382 |
| output | tt | 1.0245 | 0.9761 | 1.6382 |
| output | c_A_Y | 1.3586 | 0.7361 | 2.0468 |
| output | c_X_Y | 1.3639 | 0.7332 | 2.0468 |
| output | int_AX_Y | 1.4486 | 0.6903 | 2.0468 |
| output | Y_lag | 1.2345 | 0.81 | 2.0468 |
| output | growth | 1.0351 | 0.9661 | 2.0468 |
| output | inflation_cpi | 1.0349 | 0.9663 | 2.0468 |
| output | reserves | 1.0167 | 0.9836 | 2.0468 |
| output | tt | 1.0267 | 0.974 | 2.0468 |


绝对相关系数不低于 0.60 的非重复变量对：

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |
| baseline | ln_debt | ln_constantgdp | 0.9611 |

## 6. 统计与程序验证

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | F | 分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 40.9804 | 2 | 1,080 | <0.001 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 74.6938 | 1 | 1,080 | <0.001 |
| baseline | Interact_AX | c_A = int_AX = 0 | 2.948 | 2 | 1,080 | 0.053 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 1.8708 | 1 | 1,080 | 0.172 |
| baseline | Interact_all | c_A = int_AB = 0 | 38.3668 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AX = 0 | 0.1696 | 2 | 1,079 | 0.844 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 27.4013 | 3 | 1,079 | <0.001 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 37.4218 | 2 | 1,079 | <0.001 |
| output | Y5_macro | inflation control zero | 0.581 | 1 | 1,393 | 0.446 |
| output | Y7_layer2_A | external controls jointly zero | 4.7264 | 2 | 1,391 | 0.009 |
| output | Y7_layer2_A | all controls jointly zero | 3.3207 | 3 | 1,391 | 0.019 |
| output | Y8_interact_core | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 0.2061 | 2 | 1,393 | 0.814 |
| output | Y8_interact_core | interaction zero: int_AX_Y = 0 | 0.157 | 1 | 1,393 | 0.692 |
| output | Y9_interact_macro | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 0.1385 | 2 | 1,392 | 0.871 |
| output | Y9_interact_macro | interaction zero: int_AX_Y = 0 | 0.0976 | 1 | 1,392 | 0.755 |
| output | Y10_interact_full | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 0.065 | 2 | 1,390 | 0.937 |
| output | Y10_interact_full | interaction zero: int_AX_Y = 0 | 0.0867 | 1 | 1,390 | 0.769 |
| output | Y9_interact_macro | inflation control zero | 0.5338 | 1 | 1,392 | 0.465 |
| output | Y10_interact_full | external controls jointly zero | 4.734 | 2 | 1,390 | 0.009 |
| output | Y10_interact_full | all controls jointly zero | 3.3178 | 3 | 1,390 | 0.019 |
| doomloop | DN3_full | low- and high-branch coefficients jointly zero | 9.7985 | 2 | 1,338 | <0.001 |
| doomloop | DN3_full | macro controls jointly zero | 4.6131 | 1 | 1,338 | 0.032 |
| doomloop | DN3_full | external controls jointly zero | 2.6529 | 2 | 1,338 | 0.071 |
| doomloop | DN3_full | all controls jointly zero | 2.5495 | 3 | 1,338 | 0.054 |
| doomloop | RDN3_full | branches jointly zero; debt-equation cutoff | 1.4888 | 2 | 1,354 | 0.226 |
| doomloop | RDN3_full | macro controls jointly zero | 0.2547 | 1 | 1,354 | 0.614 |
| doomloop | RDN3_full | external controls jointly zero | 0.9751 | 2 | 1,354 | 0.377 |
| doomloop | RDN3_full | all controls jointly zero | 0.8582 | 3 | 1,354 | 0.462 |

### 6.2 代数、映射与 hinge 公式

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | Y(t+1) equals exact F.ln_constantgdp | 0 | 1.00e-12 | 通过 |
| theta | Y(t) equals current ln_constantgdp | 0 | 1.00e-12 | 通过 |
| theta | b_it equals ln_debt exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 5.55e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw output formula | 3.47e-18 | 1.00e-12 | 通过 |
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
| baseline | Layer2_A | vulnerability_delta100 | -0.0202 | -0.0202 | 8.01e-15 | 5.03e-15 |
| baseline | Layer2_A | readiness_delta100 | -0.0318 | -0.0318 | 8.88e-16 | 7.29e-17 |
| baseline | Layer2_A | ln_debt | 0.0196 | 0.0196 | 5.41e-16 | 2.51e-15 |
| baseline | Layer2_A | growth | -0.1837 | -0.1837 | 2.03e-15 | 5.69e-16 |
| baseline | Layer2_A | ln_constantgdp | -0.0246 | -0.0246 | 2.16e-15 | 9.67e-15 |
| baseline | Layer2_A | inflation_cpi | 0.1536 | 0.1536 | 4.08e-15 | 4.61e-16 |
| baseline | Layer2_A | reserves | -0.0031 | -0.0031 | 2.17e-15 | 5.62e-16 |
| baseline | Layer2_A | tt | -0.0025 | -0.0025 | 1.14e-15 | 9.80e-16 |
| baseline | Interact_all | c_A | 0.0099 | 0.0099 | 2.28e-15 | 1.11e-16 |
| baseline | Interact_all | c_X | 0.1066 | 0.1066 | 1.34e-14 | 1.95e-15 |
| baseline | Interact_all | c_b | 0.019 | 0.019 | 4.79e-16 | 7.87e-16 |
| baseline | Interact_all | int_AB | -0.0307 | -0.0307 | 4.41e-16 | 2.75e-16 |
| baseline | Interact_all | int_AX | -0.0056 | -0.0056 | 4.30e-14 | 2.26e-14 |
| baseline | Interact_all | growth | -0.1766 | -0.1766 | 8.88e-16 | 4.86e-16 |
| baseline | Interact_all | ln_constantgdp | -0.0224 | -0.0224 | 2.58e-15 | 5.42e-15 |
| baseline | Interact_all | inflation_cpi | 0.1459 | 0.1459 | 4.55e-15 | 2.08e-17 |
| baseline | Interact_all | reserves | 0.0003 | 0.0003 | 1.92e-15 | 2.83e-16 |
| baseline | Interact_all | tt | -0.0039 | -0.0039 | 1.34e-15 | 6.94e-18 |
| tax | Spread_Interact_all | c_A | 0.0099 | 0.0099 | 1.54e-15 | 1.73e-17 |
| tax | Spread_Interact_all | c_X | 0.1066 | 0.1066 | 1.30e-14 | 1.14e-15 |
| tax | Spread_Interact_all | c_b | 0.019 | 0.019 | 4.16e-17 | 1.26e-15 |
| tax | Spread_Interact_all | int_AB | -0.0307 | -0.0307 | 6.63e-16 | 4.99e-17 |
| tax | Spread_Interact_all | int_AX | -0.0056 | -0.0056 | 3.77e-14 | 3.40e-14 |
| tax | Spread_Interact_all | growth | -0.1766 | -0.1766 | 6.38e-16 | 5.62e-16 |
| tax | Spread_Interact_all | ln_constantgdp | -0.0224 | -0.0224 | 2.58e-15 | 1.36e-15 |
| tax | Spread_Interact_all | inflation_cpi | 0.1459 | 0.1459 | 3.16e-15 | 2.08e-16 |
| tax | Spread_Interact_all | reserves | 0.0003 | 0.0003 | 1.42e-15 | 2.16e-16 |
| tax | Spread_Interact_all | tt | -0.0039 | -0.0039 | 1.28e-15 | 3.97e-16 |
| tax | Y7_layer2_A | vulnerability_delta100 | -0.055 | -0.055 | 9.40e-13 | 1.19e-14 |
| tax | Y7_layer2_A | readiness_delta100 | 0.0027 | 0.0027 | 4.97e-16 | 6.48e-15 |
| tax | Y7_layer2_A | Y_lag | 0.9703 | 0.9703 | 5.68e-13 | 4.37e-15 |
| tax | Y7_layer2_A | growth | 0.2583 | 0.2583 | 2.15e-13 | 6.18e-16 |
| tax | Y7_layer2_A | inflation_cpi | -0.0142 | -0.0142 | 4.58e-14 | 2.89e-15 |
| tax | Y7_layer2_A | reserves | 0.0229 | 0.0229 | 9.02e-14 | 2.89e-15 |
| tax | Y7_layer2_A | tt | -0.0025 | -0.0025 | 8.95e-15 | 1.82e-16 |
| tax | Y10_interact_full | c_A_Y | 0.0053 | 0.0053 | 4.38e-13 | 5.13e-16 |
| tax | Y10_interact_full | c_X_Y | -0.0587 | -0.0587 | 1.70e-12 | 2.42e-14 |
| tax | Y10_interact_full | int_AX_Y | -0.062 | -0.062 | 9.83e-12 | 3.00e-13 |
| tax | Y10_interact_full | Y_lag | 0.9697 | 0.9697 | 7.87e-13 | 6.19e-15 |
| tax | Y10_interact_full | growth | 0.2588 | 0.2588 | 3.25e-13 | 5.97e-15 |
| tax | Y10_interact_full | inflation_cpi | -0.0137 | -0.0137 | 1.31e-13 | 4.42e-15 |
| tax | Y10_interact_full | reserves | 0.0229 | 0.0229 | 1.02e-13 | 4.80e-15 |
| tax | Y10_interact_full | tt | -0.0025 | -0.0025 | 2.18e-14 | 1.86e-16 |
| doomloop | theta | beta_L | 1.1426 | 1.1426 | 1.32e-13 | 3.24e-14 |
| doomloop | theta | beta_H | -0.1893 | -0.1893 | 8.47e-15 | 4.83e-15 |
| doomloop | b | beta_L | 0.1456 | 0.1456 | 5.00e-15 | 2.46e-15 |
| doomloop | b | beta_H | -0.0646 | -0.0646 | 2.55e-15 | 5.07e-16 |
| doomloop | mA | beta_L | 4.7295 | 4.7295 | 1.95e-14 | 9.55e-15 |
| doomloop | mA | beta_H | -2.1008 | -2.1008 | 7.19e-14 | 1.51e-14 |
| doomloop | YA | beta_L | 3.1897 | 3.1897 | 4.77e-13 | 1.99e-12 |
| doomloop | YA | beta_H | -115.9081 | -115.9081 | 2.22e-12 | 4.04e-12 |
| doomloop | b*mA | beta_L | 1.1231 | 1.1231 | 4.42e-14 | 1.80e-14 |
| doomloop | b*mA | beta_H | -0.189 | -0.189 | 9.24e-15 | 3.93e-15 |
| doomloop | readiness | delta_L | -0.0554 | -0.0554 | 8.88e-16 | 7.63e-17 |
| doomloop | readiness | delta_H | -0.0063 | -0.0063 | 7.66e-16 | 1.69e-15 |

### 6.4 Cutoff 最小 RSS 与样本加总

| Criterion | 记录 cutoff | 最小 RSS | cutoff RSS | \|差值\| | N | N_low | N_high | 加总 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | -0.0602 | 12.507612 | 12.507612 | 0 | 1,433 | 855 | 578 | 通过 | 通过 |
| $b_{it}$ | 7.7054 | 12.502542 | 12.502542 | 0 | 1,433 | 887 | 546 | 通过 | 通过 |
| $\widehat m^A_{it}$ | -0.0057 | 12.503581 | 12.503581 | 0 | 1,433 | 886 | 547 | 通过 | 通过 |
| $\widehat Y^A_{it}$ | 0.0092 | 12.620148 | 12.620148 | 0 | 1,433 | 1,279 | 154 | 通过 | 通过 |
| $b_{it}\widehat m^A_{it}$ | -0.0622 | 12.509861 | 12.509861 | 0 | 1,433 | 860 | 573 | 通过 | 通过 |

Readiness cutoff 继承检查：

| 方程 | cutoff 来源 | cutoff | 债务 profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| debt | debt_full | -0.0602 | 12.5076 | 12.5076 | 0 | 通过 |
| ready_debt | debt_full | -0.0602 | 12.5076 | 12.5076 | 0 | 通过 |

### 6.5 五判据共同样本与拟合排序

| RSS 排名 | Criterion | N | RSS | Within R2 | 理论方向 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | $b_{it}$ | 1,433 | 12.502542 | 0.1997 | Match (+,-) |
| 2 | $\widehat m^A_{it}$ | 1,433 | 12.503581 | 0.1997 | Match (+,-) |
| 3 | $\widehat\theta^A_{it}$ | 1,433 | 12.507612 | 0.1994 | Match (+,-) |
| 4 | $b_{it}\widehat m^A_{it}$ | 1,433 | 12.509861 | 0.1993 | Match (+,-) |
| 5 | $\widehat Y^A_{it}$ | 1,433 | 12.620148 | 0.1922 | Match (+,-) |

## 7. 图形 QA

| 图形 | 字节 | 状态 |
| --- | ---: | ---: |
| debt_marginal_effect_no_b.png | 174,658 | 通过 |
| debt_marginal_effect_no_b.pdf | 73,234 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.png | 176,637 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.pdf | 71,417 | 通过 |
| kink_marginal_effects_no_state.png | 221,340 | 通过 |
| kink_marginal_effects_no_state.pdf | 78,750 | 通过 |

债务图和 readiness 图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0。Readiness 图的竖直线来自债务全控制方程。

## 8. Required Caveats for Stakeholders

- 当前 `vce(robust)` 处理异方差，但不处理同一国家内序列相关。
- theta 是两条上游回归的生成变量；cutoff 又在同一样本中搜索，常规 p 值没有覆盖联合不确定性。
- 比较五种判据会引入模型选择和多重比较问题；最低 RSS 仅代表本样本内拟合。
- 固定效应相关性结果不支持因果措辞。

## 9. 原始输出索引

完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。
