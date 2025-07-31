"""Pytest entry point for alternating chains of nested ungrouped/grouped models."""

import pytest

from pydantic import BaseModel, Field
from rdfproxy import ConfigDict
from rdfproxy.mapper import _ModelBindingsMapper
from tests.utils._types import ModelBindingsMapperParameter


bindings = [
    {
        "x": 1,
        "a": 2,
        "b": 5,
        "y": 1,
        "c": 2,
        "d": 5,
    },
    {
        "x": 2,
        "a": 2,
        "b": 6,
        "y": 2,
        "c": 2,
        "d": 6,
    },
    {
        "x": 3,
        "a": 3,
        "b": 7,
        "y": 3,
        "c": 3,
        "d": 7,
    },
    {
        "x": 3,
        "a": 3,
        "b": 8,
        "y": 3,
        "c": 3,
        "d": 8,
    },
]


class DeeplyNestedGroupedModel(BaseModel):
    model_config = ConfigDict(group_by="c")

    c: int = Field(exclude=True)
    d: list[int]


class DeeplyNestedUngroupedModel(BaseModel):
    y: int
    deeply_nested_grouped: DeeplyNestedGroupedModel


class NestedGroupedModel(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: int = Field(exclude=True)
    b: list[int]

    deeply_nested_ungrouped: DeeplyNestedUngroupedModel


## ungrouped - grouped - ungrouped - grouped
class UngroupedRootModel(BaseModel):
    x: int
    nested: NestedGroupedModel


## grouped - grouped - ungrouped - grouped
class GroupedRootModel(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int
    nested: list[NestedGroupedModel]


params = [
    ModelBindingsMapperParameter(
        model=UngroupedRootModel,
        bindings=bindings,
        expected=[
            {
                "x": 1,
                "nested": {
                    "b": [5, 6],
                    "deeply_nested_ungrouped": {
                        "y": 1,
                        "deeply_nested_grouped": {"d": [5, 6]},
                    },
                },
            },
            {
                "x": 2,
                "nested": {
                    "b": [5, 6],
                    "deeply_nested_ungrouped": {
                        "y": 1,
                        "deeply_nested_grouped": {"d": [5, 6]},
                    },
                },
            },
            {
                "x": 3,
                "nested": {
                    "b": [7, 8],
                    "deeply_nested_ungrouped": {
                        "y": 3,
                        "deeply_nested_grouped": {"d": [7, 8]},
                    },
                },
            },
            {
                "x": 3,
                "nested": {
                    "b": [7, 8],
                    "deeply_nested_ungrouped": {
                        "y": 3,
                        "deeply_nested_grouped": {"d": [7, 8]},
                    },
                },
            },
        ],
    ),
    ModelBindingsMapperParameter(
        model=GroupedRootModel,
        bindings=bindings,
        expected=[
            {
                "x": 1,
                "nested": [
                    {
                        "b": [5],
                        "deeply_nested_ungrouped": {
                            "y": 1,
                            "deeply_nested_grouped": {"d": [5]},
                        },
                    }
                ],
            },
            {
                "x": 2,
                "nested": [
                    {
                        "b": [6],
                        "deeply_nested_ungrouped": {
                            "y": 2,
                            "deeply_nested_grouped": {"d": [6]},
                        },
                    }
                ],
            },
            {
                "x": 3,
                "nested": [
                    {
                        "b": [7, 8],
                        "deeply_nested_ungrouped": {
                            "y": 3,
                            "deeply_nested_grouped": {"d": [7, 8]},
                        },
                    }
                ],
            },
        ],
    ),
]


@pytest.mark.parametrize("params", params)
def test_ungrouped_grouped_nested_grouped_basic(params):
    mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
    result: list[dict] = [model.model_dump() for model in mapper.get_models()]

    assert result == params.expected
