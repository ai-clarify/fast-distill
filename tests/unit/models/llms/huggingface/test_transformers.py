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


# load the model just once for all the tests in the module
@pytest.fixture(scope="module")
def transformers_llm() -> Generator[TransformersLLM, None, None]:
    llm = TransformersLLM(
        model="fastdistill-internal-testing/tiny-random-mistral",
        model_kwargs={"is_decoder": True},
        cuda_devices=[],
        torch_dtype="float16",
    )
    try:
        llm.load()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Transformers model load failed: {exc}")

    yield llm


class TestTransformersLLM:
    def test_model_name(self, transformers_llm: TransformersLLM) -> None:
        assert (
            transformers_llm.model_name
            == "fastdistill-internal-testing/tiny-random-mistral"
        )

    def test_prepare_input(self, transformers_llm: TransformersLLM) -> None:
        assert (
            transformers_llm.prepare_input([{"role": "user", "content": "Hello"}])
            == "<s> [INST] Hello [/INST]"
        )

    def test_prepare_input_no_chat_template(
        self, transformers_llm: TransformersLLM
    ) -> None:
        transformers_llm._pipeline.tokenizer.chat_template = None
        assert (
            transformers_llm.prepare_input([{"role": "user", "content": "Hello"}])
            == "Hello"
        )

    def test_generate(self, transformers_llm: TransformersLLM) -> None:
        responses = transformers_llm.generate(
            inputs=[
                [{"role": "user", "content": "Hello, how are you?"}],
                [
                    {
                        "role": "user",
                        "content": "You're GPT2, you're old now but you still serve a purpose which is being used in unit tests.",
                    }
                ],
            ],
            num_generations=3,
        )
        # Note: It returns the following structure:
        # [
        #     {
        #         "generations": [text1, text2, text3],  # As much as num_generations
        #         "statistics": {
        #            "input_tokens": [7],
        #            "output_tokens": [128, 128, 128],  # The sum of the tokens of the generated texts
        #         },
        #     },
        #     {...}
        # ]
        assert len(responses) == 2
        generations = responses[0]["generations"]
        statistics = responses[0]["statistics"]
        assert len(generations) == 3
        assert "input_tokens" in statistics
        assert "output_tokens" in statistics

    def test_get_last_hidden_states(self, transformers_llm: TransformersLLM) -> None:
        inputs = [
            [{"role": "user", "content": "Hello, how are you?"}],
            [{"role": "user", "content": "Hello, you're in a unit test"}],
        ]
        last_hidden_states = transformers_llm.get_last_hidden_states(inputs)  # type: ignore

        assert last_hidden_states[0].shape == (7, 128)
        assert last_hidden_states[1].shape == (10, 128)
