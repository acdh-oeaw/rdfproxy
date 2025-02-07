"""SPARQL/FastAPI utils."""

from collections import UserDict
from collections.abc import Callable
from functools import partial
from typing import Any, Generic, Self, TypeVar

from pydantic import BaseModel
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils._types import SPARQLBinding
from rdfproxy.utils.mapper_utils import _is_scalar_type


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


class NamespacedFieldBindingsMap(FieldsBindingsMap):
    """Recursive FieldBindingsMap that generates namespaced key entries."""

    @staticmethod
    def _get_field_binding_mapping(model: type[_TModelInstance]) -> dict[str, str]:
        """Resolve model fields against rdfproxy.SPARQLBindings."""

        def _construct_bindings(model, top_level=True):
            bindings_map = FieldsBindingsMap(model)

            for k, v in model.model_fields.items():
                if isinstance(v.annotation, type(BaseModel)):
                    yield from _construct_bindings(v.annotation, top_level=False)

                if _is_scalar_type(v.annotation):
                    yield (k if top_level else f"{model.__name__}.{k}", bindings_map[k])

        return dict(_construct_bindings(model))


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


class CurryModel(Generic[_TModelInstance]):
    """Constructor for currying a Pydantic Model.

    A CurryModel instance can be called with kwargs which are run against
    the respective model field validators and kept in a kwargs cache.
    Once the model can be instantiated, calling a CurryModel object will
    instantiate the Pydantic model and return the model instance.

    If the eager flag is True (default), model field default values are
    added to the cache automatically, which means that models can be instantiated
    as soon possible, i.e. as soon as all /required/ field values are provided.
    """

    def __init__(self, model: type[_TModelInstance], eager: bool = True) -> None:
        self.model = model
        self.eager = eager

        self._kwargs_cache: dict = (
            {k: v.default for k, v in model.model_fields.items() if not v.is_required()}
            if eager
            else {}
        )

    def __repr__(self):  # pragma: no cover
        return f"CurryModel object {self._kwargs_cache}"

    @staticmethod
    def _validate_field(model: type[_TModelInstance], field: str, value: Any) -> Any:
        """Validate value for a single field given a model.

        Note: Using a TypeVar for value is not possible here,
        because Pydantic might coerce values (if not not in Strict Mode).
        """
        result = model.__pydantic_validator__.validate_assignment(
            model.model_construct(), field, value
        )
        return result

    def __call__(self, **kwargs: Any) -> Self | _TModelInstance:
        for k, v in kwargs.items():
            self._validate_field(self.model, k, v)

        self._kwargs_cache.update(kwargs)

        if self.model.model_fields.keys() == self._kwargs_cache.keys():
            return self.model(**self._kwargs_cache)
        return self
