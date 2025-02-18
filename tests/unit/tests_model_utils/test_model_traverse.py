"""Unit tests for model_traverse."""

from typing import Annotated

from pydantic import BaseModel
import pytest
from rdfproxy.utils._types import SPARQLBinding
from rdfproxy.utils.model_utils import model_traverse


class SomeModel(BaseModel):
    i: int


class ReallyDeeplyNestedModel(BaseModel):
    field: Annotated[str, SPARQLBinding("alias_field")]


class DeeplyNestedModel(BaseModel):
    really_deeply_nested: ReallyDeeplyNestedModel


class NestedModel(BaseModel):
    deeply_nested: DeeplyNestedModel


class TopModel(BaseModel):
    a: int = 1
    b: list[int] = []

    x: NestedModel
    y: list[SomeModel]
    z: SomeModel | None


self_true_parameters = [
    (
        TopModel,
        [
            "TopModel",
            "NestedModel",
            "DeeplyNestedModel",
            "ReallyDeeplyNestedModel",
            "SomeModel",
            "SomeModel",
        ],
    ),
    (NestedModel, ["NestedModel", "DeeplyNestedModel", "ReallyDeeplyNestedModel"]),
    (DeeplyNestedModel, ["DeeplyNestedModel", "ReallyDeeplyNestedModel"]),
    (ReallyDeeplyNestedModel, ["ReallyDeeplyNestedModel"]),
]

self_false_parameters = map(
    lambda param: (param[0], param[1][1:]), self_true_parameters
)


@pytest.mark.parametrize(["model", "expected"], self_true_parameters)
def test_model_traverse_self_true(model, expected):
    result = list(model_traverse(model, lambda x: x.__name__))
    assert result == expected


@pytest.mark.parametrize(["model", "expected"], self_false_parameters)
def test_model_traverse_self_false(model, expected):
    result = list(model_traverse(model, lambda x: x.__name__, _self=False))
    assert result == expected
