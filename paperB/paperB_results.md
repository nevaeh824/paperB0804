# Paper B：统一回归公式与结果表

> 数据：`data0804/invest_panel_weo.csv` 与 `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`；整合生成时间：2026-08-18 17:34（Asia/Shanghai）。
> 本文档呈现正式公式、回归表、边际效应、债务 cutoff 与竞争判据结果。数据检查和统计验证见 `paperB_diagnostics.md`。主面板源比率、百分数和 0—100 指数均先除以 100；WSDI 天数乘以 0.01 后作为 X 进入回归。

## 技术摘要

- Baseline 全交互模型中，A×b-pre 系数为 -0.0593（p=0.023），A×X 系数为 -0.0043（p=0.885）。
- 全控制 T 指标模型的原始尺度适应能力系数为 -0.0332（p=0.153），A×X 系数为 0.1095（p=0.036）。
- 第四节唯一主规格的债务 cutoff 为 0.0518；债务两支联合检验 p=<0.001，使用同一 cutoff 的 readiness 两支联合检验 p=0.016。
- 五个替代判据按各自当前变量取完整案例，N 范围为 742–996；完整 theta 的样本内 RSS=1.068947。因样本量可能不同，RSS 不作跨判据排名。
- 第 2—3 节为含国家与年份效应的动态面板 LSDVC 相关性估计，采用 Blundell–Bond 初始化、`bias(1)` 与 50 次 bootstrap 标准误；第 4 节仍为双向固定效应并报告国家聚类标准误。theta 和 cutoff 是生成量，末阶段聚类标准误仍未覆盖完整上游估计与 cutoff 搜索不确定性。

## 1. 统一符号、控制变量与估计口径

令 $s_{it}$ 为主权利差比率，$A_{it}$ 为适应能力比率，$X_{it}=wsdi\_days_{it}\times0.01$，$b^{pre}_{it}=b_{i,t-1}=debt\_gdp_{i,t-1}$。Baseline 的宏观控制为 Growth、Inflation，不控制 $\ln(ConstantGDP)$；T 指标方程的宏观控制仅为 Inflation，不控制 Growth；Doomloop 的宏观控制仍为 Growth、Inflation。外部控制为 Reserves、Terms of trade。全部模型含国家和年份效应。第 2—3 节使用 `xtlsdvc, initial(bb) bias(1) vcov(50)`：一阶偏差修正精度为 $O(T^{-1})$，标准误来自 50 次 bootstrap；动态滞后因变量由 LSDVC 自动加入。第 4 节使用按 `country_id` 聚类的双向固定效应。每个回归使用其因变量、动态滞后项与当前右侧变量的联合非缺失样本，不再设置跨模型或跨阶段固定样本。生成量不向来源回归样本外外推：$\widehat m^A$ 限于 Spread_Interact_all 的实际样本，$\widehat T^A$ 限于 T10_interact_full 的实际样本，theta 限于两个来源样本的交集。三阶修正曾在当前短而不平衡的面板上产生爆炸性动态系数，因此主流程采用数值更稳定的 `bias(1)`。

## 2. Baseline：主权利差回归

### 2.1 回归公式

$$s_{it}=\alpha_i+\lambda_t+\rho_s s_{i,t-1}+\beta_AA_{it}+\beta_Bb^{pre}_{it}+\beta_XX_{it}+\beta_{AB}A_{it}b^{pre}_{it}+\beta_{AX}A_{it}X_{it}+\Gamma_m'W^m_{it}+\varepsilon^m_{it}.$$

交互回归在对应完整交互式的实际样本内中心化。原始尺度适应能力斜率和边际利差节约为

$$\widehat\beta_A^{raw}=\widehat\beta_A^c-\widehat\beta_{AB}\overline{b^{pre}}_s-\widehat\beta_{AX}\bar X_s,$$

$$\widehat m^A_{it}=-\left(\widehat\beta_A^{raw}+\widehat\beta_{AB}b^{pre}_{it}+\widehat\beta_{AX}X_{it}\right).$$

### 2.2 逐步回归表

系数下方括号为基于 50 次 bootstrap 标准误的 z 值；`***`、`**`、`*` 分别表示 1%、5%、10% 显著性。

**Panel A：核心变量与控制变量**

