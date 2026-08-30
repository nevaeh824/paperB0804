# Paper B 滞后一期债务镜像流程

## 1. 目标与交付结构

`paperB_debt_lag` 是 `paperB` 的自包含镜像，唯一实质性规格差异是 baseline 及其下游 theta 使用严格滞后一期债务状态 $b_{i,t-1}=L.debt\_gdp_{it}$。完整 Stata 源码保存在 `paperB_debt_lag/code/`；所有新结果只写入 `paperB_debt_lag/paperB_debt_lag/`，不会覆盖当期债务结果。

```text
paperB_debt_lag/
├─ run_workflow.ps1          # 滞后一期债务主流程入口
├─ run_robustness.ps1        # 两种债务时点的联合稳健性入口
├─ compare_debt_timing.py    # RSS、共同样本与 bootstrap 汇总
├─ render_figures.py         # 从已验证 CSV 生成期刊风格 PNG/PDF
├─ render_output.py          # 统一读取 CSV 并生成三份文档
├─ WORKFLOW.md               # 本流程说明
├─ code/                     # 滞后一期债务镜像的 Stata 权威源码
└─ paperB_debt_lag/          # 本流程唯一结果根目录
   ├─ paperB_results.md
   ├─ paperB_diagnostics.md
   ├─ progress.md
   ├─ baseline/
   ├─ empirical_theta/
   ├─ doomloop/
   ├─ figures/
   └─ robustness/
```

当前主流程使用的三份估计源码及其机器可读输出分别位于：

- `paperB_debt_lag/code/baseline_twfe.do` → `paperB_debt_lag/paperB_debt_lag/baseline/stata_outputs/`
- `paperB_debt_lag/code/empirical_theta.do` → `paperB_debt_lag/paperB_debt_lag/empirical_theta/stata_outputs/`
- `paperB_debt_lag/code/doomloop_no_state.do` → `paperB_debt_lag/paperB_debt_lag/doomloop/stata_outputs/`

统一入口会顺序执行三个估计阶段：baseline、empirical theta，以及一期、去状态变量的 Doomloop 主规格（其中包括 Criterion Decomposition / Competing Criterion Test）。`doomloop.do` 的含状态变量规格和 `doomloop_forward/` 的两期前瞻规格不再进入主流程。入口检查每个 Stata 日志的完成标记和 `r(#);` 错误，然后复制图形、重新渲染文档并执行整合 QA。日常维护只修改 `paperB/code/` 中当前主流程的权威源码，避免两套代码静默分叉。

统一流程不读取、也不引用项目根目录下的旧实证方案草稿。分析输入是 `data0804/invest_panel_weo.csv` 与 `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`。两者按唯一 `iso3 year` 键合并，主面板始终作为 master；不会追加仅存在于 WSDI 的行，也不会删除主面板行。若要从更上游重新构建主面板 CSV，`data0804/build_invest_panel_weo.py` 还需要基础面板 `cleaned_imf_like_panel_1995_2023.csv` 与 `WEOApr2026all.xlsx`；这两份源文件当前未纳入仓库，因此主面板数据构建层尚未完全自包含。

## 2. 软件与运行方式

默认环境：Stata 18 MP、PowerShell、Python 3.14。默认 Stata 路径是 `C:\Environment_tools\Stata18\StataMP-64.exe`。

在项目根目录运行完整估计：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB_debt_lag\run_workflow.ps1
```

指定 Stata：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB_debt_lag\run_workflow.ps1 `
  -StataExe 'D:\Stata18\StataMP-64.exe'
```

只使用现有 Stata 输出重新生成和核验统一文档：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB_debt_lag\run_workflow.ps1 -SkipStata
```

`-SkipStata` 不重新估计，但仍会读取和核验现有机器可读输出、重新绘制并复制最终图形、重新生成三份汇总文档，并执行 paperB 层面的公式和文件检查。

完整主流程一旦重新估计，会在本轮文档中暂不载入可能过期的旧 `robustness/` 结果；旧文件保留用于审计，但必须在两套主流程都刷新后重新运行 `run_robustness.ps1`，联合实验才会重新写入两份文档。若稳健性文件尚未生成，主流程仍可在干净结果目录中独立完成。

