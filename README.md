# paperB0804

Paper B 的可复现实证分析仓库，包含分析数据、完整 Stata 源码、机器可读输出、诊断材料、图形与进展记录。

## 快速运行

在仓库根目录执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1
```

只基于现有 Stata 输出重新生成文档：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paperB\run_workflow.ps1 -SkipStata
```

默认环境为 Stata 18 MP、PowerShell 与 Python 3.14。完整执行顺序和口径见 [`paperB/WORKFLOW.md`](paperB/WORKFLOW.md)。

## 主要交付

- [`paperB/progress.md`](paperB/progress.md)：当前进展、实证结论、核心卡点与下一步。
- [`paperB/paperB_results.md`](paperB/paperB_results.md)：正式模型、系数、边际效应、cutoff 与图形。
- [`paperB/paperB_diagnostics.md`](paperB/paperB_diagnostics.md)：数据、样本、统计检验与程序 QA。
- `baseline/stata_outputs/`、`empirical_theta/stata_outputs/`、`doomloop/stata_outputs/`：CSV、DTA 与运行日志。

## 解释边界

当前结果是双向固定效应相关性证据。国家聚类标准误、theta/cutoff 全流程 bootstrap 与 cutoff 敏感性分析仍是正式推断前的优先工作；数据构建脚本所需的两份上游源文件也尚未纳入仓库。
