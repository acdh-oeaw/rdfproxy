"""Functionality for dynamic SPARQL query modifcation."""

from itertools import chain
import re
from typing import overload

from rdflib import Variable
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue, ParseResults
from rdfproxy.utils._exceptions import QueryConstructionException


def replace_query_select_clause(query: str, repl: str) -> str:
    """Replace the SELECT clause of a query with repl."""
    pattern: re.Pattern = re.compile(
        r"select\s+.*?(?=\s+where)", flags=re.IGNORECASE | re.DOTALL
    )

    if re.search(pattern=pattern, string=query) is None:
        raise QueryConstructionException("Unable to obtain SELECT clause.")

    modified_query = re.sub(
        pattern=pattern,
        repl=repl,
        string=query,
        count=1,
    )

    return modified_query


def remove_sparql_prefixes(query: str) -> str:
    """Remove SPARQL prefixes from a query.

    This is needed for subquery injection, because subqueries cannot have prefixes.
    Note that this is not generic, all prefixes are simply cut from the subquery
    and are not resolved against the outer query prefixes.
    """
    prefix_pattern = re.compile(r"PREFIX\s+\w*:\s?<[^>]+>\s*", flags=re.IGNORECASE)
    cleaned_query = re.sub(prefix_pattern, "", query).strip()
    return cleaned_query


def inject_into_query(query: str, injectant: str) -> str:
    """Inject some injectant (e.g. subquery or filter clause) into a query."""
    if (tail := re.search(r"}[^}]*\Z", query)) is None:
        raise QueryConstructionException(
            "Unable to inject subquery."
        )  # pragma: no cover ; this will be unreachable once query checking runs

    tail_index: int = tail.start()
    injected_query: str = f"{query[:tail_index]} {{{injectant}}} {query[tail_index:]}"
    return injected_query


def add_solution_modifier(
    query: str,
    *,
    order_by: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> str:
    """Add optional solution modifiers in SPARQL-conformant order to a query."""
    modifiers = []

    if order_by is not None:
        modifiers.append(f"order by ?{order_by}")
    if limit is not None:
        modifiers.append(f"limit {limit}")
    if offset is not None:
        modifiers.append(f"offset {offset}")

    return f"{query} {' '.join(modifiers)}".strip()


@overload
def _compvalue_to_dict(comp_value: dict | CompValue) -> dict: ...


@overload
def _compvalue_to_dict(comp_value: list | ParseResults) -> list: ...


def _compvalue_to_dict(comp_value: CompValue):
    """Convert a CompValue parsing object into a Python dict/list representation.

    Helper for get_query_projection.
    """
    if isinstance(comp_value, dict):
        return {key: _compvalue_to_dict(value) for key, value in comp_value.items()}
    elif isinstance(comp_value, list | ParseResults):
        return [_compvalue_to_dict(item) for item in comp_value]
    else:
        return comp_value


def get_query_projection(query: str) -> list[Variable]:
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
        case _:  # pragma: no cover
            raise Exception("Unable to obtain query projection.")
