# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: F401

import importlib
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastdistill.steps.tasks.apigen.execution_checker import APIGenExecutionChecker
    from fastdistill.steps.tasks.apigen.generator import APIGenGenerator
    from fastdistill.steps.tasks.apigen.semantic_checker import APIGenSemanticChecker
    from fastdistill.steps.tasks.argilla_labeller import ArgillaLabeller
    from fastdistill.steps.tasks.base import GeneratorTask, ImageTask, Task
    from fastdistill.steps.tasks.clair import CLAIR
    from fastdistill.steps.tasks.complexity_scorer import ComplexityScorer
    from fastdistill.steps.tasks.decorator import task
    from fastdistill.steps.tasks.evol_instruct.base import EvolInstruct
    from fastdistill.steps.tasks.evol_instruct.evol_complexity.base import (
        EvolComplexity,
    )
    from fastdistill.steps.tasks.evol_instruct.evol_complexity.generator import (
        EvolComplexityGenerator,
    )
    from fastdistill.steps.tasks.evol_instruct.generator import EvolInstructGenerator
    from fastdistill.steps.tasks.evol_quality.base import EvolQuality
    from fastdistill.steps.tasks.generate_embeddings import GenerateEmbeddings
    from fastdistill.steps.tasks.genstruct import Genstruct
    from fastdistill.steps.tasks.image_generation import ImageGeneration
    from fastdistill.steps.tasks.improving_text_embeddings import (
        BitextRetrievalGenerator,
        EmbeddingTaskGenerator,
        GenerateLongTextMatchingData,
        GenerateShortTextMatchingData,
        GenerateTextClassificationData,
        GenerateTextRetrievalData,
        MonolingualTripletGenerator,
    )
    from fastdistill.steps.tasks.instruction_backtranslation import (
        InstructionBacktranslation,
    )
    from fastdistill.steps.tasks.magpie.base import Magpie
    from fastdistill.steps.tasks.magpie.generator import MagpieGenerator
    from fastdistill.steps.tasks.math_shepherd.completer import MathShepherdCompleter
    from fastdistill.steps.tasks.math_shepherd.generator import MathShepherdGenerator
    from fastdistill.steps.tasks.math_shepherd.utils import FormatPRM
    from fastdistill.steps.tasks.pair_rm import PairRM
    from fastdistill.steps.tasks.prometheus_eval import PrometheusEval
    from fastdistill.steps.tasks.quality_scorer import QualityScorer
    from fastdistill.steps.tasks.self_instruct import SelfInstruct
    from fastdistill.steps.tasks.sentence_transformers import GenerateSentencePair
    from fastdistill.steps.tasks.structured_generation import StructuredGeneration
    from fastdistill.steps.tasks.text_classification import TextClassification
    from fastdistill.steps.tasks.text_generation import ChatGeneration, TextGeneration
    from fastdistill.steps.tasks.text_generation_with_image import (
        TextGenerationWithImage,
    )
    from fastdistill.steps.tasks.ultrafeedback import UltraFeedback
    from fastdistill.steps.tasks.urial import URIAL
    from fastdistill.typing import ChatItem, ChatType

