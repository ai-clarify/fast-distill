# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import inspect
from typing import Generator, List, Type, TypedDict, TypeVar

from fastdistill.models.embeddings.base import Embeddings
from fastdistill.models.image_generation.base import ImageGenerationModel
from fastdistill.models.llms.base import LLM
from fastdistill.steps.base import _Step
from fastdistill.steps.tasks.base import _Task
from fastdistill.steps.tasks.generate_embeddings import GenerateEmbeddings
from fastdistill.steps.tasks.pair_rm import PairRM
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


T = TypeVar("T", covariant=True)


def _get_steps() -> List[Type["_Step"]]:
    """Get all `Step` subclasses, that are not abstract classes and not `Task` subclasses.

    Returns:
        A list of `Step` subclasses, except `Task` subclasses
    """
    return [
        step_type
        for step_type in _recursive_subclasses(_Step)
        if not inspect.isabstract(step_type)
        and not issubclass(step_type, _Task)
        and step_type not in [PairRM, GenerateEmbeddings]
    ]


def _get_tasks() -> List[Type["_Task"]]:
    """Get all `Task` subclasses, that are not abstract classes.

    Returns:
        A list of `Task` subclasses
    """
    tasks = [
        task_type
        for task_type in _recursive_subclasses(_Task)
        if not inspect.isabstract(task_type)
    ]

    tasks.extend([PairRM, GenerateEmbeddings])  # type: ignore

    return tasks


def _get_llms() -> List[Type["LLM"]]:
    """Get all `LLM` subclasses, that are not abstract classes.

    Returns:
        A list of `LLM` subclasses, except `AsyncLLM` subclass
    """
    return [
        llm_type
        for llm_type in _recursive_subclasses(LLM)
        if not inspect.isabstract(llm_type)
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
        for igm_type in _recursive_subclasses(ImageGenerationModel)
        if not inspect.isabstract(igm_type)
    ]


def _get_embeddings() -> List[Type["Embeddings"]]:
    """Get all `Embeddings` subclasses, that are not abstract classes.

    Returns:
        A list of `Embeddings` subclasses, except `AsyncLLM` subclass
    """
    return [
        embeddings_type
        for embeddings_type in _recursive_subclasses(Embeddings)
        if not inspect.isabstract(embeddings_type)
    ]


# Reference: https://adamj.eu/tech/2024/05/10/python-all-subclasses/
def _recursive_subclasses(klass: Type[T]) -> Generator[Type[T], None, None]:
    """Recursively get all subclasses of a class.

    Args:
        klass: A class to get subclasses from.

    Yield:
        A generator of subclasses of the given class.
    """
    for subclass in klass.__subclasses__():
        yield subclass
        yield from _recursive_subclasses(subclass)
