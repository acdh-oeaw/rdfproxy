"""Parameters for instantiate_model_from_bindings with grouping models tests."""

from tests.data.models.grouping_model import GroupingComplexModel
from tests.utils._types import Parameter


grouping_parameters = [
    Parameter(
        model=GroupingComplexModel,
        bindings=[{"a": "a value", "x": 1, "y": 2, "p": "p value"}],
        expected=[{"p": "p value", "q": [{"a": "a value", "b": {"x": 1, "y": 2}}]}],
    ),
    Parameter(
        model=GroupingComplexModel,
        bindings=[
            {"a": "a value", "x": 1, "y": 2, "p": "p value"},
            {"a": "a value", "x": 3, "y": 4, "p": "p value"},
        ],
        expected=[
            {"p": "p value", "q": [{"a": "a value", "b": {"x": 1, "y": 2}}]},
            {"p": "p value", "q": [{"a": "a value", "b": {"x": 3, "y": 4}}]},
        ],
    ),
    Parameter(
        model=GroupingComplexModel,
        bindings=[
            {"a": "a value", "x": 1, "y": 2, "p": "p value"},
            {"a": "a value", "x": 3, "y": 4, "p": "p value"},
            {"a": "a value", "x": 1, "y": 4, "p": "p value"},
        ],
        expected=[
            {
                "p": "p value",
                "q": [
                    {"a": "a value", "b": {"x": 1, "y": 2}},
                    {"a": "a value", "b": {"x": 1, "y": 4}},
                ],
            },
            {"p": "p value", "q": [{"a": "a value", "b": {"x": 3, "y": 4}}]},
        ],
    ),
]
