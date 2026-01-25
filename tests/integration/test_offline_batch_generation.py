# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, List, Union

from fastdistill.exceptions import FastDistillOfflineBatchGenerationNotFinishedException
from fastdistill.models.llms import LLM
from fastdistill.pipeline import Pipeline
from fastdistill.steps import LoadDataFromDicts
from fastdistill.steps.tasks import TextGeneration

if TYPE_CHECKING:
    from fastdistill.typing import FormattedInput, GenerateOutput


class DummyOfflineBatchGenerateLLM(LLM):
    def load(self) -> None:
        super().load()

    @property
    def model_name(self) -> str:
        return "test"

    def generate(  # type: ignore
        self, inputs: "FormattedInput", num_generations: int = 1
    ) -> "GenerateOutput":
        return ["output" for _ in range(num_generations)]

    def offline_batch_generate(
        self,
        inputs: Union[List["FormattedInput"], None] = None,
        num_generations: int = 1,
        **kwargs: Any,
    ) -> List["GenerateOutput"]:
        # Simulate that the first time we create the jobs
        if not self.jobs_ids:
            self.jobs_ids = ("1234", "5678")
            raise FastDistillOfflineBatchGenerationNotFinishedException(
                jobs_ids=self.jobs_ids  # type: ignore
            )
        return [
            {
                "generations": [f"output {i}" for i in range(num_generations)],
                "statistics": {
                    "input_tokens": [12] * num_generations,
                    "output_tokens": [12] * num_generations,
                },
            }
        ] * len(inputs)


def test_offline_batch_generation() -> None:
    with TemporaryDirectory() as tmp_dir:
        with Pipeline(cache_dir=tmp_dir) as pipeline:
            load_data = LoadDataFromDicts(
                data=[{"instruction": f"{i} instruction"} for i in range(100)]
            )

            text_generation = TextGeneration(
                llm=DummyOfflineBatchGenerateLLM(use_offline_batch_generation=True)
            )

            load_data >> text_generation

        distiset = pipeline.run()

        # First call no results
        assert len(distiset) == 0

        distiset = pipeline.run(use_cache=True)
        assert len(distiset) == 1
