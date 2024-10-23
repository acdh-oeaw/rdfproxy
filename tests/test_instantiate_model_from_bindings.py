"""Pytest entry point for rdfproxy.utils.utils.instantiate_model_from_bindings tests."""

import pytest

from rdfproxy.mapper import ModelBindingsMapper
from tests.data.parameters.instantiate_model_parameters import (
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
def test_basic_instantiate_model_from_bindings(model, bindings, expected):
    mapper = ModelBindingsMapper(model, *bindings)
    models = mapper.get_models()
    assert [model.model_dump() for model in models] == expected
