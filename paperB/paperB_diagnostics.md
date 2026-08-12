# Paper B：统计检验与数据检查

> 生成时间：2026-08-12 22:23（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。

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

唯一原始分析输入是 `data0804/invest_panel_weo.csv`。A=`readiness_delta100/100`，X=`vulnerability_delta100/100`，b=`debt_gdp/100`；金额变量不缩放。Baseline、利差构造方程与 Doomloop 控制 growth 和 ln_constantgdp；所有产出模型控制相邻期 ConstantGDP 增长比率 Y_lag，并取消 growth 与 ln_constantgdp。Doomloop 从 empirical-theta panel 读取构造量，并单独将源 `interest_revenue` 除以 100。

- $Y_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$，$Y_{i,t+1}=ConstantGDP_{i,t+1}/ConstantGDP_{it}$，严格要求相邻年份。
- $\Delta debt\_gdp_{i,t+1}=F.debt\_gdp_{it}-debt\_gdp_{it}$，严格要求相邻年份。
- Readiness 因变量为 $A_{it}-A_{i,t-1}$；$A_{i,t-1}$ 只用于构造差分，不作为右侧状态控制。

### 2.1 Doomloop 源字段换算

| 变量 | 源最小值 | 源最大值 | 比率最小值 | 比率最大值 | 最大误差 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| interest_revenue | -14.8211 | 79.8698 | -0.1482 | 0.7987 | 0 | 通过 |

## 3. 固定样本与描述统计

| 固定样本 | N | 国家数 | 年份数 | 年份范围 |
| --- | ---: | ---: | ---: | ---: |
| Baseline 全交互 | 1,174 | 60 | 26 | 1998–2023 |
| Y 全控制交互 | 1,461 | 60 | 27 | 1996–2022 |
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
| debt_gdp | 1,724 | 0.5774 | 0.3489 | 0.0005 | 0.5117 | 2.6096 |
| reserves | 1,757 | 0.1664 | 0.188 | 0.0034 | 0.1134 | 1.4339 |
| tt | 1,605 | 1.0069 | 0.1859 | 0.3188 | 0.9942 | 2.7308 |
| ln_constantgdp | 1,825 | 8.1897 | 2.735 | 2.9628 | 7.8151 | 16.3252 |

### 3.2 Y 与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Y_outcome | output | 1,461 | 1.0325 | 0.0356 | 0.8545 | 1.0329 | 1.2462 |
| Y_lag | output | 1,461 | 1.0338 | 0.0358 | 0.8545 | 1.0346 | 1.2462 |
| mA_hat_spread_ratio | theta_support | 1,114 | 0.0919 | 0.057 | -0.0278 | 0.0821 | 0.3421 |
| mA_hat | theta_support | 1,114 | 0.0919 | 0.057 | -0.0278 | 0.0821 | 0.3421 |
| debt_gdp_mA_hat | theta_support | 1,114 | 0.0756 | 0.1015 | -0.0119 | 0.0433 | 0.7826 |
| spread_saving_component | theta_support | 1,114 | 0.0756 | 0.1015 | -0.0119 | 0.0433 | 0.7826 |
| YA_hat | theta_support | 1,114 | -0.0128 | 0.0174 | -0.0581 | -0.0151 | 0.0934 |
| theta_hat_A | theta_support | 1,114 | 0.0627 | 0.1027 | -0.0458 | 0.0311 | 0.7821 |
| theta_hat_A | all_constructible | 1,677 | 0.0568 | 0.0985 | -0.0504 | 0.0298 | 1.0163 |

