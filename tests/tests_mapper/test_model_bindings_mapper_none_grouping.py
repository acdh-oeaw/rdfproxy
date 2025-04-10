"""Pytest entry point for _ModelBindingsMapper tests for grouping by None-valued fields."""

from pydantic import BaseModel
import pytest
from rdfproxy import ConfigDict
from rdfproxy.mapper import _ModelBindingsMapper
from tests.utils._types import ModelBindingsMapperParameter


class DeeplyNested(BaseModel):
    z: int | None


class Nested(BaseModel):
    model_config = ConfigDict(group_by="y")

    y: int | None
    deeply_nested: list[DeeplyNested]


class Model(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int | None
    nested: list[Nested]


params = [
    ## failed with []
    ModelBindingsMapperParameter(
        model=Model,
        bindings=[{"x": None, "y": None, "z": None}],
        expected=[{"x": None, "nested": []}],
    ),
    ModelBindingsMapperParameter(
        model=Model,
        bindings=[{"x": None, "y": 2, "z": None}],
        expected=[{"x": None, "nested": [{"y": 2, "deeply_nested": []}]}],
    ),
    ModelBindingsMapperParameter(
        model=Model,
        bindings=[{"x": None, "y": None, "z": 3}],
        expected=[{"x": None, "nested": [{"y": None, "deeply_nested": [{"z": 3}]}]}],
    ),
    ## failed with AssertionError
    ModelBindingsMapperParameter(
        model=Model,
        bindings=[{"x": 1, "y": None, "z": None}],
        expected=[{"x": 1, "nested": []}],
    ),
    ## also passed before bug fix, but still test-worthy
    ModelBindingsMapperParameter(
        model=Model,
        bindings=[{"x": 1, "y": 2, "z": None}],
        expected=[{"x": 1, "nested": [{"y": 2, "deeply_nested": []}]}],
    ),
    ModelBindingsMapperParameter(
        model=Model,
        bindings=[{"x": 1, "y": 2, "z": 3}],
        expected=[{"x": 1, "nested": [{"y": 2, "deeply_nested": [{"z": 3}]}]}],
    ),
]


@pytest.mark.parametrize(["model", "bindings", "expected"], params)
def test_model_bindings_mapper_none_grouping(model, bindings, expected):
    mapper = _ModelBindingsMapper(model=model, bindings=bindings)
    models = mapper.get_models()
    assert [model.model_dump() for model in models] == expected
