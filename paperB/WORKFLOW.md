# Paper B 完整可复现流程

## 1. 目标与交付结构

`paperB` 是 `baseline`、`empirical_theta`、`doomloop` 三个板块的统一入口与汇总层。三份进入当前主流程的完整 Stata 源码统一保存在 `paperB/code/`；`paperB/run_workflow.ps1` 按依赖顺序直接调用这些源码，重建板块输出并生成统一文档。当前仓库因此可从已交付的分析 CSV 独立重跑，不再依赖仓库外的模块脚本。

```text
paperB/
├─ run_workflow.ps1          # 唯一运行入口
├─ render_output.py          # 统一读取 CSV 并生成三份文档
├─ paperB_results.md         # 公式、正式回归表、边际效应、cutoff、图形
├─ paperB_diagnostics.md     # 描述统计、数据检查、统计检验、验证与限制
├─ progress.md               # 当前进展、实证结论、核心卡点与下一步
├─ WORKFLOW.md               # 本流程说明
├─ code/                     # 当前主流程使用的 Stata 估计模块权威源码
└─ figures/                  # 最终 kink 图的 PNG/PDF 快照
```

当前主流程使用的三份估计源码及其机器可读输出分别位于：

- `paperB/code/baseline_twfe.do` → `baseline/stata_outputs/`
- `paperB/code/empirical_theta.do` → `empirical_theta/stata_outputs/`
- `paperB/code/doomloop_no_state.do` → `doomloop/stata_outputs/`

统一入口会顺序执行三个估计阶段：baseline、empirical theta，以及一期、去状态变量的 Doomloop 主规格（其中包括 Criterion Decomposition / Competing Criterion Test）。`doomloop.do` 的含状态变量规格和 `doomloop_forward/` 的两期前瞻规格不再进入主流程，但仍可从 `paperB/code/` 权威源码重建历史快照。入口检查每个 Stata 日志的完成标记和 `r(#);` 错误，然后复制图形、重新渲染文档并执行整合 QA；QA 逐模型确认 `growth` 与 `ln_constantgdp` 均按下述无重复口径进入回归。

