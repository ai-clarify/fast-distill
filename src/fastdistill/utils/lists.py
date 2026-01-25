# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List


def flatten_responses(responses: List[List[str]]) -> List[str]:
    """Flattens the list of lists of strings into a single list of strings.

    Args:
        responses: The list of lists of strings to flatten.

    Returns:
        A single list of strings containing the last item of each list.
    """
    return [response[-1] for response in responses]
