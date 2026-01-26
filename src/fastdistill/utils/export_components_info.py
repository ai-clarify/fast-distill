# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import inspect
from typing import Iterable, List, Type, TypedDict

from fastdistill.models.embeddings.base import Embeddings
from fastdistill.models.image_generation.base import ImageGenerationModel
from fastdistill.models.llms.base import LLM
from fastdistill.registry import (
    embeddings_registry,
    image_generation_registry,
    llm_registry,
    step_registry,
    task_registry,
)
from fastdistill.steps.base import _Step
from fastdistill.steps.tasks.base import _Task
from fastdistill.utils.docstring import parse_google_docstring


class ComponentsInfo(TypedDict):
    """A dictionary containing `fastdistill` components information."""

    llms: List
    image_generation_models: List
    steps: List
    tasks: List
    embeddings: List


def export_components_info() -> ComponentsInfo:
    """Exports `fastdistill` components (`LLM`s, `Step`s and `Task`s) information in a dictionary
    format. This information can be used to generate `fastdistill` components documentation,
    or to be used in 3rd party applications (UIs, etc).

    Returns:
        A dictionary containing `fastdistill` components information
    """

    return {
        "steps": [
            {"name": step_type.__name__, "docstring": parse_google_docstring(step_type)}
            for step_type in _get_steps()
        ],
        "tasks": [
            {"name": task_type.__name__, "docstring": parse_google_docstring(task_type)}
            for task_type in _get_tasks()
        ],
        "llms": [
            {"name": llm_type.__name__, "docstring": parse_google_docstring(llm_type)}
            for llm_type in _get_llms()
        ],
        "image_generation_models": [
            {"name": igm_type.__name__, "docstring": parse_google_docstring(igm_type)}
            for igm_type in _get_image_generation_models()
        ],
        "embeddings": [
            {
                "name": embeddings_type.__name__,
                "docstring": parse_google_docstring(embeddings_type),
            }
            for embeddings_type in _get_embeddings()
        ],
    }


def _iter_registry(registry) -> Iterable[type]:
    for name in registry.names():
        component = registry.get(name)
        if not inspect.isclass(component):
            continue
        if inspect.isabstract(component):
            continue
        yield component


def _get_steps() -> List[Type["_Step"]]:
    """Get all `Step` subclasses, that are not abstract classes and not `Task` subclasses.

    Returns:
        A list of `Step` subclasses, except `Task` subclasses
    """
    return [
        step_type
        for step_type in _iter_registry(step_registry)
        if issubclass(step_type, _Step) and not issubclass(step_type, _Task)
    ]


def _get_tasks() -> List[Type["_Task"]]:
    """Get all `Task` subclasses, that are not abstract classes.

    Returns:
        A list of `Task` subclasses
    """
    return [
        task_type
        for task_type in _iter_registry(task_registry)
        if issubclass(task_type, _Task)
    ]


def _get_llms() -> List[Type["LLM"]]:
    """Get all `LLM` subclasses, that are not abstract classes.

    Returns:
        A list of `LLM` subclasses, except `AsyncLLM` subclass
    """
    return [
        llm_type
        for llm_type in _iter_registry(llm_registry)
        if issubclass(llm_type, LLM)
    ]


def _get_image_generation_models() -> List[Type["ImageGenerationModel"]]:
    """Get all `ImageGenerationModel` subclasses, that are not abstract classes.

    Note:
        This is a placeholder as we don't have `ImageGenerationModel` classes yet.

    Returns:
        The list of all the classes under `fastdistill.models.image_generation` that are not abstract classes.
    """
    return [
        igm_type
        for igm_type in _iter_registry(image_generation_registry)
        if issubclass(igm_type, ImageGenerationModel)
    ]


def _get_embeddings() -> List[Type["Embeddings"]]:
    """Get all `Embeddings` subclasses, that are not abstract classes.

    Returns:
        A list of `Embeddings` subclasses, except `AsyncLLM` subclass
    """
    return [
        embeddings_type
        for embeddings_type in _iter_registry(embeddings_registry)
        if issubclass(embeddings_type, Embeddings)
    ]
