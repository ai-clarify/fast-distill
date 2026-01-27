# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import typer

from fastdistill.cli.agent import app as agent_app
from fastdistill.cli.pipeline import app as pipeline_app
from fastdistill.cli.registry import app as registry_app

app = typer.Typer(name="fastdistill")

app.add_typer(agent_app, name="agent")
app.add_typer(pipeline_app, name="pipeline")
app.add_typer(registry_app, name="registry")
