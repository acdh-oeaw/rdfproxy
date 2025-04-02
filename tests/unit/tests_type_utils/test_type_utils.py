"""Unit tests for the type_utils module."""

from typing import Optional, Union

from pydantic import BaseModel, create_model
import pytest
from rdfproxy.utils.type_utils import (
    _is_list_pydantic_model_static_type,
    _is_list_static_type,
    _is_pydantic_model_static_type,
    _is_pydantic_model_union_static_type,
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