### 3.3 Doomloop 主规格与判据变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_no_b | debt | b_outcome | dependent_variable | 1,433 | 0.0077 | 0.0635 | -0.5417 | 0.0019 | 0.4186 |
| debt_no_b | debt | debt_kink_low | regressor | 1,433 | 0.0017 | 0.0037 | -0.0066 | 0 | 0.0214 |
| debt_no_b | debt | debt_kink_high | regressor | 1,433 | 0.0027 | 0.0124 | -0.0319 | 0 | 0.1401 |
| debt_no_b | debt | vulnerability_delta100 | regressor | 1,433 | -0.036 | 0.0561 | -0.183 | -0.0444 | 0.2955 |
| debt_no_b | debt | growth | regressor | 1,433 | 0.0338 | 0.0361 | -0.1455 | 0.0344 | 0.2462 |
| debt_no_b | debt | ln_constantgdp | regressor | 1,433 | 8.248 | 2.785 | 3.1901 | 7.8017 | 16.276 |
| debt_no_b | debt | inflation_cpi | regressor | 1,433 | 0.0462 | 0.0542 | -0.0177 | 0.0314 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,433 | 0.1627 | 0.1669 | 0.0034 | 0.1178 | 1.4339 |
| debt_no_b | debt | tt | regressor | 1,433 | 1.0089 | 0.1826 | 0.3188 | 0.9942 | 2.7308 |
| debt_no_b | debt | readiness_delta100 | construction_input | 1,433 | 0.0623 | 0.0882 | -0.3264 | 0.0526 | 0.3034 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,433 | 0.0568 | 0.1001 | -0.0458 | 0.0275 | 1.0163 |
| debt_no_b | debt | debt_gdp | construction_input | 1,433 | 0.5824 | 0.3516 | 0.039 | 0.5064 | 2.6096 |
| debt_no_b | debt | mA_hat | construction_input | 1,433 | 0.0852 | 0.0571 | -0.0278 | 0.0764 | 0.3879 |
| debt_no_b | debt | YA_hat | construction_input | 1,433 | -0.0116 | 0.0178 | -0.0581 | -0.0142 | 0.0934 |
| debt_no_b | debt | debt_gdp_mA_hat | construction_input | 1,433 | 0.0684 | 0.0991 | -0.0119 | 0.038 | 1.0123 |
| ready_no_lag_debt_cutoff | ready_debt | A_outcome | dependent_variable | 1,448 | -0.0025 | 0.0199 | -0.2212 | -0.0014 | 0.0974 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 1,448 | 0.0011 | 0.0019 | -0.0045 | 0.0005 | 0.0152 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 1,448 | 0.0029 | 0.0087 | -0.0031 | 0 | 0.1175 |
| ready_no_lag_debt_cutoff | ready_debt | vulnerability_delta100 | regressor | 1,448 | -0.0375 | 0.0521 | -0.183 | -0.0437 | 0.2096 |
| ready_no_lag_debt_cutoff | ready_debt | growth | regressor | 1,448 | 0.033 | 0.0353 | -0.1455 | 0.0331 | 0.2462 |
| ready_no_lag_debt_cutoff | ready_debt | ln_constantgdp | regressor | 1,448 | 8.3086 | 2.7973 | 3.1901 | 7.838 | 16.3252 |
| ready_no_lag_debt_cutoff | ready_debt | inflation_cpi | regressor | 1,448 | 0.048 | 0.0564 | -0.0177 | 0.0329 | 0.723 |
| ready_no_lag_debt_cutoff | ready_debt | reserves | regressor | 1,448 | 0.1494 | 0.1356 | 0.0034 | 0.1152 | 1.4339 |
| ready_no_lag_debt_cutoff | ready_debt | tt | regressor | 1,448 | 1.008 | 0.1759 | 0.3188 | 0.9945 | 2.7308 |
| ready_no_lag_debt_cutoff | ready_debt | interest_revenue | construction_input | 1,448 | 0.0852 | 0.0977 | -0.069 | 0.0567 | 0.7987 |
| ready_no_lag_debt_cutoff | ready_debt | theta_hat_A | construction_input | 1,448 | 0.0567 | 0.1013 | -0.0458 | 0.0275 | 1.0163 |

## 4. 缺失、重复键与 Within 变异

