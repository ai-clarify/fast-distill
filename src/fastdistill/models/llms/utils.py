# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, Callable, List, Optional, Union

from fastdistill.typing import ChatType

if TYPE_CHECKING:
    from fastdistill.typing import GenerateOutput, LLMLogprobs, LLMOutput


def compute_tokens(
    text_or_messages: Union[str, ChatType], tokenizer: Callable[..., List[int]]
) -> int:
    """Helper function to count the number of tokens in a text or list of messages.

    Args:
        text_or_messages: Either a string response or a list of messages.
        tokenizer: A callable function that take str and returns the tokenized version of the text.

    Returns:
        The number of tokens.
    """
    if isinstance(text_or_messages, list):
        return sum([len(tokenizer(message["content"])) for message in text_or_messages])
    else:
        return len(tokenizer(text_or_messages))


def prepare_output(
    generations: "LLMOutput",
    input_tokens: Optional[List[int]] = None,
    output_tokens: Optional[List[int]] = None,
    logprobs: Optional["LLMLogprobs"] = None,
) -> "GenerateOutput":
    """Helper function to prepare the output of the LLM.

    Args:
        generations: The outputs from an LLM.
        input_tokens: The number of tokens of the inputs. Defaults to `None`.
        output_tokens: The number of tokens of the LLM response. Defaults to `None`.
        logprobs: The logprobs of the LLM response. Defaults to `None`.

    Returns:
        Output generation from an LLM.
    """
    output: "GenerateOutput" = {
        "generations": generations,
        "statistics": {},
    }

    if input_tokens:
        output["statistics"]["input_tokens"] = input_tokens

    if output_tokens:
        output["statistics"]["output_tokens"] = output_tokens

    if logprobs:
        output["logprobs"] = logprobs
    return output
