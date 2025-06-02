"""Unit tests for model union type field checks."""

from typing import Any, Optional, Union

from pydantic import BaseModel
import pytest
from rdfproxy.utils.checkers.model_checker import check_model
from rdfproxy.utils.exceptions import ModelFieldException


class Nested(BaseModel):
    pass


class OtherNested(BaseModel):
    pass


class InvalidModelUnionField1(BaseModel):
    nested: Nested | None


class InvalidModelUnionField2(BaseModel):
    nested: Nested | Any


class InvalidModelUnionField3(BaseModel):
    nested: Nested | str | None


class InvalidModelUnionField4(BaseModel):
    nested: Nested | OtherNested


class InvalidModelUnionField5(BaseModel):
    nested: Nested | OtherNested | None


class InvalidModelUnionField6(BaseModel):
    nested: Optional[Nested]


class InvalidModelUnionField7(BaseModel):
    nested: Union[Nested, None]


class InvalidModelUnionField8(BaseModel):
    nested: Union[Nested, str, None]


class InvalidModelUnionField9(BaseModel):
    class DeeplyNested(BaseModel):
        nested: Nested | None

    deeply_nested: DeeplyNested


invalid_model_unions = [
    InvalidModelUnionField1,
    InvalidModelUnionField2,
    InvalidModelUnionField3,
    InvalidModelUnionField4,
    InvalidModelUnionField5,
    InvalidModelUnionField6,
    InvalidModelUnionField7,
    InvalidModelUnionField8,
    InvalidModelUnionField9,
]


class ValidModelUnionField1(BaseModel):
    nested: Nested | None = None


class ValidModelUnionField2(BaseModel):
    nested: Nested | str = "default"


class ValidModelUnionField3(BaseModel):
    nested: Nested | str = ""


class ValidModelUnionField4(BaseModel):
    nested: Nested | str | None = ""


class ValidModelUnionField5(BaseModel):
    nested: Nested | None = Nested()


class ValidModelUnionField6(BaseModel):
    nested: Optional[Nested] = None


class ValidModelUnionField7(BaseModel):
    nested: Union[Nested, None] = None


class ValidModelUnionField8(BaseModel):
    nested: Union[Nested, str] = "default"


class ValidModelUnionField9(BaseModel):
    nested: Union[Nested, None, str] = ""


valid_model_unions = [
    ValidModelUnionField1,
    ValidModelUnionField2,
    ValidModelUnionField3,
    ValidModelUnionField4,
    ValidModelUnionField5,
    ValidModelUnionField6,
    ValidModelUnionField7,
    ValidModelUnionField8,
    ValidModelUnionField9,
]


@pytest.mark.parametrize("model", invalid_model_unions)
def test_check_invalid_union_type_fields(model):
    with pytest.raises(ModelFieldException):
        check_model(model)


@pytest.mark.parametrize("model", valid_model_unions)
def test_check_valid_union_type_fields(model):
    check_model(model)
