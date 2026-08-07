# Paper B：统计检验与数据检查

> 生成时间：2026-08-07 16:56（Asia/Shanghai）。本文件汇总三个板块的诊断、样本审计、单位审计、稳健性检验与验证结果；正式公式和回归表见 `paperB_results.md`。

## 1. 总体评估：可在明确限制条件下使用

单位换算检查通过 29/29 项；代数/构造检查通过 44/44 项；cutoff 最小 RSS 复核通过 12/12 项。当前结果在代码一致性和样本内计算层面通过，但仍属于“Share with caveats”：生成 theta、样本内 cutoff 搜索和面板相关推断的不确定性尚未由完整流程 bootstrap 与国家聚类标准误覆盖。

## 2. 数据来源、单位与时序检查

唯一原始输入是 `data0804/invest_panel_weo.csv`。所有源百分数、比率和 0—100 指数（包括 `taxgdp`）在读入后除以 100；金额变量 `revenue`、`debt`、`CurrentGDP` 不缩放。`ln_currentgdp=ln(CurrentGDP)` 只进入 baseline，不进入税基或 Doomloop 方程。关键因变量的精确定义为：

- $T_{i,t+1}=taxgdp_{i,t+1}\times0.01$。
- $T_{it}=taxgdp_{it}\times0.01$。
- 第四节使用 $\Delta b_{i,t+1}=F.debt\_gdp_{it}-debt\_gdp_{it}$ 与 $A_{it}=readiness100_{it}$。
- 第五节使用 $\Delta b_{i,t+2}=F2.debt\_gdp_{it}-debt\_gdp_{it}$ 与 $A_{i,t+1}=F.readiness100_{it}$；所有 lead 均要求严格相邻年份。

### 2.1 基准单位换算审计

| 变量 | 源最小值 | 源最大值 | 比率最小值 | 比率最大值 | 最大换算误差 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bond_spreads | -3.4057 | 34.3087 | -0.0341 | 0.3431 | 0 | 通过 |
| bond_10y | -0.5059 | 35.2028 | -0.0051 | 0.352 | 0 | 通过 |
| vulnerability100 | 25.103 | 58.08 | 0.251 | 0.5808 | 0 | 通过 |
| readiness100 | 17.9342 | 80.7202 | 0.1793 | 0.8072 | 0 | 通过 |
| growth | -14.547 | 24.624 | -0.1455 | 0.2462 | 0 | 通过 |
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
| Baseline 共同样本 | 1,174 | 60 | 26 | 1998–2023 |
| Tax 共同样本 | 1,414 | 60 | 28 | 1995–2022 |
| 第四节 Δb(t+1) | 1,433 | 60 | 28 | 1995–2022 |
| 第四节 A(t) | 1,448 | 59 | 28 | 1996–2023 |
| 第五节 Δb(t+2) | 1,373 | 60 | 27 | 1995–2021 |
| 第五节 A(t+1) | 1,389 | 59 | 27 | 1996–2022 |

### 3.1 Baseline 输入变量（全数据非缺失分布）

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

### 3.3 第四、第五节 Doomloop 回归变量

