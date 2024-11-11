"""Sad path tests for rdfprox.utils.sparql_utils.get_bindings_from_query_result."""

from unittest import mock

import pytest

from rdfproxy.utils.sparql_utils import get_bindings_from_query_result


def test_basic_sad_path_get_bindings_from_query_result():
    with mock.patch("SPARQLWrapper.QueryResult") as mock_query_result:
        mock_query_result.return_value.requestedFormat = "xml"
        exception_message = (
            "Only QueryResult objects with JSON format are currently supported."
        )
        with pytest.raises(Exception, match=exception_message):
            get_bindings_from_query_result(mock_query_result)
