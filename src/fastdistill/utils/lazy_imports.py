# Copyright 2026 cklxx
#
# Licensed under the MIT License.

"""Shared helpers for lazy module attribute loading."""

from __future__ import annotations

import importlib
from typing import Any, Mapping, MutableMapping


def load_by_name(
    name: str, mapping: Mapping[str, str], namespace: MutableMapping[str, Any]
) -> Any:
    """Load a lazily-imported attribute and cache it in the module namespace.

    Args:
        name: Attribute name to resolve.
        mapping: Mapping of attribute name -> "module:attr" target.
        namespace: The module globals to cache the resolved attribute.

    Returns:
        The resolved attribute.
    """
    target = mapping[name]
    module_path, attr = target.rsplit(":", 1)
    value = getattr(importlib.import_module(module_path), attr)
    namespace[name] = value
    return value
