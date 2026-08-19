# Paper B：统一回归公式与结果表

> 数据：`data0804/invest_panel_weo.csv` 与 `WSDI/data/processed/wsdi_sovereign61_1995_2018.csv`；整合生成时间：2026-08-19 15:29（Asia/Shanghai）。
> 本文档呈现正式公式、回归表、边际效应、债务 cutoff 与竞争判据结果。数据检查和统计验证见 `paperB_diagnostics.md`。主面板源比率、百分数和 0—100 指数均先除以 100；WSDI 天数乘以 0.01 后作为 X 进入回归。

## 技术摘要

- Baseline 全交互模型中，A×b-pre 系数为 0.0232（p=0.528），A×X 系数为 0.0142（p=0.707）。
- 全控制 T 指标模型的原始尺度适应能力系数为 -0.0077（p=0.898），A×X 系数为 0.1126（p=0.066）。
- 第四节唯一主规格的债务 cutoff 为 -0.025；债务两支联合检验 p=<0.001，使用同一 cutoff 的 A（1−Capacity）两支联合检验 p=0.213。
- 五个替代判据按各自当前变量取完整案例，N 范围为 742–996；完整 theta 的样本内 RSS=1.096934。因样本量可能不同，RSS 不作跨判据排名。
- 第 2—3 节为含国家与年份效应的动态面板 LSDVC 相关性估计，采用 Blundell–Bond 初始化、`bias(2)` 与 50 次 bootstrap 标准误；第 4 节仍为双向固定效应并报告国家聚类标准误。theta 和 cutoff 是生成量，末阶段聚类标准误仍未覆盖完整上游估计与 cutoff 搜索不确定性。

## 1. 统一符号、控制变量与估计口径

令 $s_{it}$ 为主权利差比率，$A_{it}=1-Capacity_{it}$ 为适应能力比率（ND-GAIN `capacity.csv` 已为 0—1 尺度），$X_{it}=wsdi\_days_{it}\times0.01$，$b^{pre}_{it}=b_{i,t-1}=debt\_gdp_{i,t-1}$。Baseline 的宏观控制为 Growth、Inflation，不控制 $\ln(ConstantGDP)$；T 指标方程的宏观控制仅为 Inflation，不控制 Growth；Doomloop 的宏观控制仍为 Growth、Inflation。外部控制为 Reserves、Terms of trade。全部模型含国家和年份效应。第 2—3 节使用 `xtlsdvc, initial(bb) bias(2) vcov(50)`：偏差修正精度为 $O((NT)^{-1})$，标准误来自 50 次 bootstrap；动态滞后因变量由 LSDVC 自动加入。第 4 节使用按 `country_id` 聚类的双向固定效应。每个回归使用其因变量、动态滞后项与当前右侧变量的联合非缺失样本，不再设置跨模型或跨阶段固定样本。生成量不向来源回归样本外外推：$\widehat m^A$ 限于 Spread_Interact_all 的实际样本，$\widehat T^A$ 限于 T10_interact_full 的实际样本，theta 限于两个来源样本的交集。`bias(2)` 在代表性规格中与 `bias(1)` 数值接近且稳定；`bias(3)` 曾在当前短而不平衡的面板上产生爆炸性动态系数，因此不作为主规格。

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
| WSDI 天数×0.01 $X_{it}$ | 0.0114**<br>(2.042) | — | — | 0.0111**<br>(2.039) | 0.0097*<br>(1.919) | 0.0098*<br>(1.67) | 0.0098*<br>(1.692) |
| 适应能力 $A_{it}=1-Capacity_{it}$ | — | -0.0054<br>(-0.215) | — | -0.0036<br>(-0.089) | 0.0213<br>(0.615) | — | 0.0172<br>(0.418) |
| 前一期债务/GDP $b^{pre}_{it}=b_{i,t-1}$ | — | — | 0.0004<br>(0.143) | 0.0013<br>(0.365) | 0.0052*<br>(1.695) | 0.0042<br>(0.916) | 0.0039<br>(0.882) |
| 滞后主权利差 $s_{i,t-1}$ | 0.8135***<br>(28.863) | 0.8053***<br>(33.09) | 0.8075***<br>(41.664) | 0.7948***<br>(26.625) | 0.6667***<br>(22.363) | 0.6793***<br>(18.39) | 0.6739***<br>(18.682) |
| Growth | — | — | — | — | -0.1621***<br>(-9.195) | -0.1622***<br>(-8.338) | -0.1628***<br>(-8.489) |
| Inflation | — | — | — | — | 0.1405***<br>(6.721) | 0.1468***<br>(5.925) | 0.1482***<br>(5.965) |
| Reserves | — | — | — | — | — | -0.0089<br>(-1.29) | -0.009<br>(-1.339) |
| Terms of trade | — | — | — | — | — | 0.0037<br>(0.765) | 0.0035<br>(0.749) |
| 宏观控制 | 否 | 否 | 否 | 否 | 是 | 是 | 是 |
| 外部控制 | 否 | 否 | 否 | 否 | 否 | 是 | 是 |
| 国家固定效应 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Bootstrap 次数 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads | L.bond_spreads |
| 国家数 | 50 | 61 | 63 | 50 | 50 | 50 | 50 |
| 年份数 | 23 | 28 | 28 | 23 | 23 | 20 | 20 |
| 样本量 | 823 | 1,213 | 1,245 | 812 | 811 | 742 | 742 |

