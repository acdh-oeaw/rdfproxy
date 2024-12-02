"""Unit tests for inject_subquery."""

from typing import NamedTuple

import pytest
from rdfproxy.utils.sparql_utils import inject_subquery


class InjectSubqueryParameter(NamedTuple):
    query: str
    subquery: str
    expected: str


inject_subquery_parameters = [
    InjectSubqueryParameter(
        query="select * where {?s ?p ?o .}",
        subquery="select * where {?s ?p ?o .}",
        expected="select * where {?s ?p ?o . {select * where {?s ?p ?o .}} }",
    ),
    InjectSubqueryParameter(
        query="select * where {?s ?p ?o .}",
        subquery="prefix : <some_prefix> select * where {?s ?p ?o .}",
        expected="select * where {?s ?p ?o . {select * where {?s ?p ?o .}} }",
    ),
    InjectSubqueryParameter(
        query="prefix : <some_prefix> select * where {?s ?p ?o .}",
        subquery="prefix : <some_prefix> select * where {?s ?p ?o .}",
        expected="prefix : <some_prefix> select * where {?s ?p ?o . {select * where {?s ?p ?o .}} }",
    ),
    InjectSubqueryParameter(
        query="PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/> select * where {?s ?p ?o .}",
        subquery="select * where {?s ?p ?o .}",
        expected="PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/> select * where {?s ?p ?o . {select * where {?s ?p ?o .}} }",
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
        subquery="select * where {?s ?p ?o .}",
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
         {select * where {?s ?p ?o .}} }
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
        subquery="select * where {?s ?p ?o .}",
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
         {select * where {?s ?p ?o .}} }
        """,
    ),
]


@pytest.mark.parametrize(["query", "subquery", "expected"], inject_subquery_parameters)
def test_inject_subquery(query, subquery, expected):
    injected = inject_subquery(query=query, subquery=subquery)
    assert injected == expected
