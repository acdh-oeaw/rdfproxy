"""SPARQL/FastAPI utils."""

from collections import UserDict
from collections.abc import Callable
from functools import partial
from typing import TypeVar

from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils._types import SPARQLBinding


T = TypeVar("T")


class FieldsBindingsMap(UserDict):
    """Mapping for resolving SPARQLBinding aliases.

    Model field names are mapped to SPARQLBinding names.
    The FieldsBindingsMap.reverse allows reverse lookup
    (i.e. from SPARQLBindings to model fields).

    Note: It might be useful to recursively resolve aliases for nested models.
    """

    def __init__(self, model: type[_TModelInstance]) -> None:
        self.data = self._get_field_binding_mapping(model)
        self._reversed = {v: k for k, v in self.data.items()}

    @property
    def reverse(self) -> dict[str, str]:
        """Reverse lookup map from SPARQL bindings to model fields."""
        return self._reversed

    @staticmethod
    def _get_field_binding_mapping(model: type[_TModelInstance]) -> dict[str, str]:
        """Resolve model fields against rdfproxy.SPARQLBindings."""
        return {
            k: next(filter(lambda x: isinstance(x, SPARQLBinding), v.metadata), k)
            for k, v in model.model_fields.items()
        }


def compose_left(*fns: Callable[[T], T]) -> Callable[[T], T]:
    """Left associative compose."""

    def _left_wrapper(*fns):
        fn, *rest_fns = fns

        if rest_fns:
            return lambda *args, **kwargs: fn(_left_wrapper(*rest_fns)(*args, **kwargs))
        return fn

    return _left_wrapper(*reversed(fns))


class QueryConstructorComponent:
    """Query modification component factory.

    Components either call the wrapped function with non-None value kwargs applied
    or (if all kwargs values are None) fall back to the identity function.

    QueryConstructorComponents are used in QueryConstructor for query modification compose chains.
    """

    def __init__(self, f: Callable[..., str], **kwargs) -> None:
        self.f = f
        self.kwargs = kwargs

    def __call__(self, query) -> str:
        if tkwargs := {k: v for k, v in self.kwargs.items() if v is not None}:
            return partial(self.f, **tkwargs)(query)
        return query
