"""RDFProxy check runners."""

from collections.abc import Callable
from typing import Annotated, NoReturn, TypeVar

from rdfproxy.checks.query_checks import (
    check_parse_query,
    check_select_query,
    check_solution_modifiers,
)


T = TypeVar("T")
_TCheck = Callable[[T], T | NoReturn]


def compose_left(*fns: Callable) -> Callable:
    def _left_wrapper(*fns):
        fn, *rest_fns = fns

        if rest_fns:
            return lambda *args, **kwargs: fn(_left_wrapper(*rest_fns)(*args, **kwargs))
        return fn

    return _left_wrapper(*reversed(fns))


def compose_checker(*checkers: _TCheck) -> _TCheck:
    return compose_left(*checkers)


check_query: Annotated[
    _TCheck, "Run a series of checks on a query and return the query."
] = compose_checker(check_parse_query, check_select_query, check_solution_modifiers)
