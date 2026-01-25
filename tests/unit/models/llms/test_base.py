# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

from fastdistill.errors import FastDistillNotImplementedError
from tests.unit.conftest import DummyLLM


class TestLLM:
    def test_offline_batch_generate_raise_fastdistill_not_implemented_error(
        self,
    ) -> None:
        llm = DummyLLM()

        with pytest.raises(FastDistillNotImplementedError):
            llm.offline_batch_generate()
