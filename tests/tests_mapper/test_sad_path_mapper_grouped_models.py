import pytest

from pydantic import BaseModel, ConfigDict
from rdfproxy import ModelBindingsMapper
from rdfproxy.utils._exceptions import (
    MissingModelConfigException,
    UnboundGroupingKeyException,
)


class ModelMissingGroupByConfig(BaseModel):
    x: list[int]


class ModelMissingGroupByValue(BaseModel):
    model_config = ConfigDict(group_by="y")

    x: list[int]


def test_sad_path_adapter_missing_grouping_config():
    with pytest.raises(MissingModelConfigException):
        ModelBindingsMapper(ModelMissingGroupByConfig, {"x": 1}).get_models()


def test_sad_path_adapter_missing_grouping_value():
    with pytest.raises(UnboundGroupingKeyException):
        ModelBindingsMapper(ModelMissingGroupByValue, {"x": 1}).get_models()
