"""RDFProxy typing utils."""

import types
import typing
from typing import Any, TypeGuard, get_args, get_origin

from pydantic import BaseModel


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


def _is_union_pydantic_model_static_type(
    obj: Any,
) -> bool:
    """Check if object is a union type of a Pydantic model."""
    is_union_type: bool = get_origin(obj) in (types.UnionType, typing.Union)
    has_any_model: bool = any(
        _is_pydantic_model_static_type(obj) for obj in get_args(obj)
    )

    return is_union_type and has_any_model
