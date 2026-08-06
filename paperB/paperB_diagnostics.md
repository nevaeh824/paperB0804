# Paper B：统计检验与数据检查

> 生成时间：2026-08-07 02:11（Asia/Shanghai）。本文件汇总三个板块的诊断、样本审计、单位审计、稳健性检验与验证结果；正式公式和回归表见 `paperB_results.md`。

## 1. 总体评估：可在明确限制条件下使用

单位换算检查通过 28/28 项；代数/构造检查通过 22/22 项；cutoff 最小 RSS 复核通过 4/4 项。当前结果在代码一致性和样本内计算层面通过，但仍属于“Share with caveats”：生成 theta、样本内 cutoff 搜索和面板相关推断的不确定性尚未由完整流程 bootstrap 与国家聚类标准误覆盖。

## 2. 数据来源、单位与时序检查

唯一原始输入是 `data0804/invest_panel_weo.csv`。所有源百分数、比率和 0—100 指数（包括 `taxgdp`）在读入后除以 100；金额变量 `revenue`、`debt`、`CurrentGDP` 不缩放。`ln_currentgdp=ln(CurrentGDP)` 仅用于仍包含规模控制的方程。关键因变量的精确定义为：

- $\widetilde T_{i,t+1}^{(t)}=(taxgdp_{i,t+1}\times0.01)CurrentGDP_{i,t+1}/CurrentGDP_{it}$。
- $\widetilde T_{it}^{(t-1)}=taxgdp_{it}\times0.01$。
- $\Delta d_{i,t+1}^{(t)}=(debt_{i,t+1}-debt_{it})/CurrentGDP_{it}$，不乘 100。
- $J_{it}=A_{it}-A_{i,t-1}$，其中 A 已经是 0—1 比率。

### 2.1 基准单位换算审计

| 变量 | 源最小值 | 源最大值 | 比率最小值 | 比率最大值 | 最大换算误差 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bond_spreads | -3.4057 | 34.3087 | -0.0341 | 0.3431 | 0 | 通过 |
| bond_10y | -0.5059 | 35.2028 | -0.0051 | 0.352 | 0 | 通过 |
| vulnerability100 | 25.103 | 58.08 | 0.251 | 0.5808 | 0 | 通过 |
| readiness100 | 17.9342 | 80.7202 | 0.1793 | 0.8072 | 0 | 通过 |
| growth | -16.04 | 24.624 | -0.1604 | 0.2462 | 0 | 通过 |
| inflation_cpi | -3.967 | 197.3 | -0.0397 | 1.973 | 0 | 通过 |
| debt_gdp | 0.052 | 260.964 | 0.0005 | 2.6096 | 0 | 通过 |
| PrimaryBalance_gdp | -29.952 | 23.449 | -0.2995 | 0.2345 | 0 | 通过 |
| reserves | 0.0001 | 152.7072 | 1.31e-06 | 1.5271 | 0 | 通过 |
| tt | 31.8761 | 273.0755 | 0.3188 | 2.7308 | 0 | 通过 |
| Revenue_gdp | 3.634 | 60.918 | 0.0363 | 0.6092 | 0 | 通过 |
| OverallBalance_gdp | -32.145 | 24.668 | -0.3214 | 0.2467 | 0 | 通过 |
| interest_revenue | -14.8211 | 79.8698 | -0.1482 | 0.7987 | 0 | 通过 |

Baseline 执行 13 项单位审计；Empirical-theta 在此基础上加入 `taxgdp`，执行 14 项审计；doomloop 从已审计的 theta panel 读入并对关键上游比例变量复核。全部检查的原始 CSV 保留在各板块 `stata_outputs` 目录。

## 3. 样本覆盖与描述性统计

| 固定样本 | N | 国家数 | 年份数 | 基准年份范围 |
| --- | ---: | ---: | ---: | ---: |
| Baseline 共同样本 | 1,286 | 65 | 26 | 1998–2023 |
| Tax 共同样本 | 1,533 | 65 | 28 | 1995–2022 |
| Doomloop 债务方程 | 1,552 | 65 | 28 | 1995–2022 |
| Doomloop readiness 方程 | 1,571 | 64 | 28 | 1996–2023 |

### 3.1 Baseline 输入变量（全数据非缺失分布）

| 变量 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bond_spreads | 1,447 | 0.0229 | 0.0452 | -0.0341 | 0.0061 | 0.3431 |
| vulnerability100 | 1,914 | 0.3818 | 0.0781 | 0.251 | 0.3662 | 0.5808 |
| readiness100 | 1,914 | 0.4986 | 0.1423 | 0.1793 | 0.4943 | 0.8072 |
| growth | 1,961 | 0.0341 | 0.0358 | -0.1604 | 0.035 | 0.2462 |
| inflation_cpi | 1,965 | 0.0565 | 0.1062 | -0.0397 | 0.0314 | 1.973 |
| debt_gdp | 1,866 | 0.5683 | 0.3443 | 0.0005 | 0.5058 | 2.6096 |
| reserves | 1,896 | 0.056 | 0.1249 | 1.31e-06 | 0.0203 | 1.5271 |
| tt | 1,730 | 1.0054 | 0.1831 | 0.3188 | 0.995 | 2.7308 |
| ln_currentgdp | 1,970 | 7.5434 | 2.9805 | 0.6323 | 7.3756 | 16.8549 |

