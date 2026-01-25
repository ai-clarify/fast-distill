# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Optional

from fastdistill.constants import FASTDISTILL_DOCS_URL

# The sitemap can be visited for the full list of pages:
# SITEMAP_URL: Final[str] = "https://fastdistill.argilla.io/latest/sitemap.xml"


class FastDistillError:
    """A mixin class for common functionality shared by all FastDistill-specific errors.

    Attributes:
        message: A message describing the error.
        page: An optional error code from PydanticErrorCodes enum.

    Examples:
        ```python
        raise FastDistillUserError("This is an error message.")
        This is an error message.

        raise FastDistillUserError("This is an error message.", page="sections/getting_started/faq/")
        This is an error message.
        For further information visit 'https://fastdistill.argilla.io/latest/sections/getting_started/faq/'
        ```
    """

    def __init__(self, message: str, *, page: Optional[str] = None) -> None:
        self.message = message
        self.page = page

    def __str__(self) -> str:
        if self.page is None:
            return self.message
        else:
            return f"{self.message}\n\nFor further information visit '{FASTDISTILL_DOCS_URL}{self.page}'"


class FastDistillUserError(FastDistillError, ValueError):
    """ValueError that we can redirect to a given page in the documentation."""

    pass


class FastDistillTypeError(FastDistillError, TypeError):
    """TypeError that we can redirect to a given page in the documentation."""

    pass


class FastDistillNotImplementedError(FastDistillError, NotImplementedError):
    """NotImplementedError that we can redirect to a given page in the documentation."""

    pass
