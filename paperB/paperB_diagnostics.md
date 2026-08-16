# Paper B：统计检验与数据检查

> 生成时间：2026-08-16 18:00（Asia/Shanghai）。本文件验证数据、样本、公式、估计器、cutoff 与竞争判据；正式公式和回归表见 `paperB_results.md`。

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

唯一原始分析输入是 `data0804/invest_panel_weo.csv`。源百分数、比率和 0—100 指数先除以 100；金额变量不缩放。`ln_constantgdp` 只进入 baseline 及 empirical-theta 的 baseline 复核路径。Doomloop 从 empirical-theta panel 读取已换算变量，并单独将源 `interest_revenue` 除以 100。

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
| reserves | 1,757 | 0.1664 | 0.188 | 0.0034 | 0.1134 | 1.4339 |
| tt | 1,605 | 1.0069 | 0.1859 | 0.3188 | 0.9942 | 2.7308 |
| ln_constantgdp | 1,825 | 8.1897 | 2.735 | 2.9628 | 7.8151 | 16.3252 |

### 3.2 Tax 与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| taxbase_lead | tax | 1,414 | 0.2053 | 0.0804 | 0.0213 | 0.1974 | 0.4977 |
| taxbase_lag | tax | 1,414 | 0.2052 | 0.0806 | 0.0213 | 0.1971 | 0.4977 |
| mA_hat_spread_ratio | theta_support | 1,103 | 0.0863 | 0.0752 | -0.0358 | 0.0697 | 0.4389 |
| mA_hat | theta_support | 1,103 | 0.0863 | 0.0752 | -0.0358 | 0.0697 | 0.4389 |
| spread_saving_component | theta_support | 1,103 | 0.08 | 0.1259 | -0.0023 | 0.0376 | 1.0041 |
| TA_hat | theta_support | 1,103 | -0.0352 | 0.0191 | -0.0655 | -0.0402 | 0.0186 |
| theta_hat_A | theta_support | 1,103 | 0.0449 | 0.1258 | -0.0642 | 0.0104 | 0.9703 |
| theta_hat_A | all_constructible | 1,677 | 0.0411 | 0.1207 | -0.0642 | 0.0097 | 1.3261 |