### 3.2 Tax 与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| taxbase_lead | tax | 1,533 | 0.2202 | 0.0819 | 0.0256 | 0.2141 | 0.5254 |
| taxbase_lag | tax | 1,533 | 0.205 | 0.0797 | 0.0213 | 0.2001 | 0.4977 |
| mA_hat_spread_ratio | theta_support | 1,210 | 0.0813 | 0.0659 | -0.0263 | 0.0674 | 0.3945 |
| mA_hat | theta_support | 1,210 | 0.0813 | 0.0659 | -0.0263 | 0.0674 | 0.3945 |
| spread_saving_component | theta_support | 1,210 | 0.0723 | 0.1101 | -0.0016 | 0.0357 | 0.9026 |
| TA_hat | theta_support | 1,210 | -0.024 | 0.0148 | -0.0478 | -0.0277 | 0.0182 |
| theta_hat_A | theta_support | 1,210 | 0.0483 | 0.1098 | -0.0449 | 0.0173 | 0.8796 |
| theta_hat_A | all_constructible | 1,819 | 0.0446 | 0.1053 | -0.0453 | 0.0171 | 1.1775 |

### 3.3 四组 doomloop 回归变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_with_b | debt | delta_debt_lead | dependent_variable | 1,552 | 0.0494 | 0.0623 | -0.4484 | 0.0408 | 0.5778 |
| debt_with_b | debt | debt_kink_low | regressor | 1,552 | 0.0004 | 0.0013 | 0 | 0 | 0.0106 |
| debt_with_b | debt | debt_kink_high | regressor | 1,552 | 0.0374 | 0.0643 | 0 | 0.0177 | 0.6183 |
| debt_with_b | debt | debt_gdp | regressor | 1,552 | 0.5735 | 0.3469 | 0.039 | 0.5036 | 2.6096 |
| debt_with_b | debt | vulnerability100 | regressor | 1,552 | 0.3823 | 0.078 | 0.251 | 0.3675 | 0.5808 |
| debt_with_b | debt | growth | regressor | 1,552 | 0.0343 | 0.0366 | -0.1604 | 0.035 | 0.2462 |
| debt_with_b | debt | inflation_cpi | regressor | 1,552 | 0.0474 | 0.0579 | -0.0177 | 0.0305 | 0.723 |
| debt_with_b | debt | reserves | regressor | 1,552 | 0.0577 | 0.1326 | 2.41e-06 | 0.0189 | 1.5271 |
| debt_with_b | debt | tt | regressor | 1,552 | 1.0072 | 0.1799 | 0.3188 | 0.995 | 2.7308 |
| debt_with_b | debt | readiness100 | construction_input | 1,552 | 0.5054 | 0.1435 | 0.2021 | 0.5005 | 0.8072 |
| debt_with_b | debt | theta_hat_A | construction_input | 1,552 | 0.045 | 0.107 | -0.0449 | 0.0171 | 1.1775 |
| ready_with_lag | ready | J_readiness | dependent_variable | 1,571 | 0.0025 | 0.0183 | -0.22 | 0.0021 | 0.0823 |
| ready_with_lag | ready | ready_kink_low | regressor | 1,571 | 0.0006 | 0.0011 | -0.0033 | 0 | 0.0081 |
| ready_with_lag | ready | ready_kink_high | regressor | 1,571 | 0.0039 | 0.0107 | -0.0034 | 0 | 0.1419 |
| ready_with_lag | ready | readiness_lag | regressor | 1,571 | 0.5012 | 0.1411 | 0.2021 | 0.4971 | 0.7973 |
| ready_with_lag | ready | vulnerability100 | regressor | 1,571 | 0.3807 | 0.0783 | 0.251 | 0.3648 | 0.5808 |
| ready_with_lag | ready | growth | regressor | 1,571 | 0.0334 | 0.0359 | -0.1604 | 0.0337 | 0.2462 |
| ready_with_lag | ready | ln_currentgdp | regressor | 1,571 | 7.7309 | 3.0193 | 1.0006 | 7.4927 | 16.8549 |
| ready_with_lag | ready | inflation_cpi | regressor | 1,571 | 0.049 | 0.0588 | -0.0177 | 0.0323 | 0.723 |
| ready_with_lag | ready | reserves | regressor | 1,571 | 0.0492 | 0.115 | 2.41e-06 | 0.0188 | 1.5271 |
| ready_with_lag | ready | tt | regressor | 1,571 | 1.0066 | 0.1732 | 0.3188 | 0.995 | 2.7308 |
| ready_with_lag | ready | interest_revenue | construction_input | 1,571 | 0.0859 | 0.1002 | -0.069 | 0.0562 | 0.7987 |
| ready_with_lag | ready | theta_hat_A | construction_input | 1,571 | 0.0442 | 0.108 | -0.0449 | 0.0166 | 1.1775 |
| ready_with_lag | ready | readiness100 | construction_input | 1,571 | 0.5037 | 0.1416 | 0.2021 | 0.5001 | 0.7973 |
| debt_no_b | debt | delta_debt_lead | dependent_variable | 1,552 | 0.0494 | 0.0623 | -0.4484 | 0.0408 | 0.5778 |
| debt_no_b | debt | debt_kink_low | regressor | 1,552 | 0.0121 | 0.0141 | 0 | 0.0067 | 0.0578 |
| debt_no_b | debt | debt_kink_high | regressor | 1,552 | 0.0191 | 0.0577 | 0 | 0 | 0.5778 |
| debt_no_b | debt | vulnerability100 | regressor | 1,552 | 0.3823 | 0.078 | 0.251 | 0.3675 | 0.5808 |
| debt_no_b | debt | growth | regressor | 1,552 | 0.0343 | 0.0366 | -0.1604 | 0.035 | 0.2462 |
| debt_no_b | debt | inflation_cpi | regressor | 1,552 | 0.0474 | 0.0579 | -0.0177 | 0.0305 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,552 | 0.0577 | 0.1326 | 2.41e-06 | 0.0189 | 1.5271 |
| debt_no_b | debt | tt | regressor | 1,552 | 1.0072 | 0.1799 | 0.3188 | 0.995 | 2.7308 |
| debt_no_b | debt | readiness100 | construction_input | 1,552 | 0.5054 | 0.1435 | 0.2021 | 0.5005 | 0.8072 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,552 | 0.045 | 0.107 | -0.0449 | 0.0171 | 1.1775 |
| ready_no_lag | ready | J_readiness | dependent_variable | 1,571 | 0.0025 | 0.0183 | -0.22 | 0.0021 | 0.0823 |
| ready_no_lag | ready | ready_kink_low | regressor | 1,571 | 1.74e-06 | 0.0001 | -0.0008 | 0 | 0.0005 |
| ready_no_lag | ready | ready_kink_high | regressor | 1,571 | 0.0074 | 0.014 | -0.0046 | 0.0024 | 0.1787 |
| ready_no_lag | ready | vulnerability100 | regressor | 1,571 | 0.3807 | 0.0783 | 0.251 | 0.3648 | 0.5808 |
| ready_no_lag | ready | growth | regressor | 1,571 | 0.0334 | 0.0359 | -0.1604 | 0.0337 | 0.2462 |
| ready_no_lag | ready | ln_currentgdp | regressor | 1,571 | 7.7309 | 3.0193 | 1.0006 | 7.4927 | 16.8549 |
| ready_no_lag | ready | inflation_cpi | regressor | 1,571 | 0.049 | 0.0588 | -0.0177 | 0.0323 | 0.723 |
| ready_no_lag | ready | reserves | regressor | 1,571 | 0.0492 | 0.115 | 2.41e-06 | 0.0188 | 1.5271 |
| ready_no_lag | ready | tt | regressor | 1,571 | 1.0066 | 0.1732 | 0.3188 | 0.995 | 2.7308 |
| ready_no_lag | ready | interest_revenue | construction_input | 1,571 | 0.0859 | 0.1002 | -0.069 | 0.0562 | 0.7987 |
| ready_no_lag | ready | theta_hat_A | construction_input | 1,571 | 0.0442 | 0.108 | -0.0449 | 0.0166 | 1.1775 |
| ready_no_lag | ready | readiness100 | construction_input | 1,571 | 0.5037 | 0.1416 | 0.2021 | 0.5001 | 0.7973 |