三个估计阶段均对国家—年份键执行 fail-closed 唯一性检查；不会自动去重。每个方程在估计前锁定全控制样本，五种判据进一步共用同一债务样本。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 (%) | 独占损失 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 497 | 27.2 | 319 |
| baseline | — | vulnerability_delta100 | 58 | 3.17 | 0 |
| baseline | — | readiness_delta100 | 58 | 3.17 | 0 |
| baseline | — | debt_gdp | 103 | 5.64 | 11 |
| baseline | — | growth | 5 | 0.27 | 0 |
| baseline | — | ln_constantgdp | 2 | 0.11 | 0 |
| baseline | — | inflation_cpi | 7 | 0.38 | 1 |
| baseline | — | reserves | 70 | 3.83 | 3 |
| baseline | — | tt | 222 | 12.15 | 90 |
| output | — | Y_outcome | 65 | 3.56 | 60 |
| output | — | readiness_delta100 | 58 | 3.17 | 0 |
| output | — | vulnerability_delta100 | 58 | 3.17 | 0 |
| output | — | Y_lag | 65 | 3.56 | 24 |
| output | — | inflation_cpi | 7 | 0.38 | 1 |
| output | — | reserves | 70 | 3.83 | 27 |
| output | — | tt | 222 | 12.15 | 148 |
| doomloop | debt | b_outcome | 166 | 9.09 | 60 |
| doomloop | debt | readiness_delta100 | 58 | 3.17 | 0 |
| doomloop | debt | theta_hat_A | 150 | 8.21 | 0 |
| doomloop | debt | debt_gdp | 103 | 5.64 | 0 |
| doomloop | debt | mA_hat | 150 | 8.21 | 0 |
| doomloop | debt | YA_hat | 58 | 3.17 | 0 |
| doomloop | debt | debt_gdp_mA_hat | 150 | 8.21 | 0 |
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
| baseline | — | revenue | 220774.6159 | 135491.17 | 0.6137 | adequate |
| baseline | — | debt | 519926.9212 | 304445.22 | 0.5856 | adequate |
| baseline | — | interest_revenue | 0.0959 | 0.0468 | 0.488 | adequate |
| baseline | — | taxgdp | 8.1057 | 1.6723 | 0.2063 | adequate |
| baseline | — | ln_constantgdp | 2.735 | 0.308 | 0.1126 | adequate |
| output | — | Y_outcome | 0.0356 | 0.0314 | 0.8829 | adequate |
| output | — | Y_lag | 0.0358 | 0.0317 | 0.8838 | adequate |
| output | — | readiness_delta100 | 0.0882 | 0.0396 | 0.4495 | adequate |
| output | — | vulnerability_delta100 | 0.0564 | 0.024 | 0.426 | adequate |
| output | — | inflation_cpi | 0.0675 | 0.051 | 0.7564 | adequate |
| output | — | reserves | 0.1654 | 0.0764 | 0.4617 | adequate |
| output | — | tt | 0.1797 | 0.1612 | 0.8968 | adequate |
| doomloop | debt | b_outcome | 0.0635 | 0.062 | 0.9756 | adequate |
| doomloop | debt | theta_hat_A | 0.1001 | 0.0535 | 0.534 | adequate |
| doomloop | debt | debt_gdp | 0.3516 | 0.1708 | 0.4857 | adequate |
| doomloop | debt | mA_hat | 0.0571 | 0.0263 | 0.4599 | adequate |
| doomloop | debt | YA_hat | 0.0178 | 0.0077 | 0.4319 | adequate |
| doomloop | debt | debt_gdp_mA_hat | 0.0991 | 0.0522 | 0.5266 | adequate |
| doomloop | debt | readiness_delta100 | 0.0882 | 0.0399 | 0.4526 | adequate |
| doomloop | debt | vulnerability_delta100 | 0.0561 | 0.0242 | 0.4319 | adequate |
| doomloop | debt | growth | 0.0361 | 0.0319 | 0.8821 | adequate |
| doomloop | debt | ln_constantgdp | 2.785 | 0.2727 | 0.0979 | adequate |
| doomloop | debt | inflation_cpi | 0.0542 | 0.0416 | 0.7676 | adequate |
| doomloop | debt | reserves | 0.1669 | 0.0767 | 0.4596 | adequate |
| doomloop | debt | tt | 0.1826 | 0.1609 | 0.8807 | adequate |
| doomloop | ready | A_outcome | 0.0199 | 0.0196 | 0.988 | adequate |
| doomloop | ready | theta_hat_A | 0.1013 | 0.0535 | 0.5281 | adequate |
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
| baseline | vulnerability_delta100 | 1.5428 | 0.6482 | 2.0095 |
| baseline | readiness_delta100 | 1.4738 | 0.6785 | 2.0095 |
| baseline | debt_gdp | 1.2729 | 0.7856 | 2.0095 |
| baseline | growth | 1.0721 | 0.9328 | 2.0095 |
| baseline | ln_constantgdp | 1.1997 | 0.8335 | 2.0095 |
| baseline | inflation_cpi | 1.0453 | 0.9567 | 2.0095 |
| baseline | reserves | 1.081 | 0.925 | 2.0095 |
| baseline | tt | 1.0278 | 0.973 | 2.0095 |
| output | readiness_delta100 | 1.2024 | 0.8317 | 1.5871 |
| output | vulnerability_delta100 | 1.2146 | 0.8233 | 1.5871 |
| output | Y_lag | 1.0322 | 0.9688 | 1.5871 |
| output | inflation_cpi | 1.0213 | 0.9791 | 1.5871 |
| output | reserves | 1.0076 | 0.9925 | 1.5871 |
| output | tt | 1.0241 | 0.9765 | 1.5871 |
| output | c_A_Y | 1.3396 | 0.7465 | 1.8056 |
| output | c_X_Y | 1.2663 | 0.7897 | 1.8056 |
| output | int_AX_Y | 1.2597 | 0.7938 | 1.8056 |
| output | Y_lag | 1.0329 | 0.9681 | 1.8056 |
| output | inflation_cpi | 1.0284 | 0.9724 | 1.8056 |
| output | reserves | 1.0095 | 0.9906 | 1.8056 |
| output | tt | 1.0255 | 0.9752 | 1.8056 |


