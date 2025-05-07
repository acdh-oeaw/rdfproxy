"""Basic tests for the QueryConstructor class."""

from typing import NamedTuple

from pydantic import BaseModel
import pytest
from rdfproxy.constructor import _PageQueryConstructor
from rdfproxy.utils._types import ConfigDict
from rdfproxy.utils.models import QueryParameters


class UngroupedModel(BaseModel):
    x: int
    y: int


class GroupedModel(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int
    y: list[int]


class Expected(NamedTuple):
    count_query: str
    items_query: str


class QueryConstructorParameters(NamedTuple):
    query: str
    query_parameters: QueryParameters
    model: type[BaseModel]

    expected: Expected


parameters = [
    # ungrouped
    QueryConstructorParameters(
        query="select * where {?x ?p ?y}",
        query_parameters=QueryParameters(),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select * where {?x ?p ?y} order by ?x limit 100 offset 0",
        ),
    ),
    QueryConstructorParameters(
        query="select ?p ?y where {?x ?p ?y}",
        query_parameters=QueryParameters(),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select ?p ?y where {?x ?p ?y} order by ?p limit 100 offset 0",
        ),
    ),
    QueryConstructorParameters(
        query="select * where {?x ?p ?y}",
        query_parameters=QueryParameters(page=2, size=2),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select * where {?x ?p ?y} order by ?x limit 2 offset 2",
        ),
    ),
    # grouped
    QueryConstructorParameters(
        query="select * where {?x a ?y}",
        query_parameters=QueryParameters(),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select * where {?x a ?y {select distinct ?x where {?x a ?y} order by ?x limit 100 offset 0} } order by ?x",
        ),
    ),
    QueryConstructorParameters(
        query="select ?x ?y where {?x a ?y}",
        query_parameters=QueryParameters(),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select ?x ?y where {?x a ?y {select distinct ?x where {?x a ?y} order by ?x limit 100 offset 0} } order by ?x",
        ),
    ),
    QueryConstructorParameters(
        query="select ?x ?y where {?x a ?y}",
        query_parameters=QueryParameters(page=2, size=2),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select ?x ?y where {?x a ?y {select distinct ?x where {?x a ?y} order by ?x limit 2 offset 2} } order by ?x",
        ),
    ),
    # ordered / ungrouped
    QueryConstructorParameters(
        query="select * where {?x ?p ?y}",
        query_parameters=QueryParameters(order_by="x"),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select * where {?x ?p ?y} order by ASC(?x) limit 100 offset 0",
        ),
    ),
    QueryConstructorParameters(
        query="select * where {?x ?p ?y}",
        query_parameters=QueryParameters(order_by="x", desc=True),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select * where {?x ?p ?y} order by DESC(?x) limit 100 offset 0",
        ),
    ),
    QueryConstructorParameters(
        query="select ?p ?y where {?x ?p ?y}",
        query_parameters=QueryParameters(order_by="y"),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select ?p ?y where {?x ?p ?y} order by ASC(?y) limit 100 offset 0",
        ),
    ),
    QueryConstructorParameters(
        query="select ?p ?y where {?x ?p ?y}",
        query_parameters=QueryParameters(order_by="y", desc=True),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select ?p ?y where {?x ?p ?y} order by DESC(?y) limit 100 offset 0",
        ),
    ),
    QueryConstructorParameters(
        query="select * where {?x ?p ?y}",
        query_parameters=QueryParameters(page=2, size=2, order_by="x"),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select * where {?x ?p ?y} order by ASC(?x) limit 2 offset 2",
        ),
    ),
    QueryConstructorParameters(
        query="select * where {?x ?p ?y}",
        query_parameters=QueryParameters(page=2, size=2, order_by="x", desc=True),
        model=UngroupedModel,
        expected=Expected(
            count_query="select (count(*) as ?cnt) where {?x ?p ?y}",
            items_query="select * where {?x ?p ?y} order by DESC(?x) limit 2 offset 2",
        ),
    ),
    # ordered / grouped
    QueryConstructorParameters(
        query="select * where {?x a ?y}",
        query_parameters=QueryParameters(order_by="x"),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select * where {?x a ?y {select distinct ?x where {?x a ?y} order by ASC(?x) limit 100 offset 0} } order by ASC(?x)",
        ),
    ),
    QueryConstructorParameters(
        query="select * where {?x a ?y}",
        query_parameters=QueryParameters(order_by="x", desc=True),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select * where {?x a ?y {select distinct ?x where {?x a ?y} order by DESC(?x) limit 100 offset 0} } order by DESC(?x)",
        ),
    ),
    QueryConstructorParameters(
        query="select ?x ?y where {?x a ?y}",
        query_parameters=QueryParameters(order_by="x"),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select ?x ?y where {?x a ?y {select distinct ?x where {?x a ?y} order by ASC(?x) limit 100 offset 0} } order by ASC(?x)",
        ),
    ),
    QueryConstructorParameters(
        query="select ?x ?y where {?x a ?y}",
        query_parameters=QueryParameters(order_by="x", desc=True),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select ?x ?y where {?x a ?y {select distinct ?x where {?x a ?y} order by DESC(?x) limit 100 offset 0} } order by DESC(?x)",
        ),
    ),
    QueryConstructorParameters(
        query="select ?x ?y where {?x a ?y}",
        query_parameters=QueryParameters(page=2, size=2, order_by="x"),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select ?x ?y where {?x a ?y {select distinct ?x where {?x a ?y} order by ASC(?x) limit 2 offset 2} } order by ASC(?x)",
        ),
    ),
    QueryConstructorParameters(
        query="select ?x ?y where {?x a ?y}",
        query_parameters=QueryParameters(page=2, size=2, order_by="x", desc=True),
        model=GroupedModel,
        expected=Expected(
            count_query="select (count(distinct ?x) as ?cnt) where {?x a ?y}",
            items_query="select ?x ?y where {?x a ?y {select distinct ?x where {?x a ?y} order by DESC(?x) limit 2 offset 2} } order by DESC(?x)",
        ),
    ),
]


@pytest.mark.parametrize(["query", "query_parameters", "model", "expected"], parameters)
def test_query_constructor_items_query(query, query_parameters, model, expected):
    constructor = _PageQueryConstructor(
        query=query, query_parameters=query_parameters, model=model
    )

    assert constructor.get_count_query() == expected.count_query
    assert constructor.get_items_query() == expected.items_query
