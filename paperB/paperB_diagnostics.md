# Paper B：统计检验与数据检查

> 生成时间：2026-08-06 00:35（Asia/Shanghai）。本文件汇总三个板块的诊断、样本审计、单位审计、稳健性检验与验证结果；正式公式和回归表见 `paperB_results.md`。

## 1. 总体评估：可在明确限制条件下使用

单位换算检查通过 27/27 项；代数/构造检查通过 22/22 项；cutoff 最小 RSS 复核通过 4/4 项。当前结果在代码一致性和样本内计算层面通过，但仍属于“Share with caveats”：生成 theta、样本内 cutoff 搜索和面板相关推断的不确定性尚未由完整流程 bootstrap 与国家聚类标准误覆盖。

## 2. 数据来源、单位与时序检查

唯一原始输入是 `data0804/invest_panel_weo.csv`。所有源百分数、比率和 0—100 指数在读入后除以 100；金额变量 `revenue`、`debt`、`CurrentGDP` 不缩放。`ln_currentgdp=ln(CurrentGDP)`。关键因变量的精确定义为：

- $\widetilde T_{i,t+1}^{(t)}=revenue_{i,t+1}/CurrentGDP_{it}$，不乘 100。
- $\widetilde T_{it}^{(t-1)}=revenue_{it}/CurrentGDP_{i,t-1}$，不乘 100。
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

Empirical-theta 重新执行同一 13 项审计；doomloop 从已审计的 theta panel 读入并对关键上游比例变量复核。全部检查的原始 CSV 保留在各板块 `stata_outputs` 目录。

## 3. 样本覆盖与描述性统计

| 固定样本 | N | 国家数 | 年份数 | 基准年份范围 |
| --- | ---: | ---: | ---: | ---: |
| Baseline 共同样本 | 1,286 | 65 | 26 | 1998–2023 |
| Tax 共同样本 | 1,549 | 65 | 27 | 1996–2022 |
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
| taxbase_lead | tax | 1,549 | 0.3371 | 0.1303 | 0.0392 | 0.3535 | 0.8069 |
| taxbase_lag | tax | 1,549 | 0.3371 | 0.1307 | 0.0392 | 0.3534 | 0.8069 |
| mA_hat_spread_ratio | theta_support | 1,221 | 0.0747 | 0.0625 | -0.0586 | 0.076 | 0.3237 |
| mA_hat | theta_support | 1,221 | 0.0747 | 0.0625 | -0.0586 | 0.076 | 0.3237 |
| spread_saving_component | theta_support | 1,221 | 0.0615 | 0.0864 | -0.0221 | 0.0361 | 0.6795 |
| TA_hat | theta_support | 1,221 | -0.0061 | 0.0243 | -0.0454 | -0.012 | 0.0632 |
| theta_hat_A | theta_support | 1,221 | 0.0553 | 0.0891 | -0.0531 | 0.0393 | 0.6637 |
| theta_hat_A | all_constructible | 1,819 | 0.0588 | 0.0892 | -0.0531 | 0.0433 | 1.1042 |

