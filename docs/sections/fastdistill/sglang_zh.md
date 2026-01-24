# FastDistill + SGLang 对接

SGLang 提供 OpenAI 兼容 API，因此 FastDistill 可以通过 `SGLangLLM`
（或 `OpenAILLM` + 自定义 `base_url`）直接对接。

## 启动本地 SGLang 服务
```bash
python -m sglang.launch_server --model-path qwen/qwen2.5-0.5b-instruct --host 0.0.0.0 --port 30000
```

## FastDistill 使用示例
```python
from distilabel.models.llms import SGLangLLM

llm = SGLangLLM(model="qwen/qwen2.5-0.5b-instruct")
```

SGLang 提供 OpenAI 兼容的 `/v1` 接口（例如 `chat/completions`）。

环境变量：
- `SGLANG_BASE_URL`（默认：`http://127.0.0.1:30000/v1`）
- `SGLANG_API_KEY`（可选；仅在服务端要求鉴权时设置）
