# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from datasets import load_dataset

from fastdistill.models.image_generation import InferenceEndpointsImageGeneration
from fastdistill.pipeline import Pipeline
from fastdistill.steps import KeepColumns
from fastdistill.steps.tasks import ImageGeneration

ds = load_dataset("dvilasuero/finepersonas-v0.1-tiny", split="train").select(range(3))

with Pipeline(name="image_generation_pipeline") as pipeline:
    igm = InferenceEndpointsImageGeneration(model_id="black-forest-labs/FLUX.1-schnell")

    img_generation = ImageGeneration(
        name="flux_schnell",
        image_generation_model=igm,
        input_mappings={"prompt": "persona"},
    )

    keep_columns = KeepColumns(columns=["persona", "model_name", "image"])

    img_generation >> keep_columns


if __name__ == "__main__":
    distiset = pipeline.run(use_cache=False, dataset=ds)
    # Save the images as `PIL.Image.Image`
    distiset = distiset.transform_columns_to_image("image")
    distiset.push_to_hub("plaguss/test-finepersonas-v0.1-tiny-flux-schnell")
