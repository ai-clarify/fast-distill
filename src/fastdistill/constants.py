# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from pathlib import Path
from typing import Final

# Steps related constants
FASTDISTILL_METADATA_KEY: Final[str] = "fastdistill_metadata"

# Cache
BASE_CACHE_DIR = Path.home() / ".cache" / "fastdistill"
PIPELINES_CACHE_DIR = BASE_CACHE_DIR / "pipelines"

# Pipeline dag related constants
STEP_ATTR_NAME: Final[str] = "step"
INPUT_QUEUE_ATTR_NAME: Final[str] = "input_queue"
RECEIVES_ROUTED_BATCHES_ATTR_NAME: Final[str] = "receives_routed_batches"
ROUTING_BATCH_FUNCTION_ATTR_NAME: Final[str] = "routing_batch_function"
CONVERGENCE_STEP_ATTR_NAME: Final[str] = "convergence_step"
LAST_BATCH_SENT_FLAG: Final[str] = "last_batch_sent"

# Pipeline execution related constants
PIPELINE_NAME_ENV_NAME = "FASTDISTILL_PIPELINE_NAME"
PIPELINE_CACHE_ID_ENV_NAME = "FASTDISTILL_PIPELINE_CACHE_ID"
SIGINT_HANDLER_CALLED_ENV_NAME = "sigint_handler_called"

# Data paths constants
STEPS_OUTPUTS_PATH = "steps_outputs"
STEPS_ARTIFACTS_PATH = "steps_artifacts"

# Distiset related constants
DISTISET_CONFIG_FOLDER: Final[str] = "distiset_configs"
DISTISET_ARTIFACTS_FOLDER: Final[str] = "artifacts"
PIPELINE_CONFIG_FILENAME: Final[str] = "pipeline.yaml"
PIPELINE_LOG_FILENAME: Final[str] = "pipeline.log"

# Docs page for the custom errors
FASTDISTILL_DOCS_URL: Final[str] = "https://fastdistill.argilla.io/latest/"


__all__ = [
    "BASE_CACHE_DIR",
    "CONVERGENCE_STEP_ATTR_NAME",
    "DISTISET_ARTIFACTS_FOLDER",
    "DISTISET_CONFIG_FOLDER",
    "FASTDISTILL_DOCS_URL",
    "FASTDISTILL_METADATA_KEY",
    "INPUT_QUEUE_ATTR_NAME",
    "LAST_BATCH_SENT_FLAG",
    "PIPELINES_CACHE_DIR",
    "PIPELINE_CONFIG_FILENAME",
    "PIPELINE_LOG_FILENAME",
    "RECEIVES_ROUTED_BATCHES_ATTR_NAME",
    "ROUTING_BATCH_FUNCTION_ATTR_NAME",
    "SIGINT_HANDLER_CALLED_ENV_NAME",
    "STEPS_ARTIFACTS_PATH",
    "STEPS_OUTPUTS_PATH",
    "STEP_ATTR_NAME",
]
