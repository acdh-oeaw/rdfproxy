"""Pytest entry point for mapper tests with inconsistent grouping.

Currently, the tests contain only two cases: A case from the original
mapper tests that happens to fail the check and the example from issue #243.
"""

from pydantic import BaseModel
import pytest
from rdfproxy import ConfigDict
from rdfproxy.mapper import _ModelBindingsMapper
from rdfproxy.utils.exceptions import InconsistentGroupingException
from tests.tests_mapper.params.models.nested_grouping_model import (
    NestedGroupingComplexModel,
)
from tests.utils._types import ModelBindingsMapperParameter


class Model(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int
    y: int
    z: list[int]


inconsistent_grouping_params = [
    ModelBindingsMapperParameter(
        model=NestedGroupingComplexModel,
        bindings=[
            {"x": 1, "y": 2, "a": "a value 1", "p": "p value 1"},
            {"x": 1, "y": 2, "a": "a value 2", "p": "p value 2"},
            {"x": 1, "y": 3, "a": "a value 3", "p": "p value 3"},
            {"x": 2, "y": 2, "a": "a value 1", "p": "p value 4"},
        ],
        expected=[],
    ),
    ModelBindingsMapperParameter(
        model=Model,
        bindings=[
            {"x": 1, "y": 2, "z": 2},
            {"x": 1, "y": 3, "z": 3},
            {"x": 2, "y": 4, "z": 4},
        ],
        expected=[],
    ),
]


@pytest.mark.parametrize("params", inconsistent_grouping_params)
def test_model_bindings_mapper_raise_on_inconsistent_group(params):
    with pytest.raises(InconsistentGroupingException):
        mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
        mapper.get_models()


@pytest.mark.parametrize("params", inconsistent_grouping_params)
def test_model_bindings_mapper_warn_on_inconsistent_group(params):
    class WarnModel(params.model):
        model_config = ConfigDict(
            **params.model.model_config, enforce_grouping_consistency=False
        )

    with pytest.warns(UserWarning):
        mapper = _ModelBindingsMapper(model=WarnModel, bindings=params.bindings)
        mapper.get_models()
