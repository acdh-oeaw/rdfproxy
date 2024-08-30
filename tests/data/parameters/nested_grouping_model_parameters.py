from tests.data.models.nested_grouping_model import NestedGroupingComplexModel
from tests.utils._types import Parameter


nested_grouping_parameters = [
    Parameter(
        model=NestedGroupingComplexModel,
        bindings=[
            {"x": 1, "y": 2, "a": "a value 1", "p": "p value 1"},
            {"x": 1, "y": 2, "a": "a value 2", "p": "p value 2"},
            {"x": 1, "y": 3, "a": "a value 3", "p": "p value 3"},
            {"x": 2, "y": 2, "a": "a value 1", "p": "p value 4"},
        ],
        expected=[
            {
                "p": "p value 1",
                "q": [{"a": "a value 1", "b": [{"x": 1, "y": 2}, {"x": 2, "y": 2}]}],
            },
            {"p": "p value 2", "q": [{"a": "a value 2", "b": [{"x": 1, "y": 2}]}]},
            {"p": "p value 3", "q": [{"a": "a value 3", "b": [{"x": 1, "y": 3}]}]},
            {
                "p": "p value 4",
                "q": [{"a": "a value 1", "b": [{"x": 1, "y": 2}, {"x": 2, "y": 2}]}],
            },
        ],
    )
]
