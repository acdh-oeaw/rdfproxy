"""Unit tests for model_traverse."""

from collections import UserList
from typing import Annotated

from pydantic import BaseModel
import pytest
from rdfproxy.utils._types import SPARQLBinding
from rdfproxy.utils.model_utils import ModelVisitor


class SomeModel(BaseModel):
    i: int


class ReallyDeeplyNestedModel(BaseModel):
    field: Annotated[str, SPARQLBinding("alias_field")]


class DeeplyNestedModel(BaseModel):
    really_deeply_nested: ReallyDeeplyNestedModel


class NestedModel(BaseModel):
    deeply_nested: DeeplyNestedModel


class NestedModelUnion(BaseModel):
    nested_model_union: SomeModel | DeeplyNestedModel


class TopModel(BaseModel):
    a: int = 1
    b: list[int] = []

    x: NestedModel
    y: list[SomeModel]
    z: SomeModel | None


class OtherTopModel(TopModel):
    nested_model_union: NestedModelUnion


traverse_all_parameters = [
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
    (
        NestedModelUnion,
        [
            "NestedModelUnion",
            "SomeModel",
            "DeeplyNestedModel",
            "ReallyDeeplyNestedModel",
        ],
    ),
    (
        OtherTopModel,
        [
            "OtherTopModel",
            "NestedModel",
            "DeeplyNestedModel",
            "ReallyDeeplyNestedModel",
            "SomeModel",
            "SomeModel",
            "NestedModelUnion",
            "SomeModel",
            "DeeplyNestedModel",
            "ReallyDeeplyNestedModel",
        ],
    ),
]

traverse_submodels_parameters = map(
    lambda param: (param[0], param[1][1:]), traverse_all_parameters
)

traverse_topmodel_parameters = map(
    lambda param: (param[0], param[1][0]), traverse_all_parameters
)


class Visited(UserList):
    def __init__(self):
        self.data = []

    def __call__(self, model: type[BaseModel]) -> type[BaseModel]:
        self.data.append(model)
        return model


@pytest.mark.parametrize(["model", "expected"], traverse_all_parameters)
def test_model_traverse_self_true(model, expected):
    visited = Visited()

    visitor = ModelVisitor(model=model, all_model_hook=visited)
    visitor.visit()

    assert [model.__name__ for model in visited] == expected


@pytest.mark.parametrize(["model", "expected"], traverse_submodels_parameters)
def test_model_traverse_submodels(model, expected):
    visited = Visited()

    visitor = ModelVisitor(model=model, sub_model_hook=visited)
    visitor.visit()

    assert [model.__name__ for model in visited] == expected


@pytest.mark.parametrize(["model", "expected"], traverse_topmodel_parameters)
def test_model_traverse_topmodel(model, expected):
    visited = Visited()

    visitor = ModelVisitor(model=model, top_model_hook=visited)
    visitor.visit()

    assert [model.__name__ for model in visited] == [expected]