两种债务时点的四组补充实验由联合入口执行；从任一镜像调用的结果相同：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB_debt_lag\run_robustness.ps1
```

若已有 30 次 bootstrap 复制，只重算其余实验并同步结果可使用 `-SkipBootstrap`。稳健性结果同时保存于两套结果根目录的 `robustness/`。外层 30 次国家区组抽样使用配对国家抽样编号；每次重新估计上游方程、theta、cutoff 和末阶段分段方程，但为控制计算量使用 `vcov(0)`，不在每个外层复制中嵌套 50 次标准误 bootstrap。复制失败会保留状态和原因，汇总以有效复制为分母；只有覆盖缺失或某一规格没有任何有效复制时流程才停止。

## 3. 严格执行顺序

### Step 1：Baseline

1. 导入主面板 CSV，确认国家—年份键唯一；读取 WSDI CSV，确认 `iso3 year` 键唯一后合并。
2. 定义 $X_{it}=wsdi\_days_{it}\times0.01$。主面板中的源百分数、比率和 0—100 指数除以 100；金额变量不缩放。
3. 审计 `ConstantGDP` 非缺失值必须为正并保留 `ln_constantgdp=ln(ConstantGDP)` 供数据核验；T 直接使用 `ConstantGDP` 水平比，`ln_constantgdp` 不进入任何回归。
4. 在 `xtset country_id year` 后构造 `spread_lag=L.bond_spreads`，并定义严格滞后债务状态 `b_pre=L.debt_gdp`；只有严格相邻年份可提供 $s_{i,t-1}$，`b_pre` 仅由严格相邻的上一年份提供。
5. 不设置跨规格或跨阶段共同样本；每个 Baseline 回归使用该式因变量、动态滞后因变量与当前右侧变量的联合非缺失观测。
6. 逐步估计仅 X、仅 A、仅 $b_{i,t-1}$、三核心、宏观控制、第一层、第二层、A×$b_{i,t-1}$、A×X、双交互模型；十个模型均由 LSDVC 自动加入 `L.bond_spreads`，并在机器可读输出中映射为 `spread_lag`。
7. 所有模型使用 `xtlsdvc, initial(bb) bias(2) vcov(50)`：Blundell–Bond 初始化、$O((NT)^{-1})$ 偏差修正、50 次 bootstrap 标准误；国家效应由 LSDVC 吸收，并显式加入年份虚拟变量。
8. 输出模型系数、模型统计量、边际效应、Wald 检验、单位审计、缺失审计、变异分解、共线性、估计器复核，以及 `Layer2_A` 的国家/地区样本分布。

Baseline 全规格为：

```math
s_{it}=\alpha_i+\lambda_t+\rho_s s_{i,t-1}+\beta_AA_{it}+\beta_Bb_{i,t-1}+\beta_XX_{it}
+\beta_{AB}A_{it}b_{i,t-1}+\beta_{AX}A_{it}X_{it}
+\Gamma_m'W^m_{it}+\varepsilon^m_{it}.
```

控制变量统一为：

```text
宏观：growth inflation_cpi
外部：reserves tt
动态：spread_lag = L.bond_spreads
```

交互项使用对应完整交互规格实际样本的均值中心化：

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
+\widehat\beta_{AB}b_{i,t-1}
+\widehat\beta_{AX}X_{it}\right)
=-\left(\widehat\beta_A^c
+\widehat\beta_{AB}b^c_{i,t-1}
+\widehat\beta_{AX}X^c_{it}\right).
```

### Step 2：Empirical theta

1. 重新导入主面板与 WSDI 数据，按 `iso3 year` 合并并执行与 baseline 相同的单位审计。
2. 使用该全交互式自身的联合非缺失样本与 `spread_lag` 复现 baseline 全交互模型，并与 baseline 输出逐系数核对。
3. 定义 `T_it=ConstantGDP/L.ConstantGDP`，再通过 Stata 面板 `F.` 运算符取得 `T_lead=F.T_it`；跨年份缺口自动记为缺失。
4. T 指标逐步回归逐个检验 X、A、核心项、控制变量和交互项；所有规格使用 `xtlsdvc, initial(bb) bias(2) vcov(50)`，由动态模型自动加入 `L.T_lead=T_it`，并使用因变量、动态滞后项与当前右侧变量的联合非缺失样本。
5. 使用全控制 T 指标交互模型构造边际 T 收益。
6. `mA_hat` 仅在 `Spread_Interact_all` 经 `e(sample)` 与全套必需变量非缺失共同核验的实际估计支持集内构造，`TA_hat` 同理仅在 `T10_interact_full` 的实际估计支持集内构造，不向来源回归样本外外推系数；`theta_hat_A=b_pre*mA_hat+TA_hat` 仅在两个来源样本共同覆盖且 `b_pre` 非缺失时构造，保存可供 doomloop 直接使用的 panel。

