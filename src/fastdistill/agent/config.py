# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from pydantic import BaseModel, Field

from fastdistill.config import deep_merge_dicts, load_layered_config


class AgentSettings(BaseModel):
    task: Optional[str] = None
    name: Optional[str] = None
    output_dir: str = "~/.cache/fastdistill/agents"
    num_instructions: int = Field(default=48, ge=1)
    run_id: Optional[str] = None


class ClaudeSettings(BaseModel):
    max_turns: int = Field(default=1, ge=1)


class DistillSettings(BaseModel):
    system_prompt: Optional[str] = None
    prompt_template: Optional[str] = None
    min_output_chars: int = Field(default=24, ge=1)
    max_output_chars: int = Field(default=2048, ge=1)
    train_ratio: float = Field(default=0.9, ge=0.0, le=1.0)


class TeacherSettings(BaseModel):
    provider: str = "openrouter"
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    api_key_env: Optional[str] = None
    generation_kwargs: Dict[str, Any] = Field(default_factory=dict)


class TrainingSettings(BaseModel):
    enabled: bool = False
    mlx_config: Optional[str] = None
    model: Optional[str] = None
    iters: Optional[int] = None
    batch_size: Optional[int] = None
    max_seq_length: Optional[int] = None
    export_gguf: bool = True
    gguf_output: Optional[str] = None


class AgentConfig(BaseModel):
    agent: AgentSettings = Field(default_factory=AgentSettings)
    claude: ClaudeSettings = Field(default_factory=ClaudeSettings)
    distill: DistillSettings = Field(default_factory=DistillSettings)
    teacher: TeacherSettings = Field(default_factory=TeacherSettings)
    training: TrainingSettings = Field(default_factory=TrainingSettings)


def load_agent_config(
    config_path: Optional[str],
    *,
    config_env: Optional[str] = None,
    config_run: Optional[str] = None,
    overrides: Optional[Mapping[str, Any]] = None,
) -> AgentConfig:
    if config_path:
        data = load_layered_config(
            config_path,
            env_path=config_env,
            run_path=config_run,
            overrides=overrides,
        )
    elif overrides:
        data = deep_merge_dicts({}, overrides)
    else:
        data = {}
    return AgentConfig.model_validate(data)
