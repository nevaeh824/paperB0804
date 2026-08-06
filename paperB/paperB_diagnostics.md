# Paper B：统计检验与数据检查

> 生成时间：2026-08-06 19:24（Asia/Shanghai）。本文件汇总三个板块的诊断、样本审计、单位审计、稳健性检验与验证结果；正式公式和回归表见 `paperB_results.md`。

## 1. 总体评估：可在明确限制条件下使用

单位换算检查通过 27/27 项；代数/构造检查通过 24/24 项；cutoff 最小 RSS 复核通过 4/4 项。当前结果在代码一致性和样本内计算层面通过，但仍属于“Share with caveats”：生成 theta、样本内 cutoff 搜索和面板相关推断的不确定性尚未由完整流程 bootstrap 与国家聚类标准误覆盖。

## 2. 数据来源、单位与时序检查

唯一原始输入是 `data0804/invest_panel_weo.csv`。所有源百分数、比率和 0—100 指数在读入后除以 100；金额变量 `revenue`、`debt`、`CurrentGDP` 不缩放。本次回归直接构造 $b_{it}=debt_{it}/CurrentGDP_{it}$，不再以源字段 `debt_gdp` 作为 b；规模控制采用 `ln_currentgdp=ln(CurrentGDP)`，并严格执行：ln(CurrentGDP) is included in spread/readiness and excluded from tax/debt-change。关键因变量的精确定义为：

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
| Tax 共同样本 | 1,538 | 65 | 27 | 1996–2022 |
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
| reserves | 1,896 | 0.056 | 0.1249 | 1.31e-06 | 0.0203 | 1.5271 |
| tt | 1,730 | 1.0054 | 0.1831 | 0.3188 | 0.995 | 2.7308 |
| b_it | 1,866 | 0.5688 | 0.3448 | 0.0005 | 0.506 | 2.6097 |
| ln_currentgdp | 1,970 | 7.5434 | 2.9805 | 0.6323 | 7.3756 | 16.8549 |

### 3.2 Tax 与 theta 构造量

| 变量 | 样本 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| taxbase_lead | tax | 1,538 | 0.3386 | 0.1294 | 0.0392 | 0.3554 | 0.8069 |
| taxbase_lag | tax | 1,538 | 0.3385 | 0.1299 | 0.0392 | 0.3549 | 0.8069 |
| mA_hat_spread_ratio | theta_support | 1,221 | 0.0748 | 0.0627 | -0.0593 | 0.0763 | 0.3242 |
| mA_hat | theta_support | 1,221 | 0.0748 | 0.0627 | -0.0593 | 0.0763 | 0.3242 |
| spread_saving_component | theta_support | 1,221 | 0.0616 | 0.0865 | -0.0224 | 0.036 | 0.6806 |
| TA_hat | theta_support | 1,221 | -0.0087 | 0.0476 | -0.1218 | -0.0002 | 0.1026 |
| theta_hat_A | theta_support | 1,221 | 0.0529 | 0.1029 | -0.1289 | 0.0491 | 0.6841 |
| theta_hat_A | all_constructible | 1,819 | 0.062 | 0.1013 | -0.1289 | 0.0572 | 1.1232 |

