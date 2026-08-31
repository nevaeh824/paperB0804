# Paper B：统一回归公式与结果表

> 数据：`data0804/invest_panel_weo.csv` 与 `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`；整合生成时间：2026-08-31 15:45（Asia/Shanghai）。
> 本文档呈现正式公式、回归表、边际效应、债务 cutoff 与竞争判据结果。数据检查和统计验证见 `paperB_diagnostics.md`。主面板源比率、百分数和 0—100 指数均先除以 100；WSDI 天数乘以 0.01 后作为 X 进入回归。

## 技术摘要

- Baseline 全交互模型中，A×b(t-1) 系数为 -0.059（p=0.024），A×X 系数为 -0.0042（p=0.887）。
- 全控制 T 指标模型的原始尺度适应能力系数为 -0.0331（p=0.155），A×X 系数为 0.1095（p=0.036）。
- 第四节唯一主规格的债务 cutoff 为 0.0593；债务两支联合检验 p=<0.001，使用同一 cutoff 的 readiness 两支联合检验 p=0.019。
- 五个替代判据按各自当前变量取完整案例，N 范围为 742–996；完整 theta 的样本内 RSS=1.066297。因样本量可能不同，RSS 不作跨判据排名。
- 第 2—3 节为含国家与年份效应的动态面板 LSDVC 相关性估计，采用 Blundell–Bond 初始化、`bias(2)` 与 50 次 bootstrap 标准误；第 4 节仍为双向固定效应并报告国家聚类标准误。theta 和 cutoff 是生成量，末阶段聚类标准误仍未覆盖完整上游估计与 cutoff 搜索不确定性。

## 1. 统一符号、控制变量与估计口径

令 $s_{it}$ 为主权利差比率，$A_{it}$ 为适应能力比率，$X_{it}=wsdi\_days_{it}\times0.01$，$b_{i,t-1}=debt\_gdp_{i,t-1}$ 为滞后一期债务状态。Baseline 第 2.2 节所有规格统一控制滞后一期债务、Growth、Inflation、Reserves 与 Terms of trade；T 指标第 3.2 节所有规格统一控制 Inflation、Reserves 与 Terms of trade，不控制 Growth 或 $\ln(ConstantGDP)$；Doomloop 的宏观控制仍为 Growth、Inflation。全部模型含国家和年份效应。第 2—3 节使用 `xtlsdvc, initial(bb) bias(2) vcov(50)`：偏差修正精度为 $O((NT)^{-1})$，标准误来自 50 次 bootstrap；动态滞后因变量由 LSDVC 自动加入。第 4 节使用按 `country_id` 聚类的双向固定效应。每个回归使用其因变量、动态滞后项与当前右侧变量的联合非缺失样本，不再设置跨模型或跨阶段固定样本。生成量不向来源回归样本外外推：$\widehat m^A$ 限于 Spread_Interact_all 的实际样本，$\widehat T^A$ 限于 T10_interact_full 的实际样本，theta 限于两个来源样本的交集。`bias(2)` 在代表性规格中与 `bias(1)` 数值接近且稳定；`bias(3)` 曾在当前短而不平衡的面板上产生爆炸性动态系数，因此不作为主规格。

## 2. Baseline：主权利差回归

### 2.1 回归公式

$$s_{it}=\alpha_i+\lambda_t+\rho_s s_{i,t-1}+\beta_AA_{it}+\beta_Bb_{i,t-1}+\beta_XX_{it}+\beta_{AB}A_{it}b_{i,t-1}+\beta_{AX}A_{it}X_{it}+\Gamma_m'W^m_{it}+\varepsilon^m_{it}.$$

交互回归在对应完整交互式的实际样本内中心化。原始尺度适应能力斜率和边际利差节约为

$$\widehat\beta_A^{raw}=\widehat\beta_A^c-\widehat\beta_{AB}\bar b_s-\widehat\beta_{AX}\bar X_s,$$

$$\widehat m^A_{it}=-\left(\widehat\beta_A^{raw}+\widehat\beta_{AB}b_{i,t-1}+\widehat\beta_{AX}X_{it}\right).$$

### 2.2 逐步回归表

系数下方括号为基于 50 次 bootstrap 标准误的 z 值；`***`、`**`、`*` 分别表示 1%、5%、10% 显著性。

**Panel A：核心变量与控制变量**

