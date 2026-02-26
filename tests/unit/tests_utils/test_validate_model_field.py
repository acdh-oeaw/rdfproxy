"""Pytest entry point for rdfproxy.utils.CurryModel tests."""

from typing import NamedTuple

from pydantic import (
    AliasChoices,
    AliasPath,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
)
import pytest
from rdfproxy.utils.utils import validate_model_field


class Point(BaseModel):
    x: int
    y: int = Field(ge=0)


class PointStrict(Point):
    model_config = ConfigDict(strict=True)


class PointExtraForbid(Point):
    model_config = ConfigDict(extra="forbid")


class ValidateModelFieldParameter(NamedTuple):
    model: type[BaseModel]
    kwargs: dict
    exception: type[Exception] | None = None


def snake_to_pascal(value: str) -> str:
    return "".join(v.capitalize() for v in value.split("_"))


class User(BaseModel):
    """Model for testing field validation with Pydantic aliasing.

    The model implements an alias generators, alias paths and alias choices -
    which should cover the Pydantic validation aliasing machinery.
    """

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        extra="forbid",
    )

    id: int = Field(alias="user_id")

    display_name: str = Field(
        validation_alias=AliasChoices("displayName", "name", "label"),
    )

    created_at: str  # alias generator

    city: str = Field(
        validation_alias=AliasChoices(
            AliasPath("address", "city"),
            AliasPath("profile", "location", "city"),
        ),
    )


pass_params = [
    ValidateModelFieldParameter(model=Point, kwargs={"x": 1}),
    ValidateModelFieldParameter(model=Point, kwargs={"x": 1.0}),
    ValidateModelFieldParameter(model=Point, kwargs={"x": "1"}),
    ValidateModelFieldParameter(model=Point, kwargs={"y": 2}),
    ValidateModelFieldParameter(model=Point, kwargs={"x": 1, "y": 2}),
    ValidateModelFieldParameter(
        model=User,
        kwargs={
            "user_id": 1,
            "displayName": "Muzi",
            "CreatedAt": "some time",
            "address": {"city": "MuzTown"},
        },
    ),
    ValidateModelFieldParameter(
        model=User,
        kwargs={
            "user_id": 1,
            "name": "Muzi",
            "CreatedAt": "some time",
            "profile": {"location": {"city": "MuzTown"}},
        },
    ),
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
        model=PointExtraForbid, kwargs={"z": 3}, exception=ValidationError
    ),
    ValidateModelFieldParameter(
        model=User,
        kwargs={
            "user_id": 1,
            "displayName": "Muzi",
            "created_at": "some time",  # does not respect aliasing generator
            "address": {"city": "MuzTown"},
        },
        exception=ValidationError,
    ),
    ValidateModelFieldParameter(
        model=User,
        kwargs={
            "user_id": 1,
            "display_name": "Muzi",  # does not respect AliasChoices
            "CreatedAt": "some time",
            "profile": {"location": {"city": "MuzTown"}},
        },
        exception=ValidationError,
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
