"""Functionality for performing RDFProxy-compliance checks on Pydantic models."""

from rdfproxy.utils._exceptions import RDFProxyGroupByException
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.model_utils import model_traverse
from rdfproxy.utils.type_utils import _is_list_static_type
from rdfproxy.utils.utils import compose_left


def _check_group_by_config(model: type[_TModelInstance]) -> type[_TModelInstance]:
    """Model checker for group_by config settings and grouping model semantics."""
    model_group_by_value: str | None = model.model_config.get("group_by")
    model_has_list_field: bool = any(
        _is_list_static_type(value.annotation) for value in model.model_fields.values()
    )

    match model_group_by_value, model_has_list_field:
        case None, False:
            return model

        case None, True:
            raise RDFProxyGroupByException(
                f"Model '{model.__name__}' has a list-annotated field "
                "but  does not specify 'group_by' in its model_config."
            )

        case str(), False:
            raise RDFProxyGroupByException(
                f"Model '{model.__name__}' does not specify "
                "a grouping target (i.e. a list-annotated field)."
            )

        case str(), True:
            applicable_keys: list[str] = [
                k
                for k, v in model.model_fields.items()
                if not _is_list_static_type(v.annotation)
            ]

            if model_group_by_value in applicable_keys:
                return model

            applicable_fields_message: str = (
                "No applicable fields."
                if not applicable_keys
                else f"Applicable grouping field(s): {', '.join(applicable_keys)}"
            )

            raise RDFProxyGroupByException(
                f"Requested grouping key '{model_group_by_value}' does not denote "
                f"an applicable grouping field. {applicable_fields_message}"
            )

        case _:  # pragma: no cover
            raise AssertionError("This should never happen.")


def _check_model_bool_config(model: type[_TModelInstance]) -> type[_TModelInstance]:
    """Model checker for model_bool config settings.

    This is a stub for now, the model_bool feature is in flux right now,
    see issues #176 and #219.
    """
    return model


def check_model(model: type[_TModelInstance]) -> type[_TModelInstance]:
    composite = compose_left(_check_group_by_config, _check_model_bool_config)
    _model, *_ = model_traverse(model, composite)  # exhaust iterator for full traversal

    return _model
