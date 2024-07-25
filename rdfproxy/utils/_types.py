"""Type definitions for rdfproxy."""

from collections.abc import Iterable
from typing import Annotated, Protocol, TypeVar, runtime_checkable

from SPARQLWrapper import QueryResult
from pydantic import BaseModel


_TModelInstance = TypeVar("_TModelInstance", bound=BaseModel)


@runtime_checkable
class _TModelConstructorCallable[ModelType: BaseModel](Protocol):
    """Callback protocol for model constructor callables."""

    def __call__(self, query_result: QueryResult) -> Iterable[ModelType]: ...
