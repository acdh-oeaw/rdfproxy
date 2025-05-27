"""Basic tests for the _ItemQueryConstructor class."""

from typing import Annotated, Any, Generic, NamedTuple

from pydantic import BaseModel
import pytest
from rdflib import XSD
from rdfproxy.constructor import _ItemQueryConstructor
from rdfproxy.utils._types import SPARQLBinding, _TModelInstance


class ConstructorParameters(NamedTuple, Generic[_TModelInstance]):
    key: dict[str, Any]
    xsd_type: str | None
    lang_tag: str | None

    query: str
    model: type[_TModelInstance]

    expected: str


class Model(BaseModel):
    x: int
    y: Annotated[int, SPARQLBinding("y_alias")]


constructor_parameters = [
    ConstructorParameters(
        key={"x": 1},
        xsd_type=None,
        lang_tag=None,
        query="select * where {?x <urn:p> ?y}",
        model=Model,
        expected='select * where {?x <urn:p> ?y filter (str(?x) = "1") }',
    ),
    ConstructorParameters(
        key={"y": 1},
        xsd_type=None,
        lang_tag=None,
        query="select * where {?x <urn:p> ?y}",
        model=Model,
        expected='select * where {?x <urn:p> ?y filter (str(?y_alias) = "1") }',
    ),
    ConstructorParameters(
        key={"x": 1},
        xsd_type=XSD.integer,
        lang_tag=None,
        query="select * where {?x <urn:p> ?y}",
        model=Model,
        expected=f'select * where {{?x <urn:p> ?y filter (?x = "1"^^<{XSD.integer}>) }}',
    ),
    ConstructorParameters(
        key={"x": 1},
        xsd_type=None,
        lang_tag="en",
        query="select * where {?x <urn:p> ?y}",
        model=Model,
        expected='select * where {?x <urn:p> ?y filter (?x = "1"@en) }',
    ),
]


@pytest.mark.parametrize("params", constructor_parameters)
def test_item_query_constructor(params):
    constructor = _ItemQueryConstructor(
        key=params.key,
        xsd_type=params.xsd_type,
        lang_tag=params.lang_tag,
        query=params.query,
        model=params.model,
    )

    item_query = constructor.get_item_query()

    assert item_query == params.expected


def test_item_query_constructor_fail():
    constructor = _ItemQueryConstructor(
        key={"x": 1},
        xsd_type=XSD.integer,
        lang_tag="en",
        query="select * where {?x <urn:p> ?y}",
        model=Model,
    )

    with pytest.raises(ValueError):
        constructor.get_item_query()