统一流程不读取、也不引用项目根目录下的旧实证方案草稿。唯一分析输入是 `data0804/invest_panel_weo.csv`。若要从更上游重新构建这份 CSV，`data0804/build_invest_panel_weo.py` 还需要基础面板 `cleaned_imf_like_panel_1995_2023.csv` 与 `data0804/WEOApr2026all.xlsx`；当前工作区已有 WEO 文件，但缺少基础面板，因此数据构建层尚未完全自包含。

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
3. 构造 `ln_constantgdp=ln(ConstantGDP)` 与 `ln_debt=ln(debt)`；两项均只对严格正值定义。
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
所有规格：growth ln_constantgdp
宏观递增：inflation_cpi
外部：reserves tt
```

`growth` 与 `ln_constantgdp` 进入每一条回归，也进入共同样本锁定条件；`inflation_cpi` 和 `reserves tt` 仍按逐步规格递增。

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
3. 构造 `ln_constantgdp=ln(ConstantGDP)`，通过 Stata 面板 `F.` 运算符取得严格相邻年份的 `Y_outcome=F.ln_constantgdp`；跨年份缺口自动记为缺失。
4. 锁定 Y 共同样本，逐个检验 X、A、当期 log constant GDP、核心项、控制变量和交互项。
5. 使用全控制 Y 交互模型构造边际产出收益。
6. 在观测层面构造 `mA_hat`、`YA_hat`、`ln_debt_mA_hat` 和 `theta_hat_A`，保存可供 doomloop 直接使用的 panel。

产出时序定义为：

```math
Y_{i,t+1}
=\ln(ConstantGDP_{i,t+1}),
\qquad
Y_{it}
=\ln(ConstantGDP_{it}).
```

Y 全规格为：

```math
Y_{i,t+1}
=\alpha_i+\lambda_t
+\gamma_AA_{it}+\gamma_XX_{it}
+\gamma_{AX}A_{it}X_{it}
+\rho_YY_{it}
+\Gamma_Y'W^Y_{it}+\varepsilon^Y_{i,t+1}.
```

每个 Y 回归都控制 `growth` 与当期 `ln_constantgdp`；宏观递增控制为 `inflation_cpi`，外部递增控制为 `reserves tt`。由于 `Y_lag=ln_constantgdp`，Y3--Y10 由 `Y_lag` 唯一承载该 GDP 控制，不再重复加入完全相同的 `ln_constantgdp`；不含持久性项的 Y1、Y2 则直接加入 `ln_constantgdp`。因此每个 Y 模型中的当期 log constant GDP 恰好出现一次。

产出交互项在 Y 固定样本内中心化：

```math
A_Y^c=A-\bar A_Y,\qquad X_Y^c=X-\bar X_Y.
```

原始尺度系数和边际产出收益为：

```math
\widehat\gamma_A^{raw}
=\widehat\gamma_A^c-\widehat\gamma_{AX}\bar X_Y,
```

```math
\widehat Y^A_{it}
=\widehat\gamma_A^{raw}+\widehat\gamma_{AX}X_{it}
=\widehat\gamma_A^c+\widehat\gamma_{AX}X^c_{it}.
```

最终经验指标使用 `ln_debt` 作为 (b_{it})：

```math
\widehat\theta^A_{it}
=b_{it}\widehat m^A_{it}+\widehat Y^A_{it},
\qquad b_{it}=\ln(debt_{it}).
```

流程保存：

```text
empirical_theta/stata_outputs/empirical_theta_panel.dta
empirical_theta/stata_outputs/empirical_theta_panel.csv
```

### Step 3：第四节 Doomloop 债务变化与 readiness 变化主规格

第四节只保留一期、去状态变量规格；不再估计包含 (b_{it}) 或 (A_{i,t-1}) 的版本。

1. 读取 `empirical_theta_panel.dta`。
2. 在搜索 cutoff 前，重新计算 `ln_debt*mA_hat+YA_hat`，确认与 `theta_hat_A` 一致。
3. 构造严格时序的 `b_outcome=F.ln_debt-ln_debt` 与 `A_outcome=readiness100-L.readiness100`；面板年份不相邻时滞后值和差分自动缺失。
4. 所有 Doomloop 回归都显式加入 (X_{it})，并统一控制 `growth ln_constantgdp`；宏观递增控制为 `inflation_cpi`，外部递增控制为 `reserves tt`。
5. 分别锁定债务方程和 readiness 方程的全控制样本，后续逐步模型不得改变各自样本。
6. 仅在债务全控制方程样本内、(\widehat\theta^A_{it}) 的 P10—P90 候选上搜索 RSS 最小 cutoff，记为 (\widehat c_B^\theta)。
7. 债务方程的核心、宏观和全控制结果均使用 (\widehat c_B^\theta)。Readiness 方程不再搜索自身 cutoff；其核心、宏观和全控制结果全部固定使用债务全控制方程得到的 (\widehat c_B^\theta)。
8. 计算点边际效应、Wald 联合检验和边际效应曲线。

债务变化定义与唯一主方程为：

```math
\Delta\ln(debt)_{i,t+1}=\ln(debt_{i,t+1})-\ln(debt_{it}),
```

```math
\Delta\ln(debt)_{i,t+1}
=\alpha_i+\lambda_t
+\beta_LA_{it}(c-\widehat\theta^A_{it})_+
+\beta_HA_{it}(\widehat\theta^A_{it}-c)_+
+\gamma_XX_{it}
+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.
```

Readiness 变化的唯一主方程为：

```math
A_{it}-A_{i,t-1}
=\alpha_i+\lambda_t
+\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+
+\delta_HFT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_+
+\gamma_XX_{it}
+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.
```

Readiness 方程的两支只乘 `FT=interest_revenue`，不乘 (A_{it})；(A_{i,t-1}) 只用于构造左侧一阶差分，不作为右侧状态控制，该方程也不以自身 RSS 选择 cutoff。债务方程不另含 (b_{it}) 状态项。两类方程都控制 `growth ln_constantgdp`，并按规格加入 `inflation_cpi reserves tt`。

### Step 4：Criterion Decomposition / Competing Criterion Test

该模块检验 kink 结果究竟来自完整经验判据 (\widehat\theta^A_{it})，还是由它的组成部分或单一基础变量驱动。令阈值判据为 (q_{it})，在第四节同一债务全控制方程中估计：

```math
\Delta\ln(debt)_{i,t+1}
=\alpha_i+\lambda_t
+\beta_LA_{it}(c- q_{it})_+
+\beta_HA_{it}(q_{it}-c)_+
+\gamma_XX_{it}
+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.
```

依次使用以下五种判据：

```math
q_{it}\in\left\{
\widehat\theta^A_{it},\;
b_{it},\;
\widehat m^A_{it},\;
\widehat Y^A_{it},\;
b_{it}\widehat m^A_{it}
\right\},
\qquad
\widehat\theta^A_{it}=b_{it}\widehat m^A_{it}+\widehat Y^A_{it}.
```

其中 (\widehat\theta^A_{it}) 是基准判据，另外四项分别为 `ln_debt`、`mA_hat`、`YA_hat` 和 `ln_debt*mA_hat`。执行规则如下：

1. 五种判据使用同一个债务全控制共同样本、同一个因变量、同一组国家和年份固定效应、同一组控制变量以及同一种标准误口径，确保 RSS 可以直接比较。
2. 对每一种 (q_{it})，分别在其共同样本内 P10—P90 的候选值上执行完整网格搜索，选择使全控制方程 RSS 最小的 (\widehat c_q)。
3. 在各自的 (\widehat c_q) 上重新估计全控制方程，保存 cutoff、两支系数及 p 值、RSS、within (R^2) 和阈值两侧样本量。
4. 理论符号定义为 (\beta_L>0) 且 (\beta_H<0)。`theoretical signs` 列报告估计结果是否同时、部分或完全不符合这组方向性预测。
5. 样本量统一定义为 (N_{low}=\#\{q_{it}\leq\widehat c_q\})、(N_{high}=\#\{q_{it}>\widehat c_q\})；同时验证 (N_{low}+N_{high}=N)。

最终比较表按以下固定列序输出：

| Criterion | cutoff | beta_L | p_L | beta_H | p_H | theoretical signs | RSS | Within R2 | N_low | N_high |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|
| (\widehat\theta^A_{it}) |  |  |  |  |  |  |  |  |  |  |
| (b_{it}) |  |  |  |  |  |  |  |  |  |  |
| (\widehat m^A_{it}) |  |  |  |  |  |  |  |  |  |  |
| (\widehat Y^A_{it}) |  |  |  |  |  |  |  |  |  |  |
| (b_{it}\widehat m^A_{it}) |  |  |  |  |  |  |  |  |  |  |

各判据的 cutoff 和 (\beta_L,\beta_H) 处于各自变量尺度，不跨行比较绝对大小；模型优劣比较以共同样本上的 RSS 为主，并辅以 within (R^2)、显著性、理论符号和阈值两侧样本量。

### Step 5：边际效应与作图

仅对一期去状态变量主规格绘图：债务方程与 readiness 方程统一使用债务全控制方程选择的 (\widehat c_B^\theta)。Readiness 不生成自身 cutoff 图。边际效应统一写为：

```math
m(\theta;c)=a(c-\theta)_++b(\theta-c)_+.
```

在 (\theta=c) 处函数定义为 0。图中：

- 横轴：经验指标 (\widehat\theta^A)，统一比率尺度；
- 纵轴：对应的点边际效应；
- 竖直虚线：债务全控制方程的 RSS 最优 cutoff (\widehat c_B^\theta)；
- PNG：用于 Markdown 预览；
- PDF：用于论文排版。

### Step 6：统一渲染

`paperB/render_output.py` 只读取已验证的 CSV 输出，不重新估计模型。它生成：

1. `paperB_results.md`：全部公式、逐步回归表、构造系数、theta 描述、一期去状态变量主规格的点边际效应与图形，以及五种阈值判据的竞争比较表。
2. `paperB_diagnostics.md`：单位审计、样本、描述统计、缺失、within 变异、VIF、相关性、系数变化、Wald 检验、代数复核、估计器复核、各判据 cutoff/RSS 复核和解释限制。

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
- Competing Criterion Test 的五种判据必须进一步锁定同一个债务全控制共同样本；不得因判据不同而产生样本漂移。
- `theta_support` 是 baseline spread 样本与产出样本交集；doomloop 可使用所有能完整构造 theta 且满足各自方程变量非缺失的观测。

## 6. 自动验证与停止条件

各板块和统一入口都会检查：

1. 输入文件、Stata 日志和要求的输出文件存在；
2. Stata 日志含完成标记且不含 `r(#);` 运行错误；
3. Baseline 与 empirical-theta 的源比例变量均确实等于源值除以 100；
4. `ln_constantgdp=ln(ConstantGDP)`、`Y_lag=ln_constantgdp`、`Y_outcome=F.ln_constantgdp`、`ln_debt=ln(debt)`，且 `b_it_theta` 与 `ln_debt` 逐行一致；
5. 中心化公式与原始尺度公式逐行一致；
6. `theta_hat_A=ln_debt*mA_hat+YA_hat`；
7. Doomloop 主规格和五种竞争判据的 hinge 项与各自理论公式逐行一致；
8. (\widehat\theta^A_{it}) 及四种替代判据保存的 cutoff 均对应各自 RSS profile 的最小值；
9. Readiness 因变量逐行等于同一国家严格相邻年份的 (A_{it}-A_{i,t-1})；其所用 cutoff 与债务全控制方程的 (\widehat c_B^\theta) 完全一致，且不存在 readiness 自身 cutoff 搜索结果；
10. 每种判据的 (N_{low}+N_{high}=N)，五种判据的总样本量相同；
11. `areg` 与显式 LSDV 的关键估计一致；
12. 统一文档含正确的 $Y_{i,t+1}$、$Y_{it}$、theta、log-debt Doomloop、readiness kink 与竞争判据公式；
13. 所需 PNG/PDF 图形存在且非空。
14. Baseline、spread、Doomloop 的每一个正式模型都各含一行 `growth` 与 `ln_constantgdp` 系数；Y1、Y2 同样直接包含二者，Y3--Y10 则各含一行 `growth` 与一行等同于 `ln_constantgdp` 的 `Y_lag`，并禁止重复 GDP 项。

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
