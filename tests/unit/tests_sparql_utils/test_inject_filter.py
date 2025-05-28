"""Unit tests for query injection FILTER clauses."""

from typing import NamedTuple

import pytest
from rdfproxy.utils.sparql_utils import inject_into_query


class InjectSubqueryParameter(NamedTuple):
    query: str
    filter_clause: str
    expected: str


inject_filter_parameters = [
    InjectSubqueryParameter(
        query="select * where {?s ?p ?o .}",
        filter_clause="filter (str(?s) = 'something')",
        expected="select * where {?s ?p ?o . filter (str(?s) = 'something') }",
    ),
    InjectSubqueryParameter(
        query="prefix : <some_prefix> select * where {?s ?p ?o .}",
        filter_clause="filter (str(?s) = 'something')",
        expected="prefix : <some_prefix> select * where {?s ?p ?o . filter (str(?s) = 'something') }",
    ),
    InjectSubqueryParameter(
        query="PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/> select * where {?s ?p ?o .}",
        filter_clause="filter (str(?s) = 'something')",
        expected="PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/> select * where {?s ?p ?o . filter (str(?s) = 'something') }",
    ),
    InjectSubqueryParameter(
        query="""
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
        PREFIX star: <https://r11.eu/ns/star/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX r11: <https://r11.eu/ns/spec/>
        PREFIX r11pros: <https://r11.eu/ns/prosopography/>
        SELECT
        ?location
        ?location__location_descriptive_name
        WHERE {
        ?location a crm:E53_Place.
        ?location crm:P3_has_note ?location__location_descriptive_name.
        }
        """,
        filter_clause="filter (str(?location) = 'somewhere')",
        expected="""
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
        PREFIX star: <https://r11.eu/ns/star/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX r11: <https://r11.eu/ns/spec/>
        PREFIX r11pros: <https://r11.eu/ns/prosopography/>
        SELECT
        ?location
        ?location__location_descriptive_name
        WHERE {
        ?location a crm:E53_Place.
        ?location crm:P3_has_note ?location__location_descriptive_name.
         filter (str(?location) = 'somewhere') }
        """,
    ),
    InjectSubqueryParameter(
        query="""
        PREFIX : <some_prefix>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
        PREFIX star: <https://r11.eu/ns/star/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX r11: <https://r11.eu/ns/spec/>
        PREFIX r11pros: <https://r11.eu/ns/prosopography/>
        SELECT
        ?location
        ?location__location_descriptive_name
        WHERE {
        ?location a crm:E53_Place.
        ?location crm:P3_has_note ?location__location_descriptive_name.
        }
        """,
        filter_clause="filter (str(?location) = 'somewhere')",
        expected="""
        PREFIX : <some_prefix>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
        PREFIX star: <https://r11.eu/ns/star/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX r11: <https://r11.eu/ns/spec/>
        PREFIX r11pros: <https://r11.eu/ns/prosopography/>
        SELECT
        ?location
        ?location__location_descriptive_name
        WHERE {
        ?location a crm:E53_Place.
        ?location crm:P3_has_note ?location__location_descriptive_name.
         filter (str(?location) = 'somewhere') }
        """,
    ),
]


@pytest.mark.parametrize(
    ["query", "filter_clause", "expected"], inject_filter_parameters
)
def test_inject_subquery(query, filter_clause, expected):
    injected = inject_into_query(
        query=query, injectant=filter_clause, inject_into_pattern=False
    )
    assert injected == expected
