import os
from typing import Optional

from pydantic import Field, PrivateAttr, SecretStr

from distilabel.mixins.runtime_parameters import RuntimeParameter
from distilabel.models.llms.openai import OpenAILLM

_SGLANG_API_KEY_ENV_VAR_NAME = "SGLANG_API_KEY"


class SGLangLLM(OpenAILLM):
    """SGLang LLM implementation using the OpenAI-compatible API surface.

    Attributes:
        model: the model name to use for the LLM, e.g., "qwen/qwen2.5-0.5b-instruct".
        base_url: the base URL to use for SGLang requests. Defaults to `None`, which
            means that the value set for the environment variable `SGLANG_BASE_URL`
            will be used, or "http://127.0.0.1:30000/v1" if not set.
        api_key: the API key to authenticate requests to SGLang. Defaults to `None`,
            which means that the value set for the environment variable `SGLANG_API_KEY`
            will be used, or `None` if not set.
        _api_key_env_var: the name of the environment variable to use for the API key.
            It is meant to be used internally.

    Examples:
        Generate text:

        ```python
        from distilabel.models.llms import SGLangLLM

        llm = SGLangLLM(model="qwen/qwen2.5-0.5b-instruct")

        llm.load()

        output = llm.generate_outputs(inputs=[[{"role": "user", "content": "Hello world!"}]])
        ```
    """

    base_url: Optional[RuntimeParameter[str]] = Field(
        default_factory=lambda: os.getenv("SGLANG_BASE_URL", "http://127.0.0.1:30000/v1"),
        description="The base URL to use for the SGLang OpenAI-compatible API.",
    )
    api_key: Optional[RuntimeParameter[SecretStr]] = Field(
        default_factory=lambda: os.getenv(_SGLANG_API_KEY_ENV_VAR_NAME),
        description="The API key to authenticate the requests to SGLang.",
    )

    _api_key_env_var: str = PrivateAttr(_SGLANG_API_KEY_ENV_VAR_NAME)
