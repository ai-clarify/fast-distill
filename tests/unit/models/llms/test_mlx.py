# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import platform
from typing import Any, Dict, Generator

import pytest

pytest.importorskip("mlx_lm")

from fastdistill.models.llms.mlx import MlxLLM

from .utils import DummyUserDetail

RUNS_ON_APPLE_SILICON = platform.processor() == "arm" and platform.system() == "Darwin"


@pytest.fixture(scope="module")
def llm() -> Generator[MlxLLM, None, None]:
    if not RUNS_ON_APPLE_SILICON:
        pytest.skip("MLX only runs on Apple Silicon")
    llm = MlxLLM(path_or_hf_repo="mlx-community/Qwen2.5-0.5B-4bit")
    try:
        llm.load()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"MLX model load failed: {exc}")
    yield llm


@pytest.mark.skipif(
    not RUNS_ON_APPLE_SILICON,
    reason="MLX only runs on Apple Silicon",
)
class TestMlxLLM:
    def test_model_name(self, llm: MlxLLM) -> None:
        assert llm.path_or_hf_repo == "mlx-community/Qwen2.5-0.5B-4bit"

    def test_generate(self, llm: MlxLLM) -> None:
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
                    "path_or_hf_repo": "mlx-community/Qwen2.5-0.5B-4bit",
                    "generation_kwargs": {},
                    "structured_output": None,
                    "adapter_path": None,
                    "jobs_ids": None,
                    "offline_batch_generation_block_until_done": None,
                    "use_offline_batch_generation": False,
                    "magpie_pre_query_template": None,
                    "tokenizer_config": {},
                    "mlx_model_config": {},
                    "use_magpie_template": False,
                    "type_info": {
                        "module": "fastdistill.models.llms.mlx",
                        "name": "MlxLLM",
                    },
                },
            ),
            (
                {
                    "schema": DummyUserDetail.model_json_schema(),
                    "format": "json",
                },
                {
                    "path_or_hf_repo": "mlx-community/Qwen2.5-0.5B-4bit",
                    "generation_kwargs": {},
                    "magpie_pre_query_template": None,
                    "tokenizer_config": {},
                    "mlx_model_config": {},
                    "use_magpie_template": False,
                    "structured_output": {
                        "schema": DummyUserDetail.model_json_schema(),
                        "format": "json",
                    },
                    "adapter_path": None,
                    "jobs_ids": None,
                    "offline_batch_generation_block_until_done": None,
                    "use_offline_batch_generation": False,
                    "type_info": {
                        "module": "fastdistill.models.llms.mlx",
                        "name": "MlxLLM",
                    },
                },
            ),
        ],
    )
    def test_serialization(
        self, structured_output: Dict[str, Any], dump: Dict[str, Any]
    ) -> None:
        llm = MlxLLM(
            path_or_hf_repo="mlx-community/Qwen2.5-0.5B-4bit",
            structured_output=structured_output,
        )

        assert llm.dump() == dump
        assert isinstance(MlxLLM.from_dict(dump), MlxLLM)
