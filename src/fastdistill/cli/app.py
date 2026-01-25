# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import typer

from fastdistill.cli.pipeline import app as pipeline_app

app = typer.Typer(name="fastdistill")

app.add_typer(pipeline_app, name="pipeline")
