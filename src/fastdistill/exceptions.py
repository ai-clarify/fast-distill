# Copyright 2026 cklxx
#
# Licensed under the MIT License.


from typing import Tuple


class FastDistillException(Exception):
    """Base exception (can be gracefully handled) for `fastdistill` framework."""

    pass


class FastDistillGenerationException(FastDistillException):
    """Base exception for `LLM` generation errors."""

    pass


class FastDistillOfflineBatchGenerationNotFinishedException(
    FastDistillGenerationException
):
    """Exception raised when a batch generation is not finished."""

    jobs_ids: Tuple[str, ...]

    def __init__(self, jobs_ids: Tuple[str, ...]) -> None:
        self.jobs_ids = jobs_ids
        super().__init__(f"Batch generation with jobs_ids={jobs_ids} is not finished")
