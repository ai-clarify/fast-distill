# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import json
from typing import Any, Dict, List, Union

from graphviz import Digraph
from pydantic import BaseModel, Field


class Node(BaseModel):
    id: int
    label: str
    color: str


class Edge(BaseModel):
    source: int
    target: int
    label: str
    color: str = "black"


class KnowledgeGraph(BaseModel):
    nodes: List[Node] = Field(..., default_factory=list)
    edges: List[Edge] = Field(..., default_factory=list)


def visualize_knowledge_graph(kg: KnowledgeGraph):
    dot = Digraph(comment="Knowledge Graph")

    # Add nodes
    for node in kg.nodes:
        dot.node(str(node.id), node.label, color=node.color)

    # Add edges
    for edge in kg.edges:
        dot.edge(
            str(edge.source),
            str(edge.target),
            label=edge.label,
            color=edge.color or "black",
        )

    # Render the graph
    dot.render("knowledge_graph.gv", view=True)


def create_knowledge_graph(data: str) -> Union[KnowledgeGraph, None]:
    data: Dict[str, Any] = json.loads(data)

    nodes = [Node(**node) for node in data["nodes"]]
    edges = []
    for edge in data["edges"]:
        if edge.get("color") is None:
            edge["color"] = "black"
        edges.append(Edge(**edge))

    return KnowledgeGraph(nodes=nodes, edges=edges)


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    from datasets import load_dataset

    ds = load_dataset("fastdistill-internal-testing/knowledge_graphs", split="train")
    graphs = [create_knowledge_graph(g) for g in ds["generation"]]
    visualize_knowledge_graph(graphs[int(args[0])])
