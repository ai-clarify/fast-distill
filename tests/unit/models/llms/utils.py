# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any

from pydantic import BaseModel, PrivateAttr


class DummyUserDetail(BaseModel):
    name: str
    age: int
    _raw_response: Any = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._raw_response = data.get("_raw_response")