### 3.3 含 readiness 双 cutoff 的 doomloop 回归变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| debt_with_b | debt | delta_debt_lead | dependent_variable | 1,552 | 0.0494 | 0.0623 | -0.4484 | 0.0408 | 0.5778 |
| debt_with_b | debt | debt_kink_low | regressor | 1,552 | 0.0021 | 0.0078 | 0 | 0 | 0.0582 |
| debt_with_b | debt | debt_kink_high | regressor | 1,552 | 0.0529 | 0.0475 | 0 | 0.0457 | 0.4013 |
| debt_with_b | debt | b_it_theta | regressor | 1,552 | 0.574 | 0.3474 | 0.039 | 0.5039 | 2.6097 |
| debt_with_b | debt | vulnerability100 | regressor | 1,552 | 0.3823 | 0.078 | 0.251 | 0.3675 | 0.5808 |
| debt_with_b | debt | growth | regressor | 1,552 | 0.0343 | 0.0366 | -0.1604 | 0.035 | 0.2462 |
| debt_with_b | debt | inflation_cpi | regressor | 1,552 | 0.0474 | 0.0579 | -0.0177 | 0.0305 | 0.723 |
| debt_with_b | debt | reserves | regressor | 1,552 | 0.0577 | 0.1326 | 2.41e-06 | 0.0189 | 1.5271 |
| debt_with_b | debt | tt | regressor | 1,552 | 1.0072 | 0.1799 | 0.3188 | 0.995 | 2.7308 |
| debt_with_b | debt | readiness100 | construction_input | 1,552 | 0.5054 | 0.1435 | 0.2021 | 0.5005 | 0.8072 |
| debt_with_b | debt | theta_hat_A | construction_input | 1,552 | 0.0596 | 0.1015 | -0.1289 | 0.0555 | 1.1232 |
| ready_with_lag | ready | J_readiness | dependent_variable | 1,571 | 0.0025 | 0.0183 | -0.22 | 0.0021 | 0.0823 |
| ready_with_lag | ready | ready_kink_low | regressor | 1,571 | 0.0027 | 0.0043 | -0.0102 | 0.002 | 0.0316 |
| ready_with_lag | ready | ready_kink_high | regressor | 1,571 | 0.0024 | 0.0086 | -0.0002 | 0 | 0.1224 |
| ready_with_lag | ready | ready_debt_kink_low | regressor | 1,571 | -6.35e-06 | 0.0002 | -0.0021 | 0 | 0.0012 |
| ready_with_lag | ready | ready_debt_kink_high | regressor | 1,571 | 0.0143 | 0.0223 | -0.0038 | 0.0065 | 0.2275 |
| ready_with_lag | ready | readiness_lag | regressor | 1,571 | 0.5012 | 0.1411 | 0.2021 | 0.4971 | 0.7973 |
| ready_with_lag | ready | vulnerability100 | regressor | 1,571 | 0.3807 | 0.0783 | 0.251 | 0.3648 | 0.5808 |
| ready_with_lag | ready | growth | regressor | 1,571 | 0.0334 | 0.0359 | -0.1604 | 0.0337 | 0.2462 |
| ready_with_lag | ready | inflation_cpi | regressor | 1,571 | 0.049 | 0.0588 | -0.0177 | 0.0323 | 0.723 |
| ready_with_lag | ready | reserves | regressor | 1,571 | 0.0492 | 0.115 | 2.41e-06 | 0.0188 | 1.5271 |
| ready_with_lag | ready | tt | regressor | 1,571 | 1.0066 | 0.1732 | 0.3188 | 0.995 | 2.7308 |
| ready_with_lag | ready | ln_currentgdp | regressor | 1,571 | 7.7309 | 3.0193 | 1.0006 | 7.4927 | 16.8549 |
| ready_with_lag | ready | interest_revenue | construction_input | 1,571 | 0.0859 | 0.1002 | -0.069 | 0.0562 | 0.7987 |
| ready_with_lag | ready | theta_hat_A | construction_input | 1,571 | 0.0618 | 0.1022 | -0.1289 | 0.0577 | 1.1232 |
| ready_with_lag | ready | readiness100 | construction_input | 1,571 | 0.5037 | 0.1416 | 0.2021 | 0.5001 | 0.7973 |
| debt_no_b | debt | delta_debt_lead | dependent_variable | 1,552 | 0.0494 | 0.0623 | -0.4484 | 0.0408 | 0.5778 |
| debt_no_b | debt | debt_kink_low | regressor | 1,552 | 0.0021 | 0.0078 | 0 | 0 | 0.0582 |
| debt_no_b | debt | debt_kink_high | regressor | 1,552 | 0.0529 | 0.0475 | 0 | 0.0457 | 0.4013 |
| debt_no_b | debt | vulnerability100 | regressor | 1,552 | 0.3823 | 0.078 | 0.251 | 0.3675 | 0.5808 |
| debt_no_b | debt | growth | regressor | 1,552 | 0.0343 | 0.0366 | -0.1604 | 0.035 | 0.2462 |
| debt_no_b | debt | inflation_cpi | regressor | 1,552 | 0.0474 | 0.0579 | -0.0177 | 0.0305 | 0.723 |
| debt_no_b | debt | reserves | regressor | 1,552 | 0.0577 | 0.1326 | 2.41e-06 | 0.0189 | 1.5271 |
| debt_no_b | debt | tt | regressor | 1,552 | 1.0072 | 0.1799 | 0.3188 | 0.995 | 2.7308 |
| debt_no_b | debt | readiness100 | construction_input | 1,552 | 0.5054 | 0.1435 | 0.2021 | 0.5005 | 0.8072 |
| debt_no_b | debt | theta_hat_A | construction_input | 1,552 | 0.0596 | 0.1015 | -0.1289 | 0.0555 | 1.1232 |
| ready_no_lag | ready | J_readiness | dependent_variable | 1,571 | 0.0025 | 0.0183 | -0.22 | 0.0021 | 0.0823 |
| ready_no_lag | ready | ready_kink_low | regressor | 1,571 | 0.0046 | 0.006 | -0.0121 | 0.0038 | 0.0425 |
| ready_no_lag | ready | ready_kink_high | regressor | 1,571 | 0.0015 | 0.0068 | 0 | 0 | 0.1185 |
| ready_no_lag | ready | vulnerability100 | regressor | 1,571 | 0.3807 | 0.0783 | 0.251 | 0.3648 | 0.5808 |
| ready_no_lag | ready | growth | regressor | 1,571 | 0.0334 | 0.0359 | -0.1604 | 0.0337 | 0.2462 |
| ready_no_lag | ready | inflation_cpi | regressor | 1,571 | 0.049 | 0.0588 | -0.0177 | 0.0323 | 0.723 |
| ready_no_lag | ready | reserves | regressor | 1,571 | 0.0492 | 0.115 | 2.41e-06 | 0.0188 | 1.5271 |
| ready_no_lag | ready | tt | regressor | 1,571 | 1.0066 | 0.1732 | 0.3188 | 0.995 | 2.7308 |
| ready_no_lag | ready | ln_currentgdp | regressor | 1,571 | 7.7309 | 3.0193 | 1.0006 | 7.4927 | 16.8549 |
| ready_no_lag | ready | interest_revenue | construction_input | 1,571 | 0.0859 | 0.1002 | -0.069 | 0.0562 | 0.7987 |
| ready_no_lag | ready | theta_hat_A | construction_input | 1,571 | 0.0618 | 0.1022 | -0.1289 | 0.0577 | 1.1232 |
| ready_no_lag | ready | readiness100 | construction_input | 1,571 | 0.5037 | 0.1416 | 0.2021 | 0.5001 | 0.7973 |

## 4. 缺失值、重复键与固定效应可识别性

国家—年份重复键检查在三段流程中均为零；代码遇到重复键会直接终止，不会静默删除。各段共同样本在估计前锁定，逐步模型与 cutoff 候选使用相同观测。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 | 独占损失 |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 525 | 26.62 | 331 |
| baseline | — | vulnerability100 | 58 | 2.94 | 0 |
| baseline | — | readiness100 | 58 | 2.94 | 0 |
| baseline | — | b_it | 106 | 5.38 | 11 |
| baseline | — | growth | 11 | 0.56 | 0 |
| baseline | — | inflation_cpi | 7 | 0.35 | 1 |
| baseline | — | reserves | 76 | 3.85 | 3 |
| baseline | — | tt | 242 | 12.27 | 94 |
| baseline | — | ln_currentgdp | 2 | 0.1 | 0 |
| tax | — | taxbase_lead | 117 | 5.93 | 65 |
| tax | — | readiness100 | 58 | 2.94 | 0 |
| tax | — | vulnerability100 | 58 | 2.94 | 0 |
| tax | — | taxbase_lag | 117 | 5.93 | 14 |
| tax | — | b_it_theta | 106 | 5.38 | 11 |
| tax | — | growth | 11 | 0.56 | 1 |
| tax | — | inflation_cpi | 7 | 0.35 | 1 |
| tax | — | reserves | 76 | 3.85 | 26 |
| tax | — | tt | 242 | 12.27 | 131 |
| doomloop | debt | delta_debt_lead | 174 | 8.82 | 65 |
| doomloop | debt | readiness100 | 58 | 2.94 | 0 |
| doomloop | debt | theta_hat_A | 153 | 7.76 | 0 |
| doomloop | debt | b_it_theta | 106 | 5.38 | 0 |
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
| doomloop | ready | inflation_cpi | 7 | 0.35 | 1 |
| doomloop | ready | reserves | 76 | 3.85 | 27 |
| doomloop | ready | tt | 242 | 12.27 | 129 |
| doomloop | ready | ln_currentgdp | 2 | 0.1 | 0 |

