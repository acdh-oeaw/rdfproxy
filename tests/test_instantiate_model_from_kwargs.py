"""Pytest entry point for rdfproxy.instantiate_model_from_kwargs tests."""

import pytest

from rdfproxy import instantiate_model_from_kwargs
from tests.data.init_model_from_kwargs_parameters import (
    init_model_from_kwargs_parameters,
)


@pytest.mark.parametrize(("model", "kwargs"), init_model_from_kwargs_parameters)
def test_init_model_from_kwargs(model, kwargs):
    """Check if the init_model_from_kwargs constructor successfully inits a model based on kwargs."""
    for _kwargs in kwargs:
        model_instance = instantiate_model_from_kwargs(model, **_kwargs)
        assert isinstance(model_instance, model)
