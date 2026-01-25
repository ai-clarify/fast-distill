# FastDistill + SGLang

SGLang exposes an OpenAI-compatible API, so FastDistill can connect via
`SGLangLLM` (or `OpenAILLM` with a custom `base_url`).

## Start a local SGLang server
```bash
python -m sglang.launch_server --model-path qwen/qwen2.5-0.5b-instruct --host 0.0.0.0 --port 30000
```

## Use in FastDistill
```python
from fastdistill.models.llms import SGLangLLM

llm = SGLangLLM(model="qwen/qwen2.5-0.5b-instruct")
```

Reference pipeline switch:
```bash
FASTDISTILL_PROVIDER=sglang SGLANG_MODEL=qwen/qwen2.5-0.5b-instruct \
python examples/fastdistill/fastdistill_pipeline.py
```

The SGLang server exposes OpenAI-compatible endpoints under `/v1` (e.g. `chat/completions`).

Environment variables:
- `SGLANG_BASE_URL` (default: `http://127.0.0.1:30000/v1`)
- `SGLANG_API_KEY` (optional; set only if your server requires it)
