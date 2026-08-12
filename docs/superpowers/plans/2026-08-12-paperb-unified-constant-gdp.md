# Paper B 统一 ConstantGDP 实施计划

1. 更新结果合同测试：baseline、spread、Doomloop 直接含 `growth` 与
   `ln_constantgdp`；Y 模型按持久性规格让 ConstantGDP 恰好进入一次；面板逐行
   验证 log 和严格一期 lead。
2. 修改 `baseline_twfe.do`，生成和使用 `ln_constantgdp`，同步样本、画像和元数据。
3. 修改 `empirical_theta.do`，将产出映射和共同控制改为 ConstantGDP，并对 Y3--Y10
   去除重复 GDP 项；同步验证、导出和标签。
4. 修改 `doomloop_no_state.do`，读取并控制 `ln_constantgdp`，同步审计面板和说明。
5. 修改 `render_output.py`、`run_workflow.ps1` 与 `WORKFLOW.md`，统一符号、QA 和
   完全共线性处理说明。
6. 运行聚焦测试确认由旧结果触发预期失败；再运行完整工作流生成全部结果。
7. 运行统一入口 QA 和完整测试套件，检查日志、公式审计、模型变量、文档与 git 差异。
