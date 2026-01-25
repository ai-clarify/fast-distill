# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.models.llms.base import LLM
from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.tasks.evol_instruct.evol_complexity.generator import (
    EvolComplexityGenerator,
)
from fastdistill.steps.tasks.evol_instruct.evol_complexity.utils import (
    GENERATION_MUTATION_TEMPLATES,
)


class TestEvolComplexityGenerator:
    def test_mutation_templates(self, dummy_llm: LLM) -> None:
        pipeline = Pipeline(name="unit-test-pipeline")
        task = EvolComplexityGenerator(
            name="task", llm=dummy_llm, num_instructions=2, pipeline=pipeline
        )
        assert task.name == "task"
        assert task.llm is dummy_llm
        assert task.num_instructions == 2
        assert task.mutation_templates == GENERATION_MUTATION_TEMPLATES
        assert "BREADTH" not in task.mutation_templates