| 变量/统计量 | (A_X_only) 仅 X | (A_A_only) 仅 A | (A_b_only) 仅 b-pre | (B_all_core) 三核心 | (C_macro) +宏观 | (Layer1_X) 第一层 | (Layer2_A) 第二层 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| WSDI 天数×0.01 $X_{it}$ | 0.0114**<br>(2.043) | — | — | 0.0102*<br>(1.855) | 0.0091*<br>(1.781) | 0.0098*<br>(1.67) | 0.0092<br>(1.599) |
| 适应能力 $A_{it}$ | — | -0.034***<br>(-2.687) | — | -0.0418**<br>(-2.18) | -0.03*<br>(-1.676) | — | -0.027*<br>(-1.781) |
| 前一期债务/GDP $b^{pre}_{it}=b_{i,t-1}$ | — | — | 0.0004<br>(0.135) | 0.0016<br>(0.453) | 0.0056*<br>(1.839) | 0.0042<br>(0.916) | 0.0047<br>(1.049) |
| 滞后主权利差 $s_{i,t-1}$ | 0.816***<br>(28.846) | 0.8019***<br>(30.767) | 0.8096***<br>(41.558) | 0.7856***<br>(27.271) | 0.6611***<br>(21.844) | 0.6784***<br>(18.238) | 0.6637***<br>(17.701) |
| Growth | — | — | — | — | -0.1579***<br>(-9.264) | -0.1623***<br>(-8.339) | -0.1599***<br>(-8.2) |
| Inflation | — | — | — | — | 0.1424***<br>(6.889) | 0.147***<br>(5.93) | 0.1502***<br>(6.152) |
| Reserves | — | — | — | — | — | -0.0089<br>(-1.288) | -0.0081<br>(-1.188) |
| Terms of trade | — | — | — | — | — | 0.0037<br>(0.764) | 0.0038<br>(0.819) |
| 宏观控制 | 否 | 否 | 否 | 否 | 是 | 是 | 是 |
| 外部控制 | 否 | 否 | 否 | 否 | 否 | 是 | 是 |
| 国家固定效应 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Bootstrap 次数 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads |
| 国家数 | 50 | 61 | 63 | 50 | 50 | 50 | 50 |
| 年份数 | 23 | 28 | 28 | 23 | 23 | 20 | 20 |
| 样本量 | 823 | 1,213 | 1,245 | 812 | 811 | 742 | 742 |

**Panel B：交互模型**

| 变量/统计量 | (Interact_AB) A×b-pre | (Interact_AX) A×X | (Interact_all) 双交互 |
| --- | ---: | ---: | ---: |
| $A^c_{it}$ | -0.0341**<br>(-2.133) | -0.0259*<br>(-1.693) | -0.0337**<br>(-2.054) |
| $X^c_{it}$ | 0.0092<br>(1.606) | 0.0089<br>(1.554) | 0.0091<br>(1.593) |
| $(b^{pre}_{it})^c$ | 0.007<br>(1.563) | 0.0048<br>(1.094) | 0.0071<br>(1.581) |
| $A^c_{it}\times(b^{pre}_{it})^c$ | -0.0601**<br>(-2.405) | — | -0.0593**<br>(-2.273) |
| $A^c_{it}\times X^c_{it}$ | — | -0.0166<br>(-0.588) | -0.0043<br>(-0.145) |
| 滞后主权利差 $s_{i,t-1}$ | 0.6362***<br>(16.608) | 0.6621***<br>(17.625) | 0.6355***<br>(16.511) |
| Growth | -0.1573***<br>(-7.932) | -0.1598***<br>(-8.185) | -0.1573***<br>(-7.908) |
| Inflation | 0.157***<br>(6.234) | 0.1503***<br>(6.155) | 0.1571***<br>(6.215) |
| Reserves | -0.0089<br>(-1.298) | -0.008<br>(-1.166) | -0.0088<br>(-1.286) |
| Terms of trade | 0.0025<br>(0.544) | 0.0038<br>(0.817) | 0.0025<br>(0.543) |
| 宏观控制 | 是 | 是 | 是 |
| 外部控制 | 是 | 是 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 1 | 1 | 1 |
| Bootstrap 次数 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.bond_spreads | L.bond_spreads | L.bond_spreads |
| 国家数 | 50 | 50 | 50 |
| 年份数 | 20 | 20 | 20 |
| 样本量 | 742 | 742 | 742 |

