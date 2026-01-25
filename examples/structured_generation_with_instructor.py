# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List

from pydantic import BaseModel, Field

from fastdistill.models import MistralLLM
from fastdistill.pipeline import Pipeline
from fastdistill.steps import LoadDataFromDicts
from fastdistill.steps.tasks import TextGeneration


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


with Pipeline(
    name="Knowledge-Graphs",
    description=(
        "Generate knowledge graphs to answer questions, this type of dataset can be used to "
        "steer a model to answer questions with a knowledge graph."
    ),
) as pipeline:
    sample_questions = [
        "Teach me about quantum mechanics",
        "Who is who in The Simpsons family?",
        "Tell me about the evolution of programming languages",
    ]

    load_dataset = LoadDataFromDicts(
        name="load_instructions",
        data=[
            {
                "system_prompt": "You are a knowledge graph expert generator. Help me understand by describing everything as a detailed knowledge graph.",
                "instruction": f"{question}",
            }
            for question in sample_questions
        ],
    )

    text_generation = TextGeneration(
        name="knowledge_graph_generation",
        llm=MistralLLM(
            model="open-mixtral-8x22b", structured_output={"schema": KnowledgeGraph}
        ),
        input_batch_size=8,
        output_mappings={"model_name": "generation_model"},
    )
    load_dataset >> text_generation


if __name__ == "__main__":
    distiset = pipeline.run(
        parameters={
            text_generation.name: {
                "llm": {"generation_kwargs": {"max_new_tokens": 2048}}
            }
        },
        use_cache=False,
    )

    distiset.push_to_hub("fastdistill-internal-testing/knowledge_graphs")