## 4. 缺失值、重复键与固定效应可识别性

国家—年份重复键检查在三段流程中均为零；代码遇到重复键会直接终止，不会静默删除。各段共同样本在估计前锁定，逐步模型与 cutoff 候选使用相同观测。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 | 独占损失 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 525 | 26.62 | 331 |
| baseline | — | vulnerability100 | 58 | 2.94 | 0 |
| baseline | — | readiness100 | 58 | 2.94 | 0 |
| baseline | — | debt_gdp | 106 | 5.38 | 11 |
| baseline | — | growth | 11 | 0.56 | 0 |
| baseline | — | ln_currentgdp | 2 | 0.1 | 0 |
| baseline | — | inflation_cpi | 7 | 0.35 | 1 |
| baseline | — | reserves | 76 | 3.85 | 3 |
| baseline | — | tt | 242 | 12.27 | 94 |
| tax | — | taxbase_lead | 199 | 10.09 | 65 |
| tax | — | readiness100 | 58 | 2.94 | 0 |
| tax | — | vulnerability100 | 58 | 2.94 | 0 |
| tax | — | taxbase_lag | 150 | 7.61 | 11 |
| tax | — | growth | 11 | 0.56 | 1 |
| tax | — | inflation_cpi | 7 | 0.35 | 1 |
| tax | — | reserves | 76 | 3.85 | 20 |
| tax | — | tt | 242 | 12.27 | 163 |
| doomloop | debt | delta_debt_lead | 174 | 8.82 | 65 |
| doomloop | debt | readiness100 | 58 | 2.94 | 0 |
| doomloop | debt | theta_hat_A | 153 | 7.76 | 0 |
| doomloop | debt | debt_gdp | 106 | 5.38 | 0 |
| doomloop | debt | vulnerability100 | 58 | 2.94 | 0 |
| doomloop | debt | growth | 11 | 0.56 | 1 |
| doomloop | debt | inflation_cpi | 7 | 0.35 | 2 |
| doomloop | debt | reserves | 76 | 3.85 | 26 |
| doomloop | debt | tt | 242 | 12.27 | 159 |
| doomloop | ready | J_readiness | 124 | 6.29 | 0 |
| doomloop | ready | interest_revenue | 149 | 7.56 | 34 |
| doomloop | ready | readiness100 | 58 | 2.94 | 0 |
| doomloop | ready | theta_hat_A | 153 | 7.76 | 9 |
| doomloop | ready | readiness_lag | 124 | 6.29 | 0 |
| doomloop | ready | vulnerability100 | 58 | 2.94 | 0 |
| doomloop | ready | growth | 11 | 0.56 | 1 |
| doomloop | ready | ln_currentgdp | 2 | 0.1 | 0 |
| doomloop | ready | inflation_cpi | 7 | 0.35 | 1 |
| doomloop | ready | reserves | 76 | 3.85 | 27 |
| doomloop | ready | tt | 242 | 12.27 | 129 |