### 3.3 Doomloop 主规格与判据变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_no_b | debt | b_outcome | dependent_variable | 1,433 | 0.0077 | 0.0635 | -0.5417 | 0.0019 | 0.4186 |
| debt_no_b | debt | debt_kink_low | regressor | 1,433 | 0.0237 | 0.0225 | 0 | 0.0193 | 0.0921 |
| debt_no_b | debt | debt_kink_high | regressor | 1,433 | 0.0174 | 0.0622 | 0 | 0 | 0.6243 |
| debt_no_b | debt | vulnerability100 | regressor | 1,433 | 0.3827 | 0.0786 | 0.251 | 0.3684 | 0.5808 |
| debt_no_b | debt | growth | regressor | 1,433 | 0.0338 | 0.0361 | -0.1455 | 0.0344 | 0.2462 |
| debt_no_b | debt | inflation_cpi | regressor | 1,433 | 0.0462 | 0.0542 | -0.0177 | 0.0314 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,433 | 0.1627 | 0.1669 | 0.0034 | 0.1178 | 1.4339 |
| debt_no_b | debt | tt | regressor | 1,433 | 1.0089 | 0.1826 | 0.3188 | 0.9942 | 2.7308 |
| debt_no_b | debt | readiness100 | construction_input | 1,433 | 0.5057 | 0.1462 | 0.2021 | 0.4994 | 0.8072 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,433 | 0.0415 | 0.1225 | -0.0642 | 0.0101 | 1.3261 |
| debt_no_b | debt | debt_gdp | construction_input | 1,433 | 0.5824 | 0.3516 | 0.039 | 0.5064 | 2.6096 |
| debt_no_b | debt | mA_hat | construction_input | 1,433 | 0.0791 | 0.0741 | -0.0358 | 0.0638 | 0.5081 |
| debt_no_b | debt | TA_hat | construction_input | 1,433 | -0.0306 | 0.0208 | -0.0655 | -0.0344 | 0.0218 |
| debt_no_b | debt | bmA_hat | construction_input | 1,433 | 0.0721 | 0.1228 | -0.0023 | 0.0322 | 1.3261 |
| ready_no_lag_debt_cutoff | ready_debt | A_outcome | dependent_variable | 1,458 | 0.5029 | 0.1442 | 0.2021 | 0.4965 | 0.7973 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 1,458 | 0.0021 | 0.0028 | -0.0063 | 0.0016 | 0.0208 |
| ready_no_lag_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 1,458 | 0.0029 | 0.0102 | -0.0027 | 0 | 0.1542 |
| ready_no_lag_debt_cutoff | ready_debt | vulnerability100 | regressor | 1,458 | 0.3817 | 0.0792 | 0.251 | 0.3673 | 0.5808 |
| ready_no_lag_debt_cutoff | ready_debt | growth | regressor | 1,458 | 0.0331 | 0.0355 | -0.1455 | 0.0332 | 0.2462 |
| ready_no_lag_debt_cutoff | ready_debt | inflation_cpi | regressor | 1,458 | 0.0482 | 0.0564 | -0.0177 | 0.0331 | 0.723 |
| ready_no_lag_debt_cutoff | ready_debt | reserves | regressor | 1,458 | 0.1491 | 0.1353 | 0.0034 | 0.1149 | 1.4339 |
| ready_no_lag_debt_cutoff | ready_debt | tt | regressor | 1,458 | 1.0091 | 0.1831 | 0.3188 | 0.9945 | 2.7308 |
| ready_no_lag_debt_cutoff | ready_debt | interest_revenue | construction_input | 1,458 | 0.0857 | 0.0979 | -0.069 | 0.0567 | 0.7987 |
| ready_no_lag_debt_cutoff | ready_debt | theta_hat_A | construction_input | 1,458 | 0.0404 | 0.1234 | -0.0642 | 0.0092 | 1.3261 |

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
| baseline | — | ln_constantgdp | 2 | 0.11 | 0 |
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
| baseline | — | vulnerability_delta100 | 5.8659 | 2.8009 | 0.4775 | adequate |
| baseline | — | readiness100 | 0.1452 | 0.0434 | 0.2986 | adequate |
| baseline | — | readiness_delta100 | 8.9619 | 4.1177 | 0.4595 | adequate |
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
| tax | — | taxbase_lead | 0.0804 | 0.0162 | 0.2011 | adequate |
| tax | — | taxbase_lag | 0.0806 | 0.0163 | 0.202 | adequate |
| tax | — | readiness100 | 0.1456 | 0.0402 | 0.2761 | adequate |
| tax | — | vulnerability100 | 0.0798 | 0.0096 | 0.1204 | adequate |
| tax | — | growth | 0.0362 | 0.0318 | 0.8794 | adequate |
| tax | — | inflation_cpi | 0.0525 | 0.0399 | 0.7606 | adequate |
| tax | — | reserves | 0.1682 | 0.0771 | 0.4586 | adequate |
| tax | — | tt | 0.1853 | 0.1593 | 0.8598 | adequate |
| doomloop | debt | b_outcome | 0.0635 | 0.062 | 0.9756 | adequate |
| doomloop | debt | theta_hat_A | 0.1225 | 0.0671 | 0.5478 | adequate |
| doomloop | debt | debt_gdp | 0.3516 | 0.1708 | 0.4857 | adequate |
| doomloop | debt | mA_hat | 0.0741 | 0.036 | 0.4861 | adequate |
| doomloop | debt | TA_hat | 0.0208 | 0.0026 | 0.1253 | adequate |
| doomloop | debt | bmA_hat | 0.1228 | 0.0674 | 0.5486 | adequate |
| doomloop | debt | readiness100 | 0.1462 | 0.0403 | 0.2756 | adequate |
| doomloop | debt | vulnerability100 | 0.0786 | 0.0099 | 0.1253 | adequate |
| doomloop | debt | growth | 0.0361 | 0.0319 | 0.8821 | adequate |
| doomloop | debt | inflation_cpi | 0.0542 | 0.0416 | 0.7676 | adequate |
| doomloop | debt | reserves | 0.1669 | 0.0767 | 0.4596 | adequate |
| doomloop | debt | tt | 0.1826 | 0.1609 | 0.8807 | adequate |
| doomloop | ready | A_outcome | 0.1442 | 0.0389 | 0.2696 | adequate |
| doomloop | ready | theta_hat_A | 0.1234 | 0.0665 | 0.5384 | adequate |
| doomloop | ready | interest_revenue | 0.0979 | 0.0455 | 0.4646 | adequate |
| doomloop | ready | vulnerability100 | 0.0792 | 0.0102 | 0.1284 | adequate |
| doomloop | ready | growth | 0.0355 | 0.0312 | 0.8803 | adequate |
| doomloop | ready | inflation_cpi | 0.0564 | 0.0434 | 0.7693 | adequate |
| doomloop | ready | reserves | 0.1353 | 0.0755 | 0.5578 | adequate |
| doomloop | ready | tt | 0.1831 | 0.1615 | 0.8821 | adequate |

