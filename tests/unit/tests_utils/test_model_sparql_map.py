"""Pytest entry point for rdfproxy.utils.utils.ModelSPARQLMap tests."""

from typing import NamedTuple
from typing import Annotated

from pydantic import AnyHttpUrl, AnyUrl, BaseModel
import pytest
from rdflib import URIRef
from rdfproxy import ConfigDict, SPARQLBinding
from rdfproxy.utils.utils import ModelSPARQLMap


class ModelSPARQLMapParameters(NamedTuple):
    mapping: ModelSPARQLMap
    expected: dict


class Empty(BaseModel): ...


class DeeplyNested(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    p: str
    q: Annotated[URIRef, SPARQLBinding()]


class DeeplyNestedUnion(BaseModel):
    u: int
    v: Annotated[AnyUrl, SPARQLBinding("v_alias")]


class DeeplyNestedAggregate(BaseModel):
    r: str


class Nested(BaseModel):
    x: str
    y: Annotated[int, SPARQLBinding("y_alias")]
    z: list[int]

    deeply_nested: DeeplyNested
    deeply_nested_union: DeeplyNestedUnion | None = None
    deeply_nested_aggregate: list[DeeplyNestedAggregate]


class Model(BaseModel):
    a: AnyHttpUrl
    b: int | None
    c: Annotated[int, SPARQLBinding("c_alias")]
    d: int = 1
    e: list[int]
    f: Nested


model_sparql_map = ModelSPARQLMap(model=Model, recursive=True)

params = [
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=Model, recursive=True),
        expected={
            "a": "a",
            "b": "b",
            "c": "c_alias",
            "Nested.x": "x",
            "Nested.y": "y_alias",
            "DeeplyNested.p": "p",
            "DeeplyNested.q": "q",
            "DeeplyNestedUnion.u": "u",
            "DeeplyNestedUnion.v": "v_alias",
        },
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=Model),
        expected={
            "a": "a",
            "b": "b",
            "c": "c_alias",
        },
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=Nested, recursive=True),
        expected={
            "x": "x",
            "y": "y_alias",
            "DeeplyNested.p": "p",
            "DeeplyNested.q": "q",
            "DeeplyNestedUnion.u": "u",
            "DeeplyNestedUnion.v": "v_alias",
        },
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=Nested, recursive=False),
        expected={
            "x": "x",
            "y": "y_alias",
        },
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=DeeplyNested, recursive=True),
        expected={
            "p": "p",
            "q": "q",
        },
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=DeeplyNested, recursive=False),
        expected={
            "p": "p",
            "q": "q",
        },
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=DeeplyNestedUnion, recursive=True),
        expected={
            "u": "u",
            "v": "v_alias",
        },
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=DeeplyNestedUnion, recursive=False),
        expected={
            "u": "u",
            "v": "v_alias",
        },
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=Empty, recursive=True),
        expected={},
    ),
    ModelSPARQLMapParameters(
        mapping=ModelSPARQLMap(model=Empty, recursive=False),
        expected={},
    ),
]


@pytest.mark.parametrize("params", params)
def test_model_sparql_map(params):
    assert params.mapping == params.expected


@pytest.mark.parametrize("params", params)
def test_model_sparql_map_reverse(params):
    for k, v in params.mapping.items():
        assert params.mapping.reverse[v] == k


@pytest.mark.parametrize("params", params)
def test_model_sparql_map_sad_path(params):
    with pytest.raises(ValueError):
        params.mapping["dne"]
