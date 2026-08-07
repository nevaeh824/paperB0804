# Paper B 完整可复现流程

## 1. 目标与交付结构

`paperB` 是 `baseline`、`empirical_theta`、`doomloop` 三个板块的统一入口与汇总层。四份完整 Stata 源码统一保存在 `paperB/code/`；`paperB/run_workflow.ps1` 按依赖顺序直接调用这些源码，重建板块输出并生成统一文档。当前仓库因此可从已交付的分析 CSV 独立重跑，不再依赖仓库外的模块脚本。

```text
paperB/
├─ run_workflow.ps1          # 唯一运行入口
├─ render_output.py          # 统一读取 CSV 并生成三份文档
├─ paperB_results.md         # 公式、正式回归表、边际效应、cutoff、图形
├─ paperB_diagnostics.md     # 描述统计、数据检查、统计检验、验证与限制
├─ progress.md               # 当前进展、实证结论、核心卡点与下一步
├─ WORKFLOW.md               # 本流程说明
├─ code/                     # 四个 Stata 估计模块的权威源码
└─ figures/                  # 最终 kink 图的 PNG/PDF 快照
```

四份估计源码及其机器可读输出分别位于：

- `paperB/code/baseline_twfe.do` → `baseline/stata_outputs/`
- `paperB/code/empirical_theta.do` → `empirical_theta/stata_outputs/`
- `paperB/code/doomloop.do`、`paperB/code/doomloop_no_state.do`：`horizon=1` → `doomloop/stata_outputs/`，`horizon=2` → `doomloop_forward/stata_outputs/`

统一入口会顺序执行六个估计阶段：baseline、empirical theta，以及 Doomloop 主规格/去状态规格在两个结果时距上的四次运行。入口检查每个 Stata 日志的完成标记和 `r(#);` 错误，然后复制图形、重新渲染文档并执行整合 QA。日常维护只修改 `paperB/code/` 中的权威源码，避免两套代码静默分叉。

统一流程不读取、也不引用项目根目录下的旧实证方案草稿。唯一分析输入是 `data0804/invest_panel_weo.csv`。若要从更上游重新构建这份 CSV，`data0804/build_invest_panel_weo.py` 还需要基础面板 `cleaned_imf_like_panel_1995_2023.csv` 与 `WEOApr2026all.xlsx`；这两份源文件当前未纳入仓库，因此数据构建层尚未完全自包含。

## 2. 软件与运行方式

默认环境：Stata 18 MP、PowerShell、Python 3.14。默认 Stata 路径是 `C:\Environment_tools\Stata18\StataMP-64.exe`。

在项目根目录运行完整估计：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1
```

指定 Stata：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1 `
  -StataExe 'D:\Stata18\StataMP-64.exe'
```

只使用现有 Stata 输出重新生成和核验统一文档：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1 -SkipStata
```

`-SkipStata` 不重新估计，但仍会读取和核验现有机器可读输出、复制最终图形、重新生成三份汇总文档，并执行 paperB 层面的公式和文件检查。

## 3. 严格执行顺序

### Step 1：Baseline

1. 导入原始 CSV，确认国家—年份键唯一。
2. 将源百分数、比率和 0—100 指数除以 100；金额变量不缩放。
3. 构造 `ln_currentgdp=ln(CurrentGDP)`。
4. 锁定 baseline 共同样本。
5. 逐步估计仅 X、仅 A、仅 b、三核心、宏观控制、第一层、第二层、A×b、A×X、双交互模型。
6. 所有模型包含国家和年份固定效应；使用观测层面的异方差稳健标准误。
7. 输出模型系数、模型统计量、边际效应、Wald 检验、单位审计、缺失审计、变异分解、共线性和估计器复核。

Baseline 全规格为：

```math
s_{it}=\alpha_i+\lambda_t+\beta_AA_{it}+\beta_Bb_{it}+\beta_XX_{it}
+\beta_{AB}A_{it}b_{it}+\beta_{AX}A_{it}X_{it}
+\Gamma_m'W^m_{it}+\varepsilon^m_{it}.
```

