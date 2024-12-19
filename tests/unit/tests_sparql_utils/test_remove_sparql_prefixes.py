from typing import NamedTuple

import pytest

from rdfproxy.utils.sparql_utils import remove_sparql_prefixes
from tests.utils.utils import normalize_query


class SPARQLRemovePrefixParameter(NamedTuple):
    query: str
    expected: str


parameters = [
    SPARQLRemovePrefixParameter(
        query="""
        select * where { ?s ?p ?o .}
        """,
        expected="select * where { ?s ?p ?o . }",
    ),
    SPARQLRemovePrefixParameter(
        query="""
        prefix ns: <https://some.prefix>
        prefix other_ns: <https://another.prefix>
        select * where { ?s ?p ?o .}
        """,
        expected="select * where { ?s ?p ?o . }",
    ),
    SPARQLRemovePrefixParameter(
        query="""
        prefix ns: <https://some.prefix> prefix other_ns: <https://another.prefix>
        select * where { ?s ?p ?o .}
        """,
        expected="select * where { ?s ?p ?o . }",
    ),
    SPARQLRemovePrefixParameter(
        query="""
        prefix ns: <https://some.prefix>

        prefix other_ns: <https://another.prefix>
        select * where { ?s ?p ?o .}
        """,
        expected="select * where { ?s ?p ?o . }",
    ),
    SPARQLRemovePrefixParameter(
        query="""
        prefix ns: <https://some.prefix>

        prefix other_ns: <https://another.prefix>

        select * where { ?s ?p ?o .}
        """,
        expected="select * where { ?s ?p ?o . }",
    ),
]


@pytest.mark.parametrize(["query", "expected"], parameters)
def test_remove_sparql_prefixes(query, expected):
    modified_query = remove_sparql_prefixes(query)
    assert normalize_query(modified_query) == expected
