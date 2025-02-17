"""RDFProxy typing utils."""

import types
from typing import Any, TypeGuard, get_args, get_origin

from pydantic import BaseModel


def _is_type(obj: type | None, _type: type) -> bool:
    """Check if an obj is type _type or a GenericAlias with origin _type."""
    return (obj is _type) or (get_origin(obj) is _type)


def _is_list_type(obj: type | None) -> bool:
    """Check if obj is a list type."""
    return _is_type(obj, list)


def _is_list_basemodel_type(obj: type | None) -> bool:
    """Check if a type is list[pydantic.BaseModel]."""
    return (get_origin(obj) is list) and all(
        issubclass(cls, BaseModel) for cls in get_args(obj)
    )


def _is_pydantic_model_class(obj: Any) -> TypeGuard[type[BaseModel]]:
    """Predicate for checking if an object is a Pydantic model class."""
    return isinstance(obj, type) and issubclass(obj, BaseModel)


def _is_union_pydantic_model_type(obj: Any) -> bool:
    """Predicate for checking if a type is union type of a Pydantic model."""
    is_union_type: bool = get_origin(obj) is types.UnionType
    has_any_model: bool = any(_is_pydantic_model_class(obj) for obj in get_args(obj))

    return is_union_type and has_any_model
