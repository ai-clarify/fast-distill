# Copyright 2026 cklxx
#
# Licensed under the MIT License.
import pytest

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.generators.data import LoadDataFromDicts


class TestLoadDataFromDicts:
    data = [{"instruction": "test"}] * 10

    def test_init(self) -> None:
        pipeline = Pipeline(name="unit-test-pipeline")
        data: list[dict[str, str]] = self.data
        task = LoadDataFromDicts(
            name="task", pipeline=pipeline, data=data, batch_size=10
        )
        assert task.data == data
        assert task.batch_size == 10

    def test_process(self) -> None:
        pipeline = Pipeline(name="unit-test-pipeline")
        data: list[dict[str, str]] = self.data
        batch_size = 1
        task = LoadDataFromDicts(
            name="task", pipeline=pipeline, data=data, batch_size=batch_size
        )

        result = task.process()
        for i in range(len(self.data) - batch_size):
            assert next(result) == ([self.data[i]], False)
        assert next(result) == ([self.data[-batch_size]], True)
        with pytest.raises(StopIteration):
            next(result)
