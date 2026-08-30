# Paper B 图题、注释、图例与变量名称记录

本文件记录从图内移出的标题、副标题、文字标注、图例、坐标轴变量名称及其含义。正式排版时可将这些内容作为图题、图注或正文说明使用。当前 PNG/PDF 保留数据图形、无变量名称的刻度轴、零基准线与 cutoff 参考线。

## 统一图形规范

- 白色背景、Times 系列字体，以深蓝 `#1F4E79` 为主线、中蓝 `#5B9BD5` 为辅助线、浅蓝 `#DCE6F1` 为填充色。
- 空心中蓝圆与实心深蓝方块用于无需图例也可区分的类别；线型和填充差异也保证灰度打印时可辨。
- 竖直深灰虚线表示债务方程全控制规格的 RSS 最小化 cutoff，精确值为 0.0517856469405607，文中可写为 0.0518。
- 水平深灰点划线表示零边际效应。
- 单图绘图区为正方形；横向组合图为两个正方形面板并排；纵向组合图为两个正方形面板上下排列。

## figure1a_theta_distribution_cutoff

建议图题：**Country-year distribution of empirical theta and debt-equation cutoff**

原标题与副标题：

- Country-year distribution of theta^A
- Full debt-equation sample; N=742

原图例：

- 浅蓝色直方柱：Histogram
- 深蓝色实线：Kernel density

原注释：

- Dashed line: preferred RSS-minimizing cutoff = 0.0518.

移出的坐标轴变量名称：

- Empirical adaptation index theta^A；Density

## figure1b_theta_country_rank_cutoff

建议图题：**Countries ranked by mean theta^A and debt-equation cutoff**

原标题与副标题：

- Countries ranked by mean theta^A
- Country means; G=50

原图例：

- 空心中蓝圆：Below cutoff
- 实心深蓝方块：At/above cutoff

图中文字标注：

- Chile：国家平均 theta 排名最低。
- Italy、Greece、Japan：国家平均 theta 排名最高的三个国家。

移出的坐标轴变量名称：

- Country-average theta^A；Rank

## figure2_mA_by_debt_wsdi

建议图题：**Empirical marginal spread relief m^A**

原面板标题与副标题：

- Panel A: By prior debt/GDP
- Panel A subtitle: WSDI held at its source-sample mean
- Panel B: By WSDI exposure
- Panel B subtitle: Current debt/GDP held at its source-sample mean

原注释：

- Panel A raw values (P10–P90): 0.260, 0.374, 0.513, 0.754, 1.049
- Panel B raw values (P10–P90): 0.054, 0.095, 0.152, 0.225, 0.326
- Dots: point estimates. Bars: pointwise 95% CI from the Interact_all LSDVC 50-repetition bootstrap VCE.

符号说明：

- 空心圆及连接实线：点估计。
- 带端帽的垂直误差棒：逐点 95% 置信区间。
- 水平点划线：零边际利差节约。

移出的坐标轴变量名称：

- Panel A：Current debt/GDP percentile；Marginal spread relief m^A
- Panel B：WSDI percentile (scaled ratio)

## debt_marginal_effect_no_b

建议图题：**Debt/GDP change at t+1: no separate b_it state**

原副标题：

- Full controls; pointwise 95% CI; P1-P99 theta support

原图例：

- 深蓝实线：Point estimate
- 浅蓝色带：95% CI

原注释：

- Dashed line: RSS-minimizing cutoff in the full debt equation.

参考线：

- 竖直虚线：债务方程 cutoff。
- 水平点划线：零边际效应。

移出的坐标轴变量名称：

- Empirical adaptation index theta^A
- Marginal effect on change in debt/GDP

## readiness_marginal_effect_debt_cutoff_no_lag

建议图题：**Readiness at t: no lagged A**

原副标题：

- Cutoff inherited from full debt equation; pointwise 95% CI

原图例：

- 深蓝实线：Point estimate
- 浅蓝色带：95% CI

原注释：

- Dashed line: debt-equation cutoff; readiness has no own cutoff search.

参考线：

- 竖直虚线：继承自债务方程的 cutoff；readiness 方程未单独搜索 cutoff。
- 水平点划线：零边际效应。

移出的坐标轴变量名称：

- Empirical adaptation index theta^A
- Marginal effect on readiness level

## kink_marginal_effects_no_state

该文件是上述债务边际效应图与 readiness 边际效应图的纵向组合版本。图题、副标题、图例与注释均沿用前两节记录，不在组合图内重复显示。