### 2.3 构造用原始尺度系数

| 参数 | 估计值 | Bootstrap SE | z | p | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| beta_A_raw | 0.0025 | 0.0169 | 0.145 | 0.884 | [-0.0307, 0.0356] |
| beta_AB | -0.0593 | 0.0261 | -2.273 | 0.023 | [-0.1104, -0.0082] |
| beta_AX | -0.0043 | 0.0299 | -0.145 | 0.885 | [-0.0628, 0.0542] |

<details><summary>展开：baseline 点边际效应</summary>

| 模型 | 点 | 调节变量 | 边际效应 | SE | p | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Interact_AB | P10 | 0.26 | -0.0138 | 0.0146 | 0.343 | [-0.0424, 0.0148] |
| Interact_AB | P25 | 0.3741 | -0.0207 | 0.0145 | 0.155 | [-0.0492, 0.0078] |
| Interact_AB | P50 | 0.5128 | -0.029 | 0.0152 | 0.056 | [-0.0589, 0.0008] |
| Interact_AB | P75 | 0.7541 | -0.0436 | 0.018 | 0.016 | [-0.0788, -0.0083] |
| Interact_AB | P90 | 1.0494 | -0.0613 | 0.0232 | 0.008 | [-0.1067, -0.0159] |
| Interact_AB | Mean_minus_1SD | 0.255 | -0.0135 | 0.0146 | 0.354 | [-0.0422, 0.0151] |
| Interact_AB | Mean | 0.5967 | -0.0341 | 0.016 | 0.033 | [-0.0654, -0.0028] |
| Interact_AB | Mean_plus_1SD | 0.9385 | -0.0546 | 0.0211 | 0.009 | [-0.0959, -0.0134] |
| Interact_AX | P10 | 0.0544 | -0.024 | 0.0161 | 0.136 | [-0.0554, 0.0075] |
| Interact_AX | P25 | 0.0951 | -0.0246 | 0.0157 | 0.117 | [-0.0555, 0.0062] |
| Interact_AX | P50 | 0.1523 | -0.0256 | 0.0154 | 0.096 | [-0.0557, 0.0046] |
| Interact_AX | P75 | 0.2251 | -0.0268 | 0.0152 | 0.077 | [-0.0565, 0.0029] |
| Interact_AX | P90 | 0.3256 | -0.0285 | 0.0153 | 0.064 | [-0.0585, 0.0016] |
| Interact_AX | Mean_minus_1SD | 0.0658 | -0.0241 | 0.016 | 0.130 | [-0.0554, 0.0071] |
| Interact_AX | Mean | 0.1709 | -0.0259 | 0.0153 | 0.091 | [-0.0559, 0.0041] |
| Interact_AX | Mean_plus_1SD | 0.2761 | -0.0276 | 0.0152 | 0.069 | [-0.0574, 0.0021] |
| Interact_all | P10 | 0.26 | -0.0137 | 0.0146 | 0.350 | [-0.0424, 0.015] |
| Interact_all | P25 | 0.3741 | -0.0205 | 0.0147 | 0.163 | [-0.0492, 0.0083] |
| Interact_all | P50 | 0.5128 | -0.0287 | 0.0155 | 0.064 | [-0.0591, 0.0017] |
| Interact_all | P75 | 0.7541 | -0.043 | 0.0186 | 0.021 | [-0.0795, -0.0065] |
| Interact_all | P90 | 1.0494 | -0.0605 | 0.0242 | 0.012 | [-0.1079, -0.0131] |
| Interact_all | Mean_minus_1SD | 0.255 | -0.0134 | 0.0146 | 0.361 | [-0.0421, 0.0153] |
| Interact_all | Mean | 0.5967 | -0.0337 | 0.0164 | 0.040 | [-0.0658, -0.0015] |
| Interact_all | Mean_plus_1SD | 0.9385 | -0.0539 | 0.0219 | 0.014 | [-0.0969, -0.0109] |
| Interact_all | P10 | 0.0544 | -0.0331 | 0.0175 | 0.059 | [-0.0675, 0.0012] |
| Interact_all | P25 | 0.0951 | -0.0333 | 0.0171 | 0.051 | [-0.0668, 0.0001] |
| Interact_all | P50 | 0.1523 | -0.0336 | 0.0165 | 0.042 | [-0.066, -0.0012] |
| Interact_all | P75 | 0.2251 | -0.0339 | 0.0161 | 0.035 | [-0.0654, -0.0024] |
| Interact_all | P90 | 0.3256 | -0.0343 | 0.0159 | 0.031 | [-0.0656, -0.0031] |
| Interact_all | Mean_minus_1SD | 0.0658 | -0.0332 | 0.0174 | 0.056 | [-0.0673, 0.0009] |
| Interact_all | Mean | 0.1709 | -0.0337 | 0.0164 | 0.040 | [-0.0658, -0.0015] |
| Interact_all | Mean_plus_1SD | 0.2761 | -0.0341 | 0.0159 | 0.032 | [-0.0653, -0.0029] |

