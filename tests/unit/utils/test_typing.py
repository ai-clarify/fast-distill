# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import inspect

from typing_extensions import Annotated

from fastdistill.utils.typing_ import is_parameter_annotated_with


def test_is_parameter_annotated_with() -> None:
    def dummy_function(arg: Annotated[int, "unit-test"], arg2: int) -> None:
        pass

    signature = inspect.signature(dummy_function)
    arg_parameter = signature.parameters["arg"]
    arg2_parameter = signature.parameters["arg2"]

    assert is_parameter_annotated_with(arg_parameter, "hello") is False
    assert is_parameter_annotated_with(arg_parameter, "unit-test") is True
    assert is_parameter_annotated_with(arg2_parameter, "unit-test") is False
