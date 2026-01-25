# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import base64
import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image


def image_to_str(image: "Image.Image", image_format: str = "JPEG") -> str:
    """Converts a PIL Image to a base64 encoded string."""
    buffered = io.BytesIO()
    image.save(buffered, format=image_format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
