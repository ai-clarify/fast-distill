# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import multiprocessing as mp
import os
import tempfile
from typing import Generator

import pytest


def _manager_available() -> tuple[bool, str]:
    try:
        manager = mp.Manager()
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    manager.shutdown()
    manager.join()
    return True, ""


manager_ok, manager_error = _manager_available()
if not manager_ok:
    pytest.skip(
        f"multiprocessing.Manager unavailable: {manager_error}",
        allow_module_level=True,
    )


@pytest.fixture(autouse=True)
def temp_cache_dir() -> Generator[None, None, None]:
    """Set the cache directory to a temporary directory for all tests."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.environ["FASTDISTILL_CACHE_DIR"] = tmpdirname
        yield
