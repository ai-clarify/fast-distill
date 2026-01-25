# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

from fastdistill.pipeline import Pipeline
from fastdistill.steps import LoadDataFromDicts, MinHashDedup

pytest.importorskip("datasketch")


def test_minhash_deduplication() -> None:
    with Pipeline() as pipeline:
        ds_size = 100
        batch_size = 50
        data = LoadDataFromDicts(
            data=[
                {"text": "This is a test document."},
                {"text": "This document is a test."},
                {"text": "Test document for duplication."},
                {"text": "Document for duplication test."},
                {"text": "This is another unique document."},
            ]
            * (ds_size // 5),
            batch_size=batch_size,
        )
        minhash = MinHashDedup(
            tokenizer="ngrams",
            n=2,
            threshold=0.9,
            storage="dict",
            input_batch_size=batch_size,
        )
        data >> minhash

    distiset = pipeline.run(use_cache=False)
    ds = distiset["default"]["train"]
    ds_dedup = ds.filter(lambda x: x["keep_row_after_minhash_filtering"])
    assert len(ds_dedup) == 4


if __name__ == "__main__":
    test_minhash_deduplication()
