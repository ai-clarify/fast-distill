# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
import sys
from typing import Any, Dict
from unittest import mock

import nest_asyncio
import pytest

from fastdistill.models.llms.cohere import CohereLLM

from .utils import DummyUserDetail

pytest.importorskip("cohere")
tokenizers = pytest.importorskip("tokenizers")
Tokenizer = tokenizers.Tokenizer


@mock.patch("cohere.AsyncClient")
class TestCohereLLM:
    def test_cohere_llm(self, _: mock.MagicMock) -> None:
        llm = CohereLLM(model="command-r", api_key="api.key")

        assert isinstance(llm, CohereLLM)
        assert llm.model_name == "command-r"

    def test_cohere_llm_env_vars(self, _: mock.MagicMock) -> None:
        with mock.patch.dict(os.environ, clear=True):
            os.environ["COHERE_API_KEY"] = "another.api.key"
            os.environ["COHERE_BASE_URL"] = "https://example.com"

            llm = CohereLLM(model="command-r")

            assert isinstance(llm, CohereLLM)
            assert llm.model_name == "command-r"
            assert llm.base_url == "https://example.com"
            assert llm.api_key.get_secret_value() == "another.api.key"  # type: ignore

    @pytest.mark.asyncio
    async def test_agenerate(self, mock_async_client: mock.MagicMock) -> None:
        llm = CohereLLM(model="command-r")
        llm._aclient = mock_async_client  # type: ignore

        mocked_completion = mock.Mock(text="Aenean hendrerit aliquam velit...")
        llm._aclient.chat = mock.AsyncMock(return_value=mocked_completion)

        llm._tokenizer = Tokenizer.from_pretrained("bert-base-uncased")

        result = await llm.agenerate(
            input=[
                {"role": "system", "content": ""},
                {
                    "role": "user",
                    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                },
            ]
        )
        assert result == {
            "generations": ["Aenean hendrerit aliquam velit..."],
            "statistics": {"input_tokens": [25], "output_tokens": [16]},
        }

    @pytest.mark.skipif(
        sys.version_info < (3, 9), reason="`cohere` requires Python 3.9 or higher"
    )
    @pytest.mark.asyncio
    async def test_agenerate_structured(
        self, mock_async_client: mock.MagicMock
    ) -> None:
        llm = CohereLLM(
            model="command-r",
            structured_output={
                "schema": DummyUserDetail,
                "mode": "tool_call",
                "max_retries": 1,
            },
        )
        llm._aclient = mock_async_client  # type: ignore

        sample_user = DummyUserDetail(name="John Doe", age=30)

        llm._aclient.chat = mock.AsyncMock(return_value=sample_user)
        llm._tokenizer = Tokenizer.from_pretrained("bert-base-uncased")

        generation = await llm.agenerate(
            input=[
                {"role": "system", "content": ""},
                {
                    "role": "user",
                    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                },
            ]
        )
        assert generation == {
            "generations": [sample_user.model_dump_json()],
            "statistics": {"input_tokens": [25], "output_tokens": [26]},
        }

    @pytest.mark.asyncio
    async def test_generate(self, mock_async_client: mock.MagicMock) -> None:
        llm = CohereLLM(model="command-r")
        llm._aclient = mock_async_client  # type: ignore

        mocked_completion = mock.Mock(text="Aenean hendrerit aliquam velit...")
        llm._aclient.chat = mock.AsyncMock(return_value=mocked_completion)

        llm._tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
        nest_asyncio.apply()

        result = llm.generate(
            inputs=[
                [
                    {"role": "system", "content": ""},
                    {
                        "role": "user",
                        "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    },
                ]
            ]
        )
        assert result == [
            {
                "generations": ["Aenean hendrerit aliquam velit..."],
                "statistics": {"input_tokens": [25], "output_tokens": [16]},
            }
        ]

    @pytest.mark.parametrize(
        "structured_output, dump",
        [
            (
                None,
                {
                    "model": "command-r",
                    "generation_kwargs": {},
                    "base_url": "https://api.cohere.ai/v1",
                    "timeout": 120,
                    "client_name": "fastdistill",
                    "structured_output": None,
                    "jobs_ids": None,
                    "offline_batch_generation_block_until_done": None,
                    "use_offline_batch_generation": False,
                    "type_info": {
                        "module": "fastdistill.models.llms.cohere",
                        "name": "CohereLLM",
                    },
                },
            ),
            (
                {
                    "schema": DummyUserDetail.model_json_schema(),
                    "mode": "tool_call",
                    "max_retries": 1,
                },
                {
                    "model": "command-r",
                    "generation_kwargs": {},
                    "base_url": "https://api.cohere.ai/v1",
                    "timeout": 120,
                    "client_name": "fastdistill",
                    "structured_output": {
                        "schema": DummyUserDetail.model_json_schema(),
                        "mode": "tool_call",
                        "max_retries": 1,
                    },
                    "jobs_ids": None,
                    "offline_batch_generation_block_until_done": None,
                    "use_offline_batch_generation": False,
                    "type_info": {
                        "module": "fastdistill.models.llms.cohere",
                        "name": "CohereLLM",
                    },
                },
            ),
        ],
    )
    def test_serialization(
        self, _: mock.MagicMock, structured_output: Dict[str, Any], dump: Dict[str, Any]
    ) -> None:
        llm = CohereLLM(model="command-r", structured_output=structured_output)

        assert llm.dump() == dump
        assert isinstance(CohereLLM.from_dict(dump), CohereLLM)
