"""Pytest entry point for rdfproxy.utils.sparql_utils.construct_count_query tests."""

from pydantic import BaseModel, ConfigDict
from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult
from rdfproxy.utils.sparql_utils import construct_count_query


query = """
select ?x ?y ?z
where {
    values (?x ?y ?z) {
        (1 2 3)
        (1 22 33)
        (2 222 333)
    }
}
"""

graph: Graph = Graph()


class Dummy(BaseModel):
    pass


class GroupedDummy(BaseModel):
    model_config = ConfigDict(group_by="x")


count_query_dummy = construct_count_query(query=query, model=Dummy)
count_query_grouped_dummy = construct_count_query(query=query, model=GroupedDummy)


def _get_cnt_value_from_sparql_result(
    result: SPARQLResult, count_var: str = "cnt"
) -> int:
    return int(result.bindings[0][count_var])


def test_basic_construct_count_query():
    result_dummy: SPARQLResult = graph.query(count_query_dummy)
    result_grouped_dummy: SPARQLResult = graph.query(count_query_grouped_dummy)

    assert _get_cnt_value_from_sparql_result(result_dummy) == 3
    assert _get_cnt_value_from_sparql_result(result_grouped_dummy) == 2
