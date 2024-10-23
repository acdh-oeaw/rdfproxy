"""Pytest entry point for rdfproxy.utils.sparql_utils.construct_count_query tests."""

from itertools import groupby

import pytest

from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult
from rdfproxy.utils.sparql_utils import construct_count_query
from tests.data.parameters.count_query_parameters import count_query_parameters


def _get_cnt_value_from_sparql_result(
    result: SPARQLResult, count_var: str = "cnt"
) -> int:
    """Get the 'cnt' binding of a count query from a SPARQLResult object."""
    return int(result.bindings[0][count_var])


@pytest.mark.parametrize(["query", "model", "grouped_model"], count_query_parameters)
def test_basic_construct_count_query(query, model, grouped_model):
    """Check the count of a grouped model.

    The count query constructed based on a grouped value must only count
    distinct values according to the grouping specified in the model.
    """
    graph: Graph = Graph()

    count_query_dummy: str = construct_count_query(query=query, model=model)
    count_query_grouped_dummy: str = construct_count_query(
        query=query, model=grouped_model
    )

    result_initial_query: SPARQLResult = graph.query(query)
    result_dummy: SPARQLResult = graph.query(count_query_dummy)
    result_grouped_dummy: SPARQLResult = graph.query(count_query_grouped_dummy)

    expected_dummy: int = len(result_initial_query.bindings)
    expected_grouped_dummy: int = len(
        list(
            groupby(
                result_initial_query.bindings,
                lambda x: x[grouped_model.model_config["group_by"]],
            )
        )
    )

    cnt_from_query_dummy: int = _get_cnt_value_from_sparql_result(result_dummy)
    cnt_from_query_grouped_dummy: int = _get_cnt_value_from_sparql_result(
        result_grouped_dummy
    )

    assert cnt_from_query_dummy == expected_dummy
    assert cnt_from_query_grouped_dummy == expected_grouped_dummy
