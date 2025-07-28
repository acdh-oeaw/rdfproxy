"""Pytest entry point for rdfproxy.utils.CurryModel tests."""

from typing import NamedTuple

from pydantic import BaseModel, ConfigDict, Field, ValidationError
import pytest
from rdfproxy.utils.utils import validate_model_field


class Point(BaseModel):
    x: int
    y: int = Field(ge=0)


class PointStrict(Point):
    model_config = ConfigDict(strict=True)


class ValidateModelFieldParameter(NamedTuple):
    model: type[BaseModel]
    kwargs: dict
    exception: type[Exception] | None = None


pass_params = [
    ValidateModelFieldParameter(model=Point, kwargs={"x": 1}),
    ValidateModelFieldParameter(model=Point, kwargs={"x": 1.0}),
    ValidateModelFieldParameter(model=Point, kwargs={"x": "1"}),
    ValidateModelFieldParameter(model=Point, kwargs={"y": 2}),
    ValidateModelFieldParameter(model=Point, kwargs={"x": 1, "y": 2}),
]

fail_params = [
    ValidateModelFieldParameter(
        model=Point, kwargs={"x": object()}, exception=ValidationError
    ),
    ValidateModelFieldParameter(
        model=PointStrict, kwargs={"x": 1.0}, exception=ValidationError
    ),
    ValidateModelFieldParameter(
        model=PointStrict, kwargs={"x": "1"}, exception=ValidationError
    ),
    ValidateModelFieldParameter(
        model=PointStrict, kwargs={"z": 3}, exception=ValueError
    ),
]


@pytest.mark.parametrize("param", pass_params)
def test_validate_model_field_basic_pass(param):
    for k, v in param.kwargs.items():
        validate_model_field(model=param.model, field=k, value=v)


@pytest.mark.parametrize("param", fail_params)
def test_validate_model_field_basic_fail(param):
    with pytest.raises(param.exception):
        for k, v in param.kwargs.items():
            validate_model_field(model=param.model, field=k, value=v)