### 4.2 Within 变异

| 板块 | 方程 | 变量 | 总体 SD | Within SD | Within/总体 | FE 识别 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 0.0452 | 0.0181 | 0.4003 | adequate |
| baseline | — | bond_10y | 0.0449 | 0.0228 | 0.5081 | adequate |
| baseline | — | vulnerability100 | 0.0781 | 0.0106 | 0.1362 | adequate |
| baseline | — | readiness100 | 0.1423 | 0.0435 | 0.3054 | adequate |
| baseline | — | lnrgdp | 2.9224 | 0.3096 | 0.1059 | adequate |
| baseline | — | growth | 0.0358 | 0.0324 | 0.9062 | adequate |
| baseline | — | inflation_cpi | 0.1062 | 0.0906 | 0.8534 | adequate |
| baseline | — | debt_gdp | 0.3443 | 0.1814 | 0.5267 | adequate |
| baseline | — | PrimaryBalance_gdp | 0.0338 | 0.0289 | 0.8556 | adequate |
| baseline | — | reserves | 0.1249 | 0.0717 | 0.5741 | adequate |
| baseline | — | gee | 0.8981 | 0.1926 | 0.2145 | adequate |
| baseline | — | rqe | 0.848 | 0.1803 | 0.2126 | adequate |
| baseline | — | tt | 0.1831 | 0.1626 | 0.8881 | adequate |
| baseline | — | is_advanced | 0.4999 | 0 | 0 | not_identified_by_FE |
| baseline | — | Revenue_gdp | 0.129 | 0.0244 | 0.1891 | adequate |
| baseline | — | CurrentGDP | 1.32e+06 | 847890.13 | 0.6408 | adequate |
| baseline | — | OverallBalance_gdp | 0.0394 | 0.0291 | 0.7377 | adequate |
| baseline | — | revenue | 212976.3026 | 130533.59 | 0.6129 | adequate |
| baseline | — | debt | 500421.1398 | 292625.66 | 0.5848 | adequate |
| baseline | — | interest_revenue | 0.098 | 0.0475 | 0.4851 | adequate |
| baseline | — | taxgdp | 7.9901 | 1.7075 | 0.2137 | adequate |
| baseline | — | ln_currentgdp | 2.9805 | 0.7723 | 0.2591 | adequate |
| tax | — | taxbase_lead | 0.0819 | 0.0226 | 0.2754 | adequate |
| tax | — | taxbase_lag | 0.0797 | 0.0164 | 0.2063 | adequate |
| tax | — | readiness100 | 0.1429 | 0.0401 | 0.2802 | adequate |
| tax | — | vulnerability100 | 0.079 | 0.0099 | 0.1248 | adequate |
| tax | — | growth | 0.0367 | 0.0326 | 0.8885 | adequate |
| tax | — | inflation_cpi | 0.0566 | 0.0421 | 0.7442 | adequate |
| tax | — | reserves | 0.1332 | 0.0628 | 0.4711 | adequate |
| tax | — | tt | 0.1824 | 0.157 | 0.8606 | adequate |
| doomloop | debt | delta_debt_lead | 0.0623 | 0.0551 | 0.8844 | adequate |
| doomloop | debt | theta_hat_A | 0.107 | 0.0585 | 0.5463 | adequate |
| doomloop | debt | readiness100 | 0.1435 | 0.0401 | 0.2798 | adequate |
| doomloop | debt | debt_gdp | 0.3469 | 0.1697 | 0.4893 | adequate |
| doomloop | debt | vulnerability100 | 0.078 | 0.0101 | 0.1293 | adequate |
| doomloop | debt | growth | 0.0366 | 0.0326 | 0.8907 | adequate |
| doomloop | debt | inflation_cpi | 0.0579 | 0.0435 | 0.7513 | adequate |
| doomloop | debt | reserves | 0.1326 | 0.0637 | 0.4805 | adequate |
| doomloop | debt | tt | 0.1799 | 0.1584 | 0.8807 | adequate |
| doomloop | ready | J_readiness | 0.0183 | 0.0182 | 0.9936 | adequate |
| doomloop | ready | theta_hat_A | 0.108 | 0.058 | 0.5375 | adequate |
| doomloop | ready | interest_revenue | 0.1002 | 0.0464 | 0.4634 | adequate |
| doomloop | ready | readiness100 | 0.1416 | 0.0387 | 0.2731 | adequate |
| doomloop | ready | readiness_lag | 0.1411 | 0.0397 | 0.2815 | adequate |
| doomloop | ready | vulnerability100 | 0.0783 | 0.0103 | 0.132 | adequate |
| doomloop | ready | growth | 0.0359 | 0.032 | 0.8902 | adequate |
| doomloop | ready | ln_currentgdp | 3.0193 | 0.6459 | 0.2139 | adequate |
| doomloop | ready | inflation_cpi | 0.0588 | 0.0441 | 0.7499 | adequate |
| doomloop | ready | reserves | 0.115 | 0.0623 | 0.5418 | adequate |
| doomloop | ready | tt | 0.1732 | 0.1545 | 0.892 | adequate |

## 5. 共线性、相关性与系数变化

