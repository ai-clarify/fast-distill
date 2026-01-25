# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import os
import tempfile
from typing import Generator

import pytest


@pytest.fixture(autouse=True)
def temp_cache_dir() -> Generator[None, None, None]:
    """Set the cache directory to a temporary directory for all tests."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.environ["FASTDISTILL_CACHE_DIR"] = tmpdirname
        yield