| 规格 | 方程 | 变量 | 角色 | N | 均值 | SD | 最小值 | P50 | 最大值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 第四节-debt_with_b | debt | b_outcome | dependent_variable | 1,433 | 0.0077 | 0.0635 | -0.5417 | 0.0019 | 0.4186 |
| 第四节-debt_with_b | debt | debt_kink_low | regressor | 1,433 | 0.0102 | 0.0133 | 0 | 0.0035 | 0.0573 |
| 第四节-debt_with_b | debt | debt_kink_high | regressor | 1,433 | 0.0206 | 0.0592 | 0 | 0 | 0.5763 |
| 第四节-debt_with_b | debt | debt_gdp | regressor | 1,433 | 0.5824 | 0.3516 | 0.039 | 0.5064 | 2.6096 |
| 第四节-debt_with_b | debt | vulnerability100 | regressor | 1,433 | 0.3827 | 0.0786 | 0.251 | 0.3684 | 0.5808 |
| 第四节-debt_with_b | debt | growth | regressor | 1,433 | 0.0338 | 0.0361 | -0.1455 | 0.0344 | 0.2462 |
| 第四节-debt_with_b | debt | inflation_cpi | regressor | 1,433 | 0.0462 | 0.0542 | -0.0177 | 0.0314 | 0.723 |
| 第四节-debt_with_b | debt | reserves | regressor | 1,433 | 0.0546 | 0.1342 | 2.41e-06 | 0.0151 | 1.5271 |
| 第四节-debt_with_b | debt | tt | regressor | 1,433 | 1.0089 | 0.1826 | 0.3188 | 0.9942 | 2.7308 |
| 第四节-debt_with_b | debt | readiness100 | construction_input | 1,433 | 0.5057 | 0.1462 | 0.2021 | 0.4994 | 0.8072 |
| 第四节-debt_with_b | debt | theta_hat_A | construction_input | 1,433 | 0.0325 | 0.1084 | -0.0617 | 0.0045 | 1.1823 |
| 第四节-ready_with_lag | ready | A_outcome | dependent_variable | 1,448 | 0.5038 | 0.1443 | 0.2021 | 0.4989 | 0.7973 |
| 第四节-ready_with_lag | ready | ready_kink_low | regressor | 1,448 | 0.0009 | 0.0015 | -0.0041 | 0.0006 | 0.0101 |
| 第四节-ready_with_lag | ready | ready_kink_high | regressor | 1,448 | 0.0034 | 0.0103 | -0.0028 | 0 | 0.1405 |
| 第四节-ready_with_lag | ready | readiness_lag | regressor | 1,448 | 0.5013 | 0.1437 | 0.2021 | 0.4943 | 0.7973 |
| 第四节-ready_with_lag | ready | vulnerability100 | regressor | 1,448 | 0.3812 | 0.0791 | 0.251 | 0.3671 | 0.5808 |
| 第四节-ready_with_lag | ready | growth | regressor | 1,448 | 0.033 | 0.0353 | -0.1455 | 0.0331 | 0.2462 |
| 第四节-ready_with_lag | ready | inflation_cpi | regressor | 1,448 | 0.048 | 0.0564 | -0.0177 | 0.0329 | 0.723 |
| 第四节-ready_with_lag | ready | reserves | regressor | 1,448 | 0.0454 | 0.115 | 2.41e-06 | 0.015 | 1.5271 |
| 第四节-ready_with_lag | ready | tt | regressor | 1,448 | 1.008 | 0.1759 | 0.3188 | 0.9945 | 2.7308 |
| 第四节-ready_with_lag | ready | interest_revenue | construction_input | 1,448 | 0.0852 | 0.0977 | -0.069 | 0.0567 | 0.7987 |
| 第四节-ready_with_lag | ready | theta_hat_A | construction_input | 1,448 | 0.0316 | 0.1095 | -0.0617 | 0.0041 | 1.1823 |
| 第四节-ready_debt_cutoff | ready_debt | A_outcome | dependent_variable | 1,448 | 0.5038 | 0.1443 | 0.2021 | 0.4989 | 0.7973 |
| 第四节-ready_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 1,448 | 0.0005 | 0.0011 | -0.0032 | 0.0001 | 0.006 |
| 第四节-ready_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 1,448 | 0.0041 | 0.0111 | -0.0031 | 0 | 0.1448 |
| 第四节-ready_debt_cutoff | ready_debt | readiness_lag | regressor | 1,448 | 0.5013 | 0.1437 | 0.2021 | 0.4943 | 0.7973 |
| 第四节-ready_debt_cutoff | ready_debt | vulnerability100 | regressor | 1,448 | 0.3812 | 0.0791 | 0.251 | 0.3671 | 0.5808 |
| 第四节-ready_debt_cutoff | ready_debt | growth | regressor | 1,448 | 0.033 | 0.0353 | -0.1455 | 0.0331 | 0.2462 |
| 第四节-ready_debt_cutoff | ready_debt | inflation_cpi | regressor | 1,448 | 0.048 | 0.0564 | -0.0177 | 0.0329 | 0.723 |
| 第四节-ready_debt_cutoff | ready_debt | reserves | regressor | 1,448 | 0.0454 | 0.115 | 2.41e-06 | 0.015 | 1.5271 |
| 第四节-ready_debt_cutoff | ready_debt | tt | regressor | 1,448 | 1.008 | 0.1759 | 0.3188 | 0.9945 | 2.7308 |
| 第四节-ready_debt_cutoff | ready_debt | interest_revenue | construction_input | 1,448 | 0.0852 | 0.0977 | -0.069 | 0.0567 | 0.7987 |
| 第四节-ready_debt_cutoff | ready_debt | theta_hat_A | construction_input | 1,448 | 0.0316 | 0.1095 | -0.0617 | 0.0041 | 1.1823 |
| 第四节-debt_no_b | debt | b_outcome | dependent_variable | 1,433 | 0.0077 | 0.0635 | -0.5417 | 0.0019 | 0.4186 |
| 第四节-debt_no_b | debt | debt_kink_low | regressor | 1,433 | 0.0213 | 0.0203 | 0 | 0.017 | 0.0831 |
| 第四节-debt_no_b | debt | debt_kink_high | regressor | 1,433 | 0.0152 | 0.0549 | 0 | 0 | 0.5541 |
| 第四节-debt_no_b | debt | vulnerability100 | regressor | 1,433 | 0.3827 | 0.0786 | 0.251 | 0.3684 | 0.5808 |
| 第四节-debt_no_b | debt | growth | regressor | 1,433 | 0.0338 | 0.0361 | -0.1455 | 0.0344 | 0.2462 |
| 第四节-debt_no_b | debt | inflation_cpi | regressor | 1,433 | 0.0462 | 0.0542 | -0.0177 | 0.0314 | 0.723 |
| 第四节-debt_no_b | debt | reserves | regressor | 1,433 | 0.0546 | 0.1342 | 2.41e-06 | 0.0151 | 1.5271 |
| 第四节-debt_no_b | debt | tt | regressor | 1,433 | 1.0089 | 0.1826 | 0.3188 | 0.9942 | 2.7308 |
| 第四节-debt_no_b | debt | readiness100 | construction_input | 1,433 | 0.5057 | 0.1462 | 0.2021 | 0.4994 | 0.8072 |
| 第四节-debt_no_b | debt | theta_hat_A | construction_input | 1,433 | 0.0325 | 0.1084 | -0.0617 | 0.0045 | 1.1823 |
| 第四节-ready_no_lag | ready | A_outcome | dependent_variable | 1,458 | 0.5029 | 0.1442 | 0.2021 | 0.4965 | 0.7973 |
| 第四节-ready_no_lag | ready | ready_kink_low | regressor | 1,458 | 0.0017 | 0.0024 | -0.0054 | 0.0014 | 0.017 |
| 第四节-ready_no_lag | ready | ready_kink_high | regressor | 1,458 | 0.0026 | 0.0092 | -0.0023 | 0 | 0.1382 |
| 第四节-ready_no_lag | ready | vulnerability100 | regressor | 1,458 | 0.3817 | 0.0792 | 0.251 | 0.3673 | 0.5808 |
| 第四节-ready_no_lag | ready | growth | regressor | 1,458 | 0.0331 | 0.0355 | -0.1455 | 0.0332 | 0.2462 |
| 第四节-ready_no_lag | ready | inflation_cpi | regressor | 1,458 | 0.0482 | 0.0564 | -0.0177 | 0.0331 | 0.723 |
| 第四节-ready_no_lag | ready | reserves | regressor | 1,458 | 0.0451 | 0.1146 | 2.41e-06 | 0.0146 | 1.5271 |
| 第四节-ready_no_lag | ready | tt | regressor | 1,458 | 1.0091 | 0.1831 | 0.3188 | 0.9945 | 2.7308 |
| 第四节-ready_no_lag | ready | interest_revenue | construction_input | 1,458 | 0.0857 | 0.0979 | -0.069 | 0.0567 | 0.7987 |
| 第四节-ready_no_lag | ready | theta_hat_A | construction_input | 1,458 | 0.0315 | 0.1092 | -0.0617 | 0.0041 | 1.1823 |
| 第四节-ready_debt_cutoff_ns | ready_debt | A_outcome | dependent_variable | 1,458 | 0.5029 | 0.1442 | 0.2021 | 0.4965 | 0.7973 |
| 第四节-ready_debt_cutoff_ns | ready_debt | ready_debt_kink_low | regressor | 1,458 | 0.0018 | 0.0025 | -0.0055 | 0.0014 | 0.0175 |
| 第四节-ready_debt_cutoff_ns | ready_debt | ready_debt_kink_high | regressor | 1,458 | 0.0026 | 0.0091 | -0.0023 | 0 | 0.138 |
| 第四节-ready_debt_cutoff_ns | ready_debt | vulnerability100 | regressor | 1,458 | 0.3817 | 0.0792 | 0.251 | 0.3673 | 0.5808 |
| 第四节-ready_debt_cutoff_ns | ready_debt | growth | regressor | 1,458 | 0.0331 | 0.0355 | -0.1455 | 0.0332 | 0.2462 |
| 第四节-ready_debt_cutoff_ns | ready_debt | inflation_cpi | regressor | 1,458 | 0.0482 | 0.0564 | -0.0177 | 0.0331 | 0.723 |
| 第四节-ready_debt_cutoff_ns | ready_debt | reserves | regressor | 1,458 | 0.0451 | 0.1146 | 2.41e-06 | 0.0146 | 1.5271 |
| 第四节-ready_debt_cutoff_ns | ready_debt | tt | regressor | 1,458 | 1.0091 | 0.1831 | 0.3188 | 0.9945 | 2.7308 |
| 第四节-ready_debt_cutoff_ns | ready_debt | interest_revenue | construction_input | 1,458 | 0.0857 | 0.0979 | -0.069 | 0.0567 | 0.7987 |
| 第四节-ready_debt_cutoff_ns | ready_debt | theta_hat_A | construction_input | 1,458 | 0.0315 | 0.1092 | -0.0617 | 0.0041 | 1.1823 |
| 第五节-debt_with_b | debt | b_outcome | dependent_variable | 1,373 | 0.0163 | 0.1039 | -1.0491 | 0.0114 | 0.6076 |
| 第五节-debt_with_b | debt | debt_kink_low | regressor | 1,373 | 0.0102 | 0.0133 | 0 | 0.0037 | 0.0573 |
| 第五节-debt_with_b | debt | debt_kink_high | regressor | 1,373 | 0.0199 | 0.0576 | 0 | 0 | 0.5763 |
| 第五节-debt_with_b | debt | debt_gdp | regressor | 1,373 | 0.5768 | 0.3492 | 0.039 | 0.5038 | 2.6096 |
| 第五节-debt_with_b | debt | vulnerability100 | regressor | 1,373 | 0.3833 | 0.0788 | 0.2525 | 0.369 | 0.5808 |
| 第五节-debt_with_b | debt | growth | regressor | 1,373 | 0.0335 | 0.0364 | -0.1455 | 0.0337 | 0.2462 |
| 第五节-debt_with_b | debt | inflation_cpi | regressor | 1,373 | 0.0437 | 0.0497 | -0.0177 | 0.0291 | 0.5504 |
| 第五节-debt_with_b | debt | reserves | regressor | 1,373 | 0.0537 | 0.1321 | 2.41e-06 | 0.0147 | 1.5271 |
| 第五节-debt_with_b | debt | tt | regressor | 1,373 | 1.0082 | 0.1805 | 0.3188 | 0.996 | 2.7308 |
| 第五节-debt_with_b | debt | readiness100 | construction_input | 1,373 | 0.5048 | 0.1462 | 0.2021 | 0.4971 | 0.8072 |
| 第五节-debt_with_b | debt | theta_hat_A | construction_input | 1,373 | 0.0313 | 0.1067 | -0.0617 | 0.0042 | 1.1823 |
| 第五节-ready_with_lag | ready | A_outcome | dependent_variable | 1,389 | 0.5054 | 0.1449 | 0.2021 | 0.5004 | 0.7973 |
| 第五节-ready_with_lag | ready | ready_kink_low | regressor | 1,389 | 0.0009 | 0.0015 | -0.0041 | 0.0006 | 0.01 |
| 第五节-ready_with_lag | ready | ready_kink_high | regressor | 1,389 | 0.0033 | 0.0098 | -0.0028 | 0 | 0.1405 |
| 第五节-ready_with_lag | ready | readiness_lag | regressor | 1,389 | 0.5004 | 0.1438 | 0.2021 | 0.4932 | 0.7973 |
| 第五节-ready_with_lag | ready | vulnerability100 | regressor | 1,389 | 0.3817 | 0.0793 | 0.251 | 0.3673 | 0.5808 |
| 第五节-ready_with_lag | ready | growth | regressor | 1,389 | 0.0334 | 0.0357 | -0.1455 | 0.0335 | 0.2462 |
| 第五节-ready_with_lag | ready | inflation_cpi | regressor | 1,389 | 0.0465 | 0.0545 | -0.0177 | 0.0316 | 0.723 |
| 第五节-ready_with_lag | ready | reserves | regressor | 1,389 | 0.0448 | 0.1135 | 2.41e-06 | 0.0146 | 1.5271 |
| 第五节-ready_with_lag | ready | tt | regressor | 1,389 | 1.0075 | 0.1766 | 0.3188 | 0.9947 | 2.7308 |
| 第五节-ready_with_lag | ready | interest_revenue | construction_input | 1,389 | 0.0845 | 0.095 | -0.069 | 0.0567 | 0.7777 |
| 第五节-ready_with_lag | ready | theta_hat_A | construction_input | 1,389 | 0.0307 | 0.1086 | -0.0617 | 0.0039 | 1.1823 |
| 第五节-ready_debt_cutoff | ready_debt | A_outcome | dependent_variable | 1,389 | 0.5054 | 0.1449 | 0.2021 | 0.5004 | 0.7973 |
| 第五节-ready_debt_cutoff | ready_debt | ready_debt_kink_low | regressor | 1,389 | 0.0005 | 0.0011 | -0.0032 | 0.0001 | 0.006 |
| 第五节-ready_debt_cutoff | ready_debt | ready_debt_kink_high | regressor | 1,389 | 0.0039 | 0.0105 | -0.0031 | 0 | 0.1448 |
| 第五节-ready_debt_cutoff | ready_debt | readiness_lag | regressor | 1,389 | 0.5004 | 0.1438 | 0.2021 | 0.4932 | 0.7973 |
| 第五节-ready_debt_cutoff | ready_debt | vulnerability100 | regressor | 1,389 | 0.3817 | 0.0793 | 0.251 | 0.3673 | 0.5808 |
| 第五节-ready_debt_cutoff | ready_debt | growth | regressor | 1,389 | 0.0334 | 0.0357 | -0.1455 | 0.0335 | 0.2462 |
| 第五节-ready_debt_cutoff | ready_debt | inflation_cpi | regressor | 1,389 | 0.0465 | 0.0545 | -0.0177 | 0.0316 | 0.723 |
| 第五节-ready_debt_cutoff | ready_debt | reserves | regressor | 1,389 | 0.0448 | 0.1135 | 2.41e-06 | 0.0146 | 1.5271 |
| 第五节-ready_debt_cutoff | ready_debt | tt | regressor | 1,389 | 1.0075 | 0.1766 | 0.3188 | 0.9947 | 2.7308 |
| 第五节-ready_debt_cutoff | ready_debt | interest_revenue | construction_input | 1,389 | 0.0845 | 0.095 | -0.069 | 0.0567 | 0.7777 |
| 第五节-ready_debt_cutoff | ready_debt | theta_hat_A | construction_input | 1,389 | 0.0307 | 0.1086 | -0.0617 | 0.0039 | 1.1823 |
| 第五节-debt_no_b | debt | b_outcome | dependent_variable | 1,373 | 0.0163 | 0.1039 | -1.0491 | 0.0114 | 0.6076 |
| 第五节-debt_no_b | debt | debt_kink_low | regressor | 1,373 | 0.0332 | 0.0258 | 0 | 0.0295 | 0.1064 |
| 第五节-debt_no_b | debt | debt_kink_high | regressor | 1,373 | 0.0117 | 0.0496 | 0 | 0 | 0.5341 |
| 第五节-debt_no_b | debt | vulnerability100 | regressor | 1,373 | 0.3833 | 0.0788 | 0.2525 | 0.369 | 0.5808 |
| 第五节-debt_no_b | debt | growth | regressor | 1,373 | 0.0335 | 0.0364 | -0.1455 | 0.0337 | 0.2462 |
| 第五节-debt_no_b | debt | inflation_cpi | regressor | 1,373 | 0.0437 | 0.0497 | -0.0177 | 0.0291 | 0.5504 |
| 第五节-debt_no_b | debt | reserves | regressor | 1,373 | 0.0537 | 0.1321 | 2.41e-06 | 0.0147 | 1.5271 |
| 第五节-debt_no_b | debt | tt | regressor | 1,373 | 1.0082 | 0.1805 | 0.3188 | 0.996 | 2.7308 |
| 第五节-debt_no_b | debt | readiness100 | construction_input | 1,373 | 0.5048 | 0.1462 | 0.2021 | 0.4971 | 0.8072 |
| 第五节-debt_no_b | debt | theta_hat_A | construction_input | 1,373 | 0.0313 | 0.1067 | -0.0617 | 0.0042 | 1.1823 |
| 第五节-ready_no_lag | ready | A_outcome | dependent_variable | 1,399 | 0.5046 | 0.1448 | 0.2021 | 0.4994 | 0.7973 |
| 第五节-ready_no_lag | ready | ready_kink_low | regressor | 1,399 | 0.0014 | 0.002 | -0.0049 | 0.0011 | 0.0144 |
| 第五节-ready_no_lag | ready | ready_kink_high | regressor | 1,399 | 0.0028 | 0.0091 | -0.0025 | 0 | 0.1391 |
| 第五节-ready_no_lag | ready | vulnerability100 | regressor | 1,399 | 0.3822 | 0.0794 | 0.251 | 0.3676 | 0.5808 |
| 第五节-ready_no_lag | ready | growth | regressor | 1,399 | 0.0336 | 0.0359 | -0.1455 | 0.0337 | 0.2462 |
| 第五节-ready_no_lag | ready | inflation_cpi | regressor | 1,399 | 0.0468 | 0.0546 | -0.0177 | 0.0317 | 0.723 |
| 第五节-ready_no_lag | ready | reserves | regressor | 1,399 | 0.0445 | 0.1131 | 2.41e-06 | 0.0143 | 1.5271 |
| 第五节-ready_no_lag | ready | tt | regressor | 1,399 | 1.0087 | 0.1841 | 0.3188 | 0.9947 | 2.7308 |
| 第五节-ready_no_lag | ready | interest_revenue | construction_input | 1,399 | 0.0849 | 0.0952 | -0.069 | 0.057 | 0.7777 |
| 第五节-ready_no_lag | ready | theta_hat_A | construction_input | 1,399 | 0.0306 | 0.1083 | -0.0617 | 0.0039 | 1.1823 |
| 第五节-ready_debt_cutoff_ns | ready_debt | A_outcome | dependent_variable | 1,399 | 0.5046 | 0.1448 | 0.2021 | 0.4994 | 0.7973 |
| 第五节-ready_debt_cutoff_ns | ready_debt | ready_debt_kink_low | regressor | 1,399 | 0.0035 | 0.004 | -0.0075 | 0.0029 | 0.0282 |
| 第五节-ready_debt_cutoff_ns | ready_debt | ready_debt_kink_high | regressor | 1,399 | 0.0017 | 0.0074 | -0.0015 | 0 | 0.1344 |
| 第五节-ready_debt_cutoff_ns | ready_debt | vulnerability100 | regressor | 1,399 | 0.3822 | 0.0794 | 0.251 | 0.3676 | 0.5808 |
| 第五节-ready_debt_cutoff_ns | ready_debt | growth | regressor | 1,399 | 0.0336 | 0.0359 | -0.1455 | 0.0337 | 0.2462 |
| 第五节-ready_debt_cutoff_ns | ready_debt | inflation_cpi | regressor | 1,399 | 0.0468 | 0.0546 | -0.0177 | 0.0317 | 0.723 |
| 第五节-ready_debt_cutoff_ns | ready_debt | reserves | regressor | 1,399 | 0.0445 | 0.1131 | 2.41e-06 | 0.0143 | 1.5271 |
| 第五节-ready_debt_cutoff_ns | ready_debt | tt | regressor | 1,399 | 1.0087 | 0.1841 | 0.3188 | 0.9947 | 2.7308 |
| 第五节-ready_debt_cutoff_ns | ready_debt | interest_revenue | construction_input | 1,399 | 0.0849 | 0.0952 | -0.069 | 0.057 | 0.7777 |
| 第五节-ready_debt_cutoff_ns | ready_debt | theta_hat_A | construction_input | 1,399 | 0.0306 | 0.1083 | -0.0617 | 0.0039 | 1.1823 |

