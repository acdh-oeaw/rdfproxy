"""Compliance checks for RDFProxy Pydantic models."""

from rdfproxy.utils._exceptions import (
    RDFProxyGroupByException,
    RDFProxyModelBoolException,
)
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.type_utils import _is_list_static_type


def _check_group_by_config(model: type[_TModelInstance]) -> type[_TModelInstance]:
    """Model check for group_by config settings and grouping model semantics."""

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


def _check_model_bool_config_sub_models(
    model: type[_TModelInstance],
) -> type[_TModelInstance]:
    """Model check for model_bool config settings in submodels.

    Stub for now.
    This check could run against all keys in OrderableFieldsBindingsMap -
    which should be the fields applicable for model_bool checking.

    Invalid model_bool values currently fail in the mapper (e.g. with KeyError),
    so a check might not actually be needed.
    """
    return model


def _check_model_bool_config_root_model(
    model: type[_TModelInstance],
) -> type[_TModelInstance]:
    """Model check for disallowing model_bool in root models."""

    if model.model_config.get("model_bool") is not None:
        raise RDFProxyModelBoolException(
            "Setting model_bool in root models is not supported. "
            "model_bool semantics of root models should be controlled "
            "explicitely with SPARQL query result sets.\n"
            "See #176 (https://github.com/acdh-oeaw/rdfproxy/issues/176)."
        )

    return model
