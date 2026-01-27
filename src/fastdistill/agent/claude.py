# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from fastdistill.agent.specs import DistillAgentSpec
from fastdistill.errors import FastDistillUserError


def _require_claude_agent_sdk() -> None:
    try:
        import claude_agent_sdk  # noqa: F401
    except ImportError as exc:
        raise FastDistillUserError(
            "claude-agent-sdk is required. Install with `pip install 'fastdistill[claude-agent]'`."
        ) from exc


def _build_prompt(
    *,
    task: str,
    num_instructions: int,
    system_prompt_hint: Optional[str],
    prompt_template_hint: Optional[str],
    min_output_chars: int,
    max_output_chars: int,
) -> str:
    hints = []
    if system_prompt_hint:
        hints.append(f"System prompt (use exactly): {system_prompt_hint}")
    if prompt_template_hint:
        hints.append(f"Prompt template (use exactly): {prompt_template_hint}")
    hint_block = "\n".join(hints)
    if hint_block:
        hint_block = f"\n\nHints:\n{hint_block}"
    return (
        "You are building a FastDistill agent spec.\n"
        "Return a spec for distilling a small model agent for the task below.\n"
        f"Task: {task}\n\n"
        f"Requirements:\n"
        f"- Create exactly {num_instructions} instructions.\n"
        "- Each instruction should be concrete and testable.\n"
        "- Provide a short name and description for the agent.\n"
        "- Include a system_prompt and a Jinja2 prompt_template.\n"
        "- Each instruction item must include task_id, instruction, and optional context.\n"
        f"- Set min_output_chars={min_output_chars} and max_output_chars={max_output_chars}.\n"
        "- Include suggested teacher_model and student_model when possible.\n"
        "- Call the submit_distill_spec tool with the full JSON spec."
        f"{hint_block}"
    )


async def _generate_spec_async(
    *,
    task: str,
    num_instructions: int,
    system_prompt_hint: Optional[str],
    prompt_template_hint: Optional[str],
    min_output_chars: int,
    max_output_chars: int,
    max_turns: int,
) -> DistillAgentSpec:
    _require_claude_agent_sdk()
    from claude_agent_sdk import (
        ClaudeAgentOptions,
        ClaudeSDKClient,
        create_sdk_mcp_server,
        tool,
    )

    spec_holder: Dict[str, Any] = {}

    @tool(
        "submit_distill_spec",
        "Submit the FastDistill agent spec as JSON.",
        {"spec": dict},
    )
    async def submit_distill_spec(args: Dict[str, Any]) -> Dict[str, Any]:
        spec_holder["spec"] = args.get("spec", args)
        return {"content": [{"type": "text", "text": "Spec received."}]}

    server = create_sdk_mcp_server(name="distill_spec", tools=[submit_distill_spec])
    options = ClaudeAgentOptions(
        system_prompt="You are a careful distillation planner.",
        mcp_servers={"distill_spec": server},
        allowed_tools=["mcp__distill_spec__submit_distill_spec"],
        permission_mode="acceptEdits",
        max_turns=max_turns,
    )

    prompt = _build_prompt(
        task=task,
        num_instructions=num_instructions,
        system_prompt_hint=system_prompt_hint,
        prompt_template_hint=prompt_template_hint,
        min_output_chars=min_output_chars,
        max_output_chars=max_output_chars,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for _ in client.receive_response():
            pass

    if "spec" not in spec_holder:
        raise FastDistillUserError("Claude agent did not return a distillation spec.")
    return DistillAgentSpec.model_validate(spec_holder["spec"])


def generate_spec(
    *,
    task: str,
    num_instructions: int,
    system_prompt_hint: Optional[str],
    prompt_template_hint: Optional[str],
    min_output_chars: int,
    max_output_chars: int,
    max_turns: int,
) -> DistillAgentSpec:
    return asyncio.run(
        _generate_spec_async(
            task=task,
            num_instructions=num_instructions,
            system_prompt_hint=system_prompt_hint,
            prompt_template_hint=prompt_template_hint,
            min_output_chars=min_output_chars,
            max_output_chars=max_output_chars,
            max_turns=max_turns,
        )
    )
