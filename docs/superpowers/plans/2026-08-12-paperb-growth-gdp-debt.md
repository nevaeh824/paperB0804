# Paper B Growth、GDP 与债务口径更新 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Paper B 主流程统一改为每条回归控制 growth 与 ln_capitagdp、Y=ln(CurrentGDP) 替代税基 T、ln(debt) 替代原 b，并重跑全部结果。

**Architecture:** 保留 baseline → empirical theta → no-state Doomloop 的依赖顺序。三份 Stata 源码负责估计和机器可读输出，PowerShell 入口负责跨阶段 QA，Python 渲染器只消费通过验证的 CSV 并重建正式文档。

**Tech Stack:** Stata 18 MP、PowerShell、Python 3.14 `unittest`、CSV/Markdown/PNG/PDF。

## Global Constraints

- 唯一分析输入是 `data0804/invest_panel_weo.csv`。
- 每条回归必须包含 `growth ln_capitagdp`，固定样本也必须包含二者的非缺失条件。
- `ln_currentgdp=ln(CurrentGDP)`、`ln_debt=ln(debt)` 仅对严格正值定义。
- 固定效应、稳健标准误、cutoff 网格和 readiness 共用债务 cutoff 的规则不变。
- 只修改当前主流程，不修改退出主流程的历史规格。

---

### Task 1: 建立新口径的输出契约测试

**Files:**
- Create: `tests/test_paperb_growth_gdp_debt_contract.py`
- Modify: `tests/test_constant_gdp_contract.py`

**Interfaces:**
- Consumes: 当前各阶段 CSV 与生成 Markdown。
- Produces: 可在重跑前失败、重跑后通过的端到端输出契约。

- [ ] **Step 1: 写入输出契约测试**

  测试所有模型包含 `growth` 与 `ln_capitagdp`，baseline 使用 `ln_debt`，empirical theta 使用 `Y1`—`Y10`、`Y_lag` 与 `YA_hat`，panel 满足 log 映射和 theta 恒等式，Doomloop 使用 `ln_debt` 判据和 log 差分。

- [ ] **Step 2: 运行测试并确认旧结果按预期失败**

  Run: `python -m unittest tests.test_paperb_growth_gdp_debt_contract -v`

  Expected: FAIL，原因是旧输出仍排除 growth、使用 `debt_gdp` 和 tax-base T。

- [ ] **Step 3: 修改旧测试中的过时排除断言**

  保留 WEO 数据来源测试，删除“结果必须排除 growth/aggregate GDP”的旧口径断言，避免新旧契约互相冲突。

### Task 2: 更新 baseline 与 empirical theta 估计

**Files:**
- Modify: `paperB/code/baseline_twfe.do`
- Modify: `paperB/code/empirical_theta.do`

**Interfaces:**
- Consumes: `CurrentGDP`、`debt`、`growth`、`capitaGDP` 及现有面板变量。
- Produces: baseline CSV；含 `ln_debt`、`ln_currentgdp`、`YA_hat`、`theta_hat_A` 的 empirical-theta panel。

- [ ] **Step 1: 在 baseline 构造并审计 `ln_debt`**

  将核心 b、共同样本、中心化、交互、边际效应、公式检查和导出映射从 `debt_gdp` 改为 `ln_debt`。

- [ ] **Step 2: 将 `growth ln_capitagdp` 加入每个 baseline RHS**

  保留 inflation/external 的逐层递增，确保所有十个模型实际输出两个共同控制系数。

- [ ] **Step 3: 在 empirical theta 构造三个 log 量并复现新 baseline**

  使用与 baseline 完全相同的 `ln_debt` 交互与 always-controls，逐系数复核保持有效。

- [ ] **Step 4: 将税基 T 方程改为 Y 方程**

  构造 `Y_outcome=F.ln_currentgdp`、`Y_lag=ln_currentgdp`，将模型标识改为 `Y1`—`Y10`，所有 RHS 加入共同控制。

- [ ] **Step 5: 更新构造量与恒等式**

  生成 `YA_hat`、`ln_debt_mA_hat` 和 `theta_hat_A=ln_debt*mA_hat+YA_hat`，同步审计字段、参数来源与导出 panel。

### Task 3: 更新 Doomloop 主规格

**Files:**
- Modify: `paperB/code/doomloop_no_state.do`

**Interfaces:**
- Consumes: Task 2 生成的 empirical-theta DTA。
- Produces: log-debt 结果、更新后的五判据 cutoff/RSS、图形与诊断 CSV。

- [ ] **Step 1: 改写输入检查和债务结果**

  检查 `ln_debt` 映射与 theta 恒等式，构造 `b_outcome=F.ln_debt-ln_debt`。

- [ ] **Step 2: 把共同控制加入全部 Doomloop 回归**

  令 debt/readiness 的 core、macro、full、cutoff 搜索、竞争判据与估计器复核全部含 `growth ln_capitagdp`。

- [ ] **Step 3: 更新竞争判据和诊断导出**

  五判据使用 `theta_hat_A`、`ln_debt`、`mA_hat`、`YA_hat`、`ln_debt_mA_hat`，维持同一共同样本和 RSS 可比性。

### Task 4: 更新渲染和跨阶段 QA

**Files:**
- Modify: `paperB/render_output.py`
- Modify: `paperB/run_workflow.ps1`
- Modify: `paperB/WORKFLOW.md`

**Interfaces:**
- Consumes: Tasks 2—3 的 CSV、DTA、日志和图形。
- Produces: 新公式/标签的结果、诊断、进度文档及严格入口验证。

- [ ] **Step 1: 更新渲染器的模型名、变量标签、公式和表格行**

  将 T/tax-base 表述改为 Y/current GDP，将 debt/GDP 改为 log debt，并在所有模型表显示 growth 与 ln_capitagdp。

- [ ] **Step 2: 更新 PowerShell 输入和输出 QA**

  检查 `CurrentGDP debt capitaGDP` 正值；检查所有报告模型含共同控制；检查 Y、log-debt、theta 和五判据的新命名与恒等式。

- [ ] **Step 3: 更新 WORKFLOW**

  准确记录新变量、模型、控制顺序、公式和自动停止条件。

### Task 5: 全流程重跑与验证

**Files:**
- Regenerate: `baseline/stata_outputs/*`
- Regenerate: `empirical_theta/stata_outputs/*`
- Regenerate: `doomloop/stata_outputs/*`
- Regenerate: `doomloop/figures/*`
- Regenerate: `paperB/figures/*`
- Regenerate: `paperB/paperB_results.md`
- Regenerate: `paperB/paperB_diagnostics.md`
- Regenerate: `paperB/progress.md`

**Interfaces:**
- Consumes: 修改后的权威源码和原始 CSV。
- Produces: 完整更新并经 QA 的 Paper B 结果集。

- [ ] **Step 1: 运行完整工作流**

  Run: `powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1`

  Expected: 三段 Stata 日志均含完成标志，renderer 与 integrated QA 退出码为 0。

- [ ] **Step 2: 运行 Python 回归测试**

  Run: `python -m unittest discover -s tests -v`

  Expected: 全部通过，0 failures/errors。

- [ ] **Step 3: 执行结果完整性复核**

  检查 `git diff --check`、工作树差异、日志中的 `r(#);`、新结果的样本量/核心系数/cutoff，并确认用户未跟踪文件未被改动。
