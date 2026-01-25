# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
from typing import Optional

from pydantic import Field, PrivateAttr, SecretStr

from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.models.llms.openai import OpenAILLM

_ANYSCALE_API_KEY_ENV_VAR_NAME = "ANYSCALE_API_KEY"


class AnyscaleLLM(OpenAILLM):
    """Anyscale LLM implementation running the async API client of OpenAI.

    Attributes:
        model: the model name to use for the LLM, e.g., `google/gemma-7b-it`. See the
            supported models under the "Text Generation -> Supported Models" section
            [here](https://docs.endpoints.anyscale.com/).
        base_url: the base URL to use for the Anyscale API requests. Defaults to `None`, which
            means that the value set for the environment variable `ANYSCALE_BASE_URL` will be used, or
            "https://api.endpoints.anyscale.com/v1" if not set.
        api_key: the API key to authenticate the requests to the Anyscale API. Defaults to `None` which
            means that the value set for the environment variable `ANYSCALE_API_KEY` will be used, or
            `None` if not set.
        _api_key_env_var: the name of the environment variable to use for the API key.
            It is meant to be used internally.

    Examples:
        Generate text:

        ```python
        from fastdistill.models.llms import AnyscaleLLM

        llm = AnyscaleLLM(model="google/gemma-7b-it", api_key="api.key")

        llm.load()

        output = llm.generate_outputs(inputs=[[{"role": "user", "content": "Hello world!"}]])
        ```
    """

    base_url: Optional[RuntimeParameter[str]] = Field(
        default_factory=lambda: os.getenv(
            "ANYSCALE_BASE_URL", "https://api.endpoints.anyscale.com/v1"
        ),
        description="The base URL to use for the Anyscale API requests.",
    )
    api_key: Optional[RuntimeParameter[SecretStr]] = Field(
        default_factory=lambda: os.getenv(_ANYSCALE_API_KEY_ENV_VAR_NAME),
        description="The API key to authenticate the requests to the Anyscale API.",
    )

    _api_key_env_var: str = PrivateAttr(_ANYSCALE_API_KEY_ENV_VAR_NAME)
