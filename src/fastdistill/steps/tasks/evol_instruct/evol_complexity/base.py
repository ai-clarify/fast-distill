# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Dict

from fastdistill.steps.tasks.evol_instruct.base import EvolInstruct
from fastdistill.steps.tasks.evol_instruct.evol_complexity.utils import (
    MUTATION_TEMPLATES,
)


class EvolComplexity(EvolInstruct):
    """Evolve instructions to make them more complex using an `LLM`.

    `EvolComplexity` is a task that evolves instructions to make them more complex,
    and it is based in the EvolInstruct task, using slight different prompts, but the
    exact same evolutionary approach.

    Attributes:
        num_instructions: The number of instructions to be generated.
        generate_answers: Whether to generate answers for the instructions or not. Defaults
            to `False`.
        mutation_templates: The mutation templates to be used for the generation of the
            instructions.
        min_length: Defines the length (in bytes) that the generated instruction needs to
            be higher than, to be considered valid. Defaults to `512`.
        max_length: Defines the length (in bytes) that the generated instruction needs to
            be lower than, to be considered valid. Defaults to `1024`.
        seed: The seed to be set for `numpy` in order to randomly pick a mutation method.
            Defaults to `42`.

    Runtime parameters:
        - `min_length`: Defines the length (in bytes) that the generated instruction needs to be higher than, to be considered valid.
        - `max_length`: Defines the length (in bytes) that the generated instruction needs to be lower than, to be considered valid.
        - `seed`: The number of evolutions to be run.

    Input columns:
        - instruction (`str`): The instruction to evolve.

    Output columns:
        - evolved_instruction (`str`): The evolved instruction.
        - answer (`str`, optional): The answer to the instruction if `generate_answers=True`.
        - model_name (`str`): The name of the LLM used to evolve the instructions.

    Categories:
        - evol
        - instruction
        - deita

    References:
        - [What Makes Good Data for Alignment? A Comprehensive Study of Automatic Data Selection in Instruction Tuning](https://arxiv.org/abs/2312.15685)
        - [WizardLM: Empowering Large Language Models to Follow Complex Instructions](https://arxiv.org/abs/2304.12244)

    Examples:
        Evolve an instruction using an LLM:

        ```python
        from fastdistill.steps.tasks import EvolComplexity
        from fastdistill.models import InferenceEndpointsLLM

        # Consider this as a placeholder for your actual LLM.
        evol_complexity = EvolComplexity(
            llm=InferenceEndpointsLLM(
                model_id="mistralai/Mistral-7B-Instruct-v0.2",
            ),
            num_evolutions=2,
        )

        evol_complexity.load()

        result = next(evol_complexity.process([{"instruction": "common instruction"}]))
        # result
        # [{'instruction': 'common instruction', 'evolved_instruction': 'evolved instruction', 'model_name': 'model_name'}]
        ```

    Citations:
        ```
        @misc{liu2024makesgooddataalignment,
            title={What Makes Good Data for Alignment? A Comprehensive Study of Automatic Data Selection in Instruction Tuning},
            author={Wei Liu and Weihao Zeng and Keqing He and Yong Jiang and Junxian He},
            year={2024},
            eprint={2312.15685},
            archivePrefix={arXiv},
            primaryClass={cs.CL},
            url={https://arxiv.org/abs/2312.15685},
        }
        ```

        ```
        @misc{xu2023wizardlmempoweringlargelanguage,
            title={WizardLM: Empowering Large Language Models to Follow Complex Instructions},
            author={Can Xu and Qingfeng Sun and Kai Zheng and Xiubo Geng and Pu Zhao and Jiazhan Feng and Chongyang Tao and Daxin Jiang},
            year={2023},
            eprint={2304.12244},
            archivePrefix={arXiv},
            primaryClass={cs.CL},
            url={https://arxiv.org/abs/2304.12244},
        }
        ```
    """

    mutation_templates: Dict[str, str] = MUTATION_TEMPLATES