绝对相关系数不低于 0.60 的非重复变量对：

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |

## 6. 统计与程序验证

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | F | 分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 10.5038 | 2 | 1,080 | <0.001 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 10.9001 | 1 | 1,080 | <0.001 |
| baseline | Interact_AX | c_A = int_AX = 0 | 7.0029 | 2 | 1,080 | <0.001 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 1.2404 | 1 | 1,080 | 0.266 |
| baseline | Interact_all | c_A = int_AB = 0 | 14.3758 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AX = 0 | 11.7647 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 9.584 | 3 | 1,079 | <0.001 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 8.9129 | 2 | 1,079 | <0.001 |
| output | Y5_macro | inflation control zero | 0.5251 | 1 | 1,371 | 0.469 |
| output | Y7_layer2_A | external controls jointly zero | 7.2788 | 2 | 1,369 | <0.001 |
| output | Y7_layer2_A | all controls jointly zero | 5.0126 | 3 | 1,369 | 0.002 |
| output | Y8_interact_core | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 1.3485 | 2 | 1,371 | 0.260 |
| output | Y8_interact_core | interaction zero: int_AX_Y = 0 | 2.6957 | 1 | 1,371 | 0.101 |
| output | Y9_interact_macro | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 1.5136 | 2 | 1,370 | 0.220 |
| output | Y9_interact_macro | interaction zero: int_AX_Y = 0 | 3.0117 | 1 | 1,370 | 0.083 |
| output | Y10_interact_full | adaptation terms jointly zero: c_A_Y = int_AX_Y = 0 | 1.3014 | 2 | 1,368 | 0.272 |
| output | Y10_interact_full | interaction zero: int_AX_Y = 0 | 2.4875 | 1 | 1,368 | 0.115 |
| output | Y9_interact_macro | inflation control zero | 0.6984 | 1 | 1,370 | 0.403 |
| output | Y10_interact_full | external controls jointly zero | 6.9038 | 2 | 1,368 | 0.001 |
| output | Y10_interact_full | all controls jointly zero | 4.8191 | 3 | 1,368 | 0.002 |
| doomloop | DN3_full | low- and high-branch coefficients jointly zero | 1.3019 | 2 | 1,338 | 0.272 |
| doomloop | DN3_full | macro controls jointly zero | 4.8922 | 1 | 1,338 | 0.027 |
| doomloop | DN3_full | external controls jointly zero | 5.6395 | 2 | 1,338 | 0.004 |
| doomloop | DN3_full | all controls jointly zero | 6.1058 | 3 | 1,338 | <0.001 |
| doomloop | RDN3_full | branches jointly zero; debt-equation cutoff | 0.0418 | 2 | 1,354 | 0.959 |
| doomloop | RDN3_full | macro controls jointly zero | 0.6232 | 1 | 1,354 | 0.430 |
| doomloop | RDN3_full | external controls jointly zero | 0.8263 | 2 | 1,354 | 0.438 |
| doomloop | RDN3_full | all controls jointly zero | 0.9956 | 3 | 1,354 | 0.394 |