控制变量统一为：

```text
宏观：growth ln_currentgdp inflation_cpi
外部：reserves tt
```

交互项使用 baseline 固定样本均值中心化：

```math
A^c=A-\bar A_s,\qquad b^c=b-\bar b_s,\qquad X^c=X-\bar X_s.
```

从中心化系数还原原始尺度：

```math
\widehat\beta_A^{raw}
=\widehat\beta_A^c
-\widehat\beta_{AB}\bar b_s
-\widehat\beta_{AX}\bar X_s.
```

因此适应能力的边际利差节约为：

```math
\widehat m^A_{it}
=-\left(\widehat\beta_A^{raw}
+\widehat\beta_{AB}b_{it}
+\widehat\beta_{AX}X_{it}\right)
=-\left(\widehat\beta_A^c
+\widehat\beta_{AB}b^c_{it}
+\widehat\beta_{AX}X^c_{it}\right).
```

### Step 2：Empirical theta

1. 重新导入原始数据并执行与 baseline 相同的单位审计。
2. 复现 baseline 全交互模型并与 baseline 输出逐系数核对。
3. 通过 Stata 面板 `F.` 运算符取得严格相邻年份的 `taxgdp`；跨年份缺口自动记为缺失。
4. 锁定 tax 共同样本，逐个检验 X、A、当期税收比率、核心项、控制变量和交互项。
5. 使用全控制税基交互模型构造边际税基收益。
6. 在观测层面构造 `mA_hat`、`TA_hat` 和 `theta_hat_A`，保存可供 doomloop 直接使用的 panel。

`taxgdp` 的源单位为 GDP 百分比，读入后乘 0.01 转成 0—1 比率。税基时序定义为：

```math
T_{i,t+1}
=taxgdp_{i,t+1}\times0.01,
\qquad
T_{it}
=taxgdp_{it}\times0.01.
```

两项均为比率，不乘 100。税基全规格为：

```math
T_{i,t+1}
=\alpha_i+\lambda_t
+\gamma_AA_{it}+\gamma_XX_{it}
+\gamma_{AX}A_{it}X_{it}
+\rho_TT_{it}
+\Gamma_T'W^T_{it}+\varepsilon^T_{i,t+1}.
```

该方程的宏观控制为 `growth inflation_cpi`，外部控制为 `reserves tt`；不加入 `CurrentGDP` 或 `ln_currentgdp`，也不使用 `CurrentGDP` 构造因变量。实现中 `ln_currentgdp` 仅用于复现 baseline 的固定共同样本。

税基交互项在 tax 固定样本内中心化：

```math
A_T^c=A-\bar A_T,\qquad X_T^c=X-\bar X_T.
```

原始尺度系数和边际税基收益为：

```math
\widehat\gamma_A^{raw}
=\widehat\gamma_A^c-\widehat\gamma_{AX}\bar X_T,
```

```math
\widehat T^A_{it}
=\widehat\gamma_A^{raw}+\widehat\gamma_{AX}X_{it}
=\widehat\gamma_A^c+\widehat\gamma_{AX}X^c_{it}.
```

最终经验指标使用 `debt_gdp` 作为 (b_{it})：

```math
\widehat\theta^A_{it}
=b_{it}\widehat m^A_{it}+\widehat T^A_{it},
\qquad b_{it}=debt\_gdp_{it}.
```

流程保存：

```text
empirical_theta/stata_outputs/empirical_theta_panel.dta
empirical_theta/stata_outputs/empirical_theta_panel.csv
```

### Step 3：第四节 Doomloop 债务变化与 readiness 水平主规格

