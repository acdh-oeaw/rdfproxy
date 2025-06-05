"""Checker definitions for SPARQLModelAdapter.get_item."""

from typing import Any

from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.exceptions import (
    MultipleResultsFound,
    NoResultsFound,
    UnprojectedKeyBindingException,
)
from rdfproxy.utils.sparql_utils import get_query_projection
from rdfproxy.utils.utils import FieldsBindingsMap


def check_key(
    key: dict[str, Any], query: str, model: type[_TModelInstance]
) -> dict[str, Any]:
    """Check a given model ID key.

    The key must be a single kwarg that denotes a model field
    as well as a corresponding SPARQL binding (when de-aliased).
    """

    if len(key) != 1:
        raise ValueError(f"Expected exactly 1 keyword argument. Got {key}.")

    bindings_map = FieldsBindingsMap(model)
    query_projection = [str(var) for var in get_query_projection(query)]

    (k, _), *_ = key.items()

    if (binding := bindings_map[k]) not in query_projection:
        raise UnprojectedKeyBindingException(
            f"SPARQL binding '{binding}' for model field '{model.__name__}.{k}' not in query projection."
        )

    return key


def check_item_model(
    models: list[_TModelInstance],
    model_type: type[_TModelInstance],
    key: dict[str, Any],
) -> _TModelInstance:
    """Check the _ModelBindingsMapper result for single model retrieval."""
    match models:
        case [_model]:
            return _model
        case [_, *_]:
            raise MultipleResultsFound(
                f"Multiple results were returned for SPARQLModelAdapter[{model_type.__name__}].get_item with key {key}."
            )
        case []:
            raise NoResultsFound(
                f"No results were returned for SPARQLModelAdapter[{model_type.__name__}].get_item with key {key}."
            )
        case _:  # pragma: no cover
            assert False, "This should never happen."
