"""Unit tests for QueryParameters model parametrization."""

from typing import Annotated, get_args

from pydantic import BaseModel
from rdfproxy.utils._types import SPARQLBinding
from rdfproxy.utils.models import QueryParameters


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


def test_query_parameters_model_parametrization():
    parametrized_model = QueryParameters[TopModel]()
    order_by_values = parametrized_model.model_fields["order_by"]
    orderable_fields = [
        field.value
        for field in get_args(order_by_values.annotation)[0]  # can be hardcoded
    ]

    assert orderable_fields == ["a", "NestedModel.b", "ReallyDeeplyNestedModel.c"]
