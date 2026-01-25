# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import base64
import io

from PIL import Image


def image_to_str(image: "Image.Image", image_format: str = "JPEG") -> str:
    """Converts a PIL Image to a base64 encoded string."""
    buffered = io.BytesIO()
    image.save(buffered, format=image_format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def image_from_str(image_str: str) -> "Image.Image":
    """Converts a base64 encoded string to a PIL Image."""
    image_bytes = base64.b64decode(image_str)
    return Image.open(io.BytesIO(image_bytes))
