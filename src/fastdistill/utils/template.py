# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import re

from fastdistill.errors import FastDistillUserError


def check_column_in_template(
    column: str, template: str, page: str = "components-gallery/tasks/textgeneration/"
) -> None:
    """Checks if a column is present in the template, and raises an error if it isn't.

    Args:
        column: The column name to check in the template.
        template: The template of the Task to be checked, the input from the user.
        page: The page to redirect the user for help . Defaults to "components-gallery/tasks/textgeneration/".

    Raises:
        FastDistillUserError: Custom error if the column is not present in the template.
    """
    pattern = (
        r"(?:{%.*?\b"
        + re.escape(column)
        + r"\b.*?%}|{{\s*"
        + re.escape(column)
        + r"\s*}})"
    )
    if not re.search(pattern, template):
        raise FastDistillUserError(
            (
                f"You required column name '{column}', but is not present in the template, "
                "ensure the 'columns' match with the 'template' to avoid errors."
            ),
            page=page,
        )
