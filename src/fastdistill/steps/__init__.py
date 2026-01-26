# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: F401

import importlib
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastdistill.steps.argilla.preference import PreferenceToArgilla
    from fastdistill.steps.argilla.text_generation import TextGenerationToArgilla
    from fastdistill.steps.base import (
        GeneratorStep,
        GlobalStep,
        Step,
        StepInput,
        StepResources,
    )
    from fastdistill.steps.clustering.dbscan import DBSCAN
    from fastdistill.steps.clustering.text_clustering import TextClustering
    from fastdistill.steps.clustering.umap import UMAP
    from fastdistill.steps.columns.combine import CombineOutputs
    from fastdistill.steps.columns.expand import ExpandColumns
    from fastdistill.steps.columns.group import GroupColumns
    from fastdistill.steps.columns.keep import KeepColumns
    from fastdistill.steps.columns.merge import MergeColumns
    from fastdistill.steps.decorator import step
    from fastdistill.steps.deita import DeitaFiltering
    from fastdistill.steps.embeddings.embedding_generation import EmbeddingGeneration
    from fastdistill.steps.embeddings.nearest_neighbour import FaissNearestNeighbour
    from fastdistill.steps.fastdistill.canonicalize import CanonicalizeFields
    from fastdistill.steps.fastdistill.filtering import RuleFilter, SelectByBool
    from fastdistill.steps.fastdistill.hashing import ComputeHash
    from fastdistill.steps.fastdistill.manifest import WriteManifest
    from fastdistill.steps.fastdistill.quality_report import WriteQualityReport
    from fastdistill.steps.fastdistill.score_agreement import WriteScoreAgreementReport
    from fastdistill.steps.fastdistill.sql_eval import SQLiteExecEval
    from fastdistill.steps.fastdistill.timing import MarkTime, WriteTimingReport
    from fastdistill.steps.filtering.embedding import EmbeddingDedup
    from fastdistill.steps.filtering.minhash import MinHashDedup
    from fastdistill.steps.formatting.conversation import ConversationTemplate
    from fastdistill.steps.formatting.dpo import (
        FormatChatGenerationDPO,
        FormatTextGenerationDPO,
    )
    from fastdistill.steps.formatting.sft import (
        FormatChatGenerationSFT,
        FormatTextGenerationSFT,
    )
    from fastdistill.steps.generators.data import LoadDataFromDicts
    from fastdistill.steps.generators.data_sampler import DataSampler
    from fastdistill.steps.generators.huggingface import (
        LoadDataFromDisk,
        LoadDataFromFileSystem,
        LoadDataFromHub,
    )
    from fastdistill.steps.generators.utils import make_generator_step
    from fastdistill.steps.globals.huggingface import PushToHub
    from fastdistill.steps.reward_model import RewardModelScore
    from fastdistill.steps.truncate import TruncateTextColumn
    from fastdistill.typing import GeneratorStepOutput, StepOutput

_LAZY_IMPORTS = {
    "DBSCAN": "fastdistill.steps.clustering.dbscan:DBSCAN",
    "UMAP": "fastdistill.steps.clustering.umap:UMAP",
    "CanonicalizeFields": "fastdistill.steps.fastdistill.canonicalize:CanonicalizeFields",
    "CombineOutputs": "fastdistill.steps.columns.combine:CombineOutputs",
    "ComputeHash": "fastdistill.steps.fastdistill.hashing:ComputeHash",
    "ConversationTemplate": "fastdistill.steps.formatting.conversation:ConversationTemplate",
    "DataSampler": "fastdistill.steps.generators.data_sampler:DataSampler",
    "DeitaFiltering": "fastdistill.steps.deita:DeitaFiltering",
    "EmbeddingDedup": "fastdistill.steps.filtering.embedding:EmbeddingDedup",
    "EmbeddingGeneration": "fastdistill.steps.embeddings.embedding_generation:EmbeddingGeneration",
    "ExpandColumns": "fastdistill.steps.columns.expand:ExpandColumns",
    "FaissNearestNeighbour": "fastdistill.steps.embeddings.nearest_neighbour:FaissNearestNeighbour",
    "FormatChatGenerationDPO": "fastdistill.steps.formatting.dpo:FormatChatGenerationDPO",
    "FormatChatGenerationSFT": "fastdistill.steps.formatting.sft:FormatChatGenerationSFT",
    "FormatTextGenerationDPO": "fastdistill.steps.formatting.dpo:FormatTextGenerationDPO",
    "FormatTextGenerationSFT": "fastdistill.steps.formatting.sft:FormatTextGenerationSFT",
    "GeneratorStep": "fastdistill.steps.base:GeneratorStep",
    "GeneratorStepOutput": "fastdistill.typing:GeneratorStepOutput",
    "GlobalStep": "fastdistill.steps.base:GlobalStep",
    "GroupColumns": "fastdistill.steps.columns.group:GroupColumns",
    "KeepColumns": "fastdistill.steps.columns.keep:KeepColumns",
    "LoadDataFromDicts": "fastdistill.steps.generators.data:LoadDataFromDicts",
    "LoadDataFromDisk": "fastdistill.steps.generators.huggingface:LoadDataFromDisk",
    "LoadDataFromFileSystem": "fastdistill.steps.generators.huggingface:LoadDataFromFileSystem",
    "LoadDataFromHub": "fastdistill.steps.generators.huggingface:LoadDataFromHub",
    "MarkTime": "fastdistill.steps.fastdistill.timing:MarkTime",
    "MergeColumns": "fastdistill.steps.columns.merge:MergeColumns",
    "MinHashDedup": "fastdistill.steps.filtering.minhash:MinHashDedup",
    "PreferenceToArgilla": "fastdistill.steps.argilla.preference:PreferenceToArgilla",
    "PushToHub": "fastdistill.steps.globals.huggingface:PushToHub",
    "RewardModelScore": "fastdistill.steps.reward_model:RewardModelScore",
    "RuleFilter": "fastdistill.steps.fastdistill.filtering:RuleFilter",
    "SQLiteExecEval": "fastdistill.steps.fastdistill.sql_eval:SQLiteExecEval",
    "SelectByBool": "fastdistill.steps.fastdistill.filtering:SelectByBool",
    "Step": "fastdistill.steps.base:Step",
    "StepInput": "fastdistill.steps.base:StepInput",
    "StepOutput": "fastdistill.typing:StepOutput",
    "StepResources": "fastdistill.steps.base:StepResources",
    "TextClustering": "fastdistill.steps.clustering.text_clustering:TextClustering",
    "TextGenerationToArgilla": "fastdistill.steps.argilla.text_generation:TextGenerationToArgilla",
    "TruncateTextColumn": "fastdistill.steps.truncate:TruncateTextColumn",
    "WriteManifest": "fastdistill.steps.fastdistill.manifest:WriteManifest",
    "WriteQualityReport": "fastdistill.steps.fastdistill.quality_report:WriteQualityReport",
    "WriteScoreAgreementReport": "fastdistill.steps.fastdistill.score_agreement:WriteScoreAgreementReport",
    "WriteTimingReport": "fastdistill.steps.fastdistill.timing:WriteTimingReport",
    "make_generator_step": "fastdistill.steps.generators.utils:make_generator_step",
    "step": "fastdistill.steps.decorator:step",
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
    return sorted(
        list(sys.modules[__name__].__dict__.keys()) + list(_LAZY_IMPORTS.keys())
    )