### 4.2 Within 变异

| 板块 | 方程 | 变量 | 总体 SD | Within SD | Within/总体 | FE 识别 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | — | bond_spreads | 0.0452 | 0.0181 | 0.4003 | adequate |
| baseline | — | bond_10y | 0.0449 | 0.0228 | 0.5081 | adequate |
| baseline | — | vulnerability100 | 0.0781 | 0.0106 | 0.1362 | adequate |
| baseline | — | readiness100 | 0.1423 | 0.0435 | 0.3054 | adequate |
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
| baseline | — | capitaGDP | 25419.7298 | 7055.147 | 0.2775 | adequate |
| baseline | — | interest_revenue | 0.098 | 0.0475 | 0.4851 | adequate |
| baseline | — | b_it | 0.3448 | 0.1815 | 0.5263 | adequate |
| baseline | — | ln_currentgdp | 2.9805 | 0.7723 | 0.2591 | adequate |
| tax | — | taxbase_lead | 0.1294 | 0.0313 | 0.2418 | adequate |
| tax | — | taxbase_lag | 0.1299 | 0.0315 | 0.2428 | adequate |
| tax | — | readiness100 | 0.1435 | 0.0399 | 0.2779 | adequate |
| tax | — | vulnerability100 | 0.0778 | 0.01 | 0.1284 | adequate |
| tax | — | b_it_theta | 0.3482 | 0.1701 | 0.4886 | adequate |
| tax | — | growth | 0.0365 | 0.0326 | 0.8919 | adequate |
| tax | — | inflation_cpi | 0.0563 | 0.0421 | 0.7481 | adequate |
| tax | — | reserves | 0.1328 | 0.0638 | 0.4806 | adequate |
| tax | — | tt | 0.1727 | 0.1538 | 0.8903 | adequate |
| doomloop | debt | delta_debt_lead | 0.0623 | 0.0551 | 0.8844 | adequate |
| doomloop | debt | theta_hat_A | 0.1015 | 0.0514 | 0.506 | adequate |
| doomloop | debt | readiness100 | 0.1435 | 0.0401 | 0.2798 | adequate |
| doomloop | debt | b_it_theta | 0.3474 | 0.1698 | 0.4888 | adequate |
| doomloop | debt | vulnerability100 | 0.078 | 0.0101 | 0.1293 | adequate |
| doomloop | debt | growth | 0.0366 | 0.0326 | 0.8907 | adequate |
| doomloop | debt | inflation_cpi | 0.0579 | 0.0435 | 0.7513 | adequate |
| doomloop | debt | reserves | 0.1326 | 0.0637 | 0.4805 | adequate |
| doomloop | debt | tt | 0.1799 | 0.1584 | 0.8807 | adequate |
| doomloop | ready | J_readiness | 0.0183 | 0.0182 | 0.9936 | adequate |
| doomloop | ready | theta_hat_A | 0.1022 | 0.0513 | 0.5021 | adequate |
| doomloop | ready | interest_revenue | 0.1002 | 0.0464 | 0.4634 | adequate |
| doomloop | ready | readiness100 | 0.1416 | 0.0387 | 0.2731 | adequate |
| doomloop | ready | readiness_lag | 0.1411 | 0.0397 | 0.2815 | adequate |
| doomloop | ready | vulnerability100 | 0.0783 | 0.0103 | 0.132 | adequate |
| doomloop | ready | growth | 0.0359 | 0.032 | 0.8902 | adequate |
| doomloop | ready | inflation_cpi | 0.0588 | 0.0441 | 0.7499 | adequate |
| doomloop | ready | reserves | 0.115 | 0.0623 | 0.5418 | adequate |
| doomloop | ready | tt | 0.1732 | 0.1545 | 0.892 | adequate |
| doomloop | ready | ln_currentgdp | 3.0193 | 0.6459 | 0.2139 | adequate |

## 5. 共线性、相关性与系数变化

### 5.1 VIF/条件数

