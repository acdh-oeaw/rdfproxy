"""SPARQL/FastAPI utils."""

from collections import UserDict
from collections.abc import Callable, Hashable, Iterator
from functools import partial
from typing import Annotated, Any, Generic, NoReturn, Self, TypeVar, get_args

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from rdfproxy.utils._types import SPARQLBinding, _TModelInstance
from rdfproxy.utils.type_utils import (
    _is_pydantic_model_static_type,
    _is_pydantic_model_union_static_type,
    _is_sparql_bound_field_type,
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


class ModelSPARQLMap(UserDict):
    """Mapping for resolving SPARQL-bound model fields against SPARQLBinding aliases.

    A SPARQL-bound type is either a subtype of _TSPARQLBoundField
    or a union type of subtypes of _TSPARQLBoundField or None.

    If recursve=True, model and model union typed fields are resolved recursively.
    For nested models, ModelSPARQLMap keys get namespaced.

    ModelSPARQLMap.reverse allows reverse lookup (i.e. from SPARQLBindings to model fields).
    """

    def __init__(self, model: type[_TModelInstance], recursive: bool = False) -> None:
        self.model = model
        self.recursive = recursive

        self.data = self._get_model_sparql_mapping()

    @property
    def reverse(self) -> dict[str, str]:
        """Reverse lookup map from SPARQL bindings to model fields."""
        reverse = {v: k for k, v in self.data.items()}
        return reverse

    def __missing__(self, key: Hashable) -> NoReturn:
        sparql_bound_fields = [f"'{k}'" for k in self.data.keys()]
        model_name = self.model.__name__

        raise ValueError(
            f"Parameter '{key}' does not reference a SPARQL-bound field of model '{model_name}'.\n"
            f"Applicable values: {', '.join(sparql_bound_fields) if sparql_bound_fields else 'none'}."
        )

    # this is also used in FieldsBindingsMap
    @staticmethod
    def _get_sparql_bound_field_value(field_name: str, field_info: FieldInfo) -> str:
        """Resolve the SPARQL binding name given model field information.

        Empty SPARQLBinding objects are supported for additional/future semantics and fall back to the field_name.
        """
        _field_metadata = filter(
            lambda x: isinstance(x, SPARQLBinding) and x,
            field_info.metadata,
        )

        return next(_field_metadata, field_name)

    def _construct_mapping(
        self, model: type[BaseModel], top_level: bool = True
    ) -> Iterator[tuple[str, str]]:
        """Recursive generator for Model-SPARQL mapping construction.

        The iterator traverses model fields to determine and yield SPARQL-bound fields;
        if recursve=True, model and model union typed fields are resolved recursively.
        """

        fields_map: Annotated[
            Iterator[tuple[str, FieldInfo]],
            """Pydantic model_fields items data with default value fields filtered out.

            Model union types are excluded from default value filtering to allow for recursion.
            """,
        ] = (
            (field_name, field_info)
            for field_name, field_info in model.model_fields.items()
            if field_info.is_required()
            or _is_pydantic_model_union_static_type(field_info.annotation)
        )

        for field_name, field_info in fields_map:
            if self.recursive and _is_pydantic_model_union_static_type(
                model_union := field_info.annotation
            ):
                union_model: type[BaseModel] = next(
                    filter(
                        _is_pydantic_model_static_type,
                        get_args(model_union),
                    )
                )
                yield from self._construct_mapping(model=union_model, top_level=False)

            elif self.recursive and _is_pydantic_model_static_type(
                nested_model := field_info.annotation
            ):
                yield from self._construct_mapping(model=nested_model, top_level=False)

            elif _is_sparql_bound_field_type(field_info.annotation):
                yield (
                    field_name if top_level else f"{model.__name__}.{field_name}",
                    self._get_sparql_bound_field_value(field_name, field_info),
                )
            else:
                continue

    def _get_model_sparql_mapping(self) -> dict[str, str]:
        """Construct a Model-SPARQL mapping given a model."""
        return dict(self._construct_mapping(model=self.model))


def compose_left(*fns: Callable) -> Callable:
    """Left associative compose."""

    def _left_wrapper(*fns):
        fn, *rest_fns = fns

        if rest_fns:
            return lambda *args, **kwargs: fn(_left_wrapper(*rest_fns)(*args, **kwargs))
        return fn

    return _left_wrapper(*reversed(fns))


def identity(arg):
    """Identity function."""
    return arg


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
