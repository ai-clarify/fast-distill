# Copyright 2023-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pydantic import Field

from distilabel.errors import DistilabelUserError
from distilabel.mixins.runtime_parameters import RuntimeParameter
from distilabel.steps.base import GlobalStep, StepInput
from distilabel.utils.serialization import write_json


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
            raise DistilabelUserError("WriteManifest requires output_dir to be set.")

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