T 指标直接由相邻年份固定价格 GDP 的水平比构造：

```math
T_{it}
=\frac{(ConstantGDP_{it})}{(ConstantGDP_{i,t-1})},
\qquad
T_{i,t+1}
=\frac{(ConstantGDP_{i,t+1})}{(ConstantGDP_{it})}=F.T_{it}.
```

两项均不再进行百分比缩放。T 指标全规格为：

```math
T_{i,t+1}
=\alpha_i+\lambda_t
+\gamma_AA_{it}+\gamma_XX_{it}
+\gamma_{AX}A_{it}X_{it}
+\rho_TT_{it}
+\Gamma_T'W^T_{it}+\varepsilon^T_{i,t+1}.
```

该方程的宏观控制仅为 `inflation_cpi`，明确不控制 `growth`；外部控制为 `reserves tt`。不把 `CurrentGDP`、`ConstantGDP` 或其对数另作独立解释变量；`ConstantGDP` 只通过相邻年份水平比进入 T。

T 指标交互项在全控制交互规格的实际样本内中心化：

```math
A_T^c=A-\bar A_T,\qquad X_T^c=X-\bar X_T.
```

原始尺度系数和边际 T 收益为：

```math
\widehat\gamma_A^{raw}
=\widehat\gamma_A^c-\widehat\gamma_{AX}\bar X_T,
```

```math
\widehat T^A_{it}
=\widehat\gamma_A^{raw}+\widehat\gamma_{AX}X_{it}
=\widehat\gamma_A^c+\widehat\gamma_{AX}X^c_{it}.
```

最终经验指标统一使用滞后一期债务状态 `b_pre=L.debt_gdp`：

```math
\widehat\theta^A_{it}
=b_{i,t-1}\widehat m^A_{it}+\widehat T^A_{it},
\qquad b_{i,t-1}=debt\_gdp_{i,t-1}.
```

流程保存：

```text
empirical_theta/stata_outputs/empirical_theta_panel.dta
empirical_theta/stata_outputs/empirical_theta_panel.csv
```

### Step 3：第四节 Doomloop 债务变化与 readiness 一阶差分主规格

第四节只保留一期、去状态变量规格；不再估计另行包含 $b_{i,t-1}$ 或 $A_{i,t-1}$ 状态控制的版本。

1. 读取 `empirical_theta_panel.dta`。
2. 在搜索 cutoff 前，先确认 `mA_hat` 来自 `Spread_Interact_all` 的实际样本、`TA_hat` 来自 `T10_interact_full` 的实际样本，再取两个来源样本的交集并重新计算 `b_pre*mA_hat+TA_hat`；任一来源样本不覆盖或任一组成项缺失时 theta 必须缺失。
3. 构造严格时序的 `b_outcome=F.debt_gdp-debt_gdp` 与 `A_outcome=readiness100-L.readiness100`；readiness 差分只允许严格相邻年份。
4. 所有 Doomloop 回归都显式加入 $X_{it}=wsdi\_days_{it}\times0.01$。宏观控制统一为 `growth inflation_cpi`，外部控制统一为 `reserves tt`；任何规格都不加入 `CurrentGDP`、`ConstantGDP` 或其对数。
5. 债务方程与 readiness 方程分别按当前因变量、hinge 构造量和控制变量取联合非缺失样本；核心、宏观和全控制逐步模型也各自使用当前规格样本，不要求两条方程或不同列的国家—年份观测相同。
6. 仅在债务全控制方程样本内、(\widehat\theta^A_{it}) 的 P10—P90 候选上搜索 RSS 最小 cutoff，记为 (\widehat c_B^\theta)。
7. 债务方程的核心、宏观和全控制结果均使用 (\widehat c_B^\theta)。Readiness 方程不再搜索自身 cutoff；其核心、宏观和全控制结果全部固定使用债务全控制方程得到的 (\widehat c_B^\theta)。
8. 计算点边际效应、Wald 联合检验和边际效应曲线；同时在债务全控制方程实际样本上导出 theta 分布、国家均值排序及 cutoff 绘图数据。

债务变化定义与唯一主方程为：

