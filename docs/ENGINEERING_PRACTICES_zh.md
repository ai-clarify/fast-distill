# 工程实践

本仓库强调正确性、可维护性与可复现性。请按以下清单执行。

## 核心规则
- 多步骤工作需在 `docs/plans/` 建计划并持续更新。
- 重要事故记录在 `docs/error-experience/entries/`，并在
  `docs/error-experience/summary/entries/` 写摘要（索引文件仅保留索引）。
- 配置文件统一使用 YAML，避免 JSON 配置示例。
- 若上下文保证不变式，避免多余防御式代码。
- 交付前运行相关测试（单测 + 受影响的集成路径）。

## FastDistill 约定
- 产出可复现的清单与质量报告。
- 基线结果记录在 `docs/sections/fastdistill/baseline.md`。
- 性能指标记录在 `docs/sections/fastdistill/performance.md`。

## 文档规范
- 关键改动需更新 README。
- 新增 FastDistill 内容尽量补充中英文文档。
