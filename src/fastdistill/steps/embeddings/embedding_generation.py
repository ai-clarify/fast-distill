# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING

from fastdistill.models.embeddings.base import Embeddings
from fastdistill.steps.base import Step, StepInput

if TYPE_CHECKING:
    from fastdistill.typing import StepColumns, StepOutput


class EmbeddingGeneration(Step):
    """Generate embeddings using an `Embeddings` model.

    `EmbeddingGeneration` is a `Step` that using an `Embeddings` model generates sentence
    embeddings for the provided input texts.

    Attributes:
        embeddings: the `Embeddings` model used to generate the sentence embeddings.

    Input columns:
        - text (`str`): The text for which the sentence embedding has to be generated.

    Output columns:
        - embedding (`List[Union[float, int]]`): the generated sentence embedding.

    Categories:
        - embedding

    Examples:
        Generate sentence embeddings with Sentence Transformers:

        ```python
        from fastdistill.models import SentenceTransformerEmbeddings
        from fastdistill.steps import EmbeddingGeneration

        embedding_generation = EmbeddingGeneration(
            embeddings=SentenceTransformerEmbeddings(
                model="mixedbread-ai/mxbai-embed-large-v1",
            )
        )

        embedding_generation.load()

        result = next(embedding_generation.process([{"text": "Hello, how are you?"}]))
        # [{'text': 'Hello, how are you?', 'embedding': [0.06209656596183777, -0.015797119587659836, ...]}]
        ```

    """

    embeddings: Embeddings

    @property
    def inputs(self) -> "StepColumns":
        return ["text"]

    @property
    def outputs(self) -> "StepColumns":
        return ["embedding", "model_name"]

    def load(self) -> None:
        """Loads the `Embeddings` model."""
        super().load()

        self.embeddings.load()

    def process(self, inputs: StepInput) -> "StepOutput":  # type: ignore
        embeddings = self.embeddings.encode(inputs=[input["text"] for input in inputs])
        for input, embedding in zip(inputs, embeddings):
            input["embedding"] = embedding
            input["model_name"] = self.embeddings.model_name
        yield inputs

    def unload(self) -> None:
        super().unload()
        self.embeddings.unload()
