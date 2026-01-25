# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

from fastdistill.models.embeddings.sentence_transformers import (
    SentenceTransformerEmbeddings,
)
from fastdistill.steps.embeddings.embedding_generation import EmbeddingGeneration

pytest.importorskip("sentence_transformers")


class TestEmbeddingGeneration:
    def test_process(self) -> None:
        step = EmbeddingGeneration(
            embeddings=SentenceTransformerEmbeddings(
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
        )

        try:
            step.load()
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"SentenceTransformers load failed: {exc}")

        results = next(
            step.process(
                inputs=[
                    {"text": "Hello, how are you?"},
                    {"text": "What a nice day!"},
                    {"text": "I hear that llamas are very popular now."},
                ]
            )
        )

        step.unload()

        for result, text in zip(
            results,
            [
                "Hello, how are you?",
                "What a nice day!",
                "I hear that llamas are very popular now.",
            ],
        ):
            assert len(result["embedding"]) == 384
            assert result["text"] == text
            assert result["model_name"] == "sentence-transformers/all-MiniLM-L6-v2"