| 变量/统计量 | (A_b_only) 控制基准 | (A_X_only) +X | (A_A_only) +A | (Layer2_A) +X+A |
| --- | ---: | ---: | ---: | ---: |
| WSDI 天数×0.01 $X_{it}$ | — | 0.0098*<br>(1.67) | — | 0.0092<br>(1.597) |
| 适应能力 $A_{it}$ | — | — | -0.0316**<br>(-2.301) | -0.0269*<br>(-1.776) |
| 滞后一期债务/GDP $b_{i,t-1}=debt\_gdp_{i,t-1}$ | 0.0022<br>(0.587) | 0.0042<br>(0.916) | 0.0032<br>(0.937) | 0.0046<br>(1.043) |
| 滞后主权利差 $s_{i,t-1}$ | 0.7048***<br>(26.919) | 0.6793***<br>(18.39) | 0.6877***<br>(23.901) | 0.6659***<br>(17.886) |
| Growth | -0.1172***<br>(-8.165) | -0.1622***<br>(-8.338) | -0.1162***<br>(-7.998) | -0.1597***<br>(-8.193) |
| Inflation | 0.1122***<br>(8.055) | 0.1468***<br>(5.925) | 0.1145***<br>(10.24) | 0.15***<br>(6.149) |
| Reserves | -0.005<br>(-0.999) | -0.0089<br>(-1.29) | -0.005<br>(-0.865) | -0.0081<br>(-1.189) |
| Terms of trade | 0.004<br>(1.024) | 0.0037<br>(0.765) | 0.004<br>(1.044) | 0.0038<br>(0.819) |
| 宏观控制 | 是 | 是 | 是 | 是 |
| 外部控制 | 是 | 是 | 是 | 是 |
| 国家固定效应 | 是 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 2 | 2 | 2 | 2 |
| Bootstrap 次数 | 50 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads |
| 国家数 | 61 | 50 | 60 | 50 |
| 年份数 | 25 | 20 | 25 | 20 |
| 样本量 | 1,148 | 742 | 1,130 | 742 |

**Panel B：交互模型**

| 变量/统计量 | (Interact_AB) A×b(t-1) | (Interact_AX) A×X | (Interact_all) 双交互 |
| --- | ---: | ---: | ---: |
| $A^c_{it}$ | -0.034**<br>(-2.126) | -0.0258*<br>(-1.688) | -0.0335**<br>(-2.047) |
| $X^c_{it}$ | 0.0092<br>(1.604) | 0.0089<br>(1.553) | 0.0091<br>(1.59) |
| $b^c_{i,t-1}$ | 0.007<br>(1.552) | 0.0048<br>(1.088) | 0.007<br>(1.571) |
| $A^c_{it}\times b^c_{i,t-1}$ | -0.0599**<br>(-2.394) | — | -0.059**<br>(-2.263) |
| $A^c_{it}\times X^c_{it}$ | — | -0.0166<br>(-0.586) | -0.0042<br>(-0.142) |
| 滞后主权利差 $s_{i,t-1}$ | 0.6392***<br>(16.812) | 0.6642***<br>(17.81) | 0.6385***<br>(16.715) |
| Growth | -0.157***<br>(-7.921) | -0.1596***<br>(-8.178) | -0.157***<br>(-7.897) |
| Inflation | 0.1567***<br>(6.229) | 0.1502***<br>(6.151) | 0.1568***<br>(6.211) |
| Reserves | -0.0089<br>(-1.3) | -0.008<br>(-1.167) | -0.0088<br>(-1.288) |
| Terms of trade | 0.0025<br>(0.544) | 0.0038<br>(0.817) | 0.0025<br>(0.543) |
| 宏观控制 | 是 | 是 | 是 |
| 外部控制 | 是 | 是 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 2 | 2 | 2 |
| Bootstrap 次数 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.bond_spreads | L.bond_spreads | L.bond_spreads |
| 国家数 | 50 | 50 | 50 |
| 年份数 | 20 | 20 | 20 |
| 样本量 | 742 | 742 | 742 |

### 2.3 构造用原始尺度系数

| 参数 | 估计值 | Bootstrap SE | z | p | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| beta_A_raw | 0.0024 | 0.0169 | 0.144 | 0.886 | [-0.0307, 0.0356] |
| beta_AB | -0.059 | 0.0261 | -2.263 | 0.024 | [-0.1102, -0.0079] |
| beta_AX | -0.0042 | 0.0299 | -0.142 | 0.887 | [-0.0628, 0.0543] |

<details><summary>展开：baseline 点边际效应</summary>

