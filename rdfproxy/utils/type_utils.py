"""RDFProxy typing utils."""

import types
import typing
from typing import Annotated, Any, TypeGuard, get_args, get_origin

from pydantic import BaseModel
from rdfproxy.utils._types import _TSPARQLBoundField


def _is_list_static_type(obj: Any) -> TypeGuard[type[list]]:
    """Check if object is a list type."""
    return (obj is list) or (get_origin(obj) is list)


def _is_pydantic_model_static_type(obj: Any) -> TypeGuard[type[BaseModel]]:
    """Check if object is a Pydantic model type."""
    return (
        isinstance(obj, type) and issubclass(obj, BaseModel) and (obj is not BaseModel)
    )


def _is_list_pydantic_model_static_type(
    obj: Any,
) -> TypeGuard[type[list[type[BaseModel]]]]:
    """Check if an object is a list of Pydantic models type."""
    return _is_list_static_type(obj) and all(
        _is_pydantic_model_static_type(t) for t in get_args(obj)
    )


def _is_pydantic_model_union_static_type(
    obj: Any,
) -> TypeGuard[types.UnionType]:
    """Check if object is a union type of a Pydantic model."""
    is_union_type: bool = get_origin(obj) in (types.UnionType, typing.Union)
    has_any_model: bool = any(
        _is_pydantic_model_static_type(obj) for obj in get_args(obj)
    )

    return is_union_type and has_any_model


def _is_sparql_bound_field_type(
    value: type | None,
) -> TypeGuard[_TSPARQLBoundField]:
    """Check if an object is a SPARQL-bound type.

    A SPARQL-bound type is either a subtype of _TSPARQLBoundField
    or a union type of subtypes of _TSPARQLBoundField or None.
    """
    origin: type | None = get_origin(value)
    args: tuple = get_args(value)

    match origin, args, value:
        case *_, None:
            return True
        case types.UnionType | typing.Union, args, _:
            return all(_is_sparql_bound_field_type(arg) for arg in args)
        case None, (), value:
            if not isinstance(value, type):
                msg = f"Expected type | None for value argument. Got '{value}'."
                raise ValueError(msg)

            assert value is not None  # type narrow
            return issubclass(value, _TSPARQLBoundField)
        case _ if origin is Annotated:
            value, *_ = args
            return _is_sparql_bound_field_type(value)
        case _:
            return False
