"""Pytest entry point for testing rdfproxy.mapper.ModelBindingsMapper with model_flag config."""

import pytest

from pydantic import BaseModel
from rdfproxy.mapper import _ModelBindingsMapper
from tests.tests_mapper.params.model_bindings_mapper_model_bool_parameters import (
    parent_child_parameters,
)


@pytest.mark.parametrize(
    ["model", "bindings", "expected"],
    parent_child_parameters,
)
def test_basic_model_bindings_mapper(model, bindings, expected):
    """Test for rdfproxy.ModelBindingsMapper with model_bool config..

    Given a model and a set of bindings, run the BindingsModelMapper logic
    and compare the result against the expected shape.
    """
    mapper: _ModelBindingsMapper = _ModelBindingsMapper(model, *bindings)
    models: list[BaseModel] = mapper.get_models()
    assert [model.model_dump() for model in models] == expected
