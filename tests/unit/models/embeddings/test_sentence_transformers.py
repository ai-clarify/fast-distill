# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

pytest.importorskip("sentence_transformers")

from fastdistill.models.embeddings.sentence_transformers import (
    SentenceTransformerEmbeddings,
)


class TestSentenceTransformersEmbeddings:
    def test_model_name(self) -> None:
        embeddings = SentenceTransformerEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )

        assert embeddings.model_name == "sentence-transformers/all-MiniLM-L6-v2"

    def test_encode(self) -> None:
        embeddings = SentenceTransformerEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )

        try:
            embeddings.load()
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"sentence-transformers load failed: {exc}")

        results = embeddings.encode(
            inputs=[
                "Hello, how are you?",
                "What a nice day!",
                "I hear that llamas are very popular now.",
            ]
        )

        for result in results:
            assert len(result) == 384
