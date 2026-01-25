# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import nest_asyncio
import pytest

pytest.importorskip("litellm")

from fastdistill.models.llms.litellm import LiteLLM


@pytest.fixture(params=["mistral/mistral-tiny", "gpt-4"])
def model(request) -> list:
    return request.param


@patch("litellm.acompletion")
class TestLiteLLM:
    def test_litellm_llm(self, _: MagicMock, model: str) -> None:
        llm = LiteLLM(model=model)  # type: ignore
        assert isinstance(llm, LiteLLM)
        assert llm.model_name == model

    @pytest.mark.asyncio
    async def test_agenerate(self, mock_litellm: MagicMock, model: str) -> None:
        llm = LiteLLM(model=model)  # type: ignore
        llm._aclient = mock_litellm

        mocked_completion = Mock(
            choices=[Mock(message=Mock(content=" Aenean hendrerit aliquam velit. ..."))]
        )
        llm._aclient = AsyncMock(return_value=mocked_completion)

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
            "generations": [" Aenean hendrerit aliquam velit. ..."],
            "statistics": {"input_tokens": [21], "output_tokens": [11]},
        }

    @pytest.mark.asyncio
    async def test_generate(self, mock_litellm: MagicMock, model: str) -> None:
        llm = LiteLLM(model=model)  # type: ignore
        llm._aclient = mock_litellm

        mocked_completion = Mock(
            choices=[Mock(message=Mock(content=" Aenean hendrerit aliquam velit. ..."))]
        )
        llm._aclient = AsyncMock(return_value=mocked_completion)

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
                "generations": [" Aenean hendrerit aliquam velit. ..."],
                "statistics": {"input_tokens": [21], "output_tokens": [11]},
            }
        ]

    def test_serialization(self, _: MagicMock, model: str) -> None:
        llm = LiteLLM(model=model)  # type: ignore

        _dump = {
            "model": model,
            "verbose": False,
            "structured_output": None,
            "jobs_ids": None,
            "offline_batch_generation_block_until_done": None,
            "use_offline_batch_generation": False,
            "type_info": {
                "module": "fastdistill.models.llms.litellm",
                "name": "LiteLLM",
            },
            "generation_kwargs": {},
        }

        assert llm.dump() == _dump
        assert isinstance(LiteLLM.from_dict(_dump), LiteLLM)
