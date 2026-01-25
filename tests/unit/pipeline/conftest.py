# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

from fastdistill.pipeline._dag import DAG
from fastdistill.pipeline.batch_manager import _BatchManager
from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.base import GeneratorStep, GlobalStep, Step

from .utils import DummyGeneratorStep, DummyGlobalStep, DummyStep1, DummyStep2


@pytest.fixture(name="pipeline")
def pipeline_fixture() -> Pipeline:
    return Pipeline(name="unit-test-pipeline")


@pytest.fixture(name="dummy_step_1")
def dummy_step_1_fixture(pipeline: "Pipeline") -> DummyStep1:
    return DummyStep1(name="dummy_step_1", pipeline=pipeline)


@pytest.fixture(name="dummy_step_2")
def dummy_step_2_fixture(pipeline: "Pipeline") -> DummyStep2:
    return DummyStep2(name="dummy_step_2", pipeline=pipeline)


@pytest.fixture(name="dummy_generator_step")
def dummy_generator_step_fixture(pipeline: "Pipeline") -> DummyGeneratorStep:
    return DummyGeneratorStep(name="dummy_generator_step", pipeline=pipeline)


@pytest.fixture(name="dummy_global_step")
def dummy_global_step_fixture(pipeline: "Pipeline") -> DummyGlobalStep:
    return DummyGlobalStep(name="dummy_global_step", pipeline=pipeline)


@pytest.fixture(name="dummy_dag")
def dummy_dag_fixture(
    dummy_generator_step: "GeneratorStep",
    dummy_step_1: "Step",
    dummy_step_2: "Step",
    dummy_global_step: "GlobalStep",
) -> DAG:
    dag = DAG()
    dag.add_step(dummy_generator_step)
    dag.add_step(dummy_step_1)
    dag.add_step(dummy_step_2)
    dag.add_step(dummy_global_step)
    dag.add_edge("dummy_generator_step", "dummy_step_1")
    dag.add_edge("dummy_generator_step", "dummy_global_step")
    dag.add_edge("dummy_step_1", "dummy_step_2")
    return dag


@pytest.fixture(name="dummy_batch_manager")
def dummy_batch_manager_from_dag_fixture(dummy_dag: DAG) -> _BatchManager:
    return _BatchManager.from_dag(dummy_dag)
