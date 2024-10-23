"""Types for testing."""

from typing import NamedTuple

from pydantic import BaseModel


class InstantiateModelParameter(NamedTuple):
    """Parameter type for ModelBindingsMapper tests."""

    model: BaseModel
    bindings: list[dict]
    expected: list[dict]


class CountQueryParameter(NamedTuple):
    """Parameter type for construct_count_query tests."""

    query: str
    model: type[BaseModel]
    grouped_model: type[BaseModel]
