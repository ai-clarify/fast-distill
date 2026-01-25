# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.pipeline import Pipeline
from fastdistill.steps import LoadDataFromDicts, StepInput, StepOutput, step


@step(inputs=["instruction"], outputs=["response"])
def SucceedAlways(inputs: StepInput) -> "StepOutput":
    for input in inputs:
        input["response"] = "This step always succeeds"
    yield inputs


def test_dry_run():
    load_dataset_name = "load_dataset"

    def get_pipeline():
        with Pipeline(name="other-pipe") as pipeline:
            load_dataset = LoadDataFromDicts(
                name=load_dataset_name,
                data=[
                    {"instruction": "Tell me a joke."},
                ]
                * 50,
                batch_size=20,
            )
            text_generation = SucceedAlways()

            load_dataset >> text_generation
        return pipeline

    # Test with and without parameters
    pipeline = get_pipeline()
    distiset = pipeline.dry_run(batch_size=2)
    assert len(distiset["default"]["train"]) == 2
    assert pipeline._dry_run is False

    pipeline = get_pipeline()
    distiset = pipeline.dry_run(parameters={load_dataset_name: {"batch_size": 8}})
    assert len(distiset["default"]["train"]) == 1
    assert pipeline._dry_run is False

    pipeline = get_pipeline()
    distiset = pipeline.run(
        parameters={load_dataset_name: {"batch_size": 10}}, use_cache=False
    )
    assert len(distiset["default"]["train"]) == 50
