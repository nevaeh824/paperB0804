# Paper B 统一 ConstantGDP 口径设计

## 目标

Paper B 当前主流程的共同 GDP 控制由 `ln_capitagdp=ln(capitaGDP)` 改为
`ln_constantgdp=ln(ConstantGDP)`。产出方程同时由 log current GDP 改为 log
constant GDP：`Y_outcome=F.ln_constantgdp`，`Y_lag=ln_constantgdp`。

## 范围

修改当前统一流程的三份权威 Stata 脚本：`baseline_twfe.do`、
`empirical_theta.do`、`doomloop_no_state.do`，以及统一入口、渲染器、工作流文档、
合同测试和全部派生结果。历史规格 `doomloop.do` 与 `doomloop_forward/` 不进入当前
主流程，因此不改写。

## 产出模型中的共线性处理

产出方程把 `Y_lag` 定义为 `ln_constantgdp` 后，两者是同一个逐行变量，不能作为
两个独立回归项同时进入。为避免依赖 Stata 自动丢弃完全共线项：

- Y1、Y2 没有持久性项，直接加入 `growth ln_constantgdp`；
- Y3--Y10 已含 `Y_lag`，只另加 `growth`，并由 `Y_lag` 唯一承载当期
  `ln(ConstantGDP)`；
- spread、baseline 与 Doomloop 的每个正式模型都直接加入
  `growth ln_constantgdp`。

统一样本仍按全部递增控制锁定，因而 Y1--Y10 的样本可比性不变。

## 数据与审计

`data0804/invest_panel_weo.csv` 已含 WEO `NGDP_R` 对应的 `ConstantGDP`。主流程只对
严格正值生成自然对数，并导出逐行 `ConstantGDP`、`ln_constantgdp`、`Y_outcome`
和 `Y_lag`，用公式审计验证严格相邻年份的 `F.` 映射。统一入口检查源列存在、
非正值、每模型的 GDP 控制表示，以及产出模型中不出现重复的
`Y_lag + ln_constantgdp`。

## 验证

先让结果合同测试因旧输出仍使用 capita/current GDP 而失败，再修改实现。随后运行
完整 Stata 工作流、渲染和整合 QA，最后运行全部 Python 测试并检查生成文档不再把
capita/current GDP 描述为当前估计口径。
