"""Basic tests for rdfproxy.SPARQLModelAdapter pagination with grouped models."""

from itertools import chain
from typing import Annotated, Any, NamedTuple

import pytest

from pydantic import BaseModel
from rdfproxy import (
    ConfigDict,
    Page,
    QueryParameters,
    SPARQLBinding,
    SPARQLModelAdapter,
)

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

all_undef_query = """
select ?parent ?child ?name
where {
    values (?parent ?child ?name) {
        ('x' 'c' UNDEF)
        ('y' 'd' UNDEF)
        ('y' 'e' UNDEF)
        ('z' UNDEF UNDEF)
    }
}
"""

all_undef_binding_query = """
select ?parentBinding ?child ?name
where {
    values (?parentBinding ?child ?name) {
        ('x' 'c' UNDEF)
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
    model: type[BaseModel]
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
                BindingParent(**{"parent": "x", "children": [{"name": "foo"}]}),
                BindingParent(**{"parent": "y", "children": []}),
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
            items=[BindingParent(**{"parent": "z", "children": []})],
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
            items=[BindingParent(**{"parent": "x", "children": [{"name": "foo"}]})],
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
            items=[BindingParent(**{"parent": "y", "children": []})],
            page=2,
            size=1,
            total=3,
            pages=3,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 3, "size": 1},
        expected=Page[BindingParent](
            items=[BindingParent(**{"parent": "z", "children": []})],
            page=3,
            size=1,
            total=3,
            pages=3,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={},
        expected=Page[BindingParent](
            items=[
                BindingParent(**{"parent": "x", "children": [{"name": "foo"}]}),
                BindingParent(**{"parent": "y", "children": []}),
                BindingParent(**{"parent": "z", "children": []}),
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
                Parent(**{"parent": "x", "children": [{"name": "foo"}]}),
                Parent(**{"parent": "y", "children": []}),
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
            items=[Parent(**{"parent": "z", "children": []})],
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
            items=[Parent(**{"parent": "x", "children": [{"name": "foo"}]})],
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
            items=[Parent(**{"parent": "y", "children": []})],
            page=2,
            size=1,
            total=3,
            pages=3,
        ),
    ),
    AdapterParameter(
        model=Parent,
        query=query,
        query_parameters={"page": 3, "size": 1},
        expected=Page[Parent](
            items=[Parent(**{"parent": "z", "children": []})],
            page=3,
            size=1,
            total=3,
            pages=3,
        ),
    ),
    AdapterParameter(
        model=Parent,
        query=query,
        query_parameters={},
        expected=Page[Parent](
            items=[
                Parent(**{"parent": "x", "children": [{"name": "foo"}]}),
                Parent(**{"parent": "y", "children": []}),
                Parent(**{"parent": "z", "children": []}),
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
            items=[Child(**{"name": "foo"})], page=1, size=100, total=1, pages=1
        ),
    ),
    AdapterParameter(
        model=Child,
        query=query,
        query_parameters={},
        expected=Page[Child](
            items=[Child(**{"name": "foo"})], page=1, size=100, total=1, pages=1
        ),
    ),
]

all_undef_adapter_parameters = [
    AdapterParameter(
        model=Parent,
        query=all_undef_query,
        query_parameters={},
        expected=Page[Parent](
            items=[
                Parent(parent="x", children=[]),
                Parent(parent="y", children=[]),
                Parent(parent="z", children=[]),
            ],
            page=1,
            size=100,
            total=3,
            pages=1,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=all_undef_binding_query,
        query_parameters={},
        expected=Page[BindingParent](
            items=[
                BindingParent(parent="x", children=[]),
                BindingParent(parent="y", children=[]),
                BindingParent(parent="z", children=[]),
            ],
            page=1,
            size=100,
            total=3,
            pages=1,
        ),
    ),
]

ordered_binding_adapter_parameters = [
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"order_by": "parent"},
        expected=Page[BindingParent](
            items=[
                BindingParent(**{"parent": "x", "children": [{"name": "foo"}]}),
                BindingParent(**{"parent": "y", "children": []}),
                BindingParent(**{"parent": "z", "children": []}),
            ],
            page=1,
            size=100,
            total=3,
            pages=1,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"order_by": "parent", "desc": False},
        expected=Page[BindingParent](
            items=[
                BindingParent(**{"parent": "x", "children": [{"name": "foo"}]}),
                BindingParent(**{"parent": "y", "children": []}),
                BindingParent(**{"parent": "z", "children": []}),
            ],
            page=1,
            size=100,
            total=3,
            pages=1,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"order_by": "parent", "desc": True},
        expected=Page[BindingParent](
            items=[
                BindingParent(**{"parent": "z", "children": []}),
                BindingParent(**{"parent": "y", "children": []}),
                BindingParent(**{"parent": "x", "children": [{"name": "foo"}]}),
            ],
            page=1,
            size=100,
            total=3,
            pages=1,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 1, "size": 2, "order_by": "parent", "desc": True},
        expected=Page[BindingParent](
            items=[
                BindingParent(**{"parent": "z", "children": []}),
                BindingParent(**{"parent": "y", "children": []}),
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
        query_parameters={"page": 2, "size": 2, "order_by": "parent", "desc": True},
        expected=Page[BindingParent](
            items=[
                BindingParent(**{"parent": "x", "children": [{"name": "foo"}]}),
            ],
            page=2,
            size=2,
            total=3,
            pages=2,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 1, "size": 1, "order_by": "parent", "desc": True},
        expected=Page[BindingParent](
            items=[BindingParent(**{"parent": "z", "children": []})],
            page=1,
            size=1,
            total=3,
            pages=3,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 2, "size": 1, "desc": True, "order_by": "parent"},
        expected=Page[BindingParent](
            items=[BindingParent(**{"parent": "y", "children": []})],
            page=2,
            size=1,
            total=3,
            pages=3,
        ),
    ),
    AdapterParameter(
        model=BindingParent,
        query=binding_query,
        query_parameters={"page": 3, "size": 1, "order_by": "parent", "desc": True},
        expected=Page[BindingParent](
            items=[BindingParent(**{"parent": "x", "children": [{"name": "foo"}]})],
            page=3,
            size=1,
            total=3,
            pages=3,
        ),
    ),
]


@pytest.mark.parametrize(
    "params",
    chain(
        binding_adapter_parameters,
        adapter_parameters,
        all_undef_adapter_parameters,
        ordered_binding_adapter_parameters,
    ),
)
def test_adapter_grouped_pagination(target, params):
    adapter = SPARQLModelAdapter(
        target=target,
        query=params.query,
        model=params.model,
    )

    parameters = QueryParameters(**params.query_parameters)
    assert adapter.get_page(parameters) == params.expected

    with pytest.deprecated_call():
        assert adapter.query(parameters) == params.expected


@pytest.mark.xfail
@pytest.mark.parametrize("params", ungrouped_adapter_parameters)
def test_basic_ungrouped_pagination(target, params):
    """This shows a possible pagination count bug that needs investigating."""
    adapter = SPARQLModelAdapter(
        target=target,
        query=params.query,
        model=params.model,
    )

    parameters = QueryParameters(**params.query_parameters)
    assert adapter.query(parameters) == params.expected
