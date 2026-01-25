# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import Field

from fastdistill.errors import FastDistillUserError
from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.steps.base import GlobalStep, StepInput
from fastdistill.utils.serialization import write_json


class WriteManifest(GlobalStep):
    """Write a manifest.json with row count and schema fingerprint.

    This is a GlobalStep to guarantee a complete view of the dataset at
    each stage. For very large datasets consider sharding before this step.

    Attributes:
        output_dir: Base directory for manifest files.
        stage: Stage name (raw, canonical, filtered, distilled, etc.).
        sample_id_field: Column name used to compute min/max sample_id.
        run_id: Optional run identifier stored in the manifest.
        run_id_env: Environment variable used as fallback for run_id.

    Output:
        - Writes a manifest.json to {output_dir}/{stage}/manifest.json
        - Passes inputs through unchanged
    """

    output_dir: RuntimeParameter[str] = Field(
        default="artifacts/manifests",
        description="Base directory for manifest files.",
    )
    stage: RuntimeParameter[str] = Field(
        default="stage",
        description="Stage name (raw, canonical, filtered, distilled, etc.).",
    )
    sample_id_field: str = Field(
        default="sample_id",
        description="Column name used to compute min/max sample_id.",
    )
    run_id: Optional[RuntimeParameter[str]] = Field(
        default=None,
        description="Optional run identifier stored in the manifest.",
    )
    run_id_env: str = Field(
        default="FASTDISTILL_RUN_ID",
        description="Environment variable used as fallback for run_id.",
    )

    def process(self, inputs: StepInput):  # type: ignore[override]
        if not self.output_dir:
            raise FastDistillUserError("WriteManifest requires output_dir to be set.")

        columns = sorted({key for row in inputs for key in row.keys()})
        field_hash = hashlib.sha256("|".join(columns).encode("utf-8")).hexdigest()
        sample_ids = [
            row.get(self.sample_id_field)
            for row in inputs
            if row.get(self.sample_id_field) is not None
        ]
        min_sample_id = min(sample_ids) if sample_ids else None
        max_sample_id = max(sample_ids) if sample_ids else None

        run_id = self.run_id or os.getenv(self.run_id_env)
        manifest = {
            "run_id": run_id,
            "stage": self.stage,
            "count": len(inputs),
            "field_hash": field_hash,
            "min_sample_id": min_sample_id,
            "max_sample_id": max_sample_id,
            "columns": columns,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        output_path = Path(self.output_dir) / str(self.stage) / "manifest.json"
        write_json(output_path, manifest)
        yield inputs
