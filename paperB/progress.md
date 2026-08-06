# Paper B 工作进展与核心卡点

> 更新时间：2026-08-06 19:24（Asia/Shanghai）。本文件由 `paperB/render_output.py` 基于本次 Stata 机器可读输出自动生成。

## 技术摘要：分析链已跑通，核心门槛结论仍需稳健性支持

- 当前 `invest_panel_weo.csv` 已完成 baseline、empirical theta、doomloop 与去状态变量四段重估；结果、诊断、图形、CSV、DTA 和日志均已刷新。
- 边际税基收益现由 T11 完整二阶模型生成：$\gamma_{AA}$=-0.3985（p=0.026）、$\gamma_{AX}$=-0.1708（p=0.471），并控制滞后税基、$b_{it}$ 与四个非规模控制。
- 方程级规模控制已落实：$\ln(CurrentGDP)$ 在完整二阶利差、readiness 主规格和去滞后规格中的系数分别为 0.0147（p<0.001）、-0.0026（p=0.094）和 0.0003（p=0.790）；tax 与 debt-change 全部排除该项。
- `mA_hat` 已改由完整二阶 spread 模型生成：$\beta_{AA}$=0.4444（p=0.001）、$\beta_{Ab}$=-0.1516（p<0.001）、$\beta_{AX}$=0.5114（p=0.033）。
- Doomloop 联合检验：债务方程含/不含 b 时分别为 p=0.123、p=0.112；readiness 使用自身 min-RSS cutoff、债务方程 cutoff、去滞后 A 时分别为 p<0.001、p=0.005、p=0.004。
- readiness 的 min-RSS、债务-cutoff 与去滞后 A 三个规格的低、高分支依次为同号、异号、同号；异号才满足经验 single-crossing 的形状要求。
- 当前结果可作为双向固定效应相关性证据使用，但尚未纳入国家内序列相关、theta 生成误差与 cutoff 搜索不确定性，不能解释为因果效应或最终门槛证据。

## 1. 已完成：数据输入已审计，四段估计和统一输出均成功

| 板块 | 状态 | 本次交付/样本 | 判断 |
| --- | ---: | ---: | ---: |
| 分析输入 | 完成 | 1,972 行、68 国、1995–2023；国家—年份重复键为 0 | 可作为本次 Stata 分析的固定输入 |
| Baseline | 完成 | N=1,286，65 国，26 年 | 完整二阶 TWFE、原始尺度还原、Wald 与诊断已输出 |
| Empirical theta | 完成 | N=1,538，65 国，27 年 | 税基方程、theta panel 与构造审计已输出 |
| Doomloop debt | 完成 | N=1,552，cutoff=-0.0554 | 原始与去 b 规格均已重估 |
| Doomloop readiness | 完成 | N=1,571，minRSS cutoff=0.1148，债务 cutoff=-0.0554 | 两种 cutoff 与去滞后 A 规格均已重估 |
| 统一交付 | 完成 | results、diagnostics、progress、PNG/PDF、CSV/DTA、日志 | 统一入口可从现有分析 CSV 重跑 |

范围说明：回归中的百分比、比率和 0–100 指数均先除以 100；金额变量保持原尺度，$b_{it}$ 由同年 `debt/CurrentGDP` 直接计算。宏观控制为 Growth、Inflation，外部控制为 Reserves、Terms of trade；规模控制为 `ln_currentgdp=ln(CurrentGDP)`，规则是 ln(CurrentGDP) is included in spread/readiness and excluded from tax/debt-change。所有正式模型包含国家和年份固定效应，当前标准误为观测层异方差稳健标准误。

## 2. 当前证据：baseline 机制较稳定，doomloop 门槛尚不稳定

| 证据节点 | 估计/检验 | p 值 | 当前解释 |
| --- | ---: | ---: | ---: |
| 利差：A² | 0.4444 | 0.001 | 适应能力边际利差效应随 A 自身水平变化 |
| 利差：A×债务 | -0.1516 | <0.001 | 债务水平调节适应能力的边际利差效应 |
| 利差：A×脆弱性 | 0.5114 | 0.033 | 脆弱性水平调节适应能力的边际利差效应 |
| 税基：A 原始尺度 | 0.2673 | 0.123 | 未达 10% 显著性水平 |
| 税基：A² | -0.3985 | 0.026 | 达到 5% 显著性水平 |
| 税基：A×脆弱性 | -0.1708 | 0.471 | 未达 10% 显著性水平；边际 A 项联合检验 p=0.106 |
| 原始 debt kink | cutoff=-0.0554 | 0.123 | 未达 10% 显著性水平；两支异号 |
| 原始 readiness kink | cutoff=0.1148 | <0.001 | 达到 1% 显著性水平；两支同号 |
| readiness：债务方程 cutoff | cutoff=-0.0554 | 0.005 | 达到 1% 显著性水平；两支异号；RSS 差=0.0295 |
| 去 b debt kink | cutoff=-0.0554 | 0.112 | 未达 10% 显著性水平；两支异号 |
| 去滞后 A readiness kink | cutoff=0.147 | 0.004 | 达到 1% 显著性水平；两支同号 |

