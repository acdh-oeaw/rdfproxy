"""Basic unit tests for rdfproxy.SPARQLWrapper."""

import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from rdflib import BNode, Literal, URIRef, XSD


query_types = """
select *
where {
  values (?x) {
     (2)
     (2.2)
     (UNDEF)
     (<https://test.uri>)
     ('2024-01-01'^^xsd:date)
     ('2024'^^xsd:gYear)
     ('2024-01'^^xsd:gYearMonth)
    }
}
"""

query_bnode = """
select *
where {
    bind (BNODE() as ?x)
}
"""


def test_sparqlwrapper_python_cast_types(sparql_wrapper):
    """Run a query featuring several RDF types and check for Python-casting."""
    result = list(sparql_wrapper.query(query_types))

    expected = [
        {"x": 2},
        {"x": Decimal("2.2")},
        {"x": None},
        {"x": URIRef("https://test.uri")},
        {"x": datetime.date(2024, 1, 1)},
        {"x": Literal("2024", datatype=XSD.gYear)},
        {"x": Literal("2024-01", datatype=XSD.gYearMonth)},
    ]

    assert result == expected


def test_sparqlwrapper_python_cast_bnodes(sparql_wrapper):
    """Run a query which mocks a BNode and check for BNode-casting."""
    result, *_ = list(sparql_wrapper.query(query_bnode))

    assert isinstance(result["x"], BNode)


@pytest.mark.parametrize(
    "query",
    [
        "select * where {?s ?p ?o .} limit 0",
        f"select * where {{<urn:{uuid4()}> <urn:{uuid4()}> '{uuid4()}'}}",
    ],
)
def test_sparqlwrapper_empty_result_set(sparql_wrapper, query):
    """Check if SPARQLWrapper.query produces empty iterators given empty SPARQL result sets.

    The test parametrization uses decorator stacking over itertools.product
    because this allows to mark the GraphDB targeting SPARQLWrapper as 'remote'.
    """
    result = sparql_wrapper.query(query)
    assert list(result) == []
