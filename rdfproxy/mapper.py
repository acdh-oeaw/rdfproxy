"""ModelBindingsMapper: Functionality for mapping binding maps to a Pydantic model."""

from collections.abc import Iterator
from typing import Any, Generic, get_args

from pydantic import BaseModel
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.utils import (
    _collect_values_from_bindings,
    _get_group_by,
    _get_key_from_metadata,
    _is_list_basemodel_type,
    _is_list_type,
)


class ModelBindingsMapper(Generic[_TModelInstance]):
    """Utility class for mapping flat bindings to a (potentially nested) Pydantic model."""

    def __init__(self, model: type[_TModelInstance], *bindings: dict):
        self.model = model
        self.bindings = bindings
        self._contexts = []

    def get_models(self) -> list[_TModelInstance]:
        """Generate a list of (potentially nested) Pydantic models based on (flat) bindings."""
        return self._get_unique_models(self.model, self.bindings)

    def _get_unique_models(self, model, bindings):
        """Call the mapping logic and collect unique and non-empty models."""
        models = []
        for _bindings in bindings:
            _model = model(**dict(self._generate_binding_pairs(model, **_bindings)))

            if any(_model.model_dump().values()) and (_model not in models):
                models.append(_model)

        return models

    def _get_group_by(self, model, kwargs) -> str:
        """Get the group_by value from a model and register it in self._contexts."""
        group_by: str = _get_group_by(model, kwargs)

        if group_by not in self._contexts:
            self._contexts.append(group_by)

        return group_by

    def _generate_binding_pairs(
        self,
        model: type[BaseModel],
        **kwargs,
    ) -> Iterator[tuple[str, Any]]:
        """Generate an Iterator[tuple] projection of the bindings needed for model instantation."""
        for k, v in model.model_fields.items():
            if _is_list_basemodel_type(v.annotation):
                group_by: str = self._get_group_by(model, kwargs)
                group_model, *_ = get_args(v.annotation)

                applicable_bindings = filter(
                    lambda x: (x[group_by] == kwargs[group_by])
                    and (x[self._contexts[0]] == kwargs[self._contexts[0]]),
                    self.bindings,
                )

                value = self._get_unique_models(group_model, applicable_bindings)

            elif _is_list_type(v.annotation):
                group_by: str = self._get_group_by(model, kwargs)
                applicable_bindings = filter(
                    lambda x: x[group_by] == kwargs[group_by],
                    self.bindings,
                )

                binding_key: str = _get_key_from_metadata(v, default=k)
                value = _collect_values_from_bindings(binding_key, applicable_bindings)

            elif isinstance(v.annotation, type(BaseModel)):
                nested_model = v.annotation
                value = nested_model(
                    **dict(self._generate_binding_pairs(nested_model, **kwargs))
                )
            else:
                binding_key: str = _get_key_from_metadata(v, default=k)
                value = kwargs.get(binding_key, v.default)

            yield k, value