### 6.2 代数、映射与 hinge 公式

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | Y(t+1) equals F.ConstantGDP/ConstantGDP | 0 | 1.00e-12 | 通过 |
| theta | Y(t) equals ConstantGDP/L.ConstantGDP | 0 | 1.00e-12 | 通过 |
| theta | b_it equals debt_gdp exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 5.55e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw output formula | 1.39e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl output margin | 0 | 1.00e-12 | 通过 |
| theta | theta component identity | 0 | 1.00e-12 | 通过 |
| doomloop | theta uses debt_gdp*mA_hat + YA_hat | 0 | 1.00e-10 | 通过 |
| doomloop | b_it maps exactly to debt_gdp | 0 | 1.00e-10 | 通过 |
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
| baseline | Layer2_A | vulnerability_delta100 | -0.0854 | -0.0854 | 1.23e-14 | 2.98e-16 |
| baseline | Layer2_A | readiness_delta100 | -0.0588 | -0.0588 | 2.64e-15 | 4.51e-17 |
| baseline | Layer2_A | debt_gdp | 0.0455 | 0.0455 | 4.77e-15 | 9.72e-16 |
| baseline | Layer2_A | growth | -0.1945 | -0.1945 | 2.55e-15 | 9.71e-17 |
| baseline | Layer2_A | ln_constantgdp | 0.0146 | 0.0146 | 1.13e-14 | 1.86e-15 |
| baseline | Layer2_A | inflation_cpi | 0.1846 | 0.1846 | 3.05e-16 | 6.07e-16 |
| baseline | Layer2_A | reserves | -0.0032 | -0.0032 | 4.28e-15 | 1.12e-15 |
| baseline | Layer2_A | tt | 0.0062 | 0.0062 | 1.47e-16 | 2.29e-16 |
| baseline | Interact_all | c_A | -0.0918 | -0.0918 | 1.48e-14 | 6.18e-16 |
| baseline | Interact_all | c_X | -0.0611 | -0.0611 | 3.92e-14 | 5.59e-15 |
| baseline | Interact_all | c_b | 0.0472 | 0.0472 | 8.17e-15 | 5.56e-15 |
| baseline | Interact_all | int_AB | -0.1581 | -0.1581 | 1.26e-14 | 1.80e-15 |
| baseline | Interact_all | int_AX | 0.3615 | 0.3615 | 2.18e-13 | 7.03e-14 |
| baseline | Interact_all | growth | -0.2038 | -0.2038 | 5.83e-16 | 3.96e-16 |
| baseline | Interact_all | ln_constantgdp | 0.0209 | 0.0209 | 1.77e-14 | 2.59e-14 |
| baseline | Interact_all | inflation_cpi | 0.1842 | 0.1842 | 2.66e-15 | 1.21e-16 |
| baseline | Interact_all | reserves | 0.0007 | 0.0007 | 6.24e-15 | 2.40e-15 |
| baseline | Interact_all | tt | 0.0039 | 0.0039 | 1.45e-15 | 3.64e-17 |
| tax | Spread_Interact_all | c_A | -0.0918 | -0.0918 | 1.33e-14 | 2.12e-15 |
| tax | Spread_Interact_all | c_X | -0.0611 | -0.0611 | 3.75e-14 | 3.93e-15 |
| tax | Spread_Interact_all | c_b | 0.0472 | 0.0472 | 7.60e-15 | 2.04e-15 |
| tax | Spread_Interact_all | int_AB | -0.1581 | -0.1581 | 1.22e-14 | 1.97e-15 |
| tax | Spread_Interact_all | int_AX | 0.3615 | 0.3615 | 2.04e-13 | 8.09e-14 |
| tax | Spread_Interact_all | growth | -0.2038 | -0.2038 | 7.77e-16 | 4.09e-16 |
| tax | Spread_Interact_all | ln_constantgdp | 0.0209 | 0.0209 | 1.65e-14 | 2.24e-14 |
| tax | Spread_Interact_all | inflation_cpi | 0.1842 | 0.1842 | 2.19e-15 | 1.28e-16 |
| tax | Spread_Interact_all | reserves | 0.0007 | 0.0007 | 5.96e-15 | 1.09e-15 |
| tax | Spread_Interact_all | tt | 0.0039 | 0.0039 | 1.52e-15 | 2.43e-16 |
| tax | Y7_layer2_A | vulnerability_delta100 | -0.0136 | -0.0136 | 1.70e-15 | 7.15e-16 |
| tax | Y7_layer2_A | readiness_delta100 | 0.002 | 0.002 | 1.28e-14 | 4.37e-16 |
| tax | Y7_layer2_A | Y_lag | 0.2737 | 0.2737 | 5.22e-15 | 3.99e-14 |
| tax | Y7_layer2_A | inflation_cpi | -0.0168 | -0.0168 | 4.47e-15 | 8.67e-17 |
| tax | Y7_layer2_A | reserves | 0.0303 | 0.0303 | 5.01e-15 | 2.76e-16 |
| tax | Y7_layer2_A | tt | -0.0031 | -0.0031 | 9.05e-16 | 4.16e-17 |
| tax | Y10_interact_full | c_A_Y | -0.0115 | -0.0115 | 1.43e-14 | 5.90e-16 |
| tax | Y10_interact_full | c_X_Y | 0.0007 | 0.0007 | 2.96e-16 | 1.03e-15 |
| tax | Y10_interact_full | int_AX_Y | 0.3168 | 0.3168 | 3.86e-14 | 1.03e-15 |
| tax | Y10_interact_full | Y_lag | 0.2724 | 0.2724 | 5.11e-15 | 3.65e-14 |
| tax | Y10_interact_full | inflation_cpi | -0.019 | -0.019 | 4.72e-15 | 3.37e-16 |
| tax | Y10_interact_full | reserves | 0.0295 | 0.0295 | 4.90e-15 | 3.23e-16 |
| tax | Y10_interact_full | tt | -0.0034 | -0.0034 | 9.48e-16 | 4.51e-17 |
| doomloop | theta | beta_L | -0.6578 | -0.6578 | 2.74e-13 | 1.43e-13 |
| doomloop | theta | beta_H | -0.4398 | -0.4398 | 1.34e-13 | 2.02e-14 |
| doomloop | b | beta_L | -0.0641 | -0.0641 | 1.77e-14 | 4.02e-16 |
| doomloop | b | beta_H | -0.2759 | -0.2759 | 4.87e-14 | 1.55e-15 |
| doomloop | mA | beta_L | -0.2342 | -0.2342 | 6.78e-13 | 4.18e-13 |
| doomloop | mA | beta_H | -1.1378 | -1.1378 | 1.14e-13 | 8.94e-15 |
| doomloop | YA | beta_L | -3.825 | -3.825 | 1.07e-12 | 7.66e-14 |
| doomloop | YA | beta_H | -3.9763 | -3.9763 | 6.11e-13 | 6.93e-14 |
| doomloop | b*mA | beta_L | 0.9308 | 0.9308 | 2.23e-12 | 4.71e-14 |
| doomloop | b*mA | beta_H | -0.4124 | -0.4124 | 7.39e-14 | 3.13e-14 |
| doomloop | readiness | delta_L | -0.0139 | -0.0139 | 4.37e-16 | 7.49e-15 |
| doomloop | readiness | delta_H | -0.0169 | -0.0169 | 4.47e-15 | 1.83e-14 |