**Panel B：交互模型**

| 变量/统计量 | (Interact_AB) A×b-pre | (Interact_AX) A×X | (Interact_all) 双交互 |
| --- | ---: | ---: | ---: |
| $A^c_{it}$ | 0.0224<br>(0.545) | 0.0183<br>(0.44) | 0.0234<br>(0.562) |
| $X^c_{it}$ | 0.0098*<br>(1.692) | 0.0097*<br>(1.678) | 0.0097*<br>(1.679) |
| $(b^{pre}_{it})^c$ | 0.0026<br>(0.564) | 0.0038<br>(0.854) | 0.0025<br>(0.551) |
| $A^c_{it}\times(b^{pre}_{it})^c$ | 0.0237<br>(0.652) | — | 0.0232<br>(0.631) |
| $A^c_{it}\times X^c_{it}$ | — | 0.0157<br>(0.42) | 0.0142<br>(0.376) |
| 滞后主权利差 $s_{i,t-1}$ | 0.6749***<br>(19.054) | 0.674***<br>(18.583) | 0.6749***<br>(18.955) |
| Growth | -0.1652***<br>(-8.386) | -0.1626***<br>(-8.461) | -0.1649***<br>(-8.347) |
| Inflation | 0.1465***<br>(5.723) | 0.1482***<br>(5.976) | 0.1465***<br>(5.725) |
| Reserves | -0.009<br>(-1.326) | -0.0093<br>(-1.381) | -0.0092<br>(-1.365) |
| Terms of trade | 0.0037<br>(0.797) | 0.0035<br>(0.754) | 0.0037<br>(0.801) |
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
| beta_A_raw | 0.0071 | 0.0442 | 0.161 | 0.872 | [-0.0795, 0.0938] |
| beta_AB | 0.0232 | 0.0367 | 0.631 | 0.528 | [-0.0488, 0.0951] |
| beta_AX | 0.0142 | 0.0378 | 0.376 | 0.707 | [-0.0598, 0.0882] |

<details><summary>展开：baseline 点边际效应</summary>