### 3.3 四组 doomloop 回归变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_with_b | debt | delta_debt_lead | dependent_variable | 1,552 | 0.0494 | 0.0623 | -0.4484 | 0.0408 | 0.5778 |
| debt_with_b | debt | debt_kink_low | regressor | 1,552 | 0.0056 | 0.0109 | 0 | 0 | 0.0541 |
| debt_with_b | debt | debt_kink_high | regressor | 1,552 | 0.0239 | 0.0433 | 0 | 0.0123 | 0.3966 |
| debt_with_b | debt | debt_gdp | regressor | 1,552 | 0.5735 | 0.3469 | 0.039 | 0.5036 | 2.6096 |
| debt_with_b | debt | vulnerability100 | regressor | 1,552 | 0.3823 | 0.078 | 0.251 | 0.3675 | 0.5808 |
| debt_with_b | debt | growth | regressor | 1,552 | 0.0343 | 0.0366 | -0.1604 | 0.035 | 0.2462 |
| debt_with_b | debt | ln_currentgdp | regressor | 1,552 | 7.6539 | 2.9952 | 0.6323 | 7.4206 | 16.7905 |
| debt_with_b | debt | inflation_cpi | regressor | 1,552 | 0.0474 | 0.0579 | -0.0177 | 0.0305 | 0.723 |
| debt_with_b | debt | reserves | regressor | 1,552 | 0.0577 | 0.1326 | 2.41e-06 | 0.0189 | 1.5271 |
| debt_with_b | debt | tt | regressor | 1,552 | 1.0072 | 0.1799 | 0.3188 | 0.995 | 2.7308 |
| debt_with_b | debt | readiness100 | construction_input | 1,552 | 0.5054 | 0.1435 | 0.2021 | 0.5005 | 0.8072 |
| debt_with_b | debt | theta_hat_A | construction_input | 1,552 | 0.0583 | 0.0894 | -0.0531 | 0.0435 | 1.1042 |
| ready_with_lag | ready | J_readiness | dependent_variable | 1,571 | 0.0025 | 0.0183 | -0.22 | 0.0021 | 0.0823 |
| ready_with_lag | ready | ready_kink_low | regressor | 1,571 | 0.0028 | 0.0034 | -0.008 | 0.0026 | 0.0191 |
| ready_with_lag | ready | ready_kink_high | regressor | 1,571 | 0.0018 | 0.0075 | -0.0003 | 0 | 0.1208 |
| ready_with_lag | ready | readiness_lag | regressor | 1,571 | 0.5012 | 0.1411 | 0.2021 | 0.4971 | 0.7973 |
| ready_with_lag | ready | vulnerability100 | regressor | 1,571 | 0.3807 | 0.0783 | 0.251 | 0.3648 | 0.5808 |
| ready_with_lag | ready | growth | regressor | 1,571 | 0.0334 | 0.0359 | -0.1604 | 0.0337 | 0.2462 |
| ready_with_lag | ready | ln_currentgdp | regressor | 1,571 | 7.7309 | 3.0193 | 1.0006 | 7.4927 | 16.8549 |
| ready_with_lag | ready | inflation_cpi | regressor | 1,571 | 0.049 | 0.0588 | -0.0177 | 0.0323 | 0.723 |
| ready_with_lag | ready | reserves | regressor | 1,571 | 0.0492 | 0.115 | 2.41e-06 | 0.0188 | 1.5271 |
| ready_with_lag | ready | tt | regressor | 1,571 | 1.0066 | 0.1732 | 0.3188 | 0.995 | 2.7308 |
| ready_with_lag | ready | interest_revenue | construction_input | 1,571 | 0.0859 | 0.1002 | -0.069 | 0.0562 | 0.7987 |
| ready_with_lag | ready | theta_hat_A | construction_input | 1,571 | 0.059 | 0.091 | -0.0531 | 0.0435 | 1.1042 |
| ready_with_lag | ready | readiness100 | construction_input | 1,571 | 0.5037 | 0.1416 | 0.2021 | 0.5001 | 0.7973 |
| debt_no_b | debt | delta_debt_lead | dependent_variable | 1,552 | 0.0494 | 0.0623 | -0.4484 | 0.0408 | 0.5778 |
| debt_no_b | debt | debt_kink_low | regressor | 1,552 | 0.0056 | 0.0108 | 0 | 0 | 0.054 |
| debt_no_b | debt | debt_kink_high | regressor | 1,552 | 0.0239 | 0.0433 | 0 | 0.0123 | 0.3967 |
| debt_no_b | debt | vulnerability100 | regressor | 1,552 | 0.3823 | 0.078 | 0.251 | 0.3675 | 0.5808 |
| debt_no_b | debt | growth | regressor | 1,552 | 0.0343 | 0.0366 | -0.1604 | 0.035 | 0.2462 |
| debt_no_b | debt | ln_currentgdp | regressor | 1,552 | 7.6539 | 2.9952 | 0.6323 | 7.4206 | 16.7905 |
| debt_no_b | debt | inflation_cpi | regressor | 1,552 | 0.0474 | 0.0579 | -0.0177 | 0.0305 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,552 | 0.0577 | 0.1326 | 2.41e-06 | 0.0189 | 1.5271 |
| debt_no_b | debt | tt | regressor | 1,552 | 1.0072 | 0.1799 | 0.3188 | 0.995 | 2.7308 |
| debt_no_b | debt | readiness100 | construction_input | 1,552 | 0.5054 | 0.1435 | 0.2021 | 0.5005 | 0.8072 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,552 | 0.0583 | 0.0894 | -0.0531 | 0.0435 | 1.1042 |
| ready_no_lag | ready | J_readiness | dependent_variable | 1,571 | 0.0025 | 0.0183 | -0.22 | 0.0021 | 0.0823 |
| ready_no_lag | ready | ready_kink_low | regressor | 1,571 | 0.0028 | 0.0034 | -0.008 | 0.0026 | 0.0191 |
| ready_no_lag | ready | ready_kink_high | regressor | 1,571 | 0.0018 | 0.0075 | -0.0003 | 0 | 0.1208 |
| ready_no_lag | ready | vulnerability100 | regressor | 1,571 | 0.3807 | 0.0783 | 0.251 | 0.3648 | 0.5808 |
| ready_no_lag | ready | growth | regressor | 1,571 | 0.0334 | 0.0359 | -0.1604 | 0.0337 | 0.2462 |
| ready_no_lag | ready | ln_currentgdp | regressor | 1,571 | 7.7309 | 3.0193 | 1.0006 | 7.4927 | 16.8549 |
| ready_no_lag | ready | inflation_cpi | regressor | 1,571 | 0.049 | 0.0588 | -0.0177 | 0.0323 | 0.723 |
| ready_no_lag | ready | reserves | regressor | 1,571 | 0.0492 | 0.115 | 2.41e-06 | 0.0188 | 1.5271 |
| ready_no_lag | ready | tt | regressor | 1,571 | 1.0066 | 0.1732 | 0.3188 | 0.995 | 2.7308 |
| ready_no_lag | ready | interest_revenue | construction_input | 1,571 | 0.0859 | 0.1002 | -0.069 | 0.0562 | 0.7987 |
| ready_no_lag | ready | theta_hat_A | construction_input | 1,571 | 0.059 | 0.091 | -0.0531 | 0.0435 | 1.1042 |
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
| tax | — | taxbase_lead | 117 | 5.93 | 65 |
| tax | — | readiness100 | 58 | 2.94 | 0 |
| tax | — | vulnerability100 | 58 | 2.94 | 0 |
| tax | — | taxbase_lag | 117 | 5.93 | 25 |
| tax | — | growth | 11 | 0.56 | 1 |
| tax | — | ln_currentgdp | 2 | 0.1 | 0 |
| tax | — | inflation_cpi | 7 | 0.35 | 1 |
| tax | — | reserves | 76 | 3.85 | 26 |
| tax | — | tt | 242 | 12.27 | 149 |
| doomloop | debt | delta_debt_lead | 174 | 8.82 | 65 |
| doomloop | debt | readiness100 | 58 | 2.94 | 0 |
| doomloop | debt | theta_hat_A | 153 | 7.76 | 0 |
| doomloop | debt | debt_gdp | 106 | 5.38 | 0 |
| doomloop | debt | vulnerability100 | 58 | 2.94 | 0 |
| doomloop | debt | growth | 11 | 0.56 | 1 |
| doomloop | debt | ln_currentgdp | 2 | 0.1 | 0 |
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
| baseline | — | ln_currentgdp | 2.9805 | 0.7723 | 0.2591 | adequate |
| tax | — | taxbase_lead | 0.1303 | 0.0312 | 0.2397 | adequate |
| tax | — | taxbase_lag | 0.1307 | 0.0315 | 0.2407 | adequate |
| tax | — | readiness100 | 0.1438 | 0.0398 | 0.277 | adequate |
| tax | — | vulnerability100 | 0.0788 | 0.0101 | 0.1277 | adequate |
| tax | — | growth | 0.0365 | 0.0326 | 0.8912 | adequate |
| tax | — | ln_currentgdp | 2.9837 | 0.6302 | 0.2112 | adequate |
| tax | — | inflation_cpi | 0.0562 | 0.0421 | 0.7482 | adequate |
| tax | — | reserves | 0.1324 | 0.0636 | 0.4803 | adequate |
| tax | — | tt | 0.1766 | 0.1584 | 0.8967 | adequate |
| doomloop | debt | delta_debt_lead | 0.0623 | 0.0551 | 0.8844 | adequate |
| doomloop | debt | theta_hat_A | 0.0894 | 0.0482 | 0.5395 | adequate |
| doomloop | debt | readiness100 | 0.1435 | 0.0401 | 0.2798 | adequate |
| doomloop | debt | debt_gdp | 0.3469 | 0.1697 | 0.4893 | adequate |
| doomloop | debt | vulnerability100 | 0.078 | 0.0101 | 0.1293 | adequate |
| doomloop | debt | growth | 0.0366 | 0.0326 | 0.8907 | adequate |
| doomloop | debt | ln_currentgdp | 2.9952 | 0.635 | 0.212 | adequate |
| doomloop | debt | inflation_cpi | 0.0579 | 0.0435 | 0.7513 | adequate |
| doomloop | debt | reserves | 0.1326 | 0.0637 | 0.4805 | adequate |
| doomloop | debt | tt | 0.1799 | 0.1584 | 0.8807 | adequate |
| doomloop | ready | J_readiness | 0.0183 | 0.0182 | 0.9936 | adequate |
| doomloop | ready | theta_hat_A | 0.091 | 0.0484 | 0.5319 | adequate |
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
| baseline-linear | vulnerability100 | 1.4677 | 0.6814 | 2.1222 |
| baseline-linear | readiness100 | 1.0141 | 0.9861 | 2.1222 |
| baseline-linear | debt_gdp | 1.1393 | 0.8778 | 2.1222 |
| baseline-linear | growth | 1.0788 | 0.927 | 2.1222 |
| baseline-linear | ln_currentgdp | 1.6307 | 0.6132 | 2.1222 |
| baseline-linear | inflation_cpi | 1.1252 | 0.8887 | 2.1222 |
| baseline-linear | reserves | 1.1005 | 0.9087 | 2.1222 |
| baseline-linear | tt | 1.0507 | 0.9518 | 2.1222 |
| baseline-quadratic | c_A | 1.2369 | 0.8085 | 4.5979 |
| baseline-quadratic | c_b | 1.4672 | 0.6816 | 4.5979 |
| baseline-quadratic | c_X | 1.898 | 0.5269 | 4.5979 |
| baseline-quadratic | half_A2 | 2.8943 | 0.3455 | 4.5979 |
| baseline-quadratic | half_b2 | 1.5841 | 0.6313 | 4.5979 |
| baseline-quadratic | half_X2 | 2.4071 | 0.4154 | 4.5979 |
| baseline-quadratic | int_AB | 2.1575 | 0.4635 | 4.5979 |
| baseline-quadratic | int_AX | 3.1401 | 0.3185 | 4.5979 |
| baseline-quadratic | int_bX | 2.3591 | 0.4239 | 4.5979 |
| baseline-quadratic | growth | 1.0986 | 0.9103 | 4.5979 |
| baseline-quadratic | ln_currentgdp | 2.2535 | 0.4438 | 4.5979 |
| baseline-quadratic | inflation_cpi | 1.1478 | 0.8712 | 4.5979 |
| baseline-quadratic | reserves | 1.2339 | 0.8105 | 4.5979 |
| baseline-quadratic | tt | 1.0719 | 0.9329 | 4.5979 |
| tax | readiness100 | 1.0482 | 0.954 | 1.9711 |
| tax | vulnerability100 | 1.2926 | 0.7736 | 1.9711 |
| tax | taxbase_lag | 1.1946 | 0.8371 | 1.9711 |
| tax | growth | 1.1168 | 0.8954 | 1.9711 |
| tax | ln_currentgdp | 1.4153 | 0.7066 | 1.9711 |
| tax | inflation_cpi | 1.1083 | 0.9023 | 1.9711 |
| tax | reserves | 1.0319 | 0.9691 | 1.9711 |
| tax | tt | 1.114 | 0.8977 | 1.9711 |
| tax | c_A_T | 1.112 | 0.8993 | 2.0413 |
| tax | c_X_T | 1.3809 | 0.7242 | 2.0413 |
| tax | int_AX_T | 1.2681 | 0.7886 | 2.0413 |
| tax | taxbase_lag | 1.2078 | 0.8279 | 2.0413 |
| tax | growth | 1.1175 | 0.8949 | 2.0413 |
| tax | ln_currentgdp | 1.4955 | 0.6687 | 2.0413 |
| tax | inflation_cpi | 1.1086 | 0.902 | 2.0413 |
| tax | reserves | 1.0408 | 0.9608 | 2.0413 |
| tax | tt | 1.1158 | 0.8962 | 2.0413 |