| 模型 | 点 | 调节变量 | 边际效应 | SE | p | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Interact_AB | P10 | 0.26 | -0.0138 | 0.0146 | 0.344 | [-0.0424, 0.0148] |
| Interact_AB | P25 | 0.3741 | -0.0206 | 0.0145 | 0.156 | [-0.0491, 0.0079] |
| Interact_AB | P50 | 0.5128 | -0.0289 | 0.0152 | 0.057 | [-0.0587, 0.0009] |
| Interact_AB | P75 | 0.7541 | -0.0434 | 0.018 | 0.016 | [-0.0787, -0.0081] |
| Interact_AB | P90 | 1.0494 | -0.0611 | 0.0232 | 0.008 | [-0.1065, -0.0157] |
| Interact_AB | Mean_minus_1SD | 0.255 | -0.0135 | 0.0146 | 0.355 | [-0.0421, 0.0151] |
| Interact_AB | Mean | 0.5967 | -0.034 | 0.016 | 0.034 | [-0.0653, -0.0026] |
| Interact_AB | Mean_plus_1SD | 0.9385 | -0.0544 | 0.0211 | 0.010 | [-0.0957, -0.0132] |
| Interact_AX | P10 | 0.0544 | -0.0239 | 0.0161 | 0.137 | [-0.0554, 0.0076] |
| Interact_AX | P25 | 0.0951 | -0.0245 | 0.0157 | 0.118 | [-0.0554, 0.0063] |
| Interact_AX | P50 | 0.1523 | -0.0255 | 0.0154 | 0.097 | [-0.0556, 0.0046] |
| Interact_AX | P75 | 0.2251 | -0.0267 | 0.0152 | 0.078 | [-0.0564, 0.003] |
| Interact_AX | P90 | 0.3256 | -0.0284 | 0.0153 | 0.064 | [-0.0584, 0.0017] |
| Interact_AX | Mean_minus_1SD | 0.0658 | -0.0241 | 0.016 | 0.132 | [-0.0553, 0.0072] |
| Interact_AX | Mean | 0.1709 | -0.0258 | 0.0153 | 0.091 | [-0.0558, 0.0042] |
| Interact_AX | Mean_plus_1SD | 0.2761 | -0.0275 | 0.0152 | 0.070 | [-0.0573, 0.0022] |
| Interact_all | P10 | 0.26 | -0.0136 | 0.0146 | 0.351 | [-0.0423, 0.015] |
| Interact_all | P25 | 0.3741 | -0.0204 | 0.0147 | 0.165 | [-0.0491, 0.0084] |
| Interact_all | P50 | 0.5128 | -0.0286 | 0.0155 | 0.065 | [-0.059, 0.0018] |
| Interact_all | P75 | 0.7541 | -0.0428 | 0.0186 | 0.021 | [-0.0793, -0.0063] |
| Interact_all | P90 | 1.0494 | -0.0603 | 0.0242 | 0.013 | [-0.1077, -0.0129] |
| Interact_all | Mean_minus_1SD | 0.255 | -0.0133 | 0.0146 | 0.362 | [-0.042, 0.0153] |
| Interact_all | Mean | 0.5967 | -0.0335 | 0.0164 | 0.041 | [-0.0656, -0.0014] |
| Interact_all | Mean_plus_1SD | 0.9385 | -0.0537 | 0.0219 | 0.014 | [-0.0967, -0.0107] |
| Interact_all | P10 | 0.0544 | -0.033 | 0.0175 | 0.060 | [-0.0674, 0.0013] |
| Interact_all | P25 | 0.0951 | -0.0332 | 0.0171 | 0.052 | [-0.0666, 0.0002] |
| Interact_all | P50 | 0.1523 | -0.0334 | 0.0165 | 0.043 | [-0.0658, -0.0011] |
| Interact_all | P75 | 0.2251 | -0.0338 | 0.0161 | 0.036 | [-0.0653, -0.0022] |
| Interact_all | P90 | 0.3256 | -0.0342 | 0.0159 | 0.032 | [-0.0654, -0.003] |
| Interact_all | Mean_minus_1SD | 0.0658 | -0.0331 | 0.0174 | 0.057 | [-0.0672, 0.001] |
| Interact_all | Mean | 0.1709 | -0.0335 | 0.0164 | 0.041 | [-0.0656, -0.0014] |
| Interact_all | Mean_plus_1SD | 0.2761 | -0.034 | 0.0159 | 0.033 | [-0.0652, -0.0027] |

</details>

## 3. Empirical theta：边际 T 收益与经验指标

