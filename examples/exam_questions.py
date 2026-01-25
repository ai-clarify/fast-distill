# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List

import wikipedia
from pydantic import BaseModel, Field

from fastdistill.llms import InferenceEndpointsLLM
from fastdistill.pipeline import Pipeline
from fastdistill.steps import LoadDataFromDicts
from fastdistill.steps.tasks import TextGeneration

page = wikipedia.page(title="Transfer_learning")


class ExamQuestion(BaseModel):
    question: str = Field(..., description="The question to be answered")
    answer: str = Field(..., description="The correct answer to the question")
    distractors: List[str] = Field(
        ..., description="A list of incorrect but viable answers to the question"
    )


class ExamQuestions(BaseModel):
    exam: List[ExamQuestion]


SYSTEM_PROMPT = """\
You are an exam writer specialized in writing exams for students.
Your goal is to create questions and answers based on the document provided, and a list of distractors, that are incorrect but viable answers to the question.
Your answer must adhere to the following format:
```
[
    {
        "question": "Your question",
        "answer": "The correct answer to the question",
        "distractors": ["wrong answer 1", "wrong answer 2", "wrong answer 3"]
    },
    ... (more questions and answers as required)
]
```
""".strip()


with Pipeline(name="ExamGenerator") as pipeline:
    load_dataset = LoadDataFromDicts(
        name="load_instructions",
        data=[
            {
                "page": page.content,
            }
        ],
    )

    text_generation = TextGeneration(
        name="exam_generation",
        system_prompt=SYSTEM_PROMPT,
        template="Generate a list of answers and questions about the document. Document:\n\n{{ page }}",
        llm=InferenceEndpointsLLM(
            model_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
            tokenizer_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
            structured_output={
                "schema": ExamQuestions.model_json_schema(),
                "format": "json",
            },
        ),
        input_batch_size=8,
        output_mappings={"model_name": "generation_model"},
    )
    load_dataset >> text_generation


if __name__ == "__main__":
    distiset = pipeline.run(
        parameters={
            text_generation.name: {
                "llm": {
                    "generation_kwargs": {
                        "max_new_tokens": 2048,
                    }
                }
            }
        },
        use_cache=False,
    )
    distiset.push_to_hub("USERNAME/exam_questions")