| 板块 | 变量 | VIF | 容忍度 | 条件数 |
| --- | ---: | ---: | ---: | ---: |
| baseline-linear | vulnerability100 | 1.4688 | 0.6808 | 2.1233 |
| baseline-linear | readiness100 | 1.0142 | 0.986 | 2.1233 |
| baseline-linear | b_it | 1.1397 | 0.8774 | 2.1233 |
| baseline-linear | growth | 1.0782 | 0.9275 | 2.1233 |
| baseline-linear | inflation_cpi | 1.1254 | 0.8886 | 2.1233 |
| baseline-linear | reserves | 1.1001 | 0.909 | 2.1233 |
| baseline-linear | tt | 1.0507 | 0.9517 | 2.1233 |
| baseline-linear | ln_currentgdp | 1.6317 | 0.6129 | 2.1233 |
| baseline-quadratic | c_A | 1.2357 | 0.8093 | 4.5979 |
| baseline-quadratic | c_b | 1.4712 | 0.6797 | 4.5979 |
| baseline-quadratic | c_X | 1.8994 | 0.5265 | 4.5979 |
| baseline-quadratic | half_A2 | 2.8977 | 0.3451 | 4.5979 |
| baseline-quadratic | half_b2 | 1.5919 | 0.6282 | 4.5979 |
| baseline-quadratic | half_X2 | 2.4076 | 0.4153 | 4.5979 |
| baseline-quadratic | int_AB | 2.1547 | 0.4641 | 4.5979 |
| baseline-quadratic | int_AX | 3.1412 | 0.3184 | 4.5979 |
| baseline-quadratic | int_bX | 2.345 | 0.4264 | 4.5979 |
| baseline-quadratic | growth | 1.0986 | 0.9103 | 4.5979 |
| baseline-quadratic | inflation_cpi | 1.1477 | 0.8713 | 4.5979 |
| baseline-quadratic | reserves | 1.2345 | 0.81 | 4.5979 |
| baseline-quadratic | tt | 1.072 | 0.9328 | 4.5979 |
| baseline-quadratic | ln_currentgdp | 2.2516 | 0.4441 | 4.5979 |
| tax | readiness100 | 1.0402 | 0.9613 | 1.5695 |
| tax | vulnerability100 | 1.0589 | 0.9444 | 1.5695 |
| tax | taxbase_lag | 1.1648 | 0.8585 | 1.5695 |
| tax | growth | 1.1181 | 0.8944 | 1.5695 |
| tax | inflation_cpi | 1.1065 | 0.9037 | 1.5695 |
| tax | reserves | 1.0139 | 0.9863 | 1.5695 |
| tax | tt | 1.055 | 0.9479 | 1.5695 |
| tax | c_A_T | 1.0976 | 0.9111 | 1.6635 |
| tax | c_X_T | 1.2182 | 0.8209 | 1.6635 |
| tax | int_AX_T | 1.2075 | 0.8281 | 1.6635 |
| tax | taxbase_lag | 1.1701 | 0.8546 | 1.6635 |
| tax | growth | 1.1184 | 0.8941 | 1.6635 |
| tax | inflation_cpi | 1.1072 | 0.9032 | 1.6635 |
| tax | reserves | 1.029 | 0.9718 | 1.6635 |
| tax | tt | 1.0565 | 0.9465 | 1.6635 |
| tax | c_A_T | 1.2563 | 0.796 | 3.6146 |
| tax | c_X_T | 1.7223 | 0.5806 | 3.6146 |
| tax | half_A2_T | 2.4263 | 0.4121 | 3.6146 |
| tax | half_X2_T | 2.3177 | 0.4315 | 3.6146 |
| tax | int_AX_T | 2.8963 | 0.3453 | 3.6146 |
| tax | taxbase_lag | 1.2694 | 0.7878 | 3.6146 |
| tax | b_it_theta | 1.1982 | 0.8346 | 3.6146 |
| tax | growth | 1.1892 | 0.8409 | 3.6146 |
| tax | inflation_cpi | 1.1306 | 0.8845 | 3.6146 |
| tax | reserves | 1.1323 | 0.8831 | 3.6146 |
| tax | tt | 1.1291 | 0.8857 | 3.6146 |

### 5.2 高绝对相关系数（排除对角线与镜像重复）

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |
| baseline | vulnerability100 | readiness100 | -0.7642 |
| tax | readiness100 | vulnerability100 | -0.7792 |
| tax | readiness100 | taxbase_lag | 0.6306 |
| tax | vulnerability100 | taxbase_lag | -0.7612 |

### 5.3 加入控制变量后的系数变化

| 板块 | 模型 | 变量 | 基准系数 | 新系数 | 绝对变化 | %变化 | 报告规则 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | C_macro | vulnerability100 | 0.3033 | 0.1456 | -0.1577 | -52 | percent |
| baseline | C_macro | readiness100 | -0.0639 | -0.0594 | 0.0044 | 7 | percent |
| baseline | C_macro | b_it | 0.0617 | 0.0515 | -0.0102 | -16.6 | percent |
| baseline | Layer1_X | vulnerability100 | 0.3033 | 0.1995 | -0.1037 | -34.2 | percent |
| baseline | Layer1_X | b_it | 0.0617 | 0.0519 | -0.0098 | -15.9 | percent |
| baseline | Layer2_A | vulnerability100 | 0.3033 | 0.2044 | -0.0988 | -32.6 | percent |
| baseline | Layer2_A | readiness100 | -0.0639 | -0.062 | 0.0019 | 2.9 | percent |
| baseline | Layer2_A | b_it | 0.0617 | 0.0527 | -0.009 | -14.7 | percent |
| tax | T5_macro | vulnerability100 | 0.1046 | 0.1405 | 0.0359 | 34.3 | percent |
| tax | T5_macro | readiness100 | 0.0286 | 0.0251 | -0.0034 | -12.1 | percent |
| tax | T5_macro | taxbase_lag | 0.6741 | 0.7078 | 0.0337 | 5 | percent |
| tax | T7_layer2_A | vulnerability100 | 0.1046 | 0.0715 | -0.0331 | -31.6 | percent |
| tax | T7_layer2_A | readiness100 | 0.0286 | 0.0135 | -0.0151 | -52.9 | percent |
| tax | T7_layer2_A | taxbase_lag | 0.6741 | 0.7113 | 0.0371 | 5.5 | percent |
| tax | T9_interact_macro | c_A_T | 0.026 | 0.0225 | -0.0036 | -13.7 | percent |
| tax | T9_interact_macro | c_X_T | 0.1239 | 0.1607 | 0.0368 | 29.7 | percent |
| tax | T9_interact_macro | int_AX_T | 0.1144 | 0.1197 | 0.0053 | 4.6 | percent |
| tax | T9_interact_macro | taxbase_lag | 0.6733 | 0.7069 | 0.0336 | 5 | percent |
| tax | T10_interact_full | c_A_T | 0.026 | 0.0096 | -0.0165 | -63.2 | percent |
| tax | T10_interact_full | c_X_T | 0.1239 | 0.1002 | -0.0237 | -19.1 | percent |
| tax | T10_interact_full | int_AX_T | 0.1144 | 0.1671 | 0.0526 | 46 | percent |
| tax | T10_interact_full | taxbase_lag | 0.6733 | 0.71 | 0.0367 | 5.4 | percent |

## 6. 统计检验

### 6.1 Wald 联合检验