### 3.1 T 指标回归公式与时序

$$T_{it}=\frac{(ConstantGDP_{it})}{(ConstantGDP_{i,t-1})},\qquad T_{i,t+1}=\frac{(ConstantGDP_{i,t+1})}{(ConstantGDP_{it})}=F.T_{it}.$$

$$T_{i,t+1}=\alpha_i+\lambda_t+\gamma_AA_{it}+\gamma_XX_{it}+\gamma_{AX}A_{it}X_{it}+\rho_TT_{it}+\Gamma_T'W^T_{it}+\varepsilon^T_{i,t+1}.$$

T 指标交互模型在全控制交互式的实际样本内中心化，故 $\widehat\gamma_A^{raw}=\widehat\gamma_A^c-\widehat\gamma_{AX}\bar X_T$，且

$$\widehat T^A_{it}=\widehat\gamma_A^{raw}+\widehat\gamma_{AX}X_{it}=\widehat\gamma_A^c+\widehat\gamma_{AX}X^c_{it}.$$

### 3.2 T 指标逐步回归表

系数下方括号为基于 50 次 bootstrap 标准误的 z 值。所有规格均由 LSDVC 自动加入 $L.T_{i,t+1}=T_{it}$。

| 变量/统计量 | (T3_persistence) 控制基准 | (T1_X_only) +X | (T2_A_only) +A | (T7_layer2_A) +X+A | (T10_interact_full) +A×X |
| --- | ---: | ---: | ---: | ---: | ---: |
| WSDI 天数×0.01 $X_{it}$ | — | -0.0025<br>(-0.264) | — | -0.0029<br>(-0.311) | — |
| 适应能力 $A_{it}$ | — | — | -0.0104<br>(-0.487) | -0.0082<br>(-0.34) | — |
| $A^c_{it}$ | — | — | — | — | -0.0149<br>(-0.645) |
| $X^c_{it}$ | — | — | — | — | -0.0005<br>(-0.05) |
| $A^c_{it}\times X^c_{it}$ | — | — | — | — | 0.1095**<br>(2.098) |
| $T_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$ | 0.3263***<br>(14.506) | 0.3427***<br>(10.549) | 0.33***<br>(13.175) | 0.3425***<br>(10.5) | 0.3401***<br>(10.418) |
| Inflation | -0.0222*<br>(-1.78) | -0.0197<br>(-1.374) | -0.0181<br>(-1.347) | -0.0185<br>(-1.279) | -0.0186<br>(-1.291) |
| Reserves | 0.0208***<br>(2.617) | 0.0245**<br>(2.51) | 0.0292***<br>(2.72) | 0.0253***<br>(2.582) | 0.0252**<br>(2.572) |
| Terms of trade | -0.003<br>(-0.859) | -0.0077<br>(-1.52) | -0.0031<br>(-0.882) | -0.0081<br>(-1.535) | -0.0086<br>(-1.642) |
| 宏观控制 | 是 | 是 | 是 | 是 | 是 |
| 外部控制 | 是 | 是 | 是 | 是 | 是 |
| 国家固定效应 | 是 | 是 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 2 | 2 | 2 | 2 | 2 |
| Bootstrap 次数 | 50 | 50 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.T_lead | L.T_lead | L.T_lead | L.T_lead | L.T_lead |
| 国家数 | 61 | 52 | 60 | 52 | 52 |
| 年份数 | 27 | 23 | 27 | 23 | 23 |
| 样本量 | 1,487 | 1,024 | 1,461 | 1,024 | 1,024 |

### 3.3 边际 T 收益与 theta 构造

| 参数 | 估计值 | Bootstrap SE | z | p | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| gamma_A_raw | -0.0331 | 0.0233 | -1.423 | 0.155 | [-0.0787, 0.0125] |
| gamma_AX | 0.1095 | 0.0522 | 2.098 | 0.036 | [0.0072, 0.2118] |

$$\widehat\theta^A_{it}=b_{i,t-1}\widehat m^A_{it}+\widehat T^A_{it},\qquad b_{i,t-1}=debt\_gdp_{i,t-1}.$$

构造支持集严格继承来源回归：`mA_hat` 仅在 Spread_Interact_all 的 `e(sample)` 内生成，`TA_hat` 仅在 T10_interact_full 的 `e(sample)` 内生成，theta 仅在二者共同覆盖时生成。

