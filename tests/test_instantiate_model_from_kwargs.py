"""Pytest entry point for rdfproxy.instantiate_model_from_kwargs tests."""

import pytest
from rdfproxy.utils.utils import instantiate_model_from_kwargs
from tests.data.init_model_from_kwargs_parameters import (
    init_model_from_kwargs_parameters,
)
from tests.data.models import Person


@pytest.mark.parametrize(("model", "kwargs"), init_model_from_kwargs_parameters)
def test_init_model_from_kwargs(model, kwargs):
    """Check if the init_model_from_kwargs constructor successfully inits a model based on kwargs."""
    for _kwargs in kwargs:
        model_instance = instantiate_model_from_kwargs(model, **_kwargs)
        assert isinstance(model_instance, model)


def test_explicit_sparql_binding_allocation():
    bindings: dict = {"title": "Test Title", "name": "Test Name"}
    expected: dict = {"name": "Test Name", "work": {"name": "Test Title"}}

    model = instantiate_model_from_kwargs(Person, **bindings)

    assert expected == model.model_dump()
