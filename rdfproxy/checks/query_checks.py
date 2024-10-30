"""Query checks definitions."""

from typing import NoReturn, TypeVar

from rdflib.plugins.sparql.parser import parseQuery
from rdfproxy.utils._exceptions import UnsupportedQueryException
from rdfproxy.utils.predicates import (
    query_has_solution_modifiers,
    query_is_select_query,
)

TQuery = TypeVar("TQuery", bound=str)


def check_parse_query(query: TQuery) -> TQuery | NoReturn:
    parseQuery(query)
    return query


def check_select_query(query: TQuery) -> TQuery | NoReturn:
    if not query_is_select_query(query):
        raise UnsupportedQueryException("Only SELECT queries are applicable.")
    return query


def check_solution_modifiers(query: TQuery) -> TQuery | NoReturn:
    if query_has_solution_modifiers(query):
        raise UnsupportedQueryException("SPARQL solution modifieres are not supported.")
    return query
