# Paper B Growth、GDP 与债务口径更新设计

## 目标

在不改变 Paper B 三阶段流水线、固定效应估计器、标准误口径、固定样本原则和结果目录的前提下，统一更新全部主流程回归：每条回归控制 `growth` 与 `ln_capitagdp`；原税基方程改为总量产出方程 `Y`，其中 `ln_currentgdp=ln(CurrentGDP)`；原来由债务/GDP 比率承担的 `b` 全部改为 `ln_debt=ln(debt)`；随后重跑 Stata 并重建文档和图形。

## 方案比较与选择

1. **推荐：原位迁移现有三阶段流水线。** 修改三份权威 `.do`、统一入口和渲染器，保留现有模型层级与输出目录。优点是结果仍可与现有流程逐表核对，影响范围清晰。
2. **新增平行规格。** 保留旧口径并新增一套 growth/Y/log-debt 结果。优点是便于对照，缺点是用户要求是“所有回归”统一修改，双口径会使正式结果含混。
3. **重写分析层。** 用 Python 或新 Stata 程序重建全流程。可简化旧代码，但会同时改变实现和计量口径，验证成本与风险最高。

采用方案 1。

## 变量与模型设计

- 从唯一输入 `data0804/invest_panel_weo.csv` 构造：
  - `ln_capitagdp = ln(capitaGDP)`，仅对严格正值定义；
  - `ln_currentgdp = ln(CurrentGDP)`，仅对严格正值定义；
  - `ln_debt = ln(debt)`，仅对严格正值定义。
- `growth` 继续按源百分数除以 100，与 `ln_capitagdp` 一起组成 `always_controls`。二者进入 baseline、Y、经验 theta 复现、Doomloop cutoff 搜索、竞争判据和 readiness 的每一条回归，并进入相应固定共同样本。
- 原宏观递增层保留 `inflation_cpi`；外部递增层保留 `reserves tt`。这样逐步模型仍有可解释的增量，同时所有模型满足共同控制要求。
- Baseline 的核心债务变量、中心化债务项与 `A×b` 交互均由 `ln_debt` 构造。
- 原税基方程改为：

  ```math
  Y_{i,t+1}=\alpha_i+\lambda_t+\gamma_AA_{it}+\gamma_XX_{it}
  +\gamma_{AX}A_{it}X_{it}+\rho_YY_{it}
  +\Gamma_Y'W^Y_{it}+\varepsilon^Y_{i,t+1},
  \qquad Y_{it}=\ln(CurrentGDP_{it}).
  ```

  实现使用严格相邻年份的 `Y_outcome=F.ln_currentgdp` 与 `Y_lag=ln_currentgdp`，模型标识由 `T1`—`T10` 改为 `Y1`—`Y10`。
- 适应能力的边际产出收益记为 `YA_hat`，经验判据改为：

  ```math
  \widehat\theta^A_{it}=\ln(debt_{it})\widehat m^A_{it}+\widehat Y^A_{it}.
  ```

- Doomloop 债务结果改为严格相邻年份的：

  ```math
  \Delta\ln(debt)_{i,t+1}=F.\ln(debt_{it})-\ln(debt_{it}).
  ```

  竞争判据相应为 `theta_hat_A`、`ln_debt`、`mA_hat`、`YA_hat` 和 `ln_debt_mA_hat`。

## 输出与验证

- 保留 `baseline/stata_outputs/`、`empirical_theta/stata_outputs/`、`doomloop/stata_outputs/` 和 `paperB/figures/` 的目录契约；现有 CSV/DTA/日志/图形由完整流程覆盖更新。
- 更新 `render_output.py` 和 `WORKFLOW.md`，使表格标签、公式、诊断说明与新口径一致，不手工修改生成结果中的数字。
- 自动测试检查真实机器可读输出：所有报告模型包含 `growth`、`ln_capitagdp`；Y 模型和构造参数使用新命名；panel 中的 log 映射和 theta 恒等式成立；Doomloop 使用 log-debt 结果与五个新判据。
- 统一入口检查输入正值、模型系数、构造恒等式、共同样本、cutoff/RSS、图形和文档公式；任何失败均停止流程。

## 非目标

- 不改变国家/年份固定效应、`areg ..., absorb(country_id) vce(robust)` 推断口径、P10—P90 cutoff 网格、readiness 共用债务方程 cutoff 的规则。
- 不更新退出主流程的 `doomloop.do` 或 `doomloop_forward/` 历史规格。
- 不重建 `invest_panel_weo.csv`，因为所需 `CurrentGDP`、`debt`、`growth` 和 `capitaGDP` 已存在且正值条件可满足。