| 模型 | 点 | 调节变量 | 边际效应 | SE | p | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Interact_AB | P10 | 0.26 | 0.0144 | 0.0419 | 0.730 | [-0.0677, 0.0965] |
| Interact_AB | P25 | 0.3741 | 0.0171 | 0.0412 | 0.678 | [-0.0637, 0.098] |
| Interact_AB | P50 | 0.5128 | 0.0204 | 0.041 | 0.618 | [-0.0599, 0.1008] |
| Interact_AB | P75 | 0.7541 | 0.0262 | 0.0421 | 0.534 | [-0.0563, 0.1086] |
| Interact_AB | P90 | 1.0494 | 0.0332 | 0.0457 | 0.468 | [-0.0564, 0.1227] |
| Interact_AB | Mean_minus_1SD | 0.255 | 0.0143 | 0.0419 | 0.733 | [-0.0678, 0.0965] |
| Interact_AB | Mean | 0.5967 | 0.0224 | 0.0412 | 0.586 | [-0.0583, 0.1031] |
| Interact_AB | Mean_plus_1SD | 0.9385 | 0.0305 | 0.0441 | 0.488 | [-0.0558, 0.1169] |
| Interact_AX | P10 | 0.0544 | 0.0165 | 0.0409 | 0.686 | [-0.0636, 0.0967] |
| Interact_AX | P25 | 0.0951 | 0.0172 | 0.0411 | 0.677 | [-0.0634, 0.0978] |
| Interact_AX | P50 | 0.1523 | 0.0181 | 0.0415 | 0.664 | [-0.0634, 0.0995] |
| Interact_AX | P75 | 0.2251 | 0.0192 | 0.0422 | 0.649 | [-0.0636, 0.1019] |
| Interact_AX | P90 | 0.3256 | 0.0208 | 0.0434 | 0.632 | [-0.0643, 0.1059] |
| Interact_AX | Mean_minus_1SD | 0.0658 | 0.0167 | 0.041 | 0.683 | [-0.0636, 0.097] |
| Interact_AX | Mean | 0.1709 | 0.0183 | 0.0417 | 0.660 | [-0.0634, 0.1001] |
| Interact_AX | Mean_plus_1SD | 0.2761 | 0.02 | 0.0428 | 0.640 | [-0.0639, 0.1039] |
| Interact_all | P10 | 0.26 | 0.0156 | 0.0426 | 0.715 | [-0.0679, 0.099] |
| Interact_all | P25 | 0.3741 | 0.0182 | 0.0418 | 0.663 | [-0.0638, 0.1002] |
| Interact_all | P50 | 0.5128 | 0.0214 | 0.0415 | 0.606 | [-0.0599, 0.1028] |
| Interact_all | P75 | 0.7541 | 0.027 | 0.0424 | 0.524 | [-0.0561, 0.1101] |
| Interact_all | P90 | 1.0494 | 0.0339 | 0.0459 | 0.460 | [-0.056, 0.1237] |
| Interact_all | Mean_minus_1SD | 0.255 | 0.0154 | 0.0426 | 0.717 | [-0.0681, 0.099] |
| Interact_all | Mean | 0.5967 | 0.0234 | 0.0416 | 0.574 | [-0.0582, 0.1049] |
| Interact_all | Mean_plus_1SD | 0.9385 | 0.0313 | 0.0443 | 0.480 | [-0.0555, 0.1181] |
| Interact_all | P10 | 0.0544 | 0.0217 | 0.041 | 0.596 | [-0.0585, 0.102] |
| Interact_all | P25 | 0.0951 | 0.0223 | 0.0411 | 0.588 | [-0.0583, 0.1029] |
| Interact_all | P50 | 0.1523 | 0.0231 | 0.0415 | 0.577 | [-0.0582, 0.1044] |
| Interact_all | P75 | 0.2251 | 0.0241 | 0.0421 | 0.566 | [-0.0583, 0.1066] |
| Interact_all | P90 | 0.3256 | 0.0256 | 0.0431 | 0.554 | [-0.059, 0.1101] |
| Interact_all | Mean_minus_1SD | 0.0658 | 0.0219 | 0.041 | 0.594 | [-0.0585, 0.1022] |
| Interact_all | Mean | 0.1709 | 0.0234 | 0.0416 | 0.574 | [-0.0582, 0.1049] |
| Interact_all | Mean_plus_1SD | 0.2761 | 0.0249 | 0.0426 | 0.559 | [-0.0586, 0.1083] |

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
| WSDI 天数×0.01 $X_{it}$ | -0.002<br>(-0.173) | — | — | -0.0022<br>(-0.197) | -0.0026<br>(-0.227) | -0.0025<br>(-0.264) | -0.0024<br>(-0.261) |
| 适应能力 $A_{it}=1-Capacity_{it}$ | — | -0.0044<br>(-0.116) | — | 0.0475<br>(1.108) | 0.0406<br>(0.918) | — | -0.0072<br>(-0.119) |
| $T_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$ | 0.3719***<br>(13.457) | 0.3584***<br>(14.45) | 0.3504***<br>(12.215) | 0.3691***<br>(13.333) | 0.3624***<br>(13.246) | 0.3427***<br>(10.549) | 0.3403***<br>(10.452) |
| Inflation | — | — | — | — | -0.0129<br>(-1.45) | -0.0197<br>(-1.374) | -0.0185<br>(-1.345) |
| Reserves | — | — | — | — | — | 0.0245**<br>(2.51) | 0.025***<br>(2.587) |
| Terms of trade | — | — | — | — | — | -0.0077<br>(-1.52) | -0.0078<br>(-1.545) |
| 宏观控制 | 否 | 否 | 否 | 否 | 是 | 是 | 是 |
| 外部控制 | 否 | 否 | 否 | 否 | 否 | 是 | 是 |
| 国家固定效应 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 | 是 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Bootstrap 次数 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.T_lead | L.T_lead | L.T_lead | L.T_lead | L.T_lead | L.T_lead | L.T_lead |
| 国家数 | 52 | 61 | 63 | 52 | 52 | 52 | 52 |
| 年份数 | 23 | 27 | 27 | 23 | 23 | 23 | 23 |
| 样本量 | 1,179 | 1,645 | 1,699 | 1,179 | 1,178 | 1,024 | 1,024 |