## 4. 缺失值、重复键与固定效应可识别性

国家—年份重复键检查在三段流程中均为零；代码遇到重复键会直接终止，不会静默删除。各段共同样本在估计前锁定，逐步模型与 cutoff 候选使用相同观测。

### 4.1 独占样本损失

| 板块 | 方程 | 变量 | 缺失数 | 缺失率 | 独占损失 |
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
| doomloop-h1 | debt | b_outcome | 166 | 9.09 | 60 |
| doomloop-h1 | debt | readiness100 | 58 | 3.17 | 0 |
| doomloop-h1 | debt | theta_hat_A | 150 | 8.21 | 0 |
| doomloop-h1 | debt | debt_gdp | 103 | 5.64 | 0 |
| doomloop-h1 | debt | vulnerability100 | 58 | 3.17 | 0 |
| doomloop-h1 | debt | growth | 5 | 0.27 | 0 |
| doomloop-h1 | debt | inflation_cpi | 7 | 0.38 | 2 |
| doomloop-h1 | debt | reserves | 70 | 3.83 | 26 |
| doomloop-h1 | debt | tt | 222 | 12.15 | 148 |
| doomloop-h1 | ready | A_outcome | 58 | 3.17 | 0 |
| doomloop-h1 | ready | interest_revenue | 141 | 7.72 | 34 |
| doomloop-h1 | ready | theta_hat_A | 150 | 8.21 | 9 |
| doomloop-h1 | ready | readiness_lag | 119 | 6.51 | 10 |
| doomloop-h1 | ready | vulnerability100 | 58 | 3.17 | 0 |
| doomloop-h1 | ready | growth | 5 | 0.27 | 0 |
| doomloop-h1 | ready | inflation_cpi | 7 | 0.38 | 1 |
| doomloop-h1 | ready | reserves | 70 | 3.83 | 27 |
| doomloop-h1 | ready | tt | 222 | 12.15 | 120 |
| doomloop-h2 | debt | b_outcome | 229 | 12.53 | 120 |
| doomloop-h2 | debt | readiness100 | 58 | 3.17 | 0 |
| doomloop-h2 | debt | theta_hat_A | 150 | 8.21 | 0 |
| doomloop-h2 | debt | debt_gdp | 103 | 5.64 | 0 |
| doomloop-h2 | debt | vulnerability100 | 58 | 3.17 | 0 |
| doomloop-h2 | debt | growth | 5 | 0.27 | 0 |
| doomloop-h2 | debt | inflation_cpi | 7 | 0.38 | 2 |
| doomloop-h2 | debt | reserves | 70 | 3.83 | 25 |
| doomloop-h2 | debt | tt | 222 | 12.15 | 148 |
| doomloop-h2 | ready | A_outcome | 119 | 6.51 | 59 |
| doomloop-h2 | ready | interest_revenue | 141 | 7.72 | 33 |
| doomloop-h2 | ready | theta_hat_A | 150 | 8.21 | 9 |
| doomloop-h2 | ready | readiness_lag | 119 | 6.51 | 10 |
| doomloop-h2 | ready | vulnerability100 | 58 | 3.17 | 0 |
| doomloop-h2 | ready | growth | 5 | 0.27 | 0 |
| doomloop-h2 | ready | inflation_cpi | 7 | 0.38 | 1 |
| doomloop-h2 | ready | reserves | 70 | 3.83 | 26 |
| doomloop-h2 | ready | tt | 222 | 12.15 | 120 |

