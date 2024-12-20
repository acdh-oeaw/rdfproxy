"""Basic tests for rdfproxy.SPARQLModelAdapter pagination with grouped models."""

from typing import Annotated, Any, NamedTuple

from pydantic import BaseModel
import pytest
from rdfproxy import (
    ConfigDict,
    HttpxStrategy,
    Page,
    QueryParameters,
    SPARQLBinding,
    SPARQLModelAdapter,
    SPARQLWrapperStrategy,
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


@pytest.fixture(params=[HttpxStrategy, SPARQLWrapperStrategy])
def adapter(request):
    return SPARQLModelAdapter(
        target="https://graphdb.r11.eu/repositories/RELEVEN",
        query=query,
        model=Parent,
        sparql_strategy=request.param,
    )


@pytest.fixture(params=[HttpxStrategy, SPARQLWrapperStrategy])
def binding_adapter(request):
    return SPARQLModelAdapter(
        target="https://graphdb.r11.eu/repositories/RELEVEN",
        query=binding_query,
        model=BindingParent,
        sparql_strategy=request.param,
    )


@pytest.fixture(params=[HttpxStrategy, SPARQLWrapperStrategy])
def ungrouped_adapter(request):
    return SPARQLModelAdapter(
        target="https://graphdb.r11.eu/repositories/RELEVEN",
        query=query,
        model=Child,
        sparql_strategy=request.param,
    )


class AdapterParameter(NamedTuple):
    query_parameters: dict[str, Any]
    expected: Page


binding_adapter_parameters = [
    AdapterParameter(
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
        query_parameters={"page": 2, "size": 1},
        expected=Page[BindingParent](
            items=[{"parent": "y", "children": []}], page=2, size=1, total=3, pages=3
        ),
    ),
    AdapterParameter(
        query_parameters={"page": 3, "size": 1},
        expected=Page[BindingParent](
            items=[{"parent": "z", "children": []}], page=3, size=1, total=3, pages=3
        ),
    ),
]
#
adapter_parameters = [
    AdapterParameter(
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
        query_parameters={"page": 2, "size": 1},
        expected=Page[Parent](
            items=[{"parent": "y", "children": []}], page=2, size=1, total=3, pages=3
        ),
    ),
    AdapterParameter(
        query_parameters={"page": 3, "size": 1},
        expected=Page[Parent](
            items=[{"parent": "z", "children": []}], page=3, size=1, total=3, pages=3
        ),
    ),
]

ungrouped_adapter_parameters = [
    AdapterParameter(
        query_parameters={"page": 1, "size": 100},
        expected=Page[Child](
            items=[{"name": "foo"}], page=1, size=100, total=1, pages=1
        ),
    ),
]


@pytest.mark.remote
@pytest.mark.parametrize(
    ["query_parameters", "expected"],
    adapter_parameters,
)
def test_basic_adapter_grouped_pagination(adapter, query_parameters, expected):
    parameters = QueryParameters(**query_parameters)
    assert adapter.query(parameters) == expected


@pytest.mark.remote
@pytest.mark.parametrize(
    ["query_parameters", "expected"],
    binding_adapter_parameters,
)
def test_basic_binding_adapter_grouped_pagination(
    binding_adapter, query_parameters, expected
):
    parameters = QueryParameters(**query_parameters)
    assert binding_adapter.query(parameters) == expected


@pytest.mark.xfail
@pytest.mark.remote
@pytest.mark.parametrize(
    ["query_parameters", "expected"],
    ungrouped_adapter_parameters,
)
def test_basic_ungrouped_pagination(ungrouped_adapter, query_parameters, expected):
    """This shows a possible pagination count bug that needs investigating."""
    parameters = QueryParameters(**query_parameters)
    assert ungrouped_adapter.query(parameters) == expected
