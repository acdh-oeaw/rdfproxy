"""Pytest entry point for basic rdfproxy.mapper.ModelBindingsMapper."""

import pytest

from pydantic import BaseModel
from rdfproxy.mapper import ModelBindingsMapper
from tests.tests_mapper.params.model_bindings_mapper_parameters import (
    author_array_collection_parameters,
    author_work_title_parameters,
    basic_parameters,
    grouping_parameters,
    nested_grouping_parameters,
)


@pytest.mark.parametrize(
    ["model", "bindings", "expected"],
    [
        *basic_parameters,
        *grouping_parameters,
        *nested_grouping_parameters,
        *author_work_title_parameters,
        *author_array_collection_parameters,
    ],
)
def test_basic_model_bindings_mapper(model, bindings, expected):
    """Basic test for rdfproxy.ModelBindingsMapper.

    Given a model and a set of bindings, run the BindingsModelMapper logic
    and compare the result against the expected shape.
    """
    mapper: ModelBindingsMapper = ModelBindingsMapper(model, *bindings)
    models: list[BaseModel] = mapper.get_models()
    assert [model.model_dump() for model in models] == expected
