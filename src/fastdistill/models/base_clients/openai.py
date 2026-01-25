# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
from typing import TYPE_CHECKING, Dict, Optional

from pydantic import BaseModel, Field, PrivateAttr, SecretStr

from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.typing import InstructorStructuredOutputType

if TYPE_CHECKING:
    from openai import AsyncOpenAI, OpenAI


_OPENAI_API_KEY_ENV_VAR_NAME = "OPENAI_API_KEY"


class OpenAIBaseClient(BaseModel):
    model: str
    base_url: Optional[RuntimeParameter[str]] = Field(
        default_factory=lambda: os.getenv(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        ),
        description="The base URL to use for the OpenAI API requests.",
    )
    api_key: Optional[RuntimeParameter[SecretStr]] = Field(
        default_factory=lambda: os.getenv(_OPENAI_API_KEY_ENV_VAR_NAME),
        description="The API key to authenticate the requests to the OpenAI API.",
    )  # type: ignore
    default_headers: Optional[RuntimeParameter[Dict[str, str]]] = Field(
        default=None,
        description="The default headers to use for the OpenAI API requests.",
    )
    max_retries: RuntimeParameter[int] = Field(
        default=6,
        description="The maximum number of times to retry the request to the API before"
        " failing.",
    )
    timeout: RuntimeParameter[int] = Field(
        default=120,
        description="The maximum time in seconds to wait for a response from the API.",
    )
    structured_output: Optional[RuntimeParameter[InstructorStructuredOutputType]] = (
        Field(
            default=None,
            description="The structured output format to use across all the generations.",
        )
    )

    _api_key_env_var: str = PrivateAttr(_OPENAI_API_KEY_ENV_VAR_NAME)
    _client: "OpenAI" = PrivateAttr(None)  # type: ignore
    _aclient: "AsyncOpenAI" = PrivateAttr(None)  # type: ignore

    def load(self) -> None:
        """Loads the `AsyncOpenAI` client to benefit from async requests."""

        try:
            from openai import AsyncOpenAI, OpenAI
        except ImportError as ie:
            raise ImportError(
                "OpenAI Python client is not installed. Please install it using"
                " `pip install 'fastdistill[openai]'`."
            ) from ie

        if self.api_key is None:
            raise ValueError(
                f"To use `{self.__class__.__name__}` an API key must be provided via `api_key`"
                f" attribute or runtime parameter, or set the environment variable `{self._api_key_env_var}`."
            )

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key.get_secret_value(),
            max_retries=self.max_retries,  # type: ignore
            timeout=self.timeout,
            default_headers=self.default_headers,
        )

        self._aclient = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key.get_secret_value(),
            max_retries=self.max_retries,  # type: ignore
            timeout=self.timeout,
            default_headers=self.default_headers,
        )

        if self.structured_output:
            # This applies only to the LLMs.
            result = self._prepare_structured_output(
                structured_output=self.structured_output,
                client=self._aclient,
                framework="openai",
            )
            self._aclient = result.get("client")  # type: ignore
            if structured_output := result.get("structured_output"):
                self.structured_output = structured_output

    def unload(self) -> None:
        """Set clients to `None` as they both contain `thread._RLock` which cannot be pickled
        in case an exception is raised and has to be handled in the main process"""

        self._client = None  # type: ignore
        self._aclient = None  # type: ignore
        self.default_headers = None
        self.structured_output = None

    @property
    def model_name(self) -> str:
        """Returns the model name used for the LLM."""
        return self.model
