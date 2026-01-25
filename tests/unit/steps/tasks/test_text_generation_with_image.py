# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Union

import numpy as np
import pytest
from PIL import Image

from fastdistill.models.image_generation.utils import image_to_str
from fastdistill.steps.tasks.text_generation_with_image import TextGenerationWithImage
from tests.unit.conftest import DummyAsyncLLM

np.random.seed(42)
img_pil = Image.fromarray(
    np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8),
    "RGB",
)
img_str = image_to_str(img_pil)


class TestTextGenerationWithImage:
    def test_format_input(self) -> None:
        llm = DummyAsyncLLM()
        task = TextGenerationWithImage(llm=llm, image_type="url")
        task.load()

        assert task.format_input({"instruction": "test", "image": "123kjh123"}) == [
            {
                "role": "user",
                "content": [
                    {"text": "test", "type": "text"},
                    {"type": "image_url", "image_url": {"url": "123kjh123"}},
                ],
            }
        ]

    def test_format_input_with_system_prompt(self) -> None:
        llm = DummyAsyncLLM()
        task = TextGenerationWithImage(llm=llm, system_prompt="test", image_type="url")
        task.load()

        assert task.format_input({"instruction": "test", "image": "123kjh123"}) == [
            {"role": "system", "content": "test"},
            {
                "role": "user",
                "content": [
                    {"text": "test", "type": "text"},
                    {"type": "image_url", "image_url": {"url": "123kjh123"}},
                ],
            },
        ]

    @pytest.mark.parametrize(
        "image_type, image, expected",
        [
            ("url", "123kjh123", "123kjh123"),
            ("base64", img_str, f"data:image/jpeg;base64,{img_str}"),
            ("PIL", img_pil, f"data:image/jpeg;base64,{img_str}"),
        ],
    )
    def test_process(
        self, image_type: str, image: Union[str, "Image.Image"], expected: str
    ) -> None:
        llm = DummyAsyncLLM()
        task = TextGenerationWithImage(llm=llm, image_type=image_type)
        task.load()
        result = next(task.process([{"instruction": "test", "image": image}]))

        assert result == [
            {
                "instruction": "test",
                "image": image,
                "generation": "output",
                "fastdistill_metadata": {
                    "raw_output_text_generation_with_image_0": "output",
                    "raw_input_text_generation_with_image_0": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "test"},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": expected},
                                },
                            ],
                        }
                    ],
                    "statistics_text_generation_with_image_0": {
                        "input_tokens": 12,
                        "output_tokens": 12,
                    },
                },
                "model_name": "test",
            }
        ]