### 5.2 高绝对相关系数（排除对角线与镜像重复）

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |
| baseline | vulnerability100 | readiness100 | -0.7642 |
| tax | readiness100 | vulnerability100 | -0.779 |
| tax | readiness100 | taxbase_lag | 0.6345 |
| tax | vulnerability100 | taxbase_lag | -0.7659 |

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
| tax | T5_macro | vulnerability100 | 0.1071 | -0.0681 | -0.1752 | -163.6 | percent |
| tax | T5_macro | readiness100 | 0.0287 | 0.0123 | -0.0163 | -56.9 | percent |
| tax | T5_macro | taxbase_lag | 0.6721 | 0.6885 | 0.0163 | 2.4 | percent |
| tax | T7_layer2_A | vulnerability100 | 0.1071 | -0.0781 | -0.1852 | -172.9 | percent |
| tax | T7_layer2_A | readiness100 | 0.0287 | 0.0078 | -0.0209 | -72.9 | percent |
| tax | T7_layer2_A | taxbase_lag | 0.6721 | 0.6957 | 0.0236 | 3.5 | percent |
| tax | T9_interact_macro | c_A_T | 0.0263 | 0.0032 | -0.0231 | -87.8 | percent |
| tax | T9_interact_macro | c_X_T | 0.1263 | -0.0225 | -0.1487 | -117.8 | percent |
| tax | T9_interact_macro | int_AX_T | 0.1132 | 0.3864 | 0.2732 | 241.3 | percent |
| tax | T9_interact_macro | taxbase_lag | 0.6712 | 0.6838 | 0.0126 | 1.9 | percent |
| tax | T10_interact_full | c_A_T | 0.0263 | -0.0004 | -0.0267 | -101.5 | percent |
| tax | T10_interact_full | c_X_T | 0.1263 | -0.0353 | -0.1616 | -128 | percent |
| tax | T10_interact_full | int_AX_T | 0.1132 | 0.3423 | 0.2291 | 202.3 | percent |
| tax | T10_interact_full | taxbase_lag | 0.6712 | 0.6915 | 0.0203 | 3 | percent |

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
| baseline | Quadratic_all | A derivative terms jointly zero | 7.6465 | 4 | 1,182 | <0.001 |
| baseline | Quadratic_all | all second-order terms jointly zero | 15.6999 | 6 | 1,182 | <0.001 |
| tax | T5_macro | macro controls jointly zero | 9.6088 | 3 | 1,452 | <0.001 |
| tax | T7_layer2_A | external controls jointly zero | 6.1286 | 2 | 1,450 | 0.002 |
| tax | T7_layer2_A | all controls jointly zero | 9.1684 | 5 | 1,450 | <0.001 |
| tax | T8_interact_core | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 1.7345 | 2 | 1,454 | 0.177 |
| tax | T8_interact_core | interaction zero: int_AX_T = 0 | 0.4616 | 1 | 1,454 | 0.497 |
| tax | T9_interact_macro | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 2.638 | 2 | 1,451 | 0.072 |
| tax | T9_interact_macro | interaction zero: int_AX_T = 0 | 4.6886 | 1 | 1,451 | 0.031 |
| tax | T10_interact_full | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 2.1262 | 2 | 1,449 | 0.120 |
| tax | T10_interact_full | interaction zero: int_AX_T = 0 | 3.8762 | 1 | 1,449 | 0.049 |
| tax | T9_interact_macro | macro controls jointly zero | 10.2645 | 3 | 1,451 | <0.001 |
| tax | T10_interact_full | external controls jointly zero | 5.8929 | 2 | 1,449 | 0.003 |
| tax | T10_interact_full | all controls jointly zero | 9.3779 | 5 | 1,449 | <0.001 |
| doomloop | D3_full | low- and high-branch coefficients jointly zero | 1.7135 | 2 | 1,451 | 0.181 |
| doomloop | D3_full | macro controls jointly zero | 7.9462 | 3 | 1,451 | <0.001 |
| doomloop | D3_full | external controls jointly zero | 0.0786 | 2 | 1,451 | 0.924 |
| doomloop | D3_full | all controls jointly zero | 5.4828 | 5 | 1,451 | <0.001 |
| doomloop | R3_full | low- and high-branch coefficients jointly zero | 4.8924 | 2 | 1,471 | 0.008 |
| doomloop | R3_full | macro controls jointly zero | 1.4715 | 3 | 1,471 | 0.221 |
| doomloop | R3_full | external controls jointly zero | 0.3937 | 2 | 1,471 | 0.675 |
| doomloop | R3_full | all controls jointly zero | 1.3752 | 5 | 1,471 | 0.231 |
| doomloop-no-state | DN3_full | low- and high-branch coefficients jointly zero | 0.8058 | 2 | 1,452 | 0.447 |
| doomloop-no-state | DN3_full | macro controls jointly zero | 8.4887 | 3 | 1,452 | <0.001 |
| doomloop-no-state | DN3_full | external controls jointly zero | 0.1 | 2 | 1,452 | 0.905 |
| doomloop-no-state | DN3_full | all controls jointly zero | 5.9171 | 5 | 1,452 | <0.001 |
| doomloop-no-state | RN3_full | low- and high-branch coefficients jointly zero | 3.8329 | 2 | 1,472 | 0.022 |
| doomloop-no-state | RN3_full | macro controls jointly zero | 1.0129 | 3 | 1,472 | 0.386 |
| doomloop-no-state | RN3_full | external controls jointly zero | 0.1117 | 2 | 1,472 | 0.894 |
| doomloop-no-state | RN3_full | all controls jointly zero | 0.7919 | 5 | 1,472 | 0.555 |

