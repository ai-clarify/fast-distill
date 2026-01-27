# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from fastdistill.agent.utils import slugify


class DistillInstruction(BaseModel):
    task_id: Optional[str] = None
    instruction: str
    context: Optional[str] = None


class DistillAgentSpec(BaseModel):
    name: str
    description: str
    task: str
    system_prompt: str
    prompt_template: str
    instructions: List[DistillInstruction]
    teacher_model: Optional[str] = None
    student_model: Optional[str] = None
    min_output_chars: int = Field(default=24, ge=1)
    max_output_chars: int = Field(default=2048, ge=1)
    train_ratio: float = Field(default=0.9, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


def normalize_spec(
    spec: DistillAgentSpec,
    *,
    default_system_prompt: Optional[str] = None,
    default_prompt_template: Optional[str] = None,
) -> DistillAgentSpec:
    payload = spec.model_dump()
    instructions = payload.get("instructions", [])
    name_slug = slugify(payload.get("name") or "agent")
    normalized = []
    for index, item in enumerate(instructions, start=1):
        task_id = item.get("task_id") or f"{name_slug or 'task'}-{index:04d}"
        context = item.get("context")
        normalized.append(
            {
                "task_id": task_id,
                "instruction": item.get("instruction"),
                "context": "" if context is None else context,
            }
        )
    payload["instructions"] = normalized
    if default_system_prompt:
        payload["system_prompt"] = default_system_prompt
    if default_prompt_template:
        payload["prompt_template"] = default_prompt_template
    return DistillAgentSpec.model_validate(payload)
