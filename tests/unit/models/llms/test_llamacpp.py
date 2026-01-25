# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
import urllib.request
from typing import Any, Dict, Generator

import pytest

pytest.importorskip("llama_cpp")

from fastdistill.models.llms.llamacpp import LlamaCppLLM

from .utils import DummyUserDetail


def download_tinyllama() -> None:
    if not os.path.exists("tinyllama.gguf"):
        try:
            urllib.request.urlretrieve(
                "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf",
                "tinyllama.gguf",
            )
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"tinyllama download failed: {exc}")


@pytest.fixture(scope="module")
def llm() -> Generator[LlamaCppLLM, None, None]:
    download_tinyllama()

    llm = LlamaCppLLM(model_path="tinyllama.gguf", n_gpu_layers=0)  # type: ignore
    llm.load()

    yield llm


class TestLlamaCppLLM:
    def test_no_tokenizer_magpie_raise_value_error(self) -> None:
        download_tinyllama()

        with pytest.raises(
            ValueError,
            match="`use_magpie_template` cannot be `True` if `tokenizer_id` is `None`",
        ):
            LlamaCppLLM(
                model_path="tinyllama.gguf",
                use_magpie_template=True,
                magpie_pre_query_template="llama3",
            )

    def test_model_name(self, llm: LlamaCppLLM) -> None:
        assert llm.model_name == "tinyllama.gguf"

    def test_generate(self, llm: LlamaCppLLM) -> None:
        responses = llm.generate(
            inputs=[
                [{"role": "user", "content": "Hello, how are you?"}],
                [
                    {
                        "role": "user",
                        "content": "You're GPT2, you're old now but you still serves a purpose which is being used in unit tests.",
                    }
                ],
            ],
            num_generations=3,
        )
        assert len(responses) == 2
        generations = responses[0]["generations"]
        statistics = responses[0]["statistics"]
        assert len(generations) == 3
        assert "input_tokens" in statistics
        assert "output_tokens" in statistics

    @pytest.mark.parametrize(
        "structured_output, dump",
        [
            (
                None,
                {
                    "chat_format": None,
                    "extra_kwargs": {},
                    "n_batch": 512,
                    "n_ctx": 512,
                    "n_gpu_layers": 0,
                    "seed": 4294967295,
                    "generation_kwargs": {},
                    "structured_output": None,
                    "jobs_ids": None,
                    "offline_batch_generation_block_until_done": None,
                    "use_offline_batch_generation": False,
                    "type_info": {
                        "module": "fastdistill.models.llms.llamacpp",
                        "name": "LlamaCppLLM",
                    },
                    "verbose": False,
                    "magpie_pre_query_template": None,
                    "tokenizer_id": None,
                    "use_magpie_template": False,
                },
            ),
            (
                {
                    "schema": DummyUserDetail.model_json_schema(),
                    "format": "json",
                },
                {
                    "chat_format": None,
                    "extra_kwargs": {},
                    "n_batch": 512,
                    "n_ctx": 512,
                    "n_gpu_layers": 0,
                    "seed": 4294967295,
                    "generation_kwargs": {},
                    "structured_output": {
                        "schema": DummyUserDetail.model_json_schema(),
                        "format": "json",
                    },
                    "jobs_ids": None,
                    "offline_batch_generation_block_until_done": None,
                    "use_offline_batch_generation": False,
                    "type_info": {
                        "module": "fastdistill.models.llms.llamacpp",
                        "name": "LlamaCppLLM",
                    },
                    "verbose": False,
                    "magpie_pre_query_template": None,
                    "tokenizer_id": None,
                    "use_magpie_template": False,
                },
            ),
        ],
    )
    def test_serialization(
        self, structured_output: Dict[str, Any], dump: Dict[str, Any]
    ) -> None:
        llm = LlamaCppLLM(
            model_path="tinyllama.gguf",
            n_gpu_layers=0,
            structured_output=structured_output,
        )

        assert llm.dump() == dump
        assert isinstance(LlamaCppLLM.from_dict(dump), LlamaCppLLM)
