# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from pydantic import BaseModel

from fastdistill.steps.columns.keep import KeepColumns
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


def test_load_with_registry_type_info() -> None:
    payload = {
        "type_info": {"registry": "step", "name": "KeepColumns"},
        "columns": ["instruction"],
    }

    instance = _Serializable.from_dict(payload)

    assert isinstance(instance, KeepColumns)
