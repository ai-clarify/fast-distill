# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.utils.lazy_imports import load_by_name


def test_load_by_name_caches() -> None:
    namespace = {}
    mapping = {"Docs": "fastdistill.constants:FASTDISTILL_DOCS_URL"}
    value = load_by_name("Docs", mapping, namespace)
    assert value == namespace["Docs"]


def test_models_lazy_attr_loads() -> None:
    import fastdistill.models as models

    if "LLM" in models.__dict__:
        del models.__dict__["LLM"]

    assert "LLM" not in models.__dict__
    _ = models.LLM
    assert "LLM" in models.__dict__


def test_steps_lazy_attr_loads() -> None:
    import fastdistill.steps as steps

    if "GeneratorStep" in steps.__dict__:
        del steps.__dict__["GeneratorStep"]

    assert "GeneratorStep" not in steps.__dict__
    _ = steps.GeneratorStep
    assert "GeneratorStep" in steps.__dict__


def test_pipeline_lazy_attr_loads() -> None:
    import fastdistill.pipeline as pipeline

    if "Pipeline" in pipeline.__dict__:
        del pipeline.__dict__["Pipeline"]

    assert "Pipeline" not in pipeline.__dict__
    _ = pipeline.Pipeline
    assert "Pipeline" in pipeline.__dict__
