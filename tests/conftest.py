# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import sys
from typing import TYPE_CHECKING, List

import pytest

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.nodes import Item


def pytest_configure(config: "Config") -> None:
    config.addinivalue_line(
        "markers",
        "skip_python_versions(versions): mark test to be skipped on specified Python versions",
    )


def pytest_collection_modifyitems(config: "Config", items: List["Item"]) -> None:
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    for item in items:
        skip_versions_marker = item.get_closest_marker("skip_python_versions")
        if skip_versions_marker:
            versions_to_skip = skip_versions_marker.args[0]
            if current_version in versions_to_skip:
                skip_reason = f"Test not supported on Python {current_version}"
                item.add_marker(pytest.mark.skip(reason=skip_reason))
