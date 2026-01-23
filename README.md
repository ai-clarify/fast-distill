# Fast Distill

High-throughput distillation pipeline with hard quality gates and replayable data contracts.

## What it is
- Unified Provider Gateway (OpenAI-compatible surface)
- Deterministic data contract (canonical input + sample_id + manifest)
- Multi-stage quality gates (rules, exec, judge)
- Per-stage timing + quality reports
- Training decoupled from data generation

## Quickstart (Text2SQL + auto-eval)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[ollama]"
OLLAMA_MODEL=qwen3:0.6b python examples/fastdistill/ollama_distill_e2e.py
```

Artifacts (default):
- `~/.cache/fastdistill/artifacts/manifests/<stage>/manifest.json`
- `~/.cache/fastdistill/artifacts/reports/<stage>/quality_report.json`
- `~/.cache/fastdistill/artifacts/reports/timing_report.json`

## Architecture
End-to-end path:
```
Raw -> Canonicalize -> Dedup -> Teacher -> Rule Filter -> Exec -> Teacher Score -> Select -> Export -> Student Gen -> Student Eval
```

Design + flowchart + perf optimization points:
- `docs/sections/fastdistill/architecture.md`
- `docs/sections/fastdistill/architecture_zh.md`

Baseline run (2026-01-23):
- `docs/sections/fastdistill/baseline.md`

## Config
Sample YAML configs:
- `configs/fastdistill/run_config.sample.yaml`
- `configs/fastdistill/quality_gates.sample.yaml`
- `configs/fastdistill/provider_gateway.sample.yaml`

## Reference pipelines
- `examples/fastdistill/fastdistill_pipeline.py`
- `examples/fastdistill/fastdistill_pipeline.yaml`
Both reference pipelines use **Text2SQL** as the task example.

## Tests
```bash
pytest tests/unit/steps/fastdistill/test_fastdistill_steps.py
```

## License
Apache-2.0
