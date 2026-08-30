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

滞后一期债务镜像及两种规格的联合稳健性入口见 [`paperB_debt_lag/WORKFLOW.md`](paperB_debt_lag/WORKFLOW.md)。联合稳健性可由 `paperB/run_robustness.ps1` 或镜像中的同名入口执行；默认运行 30 次配对国家区组全管线 bootstrap。

## 主要交付

- [`paperB/paperBresult/paperB_results.md`](paperB/paperBresult/paperB_results.md)：当期债务正式结果与补充实验。
- [`paperB_debt_lag/paperB_debt_lag/paperB_results.md`](paperB_debt_lag/paperB_debt_lag/paperB_results.md)：滞后一期债务镜像结果与补充实验。
- `paperB/paperBresult/` 与 `paperB_debt_lag/paperB_debt_lag/`：各自完整的 CSV、DTA、日志、诊断和图形。

## 解释边界

当前结果是固定效应相关性证据。已完成的 30 次国家全管线 bootstrap 是简化诊断，正式置信区间仍应使用更多复制；数据构建脚本所需的两份上游源文件也尚未纳入仓库。
