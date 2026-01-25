# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from functools import partial
from typing import Union

import pytest

from fastdistill.models.mixins.magpie import MagpieChatTemplateMixin
from fastdistill.steps import tasks as tasks_
from tests.unit.conftest import DummyLLM

# The tasks not listed here don't have a print method (or don't have a print method that works)
tasks = [
    tasks_.ComplexityScorer,
    partial(tasks_.EvolInstruct, num_evolutions=1),
    partial(tasks_.EvolComplexity, num_evolutions=1),
    partial(tasks_.EvolComplexityGenerator, num_instructions=1),
    partial(tasks_.EvolInstructGenerator, num_instructions=1),
    partial(tasks_.EvolQuality, num_evolutions=1),
    tasks_.Genstruct,
    partial(
        tasks_.BitextRetrievalGenerator,
        source_language="English",
        target_language="Spanish",
        unit="sentence",
        difficulty="elementary school",
        high_score="4",
        low_score="2.5",
    ),
    partial(tasks_.EmbeddingTaskGenerator, category="text-retrieval"),
    tasks_.GenerateLongTextMatchingData,
    tasks_.GenerateShortTextMatchingData,
    tasks_.GenerateTextClassificationData,
    tasks_.GenerateTextRetrievalData,
    tasks_.MonolingualTripletGenerator,
    tasks_.InstructionBacktranslation,
    tasks_.Magpie,
    tasks_.MagpieGenerator,
    partial(tasks_.PrometheusEval, mode="absolute", rubric="factual-validity"),
    tasks_.QualityScorer,
    tasks_.SelfInstruct,
    partial(tasks_.GenerateSentencePair, action="paraphrase"),
    tasks_.UltraFeedback,
    tasks_.URIAL,
]


class TestLLM(DummyLLM, MagpieChatTemplateMixin):
    magpie_pre_query_template: Union[str, None] = "llama3"


llm = TestLLM()


@pytest.mark.parametrize("task", tasks)
def test_prints(task) -> None:
    t = task(llm=llm)
    t.load()
    t.print()
    t.unload()
