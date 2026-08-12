# Paper B debt/GDP 与产出比率设计

## 目标

- 将所有理论记号中的 `b_it` 从 `ln(debt_it)` 攦为导入后除以 100 的 `debt_gdp_it` 比率。
- 将产出回归左侧改为 `Y_outcome = ConstantGDP_(t+1) / ConstantGDP_t`。
- 将产出回归的状态控制改为 `Y_lag = ConstantGDP_t / ConstantGDP_(t-1)`。
- 所有产出回归取消 `growth` 和 `ln_constantgdp`；其他方程沿用当前控制策略。

## 数据与时序

`debt_gdp` 属于源百分比变量，进入 Stata 后统一除以 100。`b_it_theta` 是它的精确别名；theta 构造使用 `debt_gdp_mA_hat = debt_gdp * mA_hat`，并满足 `theta_hat_A = debt_gdp_mA_hat + YA_hat`。Doomloop 左侧随之改为严格相邻年份的 `F.debt_gdp - debt_gdp`。

产出比率只在当前期、前一期或后一期 `ConstantGDP` 均严格为正且年份相邻时定义。Stata 的 `F.`/`L.` 运算符负责禁止跨年份缺口配对。每个 Y1--Y10 模型均含新的 `Y_lag`；Y1/Y2 的名称仅表示额外理论解释变量分别为 X/A，Y3 是只含共同状态控制的持久性规格。

## 影响范围

- `baseline_twfe.do`：核心债务变量、中心化、交互项、边际效应和审计映射。
- `empirical_theta.do`：spread 方程的 b、产出比率、样本、Y1--Y10、theta 构造和公式审计。
- `doomloop_no_state.do`：债务变化、theta 重构、竞争判据和输出标签。
- `run_workflow.ps1`：机器输出、控制项、映射与时序恒等式 QA。
- `render_output.py` 与 `WORKFLOW.md`：公式、表格、诊断和结果文字。
- 契约测试：独立按 CSV 的国家—年份行验证两个 GDP 比率、debt/GDP 差分和 theta 恒等式。

## 成功标准

完整 Stata 工作流退出码为 0；所有正式 b 系数和判据使用 `debt_gdp`；每个 Y 模型恰含一个 `Y_lag` 且不含 `growth`/`ln_constantgdp`；逐行数值恒等式、既有 readiness 差分、日志扫描和全部自动测试通过。
