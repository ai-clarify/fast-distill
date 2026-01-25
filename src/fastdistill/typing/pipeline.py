# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    TypeVar,
    Union,
)

from typing_extensions import TypedDict

if TYPE_CHECKING:
    import pandas as pd
    from datasets import Dataset

    from fastdistill.mixins.runtime_parameters import RuntimeParameterInfo
    from fastdistill.steps.base import GeneratorStep, GlobalStep, Step

DownstreamConnectable = Union["Step", "GlobalStep"]
"""Alias for the `Step` types that can be connected as downstream steps."""

UpstreamConnectableSteps = TypeVar(
    "UpstreamConnectableSteps",
    bound=Union["Step", "GlobalStep", "GeneratorStep"],
)
"""Type for the `Step` types that can be connected as upstream steps."""

DownstreamConnectableSteps = TypeVar(
    "DownstreamConnectableSteps",
    bound=DownstreamConnectable,
    covariant=True,
)
"""Type for the `Step` types that can be connected as downstream steps."""


class StepLoadStatus(TypedDict):
    """Dict containing information about if one step was loaded/unloaded or if it's load
    failed"""

    name: str
    status: Literal["loaded", "unloaded", "load_failed"]


PipelineRuntimeParametersInfo = Dict[
    str, Union[List["RuntimeParameterInfo"], Dict[str, "RuntimeParameterInfo"]]
]
"""Alias for the information of the runtime parameters of a `Pipeline`."""

InputDataset = Union["Dataset", "pd.DataFrame", List[Dict[str, str]]]
"""Alias for the types we can process as input dataset."""

LoadGroups = Union[List[List[Any]], Literal["sequential_step_execution"]]
"""Alias for the types that can be used as load groups.

- if `List[List[Any]]`, it's a list containing lists of steps that have to be loaded in
isolation.
- if "sequential_step_execution", each step will be loaded in a different stage i.e. only
one step will be executed at a time.
"""
