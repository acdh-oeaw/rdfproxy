"""Functionality for dynamic SPARQL query modifcation."""

from collections.abc import Iterator
from contextlib import contextmanager
import re
from string import Template
from typing import Annotated
from typing import cast

from SPARQLWrapper import QueryResult, SPARQLWrapper
from rdfproxy.utils._types import _TModelInstance


ungrouped_pagination_base_query: Annotated[
    str, "SPARQL template for query pagination."
] = Template("""
$query
limit $limit
offset $offset
""")


def replace_query_select_clause(query: str, repl: str) -> str:
    """Replace the SELECT clause of a query with repl."""
    if re.search(r"select\s.+", query, re.I) is None:
        raise Exception("Unable to obtain SELECT clause.")

    count_query = re.sub(
        pattern=r"select\s.+",
        repl=repl,
        string=query,
        count=1,
        flags=re.I,
    )

    return count_query


def construct_count_query(query: str, model: type[_TModelInstance]) -> str:
    """Construct a generic count query from a SELECT query."""
    try:
        group_by: str = model.model_config["group_by"]
        count_query = construct_grouped_count_query(query, group_by)
    except KeyError:
        count_query = replace_query_select_clause(query, "select (count(*) as ?cnt)")

    return count_query


def calculate_offset(page: int, size: int) -> int:
    """Calculate offset value for paginated SPARQL templates."""
    match page:
        case 1:
            return 0
        case 2:
            return size
        case _:
            return size * (page - 1)


def construct_grouped_count_query(query: str, group_by) -> str:
    grouped_count_query = replace_query_select_clause(
        query, f"select (count(distinct ?{group_by}) as ?cnt)"
    )

    return grouped_count_query


def _get_bindings_from_bindings_dict(bindings_dict: dict) -> Iterator[dict]:
    bindings = map(
        lambda binding: {k: v["value"] for k, v in binding.items()},
        bindings_dict["results"]["bindings"],
    )
    return bindings


def get_bindings_from_query_result(query_result: QueryResult) -> Iterator[dict]:
    """Extract just the bindings from a SPARQLWrapper.QueryResult."""
    if (result_format := query_result.requestedFormat) != "json":
        raise Exception(
            "Only QueryResult objects with JSON format are currently supported. "
            f"Received object with requestedFormat '{result_format}'."
        )

    query_json: dict = cast(dict, query_result.convert())
    bindings = _get_bindings_from_bindings_dict(query_json)

    return bindings


@contextmanager
def temporary_query_override(sparql_wrapper: SPARQLWrapper):
    """Context manager that allows to contextually overwrite a query in a SPARQLWrapper object."""
    _query_cache = sparql_wrapper.queryString

    try:
        yield sparql_wrapper
    finally:
        sparql_wrapper.setQuery(_query_cache)


def query_with_wrapper(query: str, sparql_wrapper: SPARQLWrapper) -> Iterator[dict]:
    """Execute a SPARQL query using a predefined sparql_wrapper object.

    The query attribute of the wrapper object is temporarily overridden
    and gets restored after query execution.
    """
    with temporary_query_override(sparql_wrapper=sparql_wrapper):
        sparql_wrapper.setQuery(query)
        result: QueryResult = sparql_wrapper.query()

    bindings: Iterator[dict] = get_bindings_from_query_result(result)
    return bindings
