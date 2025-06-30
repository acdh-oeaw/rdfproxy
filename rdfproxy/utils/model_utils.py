"""RDFProxy model utils."""

from collections.abc import Callable
from typing import Any, TypeAlias, get_args

from pydantic import BaseModel
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.type_utils import (
    _is_list_pydantic_model_static_type,
    _is_pydantic_model_static_type,
    _is_pydantic_model_union_static_type,
)
from rdfproxy.utils.utils import identity


_TModelHook: TypeAlias = Callable[[type[_TModelInstance]], Any]


class ModelVisitor:
    """Functional Visitor implementation for applying model hooks to a Pydantic model and its submodels.

    Within RDFProxy, ModelVisitor is currently used for running model checks;
    the class can be generally useful for applying side-effect callables to nested models though.

    Args:
        model: The root Pydantic model class to visit.
        top_model_hook: Callable hook to apply only to the top-level model.
        sub_models_hook: Callable hook to apply only to nested models.
        all_models_hook: Callable hook to apply to all models (top-level and nested).
    """

    def __init__(
        self,
        model: type[_TModelInstance],
        top_model_hook: _TModelHook = identity,
        sub_model_hook: _TModelHook = identity,
        all_model_hook: _TModelHook = identity,
    ) -> None:
        self._model = model

        self._top_model_checks = (top_model_hook, all_model_hook)
        self._sub_model_checks = (all_model_hook, sub_model_hook)

    def visit(self) -> type[BaseModel]:
        """Run the registered validation checks against the model."""
        return self._visit(self._model)

    @staticmethod
    def _run_checks(model: type[BaseModel], *checks: _TModelHook) -> None:
        for check in checks:
            check(model)

    def _visit(self, model: type[BaseModel], top_level: bool = True) -> type[BaseModel]:
        """Helper method for recursive model traversal.

        The method visits a given model and applies registered validation checks.
        """
        if top_level:
            self._run_checks(model, *self._top_model_checks)

        for _, field_info in model.model_fields.items():
            if _is_list_pydantic_model_static_type(list_model := field_info.annotation):
                nested_model, *_ = get_args(list_model)
                self._run_checks(nested_model, *self._sub_model_checks)
                self._visit(nested_model, top_level=False)

            elif _is_pydantic_model_static_type(nested_model := field_info.annotation):
                self._run_checks(nested_model, *self._sub_model_checks)
                self._visit(nested_model, top_level=False)

            # note: checks all models in a union, but only the first model is significant in RDFProxy
            elif _is_pydantic_model_union_static_type(union := field_info.annotation):
                for nested_model in filter(
                    _is_pydantic_model_static_type, get_args(union)
                ):
                    self._run_checks(nested_model, *self._sub_model_checks)
                    self._visit(nested_model, top_level=False)

            else:
                continue

        return model
