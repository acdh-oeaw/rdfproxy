from collections.abc import Iterable
from typing import TypeGuard

from pydantic import BaseModel
from rdfproxy.utils._types import ModelBoolPredicate, _TModelBoolValue


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
