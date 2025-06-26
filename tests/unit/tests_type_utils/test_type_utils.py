"""Unit tests for the type_utils module."""

import datetime
import decimal
from typing import Annotated, Optional, Union
from xml.dom.minidom import Document

from pydantic import AnyHttpUrl, AnyUrl
from pydantic import BaseModel, create_model
import pytest
from rdflib import BNode, Literal, URIRef
from rdflib.xsd_datetime import Duration
from rdfproxy.utils.type_utils import (
    _is_list_pydantic_model_static_type,
    _is_list_static_type,
    _is_pydantic_model_static_type,
    _is_pydantic_model_union_static_type,
    _is_sparql_bound_field_type,
)


class Model(BaseModel):
    pass


list_static_type_true_parameters = [
    list,
    list[None],
    list[int],
    list[int | str],
    list[int | None],
    list[BaseModel],
    list[BaseModel | str],
    list[BaseModel | None],
]

list_static_type_false_parameters = [
    int,
    str,
    Model,
    None,
    int | None,
    "1",
    1,
    object(),
    type,
    Model,
    BaseModel,
]


@pytest.mark.parametrize("obj", list_static_type_true_parameters)
def test_is_list_static_type_true(obj):
    assert _is_list_static_type(obj)


@pytest.mark.parametrize("obj", list_static_type_false_parameters)
def test_is_list_static_type_false(obj):
    assert not _is_list_static_type(obj)


pydantic_model_static_type_true_parameters = [Model, create_model("AnotherModel")]
pydantic_model_static_type_false_parameters = [
    None,
    int,
    BaseModel,
    "1",
    1,
    object(),
    type,
]

pydantic_model_union_static_type_true_parameters = [
    Model | None,
    None | Model,
    str | None | Model,
    Optional[Model],
    Union[Model, None],
    Union[None, Model],
    Union[str, None, Model],
]

sparql_bound_field_type_parameters = [
    # _TSPARQLBindingValue
    URIRef,
    BNode,
    Literal,
    None,
    datetime.date,
    datetime.datetime,
    datetime.time,
    datetime.timedelta,
    Duration,
    bytes,
    bool,
    int,
    float,
    decimal.Decimal,
    Document,
    # _TSPARQLBoundField
    str,
    AnyUrl,
    # some subtypes
    AnyHttpUrl,
    # some unions
    str | None,
    URIRef | BNode,
    URIRef | BNode | Literal,
    # annotated types
    Annotated[int, ""],
    Annotated[int | str | None, ""],
]

sparql_bound_field_type_false_parameters = [
    list[int],
    list[Model],
    tuple[str],
    Model,
    Annotated[Model, ""],
    Annotated[list[Model], ""],
]


sparql_bound_field_type_instance_fail_parameters = [
    1,
    "1",
    URIRef("https://test.org"),
    object(),
    datetime.datetime.now(),
]


@pytest.mark.parametrize("obj", pydantic_model_static_type_true_parameters)
def test_is_pydantic_model_static_type_true(obj):
    assert _is_pydantic_model_static_type(obj)


@pytest.mark.parametrize("obj", pydantic_model_static_type_false_parameters)
def test_is_pydantic_model_static_type_false(obj):
    assert not _is_pydantic_model_static_type(obj)


@pytest.mark.parametrize("obj", [list[Model]])
def test_is_list_pydantic_model_static_type_true(obj):
    assert _is_list_pydantic_model_static_type(obj)


@pytest.mark.parametrize(
    "obj", [*list_static_type_false_parameters, list[BaseModel], list[Model | None]]
)
def test_is_list_pydantic_model_static_type_false(obj):
    assert not _is_list_pydantic_model_static_type(obj)


@pytest.mark.parametrize("obj", pydantic_model_union_static_type_true_parameters)
def test_is_pydantic_model_union_static_type_true(obj):
    assert _is_pydantic_model_union_static_type(obj)


@pytest.mark.parametrize("obj", list_static_type_false_parameters)
def test_is_pydantic_model_union_static_type_false(obj):
    assert not _is_pydantic_model_union_static_type(obj)


@pytest.mark.parametrize("obj", sparql_bound_field_type_parameters)
def test_is_sparql_bound_field_type(obj):
    assert _is_sparql_bound_field_type(obj)


@pytest.mark.parametrize("obj", sparql_bound_field_type_false_parameters)
def test_is_sparql_bound_field_type_false(obj):
    assert not _is_sparql_bound_field_type(obj)


@pytest.mark.parametrize("obj", sparql_bound_field_type_instance_fail_parameters)
def test_is_sparql_bound_field_type_instance_fail(obj):
    with pytest.raises(ValueError):
        _is_sparql_bound_field_type(obj)
