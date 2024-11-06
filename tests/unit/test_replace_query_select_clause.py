"""Unit tests for rdfproxy.utils.sparql_utils.replace_query_select_clause."""

import re
from textwrap import dedent

import pytest

from rdfproxy.utils.sparql_utils import replace_query_select_clause
from tests.utils._types import QueryConstructionParameter


def _normalize_whitespace(string: str) -> str:
    return re.sub(r"\s+", " ", string.strip())


expected_simple_query = "select <test> where { ?s ?p ?o . }"

query_construction_parameters = [
    QueryConstructionParameter(
        input_query="""
        select ?s ?p ?o
        where {
        ?s ?p ?o .
        }
        """,
        expected_query=expected_simple_query,
    ),
    QueryConstructionParameter(
        input_query="""
        select ?s
        ?p ?o
        where {
        ?s ?p ?o .
        }
        """,
        expected_query=expected_simple_query,
    ),
    QueryConstructionParameter(
        input_query="""
        select ?s ?p
        ?o
        where {
        ?s ?p ?o .
        }
        """,
        expected_query=expected_simple_query,
    ),
    QueryConstructionParameter(
        input_query="""
        select ?s ?p ?o where {
        ?s ?p ?o .
        }
        """,
        expected_query=expected_simple_query,
    ),
    QueryConstructionParameter(
        input_query="select ?s ?p ?o where { ?s ?p ?o . }",
        expected_query=expected_simple_query,
    ),
]


@pytest.mark.parametrize(
    ["input_query", "expected_query"], query_construction_parameters
)
def test_basic_replace_query_select_clause(input_query, expected_query):
    _constructed_indent: str = replace_query_select_clause(input_query, "select <test>")
    _constructed_dedent: str = replace_query_select_clause(
        dedent(input_query), "select <test>"
    )

    constructed_indent = _normalize_whitespace(_constructed_indent)
    constructed_dedent = _normalize_whitespace(_constructed_dedent)

    assert constructed_dedent == constructed_indent == expected_query
