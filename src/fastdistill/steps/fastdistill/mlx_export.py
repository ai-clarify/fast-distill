# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import hashlib
from pathlib import Path
from typing import List, Optional

import orjson
from jinja2 import Environment
from pydantic import Field

from fastdistill.errors import FastDistillUserError
from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.steps.base import GlobalStep, StepInput


class WriteMlxDataset(GlobalStep):
    """Export distilled rows to MLX-friendly JSONL files.

    The output format is a JSONL file with a `messages` array per row, suitable
    for MLX chat fine-tuning. Train/valid split is deterministic and based on
    `sample_id` when available.

    Attributes:
        output_dir: Base directory for exported files.
        train_filename: Output JSONL name for the training split.
        valid_filename: Output JSONL name for the validation split.
        train_ratio: Fraction of samples to route into the train split.
        sample_id_field: Field used for deterministic split bucketing.
        prompt_template: Jinja2 template for the user message.
        assistant_field: Field used as assistant target (e.g., generation).
        system_prompt: Optional system prompt added to each example.
        system_prompt_field: Optional field name that overrides system_prompt per row.
        metadata_fields: Fields to include under a `metadata` object.
    """

    output_dir: RuntimeParameter[str] = Field(
        default="artifacts/exports/mlx",
        description="Base directory for MLX JSONL exports.",
    )
    train_filename: RuntimeParameter[str] = Field(
        default="train.jsonl",
        description="Output JSONL filename for the training split.",
    )
    valid_filename: RuntimeParameter[str] = Field(
        default="valid.jsonl",
        description="Output JSONL filename for the validation split.",
    )
    train_ratio: float = Field(
        default=0.9,
        description="Fraction of rows routed to the training split.",
        ge=0.0,
        le=1.0,
    )
    sample_id_field: str = Field(
        default="sample_id",
        description="Field used for deterministic split bucketing.",
    )
    prompt_template: RuntimeParameter[str] = Field(
        default="Schema: {{ schema }}\nQuestion: {{ instruction }}\nSQL:",
        description="Jinja2 template used for the user prompt.",
    )
    assistant_field: str = Field(
        default="generation",
        description="Field used as the assistant target.",
    )
    system_prompt: Optional[RuntimeParameter[str]] = Field(
        default="Return SQL only.",
        description="Optional system prompt included in each example.",
    )
    system_prompt_field: Optional[str] = Field(
        default=None,
        description="Optional field name to override system_prompt per row.",
    )
    metadata_fields: List[str] = Field(
        default_factory=lambda: ["sample_id"],
        description="Fields included under a metadata object.",
    )

    def _is_train_row(self, row: dict) -> bool:
        if self.train_ratio <= 0.0:
            return False
        if self.train_ratio >= 1.0:
            return True
        key = row.get(self.sample_id_field)
        if key is None:
            key = orjson.dumps(row, option=orjson.OPT_SORT_KEYS).decode("utf-8")
        digest = hashlib.sha256(str(key).encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big") / float(2**32 - 1)
        return bucket < self.train_ratio

    def _system_prompt_for_row(self, row: dict) -> Optional[str]:
        if self.system_prompt_field:
            return row.get(self.system_prompt_field) or self.system_prompt
        return self.system_prompt

    def process(self, inputs: StepInput):  # type: ignore[override]
        if not self.output_dir:
            raise FastDistillUserError("WriteMlxDataset requires output_dir to be set.")

        env = Environment(autoescape=False)
        template = env.from_string(self.prompt_template)

        output_dir = Path(self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        train_path = output_dir / str(self.train_filename)
        valid_path = output_dir / str(self.valid_filename)

        with open(train_path, "wb") as train_file, open(valid_path, "wb") as valid_file:
            for row in inputs:
                user_content = template.render(**row)
                system_prompt = self._system_prompt_for_row(row)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": user_content})
                messages.append(
                    {"role": "assistant", "content": row[self.assistant_field]}
                )

                record = {"messages": messages}
                if self.metadata_fields:
                    metadata = {
                        field: row.get(field)
                        for field in self.metadata_fields
                        if field in row
                    }
                    record["metadata"] = metadata

                payload = orjson.dumps(record, option=orjson.OPT_SERIALIZE_NUMPY)
                if self._is_train_row(row):
                    train_file.write(payload + b"\n")
                else:
                    valid_file.write(payload + b"\n")

        yield inputs
