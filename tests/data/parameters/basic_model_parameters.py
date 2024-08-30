"""Parameters for instantiate_model_from_bindings with basic models tests."""

from tests.data.models.basic_model import (
    BasicComplexModel,
    BasicNestedModel,
    BasicSimpleModel,
)
from tests.utils._types import Parameter


basic_parameters = [
    Parameter(
        model=BasicSimpleModel, bindings=[{"x": 1, "y": 2}], expected=[{"x": 1, "y": 2}]
    ),
    Parameter(
        model=BasicSimpleModel,
        bindings=[{"x": 3, "y": 4}, {"x": 5, "y": 6}],
        expected=[{"x": 3, "y": 4}, {"x": 5, "y": 6}],
    ),
    Parameter(
        model=BasicNestedModel,
        bindings=[{"a": "a value", "x": 1, "y": 2}],
        expected=[{"a": "a value", "b": {"x": 1, "y": 2}}],
    ),
    Parameter(
        model=BasicNestedModel,
        bindings=[{"a": "a value", "x": 1, "y": 2}, {"a": "a value", "x": 3, "y": 4}],
        expected=[
            {"a": "a value", "b": {"x": 1, "y": 2}},
            {"a": "a value", "b": {"x": 3, "y": 4}},
        ],
    ),
    Parameter(
        model=BasicComplexModel,
        bindings=[{"a": "a value", "x": 1, "y": 2, "p": "p value"}],
        expected=[{"p": "p value", "q": {"a": "a value", "b": {"x": 1, "y": 2}}}],
    ),
    Parameter(
        model=BasicComplexModel,
        bindings=[
            {"a": "a value", "x": 1, "y": 2, "p": "p value"},
            {"a": "a value", "x": 3, "y": 4, "p": "p value"},
        ],
        expected=[
            {"p": "p value", "q": {"a": "a value", "b": {"x": 1, "y": 2}}},
            {"p": "p value", "q": {"a": "a value", "b": {"x": 3, "y": 4}}},
        ],
    ),
]
