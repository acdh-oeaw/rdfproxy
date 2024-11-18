"""SPARQL/FastAPI utils."""

from collections.abc import Callable, Iterable
from typing import Any, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from rdfproxy.utils._exceptions import (
    MissingModelConfigException,
    UnboundGroupingKeyException,
)
from rdfproxy.utils._types import SPARQLBinding


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


def _collect_values_from_bindings(
    binding_name: str,
    bindings: Iterable[dict],
    predicate: Callable[[Any], bool] = lambda x: x is not None,
) -> list:
    """Scan bindings for a key binding_name and collect unique predicate-compliant values.

    Note that element order is important for testing, so a set cast won't do.
    """
    values = dict.fromkeys(
        value
        for binding in bindings
        if predicate(value := binding.get(binding_name, None))
    )
    return list(values)


def _get_key_from_metadata(v: FieldInfo, *, default: Any) -> str | Any:
    """Try to get a SPARQLBinding object from a field's metadata attribute.

    Helper for _generate_binding_pairs.
    """
    return next(filter(lambda x: isinstance(x, SPARQLBinding), v.metadata), default)


def _get_group_by(model: type[BaseModel], kwargs: dict) -> str:
    """Get the name of a grouping key from a model Config class."""
    try:
        group_by = model.model_config["group_by"]  # type: ignore
    except KeyError as e:
        raise MissingModelConfigException(
            "Model config with 'group_by' value required "
            "for field-based grouping behavior."
        ) from e
    else:
        if group_by not in kwargs.keys():
            raise UnboundGroupingKeyException(
                f"Requested grouping key '{group_by}' not in SPARQL binding projection.\n"
                f"Applicable grouping keys: {', '.join(kwargs.keys())}."
            )
        return group_by


def _get_model_valid_fn(model: BaseModel) -> Callable:
    match model.model_config.get("model_bool", None):
        case str() as str_obj:
            return lambda model: bool(dict(model)[str_obj])
        case model_bool_value if isinstance(model_bool_value, Iterable) and all(
            isinstance(item, str) for item in model_bool_value
        ):
            return lambda model: all(map(lambda k: dict(model)[k], model_bool_value))
        case func if callable(func):
            return func
        case None:
            return lambda model: any(dict(model).values())
        case _:
            raise TypeError(
                "Argument for 'model_bool' must be of type Callable | str | Iterable[str].\n"
                f"Received {type(model_bool_value)}"
            )