</details>

## 3. Empirical theta：边际 T 收益与经验指标

### 3.1 T 指标回归公式与时序

$$T_{it}=\frac{(ConstantGDP_{it})}{(ConstantGDP_{i,t-1})},\qquad T_{i,t+1}=\frac{(ConstantGDP_{i,t+1})}{(ConstantGDP_{it})}=F.T_{it}.$$

$$T_{i,t+1}=\alpha_i+\lambda_t+\gamma_AA_{it}+\gamma_XX_{it}+\gamma_{AX}A_{it}X_{it}+\rho_TT_{it}+\Gamma_T'W^T_{it}+\varepsilon^T_{i,t+1}.$$

T 指标交互模型在全控制交互式的实际样本内中心化，故 $\widehat\gamma_A^{raw}=\widehat\gamma_A^c-\widehat\gamma_{AX}\bar X_T$，且

$$\widehat T^A_{it}=\widehat\gamma_A^{raw}+\widehat\gamma_{AX}X_{it}=\widehat\gamma_A^c+\widehat\gamma_{AX}X^c_{it}.$$

### 3.2 T 指标逐步回归表

系数下方括号为基于 50 次 bootstrap 标准误的 z 值。所有规格均由 LSDVC 自动加入 $L.T_{i,t+1}=T_{it}$。

**Panel A：核心变量与控制变量**

| 变量/统计量 | (T1_X_only) 仅 X | (T2_A_only) 仅 A | (T3_persistence) 仅当期 T 指标 | (T4_all_core) 核心项 | (T5_macro) +宏观 | (T6_layer1_X) 第一层 | (T7_layer2_A) 第二层 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| WSDI 天数×0.01 $X_{it}$ | -0.002<br>(-0.173) | — | — | -0.0023<br>(-0.201) | -0.0027<br>(-0.239) | -0.0025<br>(-0.264) | -0.0029<br>(-0.311) |
| 适应能力 $A_{it}$ | — | -0.0227<br>(-1.332) | — | -0.0103<br>(-0.459) | -0.0118<br>(-0.523) | — | -0.0083<br>(-0.346) |
| $T_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$ | 0.3726***<br>(13.489) | 0.3594***<br>(14.56) | 0.3508***<br>(12.236) | 0.3709***<br>(13.516) | 0.363***<br>(13.384) | 0.3405***<br>(10.477) | 0.3394***<br>(10.402) |
| Inflation | — | — | — | — | -0.0139<br>(-1.571) | -0.0197<br>(-1.368) | -0.0185<br>(-1.276) |
| Reserves | — | — | — | — | — | 0.0246**<br>(2.516) | 0.0254***<br>(2.587) |
| Terms of trade | — | — | — | — | — | -0.0078<br>(-1.521) | -0.0081<br>(-1.535) |
| 宏观控制 | 否 | 否 | 否 | 否 | 是 | 是 | 是 |
| 外部控制 | 否 | 否 | 否 | 否 | 否 | 是 | 是 |
| 国家固定效应 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Bootstrap 次数 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.T_lead | L.T_lead | L.T_lead | L.T_lead | L.T_lead | L.T_lead | L.T_lead |
| 国家数 | 52 | 61 | 63 | 52 | 52 | 52 | 52 |
| 年份数 | 23 | 27 | 27 | 23 | 23 | 23 | 23 |
| 样本量 | 1,179 | 1,645 | 1,699 | 1,179 | 1,178 | 1,024 | 1,024 |

**Panel B：交互模型**