### 4.2 Within 变异

| 板块 | 方程 | 变量 | 总体 SD | Within SD | Within/总体 | FE 识别 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
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
| doomloop-h1 | debt | b_outcome | 0.0635 | 0.062 | 0.9756 | adequate |
| doomloop-h1 | debt | theta_hat_A | 0.1084 | 0.0595 | 0.549 | adequate |
| doomloop-h1 | debt | readiness100 | 0.1462 | 0.0403 | 0.2756 | adequate |
| doomloop-h1 | debt | debt_gdp | 0.3516 | 0.1708 | 0.4857 | adequate |
| doomloop-h1 | debt | vulnerability100 | 0.0786 | 0.0099 | 0.1253 | adequate |
| doomloop-h1 | debt | growth | 0.0361 | 0.0319 | 0.8821 | adequate |
| doomloop-h1 | debt | inflation_cpi | 0.0542 | 0.0416 | 0.7676 | adequate |
| doomloop-h1 | debt | reserves | 0.1342 | 0.0617 | 0.46 | adequate |
| doomloop-h1 | debt | tt | 0.1826 | 0.1609 | 0.8807 | adequate |
| doomloop-h1 | ready | A_outcome | 0.1443 | 0.0387 | 0.2684 | adequate |
| doomloop-h1 | ready | theta_hat_A | 0.1095 | 0.0591 | 0.5397 | adequate |
| doomloop-h1 | ready | interest_revenue | 0.0977 | 0.0452 | 0.4629 | adequate |
| doomloop-h1 | ready | readiness_lag | 0.1437 | 0.0397 | 0.276 | adequate |
| doomloop-h1 | ready | vulnerability100 | 0.0791 | 0.0101 | 0.1275 | adequate |
| doomloop-h1 | ready | growth | 0.0353 | 0.0311 | 0.8813 | adequate |
| doomloop-h1 | ready | inflation_cpi | 0.0564 | 0.0433 | 0.7675 | adequate |
| doomloop-h1 | ready | reserves | 0.115 | 0.0601 | 0.523 | adequate |
| doomloop-h1 | ready | tt | 0.1759 | 0.1567 | 0.891 | adequate |
| doomloop-h2 | debt | b_outcome | 0.1039 | 0.1 | 0.9626 | adequate |
| doomloop-h2 | debt | theta_hat_A | 0.1067 | 0.0592 | 0.5549 | adequate |
| doomloop-h2 | debt | readiness100 | 0.1462 | 0.0404 | 0.2762 | adequate |
| doomloop-h2 | debt | debt_gdp | 0.3492 | 0.1692 | 0.4847 | adequate |
| doomloop-h2 | debt | vulnerability100 | 0.0788 | 0.0095 | 0.1207 | adequate |
| doomloop-h2 | debt | growth | 0.0364 | 0.0319 | 0.8761 | adequate |
| doomloop-h2 | debt | inflation_cpi | 0.0497 | 0.0367 | 0.7374 | adequate |
| doomloop-h2 | debt | reserves | 0.1321 | 0.0616 | 0.4663 | adequate |
| doomloop-h2 | debt | tt | 0.1805 | 0.1574 | 0.8722 | adequate |
| doomloop-h2 | ready | A_outcome | 0.1449 | 0.0379 | 0.2614 | adequate |
| doomloop-h2 | ready | theta_hat_A | 0.1086 | 0.0595 | 0.5474 | adequate |
| doomloop-h2 | ready | interest_revenue | 0.095 | 0.0431 | 0.4544 | adequate |
| doomloop-h2 | ready | readiness_lag | 0.1438 | 0.0398 | 0.2766 | adequate |
| doomloop-h2 | ready | vulnerability100 | 0.0793 | 0.0098 | 0.1237 | adequate |
| doomloop-h2 | ready | growth | 0.0357 | 0.0315 | 0.881 | adequate |
| doomloop-h2 | ready | inflation_cpi | 0.0545 | 0.0418 | 0.7664 | adequate |
| doomloop-h2 | ready | reserves | 0.1135 | 0.0603 | 0.5313 | adequate |
| doomloop-h2 | ready | tt | 0.1766 | 0.157 | 0.8892 | adequate |