## 5. 共线性、相关性与系数变化

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline | vulnerability100 | 1.3 | 0.7692 | 2.0012 |
| baseline | readiness100 | 1.0449 | 0.957 | 2.0012 |
| baseline | debt_gdp | 1.2473 | 0.8017 | 2.0012 |
| baseline | growth | 1.0585 | 0.9447 | 2.0012 |
| baseline | ln_constantgdp | 1.4907 | 0.6708 | 2.0012 |
| baseline | inflation_cpi | 1.048 | 0.9542 | 2.0012 |
| baseline | reserves | 1.1047 | 0.9052 | 2.0012 |
| baseline | tt | 1.0306 | 0.9703 | 2.0012 |
| tax | readiness100 | 1.045 | 0.9569 | 1.2958 |
| tax | vulnerability100 | 1.0392 | 0.9623 | 1.2958 |
| tax | taxbase_lag | 1.0453 | 0.9567 | 1.2958 |
| tax | growth | 1.0232 | 0.9773 | 1.2958 |
| tax | inflation_cpi | 1.029 | 0.9718 | 1.2958 |
| tax | reserves | 1.0358 | 0.9654 | 1.2958 |
| tax | tt | 1.0265 | 0.9742 | 1.2958 |
| tax | c_A_T | 1.1443 | 0.8739 | 1.6676 |
| tax | c_X_T | 1.1711 | 0.8539 | 1.6676 |
| tax | int_AX_T | 1.2346 | 0.81 | 1.6676 |
| tax | taxbase_lag | 1.0865 | 0.9204 | 1.6676 |
| tax | growth | 1.0235 | 0.977 | 1.6676 |
| tax | inflation_cpi | 1.029 | 0.9718 | 1.6676 |
| tax | reserves | 1.0475 | 0.9547 | 1.6676 |
| tax | tt | 1.029 | 0.9718 | 1.6676 |


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
| baseline | Interact_AB | c_A = int_AB = 0 | 26.9256 | 2 | 1,080 | <0.001 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 46.8133 | 1 | 1,080 | <0.001 |
| baseline | Interact_AX | c_A = int_AX = 0 | 8.4085 | 2 | 1,080 | <0.001 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 0.4928 | 1 | 1,080 | 0.483 |
| baseline | Interact_all | c_A = int_AB = 0 | 26.3373 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AX = 0 | 12.3562 | 2 | 1,079 | <0.001 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 18.031 | 3 | 1,079 | <0.001 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 23.66 | 2 | 1,079 | <0.001 |
| tax | T5_macro | macro controls jointly zero | 0.8499 | 2 | 1,322 | 0.428 |
| tax | T7_layer2_A | external controls jointly zero | 3.1203 | 2 | 1,320 | 0.044 |
| tax | T7_layer2_A | all controls jointly zero | 1.888 | 4 | 1,320 | 0.110 |
| tax | T8_interact_core | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 7.7369 | 2 | 1,323 | <0.001 |
| tax | T8_interact_core | interaction zero: int_AX_T = 0 | 12.5998 | 1 | 1,323 | <0.001 |
| tax | T9_interact_macro | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 7.6724 | 2 | 1,321 | <0.001 |
| tax | T9_interact_macro | interaction zero: int_AX_T = 0 | 12.381 | 1 | 1,321 | <0.001 |
| tax | T10_interact_full | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 8.9452 | 2 | 1,319 | <0.001 |
| tax | T10_interact_full | interaction zero: int_AX_T = 0 | 13.5917 | 1 | 1,319 | <0.001 |
| tax | T9_interact_macro | macro controls jointly zero | 0.8084 | 2 | 1,321 | 0.446 |
| tax | T10_interact_full | external controls jointly zero | 3.4806 | 2 | 1,319 | 0.031 |
| tax | T10_interact_full | all controls jointly zero | 2.0684 | 4 | 1,319 | 0.083 |
| doomloop | DN3_full | low- and high-branch coefficients jointly zero | 20.1167 | 2 | 1,339 | <0.001 |
| doomloop | DN3_full | macro controls jointly zero | 18.6988 | 2 | 1,339 | <0.001 |
| doomloop | DN3_full | external controls jointly zero | 7.3516 | 2 | 1,339 | <0.001 |
| doomloop | DN3_full | all controls jointly zero | 14.1626 | 4 | 1,339 | <0.001 |
| doomloop | RDN3_full | branches jointly zero; debt-equation cutoff | 30.4576 | 2 | 1,364 | <0.001 |
| doomloop | RDN3_full | macro controls jointly zero | 0.313 | 2 | 1,364 | 0.731 |
| doomloop | RDN3_full | external controls jointly zero | 5.7037 | 2 | 1,364 | 0.003 |
| doomloop | RDN3_full | all controls jointly zero | 3 | 4 | 1,364 | 0.018 |

