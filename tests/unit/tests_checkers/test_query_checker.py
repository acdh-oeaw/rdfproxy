"""Unit test for rdfproxy.utils.checkers.query_checker."""

import pytest
from rdfproxy.utils.checkers.query_checker import check_query
from rdfproxy.utils.exceptions import QueryParseException, UnsupportedQueryException


fail_queries_parse_exception: list[str] = [
    "select * where {?s ?p ?o ",
    "select * where {?s ?p}",
    "select ? where {?s ?p ?o}",
    "select * where {?s ?p ?o } limit",
    """
    PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
    select * where {?s ?p ?o } limit
    """,
]
fail_queries_unsupported: list[str] = [
    # query types
    "ask where {?s ?p ?o}",
    """
    PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
    ask where {?s ?p ?o}
    """,
    "construct {?s ?p ?o} where {?s ?p ?o}",
    "describe ?s where {?s ?p ?o}",
    # solution modifiers
    "select * where {?s ?p ?o .} limit 10",
    "select * where {?s ?p ?o .} offset 1",
    "select * where {?s ?p ?o .} limit 2 offset 1",
    "select ?s where {?s ?p ?o .} group by ?s",
    "select ?s where {?s ?p ?o .} group by ?s having (?o > 1)",
]


@pytest.mark.parametrize("query", fail_queries_parse_exception)
def test_check_query_parse_exception(query):
    with pytest.raises(QueryParseException):
        check_query(query)


@pytest.mark.parametrize("query", fail_queries_unsupported)
def test_check_query_unsupported(query):
    with pytest.raises(UnsupportedQueryException):
        check_query(query)
