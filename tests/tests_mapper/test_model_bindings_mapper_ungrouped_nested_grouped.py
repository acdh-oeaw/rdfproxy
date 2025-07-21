"""Pytest entry point for running UNGROUPED nested grouped model tests."""

from pydantic import BaseModel
import pytest
from rdfproxy import ConfigDict
from rdfproxy.mapper import _ModelBindingsMapper
from tests.utils._types import ModelBindingsMapperParameter


class GroupedNested(BaseModel):
    model_config = ConfigDict(group_by="nested")

    nested: str
    nested_child_list: list[str]


class Model1(BaseModel):
    root: str
    nested: GroupedNested


class Model2(BaseModel):
    root: str
    nested: GroupedNested | None = None


class DeeplyNested(BaseModel):
    model_config = ConfigDict(group_by="c")

    c: int
    d: list[int]


class Nested3(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int
    b: list[int]

    deeply_nested: DeeplyNested | None = None


class Nested2(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int
    b: list[int]

    deeply_nested: list[DeeplyNested]


class Nested1(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int
    b: list[int]

    deeply_nested: DeeplyNested


class Model3(BaseModel):
    x: int
    nested: Nested1


class Model4(BaseModel):
    x: int
    nested: Nested2


class Model5(BaseModel):
    x: int
    nested: Nested3


class Model6(BaseModel):
    x: int
    nested: Nested3 | None = None


ungrouped_nested_grouped_params = [
    ModelBindingsMapperParameter(
        model=Model1,
        bindings=[
            {"root": "A", "nested": "AC1N", "nested_child_list": "AC1Na"},
            {"root": "B", "nested": "BC1N", "nested_child_list": "BC1Na"},
            {"root": "B", "nested": "BC1N", "nested_child_list": "BC2Nb"},
            {"root": "C", "nested": "CC1N", "nested_child_list": None},
        ],
        expected=[
            {"root": "A", "nested": {"nested": "AC1N", "nested_child_list": ["AC1Na"]}},
            {"root": "B", "nested": {"nested": "BC1N", "nested_child_list": ["BC1Na"]}},
            {"root": "B", "nested": {"nested": "BC1N", "nested_child_list": ["BC2Nb"]}},
            {"root": "C", "nested": {"nested": "CC1N", "nested_child_list": []}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=Model2,
        bindings=[
            {"root": "A", "nested": "AC1N", "nested_child_list": "AC1Na"},
            {"root": "B", "nested": "BC1N", "nested_child_list": "BC1Na"},
            {"root": "B", "nested": "BC1N", "nested_child_list": "BC2Nb"},
            {"root": "C", "nested": "CC1N", "nested_child_list": None},
        ],
        expected=[
            {"root": "A", "nested": {"nested": "AC1N", "nested_child_list": ["AC1Na"]}},
            {"root": "B", "nested": {"nested": "BC1N", "nested_child_list": ["BC1Na"]}},
            {"root": "B", "nested": {"nested": "BC1N", "nested_child_list": ["BC2Nb"]}},
            {"root": "C", "nested": {"nested": "CC1N", "nested_child_list": []}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=Model3,
        bindings=[
            {"x": 1, "a": 2, "b": 3, "c": 4, "d": 5},
            {"x": 2, "a": 2, "b": 4, "c": 5, "d": 6},
            {"x": 3, "a": 3, "b": 5, "c": 6, "d": 5},
        ],
        expected=[
            {"x": 1, "nested": {"a": 2, "b": [3], "deeply_nested": {"c": 4, "d": [5]}}},
            {"x": 2, "nested": {"a": 2, "b": [4], "deeply_nested": {"c": 5, "d": [6]}}},
            {"x": 3, "nested": {"a": 3, "b": [5], "deeply_nested": {"c": 6, "d": [5]}}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=Model4,
        bindings=[
            {"x": 1, "a": 2, "b": 3, "c": 4, "d": 5},
            {"x": 2, "a": 2, "b": 4, "c": 5, "d": 6},
            {"x": 3, "a": 3, "b": 5, "c": 6, "d": 5},
        ],
        expected=[
            {
                "x": 1,
                "nested": {"a": 2, "b": [3], "deeply_nested": [{"c": 4, "d": [5]}]},
            },
            {
                "x": 2,
                "nested": {"a": 2, "b": [4], "deeply_nested": [{"c": 5, "d": [6]}]},
            },
            {
                "x": 3,
                "nested": {"a": 3, "b": [5], "deeply_nested": [{"c": 6, "d": [5]}]},
            },
        ],
    ),
    ModelBindingsMapperParameter(
        model=Model5,
        bindings=[
            {"x": 1, "a": 2, "b": 3, "c": 4, "d": 5},
            {"x": 2, "a": 2, "b": 4, "c": 5, "d": 6},
            {"x": 3, "a": 3, "b": 5, "c": 6, "d": 5},
        ],
        expected=[
            {"x": 1, "nested": {"a": 2, "b": [3], "deeply_nested": {"c": 4, "d": [5]}}},
            {"x": 2, "nested": {"a": 2, "b": [4], "deeply_nested": {"c": 5, "d": [6]}}},
            {"x": 3, "nested": {"a": 3, "b": [5], "deeply_nested": {"c": 6, "d": [5]}}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=Model6,
        bindings=[
            {"x": 1, "a": 2, "b": 3, "c": 4, "d": 5},
            {"x": 2, "a": 2, "b": 4, "c": 5, "d": 6},
            {"x": 3, "a": 3, "b": 5, "c": 6, "d": 5},
        ],
        expected=[
            {"x": 1, "nested": {"a": 2, "b": [3], "deeply_nested": {"c": 4, "d": [5]}}},
            {"x": 2, "nested": {"a": 2, "b": [4], "deeply_nested": {"c": 5, "d": [6]}}},
            {"x": 3, "nested": {"a": 3, "b": [5], "deeply_nested": {"c": 6, "d": [5]}}},
        ],
    ),
]


@pytest.mark.parametrize("params", ungrouped_nested_grouped_params)
def test_ungrouped_nested_grouped_model(params):
    mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
    result: list[dict] = [model.model_dump() for model in mapper.get_models()]

    assert result == params.expected
