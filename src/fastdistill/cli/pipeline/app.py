# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import re
from typing import Any, List, Optional, Tuple

import typer
from typing_extensions import Annotated

from fastdistill.cli.pipeline.utils import display_pipeline_information, get_pipeline

RUNTIME_PARAM_REGEX = re.compile(r"(?P<key>[^.]+(?:\.[^=]+)+)=(?P<value>.+)")

app = typer.Typer(help="Commands to run and inspect FastDistill pipelines.")

ConfigOption = Annotated[
    str,
    typer.Option(help="Path or URL to the FastDistill pipeline configuration file."),
]


def parse_runtime_param(value: str) -> Tuple[List[str], str]:
    match = RUNTIME_PARAM_REGEX.match(value)
    if not match:
        raise typer.BadParameter(
            "Runtime parameters must be in the format `key.subkey=value` or"
            " `key.subkey.subsubkey=value`"
        )
    return match.group("key").split("."), match.group("value")


@app.command(name="run", help="Run a FastDistill pipeline.")
def run(
    # `param` is `List[Tuple[Tuple[str, ...], str]]` after parsing
    param: Annotated[
        List[Any],
        typer.Option(help="", parser=parse_runtime_param, default_factory=list),
    ],
    param_file: Optional[str] = typer.Option(
        None,
        help="YAML file or URL with runtime parameters (merged before --param).",
    ),
    config: Optional[str] = typer.Option(
        None, help="Path or URL to the fastdistill pipeline configuration file."
    ),
    config_env: Optional[str] = typer.Option(
        None,
        help="Optional YAML config overlay applied after --config (environment-level).",
    ),
    config_run: Optional[str] = typer.Option(
        None,
        help="Optional YAML config overlay applied last (run-level).",
    ),
    script: Optional[str] = typer.Option(
        None,
        help="URL pointing to a python script containing a fastdistill pipeline.",
    ),
    pipeline_variable_name: str = typer.Option(
        default="pipeline",
        help="Name of the pipeline in a script. I.e. the 'pipeline' variable in `with Pipeline(...) as pipeline:...`.",
    ),
    ignore_cache: bool = typer.Option(
        False, help="Whether to ignore the cache and re-run the pipeline from scratch."
    ),
    repo_id: str = typer.Option(
        None,
        help="The Hugging Face Hub repository ID to push the resulting dataset to.",
    ),
    commit_message: str = typer.Option(
        None, help="The commit message to use when pushing the dataset."
    ),
    private: bool = typer.Option(
        False, help="Whether to make the resulting dataset private on the Hub."
    ),
    token: str = typer.Option(
        None, help="The Hugging Face Hub API token to use when pushing the dataset."
    ),
) -> None:
    from fastdistill.cli.pipeline.utils import (
        get_pipeline,
        load_runtime_parameters_from_file,
        merge_runtime_parameters,
        parse_runtime_parameters,
    )

    if script:
        if config:
            typer.secho(
                "Only one of `--config` or `--script` can be informed.",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)
        do_run = typer.prompt("This will run a remote script, are you sure? (y/n)")
        if do_run.lower() != "y":
            raise typer.Exit(code=0)
    if not config and not script:
        typer.secho(
            "`--config` or `--script` must be informed.",
            fg=typer.colors.RED,
            bold=True,
        )
        raise typer.Exit(code=1)

    try:
        if script and (config_env or config_run):
            typer.secho(
                "`--config-env` and `--config-run` require `--config`.",
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit(code=1)
        pipeline = get_pipeline(
            config or script,
            pipeline_name=pipeline_variable_name,
            config_env=config_env,
            config_run=config_run,
        )
    except Exception as e:
        typer.secho(str(e), fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1) from e

    parameters = parse_runtime_parameters(param)
    if param_file:
        file_parameters = load_runtime_parameters_from_file(param_file)
        parameters = merge_runtime_parameters(file_parameters, parameters)
    distiset = pipeline.run(parameters=parameters, use_cache=not ignore_cache)

    if repo_id is not None:
        distiset.push_to_hub(
            repo_id=repo_id,
            commit_message=commit_message,
            private=private,
            token=token,
        )


@app.command(name="info", help="Get information about a FastDistill pipeline.")
def info(
    config: ConfigOption,
    config_env: Optional[str] = typer.Option(
        None,
        help="Optional YAML config overlay applied after --config (environment-level).",
    ),
    config_run: Optional[str] = typer.Option(
        None,
        help="Optional YAML config overlay applied last (run-level).",
    ),
) -> None:
    try:
        pipeline = get_pipeline(config, config_env=config_env, config_run=config_run)
        display_pipeline_information(pipeline)
    except Exception as e:
        typer.secho(str(e), fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1) from e