| 变量/统计量 | (T8_interact_core) 交互核心 | (T9_interact_macro) 交互+宏观 | (T10_interact_full) 交互+全控制 |
| --- | ---: | ---: | ---: |
| $A^c_{it}$ | -0.0122<br>(-0.556) | -0.014<br>(-0.636) | -0.0151<br>(-0.651) |
| $X^c_{it}$ | -0.0015<br>(-0.132) | -0.0018<br>(-0.161) | -0.0005<br>(-0.05) |
| $A^c_{it}\times X^c_{it}$ | 0.0313<br>(0.564) | 0.0362<br>(0.649) | 0.1095**<br>(2.098) |
| $T_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$ | 0.3706***<br>(13.432) | 0.3624***<br>(13.29) | 0.337***<br>(10.316) |
| Inflation | — | -0.0143<br>(-1.61) | -0.0186<br>(-1.287) |
| Reserves | — | — | 0.0253***<br>(2.578) |
| Terms of trade | — | — | -0.0086<br>(-1.641) |
| 宏观控制 | 否 | 是 | 是 |
| 外部控制 | 否 | 否 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 1 | 1 | 1 |
| Bootstrap 次数 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.T_lead | L.T_lead | L.T_lead |
| 国家数 | 52 | 52 | 52 |
| 年份数 | 23 | 23 | 23 |
| 样本量 | 1,179 | 1,178 | 1,024 |

### 3.3 边际 T 收益与 theta 构造

| 参数 | 估计值 | Bootstrap SE | z | p | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| gamma_A_raw | -0.0332 | 0.0233 | -1.428 | 0.153 | [-0.0788, 0.0124] |
| gamma_AX | 0.1095 | 0.0522 | 2.098 | 0.036 | [0.0072, 0.2118] |

$$\widehat\theta^A_{it}=b^{pre}_{it}\widehat m^A_{it}+\widehat T^A_{it},\qquad b^{pre}_{it}=debt\_gdp_{i,t-1}.$$

构造支持集严格继承来源回归：`mA_hat` 仅在 Spread_Interact_all 的 `e(sample)` 内生成，`TA_hat` 仅在 T10_interact_full 的 `e(sample)` 内生成，theta 仅在二者共同覆盖时生成。

| 构造量 | 样本 | N | 均值 | SD | P10 | P50 | P90 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mA_hat | theta_support | 742 | 0.0337 | 0.0203 | 0.0135 | 0.0288 | 0.0604 |
| spread_saving_component | theta_support | 742 | 0.027 | 0.0355 | 0.0035 | 0.0149 | 0.0634 |
| TA_hat | theta_support | 742 | -0.0145 | 0.0115 | -0.0273 | -0.0166 | 0.0024 |
| theta_hat_A | theta_support | 742 | 0.0125 | 0.0383 | -0.0201 | 0.0029 | 0.0523 |
| theta_hat_A | all_constructible | 742 | 0.0125 | 0.0383 | -0.0201 | 0.0029 | 0.0523 |

## 4. Doomloop：一期去状态变量主规格

### 4.1 方程与 cutoff 口径

$$\Delta debt_{i,t+1}=debt\_gdp_{i,t+1}-debt\_gdp_{it}.$$

$$\Delta debt_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-\widehat\theta^A_{it})_++\beta_HA_{it}(\widehat\theta^A_{it}-c)_++\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.$$

$$A_{it}-A_{i,t-1}=\alpha_i+\lambda_t+\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_++\delta_HFT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_++\gamma_XX_{it}+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.$$

债务方程不另加入 $b^{pre}_{it}$ 状态项，readiness 方程不加入 $A_{i,t-1}$。$\widehat c_B^\theta$ 仅由债务全控制方程在 theta 的 P10—P90 观测值中按最小 RSS 选择；readiness 不进行独立 cutoff 搜索。两类方程均显式控制 $X_{it}$，并依次加入 Growth、Inflation、Reserves 与 Terms of trade。

### 4.2 债务变化方程

