"""Unit tests for rdfproxy.utils.sparql_utils.get_query_projection."""

from typing import NamedTuple

import pytest

from rdfproxy.utils.sparql_utils import get_query_projection


class QueryProjectionParameter(NamedTuple):
    query: str
    exptected_projection: list[str]


queries = []


query_projection_parameters = [
    QueryProjectionParameter(
        query="select ?s ?p ?o where {?s ?p ?o .}",
        exptected_projection=["s", "p", "o"],
    ),
    QueryProjectionParameter(
        query="select ?s ?o where {?s ?p ?o .}",
        exptected_projection=["s", "o"],
    ),
    QueryProjectionParameter(
        query="select * where {?s ?p ?o .}",
        exptected_projection=[
            "s",
            "p",
            "o",
        ],
    ),
    QueryProjectionParameter(
        query="select * where {?s ?p ?o ; <urn:predicate> ?o2 .}",
        exptected_projection=[
            "s",
            "p",
            "o",
            "o2",
        ],
    ),
    QueryProjectionParameter(
        query="select * where {?s1 <urn:predicate> ?o1 ; ?p ?o .}",
        exptected_projection=[
            "s1",
            "o1",
            "p",
            "o",
        ],
    ),
    QueryProjectionParameter(
        query="select ?o ?s ?p where {?s ?p ?o ; <urn:predicate> ?o2 .}",
        exptected_projection=[
            "o",
            "s",
            "p",
        ],
    ),
    QueryProjectionParameter(
        query="select ?p ?o ?s where {?s ?p ?o .}",
        exptected_projection=[
            "p",
            "o",
            "s",
        ],
    ),
    QueryProjectionParameter(
        query="select ?s where {?s <urn:prediate> <urn:object> .}",
        exptected_projection=["s"],
    ),
    QueryProjectionParameter(
        query="select ?p where {<urn:subject> ?p <urn:object> .}",
        exptected_projection=["p"],
    ),
    QueryProjectionParameter(
        query="select ?o where {<urn:subject> <urn:predicate> ?o .}",
        exptected_projection=["o"],
    ),
    QueryProjectionParameter(
        query="select ?s where {?s ?p ?o . {?s2 ?p2 ?o2 .}}",
        exptected_projection=["s"],
    ),
    QueryProjectionParameter(
        query="select ?s2 where {?s ?p ?o . {?s2 ?p2 ?o2 .}}",
        exptected_projection=["s2"],
    ),
    QueryProjectionParameter(
        query="select ?s ?p ?o where { values (?s ?p ?o) { (1 2 3) } }",
        exptected_projection=[
            "s",
            "p",
            "o",
        ],
    ),
    QueryProjectionParameter(
        query="select * where { values (?s ?p ?o) { (1 2 3) } }",
        exptected_projection=[
            "s",
            "p",
            "o",
        ],
    ),
]


@pytest.mark.parametrize(["query", "expected_projection"], query_projection_parameters)
def test_basic_get_query_projection(query, expected_projection):
    assert list(map(str, get_query_projection(query))) == expected_projection
