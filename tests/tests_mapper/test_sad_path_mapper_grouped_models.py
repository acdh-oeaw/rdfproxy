import pytest

from pydantic import BaseModel
from rdfproxy import ConfigDict, ModelBindingsMapper
from rdfproxy.utils._exceptions import (
    InvalidGroupingKeyException,
    MissingModelConfigException,
)


class ModelMissingGroupByConfig(BaseModel):
    x: list[int]


class ModelMissingGroupByValue(BaseModel):
    model_config = ConfigDict(group_by="y")

    x: list[int]


@pytest.mark.xfail(reason="Not yet implemented, checks will run in model checkers.")
def test_sad_path_adapter_missing_grouping_config():
    with pytest.raises(MissingModelConfigException):
        ModelBindingsMapper(ModelMissingGroupByConfig, {"x": 1}).get_models()


@pytest.mark.xfail(reason="Not yet implemented, checks will run in model checkers.")
def test_sad_path_adapter_missing_grouping_value():
    with pytest.raises(InvalidGroupingKeyException):
        ModelBindingsMapper(ModelMissingGroupByValue, {"x": 1}).get_models()
