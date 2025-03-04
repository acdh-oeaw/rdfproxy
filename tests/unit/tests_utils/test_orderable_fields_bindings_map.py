"""Basic unit tests for OrderableFieldsBindingsMap"""

from typing import Annotated

from pydantic import BaseModel
import pytest
from rdfproxy.utils._types import SPARQLBinding
from rdfproxy.utils.utils import OrderableFieldsBindingsMap


class ReallyDeeplyNestedModel(BaseModel):
    c: Annotated[str, SPARQLBinding("C_ALIAS")]


class DeeplyNestedModel(BaseModel):
    really_deeply_nested: ReallyDeeplyNestedModel
    really_deeply_nested_list: list[ReallyDeeplyNestedModel]


class NestedModel(BaseModel):
    b: Annotated[str, SPARQLBinding("B_ALIAS")]
    deeply_nested: DeeplyNestedModel


class TopModel(BaseModel):
    a: str
    nested: NestedModel
    nested_list: list[NestedModel]
    nested_alias_list: Annotated[list[NestedModel], SPARQLBinding("NOT_ORDERABLE")]
    some_list: list[int]


def test_basic_ordery_by_field_bindings_map():
    mapping = OrderableFieldsBindingsMap(model=TopModel)

    expected = {
        "a": "a",
        "NestedModel.b": "B_ALIAS",
        "ReallyDeeplyNestedModel.c": "C_ALIAS",
    }
    assert mapping == expected


def test_sad_ordery_by_field_bindings_map():
    mapping = OrderableFieldsBindingsMap(model=TopModel)

    with pytest.raises(ValueError):
        mapping["dne"]
