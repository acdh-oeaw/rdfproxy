"""Type definitions for rdfproxy."""

from typing import Annotated, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel


_TModelInstance: Annotated[TypeVar, "Type defintion for Pydantic model instances."] = (
    TypeVar("_TModelInstance", bound=BaseModel)
)


@runtime_checkable
class _TModelConstructorCallable[ModelType: BaseModel](Protocol):
    """Callback protocol for model constructor callables."""

    def __call__(self, **kwargs) -> ModelType: ...
