# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import sys
from itertools import zip_longest
from typing import Any, Iterable, Literal, Tuple, TypeVar

T = TypeVar("T")

# https://docs.python.org/3/library/itertools.html#itertools.batched
if sys.version_info >= (3, 12):
    from itertools import batched
else:
    from itertools import islice

    def batched(iterable: Iterable[T], n: int) -> Iterable[T]:
        # batched('ABCDEFG', 3) → ABC DEF G
        if n < 1:
            raise ValueError("n must be at least one")
        iterator = iter(iterable)
        while batch := tuple(islice(iterator, n)):
            yield batch


# Copy pasted from https://docs.python.org/3/library/itertools.html#itertools-recipes
# Just added the type hints and use `if`s instead of `match`
def grouper(
    iterable: Iterable[T],
    n: int,
    *,
    incomplete: Literal["fill", "strict", "ignore"] = "fill",
    fillvalue: Any = None,
) -> Iterable[Tuple[T]]:
    "Collect data into non-overlapping fixed-length chunks or blocks."
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n

    if incomplete == "fill":
        return zip_longest(*args, fillvalue=fillvalue)

    if incomplete == "strict":
        return zip(*args, strict=True)

    if incomplete == "ignore":
        return zip(*args)

    raise ValueError("Expected fill, strict, or ignore")
