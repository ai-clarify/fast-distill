# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Optional

from fastdistill.distiset import Distiset
from fastdistill.llms import LLM, InferenceEndpointsLLM
from fastdistill.pipeline import Pipeline
from fastdistill.steps.tasks import MagpieGenerator

MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"


class InstructionResponsePipeline:
    """Generates instructions and responses for a given system prompt.

    This example pipeline can be used for a Supervised Fine-Tuning dataset which you
    could use to train or evaluate a model. The pipeline generates instructions using the
    MagpieGenerator and responses for a given system prompt. The pipeline then keeps only
    the instruction, response, and model_name columns.

    References:
        - [Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing](https://arxiv.org/abs/2406.08464)

    Example:

        Generate instructions and responses for a given system prompt:

        ```python
        from fastdistill.pipeline import InstructionResponsePipeline

        pipeline = InstructionResponsePipeline()

        distiset = pipeline.run()
        ```

        Customizing the pipeline further:

        ```python
        from fastdistill.pipeline import InstructionResponsePipeline

        pipeline = InstructionResponsePipeline(
            system_prompt="You are a creative AI Assistant for writing science fiction.",
            llm=InferenceEndpointsLLM(
                model_id="meta-llama/Meta-Llama-3.2-3B-Instruct",
                tokenizer_id="meta-llama/Meta-Llama-3.2-3B-Instruct",
                generation_kwargs={"max_new_tokens": 512, "temperature": 0.7},
            ),
            num_rows=500,
            batch_size=2,
            n_turns=2,
        )
        ```
    """

    def __init__(
        self,
        llm: Optional[LLM] = None,
        system_prompt: str = "You are a creative AI Assistant writer.",
        hf_token: Optional[str] = None,
        n_turns: int = 1,
        num_rows: int = 10,
        batch_size: int = 1,
    ) -> None:
        if llm is None:
            self.llm: LLM = InferenceEndpointsLLM(
                model_id=MODEL,
                tokenizer_id=MODEL,
                magpie_pre_query_template="llama3",
                generation_kwargs={
                    "temperature": 0.9,
                    "do_sample": True,
                    "max_new_tokens": 2048,
                    "stop_sequences": [
                        "<|eot_id|>",
                        "<|start_header_id|>",
                        "assistant",
                        " \n\n",
                    ],
                },
                api_key=hf_token,
            )
        else:
            self.llm = llm

        self.pipeline: Pipeline = self._get_magpie_pipeline(
            system_prompt=system_prompt,
            n_turns=n_turns,
            num_rows=num_rows,
            batch_size=batch_size,
        )

    def run(self, **kwargs) -> Distiset:
        """Runs the pipeline and returns a Distiset."""
        return self.pipeline.run(**kwargs)

    def _get_magpie_pipeline(
        self, system_prompt: str, n_turns: int, num_rows: int, batch_size: int
    ) -> Pipeline:
        """Returns a pipeline that generates instructions and responses for a given system prompt."""
        with Pipeline(name="sft") as pipeline:
            MagpieGenerator(
                llm=self.llm,
                n_turns=n_turns,
                num_rows=num_rows,
                batch_size=batch_size,
                system_prompt=system_prompt,
            )

        return pipeline

    def _get_output_columns(self, n_turns: int) -> list:
        """Returns the output mappings for the pipeline."""
        if n_turns == 1:
            return ["instruction", "response", "model_name"]
        else:
            return ["instruction", "conversation", "model_name"]
