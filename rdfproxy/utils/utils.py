"""SPARQL/FastAPI utils."""

from collections import UserDict
from collections import deque
from collections.abc import Callable, Hashable
from functools import partial
from itertools import islice
from typing import Any, Generic, NoReturn, Self, TypeVar

from rdfproxy.utils._types import SPARQLBinding, _TModelInstance
from rdfproxy.utils.type_utils import (
    _is_list_static_type,
    _is_pydantic_model_static_type,
)


T = TypeVar("T")


class FieldsBindingsMap(UserDict):
    """Mapping for resolving SPARQLBinding aliases.

    Model field names are mapped to SPARQLBinding names.
    The FieldsBindingsMap.reverse allows reverse lookup
    (i.e. from SPARQLBindings to model fields).

    Note: It might be useful to recursively resolve aliases for nested models.
    This would allow to e.g. just use a single FieldsBindingsMap instance in rdfproxy.mapper.
    Introduction of a type_utils union predicate ("_is_any_pydantic_model_static_type")
    could be an applicable approach for recursively resolving aliases.
    """

    def __init__(self, model: type[_TModelInstance]) -> None:
        self.model = model
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


class OrderableFieldsBindingsMap(FieldsBindingsMap):
    """Recursive FieldsBindingsMap that generates namespaced key entries for orderable fields."""

    def __missing__(self, key: Hashable) -> NoReturn:
        orderable_fields = [f"'{k}'" for k in self.data.keys()]
        model_name = self.model.__name__

        raise ValueError(
            f"Parameter '{key}' does not reference an orderable field of model '{model_name}'.\n"
            f"Applicable values for order_by: {', '.join(orderable_fields)}."
        )

    @staticmethod
    def _get_field_binding_mapping(model: type[_TModelInstance]) -> dict[str, str]:
        """Resolve model fields against rdfproxy.SPARQLBindings."""

        def _construct_bindings(model, top_level=True):
            bindings_map = FieldsBindingsMap(model)

            for k, v in model.model_fields.items():
                # note: check for union model type might be required in the future
                if _is_pydantic_model_static_type(v.annotation):
                    yield from _construct_bindings(v.annotation, top_level=False)

                elif not _is_list_static_type(v.annotation):
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


def consume(iterator, n=None):
    """Advance the iterator n-steps ahead. If n is None, consume entirely.

    Note: This function is from the Itertools Recipe section, see:
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    # Use functions that consume iterators at C speed.
    if n is None:
        deque(iterator, maxlen=0)
    else:  # pragma: no cover
        next(islice(iterator, n, n), None)
