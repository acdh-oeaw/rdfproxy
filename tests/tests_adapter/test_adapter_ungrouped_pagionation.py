"""Basic tests for rdfproxy.SPARQLModelAdapter pagination with ungrouped models."""

from collections.abc import Iterator
from itertools import permutations
from string import Template

import pytest

from pydantic import BaseModel
from rdfproxy import Page, QueryParameters, SPARQLModelAdapter


def _generate_queries() -> Iterator[str]:
    """Generate static queries using permuations of a VALUES data block."""
    _values = [
        "('z' 'a' 'foo')",
        "('y' 'b' UNDEF)",
        "('y' 'a' UNDEF)",
        "('x' UNDEF UNDEF)",
    ]

    values_permutations = permutations(_values, r=4)
    query_template = Template(
        """
        select ?parent ?child ?name
        where {
          values (?parent ?child ?name)
            { $values }
        }
        """
    )

    for values in values_permutations:
        values = " ".join(values)
        yield query_template.substitute(values=values)


class Model(BaseModel):
    parent: str
    child: str | None = None
    name: str | None = None


@pytest.mark.remote
@pytest.mark.parametrize("query", _generate_queries())
def test_ungrouped_pagination(query):
    """Run SPARQLModelAdapter.query with test queries and check for consistent result ordering.

    The duplicated parent 'y' rows are expected to be orderd by 'child'.
    This requires ordering by all bindings of a given projection.
    """
    expected = Page[Model](
        items=[
            {"parent": "x", "child": None, "name": None},
            {"parent": "y", "child": "a", "name": None},
            {"parent": "y", "child": "b", "name": None},
            {"parent": "z", "child": "a", "name": "foo"},
        ],
        page=1,
        size=100,
        total=4,
        pages=1,
    )

    adapter = SPARQLModelAdapter(
        target="https://graphdb.r11.eu/repositories/RELEVEN",
        query=query,
        model=Model,
    )

    query_parameters = QueryParameters(page=1, size=100)
    assert adapter.query(query_parameters=query_parameters) == expected
