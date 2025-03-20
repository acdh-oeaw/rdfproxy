"""Unit tests for model_bool config model checkers."""

from pydantic import BaseModel, Field, create_model
import pytest
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


class InvalidSub1(BaseModel):
    model_config = ConfigDict(model_bool="x")
    y: int


class InvalidSub2(BaseModel):
    model_config = ConfigDict(model_bool="x", group_by="y")
    y: int
    z: list[int]


class InvalidSub3(BaseModel):
    model_config = ConfigDict(group_by="y", model_bool="x")
    y: int
    z: list[int]


class InvalidSub4(BaseModel):
    model_config = ConfigDict(model_bool={"x"})
    y: int


class InvalidSub5(BaseModel):
    model_config = ConfigDict(model_bool={"x", "y"})
    y: int


class InvalidSub6(BaseModel):
    model_config = ConfigDict(model_bool={"y", "x"})
    y: int


class ValidSub1(BaseModel):
    model_config = ConfigDict(model_bool="y")

    y: int


class ValidSub2(BaseModel):
    model_config = ConfigDict(model_bool={"x", "y"})

    x: int
    y: int


class ValidSub3(BaseModel):
    model_config = ConfigDict(model_bool={"y", "x"})

    x: int
    y: int


class ValidSub4(BaseModel):
    model_config = ConfigDict(model_bool=lambda model: True)


class ValidSub5(BaseModel):
    model_config = ConfigDict(model_bool="x")

    x: int = Field(exclude=True)
    y: int


class ValidSub6(BaseModel):
    model_config = ConfigDict(model_bool={"x", "y"})

    x: int = Field(exclude=True)
    y: int


class ValidSub7(BaseModel):
    x: int
    y: int


class InvalidTypeSub1(BaseModel):
    model_config = ConfigDict(model_bool=["x"])


class InvalidTypeSub2(BaseModel):
    model_config = ConfigDict(model_bool=("x",))


class InvalidTypeSub3(BaseModel):
    model_config = ConfigDict(model_bool=(i for i in ["x", "y"]))


class InvalidTypeSub4(BaseModel):
    model_config = ConfigDict(model_bool=object())


invalid_root_models = [
    InvalidRoot1,
    InvalidRoot2,
    InvalidRoot3,
]

invalid_sub_models = [
    InvalidSub1,
    InvalidSub2,
    InvalidSub3,
    InvalidSub4,
    InvalidSub5,
    InvalidSub6,
]

invalid_type_sub_models = [
    InvalidTypeSub1,
    InvalidTypeSub2,
    InvalidTypeSub3,
    InvalidTypeSub4,
]

valid_sub_models = [
    ValidSub1,
    ValidSub2,
    ValidSub3,
    ValidSub4,
    ValidSub5,
    ValidSub6,
    ValidSub7,
]


@pytest.mark.parametrize("invalid_model", invalid_root_models)
def test_check_invalid_model_bool_root_models(invalid_model):
    with pytest.raises(RDFProxyModelBoolException):
        check_model(invalid_model)


@pytest.mark.parametrize("invalid_model", invalid_sub_models)
def test_check_invalid_model_bool_sub_models(invalid_model):
    Root: type[BaseModel] = create_model("Root", sub=(invalid_model, ...))

    with pytest.raises(RDFProxyModelBoolException):
        check_model(Root)


@pytest.mark.parametrize("invalid_model", invalid_type_sub_models)
def test_check_invalid_type_model_bool_sub_models(invalid_model):
    Root: type[BaseModel] = create_model("Root", sub=(invalid_model, ...))

    with pytest.raises(TypeError):
        check_model(Root)


@pytest.mark.parametrize("valid_model", valid_sub_models)
def test_check_valid_model_bool_sub_models(valid_model):
    Root: type[BaseModel] = create_model("Root", sub=(valid_model, ...))
    check_model(Root)
