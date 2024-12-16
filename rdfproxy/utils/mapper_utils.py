from collections.abc import Callable, Iterable
from typing import Any, TypeGuard, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from rdfproxy.utils._exceptions import (
    InvalidGroupingKeyException,
    MissingModelConfigException,
)
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils._types import ModelBoolPredicate, SPARQLBinding, _TModelBoolValue


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


def _get_applicable_grouping_keys(model: type[_TModelInstance]) -> list[str]:
    return [k for k, v in model.model_fields.items() if not _is_list_type(v.annotation)]


def _get_group_by(model: type[_TModelInstance]) -> str:
    """Get the name of a grouping key from a model Config class."""
    try:
        group_by = model.model_config["group_by"]  # type: ignore
    except KeyError as e:
        raise MissingModelConfigException(
            "Model config with 'group_by' value required "
            "for field-based grouping behavior."
        ) from e
    else:
        applicable_keys = _get_applicable_grouping_keys(model=model)

        if group_by not in applicable_keys:
            raise InvalidGroupingKeyException(
                f"Invalid grouping key '{group_by}'. "
                f"Applicable grouping keys: {', '.join(applicable_keys)}."
            )

        if meta := model.model_fields[group_by].metadata:
            if binding := next(
                filter(lambda entry: isinstance(entry, SPARQLBinding), meta), None
            ):
                return binding
        return group_by


def default_model_bool_predicate(model: BaseModel) -> bool:
    """Default predicate for determining model truthiness.

    Adheres to rdfproxy.utils._types.ModelBoolPredicate.
    """
    return any(dict(model).values())


def _is_iterable_of_str(iterable: Iterable) -> TypeGuard[Iterable[str]]:
    return (not isinstance(iterable, str)) and all(
        map(lambda i: isinstance(i, str), iterable)
    )


def _get_model_bool_predicate_from_config_value(
    model_bool_value: _TModelBoolValue,
) -> ModelBoolPredicate:
    """Get a model_bool predicate function given the value of the model_bool config setting."""
    match model_bool_value:
        case ModelBoolPredicate():
            return model_bool_value
        case str():
            return lambda model: bool(dict(model)[model_bool_value])
        case model_bool_value if _is_iterable_of_str(model_bool_value):
            return lambda model: all(map(lambda k: dict(model)[k], model_bool_value))
        case _:  # pragma: no cover
            raise TypeError(
                "Argument for 'model_bool' must be of type ModelBoolPredicate | str | Iterable[str].\n"
                f"Received {type(model_bool_value)}"
            )


def get_model_bool_predicate(model: BaseModel) -> ModelBoolPredicate:
    """Get the applicable model_bool predicate function given a model."""
    if (model_bool_value := model.model_config.get("model_bool", None)) is None:
        model_bool_predicate = default_model_bool_predicate
    else:
        model_bool_predicate = _get_model_bool_predicate_from_config_value(
            model_bool_value
        )

    return model_bool_predicate
