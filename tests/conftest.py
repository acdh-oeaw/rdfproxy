"""Conftest.py for RDFProxy."""

import pytest

from SPARQLWrapper import JSON, SPARQLWrapper


def _sparql_wrapper_fixture_factory(endpoint: str, return_format=JSON):
    """Return a SPARQLWrapper fixture with the endpoint and return format_set."""

    @pytest.fixture
    def sparql_wrapper():
        sparql = SPARQLWrapper(endpoint)
        sparql.setReturnFormat(return_format)
        return sparql

    return sparql_wrapper


wikidata_wrapper = _sparql_wrapper_fixture_factory("https://dbpedia.org/sparql")
