"""Basic tests for rdfproxy.SPARQLModelAdapter pagination with grouped models."""

from typing import Any, NamedTuple

import pytest

from pydantic import BaseModel, ConfigDict
from rdfproxy import Page, QueryParameters, SPARQLModelAdapter


query = """
select ?parent ?child ?name
where {
    values (?parent ?child ?name) {
        ('x' 'c' 'foo')
        ('y' 'd' UNDEF)
        ('y' 'e' UNDEF)
        ('z' UNDEF UNDEF)
    }
}
"""


class Child(BaseModel):
    name: str | None = None


class Parent(BaseModel):
    model_config = ConfigDict(group_by="parent")

    parent: str
    children: list[Child]


parent_adapter = SPARQLModelAdapter(
    target="https://graphdb.r11.eu/repositories/RELEVEN",
    query=query,
    model=Parent,
)


class AdapterParameter(NamedTuple):
    adapter: SPARQLModelAdapter
    query_parameters: dict[str, Any]
    expected: Page


adapter_parameters = [
    AdapterParameter(
        adapter=parent_adapter,
        query_parameters={"page": 1, "size": 2},
        expected=Page[Parent](
            items=[
                {"parent": "x", "children": [{"name": "foo"}]},
                {"parent": "y", "children": []},
            ],
            page=1,
            size=2,
            total=3,
            pages=2,
        ),
    ),
    AdapterParameter(
        adapter=parent_adapter,
        query_parameters={"page": 2, "size": 2},
        expected=Page[Parent](
            items=[{"parent": "z", "children": []}],
            page=2,
            size=2,
            total=3,
            pages=2,
        ),
    ),
    AdapterParameter(
        adapter=parent_adapter,
        query_parameters={"page": 1, "size": 1},
        expected=Page[Parent](
            items=[{"parent": "x", "children": [{"name": "foo"}]}],
            page=1,
            size=1,
            total=3,
            pages=3,
        ),
    ),
    AdapterParameter(
        adapter=parent_adapter,
        query_parameters={"page": 2, "size": 1},
        expected=Page[Parent](
            items=[{"parent": "y", "children": []}], page=2, size=1, total=3, pages=3
        ),
    ),
    AdapterParameter(
        adapter=parent_adapter,
        query_parameters={"page": 3, "size": 1},
        expected=Page[Parent](
            items=[{"parent": "z", "children": []}], page=3, size=1, total=3, pages=3
        ),
    ),
]


@pytest.mark.remote
@pytest.mark.parametrize(
    ["adapter", "query_parameters", "expected"], adapter_parameters
)
def test_basic_adapter_grouped_pagination(adapter, query_parameters, expected):
    parameters = QueryParameters(**query_parameters)
    assert adapter.query(parameters) == expected
