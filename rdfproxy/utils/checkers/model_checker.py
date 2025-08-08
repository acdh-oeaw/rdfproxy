"""Functionality for performing RDFProxy-compliance checks on Pydantic models."""

from pydantic import BaseModel
from rdfproxy.utils.checkers._model_checks import (
    _check_enforce_grouping_consistency_config,
    _check_group_by_config,
    _check_model_bool_config_root_model,
    _check_model_bool_config_sub_models,
    _check_model_union_types,
)
from rdfproxy.utils.model_utils import ModelVisitor
from rdfproxy.utils.utils import compose_left


def check_model(model: type[BaseModel]) -> type[BaseModel]:
    """Main model checker: Run model checks using the appropriate check runners."""

    visitor = ModelVisitor(
        model=model,
        top_model_hook=_check_model_bool_config_root_model,
        sub_model_hook=_check_model_bool_config_sub_models,
        all_model_hook=compose_left(
            _check_group_by_config,
            _check_model_union_types,
            _check_enforce_grouping_consistency_config,
        ),
    )

    return visitor.visit()
