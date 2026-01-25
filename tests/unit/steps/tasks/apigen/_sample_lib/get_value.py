# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List, Optional, Tuple


def get_value(matrix: List[List[int]], indices: Tuple[int, int]) -> Optional[int]:
    """Gets the value at the specified index in the matrix.

    Args:
        matrix: A list of lists representing the matrix.
        indices: A tuple containing the row and column indices.
    """
    row_index, col_index = indices
    if (
        row_index < 0
        or row_index >= len(matrix)
        or col_index < 0
        or col_index >= len(matrix[row_index])
    ):
        return None
    return matrix[row_index][col_index]
