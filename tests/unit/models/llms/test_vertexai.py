# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import nest_asyncio
import pytest

from fastdistill.models.llms.vertexai import VertexAILLM

vertexai_gen = pytest.importorskip("vertexai.generative_models")
Content = vertexai_gen.Content
GenerationConfig = vertexai_gen.GenerationConfig
Part = vertexai_gen.Part


@patch("vertexai.generative_models.GenerativeModel.generate_content_async")
class TestVertexAILLM:
    def test_openai_llm(self, _: MagicMock) -> None:
        llm = VertexAILLM(model="gemini-1.0-pro")
        assert isinstance(llm, VertexAILLM)
        assert llm.model_name == "gemini-1.0-pro"

    @pytest.mark.asyncio
    async def test_agenerate(self, mock_generative_model: MagicMock) -> None:
        llm = VertexAILLM(model="gemini-1.0-pro")
        llm._aclient = mock_generative_model
        llm._part_class = Part  # type: ignore
        llm._content_class = Content  # type: ignore
        llm._generation_config_class = GenerationConfig

        mocked_completion = Mock(
            candidates=[Mock(text=" Aenean hendrerit aliquam velit. ...")],
            usage_metadata=Mock(prompt_token_count=10, candidates_token_count=10),
        )
        llm._aclient.generate_content_async = AsyncMock(return_value=mocked_completion)

        result = await llm.agenerate(
            input=[
                {"role": "model", "content": ""},
                {
                    "role": "user",
                    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                },
            ]
        )
        assert result == {
            "generations": [" Aenean hendrerit aliquam velit. ..."],
            "statistics": {"input_tokens": [10], "output_tokens": [10]},
        }

    @pytest.mark.asyncio
    async def test_generate(self, mock_generative_model: MagicMock) -> None:
        llm = VertexAILLM(model="gemini-1.0-pro")
        llm._aclient = mock_generative_model
        llm._part_class = Part  # type: ignore
        llm._content_class = Content  # type: ignore
        llm._generation_config_class = GenerationConfig

        mocked_completion = Mock(
            candidates=[Mock(text=" Aenean hendrerit aliquam velit. ...")],
            usage_metadata=Mock(prompt_token_count=10, candidates_token_count=10),
        )
        llm._aclient.generate_content_async = AsyncMock(return_value=mocked_completion)

        nest_asyncio.apply()

        result = llm.generate(
            inputs=[
                [
                    {"role": "model", "content": "I am a model."},
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
                "statistics": {"input_tokens": [10], "output_tokens": [10]},
            }
        ]

    def test_serialization(self, _: MagicMock) -> None:
        llm = VertexAILLM(model="gemini-1.0-pro")

        _dump = {
            "model": "gemini-1.0-pro",
            "generation_kwargs": {},
            "jobs_ids": None,
            "offline_batch_generation_block_until_done": None,
            "use_offline_batch_generation": False,
            "type_info": {
                "module": "fastdistill.models.llms.vertexai",
                "name": "VertexAILLM",
            },
        }

        assert llm.dump() == _dump
        assert isinstance(VertexAILLM.from_dict(_dump), VertexAILLM)
