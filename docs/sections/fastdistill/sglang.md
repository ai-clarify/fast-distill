# FastDistill + SGLang

SGLang exposes an OpenAI-compatible API, so FastDistill can connect via
`SGLangLLM` (or `OpenAILLM` with a custom `base_url`).

## Start a local SGLang server
```bash
python -m sglang.launch_server --model qwen/qwen2.5-0.5b-instruct --port 30000
```

## Use in FastDistill
```python
from distilabel.models.llms import SGLangLLM

llm = SGLangLLM(model="qwen/qwen2.5-0.5b-instruct")
```

Environment variables:
- `SGLANG_BASE_URL` (default: `http://127.0.0.1:30000/v1`)
- `SGLANG_API_KEY` (optional; set only if your server requires it)
