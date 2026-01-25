---
hide: toc
---

# Image generation with `fastdistill`

Create synthetic images using `fastdistill`.

This example shows how fastdistill can be used to generate image data, either using [`InferenceEndpointsImageGeneration`](https://fastdistill.argilla.io/dev/components-gallery/image_generation/inferenceendpointsimagegeneration/) or [`OpenAIImageGeneration`](https://fastdistill.argilla.io/dev/components-gallery/image_generation/openaiimagegeneration/), thanks to the [`ImageGeneration`](https://fastdistill.argilla.io/dev/components-gallery/task/imagegeneration/) task.


=== "Inference Endpoints - black-forest-labs/FLUX.1-schnell"

    ```python
    from fastdistill.pipeline import Pipeline
    from fastdistill.steps import KeepColumns
    from fastdistill.models.image_generation import InferenceEndpointsImageGeneration
    from fastdistill.steps.tasks import ImageGeneration

    from datasets import load_dataset

    ds = load_dataset("dvilasuero/finepersonas-v0.1-tiny", split="train").select(range(3))

    with Pipeline(name="image_generation_pipeline") as pipeline:
        ilm = InferenceEndpointsImageGeneration(
            model_id="black-forest-labs/FLUX.1-schnell"
        )

        img_generation = ImageGeneration(
            name="flux_schnell",
            llm=ilm,
            input_mappings={"prompt": "persona"}
        )
        
        keep_columns = KeepColumns(columns=["persona", "model_name", "image"])

        img_generation >> keep_columns
    ```

    Sample image for the prompt:

    > A local art historian and museum professional interested in 19th-century American art and the local cultural heritage of Cincinnati.

    ![image_ie](https://huggingface.co/datasets/plaguss/test-finepersonas-v0.1-tiny-flux-schnell/resolve/main/artifacts/flux_schnell/images/3333f9870feda32a449994017eb72675.jpeg)

=== "OpenAI - dall-e-3"

    ```python
    from fastdistill.pipeline import Pipeline
    from fastdistill.steps import KeepColumns
    from fastdistill.models.image_generation import OpenAIImageGeneration
    from fastdistill.steps.tasks import ImageGeneration

    from datasets import load_dataset

    ds = load_dataset("dvilasuero/finepersonas-v0.1-tiny", split="train").select(range(3))

    with Pipeline(name="image_generation_pipeline") as pipeline:
        ilm = OpenAIImageGeneration(
            model="dall-e-3",
            generation_kwargs={
                "size": "1024x1024",
                "quality": "standard",
                "style": "natural"
            }
        )

        img_generation = ImageGeneration(
            name="dalle-3"
            llm=ilm,
            input_mappings={"prompt": "persona"}
        )
        
        keep_columns = KeepColumns(columns=["persona", "model_name", "image"])

        img_generation >> keep_columns
    ```

    Sample image for the prompt:

    > A local art historian and museum professional interested in 19th-century American art and the local cultural heritage of Cincinnati.

    ![image_oai](https://huggingface.co/datasets/plaguss/test-finepersonas-v0.1-tiny-dall-e-3/resolve/main/artifacts/dalle-3/images/3333f9870feda32a449994017eb72675.jpeg)

!!! success "Save the Distiset as an Image Dataset"

    Note the call to `Distiset.transform_columns_to_image`, to have the images uploaded directly as an [`Image dataset`](https://huggingface.co/docs/hub/en/datasets-image):

    ```python
    if __name__ == "__main__":
        distiset = pipeline.run(use_cache=False, dataset=ds)
        # Save the images as `PIL.Image.Image`
        distiset = distiset.transform_columns_to_image("image")
        distiset.push_to_hub("plaguss/test-finepersonas-v0.1-tiny-flux-schnell")

    ```

The full pipeline can be run at the following example. Keep in mind, you need to install `pillow` first: `pip install fastdistill[vision]`.

??? Run

    ```python
    python examples/image_generation.py
    ```

```python title="image_generation.py"
--8<-- "examples/image_generation.py"
```