对应完整系数、边际效应和图形见 `paperB_results.md`；本进展文档不重复嵌图，以避免与正式结果文档形成两套展示口径。

## 3. 质量核验：计算一致性通过，但不等同于推断充分

| 核验 | 通过 | 总数 | 结论 |
| --- | ---: | ---: | ---: |
| 单位换算 | 27 | 27 | 通过 |
| 代数、映射与构造 | 24 | 24 | 通过 |
| cutoff 最小 RSS | 4 | 4 | 通过 |
| readiness 双 cutoff 来源 | 3 | 3 | 通过 |
| 国家—年份唯一键 | 3 | 3 | 三段流程重复键均为 0 |
| areg 与显式 LSDV | 已复核 | 关键系数 | 数值一致 |

这些检查证明本次结果在单位、公式、样本锁定和程序实现层面一致；它们不能替代聚类推断、完整 bootstrap 或外生识别。

## 4. 核心卡点：正式推断、single-crossing 形状和上游数据复现

### 4.1 正式推断尚未覆盖三类不确定性

当前 `vce(robust)` 不处理同一国家内序列相关；theta 来自两条上游回归，cutoff 又由同一样本 RSS 搜索产生。现有标准误没有联合覆盖这三层不确定性，p 值可能偏乐观。

### 4.2 Cutoff 与分支形状对状态项设定敏感

readiness 使用自身 min-RSS cutoff=0.1148 时联合 p<0.001；固定使用债务方程 cutoff=-0.0554 时 p=0.005，其 readiness RSS 比最小值高 0.0295。去滞后 A 后 cutoff=0.147、p=0.004。三种 readiness 规格的两支分别为同号、异号、同号。因此不能把借用债务 cutoff、readiness RSS 最优、kink 显著和 single-crossing 成立视为同一结论。

### 4.3 当前仓库可复现分析，但不能从源文件重建分析 CSV

四份完整 Stata 源码与三段输出已经保留，`paperB/run_workflow.ps1` 可从 `data0804/invest_panel_weo.csv` 重跑分析。WEO 工作簿 `data0804/WEOApr2026all.xlsx` 已在库内，但数据构建脚本仍依赖当前目录中不存在的根目录基础面板 `cleaned_imf_like_panel_1995_2023.csv`；补齐该文件前，数据层只能审计现有分析 CSV，不能从最上游完整重建。

### 4.4 缺失和单位限制仍影响外推

`bond_spreads` 缺失 525 行（26.62%），`tt` 缺失 242 行（12.27%），是主要样本损失来源；财政系列在早期年份也存在缺失。`CurrentGDP`、`revenue` 和 `debt` 是不同国家的本币金额，既有 reserves 口径也不适合直接做跨国水平比较。

### 4.5 识别边界没有改变

全部结果属于双向固定效应相关性估计。没有外生冲击、工具变量、事件研究或其他识别设计时，不应使用因果措辞。

## 5. 下一步：先补推断，再决定是否强化门槛叙事

1. **P0——补齐国家层面的推断。** 并列报告国家聚类标准误；随后按国家重抽样，每次完整重估 baseline、tax、theta、cutoff 和最终 kink 回归。
2. **P0——恢复数据层完全复现。** 补齐根目录基础面板 `cleaned_imf_like_panel_1995_2023.csv`，并记录它、WEO 工作簿与最终分析 CSV 的文件哈希及生成关系。
3. **P1——做 cutoff 稳定性分析。** 系统改变 trimming、候选网格、年份窗口、状态项和控制变量，报告 cutoff 与分支系数分布，而不是只报告单点最优值。
4. **P1——处理样本选择风险。** 比较完整样本、平衡窗口和高缺失变量剔除后的结果，明确 bond spread 与 terms-of-trade 缺失是否改变国家构成。
5. **P2——收紧论文表述。** 先将完整二阶 spread 模型及其 $m^A$ 构造作为上游发现，把 doomloop/readiness 门槛定位为待验证机制；只有在 bootstrap 和敏感性分析后仍稳定，才升级为核心结论。

## 6. 待回答的问题

- 论文的主命题究竟是“适应能力的非线性边际利差效应”，还是“存在稳定 doomloop cutoff”？两者需要由更新后的稳健性结果重新排序。
- readiness 的两支同号究竟意味着单调但斜率变化的 kink，还是理论 single-crossing 约束需要重新设定？
- 补齐聚类与全流程 bootstrap 后，主规格 readiness 的 p=<0.001 是否仍能维持？
- 早期财政数据和 bond spread 缺失是否集中在特定国家组，从而限制外部有效性？