## 5. 共线性、相关性与系数变化

### 5.1 VIF/条件数

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

### 5.2 高绝对相关系数（排除对角线与镜像重复）

| 板块 | 变量 1 | 变量 2 | 相关系数 |
| --- | ---: | ---: | ---: |
| baseline | vulnerability100 | readiness100 | -0.7606 |
| tax | readiness100 | vulnerability100 | -0.777 |
| tax | readiness100 | taxbase_lag | 0.63 |
| tax | vulnerability100 | taxbase_lag | -0.655 |

### 5.3 加入控制变量后的系数变化

| 板块 | 模型 | 变量 | 基准系数 | 新系数 | 绝对变化 | %变化 | 报告规则 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | C_macro | vulnerability100 | -0.0423 | 0.1597 | 0.202 | 477.5 | percent |
| baseline | C_macro | readiness100 | -0.0673 | -0.053 | 0.0143 | 21.2 | percent |
| baseline | C_macro | debt_gdp | 0.0461 | 0.0497 | 0.0035 | 7.7 | percent |
| baseline | Layer1_X | vulnerability100 | -0.0423 | 0.2203 | 0.2626 | 620.6 | percent |
| baseline | Layer1_X | debt_gdp | 0.0461 | 0.0511 | 0.0049 | 10.7 | percent |
| baseline | Layer2_A | vulnerability100 | -0.0423 | 0.2263 | 0.2686 | 634.7 | percent |
| baseline | Layer2_A | readiness100 | -0.0673 | -0.0539 | 0.0133 | 19.8 | percent |
| baseline | Layer2_A | debt_gdp | 0.0461 | 0.0515 | 0.0054 | 11.7 | percent |
| tax | T5_macro | vulnerability100 | 0.0548 | 0.0517 | -0.003 | -5.5 | percent |
| tax | T5_macro | readiness100 | -0.0202 | -0.0203 | -0.0001 | -0.5 | percent |
| tax | T5_macro | taxbase_lag | 0.7389 | 0.737 | -0.0019 | -0.3 | percent |
| tax | T7_layer2_A | vulnerability100 | 0.0548 | 0.0484 | -0.0064 | -11.6 | percent |
| tax | T7_layer2_A | readiness100 | -0.0202 | -0.0215 | -0.0013 | -6.5 | percent |
| tax | T7_layer2_A | taxbase_lag | 0.7389 | 0.7371 | -0.0019 | -0.3 | percent |
| tax | T9_interact_macro | c_A_T | -0.0276 | -0.0277 | -0.0001 | -0.2 | percent |
| tax | T9_interact_macro | c_X_T | 0.0945 | 0.0913 | -0.0032 | -3.4 | percent |
| tax | T9_interact_macro | int_AX_T | 0.2536 | 0.2518 | -0.0018 | -0.7 | percent |
| tax | T9_interact_macro | taxbase_lag | 0.7296 | 0.7278 | -0.0018 | -0.2 | percent |
| tax | T10_interact_full | c_A_T | -0.0276 | -0.0289 | -0.0013 | -4.6 | percent |
| tax | T10_interact_full | c_X_T | 0.0945 | 0.0887 | -0.0058 | -6.1 | percent |
| tax | T10_interact_full | int_AX_T | 0.2536 | 0.2483 | -0.0053 | -2.1 | percent |
| tax | T10_interact_full | taxbase_lag | 0.7296 | 0.7278 | -0.0018 | -0.2 | percent |

