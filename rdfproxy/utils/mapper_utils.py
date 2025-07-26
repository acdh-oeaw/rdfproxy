from pydantic import BaseModel
from rdfproxy.utils._types import ModelBoolPredicate, _TModelBoolValue


def default_model_bool_predicate(model: BaseModel) -> bool:
    """Default predicate for determining model truthiness.

    Adheres to rdfproxy.utils._types.ModelBoolPredicate.
    """
    return any(dict(model).values())


def _get_model_bool_predicate_from_config_value(
    model_bool_value: _TModelBoolValue,
) -> ModelBoolPredicate:
    """Get a model_bool predicate function given the value of the model_bool config setting."""
    match model_bool_value:
        case ModelBoolPredicate():
            return model_bool_value
        case str():
            return lambda model: bool(dict(model)[model_bool_value])
        case set():
            return lambda model: all(map(lambda k: dict(model)[k], model_bool_value))
        case _:  # pragma: no cover
            assert False, "This should never happen."


def get_model_bool_predicate(model: type[BaseModel] | BaseModel) -> ModelBoolPredicate:
    """Get the applicable model_bool predicate function given a model."""
    if (model_bool_value := model.model_config.get("model_bool", None)) is None:
        model_bool_predicate = default_model_bool_predicate
    else:
        model_bool_predicate = _get_model_bool_predicate_from_config_value(
            model_bool_value
        )

    return model_bool_predicate
