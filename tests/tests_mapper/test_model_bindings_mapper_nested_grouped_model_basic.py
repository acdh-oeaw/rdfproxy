"""Pytest entrypoint for basic nested grouped model tests with ungrouped and grouped root model."""

from pydantic import BaseModel, Field
import pytest
from rdfproxy import ConfigDict
from rdfproxy.mapper import _ModelBindingsMapper
from tests.utils._types import ModelBindingsMapperParameter


bindings = [
    {"x": 1, "a": 2, "b": 5},
    {"x": 2, "a": 2, "b": 6},
    {"x": 3, "a": 3, "b": 7},
    {"x": 3, "a": 3, "b": 8},
]


class Nested(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int
    b: list[int]


class GroupedRootModel(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int
    nested: list[Nested]


class UngroupedRootModel(BaseModel):
    x: int
    nested: Nested


class DeeplyNested(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int = Field(exclude=True)
    b: list[int]


class Nested2(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int
    deeply_nested: DeeplyNested


class GroupedRootModel2(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int
    nested: list[Nested2]


class UngroupedRootModel2(BaseModel):
    x: int
    nested: Nested2


params = [
    ModelBindingsMapperParameter(
        model=UngroupedRootModel,
        bindings=bindings,
        expected=[
            {"x": 1, "nested": {"a": 2, "b": [5, 6]}},
            {"x": 2, "nested": {"a": 2, "b": [5, 6]}},
            {"x": 3, "nested": {"a": 3, "b": [7, 8]}},
            {"x": 3, "nested": {"a": 3, "b": [7, 8]}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=GroupedRootModel,
        bindings=bindings,
        expected=[
            {"x": 1, "nested": [{"a": 2, "b": [5]}]},
            {"x": 2, "nested": [{"a": 2, "b": [6]}]},
            {"x": 3, "nested": [{"a": 3, "b": [7, 8]}]},
        ],
    ),
    ModelBindingsMapperParameter(
        model=UngroupedRootModel2,
        bindings=bindings,
        expected=[
            {"x": 1, "nested": {"a": 2, "deeply_nested": {"b": [5, 6]}}},
            {"x": 2, "nested": {"a": 2, "deeply_nested": {"b": [5, 6]}}},
            {"x": 3, "nested": {"a": 3, "deeply_nested": {"b": [7, 8]}}},
            {"x": 3, "nested": {"a": 3, "deeply_nested": {"b": [7, 8]}}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=GroupedRootModel2,
        bindings=bindings,
        expected=[
            {"x": 1, "nested": [{"a": 2, "deeply_nested": {"b": [5]}}]},
            {"x": 2, "nested": [{"a": 2, "deeply_nested": {"b": [6]}}]},
            {"x": 3, "nested": [{"a": 3, "deeply_nested": {"b": [7, 8]}}]},
        ],
    ),
]


@pytest.mark.parametrize("params", params)
def test_ungrouped_grouped_nested_grouped_basic(params):
    mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
    result: list[dict] = [model.model_dump() for model in mapper.get_models()]

    assert result == params.expected