**Panel B：交互模型**

| 变量/统计量 | (T8_interact_core) 交互核心 | (T9_interact_macro) 交互+宏观 | (T10_interact_full) 交互+全控制 |
| --- | ---: | ---: | ---: |
| $A^c_{it}$ | 0.0519<br>(1.224) | 0.0452<br>(1.037) | 0.011<br>(0.177) |
| $X^c_{it}$ | -0.0021<br>(-0.181) | -0.0024<br>(-0.211) | -0.0023<br>(-0.25) |
| $A^c_{it}\times X^c_{it}$ | 0.0298<br>(0.497) | 0.0316<br>(0.524) | 0.1126*<br>(1.841) |
| $T_{it}=ConstantGDP_{it}/ConstantGDP_{i,t-1}$ | 0.3691***<br>(13.253) | 0.3624***<br>(13.159) | 0.3412***<br>(10.345) |
| Inflation | — | -0.013<br>(-1.459) | -0.0175<br>(-1.263) |
| Reserves | — | — | 0.0242**<br>(2.499) |
| Terms of trade | — | — | -0.0084*<br>(-1.692) |
| 宏观控制 | 否 | 是 | 是 |
| 外部控制 | 否 | 否 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 估计量 | LSDVC | LSDVC | LSDVC |
| 初始化 | Blundell-Bond | Blundell-Bond | Blundell-Bond |
| 偏差修正阶数 | 2 | 2 | 2 |
| Bootstrap 次数 | 50 | 50 | 50 |
| 标准误 | bootstrap | bootstrap | bootstrap |
| 动态滞后项 | L.T_lead | L.T_lead | L.T_lead |
| 国家数 | 52 | 52 | 52 |
| 年份数 | 23 | 23 | 23 |
| 样本量 | 1,179 | 1,178 | 1,024 |

### 3.3 边际 T 收益与 theta 构造

| 参数 | 估计值 | Bootstrap SE | z | p | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| gamma_A_raw | -0.0077 | 0.0603 | -0.128 | 0.898 | [-0.1259, 0.1105] |
| gamma_AX | 0.1126 | 0.0612 | 1.841 | 0.066 | [-0.0073, 0.2325] |

$$\widehat\theta^A_{it}=b^{pre}_{it}\widehat m^A_{it}+\widehat T^A_{it},\qquad b^{pre}_{it}=debt\_gdp_{i,t-1}.$$

构造支持集严格继承来源回归：`mA_hat` 仅在 Spread_Interact_all 的 `e(sample)` 内生成，`TA_hat` 仅在 T10_interact_full 的 `e(sample)` 内生成，theta 仅在二者共同覆盖时生成。

