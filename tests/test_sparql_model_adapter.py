"""Pytest entry point for rdfproxy.SPARQLModelAdapter tests."""

import pytest

from rdfproxy import SPARQLModelAdapter
from tests.data.models import ComplexModel


@pytest.mark.remote
def test_sparql_model_adapter_basic(wikidata_wrapper):
    """Simple base test for SPARQLModelAdapter."""
    query = """
    select ?x ?y ?a ?p
    where {
        values (?x ?y ?a ?p) {
            (1 2 "a value" "p value")
        }
    }
    """
    wikidata_wrapper.setQuery(query)
    adapter = SPARQLModelAdapter(sparql_wrapper=wikidata_wrapper)
    model, *_ = adapter(query=query, model_constructor=ComplexModel)

    assert isinstance(model, ComplexModel)