### 5.1 VIF/条件数

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline | vulnerability100 | 1.4677 | 0.6814 | 2.1222 |
| baseline | readiness100 | 1.0141 | 0.9861 | 2.1222 |
| baseline | debt_gdp | 1.1393 | 0.8778 | 2.1222 |
| baseline | growth | 1.0788 | 0.927 | 2.1222 |
| baseline | ln_currentgdp | 1.6307 | 0.6132 | 2.1222 |
| baseline | inflation_cpi | 1.1252 | 0.8887 | 2.1222 |
| baseline | reserves | 1.1005 | 0.9087 | 2.1222 |
| baseline | tt | 1.0507 | 0.9518 | 2.1222 |
| tax | readiness100 | 1.0438 | 0.958 | 1.3423 |
| tax | vulnerability100 | 1.05 | 0.9524 | 1.3423 |
| tax | taxbase_lag | 1.0264 | 0.9743 | 1.3423 |
| tax | growth | 1.0243 | 0.9763 | 1.3423 |
| tax | inflation_cpi | 1.0395 | 0.962 | 1.3423 |
| tax | reserves | 1.0168 | 0.9835 | 1.3423 |
| tax | tt | 1.0392 | 0.9623 | 1.3423 |
| tax | c_A_T | 1.1092 | 0.9016 | 1.6913 |
| tax | c_X_T | 1.2029 | 0.8313 | 1.6913 |
| tax | int_AX_T | 1.2324 | 0.8114 | 1.6913 |
| tax | taxbase_lag | 1.0592 | 0.9441 | 1.6913 |
| tax | growth | 1.0253 | 0.9753 | 1.6913 |
| tax | inflation_cpi | 1.0395 | 0.962 | 1.6913 |
| tax | reserves | 1.0356 | 0.9657 | 1.6913 |
| tax | tt | 1.0394 | 0.9621 | 1.6913 |

### 5.2 高绝对相关系数（排除对角线与镜像重复）

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |
| baseline | vulnerability100 | readiness100 | -0.7642 |
| tax | readiness100 | vulnerability100 | -0.7818 |
| tax | readiness100 | taxbase_lag | 0.6415 |
| tax | vulnerability100 | taxbase_lag | -0.673 |

### 5.3 加入控制变量后的系数变化

| 板块 | 模型 | 变量 | 基准系数 | 新系数 | 绝对变化 | %变化 | 报告规则 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | C_macro | vulnerability100 | -0.2138 | 0.1427 | 0.3565 | 166.7 | percent |
| baseline | C_macro | readiness100 | -0.0717 | -0.0593 | 0.0124 | 17.2 | percent |
| baseline | C_macro | debt_gdp | 0.0496 | 0.0515 | 0.0019 | 3.8 | percent |
| baseline | Layer1_X | vulnerability100 | -0.2138 | 0.1971 | 0.4109 | 192.2 | percent |
| baseline | Layer1_X | debt_gdp | 0.0496 | 0.0519 | 0.0023 | 4.7 | percent |
| baseline | Layer2_A | vulnerability100 | -0.2138 | 0.2019 | 0.4158 | 194.4 | percent |
| baseline | Layer2_A | readiness100 | -0.0717 | -0.0619 | 0.0098 | 13.6 | percent |
| baseline | Layer2_A | debt_gdp | 0.0496 | 0.0527 | 0.0031 | 6.3 | percent |
| tax | T5_macro | vulnerability100 | 0.1301 | 0.0669 | -0.0632 | -48.6 | percent |
| tax | T5_macro | readiness100 | -0.0135 | -0.0116 | 0.0019 | 14.2 | percent |
| tax | T5_macro | taxbase_lag | 0.8619 | 0.8513 | -0.0106 | -1.2 | percent |
| tax | T7_layer2_A | vulnerability100 | 0.1301 | 0.0588 | -0.0713 | -54.8 | percent |
| tax | T7_layer2_A | readiness100 | -0.0135 | -0.0155 | -0.002 | -15.2 | percent |
| tax | T7_layer2_A | taxbase_lag | 0.8619 | 0.8531 | -0.0089 | -1 | percent |
| tax | T9_interact_macro | c_A_T | -0.0187 | -0.0163 | 0.0024 | 12.7 | percent |
| tax | T9_interact_macro | c_X_T | 0.1658 | 0.0997 | -0.0662 | -39.9 | percent |
| tax | T9_interact_macro | int_AX_T | 0.2246 | 0.2048 | -0.0198 | -8.8 | percent |
| tax | T9_interact_macro | taxbase_lag | 0.8542 | 0.8443 | -0.0098 | -1.2 | percent |
| tax | T10_interact_full | c_A_T | -0.0187 | -0.0206 | -0.0019 | -10 | percent |
| tax | T10_interact_full | c_X_T | 0.1658 | 0.0933 | -0.0725 | -43.7 | percent |
| tax | T10_interact_full | int_AX_T | 0.2246 | 0.2079 | -0.0167 | -7.4 | percent |
| tax | T10_interact_full | taxbase_lag | 0.8542 | 0.8458 | -0.0084 | -1 | percent |

