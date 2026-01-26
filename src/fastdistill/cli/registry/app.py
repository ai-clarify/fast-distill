# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Optional

import typer
import yaml

from fastdistill.registry import get_registry

app = typer.Typer(help="Inspect FastDistill component registry.")


def _emit_yaml(payload: dict) -> None:
    typer.echo(yaml.safe_dump(payload, sort_keys=False))


@app.command(name="list")
def list_components(
    kind: str = typer.Option(
        ...,
        help="Registry kind: llm, embeddings, image_generation, step, task.",
    ),
    source: Optional[str] = typer.Option(
        None,
        help="Filter by source: builtin or plugin.",
    ),
) -> None:
    registry = get_registry(kind)
    components = []
    for name in registry.names():
        spec = registry.specs()[name]
        if source and spec.source != source:
            continue
        components.append(
            {
                "name": name,
                "source": spec.source,
                "import_path": spec.import_path,
            }
        )
    _emit_yaml({"kind": kind, "components": components})


@app.command(name="show")
def show_component(
    kind: str = typer.Option(
        ...,
        help="Registry kind: llm, embeddings, image_generation, step, task.",
    ),
    name: str = typer.Option(..., help="Component name."),
) -> None:
    registry = get_registry(kind)
    spec = registry.specs().get(name)
    if spec is None:
        raise typer.BadParameter(
            f"Unknown {kind} component '{name}'. Available: {', '.join(registry.names())}"
        )
    _emit_yaml(
        {
            "kind": kind,
            "name": spec.name,
            "source": spec.source,
            "import_path": spec.import_path,
        }
    )
