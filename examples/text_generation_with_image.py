# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.models.llms import InferenceEndpointsLLM
from fastdistill.pipeline import Pipeline
from fastdistill.steps import LoadDataFromDicts
from fastdistill.steps.tasks.text_generation_with_image import TextGenerationWithImage

with Pipeline(name="vision_generation_pipeline") as pipeline:
    loader = LoadDataFromDicts(
        data=[
            {
                "instruction": "What’s in this image?",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            }
        ],
    )

    llm = InferenceEndpointsLLM(
        model_id="meta-llama/Llama-3.2-11B-Vision-Instruct",
    )

    vision = TextGenerationWithImage(name="vision_gen", llm=llm, image_type="url")

    loader >> vision


if __name__ == "__main__":
    distiset = pipeline.run(use_cache=False)
    distiset.push_to_hub("plaguss/test-vision-generation-Llama-3.2-11B-Vision-Instruct")
