# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastdistill.agent.bundle import AgentBundle, build_agent_bundle
from fastdistill.agent.claude import generate_spec
from fastdistill.agent.config import AgentConfig
from fastdistill.agent.mlx import export_gguf, run_mlx_pipeline
from fastdistill.agent.pipeline import build_agent_pipeline
from fastdistill.agent.specs import DistillAgentSpec, normalize_spec
from fastdistill.agent.teacher import build_teacher_llm
from fastdistill.errors import FastDistillUserError
from fastdistill.utils.serialization import write_yaml


def _apply_overrides(
    spec: DistillAgentSpec, config: AgentConfig, task: str
) -> DistillAgentSpec:
    payload = spec.model_dump()
    payload["task"] = task

    if config.agent.name:
        payload["name"] = config.agent.name

    if config.distill.system_prompt:
        payload["system_prompt"] = config.distill.system_prompt
    if config.distill.prompt_template:
        payload["prompt_template"] = config.distill.prompt_template

    payload["min_output_chars"] = config.distill.min_output_chars
    payload["max_output_chars"] = config.distill.max_output_chars
    payload["train_ratio"] = config.distill.train_ratio

    if config.teacher.model:
        payload["teacher_model"] = config.teacher.model
    if config.training.model:
        payload["student_model"] = config.training.model

    return DistillAgentSpec.model_validate(payload)


def _write_agent_card(
    bundle: AgentBundle, spec: DistillAgentSpec, *, gguf_path: Optional[Path]
) -> None:
    gguf_value = str(gguf_path) if gguf_path else ""
    content = "\n".join(
        [
            f"# Agent: {spec.name}",
            "",
            f"- Task: {spec.task}",
            f"- Description: {spec.description}",
            f"- Run ID: {bundle.run_id}",
            f"- Instructions: {len(spec.instructions)}",
            f"- Teacher model: {spec.teacher_model or ''}",
            f"- Student model: {spec.student_model or ''}",
            "",
            "## System Prompt",
            spec.system_prompt,
            "",
            "## Prompt Template",
            "```jinja2",
            spec.prompt_template,
            "```",
            "",
            "## Artifacts",
            f"- Bundle root: {bundle.root}",
            f"- Artifacts root: {bundle.artifacts_root}",
            f"- Reports: {bundle.reports_dir}",
            f"- Manifests: {bundle.manifests_dir}",
            f"- MLX dataset: {bundle.mlx_dir}",
            f"- GGUF model: {gguf_value}",
        ]
    )
    bundle.card_path.write_text(content, encoding="utf-8")


def distill_agent(
    *,
    task: Optional[str],
    config: AgentConfig,
) -> AgentBundle:
    resolved_task = task or config.agent.task
    if not resolved_task:
        raise FastDistillUserError(
            "Task is required. Provide --task or set agent.task."
        )

    spec = generate_spec(
        task=resolved_task,
        num_instructions=config.agent.num_instructions,
        system_prompt_hint=config.distill.system_prompt,
        prompt_template_hint=config.distill.prompt_template,
        min_output_chars=config.distill.min_output_chars,
        max_output_chars=config.distill.max_output_chars,
        max_turns=config.claude.max_turns,
    )
    spec = normalize_spec(
        spec,
        default_system_prompt=config.distill.system_prompt,
        default_prompt_template=config.distill.prompt_template,
    )
    spec = _apply_overrides(spec, config, resolved_task)

    bundle = build_agent_bundle(
        config.agent.output_dir,
        name=spec.name,
        run_id=config.agent.run_id,
        gguf_output=config.training.gguf_output,
    )
    bundle.root.mkdir(parents=True, exist_ok=True)
    bundle.artifacts_root.mkdir(parents=True, exist_ok=True)

    write_yaml(bundle.spec_path, spec.model_dump())

    teacher_llm = build_teacher_llm(
        provider=config.teacher.provider,
        model=config.teacher.model,
        base_url=config.teacher.base_url,
        api_key=config.teacher.api_key,
        api_key_env=config.teacher.api_key_env,
        generation_kwargs=config.teacher.generation_kwargs,
    )

    pipeline = build_agent_pipeline(
        spec,
        teacher_llm=teacher_llm,
        artifacts_root=bundle.artifacts_root,
        run_id=bundle.run_id,
    )

    write_yaml(bundle.pipeline_path, pipeline.dump())

    pipeline.run(use_cache=False)

    gguf_path: Optional[Path] = None
    if config.training.enabled:
        repo_root = Path(__file__).resolve().parents[3]
        base_config = (
            Path(config.training.mlx_config)
            if config.training.mlx_config
            else repo_root / "configs" / "fastdistill" / "mlx_train.sample.yaml"
        )
        train_config_path = run_mlx_pipeline(
            mlx_dir=bundle.mlx_dir,
            base_config_path=base_config,
            model=config.training.model or spec.student_model,
            iters=config.training.iters,
            batch_size=config.training.batch_size,
            max_seq_length=config.training.max_seq_length,
        )
        bundle.train_config_path.write_text(
            train_config_path.read_text(encoding="utf-8"), encoding="utf-8"
        )
        if config.training.export_gguf:
            base_model = config.training.model or spec.student_model
            if not base_model:
                raise FastDistillUserError(
                    "GGUF export requires a base model (set training.model or student_model)."
                )
            gguf_path = export_gguf(
                base_model=base_model,
                adapter_path=bundle.mlx_dir / "adapters",
                output_path=bundle.gguf_path,
            )

    _write_agent_card(bundle, spec, gguf_path=gguf_path)

    return bundle
