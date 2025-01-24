"""Sad path tests for SPARQLModelAdapter with invalid queries"""

from pydantic import BaseModel
import pytest
from rdfproxy.adapter import SPARQLModelAdapter
from rdfproxy.utils._exceptions import QueryParseException, UnsupportedQueryException
from tests.unit.tests_checkers.test_query_checker import (
    fail_queries_parse_exception,
    fail_queries_unsupported,
)


class Dummy(BaseModel):
    pass


@pytest.mark.parametrize("query", fail_queries_parse_exception)
def test_adapter_parse_exception(query):
    with pytest.raises(QueryParseException):
        SPARQLModelAdapter(target="dummy.target", model=Dummy, query=query)


@pytest.mark.parametrize("query", fail_queries_unsupported)
def test_adapter_unsupported_exception(query):
    with pytest.raises(UnsupportedQueryException):
        SPARQLModelAdapter(target="dummy.target", model=Dummy, query=query)