## 6. 统计检验

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
| doomloop-h1 | D3_full | low- and high-branch coefficients jointly zero | 6.5066 | 2 | 1,338 | 0.002 |
| doomloop-h1 | D3_full | macro controls jointly zero | 26.3909 | 2 | 1,338 | <0.001 |
| doomloop-h1 | D3_full | external controls jointly zero | 0.9441 | 2 | 1,338 | 0.389 |
| doomloop-h1 | D3_full | all controls jointly zero | 13.7237 | 4 | 1,338 | <0.001 |
| doomloop-h1 | R3_full | low- and high-branch coefficients jointly zero | 4.3181 | 2 | 1,354 | 0.014 |
| doomloop-h1 | R3_full | macro controls jointly zero | 2.0074 | 2 | 1,354 | 0.135 |
| doomloop-h1 | R3_full | external controls jointly zero | 2.3565 | 2 | 1,354 | 0.095 |
| doomloop-h1 | R3_full | all controls jointly zero | 2.2843 | 4 | 1,354 | 0.058 |
| doomloop-h1 | RD3_full | branches jointly zero; debt-equation cutoff | 4.4821 | 2 | 1,354 | 0.011 |
| doomloop-h1 | RD3_full | macro controls jointly zero | 2.0339 | 2 | 1,354 | 0.131 |
| doomloop-h1 | RD3_full | external controls jointly zero | 2.2197 | 2 | 1,354 | 0.109 |
| doomloop-h1 | RD3_full | all controls jointly zero | 2.2674 | 4 | 1,354 | 0.060 |
| doomloop-h1-no-state | DN3_full | low- and high-branch coefficients jointly zero | 18.5938 | 2 | 1,339 | <0.001 |
| doomloop-h1-no-state | DN3_full | macro controls jointly zero | 19.0266 | 2 | 1,339 | <0.001 |
| doomloop-h1-no-state | DN3_full | external controls jointly zero | 1.7787 | 2 | 1,339 | 0.169 |
| doomloop-h1-no-state | DN3_full | all controls jointly zero | 10.7751 | 4 | 1,339 | <0.001 |
| doomloop-h1-no-state | RN3_full | low- and high-branch coefficients jointly zero | 32.9905 | 2 | 1,364 | <0.001 |
| doomloop-h1-no-state | RN3_full | macro controls jointly zero | 0.3808 | 2 | 1,364 | 0.683 |
| doomloop-h1-no-state | RN3_full | external controls jointly zero | 5.6734 | 2 | 1,364 | 0.004 |
| doomloop-h1-no-state | RN3_full | all controls jointly zero | 3.0169 | 4 | 1,364 | 0.017 |
| doomloop-h1-no-state | RDN3_full | branches jointly zero; debt-equation cutoff | 32.8502 | 2 | 1,364 | <0.001 |
| doomloop-h1-no-state | RDN3_full | macro controls jointly zero | 0.3692 | 2 | 1,364 | 0.691 |
| doomloop-h1-no-state | RDN3_full | external controls jointly zero | 5.6052 | 2 | 1,364 | 0.004 |
| doomloop-h1-no-state | RDN3_full | all controls jointly zero | 2.9773 | 4 | 1,364 | 0.018 |
| doomloop-h2 | D3_full | low- and high-branch coefficients jointly zero | 5.6587 | 2 | 1,279 | 0.004 |
| doomloop-h2 | D3_full | macro controls jointly zero | 30.8594 | 2 | 1,279 | <0.001 |
| doomloop-h2 | D3_full | external controls jointly zero | 1.1333 | 2 | 1,279 | 0.322 |
| doomloop-h2 | D3_full | all controls jointly zero | 15.4953 | 4 | 1,279 | <0.001 |
| doomloop-h2 | R3_full | low- and high-branch coefficients jointly zero | 8.5801 | 2 | 1,296 | <0.001 |
| doomloop-h2 | R3_full | macro controls jointly zero | 1.4093 | 2 | 1,296 | 0.245 |
| doomloop-h2 | R3_full | external controls jointly zero | 2.4202 | 2 | 1,296 | 0.089 |
| doomloop-h2 | R3_full | all controls jointly zero | 2.0046 | 4 | 1,296 | 0.092 |
| doomloop-h2 | RD3_full | branches jointly zero; debt-equation cutoff | 7.3656 | 2 | 1,296 | <0.001 |
| doomloop-h2 | RD3_full | macro controls jointly zero | 1.537 | 2 | 1,296 | 0.215 |
| doomloop-h2 | RD3_full | external controls jointly zero | 2.1874 | 2 | 1,296 | 0.113 |
| doomloop-h2 | RD3_full | all controls jointly zero | 1.9784 | 4 | 1,296 | 0.095 |
| doomloop-h2-no-state | DN3_full | low- and high-branch coefficients jointly zero | 39.9188 | 2 | 1,280 | <0.001 |
| doomloop-h2-no-state | DN3_full | macro controls jointly zero | 22.1088 | 2 | 1,280 | <0.001 |
| doomloop-h2-no-state | DN3_full | external controls jointly zero | 2.8767 | 2 | 1,280 | 0.057 |
| doomloop-h2-no-state | DN3_full | all controls jointly zero | 12.2053 | 4 | 1,280 | <0.001 |
| doomloop-h2-no-state | RN3_full | low- and high-branch coefficients jointly zero | 32.3865 | 2 | 1,306 | <0.001 |
| doomloop-h2-no-state | RN3_full | macro controls jointly zero | 0.6375 | 2 | 1,306 | 0.529 |
| doomloop-h2-no-state | RN3_full | external controls jointly zero | 5.1585 | 2 | 1,306 | 0.006 |
| doomloop-h2-no-state | RN3_full | all controls jointly zero | 2.9313 | 4 | 1,306 | 0.020 |
| doomloop-h2-no-state | RDN3_full | branches jointly zero; debt-equation cutoff | 27.9061 | 2 | 1,306 | <0.001 |
| doomloop-h2-no-state | RDN3_full | macro controls jointly zero | 0.1486 | 2 | 1,306 | 0.862 |
| doomloop-h2-no-state | RDN3_full | external controls jointly zero | 4.4086 | 2 | 1,306 | 0.012 |
| doomloop-h2-no-state | RDN3_full | all controls jointly zero | 2.2978 | 4 | 1,306 | 0.057 |

### 6.2 代数、映射与时序公式检查

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
| doomloop-h1 | theta uses debt_gdp*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | b_it maps exactly to debt_gdp | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | Delta b exact lead-minus-base formula | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | A outcome exact timing formula | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | debt low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | debt high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | readiness low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | readiness high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | readiness debt-cutoff low hinge | 0 | 1.00e-10 | 通过 |
| doomloop-h1 | readiness debt-cutoff high hinge | 0 | 1.00e-10 | 通过 |
| doomloop-h1-no-state | theta uses debt_gdp*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop-h1-no-state | b_it maps exactly to debt_gdp | 0 | 1.00e-10 | 通过 |
| doomloop-h1-no-state | no-b debt low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h1-no-state | no-b debt high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h1-no-state | no-lag readiness low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h1-no-state | no-lag readiness high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h1-no-state | no-lag readiness debt-cutoff low | 0 | 1.00e-10 | 通过 |
| doomloop-h1-no-state | no-lag readiness debt-cutoff high | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | theta uses debt_gdp*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | b_it maps exactly to debt_gdp | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | Delta b exact lead-minus-base formula | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | A outcome exact timing formula | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | debt low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | debt high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | readiness low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | readiness high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | readiness debt-cutoff low hinge | 0 | 1.00e-10 | 通过 |
| doomloop-h2 | readiness debt-cutoff high hinge | 0 | 1.00e-10 | 通过 |
| doomloop-h2-no-state | theta uses debt_gdp*mA_hat + TA_hat | 0 | 1.00e-10 | 通过 |
| doomloop-h2-no-state | b_it maps exactly to debt_gdp | 0 | 1.00e-10 | 通过 |
| doomloop-h2-no-state | no-b debt low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h2-no-state | no-b debt high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h2-no-state | no-lag readiness low hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h2-no-state | no-lag readiness high hinge regressor | 0 | 1.00e-10 | 通过 |
| doomloop-h2-no-state | no-lag readiness debt-cutoff low | 0 | 1.00e-10 | 通过 |
| doomloop-h2-no-state | no-lag readiness debt-cutoff high | 0 | 1.00e-10 | 通过 |

### 6.3 areg 与显式 LSDV 复核