1. 读取 `empirical_theta_panel.dta`。
2. 在搜索 cutoff 前，重新计算 `debt_gdp*mA_hat+TA_hat`，确认与 `theta_hat_A` 一致。
3. 构造严格时序的 `b_outcome=F.debt_gdp-debt_gdp` 与 `A_outcome=readiness100`。
4. 所有 Doomloop 回归都显式加入 (X_{it})。宏观控制统一为 `growth inflation_cpi`，外部控制统一为 `reserves tt`；任何规格都不加入 `CurrentGDP` 或 `ln_currentgdp`。
5. 分别锁定债务方程和 readiness 方程的全控制样本。
6. 在样本内 P10—P90 的 theta 候选上，分别搜索债务全控制方程与 readiness 全控制方程的 RSS 最小 cutoff。
7. readiness 额外固定在债务全控制方程的 RSS 最优 cutoff 上，形成第二种 cutoff 口径；每种口径估计核心、宏观、全控制三列。
8. 计算点边际效应、Wald 联合检验和边际效应曲线。

债务变化定义与主方程为：

```math
\Delta b_{i,t+1}=b_{i,t+1}-b_{it},
```

```math
\Delta b_{i,t+1}
=\alpha_i+\lambda_t
+\beta_LA_{it}(c-\widehat\theta^A_{it})_+
+\beta_HA_{it}(\widehat\theta^A_{it}-c)_+
+\rho_bb_{it}+\gamma_XX_{it}
+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.
```

Readiness 水平主方程为：

```math
A_{it}
=\alpha_i+\lambda_t
+\delta_LFT_{it}(c-\widehat\theta^A_{it})_+
+\delta_HFT_{it}(\widehat\theta^A_{it}-c)_+
+\rho_AA_{i,t-1}+\gamma_XX_{it}
+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.
```

第二个方程的两支只乘 `FT=interest_revenue`，不乘 (A_{it})。

两类方程的控制向量均包含 `growth inflation_cpi reserves tt`，不包含 GDP 控制。

### Step 4：去状态变量规格

在完全相同的数据口径和各方程对应的控制变量下，分别：

- 从债务变化方程去掉 (b_{it})；
- 从 readiness 水平方程去掉 (A_{i,t-1})。

由于目标函数改变，两组去状态变量规格各自重新执行完整 cutoff 搜索。去滞后 readiness 也同时报告自身 RSS cutoff 与去 b 债务全控制方程的 RSS cutoff。

### Step 5：第五节两期前瞻规格

`doomloop.do` 与 `doomloop_no_state.do` 以 `horizon=2` 再运行一次，输出到 `doomloop_forward/`，不覆盖第四节结果。规格、控制变量、固定样本、cutoff 搜索、去状态变体与第四节完全相同。两期债务变化定义为：

```math
\Delta b_{i,t+2}=b_{i,t+2}-b_{it},
```

主方程为：

```math
\Delta b_{i,t+2}
=\alpha_i+\lambda_t
+\beta_LA_{it}(c-\widehat\theta^A_{it})_+
+\beta_HA_{it}(\widehat\theta^A_{it}-c)_+
+\rho_bb_{it}+\gamma_XX_{it}
+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1},
```

```math
A_{i,t+1}
=\alpha_i+\lambda_t
+\delta_LFT_{it}(c-\widehat\theta^A_{it})_+
+\delta_HFT_{it}(\widehat\theta^A_{it}-c)_+
+\rho_AA_{i,t-1}+\gamma_XX_{it}
+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.
```

Stata 使用严格的 `F2.debt_gdp-debt_gdp` 与 `F.readiness100`，年份缺口不会被误当成 lead。

### Step 6：边际效应与作图

每个时距的债务、readiness 自身 cutoff、readiness 债务 cutoff，以及对应去状态规格统一绘制：

```math
m(\theta;c)=a(c-\theta)_++b(\theta-c)_+.
```

在 (	heta=c) 处函数定义为 0。图中：

- 横轴：经验指标 (widehat\theta^A)，统一比率尺度；
- 纵轴：对应的点边际效应；
- 竖直虚线：该规格使用的 cutoff；对 readiness 债务-cutoff 图，它来自对应债务全控制方程；
- PNG：用于 Markdown 预览；
- PDF：用于论文排版。