| 板块 | 模型 | 原假设 | F | 分子 df | 分母 df | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_AB | c_A = int_AB = 0 | 24.7865 | 2 | 1,187 | <0.001 |
| baseline | Interact_AB | all interactions = 0: int_AB = 0 | 41.8329 | 1 | 1,187 | <0.001 |
| baseline | Interact_AX | c_A = int_AX = 0 | 8.5935 | 2 | 1,187 | <0.001 |
| baseline | Interact_AX | all interactions = 0: int_AX = 0 | 0.1324 | 1 | 1,187 | 0.716 |
| baseline | Interact_all | c_A = int_AB = 0 | 24.1358 | 2 | 1,186 | <0.001 |
| baseline | Interact_all | c_A = int_AX = 0 | 12.478 | 2 | 1,186 | <0.001 |
| baseline | Interact_all | c_A = int_AB = int_AX = 0 | 16.5391 | 3 | 1,186 | <0.001 |
| baseline | Interact_all | all interactions = 0: int_AB = int_AX = 0 | 21.0436 | 2 | 1,186 | <0.001 |
| baseline | Quadratic_all | A derivative terms jointly zero | 7.7404 | 4 | 1,182 | <0.001 |
| baseline | Quadratic_all | all second-order terms jointly zero | 15.6939 | 6 | 1,182 | <0.001 |
| tax | T5_macro | macro controls jointly zero | 5.3644 | 2 | 1,442 | 0.005 |
| tax | T7_layer2_A | external controls jointly zero | 7.9019 | 2 | 1,440 | <0.001 |
| tax | T7_layer2_A | all controls jointly zero | 9.5427 | 4 | 1,440 | <0.001 |
| tax | T8_interact_core | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 1.7165 | 2 | 1,443 | 0.180 |
| tax | T8_interact_core | interaction zero: int_AX_T = 0 | 0.4656 | 1 | 1,443 | 0.495 |
| tax | T9_interact_macro | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 1.3266 | 2 | 1,441 | 0.266 |
| tax | T9_interact_macro | interaction zero: int_AX_T = 0 | 0.5017 | 1 | 1,441 | 0.479 |
| tax | T10_interact_full | adaptation terms jointly zero: c_A_T = int_AX_T = 0 | 0.8442 | 2 | 1,439 | 0.430 |
| tax | T10_interact_full | interaction zero: int_AX_T = 0 | 0.9846 | 1 | 1,439 | 0.321 |
| tax | T9_interact_macro | macro controls jointly zero | 5.4361 | 2 | 1,441 | 0.004 |
| tax | T10_interact_full | external controls jointly zero | 7.9105 | 2 | 1,439 | <0.001 |
| tax | T10_interact_full | all controls jointly zero | 9.5938 | 4 | 1,439 | <0.001 |
| tax | T11_quadratic_full | marginal-A terms jointly zero: c_A_T = half_A2_T = int_AX_T = 0 | 2.0434 | 3 | 1,436 | 0.106 |
| tax | T11_quadratic_full | all second-order tax terms jointly zero | 2.0489 | 3 | 1,436 | 0.105 |
| tax | T11_quadratic_full | b_it coefficient zero | 13.0788 | 1 | 1,436 | <0.001 |
| tax | T11_quadratic_full | all controls jointly zero | 6.6272 | 4 | 1,436 | <0.001 |
| doomloop | D3_full | low- and high-branch coefficients jointly zero | 2.0971 | 2 | 1,452 | 0.123 |
| doomloop | D3_full | macro controls jointly zero | 9.6037 | 2 | 1,452 | <0.001 |
| doomloop | D3_full | external controls jointly zero | 0.6159 | 2 | 1,452 | 0.540 |
| doomloop | D3_full | all controls jointly zero | 4.8891 | 4 | 1,452 | <0.001 |
| doomloop | R3_full | low- and high-branch coefficients jointly zero | 12.4496 | 2 | 1,471 | <0.001 |
| doomloop | R3_full | macro controls jointly zero | 0.5713 | 2 | 1,471 | 0.565 |
| doomloop | R3_full | external controls jointly zero | 0.6728 | 2 | 1,471 | 0.510 |
| doomloop | R3_full | all controls jointly zero | 0.8001 | 4 | 1,471 | 0.525 |
| doomloop | RD3_debtcut | low- and high-branch coefficients jointly zero | 5.3061 | 2 | 1,471 | 0.005 |
| doomloop | RD3_debtcut | macro controls jointly zero | 0.3165 | 2 | 1,471 | 0.729 |
| doomloop | RD3_debtcut | external controls jointly zero | 0.6711 | 2 | 1,471 | 0.511 |
| doomloop | RD3_debtcut | all controls jointly zero | 0.4859 | 4 | 1,471 | 0.746 |
| doomloop-no-state | DN3_full | low- and high-branch coefficients jointly zero | 2.1918 | 2 | 1,453 | 0.112 |
| doomloop-no-state | DN3_full | macro controls jointly zero | 10.5884 | 2 | 1,453 | <0.001 |
| doomloop-no-state | DN3_full | external controls jointly zero | 0.5112 | 2 | 1,453 | 0.600 |
| doomloop-no-state | DN3_full | all controls jointly zero | 5.4571 | 4 | 1,453 | <0.001 |
| doomloop-no-state | RN3_full | low- and high-branch coefficients jointly zero | 5.6396 | 2 | 1,472 | 0.004 |
| doomloop-no-state | RN3_full | macro controls jointly zero | 1.409 | 2 | 1,472 | 0.245 |
| doomloop-no-state | RN3_full | external controls jointly zero | 0.1957 | 2 | 1,472 | 0.822 |
| doomloop-no-state | RN3_full | all controls jointly zero | 0.9704 | 4 | 1,472 | 0.423 |

### 6.2 代数、映射与时序公式检查