| 板块 | 模型/方程 | 变量 | areg | LSDV | \|系数差\| | \|SE差\| |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | Interact_all | tt | -0.0031 | -0.0031 | 1.86e-15 | 5.72e-17 |
| baseline | Interact_all | reserves | 0.027 | 0.027 | 5.87e-15 | 3.37e-16 |
| baseline | Interact_all | inflation_cpi | 0.1567 | 0.1567 | 1.14e-14 | 7.15e-16 |
| baseline | Interact_all | ln_currentgdp | 0.0175 | 0.0175 | 5.19e-15 | 3.40e-16 |
| baseline | Interact_all | growth | -0.1649 | -0.1649 | 3.58e-15 | 2.78e-17 |
| baseline | Interact_all | int_AX | -0.0261 | -0.0261 | 2.31e-14 | 4.11e-15 |
| baseline | Interact_all | int_AB | -0.1898 | -0.1898 | 1.04e-14 | 3.47e-18 |
| baseline | Interact_all | c_b | 0.0556 | 0.0556 | 2.49e-15 | 1.65e-17 |
| baseline | Interact_all | c_X | 0.2486 | 0.2486 | 1.29e-13 | 1.56e-14 |
| baseline | Interact_all | c_A | -0.072 | -0.072 | 2.35e-15 | 3.85e-16 |
| baseline | Layer2_A | tt | 0.0005 | 0.0005 | 2.33e-15 | 3.90e-17 |
| baseline | Layer2_A | reserves | 0.0241 | 0.0241 | 6.28e-15 | 1.27e-14 |
| baseline | Layer2_A | inflation_cpi | 0.149 | 0.149 | 1.14e-14 | 4.34e-15 |
| baseline | Layer2_A | ln_currentgdp | 0.0217 | 0.0217 | 5.47e-15 | 1.04e-14 |
| baseline | Layer2_A | growth | -0.1814 | -0.1814 | 5.33e-15 | 4.86e-17 |
| baseline | Layer2_A | debt_gdp | 0.0515 | 0.0515 | 3.09e-15 | 1.03e-15 |
| baseline | Layer2_A | readiness100 | -0.0539 | -0.0539 | 1.38e-15 | 5.07e-15 |
| baseline | Layer2_A | vulnerability100 | 0.2263 | 0.2263 | 1.21e-13 | 3.90e-13 |
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
| doomloop-h1 | debt | debt_kink_low | -1.5669 | -1.5669 | 1.94e-13 | 3.40e-14 |
| doomloop-h1 | debt | debt_kink_high | 0.117 | 0.117 | 2.86e-14 | 1.71e-14 |
| doomloop-h1 | debt | debt_gdp | -0.1704 | -0.1704 | 7.49e-15 | 3.84e-15 |
| doomloop-h1 | debt | vulnerability100 | -0.0985 | -0.0985 | 7.63e-15 | 3.93e-13 |
| doomloop-h1 | debt | growth | -0.5425 | -0.5425 | 4.11e-15 | 1.67e-16 |
| doomloop-h1 | debt | inflation_cpi | -0.1225 | -0.1225 | 2.50e-16 | 1.94e-16 |
| doomloop-h1 | debt | reserves | -0.0071 | -0.0071 | 1.02e-15 | 3.12e-17 |
| doomloop-h1 | debt | tt | 0.0128 | 0.0128 | 1.14e-16 | 1.09e-16 |
| doomloop-h1 | ready | ready_kink_low | -1.1354 | -1.1354 | 4.80e-13 | 2.80e-13 |
| doomloop-h1 | ready | ready_kink_high | 0.0519 | 0.0519 | 1.65e-14 | 1.78e-15 |
| doomloop-h1 | ready | readiness_lag | 0.8519 | 0.8519 | 1.31e-14 | 1.20e-15 |
| doomloop-h1 | ready | vulnerability100 | -0.0927 | -0.0927 | 1.58e-13 | 6.09e-13 |
| doomloop-h1 | ready | growth | 0.0275 | 0.0275 | 1.37e-15 | 6.70e-16 |
| doomloop-h1 | ready | inflation_cpi | -0.0049 | -0.0049 | 1.13e-15 | 3.16e-16 |
| doomloop-h1 | ready | reserves | -0.0063 | -0.0063 | 2.61e-16 | 1.22e-15 |
| doomloop-h1 | ready | tt | -0.0035 | -0.0035 | 1.25e-15 | 1.50e-16 |
| doomloop-h1 | ready_debt | ready_debt_kink_low | -1.4003 | -1.4003 | 3.42e-13 | 1.19e-13 |
| doomloop-h1 | ready_debt | ready_debt_kink_high | 0.0561 | 0.0561 | 2.82e-15 | 1.37e-15 |
| doomloop-h1 | ready_debt | readiness_lag | 0.8548 | 0.8548 | 1.20e-14 | 2.02e-15 |
| doomloop-h1 | ready_debt | vulnerability100 | -0.0891 | -0.0891 | 1.36e-13 | 1.12e-13 |
| doomloop-h1 | ready_debt | growth | 0.0272 | 0.0272 | 1.06e-15 | 1.11e-16 |
| doomloop-h1 | ready_debt | inflation_cpi | -0.0064 | -0.0064 | 4.85e-16 | 2.32e-16 |
| doomloop-h1 | ready_debt | reserves | -0.0061 | -0.0061 | 1.10e-16 | 6.12e-16 |
| doomloop-h1 | ready_debt | tt | -0.0035 | -0.0035 | 1.03e-15 | 1.57e-16 |
| doomloop-h1-no-state | debt | debt_kink_low | 0.8282 | 0.8282 | 2.44e-14 | 1.35e-14 |
| doomloop-h1-no-state | debt | debt_kink_high | -0.4726 | -0.4726 | 1.11e-15 | 1.19e-15 |
| doomloop-h1-no-state | debt | vulnerability100 | 0.2425 | 0.2425 | 3.11e-14 | 5.30e-13 |
| doomloop-h1-no-state | debt | growth | -0.4385 | -0.4385 | 1.05e-15 | 4.16e-16 |
| doomloop-h1-no-state | debt | inflation_cpi | -0.1376 | -0.1376 | 1.94e-16 | 8.33e-17 |
| doomloop-h1-no-state | debt | reserves | -0.0077 | -0.0077 | 5.98e-17 | 1.39e-17 |
| doomloop-h1-no-state | debt | tt | 0.0183 | 0.0183 | 3.43e-16 | 6.66e-16 |
| doomloop-h1-no-state | ready | ready_kink_low | -5.7822 | -5.7822 | 1.13e-13 | 4.79e-14 |
| doomloop-h1-no-state | ready | ready_kink_high | 0.0787 | 0.0787 | 2.76e-15 | 3.39e-15 |
| doomloop-h1-no-state | ready | vulnerability100 | 0.1655 | 0.1655 | 1.75e-13 | 8.47e-14 |
| doomloop-h1-no-state | ready | growth | 0.024 | 0.024 | 2.22e-16 | 1.39e-17 |
| doomloop-h1-no-state | ready | inflation_cpi | -0.0132 | -0.0132 | 2.97e-16 | 3.02e-16 |
| doomloop-h1-no-state | ready | reserves | -0.0117 | -0.0117 | 2.57e-15 | 8.76e-17 |
| doomloop-h1-no-state | ready | tt | -0.0178 | -0.0178 | 1.01e-15 | 6.29e-16 |
| doomloop-h1-no-state | ready_debt | ready_debt_kink_low | -5.6355 | -5.6355 | 2.09e-13 | 1.83e-14 |
| doomloop-h1-no-state | ready_debt | ready_debt_kink_high | 0.0806 | 0.0806 | 3.57e-15 | 1.60e-15 |
| doomloop-h1-no-state | ready_debt | vulnerability100 | 0.1707 | 0.1707 | 2.06e-13 | 1.82e-13 |
| doomloop-h1-no-state | ready_debt | growth | 0.0238 | 0.0238 | 1.06e-15 | 1.39e-17 |
| doomloop-h1-no-state | ready_debt | inflation_cpi | -0.0128 | -0.0128 | 7.77e-16 | 3.12e-17 |
| doomloop-h1-no-state | ready_debt | reserves | -0.0117 | -0.0117 | 2.96e-15 | 1.47e-16 |
| doomloop-h1-no-state | ready_debt | tt | -0.0176 | -0.0176 | 1.20e-15 | 6.85e-16 |
| doomloop-h2 | debt | debt_kink_low | -2.5481 | -2.5481 | 5.32e-13 | 2.82e-14 |
| doomloop-h2 | debt | debt_kink_high | 0.2694 | 0.2694 | 7.41e-14 | 1.22e-15 |
| doomloop-h2 | debt | debt_gdp | -0.3583 | -0.3583 | 1.94e-14 | 5.79e-15 |
| doomloop-h2 | debt | vulnerability100 | -0.1957 | -0.1957 | 2.58e-14 | 6.27e-13 |
| doomloop-h2 | debt | growth | -0.8846 | -0.8846 | 1.60e-14 | 6.80e-16 |
| doomloop-h2 | debt | inflation_cpi | -0.1369 | -0.1369 | 1.42e-15 | 2.08e-16 |
| doomloop-h2 | debt | reserves | -0.0048 | -0.0048 | 3.07e-15 | 3.37e-16 |
| doomloop-h2 | debt | tt | 0.0206 | 0.0206 | 7.98e-17 | 1.00e-15 |
| doomloop-h2 | ready | ready_kink_low | -2.3633 | -2.3633 | 5.23e-13 | 5.62e-14 |
| doomloop-h2 | ready | ready_kink_high | 0.1033 | 0.1033 | 2.47e-15 | 4.86e-16 |
| doomloop-h2 | ready | readiness_lag | 0.6761 | 0.6761 | 2.01e-14 | 1.39e-15 |
| doomloop-h2 | ready | vulnerability100 | -0.1207 | -0.1207 | 1.40e-13 | 2.29e-13 |
| doomloop-h2 | ready | growth | 0.0333 | 0.0333 | 3.25e-15 | 3.47e-18 |
| doomloop-h2 | ready | inflation_cpi | -0.0084 | -0.0084 | 1.38e-15 | 2.95e-17 |
| doomloop-h2 | ready | reserves | -0.0095 | -0.0095 | 2.29e-15 | 2.30e-16 |
| doomloop-h2 | ready | tt | -0.0058 | -0.0058 | 1.59e-15 | 4.25e-16 |
| doomloop-h2 | ready_debt | ready_debt_kink_low | -2.6852 | -2.6852 | 5.66e-13 | 2.47e-13 |
| doomloop-h2 | ready_debt | ready_debt_kink_high | 0.1172 | 0.1172 | 3.37e-15 | 1.57e-15 |
| doomloop-h2 | ready_debt | readiness_lag | 0.6825 | 0.6825 | 1.83e-14 | 3.24e-15 |
| doomloop-h2 | ready_debt | vulnerability100 | -0.109 | -0.109 | 1.37e-13 | 3.60e-13 |
| doomloop-h2 | ready_debt | growth | 0.0329 | 0.0329 | 2.79e-15 | 1.70e-16 |
| doomloop-h2 | ready_debt | inflation_cpi | -0.0118 | -0.0118 | 4.72e-16 | 8.85e-17 |
| doomloop-h2 | ready_debt | reserves | -0.009 | -0.009 | 1.98e-15 | 3.68e-16 |
| doomloop-h2 | ready_debt | tt | -0.0056 | -0.0056 | 1.54e-15 | 3.99e-17 |
| doomloop-h2-no-state | debt | debt_kink_low | 2.0166 | 2.0166 | 8.22e-14 | 4.72e-15 |
| doomloop-h2-no-state | debt | debt_kink_high | -0.9349 | -0.9349 | 1.21e-14 | 6.38e-16 |
| doomloop-h2-no-state | debt | vulnerability100 | 0.4 | 0.4 | 7.76e-14 | 1.33e-12 |
| doomloop-h2-no-state | debt | growth | -0.6795 | -0.6795 | 7.77e-16 | 1.94e-15 |
| doomloop-h2-no-state | debt | inflation_cpi | -0.1753 | -0.1753 | 2.25e-15 | 4.16e-17 |
| doomloop-h2-no-state | debt | reserves | 0.0001 | 0.0001 | 1.68e-15 | 2.67e-16 |
| doomloop-h2-no-state | debt | tt | 0.0358 | 0.0358 | 4.44e-16 | 2.27e-16 |
| doomloop-h2-no-state | ready | ready_kink_low | -6.3419 | -6.3419 | 2.14e-13 | 3.92e-14 |
| doomloop-h2-no-state | ready | ready_kink_high | 0.161 | 0.161 | 1.41e-14 | 1.82e-15 |
| doomloop-h2-no-state | ready | vulnerability100 | 0.1481 | 0.1481 | 1.02e-13 | 5.77e-14 |
| doomloop-h2-no-state | ready | growth | 0.0293 | 0.0293 | 4.81e-15 | 4.44e-16 |
| doomloop-h2-no-state | ready | inflation_cpi | -0.0214 | -0.0214 | 3.43e-15 | 4.44e-16 |
| doomloop-h2-no-state | ready | reserves | -0.0115 | -0.0115 | 7.01e-16 | 1.08e-15 |
| doomloop-h2-no-state | ready | tt | -0.0169 | -0.0169 | 2.57e-16 | 2.48e-16 |
| doomloop-h2-no-state | ready_debt | ready_debt_kink_low | -3.3972 | -3.3972 | 1.73e-14 | 7.05e-15 |
| doomloop-h2-no-state | ready_debt | ready_debt_kink_high | 0.125 | 0.125 | 8.99e-15 | 1.79e-15 |
| doomloop-h2-no-state | ready_debt | vulnerability100 | 0.275 | 0.275 | 9.28e-14 | 1.26e-13 |
| doomloop-h2-no-state | ready_debt | growth | 0.0143 | 0.0143 | 4.71e-15 | 5.27e-16 |
| doomloop-h2-no-state | ready_debt | inflation_cpi | -0.0074 | -0.0074 | 2.77e-15 | 8.67e-17 |
| doomloop-h2-no-state | ready_debt | reserves | -0.0133 | -0.0133 | 4.16e-16 | 4.58e-16 |
| doomloop-h2-no-state | ready_debt | tt | -0.014 | -0.014 | 1.37e-16 | 2.69e-17 |