## 6. 统计检验

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | F | 分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 24.8591 | 2 | 1,187 | <0.001 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 42.0835 | 1 | 1,187 | <0.001 |
| baseline | Interact_AX | c_A = int_AX = 0 | 8.5601 | 2 | 1,187 | <0.001 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 0.1339 | 1 | 1,187 | 0.714 |
| baseline | Interact_all | c_A = int_AB = 0 | 24.2049 | 2 | 1,186 | <0.001 |
| baseline | Interact_all | c_A = int_AX = 0 | 12.5082 | 2 | 1,186 | <0.001 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 16.5892 | 3 | 1,186 | <0.001 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 21.1723 | 2 | 1,186 | <0.001 |
| tax | T5_macro | macro controls jointly zero | 30.61 | 2 | 1,436 | <0.001 |
| tax | T7_layer2_A | external controls jointly zero | 3.0353 | 2 | 1,434 | 0.048 |
| tax | T7_layer2_A | all controls jointly zero | 15.9257 | 4 | 1,434 | <0.001 |
| tax | T8_interact_core | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 2.5473 | 2 | 1,437 | 0.079 |
| tax | T8_interact_core | interaction zero: int_AX_T = 0 | 4.5223 | 1 | 1,437 | 0.034 |
| tax | T9_interact_macro | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 2.2084 | 2 | 1,435 | 0.110 |
| tax | T9_interact_macro | interaction zero: int_AX_T = 0 | 4.022 | 1 | 1,435 | 0.045 |
| tax | T10_interact_full | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 2.5043 | 2 | 1,433 | 0.082 |
| tax | T10_interact_full | interaction zero: int_AX_T = 0 | 4.0989 | 1 | 1,433 | 0.043 |
| tax | T9_interact_macro | macro controls jointly zero | 30.338 | 2 | 1,435 | <0.001 |
| tax | T10_interact_full | external controls jointly zero | 3.1178 | 2 | 1,433 | 0.045 |
| tax | T10_interact_full | all controls jointly zero | 15.9318 | 4 | 1,433 | <0.001 |
| doomloop | D3_full | low- and high-branch coefficients jointly zero | 0.5107 | 2 | 1,452 | 0.600 |
| doomloop | D3_full | macro controls jointly zero | 10.1128 | 2 | 1,452 | <0.001 |
| doomloop | D3_full | external controls jointly zero | 0.4352 | 2 | 1,452 | 0.647 |
| doomloop | D3_full | all controls jointly zero | 5.2754 | 4 | 1,452 | <0.001 |
| doomloop | R3_full | low- and high-branch coefficients jointly zero | 4.7663 | 2 | 1,471 | 0.009 |
| doomloop | R3_full | macro controls jointly zero | 1.1949 | 3 | 1,471 | 0.310 |
| doomloop | R3_full | external controls jointly zero | 0.7615 | 2 | 1,471 | 0.467 |
| doomloop | R3_full | all controls jointly zero | 1.3356 | 5 | 1,471 | 0.246 |
| doomloop-no-state | DN3_full | low- and high-branch coefficients jointly zero | 0.8475 | 2 | 1,453 | 0.429 |
| doomloop-no-state | DN3_full | macro controls jointly zero | 10.114 | 2 | 1,453 | <0.001 |
| doomloop-no-state | DN3_full | external controls jointly zero | 0.364 | 2 | 1,453 | 0.695 |
| doomloop-no-state | DN3_full | all controls jointly zero | 5.1555 | 4 | 1,453 | <0.001 |
| doomloop-no-state | RN3_full | low- and high-branch coefficients jointly zero | 1.0982 | 2 | 1,472 | 0.334 |
| doomloop-no-state | RN3_full | macro controls jointly zero | 1.3566 | 3 | 1,472 | 0.254 |
| doomloop-no-state | RN3_full | external controls jointly zero | 0.2354 | 2 | 1,472 | 0.790 |
| doomloop-no-state | RN3_full | all controls jointly zero | 1.0551 | 5 | 1,472 | 0.384 |

### 6.2 代数、映射与时序公式检查

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | taxbase_lead timing formula | 0 | 1.00e-12 | 通过 |
| theta | taxbase_lag equals taxgdp ratio | 0 | 1.00e-12 | 通过 |
| theta | b_it equals debt_gdp exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 1.11e-16 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw tax formula | 6.94e-18 | 1.00e-12 | 通过 |
| theta | stored versus predictnl tax margin | 0 | 1.00e-12 | 通过 |
| theta | theta component identity | 0 | 1.00e-12 | 通过 |
| doomloop | theta uses debt_gdp*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop | b_it maps exactly to debt_gdp | 0 | 1.00e-10 | 通过 |
| doomloop | delta_debt_lead formula | 0 | 1.00e-10 | 通过 |
| doomloop | J_readiness formula | 0 | 1.00e-10 | 通过 |
| doomloop | debt low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop | debt high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop | readiness low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop | readiness high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | theta uses debt_gdp*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | b_it maps exactly to debt_gdp | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | no-b debt low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | no-b debt high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | no-lag readiness low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | no-lag readiness high hinge regressor | 0 | 1.00e-10 | 通过 |

### 6.3 areg 与显式 LSDV 复核

