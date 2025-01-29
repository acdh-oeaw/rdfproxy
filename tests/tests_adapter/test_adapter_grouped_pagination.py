"""Basic tests for rdfproxy.SPARQLModelAdapter pagination with grouped models."""

from itertools import chain
from typing import Annotated, Any, NamedTuple

from pydantic import BaseModel
import pytest
from rdfproxy import (
    ConfigDict,
    Page,
    QueryParameters,
    SPARQLBinding,
    SPARQLModelAdapter,
)


binding_query = """
select ?parentBinding ?child ?name
where {
    values (?parentBinding ?child ?name) {
        ('x' 'c' 'foo')
        ('y' 'd' UNDEF)
        ('y' 'e' UNDEF)
        ('z' UNDEF UNDEF)
    }
}
"""

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


class BindingParent(BaseModel):
    model_config = ConfigDict(group_by="parent")

    parent: Annotated[str, SPARQLBinding("parentBinding")]
    children: list[Child]


class Parent(BaseModel):
    model_config = ConfigDict(group_by="parent")

    parent: str
    children: list[Child]


class AdapterParameter(NamedTuple):
    model: BaseModel
    query: str
    query_parameters: dict[str, Any]
    expected: Page


binding_adapter_parameters = [
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 1, "size": 2},
        expected=Page[BindingParent](
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
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 2, "size": 2},
        expected=Page[BindingParent](
            items=[{"parent": "z", "children": []}],
            page=2,
            size=2,
            total=3,
            pages=2,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 1, "size": 1},
        expected=Page[BindingParent](
            items=[{"parent": "x", "children": [{"name": "foo"}]}],
            page=1,
            size=1,
            total=3,
            pages=3,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 2, "size": 1},
        expected=Page[BindingParent](
            items=[{"parent": "y", "children": []}], page=2, size=1, total=3, pages=3
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 3, "size": 1},
        expected=Page[BindingParent](
            items=[{"parent": "z", "children": []}], page=3, size=1, total=3, pages=3
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={},
        expected=Page[BindingParent](
            items=[
                {"parent": "x", "children": [{"name": "foo"}]},
                {"parent": "y", "children": []},
                {"parent": "z", "children": []},
            ],
            page=1,
            size=100,
            total=3,
            pages=1,
        ),
    ),
]

adapter_parameters = [
    AdapterParameter(
        model=Parent,
        query=query,
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
        model=Parent,
        query=query,
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
        model=Parent,
        query=query,
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
        model=Parent,
        query=query,
        query_parameters={"page": 2, "size": 1},
        expected=Page[Parent](
            items=[{"parent": "y", "children": []}], page=2, size=1, total=3, pages=3
        ),
    ),
    AdapterParameter(
        model=Parent,
        query=query,
        query_parameters={"page": 3, "size": 1},
        expected=Page[Parent](
            items=[{"parent": "z", "children": []}], page=3, size=1, total=3, pages=3
        ),
    ),
    AdapterParameter(
        model=Parent,
        query=query,
        query_parameters={},
        expected=Page[Parent](
            items=[
                {"parent": "x", "children": [{"name": "foo"}]},
                {"parent": "y", "children": []},
                {"parent": "z", "children": []},
            ],
            page=1,
            size=100,
            total=3,
            pages=1,
        ),
    ),
]

ungrouped_adapter_parameters = [
    AdapterParameter(
        model=Child,
        query=query,
        query_parameters={"page": 1, "size": 100},
        expected=Page[Child](
            items=[{"name": "foo"}], page=1, size=100, total=1, pages=1
        ),
    ),
    AdapterParameter(
        model=Child,
        query=query,
        query_parameters={},
        expected=Page[Child](
            items=[{"name": "foo"}], page=1, size=100, total=1, pages=1
        ),
    ),
]


@pytest.mark.parametrize(
    "params",
    chain(binding_adapter_parameters, adapter_parameters),
)
def test_adapter_grouped_pagination(params):
    adapter = SPARQLModelAdapter(
        target="https://graphdb.r11.eu/repositories/RELEVEN",
        query=params.query,
        model=params.model,
    )

    parameters = QueryParameters(**params.query_parameters)
    assert adapter.query(parameters) == params.expected


@pytest.mark.xfail
@pytest.mark.remote
@pytest.mark.parametrize("params", ungrouped_adapter_parameters)
def test_basic_ungrouped_pagination(params):
    """This shows a possible pagination count bug that needs investigating."""
    adapter = SPARQLModelAdapter(
        target="https://graphdb.r11.eu/repositories/RELEVEN",
        query=params.query,
        model=params.model,
    )

    parameters = QueryParameters(**params.query_parameters)
    assert adapter.query(parameters) == params.expected