| 板块 | 检查 | 最大绝对误差 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| theta | b_it equals debt/CurrentGDP exactly | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw mA formula | 1.11e-16 | 1.00e-12 | 通过 |
| theta | centered versus raw b derivative | 5.55e-17 | 1.00e-12 | 通过 |
| theta | centered versus raw X derivative | 1.11e-16 | 1.00e-12 | 通过 |
| theta | stored versus predictnl mA | 0 | 1.00e-12 | 通过 |
| theta | centered versus raw tax formula | 5.55e-17 | 1.00e-12 | 通过 |
| theta | stored versus predictnl tax margin | 0 | 1.00e-12 | 通过 |
| theta | theta component identity | 0 | 1.00e-12 | 通过 |
| doomloop | theta uses b_it*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop | b_it maps to debt/CurrentGDP | 0 | 1.00e-10 | 通过 |
| doomloop | delta_debt_lead formula | 0 | 1.00e-10 | 通过 |
| doomloop | J_readiness formula | 0 | 1.00e-10 | 通过 |
| doomloop | debt low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop | debt high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop | readiness low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop | readiness high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop | readiness low hinge at debt cutoff | 0 | 1.00e-10 | 通过 |
| doomloop | readiness high hinge at debt cutoff | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | theta uses b_it*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | b_it maps to debt/CurrentGDP | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | no-b debt low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | no-b debt high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | no-lag readiness low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-no-state | no-lag readiness high hinge regressor | 0 | 1.00e-10 | 通过 |

### 6.3 areg 与显式 LSDV 复核