| 变量/统计量 | (DN1_core) 核心项 | (DN2_macro) +宏观 | (DN3_full) +全控制 |
| --- | ---: | ---: | ---: |
| $A_{it}(c-\widehat\theta^A_{it})_+$ | 2.7257***<br>(4.652) | 2.5423***<br>(4.339) | 2.5413***<br>(4.561) |
| $A_{it}(\widehat\theta^A_{it}-c)_+$ | -0.8832***<br>(-4.833) | -0.9954***<br>(-5.338) | -0.9697***<br>(-5.368) |
| WSDI 天数×0.01 $X_{it}$ | 0.1772***<br>(3.855) | 0.1671***<br>(3.728) | 0.1685***<br>(3.744) |
| Growth | — | -0.5046***<br>(-5.638) | -0.5073***<br>(-5.919) |
| Inflation | — | -0.1427<br>(-0.91) | -0.1163<br>(-0.74) |
| Reserves | — | — | -0.0493<br>(-0.92) |
| Terms of trade | — | — | 0.0299<br>(0.817) |
| 宏观控制 | 否 | 是 | 是 |
| 外部控制 | 否 | 否 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 聚类变量 | country_id | country_id | country_id |
| 聚类数 | 50 | 50 | 50 |
| 国家数 | 50 | 50 | 50 |
| 年份数 | 20 | 20 | 20 |
| 样本量 | 742 | 742 | 742 |
| Within $R^2$ | 0.336 | 0.378 | 0.384 |
| Overall $R^2$ | 0.062 | 0.093 | 0.104 |

### 4.3 Readiness 一阶差分方程：固定使用债务 cutoff

| 变量/统计量 | (RDN1_core) 核心项 | (RDN2_macro) +宏观 | (RDN3_full) +全控制 |
| --- | ---: | ---: | ---: |
| $FT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+$ | -1.4072**<br>(-2.526) | -1.3645**<br>(-2.457) | -1.378**<br>(-2.488) |
| $FT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_+$ | 0.6227*<br>(1.689) | 0.9236**<br>(2.312) | 0.8968**<br>(2.303) |
| WSDI 天数×0.01 $X_{it}$ | 0.0009<br>(0.118) | 0.0011<br>(0.148) | 0.0011<br>(0.147) |
| Growth | — | 0.0723***<br>(2.696) | 0.0727**<br>(2.676) |
| Inflation | — | -0.0573<br>(-1.553) | -0.0599<br>(-1.675) |
| Reserves | — | — | 0.0026<br>(0.323) |
| Terms of trade | — | — | -0.0044<br>(-0.592) |
| 宏观控制 | 否 | 是 | 是 |
| 外部控制 | 否 | 否 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 聚类变量 | country_id | country_id | country_id |
| 聚类数 | 50 | 50 | 50 |
| 国家数 | 50 | 50 | 50 |
| 年份数 | 20 | 20 | 20 |
| 样本量 | 742 | 742 | 742 |
| Within $R^2$ | 0.203 | 0.212 | 0.213 |
| Overall $R^2$ | 0.191 | 0.198 | 0.197 |

### 4.4 全控制结果、边际效应与图形

| 结果方程 | cutoff 来源 | cutoff | RSS | 候选数 | N_low | N_high | 低支系数 | p_L | 高支系数 | p_H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 债务变化 | 债务全控制 RSS | 0.0518 | 1.068947 | 592 | 667 | 75 | 2.5413 | <0.001 | -0.9697 | <0.001 |
| Readiness | 继承债务 cutoff | 0.0518 | 0.196898 | — | — | — | -1.378 | 0.016 | 0.8968 | 0.026 |

点边际效应按 $m(\theta;c)=a(c-\theta)_++b(\theta-c)_+$ 计算；在 cutoff 处定义为 0。

<details><summary>展开：主规格点边际效应</summary>

