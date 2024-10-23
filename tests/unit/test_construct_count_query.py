"""Unit tests for rdfproxy.utils.sparql_utils.construct_count_query."""

import pytest

from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult
from rdfproxy.utils.sparql_utils import construct_count_query
from tests.data.parameters.count_query_parameters import (
    construct_count_query_parameters,
)


def _get_cnt_value_from_sparql_result(
    result: SPARQLResult, count_var: str = "cnt"
) -> int:
    """Get the 'cnt' binding of a count query from a SPARQLResult object."""
    return int(result.bindings[0][count_var])


@pytest.mark.parametrize(
    ["query", "model", "expected"], construct_count_query_parameters
)
def test_basic_construct_count_query(query, model, expected):
    """Check the count of a grouped model.

    The count query constructed based on a grouped value must only count
    distinct values according to the grouping specified in the model.
    """

    graph: Graph = Graph()
    count_query: str = construct_count_query(query, model)
    query_result: SPARQLResult = graph.query(count_query)

    cnt: int = _get_cnt_value_from_sparql_result(query_result)

    assert cnt == expected