| 构造量 | 样本 | N | 均值 | SD | P10 | P50 | P90 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mA_hat | theta_support | 742 | 0.0335 | 0.0202 | 0.0134 | 0.0287 | 0.0602 |
| spread_saving_component | theta_support | 742 | 0.0269 | 0.0353 | 0.0035 | 0.0148 | 0.0632 |
| TA_hat | theta_support | 742 | -0.0144 | 0.0115 | -0.0272 | -0.0164 | 0.0025 |
| theta_hat_A | theta_support | 742 | 0.0125 | 0.0381 | -0.02 | 0.003 | 0.0523 |
| theta_hat_A | all_constructible | 742 | 0.0125 | 0.0381 | -0.02 | 0.003 | 0.0523 |

**图 1a：theta 分布与债务方程 cutoff**

![theta 分布与 cutoff](figures/figure1a_theta_distribution_cutoff.png)

[PNG](figures/figure1a_theta_distribution_cutoff.png) · [PDF](figures/figure1a_theta_distribution_cutoff.pdf) · 绘图数据：`doomloop/stata_outputs/theta_distribution_cutoff_plot_data.csv`

**图 1b：国家平均 theta 排序与债务方程 cutoff**

![国家平均 theta 排序与 cutoff](figures/figure1b_theta_country_rank_cutoff.png)

[PNG](figures/figure1b_theta_country_rank_cutoff.png) · [PDF](figures/figure1b_theta_country_rank_cutoff.pdf) · 绘图数据：`doomloop/stata_outputs/theta_country_rank_plot_data.csv`

**图 2：经验边际利差节约 $m^A$ 随债务与 WSDI 的变化**

图中 $m^A=-\partial Spread/\partial A$ 来自 `Interact_all`；每个面板分别改变一个调节变量的 P10、P25、P50、P75、P90，并将另一调节变量固定在该来源样本均值。误差棒为 LSDVC 50 次 bootstrap VCE 的点估计 95% 置信区间。

![mA 随债务与 WSDI 的变化](figures/figure2_mA_by_debt_wsdi.png)

[PNG](figures/figure2_mA_by_debt_wsdi.png) · [PDF](figures/figure2_mA_by_debt_wsdi.pdf) · 绘图数据：`doomloop/stata_outputs/mA_by_debt_wsdi_plot_data.csv`

## 4. Doomloop：一期去状态变量主规格

### 4.1 方程与 cutoff 口径

$$\Delta debt_{i,t+1}=debt\_gdp_{i,t+1}-debt\_gdp_{it}.$$

$$\Delta debt_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-\widehat\theta^A_{it})_++\beta_HA_{it}(\widehat\theta^A_{it}-c)_++\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.$$

$$A_{it}-A_{i,t-1}=\alpha_i+\lambda_t+\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_++\delta_HFT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_++\gamma_XX_{it}+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.$$

债务方程不另加入 $b_{i,t-1}$ 状态项，readiness 方程不加入 $A_{i,t-1}$。$\widehat c_B^\theta$ 仅由债务全控制方程在 theta 的全部可估观测值中按最小 RSS 选择；不设置 P10—P90 搜索范围或10%最小分支约束，只排除会使一侧 hinge 恒为零的样本最小值和最大值。readiness 不进行独立 cutoff 搜索。两类方程均显式控制 $X_{it}$，并依次加入 Growth、Inflation、Reserves 与 Terms of trade。

### 4.2 债务变化方程

| 变量/统计量 | (DN1_core) 核心项 | (DN2_macro) +宏观 | (DN3_full) +全控制 |
| --- | ---: | ---: | ---: |
| $A_{it}(c-\widehat\theta^A_{it})_+$ | 2.686***<br>(4.587) | 2.5327***<br>(4.317) | 2.5277***<br>(4.547) |
| $A_{it}(\widehat\theta^A_{it}-c)_+$ | -0.7368***<br>(-5.383) | -0.8546***<br>(-6.429) | -0.8315***<br>(-5.945) |
| WSDI 天数×0.01 $X_{it}$ | 0.1784***<br>(3.818) | 0.1692***<br>(3.715) | 0.1706***<br>(3.739) |
| Growth | — | -0.5073***<br>(-5.708) | -0.5102***<br>(-5.994) |
| Inflation | — | -0.1445<br>(-0.921) | -0.1183<br>(-0.755) |
| Reserves | — | — | -0.0491<br>(-0.92) |
| Terms of trade | — | — | 0.0297<br>(0.808) |
| 宏观控制 | 否 | 是 | 是 |
| 外部控制 | 否 | 否 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 聚类变量 | country_id | country_id | country_id |
| 聚类数 | 50 | 50 | 50 |
| 国家数 | 50 | 50 | 50 |
| 年份数 | 20 | 20 | 20 |
| 样本量 | 742 | 742 | 742 |
| Within $R^2$ | 0.337 | 0.38 | 0.386 |
| Overall $R^2$ | 0.061 | 0.091 | 0.101 |

