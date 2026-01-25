# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.columns.keep import KeepColumns


class TestKeepColumns:
    def test_init(self) -> None:
        task = KeepColumns(
            name="keep-columns",
            columns=["a", "b"],
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        assert task.inputs == ["a", "b"]
        assert task.outputs == ["a", "b"]

    def test_process(self) -> None:
        combine = KeepColumns(
            name="keep-columns",
            columns=["a", "b"],
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        output = next(combine.process([{"a": 1, "b": 2, "c": 3, "d": 4}]))
        assert output == [{"a": 1, "b": 2}]

    def test_process_preserve_order(self) -> None:
        combine = KeepColumns(
            name="keep-columns",
            columns=["b", "a"],
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        output = next(combine.process([{"a": 1, "b": 2, "c": 3, "d": 4}]))
        assert output == [{"b": 2, "a": 1}]
