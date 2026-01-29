# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Sequence

from fastdistill.agent.specs import DistillAgentSpec
from fastdistill.pipeline import Pipeline
from fastdistill.steps import LoadDataFromDicts
from fastdistill.steps.fastdistill import (
    CanonicalizeFields,
    ComputeHash,
    DeduplicateByField,
    FilterByBool,
    RuleFilter,
    WriteManifest,
    WriteMlxDataset,
    WriteQualityReport,
)
from fastdistill.steps.tasks import TextGeneration


def _instruction_rows(spec: DistillAgentSpec, columns: Sequence[str]) -> List[dict]:
    """Build rows with all columns needed by the template."""
    rows = []
    for item in spec.instructions:
        row: dict = {
            "task_id": item.task_id,
            "instruction": item.instruction,
            "context": item.context,
        }
        # Add template variables with None/empty default
        for col in columns:
            if col not in row:
                row[col] = None
        rows.append(row)
    return rows


def _canonical_fields(spec: DistillAgentSpec) -> Sequence[str]:
    fields: List[str] = ["instruction"]
    if any(item.context not in (None, "") for item in spec.instructions):
        fields.append("context")
    return fields


def _template_columns(spec: DistillAgentSpec) -> Sequence[str]:
    """Extract all variable names from Jinja2 template.

    Matches:
        - {{ variable }}
        - {{variable}}
        - {% if variable %}...{% endif %}
        - {% for item in variable %}...{% endfor %}
    """
    template = spec.prompt_template
    columns: List[str] = []

    # Pattern for {{ variable }} or {{variable}}
    var_pattern = r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}"
    # Pattern for {% if/for variable %}
    tag_pattern = r"{%\s*(?:if|for)\s+(?:\w+\s+in\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*%}"

    for pattern in [var_pattern, tag_pattern]:
        for match in re.finditer(pattern, template):
            var_name = match.group(1)
            if var_name not in columns:
                columns.append(var_name)

    return columns


def build_agent_pipeline(
    spec: DistillAgentSpec,
    *,
    teacher_llm: object,
    artifacts_root: Path,
    run_id: str,
) -> Pipeline:
    columns = _template_columns(spec)
    rows = _instruction_rows(spec, columns)
    fields = _canonical_fields(spec)

    with Pipeline(name=spec.name, description=spec.description) as pipeline:
        data = LoadDataFromDicts(data=rows)
        canonical = CanonicalizeFields(fields=list(fields))
        sample_id = ComputeHash(
            fields=["task_id", "canonical_input"], output_field="sample_id"
        )
        dedup = DeduplicateByField(field="sample_id")
        teacher = TextGeneration(
            llm=teacher_llm,
            system_prompt=spec.system_prompt,
            template=spec.prompt_template,
            columns=list(columns),
        )
        rule_filter = RuleFilter(
            text_field="generation",
            min_chars=spec.min_output_chars,
            max_chars=spec.max_output_chars,
        )
        report_candidates = WriteQualityReport(
            stage="teacher_candidates",
            output_dir=str(artifacts_root / "reports"),
            run_id=run_id,
        )
        filter_keep = FilterByBool(field="keep", value=True)
        report_distilled = WriteQualityReport(
            stage="distilled",
            output_dir=str(artifacts_root / "reports"),
            run_id=run_id,
        )
        mlx_export = WriteMlxDataset(
            output_dir=str(artifacts_root / "mlx"),
            prompt_template=spec.prompt_template,
            system_prompt=spec.system_prompt,
            train_ratio=spec.train_ratio,
            metadata_fields=["sample_id", "task_id"],
        )
        manifest = WriteManifest(
            stage="distilled",
            output_dir=str(artifacts_root / "manifests"),
            run_id=run_id,
        )

        (
            data
            >> canonical
            >> sample_id
            >> dedup
            >> teacher
            >> rule_filter
            >> report_candidates
            >> filter_keep
            >> report_distilled
            >> mlx_export
            >> manifest
        )

    return pipeline
