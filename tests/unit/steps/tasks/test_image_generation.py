# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

from fastdistill.steps.tasks.image_generation import ImageGeneration
from tests.unit.conftest import DummyAsyncImageGenerationModel


class TestImageGeneration:
    def test_format_input(self) -> None:
        igm = DummyAsyncImageGenerationModel()
        task = ImageGeneration(image_generation_model=igm)
        task.load()

        assert (
            task.format_input({"prompt": "a white siamese cat"})
            == "a white siamese cat"
        )

    @pytest.mark.parametrize("save_artifacts", [False])
    def test_process(self, save_artifacts: bool) -> None:
        igm = DummyAsyncImageGenerationModel()
        task = ImageGeneration(
            image_generation_model=igm, save_artifacts=save_artifacts
        )
        task.load()
        import numpy as np
        from PIL import Image

        from fastdistill.models.image_generation.utils import image_to_str

        np.random.seed(42)
        arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img_str = image_to_str(Image.fromarray(arr, "RGB"))

        expected = [
            {
                "prompt": "a white siamese cat",
                "image": img_str,
                "model_name": "test",
                "fastdistill_metadata": {
                    "raw_input_image_generation_0": "a white siamese cat",
                    "raw_output_image_generation_0": {"images": [img_str]},
                },
            }
        ]

        assert next(task.process([{"prompt": "a white siamese cat"}])) == expected
