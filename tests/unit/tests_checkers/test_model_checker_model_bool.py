"""Unit tests for model_bool config model checkers."""

import pytest

from pydantic import BaseModel
from rdfproxy.utils._exceptions import RDFProxyModelBoolException
from rdfproxy.utils._types import ConfigDict
from rdfproxy.utils.checkers.model_checker import check_model


class InvalidRoot1(BaseModel):
    model_config = ConfigDict(model_bool="x")

    x: int = 1


class DummyAggregate(BaseModel):
    pass


class InvalidRoot2(BaseModel):
    model_config = ConfigDict(model_bool="x", group_by="x")

    x: int = 1
    y: list[DummyAggregate]


class InvalidRoot3(BaseModel):
    model_config = ConfigDict(group_by="x", model_bool="x")

    x: int = 1
    y: list[DummyAggregate]


invalid_root_models = [
    InvalidRoot1,
    InvalidRoot2,
    InvalidRoot3,
]


@pytest.mark.parametrize("invalid_model", invalid_root_models)
def test_check_invalid_model_bool_models(invalid_model):
    with pytest.raises(RDFProxyModelBoolException):
        check_model(invalid_model)
