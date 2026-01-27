from fastdistill.agent.specs import (
    DistillAgentSpec,
    DistillInstruction,
    normalize_spec,
)


def test_normalize_spec_sets_task_ids_and_context() -> None:
    spec = DistillAgentSpec(
        name="Test Agent",
        description="desc",
        task="test-task",
        system_prompt="sys",
        prompt_template="{{ instruction }}",
        instructions=[
            DistillInstruction(instruction="Do A"),
            DistillInstruction(task_id="custom-2", instruction="Do B", context="ctx"),
        ],
    )

    normalized = normalize_spec(spec)

    assert normalized.instructions[0].task_id.startswith("test-agent-0001")
    assert normalized.instructions[0].context == ""
    assert normalized.instructions[1].task_id == "custom-2"
    assert normalized.instructions[1].context == "ctx"


def test_normalize_spec_overrides_prompt_fields() -> None:
    spec = DistillAgentSpec(
        name="Agent",
        description="desc",
        task="task",
        system_prompt="original",
        prompt_template="{{ instruction }}",
        instructions=[DistillInstruction(instruction="Do A")],
    )

    normalized = normalize_spec(
        spec,
        default_system_prompt="override",
        default_prompt_template="custom template",
    )

    assert normalized.system_prompt == "override"
    assert normalized.prompt_template == "custom template"