| 构造量 | 样本 | N | 均值 | SD | P10 | P50 | P90 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mA_hat | theta_support | 742 | -0.0234 | 0.0083 | -0.0337 | -0.0218 | -0.0146 |
| spread_saving_component | theta_support | 742 | -0.0167 | 0.0173 | -0.0354 | -0.0111 | -0.0038 |
| TA_hat | theta_support | 742 | 0.0115 | 0.0118 | -0.0016 | 0.0094 | 0.029 |
| theta_hat_A | theta_support | 742 | -0.0052 | 0.0195 | -0.025 | -0.0034 | 0.0141 |
| theta_hat_A | all_constructible | 742 | -0.0052 | 0.0195 | -0.025 | -0.0034 | 0.0141 |

**图 1：theta 分布、债务方程 cutoff 与国家均值排序**

![theta 分布与 cutoff](figures/figure1_theta_distribution_cutoff.png)

[PNG](figures/figure1_theta_distribution_cutoff.png) · [PDF](figures/figure1_theta_distribution_cutoff.pdf) · 绘图数据：`doomloop/stata_outputs/theta_distribution_cutoff_plot_data.csv`、`theta_country_rank_plot_data.csv`

**图 2：经验边际利差节约 $m^A$ 随债务与 WSDI 的变化**

图中 $m^A=-\partial Spread/\partial A$ 来自 `Interact_all`；每个面板分别改变一个调节变量的 P10、P25、P50、P75、P90，并将另一调节变量固定在该来源样本均值。误差棒为 LSDVC 50 次 bootstrap VCE 的点估计 95% 置信区间。

![mA 随债务与 WSDI 的变化](figures/figure2_mA_by_debt_wsdi.png)

[PNG](figures/figure2_mA_by_debt_wsdi.png) · [PDF](figures/figure2_mA_by_debt_wsdi.pdf) · 绘图数据：`doomloop/stata_outputs/mA_by_debt_wsdi_plot_data.csv`

## 4. Doomloop：一期去状态变量主规格

### 4.1 方程与 cutoff 口径

$$\Delta debt_{i,t+1}=debt\_gdp_{i,t+1}-debt\_gdp_{it}.$$

$$\Delta debt_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-\widehat\theta^A_{it})_++\beta_HA_{it}(\widehat\theta^A_{it}-c)_++\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1}.$$

$$A_{it}-A_{i,t-1}=\alpha_i+\lambda_t+\delta_LFT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_++\delta_HFT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_++\gamma_XX_{it}+\Gamma_A'W^A_{it}+\varepsilon^A_{it}.$$

债务方程不另加入 $b^{pre}_{it}$ 状态项，A（1−Capacity）方程不加入 $A_{i,t-1}$。$\widehat c_B^\theta$ 仅由债务全控制方程在 theta 的 P10—P90 观测值中按最小 RSS 选择；A 方程不进行独立 cutoff 搜索。两类方程均显式控制 $X_{it}$，并依次加入 Growth、Inflation、Reserves 与 Terms of trade。

### 4.2 债务变化方程

| 变量/统计量 | (DN1_core) 核心项 | (DN2_macro) +宏观 | (DN3_full) +全控制 |
| --- | ---: | ---: | ---: |
| $A_{it}(c-\widehat\theta^A_{it})_+$ | -2.147*<br>(-1.956) | -2.3179**<br>(-2.417) | -2.2634**<br>(-2.462) |
| $A_{it}(\widehat\theta^A_{it}-c)_+$ | 3.5664***<br>(4.57) | 3.361***<br>(5.118) | 3.4159***<br>(5.158) |
| WSDI 天数×0.01 $X_{it}$ | -0.1986***<br>(-3.818) | -0.1892***<br>(-4.605) | -0.1902***<br>(-4.775) |
| Growth | — | -0.5378***<br>(-5.917) | -0.5409***<br>(-6.19) |
| Inflation | — | -0.1582<br>(-1.072) | -0.1291<br>(-0.873) |
| Reserves | — | — | -0.0536<br>(-1.077) |
| Terms of trade | — | — | 0.0334<br>(0.94) |
| 宏观控制 | 否 | 是 | 是 |
| 外部控制 | 否 | 否 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 聚类变量 | country_id | country_id | country_id |
| 聚类数 | 50 | 50 | 50 |
| 国家数 | 50 | 50 | 50 |
| 年份数 | 20 | 20 | 20 |
| 样本量 | 742 | 742 | 742 |
| Within $R^2$ | 0.312 | 0.361 | 0.368 |
| Overall $R^2$ | 0.072 | 0.113 | 0.125 |