### 6.2 代数、映射与 hinge 公式

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | T(t+1) equals exact F.taxgdp ratio | 0 | 1.00e-12 | 通过 |
| theta | T(t) equals current taxgdp ratio | 0 | 1.00e-12 | 通过 |
| theta | b_it equals debt_gdp exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 1.11e-16 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw tax formula | 2.43e-17 | 1.00e-12 | 通过 |
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
| baseline | Layer2_A | vulnerability100 | 0.0312 | 0.0312 | 9.13e-14 | 1.15e-13 |
| baseline | Layer2_A | readiness100 | -0.0672 | -0.0672 | 1.38e-14 | 3.02e-16 |
| baseline | Layer2_A | debt_gdp | 0.0464 | 0.0464 | 5.61e-15 | 1.68e-15 |
| baseline | Layer2_A | growth | -0.195 | -0.195 | 3.64e-15 | 1.80e-16 |
| baseline | Layer2_A | ln_constantgdp | 0.0179 | 0.0179 | 1.46e-14 | 1.80e-14 |
| baseline | Layer2_A | inflation_cpi | 0.1824 | 0.1824 | 3.89e-16 | 1.87e-16 |
| baseline | Layer2_A | reserves | -0.0014 | -0.0014 | 5.95e-15 | 7.98e-16 |
| baseline | Layer2_A | tt | 0.0067 | 0.0067 | 5.53e-16 | 9.14e-16 |
| baseline | Interact_all | c_A | -0.087 | -0.087 | 9.56e-15 | 1.96e-15 |
| baseline | Interact_all | c_X | 0.112 | 0.112 | 2.28e-14 | 8.92e-14 |
| baseline | Interact_all | c_b | 0.0526 | 0.0526 | 4.65e-15 | 2.38e-15 |
| baseline | Interact_all | int_AB | -0.2111 | -0.2111 | 1.92e-15 | 1.07e-15 |
| baseline | Interact_all | int_AX | -0.0101 | -0.0101 | 7.06e-14 | 4.16e-15 |
| baseline | Interact_all | growth | -0.172 | -0.172 | 4.50e-15 | 7.63e-17 |
| baseline | Interact_all | ln_constantgdp | 0.0178 | 0.0178 | 1.24e-14 | 3.13e-14 |
| baseline | Interact_all | inflation_cpi | 0.1845 | 0.1845 | 1.33e-15 | 7.49e-16 |
| baseline | Interact_all | reserves | -0.0045 | -0.0045 | 4.56e-15 | 1.17e-15 |
| baseline | Interact_all | tt | 0.0015 | 0.0015 | 1.99e-16 | 7.03e-16 |
| tax | Spread_Interact_all | c_A | -0.087 | -0.087 | 1.00e-14 | 2.53e-16 |
| tax | Spread_Interact_all | c_X | 0.112 | 0.112 | 1.82e-15 | 1.37e-14 |
| tax | Spread_Interact_all | c_b | 0.0526 | 0.0526 | 3.14e-15 | 1.29e-15 |
| tax | Spread_Interact_all | int_AB | -0.2111 | -0.2111 | 1.50e-15 | 6.31e-16 |
| tax | Spread_Interact_all | int_AX | -0.0101 | -0.0101 | 2.35e-14 | 2.76e-14 |
| tax | Spread_Interact_all | growth | -0.172 | -0.172 | 3.41e-15 | 3.47e-17 |
| tax | Spread_Interact_all | ln_constantgdp | 0.0178 | 0.0178 | 7.42e-15 | 7.20e-15 |
| tax | Spread_Interact_all | inflation_cpi | 0.1845 | 0.1845 | 1.44e-15 | 4.61e-16 |
| tax | Spread_Interact_all | reserves | -0.0045 | -0.0045 | 2.91e-15 | 1.56e-15 |
| tax | Spread_Interact_all | tt | 0.0015 | 0.0015 | 2.84e-17 | 4.82e-16 |
| tax | T7_layer2_A | vulnerability100 | 0.0534 | 0.0534 | 8.88e-15 | 3.75e-14 |
| tax | T7_layer2_A | readiness100 | -0.0228 | -0.0228 | 1.13e-14 | 2.24e-15 |
| tax | T7_layer2_A | taxbase_lag | 0.7325 | 0.7325 | 1.33e-14 | 5.55e-17 |
| tax | T7_layer2_A | growth | 0.0149 | 0.0149 | 1.44e-15 | 9.02e-17 |
| tax | T7_layer2_A | inflation_cpi | -0.0036 | -0.0036 | 1.01e-15 | 1.22e-16 |
| tax | T7_layer2_A | reserves | 0.0066 | 0.0066 | 8.80e-16 | 2.60e-17 |
| tax | T7_layer2_A | tt | -0.0029 | -0.0029 | 1.86e-16 | 6.14e-17 |
| tax | T10_interact_full | c_A_T | -0.0307 | -0.0307 | 1.13e-14 | 6.94e-17 |
| tax | T10_interact_full | c_X_T | 0.096 | 0.096 | 1.91e-14 | 1.47e-15 |
| tax | T10_interact_full | int_AX_T | 0.2646 | 0.2646 | 5.26e-14 | 1.47e-15 |
| tax | T10_interact_full | taxbase_lag | 0.7221 | 0.7221 | 1.40e-14 | 6.94e-16 |
| tax | T10_interact_full | growth | 0.0143 | 0.0143 | 1.52e-15 | 1.01e-16 |
| tax | T10_interact_full | inflation_cpi | -0.0035 | -0.0035 | 1.26e-15 | 6.42e-17 |
| tax | T10_interact_full | reserves | 0.0078 | 0.0078 | 1.04e-15 | 1.09e-16 |
| tax | T10_interact_full | tt | -0.0027 | -0.0027 | 1.92e-16 | 5.72e-17 |
| doomloop | theta | beta_L | 0.8029 | 0.8029 | 3.20e-14 | 4.72e-16 |
| doomloop | theta | beta_H | -0.4149 | -0.4149 | 6.27e-15 | 9.30e-16 |
| doomloop | b | beta_L | 0.1535 | 0.1535 | 4.47e-15 | 1.11e-15 |
| doomloop | b | beta_H | -0.2184 | -0.2184 | 3.64e-15 | 1.29e-15 |
| doomloop | mA | beta_L | 0.7219 | 0.7219 | 1.65e-14 | 4.52e-15 |
| doomloop | mA | beta_H | -1.0422 | -1.0422 | 1.55e-15 | 1.80e-15 |
| doomloop | TA | beta_L | -6.8817 | -6.8817 | 2.92e-13 | 1.19e-12 |
| doomloop | TA | beta_H | -2.1093 | -2.1093 | 2.51e-13 | 3.81e-12 |
| doomloop | b*mA | beta_L | 3.6927 | 3.6927 | 4.04e-14 | 1.39e-14 |
| doomloop | b*mA | beta_H | -0.449 | -0.449 | 5.55e-16 | 3.19e-16 |
| doomloop | readiness | delta_L | -4.6961 | -4.6961 | 1.87e-13 | 2.99e-14 |
| doomloop | readiness | delta_H | 0.084 | 0.084 | 1.90e-15 | 3.41e-15 |