```math
\Delta debt_{i,t+1}=debt\_gdp_{i,t+1}-debt\_gdp_{it},
```

```math
\Delta debt_{i,t+1}
=\alpha_i+\lambda_t
+\beta_LA_{it}(c-\widehat\theta^A_{it})_+
+\beta_HA_{it}(\widehat\theta^A_{it}-c)_+
+\gamma_XX_{it}
+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.
```

Readiness 一阶差分的唯一主方程为：

```math
A_{it}-A_{i,t-1}
=\alpha_i+\lambda_t
+\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+
+\delta_HFT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_+
+\gamma_XX_{it}
+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.
```

Readiness 方程的两支只乘 `FT=interest_revenue`，不乘 $A_{it}$；该方程不含 $A_{i,t-1}$，也不以自身 RSS 选择 cutoff。债务方程不另含 $b_{i,t-1}$ 状态控制。两类方程的控制向量均包含 `growth inflation_cpi reserves tt`，不包含 GDP 控制。

### Step 4：Criterion Decomposition / Competing Criterion Test

该模块检验 kink 结果究竟来自完整经验判据 (\widehat\theta^A_{it})，还是由它的组成部分或单一基础变量驱动。令阈值判据为 (q_{it})，在第四节同一债务全控制方程中估计：

```math
\Delta debt_{i,t+1}
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
b_{i,t-1},\;
\widehat m^A_{it},\;
\widehat T^A_{it},\;
b_{i,t-1}\widehat m^A_{it}
\right\},
\qquad
\widehat\theta^A_{it}=b_{i,t-1}\widehat m^A_{it}+\widehat T^A_{it}.
```

其中 $\widehat\theta^A_{it}$ 是基准判据，另外四项分别为 `b_pre`、`mA_hat`、`TA_hat` 和 `b_pre_mA_hat`。执行规则如下：

