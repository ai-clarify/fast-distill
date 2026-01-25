# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
from typing import TYPE_CHECKING, Dict, List

from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.models.llms.huggingface.transformers import TransformersLLM
from fastdistill.models.llms.openai import OpenAILLM
from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.base import Step, StepInput
from fastdistill.steps.generators.huggingface import LoadDataFromHub
from fastdistill.steps.tasks.text_generation import TextGeneration

if TYPE_CHECKING:
    from fastdistill.typing import StepOutput


class RenameColumns(Step):
    rename_mappings: RuntimeParameter[Dict[str, str]] = None

    @property
    def inputs(self) -> List[str]:
        return []

    @property
    def outputs(self) -> List[str]:
        return list(self.rename_mappings.values())  # type: ignore

    def process(self, *inputs: StepInput) -> "StepOutput":
        outputs = []
        for input in inputs:
            outputs = []
            for item in input:
                outputs.append(
                    {self.rename_mappings.get(k, k): v for k, v in item.items()}  # type: ignore
                )
            yield outputs


def test_pipeline_with_llms_serde() -> None:
    with Pipeline(name="unit-test-pipeline") as pipeline:
        load_hub_dataset = LoadDataFromHub(name="load_dataset")
        rename_columns = RenameColumns(name="rename_columns")
        load_hub_dataset.connect(rename_columns)

        os.environ["OPENAI_API_KEY"] = "sk-***"
        generate_response = TextGeneration(
            name="generate_response",
            llm=OpenAILLM(model="gpt-3.5-turbo"),
            output_mappings={"generation": "output"},
        )
        rename_columns.connect(generate_response)

        generate_response_mini = TextGeneration(
            name="generate_response_mini",
            llm=TransformersLLM(model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"),
            output_mappings={"generation": "output"},
        )
        rename_columns.connect(generate_response_mini)
        dump = pipeline.dump()

    with Pipeline(name="unit-test-pipeline") as pipe:
        pipe = pipe.from_dict(dump)

    assert "load_dataset" in pipe.dag.G
    assert "rename_columns" in pipe.dag.G
    assert "generate_response" in pipe.dag.G
    assert "generate_response_mini" in pipe.dag.G
