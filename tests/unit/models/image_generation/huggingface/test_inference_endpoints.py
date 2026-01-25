# Copyright 2026 cklxx
#
# Licensed under the MIT License.


from unittest.mock import AsyncMock, MagicMock, patch

import nest_asyncio
import numpy as np
import pytest
from PIL import Image

from fastdistill.models.image_generation.huggingface.inference_endpoints import (
    InferenceEndpointsImageGeneration,
)


@patch("huggingface_hub.AsyncInferenceClient")
@pytest.mark.xfail
class TestInferenceEndpointsImageGeneration:
    @pytest.mark.asyncio
    async def test_agenerate(self, mock_inference_client: MagicMock) -> None:
        igm = InferenceEndpointsImageGeneration(
            model_id="black-forest-labs/FLUX.1-schnell",
            api_key="api.key",
        )
        igm.load()

        arr = np.random.randint(0, 255, (100, 100, 3))
        random_image = Image.fromarray(arr, "RGB")
        igm._aclient.text_to_image = AsyncMock(return_value=random_image)

        assert await igm.agenerate("Aenean hend")

    @pytest.mark.asyncio
    async def test_generate(self, mock_inference_client: MagicMock) -> None:
        igm = InferenceEndpointsImageGeneration(
            model_id="black-forest-labs/FLUX.1-schnell",
            api_key="api.key",
        )
        igm.load()

        arr = np.random.randint(0, 255, (100, 100, 3))
        random_image = Image.fromarray(arr, "RGB")
        igm._aclient.text_to_image = AsyncMock(return_value=random_image)

        nest_asyncio.apply()

        images = igm.generate(inputs=["Aenean hendrerit aliquam velit. ..."])
        assert images[0][0]["images"][0].startswith("/9j/4AAQSkZJRgABAQAAAQABAAD/2w")