| 板块 | 模型/方程 | 变量 | areg | LSDV | \|系数差\| | \|SE差\| |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Quadratic_all | ln_currentgdp | 0.0147 | 0.0147 | 6.44e-15 | 1.88e-15 |
| baseline | Quadratic_all | tt | 0.0011 | 0.0011 | 1.64e-15 | 9.97e-17 |
| baseline | Quadratic_all | reserves | 0.0189 | 0.0189 | 1.25e-15 | 3.12e-17 |
| baseline | Quadratic_all | inflation_cpi | 0.1634 | 0.1634 | 1.03e-14 | 6.59e-16 |
| baseline | Quadratic_all | growth | -0.1529 | -0.1529 | 2.03e-15 | 2.32e-16 |
| baseline | Quadratic_all | int_bX | 0.278 | 0.278 | 4.66e-14 | 3.12e-15 |
| baseline | Quadratic_all | int_AX | 0.5114 | 0.5114 | 4.11e-14 | 1.00e-14 |
| baseline | Quadratic_all | int_AB | -0.1516 | -0.1516 | 3.75e-15 | 6.94e-17 |
| baseline | Quadratic_all | half_X2 | -0.0672 | -0.0672 | 5.68e-13 | 8.56e-14 |
| baseline | Quadratic_all | half_b2 | 0.0254 | 0.0254 | 5.00e-15 | 5.81e-16 |
| baseline | Quadratic_all | half_A2 | 0.4444 | 0.4444 | 1.61e-14 | 4.83e-15 |
| baseline | Quadratic_all | c_X | 0.2872 | 0.2872 | 2.35e-14 | 1.20e-14 |
| baseline | Quadratic_all | c_b | 0.0483 | 0.0483 | 4.72e-16 | 1.95e-17 |
| baseline | Quadratic_all | c_A | -0.0756 | -0.0756 | 2.51e-15 | 8.33e-17 |
| baseline | Interact_all | ln_currentgdp | 0.0186 | 0.0186 | 6.01e-15 | 1.52e-15 |
| baseline | Interact_all | tt | -0.0018 | -0.0018 | 1.43e-15 | 2.34e-16 |
| baseline | Interact_all | reserves | 0.0231 | 0.0231 | 3.04e-15 | 1.64e-16 |
| baseline | Interact_all | inflation_cpi | 0.1627 | 0.1627 | 1.06e-14 | 8.81e-16 |
| baseline | Interact_all | growth | -0.1576 | -0.1576 | 3.03e-15 | 5.55e-17 |
| baseline | Interact_all | int_AX | 0.0346 | 0.0346 | 6.48e-14 | 9.41e-15 |
| baseline | Interact_all | int_AB | -0.1847 | -0.1847 | 1.19e-14 | 2.22e-16 |
| baseline | Interact_all | c_b | 0.0555 | 0.0555 | 1.60e-15 | 1.13e-16 |
| baseline | Interact_all | c_X | 0.248 | 0.248 | 8.37e-14 | 1.25e-14 |
| baseline | Interact_all | c_A | -0.0816 | -0.0816 | 4.39e-15 | 8.67e-17 |
| baseline | Layer2_A | ln_currentgdp | 0.0238 | 0.0238 | 6.30e-15 | 5.73e-15 |
| baseline | Layer2_A | tt | 0.0005 | 0.0005 | 1.79e-15 | 2.63e-16 |
| baseline | Layer2_A | reserves | 0.0196 | 0.0196 | 3.47e-15 | 7.02e-15 |
| baseline | Layer2_A | inflation_cpi | 0.1555 | 0.1555 | 1.12e-14 | 5.72e-16 |
| baseline | Layer2_A | growth | -0.1734 | -0.1734 | 4.27e-15 | 4.86e-17 |
| baseline | Layer2_A | b_it | 0.0527 | 0.0527 | 2.35e-15 | 8.37e-16 |
| baseline | Layer2_A | readiness100 | -0.062 | -0.062 | 6.90e-15 | 5.02e-15 |
| baseline | Layer2_A | vulnerability100 | 0.2044 | 0.2044 | 8.38e-14 | 2.00e-13 |
| tax | Spread_Quadratic_all | c_A | -0.0756 | -0.0756 | 7.40e-15 | 1.28e-16 |
| tax | Spread_Quadratic_all | c_b | 0.0483 | 0.0483 | 4.30e-16 | 4.03e-17 |
| tax | Spread_Quadratic_all | c_X | 0.2872 | 0.2872 | 1.85e-14 | 4.86e-15 |
| tax | Spread_Quadratic_all | half_A2 | 0.4444 | 0.4444 | 1.80e-14 | 3.33e-16 |
| tax | Spread_Quadratic_all | half_b2 | 0.0254 | 0.0254 | 3.93e-15 | 2.46e-16 |
| tax | Spread_Quadratic_all | half_X2 | -0.0672 | -0.0672 | 3.53e-13 | 1.73e-14 |
| tax | Spread_Quadratic_all | int_AB | -0.1516 | -0.1516 | 7.49e-16 | 1.80e-16 |
| tax | Spread_Quadratic_all | int_AX | 0.5114 | 0.5114 | 1.08e-13 | 2.14e-15 |
| tax | Spread_Quadratic_all | int_bX | 0.278 | 0.278 | 2.52e-14 | 3.66e-15 |
| tax | Spread_Quadratic_all | growth | -0.1529 | -0.1529 | 8.88e-16 | 1.67e-16 |
| tax | Spread_Quadratic_all | inflation_cpi | 0.1634 | 0.1634 | 5.47e-15 | 8.36e-16 |
| tax | Spread_Quadratic_all | reserves | 0.0189 | 0.0189 | 5.20e-17 | 5.72e-17 |
| tax | Spread_Quadratic_all | tt | 0.0011 | 0.0011 | 1.16e-15 | 1.76e-16 |
| tax | Spread_Quadratic_all | ln_currentgdp | 0.0147 | 0.0147 | 3.97e-15 | 4.31e-15 |
| tax | T7_layer2_A | vulnerability100 | 0.0715 | 0.0715 | 1.84e-14 | 1.66e-14 |
| tax | T7_layer2_A | readiness100 | 0.0135 | 0.0135 | 3.00e-15 | 3.28e-15 |
| tax | T7_layer2_A | taxbase_lag | 0.7113 | 0.7113 | 1.91e-14 | 8.33e-16 |
| tax | T7_layer2_A | growth | -0.0993 | -0.0993 | 1.01e-14 | 7.70e-16 |
| tax | T7_layer2_A | inflation_cpi | -0.0479 | -0.0479 | 5.52e-15 | 1.39e-17 |
| tax | T7_layer2_A | reserves | 0.001 | 0.001 | 4.67e-16 | 6.94e-17 |
| tax | T7_layer2_A | tt | -0.0239 | -0.0239 | 9.37e-17 | 2.13e-16 |
| tax | T10_interact_full | c_A_T | 0.0096 | 0.0096 | 4.53e-15 | 2.26e-16 |
| tax | T10_interact_full | c_X_T | 0.1002 | 0.1002 | 4.65e-14 | 1.40e-14 |
| tax | T10_interact_full | int_AX_T | 0.1671 | 0.1671 | 2.40e-14 | 8.60e-15 |
| tax | T10_interact_full | taxbase_lag | 0.71 | 0.71 | 1.73e-14 | 9.30e-16 |
| tax | T10_interact_full | growth | -0.0997 | -0.0997 | 1.00e-14 | 9.02e-17 |
| tax | T10_interact_full | inflation_cpi | -0.0475 | -0.0475 | 5.30e-15 | 2.50e-16 |
| tax | T10_interact_full | reserves | 0.002 | 0.002 | 9.01e-16 | 1.13e-17 |
| tax | T10_interact_full | tt | -0.024 | -0.024 | 3.82e-17 | 1.96e-16 |
| tax | T11_quadratic_full | c_A_T | 0.0003 | 0.0003 | 4.99e-15 | 4.16e-16 |
| tax | T11_quadratic_full | c_X_T | 0.1116 | 0.1116 | 4.32e-14 | 1.38e-14 |
| tax | T11_quadratic_full | half_A2_T | -0.3985 | -0.3985 | 8.44e-15 | 1.10e-14 |
| tax | T11_quadratic_full | half_X2_T | -0.3454 | -0.3454 | 6.48e-14 | 2.24e-14 |
| tax | T11_quadratic_full | int_AX_T | -0.1708 | -0.1708 | 3.61e-14 | 2.62e-14 |
| tax | T11_quadratic_full | taxbase_lag | 0.6769 | 0.6769 | 1.80e-14 | 2.28e-15 |
| tax | T11_quadratic_full | b_it_theta | 0.0206 | 0.0206 | 4.34e-16 | 1.01e-16 |
| tax | T11_quadratic_full | growth | -0.0687 | -0.0687 | 1.07e-14 | 2.08e-16 |
| tax | T11_quadratic_full | inflation_cpi | -0.0433 | -0.0433 | 5.50e-15 | 2.67e-16 |
| tax | T11_quadratic_full | reserves | 0.0058 | 0.0058 | 5.96e-16 | 2.86e-17 |
| tax | T11_quadratic_full | tt | -0.0219 | -0.0219 | 3.12e-17 | 7.46e-17 |
| doomloop | debt | debt_kink_low | 0.1715 | 0.1715 | 1.35e-14 | 2.33e-14 |
| doomloop | debt | debt_kink_high | -0.2357 | -0.2357 | 3.16e-15 | 0 |
| doomloop | debt | b_it_theta | 0.0196 | 0.0196 | 6.94e-18 | 1.80e-16 |
| doomloop | debt | vulnerability100 | -0.5894 | -0.5894 | 1.30e-14 | 2.12e-13 |
| doomloop | debt | growth | -0.2447 | -0.2447 | 3.33e-16 | 3.33e-16 |
| doomloop | debt | inflation_cpi | 0.1384 | 0.1384 | 4.44e-16 | 3.61e-16 |
| doomloop | debt | reserves | -0.0166 | -0.0166 | 4.02e-16 | 2.08e-17 |
| doomloop | debt | tt | 0.0071 | 0.0071 | 1.28e-16 | 4.34e-16 |
| doomloop | ready | ready_kink_low | 1.7613 | 1.7613 | 1.89e-14 | 3.33e-16 |
| doomloop | ready | ready_kink_high | 0.037 | 0.037 | 1.03e-15 | 2.19e-15 |
| doomloop | ready | readiness_lag | -0.2101 | -0.2101 | 3.69e-15 | 1.12e-15 |
| doomloop | ready | vulnerability100 | -0.1192 | -0.1192 | 1.05e-14 | 9.61e-14 |
| doomloop | ready | growth | 0.0086 | 0.0086 | 1.01e-16 | 1.35e-16 |
| doomloop | ready | inflation_cpi | -0.0066 | -0.0066 | 3.17e-16 | 1.35e-16 |
| doomloop | ready | reserves | 0.0022 | 0.0022 | 4.03e-17 | 1.07e-16 |
| doomloop | ready | tt | -0.0038 | -0.0038 | 3.56e-17 | 1.87e-16 |
| doomloop | ready | ln_currentgdp | -0.0026 | -0.0026 | 1.69e-17 | 4.14e-16 |
| doomloop | ready_debt | ready_debt_kink_low | 1.2504 | 1.2504 | 1.09e-14 | 1.91e-14 |
| doomloop | ready_debt | ready_debt_kink_high | -0.1093 | -0.1093 | 2.40e-15 | 2.62e-15 |
| doomloop | ready_debt | readiness_lag | -0.1566 | -0.1566 | 3.19e-15 | 4.16e-15 |
| doomloop | ready_debt | vulnerability100 | -0.1086 | -0.1086 | 4.68e-15 | 2.48e-13 |
| doomloop | ready_debt | growth | 0.0066 | 0.0066 | 2.11e-16 | 1.32e-16 |
| doomloop | ready_debt | inflation_cpi | 0.0046 | 0.0046 | 4.82e-16 | 1.73e-17 |
| doomloop | ready_debt | reserves | 0.001 | 0.001 | 2.51e-16 | 1.90e-15 |
| doomloop | ready_debt | tt | -0.004 | -0.004 | 1.21e-17 | 2.67e-16 |
| doomloop | ready_debt | ln_currentgdp | -0.0011 | -0.0011 | 1.98e-16 | 3.53e-15 |
| doomloop-no-state | debt | debt_kink_low | 0.1569 | 0.1569 | 1.31e-14 | 4.55e-15 |
| doomloop-no-state | debt | debt_kink_high | -0.1363 | -0.1363 | 2.80e-15 | 9.71e-17 |
| doomloop-no-state | debt | vulnerability100 | -0.5699 | -0.5699 | 1.71e-14 | 2.69e-13 |
| doomloop-no-state | debt | growth | -0.2574 | -0.2574 | 2.22e-16 | 1.39e-17 |
| doomloop-no-state | debt | inflation_cpi | 0.1415 | 0.1415 | 6.66e-16 | 8.33e-17 |
| doomloop-no-state | debt | reserves | -0.0165 | -0.0165 | 5.17e-16 | 2.67e-16 |
| doomloop-no-state | debt | tt | 0.0052 | 0.0052 | 1.19e-16 | 8.85e-17 |
| doomloop-no-state | ready | ready_kink_low | 0.7105 | 0.7105 | 1.11e-15 | 8.33e-16 |
| doomloop-no-state | ready | ready_kink_high | 0.0763 | 0.0763 | 4.00e-15 | 2.01e-15 |
| doomloop-no-state | ready | vulnerability100 | -0.156 | -0.156 | 3.07e-14 | 1.65e-13 |
| doomloop-no-state | ready | growth | 0.0229 | 0.0229 | 3.61e-16 | 8.50e-17 |
| doomloop-no-state | ready | inflation_cpi | -0.0019 | -0.0019 | 4.69e-16 | 1.73e-17 |
| doomloop-no-state | ready | reserves | 0.0012 | 0.0012 | 6.10e-16 | 1.70e-15 |
| doomloop-no-state | ready | tt | -0.0021 | -0.0021 | 5.03e-17 | 1.31e-16 |
| doomloop-no-state | ready | ln_currentgdp | 0.0003 | 0.0003 | 4.08e-16 | 1.81e-15 |

