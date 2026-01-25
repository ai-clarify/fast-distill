# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

from fastdistill.models.mixins.magpie import MAGPIE_PRE_QUERY_TEMPLATES
from tests.unit.conftest import DummyMagpieLLM


class TestMagpieChatTemplateMixin:
    def test_magpie_pre_query_template_set(self) -> None:
        with pytest.raises(
            ValueError,
            match="Cannot set `use_magpie_template=True` if `magpie_pre_query_template` is `None`",
        ):
            DummyMagpieLLM(use_magpie_template=True)

    def test_magpie_pre_query_template_alias_resolved(self) -> None:
        llm = DummyMagpieLLM(magpie_pre_query_template="llama3")
        assert llm.magpie_pre_query_template == MAGPIE_PRE_QUERY_TEMPLATES["llama3"]

    def test_apply_magpie_pre_query_template(self) -> None:
        llm = DummyMagpieLLM(magpie_pre_query_template="<user>")

        assert (
            llm.apply_magpie_pre_query_template(
                prompt="<system>Hello hello</system>", input=[]
            )
            == "<system>Hello hello</system>"
        )

        llm = DummyMagpieLLM(
            use_magpie_template=True, magpie_pre_query_template="<user>"
        )

        assert (
            llm.apply_magpie_pre_query_template(
                prompt="<system>Hello hello</system>", input=[]
            )
            == "<system>Hello hello</system><user>"
        )

        assert (
            llm.apply_magpie_pre_query_template(
                prompt="<system>Hello hello</system><user>Hey</user>",
                input=[{"role": "user", "content": "Hey"}],
            )
            == "<system>Hello hello</system><user>Hey</user>"
        )
