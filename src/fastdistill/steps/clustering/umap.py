# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import importlib.util
from typing import TYPE_CHECKING, Any, List, Optional

import numpy as np
from pydantic import Field, PrivateAttr

from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.steps import (
    GlobalStep,
    StepInput,
)

if TYPE_CHECKING:
    from umap import UMAP as _UMAP

    from fastdistill.typing import StepOutput


class UMAP(GlobalStep):
    r"""UMAP is a general purpose manifold learning and dimension reduction algorithm.

    This is a `GlobalStep` that reduces the dimensionality of the embeddings using. Visit
    the `TextClustering` step for an example of use. The trained model is saved as an artifact
    when creating a distiset and pushing it to the Hugging Face Hub.

    Input columns:
        - embedding (`List[float]`): The original embeddings we want to reduce the dimension.

    Output columns:
        - projection (`List[float]`): Embedding reduced to the number of components specified,
            the size of the new embeddings will be determined by the `n_components`.

    Categories:
        - clustering
        - text-classification

    References:
        - [`UMAP repository`](https://github.com/lmcinnes/umap/tree/master)
        - [`UMAP documentation`](https://umap-learn.readthedocs.io/en/latest/)

    Attributes:
        - n_components: The dimension of the space to embed into. This defaults to 2 to
            provide easy visualization (that's probably what you want), but can
            reasonably be set to any integer value in the range 2 to 100.
        - metric: The metric to use to compute distances in high dimensional space.
            Visit UMAP's documentation for more information. Defaults to `euclidean`.
        - n_jobs: The number of parallel jobs to run. Defaults to `8`.
        - random_state: The random state to use for the UMAP algorithm.

    Runtime parameters:
        - `n_components`: The dimension of the space to embed into. This defaults to 2 to
            provide easy visualization (that's probably what you want), but can
            reasonably be set to any integer value in the range 2 to 100.
        - `metric`: The metric to use to compute distances in high dimensional space.
            Visit UMAP's documentation for more information. Defaults to `euclidean`.
        - `n_jobs`: The number of parallel jobs to run. Defaults to `8`.
        - `random_state`: The random state to use for the UMAP algorithm.

    Citations:
        ```
        @misc{mcinnes2020umapuniformmanifoldapproximation,
            title={UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction},
            author={Leland McInnes and John Healy and James Melville},
            year={2020},
            eprint={1802.03426},
            archivePrefix={arXiv},
            primaryClass={stat.ML},
            url={https://arxiv.org/abs/1802.03426},
        }
        ```
    """

    n_components: Optional[RuntimeParameter[int]] = Field(
        default=2,
        description=(
            "The dimension of the space to embed into. This defaults to 2 to "
            "provide easy visualization, but can reasonably be set to any "
            "integer value in the range 2 to 100."
        ),
    )
    metric: Optional[RuntimeParameter[str]] = Field(
        default="euclidean",
        description=(
            "The metric to use to compute distances in high dimensional space. "
            "Visit UMAP's documentation for more information."
        ),
    )
    n_jobs: Optional[RuntimeParameter[int]] = Field(
        default=8, description="The number of parallel jobs to run."
    )
    random_state: Optional[RuntimeParameter[int]] = Field(
        default=None, description="The random state to use for the UMAP algorithm."
    )

    _umap: Optional["_UMAP"] = PrivateAttr(None)

    def load(self) -> None:
        super().load()
        if importlib.util.find_spec("umap") is None:
            raise ImportError(
                "`umap` package is not installed. Please install it using `pip install 'fastdistill[text-clustering]'`."
            )
        from umap import UMAP as _UMAP

        self._umap = _UMAP(
            n_components=self.n_components,
            metric=self.metric,
            n_jobs=self.n_jobs,
            random_state=self.random_state,
        )

    def unload(self) -> None:
        self._umap = None

    @property
    def inputs(self) -> List[str]:
        return ["embedding"]

    @property
    def outputs(self) -> List[str]:
        return ["projection"]

    def _save_model(self, model: Any) -> None:
        import joblib

        def save_model(path):
            with open(str(path / "UMAP.joblib"), "wb") as f:
                joblib.dump(model, f)

        self.save_artifact(
            name="UMAP_model",
            write_function=lambda path: save_model(path),
            metadata={
                "n_components": self.n_components,
                "metric": self.metric,
            },
        )

    def process(self, inputs: StepInput) -> "StepOutput":  # type: ignore
        # Shape of the embeddings is (n_samples, n_features)
        embeddings = np.array([input["embedding"] for input in inputs])

        self._logger.info("🏋️‍♀️ Start UMAP training...")
        mapper = self._umap.fit(embeddings)
        # Shape of the projection will be (n_samples, n_components)
        for input, projection in zip(inputs, mapper.embedding_):
            input["projection"] = projection

        self._save_model(mapper)
        yield inputs
