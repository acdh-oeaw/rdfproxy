"""RDFProxy model utils."""

from collections.abc import Callable, Iterator
from typing import TypeVar, get_args

from pydantic import BaseModel
from rdfproxy.utils.type_utils import (
    _is_list_pydantic_model_static_type,
    _is_pydantic_model_static_type,
    _is_pydantic_model_union_static_type,
)


T = TypeVar("T")


def model_traverse(
    model: type[BaseModel],
    f: Callable[[type[BaseModel]], T],
    include_root_model: bool = True,
) -> Iterator[T]:
    """Recursively traverse a model and apply a callable to all applicable (sub)models.

    Submodels are applicable if they are significant according to RDFProxy semantics.

    If the include_root_model flag is set to True,
    the callable will be applied to the root model as well.
    Recursive calls intentionally do not pass on the include_root_model flag.

    Note that currently all models of a model union are traversed, although only
    the first model of a model union will be considered by the RDFProxy mapper.
    This behavior is evaluated and considered in #245.
    """
    if include_root_model:
        yield f(model)

    for _, field_info in model.model_fields.items():
        if _is_list_pydantic_model_static_type(list_model := field_info.annotation):
            nested_model, *_ = get_args(list_model)
            yield from model_traverse(nested_model, f)

        elif _is_pydantic_model_static_type(nested_model := field_info.annotation):
            yield from model_traverse(nested_model, f)

        elif _is_pydantic_model_union_static_type(union := field_info.annotation):
            for nested_model in filter(_is_pydantic_model_static_type, get_args(union)):
                yield from model_traverse(nested_model, f)

        else:
            continue
