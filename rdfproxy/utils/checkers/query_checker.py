"""Functionality for performing checks on SPARQL queries."""

import logging

from rdfproxy.utils._exceptions import UnsupportedQueryException
from rdfproxy.utils._types import ParsedSPARQL, _TQuery
from rdfproxy.utils.utils import compose_left


logger = logging.getLogger(__name__)


def _check_select_query(parsed_sparql: ParsedSPARQL) -> ParsedSPARQL:
    """Check if a SPARQL query is a SELECT query.

    This is meant to run as a component in check_query.
    """
    logger.debug("Running SELECT query check.")

    if parsed_sparql.parse_object.name != "SelectQuery":
        raise UnsupportedQueryException("Only SELECT queries are applicable.")
    return parsed_sparql


def _check_solution_modifiers(parsed_sparql: ParsedSPARQL) -> ParsedSPARQL:
    """Check if a SPARQL query has a solution modifier.

    This is meant to run as a component in check_query.
    """
    logger.debug("Running solution modifier check.")

    def _has_modifier():
        for mod_name in ["limitoffset", "groupby", "having", "orderby"]:
            if (mod := getattr(parsed_sparql.parse_object, mod_name)) is not None:
                return mod
        return False

    if mod := _has_modifier():
        logger.critical("Detected solution modifier '%s' in outer query.", mod)
        raise UnsupportedQueryException(
            "Solution modifiers for top-level queries are currently not supported."
        )

    return parsed_sparql


def check_query(query: _TQuery) -> _TQuery:
    """Check a SPARQL query by running a compose pipeline of checks."""
    logger.debug("Running query check pipeline on '%s'", query)
    parsed_sparql = ParsedSPARQL(query=query)

    result: ParsedSPARQL = compose_left(
        _check_select_query,
        _check_solution_modifiers,
    )(parsed_sparql)

    return result.data