### 4.3 A（1−Capacity）一阶差分方程：固定使用债务 cutoff

| 变量/统计量 | (RDN1_core) 核心项 | (RDN2_macro) +宏观 | (RDN3_full) +全控制 |
| --- | ---: | ---: | ---: |
| $FT_{it}(\widehat c_B^\theta-\widehat\theta^A_{it})_+$ | 0.496<br>(1.323) | 0.5058<br>(1.295) | 0.6958*<br>(1.73) |
| $FT_{it}(\widehat\theta^A_{it}-\widehat c_B^\theta)_+$ | -0.2225<br>(-0.598) | -0.2421<br>(-0.636) | -0.1539<br>(-0.411) |
| WSDI 天数×0.01 $X_{it}$ | 0.0095<br>(1.637) | 0.0095<br>(1.64) | 0.0081<br>(1.437) |
| Growth | — | -0.004<br>(-0.457) | -0.0046<br>(-0.533) |
| Inflation | — | 0.0142<br>(0.957) | 0.0122<br>(0.857) |
| Reserves | — | — | 0.0115***<br>(2.796) |
| Terms of trade | — | — | 0.0038*<br>(1.681) |
| 宏观控制 | 否 | 是 | 是 |
| 外部控制 | 否 | 否 | 是 |
| 国家固定效应 | 是 | 是 | 是 |
| 年份固定效应 | 是 | 是 | 是 |
| 聚类变量 | country_id | country_id | country_id |
| 聚类数 | 50 | 50 | 50 |
| 国家数 | 50 | 50 | 50 |
| 年份数 | 20 | 20 | 20 |
| 样本量 | 742 | 742 | 742 |
| Within $R^2$ | 0.049 | 0.05 | 0.065 |
| Overall $R^2$ | 0.031 | 0.038 | 0.052 |

### 4.4 全控制结果、边际效应与图形

| 结果方程 | cutoff 来源 | cutoff | RSS | 候选数 | N_low | N_high | 低支系数 | p_L | 高支系数 | p_H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 债务变化 | 债务全控制 RSS | -0.025 | 1.096934 | 593 | 75 | 667 | -2.2634 | 0.017 | 3.4159 | <0.001 |
| A（1−Capacity） | 继承债务 cutoff | -0.025 | 0.02741 | — | — | — | 0.6958 | 0.090 | -0.1539 | 0.683 |

点边际效应按 $m(\theta;c)=a(c-\theta)_++b(\theta-c)_+$ 计算；在 cutoff 处定义为 0。

<details><summary>展开：主规格点边际效应</summary>

| 方程 | 点 | $\theta$ | 边际效应 | 国家聚类 SE | p 值 | 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 债务变化 | P10 | -0.025 | 0 | 0 | — | [0, 0] |
| 债务变化 | P25 | -0.0115 | 0.0462 | 0.009 | <0.001 | [0.0282, 0.0642] |
| 债务变化 | P50 | -0.0034 | 0.0739 | 0.0143 | <0.001 | [0.0451, 0.1026] |
| 债务变化 | Mean | -0.0052 | 0.0678 | 0.0131 | <0.001 | [0.0414, 0.0942] |
| 债务变化 | Cutoff | -0.025 | 0 | 0 | — | [0, 0] |
| 债务变化 | P75 | 0.0056 | 0.1048 | 0.0203 | <0.001 | [0.064, 0.1456] |
| 债务变化 | P90 | 0.0141 | 0.1338 | 0.0259 | <0.001 | [0.0816, 0.1859] |
| A（1−Capacity，债务 cutoff） | P10 | -0.025 | 0 | 0 | — | [0, 0] |
| A（1−Capacity，债务 cutoff） | P25 | -0.0115 | -0.0021 | 0.0051 | 0.683 | [-0.0123, 0.0081] |
| A（1−Capacity，债务 cutoff） | P50 | -0.0034 | -0.0033 | 0.0081 | 0.683 | [-0.0196, 0.013] |
| A（1−Capacity，债务 cutoff） | Mean | -0.0052 | -0.0031 | 0.0074 | 0.683 | [-0.018, 0.0119] |
| A（1−Capacity，债务 cutoff） | Cutoff | -0.025 | 0 | 0 | — | [0, 0] |
| A（1−Capacity，债务 cutoff） | P75 | 0.0056 | -0.0047 | 0.0115 | 0.683 | [-0.0278, 0.0184] |
| A（1−Capacity，债务 cutoff） | P90 | 0.0141 | -0.006 | 0.0147 | 0.683 | [-0.0355, 0.0235] |

