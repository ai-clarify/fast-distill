# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Union

from pydantic import BaseModel, ConfigDict, PrivateAttr

from fastdistill.mixins.runtime_parameters import RuntimeParametersMixin
from fastdistill.utils.serialization import _Serializable

if TYPE_CHECKING:
    from logging import Logger


class Embeddings(RuntimeParametersMixin, BaseModel, _Serializable, ABC):
    """Base class for `Embeddings` models.

    To implement an `Embeddings` subclass, you need to subclass this class and implement:
        - `load` method to load the `Embeddings` model. Don't forget to call `super().load()`,
            so the `_logger` attribute is initialized.
        - `model_name` property to return the model name used for the `Embeddings`.
        - `encode` method to generate the sentence embeddings.

    Attributes:
        _logger: the logger to be used for the `Embeddings` model. It will be initialized
            when the `load` method is called.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        protected_namespaces=(),
        validate_default=True,
        validate_assignment=True,
        extra="forbid",
    )
    _logger: "Logger" = PrivateAttr(None)

    def load(self) -> None:
        """Method to be called to initialize the `Embeddings`"""
        self._logger = logging.getLogger(
            f"fastdistill.models.embeddings.{self.model_name}"
        )

    def unload(self) -> None:
        """Method to be called to unload the `Embeddings` and release any resources."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the model name used for the `Embeddings`."""
        pass

    @abstractmethod
    def encode(self, inputs: List[str]) -> List[List[Union[int, float]]]:
        """Generates embeddings for the provided inputs.

        Args:
            inputs: a list of texts for which an embedding has to be generated.

        Returns:
            The generated embeddings.
        """
        pass
