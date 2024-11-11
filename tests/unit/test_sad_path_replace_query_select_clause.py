"""Sad path tests for rdfproxy.utils.sparql_utils.replace_query_select_clause."""

import pytest

from rdfproxy.utils.sparql_utils import replace_query_select_clause


fail_queries: list[str] = [
    "select?s where {?s ?p ?o .}",
    "select ?swhere {?s ?p ?o .}",
    "select where {?s ?p ?o .}",
    "ask where {?s ?p ?o .}",
    "construct {?s ?p ?o .} where {?s ?p ?o .}",
]


@pytest.mark.parametrize("fail_query", fail_queries)
def test_basic_sad_path_replace_query_select_clause(fail_query):
    with pytest.raises(Exception, match="Unable to obtain SELECT clause."):
        replace_query_select_clause(fail_query, "<test>")