### Step 7：统一渲染

`paperB/render_output.py` 只读取已验证的 CSV 输出，不重新估计模型。它生成：

1. `paperB_results.md`：全部公式、逐步回归表、构造系数、theta 描述、两种时距与两种 readiness cutoff 的点边际效应和图形。
2. `paperB_diagnostics.md`：单位审计、样本、描述统计、缺失、within 变异、VIF、相关性、系数变化、Wald 检验、代数复核、估计器复核、cutoff 复核和解释限制。

这样正式论文结果与审计材料相互分离，同时由同一批机器可读输出生成。

## 4. 固定效应与标准误口径

系数与推断由：

```stata
areg ..., absorb(country_id) vce(robust)
```

给出，并加入 `i.year`。`xtreg, fe` 仅用于取得可比的 within/overall (R^2)。流程另用显式国家和年份虚拟变量的 LSDV 回归对关键系数与标准误做数值复核。

这里的 `vce(robust)` 是观测层面异方差稳健标准误，不是国家聚类。若要改变为国家聚类或双向聚类，必须在三个板块中统一修改，并重新执行完整管线；不能只改最后一段。

## 5. 样本规则

- 不做逐模型样本漂移：每个板块或方程先锁定全规格共同样本。
- 面板 `F.` 和 `L.` 要求严格相邻年份；年份缺口不会被当作一阶 lead/lag。
- 国家—年份重复键会触发停止，不自动去重。
- cutoff 搜索与该方程后续所有逐步模型使用同一固定样本。
- `theta_support` 是 baseline spread 样本与 tax 样本交集；doomloop 可使用所有能完整构造 theta 且满足各自方程变量非缺失的观测。

## 6. 自动验证与停止条件

各板块和统一入口都会检查：

1. 输入文件、Stata 日志和要求的输出文件存在；
2. Stata 日志含完成标记且不含 `r(#);` 运行错误；
3. Baseline 的 13 个源比例变量、empirical-theta 加入 `taxgdp` 后的 14 个源比例变量，均确实等于源值除以 100；
4. `b_it_theta` 与 `debt_gdp` 逐行一致；
5. 中心化公式与原始尺度公式逐行一致；
6. `theta_hat_A=debt_gdp*mA_hat+TA_hat`；
7. doomloop hinge 项与理论公式逐行一致；
8. 保存的 cutoff 对应 RSS profile 的最小值；
9. `areg` 与显式 LSDV 的关键估计一致；
10. 统一文档含正确的 $T_{i,t+1}$、$T_{it}$、theta 与 readiness kink 公式；
11. 所需 PNG/PDF 图形存在且非空。

任何关键映射、公式、重复键或输出完整性检查失败，流程应停止，而不是继续生成报告。

## 7. 结果更新规则

当原始数据、变量口径、控制变量、固定样本或估计器发生变化时，必须运行完整流程，不要只运行 `render_output.py`。只有在 Stata 输出未变、仅需重新排版文档时，才使用 `-SkipStata`。

不要手工改 `paperB_results.md`、`paperB_diagnostics.md` 或 `progress.md` 中的数字；这三份文件每次运行都会从 CSV 重建。需要改变呈现逻辑时，修改 `paperB/render_output.py`，然后重新运行统一入口。

## 8. 推断限制与建议扩展

当前流程提供可复现的固定效应相关性证据，不构成因果识别。建议的下一层稳健性包括：

1. 国家层面聚类标准误，并与当前异方差稳健结果并列；
2. 以国家为重抽样单位的完整管线 bootstrap；
3. 每次 bootstrap 都重新估计 baseline、tax、theta、cutoff 和最终 kink 回归；
4. 报告 cutoff 分布、分支系数分布与 theta 生成误差；
5. 对不同 trimming、候选网格和样本窗口做 cutoff 敏感性分析。

这些扩展必须作为全流程变体实现，不能把上游生成量固定后只 bootstrap 最后一条回归。
