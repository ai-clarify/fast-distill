# FastDistill 性能分析

## 运行（2026-01-25，OpenRouter WikiSQL 1k）

### 关键指标（WikiSQL 1k）
- 蒸馏耗时：1000 条样本 1023.000s（约 3517 samples/hour）。
- 保留率：11.9%（119/1000）。
- Teacher exec_pass_rate：0.119；gold_match_rate：0.062；judge_score mean：0.0905。
- MLX 评测耗时（预训练）：889.301s；MLX 训练耗时：294.597s；MLX 评测耗时（训练后）：479.854s。
- 学生指标：exec_pass_rate 0.53 → 0.929；gold_match_rate 0.0 → 0.309；judge_score mean 0.265 → 0.619。

### 备注
- Teacher gate 默认阈值失败，使用 `FASTDISTILL_TEACHER_EVAL_GATE=0` 继续流程。

## 运行（2026-01-25，OpenRouter 快速蒸馏）

### 关键指标（Text2SQL 迷你集）
- 蒸馏耗时：1 条保留样本 35.798s（约 100.56 samples/hour）。
- 1k 样本蒸馏估算：约 9.94 小时（按保留样本线性估算）。
- Teacher exec_pass_rate：0.5（1 条 fenced SQL 执行失败）。
- Teacher gold_match_rate：0.5。

### 备注
- 建议在 SQL 执行前加入 `SqlOutputCleaner` 去除代码块，提升通过率。

## 运行（2026-01-25，Ollama 标准流程）

### 关键指标（Text2SQL 迷你集）
- 蒸馏耗时：2 条样本 35.200s（约 204.55 samples/hour）。
- Teacher exec_pass_rate：1.0（gold_match_rate 0.5）。
- Teacher judge_score mean：0.75。

### 备注
- 2 条样本触发默认 `min_total=50` gate，流程在 teacher_eval 阶段终止。

## 数据来源（2026-01-24 基线）
- Timing 报告：`~/.cache/fastdistill/artifacts/reports/timing_report.json`（2026-01-23，`examples/fastdistill/ollama_distill_e2e.py`）
- Baseline：`docs/sections/fastdistill/baseline.md`（2026-01-24，`scripts/run_ollama_mlx_e2e.py`）

## 关键指标（Text2SQL 迷你集）
- 蒸馏耗时：2 样本 20.930s（约 344 samples/hour）。
- 1k 样本蒸馏估算：约 2.91 小时（线性估算）。
- MLX 训练耗时：1k iters 约 60.187s（2 样本 smoke-test 配置）。

## 阶段耗时分布（p50，2026-01-23）
Top 阶段占比：
- `distilled -> student_gen`: 15.420s (61.9%)
- `hashed -> teacher`: 6.996s (28.1%)
- `filtered -> eval`: 0.578s (2.3%)
- `student_gen -> student_eval`: 0.450s (1.8%)
- `eval -> selected`: 0.436s (1.8%)
- 其余阶段单项 <1.2%

## 瓶颈结论
1. **LLM 生成是主耗时**：teacher + student 约占 90%。
2. **SQL 执行评测不是瓶颈**（本案例 <3%）。
3. **训练耗时独立**：MLX 训练主要受 iters 控制。

## 优化方向（按优先级）
1. **减少 token**：缩短 prompt / 输出，直接降时间与成本。
2. **并发与批量**：提高生成并发，增加 worker。
3. **前置廉价过滤**：格式规则优先过滤，减少后续计算。
4. **缓存 gold SQL**：避免重复执行同一 gold 查询。

## 训练提速手段
- 使用 `MLX_FAST=1` 降低评测和保存开销。
- 提高 `steps_per_eval` / `save_every`，减少训练中的评测与保存频率。
- 将 `batch_size` 与 `max_seq_length` 调到满足质量的最小值。

## 已实现优化
- **SQLiteExecEval gold SQL 缓存**：
  - 对重复的 gold SQL 结果做 LRU 缓存（`max_cached_gold`）。
  - 适用于大量重复 gold SQL 的任务（模板化题目）。
  - 默认开启（`cache_gold_results=True`）。
