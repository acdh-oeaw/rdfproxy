"""RDFProxy predicate functions."""

import re

from rdflib.plugins.sparql.parser import parseQuery


def query_is_select_query(query: str) -> bool:
    """Check if a SPARQL query is a SELECT query."""
    _, query_type = parseQuery(query)
    return query_type.name == "SelectQuery"


def query_has_solution_modifiers(query: str) -> bool:
    """Predicate for checking if a SPARQL query has a solution modifier."""
    pattern = r"}[^}]*\w+$"
    result = re.search(pattern, query)
    return bool(result)