_LAZY_IMPORTS = {
    "CLAIR": "fastdistill.steps.tasks.clair:CLAIR",
    "URIAL": "fastdistill.steps.tasks.urial:URIAL",
    "APIGenExecutionChecker": "fastdistill.steps.tasks.apigen.execution_checker:APIGenExecutionChecker",
    "APIGenGenerator": "fastdistill.steps.tasks.apigen.generator:APIGenGenerator",
    "APIGenSemanticChecker": "fastdistill.steps.tasks.apigen.semantic_checker:APIGenSemanticChecker",
    "ArgillaLabeller": "fastdistill.steps.tasks.argilla_labeller:ArgillaLabeller",
    "BitextRetrievalGenerator": "fastdistill.steps.tasks.improving_text_embeddings:BitextRetrievalGenerator",
    "ChatGeneration": "fastdistill.steps.tasks.text_generation:ChatGeneration",
    "ChatItem": "fastdistill.typing:ChatItem",
    "ChatType": "fastdistill.typing:ChatType",
    "ComplexityScorer": "fastdistill.steps.tasks.complexity_scorer:ComplexityScorer",
    "EmbeddingTaskGenerator": "fastdistill.steps.tasks.improving_text_embeddings:EmbeddingTaskGenerator",
    "EvolComplexity": "fastdistill.steps.tasks.evol_instruct.evol_complexity.base:EvolComplexity",
    "EvolComplexityGenerator": "fastdistill.steps.tasks.evol_instruct.evol_complexity.generator:EvolComplexityGenerator",
    "EvolInstruct": "fastdistill.steps.tasks.evol_instruct.base:EvolInstruct",
    "EvolInstructGenerator": "fastdistill.steps.tasks.evol_instruct.generator:EvolInstructGenerator",
    "EvolQuality": "fastdistill.steps.tasks.evol_quality.base:EvolQuality",
    "FormatPRM": "fastdistill.steps.tasks.math_shepherd.utils:FormatPRM",
    "GenerateEmbeddings": "fastdistill.steps.tasks.generate_embeddings:GenerateEmbeddings",
    "GenerateLongTextMatchingData": "fastdistill.steps.tasks.improving_text_embeddings:GenerateLongTextMatchingData",
    "GenerateSentencePair": "fastdistill.steps.tasks.sentence_transformers:GenerateSentencePair",
    "GenerateShortTextMatchingData": "fastdistill.steps.tasks.improving_text_embeddings:GenerateShortTextMatchingData",
    "GenerateTextClassificationData": "fastdistill.steps.tasks.improving_text_embeddings:GenerateTextClassificationData",
    "GenerateTextRetrievalData": "fastdistill.steps.tasks.improving_text_embeddings:GenerateTextRetrievalData",
    "GeneratorTask": "fastdistill.steps.tasks.base:GeneratorTask",
    "Genstruct": "fastdistill.steps.tasks.genstruct:Genstruct",
    "ImageGeneration": "fastdistill.steps.tasks.image_generation:ImageGeneration",
    "ImageTask": "fastdistill.steps.tasks.base:ImageTask",
    "InstructionBacktranslation": "fastdistill.steps.tasks.instruction_backtranslation:InstructionBacktranslation",
    "Magpie": "fastdistill.steps.tasks.magpie.base:Magpie",
    "MagpieGenerator": "fastdistill.steps.tasks.magpie.generator:MagpieGenerator",
    "MathShepherdCompleter": "fastdistill.steps.tasks.math_shepherd.completer:MathShepherdCompleter",
    "MathShepherdGenerator": "fastdistill.steps.tasks.math_shepherd.generator:MathShepherdGenerator",
    "MonolingualTripletGenerator": "fastdistill.steps.tasks.improving_text_embeddings:MonolingualTripletGenerator",
    "PairRM": "fastdistill.steps.tasks.pair_rm:PairRM",
    "PrometheusEval": "fastdistill.steps.tasks.prometheus_eval:PrometheusEval",
    "QualityScorer": "fastdistill.steps.tasks.quality_scorer:QualityScorer",
    "SelfInstruct": "fastdistill.steps.tasks.self_instruct:SelfInstruct",
    "StructuredGeneration": "fastdistill.steps.tasks.structured_generation:StructuredGeneration",
    "Task": "fastdistill.steps.tasks.base:Task",
    "TextClassification": "fastdistill.steps.tasks.text_classification:TextClassification",
    "TextGeneration": "fastdistill.steps.tasks.text_generation:TextGeneration",
    "TextGenerationWithImage": "fastdistill.steps.tasks.text_generation_with_image:TextGenerationWithImage",
    "UltraFeedback": "fastdistill.steps.tasks.ultrafeedback:UltraFeedback",
    "task": "fastdistill.steps.tasks.decorator:task",
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str) -> object:
    if name in _LAZY_IMPORTS:
        return _load_by_name(name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def _load_by_name(name: str) -> object:
    target = _LAZY_IMPORTS[name]
    module_path, attr = target.rsplit(":", 1)
    value = getattr(importlib.import_module(module_path), attr)
    sys.modules[__name__].__dict__[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
