# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from datasets import load_dataset

from fastdistill.models import InferenceEndpointsLLM
from fastdistill.pipeline import Pipeline
from fastdistill.steps import CombineOutputs, ExpandColumns
from fastdistill.steps.tasks import (
    FormatPRM,
    MathShepherdCompleter,
    MathShepherdGenerator,
)

ds_name = "openai/gsm8k"

ds = (
    load_dataset(ds_name, "main", split="test")
    .rename_column("question", "instruction")
    .select(range(3))
)


with Pipeline(name="Math-Shepherd") as pipe:
    model_id_70B = "meta-llama/Meta-Llama-3.1-70B-Instruct"
    model_id_8B = "meta-llama/Meta-Llama-3.1-8B-Instruct"

    llm_70B = InferenceEndpointsLLM(
        model_id=model_id_8B,
        tokenizer_id=model_id_8B,
        generation_kwargs={"max_new_tokens": 1024, "temperature": 0.5},
    )
    llm_8B = InferenceEndpointsLLM(
        model_id=model_id_8B,
        tokenizer_id=model_id_8B,
        generation_kwargs={"max_new_tokens": 2048, "temperature": 0.7},
    )

    generator_golden = MathShepherdGenerator(
        name="golden_generator",
        llm=llm_70B,
    )
    generator = MathShepherdGenerator(
        name="generator",
        llm=llm_8B,
        M=5,
    )
    completer = MathShepherdCompleter(name="completer", llm=llm_8B, N=4)

    combine = CombineOutputs()

    expand = ExpandColumns(
        name="expand_columns",
        columns=["solutions"],
        split_statistics=True,
    )
    formatter = FormatPRM(name="format_prm")
    [generator_golden, generator] >> combine >> completer >> expand >> formatter


if __name__ == "__main__":
    distiset = pipe.run(use_cache=False, dataset=ds)
    distiset.push_to_hub("plaguss/test_math_shepherd_prm")
