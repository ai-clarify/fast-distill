# Copyright 2026 cklxx
#
# Licensed under the MIT License.


from fastdistill.constants import FASTDISTILL_METADATA_KEY
from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.columns.group import GroupColumns


class TestGroupColumns:
    def test_init(self) -> None:
        task = GroupColumns(
            name="group-columns",
            columns=["a", "b"],
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        assert task.inputs == ["a", "b"]
        assert task.outputs == ["grouped_a", "grouped_b"]

        task = GroupColumns(
            name="group-columns",
            columns=["a", "b"],
            output_columns=["c", "d"],
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        assert task.inputs == ["a", "b"]
        assert task.outputs == ["c", "d"]

    def test_process(self) -> None:
        group = GroupColumns(
            name="group-columns",
            columns=["a", "b"],
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        output = next(
            group.process(
                [{"a": 1, "b": 2, FASTDISTILL_METADATA_KEY: {"model": "model-1"}}],
                [{"a": 3, "b": 4, FASTDISTILL_METADATA_KEY: {"model": "model-2"}}],
            )
        )
        assert output == [
            {
                "grouped_a": [1, 3],
                "grouped_b": [2, 4],
                FASTDISTILL_METADATA_KEY: {"model": ["model-1", "model-2"]},
            }
        ]
