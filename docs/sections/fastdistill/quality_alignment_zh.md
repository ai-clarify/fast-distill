# 教师-学生评分一致性

质量核心目标是学生在同一任务上的评分尽量接近教师评分。FastDistill 提供评分一致性报告用于衡量。

## 指标
- **MAE / RMSE**：学生与教师评分的绝对误差与均方误差。
- **Agreement@epsilon**：`|student - teacher| <= ε` 的比例。
- **Pearson / Spearman**：评分一致性与排序一致性。
- **Pass agreement**：可选阈值下的二分类一致率。

## 输出
Text2SQL e2e 流程会写出：
- `~/.cache/fastdistill/artifacts/reports/score_agreement/score_agreement.json`

## 使用示例（Text2SQL e2e）
```bash
OLLAMA_MODEL=qwen3:0.6b python examples/fastdistill/ollama_distill_e2e.py
```