### 4.3 Readiness 一阶差分方程：固定使用债务 cutoff

| 变量/统计量 | (RDN1_core) 核心项 | (RDN2_macro) +宏观 | (RDN3_full) +全控制 |
| --- | ---: | ---: | ---: |
| $FT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+$ | -1.2869**<br>(-2.537) | -1.2499**<br>(-2.441) | -1.2617**<br>(-2.467) |
| $FT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_+$ | 0.5172<br>(1.523) | 0.8061**<br>(2.169) | 0.7805**<br>(2.134) |
| WSDI 天数×0.01 $X_{it}$ | 0.0016<br>(0.213) | 0.002<br>(0.259) | 0.002<br>(0.258) |
| Growth | — | 0.0715***<br>(2.692) | 0.0719**<br>(2.669) |
| Inflation | — | -0.0566<br>(-1.511) | -0.0592<br>(-1.628) |
| Reserves | — | — | 0.0024<br>(0.303) |
| Terms of trade | — | — | -0.0045<br>(-0.607) |
| 宏观控制 | 否 | 是 | 是 |
| 外部控制 | 否 | 否 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 聚类变量 | country_id | country_id | country_id |
| 聚类数 | 50 | 50 | 50 |
| 国家数 | 50 | 50 | 50 |
| 年份数 | 20 | 20 | 20 |
| 样本量 | 742 | 742 | 742 |
| Within $R^2$ | 0.202 | 0.212 | 0.212 |
| Overall $R^2$ | 0.191 | 0.197 | 0.197 |

### 4.4 全控制结果、边际效应与图形

| 结果方程 | cutoff 来源 | cutoff | RSS | 候选数 | N_low | N_high | 低支系数 | p_L | 高支系数 | p_H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 债务变化 | 债务全控制 RSS | 0.0593 | 1.066297 | 740 | 687 | 55 | 2.5277 | <0.001 | -0.8315 | <0.001 |
| Readiness | 继承债务 cutoff | 0.0593 | 0.197045 | — | — | — | -1.2617 | 0.017 | 0.7805 | 0.038 |

cutoff 搜索不设最小分支规模；若最优点只由极少数观测识别，相关分支系数可能非常大且不稳定，必须结合 N_low、N_high、RSS profile 与全管线 bootstrap 解读，不能仅依据条件 p 值作结构性解释。

点边际效应按 $m(\theta;c)=a(c-\theta)_++b(\theta-c)_+$ 计算；在 cutoff 处定义为 0。

<details><summary>展开：主规格点边际效应</summary>

| 方程 | 点 | $\theta$ | 边际效应 | 国家聚类 SE | p 值 | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 债务变化 | P10 | -0.02 | 0.2005 | 0.0441 | <0.001 | [0.1119, 0.2891] |
| 债务变化 | P25 | -0.0107 | 0.1769 | 0.0389 | <0.001 | [0.0987, 0.2551] |
| 债务变化 | P50 | 0.003 | 0.1424 | 0.0313 | <0.001 | [0.0795, 0.2053] |
| 债务变化 | Mean | 0.0125 | 0.1182 | 0.026 | <0.001 | [0.066, 0.1705] |
| 债务变化 | Cutoff | 0.0593 | 0 | 0 | — | [0, 0] |
| 债务变化 | P75 | 0.0217 | 0.095 | 0.0209 | <0.001 | [0.053, 0.137] |
| 债务变化 | P90 | 0.0523 | 0.0176 | 0.0039 | <0.001 | [0.0098, 0.0254] |
| Readiness（债务 cutoff） | P10 | -0.02 | -0.1001 | 0.0406 | 0.017 | [-0.1816, -0.0186] |
| Readiness（债务 cutoff） | P25 | -0.0107 | -0.0883 | 0.0358 | 0.017 | [-0.1602, -0.0164] |
| Readiness（债务 cutoff） | P50 | 0.003 | -0.0711 | 0.0288 | 0.017 | [-0.129, -0.0132] |
| Readiness（债务 cutoff） | Mean | 0.0125 | -0.059 | 0.0239 | 0.017 | [-0.1071, -0.0109] |
| Readiness（债务 cutoff） | Cutoff | 0.0593 | 0 | 0 | — | [0, 0] |
| Readiness（债务 cutoff） | P75 | 0.0217 | -0.0474 | 0.0192 | 0.017 | [-0.0861, -0.0088] |
| Readiness（债务 cutoff） | P90 | 0.0523 | -0.0088 | 0.0036 | 0.017 | [-0.0159, -0.0016] |