1. 五种判据使用同一个因变量、同一组国家和年份固定效应、同一组控制变量以及国家聚类标准误；每种判据按自身构造量和该方程当前变量取联合非缺失样本，不强制跨判据固定样本。
2. 对每一种 (q_{it})，分别在其当前完整案例样本内 P10—P90 的候选值上执行完整网格搜索，选择使该样本全控制方程 RSS 最小的 (\widehat c_q)。
3. 在各自的 (\widehat c_q) 上重新估计全控制方程，保存 cutoff、两支系数及 p 值、RSS、within (R^2) 和阈值两侧样本量。
4. 理论符号定义为 (\beta_L>0) 且 (\beta_H<0)。`theoretical signs` 列报告估计结果是否同时、部分或完全不符合这组方向性预测。
5. 样本量统一定义为 (N_{low}=\#\{q_{it}\leq\widehat c_q\})、(N_{high}=\#\{q_{it}>\widehat c_q\})；同时验证 (N_{low}+N_{high}=N)。

最终比较表按以下固定列序输出：

| Criterion | cutoff | beta_L | p_L | beta_H | p_H | theoretical signs | RSS | Within R2 | N | N_low | N_high |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|---:|---:|---:|
| (\widehat\theta^A_{it}) |  |  |  |  |  |  |  |  |  |  |  |
| ($b_{i,t-1}$) |  |  |  |  |  |  |  |  |  |  |  |
| (\widehat m^A_{it}) |  |  |  |  |  |  |  |  |  |  |  |
| (\widehat T^A_{it}) |  |  |  |  |  |  |  |  |  |  |  |
| ($b_{i,t-1}\widehat m^A_{it}$) |  |  |  |  |  |  |  |  |  |  |  |

各判据的 cutoff 和 (\beta_L,\beta_H) 处于各自变量尺度，不跨行比较绝对大小。判据样本量不同时，RSS 与 within (R^2) 也不作跨行优劣排名；各行仅报告对应样本内拟合、显著性、理论符号和阈值两侧样本量。

### Step 5：边际效应与作图

本步骤生成三类图。第一类在债务全控制方程的实际样本上展示 theta：图 1a 为 country-year 直方图与核密度，图 1b 为国家/地区 theta 均值排序；两图都标出同一债务 RSS 最优 cutoff，图 1b 直接标注 Chile、Italy、Greece 与 Japan。对应文件为：

```text
figure1a_theta_distribution_cutoff.png
figure1a_theta_distribution_cutoff.pdf
figure1b_theta_country_rank_cutoff.png
figure1b_theta_country_rank_cutoff.pdf
theta_distribution_cutoff_plot_data.csv
theta_country_rank_plot_data.csv
```

第二类展示经验边际利差节约 $m^A=-\partial Spread/\partial A$ 分别随 `b_pre` 与 `wsdi_days` 变化。点位为来源回归样本的 P10、P25、P50、P75、P90；每个面板改变一个调节变量并把另一项固定在 `Interact_all` 来源样本均值。点估计与 95% 置信区间均由该 LSDVC 模型 50 次 bootstrap VCE 的边际效应逐项取负转换，不重新拟合另一模型。对应文件为：

```text
figure2_mA_by_debt_wsdi.png
figure2_mA_by_debt_wsdi.pdf
mA_by_debt_wsdi_plot_data.csv
```

第三类仅对一期去状态变量主规格绘图：债务方程与 readiness 方程统一使用债务全控制方程选择的 (\widehat c_B^\theta)。Readiness 不生成自身 cutoff 图。边际效应统一写为：

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

paperB/render_figures.py 从已验证的绘图 CSV 生成蓝色主题的期刊风格图形。PDF 为 TeX/PGFPlots 矢量输出，PNG 从同一 PDF 栅格化；单面板绘图区为正方形，图内不放标题、副标题、文字注释、图例或坐标轴变量名称，仅保留刻度轴。被移出的内容及符号含义记录在 paperB/figures/figure_notes.md。该步骤需要 Python、LuaLaTeX 和 pdftocairo。

`paperB/render_output.py` 只读取已验证的 CSV 输出，不重新估计模型。它生成：

1. `paperB_results.md`：全部公式、逐步回归表、构造系数、theta 描述、一期去状态变量主规格的点边际效应与图形，以及五种阈值判据的竞争比较表。
2. `paperB_diagnostics.md`：单位审计、样本、描述统计、缺失、within 变异、VIF、相关性、系数变化、Wald 检验、代数复核、估计器复核、各判据 cutoff/RSS 复核和解释限制。

这样正式论文结果与审计材料相互分离，同时由同一批机器可读输出生成。

## 4. 固定效应、动态估计与标准误口径

第 2 节 Baseline 与第 3 节 Empirical theta 的全部正式回归由：

```stata
xtlsdvc ..., initial(bb) bias(2) vcov(50)
```

给出。`initial(bb)` 使用 Blundell–Bond (1998) system-GMM 初始化；`bias(2)` 使用 $O((NT)^{-1})$ 偏差修正；`vcov(50)` 以 50 次 bootstrap 计算方差。LSDVC 自动加入一阶滞后因变量并吸收国家效应，流程另显式加入年份虚拟变量。代表性规格的 `bias(2)` 系数与 bootstrap SE 均与 `bias(1)` 接近且稳定；`bias(3)` 的 $O(N^{-1}T^{-2})$ 修正在当前短而不平衡的面板预检中产生爆炸性动态系数，因此不作为主规格。

第 4 节 Doomloop、cutoff 后报告回归和竞争判据继续由：

```stata
areg ..., absorb(country_id) vce(cluster country_id)
```

给出，并加入 `i.year`；`xtreg, fe` 用于取得 within/overall $R^2$，显式国家和年份虚拟变量的 LSDV 回归用于关键数值复核。这里的 `vce(cluster country_id)` 允许国家层面的异方差与国家内相关。主表标准误本身不传播 theta 生成误差或 cutoff 搜索不确定性；补充的国家区组全管线 bootstrap 用于诊断这两层不确定性。

## 5. 样本规则

- 每个动态 LSDVC 回归使用其因变量、隐含滞后因变量与当前右侧变量的联合非缺失样本；第 4 节使用因变量与当前右侧变量的联合非缺失样本。允许逐模型、跨板块样本量不同，不设置 $S_{all}$。
- 上游生成量不是新的独立原始变量：`mA_hat` 和 `TA_hat` 分别限制在估计它们的首选回归经完整案例核验的实际估计支持集内，theta 限制在两者交集内。因此下游含 theta 的回归样本必须是两个来源回归样本的子集。
- 面板 `F.` 和 `L.` 要求严格相邻年份；年份缺口不会被当作一阶 lead/lag。
- WSDI 源覆盖 1995—2018；WSDI 不匹配或 `wsdi_days` 缺失的主面板行保留，但不能进入要求 X 非缺失的具体回归样本。
- 国家—年份重复键会触发停止，不自动去重。
- cutoff 搜索始终使用对应全控制方程的当前变量样本；得到 cutoff 后，核心、宏观与全控制逐步模型分别按自身当前变量取样本。
- Competing Criterion Test 的五种判据分别使用各自构造量与债务全控制方程变量的联合非缺失样本，并逐行验证 (N_{low}+N_{high}=N)。
- `sample_spread`、`sample_tax`、`sample_theta_support`、`sample_debt_ns` 与 `sample_ready_ns` 是不同方程或构造量的审计标志，不要求逐行一致。

## 6. 自动验证与停止条件

各板块和统一入口都会检查：

1. 输入文件、Stata 日志和要求的输出文件存在；
2. Stata 日志含完成标记且不含 `r(#);` 运行错误；
3. 主面板比例变量确实等于源值除以 100，WSDI 的 `wsdi_days` 确实等于源值乘以 0.01；
4. Baseline 十个模型与 empirical-theta 的 Baseline 复核模型均含 `spread_lag=L.bond_spreads`、均不含 `ln_constantgdp` 控制，且不存在 `vulnerability100` 作为 X；T 指标模型均不含 `growth` 控制；
5. `b_pre` 与同一国家严格相邻上一年的 `debt_gdp` 逐行一致，年份有缺口时必须缺失；
6. 中心化公式与原始尺度公式逐行一致；
7. `mA_hat` 当且仅当观测属于 `Spread_Interact_all` 的实际样本，`TA_hat` 当且仅当观测属于 `T10_interact_full` 的实际样本，`theta_hat_A=b_pre*mA_hat+TA_hat` 当且仅当两个来源样本共同覆盖且 `b_pre` 可用；
8. Doomloop 主规格和五种竞争判据的 hinge 项与各自理论公式逐行一致；
9. (\widehat\theta^A_{it}) 及四种替代判据保存的 cutoff 均对应各自 RSS profile 的最小值；
10. Readiness 所用 cutoff 与债务全控制方程的 (\widehat c_B^\theta) 完全一致，且不存在 readiness 自身 cutoff 搜索结果；
11. 每种判据均满足 (N_{low}+N_{high}=N)，并单独报告实际 N；
12. 第 2—3 节所有模型均记录并核验 LSDVC、Blundell–Bond 初始化、`bias(2)`、50 次 bootstrap 和正确动态滞后项；第 4 节 `areg` 与显式 LSDV 的关键估计一致；
13. 统一文档含正确的 X、$s_{i,t-1}$、$T_{i,t+1}$、$T_{it}$、theta、去状态变量 Doomloop、readiness kink 与竞争判据公式；
14. 所需 PNG/PDF 图形存在且非空。
15. theta 图的 country-year 数据逐键等于债务全控制方程样本，国家排序与该样本的国家集合一致，图中 cutoff 与 `nostate_cutoffs.csv` 一致；$m^A$ 图的十个点及置信区间逐项等于 `Interact_all` 边际效应的正确符号转换。

任何关键映射、公式、重复键或输出完整性检查失败，流程应停止，而不是继续生成报告。

## 7. 结果更新规则

当原始数据、变量口径、控制变量、样本规则或估计器发生变化时，必须运行完整流程，不要只运行 `render_output.py`。只有在 Stata 输出未变、仅需重新排版文档时，才使用 `-SkipStata`。

不要手工改结果根目录内 `paperB_results.md`、`paperB_diagnostics.md` 或 `progress.md` 中的数字；这三份文件每次运行都会从 CSV 重建。需要改变呈现逻辑时，修改 `paperB_debt_lag/render_output.py`，然后重新运行统一入口。

## 8. 补充实验与推断限制

`run_robustness.ps1` 已完成两种债务时点的标准化 RSS、交叉 cutoff、共同 742 末阶段样本和 30 次国家区组全管线 bootstrap，并把结果写入两份自动生成的 `paperB_results.md`。共同 742 比较固定末阶段 country-year，但沿用各自主流程在自然样本上生成的 theta，未在 742 样本上重估上游方程；bootstrap 的每个复制则重新估计 baseline、tax、theta、cutoff 和最终 kink 方程。

当前证据仍是固定效应相关性证据，不构成因果识别。30 次复制只适合报告 cutoff 分布和分支符号稳定率，不足以形成精确尾部概率或正式置信区间。正式推断应把外层复制提高到至少 200 次，并进一步检查不同 trimming、候选网格和样本窗口。
