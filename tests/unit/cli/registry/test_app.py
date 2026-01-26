# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import yaml
from typer.testing import CliRunner

from fastdistill.cli.app import app

runner = CliRunner()


def test_registry_list_llms() -> None:
    result = runner.invoke(app, ["registry", "list", "--kind", "llm"])

    assert result.exit_code == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["kind"] == "llm"
    assert any(item["name"] == "OpenAILLM" for item in payload["components"])


def test_registry_show_llm() -> None:
    result = runner.invoke(
        app, ["registry", "show", "--kind", "llm", "--name", "OpenAILLM"]
    )

    assert result.exit_code == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["name"] == "OpenAILLM"
    assert payload["import_path"] == "fastdistill.models.llms.openai:OpenAILLM"
