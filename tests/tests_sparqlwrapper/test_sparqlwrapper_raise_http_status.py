"""Pytest entry point for SPARQLWrapper tests that raise httpx.HTTPStatusError exceptions."""

from unittest.mock import patch

import pytest

import httpx
from rdfproxy.sparqlwrapper import SPARQLWrapper


def handler_400(request: httpx.Request) -> httpx.Response:
    return httpx.Response(400, json={"text": "Oh noooo!"})


def handler_500(request: httpx.Request) -> httpx.Response:
    return httpx.Response(500, json={"text": "Oh noooo!"})


mock_transport_400 = httpx.MockTransport(handler=handler_400)
mock_transport_500 = httpx.MockTransport(handler=handler_500)


@pytest.mark.parametrize(
    "param",
    [
        (mock_transport_400, "Client error '400 Bad Request'"),
        (mock_transport_500, "Server error '500 Internal Server Error'"),
    ],
)
def test_sparqlwrapper_raise_for_status(param):
    target = "https://query.wikidata.org/bigdata/namespace/wdq/sparql/"
    sparql_wrapper = SPARQLWrapper(target=target)
    query = "select * where {?s ?p ?o .} limit 10"

    mock_transport, error_message_match = param

    with patch(
        "rdfproxy.sparqlwrapper.httpx.AsyncClient",
        return_value=httpx.AsyncClient(transport=mock_transport),
    ):
        with pytest.raises(httpx.HTTPStatusError, match=error_message_match):
            sparql_wrapper.queries(query)
