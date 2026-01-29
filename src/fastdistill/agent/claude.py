# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional, Union

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
        f"- The spec MUST include a 'task' field set to: '{task}'\n"
        "- Call the submit_distill_spec tool with the full JSON spec."
        f"{hint_block}"
    )


def _print_progress(message: str, emoji: str = "") -> None:
    """Print a friendly progress message."""
    prefix = f"{emoji} " if emoji else ""
    print(f"{prefix}{message}")


def _print_success(message: str) -> None:
    """Print a success message."""
    print(f"✓ {message}")


def _print_info(label: str, value: str) -> None:
    """Print an info line with alignment."""
    print(f"  {label:.<20} {value}")


async def _generate_spec_async(
    *,
    task: str,
    num_instructions: int,
    system_prompt_hint: Optional[str],
    prompt_template_hint: Optional[str],
    min_output_chars: int,
    max_output_chars: int,
    max_turns: int,
    verbose: bool = False,
) -> DistillAgentSpec:
    _require_claude_agent_sdk()
    from claude_agent_sdk import (
        ClaudeAgentOptions,
        ClaudeSDKClient,
        ResultMessage,
        create_sdk_mcp_server,
        tool,
    )

    spec_holder: Dict[str, Any] = {}
    message_count = 0

    @tool(
        "submit_distill_spec",
        "Submit the FastDistill agent spec as JSON.",
        {"spec": dict},
    )
    async def submit_distill_spec(args: Dict[str, Any]) -> Dict[str, Any]:
        spec_value: Union[str, dict] = args.get("spec", args)
        if isinstance(spec_value, str):
            spec_value = json.loads(spec_value)
        spec_holder["spec"] = spec_value
        _print_success("Received spec from agent")
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

    _print_progress("Planning agent distillation...", "🤔")
    _print_info("Task", task[:50] + "..." if len(task) > 50 else task)
    _print_info("Instructions needed", str(num_instructions))

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for response in client.receive_response():
            message_count += 1

            if verbose:
                print(f"  [msg #{message_count}] {type(response).__name__}")

            if isinstance(response, ResultMessage):
                _print_info("Messages exchanged", str(message_count))
                _print_info("Total cost", f"${response.total_cost_usd:.4f}")

    if "spec" not in spec_holder:
        raise FastDistillUserError("Claude agent did not return a distillation spec.")

    spec = DistillAgentSpec.model_validate(spec_holder["spec"])
    _print_success(f"Generated spec: {spec.name}")
    _print_info("Agent description", spec.description or "N/A")

    return spec


def generate_spec(
    *,
    task: str,
    num_instructions: int,
    system_prompt_hint: Optional[str],
    prompt_template_hint: Optional[str],
    min_output_chars: int,
    max_output_chars: int,
    max_turns: int,
    verbose: bool = False,
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
            verbose=verbose,
        )
    )
