# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

from typing import Any, Mapping, Optional
from urllib.parse import urlparse

import requests
import yaml

from fastdistill.errors import FastDistillUserError
from fastdistill.utils.serialization import read_yaml


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _ensure_yaml_path(path: str) -> None:
    if not path.endswith((".yaml", ".yml")):
        raise FastDistillUserError(
            f"Config files must be YAML. Unsupported file format for '{path}'."
        )


def _ensure_mapping(data: Any, source: str) -> dict[str, Any]:
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise FastDistillUserError(
            f"Config '{source}' must be a YAML mapping at the top level."
        )
    return data


def load_yaml_config(path: str) -> dict[str, Any]:
    _ensure_yaml_path(path)
    if _is_http_url(path):
        response = requests.get(path)
        response.raise_for_status()
        data = yaml.safe_load(response.text)
        return _ensure_mapping(data, path)

    data = read_yaml(path)
    return _ensure_mapping(data, path)


def deep_merge_dicts(
    base: Mapping[str, Any], override: Mapping[str, Any]
) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = deep_merge_dicts(merged[key], value)  # type: ignore[arg-type]
        else:
            merged[key] = value
    return merged


def load_layered_config(
    base_path: str,
    *,
    env_path: Optional[str] = None,
    run_path: Optional[str] = None,
    overrides: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    config = load_yaml_config(base_path)
    if env_path:
        config = deep_merge_dicts(config, load_yaml_config(env_path))
    if run_path:
        config = deep_merge_dicts(config, load_yaml_config(run_path))
    if overrides:
        config = deep_merge_dicts(config, overrides)
    return config


__all__ = [
    "deep_merge_dicts",
    "load_layered_config",
    "load_yaml_config",
]
