"""Functionality for dynamic SPARQL query modifcation."""

from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from functools import partial
from itertools import chain
import re
from typing import cast, overload

from SPARQLWrapper import QueryResult, SPARQLWrapper
from rdflib import Variable
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue, ParseResults
from rdfproxy.utils._exceptions import QueryConstructionException
from rdfproxy.utils._types import ItemsQueryConstructor, SPARQLBinding, _TModelInstance
from rdfproxy.utils.utils import _is_iterable_of_str


@overload
def _compvalue_to_dict(comp_value: dict | CompValue) -> dict: ...


@overload
def _compvalue_to_dict(comp_value: list | ParseResults) -> list: ...


def _compvalue_to_dict(comp_value: CompValue):
    """Convert a CompValue parsing object into a Python dict/list representation."""
    if isinstance(comp_value, dict):
        return {key: _compvalue_to_dict(value) for key, value in comp_value.items()}
    elif isinstance(comp_value, list | ParseResults):
        return [_compvalue_to_dict(item) for item in comp_value]
    else:
        return comp_value


def get_query_projection(query: str) -> list[str]:
    """Parse a SPARQL SELECT query and extract the ordered bindings projection.

    The first case handles explicit/literal binding projections.
    The second case handles implicit/* binding projections.
    The third case handles implicit/* binding projections with VALUES.
    """
    _parse_result: CompValue = parseQuery(query)[1]
    parsed_query: dict = _compvalue_to_dict(_parse_result)

    match parsed_query:
        case {"projection": projection}:
            return [i["var"] for i in projection]
        case {"where": {"part": [{"triples": triples}]}}:
            projection = dict.fromkeys(
                i for i in chain.from_iterable(triples) if isinstance(i, Variable)
            )
            return list(projection)
        case {"where": {"part": [{"var": var}]}}:
            return var
        case _:
            raise Exception("Unable to obtain query projection.")


def construct_ungrouped_pagination_query(
    query: str, limit: int, offset: int, order_by: str | Iterable[str] | None = None
) -> str:
    """Construct an ungrouped pagination query."""
    match order_by:
        case None:
            order_by_variables = get_query_projection(query)
        case str():
            order_by_variables = [order_by]
        case order_by if _is_iterable_of_str(order_by):
            order_by_variables = order_by
        case _:
            raise TypeError(
                "order_by value must be of type str | Iterable[str] | None."
            )

    return f"{query} order by {' '.join(map(lambda x: f'?{x}', order_by_variables))} limit {limit} offset {offset}"


def replace_query_select_clause(query: str, repl: str) -> str:
    """Replace the SELECT clause of a query with repl."""
    pattern: re.Pattern = re.compile(
        r"select\s+.*?(?=\s+where)", flags=re.IGNORECASE | re.DOTALL
    )

    if re.search(pattern=pattern, string=query) is None:
        raise Exception("Unable to obtain SELECT clause.")

    modified_query = re.sub(
        pattern=pattern,
        repl=repl,
        string=query,
        count=1,
    )

    return modified_query


def _remove_sparql_prefixes(query: str) -> str:
    """Remove SPARQL prefixes from a query.

    This is needed for subquery injection, because subqueries cannot have prefixes.
    Note that this is not generic, all prefixes are simply ut from the subquery
    and do not get appended to the outer query prefixes.
    """
    prefix_pattern = re.compile(r"PREFIX\s+\w*:\s?<[^>]+>\s*", flags=re.I)
    cleaned_query = re.sub(prefix_pattern, "", query).strip()
    return cleaned_query


def inject_subquery(query: str, subquery: str) -> str:
    """Inject a SPARQL query with a subquery."""
    if (tail := re.search(r"}[^}]*\Z", query)) is None:
        raise QueryConstructionException("Unable to inject subquery.")

    tail_index: int = tail.start()
    injected: str = f"{query[:tail_index]} {{{_remove_sparql_prefixes(subquery)}}} {query[tail_index:]}"
    return injected


def construct_grouped_pagination_query(
    query: str, group_by_value: str, limit: int, offset: int
) -> str:
    """Construct a grouped pagination query."""
    _subquery_base: str = replace_query_select_clause(
        query=query, repl=f"select distinct ?{group_by_value}"
    )
    subquery: str = construct_ungrouped_pagination_query(
        query=_subquery_base, limit=limit, offset=offset
    )

    grouped_pagination_query: str = inject_subquery(query=query, subquery=subquery)
    return grouped_pagination_query


def get_items_query_constructor(
    model: type[_TModelInstance],
) -> ItemsQueryConstructor:
    """Get the applicable query constructor function given a model class."""

    if (group_by_value := model.model_config.get("group_by", None)) is None:
        return construct_ungrouped_pagination_query

    elif meta := model.model_fields[group_by_value].metadata:
        group_by_value = next(
            filter(lambda x: isinstance(x, SPARQLBinding), meta), group_by_value
        )

    return partial(construct_grouped_pagination_query, group_by_value=group_by_value)


def construct_items_query(
    query: str, model: type[_TModelInstance], limit: int, offset: int
) -> str:
    """Construct a grouped pagination query."""
    items_query_constructor: ItemsQueryConstructor = get_items_query_constructor(
        model=model
    )
    return items_query_constructor(query=query, limit=limit, offset=offset)


def construct_count_query(query: str, model: type[_TModelInstance]) -> str:
    """Construct a generic count query from a SELECT query."""
    try:
        group_by: str = model.model_config["group_by"]
        group_by_binding = next(
            filter(
                lambda x: isinstance(x, SPARQLBinding),
                model.model_fields[group_by].metadata,
            ),
            group_by,
        )
        count_query = construct_grouped_count_query(query, group_by_binding)
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
