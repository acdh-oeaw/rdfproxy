"""Pytest entry point for SPARQModelAdapter.get_item tests."""

from typing import Annotated, Any, NamedTuple

from pydantic import BaseModel
import pytest
from rdfproxy import ConfigDict
from rdfproxy.adapter import SPARQLModelAdapter
from rdfproxy.utils._types import SPARQLBinding
from rdfproxy.utils.exceptions import (
    MultipleResultsFound,
    NoResultsFound,
    UnprojectedKeyBindingException,
)


class AdapterGetItemParameter(NamedTuple):
    model: type[BaseModel]
    query: str
    key: dict[str, Any]
    expected: dict


class AdapterGetItemFailParameter(NamedTuple):
    model: type[BaseModel]
    query: str
    key: dict[str, Any]
    exception: type[Exception]


class SimpleModel(BaseModel):
    x: int
    y: Annotated[int, SPARQLBinding("y_alias")]


class NestedModel(BaseModel):
    a: int
    nested: SimpleModel


class GroupedNestedModel(BaseModel):
    model_config = ConfigDict(group_by="p")

    p: int
    q: list[int]
    r: list[NestedModel]


simple_model_query = """
select * where {
    values (?x ?y_alias) {
        (1 2)
        (3 4)
    }
}
"""

nested_model_query = """
select * where {
    values (?a ?x ?y_alias) {
        (0 1 2)
        (3 4 5)
    }
}
"""

grouped_nested_model_query = """
select *
where {
    values (?p ?q ?a ?x ?y_alias) {
        (1 2 3 4 5)
        (1 3 3 4 5)
        (1 3 4 4 5)
        (2 2 3 4 5)
    }
}

"""


parameters = [
    AdapterGetItemParameter(
        model=SimpleModel,
        query=simple_model_query,
        key={"x": 1},
        expected={"x": 1, "y": 2},
    ),
    AdapterGetItemParameter(
        model=SimpleModel,
        query=simple_model_query,
        key={"y": 4},
        expected={"x": 3, "y": 4},
    ),
    AdapterGetItemParameter(
        model=NestedModel,
        query=nested_model_query,
        key={"a": 0},
        expected={"a": 0, "nested": {"x": 1, "y": 2}},
    ),
    AdapterGetItemParameter(
        model=NestedModel,
        query=nested_model_query,
        key={"a": 3},
        expected={"a": 3, "nested": {"x": 4, "y": 5}},
    ),
    AdapterGetItemParameter(
        model=GroupedNestedModel,
        query=grouped_nested_model_query,
        key={"p": 1},
        expected={
            "p": 1,
            "q": [2, 3],
            "r": [
                {"a": 3, "nested": {"x": 4, "y": 5}},
                {"a": 4, "nested": {"x": 4, "y": 5}},
            ],
        },
    ),
    AdapterGetItemParameter(
        model=GroupedNestedModel,
        query=grouped_nested_model_query,
        key={"p": 2},
        expected={"p": 2, "q": [2], "r": [{"a": 3, "nested": {"x": 4, "y": 5}}]},
    ),
]

fail_parameters = [
    AdapterGetItemFailParameter(
        model=SimpleModel,
        query=simple_model_query,
        key={"x": 2},
        exception=NoResultsFound,
    ),
    AdapterGetItemFailParameter(
        model=NestedModel,
        query=nested_model_query,
        key={"a": 1},
        exception=NoResultsFound,
    ),
    AdapterGetItemFailParameter(
        model=GroupedNestedModel,
        query=grouped_nested_model_query,
        key={"p": 0},
        exception=NoResultsFound,
    ),
    AdapterGetItemFailParameter(
        model=SimpleModel,
        query=simple_model_query,
        key={"dne": None},
        exception=KeyError,
    ),
    AdapterGetItemFailParameter(
        model=SimpleModel,
        query="""
        select * where {
          values (?x ?y_alias) {
            (1 2)
            (1 3)
            (3 4)
          }
        }
        """,
        key={"x": 1},
        exception=MultipleResultsFound,
    ),
    # UnprojectedKeyBindingException
    AdapterGetItemFailParameter(
        model=SimpleModel,
        query="""
        select * where {
          values (?a ?b) {
            (1 2)
            (1 3)
            (3 4)
          }
        }
        """,
        key={"x": 1},
        exception=UnprojectedKeyBindingException,
    ),
]


@pytest.mark.parametrize("params", parameters)
def test_adapter_get_item(params, target):
    adapter = SPARQLModelAdapter(
        target=target,
        query=params.query,
        model=params.model,
    )

    result = adapter.get_item(**params.key)
    assert result.model_dump() == params.expected


@pytest.mark.parametrize("params", fail_parameters)
def test_adapter_get_item_fail(params, target):
    adapter = SPARQLModelAdapter(
        target=target,
        query=params.query,
        model=params.model,
    )

    with pytest.raises(params.exception):
        adapter.get_item(**params.key)
