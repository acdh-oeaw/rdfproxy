"""Types for testing."""

from typing import NamedTuple

from pydantic import BaseModel


class ModelBindingsMapperParameter(NamedTuple):
    """Parameter type for rdfproxy.ModelBindingsMapper tests."""

    model: type[BaseModel]
    bindings: list[dict]
    expected: list[dict]


class CountQueryParameter(NamedTuple):
    """Parameter type for rdfproxy.utils.sparql_utils.construct_count_query tests."""

    query: str
    model: type[BaseModel]
    expected: int
