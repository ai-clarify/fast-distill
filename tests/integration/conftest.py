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


@pytest.fixture(autouse=True)
def _cleanup_child_processes() -> Generator[None, None, None]:
    """Kill orphaned child processes after each test.

    Pipeline tests spawn non-daemon worker processes via multiprocessing.  If a
    test fails or the pipeline teardown doesn't complete, those processes leak
    and block subsequent tests (or the entire pytest session).
    """
    children_before = {p.pid for p in mp.active_children()}
    yield
    for child in mp.active_children():
        if child.pid in children_before:
            continue
        if not child.is_alive():
            continue
        child.terminate()
        child.join(timeout=5)
        if child.is_alive():
            child.kill()
            child.join(timeout=2)