### 6.2 代数、映射与时序公式检查

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | b_it equals debt_gdp exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 1.11e-16 | 1.00e-12 | 通过 |
| theta | centered versus raw b derivative | 2.78e-17 | 1.00e-12 | 通过 |
| theta | centered versus raw X derivative | 2.22e-16 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw tax formula | 2.08e-17 | 1.00e-12 | 通过 |
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
| baseline | Quadratic_all | tt | 0.0011 | 0.0011 | 7.36e-16 | 4.73e-17 |
| baseline | Quadratic_all | reserves | 0.0189 | 0.0189 | 1.28e-15 | 2.06e-16 |
| baseline | Quadratic_all | inflation_cpi | 0.1638 | 0.1638 | 4.41e-15 | 4.75e-16 |
| baseline | Quadratic_all | ln_currentgdp | 0.0146 | 0.0146 | 2.89e-15 | 4.12e-15 |
| baseline | Quadratic_all | growth | -0.1529 | -0.1529 | 5.27e-16 | 1.67e-16 |
| baseline | Quadratic_all | int_bX | 0.2785 | 0.2785 | 2.36e-14 | 3.03e-15 |
| baseline | Quadratic_all | int_AX | 0.5085 | 0.5085 | 6.98e-14 | 1.10e-14 |
| baseline | Quadratic_all | int_AB | -0.1514 | -0.1514 | 1.55e-15 | 0 |
| baseline | Quadratic_all | half_X2 | -0.0844 | -0.0844 | 2.52e-14 | 7.52e-14 |
| baseline | Quadratic_all | half_b2 | 0.0255 | 0.0255 | 1.73e-15 | 3.68e-16 |
| baseline | Quadratic_all | half_A2 | 0.4416 | 0.4416 | 1.38e-14 | 6.97e-15 |
| baseline | Quadratic_all | c_X | 0.2842 | 0.2842 | 2.93e-14 | 1.18e-15 |
| baseline | Quadratic_all | c_b | 0.0482 | 0.0482 | 4.44e-16 | 1.65e-17 |
| baseline | Quadratic_all | c_A | -0.0756 | -0.0756 | 5.79e-15 | 6.25e-17 |
| baseline | Interact_all | tt | -0.0018 | -0.0018 | 7.34e-16 | 2.23e-16 |
| baseline | Interact_all | reserves | 0.023 | 0.023 | 2.05e-15 | 3.85e-16 |
| baseline | Interact_all | inflation_cpi | 0.1631 | 0.1631 | 6.30e-15 | 3.40e-16 |
| baseline | Interact_all | ln_currentgdp | 0.0184 | 0.0184 | 3.71e-15 | 2.83e-15 |
| baseline | Interact_all | growth | -0.1577 | -0.1577 | 1.22e-15 | 4.30e-16 |
| baseline | Interact_all | int_AX | 0.0365 | 0.0365 | 3.80e-14 | 1.19e-14 |
| baseline | Interact_all | int_AB | -0.1862 | -0.1862 | 4.80e-15 | 5.72e-16 |
| baseline | Interact_all | c_b | 0.0553 | 0.0553 | 1.35e-15 | 1.18e-16 |
| baseline | Interact_all | c_X | 0.2448 | 0.2448 | 7.19e-14 | 1.27e-14 |
| baseline | Interact_all | c_A | -0.0819 | -0.0819 | 6.08e-15 | 2.43e-16 |
| baseline | Layer2_A | tt | 0.0004 | 0.0004 | 4.34e-16 | 3.36e-16 |
| baseline | Layer2_A | reserves | 0.0197 | 0.0197 | 5.20e-16 | 1.08e-15 |
| baseline | Layer2_A | inflation_cpi | 0.1557 | 0.1557 | 3.03e-15 | 2.57e-16 |
| baseline | Layer2_A | ln_currentgdp | 0.0237 | 0.0237 | 1.89e-15 | 3.44e-15 |
| baseline | Layer2_A | growth | -0.1731 | -0.1731 | 8.33e-17 | 1.94e-16 |
| baseline | Layer2_A | debt_gdp | 0.0527 | 0.0527 | 7.29e-16 | 3.01e-16 |
| baseline | Layer2_A | readiness100 | -0.0619 | -0.0619 | 1.08e-14 | 1.05e-15 |
| baseline | Layer2_A | vulnerability100 | 0.2019 | 0.2019 | 2.01e-14 | 3.81e-14 |
| tax | Spread_Quadratic_all | c_A | -0.0756 | -0.0756 | 3.59e-15 | 7.29e-17 |
| tax | Spread_Quadratic_all | c_b | 0.0482 | 0.0482 | 5.97e-16 | 4.60e-17 |
| tax | Spread_Quadratic_all | c_X | 0.2842 | 0.2842 | 1.32e-14 | 1.79e-14 |
| tax | Spread_Quadratic_all | half_A2 | 0.4416 | 0.4416 | 2.36e-14 | 9.10e-15 |
| tax | Spread_Quadratic_all | half_b2 | 0.0255 | 0.0255 | 1.58e-15 | 4.74e-16 |
| tax | Spread_Quadratic_all | half_X2 | -0.0844 | -0.0844 | 5.45e-14 | 1.40e-13 |
| tax | Spread_Quadratic_all | int_AB | -0.1514 | -0.1514 | 5.55e-16 | 4.30e-16 |
| tax | Spread_Quadratic_all | int_AX | 0.5085 | 0.5085 | 7.88e-14 | 1.46e-14 |
| tax | Spread_Quadratic_all | int_bX | 0.2785 | 0.2785 | 1.86e-14 | 3.25e-15 |
| tax | Spread_Quadratic_all | growth | -0.1529 | -0.1529 | 1.11e-15 | 1.39e-16 |
| tax | Spread_Quadratic_all | ln_currentgdp | 0.0146 | 0.0146 | 2.89e-15 | 2.12e-15 |
| tax | Spread_Quadratic_all | inflation_cpi | 0.1638 | 0.1638 | 4.05e-15 | 8.22e-16 |
| tax | Spread_Quadratic_all | reserves | 0.0189 | 0.0189 | 6.14e-16 | 2.84e-16 |
| tax | Spread_Quadratic_all | tt | 0.0011 | 0.0011 | 8.40e-16 | 8.67e-19 |
| tax | T7_layer2_A | vulnerability100 | -0.0781 | -0.0781 | 3.85e-14 | 1.17e-13 |
| tax | T7_layer2_A | readiness100 | 0.0078 | 0.0078 | 3.06e-15 | 1.89e-15 |
| tax | T7_layer2_A | taxbase_lag | 0.6957 | 0.6957 | 3.77e-14 | 2.54e-15 |
| tax | T7_layer2_A | growth | -0.1027 | -0.1027 | 1.11e-14 | 2.57e-16 |
| tax | T7_layer2_A | ln_currentgdp | -0.0088 | -0.0088 | 2.47e-15 | 9.39e-16 |
| tax | T7_layer2_A | inflation_cpi | -0.0489 | -0.0489 | 7.93e-15 | 2.84e-16 |
| tax | T7_layer2_A | reserves | -0.0038 | -0.0038 | 4.18e-16 | 2.95e-16 |
| tax | T7_layer2_A | tt | -0.0189 | -0.0189 | 2.38e-15 | 1.28e-16 |
| tax | T10_interact_full | c_A_T | -0.0004 | -0.0004 | 7.77e-16 | 8.60e-16 |
| tax | T10_interact_full | c_X_T | -0.0353 | -0.0353 | 3.69e-14 | 6.52e-15 |
| tax | T10_interact_full | int_AX_T | 0.3423 | 0.3423 | 1.24e-13 | 3.32e-14 |
| tax | T10_interact_full | taxbase_lag | 0.6915 | 0.6915 | 3.70e-14 | 3.02e-15 |
| tax | T10_interact_full | growth | -0.1038 | -0.1038 | 1.04e-14 | 6.94e-18 |
| tax | T10_interact_full | ln_currentgdp | -0.0098 | -0.0098 | 2.94e-15 | 2.90e-16 |
| tax | T10_interact_full | inflation_cpi | -0.0484 | -0.0484 | 7.92e-15 | 4.30e-16 |
| tax | T10_interact_full | reserves | -0.0022 | -0.0022 | 2.52e-16 | 6.77e-17 |
| tax | T10_interact_full | tt | -0.0186 | -0.0186 | 2.48e-15 | 3.10e-16 |
| doomloop | debt | debt_kink_low | 0.8529 | 0.8529 | 1.60e-13 | 1.10e-13 |
| doomloop | debt | debt_kink_high | -0.2317 | -0.2317 | 1.77e-14 | 8.58e-15 |
| doomloop | debt | debt_gdp | 0.0372 | 0.0372 | 4.45e-15 | 4.13e-16 |
| doomloop | debt | vulnerability100 | -0.198 | -0.198 | 4.16e-14 | 3.78e-13 |
| doomloop | debt | growth | -0.2155 | -0.2155 | 4.39e-15 | 1.80e-15 |
| doomloop | debt | ln_currentgdp | 0.0185 | 0.0185 | 1.43e-15 | 6.40e-16 |
| doomloop | debt | inflation_cpi | 0.147 | 0.147 | 2.78e-17 | 1.39e-17 |
| doomloop | debt | reserves | -0.007 | -0.007 | 7.80e-16 | 9.23e-16 |
| doomloop | debt | tt | 0.0013 | 0.0013 | 1.56e-16 | 2.08e-17 |
| doomloop | ready | ready_kink_low | 0.7942 | 0.7942 | 5.11e-15 | 1.89e-15 |
| doomloop | ready | ready_kink_high | 0.0607 | 0.0607 | 1.24e-15 | 6.45e-16 |
| doomloop | ready | readiness_lag | -0.1515 | -0.1515 | 2.94e-15 | 2.97e-15 |
| doomloop | ready | vulnerability100 | -0.077 | -0.077 | 3.43e-15 | 9.35e-14 |
| doomloop | ready | growth | 0.0182 | 0.0182 | 1.98e-16 | 5.03e-17 |
| doomloop | ready | ln_currentgdp | -0.002 | -0.002 | 3.90e-17 | 2.90e-15 |
| doomloop | ready | inflation_cpi | -0.0072 | -0.0072 | 1.85e-16 | 7.29e-17 |
| doomloop | ready | reserves | 0.0023 | 0.0023 | 4.81e-17 | 7.24e-16 |
| doomloop | ready | tt | -0.0028 | -0.0028 | 5.25e-17 | 4.97e-16 |
| doomloop-no-state | debt | debt_kink_low | 0.502 | 0.502 | 4.41e-14 | 6.07e-14 |
| doomloop-no-state | debt | debt_kink_high | -0.0448 | -0.0448 | 5.00e-15 | 6.74e-15 |
| doomloop-no-state | debt | vulnerability100 | -0.2454 | -0.2454 | 2.00e-14 | 3.42e-13 |
| doomloop-no-state | debt | growth | -0.2408 | -0.2408 | 1.03e-15 | 7.22e-16 |
| doomloop-no-state | debt | ln_currentgdp | 0.0166 | 0.0166 | 7.81e-16 | 7.08e-16 |
| doomloop-no-state | debt | inflation_cpi | 0.1511 | 0.1511 | 1.94e-16 | 2.78e-16 |
| doomloop-no-state | debt | reserves | -0.0077 | -0.0077 | 6.64e-16 | 6.80e-16 |
| doomloop-no-state | debt | tt | -0.0008 | -0.0008 | 3.20e-16 | 2.13e-16 |
| doomloop-no-state | ready | ready_kink_low | 0.6847 | 0.6847 | 2.22e-15 | 2.25e-15 |
| doomloop-no-state | ready | ready_kink_high | 0.0516 | 0.0516 | 8.74e-16 | 5.20e-15 |
| doomloop-no-state | ready | vulnerability100 | -0.1145 | -0.1145 | 1.79e-14 | 3.05e-13 |
| doomloop-no-state | ready | growth | 0.0228 | 0.0228 | 3.02e-16 | 7.98e-17 |
| doomloop-no-state | ready | ln_currentgdp | 0.0001 | 0.0001 | 2.29e-16 | 3.34e-15 |
| doomloop-no-state | ready | inflation_cpi | -0.0035 | -0.0035 | 2.58e-16 | 1.07e-16 |
| doomloop-no-state | ready | reserves | 0.0019 | 0.0019 | 3.49e-16 | 1.55e-15 |
| doomloop-no-state | ready | tt | -0.0011 | -0.0011 | 3.10e-17 | 1.44e-16 |

