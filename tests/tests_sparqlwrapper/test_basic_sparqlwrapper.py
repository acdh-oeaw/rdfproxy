"""Basic unit tests for rdfproxy.SPARQLWrapper."""

import datetime
from decimal import Decimal

import pytest
from rdflib import BNode, URIRef
from rdfproxy.sparqlwrapper import SPARQLWrapper


query_types = """
select *
where {
  values (?x) {
     (2)
     (2.2)
     (UNDEF)
     (<https://test.uri>)
     ('2024-01-01'^^xsd:date)
    }
}
"""

query_bnode = """
select *
where {
    bind (BNODE() as ?x)
}
"""


@pytest.mark.remote
def test_sparqlwrapper_python_cast_types():
    """Run a query featuring several RDF types and check for Python-casting."""
    sparql_wrapper = SPARQLWrapper("https://graphdb.r11.eu/repositories/RELEVEN")
    result = list(sparql_wrapper.query(query_types))

    expected = [
        {"x": 2},
        {"x": Decimal("2.2")},
        {"x": None},
        {"x": URIRef("https://test.uri")},
        {"x": datetime.date(2024, 1, 1)},
    ]

    assert result == expected


@pytest.mark.remote
def test_sparqlwrapper_python_cast_bnodes():
    """Run a query which mocks a BNode and check for BNode-casting."""
    sparql_wrapper = SPARQLWrapper("https://graphdb.r11.eu/repositories/RELEVEN")
    result, *_ = list(sparql_wrapper.query(query_bnode))

    assert isinstance(result["x"], BNode)
