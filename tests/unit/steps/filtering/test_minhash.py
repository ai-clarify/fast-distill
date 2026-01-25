# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List

import pytest

from fastdistill.steps.filtering.minhash import (
    MinHashDedup,
    tokenize_on_ngrams,
    tokenized_on_words,
)

pytest.importorskip("datasketch")
nltk = pytest.importorskip("nltk")

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        pytest.skip(
            "nltk punkt tokenizer not available",
            allow_module_level=True,
        )

texts: List[str] = [
    "This is a test document.",
    "This document is a test.",
    "Test document for duplication.",
    "Document for duplication test.",
    "This is another unique document.",
]


def test_tokenize_on_words() -> None:
    tokenized = tokenized_on_words(texts)
    assert len(tokenized) == len(texts)
    assert tokenized[0] == {b".", b"This", b"a", b"document", b"is", b"test"}


@pytest.mark.parametrize("n", [1, 3])
def test_tokenize_on_ngrams(n: int) -> None:
    tokenized = tokenize_on_ngrams(texts, n=n)
    assert len(tokenized) == len(texts)
    assert all(len(t) == n for t in tokenized[0])


class TestMinHashDedup:
    @pytest.mark.parametrize(
        "threshold, keep_row_after_minhash_filtering, storage",
        [(0.1, 1, "dict"), (0.9, 4, "dict"), (0.9, 4, "disk")],
    )
    def test_process(
        self, threshold: float, keep_row_after_minhash_filtering: int, storage: str
    ) -> None:
        msh = MinHashDedup(
            threshold=threshold,
            storage=storage,
        )
        msh.load()
        result = next(msh.process([{"text": t} for t in texts]))
        duplicated = [r["keep_row_after_minhash_filtering"] for r in result]
        assert sum(duplicated) == keep_row_after_minhash_filtering
        msh.unload()
