"""Pytest entry point for running GROUPED nested grouped model tests."""

from pydantic import BaseModel
import pytest
from rdfproxy import ConfigDict
from rdfproxy.mapper import _ModelBindingsMapper
from tests.utils._types import ModelBindingsMapperParameter


bindings = [
    {"root": "A", "childlist": "AC1", "nested": "AC1N", "nested_child_list": "AC1Na"},
    {"root": "B", "childlist": "BC1", "nested": "BC1N", "nested_child_list": "BC1Na"},
    {"root": "B", "childlist": "BC1", "nested": "BC1N", "nested_child_list": "BC2Nb"},
    {"root": "C", "childlist": "CC1", "nested": "CC1N", "nested_child_list": None},
]


class Nested(BaseModel):
    model_config = ConfigDict(group_by="nested")

    nested: str
    nested_child_list: list[str]


class Root(BaseModel):
    model_config = ConfigDict(group_by="root")

    root: str

    childlist: list[str]
    nested_model: Nested


class RootGroupedNestedUnion(BaseModel):
    model_config = ConfigDict(group_by="root")

    root: str

    childlist: list[str]
    nested_model: Nested | None = None


grouped_nested_grouped_params = [
    ModelBindingsMapperParameter(
        model=Root,
        bindings=bindings,
        expected=[
            {
                "root": "A",
                "childlist": ["AC1"],
                "nested_model": {"nested": "AC1N", "nested_child_list": ["AC1Na"]},
            },
            {
                "root": "B",
                "childlist": ["BC1"],
                "nested_model": {
                    "nested": "BC1N",
                    "nested_child_list": ["BC1Na", "BC2Nb"],
                },
            },
            {
                "root": "C",
                "childlist": ["CC1"],
                "nested_model": {"nested": "CC1N", "nested_child_list": []},
            },
        ],
    )
]

grouped_nested_grouped_union_params = [
    ModelBindingsMapperParameter(
        model=RootGroupedNestedUnion,
        bindings=bindings,
        expected=[
            {
                "root": "A",
                "childlist": ["AC1"],
                "nested_model": {"nested": "AC1N", "nested_child_list": ["AC1Na"]},
            },
            {
                "root": "B",
                "childlist": ["BC1"],
                "nested_model": {
                    "nested": "BC1N",
                    "nested_child_list": ["BC1Na", "BC2Nb"],
                },
            },
            {
                "root": "C",
                "childlist": ["CC1"],
                "nested_model": {"nested": "CC1N", "nested_child_list": []},
            },
        ],
    )
]


@pytest.mark.parametrize("params", grouped_nested_grouped_params)
def test_grouped_nested_grouped_model(params):
    mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
    result: list[dict] = [model.model_dump() for model in mapper.get_models()]

    assert result == params.expected


@pytest.mark.parametrize("params", grouped_nested_grouped_union_params)
def test_grouped_nested_grouped_union_model(params):
    mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
    result: list[dict] = [model.model_dump() for model in mapper.get_models()]

    assert result == params.expected