### 6.4 Cutoff 最小 RSS 复核

| 规格 | 方程 | 记录 cutoff | profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 原始 | debt | 0.015 | 3.9138 | 3.9138 | 0 | 通过 |
| 原始 | ready | 0.1095 | 0.4115 | 0.4115 | 0 | 通过 |
| 去状态变量 | debt | 0.0148 | 3.9268 | 3.9268 | 0 | 通过 |
| 去状态变量 | ready | 0.1095 | 0.4455 | 0.4455 | 0 | 通过 |

## 7. 图形 QA

四张单方程图和两张合并图均保留 PNG 与 PDF。单方程图使用连续 theta 网格并把 cutoff 精确插入网格；竖直虚线与 CSV 中记录的 cutoff 一致。曲线在 cutoff 处为 0，低支与高支按各自估计系数绘制；轴单位为统一比率。文档引用的是四张单方程 PNG，PDF 用于排版输出。

## 8. 必须保留的限制与建议

- 当前稳健标准误处理异方差，但不处理同一国家内序列相关；面板论文通常还应报告国家聚类标准误或适当的双向聚类/空间相关推断。
- cutoff 在同一样本上搜索，条件于 cutoff 的常规标准误偏窄风险未纳入。建议按国家重抽样，完整重复 baseline、tax/theta、cutoff 搜索和最终回归。
- theta 是生成解释变量；联合不确定性依赖跨方程协方差。当前只对两个组成边际量分别做 delta-method 标准误，不提供 theta 的联合 SE。
- 结果是固定效应相关性证据，不支持没有额外识别设计的因果措辞。
- 分支异号是经验 single-crossing 的额外形状要求，不由 kink 联合显著自动保证。当前两支同号的规格为：原始 readiness、去滞后 A readiness；必须与联合检验分开报告。

## 9. 原始诊断输出索引

完整 CSV/DTA/日志仍保留在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/`、`doomloop/stata_outputs/`。本文件是汇总层，不替代这些逐项机器可读结果。