### 6.4 Cutoff 最小 RSS 与样本加总

| Criterion | 记录 cutoff | 最小 RSS | cutoff RSS | \|差值\| | N | N_low | N_high | 加总 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | 0.0484 | 3.680183 | 3.680183 | 0 | 1,433 | 916 | 517 | 通过 | 通过 |
| $b_{it}$ | 0.6447 | 3.668044 | 3.668044 | 0 | 1,433 | 925 | 508 | 通过 | 通过 |
| $\widehat m^A_{it}$ | 0.0259 | 3.67028 | 3.67028 | 0 | 1,433 | 145 | 1,288 | 通过 | 通过 |
| $\widehat Y^A_{it}$ | 0.0095 | 3.670481 | 3.670481 | 0 | 1,433 | 1,259 | 174 | 通过 | 通过 |
| $b_{it}\widehat m^A_{it}$ | 0.0049 | 3.681214 | 3.681214 | 0 | 1,433 | 145 | 1,288 | 通过 | 通过 |

Readiness cutoff 继承检查：

| 方程 | cutoff 来源 | cutoff | 债务 profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| debt | debt_full | 0.0484 | 3.6802 | 3.6802 | 0 | 通过 |
| ready_debt | debt_full | 0.0484 | 3.6802 | 3.6802 | 0 | 通过 |