### 6.4 Cutoff 最小 RSS 与样本加总

| Criterion | 记录 cutoff | 最小 RSS | cutoff RSS | \|差值\| | N | N_low | N_high | 加总 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | 0.0557 | 3.560598 | 3.560598 | 0 | 1,433 | 1,076 | 357 | 通过 | 通过 |
| $b_{it}$ | 0.6602 | 3.54162 | 3.54162 | 0 | 1,433 | 957 | 476 | 通过 | 通过 |
| $\widehat m^A_{it}$ | 0.0979 | 3.54133 | 3.54133 | 0 | 1,433 | 978 | 455 | 通过 | 通过 |
| $\widehat T^A_{it}$ | -0.0293 | 3.825233 | 3.825233 | 0 | 1,433 | 856 | 577 | 通过 | 通过 |
| $b_{it}\widehat m^A_{it}$ | 0.0141 | 3.535557 | 3.535557 | 0 | 1,433 | 431 | 1,002 | 通过 | 通过 |

Readiness cutoff 继承检查：

| 方程 | cutoff 来源 | cutoff | 债务 profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| debt | debt_full | 0.0557 | 3.5606 | 3.5606 | 0 | 通过 |
| ready_debt | debt_full | 0.0557 | 3.5606 | 3.5606 | 0 | 通过 |

