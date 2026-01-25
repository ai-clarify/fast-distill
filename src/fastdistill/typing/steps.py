# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, Iterator, List, Tuple, Union

StepOutput = Iterator[List[Dict[str, Any]]]
"""`StepOutput` is an alias of the typing `Iterator[List[Dict[str, Any]]]`"""

GeneratorStepOutput = Iterator[Tuple[List[Dict[str, Any]], bool]]
"""`GeneratorStepOutput` is an alias of the typing `Iterator[Tuple[List[Dict[str, Any]], bool]]`"""

StepColumns = Union[List[str], Dict[str, bool]]
"""`StepColumns` is an alias of the typing `Union[List[str], Dict[str, bool]]` used by the
`inputs` and `outputs` properties of an `Step`. In the case of a `List[str]`, it is a list
with the required columns. In the case of a `Dict[str, bool]`, it is a dictionary where
the keys are the columns and the values are booleans indicating whether the column is
required or not.
"""