| 板块 | 模型/方程 | 变量 | areg | LSDV | \|系数差\| | \|SE差\| |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_all | tt | -0.0018 | -0.0018 | 9.63e-16 | 2.73e-17 |
| baseline | Interact_all | reserves | 0.023 | 0.023 | 2.41e-15 | 3.93e-16 |
| baseline | Interact_all | inflation_cpi | 0.1631 | 0.1631 | 8.52e-15 | 1.46e-16 |
| baseline | Interact_all | ln_currentgdp | 0.0184 | 0.0184 | 4.46e-15 | 5.42e-16 |
| baseline | Interact_all | growth | -0.1577 | -0.1577 | 2.53e-15 | 2.88e-16 |
| baseline | Interact_all | int_AX | 0.0365 | 0.0365 | 4.76e-14 | 2.58e-15 |
| baseline | Interact_all | int_AB | -0.1862 | -0.1862 | 5.52e-15 | 9.61e-16 |
| baseline | Interact_all | c_b | 0.0553 | 0.0553 | 1.96e-15 | 3.76e-16 |
| baseline | Interact_all | c_X | 0.2448 | 0.2448 | 8.27e-14 | 7.49e-15 |
| baseline | Interact_all | c_A | -0.0819 | -0.0819 | 4.27e-15 | 5.55e-17 |
| baseline | Layer2_A | tt | 0.0004 | 0.0004 | 8.55e-16 | 1.75e-16 |
| baseline | Layer2_A | reserves | 0.0197 | 0.0197 | 1.63e-15 | 1.28e-16 |
| baseline | Layer2_A | inflation_cpi | 0.1557 | 0.1557 | 6.58e-15 | 1.96e-15 |
| baseline | Layer2_A | ln_currentgdp | 0.0237 | 0.0237 | 3.55e-15 | 3.22e-15 |
| baseline | Layer2_A | growth | -0.1731 | -0.1731 | 1.61e-15 | 9.71e-17 |
| baseline | Layer2_A | debt_gdp | 0.0527 | 0.0527 | 1.63e-15 | 3.30e-17 |
| baseline | Layer2_A | readiness100 | -0.0619 | -0.0619 | 7.88e-15 | 8.15e-17 |
| baseline | Layer2_A | vulnerability100 | 0.2019 | 0.2019 | 5.59e-14 | 2.31e-13 |
| tax | Spread_Interact_all | c_A | -0.0819 | -0.0819 | 5.56e-15 | 1.80e-16 |
| tax | Spread_Interact_all | c_X | 0.2448 | 0.2448 | 9.49e-14 | 4.03e-14 |
| tax | Spread_Interact_all | c_b | 0.0553 | 0.0553 | 2.05e-15 | 2.82e-16 |
| tax | Spread_Interact_all | int_AB | -0.1862 | -0.1862 | 8.08e-15 | 1.49e-16 |
| tax | Spread_Interact_all | int_AX | 0.0365 | 0.0365 | 6.79e-14 | 4.88e-15 |
| tax | Spread_Interact_all | growth | -0.1577 | -0.1577 | 2.72e-15 | 2.64e-16 |
| tax | Spread_Interact_all | ln_currentgdp | 0.0184 | 0.0184 | 5.46e-15 | 2.89e-15 |
| tax | Spread_Interact_all | inflation_cpi | 0.1631 | 0.1631 | 1.04e-14 | 8.29e-16 |
| tax | Spread_Interact_all | reserves | 0.023 | 0.023 | 3.02e-15 | 1.18e-16 |
| tax | Spread_Interact_all | tt | -0.0018 | -0.0018 | 1.15e-15 | 1.95e-16 |
| tax | T7_layer2_A | vulnerability100 | 0.0588 | 0.0588 | 1.31e-13 | 1.74e-13 |
| tax | T7_layer2_A | readiness100 | -0.0155 | -0.0155 | 2.90e-15 | 1.90e-15 |
| tax | T7_layer2_A | taxbase_lag | 0.8531 | 0.8531 | 3.61e-14 | 2.50e-16 |
| tax | T7_layer2_A | growth | 0.1186 | 0.1186 | 4.16e-15 | 3.82e-17 |
| tax | T7_layer2_A | inflation_cpi | 0.0727 | 0.0727 | 1.64e-15 | 6.94e-17 |
| tax | T7_layer2_A | reserves | 0.002 | 0.002 | 1.10e-15 | 2.71e-16 |
| tax | T7_layer2_A | tt | -0.0076 | -0.0076 | 2.64e-16 | 1.17e-16 |
| tax | T10_interact_full | c_A_T | -0.0206 | -0.0206 | 1.66e-15 | 3.89e-16 |
| tax | T10_interact_full | c_X_T | 0.0933 | 0.0933 | 1.31e-13 | 1.36e-14 |
| tax | T10_interact_full | int_AX_T | 0.2079 | 0.2079 | 5.30e-14 | 3.05e-16 |
| tax | T10_interact_full | taxbase_lag | 0.8458 | 0.8458 | 3.81e-14 | 1.94e-15 |
| tax | T10_interact_full | growth | 0.1178 | 0.1178 | 4.54e-15 | 2.46e-16 |
| tax | T10_interact_full | inflation_cpi | 0.0729 | 0.0729 | 1.51e-15 | 7.63e-17 |
| tax | T10_interact_full | reserves | 0.0034 | 0.0034 | 1.19e-15 | 4.77e-17 |
| tax | T10_interact_full | tt | -0.0075 | -0.0075 | 2.97e-16 | 3.04e-18 |
| doomloop | debt | debt_kink_low | 1.3698 | 1.3698 | 5.64e-14 | 1.14e-13 |
| doomloop | debt | debt_kink_high | -0.0867 | -0.0867 | 1.71e-15 | 5.65e-15 |
| doomloop | debt | debt_gdp | 0.005 | 0.005 | 6.39e-16 | 5.20e-17 |
| doomloop | debt | vulnerability100 | -0.4903 | -0.4903 | 1.24e-14 | 6.93e-13 |
| doomloop | debt | growth | -0.2494 | -0.2494 | 4.44e-16 | 1.39e-16 |
| doomloop | debt | inflation_cpi | 0.1416 | 0.1416 | 7.49e-16 | 1.67e-16 |
| doomloop | debt | reserves | -0.0143 | -0.0143 | 4.60e-16 | 9.44e-16 |
| doomloop | debt | tt | 0.0048 | 0.0048 | 6.42e-17 | 7.55e-16 |
| doomloop | ready | ready_kink_low | -1.5688 | -1.5688 | 4.22e-15 | 5.77e-14 |
| doomloop | ready | ready_kink_high | 0.0435 | 0.0435 | 3.96e-16 | 3.21e-15 |
| doomloop | ready | readiness_lag | -0.1559 | -0.1559 | 2.91e-15 | 1.36e-15 |
| doomloop | ready | vulnerability100 | -0.1006 | -0.1006 | 1.18e-15 | 7.04e-13 |
| doomloop | ready | growth | 0.0222 | 0.0222 | 1.04e-17 | 1.79e-16 |
| doomloop | ready | ln_currentgdp | -0.001 | -0.001 | 1.24e-16 | 2.82e-15 |
| doomloop | ready | inflation_cpi | -0.0039 | -0.0039 | 1.38e-16 | 3.00e-16 |
| doomloop | ready | reserves | 0.0017 | 0.0017 | 9.52e-17 | 3.30e-15 |
| doomloop | ready | tt | -0.0042 | -0.0042 | 2.95e-17 | 3.34e-17 |
| doomloop-no-state | debt | debt_kink_low | -0.0888 | -0.0888 | 2.60e-14 | 9.80e-15 |
| doomloop-no-state | debt | debt_kink_high | -0.0747 | -0.0747 | 3.33e-16 | 2.22e-16 |
| doomloop-no-state | debt | vulnerability100 | -0.5241 | -0.5241 | 4.11e-15 | 8.89e-14 |
| doomloop-no-state | debt | growth | -0.2508 | -0.2508 | 4.44e-16 | 5.00e-16 |
| doomloop-no-state | debt | inflation_cpi | 0.1412 | 0.1412 | 5.00e-16 | 2.08e-16 |
| doomloop-no-state | debt | reserves | -0.0127 | -0.0127 | 4.13e-16 | 2.08e-17 |
| doomloop-no-state | debt | tt | 0.0049 | 0.0049 | 1.24e-16 | 2.05e-16 |
| doomloop-no-state | ready | ready_kink_low | -6.0825 | -6.0825 | 8.88e-15 | 6.75e-14 |
| doomloop-no-state | ready | ready_kink_high | 0.0493 | 0.0493 | 7.63e-16 | 6.94e-16 |
| doomloop-no-state | ready | vulnerability100 | -0.1255 | -0.1255 | 2.13e-14 | 2.71e-13 |
| doomloop-no-state | ready | growth | 0.0265 | 0.0265 | 1.98e-16 | 1.61e-16 |
| doomloop-no-state | ready | ln_currentgdp | 0.0005 | 0.0005 | 2.93e-16 | 3.73e-15 |
| doomloop-no-state | ready | inflation_cpi | -0.0028 | -0.0028 | 2.36e-16 | 4.25e-17 |
| doomloop-no-state | ready | reserves | 0.002 | 0.002 | 4.15e-16 | 9.75e-16 |
| doomloop-no-state | ready | tt | -0.002 | -0.002 | 4.16e-17 | 1.78e-16 |

