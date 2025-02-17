from typing import NamedTuple

import pytest
from rdfproxy.utils.sparql_utils import add_solution_modifier


class AddSolutionModifierParameter(NamedTuple):
    query: str
    parameters: dict
    expected: str


parameters = [
    # basics
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"order_by": None, "limit": None, "offset": None},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
    ),
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"order_by": None, "limit": None, "offset": 1},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } offset 1",
    ),
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"order_by": None, "limit": 1, "offset": None},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } limit 1",
    ),
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"order_by": "?x", "limit": None, "offset": None},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } order by ?x",
    ),
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"order_by": "?x", "limit": 1, "offset": 1},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } order by ?x limit 1 offset 1",
    ),
    # order
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"offset": 1, "limit": 1, "order_by": None},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } limit 1 offset 1",
    ),
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"offset": 1, "limit": 1, "order_by": None},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } limit 1 offset 1",
    ),
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"offset": 1, "limit": None, "order_by": "?x"},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } order by ?x offset 1",
    ),
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"offset": None, "limit": 1, "order_by": "?x"},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } order by ?x limit 1",
    ),
    AddSolutionModifierParameter(
        query="prefix ns: <https://some.namespace> select * where {?s ?p ?o }",
        parameters={"offset": 1, "limit": 1, "order_by": "?x"},
        expected="prefix ns: <https://some.namespace> select * where {?s ?p ?o } order by ?x limit 1 offset 1",
    ),
]


@pytest.mark.parametrize(["query", "parameters", "expected"], parameters)
def test_add_solution_modifier(query, parameters, expected):
    modified_query = add_solution_modifier(query, **parameters)
    assert modified_query == expected
