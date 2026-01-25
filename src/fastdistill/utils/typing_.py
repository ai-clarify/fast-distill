# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import inspect
from typing import Any, Union

from pydantic.types import _SecretField
from typing_extensions import Annotated, get_args, get_origin


def is_parameter_annotated_with(parameter: inspect.Parameter, annotation: Any) -> bool:
    """Checks if a parameter type hint is `typing.Annotated` and in that case if it contains
    `annotation` as metadata.

    Args:
        parameter: the parameter to check.
        annotation: the annotation to check.

    Returns:
        `True` if the parameter type hint is `typing.Annotated` and contains `annotation`
        as metadata, `False` otherwise.
    """
    if get_origin(parameter.annotation) is not Annotated:
        return False

    for metadata in get_args(parameter.annotation):
        if metadata == annotation:
            return True

    return False


def extract_annotation_inner_type(type_hint: Any) -> Any:
    """Extracts the inner type of an annotation.

    Args:
        type_hint: The type hint to extract the inner type from.

    Returns:
        The inner type of the `RuntimeParameter` type hint.
    """
    type_hint_args = get_args(type_hint)
    if get_origin(type_hint) is Annotated:
        return extract_annotation_inner_type(type_hint_args[0])

    if get_origin(type_hint) is Union and type(None) in type_hint_args:
        return extract_annotation_inner_type(type_hint_args[0])

    return type_hint


def is_type_pydantic_secret_field(type_: type) -> bool:
    """Checks if a type is a Pydantic `_SecretField`.

    Returns:
        `True` if the type is a Pydantic `_SecretField`, `False` otherwise.
    """
    return inspect.isclass(type_) and issubclass(type_, _SecretField)
