# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, Literal, Type, Union

import pytest
from pydantic import BaseModel

pytest.importorskip("outlines")

from fastdistill.models.llms.huggingface.transformers import TransformersLLM
from fastdistill.steps.tasks.structured_outputs.outlines import (
    _is_outlines_version_below_0_1_0,
    model_to_schema,
)
from fastdistill.typing import OutlinesStructuredOutputType


class DummyUserTest(BaseModel):
    name: str
    last_name: str
    id: int


def _load_or_skip(llm: TransformersLLM) -> None:
    try:
        llm.load()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Transformers model load failed: {exc}")


DUMP_JSON = {
    "cuda_devices": "auto",
    "generation_kwargs": {},
    "magpie_pre_query_template": None,
    "jobs_ids": None,
    "offline_batch_generation_block_until_done": None,
    "use_offline_batch_generation": False,
    "structured_output": {
        "format": "json",
        "schema": {
            "properties": {
                "name": {"title": "Name", "type": "string"},
                "last_name": {"title": "Last Name", "type": "string"},
                "id": {"title": "Id", "type": "integer"},
            },
            "required": ["name", "last_name", "id"],
            "title": "DummyUserTest",
            "type": "object",
        },
    },
    "model": "openaccess-ai-collective/tiny-mistral",
    "revision": "main",
    "torch_dtype": "auto",
    "trust_remote_code": False,
    "model_kwargs": None,
    "tokenizer": None,
    "use_fast": True,
    "chat_template": None,
    "device": None,
    "device_map": None,
    "token": None,
    "use_magpie_template": False,
    "disable_cuda_device_placement": False,
    "type_info": {
        "module": "fastdistill.models.llms.huggingface.transformers",
        "name": "TransformersLLM",
    },
}

DUMP_REGEX = {
    "cuda_devices": "auto",
    "generation_kwargs": {},
    "magpie_pre_query_template": None,
    "jobs_ids": None,
    "offline_batch_generation_block_until_done": None,
    "use_offline_batch_generation": False,
    "structured_output": {
        "format": "regex",
        "schema": "((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)",
    },
    "model": "openaccess-ai-collective/tiny-mistral",
    "revision": "main",
    "torch_dtype": "auto",
    "trust_remote_code": False,
    "model_kwargs": None,
    "tokenizer": None,
    "use_fast": True,
    "chat_template": None,
    "device": None,
    "device_map": None,
    "token": None,
    "use_magpie_template": False,
    "disable_cuda_device_placement": False,
    "type_info": {
        "module": "fastdistill.models.llms.huggingface.transformers",
        "name": "TransformersLLM",
    },
}


class TestOutlinesIntegration:
    @pytest.mark.parametrize(
        "format, schema, prompt",
        [
            (
                "json",
                DummyUserTest,
                "Create a user profile with the fields name, last_name and id",
            ),
            (
                "json",
                model_to_schema(DummyUserTest),
                "Create a user profile with the fields name, last_name and id",
            ),
            (
                "regex",
                r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)",
                "What is the IP address of the Google DNS servers?",
            ),
        ],
    )
    def test_generation(
        self, format: str, schema: Union[str, Type[BaseModel]], prompt: str
    ) -> None:
        llm = TransformersLLM(
            model="fastdistill-internal-testing/tiny-random-mistral",
            structured_output=OutlinesStructuredOutputType(
                format=format, schema=schema
            ),
        )
        _load_or_skip(llm)

        prompt = [
            [{"role": "system", "content": ""}, {"role": "user", "content": prompt}]
        ]
        result = llm.generate(prompt, max_new_tokens=30, temperature=0.7)
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert "generations" in result[0] and "statistics" in result[0]

    @pytest.mark.parametrize(
        "format, schema, dump",
        [
            (
                "json",
                DummyUserTest,
                DUMP_JSON,
            ),
            (
                "json",
                model_to_schema(DummyUserTest),
                DUMP_JSON,
            ),
            (
                "regex",
                r"((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)",
                DUMP_REGEX,
            ),
        ],
    )
    def test_serialization(
        self,
        format: Literal["json", "regex"],
        schema: Union[str, Type[BaseModel]],
        dump: Dict[str, Any],
    ) -> None:
        llm = TransformersLLM(
            model="openaccess-ai-collective/tiny-mistral",
            structured_output=OutlinesStructuredOutputType(
                format=format, schema=schema
            ),
            token=None,
        )
        _load_or_skip(llm)
        assert llm.dump() == dump

    def test_load_from_dict(self) -> None:
        llm = TransformersLLM.from_dict(DUMP_JSON)
        assert isinstance(llm, TransformersLLM)
        _load_or_skip(llm)
        if _is_outlines_version_below_0_1_0():
            assert llm._prefix_allowed_tokens_fn is not None
            assert llm._logits_processor is None
        else:
            assert llm._prefix_allowed_tokens_fn is None
            assert llm._logits_processor is not None