</details>

| 债务变化 | Readiness（债务 cutoff） |
| --- | --- |
| ![债务变化边际效应](figures/debt_marginal_effect_no_b.png) | ![Readiness 边际效应](figures/readiness_marginal_effect_debt_cutoff_no_lag.png) |

合并版：[PNG](figures/kink_marginal_effects_no_state.png) · [PDF](figures/kink_marginal_effects_no_state.pdf)

## 5. Criterion Decomposition / Competing Criterion Test

令阈值判据为 $q_{it}$，每个判据均在其因变量、分支构造量和全套控制变量共同非缺失的样本上估计

$$\Delta debt_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-q_{it})_++\beta_HA_{it}(q_{it}-c)_++\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1},$$

$$q_{it}\in\left\{\widehat\theta^A_{it},\ b_{i,t-1},\ \widehat m^A_{it},\ \widehat T^A_{it},\ b_{i,t-1}\widehat m^A_{it}\right\}.$$

每种判据分别在自身全部可估观测值上搜索最小 RSS cutoff；不设置分位数范围或最小分支比例，仅排除使一侧 hinge 恒为零的两个端点。理论方向为 $\beta_L>0$、$\beta_H<0$；$N_{low}=\#\{q_{it}\le c\}$，$N_{high}=\#\{q_{it}>c\}$。

| Criterion | cutoff | beta_L | p_L | beta_H | p_H | theoretical signs | RSS | Within R2 | N | N_low | N_high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | 0.0593 | 2.5277 | <0.001 | -0.8315 | <0.001 | Match (+,-) | 1.066297 | 0.386 | 742 | 687 | 55 |
| $b_{i,t-1}$ | 0.1243 | -0.5301 | 0.092 | -0.1977 | <0.001 | Partial (-,-) | 1.3551 | 0.365 | 984 | 35 | 949 |
| $\widehat m^A_{it}$ | 0.0058 | -15.6227 | 0.001 | -3.8048 | <0.001 | Partial (-,-) | 1.036181 | 0.4033 | 742 | 23 | 719 |
| $\widehat T^A_{it}$ | -0.0326 | -415.2532 | <0.001 | -1.4537 | 0.147 | Partial (-,-) | 1.682063 | 0.2591 | 996 | 11 | 985 |
| $b_{i,t-1}\widehat m^A_{it}$ | 0.0795 | 2.5339 | <0.001 | -0.6373 | <0.001 | Match (+,-) | 1.070468 | 0.3836 | 742 | 701 | 41 |

各判据的 cutoff、分支系数和 RSS 均处于自身尺度与自身完整案例样本中。由于 N 可能不同，cutoff、系数和 RSS 不作跨行绝对排名；表格用于报告各判据内部的拟合、显著性、理论方向与阈值两侧覆盖。

## 6. 债务时点稳健性与全管线诊断

### 6.1 标准化 RSS profile 与近最优 cutoff 区间

标准化横轴为 $(c-median(\theta))/sd(\theta)$；纵轴为 $100\times(RSS/RSS_{min}-1)$。近最优区间保留超额 RSS 不超过 0.1%、0.5% 或 1.0% 的候选 cutoff。

| 规格 | 超额 RSS 阈值 | 最优 cutoff | 近优 cutoff 区间 | 标准化区间 | 候选数 | 候选占比 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 当期债务 | 0.1% | -0.0325 | [-0.0325, -0.0299] | [-0.677, -0.627] | 12/742 | 1.6% |
| 当期债务 | 0.5% | -0.0325 | [-0.0325, 0.0588] | [-0.677, 1.077] | 448/742 | 60.4% |
| 当期债务 | 1% | -0.0325 | [-0.0325, 0.0888] | [-0.677, 1.653] | 702/742 | 94.6% |
| 滞后一期债务 | 0.1% | 0.0593 | [0.0559, 0.0639] | [1.388, 1.597] | 15/740 | 2.0% |
| 滞后一期债务 | 0.5% | 0.0593 | [0.048, 0.0721] | [1.183, 1.814] | 42/740 | 5.7% |
| 滞后一期债务 | 1% | 0.0593 | [0.0404, 0.0796] | [0.981, 2.01] | 77/740 | 10.4% |

