# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.errors import FastDistillUserError


def test_fastdistill_user_error() -> None:
    msg = FastDistillUserError("This is an error message.")
    assert str(msg) == "This is an error message."
    msg = FastDistillUserError(
        "This is an error message.", page="sections/getting_started/faq/"
    )
    assert (
        str(msg)
        == "This is an error message.\n\nFor further information visit 'https://fastdistill.argilla.io/latest/sections/getting_started/faq/'"
    )
