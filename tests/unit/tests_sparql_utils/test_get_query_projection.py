"""Unit tests for sparql_utils.get_query_projection."""

from typing import NamedTuple

import pytest

from rdfproxy.utils.sparql_utils import get_query_projection


class QueryProjectionParameter(NamedTuple):
    query: str
    expected: list[str]


parameters = [
    # explicit projection
    QueryProjectionParameter(
        query="select ?s ?p ?o where {?s ?p ?o}", expected=["s", "p", "o"]
    ),
    QueryProjectionParameter(
        query="""
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        select ?s ?o where {?s ?p ?o}""",
        expected=["s", "o"],
    ),
    # implicit projection
    QueryProjectionParameter(
        query="select * where {?s ?p ?o}",
        expected=["s", "p", "o"],
    ),
    QueryProjectionParameter(
        query="""
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        select * where {?s ?p ?o}""",
        expected=["s", "p", "o"],
    ),
    # implicit projection with values clause
    QueryProjectionParameter(
        query="""
       select * where {
        values (?s ?p ?o)
        { (1 2 3) }
        }
        """,
        expected=["s", "p", "o"],
    ),
    QueryProjectionParameter(
        query="""
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
       select * where {
        values (?s ?p ?o)
        { (1 2 3) }
        }
        """,
        expected=["s", "p", "o"],
    ),
]


@pytest.mark.parametrize(["query", "expected"], parameters)
def test_get_query_projection(query, expected):
    projection = [str(binding) for binding in get_query_projection(query)]
    assert projection == expected