### 6.5 五判据共同样本与拟合排序

| RSS 排名 | Criterion | N | RSS | Within R2 | 理论方向 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | $b_{it}$ | 1,433 | 3.668044 | 0.3332 | Partial (-,-) |
| 2 | $\widehat m^A_{it}$ | 1,433 | 3.67028 | 0.3328 | Partial (-,-) |
| 3 | $\widehat Y^A_{it}$ | 1,433 | 3.670481 | 0.3327 | Partial (-,-) |
| 4 | $\widehat\theta^A_{it}$ | 1,433 | 3.680183 | 0.331 | Partial (-,-) |
| 5 | $b_{it}\widehat m^A_{it}$ | 1,433 | 3.681214 | 0.3308 | Match (+,-) |

## 7. 图形 QA

| 图形 | 字节 | 状态 |
| --- | ---: | ---: |
| debt_marginal_effect_no_b.png | 180,534 | 通过 |
| debt_marginal_effect_no_b.pdf | 73,417 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.png | 171,170 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.pdf | 71,939 | 通过 |
| kink_marginal_effects_no_state.png | 226,852 | 通过 |
| kink_marginal_effects_no_state.pdf | 79,175 | 通过 |

债务图和 readiness 图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0。Readiness 图的竖直线来自债务全控制方程。

## 8. Required Caveats for Stakeholders

- 当前 `vce(robust)` 处理异方差，但不处理同一国家内序列相关。
- theta 是两条上游回归的生成变量；cutoff 又在同一样本中搜索，常规 p 值没有覆盖联合不确定性。
- 比较五种判据会引入模型选择和多重比较问题；最低 RSS 仅代表本样本内拟合。
- 固定效应相关性结果不支持因果措辞。

## 9. 原始输出索引

完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。
