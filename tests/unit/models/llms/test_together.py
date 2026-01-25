# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
from unittest import mock

from fastdistill.models.llms.together import TogetherLLM


class TestTogetherLLM:
    model_id: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    def test_together_llm(self) -> None:
        llm = TogetherLLM(model=self.model_id, api_key="api.key")  # type: ignore

        assert isinstance(llm, TogetherLLM)
        assert llm.model_name == self.model_id

    def test_together_llm_env_vars(self) -> None:
        with mock.patch.dict(os.environ, clear=True):
            os.environ["TOGETHER_API_KEY"] = "another.api.key"
            os.environ["TOGETHER_BASE_URL"] = "https://example.com"

            llm = TogetherLLM(model=self.model_id)

            assert isinstance(llm, TogetherLLM)
            assert llm.model_name == self.model_id
            assert llm.base_url == "https://example.com"
            assert llm.api_key.get_secret_value() == "another.api.key"  # type: ignore

    def test_serialization(self) -> None:
        llm = TogetherLLM(model=self.model_id)

        _dump = {
            "model": self.model_id,
            "generation_kwargs": {},
            "max_retries": 6,
            "default_headers": None,
            "base_url": "https://api.together.xyz/v1",
            "timeout": 120,
            "structured_output": None,
            "jobs_ids": None,
            "offline_batch_generation_block_until_done": None,
            "use_offline_batch_generation": False,
            "type_info": {
                "module": "fastdistill.models.llms.together",
                "name": "TogetherLLM",
            },
        }

        assert llm.dump() == _dump
        assert isinstance(TogetherLLM.from_dict(_dump), TogetherLLM)
