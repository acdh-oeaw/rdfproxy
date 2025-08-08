"""Pytest entry point for enforce_grouping_consistency model_config setting."""

from pydantic import BaseModel
import pytest
from rdfproxy import ConfigDict
from rdfproxy.utils.checkers.model_checker import check_model


class WarnModel(BaseModel):
    model_config = ConfigDict(enforce_grouping_consistency=False)


class WarnModel2(BaseModel):
    model_config = ConfigDict(enforce_grouping_consistency=True)


class WarnModel3(BaseModel):
    model_config = ConfigDict(
        model_bool=lambda model: True, enforce_grouping_consistency=False
    )


class Model1(BaseModel):
    model_config = ConfigDict(group_by="x", enforce_grouping_consistency=False)
    x: int
    y: list[int]


class Model2(BaseModel):
    model_config = ConfigDict(enforce_grouping_consistency=False, group_by="x")
    x: int
    y: list[int]


warn_models = [WarnModel, WarnModel2, WarnModel3]
models = [Model1, Model2]


@pytest.mark.parametrize("model", warn_models)
def test_check_enforce_grouping_consistency_warn(model):
    with pytest.warns(UserWarning):
        check_model(model)


@pytest.mark.parametrize("model", models)
def test_check_enforce_grouping_consistency_ok(model):
    check_model(model)