### 6.4 Cutoff 最小 RSS 复核

| 规格 | 方程 | 记录 cutoff | profile 最小 RSS | cutoff RSS | 差值 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 第四节-含状态 | debt | 0.013 | 3.3717 | 3.3717 | 0 | 通过 |
| 第四节-含状态 | ready | 0.0253 | 0.3671 | 0.3671 | 0 | 通过 |
| 第四节-含状态 | ready_debt | 0.013 | 3.3717 | 3.3717 | 0 | 通过 |
| 第四节-去状态 | debt | 0.0455 | 3.5908 | 3.5908 | 0 | 通过 |
| 第四节-去状态 | ready | 0.0442 | 1.3252 | 1.3252 | 0 | 通过 |
| 第四节-去状态 | ready_debt | 0.0455 | 3.5908 | 3.5908 | 0 | 通过 |
| 第五节-含状态 | debt | 0.013 | 7.5739 | 7.5739 | 0 | 通过 |
| 第五节-含状态 | ready | 0.025 | 0.6959 | 0.6959 | 0 | 通过 |
| 第五节-含状态 | ready_debt | 0.013 | 7.5739 | 7.5739 | 0 | 通过 |
| 第五节-去状态 | debt | 0.0749 | 8.461 | 8.461 | 0 | 通过 |
| 第五节-去状态 | ready | 0.0369 | 1.275 | 1.275 | 0 | 通过 |
| 第五节-去状态 | ready_debt | 0.0749 | 8.461 | 8.461 | 0 | 通过 |

## 7. 图形 QA

第四、第五节分别生成含状态与去状态的债务图、readiness 自身 cutoff 图、readiness 债务 cutoff 图及合并图，全部保留 PNG 与 PDF。单方程图使用连续 theta 网格并把 cutoff 精确插入网格；竖直虚线与 CSV 中记录的 cutoff 一致。

## 8. 必须保留的限制与建议

- 当前稳健标准误处理异方差，但不处理同一国家内序列相关；面板论文通常还应报告国家聚类标准误或适当的双向聚类/空间相关推断。
- cutoff 在同一样本上搜索，条件于 cutoff 的常规标准误偏窄风险未纳入。建议按国家重抽样，完整重复 baseline、tax/theta、cutoff 搜索和最终回归。
- theta 是生成解释变量；联合不确定性依赖跨方程协方差。当前只对两个组成边际量分别做 delta-method 标准误，不提供 theta 的联合 SE。
- 结果是固定效应相关性证据，不支持没有额外识别设计的因果措辞。

## 9. 原始诊断输出索引

完整 CSV/DTA/日志仍保留在 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/`、`doomloop/stata_outputs/` 与 `doomloop_forward/stata_outputs/`。本文件是汇总层，不替代这些逐项机器可读结果。
