"""Pytest entry point for running UNGROUPED nested grouped model tests."""

from pydantic import BaseModel
import pytest
from rdfproxy import ConfigDict
from rdfproxy.mapper import _ModelBindingsMapper
from tests.utils._types import ModelBindingsMapperParameter


class GroupedNested(BaseModel):
    model_config = ConfigDict(group_by="nested")

    nested: str
    nested_child_list: list[str]


class Model(BaseModel):
    root: str
    nested: GroupedNested


class ModelGroupedNestedUnion(BaseModel):
    root: str
    nested: GroupedNested | None = None


ungrouped_nested_grouped_params = [
    ModelBindingsMapperParameter(
        model=Model,
        bindings=[
            {"root": "A", "nested": "AC1N", "nested_child_list": "AC1Na"},
            {"root": "B", "nested": "BC1N", "nested_child_list": "BC1Na"},
            {"root": "B", "nested": "BC1N", "nested_child_list": "BC2Nb"},
            {"root": "C", "nested": "CC1N", "nested_child_list": None},
        ],
        expected=[
            {"root": "A", "nested": {"nested": "AC1N", "nested_child_list": ["AC1Na"]}},
            {
                "root": "B",
                "nested": {"nested": "BC1N", "nested_child_list": ["BC1Na", "BC2Nb"]},
            },
            {
                "root": "B",
                "nested": {"nested": "BC1N", "nested_child_list": ["BC1Na", "BC2Nb"]},
            },
            {"root": "C", "nested": {"nested": "CC1N", "nested_child_list": []}},
        ],
    )
]

ungrouped_nested_grouped_union_params = [
    ModelBindingsMapperParameter(
        model=ModelGroupedNestedUnion,
        bindings=[
            {"root": "A", "nested": "AC1N", "nested_child_list": "AC1Na"},
            {"root": "B", "nested": "BC1N", "nested_child_list": "BC1Na"},
            {"root": "B", "nested": "BC1N", "nested_child_list": "BC2Nb"},
            {"root": "C", "nested": "CC1N", "nested_child_list": None},
        ],
        expected=[
            {"root": "A", "nested": {"nested": "AC1N", "nested_child_list": ["AC1Na"]}},
            {
                "root": "B",
                "nested": {"nested": "BC1N", "nested_child_list": ["BC1Na", "BC2Nb"]},
            },
            {
                "root": "B",
                "nested": {"nested": "BC1N", "nested_child_list": ["BC1Na", "BC2Nb"]},
            },
            {"root": "C", "nested": {"nested": "CC1N", "nested_child_list": []}},
        ],
    )
]


@pytest.mark.parametrize("params", ungrouped_nested_grouped_params)
def test_ungrouped_nested_grouped_model(params):
    mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
    result: list[dict] = [model.model_dump() for model in mapper.get_models()]

    assert result == params.expected


@pytest.mark.parametrize("params", ungrouped_nested_grouped_union_params)
def test_ungrouped_nested_grouped_union_model(params):
    mapper = _ModelBindingsMapper(model=params.model, bindings=params.bindings)
    result: list[dict] = [model.model_dump() for model in mapper.get_models()]

    assert result == params.expected
