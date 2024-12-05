"""Unit tests for rdfproxy.utils.sparql_utils.construct_ungrouped_pagination_query."""

from collections.abc import Iterable
from typing import NamedTuple

import pytest

from rdfproxy.utils.sparql_utils import construct_ungrouped_pagination_query


class UngroupedPaginationQueryParameter(NamedTuple):
    query: str
    expected: str
    order_by: str | Iterable[str] | None = None


ungrouped_pagination_query_parameters = [
    UngroupedPaginationQueryParameter(
        query="select ?s ?p ?o where {?s ?p ?o .}",
        expected="select ?s ?p ?o where {?s ?p ?o .} order by ?s ?p ?o limit 1 offset 2",
    ),
    UngroupedPaginationQueryParameter(
        query="select ?s ?p ?o where {?s ?p ?o .}",
        expected="select ?s ?p ?o where {?s ?p ?o .} order by ?test limit 1 offset 2",
        order_by="test",
    ),
    UngroupedPaginationQueryParameter(
        query="select ?s ?p ?o where {?s ?p ?o .}",
        expected="select ?s ?p ?o where {?s ?p ?o .} order by ?test limit 1 offset 2",
        order_by=["test"],
    ),
    UngroupedPaginationQueryParameter(
        query="select ?s ?p ?o where {?s ?p ?o .}",
        expected="select ?s ?p ?o where {?s ?p ?o .} order by ?test ?another_test limit 1 offset 2",
        order_by=["test", "another_test"],
    ),
    UngroupedPaginationQueryParameter(
        query="select * where {?s ?p ?o .}",
        expected="select * where {?s ?p ?o .} order by ?s ?p ?o limit 1 offset 2",
    ),
    UngroupedPaginationQueryParameter(
        query="select * where {?s ?p ?o .}",
        expected="select * where {?s ?p ?o .} order by ?test limit 1 offset 2",
        order_by="test",
    ),
    UngroupedPaginationQueryParameter(
        query="select * where {?s ?p ?o .}",
        expected="select * where {?s ?p ?o .} order by ?test limit 1 offset 2",
        order_by=["test"],
    ),
    UngroupedPaginationQueryParameter(
        query="select * where {?s ?p ?o .}",
        expected="select * where {?s ?p ?o .} order by ?test ?another_test limit 1 offset 2",
        order_by=["test", "another_test"],
    ),
    UngroupedPaginationQueryParameter(
        query="select ?s ?p ?o where {values (?s ?p ?o) {(1 2 3)}}",
        expected="select ?s ?p ?o where {values (?s ?p ?o) {(1 2 3)}} order by ?test limit 1 offset 2",
        order_by="test",
    ),
    UngroupedPaginationQueryParameter(
        query="select * where {values (?s ?p ?o) {(1 2 3)}}",
        expected="select * where {values (?s ?p ?o) {(1 2 3)}} order by ?test limit 1 offset 2",
        order_by="test",
    ),
    UngroupedPaginationQueryParameter(
        query="select * where {values (?s ?p ?o) {(1 2 3)}}",
        expected="select * where {values (?s ?p ?o) {(1 2 3)}} order by ?test limit 1 offset 2",
        order_by=["test"],
    ),
    UngroupedPaginationQueryParameter(
        query="select * where {values (?s ?p ?o) {(1 2 3)}}",
        expected="select * where {values (?s ?p ?o) {(1 2 3)}} order by ?test ?another_test limit 1 offset 2",
        order_by=["test", "another_test"],
    ),
]


@pytest.mark.parametrize(
    ["query", "expected", "order_by"], ungrouped_pagination_query_parameters
)
def test_basic_construct_ungrouped_pagination_query_default(query, expected, order_by):
    constructed_query = construct_ungrouped_pagination_query(
        query, 1, 2, order_by=order_by
    )
    assert constructed_query == expected