### 6.4 Cutoff 最小 RSS 复核

| 规格 | 方程 | 记录 cutoff | profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 原始 | debt | -0.0261 | 3.9634 | 3.9634 | 0 | 通过 |
| 原始 | ready | 0.0257 | 0.4133 | 0.4133 | 0 | 通过 |
| 去状态变量 | debt | 0.0332 | 3.9636 | 3.9636 | 0 | 通过 |
| 去状态变量 | ready | -0.0217 | 0.4479 | 0.4479 | 0 | 通过 |

## 7. 图形 QA

四张单方程图和两张合并图均保留 PNG 与 PDF。单方程图使用连续 theta 网格并把 cutoff 精确插入网格；竖直虚线与 CSV 中记录的 cutoff 一致。曲线在 cutoff 处为 0，低支与高支按各自估计系数绘制；轴单位为统一比率。文档引用的是四张单方程 PNG，PDF 用于排版输出。

## 8. 必须保留的限制与建议

- 当前稳健标准误处理异方差，但不处理同一国家内序列相关；面板论文通常还应报告国家聚类标准误或适当的双向聚类/空间相关推断。
- cutoff 在同一样本上搜索，条件于 cutoff 的常规标准误偏窄风险未纳入。建议按国家重抽样，完整重复 baseline、tax/theta、cutoff 搜索和最终回归。
- theta 是生成解释变量；联合不确定性依赖跨方程协方差。当前只对两个组成边际量分别做 delta-method 标准误，不提供 theta 的联合 SE。
- 结果是固定效应相关性证据，不支持没有额外识别设计的因果措辞。
- 债务去 b 规格的两支系数同号，不满足经验上的 single-crossing 符号模式；应作为负结果如实报告。

## 9. 原始诊断输出索引

完整 CSV/DTA/日志仍保留在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/`、`doomloop/stata_outputs/`。本文件是汇总层，不替代这些逐项机器可读结果。
