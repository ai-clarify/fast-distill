# Paper-driven experiments (local Ollama teacher)

This playbook turns the paper list into runnable experiments using a **local Ollama teacher**. It assumes you want to start with the strongest local model you can reliably serve.

## 0) Prereqs
- Ollama running locally (`http://localhost:11434` by default).
- FastDistill installed with Ollama support: `pip install -e ".[ollama]"`.
- Dataset + (for Text2SQL) SQLite DB. See `docs/sections/fastdistill/text2sql_wikisql.md`.

## 1) Pick a local teacher model
Use the **largest instruction-tuned model that fits** your hardware with stable latency. Start with a smaller model for a smoke test, then swap in the strongest one for the real run.

Suggested workflow:
- List installed models: `ollama list`.
- Choose the best instruct/chat model you already have.
- Set it via `OLLAMA_MODEL`.

## 2) Baseline run (local Ollama teacher)
Use the Python pipeline for full gating + Text2SQL exec eval:

```bash
FASTDISTILL_PROVIDER=ollama \
OLLAMA_MODEL=your-ollama-teacher \
OLLAMA_HOST=http://localhost:11434 \
OLLAMA_TIMEOUT=240 \
FASTDISTILL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl \
FASTDISTILL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db \
python examples/fastdistill/fastdistill_pipeline.py
```

Quick sanity check (YAML, tiny sample):

```bash
fastdistill pipeline run --config examples/fastdistill/fastdistill_pipeline_ollama.yaml
```

> Edit `examples/fastdistill/fastdistill_pipeline_ollama.yaml` and replace `ollama-strong-model` with your local model name.

## 3) Paper-to-experiment recipes

### A) Distilling Step-by-Step (rationale supervision)
**Paper:** Distilling Step-by-Step! (High feasibility)

Goal: collect short rationales alongside answers.

Minimal changes:
- Update `system_prompt` or `template` to request a **short, structured rationale** plus the final answer.
- Keep a clear delimiter so you can split later (e.g., `### RATIONALE` / `### ANSWER`).
- Store the raw output for multi-task SFT; add a parsing step later if needed.

### B) Data Distillation (multi-decode + filtering)
**Paper:** Data Distillation (High feasibility)

Goal: generate multiple candidates per input, then filter using current gates.

Minimal changes:
- Increase `num_generations` in `TextGeneration` and raise temperature.
- Keep existing `RuleFilter` + `SQLiteExecEval` gates to select.
- Use `decode_profile` or `generation_kwargs.options` to tune diversity.

### C) Born-Again Neural Networks (iterative teacher swap)
**Paper:** Born Again Neural Networks (High feasibility)

Goal: iterate teacher → student → teacher.

Minimal changes:
- Run baseline with the strong Ollama teacher.
- Train student; deploy it locally in Ollama.
- Re-run the pipeline with the student as the teacher (`OLLAMA_MODEL=student-model`).
- Track `run_id` chain and compare metrics between iterations.

### D) Preference KD (judge-based pairs)
**Paper:** Direct Preference KD (Medium feasibility)

Goal: build pairwise preference data using the judge score.

Minimal changes:
- Use existing judge/score outputs to select top vs. bottom candidates.
- Add a small post-processing step to emit `(chosen, rejected)` pairs.

## 4) Tracking + reporting
- Record baselines in `docs/sections/fastdistill/baseline.md`.
- Track throughput + latency in `docs/sections/fastdistill/performance.md`.
- Keep `run_id`, teacher model, prompt changes, and gate thresholds in the run notes.

## 5) Suggested next iterations
- Add a `split_rationale` step to persist rationale + answer separately.
- Add a preference-pair export step for DPKD.
- Add logprobs capture for MiniLLM-style reverse-KL (requires model support).