### 6.5 五判据共同样本与拟合排序

| RSS 排名 | Criterion | N | RSS | Within R2 | 理论方向 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | $b_{it}\widehat m^A_{it}$ | 1,433 | 3.535557 | 0.3573 | Match (+,-) |
| 2 | $\widehat m^A_{it}$ | 1,433 | 3.54133 | 0.3562 | Match (+,-) |
| 3 | $b_{it}$ | 1,433 | 3.54162 | 0.3561 | Match (+,-) |
| 4 | $\widehat\theta^A_{it}$ | 1,433 | 3.560598 | 0.3527 | Match (+,-) |
| 5 | $\widehat T^A_{it}$ | 1,433 | 3.825233 | 0.3046 | Partial (-,-) |

## 7. 图形 QA

| 图形 | 字节 | 状态 |
| --- | ---: | ---: |
| debt_marginal_effect_no_b.png | 183,071 | 通过 |
| debt_marginal_effect_no_b.pdf | 74,348 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.png | 182,166 | 通过 |
| readiness_marginal_effect_debt_cutoff_no_lag.pdf | 72,479 | 通过 |
| kink_marginal_effects_no_state.png | 229,300 | 通过 |
| kink_marginal_effects_no_state.pdf | 80,533 | 通过 |

债务图和 readiness 图均在连续 theta 网格中显式插入债务 cutoff 节点，并在该点把边际效应定义为 0。Readiness 图的竖直线来自债务全控制方程。

## 8. Required Caveats for Stakeholders

- 当前 `vce(robust)` 处理异方差，但不处理同一国家内序列相关。
- theta 是两条上游回归的生成变量；cutoff 又在同一样本中搜索，常规 p 值没有覆盖联合不确定性。
- 比较五种判据会引入模型选择和多重比较问题；最低 RSS 仅代表本样本内拟合。
- 固定效应相关性结果不支持因果措辞。

## 9. 原始输出索引

完整 CSV、DTA 和日志保存在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/` 与 `doomloop/stata_outputs/`。本文件不替代这些机器可读审计材料。
