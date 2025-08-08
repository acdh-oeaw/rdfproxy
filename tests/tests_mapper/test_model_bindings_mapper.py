"""Pytest entry point for basic rdfproxy.mapper.ModelBindingsMapper."""

from pydantic import BaseModel
import pytest
from rdfproxy.mapper import _ModelBindingsMapper
from tests.tests_mapper.params.model_bindings_mapper_parameters import (
    author_array_collection_parameters,
    author_work_title_parameters,
    basic_parameters,
    empty_bindings_model_parameters,
    empty_default_only_model_parameters,
    grouping_nested_model_parameters,
    grouping_parameters,
    model_validator_parameters,
    none_model_parameters,
    optional_fields_model_parameters,
)


@pytest.mark.parametrize(
    ["model", "bindings", "expected"],
    [
        *basic_parameters,
        *grouping_parameters,
        *author_work_title_parameters,
        *author_array_collection_parameters,
        *grouping_nested_model_parameters,
        *empty_default_only_model_parameters,
        *none_model_parameters,
        *optional_fields_model_parameters,
        *empty_bindings_model_parameters,
        *model_validator_parameters,
    ],
)
def test_basic_model_bindings_mapper(model, bindings, expected):
    """Basic test for rdfproxy.ModelBindingsMapper.

    Given a model and a set of bindings, run the BindingsModelMapper logic
    and compare the result against the expected shape.
    """
    mapper: _ModelBindingsMapper = _ModelBindingsMapper(model, bindings)
    models: list[BaseModel] = mapper.get_models()
    assert [model.model_dump() for model in models] == expected