| 方程 | 点 | $\theta$ | 边际效应 | 国家聚类 SE | p 值 | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 债务变化 | P10 | -0.0201 | 0.1828 | 0.0401 | <0.001 | [0.1022, 0.2633] |
| 债务变化 | P25 | -0.0108 | 0.1591 | 0.0349 | <0.001 | [0.089, 0.2292] |
| 债务变化 | P50 | 0.0029 | 0.1244 | 0.0273 | <0.001 | [0.0696, 0.1792] |
| 债务变化 | Mean | 0.0125 | 0.0999 | 0.0219 | <0.001 | [0.0559, 0.1439] |
| 债务变化 | Cutoff | 0.0518 | 0 | 0 | — | [0, 0] |
| 债务变化 | P75 | 0.0217 | 0.0764 | 0.0168 | <0.001 | [0.0427, 0.1101] |
| 债务变化 | P90 | 0.0523 | -0.0005 | 0.0001 | <0.001 | [-0.0007, -0.0003] |
| Readiness（债务 cutoff） | P10 | -0.0201 | -0.0991 | 0.0398 | 0.016 | [-0.1792, -0.0191] |
| Readiness（债务 cutoff） | P25 | -0.0108 | -0.0863 | 0.0347 | 0.016 | [-0.156, -0.0166] |
| Readiness（债务 cutoff） | P50 | 0.0029 | -0.0674 | 0.0271 | 0.016 | [-0.1219, -0.013] |
| Readiness（债务 cutoff） | Mean | 0.0125 | -0.0542 | 0.0218 | 0.016 | [-0.0979, -0.0104] |
| Readiness（债务 cutoff） | Cutoff | 0.0518 | 0 | 0 | — | [0, 0] |
| Readiness（债务 cutoff） | P75 | 0.0217 | -0.0414 | 0.0167 | 0.016 | [-0.0749, -0.008] |
| Readiness（债务 cutoff） | P90 | 0.0523 | 0.0004 | 0.0002 | 0.026 | [0.0001, 0.0008] |

</details>

| 债务变化 | Readiness（债务 cutoff） |
| --- | --- |
| ![债务变化边际效应](figures/debt_marginal_effect_no_b.png) | ![Readiness 边际效应](figures/readiness_marginal_effect_debt_cutoff_no_lag.png) |

合并版：[PNG](figures/kink_marginal_effects_no_state.png) · [PDF](figures/kink_marginal_effects_no_state.pdf)

## 5. Criterion Decomposition / Competing Criterion Test

令阈值判据为 $q_{it}$，每个判据均在其因变量、分支构造量和全套控制变量共同非缺失的样本上估计

$$\Delta debt_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-q_{it})_++\beta_HA_{it}(q_{it}-c)_++\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1},$$

$$q_{it}\in\left\{\widehat\theta^A_{it},\ b^{pre}_{it},\ \widehat m^A_{it},\ \widehat T^A_{it},\ b^{pre}_{it}\widehat m^A_{it}\right\}.$$

每种判据分别在自身 P10—P90 候选值上搜索最小 RSS cutoff。理论方向为 $\beta_L>0$、$\beta_H<0$；$N_{low}=\#\{q_{it}\le c\}$，$N_{high}=\#\{q_{it}>c\}$。

| Criterion | cutoff | beta_L | p_L | beta_H | p_H | theoretical signs | RSS | Within R2 | N | N_low | N_high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | 0.0518 | 2.5413 | <0.001 | -0.9697 | <0.001 | Match (+,-) | 1.068947 | 0.3844 | 742 | 667 | 75 |
| $b^{pre}_{it}$ | 0.211 | 0.0735 | 0.658 | -0.2005 | <0.001 | Match (+,-) | 1.35845 | 0.3634 | 984 | 99 | 885 |
| $\widehat m^A_{it}$ | 0.0136 | 1.1664 | 0.660 | -3.8322 | <0.001 | Match (+,-) | 1.04428 | 0.3986 | 742 | 76 | 666 |
| $\widehat T^A_{it}$ | -0.0108 | 0.5344 | 0.634 | -3.3759 | 0.001 | Match (+,-) | 1.688265 | 0.2564 | 996 | 705 | 291 |
| $b^{pre}_{it}\widehat m^A_{it}$ | 0.0361 | 3.235 | <0.001 | -1.3701 | 0.002 | Match (+,-) | 1.075132 | 0.3809 | 742 | 574 | 168 |

各判据的 cutoff、分支系数和 RSS 均处于自身尺度与自身完整案例样本中。由于 N 可能不同，cutoff、系数和 RSS 不作跨行绝对排名；表格用于报告各判据内部的拟合、显著性、理论方向与阈值两侧覆盖。

## 6. 结果解释边界

这些结果是相关性估计，不应表述为因果效应。第 2—3 节的 50 次 LSDVC bootstrap 标准误只对应各上游方程；第 4 节的国家聚类标准误处理国家内相关，但没有计入 theta 生成误差或 cutoff 搜索不确定性。正式联合推断仍应采用按国家重抽样、每次重估完整流程的 bootstrap。竞争判据使用各自完整案例样本，既不是同样本 RSS 比较，也不是非嵌套模型的正式显著性检验。
