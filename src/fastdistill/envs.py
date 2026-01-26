# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# Idea from: https://github.com/vllm-project/vllm/blob/main/vllm/envs.py

import os
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from fastdistill import constants
from fastdistill.errors import FastDistillUserError

if TYPE_CHECKING:
    FASTDISTILL_LOG_LEVEL: str = "INFO"
    FASTDISTILL_PIPELINE_NAME: Optional[str] = None
    FASTDISTILL_PIPELINE_CACHE_ID: Optional[str] = None
    FASTDISTILL_CACHE_DIR: Optional[str] = None
    FASTDISTILL_WRITE_BUFFER_BATCH_SIZE: int = 50


def _get_positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value in (None, ""):
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise FastDistillUserError(
            f"{name} must be a positive integer, got {raw_value!r}."
        ) from exc
    if value <= 0:
        raise FastDistillUserError(f"{name} must be a positive integer, got {value}.")
    return value


ENVIRONMENT_VARIABLES: Dict[str, Callable[[], Any]] = {
    # `fastdistill` logging level.
    "FASTDISTILL_LOG_LEVEL": lambda: os.getenv("FASTDISTILL_LOG_LEVEL", "INFO").upper(),
    # The name of the `fastdistill` pipeline currently running.
    constants.PIPELINE_NAME_ENV_NAME: lambda: os.getenv(
        constants.PIPELINE_NAME_ENV_NAME, None
    ),
    # The cache ID of the `fastdistill` pipeline currently running.
    constants.PIPELINE_CACHE_ID_ENV_NAME: lambda: os.getenv(
        constants.PIPELINE_CACHE_ID_ENV_NAME, None
    ),
    # The cache ID of the `fastdistill` pipeline currently running.
    "FASTDISTILL_CACHE_DIR": lambda: os.getenv("FASTDISTILL_CACHE_DIR", None),
    # Batch size for flushing write buffers to parquet files.
    "FASTDISTILL_WRITE_BUFFER_BATCH_SIZE": lambda: _get_positive_int_env(
        "FASTDISTILL_WRITE_BUFFER_BATCH_SIZE", 50
    ),
}


def __getattr__(name: str) -> Any:
    # lazy evaluation of environment variables
    if name in ENVIRONMENT_VARIABLES:
        return ENVIRONMENT_VARIABLES[name]()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> List[str]:
    return list(ENVIRONMENT_VARIABLES.keys())
