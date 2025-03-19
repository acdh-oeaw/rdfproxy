"""Unit tests for group_by config model checkers."""

import pytest

from pydantic import BaseModel, create_model
from rdfproxy.utils._exceptions import RDFProxyGroupByException
from rdfproxy.utils._types import ConfigDict
from rdfproxy.utils.checkers.model_checker import check_model


class Invalid1(BaseModel):
    """group_by without corresponding scalar field and without list field."""

    model_config = ConfigDict(group_by="x")


class Invalid2(BaseModel):
    """list field but no group_by config at all."""

    x: list[int]


class Invalid3(BaseModel):
    """group_by references list field."""

    model_config = ConfigDict(group_by="x")
    x: list[int]


class Invalid4(BaseModel):
    """group_by references list field + additional fields."""

    model_config = ConfigDict(group_by="x")
    x: list[int]
    y: int
    z: int


class Invalid5(BaseModel):
    """legal group_by but no list field."""

    model_config = ConfigDict(group_by="x")
    x: int


class Invalid6(BaseModel):
    """group_by without corresponding scalar field."""

    model_config = ConfigDict(group_by="x")
    y: list[int]


class Valid1(BaseModel):
    """Simple valid group_by model."""

    model_config = ConfigDict(group_by="x")

    x: int
    y: list[int]


class Valid2(BaseModel):
    """Simple valid group_by model with additional fields"""

    model_config = ConfigDict(group_by="x")

    x: int
    y: int
    z: list[int]


class Valid3(BaseModel):
    """Simple valid group_by model with aggregated nested model."""

    model_config = ConfigDict(group_by="x")

    x: int
    y: int
    z: list[Valid2]


invalid_group_by_models = [
    Invalid1,
    Invalid2,
    Invalid3,
    Invalid4,
    Invalid5,
    Invalid6,
]

valid_group_by_models = [Valid1, Valid2, Valid3]


@pytest.mark.parametrize("model", invalid_group_by_models)
def test_check_invalid_group_by_models(model):
    with pytest.raises(RDFProxyGroupByException):
        check_model(model)


@pytest.mark.parametrize("model", valid_group_by_models)
def test_check_valid_group_by_models(model):
    assert check_model(model)


@pytest.mark.parametrize("model", invalid_group_by_models)
def test_check_nested_invalid_group_by_models(model):
    nested_model = create_model("NestedModel", nested=(model, ...))
    with pytest.raises(RDFProxyGroupByException):
        check_model(nested_model)


@pytest.mark.parametrize("model", valid_group_by_models)
def test_check_nested_valid_group_by_models(model):
    nested_model = create_model("NestedModel", nested=(model, ...))
    assert check_model(nested_model)