</details>

| 债务变化 | A（1−Capacity，债务 cutoff） |
| --- | --- |
| ![债务变化边际效应](figures/debt_marginal_effect_no_b.png) | ![A（1−Capacity）边际效应](figures/readiness_marginal_effect_debt_cutoff_no_lag.png) |

合并版：[PNG](figures/kink_marginal_effects_no_state.png) · [PDF](figures/kink_marginal_effects_no_state.pdf)

## 5. Criterion Decomposition / Competing Criterion Test

令阈值判据为 $q_{it}$，每个判据均在其因变量、分支构造量和全套控制变量共同非缺失的样本上估计

$$\Delta debt_{i,t+1}=\alpha_i+\lambda_t+\beta_LA_{it}(c-q_{it})_++\beta_HA_{it}(q_{it}-c)_++\gamma_XX_{it}+\Gamma_B'W^B_{it}+\varepsilon^B_{i,t+1},$$

$$q_{it}\in\left\{\widehat\theta^A_{it},\ b^{pre}_{it},\ \widehat m^A_{it},\ \widehat T^A_{it},\ b^{pre}_{it}\widehat m^A_{it}\right\}.$$

每种判据分别在自身 P10—P90 候选值上搜索最小 RSS cutoff。理论方向为 $\beta_L>0$、$\beta_H<0$；$N_{low}=\#\{q_{it}\le c\}$，$N_{high}=\#\{q_{it}>c\}$。

| Criterion | cutoff | beta_L | p_L | beta_H | p_H | theoretical signs | RSS | Within R2 | N | N_low | N_high |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $\widehat\theta^A_{it}$ | -0.025 | -2.2634 | 0.017 | 3.4159 | <0.001 | No (-,+) | 1.096934 | 0.3683 | 742 | 75 | 667 |
| $b^{pre}_{it}$ | 1.0003 | 0.1923 | <0.001 | -0.1441 | <0.001 | Match (+,-) | 1.358765 | 0.3633 | 984 | 885 | 99 |
| $\widehat m^A_{it}$ | -0.0337 | -6.3812 | <0.001 | 8.5655 | <0.001 | No (-,+) | 1.063838 | 0.3874 | 742 | 75 | 667 |
| $\widehat T^A_{it}$ | 0.0135 | 0.2503 | 0.800 | -2.0869 | 0.011 | Match (+,-) | 1.694753 | 0.2535 | 996 | 648 | 348 |
| $b^{pre}_{it}\widehat m^A_{it}$ | -0.0354 | -1.708 | <0.001 | 4.9064 | <0.001 | No (-,+) | 1.061425 | 0.3888 | 742 | 75 | 667 |

各判据的 cutoff、分支系数和 RSS 均处于自身尺度与自身完整案例样本中。由于 N 可能不同，cutoff、系数和 RSS 不作跨行绝对排名；表格用于报告各判据内部的拟合、显著性、理论方向与阈值两侧覆盖。

## 6. 结果解释边界

这些结果是相关性估计，不应表述为因果效应。第 2—3 节的 50 次 LSDVC bootstrap 标准误只对应各上游方程；第 4 节的国家聚类标准误处理国家内相关，但没有计入 theta 生成误差或 cutoff 搜索不确定性。正式联合推断仍应采用按国家重抽样、每次重估完整流程的 bootstrap。竞争判据使用各自完整案例样本，既不是同样本 RSS 比较，也不是非嵌套模型的正式显著性检验。
