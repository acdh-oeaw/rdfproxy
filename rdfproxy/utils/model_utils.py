"""RDFProxy model utils."""

from collections.abc import Callable, Iterator
from typing import TypeVar, get_args

from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils._typing import (
    _is_list_basemodel_type,
    _is_pydantic_model_class,
    _is_union_pydantic_model_type,
)


T = TypeVar("T")


def model_traverse(
    model: type[_TModelInstance],
    f: Callable[[type[_TModelInstance]], T],
    _self: bool = True,
) -> Iterator[T]:
    """Recursively traverse a model and apply a callable to all (sub)models.

    If the _self flag is set to True, the callable will be applied to the root model model as well.
    Recursive calls intentionally do not pass on the _self flag.
    """
    if _self:
        yield f(model)

    for _, field_info in model.model_fields.items():
        if _is_list_basemodel_type(list_model := field_info.annotation):
            nested_model, *_ = get_args(list_model)
            yield from model_traverse(nested_model, f)

        elif _is_pydantic_model_class(nested_model := field_info.annotation):
            yield from model_traverse(nested_model, f)

        elif _is_union_pydantic_model_type(union := field_info.annotation):
            _model_filter = filter(_is_pydantic_model_class, get_args(union))
            nested_model = next(_model_filter)

            _multi_model_union = next(_model_filter, False)
            assert not _multi_model_union, "Multiple model unions are not supported."

            yield from model_traverse(nested_model, f)

        else:
            continue