![标准化 RSS profiles](figures/figure3_standardized_rss_profiles.png)

深色实线为当期债务规格，浅蓝虚线为滞后一期债务规格；水平参考线对应 0.1%、0.5% 与 1.0% 超额 RSS。[PNG](figures/figure3_standardized_rss_profiles.png) · [PDF](figures/figure3_standardized_rss_profiles.pdf) · 数据：`robustness/standardized_rss_profile.csv`。

### 6.2 固定旧/new cutoff 的交叉敏感性

| theta 规格 | 固定 cutoff 来源 | cutoff | beta_L | p_L | beta_H | p_H | RSS | N | N_low | N_high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 当期债务 | 当期债务 | -0.0325 | -4143.3496 | 0.002 | -0.9392 | <0.001 | 1.14108 | 744 | 1 | 743 |
| 当期债务 | 滞后一期债务 | 0.0593 | 1.2742 | <0.001 | -0.6429 | <0.001 | 1.146832 | 744 | 658 | 86 |
| 滞后一期债务 | 当期债务 | -0.0325 | 0 | — | -1.7211 | <0.001 | 1.081058 | 742 | 0 | 742 |
| 滞后一期债务 | 滞后一期债务 | 0.0593 | 2.5277 | <0.001 | -0.8315 | <0.001 | 1.066297 | 742 | 687 | 55 |

交叉固定 cutoff 表明低支符号对阈值位置高度敏感：当期 theta 固定在滞后规格 cutoff 时 beta_L 转为显著为正；滞后 theta 固定在当期 cutoff 时 beta_L 仍为正但不显著。高支在四种组合中均为负。

### 6.3 共同 742 个观测的规格比较

| 规格 | 重选 cutoff | beta_L | p_L | beta_H | p_H | RSS | N | N_low | N_high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 当期债务 | -0.0325 | -4031.7634 | 0.002 | -0.9465 | <0.001 | 1.140116 | 742 | 1 | 741 |
| 滞后一期债务 | 0.0593 | 2.5277 | <0.001 | -0.8315 | <0.001 | 1.066297 | 742 | 687 | 55 |

共同 742 比较只固定末阶段债务方程的 country-year 样本，并沿用两套主流程各自在自然样本上生成的 theta；它未在共同 742 样本上重估上游 baseline 与 T 方程。因此该结果排除了末阶段两条额外观测的直接构成效应，但不能排除它们通过上游系数与 theta 的间接影响。

### 6.4 30 次配对国家块全管线 bootstrap

| 规格 | 有效/请求 | cutoff 最小 | P25 | 中位数 | P75 | 最大 | P(beta_L>0) | P(beta_H<0) | P(两支理论符号) | 较小分支中位占比 | P(较小分支<10%) | P(较小分支≤5个观测) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 当期债务 | 30/30 | -0.0867 | -0.0297 | 0.0105 | 0.0575 | 0.1866 | 53.3% | 100.0% | 53.3% | 11.6% | 43.3% | 20.0% |
| 滞后一期债务 | 30/30 | -0.0793 | -0.0038 | 0.0309 | 0.093 | 0.2052 | 80.0% | 93.3% | 76.7% | 8.8% | 60.0% | 10.0% |

两种规格使用 seed=20260830 的同一国家抽样序列；有效/请求复制为 当期债务 30/30、滞后一期债务 30/30，合计失败 0 个规格复制。每次重新估计两条 theta 来源方程、theta、cutoff 与最终债务方程，但不在外层抽样内再嵌套 50 次 LSDVC VCE。搜索不设分位数范围或最小分支约束；较小分支频率直接报告，以揭示极端 cutoff 对系数稳定性的影响。cutoff 分布很宽，说明单一点 cutoff 的定位不稳定；本实验仅是小规模稳定性诊断，不是正式置信区间。

## 7. 结果解释边界

这些结果是相关性估计，不应表述为因果效应。第 2—3 节的 50 次 LSDVC bootstrap 标准误只对应各上游方程；第 4 节的国家聚类标准误处理国家内相关。新增 30 次国家块外层 bootstrap 传播了 baseline、T、theta、cutoff 与最终方程的点估计不确定性，但重复次数较少且未在每次抽样内嵌套标准误 bootstrap，因此只作为稳定性诊断。竞争判据使用各自完整案例样本，既不是同样本 RSS 比较，也不是非嵌套模型的正式显著性检验。
