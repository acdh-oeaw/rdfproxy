"""Pytest fixture definitions."""

import pytest
from rdflib import Graph
from rdfproxy.sparqlwrapper import SPARQLWrapper


remote_triplestore_urls = ["https://graphdb.r11.eu/repositories/RELEVEN"]

remote_triplestore_params = [
    pytest.param(store, marks=pytest.mark.remote) for store in remote_triplestore_urls
]


@pytest.fixture(params=[*remote_triplestore_params, Graph()])
def target(request) -> str | Graph:
    """Fixture for generating SPARQLWrapper/SPARQLModelAdapter targets."""
    return request.param


@pytest.fixture()
def sparql_wrapper(target) -> SPARQLWrapper:
    """Fixture for generating a SPARQLWrapper instance."""
    return SPARQLWrapper(target=target)
