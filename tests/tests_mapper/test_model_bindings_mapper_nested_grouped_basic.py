"""Pytest entrypoint for basic nested grouped model tests with ungrouped and grouped root model.

Note: The 'a' field in nested models is typed int | None; the union is only necessary for None grouping tests.
"""

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

bindings_none_group = [
    {"x": 1, "a": None, "b": 5},
    {"x": 2, "a": None, "b": 6},
    {"x": 3, "a": 3, "b": 7},
    {"x": 3, "a": 3, "b": 8},
]


class Nested(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int | None
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

    a: int | None = Field(exclude=True)
    b: list[int]


class Nested2(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int | None
    deeply_nested: DeeplyNested


class GroupedRootModel2(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int
    nested: list[Nested2]


class UngroupedRootModel2(BaseModel):
    x: int
    nested: Nested2


class DeeplyNested3(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int | None = Field(exclude=True)
    b: list[int]


class Nested3(BaseModel):
    a: int | None
    deeply_nested: DeeplyNested3


class UngroupedRootModel3(BaseModel):
    x: int
    nested: Nested3


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
    ModelBindingsMapperParameter(
        model=UngroupedRootModel3,
        bindings=bindings,
        expected=[
            {"x": 1, "nested": {"a": 2, "deeply_nested": {"b": [5, 6]}}},
            {"x": 2, "nested": {"a": 2, "deeply_nested": {"b": [5, 6]}}},
            {"x": 3, "nested": {"a": 3, "deeply_nested": {"b": [7, 8]}}},
            {"x": 3, "nested": {"a": 3, "deeply_nested": {"b": [7, 8]}}},
        ],
    ),
    # None group
    ModelBindingsMapperParameter(
        model=UngroupedRootModel,
        bindings=bindings_none_group,
        expected=[
            {"x": 1, "nested": {"a": None, "b": [5, 6]}},
            {"x": 2, "nested": {"a": None, "b": [5, 6]}},
            {"x": 3, "nested": {"a": 3, "b": [7, 8]}},
            {"x": 3, "nested": {"a": 3, "b": [7, 8]}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=GroupedRootModel,
        bindings=bindings_none_group,
        expected=[
            {"x": 1, "nested": [{"a": None, "b": [5]}]},
            {"x": 2, "nested": [{"a": None, "b": [6]}]},
            {"x": 3, "nested": [{"a": 3, "b": [7, 8]}]},
        ],
    ),
    ModelBindingsMapperParameter(
        model=UngroupedRootModel2,
        bindings=bindings_none_group,
        expected=[
            {"x": 1, "nested": {"a": None, "deeply_nested": {"b": [5, 6]}}},
            {"x": 2, "nested": {"a": None, "deeply_nested": {"b": [5, 6]}}},
            {"x": 3, "nested": {"a": 3, "deeply_nested": {"b": [7, 8]}}},
            {"x": 3, "nested": {"a": 3, "deeply_nested": {"b": [7, 8]}}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=GroupedRootModel2,
        bindings=bindings_none_group,
        expected=[
            {"x": 1, "nested": [{"a": None, "deeply_nested": {"b": [5]}}]},
            {"x": 2, "nested": [{"a": None, "deeply_nested": {"b": [6]}}]},
            {"x": 3, "nested": [{"a": 3, "deeply_nested": {"b": [7, 8]}}]},
        ],
    ),
    ModelBindingsMapperParameter(
        model=UngroupedRootModel3,
        bindings=bindings_none_group,
        expected=[
            {"x": 1, "nested": {"a": None, "deeply_nested": {"b": [5, 6]}}},
            {"x": 2, "nested": {"a": None, "deeply_nested": {"b": [5, 6]}}},
            {"x": 3, "nested": {"a": 3, "deeply_nested": {"b": [7, 8]}}},
            {"x": 3, "nested": {"a": 3, "deeply_nested": {"b": [7, 8]}}},
        ],
    ),
]


@pytest.mark.parametrize("params", params)
def test_ungrouped_grouped_nested_grouped_basic(params):
    mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
    result: list[dict] = [model.model_dump() for model in mapper.get_models()]

    assert result == params.expected