### 6.4 Cutoff 最小 RSS 复核

| 规格 | 方程 | 记录 cutoff | profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 原始 | debt | -0.0554 | 3.9507 | 3.9507 | 0 | 通过 |
| 原始 | ready | 0.1148 | 0.3835 | 0.3835 | 0 | 通过 |
| 去状态变量 | debt | -0.0554 | 3.9555 | 3.9555 | 0 | 通过 |
| 去状态变量 | ready | 0.147 | 0.4385 | 0.4385 | 0 | 通过 |

### 6.5 Readiness 双 cutoff 来源复核

| 情景 | cutoff 来源 | cutoff | readiness RSS | 最小 RSS | RSS 差 | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| readiness_minRSS | readiness_equation | 0.1148 | 0.3835 | 0.3835 | 0 | 1,571 |
| debt_equation_cutoff | debt_change_equation | -0.0554 | 0.4129 | 0.3835 | 0.0295 | 1,571 |

| 检查 | 值 | 基准 | 容差 | 状态 |
| --- | ---: | ---: | ---: | ---: |
| minRSS readiness cutoff recorded | 0.1148 | 0.1148 | 1.00e-12 | 通过 |
| borrowed readiness cutoff equals debt cutoff | -0.0554 | -0.0554 | 1.00e-12 | 通过 |
| borrowed-cutoff readiness RSS not below minimum | 0.0295 | 0 | 1.00e-10 | 通过 |

## 7. 图形 QA

新增的 readiness 债务-cutoff 单图和双 cutoff 对比图均保留 PNG 与 PDF。所有曲线使用连续 theta 网格并把相应 cutoff 精确插入；借用债务 cutoff 的图明确标注其来源，不把它表述为 readiness 的 RSS 最优点。

## 8. 必须保留的限制与建议

- 当前稳健标准误处理异方差，但不处理同一国家内序列相关；面板论文通常还应报告国家聚类标准误或适当的双向聚类/空间相关推断。
- cutoff 在同一样本上搜索，条件于 cutoff 的常规标准误偏窄风险未纳入。建议按国家重抽样，完整重复 baseline、tax/theta、cutoff 搜索和最终回归。
- theta 是生成解释变量；联合不确定性依赖跨方程协方差。当前只对两个组成边际量分别做 delta-method 标准误，不提供 theta 的联合 SE。
- 结果是固定效应相关性证据，不支持没有额外识别设计的因果措辞。
- 分支异号是经验 single-crossing 的额外形状要求，不由 kink 联合显著自动保证。当前两支同号的规格为：原始 readiness-minRSS、去滞后 A readiness；必须与联合检验分开报告。

## 9. 原始诊断输出索引

完整 CSV/DTA/日志仍保留在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/`、`doomloop/stata_outputs/`。本文件是汇总层，不替代这些逐项机器可读结果。
