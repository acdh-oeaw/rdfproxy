"""Functionality for performing RDFProxy-compliance checks on Pydantic models."""

from collections.abc import Callable

from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.checkers._model_checks import (
    _check_group_by_config,
    _check_model_bool_config_root_model,
    _check_model_bool_config_sub_models,
)
from rdfproxy.utils.model_utils import model_traverse
from rdfproxy.utils.utils import compose_left, consume


_TModelCheck = Callable[[type[_TModelInstance]], type[_TModelInstance]]


def _root_model_check_runner(
    model: type[_TModelInstance], *checks: _TModelCheck
) -> None:
    """Run checks only against the root model."""

    compose_left(*checks)(model)


def _sub_model_check_runner(
    model: type[_TModelInstance], *checks: _TModelCheck
) -> None:
    """Run checks recursively; exclude the root model."""

    composite = compose_left(*checks)
    consume(
        model_traverse(model, composite, include_root_model=False)
    )  # exhaust for traversal


def _full_model_check_runner(
    model: type[_TModelInstance], *checks: _TModelCheck
) -> None:
    """Run checks recursively; include the root model."""

    composite = compose_left(*checks)
    consume(model_traverse(model, composite))  # exhaust for traversal


def check_model(model: type[_TModelInstance]) -> type[_TModelInstance]:
    """Main model checker: Run model checks using the appropriate check runners."""

    _root_model_check_runner(model, _check_model_bool_config_root_model)
    _sub_model_check_runner(model, _check_model_bool_config_sub_models)
    _full_model_check_runner(model, _check_group_by_config)

    return model
