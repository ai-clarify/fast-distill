# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

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


def _instruction_rows(spec: DistillAgentSpec) -> List[dict]:
    rows = []
    for item in spec.instructions:
        rows.append(
            {
                "task_id": item.task_id,
                "instruction": item.instruction,
                "context": item.context,
            }
        )
    return rows


def _canonical_fields(spec: DistillAgentSpec) -> Sequence[str]:
    fields: List[str] = ["instruction"]
    if any(item.context not in (None, "") for item in spec.instructions):
        fields.append("context")
    return fields


def _template_columns(spec: DistillAgentSpec) -> Sequence[str]:
    columns: List[str] = ["instruction"]
    if any(item.context not in (None, "") for item in spec.instructions):
        columns.append("context")
    return columns


def build_agent_pipeline(
    spec: DistillAgentSpec,
    *,
    teacher_llm: object,
    artifacts_root: Path,
    run_id: str,
) -> Pipeline:
    rows = _instruction_rows(spec)
    fields = _canonical_fields(spec)
    columns = _template_columns(spec)

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
