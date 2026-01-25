# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
from typing import Generator

import pytest

if not (
    os.getenv("HF_TOKEN")
    or os.getenv("HUGGINGFACE_TOKEN")
    or os.getenv("HUGGINGFACE_HUB_TOKEN")
):
    pytest.skip(
        "Hugging Face token required for private test models", allow_module_level=True
    )

from fastdistill.models.llms.huggingface.transformers import TransformersLLM
from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.tasks.generate_embeddings import GenerateEmbeddings


@pytest.fixture(scope="module")
def transformers_llm() -> Generator[TransformersLLM, None, None]:
    llm = TransformersLLM(
        model="fastdistill-internal-testing/tiny-random-mistral",
        cuda_devices=[],
    )
    try:
        llm.load()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Transformers model load failed: {exc}")

    yield llm


class TestGenerateEmbeddings:
    def test_process(self, transformers_llm: TransformersLLM) -> None:
        task = GenerateEmbeddings(
            name="task",
            llm=transformers_llm,
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        result = next(task.process([{"text": "Hello, how are you?"}]))

        assert "embedding" in result[0]
        assert len(result[0]["embedding"]) == 128
