# Baseline 固定价格 GDP 对数控制设计

## 目标

将 Paper B 的 Baseline 宏观控制变量从 $\ln(CurrentGDP_{it})$ 完整替换为 $\ln(ConstantGDP_{it})$，并保持 tax 与 Doomloop 方程不加入任何 GDP 控制。修改后需重新估计全部主流程、刷新机器可读结果、图形和汇总文档。

## 范围

本次修改覆盖：

- `paperB/code/baseline_twfe.do` 中 Baseline 共同样本、逐步模型、交互模型、诊断与元数据。
- `paperB/code/empirical_theta.do` 中用于复现和核对 Baseline 的 spread 样本与回归；tax 方程本身保持不含 GDP 控制。
- `paperB/run_workflow.ps1` 中对 Baseline、tax 和 Doomloop 模型变量口径的整合检查。
- `paperB/render_output.py` 中变量标签、结果表、诊断表和叙述文字。
- `paperB/WORKFLOW.md` 与自动生成的 `paperB_results.md`、`paperB_diagnostics.md`、`progress.md`。
- 对应的 CSV、DTA、日志和图形产物。

本次不修改 `data0804/invest_panel_weo.csv` 的数据构建逻辑，不改变 tax 或 Doomloop 的回归控制集合，也不改变固定效应、标准误、样本锁定、theta 构造或 cutoff 搜索方法。

## 方案

### 变量构造与命名

Baseline 和 empirical-theta 的 Baseline 复核路径统一执行：

```stata
count if ConstantGDP<=0 & !missing(ConstantGDP)
assert r(N)==0
generate double ln_constantgdp = ln(ConstantGDP) if ConstantGDP>0
```

所有原来作为 Baseline 控制项的 `ln_currentgdp` 改为 `ln_constantgdp`。机器可读系数、描述统计、缺失审计、变异诊断与验证记录均使用新变量名，避免计算口径与字段名不一致。

`CurrentGDP` 仍是上游数据中的合法字段，并继续用于 `reserves` 的美元同币种分母；因此不得在数据构建脚本或数据说明中做全局删除或重命名。

### 模型边界

Baseline 宏观控制变为：

```text
growth ln_constantgdp inflation_cpi
```

empirical-theta 中的 spread 复核使用完全相同的控制集合，以继续逐系数核对 Baseline。tax 方程仍只使用 `growth inflation_cpi` 作为宏观控制，Doomloop 方程也仍只使用 `growth inflation_cpi`；二者都不得出现 `CurrentGDP`、`ConstantGDP`、`ln_currentgdp` 或 `ln_constantgdp` 回归项。

### 输出与文档

结果渲染器将 `ln_constantgdp` 显示为 $\ln(ConstantGDP_{it})$，Baseline 表格、方法文字和诊断表均使用新口径。empirical-theta panel 保存 `ConstantGDP` 与 `ln_constantgdp` 以支持复核；保留原始 `CurrentGDP` 字段不会使其进入任何模型。

完整流程重新生成：

- `baseline/stata_outputs/`
- `empirical_theta/stata_outputs/`
- `doomloop/stata_outputs/`
- `doomloop/figures/` 与 `paperB/figures/`
- `paperB/paperB_results.md`
- `paperB/paperB_diagnostics.md`
- `paperB/progress.md`

## 错误处理与质量门槛

- `ConstantGDP` 存在非缺失但非正值时立即停止，避免对无效值取对数。
- Baseline 输出必须包含 `ln_constantgdp`，且不得包含 `ln_currentgdp`。
- empirical-theta 的 spread 复核必须使用 `ln_constantgdp`；tax 系数表不得包含任何 GDP 水平或对数控制。
- Doomloop 系数表不得包含任何 GDP 水平或对数控制。
- 生成文档不得再把 $\ln(CurrentGDP)$ 描述为 Baseline 控制。
- 既有单位换算、公式、样本、cutoff、RSS 和 LSDV 复核仍须全部通过。

## 测试与验收

先增加静态回归测试，使其在旧代码上因 Baseline 仍使用 `ln_currentgdp` 而失败；再实施最小替换并确认测试通过。随后执行完整入口：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1
```

验收条件：

1. 三个 Stata 阶段均出现完成标记，日志无 `r(#);` 错误。
2. 整合 QA 通过。
3. Baseline 与 empirical-theta spread 复核只出现 `ln_constantgdp`。
4. tax 与 Doomloop 系数输出均不含 GDP 控制项。
5. 三份生成文档、三组 PNG/PDF 图形与所有机器可读输出均被刷新并可打开。
6. 对旧的 `ln_currentgdp` Baseline 口径执行语境化残留扫描，结果为零。
