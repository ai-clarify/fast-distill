# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from pydantic import BaseModel

from fastdistill.utils.serialization import _extra_serializable_fields, _Serializable


def test_extra_serializable_fields() -> None:
    class DummyAttribute(BaseModel, _Serializable):
        pass

    class Dummy(BaseModel, _Serializable):
        attr: DummyAttribute

    dummy = Dummy(attr=DummyAttribute())

    assert _extra_serializable_fields(dummy) == [
        {
            "attr": {
                "type_info": {
                    "module": "tests.unit.utils.test_serialization",
                    "name": "DummyAttribute",
                }
            }
        }
    ]
