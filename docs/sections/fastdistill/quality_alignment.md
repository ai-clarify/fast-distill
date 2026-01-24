# Teacher-Student Score Alignment

The core quality target is for student scores to match teacher scores on the
same tasks. FastDistill provides a score agreement report to measure this.

## Metrics
- **MAE / RMSE**: absolute and squared error between teacher and student scores.
- **Agreement@epsilon**: percentage of samples where `|student - teacher| <= ε`.
- **Pearson / Spearman**: correlation in raw scores and rank ordering.
- **Pass agreement**: optional binary agreement at a threshold.

## Output
The e2e Text2SQL pipeline writes:
- `~/.cache/fastdistill/artifacts/reports/score_agreement/score_agreement.json`

## Usage (Text2SQL e2e)
```bash
OLLAMA_MODEL=qwen3:0.6b python examples/fastdistill/ollama_distill_e2e.py
```

## Standardized eval prompt & split (Text2SQL)
When comparing teacher vs student, keep the eval setup fixed to avoid noisy deltas.

- **System prompt**: `Return SQL only.`
- **User template**: `Schema: {schema}\nQuestion: {instruction}\nSQL:`
- **Eval split**: `eval_200` = first 200 rows of WikiSQL eval
  - Build once: `head -n 200 ~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.jsonl > ~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval_200.jsonl`
- **Reporting**: always present pre/post/teacher on the same `eval_200` set.
