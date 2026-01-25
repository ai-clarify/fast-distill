# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.models.llms.moa import MOA_SYSTEM_PROMPT, MixtureOfAgentsLLM
from tests.unit.conftest import DummyAsyncLLM


class TestMixtureOfAgents:
    def test_model_name(self) -> None:
        llm = MixtureOfAgentsLLM(
            aggregator_llm=DummyAsyncLLM(),
            proposers_llms=[DummyAsyncLLM(), DummyAsyncLLM(), DummyAsyncLLM()],
        )

        assert llm.model_name == "moa-test-test-test-test"

    def test_build_moa_system_prompt(self) -> None:
        llm = MixtureOfAgentsLLM(
            aggregator_llm=DummyAsyncLLM(),
            proposers_llms=[DummyAsyncLLM(), DummyAsyncLLM(), DummyAsyncLLM()],
        )

        system_prompt = llm._build_moa_system_prompt(
            prev_outputs=["output1", "output2", "output3"]
        )

        assert (
            system_prompt == f"{MOA_SYSTEM_PROMPT}\n1. output1\n2. output2\n3. output3"
        )

    def test_inject_moa_system_prompt(self) -> None:
        llm = MixtureOfAgentsLLM(
            aggregator_llm=DummyAsyncLLM(),
            proposers_llms=[DummyAsyncLLM(), DummyAsyncLLM(), DummyAsyncLLM()],
        )

        results = llm._inject_moa_system_prompt(
            input=[
                {"role": "system", "content": "I'm a system prompt."},
            ],
            prev_outputs=["output1", "output2", "output3"],
        )

        assert results == [
            {
                "role": "system",
                "content": f"{MOA_SYSTEM_PROMPT}\n1. output1\n2. output2\n3. output3\n\nI'm a system prompt.",
            }
        ]
